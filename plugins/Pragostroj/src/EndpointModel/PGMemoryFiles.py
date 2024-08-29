# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any

from PyQt6.QtCore import pyqtProperty, QObject


class PGMemoryFiles(QObject):
    """Class representing machine memory file"""

    def __init__(self, filename: str, isDirectory: bool, printInfo: Dict[str, Any], creationTime: str, **kwargs) -> None:
        self.fileNamePath = filename
        self.isDirectory = isDirectory
        self.printInfo = printInfo
        self.extruders = printInfo.get("extruders") if printInfo else None
        self.creationTime = creationTime

    @pyqtProperty(str)
    def filename(self):
        return self.fileNamePath
