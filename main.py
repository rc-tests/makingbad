import os
import hashlib
import threading
import time
from datetime import datetime
import re
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, QThread


def safe_filename(filename):
    return re.sub(r'[^\w.-]', lambda x: f'_{ord(x.group(0))}_', filename)


class HashWorker(QThread):
    hash_ready = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self._is_running = True

    def run(self):
        try:
            with open(self.path, "rb") as f:
                md5 = hashlib.md5()
                while chunk := f.read(8192):
                    if not self._is_running:
                        return
                    md5.update(chunk)
                self.hash_ready.emit(md5.hexdigest())
        except Exception as e:
            self.hash_ready.emit(f"Error: {str(e)}")

    def stop(self):
        self._is_running = False


        class Backend(QObject):
            hashReady = Signal(str)

            def __init__(self):
                super().__init__()
                self.hash_value = ""
                self._is_running = False
                self.worker_thread = None
                self.hashed_file_name = ""

            def startHash(self, file_path):
                self._is_running = True
                self.hash_value = ""
                self.hashed_file_name = os.path.basename(file_path)
                self.worker_thread = threading.Thread(target=self._calculate_hash, args=(file_path,))
                self.worker_thread.start()

            def _calculate_hash(self, file_path):
                try:
                    hasher = hashlib.md5()
                    with open(file_path, 'rb') as f:
                        while True:
                            if not self._is_running:
                                return
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            hasher.update(chunk)
                    self.hash_value = hasher.hexdigest()
                    self.hashReady.emit(self.hash_value)
                except Exception as e:
                    self.hash_value = f"Error: {str(e)}"
                    self.hashReady.emit(self.hash_value)

    @Slot()
    def cancelHash(self):
        if self.worker:
            self.worker.stop()

    def send_hash(self, hash_value):
        self.hash_result = hash_value
        self.hashReady.emit(hash_value)

    @Slot(str)
    def saveHash(self):
        if self.hash_value:
            # Create the folder inside ~/Documents/HASHoutputs
            documents_dir = os.path.expanduser("~/Documents")
            output_dir = os.path.join(documents_dir, "HASHoutputs")
            os.makedirs(output_dir, exist_ok=True)

            # Clean and shorten filename
            safe_filename = "HASHof" + self.hashed_file_name[:10].replace(" ", "_").replace("'", "").replace("\"", "")
            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Full save path
            save_path = os.path.join(output_dir, f"{safe_filename}.txt")

            with open(save_path, 'w') as f:
                f.write(f"Hello there! HASHer says HASH of {self.hashed_file_name} is {self.hash_value} at {timestamp}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load("main.qml")
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
