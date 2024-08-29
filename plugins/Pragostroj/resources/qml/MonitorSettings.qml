import QtQuick 2.10
import QtQuick.Controls 2.0
import UM 1.3 as UM


Rectangle
{
        id: settings
        width: parent.width
        height: parent.height

        visible:
        {
               return currentPage == 3
        }


        Column
        {
            width: parent.width - 350
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "Machine name"
                    font.pixelSize: 18
                    //width: 700
                    anchors.left: parent.left
                }
                Label
                {
                    text: OutputDevice.getPrinterName
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }
            Spacer
            {
            }
            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "Model"
                    font.pixelSize: 18
                    //width: 700
                }
                Label
                {
                    text: OutputDevice.getMachineModel
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }
            Spacer
            {
            }
            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "Serial number"
                    font.pixelSize: 18
                    //width: 700
                }
                Label
                {
                    text: OutputDevice.getMachineSerialNumber
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }

            Spacer
            {
            }
            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "Product code"
                    font.pixelSize: 18
                    //width: 700
                }
                Label
                {
                    text: OutputDevice.getMachineProductCode
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }

            Spacer
            {
            }
            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "Version"
                    font.pixelSize: 18
                    //width: 700
                }
                Label
                {
                    text: OutputDevice.getBackendVersion
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }

            Spacer
            {
            }
            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "Storage available"
                    font.pixelSize: 18
                    //width: 700
                }
                Label
                {
                    text: OutputDevice.getStorageAvailable
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }

            Spacer
            {
            }
            Rectangle
            {
                height: 30
                width: parent.width
                Label
                {
                    text: "IP address"
                    font.pixelSize: 18
                    //width: 700
                }
                Label
                {
                    text: OutputDevice.address
                    font.pixelSize: 18
                    anchors.right: parent.right
                }
            }
        }
}