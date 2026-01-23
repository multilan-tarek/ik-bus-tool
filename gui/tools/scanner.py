import time
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QTableWidget, QAbstractItemView, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QTableWidgetItem
from bus.frame import BusFrame, BUS_DEVICES
from gui.helper import get_logo

SCANNER_ADDR = 0xFE

SCANNER_ADDR_BLACKLIST = [0x3f, 0xff, 0xbf, 0xfe, 0xe7]


class ScannerThread(QThread):
    status_update = Signal(BusFrame)
    scan_done = Signal()
    scan_stopped = Signal()

    def __init__(self, serial_manager):
        super().__init__()
        self.serial_manager = serial_manager

    def run(self):
        for addr in BUS_DEVICES.keys():
            if addr in SCANNER_ADDR_BLACKLIST:
                continue

            frame = BusFrame(SCANNER_ADDR, addr, 0x01, [])
            self.status_update.emit(frame)
            self.serial_manager.transmit_frame(frame)

            for _ in range(50):
                if self.is_interruption_requested():
                    self.scan_stopped.emit()
                    return
                self.msleep(10)

        self.scan_done.emit()

class Scanner(QDialog):
    def __init__(self, main_window):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window)

        self.serial_manager = main_window.serial_manager
        self.serial_manager.frame_received.connect(self.frame_received)

        self.thread = ScannerThread(self.serial_manager)
        self.thread.scan_done.connect(self.scan_done)
        self.thread.status_update.connect(self.status_update)
        self.thread.scan_stopped.connect(self.scan_stopped)

        self.found_devices = []

        self.window_title = "Bus Scanner"
        self.window_icon = QIcon(get_logo())
        self.set_fixed_size(400, 400)

        self.button = QPushButton("Start Scan")
        self.button.clicked.connect(self.toggle_scan)

        self.status = QLabel()

        self.table = QTableWidget()
        #self.table.style_sheet = "QTableView{border: 1px solid #d8d8d8;}"
        self.table.vertical_header().hide()
        self.table.horizontal_header().stretch_last_section = True
        self.table.edit_triggers = QAbstractItemView.EditTrigger.NoEditTriggers
        self.table.column_count = 2
        self.table.set_horizontal_header_labels(["Address", "Name"])

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.add_widget(self.button)
        header_layout.add_stretch(1)
        header_layout.add_widget(self.status)

        layout = QVBoxLayout(self)
        layout.add_widget(header)
        layout.add_widget(self.table)

    def toggle_scan(self):
        if self.thread.is_running():
            self.stop_scan()
        else:
            self.start_scan()

    def frame_received(self, frame):
        if frame.source in self.found_devices or frame.source in SCANNER_ADDR_BLACKLIST or not self.thread.is_running():
            return

        self.found_devices.append(frame.source)

        row = self.table.row_count
        self.table.insert_row(row)
        self.table.set_row_height(row, 18)
        self.table.set_item(row, 0, QTableWidgetItem(f"{frame.source:02X}"))
        self.table.set_item(row, 1, QTableWidgetItem(BUS_DEVICES.get(frame.source, "Unknown")))

    def start_scan(self):
        self.button.text = "Stop Scan"
        self.status.text = "Scan started"

        self.table.clear_contents()
        self.table.row_count = 0
        self.found_devices.clear()

        self.thread.start()

    def stop_scan(self):
        self.thread.request_interruption()
        self.thread.wait()

    def scan_done(self):
        self.button.text = "Restart Scan"
        self.status.text = "Scan done"

    def scan_stopped(self):
        self.button.text = "Start Scan"
        self.status.text = "Scan stopped"

    def status_update(self, frame):
        self.status.text = f"Checking {frame.dest_str} ({frame.dest:02X})..."

    def hide_event(self, _):
        self.stop_scan()

    def show_event(self, _):
        self.table.clear_contents()
        self.table.row_count = 0
        self.found_devices.clear()
        self.status.text = ""
        self.button.text = "Start Scan"
