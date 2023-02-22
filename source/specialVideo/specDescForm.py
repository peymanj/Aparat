from source.main.messageBox import messageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt

class specDescForm(QMainWindow):
	def __init__(self, registry):
		super(specDescForm, self).__init__()
		uic.loadUi('source/forms/specDescForm.ui', self)
		self.registry = registry
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.savePushButton.clicked.connect(self.save_desc)
		self.cancelPushButton.clicked.connect(self.close)
		self.load_desc()

	def load_desc(self):
		self.descriptionTextEdit.setPlainText(self.registry.main_form.spec_desc_str)

	def save_desc(self):
		if not self.registry.login_object.user_object.edit_special_video():
			messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
			return
		# current_class_name = self.registry.main_form.specClassComboBox.currentText()
		if self.descriptionTextEdit.toPlainText().strip() == "":
			messageBox('خطا','حداقل یک کپشن وارد شود').exec()
			return
		else:
			self.registry.main_form.spec_desc_str = self.descriptionTextEdit.toPlainText()
			self.close()