import sys
import urllib.request

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Downloader(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QGridLayout()
        layout.setSpacing(10)

        self.label_for_url = QLabel("Enter Url")
        self.url = QLineEdit()

        self.save_loc = QLineEdit()
        self.progress = QProgressBar()

        download = QPushButton("Download")
        browse = QPushButton("Browse")

        layout.addWidget(self.label_for_url, 1, 0)
        layout.addWidget(self.url, 1, 1)

        layout.addWidget(self.save_loc, 2, 1)
        layout.addWidget(browse, 2, 0)

        vlayout = QVBoxLayout()

        vlayout.addLayout(layout)
        self.progress.setMinimumWidth(400)
        vlayout.addWidget(self.progress)
        vlayout.addWidget(download)

        self.save_loc.setDisabled(True)
        self.save_loc.setReadOnly(True)
        self.progress.setVisible(False)
        self.progress.setValue(0)
        self.progress.setAlignment(Qt.AlignCenter)

        self.setLayout(vlayout)
        self.setFocus()
        self.setWindowTitle("Downloader Using Python")
        self.setGeometry(700, 300, 400, 200)

        download.clicked.connect(self.download)
        browse.clicked.connect(self.browse_file)
        self.url.editingFinished.connect(self.is_valid)

    def download(self):
        location = self.save_loc.text()
        url = self.url.text()
        if url is None or url == "" or location is None or location == "":
            self.warning("Enter Data")
            self.url.setFocus()
            return
        try:
            urllib.request.urlretrieve(url, location, self.report)
        except Exception as e:
            QMessageBox.warning(self, "Error", "Download Failed")
            print(f"error occurred while downloading file :: {e}")
            return

        QMessageBox.information(self, "Completed", "Download is completed...")
        self.progress.setValue(0)
        self.save_loc.setText("")

    def browse_file(self):
        if self.url.text().__len__() == 0:
            QMessageBox.warning(self, "Validation", "Enter Url First")
            self.url.setFocus()
            return
        path_save = QFileDialog.getExistingDirectory(self, "Select Download Directory", ".")
        path_save = path_save + "/" + self.url.text().split("/")[-1]
        self.save_loc.setText(QDir.toNativeSeparators(path_save))

    def report(self, num, size, total_size):
        readsofar = num * size
        if total_size > 0:
            percent = readsofar * 100 / total_size
            self.progress.setVisible(True)
            self.progress.setValue(int(percent))

    def is_valid(self):
        if len(self.url.text()) == 0:
            QMessageBox.warning(self, "Validation", "Enter Url")
            self.url.clear()

    def warning(self, msg):
        QMessageBox.warning(self, "Warning", msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Downloader()
    window.show()

    sys.exit(app.exec_())
