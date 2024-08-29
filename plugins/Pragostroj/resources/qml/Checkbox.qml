import QtQuick 2.10
import QtQuick.Controls 2.0
import UM 1.3 as UM

Rectangle {
    id: checkbox
    // width:78
    height:50
    width: 60
    // height:32
    anchors.verticalCenter: parent.verticalCenter

// public
    property bool checked: false
    property string filename: ''

    Image {
        anchors.verticalCenter: parent.verticalCenter
        source: "../svg/icons/checkbox0.svg"
        visible: !checked
        // width:50
        // height:50
        width: 32
        height: 32
    }

    Image {
        anchors.verticalCenter: parent.verticalCenter
        source: "../svg/icons/checkbox1.svg"
        visible: checked
        // width:50
        // height:50
        width: 32
        height: 32
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onClicked:  {
            checked = !checked
            OutputDevice.selectFile(filename, checked)
        }
    }
}