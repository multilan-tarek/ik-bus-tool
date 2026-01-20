import traceback
from PySide6.QtWidgets import QDialog, QGridLayout, QComboBox, QGroupBox, QLabel, QCheckBox, QSpinBox, QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QCoreApplication
from bus.frame import BusFrame
from gui.helper import get_logo, slugify


class SimulationInput:
    def __init__(self, area, title, on_change):
        self.fire_on_change = False
        self.area = area
        self.on_change_overwrite = on_change
        self.config = area.config
        self.config_name = f"{area.main.config_prefix}_{area.config_prefix}_{slugify(title)}"
        self.val = getattr(self.config, self.config_name)
        self.fire_on_change = True

    def on_change(self):
        if not self.fire_on_change:
            return

        if self.on_change_overwrite:
            self.on_change_overwrite(self)
        else:
            self.area.on_input_change(self)

        setattr(self.config, self.config_name, self.val)

    @property
    def val(self):
        return None

    @val.setter
    def val(self, value):
        pass


class SimulationArea(QGroupBox):
    def __init__(self, parent, title, on_input_change, grid_x, grid_y, grid_x_stretch=1, grid_y_stretch=1):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.config = parent.config
        self.title = title
        self.config_prefix = slugify(title)
        self.main = parent
        self.input_index = 0
        self.checkbox_index = 0
        self.on_input_change = on_input_change
        self.layout = QGridLayout(self)
        self.layout.set_alignment(Qt.AlignTop | Qt.AlignHCenter)
        self.layout.set_horizontal_spacing(18)
        self.layout.set_vertical_spacing(10)

        self.main.layout.add_widget(self, grid_y, grid_x, grid_y_stretch, grid_x_stretch)


class SimulationNumberInput(SimulationInput, QSpinBox):
    def __init__(self, area: SimulationArea, title, min_val=0, max_val=100, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QSpinBox.__init__(self)

        self.valueChanged.connect(self.on_change)

        index = area.input_index
        area.layout.add_widget(QLabel(title), index, 0)
        area.layout.add_widget(self, index, 1)
        area.input_index += 1

        self.minimum = min_val
        self.maximum = max_val

        SimulationInput.__init__(self, area, title, on_change)

    def on_change(self):
        super().on_change()

    @property
    def val(self):
        return self.value

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.value = value


class SimulationSelectInput(SimulationInput, QComboBox):
    def __init__(self, area: SimulationArea, title, items, bit_shift=0, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QComboBox.__init__(self)

        self.items = items
        self.bit_shift = bit_shift
        self.add_items(list(self.items.keys()))
        self.currentTextChanged.connect(self.on_change)

        index = area.input_index
        area.layout.add_widget(QLabel(title), index, 0)
        area.layout.add_widget(self, index, 1)
        area.input_index += 1

        SimulationInput.__init__(self, area, title, on_change)

    def on_change(self):
        super().on_change()

    @property
    def val(self):
        value = self.items.get(self.current_text)

        if value is None or not self.bit_shift:
            return value

        return value * 2 ** self.bit_shift

    @val.setter
    def val(self, value):
        if value is None:
            return

        available_values = list(self.items.values())

        if value not in available_values:
            traceback.format_exc()
            return

        index = available_values.index(value)
        text = list(self.items.keys())[index]
        select_index = self.find_text(text)

        if select_index >= 0:
            self.current_index = select_index


class SimulationCheckBoxInput(SimulationInput, QCheckBox):
    def __init__(self, area: SimulationArea, title, checked_value, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QCheckBox.__init__(self)

        self.checked_value = checked_value
        self.text = title
        self.toggled.connect(self.on_change)

        area.layout.add_widget(self, area.checkbox_index, 3)
        area.checkbox_index += 1

        SimulationInput.__init__(self, area, title, on_change)

    def on_change(self):
        super().on_change()

    @property
    def val(self):
        if self.checked:
            return self.checked_value

        return 0x00

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.checked = value == self.checked_value


class SimulationBase(QDialog):
    def __init__(self, main_window, title, device_id):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window)

        self.frame_routing = {
            0x01: self.pong
        }
        self.device_id = device_id
        self.device_id_filters = [device_id]
        self.device_variant = 0x00
        self.config = main_window.config
        self.bus_active = False
        self.serial_manager = main_window.serial_manager
        self.window_title = title
        self.config_prefix = slugify(title)
        self.window_icon = QIcon(get_logo())
        self.layout = QGridLayout(self)
        self.layout.set_alignment(Qt.AlignTop | Qt.AlignHCenter)

        app = QApplication.instance()
        app.aboutToQuit.connect(self._app_quiting)

        if getattr(self.config, f"{self.config_prefix}_open"):
            self.open()

    def _frame_received(self, frame):
        if frame.dest not in self.device_id_filters or frame.cmd not in self.frame_routing.keys():
            return

        for cmd, func in self.frame_routing.items():
            if cmd == frame.cmd:
                func(frame)

    def _bus_state_changed(self, state):
        self.bus_active = state
        if state:
            self.announce()

    def announce(self):
        frame = BusFrame(self.device_id, 0xBF, 0x02, [0x01 | self.device_variant])
        self.serial_manager.transmit_frame(frame)

    def pong(self, frame):
        frame = BusFrame(self.device_id, frame.source, 0x02, [self.device_variant])
        self.serial_manager.transmit_frame(frame)

    def open(self):
        self.serial_manager.frame_received.connect(self._frame_received)
        self.serial_manager.bus_state_changed.connect(self._bus_state_changed)
        self.show()

        if self.bus_active:
            self.announce()

        setattr(self.config, f"{self.config_prefix}_open", True)

    @staticmethod
    def build_byte(*inputs):
        byte = 0x00
        for i in inputs:
            byte |= i.val
        return byte

    def _app_quiting(self):
        print(self.visible)

        #setattr(self.config, f"{self.config_prefix}_open", True)

    def close_event(self, event):

        #print(QCoreApplication.closingDown())
#
        #setattr(self.config, f"{self.config_prefix}_open", False)
        self.hide()
        event.ignore()

    def hide_event(self, e):
        print("HIDE")
        e.ignore()
        return
        super().hide_event(e)