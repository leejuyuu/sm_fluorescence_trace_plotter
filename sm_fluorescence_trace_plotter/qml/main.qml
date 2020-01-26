import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14

Item {
    id: root

    // For attracting focus when clicked to leave TextField focused state
    MouseArea {
        anchors.fill: parent
        onClicked: {focus=true}

    }

    GridLayout {
        id: gridLayout
        flow: GridLayout.TopToBottom
        rows: 3
        anchors {
            fill: parent
            margins: 40
        }

        Rectangle {
            color: 'red'
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.columnSpan: 2

        }
        Rectangle {
            color:'green'
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.columnSpan: 2

        }
        Rectangle {
            color: 'blue'
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.columnSpan: 2


        }
        ListView {

            Layout.rowSpan: 3
            Layout.fillHeight: true
            //Layout.preferredWidth: 200
            Layout.preferredWidth: gridLayout.width * 0.4
            Layout.minimumWidth: 200
            model: traceInfoModel
            orientation: ListView.Vertical
            interactive: false
            spacing: 10

            //            delegate: Rectangle {
            //                implicitHeight: 40
            //                implicitWidth: 100

            //            }
            delegate: Item {
                id: entryRoot
                implicitHeight: 40

                anchors {leftMargin: 25; rightMargin: 25; left: parent.left; right: parent.right }
                Item {
                    anchors {rightMargin: entryRoot.width*0.6; fill: entryRoot}
                    Text {
                        anchors.fill: parent
                        text: model.propertyName + ':'
                        verticalAlignment: Text.AlignVCenter
                        font.pointSize: 12
                    }
                }

                Loader {
                    anchors {leftMargin: entryRoot.width * 0.4; fill: entryRoot }
                    sourceComponent: model.isEditable ? editableTextComp : nonEditTextComp

                    Component {
                        id: editableTextComp
                        TextField {
                            anchors.fill: parent
                            text: model.value
                            selectByMouse: true
                            font.pointSize: 12


                        }

                    }
                    Component {
                        id: nonEditTextComp
                        Text {
                            anchors {leftMargin: 10; fill: parent}
                            text: model.value
                            verticalAlignment: Text.AlignVCenter
                            font.pointSize: 12
                        }
                    }
                }


            }

        }
    }

    Text {
        anchors.fill: parent
        text: 'hello'
        TextField{
            id:ttt
        }

        Component.onCompleted: {console.log(ttt.implicitHeight.toString())
            console.log(ttt.implicitWidth.toString())
            console.log(ttt.leftPadding)
        }
    }




}
