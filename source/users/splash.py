from time import sleep
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap

'''
displays splash screen for desiredamount of time
'''
class splashScreen():
    def __init__(self, image_path, interval): 
        pixmap = QPixmap(image_path)
        self.splash = QSplashScreen(pixmap)
        self.splash.show()
        sleep(interval)
        # QTimer.singleShot(0, lambda: sleep(interval))

    def close(self):
        self.splash.close()
        