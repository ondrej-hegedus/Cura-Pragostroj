# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any
from PyQt6.QtCore import pyqtProperty, QObject


class PGRecentFile(QObject):
    """Class representing recent file"""

    def __init__(self, state: int, fileNamePath: str, fileExists: bool, startTime: str, stopTime: str, fractionPrinted: float, plate: Dict[str, Any], **kwargs) -> None:
        # material0: Dict[str, Any], material1: Dict[str, Any], material2: Dict[str, Any], material3: Dict[str, Any],
        self.state = state
        self.fileNamePath = fileNamePath
        self.fileExists = fileExists
        self.stopTime = stopTime
        self.startTime = startTime
        self.fractionPrinted = fractionPrinted
        self.materials = []
        self.plate = plate

        for m in range(0, 3):
            if kwargs.get("material" + str(m)):
                mat = kwargs.get("material" + str(m))
                mat['number'] = m
                self.materials.append(mat)

    @pyqtProperty(str)
    def filename(self):
        return self.fileNamePath
