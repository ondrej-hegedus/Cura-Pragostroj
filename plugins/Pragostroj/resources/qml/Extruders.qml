import QtQuick.Layouts 1.3
import QtQuick 2.10

import QtQuick.Controls 2.1
// import QtQuick.Controls.Styles 1.4
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Column
{
    property var extruders: []

    GridLayout
    {
        id: extruderGrid
        columns: 4
        rowSpacing: 10
        columnSpacing: 2
        Label
        {
        }
        Label
        {
            text: "Nozzle D (Material D)"
            font.pixelSize: 16
            font.bold: true
        }
        Label
        {
            text: "Type"
            font.pixelSize: 16
            font.bold: true
        }
        Label
        {
            text: " Temp."
            font.pixelSize: 16
            font.bold: true
        }
        Repeater
        {
            model: extruders
            delegate: Item {
                objectName: "itemWrapper"

                Component.onCompleted: {
                    // reparent all child elements into the grid
                    while (children.length)
                        children[0].parent = extruderGrid;
                }
                PGRecolorImage
                {
                    Layout.alignment: Qt.AlignRight | Qt.AlignTop
                    Layout.column: 0
                    Layout.row: index + 2
                    // color: customBlue
                    height: 32
                    width: 27
                    source:
                    {
                        return "../svg/icons/extruder_"+(index+1)+".svg"
                    }
                    sourceSize
                    {
                        height: height
                        width: width
                    }
                    visible: source != ""
                }
                Label
                {
                    Layout.alignment: Qt.AlignRight | Qt.AlignTop
                    Layout.column: 1
                    Layout.row: index + 2
                    text: modelData.outputDiameter + "mm ("+ modelData.inputDiameter +" mm)         "
                    font.pixelSize: 14
                    font.bold: true
                    horizontalAlignment: Text.AlignLeft
                }
                Label
                {
                    Layout.alignment: Qt.AlignRight | Qt.AlignTop
                    Layout.column: 2
                    Layout.row: index + 2
                    text: modelData.material + " "
                    font.pixelSize: 14
                    font.bold: true
                }
                Label
                {
                    Layout.alignment: Qt.AlignRight | Qt.AlignTop
                    Layout.column: 3
                    Layout.row: index + 2
                    text: Math.round(modelData.tempeature.current) + " °C"
                    font.pixelSize: 14
                    font.bold: true
                }
            }
        }
    }
}