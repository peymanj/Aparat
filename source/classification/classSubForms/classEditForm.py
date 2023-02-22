from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt
from source.main.messageBox import messageBox

class classEditForm(QMainWindow):
    
    def __init__(self, registry):
        super().__init__()
        uic.loadUi('source/forms/classEditForm.ui', self)
        self.registry = registry
        self.savePushButton.clicked.connect(self.save)
        self.savePushButton.clicked.connect(self.registry.main_form.classesFormObject.load_class_names)
        self.cancelPushButton.clicked.connect(self.close)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.load_class_data()

    def save(self):
        if not self.check_input():
            return

        class_param = [
            self.classNameLineEdit.text(),
            self.folderPathLineEdit.text().replace('\\','/'),
            self.classPlaylistNameLineEdit.text(),
            self.classAparatCategoryLineEdit.text(),
            self.usernameLineEdit.text(),
            self.passwordLineEdit.text(),
        ]
        queryset, status = self.registry.db_handler.update_class(class_param, self.current_class_name)
        if status:
            messageBox("پیام", "دسته با موفقیت ویرایش شد").exec()
            self.registry.main_form.update_data_signal.emit()
            self.close()
        else:
            messageBox("خطا", "امکان ویرایش دسته وجود ندارد").exec()

    def load_class_data(self):
        
        self.current_class_name = self.registry.main_form.classesFormObject.classComboBox.currentText()
        queryset, status = self.registry.db_handler.get_class(self.current_class_name)
        class_ = queryset[0]
        self.classNameLineEdit.setText(class_['name'])
        self.folderPathLineEdit.setText(class_['folder_path'])
        self.classPlaylistNameLineEdit.setText(class_['playlist_name'])
        self.classAparatCategoryLineEdit.setText(class_['aparat_category'])
        self.usernameLineEdit.setText(class_['username'])
        self.passwordLineEdit.setText(class_['password'])
    
    def check_input(self):
        if (
            self.classNameLineEdit.text() != "" and
            self.folderPathLineEdit.text() != "" and
            # self.classPlaylistNameLineEdit.text() != "" and
            # self.classAparatCategoryLineEdit.text() != "" and
            self.usernameLineEdit.text() != "" and
            self.passwordLineEdit.text() != ""
            ):
            return True
        else:
            messageBox("خطا", "پارامتر های ورودی به درستی وارد نشده است").exec()
            return False
