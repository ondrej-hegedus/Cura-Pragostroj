import QtQuick 2.10
import QtQuick.Controls 2.1
import UM 1.3 as UM
import QtQuick.Layouts 1.3

Rectangle
{
    id: monitorMemmory
    anchors.fill: parent
    anchors.margins: 0
    visible: currentPage == 2

    ListView
    {
        clip: true

        anchors.fill: parent
        anchors.margins: 5
        anchors.bottomMargin: 70

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AlwaysOn
            active: ScrollBar.AlwaysOn
        }


        orientation: ListView.Vertical
        model: OutputDevice.machineMemmory
        delegate:

        Column
        {
            id: memoryRowHolder
            spacing: 10
            width: monitorMemmory.width

            Row
            {
                id: memoryRow
                visible: modelData.type == "file"
                leftPadding: 20
                topPadding: 20
                rightPadding: 20
                bottomPadding: 20
                height: 150
                spacing: 10

                Checkbox
                {
                    filename: modelData.fileNamePath
                }

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
                    width: 730
                    anchors.verticalCenter: parent.verticalCenter
                    Row
                    {
                         spacing: 25
                         Label
                         {
                            width: 570
                            text: modelData.fileNamePath
                            font.pixelSize: 20
                         }
                         Row
                         {
                            spacing: 5
                            width: 200
                            PGRecolorImage
                            {
                                // color: customBlue
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
                                text: "Print time "+ modelData.printTime
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
                            model: modelData.extruders
                            Row
                            {
                                spacing: 5

                                PGRecolorImage
                                {
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
                                }
                                Label
                                {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: modelData.nozzleDiameter + " mm " +  modelData.material.metadata.name.material
                                    font.pixelSize: 16
                                }
                            }
                        }
                        Row
                        {
                            spacing: 5
                            PGRecolorImage
                            {
                                // color: customBlue
                                height: Math.round(25)
                                width: Math.round(25)
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
                                text: modelData.printInfo["buildPlateType"] ? modelData.printInfo["buildPlateType"] : 'N/A'
                                font.pixelSize: 16
                            }
                        }
                        Row
                        {
                            spacing: 5
                            visible: modelData.printInfo["chamberTemp"] > 0
                            PGRecolorImage
                            {
                                // color: customBlue
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
                                text: modelData.printInfo["chamberTemp"]
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
                    leftPadding: 20
                    QueueButton
                    {
                        text: 'Print'
                        active: OutputDevice.canPrint
                        onClicked: {
                            OutputDevice.printFile(modelData.fileNamePath);
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

    Column
    {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 70
        spacing: 5
        Spacer
        {
        }

        RowLayout
        {
            width: baseWidth
            height: parent.height

            Rectangle {
                Layout.alignment: Qt.AlignCenter
                Layout.preferredWidth: Math.round((parent.width)/3)
                QueueButton
                {
                    anchors.centerIn: parent
                    text: 'Delete'
                    onClicked: {
                        popup.msg = 'Are you sure you want to delete selected files?'
                        popup.msg2 = 'This action is not reversible.'
                        popup.yesText = 'Delete'
                        popup.noText = 'Back'
                        popup.showPopup = true
                        popup.clickYes = function(){
                            OutputDevice.deleteSelected()
                            console.log("clickYes = function")
                        }
                    }
                }
            }

            Rectangle {
                Layout.alignment: Qt.AlignCenter
                Layout.preferredWidth: Math.round((parent.width)/3)
                QueueButton
                {
                    anchors.centerIn: parent
                    text: 'Delete all'
                    onClicked: {
                        popup.msg = 'Are you sure you want to delete all files?'
                        popup.msg2 = 'This action is not reversible.'
                        popup.yesText = 'Delete All'
                        popup.noText = 'Back'
                        popup.showPopup = true
                        popup.clickYes = function(){
                            OutputDevice.deleteAll()
                            console.log("clickYes = function")
                        }
                    }
                }
            }

            Rectangle {
                Layout.alignment: Qt.AlignCenter
                Layout.preferredWidth: Math.round((parent.width)/3)
                SortButton
                {
                }
            }
        }
    }
}