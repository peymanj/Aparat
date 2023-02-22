from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.sip import setdeleted
from source.main.messageBox import messageBox


class newUserForm(QMainWindow):
	def __init__(self, registry):
		super(newUserForm, self).__init__()
		uic.loadUi('source/forms/newUserForm.ui', self)
		self.registry = registry
		self.cancelPushButton.clicked.connect(self.close)
		self.savePushButton.clicked.connect(self.create_user)
		self.accessComboBox.addItems([self.registry.main_form.usersFormObject.access_name(key=i) \
			for i in self.registry.login_object.user_object.user_access_string[:-1]])

	def create_user(self):
		
		if not self.check_input():
			messageBox("خطا","نام کاربری و یا رمز عبور به درستی وارد نشده است").exec()
			return
		
		if self.passLineEdit.text() != self.passRepLineEdit.text():
			self.messageLabel.setText("رمز های عبور وارد شده مطابقت ندارند")
			return None

		username = self.userLineEdit.text()
		password = self.registry.login_object.encrypt_password(self.passLineEdit.text())
		access = self.registry.main_form.usersFormObject.access_name(value=self.accessComboBox.currentText())

		queryset, status = self.registry.db_handler.get_user_by_name(username)
		if queryset == [] and status:
			queryset, status =  self.registry.db_handler.add_user(username, password, access)
		else:
			messageBox("خطا", "نام کاربری استفاده شده است").exec()
			return 

		if status:
			messageBox("پیام", "کاربر با موفقیت ثبت شد").exec()
			self.close()
		else:
			messageBox("خطا", "امکان ثبت کاربر وجود ندارد").exec()
			return 

	def check_input(self):
		if (
			self.userLineEdit.text() == "" or
			self.passLineEdit.text() == "" or
			self.passRepLineEdit.text() == "" ):
			return False
		else:
			return True
