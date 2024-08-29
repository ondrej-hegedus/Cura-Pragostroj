# Copyright (c) 2017 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import os.path
import time
import logging

from UM.Application import Application
from cura.Stages.CuraStage import CuraStage
from UM.Logger import Logger  # Adding messages to the log.
from UM.Qt.QtApplication import QtApplication
from PyQt6.QtCore import pyqtProperty, pyqtSignal, QObject, pyqtSlot, QUrl, QTimer
from UM.Application import Application
from cura.CuraApplication import CuraApplication
from cura.Machines.Models.GlobalStacksModel import GlobalStacksModel
from cura.Settings.CuraContainerRegistry import CuraContainerRegistry

from Pragostroj.src.PGNetworkedPrinterOutputDevice import PGNetworkedPrinterOutputDevice

# TODO: Create ClassDecorator @AddExceptionLoging, which will wrap each method with try: except: and log the exception

logger = logging.getLogger(__name__)


class PragostrojStage(CuraStage):
    """Stage for monitoring a 3D printing while it's printing."""

    listChange = pyqtSignal()
    popupErrorChange = pyqtSignal()

    @pyqtProperty(str)
    def test_var(self):
        return 'test_value'

    def __init__(self, parent=None):

        super().__init__(parent)

        # Wait until QML engine is created, otherwise creating the new QML components will fail
        Application.getInstance().engineCreatedSignal.connect(self._onEngineCreated)
        self._printer_output_device = None

        self._active_print_job = None
        self._active_printer = None
        self._list_component = None
        self._devices = []

        self._update_timer = QTimer()  # type: QTimer
        self._update_timer.setInterval(5000)  # TODO; Add preference for update interval
        # self._update_timer.setInterval(5)  # TODO; Add preference for update interval
        self._update_timer.setSingleShot(False)
        self._update_timer.timeout.connect(self._update)

        self._popupError = ''
        self._popupError2 = ''
        self._popupErrorShow = False
        # CuraApplication.getInstance().getMachineManager().activeMachineChanged.connect(self._onActiveMachineChanged)

    def _update(self):
        # TODO: try reconnect
        self.listChange.emit()
        # print("UPDATE")

    @pyqtProperty("QVariantList", notify=listChange)
    def progostrojDevices(self):
        active_machine_id = CuraApplication.getInstance().getPreferences().getValue("cura/active_machine")
        devices = []
        offlineDevices = []

        machine_stacks = CuraContainerRegistry.getInstance().findContainerStacksMetadata(type="machine")
        for ms in machine_stacks:
            if 'pg_network_key' in ms:
                filtredDeviceList = list(filter(lambda dev: dev.getId() == ms.get('pg_network_key'), self._devices))
                # TODO: Check whether this logic is correct
                if len(filtredDeviceList) == 1:
                    if filtredDeviceList[0].getStatus == "OFF":
                        offlineDevices.append(filtredDeviceList[0])
                    else:
                        devices.append(filtredDeviceList[0])
                else:
                    offlineDevices.append({
                        'getPrinterName': ms.get('name'),
                        'address': ms.get('id')[11:],
                        'getStatus': 'OFF',
                        # 'getPrinterModel': '??',
                        'getPrinterModel': '',
                        'isPrinting': False,
                        'getExtruders': [],
                    })

        devices.sort(key=lambda dev: dev.getPrinterName)
        for offlineDevice in offlineDevices:
            devices.append(offlineDevice)
        return devices

    def _setActivePrintJob(self, print_job):
        if self._active_print_job != print_job:
            self._active_print_job = print_job

    def _setActivePrinter(self, printer):
        # TODO: Refactor
        if self._active_printer != printer:
            if self._active_printer:
                self._active_printer.activePrintJobChanged.disconnect(self._onActivePrintJobChanged)
            self._active_printer = printer
            if self._active_printer:
                self._setActivePrintJob(self._active_printer.activePrintJob)
                # Jobs might change, so we need to listen to it's changes.
                self._active_printer.activePrintJobChanged.connect(self._onActivePrintJobChanged)
            else:
                self._setActivePrintJob(None)

    def _onActivePrintJobChanged(self):
        self._setActivePrintJob(self._active_printer.activePrintJob)

    def _onActivePrinterChanged(self):
        self._setActivePrinter(self._printer_output_device.activePrinter)

    def _onOutputDevicesChanged(self):
        try:
            # We assume that you are monitoring the device with the highest priority.
            new_output_device = Application.getInstance().getMachineManager().printerOutputDevices[0]
            if new_output_device != self._printer_output_device:
                if self._printer_output_device:
                    try:
                        self._printer_output_device.printersChanged.disconnect(self._onActivePrinterChanged)
                    except TypeError:
                        # Ignore stupid "Not connected" errors.
                        pass

                self._printer_output_device = new_output_device

                # TODO: This two lines, call self._setActivePrinter twice - probably not necessary
                self._printer_output_device.printersChanged.connect(self._onActivePrinterChanged)
                self._setActivePrinter(self._printer_output_device.activePrinter)
        except IndexError:
            pass

    def _onEngineCreated(self):
        # We can only connect now, as we need to be sure that everything is loaded (plugins get created quite early)
        Application.getInstance().getMachineManager().outputDevicesChanged.connect(self._onOutputDevicesChanged)
        self._onOutputDevicesChanged()

        plugin_path = Application.getInstance().getPluginRegistry().getPluginPath(self.getPluginId())
        if plugin_path is not None:
            # Logger.log("d", "plugin_path is not None")
            menu_component_path = os.path.join(plugin_path, "resources", "qml", "PragostrojStageMenu.qml")
            main_component_path = os.path.join(plugin_path, "resources", "qml", "PragostrojStageMain.qml")
            # Logger.log("c", menu_component_path)
            # Logger.log("c", main_component_path)
            self.addDisplayComponent("menu", menu_component_path)
            self.addDisplayComponent("main", main_component_path)

        Application.getInstance()._qml_engine.rootContext().setContextProperty("PragostrojStage", self)

    def onStageSelected(self):
        self._devices = []

        for discoveredDevice in CuraApplication.getInstance().getDiscoveredPrintersModel().discoveredPrinters:
            device = discoveredDevice.device
            if (isinstance(device, PGNetworkedPrinterOutputDevice)):
                self._devices.append(device)
                if not device.isConnected():
                    device.connect()

        self.listChange.emit()
        self._update_timer.start()

    def onStageDeselected(self) -> None:
        """Called when going to a different stage"""
        self._update_timer.stop()
        pass

    @pyqtSlot(QObject, name="selectPrepareStage")
    def selectPrepareStage(self, device):
        logger.debug(f'device: {device.getName()}')

        machine_stacks = CuraContainerRegistry.getInstance().findContainerStacksMetadata(type="machine")
        found_machines = list(filter(lambda ms: ms.get('pg_network_key', '') == device.getId(), machine_stacks))
        # import pdb
        # # pdb.set_trace()
        # breakpoint()
        if len(found_machines):
            machine = found_machines[0]
            logger.debug(f'machine: {machine}')
            CuraApplication.getInstance().getMachineManager().setActiveMachine(machine.get('id'))
            CuraApplication.getInstance().getController().setActiveStage("PrepareStage")

        # TODO: Find better place to connect it. Connect it only once
        # CuraApplication.getInstance().getMachineManager().activeMachineChanged.connect(self._onActiveMachineChanged)

    # Called after selectPrepareStage, so the material is set for selected printer
    # def _onActiveMachineChanged(self):

        # breakpoint()
        # print('placeholder')
        machine_manager = CuraApplication.getInstance().getMachineManager()
        # mm.activeMachine.id
        # pg_stage = CuraApplication.getInstance().getController().getStage('Pragostroj')
        # ps.progostrojDevices
        # NOTE: It's quite complicated to get this. THe items in progostrojDevices are somethimes intance of a class and somethimes dict
        #       + there can be multiple printers with a same name, in which case the comparison needs to be done based on address as well

        # Dicts are saved but not connected printers

        # logger.debug('--------------------')
        # logger.debug(list(filter(lambda pdev: not isinstance(pdev, dict), pg_stage.progostrojDevices)))
        # pg_active_devices = list(
        #     filter(
        #         lambda pdev: pdev.address == machine_manager.activeMachineAddress,
        #         filter(lambda pdev: not isinstance(pdev, dict), pg_stage.progostrojDevices)
        #     )
        # )

        # # TODO: handle async dependency, instead of this mechanism
        # # time.sleep(3)
        # atempts = 10
        # while (not pg_active_devices) or (device.getName() != pg_active_devices[0].getName()):
        #     logger.debug(f'atempts: {atempts}')
        #     if pg_active_devices:
        #         logger.debug(f'found_device: {pg_active_devices[0].getName()}')

        #     atempts -= 1
        #     time.sleep(0.5)
        #     pg_active_devices = list(
        #         filter(
        #             lambda pdev: pdev.address == machine_manager.activeMachineAddress,
        #             filter(lambda pdev: not isinstance(pdev, dict), pg_stage.progostrojDevices)
        #         )
        #     )

        #     if atempts == 0:
        #         logger.warning('Unable to get correct active device to setup material')
        #         return

        # pg_active_device = pg_active_devices[0]
        pg_active_device = device

        # logger.debug(f'active_device: {dir(pg_active_device)}')
        logger.debug(f'active_device: {pg_active_device.getName()}')

        #  ... .extruders ... .material ... .nozzle
        cr = CuraApplication.getInstance().getContainerRegistry()
        cr.findContainersMetadata(type='material')
        # breakpoint()
        # machine_manager.setMaterial('PETG 1.75')
        # machine_manager.setMaterialById(0, 193)
        # machine_manager.setMaterialById(0, '03f24266-0291-43c2-a6da-5211892a2699')
        # NOTE: Not valid anymore: Material is from printer in form like 'PLA 1.75' and in definition files as pragostroj_pla_175
        # machine_manager.setMaterialById(0, 'pragostroj_pva_175')
        for i, extruder in enumerate(pg_active_device.extruders):
            # breakpoint()
            # E.g. pragostroj_pva_175
            # TODO: ... Missing material
            logger.debug(f'extruder: {i}')
            if not extruder.material:
                continue
            material_id = 'pragostroj_{}_{}'.format(
                extruder.material['label'].lower(),
                str(extruder.material['diameter']).replace('.', '')
            )
            logger.debug(f'material_id: {material_id}')
            machine_manager.setMaterialById(
                i,
                # In case the material-name doesn't exist, the previus one will stay set (without error, which is wanted behaviours)
                material_id
            )
            # breakpoint()
            # the values are like 'E 0.3', 'E 0.5', 'E 0.5 (2.85)'
            variant_name = 'E {}'.format(extruder.nozzle['outputDiameter']) \
                if extruder.nozzle['inputDiameter'] == 1.75 else \
                'E {} ({})'.format(extruder.nozzle['outputDiameter'], extruder.nozzle['inputDiameter'])
            logger.debug(f'variant_name: {variant_name}')
            machine_manager.setVariantByName(i, variant_name)

            # machine_manager.setVariantByName(i, 'E 0.5')
            # cr.findContainersMetadata(type='material', id=material_id)  # Guid is from pd.extruders[0].material.guid
            # [cr._containers[k] for k in cr._containers.keys() if 'pragostroj' in k]

            # from cura.Settings.GlobalStack import GlobalStack
            # machine_definition_id = self._global_container_stack.definition.id
            # machine_node = ContainerTree.getInstance().machines.get(machine_definition_id)

            # from cura.Machines.ContainerTree import ContainerTree
            # machine_node = ContainerTree.getInstance().machines['pragostroj_1'].variants

        # cr.findContainersMetadata(type='material', GUID='3e4f98ac-a6a7-43eb-986e-cb96353b28a6')  # Guid is from pd.extruders[0].material.guid

        # mm.setVariant(4)
        # mm.setVariant('f9c7d9de-9b40-47e7-a52d-f064ae1d8ed3')
        # mm.setVariantByName(0, 'Brass')

    @pyqtSlot(QObject, name="selectMonitorStage")
    def selectMonitorStage(self, device):
        machine_stacks = CuraContainerRegistry.getInstance().findContainerStacksMetadata(type="machine")
        foundMachines = list(filter(lambda ms: ms.get('pg_network_key', '') == device.getId(), machine_stacks))
        if len(foundMachines):
            foundMachine = foundMachines[0]
            CuraApplication.getInstance().getMachineManager().setActiveMachine(foundMachine.get('id'))
            CuraApplication.getInstance().getController().setActiveStage("MonitorStage")

    @pyqtProperty(bool, notify=popupErrorChange)
    def popupError(self):
        return self._popupErrorShow

    @pyqtProperty(str, notify=popupErrorChange)
    def popupErrorText(self):
        # return 'test text hardcoded'
        return self._popupError

    @pyqtProperty(str, notify=popupErrorChange)
    def popupErrorText2(self):
        return self._popupError2

    def showPopupError(self, err_text1, err_text2):
        if not self._popupErrorShow:
            self._popupError = err_text1
            self._popupError2 = err_text2
            self._popupErrorShow = True
            self.popupErrorChange.emit()

    @pyqtSlot(name="hidePopupError")
    def hidePopupError(self):
        self._popupErrorShow = False
        self.popupErrorChange.emit()






