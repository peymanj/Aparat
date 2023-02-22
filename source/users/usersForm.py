from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem
from PyQt5 import uic
from source.main.messageBox import messageBox
from .usersSubForm.newUserForm import newUserForm
from PyQt5.QtCore import Qt


class usersForm(QMainWindow):
	
	def __init__(self, registry):
		super(usersForm, self).__init__()
		uic.loadUi('source/forms/usersForm.ui', self)
		self.registry = registry
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.userLineEdit.setText(self.registry.login_object.user_object.username)
		self.cancelPushButton.clicked.connect(self.close)
		self.savePushButton.clicked.connect(self.update_user)
		self.usersTableWidget.doubleClicked.connect(self.load_user_for_edit)
		self.deleteUserPushButton.clicked.connect(self.delete_user)
		self.newUserPushButton.clicked.connect(self.create_newUserForm)
		self.load_users()
		# if loginObject.is_admin():
		# 	self.otherUsersPushButton.setEnabled(True)

		# if loginObject.is_admin():
		# 	self.usersTableWidget.setHidden(False)
			# self.resize(self.centralwidget.sizeHint())

	def update_user(self):
		
		if not self.check_input():
			messageBox("خطا","نام کاربری و یا رمز عبور به درستی وارد نشده است").exec()
			return

		if self.newPassLineEdit.text() != self.newPassRepLineEdit.text():
			self.messageLabel.setText("رمز های عبور وارد شده مطابقت ندارند")
			return False

		username = self.userLineEdit.text()
		old_password = self.registry.login_object.encrypt_password(self.oldPassLineEdit.text())
		new_password = self.registry.login_object.encrypt_password(self.newPassLineEdit.text())
		# new_password_rep = self.registry.login_object.encrypt_password(self.newPassRepLineEdit.text())

		if username == self.registry.login_object.user_object.username:
			queryset, status = self.registry.db_handler.update_current_user(username, old_password, new_password)
		else:
			queryset, status =  self.registry.db_handler.update_other_user(username, new_password)

		if status and queryset != []:
			messageBox("پیام", "رمز عبور با موفقیت تغییر یافت.").exec()
			self.close()
		else:
			messageBox("خطا", "نام کاربری یا رمز عبور وارد شده صحیح نیست").exec()
			return

	def check_input(self):
		if (
			self.userLineEdit.text() == "" or
			(self.oldPassLineEdit.text() == "" and self.oldPassLineEdit.isEnabled())  or 
			self.newPassLineEdit.text() == "" or
			self.newPassRepLineEdit.text() == "" ):
			return False
		else:
			return True

	def load_users(self):

		if self.registry.login_object.user_object.user_access_string[:-1] ==[]:
			queryset1 = []
		else:
			queryset1, status =  self.registry.db_handler.get_users(self.registry.login_object.user_object.user_access_string[:-1])
		
		queryset2, status =  self.registry.db_handler.get_user_by_name(self.registry.login_object.user_object.username)
		queryset = queryset1 + queryset2

		if not queryset:
			return
		self.set_users_table(queryset)

	def set_users_table(self, users_data_list):
		headers = ['یوزر', 'دسترسی']
		self.usersTableWidget.setColumnCount(len(headers))
		self.usersTableWidget.setHorizontalHeaderLabels(headers)
		self.usersTableWidget.setRowCount(0)
		if users_data_list:
			self.usersTableWidget.setRowCount(len(users_data_list))
		
			for row, sequence in enumerate(users_data_list):
				column = 0
				for counter, (key, value) in enumerate(sequence.items()):
					if counter == 2:
						value = self.access_name(key=value)
					item = QTableWidgetItem(str(value))
					if not counter in [0, 3]:
						# item.setTextAlignment(Qt.AlignCenter)
						self.usersTableWidget.setItem(row, column, item)
						column += 1

			# self.usersTableWidget.resizeColumnsToContents()
			# self.usersTableWidget.resizeRowsToContents()
			self.usersTableWidget.horizontalHeader().setStretchLastSection(True)
			self.usersTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.usersTableWidget.show()

	def load_user_for_edit(self, item):
		row_clicked = item.row()		
		username = self.usersTableWidget.item(row_clicked, 0).text()
		self.userLineEdit.setText(username)
		if username == self.registry.login_object.user_object.username: 
			self.oldPassLineEdit.setEnabled(True)
		else:
			self.oldPassLineEdit.setEnabled(False)

	def delete_user(self):
		username = self.userLineEdit.text()
		if username == "":
			messageBox("خطا", "کاربری انتخاب نشده است").exec()
			return

		if username == self.registry.login_object.user_object.username:
			messageBox("خطا","امکان  حذف کاربر انتخاب شده ({}) وجود ندارد".format(username)).exec()
			return
		else:
			if messageBox("هشدار", "آیا کاربر ({}) حذف شود؟".format(username)).exec():
				queryset, status = self.registry.db_handler.delete_user(username)	
				if status:
					messageBox("پیام", "کاربر ({}) با موفقیت حذف شد.".format(username)).exec()
					self.userLineEdit.setText("")
					self.load_users()
				else:
					messageBox("خطا", "کاربر ({}) حذف نشد".format(username)).exec()
					return

	def create_newUserForm(self):
		self.newUserFormObject = newUserForm(self.registry)
		self.newUserFormObject.show()
		self.newUserFormObject.savePushButton.clicked.connect(self.load_users)

	def access_name(self, key=None, value=None):
		
		access_name_dict = {
			'guest': 'کاربر عادی',
			'admin': 'ادمین',
			'main_admin': 'ادمین اصلی',
			'superuser': 'سوپر یوزر',
		}

		if key:
			return access_name_dict[key]
		elif value:
			key_list = list(access_name_dict.keys())
			val_list = list(access_name_dict.values())
			position = val_list.index(value)
			return key_list[position]