// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.0
// import QtQuick.Controls 1.4
// import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Item
{
    anchors.fill: parent
    property bool showPopup: false
    property string msg: ''
    property var clickYes: null

    Rectangle
    {
        id: popupBackground
        visible: OutputDevice.conflictsPopup.show
        anchors.fill: parent
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: 0
        color: '#000000'
        opacity: 0.5
        MouseArea {
            anchors.fill: parent
            propagateComposedEvents: false
        }
    }

    Rectangle
    {
        id: popupMsg
        visible: OutputDevice.conflictsPopup.show
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        width: 550
        height: 250
        border.color: customGray
        border.width: 1
        radius: 10

        Label
        {
            id: msgHeading
            anchors.horizontalCenter: parent.horizontalCenter
            text:  "Warning! Preprint check has failed"
            font.pixelSize: 22
            anchors.top: parent.top
            anchors.topMargin: 20
        }
        Column
        {
            spacing: 5
            anchors.top: msgHeading.bottom
            anchors.left: popupMsg.left
            anchors.leftMargin: 30
            anchors.topMargin: 30

            Repeater
            {
                model: OutputDevice.conflictsPopup.conflicts
                Label
                {
                    text: modelData
                    font.pixelSize: 16
                }
            }
        }

        QueueButton
        {
            text: 'Print Anyway'
            active: true
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottomMargin: 30
            onClicked: {
                console.log('forcePrint')
                OutputDevice.forcePrint()
            }
        }
        QueueButton
        {
            text: 'Cancel'
            active: true
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottomMargin: 30
            onClicked: {
                console.log('dontPrint')
                OutputDevice.dontPrint()
            }
        }
    }
}