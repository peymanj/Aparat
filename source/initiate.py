
import sys
from PyQt5.QtWidgets import QApplication
from source.database.database_handler import databaseHandler
from source.users.splash import splashScreen
from source.users.login import login
from source.main.registry import registry
from source.main.messageBox import messageBox


def exception_handler(type, value, tback):	
    # sys.__excepthook__(type, value, tback)
    msg = str(tback.tb_frame) + '\n' + str(value)
    print(msg)
    messageBox('خطا', msg).exec() 

def initiateApp():
    app = QApplication(sys.argv)


    splash_screen = splashScreen('source/icons/splash.png', 3)

    registry_object = registry()
    registry_object.db_handler = databaseHandler()

    registry_object.login_object = login(registry_object)
    registry_object.login_object.login_signal.connect(splash_screen.close)
    sys.excepthook = exception_handler
    sys.exit(app.exec_())

if __name__ == "__main__":
    initiateApp()