
from source.main.messageBox import messageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt


class specTagsForm(QMainWindow):
	def __init__(self, registry):
		super(specTagsForm, self).__init__()
		uic.loadUi('source/forms/specTagsForm.ui', self)
		self.registry = registry
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.savePushButton.clicked.connect(self.save_tags)
		self.cancelPushButton.clicked.connect(self.close)
		self.load_tags()

	def load_tags(self):
		self.tagsTextEdit.setPlainText(self.registry.main_form.spec_tags_str)

	def save_tags(self):
		if not self.registry.login_object.user_object.edit_special_video():
			messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
			return
		current_class_name = self.registry.main_form.specClassComboBox.currentText()
		
		tag_list = []
		for tag in self.tagsTextEdit.toPlainText().splitlines():
			if tag.strip() != "":
				tag_list.append(tag)
			else:
				pass 
		if len(tag_list) < 3:
			messageBox('خطا','حداقل سه تک وارد شود').exec()
			return
		else:	
			self.registry.main_form.spec_tags_str = self.tagsTextEdit.toPlainText()
			self.close()