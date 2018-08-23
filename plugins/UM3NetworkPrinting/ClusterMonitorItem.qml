import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

import UM 1.3 as UM
import Cura 1.0 as Cura

Component
{
    Rectangle
    {
        id: monitorFrame
        width: maximumWidth
        height: maximumHeight
        color: UM.Theme.getColor("viewport_background")
        property var emphasisColor: UM.Theme.getColor("setting_control_border_highlight")
        property var lineColor: "#DCDCDC" // TODO: Should be linked to theme.
        property var cornerRadius: 4 * screenScaleFactor // TODO: Should be linked to theme.

        UM.I18nCatalog
        {
            id: catalog
            name: "cura"
        }

        Label
        {
            id: activePrintersLabel
            font: UM.Theme.getFont("large")

            anchors
            {
                top: parent.top
                topMargin: UM.Theme.getSize("default_margin").height * 2 // a bit more spacing to give it some breathing room
                horizontalCenter: parent.horizontalCenter
            }

            text: OutputDevice.printers.length == 0 ? catalog.i18nc("@label: arg 1 is group name", "%1 is not set up to host a group of connected Ultimaker 3 printers").arg(Cura.MachineManager.printerOutputDevices[0].name) : ""

            visible: OutputDevice.printers.length == 0
        }

        Label
        {
            id: queuedLabel
            anchors.left: queuedPrintJobs.left
            anchors.top: parent.top
            anchors.topMargin: 2 * UM.Theme.getSize("default_margin").height
            anchors.leftMargin: 3 * UM.Theme.getSize("default_margin").width
            text: catalog.i18nc("@label", "Queued")
            font: UM.Theme.getFont("large")
            color: UM.Theme.getColor("text")
        }

        ScrollView
        {
            id: queuedPrintJobs

            anchors
            {
                margins: UM.Theme.getSize("default_margin").width
                top: queuedLabel.bottom
                topMargin: 0
                left: parent.left
                bottomMargin: 0
                right: parent.right
                bottom: parent.bottom
            }
            style: UM.Theme.styles.scrollview

            ListView
            {
                anchors.fill: parent
                anchors.margins: UM.Theme.getSize("default_margin").height
                spacing: UM.Theme.getSize("default_margin").height

                model: OutputDevice.queuedPrintJobs

                delegate: PrintJobInfoBlock
                {
                    printJob: modelData
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.rightMargin: UM.Theme.getSize("default_margin").height
                    height: 175 * screenScaleFactor
                }
            }
        }

        PrinterVideoStream
        {
            visible: OutputDevice.activeCamera != null
            anchors.fill: parent
            camera: OutputDevice.activeCamera
        }

        onVisibleChanged:
        {
            if (monitorFrame != null && !monitorFrame.visible)
            {
                // After switching the Tab ensure that active printer is Null, the video stream image
                // might be active
                OutputDevice.setActiveCamera(null)
            }
        }
    }
}
