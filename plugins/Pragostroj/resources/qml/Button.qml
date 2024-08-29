Rectangle {
    id: buttonRecent

// public
    property string text: 'text'

    signal clicked();

// private
    width: 500;  height: 100 // default size
    border.color: text? 'black': 'green' // Keyboard
    border.width: 0.05 * root.height
    radius:       0.5  * root.height
    opacity:      enabled  &&  !mouseArea.pressed? 1: 0.3 // disabled/pressed state

    Text {
        text: root.text
        font.pixelSize: 0.5 * root.height
        anchors.centerIn: parent
    }

    MouseArea {
        id: mouseArea

        anchors.fill: parent

        onClicked:  root.clicked() // emit
    }
}