import time
from queue import Empty
from random import randint

from PySide6.QtCore import QThread, Signal
from serial.serialutil import SerialException

IDLE_TIME = 0.004


class BusTransmit(QThread):
    error_occurred = Signal()
    collision_retries = 0
    collision_backoff_base = 10

    def __init__(self, transmit_queue, serial, collision_data):
        self.transmit_queue = transmit_queue
        self.serial = serial
        self.collision_data = collision_data
        self.last_rx_time = time.monotonic()
        super().__init__()

    def clear_echo_queue(self):
        q = self.collision_data.echo_queue
        while True:
            try:
                q.get_nowait()
            except Empty:
                break

    def run(self):
        try:

            while self.transmit_queue:
                frame = self.transmit_queue.pop(0)

                if not self.serial or not self.serial.is_open:
                    return

                # wait for bus idle
                while True:
                    if self.is_interruption_requested():
                        return

                    if (time.monotonic() - self.collision_data.last_receive_time) >= IDLE_TIME and self.serial.in_waiting == 0:
                        break

                    self.msleep(1)

                self.collision_data.transmit_active = True

                for byte in frame.raw:
                    if self.is_interruption_requested():
                        return

                    self.serial.write(bytes([byte]))

                    try:
                        echo = self.collision_data.echo_queue.get(timeout=0.03)
                    except Empty:
                        echo = None

                    if echo != byte:
                        self.collision_data.transmit_active = False
                        self.transmit_queue.insert(0, frame)

                        self.collision_retries += 1
                        self.collision_retries = min(self.collision_retries, 6)

                        backoff_time = self.collision_backoff_base * (2 ** self.collision_retries)
                        backoff_time += randint(0, self.collision_backoff_base)
                        backoff_time = min(200, backoff_time)

                        self.msleep(backoff_time)
                        self.run()
                        return

                self.collision_data.transmit_active = False
                self.collision_retries = 0
                self.clear_echo_queue()

        except SerialException:
            self.error_occurred.emit()
