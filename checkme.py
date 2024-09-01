import sys
import os
import csv
from qtpy.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget, QListWidgetItem
from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 1000, 600)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.prev_button = QPushButton("Previous(b)", self)
        self.prev_button.clicked.connect(self.show_prev_image)

        self.next_button = QPushButton("Next(n)", self)
        self.next_button.clicked.connect(self.show_next_image)

        self.load_button = QPushButton("Load Directory", self)
        self.load_button.clicked.connect(self.load_directory)

        self.correct_button = QPushButton("True(t)", self)
        self.correct_button.clicked.connect(lambda: self.mark_image("正确"))

        self.incorrect_button = QPushButton("False(f)", self)
        self.incorrect_button.clicked.connect(lambda: self.mark_image("错误"))

        self.file_list = QListWidget(self)
        self.file_list.itemClicked.connect(self.on_file_list_item_clicked)

        hbox = QHBoxLayout()
        hbox.addWidget(self.prev_button)
        hbox.addWidget(self.next_button)
        hbox.addWidget(self.correct_button)
        hbox.addWidget(self.incorrect_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addLayout(hbox)
        vbox.addWidget(self.load_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(vbox)
        main_layout.addWidget(self.file_list)
        # 设置file_list的最大宽度
        self.file_list.setMaximumWidth(600)

        self.setLayout(main_layout)

        self.image_files = []
        self.current_index = -1
        self.csv_file = "image_status.csv"
        self.image_status = {}

    def load_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.csv_file = os.path.join(directory, "image_status.csv")
            if os.path.exists(self.csv_file):
                self.load_csv()
            else:
                self.image_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.jpg', '.jpeg', '.png'))]
                self.image_files.sort()
                self.image_status = {os.path.basename(f): "未标记" for f in self.image_files}
                self.save_csv()
            self.current_index = 0
            self.update_file_list()
            self.show_image()

    def load_csv(self):
        with open(self.csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.image_status = {row["文件名"]: row["识别状态"] for row in reader}
            self.image_files = [os.path.join(os.path.dirname(self.csv_file), filename) for filename in self.image_status.keys()]

    def save_csv(self):
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["文件名", "识别状态"])
            for filename, status in self.image_status.items():
                writer.writerow([filename, status])

    def update_file_list(self):
        self.file_list.clear()
        for filename, status in self.image_status.items():
            item = QListWidgetItem(f"{filename} - {status}")
            self.file_list.addItem(item)

    def show_image(self):
        if self.image_files and 0 <= self.current_index < len(self.image_files):
            image_path = self.image_files[self.current_index]
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.update_file_list()
            self.highlight_current_file()

    def highlight_current_file(self):
        if self.image_files and 0 <= self.current_index < len(self.image_files):
            current_file = os.path.basename(self.image_files[self.current_index])
            for index in range(self.file_list.count()):
                item = self.file_list.item(index)
                if current_file in item.text():
                    self.file_list.setCurrentItem(item)
                    break

    def show_prev_image(self):
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def show_next_image(self):
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_B:
            self.show_prev_image()
        if event.key() == Qt.Key_N:
            self.show_next_image()
        elif event.key() == Qt.Key_T:
            self.mark_image("正确")
        elif event.key() == Qt.Key_F:
            self.mark_image("错误")

    def mark_image(self, status):
        if self.image_files and 0 <= self.current_index < len(self.image_files):
            filename = os.path.basename(self.image_files[self.current_index])
            self.image_status[filename] = status
            self.save_csv()
            self.show_next_image()

    def on_file_list_item_clicked(self, item):
        filename = item.text().split(" - ")[0]
        self.current_index = self.image_files.index(os.path.join(os.path.dirname(self.csv_file), filename))
        self.show_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())