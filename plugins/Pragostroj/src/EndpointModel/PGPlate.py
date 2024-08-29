# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject


class PGPlate(QObject):
    """Class representing recent file"""

    def __init__(self, id="", pcn="", name="", **kwargs) -> None:
        self.id = id
        self.pcn = pcn
        self.name = name
