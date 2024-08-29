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

    Rectangle
    {
        id: popupBackground
        visible: OutputDevice.popupInfo
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
        visible: OutputDevice.popupInfo
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        // width: 520
        width: 700
        height: 200
        border.color: customGray
        border.width: 1
        radius: 10

        Label
        {
            id: msgHeading
            anchors.horizontalCenter: parent.horizontalCenter
            text: OutputDevice.popupInfoText
            font.pixelSize: 22
            anchors.top: parent.top
            anchors.topMargin: 30
        }
        Label
        {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: msgHeading.bottom
            text: OutputDevice.popupInfoText2
            font.pixelSize: 18
            anchors.topMargin: 30
        }
        QueueButton
        {
            text: "OK"
            active: true
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: {
                OutputDevice.hidePopupInfo()
            }
        }
    }
}