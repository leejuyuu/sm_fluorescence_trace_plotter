import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14
import QtCharts 2.14

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

        ChartView {
            id: chart1
            Layout.fillWidth: true
            Layout.fillHeight: true
            legend.visible: false
            margins {left: 0; right: 0; top: 0; bottom: 0}

            // Draw a rectangle as the border of the plot area.
            Rectangle {
                color: 'transparent'
                x: chart1.plotArea.x-1
                y: chart1.plotArea.y-1
                width: chart1.plotArea.width+2
                height: chart1.plotArea.height+2
                border {
                    color: 'black'
                    width: 1.5
                }
            }
            ValueAxis {
                id: axis1x
                gridVisible: false
                labelFormat: '%.0f'
                Component.onCompleted: {
                    axis1x.applyNiceNumbers()
                }
            }
            ValueAxis {
                id: axis1y
                gridVisible: false
                labelFormat: '%.0f'
                Component.onCompleted: {
                    axis1y.applyNiceNumbers()
                }
            }

            LineSeries {
                id: kkk
                name: 'trace1'
                axisX: axis1x
                axisY: axis1y
                width: 1.5
                color: 'green'
                VXYModelMapper {
                    model: traceModel
                    xColumn: 0
                    yColumn: 1
                }
            }
        }
        Rectangle {
            color:'green'
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
        Rectangle {
            color: 'blue'
            Layout.fillWidth: true
            Layout.fillHeight: true
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
