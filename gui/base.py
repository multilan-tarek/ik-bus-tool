from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGroupBox, QTableWidget, \
    QAbstractItemView, QTableWidgetItem, QFileDialog, QMessageBox
from serial import SerialException

from bus.frame import BusFrame
from gui.about import About
from gui.helper import get_logo, open_url
from gui.simulation.ike import IkeSimulation
from gui.tools.charset_browser import CharsetBrowser
from gui.tools.scanner import Scanner
from gui.serial_manager import SerialManager
from gui.tools.text_converter import TextConverter
from gui.transmit_area import TransmitArea


class GUI(QMainWindow):
    def __init__(self, application):
        from __feature__ import snake_case, true_property  # noqa
        super().__init__()

        self.config = application.config
        self.frame_log = []
        self.table = None

        self.serial_manager = SerialManager(self.config)
        self.serial_manager.frame_received.connect(self.frame_received)
        self.serial_manager.error_occurred.connect(self.serial_error_occurred)
        application.quit_event.connect(self.serial_manager.stop)

        self.ike_simulation = IkeSimulation(self)
        self.scanner = Scanner(self)
        self.text_converter = TextConverter(self)
        self.charset_browser = CharsetBrowser(self)
        self.about = About(self)






        self.window_title = "I/K-Bus Tool"
        self.window_icon = QIcon(get_logo())

        main_widget = QWidget()
        self.set_central_widget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        main_layout.add_spacing(8)
        main_layout.add_widget(TransmitArea(self.config, self.serial_manager))
        main_layout.add_spacing(8)
        main_layout.add_widget(self.init_filter_area())
        main_layout.add_spacing(8)
        main_layout.add_widget(self.init_receive_area())

        self.init_menu_bar()
        #self.init_status_bar()

        #self.minimum_size = main_layout.size_hint()
        self.set_fixed_width(1200)
        self.set_fixed_height(900)
        self.show()

    def frame_received(self, frame):
        self.frame_log.append(frame)

        table_row = self.table.row_count

        self.table.insert_row(table_row)
        self.table.set_row_height(table_row, 18)
        self.table.set_item(table_row, 0, QTableWidgetItem(frame.source_str))
        self.table.set_item(table_row, 1, QTableWidgetItem(frame.dest_str))
        self.table.set_item(table_row, 2, QTableWidgetItem(frame.cmd_str))
        self.table.set_item(table_row, 3, QTableWidgetItem(str(frame)))
        self.table.set_item(table_row, 4, QTableWidgetItem(frame.raw_hex))

        self.table.scroll_to_bottom()

    def init_receive_area(self):
        self.table = QTableWidget()

        self.table.style_sheet = "QTableView{border: 1px solid #d8d8d8;}"
        #self.table.horizontal_header().style_sheet = "border: none; border-bottom: 1px solid #d8d8d8;"
        self.table.horizontal_header().stretch_last_section = True
        self.table.vertical_header().hide()
        self.table.edit_triggers = QAbstractItemView.EditTrigger.NoEditTriggers

        self.table.column_count = 5
        self.table.set_horizontal_header_labels(["Source", "Destination", "Type", "Decoded", "Hex"])

        return self.table

    def init_filter_area(self):
        area = QGroupBox("Filter")


        return area

    def init_menu_bar(self):
        menu_bar = self.menu_bar()

        menu_file = menu_bar.add_menu("&File")
        menu_file_open_bin = menu_file.add_action("Open BIN")
        menu_file_open_bin.triggered.connect(self.open_bin)
        menu_file.add_separator()
        menu_file_save_bin = menu_file.add_action("Save as BIN")
        menu_file_save_bin.triggered.connect(self.save_as_bin)
        menu_file_save_text = menu_file.add_action("Save as Text")
        menu_file_save_text.triggered.connect(self.save_as_text)
        menu_file_save_hex = menu_file.add_action("Save as Hex")
        menu_file_save_hex.triggered.connect(self.save_as_hex)
        menu_file.add_separator()
        menu_file_clear = menu_file.add_action("Clear")
        menu_file_clear.triggered.connect(self.clear_table)
        menu_file.add_separator()
        menu_file_close = menu_file.add_action("Close")
        menu_file_close.triggered.connect(lambda: exit())

        self.serial_manager.init_menu(menu_bar)
        menu_sim = menu_bar.add_menu("&Simulation")


        menu_tools = menu_bar.add_menu("&Tools")
        menu_tools_text_conv = menu_tools.add_action("Text Converter")
        menu_tools_text_conv.triggered.connect(lambda: self.text_converter.show())
        menu_tools_charset_browser = menu_tools.add_action("Charset Browser")
        menu_tools_charset_browser.triggered.connect(lambda: self.charset_browser.show())
        menu_tools_scanner = menu_tools.add_action("Bus Scanner")
        menu_tools_scanner.triggered.connect(lambda: self.scanner.show())


        menu_help = menu_bar.add_menu("&Help")
        menu_help_more_docs = menu_help.add_action("More Documentation")
        menu_help_more_docs.triggered.connect(lambda: open_url("https://github.com/piersholt/wilhelm-docs"))
        menu_help.add_separator()
        menu_help_about = menu_help.add_action("About I/K-Bus Tool")
        menu_help_about.triggered.connect(lambda: self.about.show())

        menu_ike_sim = menu_sim.add_action("IKE/KMB")
        menu_ike_sim.triggered.connect(lambda: self.ike_simulation.show())

    def init_status_bar(self):
        status_bar = self.status_bar()

        #self.read_buffer_fill = QProgressBar()
        #self.read_buffer_fill.set_range(0, 100)
        #self.read_buffer_fill.value = 0
        #self.read_buffer_fill.text_visible = False
        #self.read_buffer_fill.fixed_height = 10
        #status_bar.add_permanent_widget(self.read_buffer_fill)
#
        #self.write_buffer_fill = QProgressBar()
        #self.write_buffer_fill.set_range(0, 100)
        #self.write_buffer_fill.value = 0
        #self.write_buffer_fill.text_visible = False
        #status_bar.add_permanent_widget(self.write_buffer_fill)

    def open_bin(self):
        file_path = QFileDialog.get_open_file_name(self, "Open BIN", filter="Binary Files (*.bin);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "rb") as file:
            data = file.read()

        self.table.clear_contents()
        self.table.row_count = 0

        try:
            while len(data):
                length = data[1]
                frame_length = length + 2

                if length < 2:
                    raise SyntaxError

                if frame_length > len(data):
                    break

                frame_data = data[:frame_length]

                checksum = frame_data[-1]
                checksum_bytes = frame_data[:-1]

                checksum_calced = 0
                for byte in checksum_bytes:
                    checksum_calced ^= byte

                if checksum != checksum_calced:
                    raise SyntaxError

                frame = BusFrame.from_data(frame_data)
                self.frame_received(frame)
                data = data[frame_length:]

        except SyntaxError:
            QMessageBox.critical(self, "Could not load file", "The selected file is corrupted")
            return

        QMessageBox.information(self, "File loaded", "File successfully loaded")


    def save_as_bin(self):
        file_path = QFileDialog.get_save_file_name(self, "Save as BIN", filter="Binary Files (*.bin);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "wb") as file:
            for frame in self.frame_log:
                file.write(frame.raw)

        QMessageBox.information(self, "File saved", "File successfully saved as BIN")

    def save_as_text(self):
        file_path = QFileDialog.get_save_file_name(self, "Save as Text", filter="Text Files (*.txt);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "w") as file:
            for frame in self.frame_log:
                line = f"[{frame.source_str} -> {frame.dest_str}] [{frame.cmd_str}]: {frame.raw_hex} ({str(frame)})\r\n"
                file.write(line)

        QMessageBox.information(self, "File saved", "File successfully saved as Text")

    def save_as_hex(self):
        file_path = QFileDialog.get_save_file_name(self, "Save as Hex", filter="Text Files (*.txt);;All Files (*)")[0]

        if not file_path:
            return

        with open(file_path, "w") as file:
            for frame in self.frame_log:
                file.write(f"{frame.raw_hex}\r\n")

        QMessageBox.information(self, "File saved", "File successfully saved as Hex")

    def clear_table(self):
        clear_question = QMessageBox(self)
        clear_question.window_title = "Clear data?"
        clear_question.text = "Do you want to clear the existing data?"
        clear_question.standard_buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        clear_question.icon = QMessageBox.Icon.Question
        result = clear_question.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.frame_log.clear()
            self.table.clear_contents()
            self.table.row_count = 0

    def serial_error_occurred(self, e):
        if isinstance(e, SerialException) and e.args[0] == 13:
            QMessageBox.critical(self, "Serial Error", "Could not open serial port. Permission denied.")
        else:
            QMessageBox.critical(self, "Serial Error", "An unknown error occurred.")
