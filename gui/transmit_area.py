from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QMessageBox
from bus.frame import BUS_DEVICES, BUS_COMMANDS, BusFrame


class TransmitDataInput(QLineEdit):
    def __init__(self, config, config_setting):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.config = config
        self.config_setting = config_setting
        self.enabled = False

        self.textChanged.connect(self.text_changed)
        self.text = getattr(self.config, self.config_setting)

    def text_changed(self, text):
        setattr(self.config, self.config_setting, text)

    def value(self):
        value = self.text

        if not value:
            return None

        try:
            value = bytearray.fromhex(value)
        except ValueError:
            return None

        return value


class TransmitInput(QComboBox):
    def __init__(self, presets, config, config_setting):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.config = config
        self.config_setting = config_setting
        self.insert_policy = QComboBox.InsertPolicy.NoInsert
        self.editable = True
        self.enabled = False
        self.add_items(presets)

        line_edit = self.line_edit()
        line_edit.textChanged.connect(self.text_changed)
        line_edit.text = getattr(self.config, self.config_setting)

    def text_changed(self, text):
        setattr(self.config, self.config_setting, text)

    def value(self):
        value = self.line_edit().text

        if ":" in value:
            value = value[:value.find(":")]

        if not value or not 0 < len(value) < 3:
            return None

        try:
            value = bytearray.fromhex(value)
        except ValueError:
            return None

        return value


class TransmitArea(QGroupBox):
    def __init__(self, config, serial_manager):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.serial_manager = serial_manager
        self.serial_manager.bus_state_changed.connect(self.bus_state_changed)

        self.title = "Send Frame"
        layout = QHBoxLayout(self)

        device_presets = self.get_device_presets()
        command_presets = self.get_command_presets()

        self.source = TransmitInput(device_presets, config, "transmit_source")
        layout.add_widget(self.source)

        self.dest = TransmitInput(device_presets, config, "transmit_dest")
        layout.add_widget(self.dest)

        self.cmd = TransmitInput(command_presets, config, "transmit_cmd")
        layout.add_widget(self.cmd)

        self.data = TransmitDataInput(config, "transmit_data")
        layout.add_widget(self.data)

        self.button = QPushButton("Send")
        self.button.enabled = False
        self.button.clicked.connect(self.send_frame)
        layout.add_widget(self.button)

    def send_frame(self):
        source = self.source.value()
        dest = self.dest.value()
        cmd = self.cmd.value()
        data = self.data.value()

        if not source:
            QMessageBox.critical(self, "Could not send frame", "Source input is invalid")

        if not dest:
            QMessageBox.critical(self, "Could not send frame", "Destination input is invalid")

        if not cmd:
            QMessageBox.critical(self, "Could not send frame", "Command input is invalid")

        if not self.serial_manager.bus:
            return

        frame = BusFrame(source[0], dest[0], cmd[0], data)
        self.serial_manager.transmit_frame(frame)

    @staticmethod
    def get_device_presets():
        device_presets = []

        for address, name in BUS_DEVICES.items():
            device_presets.append(f"{address:02X}: {name}")

        return device_presets

    @staticmethod
    def get_command_presets():
        command_presets = []

        for cmd, name in BUS_COMMANDS.items():
            command_presets.append(f"{cmd:02X}: {name}")

        return command_presets

    def bus_state_changed(self, state):
        if state:
            self.button.enabled = True
            self.data.enabled = True
            self.cmd.enabled = True
            self.dest.enabled = True
            self.source.enabled = True
            return

        self.button.enabled = False
        self.data.enabled = False
        self.cmd.enabled = False
        self.dest.enabled = False
        self.source.enabled = False
