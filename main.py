from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QThread, QMutex, QMetaObject, Qt, Q_ARG
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import hashlib
import sys
import os
import re
import datetime

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



    @Slot(str, str)
    def calculate_hash(self, file_path, myHashAlgorithm):
        
        print("calculate_hash is called")

        try:
            self._mutex.lock()
            self._should_cancel = False
            self._mutex.unlock()

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_size = os.path.getsize(file_path)
            processed = 0

            #hasher = getattr(hashlib, myHashAlgorithm)()
            hasher = getattr(hashlib, myHashAlgorithm)()

            with open(file_path, "rb") as f:
                print("File is opened")
                while True:
                    self._mutex.lock()
                    if self._should_cancel:
                        self._mutex.unlock()
                        return
                    self._mutex.unlock()

                    chunk = f.read(4096) 
                    if not chunk:
                        break
                    print("File is read")
                    hasher.update(chunk)

                    processed += len(chunk)
                    self.progressChanged.emit(processed / file_size * 100)
                print("hash sent to hashCalculated")
                self.hashCalculated.emit(hasher.hexdigest())
                
        except Exception as e:
            self.errorOccurred.emit(f"Error N: {str(e)}")

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
    startHashSignal = Signal(str, str)

    def __init__(self):
        super().__init__()
        self._hash_value = ""
        self._worker_thread = QThread()
        self._worker = HashWorker()
        self._worker.moveToThread(self._worker_thread)
        self._selected_algorithm = "sha256"
        if ConnectionError:
            print(ConnectionError)
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
                self._selected_algorithm ="sha256" #hashlib.sha256()
            elif algorithm == "MD5":
                self._selected_algorithm = "md5" # hashlib.md5()
            elif algorithm == "SHA-1":
                self._selected_algorithm = "sha1" #hashlib.sha1()
            elif algorithm == "SHA-512":
                self._selected_algorithm = "sha512" #hashlib.sha512()
            else:
                raise ValueError("Unsupported algorithm selected.")
        except Exception as e:
            self.errorOccurred.emit(f"Error: {str(e)}")
        
    
    @Slot(str)
    def startHash(self, file_url):
        file_path = QUrl(file_url).toLocalFile()
        print("startHash is called")
        if file_path and hasattr(self, "_selected_algorithm"):
            self._original_filename = os.path.basename(file_path)
            self._safe_filename = clean_filename(self._original_filename)
            algorithm_name = self._selected_algorithm

            #self.startHashSignal.emit(file_path, algorithm_name)
            self._worker.calculate_hash(file_path, algorithm_name)

        else:
            self.errorOccurred.emit("Invalid file path")

    @Slot()
    def cancelOperation(self):
        QMetaObject.invokeMethod(self._worker, "cancel", Qt.QueuedConnection)
        self.operationCancelled.emit()

    def _on_hash_calculated(self, hash_value):
        print("_on_hash_calculated is called")
        self._hash_value = hash_value
        self.hashChanged.emit(hash_value)

    @Slot()
    def saveHash(self):

        if self._hash_value:
            try:
                print("Initiating save")
                folder_name = "HASHOutput"
                hashfile_name = f"HASHof{self._safe_filename[:10]}.txt"
                file_content = f"Hello there! HASHer says {self._selected_algorithm} HASH of {self._original_filename} is {self._hash_value}.\n\nThis operation took {operation_time} seconds."
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
