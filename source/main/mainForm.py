from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QThread, QTimer, QEventLoop
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QFileDialog
import datetime
from source.setting.settingClass import settingClass
from source.setting.settingForm import settingForm
from source.sequence.sequenceForm import sequenceForm
from source.main.descriptionsForm import descriptionsForm
from source.main.tagsForm import tagsForm
from source.main.titlesForm import titlesForm
from source.users.usersForm import usersForm
from source.report.reportForm import reportForm
from source.robot.robotWorker import robotWorker
from source.main.messageBox import messageBox
from source.specialVideo.specDescForm import specDescForm
from source.specialVideo.specTagsForm import specTagsForm
from datetime import datetime
import jdatetime


class mainForm(QMainWindow):

    update_data_signal = pyqtSignal()
    robot_start_signal = pyqtSignal(list)
    
    def __init__(self, registry):
        super(mainForm, self).__init__()
        uic.loadUi('source/forms/mainForm.ui', self)
        self.last_time_checked = datetime.now().date()
        self.date_timer = QTimer(self)
        self.date_timer.timeout.connect(self.check_date)
        self.date_timer.start(20000)
        self.registry = registry
        self.pixmap = QPixmap('source/icons/main_logo.png')#
        self.logoLabel.setPixmap(self.pixmap) # .scaled( self.logoLabel.height(),  self.logoLabel.width(), Qt.KeepAspectRatio))
        self.actionTags.triggered.connect(self.create_tagsForm)
        self.actionTitles.triggered.connect(self.create_titlesForm)
        self.actionClasses.triggered.connect(self.create_classesForm)
        self.actionProfiles.triggered.connect(self.create_sequenceForm)
        self.actionDescriptions.triggered.connect(self.create_descriptionsForm)
        self.actionSetting.triggered.connect(self.create_settingForm)
        self.actionUsers.triggered.connect(self.create_usersForm)
        self.actionExit.triggered.connect(self.close)
        self.update_data_signal.connect(self.load_sequences)
        self.update_data_signal.connect(self.load_profiles)
        self.profileComboBox.currentIndexChanged.connect(self.load_sequences)
        self.startPushButton.clicked.connect(self.start_upload)
        self.startPushButton.clicked.connect(lambda: self.startPushButton.setEnabled(False))
        self.endPushButton.clicked.connect(lambda: self.endPushButton.setEnabled(False))
        self.startPushButton.clicked.connect(lambda: self.endPushButton.setEnabled(True))
        self.clearHistoryPushButton.clicked.connect(self.clear_history)
        self.actionReport.triggered.connect(self.create_reportForm)
        self.endPushButton.setEnabled(False)
        self.settingObject = settingClass(registry)
        self.row = 0 # log table row count

        # TAB 2:

        self.loadFilePushButton.clicked.connect(self.load_spec_video_directory)
        self.spec_tags_str = ""
        self.specTagsPushButton.clicked.connect(self.create_specTagsForm)
        self.specDescriptionPushButton.clicked.connect(self.create_specDescForm)
        self.submitSequencePushButton.clicked.connect(self.save_spec_video_sequence)
        self.submitSequencePushButton.clicked.connect(self.load_spec_video_sequences)
        self.specSequenceTableWidget.doubleClicked.connect(self.load_for_edit_spec_sequence)
        self.cancelEditSequencePushButton.clicked.connect(self.clean_spec_input)
        self.editSequencePushButton.clicked.connect(self.update_spec_sequence)
        self.deleteSequencePushButton.clicked.connect(self.delete_spec_sequence)
        self.spec_desc_str = ""
        #  -----------------------------------------------
        # TAB 1
        self.show()
        self.load_profiles()
        self.load_sequences()
        
        # TAB 2
        self.load_class_names()
        self.load_spec_video_sequences()


    # TAB 1 METHODS

    

    def persian_to_english(self, string):
        new_string = ''
        persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
        english_numbers  = '0123456789'
        for s in string:
            if s in persian_numbers:
                new_string += english_numbers[persian_numbers.index(s)]
            else:
                new_string += s
        return new_string

    def load_profiles(self):
        today = str(datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S"))
        
        queryset, status = self.registry.db_handler.get_profile_by_date(today)
        self.profileComboBox.clear()
        if queryset:
            profile_name = [queryset[0]['name']]
            self.profileComboBox.addItems(profile_name)
            [y, m , d] = [int(n) for n in queryset[0]['date'].split(' ')[0].split('-')]
            profile_date = "/".join([str(n) for n in jdatetime.GregorianToJalali(gyear=y, gmonth=m, gday=d).getJalaliList()])
            self.dateLineEdit.setText(profile_date)

    def create_sequenceForm(self):
        if not self.registry.login_object.user_object.view_profiles():
            messageBox(u'خطا',u'شما به این بخش دسترسی ندارید').exec()
            return

        self.sequenceFormObject = sequenceForm(self.registry)
        self.sequenceFormObject.show()

    def load_sequences(self):

        profile_name = self.profileComboBox.currentText()
        profile_data_list, status = self.registry.db_handler.get_sequence(profile_name)
        self.set_detail_table(profile_data_list)
        return profile_data_list

    def set_detail_table(self, profile_data_list):
        headers = [ "دسته", "زمان شروع", "زمان پایان", "تعداد ویدئو"]
        self.detailTableWidget.setColumnCount(len(headers))
        self.detailTableWidget.setHorizontalHeaderLabels(headers)
        self.detailTableWidget.setRowCount(0)

        if profile_data_list:
            self.detailTableWidget.setRowCount(len(profile_data_list))
        
            for row, sequence in enumerate(profile_data_list):
                for column, (key, value) in enumerate(sequence.items()):
                    item = QTableWidgetItem(str(value))
                    if column != 0:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.detailTableWidget.setItem(row, column, item)

            # self.tableWidget.resizeColumnsToContents()
            # self.tableWidget.resizeRowsToContents()
            self.detailTableWidget.horizontalHeader().setStretchLastSection(True)
            self.detailTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.detailTableWidget.show()

    def start_upload(self):
        
        self.sequence_list = self.load_sequences()
        self.spec_sequence_list = self.load_spec_video_sequences()
        self.robot_thread = QThread()
        self.robot_worker = robotWorker(self.registry)
        self.robot_worker.moveToThread(self.robot_thread)
        self.robot_thread.started.connect(self.robot_worker.run_robot)
        self.robot_worker.finished.connect(self.robot_thread.quit)
        self.robot_worker.send_log_signal.connect(self.save_log)
        self.endPushButton.clicked.connect(self.robot_worker.robotInitiatorObject.exit_slot)
        self.robot_worker.finished.connect(lambda: self.startPushButton.setEnabled(True))
        self.robot_worker.finished.connect(lambda: self.endPushButton.setEnabled(False))
        self.robot_thread.setTerminationEnabled(True)
        self.robot_thread.start()

    def save_log(self, log):
        queryset, status = self.registry.db_handler.add_log(log)
        self.update_log_table(log)

    def update_log_table(self, log):
        headers = ['نام فایل', 'دسته', 'زمان آپلود', 'وضعیت آپلود']
        self.historyTableWidget.setColumnCount(len(headers))
        self.historyTableWidget.setRowCount(self.row)
        self.historyTableWidget.insertRow(0)
        self.historyTableWidget.setHorizontalHeaderLabels(headers)
        value = log['video_name']
        item = QTableWidgetItem(value)
        self.historyTableWidget.setItem(0, 0, item)

        value = log['class_name']
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignCenter)
        self.historyTableWidget.setItem(0, 1, item)

        value = log['upload_time']
        value = str(value).split(' ')[1].split('.')[0]
        item =QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignCenter)
        self.historyTableWidget.setItem(0, 2, item)

        value = log['status']
        if value == 1:
            value = 'موفق'
        if value == 0:
            value = 'ناموفق'        
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignCenter)
        self.historyTableWidget.setItem(0 , 3, item)

        self.row += 1
        # self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.resizeRowsToContents()
        self.historyTableWidget.horizontalHeader().setStretchLastSection(True)
        self.historyTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.historyTableWidget.show()
    
    def clear_history(self):
        self.historyTableWidget.setRowCount(0)
        self.row = 0

    def create_tagsForm(self):
        if not self.registry.login_object.user_object.view_tag():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return

        self.tagsFormObject = tagsForm(self.registry)
        self.tagsFormObject.show()

    def create_titlesForm(self):
        if not self.registry.login_object.user_object.view_desc():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return

        self.titlesFormObject = titlesForm(self.registry)
        self.titlesFormObject.show()

    def create_descriptionsForm(self):
        if not self.registry.login_object.user_object.view_desc():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        self.descriptionsFormObject = descriptionsForm(self.registry)
        self.descriptionsFormObject.show()
    
    def create_classesForm(self):
        if not self.registry.login_object.user_object.view_class():
            messageBox('خطا','شما به این بخش دسترسی 2333ندارید').exec()
            return
        from source.classification.classesForm import classesForm
        self.classesFormObject = classesForm(self.registry)
        self.classesFormObject.show()

    def create_settingForm(self):
        if not self.registry.login_object.user_object.edit_setting():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        self.settingFormObject = settingForm(self.registry)
        self.settingFormObject.show()

    def create_reportForm(self):
        if not self.registry.login_object.user_object.get_report():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        self.reportFormObject = reportForm(self.registry)
        self.reportFormObject.show()

    def create_usersForm(self):
        if not self.registry.login_object.user_object.edit_users():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        self.usersFormObject = usersForm(self.registry)
        self.usersFormObject.show()
    
    def check_date(self):
        self.now = datetime.now().date()
        self.robot_is_running = False
        if self.now > self.last_time_checked:
            self.last_time_checked = self.now
            if self.endPushButton.isEnabled():
                self.robot_is_running = True
                self.endPushButton.clicked.emit()
            QTimer.singleShot(30000, self.reset_robot)
            self.load_profiles()
            self.load_sequences()
            self.update_data_signal.emit()
            self.date_timer.stop()

        else:
            pass

    def reset_robot(self):
        print('resetting robot')
        if self.robot_is_running:
            while not self.startPushButton.isEnabled():
                print('wait s')
                loop = QEventLoop()
                QTimer.singleShot(3000, loop.quit)
                loop.exec_()
            print('wait e')
            self.startPushButton.clicked.emit()
            self.date_timer.start(20000)
            print('rddddd')
        print('started')



    # TAB 2 METHODS

    def load_spec_video_directory(self):
        options = QFileDialog.Options()
        # options = QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        options |= QFileDialog.DontResolveSymlinks
        file_path, _= QFileDialog.getOpenFileName(self, options=options)
        if file_path:
            self.filePathlineEdit.setText(file_path)

    def load_class_names(self):

        class_data_list, status = self.registry.db_handler.get_classes()
        class_name_list  = [class_['name'] for class_ in class_data_list]
        self.specClassComboBox.clear()
        self.specClassComboBox.blockSignals(True)
        self.specClassComboBox.addItems(class_name_list)
        self.specClassComboBox.blockSignals(False)
        self.specClassComboBox.setCurrentIndex(0)

    def create_specTagsForm(self):
        if not self.registry.login_object.user_object.view_special_video():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        self.specTagsFormObject = specTagsForm(self.registry)
        self.specTagsFormObject.show()

    def create_specDescForm(self):
        if not self.registry.login_object.user_object.view_special_video():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        self.specDescFormObject = specDescForm(self.registry)
        self.specDescFormObject.show()
    
    def save_spec_video_sequence(self):
        if not self.registry.login_object.user_object.edit_special_video():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        video_path = self.filePathlineEdit.text().replace('\\','/')
        class_name = self.specClassComboBox.currentText()
        time = self.persian_to_english(self.uploadTimeEdit.time().toString('hh:mm:ss'))
        
        # time_value = datetime.strptime(time,'%H:%M:%S')
        if not self.check_input():
            return
        else:
            queryset, status = self.registry.db_handler.set_spec_video_sequence(video_path, class_name, \
                self.spec_tags_str, self.spec_desc_str, time)
            if status:
                self.clean_spec_input()
            else:
                messageBox("خطا", "اطلاعات ذخیره نشد").exec()
    
    def load_spec_video_sequences(self):
        spec_sequence_data_list, status = self.registry.db_handler.get_spec_video_sequence()
        self.set_spec_sequence_table(spec_sequence_data_list)
        return spec_sequence_data_list
         
    def set_spec_sequence_table(self, spec_sequence_data_list):
        headers = ['مسیر ویدئو','دسته','تگ ها','کپشن','زمان اپلود','وضعیت']
        self.specSequenceTableWidget.setColumnCount(len(headers))
        self.specSequenceTableWidget.setHorizontalHeaderLabels(headers)
        self.specSequenceTableWidget.setRowCount(0)
        if spec_sequence_data_list:
            self.specSequenceTableWidget.setRowCount(len(spec_sequence_data_list))
        
            for row, sequence in enumerate(spec_sequence_data_list):
                for column, (key, value) in enumerate(sequence.items()):
                    item = QTableWidgetItem(str(value))
                    if not column in [0, 1, 2, 3]:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.specSequenceTableWidget.setItem(row, column, item)

            # self.specSequenceTableWidget.resizeColumnsToContents()
            # self.specSequenceTableWidget.resizeRowsToContents()
            self.specSequenceTableWidget.horizontalHeader().setStretchLastSection(True)
            self.specSequenceTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.specSequenceTableWidget.show()

    def load_for_edit_spec_sequence(self, item ):
        row_clicked = item.row()		
        headers = ['مسیر ویدئو','دسته','تگ ها','کپشن','زمان اپلود','وضعیت']
        headercount = self.specSequenceTableWidget.columnCount()
        for x in range(0,headercount,1):
            headertext = self.specSequenceTableWidget.horizontalHeaderItem(x).text()
            current_value = self.specSequenceTableWidget.item(row_clicked, x).text()
            if headers[0] == headertext:
                self.video_path_old = current_value
            elif headers[1] == headertext:
                self.class_name_old = current_value
            elif headers[2] == headertext:
                self.tags_old = current_value
            elif headers[3] == headertext:
                self.desc_old = current_value
            elif headers[4] == headertext:
                self.upload_time_old = current_value

        self.filePathlineEdit.setText(self.video_path_old)
        self.specClassComboBox.setCurrentIndex(self.specClassComboBox.findText(self.class_name_old))
        self.uploadTimeEdit.setTime(datetime.strptime(self.persian_to_english(self.upload_time_old),'%H:%M:%S').time())
        self.spec_tags_str = self.tags_old
        self.spec_desc_str = self.desc_old
        self.editSequencePushButton.setEnabled(True)
        self.cancelEditSequencePushButton.setEnabled(True)

        self.submitSequencePushButton.setEnabled(False)
        self.deleteSequencePushButton.setEnabled(False)

    def update_spec_sequence(self):	
        if not self.registry.login_object.user_object.edit_special_video():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        if not self.check_input():
            return
        else:
            queryset, status = self.registry.db_handler.update_spec_sequence(self.video_path_old, self.class_name_old, self.persian_to_english(self.upload_time_old),\
                    self.filePathlineEdit.text().replace('\\','/'), self.specClassComboBox.currentText(),\
                    self.persian_to_english(self.uploadTimeEdit.time().toString('hh:mm:ss')), self.spec_tags_str, self.spec_desc_str)
            self.load_spec_video_sequences()
            self.clean_spec_input()

    def clean_spec_input(self):
        self.editSequencePushButton.setEnabled(False)
        self.cancelEditSequencePushButton.setEnabled(False)

        self.submitSequencePushButton.setEnabled(True)
        self.deleteSequencePushButton.setEnabled(True)

        self.spec_desc_str = ""
        self.spec_tags_str = ""
        self.filePathlineEdit.setText("")
        self.specClassComboBox.setCurrentIndex(0)
        self.uploadTimeEdit.setTime(datetime.strptime('00:00:00','%H:%M:%S').time())	

    def delete_spec_sequence(self):
        if not self.registry.login_object.user_object.edit_special_video():
            messageBox('خطا','شما به این بخش دسترسی ندارید').exec()
            return
        video_path = self.specSequenceTableWidget.selectedItems()[0].text()
        class_name = self.specSequenceTableWidget.selectedItems()[1].text()
        upload_time = self.specSequenceTableWidget.selectedItems()[4].text()
        queryset, status = self.registry.db_handler.delete_spec_sequence(video_path, class_name, upload_time)
        self.load_spec_video_sequences()

    def check_input(self):
        if (
            self.filePathlineEdit.text() != "" and
            self.specClassComboBox.currentText() != "" and
            self.spec_desc_str != "" and
            self.spec_tags_str != ""):
            return True
        else:
            messageBox("خطا", "پارامتر های ورودی به درستی وارد نشده است").exec()
            return False
