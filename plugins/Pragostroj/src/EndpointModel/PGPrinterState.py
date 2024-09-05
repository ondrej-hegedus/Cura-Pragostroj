# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject


class PGPrinterState(QObject):
    """Class representing recent file"""

    def __init__(self, printerEmpty: bool, ready: bool, **kwargs) -> None:
        self.printerEmpty = printerEmpty
        self.ready = ready
