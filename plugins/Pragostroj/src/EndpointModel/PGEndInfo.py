# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject


class PGEndInfo(QObject):
    """Class representing recent file"""

    def __init__(self, id=0, state=0, fileNamePath='', fractionPrinted=0, **kwargs) -> None:
        self.id = id
        self.state = state
        self.fileNamePath = fileNamePath
        self.fractionPrinted = fractionPrinted
