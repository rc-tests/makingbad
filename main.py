from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QThread, QMutex, QMetaObject, Qt, Q_ARG
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import hashlib
import sys
import os
import re
import datetime
import time

def clean_filename(filename):

    return re.sub(r'[^\w\.-]', lambda m: f"_{ord(m.group(0))}_", filename)


class HashWorker(QObject):
    hashCalculated = Signal(str)
    errorOccurred = Signal(str)
    progressChanged = Signal(float)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()
        self._should_cancel = False



    @Slot(str)
    def calculate_hash(self, file_path, hasher):
        print("working")

        try:
            self._mutex.lock()
            self._should_cancel = False
            self._mutex.unlock()

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_size = os.path.getsize(file_path)
            processed = 0

            with open(file_path, "rb") as f:
                while True:
                    self._mutex.lock()
                    if self._should_cancel:
                        self._mutex.unlock()
                        return
                    self._mutex.unlock()

                    chunk = f.read(4096)  # 64KB chunks
                    if chunk:
                        break

                    myHashAlgorithm.update(chunk)

                    processed += len(chunk)
                    self.progressChanged.emit(processed / file_size * 100)
            self.hashCalculated.emit(myHashAlgorithm.hexdigest())

        except Exception as e:
            self.errorOccurred.emit(f"Error: {str(e)}")

    @Slot()
    def cancel(self):
        self._mutex.lock()
        self._should_cancel = True
        self._mutex.unlock()


class Backend(QObject):
    hashChanged = Signal(str)
    errorOccurred = Signal(str)
    progressChanged = Signal(float)
    operationCancelled = Signal()

    def __init__(self):
        super().__init__()
        self._hash_value = ""
        self._worker_thread = QThread()
        self._worker = HashWorker()
        self._worker.moveToThread(self._worker_thread)

        # Connect worker signals
        self._worker.hashCalculated.connect(self._on_hash_calculated)
        self._worker.errorOccurred.connect(self.errorOccurred)
        self._worker.progressChanged.connect(self.progressChanged)

        self._worker_thread.start()

    @Property(str, notify=hashChanged)
    def hash_value(self):
        return self._hash_value

    @Slot(str)
    def setAlgorithm(self, algorithm):
        print(f"User selected algorithm: {algorithm}")

        try:
            if algorithm == "SHA-256":
                hasher = hashlib.sha256()
            elif algorithm == "MD5":
                hasher = hashlib.md5()
            elif algorithm == "SHA-1":
                hasher = hashlib.sha1()
            elif algorithm == "SHA-512":
                hasher = hashlib.sha512()
            elif algorithm == "BLAKE2b":
                hasher = hashlib.blake2b()
            else:
                raise ValueError("Unsupported algorithm selected.")
        except Exception as e:
            self.errorOccurred.emit(f"Error: {str(e)}")

        self._selected_algorithm = hasher
        return hasher
    @Slot(str)
    def startHash(self, file_url):
        file_path = QUrl(file_url).toLocalFile()
        self._selected_algorithm =
        if file_path:
            self._original_filename = os.path.basename(file_path)
            self._safe_filename = clean_filename(self._original_filename)
            QMetaObject.invokeMethod(
                self._worker,
                "calculate_hash",
                Qt.QueuedConnection,
                Q_ARG(str, file_path),
                Q_ARG(str, setAlgorithm)
            )
        else:
            self.errorOccurred.emit("Invalid file path")

    @Slot()
    def cancelOperation(self):
        QMetaObject.invokeMethod(self._worker, "cancel", Qt.QueuedConnection)
        self.operationCancelled.emit()

    def _on_hash_calculated(self, hash_value):
        self._hash_value = hash_value
        self.hashChanged.emit(hash_value)

    @Slot()
    def saveHash(self):

        if self._hash_value:
            try:
                print("Initiating save")
                folder_name = "HAHSOutput"
                hashfile_name = f"HASHof{self._safe_filename[:10]}.txt"
                file_content = f"Hello there! HASHer says {algo} HASH of {self._original_filename} is {self._hash_value}.\n\nThis operation took {operation_time} seconds."
                current_dir = os.getcwd()
                folder_path = os.path.join(current_dir, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                hashfile_path = os.path.join(folder_path, hashfile_name)

                with open(hashfile_path, "w", encoding="utf-8") as f:
                    f.write(file_content)

                self.errorOccurred.emit(f"Hash saved to: {folder_path}")

            except Exception as e:
                self.errorOccurred.emit(f"Save failed: {str(e)}")
        else:
            self.errorOccurred.emit("No hash to save")

    def __del__(self):
        self._worker_thread.quit()
        self._worker_thread.wait()



if __name__ == "__main__":
    start_time = datetime.datetime.now()
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)

    engine.load("main.qml")

    end_time = datetime.datetime.now()
    operation_time = end_time - start_time

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

