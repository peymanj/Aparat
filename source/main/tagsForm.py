from source.main.messageBox import messageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt


class tagsForm(QMainWindow):
	def __init__(self, registry):
		super(tagsForm, self).__init__()
		uic.loadUi('source/forms/tagsForm.ui', self)
		self.registry = registry
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.load_class_names()
		self.load_class_tags()
		self.classComboBox.currentIndexChanged.connect(self.load_class_tags)
		self.savePushButton.clicked.connect(self.set_class_tags)
		self.cancelPushButton.clicked.connect(self.close)
	def load_class_names(self):

		class_data_list, status = self.registry.db_handler.get_classes()
		class_name_list  = [class_['name'] for class_ in class_data_list]
		self.classComboBox.clear()
		self.classComboBox.blockSignals(True)
		self.classComboBox.addItems(class_name_list)
		self.classComboBox.blockSignals(False)
		self.classComboBox.setCurrentIndex(0) 

	def load_class_tags(self):
		current_class_name = self.classComboBox.currentText()
		queryset, status = self.registry.db_handler.get_tags(current_class_name)
		self.old_tags = []
		tag_str = ''
		if queryset:
			for item in queryset:
				tag_str += item['name'] + '\n'
				self.old_tags.append(item['name'])
		self.tagsTextEdit.setPlainText(tag_str)
	
	def set_class_tags(self):
		if not self.registry.login_object.user_object.add_tag():
			messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
			return
		current_class_name = self.classComboBox.currentText()
		tag_str = self.tagsTextEdit.toPlainText()
		tag_list = []
		for tag in tag_str.splitlines():
			if tag.strip() != "":
				tag_list.append(tag)
			else:
				pass 
		if len(tag_list) < 3:
			messageBox('خطا','حداقل سه تک وارد شود').exec()
			return
		else:	   
			queryset, status = self.registry.db_handler.set_tags(self.old_tags, tag_list, current_class_name)
			self.close()