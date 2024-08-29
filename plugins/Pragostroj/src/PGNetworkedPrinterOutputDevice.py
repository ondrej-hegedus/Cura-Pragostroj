# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import os
from time import sleep
from time import time
from typing import List, Optional, Dict
import logging

from PyQt6.QtCore import pyqtProperty, pyqtSignal, QObject, pyqtSlot

from UM.Logger import Logger
from cura.CuraApplication import CuraApplication
from cura.PrinterOutput.Models.PrinterOutputModel import PrinterOutputModel
from cura.PrinterOutput.NetworkedPrinterOutputDevice import NetworkedPrinterOutputDevice, AuthState
from cura.PrinterOutput.PrinterOutputDevice import ConnectionType, ConnectionState
from PyQt6.QtNetwork import QHttpPart, QNetworkRequest, QNetworkReply

from UM.Qt.QtApplication import QtApplication

from Pragostroj.src.PGApiClient import PGApiClient
from Pragostroj.src.EndpointModel.PGRecentFile import PGRecentFile
from Pragostroj.src.EndpointModel.PGPrintResult import PGPrintResult
from Pragostroj.src.EndpointModel.PGExtruder import PGExtruder
from Pragostroj.src.ExportFileJob import ExportFileJob
from Pragostroj.src.EndpointModel.PGProductInfo import PGProductInfo
from Pragostroj.src.EndpointModel.PGMemoryFiles import PGMemoryFiles
from Pragostroj.src.EndpointModel.PGPrintInfo import PGPrintInfo
from functools import partial
from datetime import datetime
from Pragostroj.src.EndpointModel.PGPlate import PGPlate
from Pragostroj.src.EndpointModel.PGPrinterStatus import PGPrinterStatus
from Pragostroj.src.EndpointModel.PGPrinterState import PGPrinterState
from Pragostroj.src.EndpointModel.PGCheckFile import PGCheckFile
from Pragostroj.src.EndpointModel.PGEndInfo import PGEndInfo
from Pragostroj.src.PGUtils import formatTime
from cura.Settings.CuraContainerRegistry import CuraContainerRegistry


logger = logging.getLogger(__name__)


# TODO: Register as type, usable in QML
# class ConflictsPopup():
#     def __init__(self, show, print_file, conflicts):
#         self.show = show
#         self.print_file = print_file
#         self.conflicts = conflicts


class PGNetworkedPrinterOutputDevice(NetworkedPrinterOutputDevice):
    """Output device class that forms the basis of Ultimaker networked printer output devices.

    Currently used for local networking and cloud printing using Ultimaker Connect.
    This base class primarily contains all the Qt properties and slots needed for the monitor page to work.
    """

    META_NETWORK_KEY = "pg_network_key"
    META_CLUSTER_ID = "pg_cloud_cluster_id"

    # Signal emitted when the status of the print jobs for this cluster were changed over the network.
    printJobsChanged = pyqtSignal()

    # Signal emitted when the currently visible printer card in the UI was changed by the user.
    activePrinterChanged = pyqtSignal()

    # Notify can only use signals that are defined by the class that they are in, not inherited ones.
    # Therefore we create a private signal used to trigger the printersChanged signal.
    _clusterPrintersChanged = pyqtSignal()

    # States indicating if a print job is queued.
    QUEUED_PRINT_JOBS_STATES = {"queued", "error"}

    monitorChange = pyqtSignal()

    states = {
        "B": "The printer executes a command.",
        "C": "Printer configuration in progress.",
        "F": "DUET3 firmware upgrade in progress.",
        "I": "Ready to print.",
        "A": "Print is paused.",
        "D": "Printing, please wait.",
        "E": "Warming up.",
        "P": "Printing",
        "R": "Resuming a paused print.",
        "S": "Print is paused.",
        "T": "Changing the extruder.",
        "?": "Unknown",
        "PF": "Print has been finished!",
        "OFF": "Printer is offline",
        "PC": "Print has been canceled.",
        "PE": "Print error."
    }

    # states = {
    #     "B": "tiskárna provádí příkaz",
    #     "C": "probíhá konfigurace tiskárny",
    #     "F": "probíhá upgrade firmware v DUET3",
    #     "I": "Ready to print",
    #     "A": "Printing paused",
    #     "D": "Printing / please wait",
    #     "E": "Warming up",
    #     "P": "Printing",
    #     "R": "znovuobnovení pozastaveného tisku",
    #     "S": "tiskárna byla zastavena",
    #     "T": "změna extruderu",
    #     "?": "Unknown",
    #     "PF": "Print has finished!",
    #     "OFF": "Offline",
    #     "PC": "Print canceled",
    #     "PE": "Print error"
    # }

    # conflicts = {
    #     "NOZZLE_DIAMETER_CONFLICT": "Nozzle diameter does not correspond to the file",
    #     "NOZZLE_DIAMETER_CONFLICT_0": "Nozzle 1 diameter does not correspond to the file",
    #     "NOZZLE_DIAMETER_CONFLICT_1": "Nozzle 2 diameter does not correspond to the file",
    #     "NOZZLE_DIAMETER_CONFLICT_2": "Nozzle 3 diameter does not correspond to the file",
    #     "NOZZLE_DIAMETER_CONFLICT_3": "Nozzle 4 diameter does not correspond to the file",
    #     "NOZZLE_MATERIAL_CONFLICT": "Material used does not correspond to the nozzle",
    #     "NOZZLE_MATERIAL_CONFLICT_0": "Material 1 used does not correspond to the nozzle",
    #     "NOZZLE_MATERIAL_CONFLICT_1": "Material 2 used does not correspond to the nozzle",
    #     "NOZZLE_MATERIAL_CONFLICT_2": "Material 3 used does not correspond to the nozzle",
    #     "NOZZLE_MATERIAL_CONFLICT_3": "Material 4 used does not correspond to the nozzle",
    #     "MATERIAL_DIAMETER_CONFLICT": "Material diameter mismatch",
    #     "MATERIAL_DIAMETER_CONFLICT_0": "Material 1 diameter mismatch",
    #     "MATERIAL_DIAMETER_CONFLICT_1": "Material 2 diameter mismatch",
    #     "MATERIAL_DIAMETER_CONFLICT_2": "Material 3 diameter mismatch",
    #     "MATERIAL_DIAMETER_CONFLICT_3": "Material 4 diameter mismatch",
    #     "MATERIAL_CONFLICT": "Material type mismatch",
    #     "MATERIAL_CONFLICT_0": "Material type mismatch in extruder 1",
    #     "MATERIAL_CONFLICT_1": "Material type mismatch in extruder 2",
    #     "MATERIAL_CONFLICT_2": "Material type mismatch in extruder 3",
    #     "MATERIAL_CONFLICT_3": "Material type mismatch in extruder 4",
    #     "EMPTY_EXTRUDER": "The extruder is empty",
    #     "EMPTY_EXTRUDER_0": "The extruder 1 is empty",
    #     "EMPTY_EXTRUDER_1": "The extruder 2 is empty",
    #     "EMPTY_EXTRUDER_2": "The extruder 3 is empty",
    #     "EMPTY_EXTRUDER_3": "The extruder 4 is empty",
    #     "PLATE_CONFLICT": "Plate type mismatch",
    #     "PLATE_IS_NOT_EMPTY": "Plate is not empty!",
    #     "EXTRUDER_COUNT_CONFLICT": "Extruders count mismatch",
    #     "NOZZLE_NOT_FOUND_EXTRUDER": "Nozzle not found",
    #     "NOZZLE_NOT_FOUND_EXTRUDER_1": "Nozzle 1 not found",
    #     "NOZZLE_NOT_FOUND_EXTRUDER_2": "Nozzle 2 not found",
    #     "NOZZLE_NOT_FOUND_EXTRUDER_3": "Nozzle 3 not found",
    #     "UNKNOWN_MATERIAL_EXTRUDER": "Unknown material in the extruder",
    #     "UNKNOWN_MATERIAL_EXTRUDER_1": "Unknown material in the extruder 1",
    #     "UNKNOWN_MATERIAL_EXTRUDER_2": "Unknown material in the extruder 2",
    #     "UNKNOWN_MATERIAL_EXTRUDER_3": "Unknown material in the extruder 3",
    #     "NO_EXTRUDERS_INFO": "No print info available",
    #     "NO_HEATED_CHAMBER": "No heated chamber available"
    # }

    def __init__(self, device_id: str, address: str, properties: Dict[bytes, bytes], productInfo: PGProductInfo, parent=None) -> None:

        super().__init__(device_id=device_id,
                         address=address,
                         properties=properties,
                         connection_type=ConnectionType.NetworkConnection,
                         parent=parent)

        # self._errorPopup = {
        #     'errorLine1': error_line_1,
        #     'errorLine2': error_line_2,
        #     'show': True,
        # }

        self.device_id = device_id
        self._productInfo = productInfo  # type: PGProductInfo
        self._api = None
        # Trigger the printersChanged signal when the private signal is triggered.
        self.printersChanged.connect(self._clusterPrintersChanged)
        # self.printerType = "pragostroj"

        # Keeps track the last network response to determine if we are still connected.
        self._time_of_last_response = time()
        self._time_of_last_request = time()

        # Set the display name from the properties.
        self.setName(self.getProperty("name"))

        # Set the display name of the printer type.
        definitions = None  # CuraApplication.getInstance().getContainerRegistry().findContainers(id=self.printerType)
        self._printer_type_name = definitions[0].getName() if definitions else ""

        # Keeps track of all printers in the cluster.
        self._printers = []  # type: List[PrinterOutputModel]
        self._has_received_printers = False

        # Keeps track of all print jobs in the cluster.
        self._print_jobs = []  # type: List[UM3PrintJobOutputModel]

        # Keep track of the printer currently selected in the UI.
        self._active_printer = None  # type: Optional[PrinterOutputModel]

        # By default we are not authenticated. This state will be changed later.
        self._authentication_state = AuthState.NotAuthenticated

        # Load the Monitor UI elements.
        self._loadMonitorTab()

        # The job upload progress message modal.
        # self._progress = PrintJobUploadProgressMessage()

        self._timeout_time = 10

        self._num_is_host_check_failed = 0

        self.printerName = self.getProperty("name")  # type: str
        self.status = None  # type: PGPrinterStatus
        self.printerModel = self.getProperty("model") + " " + self.getProperty("firmware_version")  # type: str
        self.printerState = None  # type: PGPrinterState
        # Note: this could propably replace ._address. I put it here now, just to be able to show IP adress in UI, when printer is offline
        # self.offline_address = self.getProperty("address")

        self.files = []  # type: List[PGRecentFile]
        self.memoryFiles = []  # type: List[PGMemoryFiles]
        self.extruders = []  # type: List[PGExtruder]
        self.lastStatus = ""
        self.printInfo = {}  # type: Dict[PGPrintInfo]
        self.plate = None  # type: PGPlate

        self._setInterfaceElements()
        self.uploadedFileName = ""

        self.selectedFiles = {}  # type: Dict[str]

        self._mmsort = 0  # type int
        # self._conflictsPopupShow = False
        # self._conflictsPopupPrintFile = ''
        # self._conflictsPopupConflicts = []
        # self._conflicts_popup = ConflictsPopup(False, '', None)
        self._conflictsPopupShow = False
        self._conflictsPopup = {
            'show': False,
            'printFile': '',
            'conflicts': []
        }

        self._errorPopup = {
            'show': False,
            'textLine1': '',
            'textLine2': ''
        }
        # self._currentPrintFile = None
        # self._currentPrintConflicts = []
        self._endStatus = None #type: PGEndInfo

        self._popupInfo = ''
        self._popupInfo2 = ''
        self._popupInfoShow = False

        # self._popupError = ''
        # self._popupError2 = ''
        # self._popupErrorShow = False

        self._isInCura = True

        CuraApplication.getInstance().getController().activeStageChanged.connect(self._onStageChanged)

    def _setInterfaceElements(self) -> None:
        """Set all the interface elements and texts for this output device."""

        self.setPriority(3)  # Make sure the output device gets selected above local file output
        self.setShortDescription("Print over network")
        self.setDescription("Print over network")
        self.setConnectionText("Connected over the network")

    def requestWrite(self, nodes: List["SceneNode"], file_name: Optional[str] = None, limit_mimetypes: bool = False,
                     file_handler: Optional["FileHandler"] = None, filter_by_machine: bool = False, **kwargs) -> None:
        Logger.log('i', '---PGNetwOD: requestWrite ----')

        self.writeStarted.emit(self)
        job = ExportFileJob(file_handler=file_handler, nodes=nodes, firmware_version=self.firmwareVersion)
        job.finished.connect(self._onPrintJobCreated)
        job.start()

    def _onPrintJobCreated(self, job: ExportFileJob) -> None:
        """Handler for when the print job was created locally.
        It can now be sent over the network.
        """

        logger.debug('---PRINT-JOB-CREATED---')
        CuraApplication.getInstance().getController().setActiveStage("MonitorStage")
        # TODO: show popup
        self._active_exported_job = job
        self._startPrintJobUpload()

    def _startPrintJobUpload(self, unique_name: str = None) -> None:
        """Upload the print job to the group."""

        if not self._active_exported_job:
            Logger.log("e", "No active exported job to upload!")
            return

        output = self._active_exported_job.getOutput()
        # logger.debug('---TO PRINT: ---')
        # logger.debug(output.decode())
        # logger.debug(output)
        # self._progress.show()
        parts = [
            self._createFormPart("name=\"file\"; filename=\"%s\"" % self._active_exported_job.getFileName(), output)
        ]
        self.uploadedFileName = self._active_exported_job.getFileName()
        # If a specific printer was selected we include the name in the request.
        # FIXME: Connect should allow the printer UUID here instead of the 'unique_name'.
        if unique_name is not None:
            parts.append(self._createFormPart("name=require_printer_name", bytes(unique_name, "utf-8"), "text/plain"))
        # FIXME: move form posting to API client
        url = "{}/file/upload".format(self._getApiClient().PRINTER_API_PREFIX)
        logger.debug(f'Requesting: {url}')
        self.postFormWithParts(url, parts, on_finished=self._onPrintUploadCompleted, on_progress=self._onPrintJobUploadProgress)
        self._active_exported_job = None

    def _onPrintJobUploadProgress(self, bytes_sent: int, bytes_total: int) -> None:
        """Handler for print job upload progress."""

        percentage = (bytes_sent / bytes_total) if bytes_total else 0
        #TODO: show progress
        # self._progress.setProgress(percentage * 100)
        # self.writeProgress.emit()
        ##print("_____UPLOAD progress: " + str(percentage))

    def _onPrintUploadCompleted(self, reply: QNetworkReply) -> None:
        """Handler for when the print job was fully uploaded to the cluster."""
        # self._progress.hide()
        # PrintJobUploadSuccessMessage().show()
        # self.writeFinished.emit()
        #        print("wait")
        #        sleep(1)
        #        self._getApiClient().getMachineFiles(lambda files: self.testPrint(files))
        #
        #    def testPrint(self, files):
        # #print("api.printFile")
        # logger.debug(f'Response: {reply.error()} , {reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)} \n {reply.readAll()}')
        # self._getApiClient().printFile(self.uploadedFileName, lambda res: self._printOperationResult(res), lambda res: self._printOperationResult(res))
        self.printFile(self.uploadedFileName)

    def _createFormPart(self, content_header: str, data: bytes, content_type: Optional[str] = None) -> QHttpPart:
        part = QHttpPart()

        if not content_header.startswith("form-data;"):
            content_header = "form-data; " + content_header
        part.setHeader(QNetworkRequest.KnownHeaders.ContentDispositionHeader, content_header)

        if content_type is not None:
            part.setHeader(QNetworkRequest.ContentTypeHeader, content_type)

        part.setBody(data)
        return part

    # @pyqtProperty(str, constant=True)
    # def offlineAddress(self) -> str:
    #     """The IP address of the printer."""
    #     return self.offline_address

    # @pyqtProperty(str, constant=True)
    # def address(self) -> str:
    #     """The IP address of the printer."""
    #     return self._address

    @pyqtProperty(str, constant=True)
    def imgpath(self) -> str:
        return 'http://' + self._address + self._getApiClient().PRINTER_API_PREFIX

    @pyqtProperty(str, constant=True)
    def printerTypeName(self) -> str:
        """The display name of the printer."""
        return self._printer_type_name

    # Get the currently active printer in the UIpyqtProperty(QObject, notify=activePrinterChanged)
    @pyqtProperty(QObject)
    def activePrinter(self) -> Optional[PrinterOutputModel]:
        return self._active_printer

    # Set the currently active printer from the UI.
    @pyqtSlot(QObject, name="setActivePrinter")
    def setActivePrinter(self, printer: Optional[PrinterOutputModel]) -> None:
        if self.activePrinter == printer:
            return
        self._active_printer = printer
        self.activePrinterChanged.emit()

    # NOTE: disabled-function-logging because of "spam"
    def _update(self) -> None:
        machine_stacks = CuraContainerRegistry.getInstance().findContainerStacksMetadata(type="machine")
        isInCura = False
        for ms in machine_stacks:
            if 'pg_network_key' in ms:
                if ms.get('pg_network_key') == self.device_id:
                    isInCura = True
                    break

        # update only when device is added in cura
        if not isInCura:
            return

        super()._update()
        #print("UPDATE "+self.device_id)

        self._getApiClient().getStatus(lambda status: self._checkStatus(status))
        self._checkStillConnected()
        self.updatePlate()
        self.updatePrinterState()
        self.updateEndInfo()
        self.updateExtruders()

    @pyqtSlot(name="updateRecentFiles")
    def updateRecentFiles(self):
        self._getApiClient().getRecentFiles(lambda files: self._updateRecentFiles(files))

    @pyqtSlot(name="updateMachineMemory")
    def updateMachineMemory(self):
        self._getApiClient().getMachineFiles(lambda files: self._updateMachineFiles(files))

    @pyqtSlot(name="updateQueue")
    def updateQueue(self):
        pass
        # self._getApiClient().getQueue(lambda queue: self._updateQueue(queue))

    # NOTE: disabled-function-logging because of "spam"
    def _checkStatus(self, status):
        lastState = self.getState
        self.status = status
        self._responseReceived()
        self.checkStateTransition(lastState, self.getState)
        # #print("EMIT")
        self.monitorChange.emit()

    def _updateQueue(self, queue):
        self.queue = queue

    def _updateRecentFiles(self, files):
        self.files = files

    def _updateMachineFiles(self, files):
        self.memoryFiles = files

    # NOTE: disabled-function-logging because of "spam"
    def updateExtruders(self):
        self._getApiClient().getExtruders(lambda extruders: self._updateExtruders(extruders))

    # NOTE: disabled-function-logging because of "spam"
    def _updateExtruders(self, extruders):
        self.extruders = extruders

    def getPrintInfo(self, filename):
        savePrintInfoFunc = partial(self.savePrintInfo, filename)
        self._getApiClient().getFilePrintInfo(filename, savePrintInfoFunc)

    def savePrintInfo(self, filename, printInfo):
        self.printInfo[filename] = printInfo

    @pyqtProperty("QVariantList", notify=monitorChange)
    def getQueue(self):
        result = []
        i = 0
        for q in self.queue:
            printInfo = self.printInfo.get(q.filePath)
            if printInfo:
                result.append(
                    {"id": q.id, "fileNamePath": q.filePath, "fileExists": q.exists, "fileCheck": q.fileCheck,
                     "first": i == 0, "second": i == 1, "last": i == (len(self.queue) - 1), "printing": q.printing,
                     "plate": printInfo.buildPlateType or None, "extruders": printInfo.extruders or None})
            i = i + 1
        return result

    @pyqtProperty("QVariantList", notify=monitorChange)
    def recentFiles(self):
        result = []
        format = "%Y-%m-%d %H:%M:%S"

        for f in self.files:
            stopTime = datetime.strptime(f.stopTime, format) if f.stopTime else None
            startTime = datetime.strptime(f.startTime, format) if f.startTime else None
            if stopTime and startTime:
                duration = stopTime - startTime
                hours = 24 * duration.days + duration.seconds // 3600
                minutes = (duration.seconds // 60) % 60
                durationString = str(hours) + ":" + ("0" if minutes < 10 else "") + str(minutes)
            else:
                durationString = "N/A"
            plate = ""
            if f.plate:
                plate = f.plate.get('name')
            result.append({
                "fileNamePath": f.fileNamePath,
                "fileExists": f.fileExists,
                "stopTime": f.stopTime,
                "duration": durationString,
                "fractionPrinted": f.fractionPrinted,
                "state": f.state,
                "plate": plate,
                "materials": f.materials
            })
        return result

    @pyqtProperty("QVariantList", notify=monitorChange)
    def machineMemmory(self):
        result = []
        for f in self.memoryFiles:
            if not f.isDirectory:
                type = "file"
            else:
                type = "folder"

            printTimeSeconds = f.printInfo.get("printTime", 0)
            hours = round(printTimeSeconds // 3600)
            minutes = round((printTimeSeconds // 60) % 60)
            printTime = str(hours) + ":" + ("0" if minutes < 10 else "") + str(minutes)

            result.append(
                {"fileNamePath": f.filename, "fileExists": 1, "extruders": f.extruders, "printInfo": f.printInfo, "isDirectory": f.isDirectory,
                 "folderIcon": "folder.svg",
                 "type": type, "printTime": printTime, "creationTime": f.creationTime})
            # TODO: dont send icon with files

        if self._mmsort == 0:
            result.sort(key=lambda i: i.get('creationTime'), reverse=True)
        elif self._mmsort == 1:
            result.sort(key=lambda i: i.get('creationTime'))
        elif self._mmsort == 2:
            result.sort(key=lambda i: i.get('fileNamePath'))
        elif self._mmsort == 3:
            result.sort(key=lambda i: i.get('fileNamePath'), reverse=True)

        return result

    @pyqtProperty(str, notify=monitorChange)
    def timestamp(self):
        if self.status and self.status.timestamp:
            return self.status.timestamp
        return "N/A"

    # NOTE: disabled-function-logging because of "spam"
    @pyqtProperty("QVariant", notify=monitorChange)
    def getChamber(self):
        ret = {
            "hasChamber": 0,
        }
        if self._productInfo and self._productInfo.printer and self._productInfo.printer.get('has_chamber'):
            if self.status and self.status.chamberTemperatures:
                ret = {
                    "hasChamber": 1,
                    "current": self.status.chamberTemperatures.get('current', 'n/a'),
                    "setpoint": self.status.chamberTemperatures.get('setpoint', 'n/a')
                }
            else:
                ret = {
                    "hasChamber": 1,
                    "current": "N/A",
                    "setpoint": "N/A",
                }
        return ret

    @pyqtProperty(str, notify=monitorChange)
    def getStatus(self):
        if self.status and self.getState:
            return self.getState
        return "N/A"

    @pyqtProperty(str, notify=monitorChange)
    def getStatusTranslated(self):
        # + ((OutputDevice.isPrinting || OutputDevice.getState=="PE" || OutputDevice.getState=="PC")? ' ' + Math.round(OutputDevice.getPrintPct) +' %':'')

        # Emergency button was pressed
        if self.status and self.status.machineState == "H":
            return "Emergency stop"

        state = self.states.get(self.getState, "ERROR")
        if self.getState == "P":
            state = state
        if self.isPrinting or self.getState in ["PC", "PE"]:
            state = state + " "+ str(round(self.getPrintPct)) + " %"
        return state

    # NOTE: disabled-function-logging because of "spam"
    @pyqtProperty(str, notify=monitorChange)
    def getState(self):
        # printer status from API - with added states
        if not self.isConnected():
            return "OFF"

        # Emergency button was pressed
        if self.status and self.status.machineState == "H":
            return "H"

        if self.status and self.status.machineState == "I" and self.printerState and not self.printerState.printerEmpty:
            if self._endStatus:
                if self._endStatus.state == 1:
                    return "PF"     # print finished
                elif self._endStatus.state == 2:
                    return "PC"     # print canceled by user
                elif self._endStatus.state == 3:
                    return "PE"     # print error

        if self.status and self.status.machineState:
            return self.status.machineState
        return "?"

    @pyqtProperty(str)
    def getStatusSmallMessage(self):
        # Emergency button was pressed
        if self.status and self.status.machineState == "H":
            return "The printer needs to be restarted"
        elif self.isPrinting:
            return 'Remaining time: '+ self.getRemainingTime


    @pyqtProperty(str, notify=monitorChange)
    def getPrintedFilename(self):
        # TEST
        # return "Madlo_25.ufp"
        if self.status and self.status.fileinfo:
            return self.status.fileinfo['filename']
        return ""

    @pyqtProperty(bool, notify=monitorChange)
    def canPrint(self):
        if not self.status:
            return False
        return self.status and self.getState == "I"

    @pyqtProperty(bool, notify=monitorChange)
    def isPrinting(self):
        # TEST
        # return True
        if not self.status:
            return False
        return self.status and self.getState in ["B", "A", "D", "E", "P", "R", "S"]

    @pyqtProperty(bool, notify=monitorChange)
    def isPaused(self):
        if not self.status:
            return False
        return self.status and self.getState in ["S"]  # TODO: overit stav pauzy s Ondrejem

    @pyqtProperty(str, notify=monitorChange)
    def getMachineModel(self):
        if not self._productInfo:
            return "n/a"
        return self._productInfo.printer['model'] or "N/A"

    @pyqtProperty(str, notify=monitorChange)
    def getMachineSerialNumber(self):
        if not self._productInfo:
            return "n/a"
        return self._productInfo.printer['serial_number'] or "N/A"

    @pyqtProperty(str, notify=monitorChange)
    def getMachineProductCode(self):
        if not self._productInfo:
            return "n/a"
        return self._productInfo.printer['product_code'] or "N/A"

    @pyqtProperty(str, notify=monitorChange)
    def getBackendVersion(self):
        if not self._productInfo:
            return "n/a"
        return self._productInfo.software['backend_version'] or "N/A"

    @pyqtProperty(str, notify=monitorChange)
    def getRemainingTime(self):
        # TODO: convert
        if self.status and self.status.printing and self.status.printing['tl_file']:
            return formatTime(self.status.printing['tl_file'])
        return ""

    @pyqtProperty(int, notify=monitorChange)
    def getPrintPct(self):
        if self.getState in ["PC", "PE"] and self._endStatus:
            return round(self._endStatus.fractionPrinted)

        if self.status and self.status.printing and self.status.printing['fractionPrinted']:
            return round(self.status.printing['fractionPrinted'])
        return 0

    @pyqtProperty(str, notify=monitorChange)
    def getStorageAvailable(self):
        return self._productInfo.freespace or "N/A"

    # @pyqtProperty(str, constant=True)
    @pyqtProperty(str, constant=False)
    def getPrinterName(self):
        return self.printerName

    # @pyqtProperty(str, constant=True)
    @pyqtProperty(str, constant=False)
    def getPrinterModel(self):
        return self.printerModel

    @pyqtProperty("QVariantList", notify=monitorChange)
    def getExtruders(self):
        if not self.status or not self.extruders:
            return []
        result = []
        for extruder in self.extruders:
            e = {
                "id": extruder.id,
                "outputDiameter": extruder.nozzle["outputDiameter"],
                "inputDiameter": extruder.nozzle["inputDiameter"],
                "material": extruder.material["material"] if extruder.material else "?",
                "tempeature": self.status.extrudersTemperatures[extruder.id - 1] or None,
            }
            result.append(e)
        return result

    #        self._responseReceived()
    @pyqtProperty(str, notify=monitorChange)
    def getLastStatus(self):
        return self.lastStatus

    # NOTE: disabled-function-logging because of "spam"
    @pyqtProperty("QVariant", notify=monitorChange)
    def getBed(self):
        result = {
            "temperature": self.status.bedTemperatures.get('current') if self.status and self.status.bedTemperatures else "N/A",
            "plate": self.plate.name if self.plate else "N/A",
        }
        return result

    def _checkStillConnected(self) -> None:
        """Check if we're still connected by comparing the last timestamps for network response and the current time.

        This implementation is similar to the base NetworkedPrinterOutputDevice, but is tweaked slightly.
        Re-connecting is handled automatically by the output device managers in this plugin.
        TODO: it would be nice to have this logic in the managers, but connecting those with signals causes crashes.
        """
        time_since_last_response = time() - self._time_of_last_response
        if time_since_last_response > self._timeout_time:
            Logger.log("d", "It has been %s seconds since the last response for outputdevice %s, so assume a timeout",
                       time_since_last_response, self.key)
            self.setConnectionState(ConnectionState.Closed)
            if self.key in CuraApplication.getInstance().getOutputDeviceManager().getOutputDeviceIds():
                CuraApplication.getInstance().getOutputDeviceManager().removeOutputDevice(self.key)
        elif self.connectionState == ConnectionState.Closed:
            self._reconnectForActiveMachine()

    def _reconnectForActiveMachine(self) -> None:
        """Reconnect for the active output device.

        Does nothing if the device is not meant for the active machine.
        """
        print("_reconnectForActiveMachine")
        print(self.key)

        active_machine = CuraApplication.getInstance().getGlobalContainerStack()
        if not active_machine:
            return

        # Indicate this device is now connected again.
        Logger.log("d", "Reconnecting output device after timeout.")
        self.setConnectionState(ConnectionState.Connected)

        # If the device was already registered we don't need to register it again.
        if self.key in CuraApplication.getInstance().getOutputDeviceManager().getOutputDeviceIds():
            return

        # Try for local network device.
        stored_device_id = active_machine.getMetaDataEntry(self.META_NETWORK_KEY)
        if self.key == stored_device_id:
            CuraApplication.getInstance().getOutputDeviceManager().addOutputDevice(self)

        # Try for cloud device.
        stored_cluster_id = active_machine.getMetaDataEntry(self.META_CLUSTER_ID)
        if self.key == stored_cluster_id:
            CuraApplication.getInstance().getOutputDeviceManager().addOutputDevice(self)

    def _responseReceived(self) -> None:
        self._time_of_last_response = time()

    def _loadMonitorTab(self) -> None:
        """Load Monitor tab QML."""

        plugin_registry = CuraApplication.getInstance().getPluginRegistry()
        if not plugin_registry:
            Logger.log("e", "Could not get plugin registry")
            return
        plugin_path = plugin_registry.getPluginPath("Pragostroj")
        if not plugin_path:
            Logger.log("e", "Could not get plugin path")
            return
        self._monitor_view_qml_path = os.path.join(plugin_path, "resources", "qml", "MonitorStage.qml")

    def _on_api_error(self, error):
        Logger.log("e", str(error))
        # Don't show multiple pupups
        # if not self._popupErrorShow:
        # self._popupError = "Printer server error"
        # self._popupError2 = str(error)

        # self.showPopupError("Printer Error", str(error))

        # self._popupErrorShow = True
        # self.monitorChange.emit()

    # NOTE: disabled-function-logging because of "spam"
    def _getApiClient(self) -> PGApiClient:
        """Get the API client instance."""

        if not self._api:
            self._api = PGApiClient(self.address, on_error=self._on_api_error)
        return self._api

    def _createMonitorViewFromQML(self) -> None:
        # super(PGNetworkedPrinterOutputDevice, self)._createMonitorViewFromQML()
        self._getApiClient().getRecentFiles(lambda files: self._updateRecentFiles(files))
        self._getApiClient().getMachineFiles(lambda files: self._updateMachineFiles(files))
        self._getApiClient().getExtruders(lambda extruders: self._updateExtruders(extruders))
        self.updatePlate()

        if not self._monitor_view_qml_path:
            return

        if self._monitor_item is None:
            self._monitor_item = QtApplication.getInstance().createQmlComponent(self._monitor_view_qml_path, {"OutputDevice": self})

    def _onStageChanged(self):
        if (
            (self.key in CuraApplication.getInstance().getOutputDeviceManager().getOutputDeviceIds())
            and (str(
                CuraApplication.getInstance().getController()._active_stage
            ).startswith("<MonitorStage.MonitorStage.MonitorStage"))
        ):
            self.setPopupMessage()

    # NOTE: disabled-function-logging because of "spam"
    def checkStateTransition(self, lastState, currentState):
        if lastState != self.getState:
            self.setPopupMessage()

            # print removed form printer
            if self._popupInfoShow and currentState == "I" and lastState in ["PC", "PE", "PF"]:
                self._popupInfoShow = False

            # unpaused
            if self._popupInfoShow and currentState != "S" and lastState == "S":
                self._popupInfoShow = False

    def setPopupMessage(self):
        state = self.getState
        if not self._popupInfoShow:
            if (state == "PF"):
                self._popupInfo = "Print finished!"
                self._popupInfo2 = "Please remove the print and confirm removal personally."
                self._popupInfoShow = True
            elif (state == "PC"):
                self._popupInfo = "Print canceled at " + str(round(self._endStatus.fractionPrinted)) + " %"
                self._popupInfo2 = "Please remove the print and confirm removal personally."
                self._popupInfoShow = True
            elif (state == "PE"):
                self._popupInfo = "Print error at " + str(round(self._endStatus.fractionPrinted)) + " %"
                self._popupInfo2 = "Please remove the print and confirm removal personally."
                self._popupInfoShow = True
            elif (self.isPaused):
                self._popupInfo = "Print is paused."
                self._popupInfo2 = ""
                self._popupInfoShow = True

    @pyqtSlot(name="hidePopupInfo")
    def hidePopupInfo(self):
        self._popupInfoShow = False

    @pyqtProperty(bool, notify=monitorChange)
    def popupInfo(self):
        return self._popupInfoShow

    @pyqtProperty(str, notify=monitorChange)
    def popupInfoText(self):
        return self._popupInfo

    @pyqtProperty(str, notify=monitorChange)
    def popupInfoText2(self):
        return self._popupInfo2

    @pyqtProperty("QVariantMap", notify=monitorChange)
    def errorPopup(self):
        return self._errorPopup

    def _show_error_popup(self, error_line_1, error_line_2):
        self._errorPopup = {
            'errorLine1': error_line_1,
            'errorLine2': error_line_2,
            'show': True,
        }

    def _hide_error_popup(self):
        self._errorPopup = {
            'errorLine1': '',
            'errorLine2': '',
            'show': False,
        }

    @pyqtSlot(name="hideErrorPopup")
    def hideErrorPopup(self):
        self._hide_error_popup()

    # def showPopupError(self, err_text1, err_text2):
    #     # self._popupError = err_text1
    #     # self._popupError2 = err_text2
    #     # self._popupErrorShow = True
    #     # self.monitorChange.emit()
    #     p_stage = CuraApplication.getInstance().getController().getStage('Pragostroj')
    #     p_stage.showPopupError(err_text1, err_text2)

    # @pyqtSlot(name="hidePopupError")
    # def hidePopupError(self):
    #     print('')
    #     print('')
    #     print('---HIDE PopUp Error---')
    #     print('')
    #     self._popupErrorShow = False

    # @pyqtProperty(bool, notify=monitorChange)
    # def popupError(self):
    #     return self._popupErrorShow

    # @pyqtProperty(str, notify=monitorChange)
    # def popupErrorText(self):
    #     return self._popupError

    # @pyqtProperty(str, notify=monitorChange)
    # def popupErrorText2(self):
    #     return self._popupError2

    @pyqtSlot(str, name="delete")
    def delete(self, fileNamePath: str):
        self._getApiClient().delete(lambda res: self._machineMemoryOperation(res), fileNamePath, lambda res: self._printError(res))

    @pyqtSlot(name="deleteSelected")
    def deleteSelected(self):
        fileList = []
        for file in self.selectedFiles:
            fileList.append(file)
        self.deleteFiles(None, fileList)

    @pyqtSlot(name="deleteAll")
    def deleteAll(self):
        fileList = []
        for machineMemoryRecord in self.machineMemmory:
            fileList.append(machineMemoryRecord['fileNamePath'])
        self.deleteFiles(None, fileList)

    def deleteFiles(self, response=None, fileList=[]):
        if (len(fileList)):
            self._getApiClient().delete(lambda res: self.deleteFiles(res, fileList[1:]), fileList[0], lambda res: self._printError(res))
        else:
            self.updateMachineMemory()

    @pyqtSlot(str, name="printFile")
    def printFile(self, fileNamePath: str):
        logger.debug('--------PRINT FILE----------')
        self._getApiClient().checkFile(fileNamePath, lambda res: self._fileChecked(res, fileNamePath))

    def _fileChecked(self, result: PGCheckFile, fileNamePath: str):
        logger.debug('--------FILE CHECKED----------')
        if result.conflictTexts:
            self._currentPrintConflicts = result.conflictTexts
            self._currentPrintFile = fileNamePath
            # self.conflictsPopup['conflicts'] = result.conflictTexts
            # self.conflictsPopup['printFile'] = fileNamePath
            # self.conflictsPopup['show'] = True
            # self._conflicts_popup = ConflictsPopup(True, fileNamePath, result.conflictTexts)
            self.show_conflicts_popup(fileNamePath, result.conflictTexts)
        else:
            self._getApiClient().printFile(
                fileNamePath,
                on_finished=(lambda res: self._printOperationResult(res)),
                # lambda res: self._printFileError(res)
                on_error=(self._showPrintErrorFromResponse)
    )

    @pyqtProperty("QVariantList", notify=monitorChange)
    def printConflicts(self):
        return self._currentPrintConflicts

    # TODO: Currently, the popup (forcePrint/dontPrint) is shown based on this property
    # @pyqtProperty(str, notify=monitorChange)
    # def currentPrintFile(self):
    #     return self._currentPrintFile

    # @pyqtProperty(bool, notify=monitorChange)
    # def conflictsPopupShow(self):
    #     return self._conflictsPopupShow
    #     # return self._conflictsPopup['show']

    # @pyqtProperty(str, notify=monitorChange)
    # def conflictsPopupPrintFile(self):
    #     # return self._conflictsPopupPrintFile
    #     return self._conflictsPopup['printFile']

    # @pyqtProperty("QVariantList", notify=monitorChange)
    # def conflictsPopupConflicts(self):
    #     # return self._conflictsPopupConflicts
    #     return self._conflictsPopup['conflicts'] or []

    # TODO: Make this working, instead of separated properties
    @pyqtProperty("QVariantMap", notify=monitorChange)
    def conflictsPopup(self):
        return self._conflictsPopup

    def show_conflicts_popup(self, print_file_name, conflicts):
        # self._conflictsPopup['printFile'] = print_file_name
        # self._conflictsPopup['conflicts'] = conflicts
        # self._conflictsPopup['show'] = True
        # self._conflictsPopupShow = True
        logger.debug('-----------__SHOW CONFLICTS----------')
        self._conflictsPopup = {
            'show': True,
            'printFile': print_file_name,
            'conflicts': conflicts,
        }

    def hide_conflicts_popup(self):
        # self._conflictsPopupShow = False
        # self._conflictsPopup['conflicts'] = ''
        # self._conflictsPopup['printFile'] = ''
        # self._conflictsPopup['show'] = False
        self._conflictsPopup = {
            'show': False,
            'printFile': '',
            'conflicts': []
        }

    @pyqtSlot(name="forcePrint")
    def forcePrint(self):
        self._getApiClient().printFileForce(
            self._currentPrintFile,
            lambda res: self._printOperationResult(res),
            lambda res: self._printOperationResult(res)
        )
        self._currentPrintFile = None
        # self._conflicts_popup = ConflictsPopup(False, '', None)
        self.hide_conflicts_popup()

    @pyqtSlot(name="dontPrint")
    def dontPrint(self):
        # self._currentPrintFile = None
        # self._currentPrintConflicts = []
        # self._conflicts_popup = ConflictsPopup(False, '', None)
        # self.conflictsPopup['conflicts'] = ''
        # self.conflictsPopup['printFile'] = ''
        # self.conflictsPopup['show'] = False
        self.hide_conflicts_popup()

    @pyqtSlot(name="pausePrint")
    def pausePrint(self):
        self._getApiClient().pausePrint(lambda res: self._queueOperationResult(res), lambda res: self._printError(res))

    @pyqtSlot(name="resumePrint")
    def resumePrint(self):
        self._getApiClient().resumePrint(lambda res: self._queueOperationResult(res), lambda res: self._printError(res))

    @pyqtSlot(name="stopPrint")
    def stopPrint(self):
        self._getApiClient().cancelPrint(lambda res: self._queueOperationResult(res), lambda res: self._printError(res))

    def _moved(self, result):
        self.updateQueue()

    def _moveError(self, result):
        self.updateQueue()

    def _printError(self, printResult):
        self._on_api_error(printResult)
        self.lastStatus = printResult.type
        self._showErrorFromResponse(printResult)
        # self._show_error_popup(printResult.check, printResult.checkText)
        # self.updateQueue()

    def _printOperationResult(self, printResult: PGPrintResult):
        # logger.debug(f'Response: {printResult}, {printResult.type}, {printResult.error}')
        self.lastStatus = printResult.type
        self.updateQueue()

    # def _printFileError(self, printResult: PGPrintResult):
    #     logger.debug(f'ErrorResponse: {printResult}')
    #     self._show_error_popup(printResult.check, printResult.checkText)
    #     # self.lastStatus = printResult.type
    #     self.updateQueue()

    def _showErrorFromResponse(self, printResult: PGPrintResult):
        logger.debug(f'ErrorResponse: {printResult}')
        # self._show_error_popup(printResult.textType, printResult.textReason)
        self._show_error_popup(printResult.textType, printResult.reason)
        # self.lastStatus = printResult.type
        self.updateQueue()

    def _showCheckErrorFromResponse(self, printResult: PGPrintResult):
        logger.debug(f'ErrorResponse: {printResult}')
        # self._show_error_popup(printResult.check, printResult.checkText)
        conflict_texts = '\n'.join(printResult.conflictTexts)
        self._show_error_popup("", conflict_texts)
        # self.lastStatus = printResult.type
        self.updateQueue()

    def _showPrintErrorFromResponse(self, printResult):
        logger.debug(f'ErrorResponse: {printResult}')
        # FIXME: This is a dirty solution for different schemas per different status_codes
        #        Current implementation of API client doesn't support multiple schemas per endpoint
        if printResult.text:
            self._show_error_popup("", printResult.text)
        else:
            # NOTE: Yep, another thing is, that there are messages placed in different
            #       fields, based on the tipe of message
            #       e.g. DOORS_ARE_OPEN has a text in checkText
            if printResult.conflictTexts:
                conflict_texts = '\n'.join(printResult.conflictTexts)
                self._show_error_popup("", conflict_texts)
            else:
                self._show_error_popup("", printResult.checkText)
        # self.lastStatus = printResult.type
        self.updateQueue()

    def _queueOperationResult(self, printResult: PGPrintResult):
        self.lastStatus = printResult.type
        self.updateQueue()

    def _machineMemoryOperation(self, printResult: PGPrintResult):
        self.lastStatus = printResult.type
        self.updateMachineMemory()

    @pyqtProperty(str, notify=monitorChange)
    def pragostroj(self):
        return "pragostroj " + self.device_id

    def updatePlate(self):
        self._getApiClient().getPlate(lambda plate: self.updatePlateResponse(plate), lambda res: self.updatePlateResponseError(res))

    # NOTE: disabled-function-logging because of "spam"
    def updatePlateResponse(self, plate: PGPlate):
        self.plate = plate

    def updatePlateResponseError(self, response):
        self.plate = None

    # NOTE: disabled-function-logging because of "spam"
    def updatePrinterState(self):
        self._getApiClient().getPrinterState(lambda res: self.updatePrinterStateResponse(res), lambda res: self.updatePrinterStateResponseError(res))

    # NOTE: disabled-function-logging because of "spam"
    def updatePrinterStateResponse(self, printerState: PGPrinterState):
        lastState = self.getState
        self.printerState = printerState
        self.checkStateTransition(lastState, self.getState)

    def updatePrinterStateResponseError(self, response):
        self.printerState = None

    @pyqtSlot(str, bool, name="selectFile")
    def selectFile(self, filename: str, selected: bool):
        self.selectedFiles[filename] = selected
        print(self.selectedFiles)

    @pyqtProperty(int, notify=monitorChange)
    def getSort(self):
        return self._mmsort

    @pyqtSlot(int, name="setSort")
    def setSort(self, sort: int):
        self._mmsort = sort

    # NOTE: disabled-function-logging because of "spam"
    def updateEndInfo(self):
        self._getApiClient().getEndInfo(lambda res: self._endInfoResponse(res))

    # NOTE: disabled-function-logging because of "spam"
    def _endInfoResponse(self, endInfo: PGEndInfo):
        self._endStatus = endInfo

    # device is added in cura
    def setInCura(self, inCura: bool):
        self._isInCura = inCura
