# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any

from Pragostroj.src.EndpointModel.PGBaseModel import PGBaseModel


class PGPrinterStatus(PGBaseModel):
    """Class representing the system status of a printer."""

    def __init__(self, machineState: str, bedTemperatures: Dict[str, Any], extrudersTemperatures: Dict[str, Any], chamberTemperatures: Dict[str, Any], printing: Dict[str, Any], timestamp: str, fileinfo: Dict[str, Any], **kwargs) -> None:
        self.machineState = machineState
        self.bedTemperatures = bedTemperatures
        self.extrudersTemperatures = extrudersTemperatures
        self.chamberTemperatures = chamberTemperatures
        self.timestamp = timestamp
        self.printing = printing
        self.fileinfo = fileinfo
        super().__init__(**kwargs)
