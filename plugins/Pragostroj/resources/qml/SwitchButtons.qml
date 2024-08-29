import QtQuick.Layouts 1.3
import QtQuick 2.10

// import QtQuick.Controls 1.4
// import QtQuick.Controls.Styles 1.4
import UM 1.3 as UM
import Cura 1.0 as Cura
// import QtGraphicalEffects 1.0

Item {

    Rectangle
    {
        id: buttonsBackground
        width: baseWidth
        color: backgroundGray
        height: 10
    }

    RowLayout
    {
        id: buttons
        width: baseWidth
        spacing: 0

        SwitchButton
        {
            text: 'History'
            page: 1
            onClicked: {
                OutputDevice.updateRecentFiles()
                currentPage = 1
            }
        }
        SwitchButton
        {
            text: 'Machine memory'
            page: 2
            onClicked: {
                OutputDevice.updateMachineMemory()
                currentPage = 2
            }
        }
        SwitchButton
        {
            text: 'Settings'
            page: 3
            onClicked: currentPage = 3
        }
    }

}