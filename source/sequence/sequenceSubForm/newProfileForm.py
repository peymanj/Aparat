from datetime import datetime
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from source.main.messageBox import messageBox
from PyQt5.QtCore import Qt
import jdatetime
from datetime import datetime
import traceback

class newProfileForm(QMainWindow):

    def __init__(self, registry):
        super(newProfileForm, self).__init__()
        uic.loadUi('source/forms/newProfileForm.ui', self)
        self.registry = registry
        self.savePushButton.clicked.connect(self.add_profile)
        self.cancelPushButton.clicked.connect(self.close)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def add_profile(self):
        name = self.profileNameLineEdit.text()
        date = self.dateLineEdit.text()

        if name == "" or date == "":
            messageBox("خطا", "پارامتر های ورودی به درستی وارد نشده است").exec()
            return

        try:
            [sy, sm, sd] = [int(n) for n in date.split('/')]
            g_date = list(jdatetime.JalaliToGregorian(jyear=sy, jmonth=sm, jday=sd).getGregorianList())
        except Exception as e:
            traceback.print_exc()
            print(e)
            messageBox('خطا','تاریخ وارد شده صحیح نیست').exec()

        self.date = datetime(*g_date)

        queryset, status = self.registry.db_handler.get_profile_by_date(self.date)
        if queryset:
            messageBox("خطا", "پروفایل دیگری در این تاریخ وجود دارد").exec()
            return
        query, status = self.registry.db_handler.add_profile(name, self.date)
        if status:
            self.registry.main_form.update_data_signal.emit()
            self.close()
        else:
            messageBox("خطا", "امکان اضافه کردن پروفایل وجود ندارد").exec()
            return
