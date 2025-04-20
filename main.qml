import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 600
    height: 400
    title: "HASHer - File Hash Calculator"

    Rectangle {
        id: dropArea
        width: parent.width - 40
        height: 200
        color: "#f8f9fa"
        border.color: "#6c757d"
        border.width: 2
        radius: 10
        anchors.centerIn: parent
        visible: true

   

        Text {
            id: dropText
            anchors.centerIn: parent
            text: "Drop file here to calculate hash"
            font.bold: true
            font.pixelSize: 16
            color: "#495057"
        }

        }
        

        DropArea {
            anchors.fill: parent
            onEntered: {
                dropArea.border.color = "#28a745"
                dropText.text = "Release to calculate hash"
            }
            onExited: {
                dropArea.border.color = "#6c757d"
                dropText.text = "Drop file here to calculate hash"
            }
            onDropped: (drop) => {
                if (drop.hasUrls && drop.urls.length > 0) {
                    backend.startHash(drop.urls[0])
                    progress.visible = true
                    cancelButton.visible = true
                }
            }
        }

    ComboBox {
        id: hashDropdown
        width: 200
        model: ["SHA-256", "MD5", "SHA-1", "SHA-512"]
        currentIndex: 0
        anchors.top: dropArea.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        onCurrentTextChanged: {
        backend.setAlgorithm(currentText)
        }
    }  

    
    Button {
        text: "Exit"
        anchors.bottom: ComboBox.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        onClicked: Qt.quit()
    }

    BusyIndicator {
        id: progress
        anchors.centerIn: parent
        visible: false
        width: 64
        height: 64
    }

    ProgressBar {
        id: progressBar
        anchors.top: progress.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width * 0.8
        visible: progress.visible
        value: 0
    }

    Button {
        id: cancelButton
        text: "Cancel"
        visible: false 
        onClicked: {
            backend.cancelOperation()
            progress.visible = false
            cancelButton.visible = false
            progressBar.value = 0
        }
    }

    Rectangle {
        id: resultPage
        width: parent.width
        height: parent.height
        color: "#e9ecef"
        visible: false

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            Text {
                id: hashLabel
                text: "HASH of your file: " + backend.hash_value
                font.bold: true
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }

            Button {
                text: "Save to File"
                Layout.alignment: Qt.AlignHCenter
                onClicked: backend.saveHash()
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 20

                Button {
                    text: "Restart"
                    onClicked: {
                        resultPage.visible = false
                        dropArea.visible = true
                        dropText.text = "Drop file here to calculate hash"
                    }
                }

                Button {
                    text: "Exit"
                    onClicked: Qt.quit()
                }
            }
        }
    }

    Connections {
        target: backend
        function onHashChanged(hash) {
            resultPage.visible = true
            dropArea.visible = false
            progress.visible = false
            cancelButton.visible = false
            progressBar.value = 0
        }

        function onErrorOccurred(message) {
            dropText.text = message
            dropArea.border.color = "#dc3545"
            progress.visible = false
            cancelButton.visible = false
            progressBar.value = 0
            errorTimer.start()
        }

        function onProgressChanged(value) {
            progressBar.value = value
        }

        function onOperationCancelled() {
            dropText.text = "Operation cancelled"
            dropArea.border.color = "#ffc107"
            progress.visible = false
            cancelButton.visible = false
            progressBar.value = 0
            errorTimer.start()
        }
    }

    Timer {
        id: errorTimer
        interval: 60000
        onTriggered: {
            dropText.text = "Drop file here to hash"
            dropArea.border.color = "#6c757d"
        }
    }
}