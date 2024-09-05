# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import pyqtProperty, QObject


class PGFile(QObject):
    """Class representing recent file"""

    def __init__(self, filename: str, **kwargs) -> None:
        self.fileNamePath = filename

    @pyqtProperty(str)
    def filename(self):
        return self.fileNamePath
