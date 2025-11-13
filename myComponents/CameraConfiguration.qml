import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15

Rectangle {
    property var cameraConfig
    color: "tomato"
    Layout.fillWidth: true
    Layout.fillHeight: true
    ColumnLayout {
        // Camera name
        RowLayout {
            Text { text: "Camera Name" }
            TextInput { text: cameraConfig.name }
        }
        // Video file
        Button {
            text: "Choose cameraConfiguration video"
        }
        // Orientation
        RowLayout {
            Text { text: "Rotate (degrees):" }
            TextInput { text: cameraConfig.rotation }
            Text { text: "Flip vertically:" }
            CheckBox { checked: cameraConfig.flip_v}
            Text { text: "Flip horizontally:" }
            CheckBox { checked: cameraConfig.flip_h }
        }    
    }
}
