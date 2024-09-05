import QtQuick 2.10

Rectangle
{
    property int space: 0
    width: parent.width - 2 * space
    //leftPadding: space
    anchors.leftMargin: 100
    height: 1
    color: customGray
}