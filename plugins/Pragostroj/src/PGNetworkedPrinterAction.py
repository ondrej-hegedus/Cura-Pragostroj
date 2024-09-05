# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import logging
from typing import Optional, cast

from PyQt6.QtCore import pyqtSlot, pyqtSignal, pyqtProperty, QObject

from UM import i18nCatalog
from cura.CuraApplication import CuraApplication
from cura.MachineAction import MachineAction

from Pragostroj.src.PGOutputDevicePlugin import PGOutputDevicePlugin
from Pragostroj.src.PGNetworkedPrinterOutputDevice import PGNetworkedPrinterOutputDevice

from UM.Logger import Logger

I18N_CATALOG = i18nCatalog("cura")

logger = logging.getLogger(__name__)


class PGNetworkedPrinterAction(MachineAction):
    """Machine action that allows to connect the active machine to a networked devices.

    TODO: in the future this should be part of the new discovery workflow baked into Cura.
    """

    # Signal emitted when discovered devices have changed.
    discoveredDevicesChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__("DiscoverPGAction", I18N_CATALOG.i18nc("@action", "Connect via Network"))
        self._qml_url = "resources/qml/DiscoverUM3Action.qml"
        self._network_plugin = None  # type: Optional[PGOutputDevicePlugin]

    @property
    def _networkPlugin(self) -> PGOutputDevicePlugin:
        """Get the network manager from the plugin."""

        if not self._network_plugin:
            output_device_manager = CuraApplication.getInstance().getOutputDeviceManager()
            network_plugin = output_device_manager.getOutputDevicePlugin("Pragostroj")
            self._network_plugin = cast(PGOutputDevicePlugin, network_plugin)
        return self._network_plugin

    @pyqtSlot(QObject, name="associateActiveMachineWithPrinterDevice")
    def associateActiveMachineWithPrinterDevice(self, device: PGNetworkedPrinterOutputDevice) -> None:
        """Connect a device selected in the list with the active machine."""
        self._networkPlugin.associateActiveMachineWithPrinterDevice(device)

    @pyqtProperty("QVariantList", notify=discoveredDevicesChanged)
    def foundDevices(self):
        """Get the devices discovered in the local network sorted by name."""
        discovered_devices = list(self._networkPlugin.getDiscoveredDevices().values())
        discovered_devices.sort(key=lambda d: d.name)

        return discovered_devices

    def _createViewFromQML(self) -> None:
        super()._createViewFromQML()
