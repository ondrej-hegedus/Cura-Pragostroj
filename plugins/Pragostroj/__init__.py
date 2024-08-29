# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import logging
from Pragostroj.src import PGOutputDevicePlugin
from Pragostroj.src import PGNetworkedPrinterAction
from Pragostroj.src import PragostrojList
from Pragostroj.src import PragostrojStage


logger = logging.getLogger(__name__)

def getMetaData():
    return {}
    # TODO: supported_sdk_versions - not so specific
    # return {
    #     "plugin": {
    #         "name": "Pragostroj",
    #         "author": "Ondrej Hegedus",
    #         "version": "0.1",
    #         "description": "Pragostroj plugin",
    #         "supported_sdk_versions": ["5.0", "5.1", "5.2"]
    #     }
    # }
def register(app):
    logger.debug('---------------------------------')
    logger.debug('register')
    return {
        "output_device": PGOutputDevicePlugin.PGOutputDevicePlugin(),
        "machine_action": PGNetworkedPrinterAction.PGNetworkedPrinterAction(),
        "extension": PragostrojList.PragostrojList(),
        "stage": PragostrojStage.PragostrojStage(),
    }
