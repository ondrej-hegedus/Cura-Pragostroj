# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject


class PGCheckFile(QObject):
    """Class representing recent file"""

    def __init__(self, type="", conflicts=[], conflictTexts=[],  **kwargs) -> None:
        self.conflicts = conflicts
        self.conflictTexts = conflictTexts
        self.type = type
