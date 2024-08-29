# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any

from Pragostroj.src.EndpointModel.PGBaseModel import PGBaseModel


class PGProductInfo(PGBaseModel):
    """Class representing the system status of a printer."""

    def __init__(self, printerName: str, printer: Dict[str, Any], software: Dict[str, Any], freespace: str, **kwargs) -> None:
        self.printer = printer
        self.software = software
        self.freespace = freespace
        self.printerName = printerName
        super().__init__(**kwargs)
