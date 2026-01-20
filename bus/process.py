from PySide6.QtCore import QThread, Signal
from bus.frame import BusFrame


class BusProcess(QThread):
    error_occurred = Signal(Exception)
    frame_received = Signal(BusFrame)

    def __init__(self, receive_buffer):
        super().__init__()
        self.receive_buffer = receive_buffer

    def run(self):
        while len(self.receive_buffer) != 0:
            if len(self.receive_buffer) <= 4:
                break

            length = self.receive_buffer[1]
            frame_length = length + 2

            if length < 2:
                del self.receive_buffer[0]
                continue

            if frame_length > len(self.receive_buffer):
                break

            checksum = self.receive_buffer[frame_length - 1]
            checksum_bytes = self.receive_buffer[0:frame_length - 1]

            checksum_calced = 0
            for byte in checksum_bytes:
                checksum_calced ^= byte

            if checksum != checksum_calced:
               del self.receive_buffer[0]
               continue

            frame_raw = self.receive_buffer[0:frame_length]
            frame = BusFrame.from_data(frame_raw)
            self.frame_received.emit(frame)

            del self.receive_buffer[0:frame_length]

            if self.is_interruption_requested():
                return
