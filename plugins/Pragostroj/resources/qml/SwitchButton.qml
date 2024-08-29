import QtQuick.Layouts 1.3
import QtQuick 2.10

// import QtQuick.Controls 1.4
// import QtQuick.Controls.Styles 1.4
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Rectangle {
    Layout.alignment: Qt.AlignHCenter
    Layout.preferredWidth: Math.round((parent.width)/3)
    Layout.leftMargin: 0
    Layout.rightMargin: 0
    color: currentPage == page ? '#ffffff': backgroundGray
    border.color: customGray
    border.width: 1
    radius: 10


// public
    property string text: 'text'
    property int page: 0

    signal clicked();

// private
//    width: Math.round(parent.width -20 /4)
    height: 50

    Text {
        text: parent.text
        anchors.centerIn: parent
        font.pixelSize: 20
        color: currentPage == page ? '#48a8de': customGray
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        onClicked:  parent.clicked() // emit
    }

    Rectangle
    {
        height: 15
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        visible: currentPage == page
        anchors.leftMargin: 1
        anchors.rightMargin: 1
    }

}