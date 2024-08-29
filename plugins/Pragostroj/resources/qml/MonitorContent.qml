import QtQuick 2.10
import QtQuick.Controls 2.0
import UM 1.3 as UM


    Rectangle {
        id: contentHolder
        border.color: customGray
        border.width: 1
        radius: 10
        width: parent.width

        Rectangle {
            id: buttonHolder
            anchors.top: contentHolder.top
            height: 50

            SwitchButtons
            {
            }
        }

        Rectangle {
            anchors.top: buttonHolder.bottom
            anchors.bottom: contentHolder.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 3

            MonitorRecent{}
            MonitorMemmory{}
            MonitorSettings{}
        }
    }
