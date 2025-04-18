import sys
import hashlib
import os
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
        self.worker = None
        self.hash_result = ""

    @Slot(str)
    def startHash(self, filepath):
        if self.worker and self.worker.isRunning():
            return
        self.worker = HashWorker(filepath)
        self.worker.hash_ready.connect(self.send_hash)
        self.worker.start()

    @Slot()
    def cancelHash(self):
        if self.worker:
            self.worker.stop()

    def send_hash(self, hash_value):
        self.hash_result = hash_value
        self.hashReady.emit(hash_value)

    @Slot(str)
    def saveHash(self, filepath):
        try:
            base = os.path.basename(filepath)
            safe = safe_filename(base[:10])
            with open(f"HASHof{safe}.txt", "w") as f:
                f.write(self.hash_result)
        except Exception as e:
            print(f"Failed to save: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load("main.qml")
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
