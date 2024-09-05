import QtQuick.Layouts 1.3
import QtQuick 2.10

import QtQuick.Controls 2.1
// import QtQuick.Controls.Styles 1.4
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Rectangle {
    id: cameraButton
    property string text: ''
    property string icon: 'none'
    property string address: ''
    property bool active: true
    signal clicked();

    height: 40
    width: 80
    border.color: cameraButton.active ? customBlue: 'gray'
    border.width: 2
    radius: 20
    Layout.alignment: Qt.AlignHCenter

    Row
    {
        spacing: 1
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        PGRecolorImage
        {
            anchors.verticalCenter: parent.verticalCenter
            // color: cameraButton.active ? customBlue: 'gray'
            // color: cameraButton.active ? 'blue': 'gray'
            height: 25
            width: 44

            source:
            {
                // return "../svg/icons/camera.svg"
                return cameraButton.active ? "../svg/icons/camera.svg":"../svg/icons/gray_camera.svg"
            }
            sourceSize
            {
                height: height
                width: width
            }
        }
    }

    MouseArea {
        id: mouseArea

        anchors.fill: parent

        // onClicked: {
        //     if(parent.active){
        //         parent.clicked() // emit
        //     }
        // }

        // onClicked: {
        //     var component = Qt.createComponent("CameraWindow.qml")
        //     var window    = component.createObject(mouseArea)
        //     window.show()
        // }
        onClicked: {
            // Qt.openUrlExternally("http://google.com")
            Qt.openUrlExternally(cameraButton.address)
        }

    }
}