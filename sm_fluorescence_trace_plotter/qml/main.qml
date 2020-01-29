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

        TraceChart {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Somehow, when the variable name and the property name collide, the plot
            // won't show properly
            traceDataModel: traceModel
            traceColor: 'red'
            timeColumnNumber: 0
        }

        TraceChart {
            Layout.fillWidth: true
            Layout.fillHeight: true
            traceDataModel: traceModel
            traceColor: 'green'
            timeColumnNumber: 0
        }

        TraceChart {
            Layout.fillWidth: true
            Layout.fillHeight: true
            traceDataModel: traceModel
            traceColor: 'blue'
            timeColumnNumber: 0
        }

        ListView {

            Layout.rowSpan: 2
            Layout.fillHeight: true
            Layout.preferredWidth: gridLayout.width * 0.4
            Layout.minimumWidth: 200
            model: traceInfoModel
            orientation: ListView.Vertical
            interactive: false
            spacing: 10

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
                            id: listTextField

                            anchors.fill: parent
                            text: focus ? model.edit : model.value
                            font.pointSize: 12
                            selectByMouse: true                            

                            onFocusChanged: {
                                if (focus){}
                                else{ editingFinished() }
                            }

                            onEditingFinished: {
                                focus = false
                                model.edit = text
                            }
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

        Rectangle {
            Layout.rowSpan: 1
            Layout.preferredWidth: gridLayout.width * 0.4
            Layout.fillHeight: true

            Button {
                text: 'Debug trace info'
                onClicked: traceInfoModel.debug()
                anchors.centerIn: parent
            }
        }
    }

    Text {
        anchors.fill: parent
        text: 'hello'
        TextField {
            id:ttt
        }

        Component.onCompleted: {console.log(ttt.implicitHeight.toString())
            console.log(ttt.implicitWidth.toString())
            console.log(ttt.leftPadding)
        }
    }




}
