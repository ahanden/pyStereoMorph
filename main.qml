import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "HelloApp"

    RowLayout {
        anchors.fill: parent
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 120
            Layout.maximumWidth: parent.width * 0.25
            Rectangle {
                color: "darkseagreen"
                Layout.fillWidth: true
                height: 120
                Text {
                    text: "Board"
                }
            }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                ListView {
                    clip: true
                    model: cameraModel
                    orientation: Qt.Vertical
                    spacing: 5
                    delegate: Rectangle {
                        id: cameraItem
                        color: "lightsteelblue"
                        height: 120
                        width: parent.width
                        Text {
                            text: display
                        }
                    }
                }
            }
            Button {
                text: "Add Camera"
                onClicked: addCameraBtn.click()
            }
        }
        Rectangle {
            color: "tomato"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Text {
                text: "Focus Box"
            }
        }
    }
}
