from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QGridLayout, QLineEdit, QGroupBox, QPushButton, QApplication
from gui.helper import get_logo, encode_string, decode_string
from gui.widgets.display import DisplayWidget


class About(QDialog):
    def __init__(self, main_window):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__(main_window)

        self.window_title = "About I/K-Bus Tool"
        self.window_icon = QIcon(get_logo())

        layout = QGridLayout(self)
        layout.set_horizontal_spacing(30)
        layout.set_vertical_spacing(8)

        git_link = QLabel("<a href='https://git.multilan.de/tarek/ik-bus-tool'>Git Page</a>")
        git_link.open_external_links = True

        docs_link = QLabel("<a href='https://github.com/piersholt/wilhelm-docs'>More Documentation</a>")
        docs_link.open_external_links = True

        disclaimer = QLabel("This software is an independent third-party project and is not affiliated with, endorsed by, or connected to BMW AG.\nBMW is a trademark of BMW AG.")
        disclaimer.style_sheet = "color: gray;"

        logo = QLabel()
        logo.pixmap = get_logo().scaled_to_height(60)

        layout.add_widget(logo, 0, 0, 5, 1)
        layout.add_widget(QLabel("BMW I/K-Bus Protocol Toolkit"), 0, 1)
        layout.add_widget(QLabel("© Copyright 2026 multilan.de"), 1, 1)
        layout.add_widget(QLabel(), 2, 1)
        layout.add_widget(git_link, 3, 1)
        layout.add_widget(docs_link, 4, 1)
        layout.add_widget(QLabel(), 5, 1)
        #layout.add_widget(disclaimer, 4, 0, 1, 2)

        self.set_fixed_size(self.size_hint)