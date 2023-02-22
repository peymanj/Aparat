from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from .DBConfig import CONFIG
from PyQt5.QtCore import Qt

class settingForm(QMainWindow):
	def __init__(self, registry):
		super(settingForm, self).__init__()
		uic.loadUi('source/forms/settingForm.ui', self)
		self.registry = registry
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.savePushButton.clicked.connect(self.save_setting)
		self.savePushButton.clicked.connect(self.registry.main_form.settingObject.load_setting)
		self.cancelPushButton.clicked.connect(self.close)
		self.load_setting()

	def load_setting(self):
		queryset, status = self.registry.db_handler.get_setting()
		try:
			self.dbPathLineEdit.setText(CONFIG['db_path'])
			self.coverImageFolderLineEdit.setText(queryset[0]['img_path'])
			self.coverImageFormatLineEdit.setText(queryset[0]['cover_pic_format'])
			self.tagsSpinBox.setValue(queryset[0]['tag_number'])
			self.browserViewCheckBox.setChecked(bool(queryset[0]['show_browser']))		
			self.waitMinSpinBox.setValue(queryset[0]['wait_min'])
			self.waitMaxSpinBox.setValue(queryset[0]['wait_max'])
			self.multiInstanceCheckBox.setChecked(bool(queryset[0]['multi_instance']))		
		except:
			print('error loading setting')

		
	def save_setting(self):
		queryset, status = self.registry.db_handler.save_setting(
		self.coverImageFolderLineEdit.text(),
		self.coverImageFormatLineEdit.text(),
		self.tagsSpinBox.value(),
		int(self.browserViewCheckBox.checkState()),
		self.waitMinSpinBox.value(),
		self.waitMaxSpinBox.value(),
		int(self.multiInstanceCheckBox.checkState()),
		)
		self.close()
