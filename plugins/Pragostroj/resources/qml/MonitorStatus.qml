import QtQuick 2.10
import UM 1.3 as UM
import QtQuick.Layouts 1.3
import Cura 1.0 as Cura
import QtQuick.Controls 2.1



Rectangle
{
    border.color: customGray
    border.width: 1
    radius: 10
    width: baseWidth
    height: OutputDevice.isPrinting ? 300: 200

    Rectangle
    {
        id: statusCol
        width: baseWidth

// ---

        Row
        {
            spacing: 20 * screenScaleFactor
            leftPadding: 20
            topPadding: 20
            rightPadding: 20
            bottomPadding: 20
            height: 200
            width: parent.width
            Image {
                id: printerIcon
                source: "../svg/printer/printer_"+OutputDevice.getStatus+".svg"
                width:140
                height:140
            }
            Column
            {
                //status
                // width: 190
                width: 200
                Label
                {
                    text: OutputDevice.getPrinterName
                    font.pixelSize: 20
                    font.bold: true
                }
                Label
                {
                    text: OutputDevice.getPrinterModel
                    font.pixelSize: 10
                    color: customGray
                    font.bold: true
                }
                Label
                {
                    text: "IP: " + OutputDevice.address
                    font.pixelSize: 20
                    font.bold: true
                    topPadding: 16
                    bottomPadding: 16
                }
                Label
                {
                    text: OutputDevice.getStatusTranslated
                    font.pixelSize: 16
                    font.bold: true
                    color: OutputDevice.getStatus == 'OFF'? customGray:customBlue
                }
                Label
                {
                    topPadding: 6
                    visible: OutputDevice.isPrinting
                    text: 'Remaining time: '+ OutputDevice.getRemainingTime
                    font.pixelSize: 12
                    font.bold: true
                    color: customGray
                }
            }
            VSpacer
            {
            }
            Extruders
            {
                extruders: OutputDevice.getExtruders
                width: 400
            }
            VSpacer
            {
            }
            Column
            {
                id: tempinfo
                // width: 380
                width: 340
                height: parent.height
                spacing: 2
                // topPadding: 0
                // padding: 0

                // anchors.margins: 0

                RowLayout
                {
                    // anchors.margins: 0

                    // height: 100
                    width: parent.width
                    // Layout.topMargin: 0
                    // Layout.margins: 0
                    // anchors.top: tempinfo.top

                    // Layout.alignment: Qt.AlignVCenter

                    // QueueButton
                    // {
                    //     active: OutputDevice.getStatus != 'OFF'
                    //     width: 110
                    //     text: 'Prepare'
                    //     onClicked: {
                    //         UM.Controller.activeStage.selectPrepareStage(OutputDevice)
                    //     }
                    // }

                    // Rectangle {
                    //     height: 40
                    //     width: 20
                    //     color: "#ff0000"
                    // }
                    GridLayout
                    {
                        height: 100
                        Layout.topMargin: 0
                        Layout.preferredWidth: 180
                        columns: 3
                        rowSpacing: 10
                        columnSpacing: 15
                        Label
                        {
                        }
                        Label
                        {
                            text: "Bed"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        Label
                        {
                            text: "Temp."
                            font.pixelSize: 16
                            font.bold: true
                        }
                        PGRecolorImage
                        {
                            // color: customBlue
                            height: Math.round(25)
                            width: Math.round(25)
                            source:
                            {
                                // return "../svg/icons/buildplate.svg"
                                return OutputDevice.getStatus == 'OFF'? "../svg/icons/gray_buildplate.svg":"../svg/icons/buildplate.svg"
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
                            visible: OutputDevice.getStatus != 'OFF'
                            text: OutputDevice.getBed.plate
                            font.pixelSize: 14
                            font.bold: true
                        }
                        Label
                        {
                            visible: OutputDevice.getStatus != 'OFF'
                            text: Math.round(OutputDevice.getBed.temperature) +" °C "
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                    VSpacer
                    {
                    }
                    GridLayout
                    {
                        Layout.preferredWidth: 180
                        columns: 3
                        rowSpacing: 10
                        columnSpacing: 15
                        Label
                        {
                        }
                        Label
                        {
                            text: "Chamber"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        Label
                        {
                            text: "Temp."
                            font.pixelSize: 16
                            font.bold: true
                        }
                        PGRecolorImage
                        {
                            // color: customBlue
                            height: Math.round(25)
                            width: Math.round(25)
                            source:
                            {
                                // return "../svg/icons/chamber.svg"
                                return OutputDevice.getStatus == 'OFF'? "../svg/icons/gray_chamber.svg":"../svg/icons/chamber.svg"
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
                            text: OutputDevice.getChamber.hasChamber ? "Heated" : "Non heated"
                            font.pixelSize: 14
                            font.bold: true
                        }
                        Label
                        {
                            text: OutputDevice.getChamber.current ? (Math.round(OutputDevice.getChamber.current) + (OutputDevice.getChamber.setpoint? " / " + Math.round(OutputDevice.getChamber.setpoint): "") + " °C") : " - °C"
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                }

                RowLayout
                {
                    spacing: 10
                    Layout.alignment: Qt.AlignVCenter
                    width: parent.width
                    anchors.bottom: tempinfo.bottom
                    anchors.bottomMargin: 40
                    CameraButton
                    {
                        active: OutputDevice.getStatus != 'OFF'
                        address: "http://" + OutputDevice.ipAddress + ":8080/camera.html"
                    }
                }
            }
        }
        Spacer
        {
            anchors.top: parent.top
            anchors.topMargin: 200
            id: printerSpacer
            width: 1200
            visible: OutputDevice.isPrinting
        }
        RowLayout
        {
            anchors.top: parent.top
            anchors.topMargin: 200
            width: 1200
            visible: OutputDevice.isPrinting
            Column
            {
                width: 150
                Layout.leftMargin: 50
                Layout.rightMargin: 50
                Layout.topMargin: 10
                Image {
                    source: OutputDevice.imgpath + "/file/thumbnail/"+OutputDevice.getPrintedFilename
                    width:80
                    height:80
                }
            }
            Rectangle
            {
                id: printedHolder
                // width: 600
                width: 700
                height: 35
                Label
                {
                    id: printFileName
                    width: 300
                    anchors.left: parent.left
                    text: OutputDevice.getPrintedFilename
                    font.pixelSize: 18
                }
                // Label
                // {
                //     anchors.left: printFileName.right
                //     text: Math.round(OutputDevice.getPrintPct) +' %'
                //     color: customBlue
                //     font.pixelSize: 16
                // }
                Label
                {
                    text: 'Remaining time: '+ OutputDevice.getRemainingTime
                    font.pixelSize: 16
                    anchors.right: parent.right
                }
                Rectangle
                {
                    id: printedBar
                    anchors.bottom: printedHolder.bottom
                    // width: Math.round(6 * OutputDevice.getPrintPct)
                    width: Math.round(6 * OutputDevice.getPrintPct)
                    height: 5
                    color: customBlue
                }
                Rectangle
                {
                    anchors.left: printedBar.right
                    anchors.bottom: printedHolder.bottom
                    // width: (600 - Math.round(6 * OutputDevice.getPrintPct))
                    width: (700 - Math.round(6 * OutputDevice.getPrintPct))
                    height: 5
                    color: '#c4c4c4'
                }
            }
            RowLayout
            {
                spacing: 30
                width: 250
                QueueButton
                {
                    width: 100
                    visible: OutputDevice.isPaused
                    active: OutputDevice.isPaused
                    icon: 'play'
                    onClicked: {
                        OutputDevice.resumePrint();
                    }
                }
                QueueButton
                {
                    width: 100
                    visible: !OutputDevice.isPaused
                    active: OutputDevice.getState == "P"
                    icon: OutputDevice.getState == "P" ? 'pause' : 'gray_pause'
                    onClicked: {
                        OutputDevice.pausePrint();
                    }

                }
                QueueButton
                {
                    width: 100
                    active: OutputDevice.isPrinting
                    icon: 'stop'
                    onClicked: {
                        popup.msg = 'Do you really wish to stop printing?'
                        popup.msg2 = ''
                        popup.yesText = 'Yes'
                        popup.noText = 'No'
                        popup.showPopup = true
                        popup.clickYes = function(){
                            OutputDevice.stopPrint();
                        }
                    }
                }
            }
            VSpacer
            {
            }
        }
    }
}
