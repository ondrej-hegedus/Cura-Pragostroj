# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The LinearAdvanceSettingPlugin is released under the terms of the AGPLv3 or higher.

from . import PragostrojLinearAdvanceSettingPlugin


def getMetaData():
    return {}


def register(app):
    return {"extension": PragostrojLinearAdvanceSettingPlugin.PragostrojLinearAdvanceSettingPlugin()}
