# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The LinearAdvanceSettingPlugin is released under the terms of the AGPLv3 or higher.

from typing import List, Optional, Any, Dict, TYPE_CHECKING
import os.path
import json
import collections
from UM.Extension import Extension
from cura.CuraApplication import CuraApplication
from UM.Logger import Logger
from UM.Version import Version
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("PragostrojLinearAdvanceSettingPlugin")


if TYPE_CHECKING:
    from UM.OutputDevice.OutputDevice import OutputDevice


class PragostrojLinearAdvanceSettingPlugin(Extension):
    def __init__(self) -> None:
        super().__init__()

        self._application = CuraApplication.getInstance()

        self._i18n_catalog = None  # type: Optional[i18nCatalog]

        self.activeTool = -1

        self.linesFromToolChange = 0

        self._settings_dict = {}  # type: Dict[str, Any]
        # type: List[str]  # temporary list used while creating nested settings
        self._expanded_categories = []

        try:
            api_version = self._application.getAPIVersion()
        except AttributeError:
            # UM.Application.getAPIVersion was added for API > 6 (Cura 4)
            # Since this plugin version is only compatible with Cura 3.5 and newer, and no version-granularity
            # is required before Cura 4.7, it is safe to assume API 5
            api_version = Version(5)

        if api_version < Version("7.3.0"):
            settings_definition_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "linear_advance35.def.json")
        else:
            settings_definition_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "linear_advance47.def.json")
        try:
            with open(settings_definition_path, "r", encoding="utf-8") as f:
                self._settings_dict = json.load(
                    f, object_pairs_hook=collections.OrderedDict)
        except:
            Logger.logException(
                "e", "Could not load linear advance settings definition")
            return

        ContainerRegistry.getInstance().containerLoadComplete.connect(
            self._onContainerLoadComplete)
        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode)

    # obtain info about extruders from Cura
    def processExtruders(self) -> None:
        exManager = self._application.getExtruderManager()  # ExtruderManager.getInstance()
        # obtain active extruders as list. It can be not sorted by extruder number.
        activeExtruders = exManager.getUsedExtruderStacks()
        self.extruderList = [None]*4

        for extr in activeExtruders:
            enr = extr.getProperty("extruder_nr", "value")
            self.extruderList[enr] = extr
        return

    def processM104(self, line):
        line = line.splitlines(False)[0]
        params = line[5:].split(" ")
        extruderNum = str(self.activeTool)
        temp = "-1"
        for item in params:
            if item[:1] == "T":
                extruderNum = item[1:]
            elif item[:1] == "S":
                temp = item[1:]

        newline = "M568 P"+extruderNum+" S"+temp
        if self.activeTool != int(extruderNum):
            Logger.log("Extruder: "+extruderNum)
            extr = self.extruderList[int(extruderNum)]
            stby = extr.getProperty("material_standby_temperature", "value")
            if float(temp) == stby:
                newline = ";"+newline
            else:
                newline += " A2"

        return newline+"\r\n"

    def processM109(self, line):
        line = line.splitlines(False)[0]
        params = line[5:].split(" ")
        extruderNum = str(self.activeTool)
        temp = "-1"
        for item in params:
            if item[:1] == "T":
                extruderNum = item[1:]
            elif item[:1] == "S":
                temp = item[1:]

        newline = "M568 P"+extruderNum+" S"+temp+"\r\nM116 P"+extruderNum+" S5"

        return newline+"\r\n"

    def processM106(self, line):
        # M106 with fan number
        line = line.splitlines(False)[0]
        params = line[5:].split(" ")
        extruderNum = str(self.activeTool)
        comment = ""
        fanvalue = "0"
        fannum = "0"
        if extruderNum == "0":
            fannum = "0"
        elif extruderNum == "1":
            fannum = "2"

        for item in params:
            if item[:1] == "P":
                fannum = item[1:]
            elif item[:1] == "S":
                fanvalue = item[1:]
        #    elif item[:1]==";":
        #        comment = line[line.index(";"):]
        newline = "M106 P"+fannum+" S"+fanvalue+" "+comment+"\r\n"
        return newline

    def processM900(self, line):
        # convert from M900 to M572 GCode    M900 T0 Kx -> M572 D0 Sx
        line = line.splitlines(False)[0]
        params = line[5:].split(" ")
        extruderNum = str(self.activeTool)
        comment = ""
        kfactor = "0"
        for item in params:
            if item[:1] == "T":
                extruderNum = item[1:]
            elif item[:1] == "K":
                kfactor = item[1:]
        #    elif item[:1]==";":
        #        comment = line[line.index(";"):]
        newline = "M572 D"+extruderNum+" K"+kfactor+" "+comment+"\r\n"
        return newline

    def processStartSection(self, line):
        initTempGcode = "\r\n;Inserted by PragostrojPostProcessor\r\n"
        for extr in self.extruderList:
            initTempGcode += "M568 P"+str(extr.getProperty("extruder_nr", "value"))+" S"+str(extr.getProperty(
                "material_initial_print_temperature", "value"))+" R"+str(extr.getProperty("material_standby_temperature", "value"))+"\r\n"
        initTempGcode += ";End section PragostrojPostProcessor\r\n"
        newline = line + "\r\n" + initTempGcode
        return newline

    def processGCodeChanges(self, layer):
        lines = layer.splitlines(True)
        data = ""
        for line in lines:
            if line.startswith("T"):  # save active extruder number
                self.activeTool = int(line[1:2])
                self.linesFromToolChange = 0
            elif line.startswith("M104"):
                line = self.processM104(line)
            elif line.startswith("M109"):
                line = self.processM109(line)
            elif line.startswith("M900"):
                line = self.processM900(line)
            elif line.startswith("M106"):
                line = self.processM106(line)
            elif line.startswith(";Generated with Cura_SteamEngine"):
                line = self.processStartSection(line)
            data += line
            self.linesFromToolChange += 1
        return data

    def _onContainerLoadComplete(self, container_id: str) -> None:
        if not ContainerRegistry.getInstance().isLoaded(container_id):
            # skip containers that could not be loaded, or subsequent findContainers() will cause an infinite loop
            return

        try:
            container = ContainerRegistry.getInstance(
            ).findContainers(id=container_id)[0]
        except IndexError:
            # the container no longer exists
            return

        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        try:
            material_category = container.findDefinitions(key="material")[0]
        except IndexError:
            Logger.log(
                "e", "Could not find parent category setting to add settings to")
            return

        for setting_key in self._settings_dict.keys():
            setting_definition = SettingDefinition(
                setting_key, container, material_category, self._i18n_catalog)
            setting_definition.deserialize(self._settings_dict[setting_key])

            # add the setting to the already existing material settingdefinition
            # private member access is naughty, but the alternative is to serialise, nix and deserialise the whole thing,
            # which breaks stuff
            material_category._children.append(setting_definition)
            container._definition_cache[setting_key] = setting_definition

            self._expanded_categories = self._application.expandedCategories.copy()
            self._updateAddedChildren(container, setting_definition)
            self._application.setExpandedCategories(self._expanded_categories)
            self._expanded_categories = []  # type: List[str]
            container._updateRelations(setting_definition)

    def _updateAddedChildren(self, container: DefinitionContainer, setting_definition: SettingDefinition) -> None:
        children = setting_definition.children
        if not children or not setting_definition.parent:
            return

        # make sure this setting is expanded so its children show up  in setting views
        if setting_definition.parent.key in self._expanded_categories:
            self._expanded_categories.append(setting_definition.key)

        for child in children:
            container._definition_cache[child.key] = child
            self._updateAddedChildren(container, child)

    def _filterGcode(self, output_device: "OutputDevice") -> None:

        Logger.log('i', '------------------- _filterGcode started ------------------------------')
        self.processExtruders()
        scene = self._application.getController().getScene()

        global_container_stack = self._application.getGlobalContainerStack()
        used_extruder_stacks = self._application.getExtruderManager().getUsedExtruderStacks()
        if not global_container_stack or not used_extruder_stacks:
            return

        if not global_container_stack.getProperty("material_linear_advance_enable", "value"):
            print('-----------Linear Advanced is not enabled------------')
            return

        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict:  # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return

        gcode_flavor = global_container_stack.getProperty(
            "machine_gcode_flavor", "value")
        if gcode_flavor == "RepRap (RepRap)" or gcode_flavor.find('Griffin') != -1:
            # Pressure Advance (for RepRap / Duet)
            gcode_command_pattern = "M572 S%f D%d"
        else:
            # Linear Advance (for Marlin)
            gcode_command_pattern = "M900 K%f T%d"
        gcode_command_pattern += " ;added by LinearAdvanceSettingPlugin"

        dict_changed = False

        for plate_id in gcode_dict:
            gcode_list = gcode_dict[plate_id]
            if len(gcode_list) < 2:
                Logger.log(
                    "w", "Plate %s does not contain any layers", plate_id)
                continue

            if ";LINEARADVANCEPROCESSED\n" in gcode_list[0]:
                Logger.log(
                    "d", "Plate %s has already been processed", plate_id)
                continue

            setting_key = "material_linear_advance_factor"

            current_linear_advance_factors = {}  # type: Dict[int, float]
            apply_factor_per_feature = {}  # type: Dict[int, bool]

            for extruder_stack in used_extruder_stacks:
                extruder_nr = int(
                    extruder_stack.getProperty("extruder_nr", "value"))
                linear_advance_factor = extruder_stack.getProperty(
                    setting_key, "value")

                gcode_list[1] = gcode_list[1] + \
                    gcode_command_pattern % (
                        linear_advance_factor, extruder_nr) + "\n"

                dict_changed = True

                current_linear_advance_factors[extruder_nr] = linear_advance_factor

                apply_factor_per_feature[extruder_nr] = False
                for feature_setting_key in self.__gcode_type_to_setting_key.values():
                    if extruder_stack.getProperty(feature_setting_key, "value") != linear_advance_factor:
                        apply_factor_per_feature[extruder_nr] = True
                        break

            if any(apply_factor_per_feature.values()):
                current_layer_nr = -1
                for layer_nr, layer in enumerate(gcode_list):
                    lines = layer.split("\n")
                    lines_changed = False
                    for line_nr, line in enumerate(lines):

                        if line.startswith(";LAYER:"):
                            try:
                                current_layer_nr = int(line[7:])
                            except ValueError:
                                Logger.log(
                                    "w", "Could not parse layer number: ", line)
                        if line.startswith(";TYPE:"):
                            # Changed line type
                            feature_type = line[6:]  # remove ";TYPE:"
                            try:
                                feature_setting_key = self.__gcode_type_to_setting_key[feature_type]
                            except KeyError:
                                Logger.log(
                                    "w", "Unknown feature type in gcode: ", feature_type)
                                feature_setting_key = ""

                            if current_layer_nr <= 0 and feature_type != "SKIRT":
                                feature_setting_key = "material_linear_advance_factor_layer_0"

                            for extruder_stack in used_extruder_stacks:
                                extruder_nr = extruder_stack.getProperty(
                                    "extruder_nr", "value")

                                if not apply_factor_per_feature[extruder_nr]:
                                    continue

                                if feature_setting_key:
                                    linear_advance_factor = extruder_stack.getProperty(
                                        feature_setting_key, "value")
                                else:  # unknown feature type
                                    linear_advance_factor = 0  # no linear advance compensation for this feature

                                if linear_advance_factor != current_linear_advance_factors.get(extruder_nr, None):
                                    current_linear_advance_factors[extruder_nr] = linear_advance_factor

                                    lines.insert(
                                        line_nr + 1, gcode_command_pattern % (linear_advance_factor, extruder_nr))

                                    lines_changed = True

                    if lines_changed:
                        gcode_list[layer_nr] = "\n".join(lines)
                        dict_changed = True

            gcode_list[0] += ";PRAGOSTROJ LINEARADVANCEPROCESSED v0.9\n"

            for layer_nr, layer in enumerate(gcode_list):
                layer = self.processGCodeChanges(layer)
                gcode_list[layer_nr] = layer
                dict_changed = True

            gcode_dict[plate_id] = gcode_list

        if dict_changed:
            setattr(scene, "gcode_dict", gcode_dict)

        if dict_changed:
            Logger.log('i', '-------------------GCODE DICT CHANGED ------------------------------')
        else:
            Logger.log('i', '-------------------GCODE DICT HAS NOT CHANGED ------------------------------')

    __gcode_type_to_setting_key = {
        "WALL-OUTER": "material_linear_advance_factor_wall_0",
        "WALL-INNER": "material_linear_advance_factor_wall_x",
        "SKIN": "material_linear_advance_factor_topbottom",
        "SUPPORT": "material_linear_advance_factor_support",
        "SUPPORT-INTERFACE": "material_linear_advance_factor_support_interface",
        "SKIRT": "material_linear_advance_factor_skirt_brim",
        "FILL": "material_linear_advance_factor_infill",
        "PRIME-TOWER": "material_linear_advance_factor_prime_tower"
    }
