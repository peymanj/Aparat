from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import Qt
from source.main.messageBox import messageBox
import datetime
from .sequenceSubForm.newProfileForm import newProfileForm
from .sequenceSubForm.editProfileForm import editProfileForm
import jdatetime
import traceback

class sequenceForm(QMainWindow):
    
    def __init__(self, registry):
        super(sequenceForm, self).__init__()

        uic.loadUi('source/forms/sequenceForm.ui', self)
        self.registry = registry
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.load_profiles()
        self.load_active_classes()
        self.load_sequences()
        self.load_date()
        self.newProfilePushButton.clicked.connect(self.create_newProfileForm)
        self.submitSequencePushButton.clicked.connect(self.add_sequence)
        self.submitSequencePushButton.clicked.connect(self.registry.main_form.load_sequences)
        self.profileComboBox.currentIndexChanged.connect(self.load_sequences)
        self.profileComboBox.currentIndexChanged.connect(self.load_date)
        self.deleteSequencePushButton.clicked.connect(self.delete_sequence)
        self.deleteProfilePushButton.clicked.connect(self.delete_profile)
        self.registry.main_form.update_data_signal.connect(self.load_profiles)
        self.registry.main_form.update_data_signal.connect(self.load_sequences)
        self.editProfilePushButton.clicked.connect(self.create_editProfileForm)

    def load_profiles(self):
        profile_list, status = self.registry.db_handler.get_profiles()
        self.profileComboBox.clear()
        if profile_list:
            profile_name_list  = [profile['name'] for profile in profile_list]
            self.profileComboBox.blockSignals(True)
            self.profileComboBox.addItems(profile_name_list)
            self.profileComboBox.blockSignals(False)

    def load_active_classes(self):
        active_class_data_list, status = self.registry.db_handler.get_active_classes()
        if active_class_data_list:
            class_name_list  = [class_['name'] for class_ in active_class_data_list]
            self.activeClassComboBox.clear()
            self.activeClassComboBox.blockSignals(True)
            self.activeClassComboBox.addItems(class_name_list)
            self.activeClassComboBox.blockSignals(False)
            self.activeClassComboBox.setCurrentIndex(0)
            # self.load_class_data()
    
    def add_sequence(self):
        start = self.startTimeEdit.time().toString('hh:mm:ss')
        end = self.endTimeEdit.time().toString('hh:mm:ss')
        class_name = self.activeClassComboBox.currentText()
        profile_name = self.profileComboBox.currentText()
        video_count = self.videoCountSpinBox.value()

        if class_name and profile_name and video_count:
            pass
        else:
            messageBox("خطا", "پارامتر های ورودی به درستی وارد نشده است").exec()
            return

        try:
            start_value = datetime.datetime.strptime(self.registry.main_form.persian_to_english(start),'%H:%M:%S')
            end_value = datetime.datetime.strptime(self.registry.main_form.persian_to_english(end),'%H:%M:%S')
        except Exception as e:
            traceback.print_exc()
            print(e)
            messageBox("خطا", "زمان وارد شده صحیح نیست").exec()
            return

        if end_value <= start_value:
            messageBox("خطا", "زمان پایان کمتر از زمان شروع است").exec()
        else:
            profile_data_list, status = self.registry.db_handler.get_sequence(profile_name)
            for seq in profile_data_list:
                if start_value <= datetime.datetime.strptime(seq['end_time'],'%H:%M:%S'):
                    if end_value >= datetime.datetime.strptime(seq['start_time'],'%H:%M:%S'):
                        messageBox("خطا", "زمان انتخاب شده با سایر زمان بندی ها تداخل دارد").exec()
                        return
            queryset, status = self.registry.db_handler.add_sequence(profile_name, class_name, self.registry.main_form.persian_to_english(start)\
                ,self.registry.main_form.persian_to_english(end), video_count)
            if status:
                self.load_sequences()
            else:
                messageBox("خطا", "امکان اضافه کردن زمان بندی وجود ندارد").exec()

    def load_sequences(self):

        profile_name = self.profileComboBox.currentText()
        profile_data_list, status = self.registry.db_handler.get_sequence(profile_name)
        self.set_table(profile_data_list)
        self.load_date()

    def load_date(self):
        profile_name = self.profileComboBox.currentText()
        profile_name, status = self.registry.db_handler.get_profile_date(profile_name)
        if profile_name:
            [y, m , d] = [int(n) for n in profile_name[0]['date'].split(' ')[0].split('-')]
            profile_date = "/".join([str(n) for n in jdatetime.GregorianToJalali(gyear=y, gmonth=m, gday=d).getJalaliList()])
            self.dateLineEdit.setText(profile_date)

    def set_table(self, profile_data_list):
        headers = [ "دسته", "زمان شروع", "زمان پایان", "تعداد ویدئو"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(len(profile_data_list))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        
        for row, sequence in enumerate(profile_data_list):
            for column, (key, value) in enumerate(sequence.items()):
                item = QTableWidgetItem(str(value))
                if column != 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row, column, item)

        # self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.resizeRowsToContents()
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tableWidget.show()

    def delete_sequence(self):
        try:
            if messageBox("هشدار", "زمان بندی انتخاب شده حذف گردد؟").exec():
                profile_name = self.profileComboBox.currentText()
                class_name = self.tableWidget.selectedItems()[0].text()
                start = self.tableWidget.selectedItems()[1].text()
                queryset, status = self.registry.db_handler.delete_sequence(profile_name, class_name, start)
                if status:
                    self.load_sequences()
                else:
                    messageBox("خطا", "امکان حذف رمان بندی وجود ندارد").exec()
        except Exception as e:
            traceback.print_exc()
            print(e)
            messageBox("خطا", "امکان حذف زمان بندی وجود ندارد").exec()

    def create_newProfileForm(self):
        self.newProfileFormObject = newProfileForm(self.registry)
        self.newProfileFormObject.show()

    def delete_profile(self):
        if messageBox("هشدار", "آیا از حذف پروفایل مطمئن هستید؟").exec():
            profile_name = self.profileComboBox.currentText()
            queryset, status = self.registry.db_handler.delete_profile(profile_name)
            self.registry.main_form.update_data_signal.emit()

    def create_editProfileForm(self):
        if self.profileComboBox.currentText() != "":
            self.editProfileForm = editProfileForm(self.registry)
            self.editProfileForm.show()
