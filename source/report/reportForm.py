from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import uic
from .xls_handler import xls_write
import jdatetime
import datetime
from source.main.messageBox import messageBox
from PyQt5.QtCore import Qt
import traceback

class reportForm(QMainWindow):
    def __init__(self, registry):
        super(reportForm, self).__init__()
        uic.loadUi('source/forms/reportForm.ui', self)
        self.registry = registry
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.savePushButton.clicked.connect(self.get_dates)
        self.cancelPushButton.clicked.connect(self.close)
        
    def get_dates(self):
        try:
            [sy, sm, sd] = [int(n) for n in self.startDateLineEdit.text().split('/')]
            start_g_date = list(jdatetime.JalaliToGregorian(jyear=sy, jmonth=sm, jday=sd).getGregorianList())
            [ey, em, ed] = [int(n) for n in self.endDateLineEdit.text().split('/')]
            end_g_date = list(jdatetime.JalaliToGregorian(jyear=ey, jmonth=em, jday=ed).getGregorianList())
        except Exception as e:
            traceback.print_exc()
            print(e)
            messageBox('خطا','تاریخ های وارد شده صحیح نیست').exec()

        self.start_date = datetime.datetime(*start_g_date)
        self.end_date = datetime.datetime(*end_g_date) + datetime.timedelta(hours=23, minutes=59, seconds=59)
        self.get_data_from_db()

    def get_data_from_db(self):
        queryset, status = self.registry.db_handler.get_log(self.start_date, self.end_date)
        log_list = [['نام فایل', 'نام دسته', 'تاریخ آپلود','ساعت آپلود', 'وضعیت آپلود']]
        for log in queryset:
            [y, m , d] = [int(n) for n in log['upload_date'].split(' ')[0].split('-')]
            if log['upload_status'] == 1:
                up_status = 'موفق'
            else:
                up_status = 'ناموفق'

            log_conv = [
                log['file_name'],
                log['class_name'],
                "-".join([str(n) for n in jdatetime.GregorianToJalali(gyear=y, gmonth=m, gday=d).getJalaliList()]),
                log['upload_date'].split(' ')[1].split('.')[0],
                up_status,
            ]
    
            log_list.append(log_conv)

        self.save_to_xls(log_list)

    def save_to_xls(self, data):
        options = QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        options |= QFileDialog.DontResolveSymlinks
        folder_name= QFileDialog.getExistingDirectory(self, options=options)
        if not folder_name:
            return
        try:
            xls_write(data, folder_name + '/LOG Report.xls')
            messageBox('پیام','صدور گزارش با موفقیت انجام شد').exec()
            self.close()
        except Exception as e:
            traceback.print_exc()
            print(e)
            messageBox('خطا','عملیات انجام نشد').exec()
