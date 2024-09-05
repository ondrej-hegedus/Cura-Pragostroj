import QtQuick.Layouts 1.3
import QtQuick 2.10

import QtQuick.Controls 2.0
// import QtQuick.Controls 1.4
// import QtQuick.Controls.Styles 1.4
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Rectangle {
    id: sortButton
    property bool active: true
    property int sortMode: 0
    property string sortLabel: 'Newest'

    signal clicked();

    height: 40
    width: 150
    border.color: customBlue
    border.width: 2
    radius: 20
    Layout.alignment: Qt.AlignHCenter
    anchors.centerIn: parent

    function setSort() {
        sortMode = (sortMode+1)%4
        console.log('sortMode')
        console.log(sortMode)
        switch(sortMode){
            case 0:
                sortLabel = 'Newest'
                break
            case 1:
                sortLabel = 'Oldest'
                break
            case 2:
                sortLabel = 'A-Z'
                break
            case 3:
                sortLabel = 'Z-A'
                break
        }
        OutputDevice.setSort(sortMode)
    }

    Row
    {
        spacing: 1
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        PGRecolorImage
        {
            anchors.verticalCenter: parent.verticalCenter
            // color: customBlue
            height: 15
            width: 15
            source:
            {
                return "../svg/icons/sort.svg"
            }
            sourceSize
            {
                height: height
                width: width
            }
        }
        Label {
            id: sortText
            anchors.verticalCenter: parent.verticalCenter
            text: sortLabel
            font.pixelSize: 20
            color: customBlue
        }
    }

    MouseArea {
        id: mouseArea

        anchors.fill: parent

        onClicked: {
            sortButton.setSort()
        }
    }
}