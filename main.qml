import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import "myComponents"

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
            Text { text: "Calibration Board" }
            Rectangle {
                color: "darkseagreen"
                Layout.fillWidth: true
                height: 120
                Text {
                    text: "Board"
                }
            }
            Text { text: "Cameras" }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ListView {
                    id: cameraList
                    clip: true
                    model: cameraModel
                    orientation: Qt.Vertical
                    spacing: 5
                    //delegateModelAccess: DelegateModel.ReadOnly
                    delegate: Rectangle {
                        color: "lightsteelblue"
                        height: 130
                        width: parent.width
                        ColumnLayout {
                            Text {
                                text: display.name
                            }
                            RowLayout {
                                CheckBox { checkable: false }
                                Text { text: "Video File Selected" }
                            }
                            RowLayout {
                                CheckBox { checkable: false }
                                Text { text: "Calibrated" }
                            }
                            Button {
                                text: "Configure"
                                onClicked: focusConfig(index)
                            }
                        }
                    }
                }
            }
            Button {
                text: "Add Camera"
                onClicked: addCameraBtn.click()
            }
        }
        CameraConfiguration { 
            cameraConfig: focusArea
        }
        /*Rectangle {
            color: "tomato"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Text {
                text: "Focus Box"
            }
        }*/
    }
}
