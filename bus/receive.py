import time
from PySide6.QtCore import QThread, Signal

class BusReceive(QThread):
    error_occurred = Signal(Exception)
    data_received = Signal(bytes)

    def __init__(self, serial, collision_data):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.serial = serial
        self.collision_data = collision_data

    def run(self):
        try:
            while True:
                if not self.serial.is_open or self.is_interruption_requested():
                    return

                data = self.serial.read(1)

                if not len(data):
                    continue

                self.collision_data.last_receive_time = time.monotonic()

                if self.collision_data.transmit_active:
                    self.collision_data.echo_queue.put_nowait(data[0])

                self.data_received.emit(data)

        except Exception as e:
            self.error_occurred.emit(e)

