# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import asyncio
import socket
import ipaddress
import logging
from typing import Dict, Optional, Callable, List
from multiprocessing.pool import ThreadPool

import ifaddr
from PyQt6.QtCore import pyqtSlot

from UM import i18nCatalog
from UM.Logger import Logger
from UM.Signal import Signal
from UM.Version import Version
from UM.OutputDevice.OutputDeviceManager import ManualDeviceAdditionAttempt
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin

from cura.Settings.CuraContainerRegistry import CuraContainerRegistry
from cura.CuraApplication import CuraApplication
from cura.Settings.CuraStackBuilder import CuraStackBuilder
from cura.Settings.GlobalStack import GlobalStack

from Pragostroj.src.PGApiClient import PGApiClient
from Pragostroj.src.PGNetworkedPrinterOutputDevice import PGNetworkedPrinterOutputDevice
from Pragostroj.src.EndpointModel.PGProductInfo import PGProductInfo


# import PluginRegistry

I18N_CATALOG = i18nCatalog("cura")


logger = logging.getLogger(__name__)


class PGOutputDevicePlugin(OutputDevicePlugin):
    """
    from documentation in UM.OutputDevice.OutputDeviceManager:

      OutputDevicePlugin and OutputDevice creation/removal
    ----------------------------------------------------

    Each instance of an OutputDevicePlugin is meant as an OutputDevice creation object.
    Subclasses of OutputDevicePlugin are meant to perform device lookup and listening
    for events like device hot-plugging. When a new device has been detected, the plugin
    class should create an instance of an OutputDevice subclass and add it to this
    manager class using addOutputDevice(). Similarly, if a device has been removed the
    OutputDevicePlugin is expected to call removeOutputDevice() to remove the proper
    device.
    """

    META_NETWORK_KEY = "pg_network_key"

    MANUAL_DEVICES_PREFERENCE_KEY = "pragostroj/manual_instances"
    MIN_SUPPORTED_CLUSTER_VERSION = Version("4.0.0")

    # The translation catalog for this device.
    I18N_CATALOG = i18nCatalog("cura")

    # Signal emitted when the list of discovered devices changed.
    discoveredDevicesChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._devices = []

        # Persistent? dict containing the networked clusters.
        self._discovered_devices = {}  # type: Dict[str, PGNetworkedPrinterOutputDevice]
        self._output_device_manager = CuraApplication.getInstance().getOutputDeviceManager()
        self.discoveredDevicesChanged.connect(self.discoveredDevicesChanged)
        CuraApplication.getInstance().globalContainerStackChanged.connect(self.refreshConnections)

        # Hook up ZeroConf client.
        # self._zero_conf_client = ZeroConfClient()
        # self._zero_conf_client.addedNetworkCluster.connect(self._onDeviceDiscovered)
        # self._zero_conf_client.removedNetworkCluster.connect(self._onDiscoveredDeviceRemoved)
        # CuraApplication.getInstance().getOutputDeviceManager().outputDevicesChanged.connect(self._onOutputDevicesChanged)
        self.start()

    # TODO: find out when is start() called and when startDiscovery.
    #       Move _get_priters_addresses and start_async_discovery appropriately, based on that.
    def startDiscovery(self):
        """Restart discovery on the local network."""

        self.stop()
        self.start()

    def start(self) -> None:
        """Start the network discovery."""
        for ip_addr in self._get_priters_addresses():
            # TODO: It should be done not by adding manual device, but by returning list of addreses, not?
            self.addManualDevice(ip_addr)

        for ip_addr in self._discover_network_printers():
            self.addManualDevice(ip_addr)

    def stop(self) -> None:
        """Stop network discovery and clean up discovered devices."""

        # self._zero_conf_client.stop()
        # for instance_name in list(self._discovered_devices):
        #    self._onDiscoveredDeviceRemoved(instance_name)

    def canAddManualDevice(self, address: str = "") -> ManualDeviceAdditionAttempt:
        # TODO: Carefull about this
        """Indicate that this plugin supports adding networked printers manually."""

        return ManualDeviceAdditionAttempt.PRIORITY

    def addManualDevice(self, address: str, callback: Optional[Callable[[bool, str], None]] = None) -> None:
        """Add a manual device by the specified address."""
        logger.debug(f'----ADDING-MANUAL {self}: {address}')
        api_client = PGApiClient(address, lambda error: Logger.log("e", str(error)))
        api_client.getProductInfo(lambda status: self._onCheckManualDeviceResponse(address, status, callback))

    def removeManualDevice(self, key: str, address: Optional[str] = None) -> None:
        """Remove a manual device by either the name and/or the specified address."""

        if key not in self._discovered_devices and address is not None:
            key = "manual:{}".format(address)

        # TODO: Is there a need to distinguish between discoveded and manualy added devices?
        if key in self._discovered_devices:
            address = address or self._discovered_devices[key].ipAddress
            self._onDiscoveredDeviceRemoved(key)

        if address in self._getStoredManualAddresses():
            self._removeStoredManualAddress(address)

    def refreshConnections(self) -> None:
        """Force reset all network device connections."""

        self._connectToActiveMachine()

    def _onOutputDevicesChanged(self):
        # WIP:
        return
        print("_onOutputDevicesChanged")

        pgDevices = []
        machine_stacks = CuraContainerRegistry.getInstance().findContainerStacksMetadata(type="machine")
        for ms in machine_stacks:
            if 'pg_network_key' in ms:
                pgDevices.append(ms.get('pg_network_key'))

        print("pgDevices")
        print(pgDevices)

        for discoveredDevice in CuraApplication.getInstance().getDiscoveredPrintersModel().discoveredPrinters:
            device = discoveredDevice.device
            if isinstance(device, PGNetworkedPrinterOutputDevice):
                print("device.device_id")
                print(device.device_id)
                if device.device_id in pgDevices:
                    print("activated")
                    device.setInCura(True)
                else:
                    print("detivated")
                    device.setInCura(False)

    def _get_priters_addresses(self):
        # Manually added adresses
        # self._zero_conf_client.start()
        addresses = self._getStoredManualAddresses()
        addresses = [a for a in addresses if a]

        return addresses

    # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    def _get_active_nic_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))  # any IP adress
            host_ip = s.getsockname()[0]  # get the local address to which the socket was connected to on previous line
        except Exception:
            return None
        finally:
            s.close()
        return host_ip

        # Another Alternative to get IP address
        # import socket
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(("8.8.8.8", 80))
        # print(s.getsockname()[0])

    @staticmethod
    def _check_port(ip_addr, port):
        logger.debug(f'checking: {ip_addr}')
        # return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip_addr, port))
        sock.close()
        if result == 0:
            return ip_addr
        return None

    # def _start_async_discovery(self):
    def _discover_network_printers(self):
        host_ip = self._get_active_nic_ip()
        found_adapters = list(filter(
            lambda adapter: host_ip in [ip.ip for ip in adapter.ips],
            ifaddr.get_adapters()
        ))

        if len(found_adapters) != 1:
            logger.info(f'Cannot find network interface for printers discovery. Found adapters: {found_adapters}')
            return

        main_adapter = found_adapters[0]
        host_ip_obj = [ip for ip in main_adapter.ips if ip.ip == host_ip][0]
        main_network_prefix = host_ip_obj.network_prefix

        # FIXME: for testing on VPN I put here static mask
        main_network_prefix = 24

        all_ips_in_network = [
            str(ip) for ip in ipaddress.ip_network('{}/{}'.format(host_ip, main_network_prefix), strict=False)
        ]

        pool = ThreadPool(100)

        results = pool.starmap(self._check_port, [(ip_addr, 8080) for ip_addr in all_ips_in_network])
        pool.close()
        pool.join()
        return list(filter(lambda ip: bool(ip), results))

    def _connectToActiveMachine(self) -> None:
        """Callback for when the active machine was changed by the user or a new remote cluster was found."""
        active_machine = CuraApplication.getInstance().getGlobalContainerStack()
        output_device_manager = CuraApplication.getInstance().getOutputDeviceManager()

        # TODO:
        # The issue seems to be that the discovered machine/device? doesn't become active
        if not active_machine:
            # logger.debug('--NOT ACTIVE--')
            return
        # logger.debug('--ACTIVE--')
        # logger.debug(active_machine)
        # logger.debug('')

        stored_device_id = active_machine.getMetaDataEntry(self.META_NETWORK_KEY)
        for device in self._discovered_devices.values():
            if device.key == stored_device_id:
                # Connect to it if the stored key matches.
                self._connectToOutputDevice(device, active_machine)
            elif device.key in output_device_manager.getOutputDeviceIds():
                # Remove device if it is not meant for the active machine.
                output_device_manager.removeOutputDevice(device.key)

    def _onCheckManualDeviceResponse(self, address: str, productInfo: PGProductInfo,
                                     callback: Optional[Callable[[bool, str], None]] = None) -> None:
        """Callback for when a manual device check request was responded to."""

        extruderCount = productInfo.printer["extruder_slots"] or 1
        # chamber C
        # bed B
        printerType = "pragostroj_" + str(extruderCount)
        if productInfo.printer["has_chamber"]:
            printerType = printerType + "hc"

        self._onDeviceDiscovered(
            "manual:{}".format(address),
            address,
            {
                b"name": productInfo.printerName.encode(),
                b"address": address.encode(),
                b"printer_type": printerType.encode("utf-8"),
                b"manual": b"true",
                b"firmware_version": productInfo.software["backend_version"].encode(),
                b"frontend_version": productInfo.software["frontend_version"].encode(),
                b"model": productInfo.printer["model"].encode(),
            },
            productInfo
        )
        self._storeManualAddress(address)
        if callback is not None:
            CuraApplication.getInstance().callLater(callback, True, address)

    def _onDiscoveredDeviceRemoved(self, device_id: str) -> None:
        """Remove a device."""

        device = self._discovered_devices.pop(device_id, None)  # type: Optional[LocalClusterOutputDevice]
        if not device:
            return
        device.close()
        CuraApplication.getInstance().getDiscoveredPrintersModel().removeDiscoveredPrinter(device.address)
        self.discoveredDevicesChanged.emit()

    def _createMachineFromDiscoveredDevice(self, device_id: str) -> None:
        """Create a machine instance based on the discovered network printer."""

        device = self._discovered_devices.get(device_id)
        if device is None:
            return

        machine_stacks = CuraContainerRegistry.getInstance().findContainerStacksMetadata(type="machine")
        for ms in machine_stacks:
            if ms.get('pg_network_key', '') == device.key:
                # this device is already added
                return

        # Create a new machine and activate it.
        # We do not use use MachineManager.addMachine here because we need to set the network key before activating it.
        # If we do not do this the auto-pairing with the cloudq-equivalent device will not work.
        new_machine = CuraStackBuilder.createMachine(device.name, device.printerType.lower())

        if not new_machine:
            Logger.log("e", "Failed creating a new machine")
            return
        new_machine.setMetaDataEntry(self.META_NETWORK_KEY, device.key)
        CuraApplication.getInstance().getMachineManager().setActiveMachine(new_machine.getId())
        self._connectToOutputDevice(device, new_machine)

    def _storeManualAddress(self, address: str) -> None:
        """Add an address to the stored preferences."""

        stored_addresses = self._getStoredManualAddresses()
        if address in stored_addresses:
            return  # Prevent duplicates.
        stored_addresses.append(address)
        new_value = ",".join(stored_addresses)
        CuraApplication.getInstance().getPreferences().setValue(self.MANUAL_DEVICES_PREFERENCE_KEY, new_value)

    def _removeStoredManualAddress(self, address: str) -> None:
        """Remove an address from the stored preferences."""

        stored_addresses = self._getStoredManualAddresses()
        try:
            stored_addresses.remove(address)  # Can throw a ValueError
            new_value = ",".join(stored_addresses)
            CuraApplication.getInstance().getPreferences().setValue(self.MANUAL_DEVICES_PREFERENCE_KEY, new_value)
        except ValueError:
            Logger.log("w", "Could not remove address from stored_addresses, it was not there")

    def _getStoredManualAddresses(self) -> List[str]:
        """Load the user-configured manual devices from Cura preferences."""

        preferences = CuraApplication.getInstance().getPreferences()
        preferences.addPreference(self.MANUAL_DEVICES_PREFERENCE_KEY, "")
        manual_instances = preferences.getValue(self.MANUAL_DEVICES_PREFERENCE_KEY).split(",")
        return manual_instances

    def _onDeviceDiscovered(self, key: str, address: str, properties: Dict[bytes, bytes], productInfo: PGProductInfo) -> None:
        """Add a new device."""
        device = PGNetworkedPrinterOutputDevice(key, address, properties, productInfo)

        discovered_printers_model = CuraApplication.getInstance().getDiscoveredPrintersModel()
        if address in list(discovered_printers_model.discoveredPrintersByAddress.keys()):
            # TODO: This may be unnecesary, and unnecesarily trigerring actions after device update

            # The printer was already added, we just update the available data.
            discovered_printers_model.updateDiscoveredPrinter(
                ip_address=address,
                name=device.getName(),
                machine_type=device.printerType
            )
        else:
            # The printer was not added yet so let's do that.
            discovered_printers_model.addDiscoveredPrinter(
                ip_address=address,
                key=device.getId(),
                name=device.getName(),
                create_callback=self._createMachineFromDiscoveredDevice,
                machine_type=device.printerType,
                device=device
            )
        self._discovered_devices[device.getId()] = device
        self.discoveredDevicesChanged.emit()
        # TODO: This may be unnecesary
        self._connectToActiveMachine()

    def _connectToOutputDevice(self, device: PGNetworkedPrinterOutputDevice, machine: GlobalStack) -> None:
        """Add a device to the current active machine."""
        machine.setName(device.name)
        machine.setMetaDataEntry(self.META_NETWORK_KEY, device.key)
        machine.setMetaDataEntry("group_name", device.name)
        machine.addConfiguredConnectionType(device.connectionType.value)

        output_device_manager = CuraApplication.getInstance().getOutputDeviceManager()

        if not device.isConnected():
            device.connect()
            device.setInCura(True)

        if device.key not in output_device_manager.getOutputDeviceIds():
            # TODO: It seems wierd, it's here
            output_device_manager.addOutputDevice(device)

    @pyqtSlot(str, result=str)
    def getProperty(self, key: str) -> str:
        bytes_key = key.encode("utf-8")
        if bytes_key in self._properties:
            return self._properties.get(bytes_key, b"").decode("utf-8")
        else:
            return ""
