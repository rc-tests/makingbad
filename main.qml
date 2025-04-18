import QtQuick 6.2
import QtQuick.Controls 6.2
import QtQuick.Layouts 6.2
import QtQuick.Window 6.2

Window {
    id: mainWindow
    visible: true
    width: 500
    height: 400
    title: "HASH your file"
    color: "#ffe6f0"

    property string droppedPath: ""

    StackLayout {
        id: views
        anchors.fill: parent

        // Drop Page
        Item {
            id: dropView
            Layout.fillWidth: true
            Layout.fillHeight: true

            Column {
                anchors.centerIn: parent
                spacing: 20

                Rectangle {
                    id: dropArea
                    width: 300
                    height: 100
                    color: "#ffb3c6"
                    radius: 20
                    border.color: "white"
                    border.width: 2

                    Text {
                        anchors.centerIn: parent
                        text: "Drop File Here"
                        color: "white"
                        font.pixelSize: 16
                    }

                    DropArea {
                        anchors.fill: parent
                        onDropped: (drop) => {
                            let fileUrl = drop.urls[0]
                                       mainWindow.droppedPath = decodeURIComponent(fileUrl.toString().replace("file:///", ""))
                                          errorText.text = ""
                        }
                    }
                }

                Text {
                    id: errorText
                    text: ""
                    color: "#7d0243"
                    visible: text !== ""
                    
                }


                Button {
                    text: "Start"
                    onClicked: {
                        if (mainWindow.droppedPath === "") {
                                   errorText.text = "Please enter a file"
                               } else {
                                   errorText.text = ""
                                    backend.startHash(mainWindow.droppedPath)
                                    views.currentIndex = 1
                        }
                    }
                }
            }
        }

        // Working View
        Item {
            id: workingView
            Layout.fillWidth: true
            Layout.fillHeight: true

            Column {
                anchors.centerIn: parent
                spacing: 20

                Text {
                    text: "Hashing in progress..."
                    color: "black"
                }

                Button {
                    text: "Cancel"
                    onClicked: {
                        backend.cancelHash()
                        views.currentIndex = 0
                    }
                }
            }
        }

        // Result View
        Item {
            id: resultView
            Layout.fillWidth: true
            Layout.fillHeight: true

            Column {
                anchors.centerIn: parent
                spacing: 20

                Text {
                    id: hashOutput
                    text: "MD5: (waiting...)"
                    wrapMode: Text.Wrap
                    width: parent.width * 0.8
                }

                Button {
                    text: "Save"
                    onClicked: backend.saveHash(mainWindow.droppedPath)
                }

                Button {
                    text: "Restart"
                    onClicked: {
                        mainWindow.droppedPath = ""
                        hashOutput.text = ""
                        views.currentIndex = 0
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
        function onHashReady(hash) {
            hashOutput.text = "MD5: " + hash
            views.currentIndex = 2
        }
    }
}
