import QtQuick.Layouts 1.3
import QtQuick 2.10

import QtQuick.Controls 2.1
// import QtQuick.Controls.Styles 1.4
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Rectangle {
    id: qbutton
    property string text: ''
    property string icon: 'none'
    property bool active: true
    signal clicked();

    height: 40
    width: 150
    border.color: qbutton.active?customBlue:'gray'
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
            visible: icon != "none"
            // color: qbutton.active ? customBlue: 'gray'
            height: qbutton.text==""?25:15
            width: qbutton.text==""?25:15
            source:
            {
                return "../svg/icons/"+icon+".svg"
            }
            sourceSize
            {
                height: height
                width: width
            }
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            visible: qbutton.text!=""
            text: qbutton.text
            font.pixelSize: 20
            color: qbutton.active ? customBlue : 'gray'
        }
    }

    MouseArea {
        id: mouseArea

        anchors.fill: parent

        onClicked: {
            if(parent.active){
                parent.clicked() // emit
            }
        }
    }
}