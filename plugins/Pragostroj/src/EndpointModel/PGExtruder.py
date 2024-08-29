# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any

from Pragostroj.src.EndpointModel.PGBaseModel import PGBaseModel


class PGExtruder(PGBaseModel):
    """Class representing the system status of a printer."""

    def __init__(self, id: int, material: Dict[str, Any], nozzle: Dict[str, Any], extruderType: Dict[str, Any], **kwargs) -> None:
        self.id = id
        self.material = material
        self.nozzle = nozzle
        self.extruderType = extruderType
        super().__init__(**kwargs)
