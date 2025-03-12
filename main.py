import sys
import os
import win32api
import win32con
import time
import threading
import log
from PIL import ImageGrab
from PyQt6.QtWidgets import QLabel, QComboBox, QMainWindow, QApplication, QPushButton, QMessageBox, QWidget, QGroupBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPainter

class Signals(QThread):
        msg_signal = pyqtSignal(str)

class Maingui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.main_thread = threading.main_thread()
        self.stop_event_lshift = threading.Event()
        self.stop_event_rgb = threading.Event()

        thread = threading.Thread(target=self.loop_RGB, name="loop_RGB")
        thread.start()
        self.start_lshift()

        self.signals = Signals()
        self.signals.msg_signal.connect(self.handle_msg)
        self.signals.msg_signal.connect(self.func_label_mouse_pos)
        self.signals.start()

        self.overwrite_log()
    
    def initUI(self):
        self.setWindowTitle("Screen Color")
        self.setFixedSize(190, 190)
        self.setStyleSheet("font-size: 12px")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        groupbox = QGroupBox("Info", central_widget)
        groupbox.setGeometry(0, 0, 190, 50)

        self.label_mouse_xy = QLabel("Mouse pos     X: Y:", self)
        self.label_mouse_xy.setGeometry(0, 5, 150, 30)

        self.color_label = QLabel("RGB: , Hex: ", self)
        self.color_label.setGeometry(0, 25, 190, 30)

        left_click_label = QLabel("Press L-shift to record log", self)
        left_click_label.setGeometry(25, 50, 170, 40)

        self.lshift_combo = QComboBox(central_widget)
        for s in ["ON", "OFF"]:
            self.lshift_combo.addItem(s)
        self.lshift_combo.setGeometry(0, 80, 190, 20)

        label_log_overwrite = QLabel("At launch to overwrite the log", self)
        label_log_overwrite.setGeometry(20, 100, 160, 30)

        self.combo_log_overwrite = QComboBox(central_widget)
        if not os.path.exists("app.conf"):
            with open("app.conf", "w", encoding="utf-8") as conf:
                conf.write("True")

        if os.path.exists("app.conf"):
            with open("app.conf", "r", encoding="utf-8") as conf:
                config = conf.read()
                if config == "True":
                    for s in ["ON", "OFF"]:
                        self.combo_log_overwrite.addItem(s)
                else:
                    for s in ["OFF", "ON"]:
                        self.combo_log_overwrite.addItem(s)
        else:
            for s in ["ON", "OFF"]:
                self.combo_log_overwrite.addItem(s)
        self.combo_log_overwrite.currentTextChanged.connect(self.conf_write)
        self.combo_log_overwrite.setGeometry(0, 130, 190, 20)

        ok_button = QPushButton("OK", self)
        ok_button.setGeometry(70, 160, 60, 20)
        ok_button.clicked.connect(self.lshift_ok)

    def conf_write(self):
        if self.combo_log_overwrite.currentText() == "ON":
            with open("app.conf", "w", encoding="utf-8") as conf:
                conf.write("True")
        else:
            with open("app.conf", "w", encoding="utf-8") as conf:
                conf.write("False")

    def overwrite_log(self):
        if os.path.exists("app.conf"):
            with open("app.conf", "r", encoding="utf-8") as conf:
                config = conf.read()
                if config == "True":
                    with open("app.log", "w", encoding="utf-8"):
                        ""
                else:
                    pass

    def start_lshift(self):
        self.stop_event_lshift.clear()
        self.repeat_thread_lshift = threading.Thread(target=self.detec_lshift, name="detected_lshift")
        self.repeat_thread_lshift.start()

    def stop_lshift(self):
        if self.repeat_thread_lshift.is_alive():
            self.stop_event_lshift.set()

    def get_color_at(self, x, y):
        image = ImageGrab.grab(bbox=(x, y, x+1, y+1))
        pixel = image.getpixel((0, 0))
        return pixel
    
    def rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    
    def loop_RGB(self):
        while self.main_thread.is_alive():
            self.Mouse_x, self.Mouse_y = win32api.GetCursorPos()
            self.rgb = self.get_color_at(self.Mouse_x, self.Mouse_y)
            self.hex_color = self.rgb_to_hex(self.rgb)
            self.label_mouse_xy.setText(f"Mouse pos     X:{self.Mouse_x} Y:{self.Mouse_y}")
            self.color_label.setText(f"RGB: {self.rgb}, Hex: {self.hex_color}")
            time.sleep(0.5)

    def detec_lshift(self):
        press_lshift = False
        while self.main_thread.is_alive():
            if self.lshift_combo.currentText() == "ON" and win32api.GetKeyState(win32con.VK_LSHIFT) < 0 and not press_lshift and not self.stop_event_lshift.is_set():
                self.signals.msg_signal.emit(f"RGB: {self.rgb}, Hex: {self.hex_color}")
                log.logger.info(f"RGB: {self.rgb}, Hex: {self.hex_color}")
                press_lshift = True
                time.sleep(0.5)
            else:
                press_lshift = False

    def lshift_ok(self):
        if self.lshift_combo.currentText() == "ON":
            if self.repeat_thread_lshift.is_alive():
                pass
            else:
                self.start_lshift()
        else:
            self.stop_lshift()

    def handle_msg(self):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"RGB: {self.rgb}, Hex: {self.hex_color}")
        message_box.exec()

    def func_label_mouse_pos(self, text):
        painter = QPainter(self.label_mouse_xy)
        self.label_mouse_xy.setText(str(text))
        self.label_mouse_xy.repaint()
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Maingui()
    window.show()
    app.exec()
