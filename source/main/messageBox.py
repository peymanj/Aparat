from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt



class messageBox(QMessageBox):
	def __init__(self, title, message, parent=None):
		super().__init__(parent)

		self.setText(message)
		self.setWindowTitle(title)
		self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
		if title.lower() == 'هشدار':
			self.addButton('انصراف', QMessageBox.ButtonRole.RejectRole)
			self.addButton('تأیید', QMessageBox.ButtonRole.AcceptRole)
			self.setIcon(QMessageBox.Warning)
		elif title.lower() == 'خطا':
			self.addButton('تأیید', QMessageBox.ButtonRole.AcceptRole)
			self.setIcon(QMessageBox.Critical)
		elif title.lower() == 'پیام':
			self.addButton('تأیید', QMessageBox.ButtonRole.AcceptRole)
			self.setIcon(QMessageBox.Information)

	def exec(self):
		status = super().exec()
		return bool(status)
