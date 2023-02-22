from PyQt5 import QtWidgets, uic
from hashlib import sha256, md5
from . import userAccess
from PyQt5.QtCore import pyqtSignal
from source.main.mainForm import mainForm


class login(QtWidgets.QMainWindow):

    
    login_signal = pyqtSignal()
    
    def __init__(self, registry) -> None:
        super(login, self).__init__()
        uic.loadUi('source/forms/loginForm.ui', self)
        self.userLineEdit.setFocus()
        self.loginPushButton.clicked.connect(lambda: self.validate(registry))
        self.cancelPushButton.clicked.connect(self.close)
        self.show()

    def validate(self, registry):
        username = self.userLineEdit.text()
        password = self.passLineEdit.text()
        pass_enc = self.encrypt_password(password)
        
        queryset, status = registry.db_handler.login(username, pass_enc)

        if queryset !=[] and status:
            
            registry.main_form = mainForm(registry)

            self.create_user_object(queryset[0]['user'], queryset[0]['access'])

            self.login_signal.emit()
            self.close()
        else:
            self.messageLabel.setText("نام کاربری یا رمز عبور اشتباه است.")

    def encrypt_password(self, password):
        sha1_pass = sha256(password.encode()).hexdigest()
        md5_pass = md5(sha1_pass.encode()).hexdigest()
        return md5_pass

    def create_user_object(self, username, user_access):
        if user_access == 'superuser':
            self.user_object = userAccess.superuser()
        elif user_access == 'main_admin':
            self.user_object = userAccess.mainAdmin()
        elif user_access == 'admin':
            self.user_object = userAccess.admin()
        elif user_access == 'guest':
            self.user_object = userAccess.guest()

        self.user_object.username = username
