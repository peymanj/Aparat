from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from source.main.messageBox import messageBox
from PyQt5.QtCore import Qt
import jdatetime
from datetime import datetime
import traceback

class editProfileForm(QMainWindow):

    def __init__(self, registry):
        super(editProfileForm, self).__init__()
        uic.loadUi('source/forms/editProfileForm.ui', self)
        self.registry = registry
        self.savePushButton.clicked.connect(self.update_profile)
        self.cancelPushButton.clicked.connect(self.close)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.load_profile()


    def update_profile(self):
        old_name = self.registry.main_form.sequenceFormObject.profileComboBox.currentText()
        new_name = self.profileNameLineEdit.text()
        date = self.dateLineEdit.text()


        if new_name == "":
            messageBox("خطا", "پارامتر های ورودی به درستی وارد نشده است").exec()
            return

        try:
            [sy, sm, sd] = [int(n) for n in date.split('/')]
            g_date = list(jdatetime.JalaliToGregorian(jyear=sy, jmonth=sm, jday=sd).getGregorianList())
        except Exception as e:
            traceback.print_exc()
            print(e)
            messageBox('خطا','تاریخ وارد شده صحیح نیست').exec()
            return

        self.date = datetime(*g_date)

        queryset, status = self.registry.db_handler.get_profile_by_date(self.date)
        if queryset:
            messageBox("خطا", "پروفایل دیگری در این تاریخ وجود دارد").exec()
            return
            
        query, status =  self.registry.db_handler.update_profile(old_name, new_name, self.date)
        if status:
            messageBox("پیام", "پروفایل با موفقیت ویرایش شد").exec()
            self.registry.main_form.update_data_signal.emit()
            self.close()
        else:
            messageBox("خطا", "امکان ویرایش پروفایل وجود ندارد").exec()
            return


    def load_profile(self):
        self.profileNameLineEdit.setText(self.registry.main_form.sequenceFormObject.profileComboBox.currentText())
        self.dateLineEdit.setText(self.registry.main_form.sequenceFormObject.dateLineEdit.text())
