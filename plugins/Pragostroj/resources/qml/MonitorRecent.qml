import QtQuick 2.10
import QtQuick.Controls 2.1
import UM 1.3 as UM
import QtQuick.Layouts 1.3

 ListView
 {
     visible: {
       return currentPage == 1
    }
    clip: true

    anchors.fill: parent
    anchors.margins: 5

    orientation: ListView.Vertical
    model: OutputDevice.recentFiles

    ScrollBar.vertical: ScrollBar {
        policy: ScrollBar.AlwaysOn
        active: ScrollBar.AlwaysOn
    }

    delegate:

    Column
    {
        id: recentRowHolder
        spacing: 10
        width: parent.width

        Row
        {
            id: recentRow
            leftPadding: 20
            topPadding: 20
            rightPadding: 20
            bottomPadding: 20
            height: 150
            spacing: 10

            Image {
                source: OutputDevice.imgpath + "/file/thumbnail/"+modelData.fileNamePath
                width:100
                height:100
            }
            Label
            {
                width: 30
            }
            Column
            {
                spacing: 10
                width: 800
                anchors.verticalCenter: parent.verticalCenter
                Row
                {
                    width: parent.width
                     spacing: 25
                     Label
                     {
                        width: 400
                        text: modelData.fileNamePath
                        font.pixelSize: 20
                        elide: Text.ElideRight
                     }
                     Row
                     {
                        spacing: 5
                        width: 200
                        PGRecolorImage
                        {
                            color: modelData.fileExists ? customBlue: 'gray'
                            height: 20
                            width: 20
                            source:
                            {
                                return "../svg/icons/clock.svg"
                            }
                            sourceSize
                            {
                                height: height
                                width: width
                            }
                        }
                        Label
                        {
                            text: "Print time "+ modelData.duration
                            font.pixelSize: 16
                        }
                     }
                     Column
                     {
                        width: 150
                        Label
                        {
                            text: "Finished"
                            font.pixelSize: 20
                            visible: modelData.state == 1
                        }
                        Label
                        {
                            text: "Canceled at "+ modelData.fractionPrinted
                            font.pixelSize: 20
                            visible: modelData.state == 2
                        }
                        Label
                        {
                            text: "Error at "+ modelData.fractionPrinted
                            font.pixelSize: 20
                            visible: modelData.state == 3
                        }
                        Label
                        {
                            text: modelData.stopTime
                            font.pixelSize: 16
                        }
                     }
                }
                Spacer
                {
                    height: 1
                }
                Row
                {
                    id: extrudersHolder
                    property var recentFileModel: modelData
                    spacing: 50
                    Repeater {
                        model: modelData.materials
                        Row
                        {
                            spacing: 15

                            PGRecolorImage
                            {
                                color: extrudersHolder.recentFileModel.fileExists ? customBlue: 'gray'
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
                            }
                            Label
                            {
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData.diameter + " mm " +  modelData.material
                                font.pixelSize: 16
                            }
                            Row
                            {
                                spacing: 5

                                PGRecolorImage
                                {
                                    color: modelData.fileExists ? customBlue: 'gray'
                                    // height: Math.round(25)
                                    // width: Math.round(25)
                                    height: 32
                                    width: 27
                                    source:
                                    {
                                        return "../svg/icons/buildplate.svg"
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
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: modelData.bedTemperature + " °C"
                                    font.pixelSize: 16
                                }
                                }
                                }
                    }
                    // Row
                    // {
                    //     spacing: 5
                    //     PGRecolorImage
                    //     {
                    //         color: modelData.fileExists ? customBlue: 'gray'
                    //         height: Math.round(25)
                    //         width: Math.round(25)
                    //         source:
                    //         {
                    //             return "../svg/icons/buildplate.svg"
                    //         }
                    //         sourceSize
                    //         {
                    //             height: height
                    //             width: width
                    //         }
                    //         visible: source != ""
                    //     }
                    //     Label
                    //     {
                    //         text: modelData.plate
                    //         font.pixelSize: 16
                    //     }
                    // }
                    Row
                    {
                        spacing: 5
                        visible: false && OutputDevice.getChamber.hasChamber
                        PGRecolorImage
                        {
                            color: modelData.fileExists ? customBlue: 'gray'
                            height: Math.round(25)
                            width: Math.round(25)
                            source:
                            {
                                return "../svg/icons/chamber.svg"
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
                            text: (OutputDevice.getChamber.setpoint?Math.round(OutputDevice.getChamber.setpoint): "-") + " °C "
                            font.pixelSize: 20
                        }
                    }
                }
            }
            Column
            {
                width:160
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3
                leftPadding: 30
                QueueButton
                {
                    text: 'Print'
                    visible: modelData.fileExists
                    active: OutputDevice.canPrint
                    onClicked: {
                        OutputDevice.printFile(modelData.fileNamePath);
                    }
                }
                QueueButton
                {
                    text: 'Not available'
                    visible: !modelData.fileExists
                    active: false
                    onClicked: {
                    }
                }
            }
        }

        Spacer
        {
            width: baseWidth - 35
        }
    }
}