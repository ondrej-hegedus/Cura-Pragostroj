# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import QObject


class PGPrintOperationResult(QObject):
    """Class representing recent file"""

    # def __init__(self, type="", error="", reason="", internal_message="", **kwargs) -> None:
    #     # super().__init__(**kwargs)
    #     super().__init__()
    #     self.type = type
    #     self.error = error
    #     self.reason = reason
    #     self.internal_message = internal_message

    def __init__(self, type="", textType="", reason="", textReason="", internal_message="", **kwargs) -> None:
        # super().__init__(**kwargs)
        super().__init__()
        self.type = type
        self.textType = textType
        self.reason = reason
        self.textReason = textReason
        self.internal_message = internal_message
