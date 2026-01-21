from functools import partial
from random import randint, uniform
from PySide6.QtCore import QDate, QTime, QTimer
from bus.frame import BusFrame
from gui.helper import encode_string
from gui.simulation.base import SimulationBase, SimulationArea, SimulationNumberInput, SimulationSelectInput, SimulationCheckBoxInput, SimulationFloatInput, SimulationTimeInput, SimulationDateInput, SimulationButtonInput, SimulationDisplay


class MFLSimulation(SimulationBase):
    def __init__(self, main_window):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window, "MFL Simulation", 0x50)

        self._init_button_area()
        self._init_mode_area()

        self.vol_hold_direction = 0x00
        self.vol_hold_timer = QTimer(interval=100)
        self.vol_hold_timer.timeout.connect(lambda: self.transmit_volume(self.vol_hold_direction))

        self.set_fixed_size(self.size_hint)

    def _init_mode_area(self):
        area = SimulationArea(self, "Mode", None, 0, 0)
        self.mode_checkbox = SimulationCheckBoxInput(area, "Phone Mode", 0x40)
        self.mode_checkbox.enabled = False

    def _init_button_area(self):
        area = SimulationArea(self, "Buttons", None, 0, 1)

        buttons = {
            "Up": 0x01,
            "Down": 0x08,
            "Vol Up": 0xF01,
            "Vol Down": 0xF00,
            "R/T": 0x40,
            "Call/Talk": 0x80,
            "Recirculation": 0x3A,
        }

        for name, attrs in buttons.items():
            SimulationButtonInput(
                area, name,
                on_press=partial(self.transmit_button_state, button=attrs, state=0x00),
                on_release=partial(self.transmit_button_state, button=attrs, state=0x20),
                on_hold=partial(self.transmit_button_state, button=attrs, state=0x10),
            )

    def transmit_volume(self, direction):
        dest = 0x68 if self.mode_checkbox.val == 0x00 else 0xC8
        frame = BusFrame(0x50, dest, 0x32, [0x10 | direction])
        self.serial_manager.transmit_frame(frame)

    def transmit_button_state(self, button, state):
        if button == 0x40:
            if state != 0x00: return

            self.mode_checkbox.val = 0x40 if self.mode_checkbox.val == 0x00 else 0x00
            self.transmit_mode()
            return

        elif button == 0x3A:
            if state != 0x00: return

            frame = BusFrame(0x50, 0x5B, 0x3A, [])
            self.serial_manager.transmit_frame(frame)
            return

        elif button in [0xF00, 0xF01]:
            direction = (button & 0x01)

            if state == 0x10:
                self.vol_hold_direction = direction
                self.vol_hold_timer.start()

            elif state == 0x20:
                self.vol_hold_timer.stop()

            elif state == 0x00:
                self.transmit_volume(button & 0x01)

            return

        dest = 0x68 if self.mode_checkbox.val == 0x00 and button != 0x80 else 0xC8
        frame = BusFrame(0x50, dest, 0x3B, [button | state])
        self.serial_manager.transmit_frame(frame)

    def transmit_mode(self):
        frame = BusFrame(0x50, 0xC8, 0x3B, [self.mode_checkbox.val])
        self.serial_manager.transmit_frame(frame)

    def announce(self):
        super().announce()
        self.transmit_mode()