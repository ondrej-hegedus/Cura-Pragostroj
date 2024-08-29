# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any

from Pragostroj.src.EndpointModel.PGBaseModel import PGBaseModel


class PGPrintInfo(PGBaseModel):
    """Class representing the system status of a printer."""

    def __init__(self, buildPlateType: str, extruders: Dict[str, Any], **kwargs) -> None:
        self.buildPlateType = buildPlateType
        self.extruders = extruders
        super().__init__(**kwargs)
