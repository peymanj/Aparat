from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt
from source.main.messageBox import messageBox


class newClassForm(QMainWindow):
    
    def __init__(self, registry):
        super().__init__()
        uic.loadUi('source/forms/newClassForm.ui', self)
        self.registry = registry
        self.savePushButton.clicked.connect(self.add_class_to_db)
        self.cancelPushButton.clicked.connect(self.close)
        self.openFolderPushButton.clicked.connect(self.load_folder_directory)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def add_class_to_db(self):
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
        queryset, status = self.registry.db_handler.add_class(class_param)
        if status:
            self.registry.main_form.update_data_signal.emit()
            self.close()
        else:
            messageBox("خطا", "امکان اضافه کردن دسته وجود ندارد").exec()
        
    def load_folder_directory(self):
        options = QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        options |= QFileDialog.DontResolveSymlinks
        folder_name= QFileDialog.getExistingDirectory(self, options=options)
        if folder_name:
            self.folderPathLineEdit.setText(folder_name)

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

