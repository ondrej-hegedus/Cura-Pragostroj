import QtQuick 2.10
// import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0
import QtQuick.Controls 2.1

Rectangle
{
    id: pragostrojStageRect

    property var customBlue: '#00C4FE'
    property var customGray: '#808080'
    property var backgroundGray:'#f6f6f6'

    anchors.top: parent.top
    anchors.bottom: parent.bottom
    // property var baseWidth: 1200
    property var baseWidth: 1220
    color: backgroundGray



    Rectangle
    {
        id: banner_outer
        width: baseWidth
        height: 150
        anchors.horizontalCenter: parent.horizontalCenter
        color: backgroundGray

        Rectangle
        {
            id: banner
            border.color: customBlue
            border.width: 1
            radius: 10
            width: baseWidth
            height: 110
            color: '#ffffff'
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "../svg/logo.svg"
            }

            MouseArea
            {
                id: mouseArea
                anchors.fill: parent
                onClicked: {
                    Qt.openUrlExternally("http://pragostroj.com/");
                }
                cursorShape: Qt.OpenHandCursor
            }
        }
    }



    Rectangle
    {
        id: rect2
        width: baseWidth + 30
        height: 200
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: banner_outer.bottom
        anchors.bottom: parent.bottom

        color: backgroundGray

        ListView
        {
            clip: true
            width: baseWidth + 30

            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20

            orientation: ListView.Vertical

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AlwaysOn
                active: ScrollBar.AlwaysOn
            }

            model: UM.Controller.activeStage.progostrojDevices

            delegate:
                Rectangle
                {
                    height: 220
                    width: parent.width - 30
                    color: backgroundGray
                    anchors.horizontalCenter: parent.horizontalCenter

                Rectangle
                {
                    //anchors.bottom: parent.bottom
                    border.color: customGray
                    border.width: 1
                    radius: 10
                    width: parent.width
                    height: 200
                    color: '#ffffff'

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
                            source: "../svg/printer/printer_" + modelData.getStatus + ".svg"
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
                                text: modelData.getPrinterName
                                font.pixelSize: 20
                                font.bold: true
                            }
                            Label
                            {
                                text: modelData.getPrinterModel
                                font.pixelSize: 10
                                color: customGray
                                font.bold: true
                            }
                            Label
                            {
                                text: "IP: " + modelData.address
                                font.pixelSize: 20
                                font.bold: true
                                topPadding: 16
                                bottomPadding: 16
                            }
                            Label
                            {
                                text: modelData.getStatusTranslated
                                font.pixelSize: 16
                                font.bold: true
                                color: modelData.getStatus == 'OFF'? customGray:customBlue
                            }
                            Label
                            {
                                topPadding: 6
                                visible: modelData.isPrinting || modelData.getStatus == 'H'
                                text: modelData.getStatusSmallMessage
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
                            extruders: modelData.getExtruders
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
                                //     active: modelData.getStatus != 'OFF'
                                //     width: 110
                                //     text: 'Prepare'
                                //     onClicked: {
                                //         UM.Controller.activeStage.selectPrepareStage(modelData)
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
                                            return modelData.getStatus == 'OFF'? "../svg/icons/gray_buildplate.svg":"../svg/icons/buildplate.svg"
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
                                        visible: modelData.getStatus != 'OFF'
                                        text: modelData.getBed.plate
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                    Label
                                    {
                                        visible: modelData.getStatus != 'OFF'
                                        text: Math.round(modelData.getBed.temperature) +" °C "
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
                                            return modelData.getStatus == 'OFF'? "../svg/icons/gray_chamber.svg":"../svg/icons/chamber.svg"
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
                                        text: modelData.getChamber.hasChamber ? "Heated" : "Non heated"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                    Label
                                    {
                                        text: modelData.getChamber.current ? (Math.round(modelData.getChamber.current) + (modelData.getChamber.setpoint? " / " + Math.round(modelData.getChamber.setpoint): "") + " °C") : " - °C"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                }
                            }
                            // Rectangle {
                            //     height: 20
                            //     width: parent.width
                            // }
                            RowLayout
                            {
                                spacing: 10
                                Layout.alignment: Qt.AlignVCenter
                                width: parent.width
                                anchors.bottom: tempinfo.bottom
                                anchors.bottomMargin: 40
                                // Rectangle {
                                //     height: 80
                                //     width: 20
                                //     color: "#ff0000"
                                // }
                                QueueButton
                                {
                                    active: modelData.getStatus != 'OFF'
                                    width: 110
                                    text: 'Prepare'
                                    onClicked: {
                                        UM.Controller.activeStage.selectPrepareStage(modelData)
                                    }
                                }
                                QueueButton
                                {
                                    active: modelData.getStatus != 'OFF'
                                    width: 110
                                    text: 'Monitor'
                                    onClicked: {
                                        UM.Controller.activeStage.selectMonitorStage(modelData)
                                    }
                                }
                                CameraButton
                                {
                                    active: modelData.getStatus != 'OFF'
                                    address: "http://" + modelData.ipAddress + ":8080/camera.html"
                                }
                            }
                        }
                    }
                }
            }

        }
    }

    PopupErrorPGStage
    {
        id: popupErrorPGStage
    }

    // Rectangle
    // {
    //     id: recttest

    //     width: baseWidth
    //     height: 150

    //     // anchors.horizontalCenter: parent.horizontalCenter
    //     // anchors.horizontalCenter: parent.horizontalCenter
    //     // anchors.top: rect2.bottom
    //     // anchors.bottom: parent.bottom

    //     color: backgroundGray

    //     Text {
    //         text: '------------------TEST---------------------'
    //         height: 200
    //     }
    // }


}
