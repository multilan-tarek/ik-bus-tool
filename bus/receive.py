from PySide6.QtCore import QThread, Signal
from serial import SerialException


class BusReceive(QThread):
    error_occurred = Signal(Exception)
    data_received = Signal(bytes)

    def __init__(self, serial):
        super().__init__()
        self.serial = serial

    def run(self):
        try:
            while True:
                if not self.serial.is_open:
                    return

                data = self.serial.read()

                if self.is_interruption_requested():
                    return

                if data:
                    self.data_received.emit(data)

        except SerialException as e:
            self.error_occurred.emit(e)

        except TypeError:
            return