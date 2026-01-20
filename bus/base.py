from PySide6.QtCore import Signal, QObject, QThread

from bus.frame import BusFrame
from bus.process import BusProcess
from bus.receive import BusReceive
from serial import SerialException, Serial, EIGHTBITS, PARITY_EVEN, STOPBITS_ONE

from bus.transmit import BusTransmit


class Bus(QObject):
    error_occurred = Signal(Exception)
    frame_received = Signal(BusFrame)

    def __init__(self, port):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.serial = None
        self.receive_buffer = bytearray()
        self.transmit_queue = []
        self.processing = False
        self.transmitting = False

        try:
            self.serial = Serial(
                port=port.device,
                baudrate=9600,
                bytesize=EIGHTBITS,
                parity=PARITY_EVEN,
                stopbits=STOPBITS_ONE
            )

            self.transmit_thread = BusTransmit(self.transmit_queue, self.serial)
            self.transmit_thread.error_occurred.connect(self.thread_error_occurred)
            self.transmit_thread.finished.connect(self.transmitting_finished)

            self.process_thread = BusProcess(self.receive_buffer)
            self.process_thread.error_occurred.connect(self.thread_error_occurred)
            self.process_thread.frame_received.connect(self.thread_frame_received)
            self.process_thread.finished.connect(self.processing_finished)

            self.receive_thread = BusReceive(self.serial)
            self.receive_thread.error_occurred.connect(self.thread_error_occurred)
            self.receive_thread.data_received.connect(self.data_received)
            self.receive_thread.start()

        except SerialException as e:
            self.error_occurred.emit(e)
            return

    def thread_error_occurred(self, e):
        self.error_occurred.emit(e)

    def data_received(self, data):
        self.receive_buffer.extend(data)

        if not self.processing:
            self.processing = True
            self.process_thread.start(QThread.Priority.TimeCriticalPriority)

    def thread_frame_received(self, frame):
        self.frame_received.emit(frame)

    def processing_finished(self):
        self.processing = False

    def transmitting_finished(self):
        self.transmitting = False

    def stop(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

        print("Stopping Threads...")
        self.transmit_thread.request_interruption()
        self.transmit_thread.quit()
        self.transmit_thread.wait()

        self.process_thread.request_interruption()
        self.process_thread.quit()
        self.process_thread.wait()

        self.receive_thread.request_interruption()
        self.receive_thread.quit()
        self.receive_thread.wait()

    def transmit_frame(self, frame):
        self.transmit_queue.append(frame)

        if not self.transmitting:
            self.transmitting = True
            self.transmit_thread.start(QThread.Priority.TimeCriticalPriority)
