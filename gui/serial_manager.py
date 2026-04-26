import glob
import sys
from functools import partial
from PySide6.QtCore import QTimer, Signal, QObject
from serial.tools import list_ports
from serial.tools.list_ports_linux import SysFS

from bus.base import Bus
from bus.frame import BusFrame


class SerialManager(QObject):
    error_occurred = Signal(Exception)
    frame_received = Signal(BusFrame)
    bus_state_changed = Signal(bool)

    def __init__(self, config):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.config = config
        self.check_timer = None
        self.menu = None
        self.menu_start = None
        self.menu_auto_start = None
        self.menu_ports = None
        self.ports = self.get_ports()

        self.selected_port = None
        self.bus = None

    @staticmethod
    def get_ports():
        ports = list_ports.comports()

        if sys.platform == "linux" or sys.platform == "linux2":
            devices = glob.glob('/dev/lin/*')

            for device in devices:
                sys_fs = SysFS(device)

                if sys_fs.subsystem == "platform":
                    continue

                sys_fs.description = f"LIN Bus {sys_fs.name.upper()}"
                sys_fs.name = sys_fs.description

                ports.append(sys_fs)

        return ports

    def load_port_config(self):
        for port in self.ports:
            if port.device == self.config.serial_selected_port:
                self.selected_port = port
                break

        if self.config.serial_auto_start and self.selected_port is not None:
            self.start()

    def check_ports(self):
        available_ports = self.get_ports()

        if self.ports == available_ports: return
        self.ports = available_ports

        if self.selected_port not in self.ports:
            self.selected_port = None

        self.refresh_menu()

    def init_menu(self, menu_bar):
        self.menu = menu_bar.add_menu("&Serial")

        self.menu_start = self.menu.add_action("Start")
        self.menu_start.triggered.connect(lambda: self.toggle_start_stop())

        self.menu_auto_start = self.menu.add_action("Auto Start")
        self.menu_auto_start.checkable = True
        self.menu_auto_start.checked = self.config.serial_auto_start or False
        self.menu_auto_start.toggled.connect(self._auto_start_toggled)

        self.menu_ports = self.menu.add_menu("&Port")

        self.load_port_config()
        self.refresh_menu()

        self.check_timer = QTimer()
        self.check_timer.interval = 500
        self.check_timer.timeout.connect(self.check_ports)
        self.check_timer.start()

    def _auto_start_toggled(self):
        self.config.serial_auto_start = self.menu_auto_start.checked

    def select_port(self, port):
        self.selected_port = port
        self.config.serial_selected_port = port.device
        self.refresh_menu()

    def refresh_menu(self):
        self.menu_start.enabled = self.selected_port is not None
        self.menu_ports.clear()

        if self.selected_port:
            self.menu_ports.title = f"Port ({self.selected_port.name})"
        else:
            self.menu_ports.title = "Port"

        for port in self.ports:
            port_name = port.description
            if port.name not in port_name:
                port_name += f" ({port.name})"

            port_action = self.menu_ports.add_action(port_name)
            port_action.checkable = True
            port_action.checked = port == self.selected_port
            port_action.triggered.connect(partial(lambda p: self.select_port(p), p=port))

    def toggle_start_stop(self):
        if self.bus:
            self.stop()
        else:
            self.start()

    def stop(self):
        self.menu_start.text = "Start"
        self.menu_ports.enabled = True

        if self.bus:
            self.bus.stop()
            self.bus = None

        self.bus_state_changed.emit(False)

    def start(self):
        if self.selected_port is None:
            self.menu_start.enabled = False
            return

        self.menu_start.text = "Stop"
        self.menu_ports.enabled = False

        self.bus = Bus(self.selected_port)
        self.bus.error_occurred.connect(self.bus_error_occurred)
        self.bus.frame_received.connect(self.bus_frame_received)
        self.bus.start()

        self.bus_state_changed.emit(True)

    def transmit_frame(self, frame):
        if self.bus:
            self.bus.transmit_frame(frame)

    def bus_frame_received(self, frame):
        self.frame_received.emit(frame)

    def bus_error_occurred(self, e):
        self.error_occurred.emit(e)
        self.stop()
