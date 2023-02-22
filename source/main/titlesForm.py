import os
from os.path import isfile

from source.main.messageBox import messageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt


class titlesForm(QMainWindow):
    def __init__(self, registry):
        super(titlesForm, self).__init__()
        uic.loadUi('source/forms/titlesForm.ui', self)
        self.registry = registry
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.classComboBox.currentIndexChanged.connect(self.load_class_video_names)
        self.videoComboBox.currentIndexChanged.connect(self.load_video_titles)
        self.load_class_names()
        self.savePushButton.clicked.connect(self.set_video_titles)
        self.cancelPushButton.clicked.connect(self.close)

    def load_class_names(self):
        self.class_data_list, status = self.registry.db_handler.get_classes()
        class_name_list = [class_['name'] for class_ in self.class_data_list]
        self.classComboBox.clear()
        self.classComboBox.blockSignals(True)
        self.classComboBox.addItems(class_name_list)
        self.classComboBox.blockSignals(False)
        self.classComboBox.currentIndexChanged.emit(0)

    def load_class_video_names(self):
        video_path = self.class_data_list[self.classComboBox.currentIndex()].get('folder_path')
        scanned_path = os.scandir(video_path)  # Scanning PDF folder for existing files.
        self.video_data = {}
        self.video_name_list = []
        for video_file in scanned_path:
            if isfile(video_file):
                self.video_data[video_file.name] = video_file.path
                self.video_name_list.append(video_file.name)
        self.videoComboBox.clear()
        self.videoComboBox.blockSignals(True)
        self.videoComboBox.addItems(self.video_name_list)
        self.videoComboBox.blockSignals(False)
        self.videoComboBox.currentIndexChanged.emit(0)

    def load_video_titles(self):
        current_video_name = self.videoComboBox.currentText()
        self.video_path = self.video_data.get(current_video_name)
        queryset, status = self.registry.db_handler.get_titles(self.video_path)
        self.old_titles = []
        title_str = ''
        if queryset:
            for item in queryset:
                title_str += item['title'] + '\n'
                self.old_titles.append(item['title'])
        self.titlesTextEdit.setPlainText(title_str)

    def set_video_titles(self):
        if not self.registry.login_object.user_object.add_desc():
            messageBox('خطا', 'شما به این بخش دسترسی ندارید').exec()
            return
        title_str = self.titlesTextEdit.toPlainText()
        title_list = []
        for title in title_str.splitlines():
            if title.strip() != "":
                title_list.append(title.strip())

        queryset, status = self.registry.db_handler.set_titles(self.old_titles, title_list, self.video_path)
        self.close()
