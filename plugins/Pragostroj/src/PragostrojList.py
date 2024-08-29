from UM.Application import Application  # To listen to the event of creating the main window, and get the QML engine.
from UM.Extension import Extension  # The PluginObject we're going to extend.
from UM.Logger import Logger  # Adding messages to the log.
from cura.CuraApplication import CuraApplication


import logging
logger = logging.getLogger(__name__)


class PragostrojList(Extension):

    def __init__(self):
        super().__init__()
        self.setMenuName("Pragostroj list")
        self.addMenuItem("Show list", self.showList)

    def showList(self):
        CuraApplication.getInstance().getController().setActiveStage("Pragostroj")
