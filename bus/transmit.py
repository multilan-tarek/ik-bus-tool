from PySide6.QtCore import QThread, Signal
from serial.serialutil import SerialException
import time

class BusTransmit(QThread):
    error_occurred = Signal()

    def __init__(self, transmit_queue, serial):
        self.transmit_queue = transmit_queue
        self.serial = serial
        super().__init__()

    def run(self):
        try:
            while self.transmit_queue:
                frame = self.transmit_queue.pop(0)

                while True:
                    if self.serial.in_waiting == 0:
                        self.serial.write(frame.raw)
                        self.serial.flush()
                        break

                        #timeout_counter = 0
                        #while self.main.waiting_for_packet is not None:
                        #    if timeout_counter > 100:
                        #        break
                        #    timeout_counter += 1
                        #    time.sleep(0.01)
#
                        #if timeout_counter <= 100:
                        #    break

                time.sleep(0.05)


        except SerialException:
            self.error_occurred.emit()
