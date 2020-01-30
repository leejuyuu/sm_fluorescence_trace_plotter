import QtQuick 2.14
import QtCharts 2.14

Item {
    id: root

    property alias traceDataModel: mapper.model
    property int timeColumnNumber: -1   //default: invalid data mapping
    property color traceColor: 'black'

    ChartView {
        id: chart

        anchors.fill: root
        legend.visible: false
        margins {left: 0; right: 0; top: 0; bottom: 0}

        // Draw a rectangle as the border of the plot area.
        Rectangle {
            color: 'transparent'
            x: chart.plotArea.x-1
            y: chart.plotArea.y-1
            width: chart.plotArea.width+2
            height: chart.plotArea.height+2
            border {
                color: 'black'
                width: 1.5
            }
        }

        ValueAxis {
            id: axisX
            gridVisible: false
            labelFormat: '%.0f'
            Component.onCompleted: {
                axisX.applyNiceNumbers()
            }
        }

        ValueAxis {
            id: axisY
            gridVisible: false
            labelFormat: '%.0f'
            Component.onCompleted: {
                axisY.applyNiceNumbers()
            }
        }

        LineSeries {
            name: 'eb_state_trajectory'
            axisX: axisX
            axisY: axisY
            width: 3
            color: 'black'

            HXYModelMapper {
                id: mapper
                model: root.traceDataModel
                xRow: root.timeColumnNumber
                yRow: root.timeColumnNumber + 2
            }
        }

        LineSeries {
            name: 'intensity'
            axisX: axisX
            axisY: axisY
            width: 1.5
            color: root.traceColor

            HXYModelMapper {
                model: root.traceDataModel
                xRow: root.timeColumnNumber
                yRow: root.timeColumnNumber + 1
            }
        }
    }
}
