from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt
from source.main.messageBox import messageBox


class classesForm(QMainWindow):

	def __init__(self, registry):
		super().__init__()
		uic.loadUi('source/forms/classesForm.ui', self)
		self.registry = registry
		self.newClassPushButton.clicked.connect(self.create_newClassForm)
		self.classComboBox.currentIndexChanged.connect(self.load_class_data)
		self.editClassPushButton.clicked.connect(self.load_class_edit_window)
		self.activeClassCheckBox.toggled['bool'].connect(lambda: self.active_state('set'))
		self.deleteClassPushButton.clicked.connect(self.delete_class)
		self.registry.main_form.update_data_signal.connect(self.load_class_names)
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.setWindowModality(Qt.ApplicationModal)
		self.load_class_names()

	def load_class_names(self):

		class_data_list, status = self.registry.db_handler.get_classes()
		class_name_list  = [class_['name'] for class_ in class_data_list]
		self.classComboBox.clear()
		self.classComboBox.blockSignals(True)
		self.classComboBox.addItems(class_name_list)
		self.classComboBox.blockSignals(False)
		self.classComboBox.setCurrentIndex(0)
		self.load_class_data()

	def load_class_data(self):
		self.clear_class_data()
		current_class_name = self.classComboBox.currentText()
		queryset, status = self.registry.db_handler.get_class(current_class_name)
		try:
			class_ = queryset[0]
			self.classNameLineEdit.setText(class_['name'])
			self.folderPathLineEdit.setText(class_['folder_path'])
			self.classPlaylistNameLineEdit.setText(class_['playlist_name'])
			self.classAparatCategoryLineEdit.setText(class_['aparat_category'])
			self.activeClassCheckBox.blockSignals(True)
			self.activeClassCheckBox.setChecked(self.active_state('get'))
			self.activeClassCheckBox.blockSignals(False)
			self.usernameLineEdit.setText(class_['username'])
			self.passwordLineEdit.setText(class_['password'])
		except Exception as e:
			pass
	
	def clear_class_data(self):
		self.classNameLineEdit.setText('')
		self.folderPathLineEdit.setText('')
		self.classPlaylistNameLineEdit.setText('')
		self.classAparatCategoryLineEdit.setText('')
		self.activeClassCheckBox.blockSignals(True)
		self.activeClassCheckBox.setChecked(False)
		self.activeClassCheckBox.blockSignals(False)
		self.usernameLineEdit.setText('')
		self.passwordLineEdit.setText('')

	def active_state(self, mode):
		current_class_name = self.classComboBox.currentText()
		class_active_state = int(self.activeClassCheckBox.isChecked() == True)
		if mode=='set':
			if not self.registry.login_object.user_object.add_class():
				messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
				return
			query, status = self.registry.db_handler.set_class_active_status(class_active_state, current_class_name)
		if mode=='get':
			query, status = self.registry.db_handler.get_class_active_status(current_class_name)
			return bool(query[0]['active'])
		


		# self.classNameLineEdit.setText(class_['aparat_category'])

	def load_class_edit_window(self):
		if not self.registry.login_object.user_object.add_class():
			messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
			return
		current_class_name = self.classComboBox.currentText()
		if current_class_name == "":
			return
		from .classSubForms.classEditForm import classEditForm
		self.classEditFormObject= classEditForm(self.registry)
		self.classEditFormObject.show()

	def create_newClassForm(self):
		if not self.registry.login_object.user_object.add_class():
				messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
				return
		from .classSubForms.newClassForm import newClassForm
		self.newClassFormObject = newClassForm(self.registry)
		self.newClassFormObject.show()

	def delete_class(self):
		if not self.registry.login_object.user_object.add_class():
				messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
				return
		if self.classComboBox.currentText() != "":
			if messageBox("هشدار", "آیا از حذف دسته مطمئن هستید؟").exec():
				class_name = self.classComboBox.currentText()
				queryset, status = self.registry.db_handler.delete_class(class_name)
				self.registry.main_form.update_data_signal.emit()
