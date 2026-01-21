import traceback
from PySide6.QtWidgets import QDialog, QGridLayout, QComboBox, QGroupBox, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QEvent, QTime, QDate, QTimer
from bus.frame import BusFrame
from gui.widgets.display import DisplayWidget
from gui.helper import get_logo, slugify


class SimulationInput:
    fire_on_change = False

    def __init__(self, area, title, on_change):
        self.area = area
        self._on_change_func = on_change
        self.config = area.config
        self.config_name = f"{area.main.config_prefix}_{area.config_prefix}_{slugify(title)}"
        self.val = getattr(self.config, self.config_name)
        self.fire_on_change = True
        self.trigger_on_change = True

    def on_change(self):
        if not self.fire_on_change or not self.trigger_on_change:
            return

        if self._on_change_func:
            self._on_change_func(self)

        if self.area.on_input_change:
            self.area.on_input_change(self)

        self.save()

    def save(self):
        setattr(self.config, self.config_name, self.val)

    @property
    def val(self):
        return None

    @property
    def val_raw(self):
        return None

    @val.setter
    def val(self, value):
        pass

    @val_raw.setter
    def val_raw(self, value):
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

    @property
    def val(self):
        return self.value

    @property
    def val_raw(self):
        return self.val

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.value = value
        self.save()

    @val_raw.setter
    def val_raw(self, value):
        self.val = value


class SimulationFloatInput(SimulationInput, QDoubleSpinBox):
    def __init__(self, area: SimulationArea, title, min_val=0, max_val=100, val_step=0.1, val_decimals=1, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QDoubleSpinBox.__init__(self)

        self.valueChanged.connect(self.on_change)

        index = area.input_index
        area.layout.add_widget(QLabel(title), index, 0)
        area.layout.add_widget(self, index, 1)
        area.input_index += 1

        self.minimum = min_val
        self.maximum = max_val
        self.decimals = val_decimals
        self.single_step = val_step

        SimulationInput.__init__(self, area, title, on_change)

    @property
    def val(self):
        return self.value

    @property
    def val_raw(self):
        return self.val

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.value = value
        self.save()

    @val_raw.setter
    def val_raw(self, value):
        self.val = value


class SimulationTimeInput(SimulationInput, QTimeEdit):
    def __init__(self, area: SimulationArea, title, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QTimeEdit.__init__(self)

        self.timeChanged.connect(self.on_change)

        index = area.input_index
        area.layout.add_widget(QLabel(title), index, 0)
        area.layout.add_widget(self, index, 1)
        area.input_index += 1

        self.display_format = "HH:mm"

        SimulationInput.__init__(self, area, title, on_change)

    @property
    def val(self):
        return self.time.to_string("HH-mm")

    @property
    def val_raw(self):
        return self.val

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.time = QTime.from_string(value, "HH-mm")
        self.save()

    @val_raw.setter
    def val_raw(self, value):
        self.val = value


class SimulationDateInput(SimulationInput, QDateEdit):
    def __init__(self, area: SimulationArea, title, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QDateEdit.__init__(self)

        self.dateChanged.connect(self.on_change)

        index = area.input_index
        area.layout.add_widget(QLabel(title), index, 0)
        area.layout.add_widget(self, index, 1)
        area.input_index += 1

        self.display_format = "dd.MM.yyyy"

        SimulationInput.__init__(self, area, title, on_change)

    @property
    def val(self):
        return self.date.to_string("dd-MM-yyyy")

    @property
    def val_raw(self):
        return self.val

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.date = QDate.from_string(value, "dd-MM-yyyy")
        self.save()

    @val_raw.setter
    def val_raw(self, value):
        self.val = value


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

    @property
    def val(self):
        value = self.val_raw

        if value is None or not self.bit_shift:
            return value

        return value * (2 ** self.bit_shift)

    @property
    def val_raw(self):
        return self.items.get(self.current_text)

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.val_raw = value // (2 ** self.bit_shift)

    @val_raw.setter
    def val_raw(self, value):
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

        self.save()


class SimulationCheckBoxInput(SimulationInput, QCheckBox):
    def __init__(self, area: SimulationArea, title, checked_value=1, on_change=None):
        from __feature__ import snake_case, true_property  # noqa
        QCheckBox.__init__(self)

        self.checked_value = checked_value
        self.text = title
        self.toggled.connect(self.on_change)

        area.layout.add_widget(self, area.checkbox_index, 3)
        area.checkbox_index += 1

        SimulationInput.__init__(self, area, title, on_change)

    @property
    def val(self):
        if self.checked:
            return self.checked_value

        return 0x00

    @property
    def val_raw(self):
        return self.val

    @val.setter
    def val(self, value):
        if value is None:
            return

        self.checked = value == self.checked_value
        self.save()

    @val_raw.setter
    def val_raw(self, value):
        self.val = value


class SimulationButtonInput(QPushButton):
    def __init__(self, area: SimulationArea, text, on_press=None, on_release=None, on_hold=None):
        from __feature__ import snake_case, true_property  # noqa
        QPushButton.__init__(self)

        self.text = text
        self.set_fixed_size(200, 50)
        self.on_press_func = on_press
        self.on_release_func = on_release
        self.on_hold_func = on_hold
        self.pressed_down = False

        self.pressed.connect(self._on_press)
        self.released.connect(self._on_release)

        area.layout.add_widget(self, area.input_index, 0)
        area.input_index += 1

    def _on_press(self):
        self.pressed_down = True
        QTimer.single_shot(600, self._on_hold)

        if self.on_press_func:
            self.on_press_func()

    def _on_release(self):
        self.pressed_down = False

        if self.on_release_func:
            self.on_release_func()

    def _on_hold(self):
        if not self.pressed_down:
            return

        if self.on_hold_func:
            self.on_hold_func()


class SimulationDisplay(DisplayWidget):
    def __init__(self, area: SimulationArea):
        from __feature__ import snake_case, true_property  # noqa
        DisplayWidget.__init__(self, char_count=20, check_control=True)

        area.layout.add_widget(self, area.input_index, 0)
        area.input_index += 1


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

        main_window.install_event_filter(self)

        if getattr(self.config, f"{self.config_prefix}_open"):
            self.show()

    def event_filter(self, obj, ev):
        if obj is self.parent() and ev.type() == QEvent.Close:
            setattr(self.config, f"{self.config_prefix}_open", self.visible)

        return False

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

    def show_event(self, e):
        self.serial_manager.frame_received.connect(self._frame_received)
        self.serial_manager.bus_state_changed.connect(self._bus_state_changed)
        self.show()

        if self.bus_active:
            self.announce()

        super().show_event(e)

    @staticmethod
    def build_byte(*inputs):
        byte = 0x00
        for i in inputs:
            byte |= i.val
        return byte
