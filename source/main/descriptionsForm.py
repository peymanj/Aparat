
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from source.main.messageBox import messageBox
from PyQt5.QtCore import Qt


class descriptionsForm(QMainWindow):
	def __init__(self, registry):
		super(descriptionsForm, self).__init__()
		uic.loadUi('source/forms/descriptionsForm.ui', self)
		self.registry = registry
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.load_class_names()
		self.load_class_desc()
		self.classComboBox.currentIndexChanged.connect(self.load_class_desc)
		self.savePushButton.clicked.connect(self.set_class_desc)
		self.cancelPushButton.clicked.connect(self.close)

	def load_class_names(self):

		class_data_list, status = self.registry.db_handler.get_classes()
		class_name_list  = [class_['name'] for class_ in class_data_list]
		self.classComboBox.clear()
		self.classComboBox.blockSignals(True)
		self.classComboBox.addItems(class_name_list)
		self.classComboBox.blockSignals(False)
		self.classComboBox.setCurrentIndex(0) 

	def load_class_desc(self):
		current_class_name = self.classComboBox.currentText()
		queryset, status = self.registry.db_handler.get_descriptions(current_class_name)
		self.old_desc = []
		desc_str = ''
		if queryset:
			for item in queryset:
				desc_str += item['name'] + '\n&\n'
				self.old_desc.append(item['name'])
		self.descriptionsTextEdit.setPlainText(desc_str)
	
	def set_class_desc(self):
		if not self.registry.login_object.user_object.add_desc():
			messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
			return
		current_class_name = self.classComboBox.currentText()
		desc_str = self.descriptionsTextEdit.toPlainText()
		desc_list = [] 
		for s in desc_str.split('&'):
			if s.strip() !="":
				desc_list.append(s.strip())				
			else:
				pass 
		if len(desc_list) < 1:
			messageBox('خطا','حداقل یک کپشن وارد شود').exec()
			return
		else:	
			queryset, status = self.registry.db_handler.set_descriptions(self.old_desc, desc_list, current_class_name)
			self.close()