// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
// import QtQuick.Controls 1.4
// import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

// This is the root component for the monitor stage.
Component
{
    id: mainComponent
    Rectangle
    {
        id: monitorFrame

        property var currentPage: 1
        property var customBlue: '#00C4FE'
        property var customGray: '#808080'
        property var backgroundGray:'#f6f6f6'

        property var baseWidth: 1200

        anchors.fill: parent
        //anchors.leftMargin: (maximumWidth -baseWidth)/2
        //anchors.rightMargin: (maximumWidth -baseWidth)/2
        //anchors.topMargin: 20
        //anchors.bottomMargin: 20
        color: backgroundGray

        onVisibleChanged:
        {
        }

        Component.onCompleted: forceActiveFocus()

        UM.I18nCatalog
        {
            id: catalog
            name: "cura"
        }

        MonitorStatus
        {
            id: monitorStatus
            anchors.top: parent.top
            anchors.topMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
        }

        MonitorContent{
            id: monitorContent
            width: baseWidth
            anchors.topMargin: 20
            anchors.bottomMargin: 20
            anchors.top: monitorStatus.bottom
            anchors.bottom: monitorFrame.bottom
            anchors.horizontalCenter: parent.horizontalCenter
        }

        PopupErrorMonitorStage
        {
            id: popupErrorMonitorStage
        }

        Popup
        {
            id: popup
        }
        PrintPopup
        {
            id: printPopup
        }
        PopupInfo
        {
            id: popupInfo
        }
    }
}
