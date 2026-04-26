from functools import partial
from random import randint, uniform
from PySide6.QtCore import QDate, QTime
from bus.frame import BusFrame
from gui.helper import encode_string
from gui.simulation.base import SimulationBase, SimulationArea, SimulationNumberInput, SimulationSelectInput, SimulationCheckBoxInput, SimulationFloatInput, SimulationTimeInput, SimulationDateInput, SimulationButtonInput, SimulationDisplay


class IKESimulation(SimulationBase):
    def __init__(self, main_window):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window, "IKE/KMB Simulation", 0x80)

        self.frame_routing[0x10] = self.transmit_ignition_status
        self.frame_routing[0x12] = self.transmit_sensor_status
        self.frame_routing[0x14] = self.transmit_coding
        self.frame_routing[0x15] = self.update_coding
        self.frame_routing[0x16] = self.transmit_odometer
        self.frame_routing[0x41] = self.process_bc_request
        self.frame_routing[0x23] = self.process_display_text

        self._init_ignition_status_area()
        self._init_sensor_status_area()
        self._init_coding_area()
        self._init_odometer_area()
        self._init_bc_data_area()
        self._init_button_area()
        self._init_display_area()

    def _init_ignition_status_area(self):
        self.ignition_states = {
            "KL-30": 0x00,
            "KL-R": 0x01,
            "KL-15": 0x03,
            "KL-50": 0x07,
        }

        area = SimulationArea(self, "Ignition Status", self.transmit_ignition_status, 0, 0)

        self.ignition_state = SimulationSelectInput(area, "State", self.ignition_states)

    def _init_sensor_status_area(self):
        self.sensor_status_variants = {
            "0x0A Bytes (New)": 0x0A,
            "0x06 Bytes (Old)": 0x06
        }

        self.sensor_status_gears = {
            "Unknown": 0x00,
            "Park": 0xB0,
            "Reverse": 0x10,
            "Neutral": 0x70,
            "1st Gear": 0x20,
            "2nd Gear": 0x60,
            "3rd Gear": 0xD0,
            "4th Gear": 0xC0,
            "5th Gear": 0xE0,
            "6th Gear": 0xF0,
        }

        area = SimulationArea(self, "Sensor Status", self.transmit_sensor_status, 0, 1, grid_x_stretch=3)

        self.sensor_status_variant = SimulationSelectInput(area, "Variant", self.sensor_status_variants)
        self.sensor_status_gear = SimulationSelectInput(area, "Gear", self.sensor_status_gears)
        self.sensor_status_fuel_level = SimulationNumberInput(area, "Fuel Level")
        self.sensor_status_handbrake = SimulationCheckBoxInput(area, "Handbrake On", 0x01)
        self.sensor_status_oil_pressure = SimulationCheckBoxInput(area, "Oil Pressure Fault", 0x02)
        self.sensor_status_brake_pads = SimulationCheckBoxInput(area, "Brake Pads Fault", 0x04)
        self.sensor_status_transmission = SimulationCheckBoxInput(area, "Transmission Fault", 0x10)
        self.sensor_status_engine = SimulationCheckBoxInput(area, "Engine Running", 0x01)
        self.sensor_status_door = SimulationCheckBoxInput(area, "Drivers Door Open", 0x02)
        self.sensor_status_aux_heat = SimulationCheckBoxInput(area, "Aux. Heating On", 0x04)
        self.sensor_status_aux_heat.enabled = False
        self.sensor_status_aux_vent = SimulationCheckBoxInput(area, "Aux. Venting On", 0x08)
        self.sensor_status_aux_vent.enabled = False

    def _init_coding_area(self):
        self.coding_languages = {
            "DE": 0x00,
            "EN (GB)": 0x01,
            "EN (US)": 0x02,
            "IT": 0x03,
            "ES": 0x04,
            "JP": 0x05,
            "FR": 0x06,
            "EN (CA)": 0x07,
            "GOLF": 0x08
        }

        self.coding_cluster_types = {
            "E38, E39/E53 HIGH": 0x00,
            "E39/E53 LOW": 0x30,
            "E46 Variant A": 0x40,
            "E46 Variant B": 0x60,
            "E46 Variant C": 0xF0,
            "E83, E85": 0xA0,
        }

        self.coding_time_formats = {
            "24H": 0x00,
            "12H": 0x01
        }

        self.coding_temp_units = {
            "°C": 0x00,
            "°F": 0x01
        }

        self.coding_speed_units = {
            "km/h": 0x00,
            "mph": 0x01
        }

        self.coding_distance_units = {
            "km": 0x00,
            "mls": 0x01
        }

        self.coding_consumption_units = {
            "l/100km": 0x00,
            "mpg (UK)": 0x01,
            "mpg (US)": 0x04,
            "km/l": 0x03
        }

        self.coding_memo_types = {
            "IKE": 0x00,
            "LCM": 0x80
        }

        self.coding_engine_types = {
            "Gasoline": 0x00,
            "Diesel": 0x08
        }

        self.coding_aux_ctl_types = {
            "Before PU96": 0x00,
            "After PU96": 0x40,
        }

        area = SimulationArea(self, "Coding", self.transmit_coding, 3, 0, grid_y_stretch=2)

        self.coding_cluster_type = SimulationSelectInput(area, "Cluster Type", self.coding_cluster_types)
        self.coding_language = SimulationSelectInput(area, "Language", self.coding_languages)
        self.coding_time_format = SimulationSelectInput(area, "Time Format", self.coding_time_formats, on_change=self._sync_time_formats)
        self.coding_temp_unit = SimulationSelectInput(area, "Temp Unit", self.coding_temp_units, 1)
        self.coding_avg_speed_unit = SimulationSelectInput(area, "Avg. Speed Unit", self.coding_speed_units, 4, on_change=self._sync_speed_units)
        self.coding_speed_limit_unit = SimulationSelectInput(area, "Speed Limit Unit", self.coding_speed_units, 5, on_change=self._sync_speed_units)
        self.coding_distance_unit = SimulationSelectInput(area, "Distance Unit", self.coding_distance_units, 6, on_change=self._sync_distance_units)
        self.coding_arrival_time_format = SimulationSelectInput(area, "Arrival Time Format", self.coding_time_formats, 7, on_change=self._sync_time_formats)
        self.coding_consumption_1_unit = SimulationSelectInput(area, "Consumption 1 Unit", self.coding_consumption_units, on_change=self._sync_consumption_units)
        self.coding_consumption_2_unit = SimulationSelectInput(area, "Consumption 2 Unit", self.coding_consumption_units, 2, on_change=self._sync_consumption_units)
        self.coding_range_unit = SimulationSelectInput(area, "Range Unit", self.coding_distance_units, 4, on_change=self._sync_distance_units)
        self.coding_aux_timer_1_format = SimulationSelectInput(area, "Aux. Timer 1 Format", self.coding_time_formats, 5, on_change=self._sync_time_formats)
        self.coding_aux_timer_2_format = SimulationSelectInput(area, "Aux. Timer 2 Format", self.coding_time_formats, 6, on_change=self._sync_time_formats)
        self.coding_memo_type = SimulationSelectInput(area, "Memo Type", self.coding_memo_types)
        self.coding_engine_type = SimulationSelectInput(area, "Engine Type", self.coding_engine_types)
        self.coding_aux_ctl_type = SimulationSelectInput(area, "Aux. Controller Type", self.coding_aux_ctl_types)
        self.coding_bc_resume = SimulationCheckBoxInput(area, "BC Resume at KL-R", 0x04)
        self.coding_bc_speed_correction = SimulationCheckBoxInput(area, "BC Speed Correction", 0x08)
        self.coding_aux_heat = SimulationCheckBoxInput(area, "Aux. Heating", 0x01)
        self.coding_aux_vent = SimulationCheckBoxInput(area, "Aux. Venting", 0x02)
        self.coding_rcc_time = SimulationCheckBoxInput(area, "RCC Time", 0x10)

        self.coding_sim_sync_formats_units = SimulationCheckBoxInput(area, "[Sim] Sync Formats/Units", on_change=self._sync_formats_and_units)

    def _init_display_area(self):
        area = SimulationArea(self, "Display", None, 0, 3, grid_x_stretch=5)
        self.display = SimulationDisplay(area)

    def _sync_formats_and_units(self, _):
        if not self.coding_sim_sync_formats_units.val:
            return

        self._sync_time_formats(self.coding_time_format)
        self._sync_speed_units(self.coding_speed_limit_unit)
        self._sync_distance_units(self.coding_distance_unit)
        self._sync_consumption_units(self.coding_consumption_1_unit)

    def _sync_consumption_units(self, source):
        if not self.coding_sim_sync_formats_units.val:
            return

        self.coding_consumption_1_unit.trigger_on_change = False
        self.coding_consumption_2_unit.trigger_on_change = False

        value = source.val_raw
        self.coding_consumption_1_unit.val_raw = value
        self.coding_consumption_2_unit.val_raw = value

        self.coding_consumption_1_unit.trigger_on_change = True
        self.coding_consumption_2_unit.trigger_on_change = True

        self.transmit_bc_data(None, 0x04)
        self.transmit_bc_data(None, 0x05)

    def _sync_distance_units(self, source):
        if not self.coding_sim_sync_formats_units.val:
            return

        self.coding_distance_unit.trigger_on_change = False
        self.coding_range_unit.trigger_on_change = False

        value = source.val_raw
        self.coding_distance_unit.val_raw = value
        self.coding_range_unit.val_raw = value

        self.coding_distance_unit.trigger_on_change = True
        self.coding_range_unit.trigger_on_change = True

        self.transmit_bc_data(None, 0x06)
        self.transmit_bc_data(None, 0x07)

    def _sync_speed_units(self, source):
        if not self.coding_sim_sync_formats_units.val:
            return

        self.coding_speed_limit_unit.trigger_on_change = False
        self.coding_avg_speed_unit.trigger_on_change = False

        value = source.val_raw
        self.coding_speed_limit_unit.val_raw = value
        self.coding_avg_speed_unit.val_raw = value

        self.coding_speed_limit_unit.trigger_on_change = True
        self.coding_avg_speed_unit.trigger_on_change = True

        self.transmit_bc_data(None, 0x09)
        self.transmit_bc_data(None, 0x0A)

    def _sync_time_formats(self, source):
        if not self.coding_sim_sync_formats_units.val:
            return

        self.coding_time_format.trigger_on_change = False
        self.coding_arrival_time_format.trigger_on_change = False
        self.coding_aux_timer_1_format.trigger_on_change = False
        self.coding_aux_timer_2_format.trigger_on_change = False

        value = source.val_raw
        self.coding_time_format.val_raw = value
        self.coding_arrival_time_format.val_raw = value
        self.coding_aux_timer_1_format.val_raw = value
        self.coding_aux_timer_2_format.val_raw = value

        self.coding_time_format.trigger_on_change = True
        self.coding_arrival_time_format.trigger_on_change = True
        self.coding_aux_timer_1_format.trigger_on_change = True
        self.coding_aux_timer_2_format.trigger_on_change = True

        self.transmit_bc_data(None, 0x01)
        self.transmit_bc_data(None, 0x08)
        self.transmit_bc_data(None, 0x0F)
        self.transmit_bc_data(None, 0x10)

    def _init_odometer_area(self):
        area = SimulationArea(self, "Odometer", self.transmit_odometer, 1, 0)

        self.odometer = SimulationNumberInput(area, "Value", min_val=0, max_val=999999)

    def _init_bc_data_area(self):
        area = SimulationArea(self, "BC Data", None, 4, 0, grid_y_stretch=2)

        self.bc_time = SimulationTimeInput(area, "Time", on_change=partial(self.transmit_bc_data, target=0x01))
        self.bc_date = SimulationDateInput(area, "Date", on_change=partial(self.transmit_bc_data, target=0x02))
        self.bc_temperature = SimulationFloatInput(area, "Temperature", min_val=-40, max_val=99, on_change=partial(self.transmit_bc_data, target=0x03))
        self.bc_consumption_1 = SimulationFloatInput(area, "Consumption 1", min_val=0, max_val=99, on_change=partial(self.transmit_bc_data, target=0x04))
        self.bc_consumption_2 = SimulationFloatInput(area, "Consumption 2", min_val=0, max_val=99, on_change=partial(self.transmit_bc_data, target=0x05))
        self.bc_range = SimulationNumberInput(area, "Range", min_val=0, max_val=999, on_change=partial(self.transmit_bc_data, target=0x06))
        self.bc_distance = SimulationNumberInput(area, "Distance", min_val=0, max_val=9999, on_change=partial(self.transmit_bc_data, target=0x07))
        self.bc_arrival = SimulationTimeInput(area, "Arrival Time", on_change=partial(self.transmit_bc_data, target=0x08))
        self.bc_speed_limit = SimulationNumberInput(area, "Speed Limit", min_val=6, max_val=299, on_change=partial(self.transmit_bc_data, target=0x09))
        self.bc_avg_speed = SimulationFloatInput(area, "Avg. Speed", min_val=0, max_val=299, on_change=partial(self.transmit_bc_data, target=0x0A))
        self.bc_timer = SimulationFloatInput(area, "Timer", min_val=0, max_val=9999999, on_change=partial(self.transmit_bc_data, target=0x0E))
        self.bc_timer_lap = SimulationFloatInput(area, "Timer Lap", min_val=0, max_val=9999999, on_change=partial(self.transmit_bc_data, target=0x1A))
        self.bc_aux_timer_1 = SimulationTimeInput(area, "Aux. Timer 1", on_change=partial(self.transmit_bc_data, target=0x0F))
        self.bc_aux_timer_2 = SimulationTimeInput(area, "Aux. Timer 2", on_change=partial(self.transmit_bc_data, target=0x10))

        self.bc_memo_on = SimulationCheckBoxInput(area, "Memo On", 0x20, on_change=self.transmit_bc_status)
        self.bc_timer_running = SimulationCheckBoxInput(area, "Timer Running", 0x08, on_change=self.transmit_bc_status)
        self.bc_speed_limit_on = SimulationCheckBoxInput(area, "Speed Limit On", 0x02, on_change=self.transmit_bc_status)
        self.bc_code_set = SimulationCheckBoxInput(area, "Code Set", 0x40, on_change=self.transmit_bc_status)
        self.bc_aux_heat_on = SimulationCheckBoxInput(area, "Aux. Heating On", 0x20, on_change=self.transmit_bc_status)
        self.bc_aux_vent_on = SimulationCheckBoxInput(area, "Aux. Venting On", 0x08, on_change=self.transmit_bc_status)
        self.bc_aux_timer_1_on = SimulationCheckBoxInput(area, "Aux. Timer 1 On", 0x04, on_change=self.transmit_bc_status)
        self.bc_aux_timer_2_on = SimulationCheckBoxInput(area, "Aux. Timer 2 On", 0x10, on_change=self.transmit_bc_status)

    def _init_button_area(self):
        area = SimulationArea(self, "Buttons", None, 2, 0)

        SimulationButtonInput(area, "Check Button",
                              on_press=partial(self.transmit_button_state, button=0x01, state=0x00),
                              on_release=partial(self.transmit_button_state, button=0x01, state=0x40))

        SimulationButtonInput(area, "BC Button",
                              on_press=partial(self.transmit_button_state, button=0x02, state=0x00),
                              on_release=partial(self.transmit_button_state, button=0x02, state=0x40))

    def transmit_ignition_status(self, _):
        frame = BusFrame(0x80, 0xBF, 0x11, [self.ignition_state.val])
        self.serial_manager.transmit_frame(frame)

    def transmit_sensor_status(self, _):
        data = [self.build_byte(
            self.sensor_status_handbrake,
            self.sensor_status_oil_pressure,
            self.sensor_status_brake_pads,
            self.sensor_status_transmission
        ), self.build_byte(
            self.sensor_status_engine,
            self.sensor_status_door,
            self.sensor_status_gear
        ), self.build_byte(
            self.sensor_status_aux_vent,
            self.sensor_status_aux_heat
        )]

        variant = self.sensor_status_variant.val
        if variant == 0x0A:
            data.extend([0x00, 0x00, 0x00, 0x00, self.sensor_status_fuel_level.val])

        frame = BusFrame(0x80, 0xBF, 0x13, data)
        self.serial_manager.transmit_frame(frame)

    def transmit_coding(self, _):
        data = [
            self.build_byte(
                self.coding_language,
                self.coding_cluster_type
            ),
            self.build_byte(
                self.coding_time_format,
                self.coding_temp_unit,
                self.coding_bc_resume,
                self.coding_bc_speed_correction,
                self.coding_avg_speed_unit,
                self.coding_speed_limit_unit,
                self.coding_distance_unit,
                self.coding_arrival_time_format
            ),
            self.build_byte(
                self.coding_consumption_1_unit,
                self.coding_consumption_2_unit,
                self.coding_range_unit,
                self.coding_aux_timer_1_format,
                self.coding_aux_timer_2_format,
                self.coding_memo_type
            ),
            self.build_byte(
                self.coding_aux_heat,
                self.coding_aux_vent,
                self.coding_engine_type,
                self.coding_rcc_time,
                self.coding_aux_ctl_type
            ),
        ]

        frame = BusFrame(0x80, 0xBF, 0x15, data)
        self.serial_manager.transmit_frame(frame)

    def transmit_odometer(self, _):
        odometer = self.odometer.val

        data = [
            odometer & 0xFF,
            (odometer >> 8) & 0xFF,
            (odometer >> 16) & 0xFF
        ]

        frame = BusFrame(0x80, 0xBF, 0x17, data)
        self.serial_manager.transmit_frame(frame)

    def transmit_bc_data(self, _, target):
        string = ""

        match target:
            case 0x01:
                value = QTime.from_string(self.bc_time.val, "HH-mm")
                string = value.to_string("h:mmAP") if self.coding_time_format.val else value.to_string("HH:mm")
                string = string.rjust(7)

            case 0x02:
                value = QDate.from_string(self.bc_date.val, "dd-MM-yyyy")
                string = value.to_string("dd/MM/yyyy") if self.coding_time_format.val else value.to_string("dd.MM.yyyy")
                string = string.rjust(10)

            case 0x03:
                prefix = "+" if self.bc_temperature.val >= 0 else ""
                string = f"{prefix}{self.bc_temperature.val:.1f}".ljust(5)

            case 0x04 | 0x05:
                suffix = "L/100"
                value = self.bc_consumption_1.val if target == 0x04 else self.bc_consumption_2.val
                string = f"{value:.1f} {suffix}".ljust(10)

            case 0x06:
                suffix = "MLS" if self.coding_range_unit.val else "KM"
                value = str(self.bc_range.val).rjust(3)
                string = f"{value} {suffix}".ljust(7)

            case 0x07:
                suffix = "MLS" if self.coding_distance_unit.val else "KM"
                value = str(self.bc_distance.val).rjust(3)
                string = f"{value} {suffix}".ljust(8)

            case 0x08:
                value = QTime.from_string(self.bc_arrival.val, "HH-mm")
                string = value.to_string("h:mmAP") if self.coding_arrival_time_format.val else value.to_string("HH:mm")
                string = string.rjust(7)

            case 0x09:
                suffix = "MPH" if self.coding_speed_limit_unit.val else "KM/H"
                value = str(self.bc_speed_limit.val).rjust(2)
                string = f"{value} {suffix}".ljust(8)

            case 0x0A:
                suffix = "MPH" if self.coding_avg_speed_unit.val else "KM/H"
                value = self.bc_avg_speed.val
                string = f"{value:.1f}" if value < 100 else f"{value:.0f}"
                string = f"{string} {suffix}".ljust(9)

            case 0x0E | 0x1A:
                suffix = "SEC"
                value = self.bc_timer.val if target == 0x0E else self.bc_timer_lap.val
                string = f"{value:.1f}" if value < 60 else f"{value:.0f}"

                if target == 0x0E:
                    string = string.rjust(4)

                string = f"{string} {suffix}".ljust(10)

            case 0x0F:
                value = QTime.from_string(self.bc_aux_timer_1.val, "HH-mm")
                string = value.to_string("h:mmAP") if self.coding_aux_timer_1_format.val else value.to_string("HH:mm")
                string = string.rjust(7)

            case 0x10:
                value = QTime.from_string(self.bc_aux_timer_2.val, "HH-mm")
                string = value.to_string("h:mmAP") if self.coding_aux_timer_2_format.val else value.to_string("HH:mm")
                string = string.rjust(7)

        data = [target, 0x00]
        data.extend(encode_string(string))

        frame = BusFrame(0x80, 0xE7, 0x24, data)
        self.serial_manager.transmit_frame(frame)

    def transmit_bc_status(self, _):
        self.sensor_status_aux_heat.val = self.sensor_status_aux_heat.checked_value if self.bc_aux_heat_on.val else 0x00
        self.sensor_status_aux_vent.val = self.sensor_status_aux_vent.checked_value if self.bc_aux_vent_on.val else 0x00

        data = [
            self.build_byte(
                self.bc_memo_on,
                self.bc_timer_running,
                self.bc_speed_limit_on,
            ),
            self.build_byte(
                self.bc_code_set,
                self.bc_aux_heat_on,
                self.bc_aux_vent_on,
                self.bc_aux_timer_1_on,
                self.bc_aux_timer_2_on
            )
        ]

        frame = BusFrame(0x80, 0xE7, 0x2A, data)
        self.serial_manager.transmit_frame(frame)

    def transmit_button_state(self, button, state):
        frame = BusFrame(0x80, 0xFF, 0x57, [button | state])
        self.serial_manager.transmit_frame(frame)

    def update_coding(self, frame):
        data = frame.data

        byte_1 = data[0]
        self.coding_language.val = byte_1 & 0x0F
        self.coding_cluster_type.val = byte_1 & 0xF0

        byte_2 = data[1]
        self.coding_time_format.val = byte_2 & 0x01
        self.coding_temp_unit.val = byte_2 & 0x02
        self.coding_bc_resume.val = byte_2 & 0x04
        self.coding_bc_speed_correction.val = byte_2 & 0x08
        self.coding_avg_speed_unit.val = byte_2 & 0x10
        self.coding_speed_limit_unit.val = byte_2 & 0x20
        self.coding_distance_unit.val = byte_2 & 0x40
        self.coding_arrival_time_format.val = byte_2 & 0x80

        byte_3 = data[2]
        self.coding_consumption_1_unit.val = byte_3 & 0x03
        self.coding_consumption_2_unit.val = byte_3 & 0x0C
        self.coding_range_unit.val = byte_3 & 0x10
        self.coding_aux_timer_1_format.val = byte_3 & 0x20
        self.coding_aux_timer_2_format.val = byte_3 & 0x40
        self.coding_memo_type.val = byte_3 & 0x80

        byte_4 = data[3]
        self.coding_aux_heat.val = byte_4 & 0x01
        self.coding_aux_vent.val = byte_4 & 0x02
        self.coding_engine_type.val = byte_4 & 0x08
        self.coding_rcc_time.val = byte_4 & 0x10
        self.coding_aux_ctl_type.val = byte_4 & 0x40

        self.transmit_coding(None)

    def process_display_text(self, frame):
        self.display.data = frame.data[2:]


        # 62 30   C6 C8 20 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 B2 AC

    def process_bc_request(self, frame):
        property_id = frame.data[0]

        match property_id:
            case 0x11:
                self.bc_aux_heat_on.val = 0x00
            case 0x12:
                self.bc_aux_heat_on.val = self.bc_aux_heat_on.checked_value
            case 0x13:
                self.bc_aux_vent_on.val = 0x00
            case 0x14:
                self.bc_aux_vent_on.val = self.bc_aux_vent_on.checked_value
            case 0x11 | 0x12 | 0x13 | 0x14:
                self.transmit_bc_status(None)

        if frame.length < 0x05:
            return

        control = frame.data[1]

        match control:
            case 0x01:
                self.transmit_bc_data(None, property_id)
            case 0x02:
                self.transmit_bc_status(None)

            case 0x04 | 0x08:
                match property_id:
                    case 0x0C:
                        self.bc_memo_on.val = self.bc_memo_on.checked_value if control == 0x04 else 0x00
                    case 0x09:
                        self.bc_speed_limit_on.val = self.bc_speed_limit_on.checked_value if control == 0x04 else 0x00
                    case 0x0E:
                        self.bc_timer_running.val = self.bc_timer_running.checked_value if control == 0x04 else 0x00
                    case 0x0F:
                        self.bc_aux_timer_1_on.val = self.bc_aux_timer_1_on.checked_value if control == 0x04 else 0x00
                    case 0x10:
                        self.bc_aux_timer_2_on.val = self.bc_aux_timer_2_on.checked_value if control == 0x04 else 0x00

                self.transmit_bc_status(None)

            case 0x10:
                match property_id:
                    case 0x04:
                        self.bc_consumption_1.val = uniform(1.0, 90.0)
                    case 0x05:
                        self.bc_consumption_2.val = uniform(1.0, 90.0)
                    case 0x0A:
                        self.bc_avg_speed.val = uniform(0.0, 250)

                self.transmit_bc_data(None, property_id)

            case 0x20:
                self.bc_speed_limit.val = randint(6, 299)
                self.transmit_bc_data(None, property_id)

    def announce(self):
        super().announce()

        self.transmit_odometer(None)
        self.transmit_coding(None)
        self.transmit_ignition_status(None)
        self.transmit_sensor_status(None)
        self.transmit_bc_status(None)
        self.transmit_bc_data(None, 0x01)
        self.transmit_bc_data(None, 0x02)
        self.transmit_bc_data(None, 0x03)
        self.transmit_bc_data(None, 0x04)
        self.transmit_bc_data(None, 0x05)
        self.transmit_bc_data(None, 0x06)
        self.transmit_bc_data(None, 0x07)
        self.transmit_bc_data(None, 0x08)
        self.transmit_bc_data(None, 0x09)
        self.transmit_bc_data(None, 0x0A)
        self.transmit_bc_data(None, 0x0E)
        self.transmit_bc_data(None, 0x1A)
        self.transmit_bc_data(None, 0x0F)
        self.transmit_bc_data(None, 0x10)