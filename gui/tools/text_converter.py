from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QGridLayout, QLineEdit, QGroupBox, QPushButton, QApplication
from gui.helper import get_logo, encode_string, decode_string
from gui.widgets.display import DisplayWidget


class TextConverter(QDialog):
    def __init__(self, main_window):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window)

        self.window_title = "Text Converter"
        self.window_icon = QIcon(get_logo())

        self.decoded_data = QLineEdit()
        self.decoded_data.textEdited.connect(self.decoded_data_changed)

        self.decoded_data_copy = QPushButton("Copy")
        self.decoded_data_copy.clicked.connect(self.copy_decoded_data)

        self.encoded_data = QLineEdit()
        self.encoded_data.textEdited.connect(self.encoded_data_changed)

        self.encoded_data_copy = QPushButton("Copy")
        self.encoded_data_copy.clicked.connect(self.copy_encoded_data)

        self.display = DisplayWidget(pixel_spacing=1, pixel_size=5, padding=2)

        preview = QGroupBox("Display Preview")
        preview_layout = QHBoxLayout(preview)
        preview_layout.add_widget(self.display)

        layout = QGridLayout(self)
        layout.set_horizontal_spacing(10)
        layout.set_vertical_spacing(18)

        layout.add_widget(QLabel("Decoded Data"), 0, 0)
        layout.add_widget(self.decoded_data, 0, 1)
        layout.add_widget(self.decoded_data_copy, 0, 2)

        layout.add_widget(QLabel("Encoded Data"), 1, 0)
        layout.add_widget(self.encoded_data, 1, 1)
        layout.add_widget(self.encoded_data_copy, 1, 2)

        layout.add_widget(preview, 2, 0, 1, 3)

        self.set_fixed_size(self.size_hint)

    def decoded_data_changed(self):
        encoded_data = encode_string(self.decoded_data.text)
        self.display.data = encoded_data
        self.encoded_data.text = encoded_data.hex(" ").upper()

    def copy_decoded_data(self):
        QApplication.clipboard().set_text(self.decoded_data.text)

    def encoded_data_changed(self):
        hex_string = self.encoded_data.text

        try:
            encoded_data = bytearray.fromhex(hex_string)
        except ValueError:
            return

        self.encoded_data.text = encoded_data.hex(" ").upper()
        self.display.data = encoded_data
        self.decoded_data.text = decode_string(encoded_data)

    def copy_encoded_data(self):
        QApplication.clipboard().set_text(self.encoded_data.text)