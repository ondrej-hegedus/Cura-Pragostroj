import QtQuick 2.10
import QtQuick.Controls 2.0
import UM 1.3 as UM


Item
{
    Row
    {
        width: parent.width - 60
        spacing: 20 * screenScaleFactor
        leftPadding: 20
        topPadding: 20
        rightPadding: 20
        bottomPadding: 20

        Column
        {
            width: Math.round(parent.width/6)
            UM.RecolorImage
            {
                id: printerIcon
                color: '#00ff00'
                height: Math.round(100 * screenScaleFactor)
                width: Math.round(100 * screenScaleFactor)
                source:
                {
                    return "../svg/UMs5-icon.svg"
                }
                sourceSize
                {
                    height: height
                    width: width
                }
                visible: source != ""
            }
        }

        Column
        {
            //status
            width: Math.round(parent.width/6)
            Label
            {
                text: modelData.getMachineModel
                font.pixelSize: 20
            }
            Label
            {
                text: "machineState: " + modelData.getStatus + " " + modelData.getLastStatus
                font.pixelSize: 20
            }
        }

        Column
        {
            //materials
            width: Math.round(parent.width/3)
            Repeater
            {
                model: modelData.getExtruders

                Row
                {
                    padding: 5
                    UM.RecolorImage
                    {
                        color: '#00ff00'
                        height: Math.round(25)
                        width: Math.round(25)
                        source:
                        {
                            return "../svg/icons/extruder.svg"
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
                        text: " " + modelData.outputDiameter + "mm ("+ modelData.inputDiameter +" mm) "
                        font.pixelSize: 16
                    }
                    Label
                    {
                        text: modelData.material
                        font.pixelSize: 16
                    }
                }
            }
        }

        Grid
        {
            columns: 2
            width: Math.round(parent.width/3)
            Label
            {
                font.pixelSize: 16
                width: Math.round(parent.width * 0.5)
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                text: "Building plate:"
            }
            Label
            {
                font.pixelSize: 16
                width: Math.round(parent.width * 0.5)
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                text: "(t) glass"
            }
            Label
            {
                font.pixelSize: 16
                width: Math.round(parent.width * 0.5)
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                text: "Chamber:"
            }
            Label
            {
                font.pixelSize: 16
                width: Math.round(parent.width * 0.5)
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                text: ""
            }
        }
    }

}