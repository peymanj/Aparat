from PyQt5.QtCore import QObject, pyqtSignal
from .robot_initiator import robotInitiator
from source.main.messageBox import messageBox
import requests
from PyQt5.QtCore import QTimer
# import ptvsd 

class robotWorker(QObject):
    send_log_signal = pyqtSignal(dict)
    finished = pyqtSignal()
    finished_with_error = pyqtSignal(str)
    
    def __init__(self, registry,  parent=None):
        super().__init__(parent)
        self.registry = registry
        self.robotInitiatorObject = robotInitiator()
        self.finished_with_error.connect(self.finish_sequence)
        # ptvsd.debug_this_thread()
        pass

    def run_robot(self):
        self.robotInitiatorObject.initiate(self.registry.main_form.sequence_list, self.registry.main_form.spec_sequence_list,\
              self.send_log_signal, self.registry.main_form.settingObject, self.finished, self.finished_with_error)

    def finish_sequence(self, message):
        message = 'امکان اتصال وجود ندارد\n\n' + message
        messageBox('خطا',message).exec()

