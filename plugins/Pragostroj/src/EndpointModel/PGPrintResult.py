# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject


class PGPrintResult(QObject):
    """Class representing recent file"""

    def __init__(
            self,
            type="",
            error="",
            check="",
            checkText="",
            conflicts=[],
            conflictTexts=[],
            filePath="",
            text="",
            **kwargs
    ) -> None:
        self.type = type
        self.error = error

        # NOTE: For some reason, printer returns DOORS_ARE_OPEN as a conflict, not as an error structure
        self.check = check
        self.checkText = checkText
        self.conflicts = conflicts
        self.conflictTexts = conflictTexts
        self.type = type

        # There are a fields of all the possible schemas for this endpoint
        # For any status code.
        #  printFile returns 406 and 409 in different schemas
        self.filePath = filePath
        self.text = text
