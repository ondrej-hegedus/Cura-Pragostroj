import QtQuick
import QtQuick.Window
import QtWebEngine
import QtQuick.Controls

ApplicationWindow {
    id: cameraWindow
    visible: true
    width: 600
    height: 500
    title: "Camera"

    WebEngineView {
        anchors.fill: parent
        url: "https://www.google.com"
    }
}