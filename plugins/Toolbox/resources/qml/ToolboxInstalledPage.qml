// Copyright (c) 2019 Ultimaker B.V.
// Toolbox is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3

import UM 1.1 as UM

ScrollView
{
    id: page
    clip: true
    width: parent.width
    height: parent.height

    Column
    {
        spacing: UM.Theme.getSize("default_margin").height
        visible: toolbox.pluginsInstalledModel.items.length > 0
        height: childrenRect.height + 4 * UM.Theme.getSize("default_margin").height

        anchors
        {
            right: parent.right
            left: parent.left
            margins: UM.Theme.getSize("default_margin").width
            top: parent.top
        }

        Label
        {
            width: page.width
            text: catalog.i18nc("@title:tab", "Plugins")
            color: UM.Theme.getColor("text_medium")
            font: UM.Theme.getFont("large")
            renderType: Text.NativeRendering
        }
        Rectangle
        {
            id: installedPlugins
            color: "transparent"
            width: parent.width
            height: childrenRect.height + UM.Theme.getSize("default_margin").width
            border.color: UM.Theme.getColor("lining")
            border.width: UM.Theme.getSize("default_lining").width
            Column
            {
                anchors
                {
                    top: parent.top
                    right: parent.right
                    left: parent.left
                    margins: UM.Theme.getSize("default_margin").width
                }
                Repeater
                {
                    id: materialList
                    model: toolbox.pluginsInstalledModel
                    delegate: ToolboxInstalledTile {}
                }
            }
        }
        Label
        {
            text: catalog.i18nc("@title:tab", "Materials")
            color: UM.Theme.getColor("text_medium")
            font: UM.Theme.getFont("medium")
            renderType: Text.NativeRendering
        }

        Rectangle
        {
            id: installedMaterials
            color: "transparent"
            width: parent.width
            height: childrenRect.height + UM.Theme.getSize("default_margin").width
            border.color: UM.Theme.getColor("lining")
            border.width: UM.Theme.getSize("default_lining").width
            Column
            {
                anchors
                {
                    top: parent.top
                    right: parent.right
                    left: parent.left
                    margins: UM.Theme.getSize("default_margin").width
                }
                Repeater
                {
                    id: pluginList
                    model: toolbox.materialsInstalledModel
                    delegate: ToolboxInstalledTile {}
                }
            }
        }
    }
}
