import base64
import os
import time
import traceback
from functools import partial
import serial
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QGridLayout, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QHBoxLayout, QLabel, QProgressBar, QGroupBox, QVBoxLayout, QSpinBox, QMainWindow
import logging
import sys
import serial.tools.list_ports
from serial.serialutil import SerialException

LOG_LEVEL_SCREEN = logging.INFO
LOG_LEVEL_FILE = logging.INFO
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

devs = {
    0x00: "GM",
    0x01: "MID1",
    0x02: "EKM",
    0x08: "SHD",
    0x09: "ZKE",
    0x12: "DME",
    0x18: "CDC",
    0x24: "HKM",
    0x28: "RCC",
    0x30: "CCM",
    0x32: "EGS",
    0x3b: "GT",
    0x3f: "DIA",
    0x40: "FBZV",
    0x43: "GTF",
    0x44: "EWS",
    0x46: "CID",
    0x47: "FMBT",
    0x50: "MFL",
    0x51: "MML",
    0x56: "ASC",
    0x57: "LWS",
    0x5b: "IHKA",
    0x60: "PDC",
    0x65: "EKP",
    0x66: "AHL",
    0x67: "ONL",
    0x68: "RAD",
    0x6a: "DSP",
    0x6b: "STH",
    0x70: "RDC",
    0x72: "SM",
    0x73: "SDRS",
    0x74: "SOR",
    0x76: "CDCD",
    0x7f: "NAV",
    0x80: "IKE",
    0x81: "RCSC",
    0x9a: "HAC",
    0x9b: "MMR",
    0x9c: "CVM",
    0xa0: "FID",
    0xa4: "AB",
    0xa6: "GR",
    0xa7: "FHK",
    0xa8: "NAC",
    0xac: "EDC",
    0xb0: "SES",
    0xbb: "NAJ",
    0xbf: "Broadcast",
    0xc0: "MID",
    0xc8: "TEL",
    0xca: "TCU",
    0xd0: "LCM",
    0xda: "SMAD",
    0xe0: "IRIS",
    0xe7: "ANZV",
    0xe8: "RLS",
    0xea: "DSPC",
    0xed: "VID",
    0xf0: "BMBT",
    0xf1: "PIC",
    0xf5: "SZM",
    0xff: "Broadcast",
}

commands = {
    0x01: "Device Status Request",
    0x02: "Device Status",
    0x03: "Bus Status Request",
    0x04: "Bus Status",
    0x05: "Backlight control",
    0x06: "Identification",
    0x07: "Gong status",
    0x0c: "Vehicle control",
    0x10: "Ignition Status Request",
    0x11: "ignition Status",
    0x12: "IKE sensor status request",
    0x13: "IKE sensor status",
    0x14: "Country coding status request",
    0x15: "Country coding status",
    0x16: "Odometer Request",
    0x17: "Odometer",
    0x18: "Speed/RPM",
    0x19: "Temperature",
    0x1a: "IKE text/gong",
    0x1b: "IKE text status",
    0x1c: "Gong",
    0x1d: "Temperature request",
    0x1f: "Time and date",
    0x20: "Display status",
    0x21: "Menu text",
    0x22: "Text display confirmation",
    0x23: "Display text",
    0x24: "Update text",
    0x27: "MID display request",
    0x28: "MID denied access",
    0x29: "Report MID display",
    0x2a: "OBC Special Indicators",
    0x2b: "Telephone LED",
    0x2c: "Telephone Status",
    0x2d: "Telephone Number",
    0x31: "Button",
    0x32: "Volume control",
    0x33: "Part number status",
    0x34: "DSP equaliser button",
    0x35: "Car memory response",
    0x36: "Audio control",
    0x37: "Select menu",
    0x38: "CD control",
    0x39: "CD status",
    0x3a: "Recirculating air control",
    0x3b: "Radio/Telephone control",
    0x3c: "DSP preset sound patterns",
    0x40: "OBC Set Datetime",
    0x41: "OBC Data Request",
    0x42: "OBC Set Items",
    0x43: "Mono display",
    0x44: "E46 IKE text",
    0x45: "Radio status request",
    0x46: "LCD clear",
    0x47: "BM Status",
    0x48: "BM Button",
    0x49: "BM Dial",
    0x4a: "Cassette control",
    0x4b: "Cassette status",
    0x4e: "Audio Source Selection",
    0x4f: "BM Control",
    0x50: "Check control sensor request",
    0x51: "Check control sensors",
    0x52: "Text display update",
    0x53: "Vehicle data status request",
    0x54: "Vehicle data status",
    0x55: "Service interval display",
    0x56: "Light control status request",
    0x57: "Check control button",
    0x58: "Headlight wipe interval",
    0x59: "Light control status",
    0x5a: "Lamp status request",
    0x5b: "Lamp status",
    0x5c: "Light dimmer status",
    0x5d: "Light dimmer status request",
    0x5e: "LAM sensor",
    0x5f: "Info swap",
    0x60: "Suspension control status request",
    0x61: "Suspension control",
    0x62: "RDC Status",
    0x6d: "Mirror control",
    0x70: "Remote control central locking status",
    0x71: "Rain Sensor Status",
    0x72: "Check control remote central locking",
    0x73: "Immobiliser status request",
    0x74: "Immobiliser status",
    0x75: "Wiper status request",
    0x76: "Crash alarm",
    0x77: "Wiper status",
    0x78: "Seat memory",
    0x79: "Doors/flaps status request",
    0x7a: "Doors/flaps status",
    0x7c: "Sunroof Status",
    0x7d: "Sunroof Control",
    0x83: "AC Compressor Status",
    0x86: "Aux Heating/Vent Status",
    0x87: "Aux Heating/Vent Status Request",
    0x92: "Heater Status",
    0x93: "Heater Status Request",
    0x9f: "Headphone Status",
    0xa1: "Current Position Request",
    0xa2: "Current Position",
    0xa3: "Current Location Request",
    0xa4: "Current Location",
    0xa5: "Screen Text",
    0xa6: "Special Indicators",
    0xa7: "TMC Status Request",
    0xa8: "TMC Data",
    0xa9: "Telephone Data",
    0xaa: "Nav Control",
    0xab: "Remote Control Status",
    0xd4: "NG-RAD Station List"

}


class IBusWrite(QThread):
    error_signal = pyqtSignal()
    buffer_update_signal = pyqtSignal()

    def __init__(self, ibus_main):
        self.main = ibus_main
        super().__init__()

    def run(self):
        self.buffer_update_signal.emit()
        try:
            if self.main.writing:
                return

            self.main.writing = True

            while self.main.write_queue:
                packet = self.main.write_queue.pop(0)
                self.buffer_update_signal.emit()
                self.main.waiting_for_packet = packet

                while True:
                    if self.main.serial.in_waiting == 0:
                        self.main.serial.write(packet)
                        self.main.serial.flush()

                        timeout_counter = 0
                        while self.main.waiting_for_packet is not None:
                            if timeout_counter > 100:
                                break
                            timeout_counter += 1
                            time.sleep(0.01)

                        if timeout_counter <= 100:
                            break

                time.sleep(0.05)

            self.main.writing = False

        except SerialException:
            self.error_signal.emit()


class IBusRead(QThread):
    error_signal = pyqtSignal()
    buffer_update_signal = pyqtSignal()

    def __init__(self, ibus_main):
        self.main = ibus_main
        super().__init__()

    def run(self):
        try:
            while True:
                if not self.main.serial.is_open:
                    return False

                data = self.main.serial.read()
                self.main.read_buffer.extend(data)
                self.buffer_update_signal.emit()
                self.main.process_thread.start(QThread.Priority.TimeCriticalPriority)
        except AttributeError:
            return
        except SerialException:
            self.error_signal.emit()


class IBusProcess(QThread):
    signal = pyqtSignal(dict)
    buffer_update_signal = pyqtSignal()

    def __init__(self, ibus_main):
        self.main = ibus_main
        super().__init__()

    def run(self):
        self.buffer_update_signal.emit()
        if self.main.processing:
            return

        self.main.processing = True

        while len(self.main.read_buffer) != 0:
            if len(self.main.read_buffer) <= 4:
                break

            length = self.main.read_buffer[1]

            if length < 2:
                del self.main.read_buffer[0]
                continue

            if length > 50:
                del self.main.read_buffer[0]
                continue

            wanted_checksum = self.main.read_buffer[1 + length:2 + length]
            if not wanted_checksum:
                break

            checksum_bytes = self.main.read_buffer[0:1 + length]
            checksum = 0

            for byte in checksum_bytes:
                checksum ^= byte

            if wanted_checksum[0] != checksum:
                del self.main.read_buffer[0]
                break

            packet = self.main.read_buffer[0:2 + length]
            del self.main.read_buffer[0:2 + length]
            self.buffer_update_signal.emit()

            if not self.main.serial.is_open:
                return False

            self.main.waiting_for_packet = None
            self.signal.emit({"packet": packet})

        self.main.processing = False


class IBus:
    def __init__(self, port, data_function, error_function, buffer_update_function):
        self.reading = False
        self.processing = False
        self.writing = False
        self.read_buffer = bytearray()
        self.write_queue = []
        self.waiting_for_packet = None
        self.data_function = data_function
        self.error_function = error_function
        self.buffer_update_function = buffer_update_function

        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE
            )
            self.write_thread = IBusWrite(self)
            self.write_thread.error_signal.connect(self.error_function)
            self.write_thread.buffer_update_signal.connect(lambda: self.buffer_update_function(read=len(self.read_buffer), write=len(self.write_queue)))

            self.process_thread = IBusProcess(self)
            self.process_thread.signal.connect(lambda data: self.data_function(data["packet"]))
            self.process_thread.buffer_update_signal.connect(lambda: self.buffer_update_function(read=len(self.read_buffer), write=len(self.write_queue)))

            self.read_thread = IBusRead(self)
            self.read_thread.error_signal.connect(self.error_function)
            self.read_thread.buffer_update_signal.connect(lambda: self.buffer_update_function(read=len(self.read_buffer), write=len(self.write_queue)))
            self.read_thread.start()

        except SerialException as e:
            if "Permission denied" in str(e):
                self.error_function("Permission denied")
                return
            self.error_function()

    def stop(self):
        if hasattr(self, "serial"):
            self.serial.close()
        self.buffer_update_function(0, 0)

    def send_packet(self, source, dest, data):
        packet = b''
        packet += bytes(source)
        packet += bytes([2 + len(data)])
        packet += bytes(dest)
        packet += bytes(data)

        checksum = 0
        for byte in packet:
            checksum ^= byte

        packet += bytes([checksum])

        self.write_queue.append(packet)
        self.write_thread.start(QThread.Priority.TimeCriticalPriority)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("I/K-Bus Tool")
        self.setWindowIcon(QIcon(self.get_logo()))
        self.show()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.clear_after_writing = None
        self.serial_ports = []
        self.running = False
        self.data = []
        self.ibus = None
        self.file_data = None

        layout.addWidget(self._init_serial_ui())
        layout.addSpacing(8)
        layout.addWidget(self._init_write_ui())
        layout.addSpacing(8)
        layout.addWidget(self._init_write_file_ui())
        layout.addSpacing(8)
        layout.addWidget(self._init_read_ui())

        self.setMinimumSize(layout.sizeHint())

    @staticmethod
    def get_logo():
        image_data = base64.b64decode(
            "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")
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        return pixmap

    def _init_serial_ui(self):
        serial_container = QGroupBox("Serial")
        serial_container.setMaximumWidth(900)
        serial_layout = QGridLayout()
        serial_container.setLayout(serial_layout)

        self.serial_select = QComboBox()
        serial_layout.addWidget(self.serial_select, 0, 0, 1, 2)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedWidth(100)
        self.refresh_button.clicked.connect(partial(self.refresh_serial_devices, with_delay=True))
        serial_layout.addWidget(self.refresh_button, 0, 2)

        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setFixedWidth(100)
        self.start_stop_button.clicked.connect(self.start)
        serial_layout.addWidget(self.start_stop_button, 0, 3)

        self.serial_spacer = QWidget()
        self.serial_spacer.setFixedHeight(5)
        serial_layout.addWidget(self.serial_spacer, 1, 0, 1, 4)

        self.read_buffer = QProgressBar()
        self.read_buffer.setFixedHeight(24)
        self.read_buffer.setTextVisible(False)
        self.read_buffer.setMaximum(32)
        self.read_buffer_heading = QLabel("Read buffer (0/32)")
        serial_layout.addWidget(self.read_buffer_heading, 2, 0)
        serial_layout.addWidget(self.read_buffer, 2, 1, 1, 3)

        self.write_buffer = QProgressBar()
        self.write_buffer.setFixedHeight(24)
        self.write_buffer.setTextVisible(False)
        self.write_buffer.setMaximum(32)
        self.write_buffer_heading = QLabel("Write buffer (0/32)")
        self.write_buffer_heading.setFixedWidth(self.write_buffer_heading.sizeHint().width())
        self.read_buffer_heading.setFixedWidth(self.write_buffer_heading.sizeHint().width())
        serial_layout.addWidget(self.write_buffer_heading, 3, 0)
        serial_layout.addWidget(self.write_buffer, 3, 1, 1, 3)

        self.refresh_serial_devices()

        self.serial_spacer.hide()
        self.read_buffer.hide()
        self.write_buffer.hide()
        self.read_buffer_heading.hide()
        self.write_buffer_heading.hide()

        return serial_container

    def _init_t2d_ui(self):
        t2d_window = QWidget()
        t2d_window.setWindowIcon(QIcon(self.get_logo()))
        t2d_window.setWindowTitle("Text to Data")
        t2d_window.setFixedSize(300, 120)
        t2d_layout = QGridLayout()
        t2d_window.setLayout(t2d_layout)

        t2d_data_output = QLineEdit()
        t2d_data_output.setPlaceholderText("Data")
        t2d_data_output.setReadOnly(True)

        t2d_text_input = QLineEdit()
        t2d_text_input.setPlaceholderText("Text")
        t2d_text_input.textChanged[str].connect(lambda: t2d_data_output.setText(bytearray(str(t2d_text_input.text()).encode("latin-1", "replace")).hex(" ")))

        t2d_layout.addWidget(t2d_text_input, 0, 0, 1, 3)
        t2d_layout.addWidget(t2d_data_output, 1, 0, 1, 3)

        t2d_cancel_button = QPushButton("Cancel")
        t2d_cancel_button.clicked.connect(t2d_window.close)
        t2d_layout.addWidget(t2d_cancel_button, 2, 0)

        t2d_copy_button = QPushButton("Copy")
        t2d_copy_button.clicked.connect(lambda: (QApplication.clipboard().setText(t2d_data_output.text()), t2d_window.close()))
        t2d_layout.addWidget(t2d_copy_button, 2, 1)

        t2d_set_button = QPushButton("Set")
        t2d_set_button.clicked.connect(lambda: (self.write_data.setText(t2d_data_output.text()), t2d_window.close()))
        t2d_layout.addWidget(t2d_set_button, 2, 2)

        self.text_to_data = QPushButton("Text to Data")
        self.text_to_data.setFixedWidth(100)
        self.text_to_data.clicked.connect(lambda: (t2d_data_output.clear(), t2d_text_input.clear(), t2d_window.show(), t2d_text_input.focusWidget()))
        self.text_to_data.setEnabled(False)
        return self.text_to_data

    def _init_write_ui(self):
        write_container = QGroupBox("Write")
        write_container.setMaximumWidth(900)
        write_layout = QHBoxLayout()
        write_container.setLayout(write_layout)

        self.write_source = QLineEdit()
        self.write_source.setEnabled(False)
        self.write_source.setFixedWidth(100)
        self.write_source.setToolTip("e.g. 68")
        self.write_source.setToolTipDuration(0)
        self.write_source.setPlaceholderText("Source")
        write_layout.addWidget(self.write_source)

        self.write_dest = QLineEdit()
        self.write_dest.setEnabled(False)
        self.write_dest.setFixedWidth(100)
        self.write_dest.setToolTip("e.g. 6a")
        self.write_dest.setToolTipDuration(0)
        self.write_dest.setPlaceholderText("Destination")
        write_layout.addWidget(self.write_dest)

        self.write_data = QLineEdit()
        self.write_data.setEnabled(False)
        self.write_data.setPlaceholderText("Data (FF FF FF ..)")
        write_layout.addWidget(self.write_data)

        write_layout.addWidget(self._init_t2d_ui())

        self.write_button = QPushButton("Write")
        self.write_button.setEnabled(False)
        self.write_button.clicked.connect(self.write)
        self.write_button.setFixedWidth(100)
        write_layout.addWidget(self.write_button)

        return write_container

    def _init_write_file_ui(self):
        write_file_container = QGroupBox("Write File")
        write_file_container.setMaximumWidth(900)
        write_file_layout = QGridLayout()
        write_file_container.setLayout(write_file_layout)

        write_file_layout.addWidget(self._init_file_help_ui(), 0, 0)

        self.write_file_open = QPushButton("Open File")
        self.write_file_open.clicked.connect(self.open_write_file)
        self.write_file_open.setFixedWidth(100)
        write_file_layout.addWidget(self.write_file_open, 0, 1)

        self.write_file_button = QPushButton("Write")
        self.write_file_button.setEnabled(False)
        self.write_file_button.clicked.connect(self.write_file)
        self.write_file_button.setFixedWidth(100)
        write_file_layout.addWidget(self.write_file_button, 0, 2)

        interval_heading = QLabel("Interval:")
        interval_heading.setFixedWidth(interval_heading.sizeHint().width())
        write_file_layout.addWidget(interval_heading, 0, 3)

        self.write_file_interval = QSpinBox()
        self.write_file_interval.setMaximum(10000)
        self.write_file_interval.setMinimum(100)
        self.write_file_interval.setFixedWidth(60)
        self.write_file_interval.setEnabled(False)
        write_file_layout.addWidget(self.write_file_interval, 0, 4)

        interval_unit = QLabel("ms")
        interval_unit.setFixedWidth(interval_unit.sizeHint().width())
        write_file_layout.addWidget(interval_unit, 0, 5)

        write_file_layout.addWidget(QWidget(), 0, 6)

        self.write_file_name = QLabel()
        self.write_file_name.setAlignment(Qt.AlignmentFlag.AlignRight)
        write_file_layout.addWidget(self.write_file_name, 0, 7)

        self.write_file_spacer = QWidget()
        self.write_file_spacer.setFixedHeight(5)
        write_file_layout.addWidget(self.write_file_spacer, 1, 0, 1, 8)

        self.write_file_progress_heading = QLabel()
        write_file_layout.addWidget(self.write_file_progress_heading, 2, 0)

        self.write_file_progress = QProgressBar()
        self.write_file_progress.setFixedHeight(24)
        self.write_file_progress.setTextVisible(False)
        write_file_layout.addWidget(self.write_file_progress, 2, 1, 1, 7)

        self.write_file_progress_heading.hide()
        self.write_file_progress.hide()
        self.write_file_spacer.hide()

        return write_file_container

    def _init_read_ui(self):
        read_container = QWidget()
        read_layout = QGridLayout()
        read_layout.setContentsMargins(0, 0, 0, 0)
        read_container.setLayout(read_layout)

        self.output = QTableWidget()
        self.output.setStyleSheet("QTableView{border: 1px solid #d8d8d8;}")
        self.output.horizontalHeader().setStyleSheet("border: none; border-bottom: 1px solid #d8d8d8;")
        self.output.horizontalHeader().setStretchLastSection(True)
        self.output.verticalHeader().hide()
        self.output.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for index, text in enumerate(["Source", "Destination", "Type", "Decoded", "Hex"]):
            self.output.insertColumn(index)
            self.output.setHorizontalHeaderItem(index, QTableWidgetItem(text))

        read_layout.addWidget(self.output, 0, 0, 1, 6)

        spacer = QWidget()
        spacer.setFixedHeight(8)
        read_layout.addWidget(spacer, 1, 0, 1, 6)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedWidth(100)
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear)
        read_layout.addWidget(self.clear_button, 2, 0)

        self.scroll_to_bottom = QCheckBox("Scroll to bottom")
        self.scroll_to_bottom.setChecked(True)
        self.scroll_to_bottom.clicked.connect(lambda: (self.output.scrollToBottom() if self.scroll_to_bottom.isChecked() else False))
        read_layout.addWidget(self.scroll_to_bottom, 2, 1)

        self.save_bin_button = QPushButton("Save as BIN")
        self.save_bin_button.setFixedWidth(100)
        self.save_bin_button.setEnabled(False)
        self.save_bin_button.clicked.connect(self.save_bin)
        read_layout.addWidget(self.save_bin_button, 2, 2)

        self.save_hex_button = QPushButton("Save as Hex")
        self.save_hex_button.setFixedWidth(100)
        self.save_hex_button.setEnabled(False)
        self.save_hex_button.clicked.connect(self.save_hex)
        read_layout.addWidget(self.save_hex_button, 2, 3)

        self.save_text_button = QPushButton("Save as Text")
        self.save_text_button.setFixedWidth(100)
        self.save_text_button.setEnabled(False)
        self.save_text_button.clicked.connect(self.save_text)
        read_layout.addWidget(self.save_text_button, 2, 4)

        read_layout.addWidget(self._init_info_ui(), 2, 5)

        return read_container

    def _init_info_ui(self):
        info_window = QWidget()
        info_window.setWindowIcon(QIcon(self.get_logo()))
        info_window.setWindowTitle("Info")
        info_layout = QGridLayout()
        info_window.setLayout(info_layout)

        label_1 = QLabel("<a href='https://git.multilan.de/tarek/ik-bus-tool'>https://git.multilan.de/tarek/ik-bus-tool</a>")
        label_1.setOpenExternalLinks(True)
        label_2 = QLabel("<a href='https://www.e39-forum.de/wcf_wbb4/index.php?user/60063-tarek/'>https://www.e39-forum.de/wcf_wbb4/index.php?user/60063-tarek/</a>")
        label_2.setOpenExternalLinks(True)
        icon = QLabel()
        icon.setPixmap(self.get_logo().scaledToHeight(60))
        icon.setContentsMargins(0, 0, 10, 0)

        info_layout.addWidget(icon, 0, 0, 3, 1)
        info_layout.addWidget(QLabel("LIN-Bus (BMW I/K-Bus Protocol) Logger & Writer"), 0, 1)
        info_layout.addWidget(QLabel("© Copyright 2024 Tarek Poltermann"), 1, 1)
        info_layout.addWidget(label_1, 2, 1)
        info_layout.addWidget(label_2, 3, 1)

        info_button = QPushButton("i")
        info_button.setFixedWidth(25)
        info_button.clicked.connect(lambda: info_window.show())

        info_window.setFixedSize(info_layout.sizeHint())

        return info_button

    def _init_file_help_ui(self):
        help_window = QWidget()
        help_window.setWindowIcon(QIcon(self.get_logo()))
        help_window.setWindowTitle("Help")
        help_layout = QVBoxLayout()
        help_window.setLayout(help_layout)

        text = QLabel("Insert one command per line.\nLength and checksum will be calculated.\nUse a hex value as a placeholder.\n\nExample:\n68 FF 6A 01 FF\n6A FF FF 02 00 FF\nF0 FF 68 32 31 FF")

        help_layout.addWidget(text)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: help_window.close())
        help_layout.addWidget(ok_button)

        help_button = QPushButton("?")
        help_button.setFixedWidth(25)
        help_button.clicked.connect(lambda: help_window.show())

        help_window.setFixedSize(help_layout.sizeHint())

        return help_button

    def write(self):
        source = self.write_source.text().strip()
        dest = self.write_dest.text().strip()
        data = self.write_data.text().strip()

        if not source or not 0 < len(source) < 3:
            QMessageBox.critical(self, "Could not write", "Source input is invalid")
            return

        if not dest or not 0 < len(dest) < 3:
            QMessageBox.critical(self, "Could not write", "Destination input is invalid")
            return

        if not data:
            QMessageBox.critical(self, "Could not write", "Data input is invalid")
            return

        try:
            source = bytearray.fromhex(source)
        except ValueError:
            QMessageBox.critical(self, "Could not write", "Source input is invalid")
            return

        try:
            dest = bytearray.fromhex(dest)
        except ValueError:
            QMessageBox.critical(self, "Could not write", "Destination input is invalid")
            return

        try:
            data = bytearray.fromhex(data)
        except ValueError:
            QMessageBox.critical(self, "Could not write", "Data input is invalid")
            return

        if self.ibus:
            self.ibus.send_packet(source, dest, data)

            if self.clear_after_writing is None:
                clear_question = QMessageBox(self)
                clear_question.setWindowTitle("Clear after writing?")
                clear_question.setText("Do you want to clear the fields after writing?")
                clear_question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                clear_question.setIcon(QMessageBox.Icon.Question)
                result = clear_question.exec()

                if result == QMessageBox.StandardButton.Yes:
                    self.clear_after_writing = True
                else:
                    self.clear_after_writing = False

            if self.clear_after_writing:
                self.write_source.clear()
                self.write_dest.clear()
                self.write_data.clear()

    def write_file(self):
        if not self.file_data or not self.ibus:
            return

        self.write_file_progress_heading.show()
        self.write_file_progress.show()
        self.write_file_spacer.show()
        self.write_file_open.setEnabled(False)
        self.write_file_button.setEnabled(False)
        self.write_file_interval.setEnabled(False)
        self.write_dest.setEnabled(False)
        self.write_source.setEnabled(False)
        self.write_data.setEnabled(False)
        self.write_button.setEnabled(False)
        self.text_to_data.setEnabled(False)

        lines = self.file_data.splitlines()
        self.write_file_progress.setMaximum(len(lines))

        def write_packet(line_index=0):
            try:
                if self.ibus is None:
                    return

                packet = bytearray.fromhex(lines[line_index])
                self.ibus.send_packet(packet[0:1], packet[2:3], packet[3:-1])
                self.write_file_progress_heading.setText(f"Lines written ({line_index + 1}/{len(lines)})")
                self.write_file_progress.setValue(line_index + 1)

                QTimer.singleShot(int(self.write_file_interval.text()), lambda: (write_packet(line_index + 1)))

            except IndexError:
                self.write_file_progress_heading.hide()
                self.write_file_progress.hide()
                self.write_file_spacer.hide()
                self.write_file_open.setEnabled(True)
                self.write_file_button.setEnabled(True)
                self.write_file_interval.setEnabled(True)
                self.write_dest.setEnabled(True)
                self.write_source.setEnabled(True)
                self.write_data.setEnabled(True)
                self.write_button.setEnabled(True)
                self.text_to_data.setEnabled(True)

        write_packet()

    def open_write_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Open file for writing", filter="Text Files (*.txt);;All Files (*)")[0]

        try:
            with open(file_path) as file:
                content = str(file.read())
                for line in content.splitlines():
                    bytearray.fromhex(line)

                self.file_data = content
                self.write_file_name.setText(os.path.basename(file_path))

                if self.write_button.isEnabled():
                    self.write_file_button.setEnabled(True)

        except UnicodeDecodeError:
            QMessageBox.critical(self, "Decode Error", "Cannot decode file content")
            self.file_data = None
            self.write_file_name.clear()
            self.write_file_button.setEnabled(False)

        except ValueError:
            QMessageBox.critical(self, "File Error", "The file content is invalid")
            self.file_data = None
            self.write_file_name.clear()
            self.write_file_button.setEnabled(False)

    def refresh_serial_devices(self, with_delay=False):
        self.serial_select.setEnabled(False)
        self.refresh_button.setEnabled(False)

        self.serial_select.clear()
        self.serial_ports.clear()
        for port in serial.tools.list_ports.comports():
            friendly_port_name = port.description
            if port.name not in friendly_port_name:
                friendly_port_name += f" ({port.name})"
            self.serial_select.addItem(friendly_port_name)
            self.serial_ports.append(port.device)

        if with_delay:
            QTimer.singleShot(500, lambda: (self.serial_select.setEnabled(True), self.refresh_button.setEnabled(True)))
        else:
            self.serial_select.setEnabled(True)
            self.refresh_button.setEnabled(True)

    def closeEvent(self, a0):
        if self.ibus:
            self.ibus.stop()

    def save_bin(self):
        file_path = QFileDialog.getSaveFileName(self, "Save as BIN", filter="Binary Files (*.bin);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "wb") as file:
            for packet in self.data:
                file.write(packet)
        QMessageBox.information(self, "File saved", "File successfully saved as BIN")

    def save_hex(self):
        file_path = QFileDialog.getSaveFileName(self, "Save as Hex", filter="Text Files (*.txt);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "w") as file:
            for packet in self.data:
                _, _, _, message = self.parse_packet(packet)
                file.write(f"{message}\n")
        QMessageBox.information(self, "File saved", "File successfully saved as Hex")

    def save_text(self):
        file_path = QFileDialog.getSaveFileName(self, "Save as Text", filter="Text Files (*.txt);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "w") as file:
            for packet in self.data:
                source_dev, dest_dev, message_name, message = self.parse_packet(packet)
                decoded = packet[2:-1].replace(b"\n", b"").replace(b"\r", b"").decode("ascii", errors="ignore")
                file.write(f"{source_dev} -> {dest_dev} - {message_name}: {message} ({decoded})\n")
        QMessageBox.information(self, "File saved", "File successfully saved as Text")

    @staticmethod
    def parse_packet(packet):
        try:
            source_dev_name = "Unknown"
            dest_dev_name = "Unknown"
            message_name = "Unknown"

            source_dev = packet[0]
            dest_dev = packet[2]
            message_type = packet[3]

            if source_dev in devs.keys():
                source_dev_name = devs[source_dev]
            if dest_dev in devs.keys():
                dest_dev_name = devs[dest_dev]
            if message_type in commands.keys():
                message_name = commands[message_type]

            formatted_line = packet.hex(" ").upper()

            return source_dev_name, dest_dev_name, message_name, formatted_line

        except IndexError:
            return None

    def add_data(self, packet):
        if packet:
            self.save_hex_button.setEnabled(True)
            self.save_bin_button.setEnabled(True)
            self.save_text_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.data.append(packet)

            source_dev, dest_dev, message_name, message = self.parse_packet(packet)
            row = self.output.rowCount()
            decoded = packet[3:-1].replace(b"\n", b"").replace(b"\r", b"").decode("ascii", errors="ignore")
            self.output.insertRow(row)
            self.output.setRowHeight(row, 18)
            self.output.setItem(row, 0, QTableWidgetItem(source_dev))
            self.output.setItem(row, 1, QTableWidgetItem(dest_dev))
            self.output.setItem(row, 2, QTableWidgetItem(message_name))
            self.output.setItem(row, 3, QTableWidgetItem(decoded))
            self.output.setItem(row, 4, QTableWidgetItem(message))

            if self.scroll_to_bottom.isChecked():
                self.output.scrollToBottom()

    def start(self):
        if self.running:
            self.reset()

        else:
            if self.data:
                self.clear()

            self.running = True
            self.start_stop_button.setText("Stop")
            self.serial_select.setEnabled(False)
            self.refresh_button.setEnabled(False)

            self.write_source.setEnabled(True)
            self.write_dest.setEnabled(True)
            self.write_data.setEnabled(True)
            self.text_to_data.setEnabled(True)
            self.write_button.setEnabled(True)

            self.write_file_open.setEnabled(True)
            if self.file_data:
                self.write_file_button.setEnabled(True)
            self.write_file_interval.setEnabled(True)

            self.serial_spacer.show()
            self.read_buffer.show()
            self.write_buffer.show()
            self.read_buffer_heading.show()
            self.write_buffer_heading.show()

            serial_port = self.serial_ports[self.serial_select.currentIndex()]
            self.ibus = IBus(serial_port, self.add_data, self.error_occurred, self.buffer_update)

    def reset(self):
        self.running = False
        self.start_stop_button.setText("Start")
        self.serial_select.setEnabled(True)
        self.refresh_button.setEnabled(True)

        self.write_source.setEnabled(False)
        self.write_dest.setEnabled(False)
        self.write_data.setEnabled(False)
        self.text_to_data.setEnabled(False)
        self.write_button.setEnabled(False)

        self.write_file_open.setEnabled(True)
        self.write_file_button.setEnabled(False)
        self.write_file_interval.setEnabled(False)
        self.write_file_spacer.hide()
        self.write_file_progress.hide()
        self.write_file_progress_heading.hide()

        self.serial_spacer.hide()
        self.read_buffer.hide()
        self.write_buffer.hide()
        self.read_buffer_heading.hide()
        self.write_buffer_heading.hide()

        if self.ibus:
            self.ibus.stop()

    def buffer_update(self, read, write):
        self.write_buffer.setValue(write)
        self.read_buffer.setValue(read)
        self.write_buffer_heading.setText(f"Write buffer ({write}/32)")
        self.read_buffer_heading.setText(f"Read buffer ({read}/32)")

        if read > 32:
            self.read_buffer.setStyleSheet("QProgressBar::chunk{background-color: red;}")
        else:
            self.read_buffer.setStyleSheet("")

        if write > 32:
            self.write_buffer.setStyleSheet("QProgressBar::chunk{background-color: red;}")
        else:
            self.write_buffer.setStyleSheet("")

    def clear(self):
        clear_question = QMessageBox(self)
        clear_question.setWindowTitle("Clear data?")
        clear_question.setText("Do you want to clear the existing data?")
        clear_question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        clear_question.setIcon(QMessageBox.Icon.Question)
        result = clear_question.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.data.clear()
            self.output.setRowCount(0)
            self.save_hex_button.setEnabled(False)
            self.save_bin_button.setEnabled(False)
            self.save_text_button.setEnabled(False)
            self.clear_button.setEnabled(False)

    def error_occurred(self, message="Could not communicate with serial device"):
        self.reset()
        self.refresh_serial_devices()
        QMessageBox.critical(self, "Serial error", message)


sys.excepthook = lambda exc_type, exc_val, tracebackobj: print(''.join(traceback.format_exception(exc_type, exc_val, tracebackobj)))

main = QApplication(sys.argv)
ex = Main()
sys.exit(main.exec())
