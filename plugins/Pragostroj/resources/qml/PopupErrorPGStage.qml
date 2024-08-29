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
        visible: PragostrojStage.popupError
        // visible: false
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
        // visible: UM.Controller.getStage("Pragostroj").popupError
        visible: PragostrojStage.popupError
        // visible: false
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        width: 520
        height: popupError.msg2?200:170
        border.color: customGray
        border.width: 1
        radius: 10

        Label
        {
            id: msgHeading
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 30
            // text: UM.Controller.getStage("Pragostroj").popupErrorText
            text: PragostrojStage.popupErrorText
            // text: "TEST TEXT 1"
            font.pixelSize: 22
        }
        Label
        {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: msgHeading.bottom
            anchors.topMargin: 30
            // text: OutputDevice.popupErrorText2
            text: PragostrojStage.popupErrorText2
            // text: "TEST TEXT 3"
            font.pixelSize: 18
        }
        QueueButton
        {
            text: "OK"
            active: true
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter

            onClicked: {
                PragostrojStage.hidePopupError()
            }
        }
    }
}