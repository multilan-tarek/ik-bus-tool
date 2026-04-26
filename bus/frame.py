from copy import copy

from gui.helper import decode_string

BUS_DEVICES = {
    0x00: "GM",
    0x01: "MID1",
    0x02: "EKM",
    0x08: "SHD",
    0x09: "ZKE",
    0x12: "DME",
    0x18: "CDC",
    0x24: "HKM",
    0x28: "RCC",
    0x30: "CCM",
    0x32: "EGS",
    0x3b: "GT",
    0x3f: "DIA",
    0x40: "FBZV",
    0x43: "GTF",
    0x44: "EWS",
    0x46: "CID",
    0x47: "FMBT",
    0x50: "MFL",
    0x51: "MML",
    0x56: "ASC",
    0x57: "LWS",
    0x5b: "IHKA",
    0x60: "PDC",
    0x65: "EKP",
    0x66: "AHL",
    0x67: "ONL",
    0x68: "RAD",
    0x6a: "DSP",
    0x6b: "STH",
    0x70: "RDC",
    0x72: "SM",
    0x73: "SDRS",
    0x74: "SOR",
    0x76: "CDCD",
    0x7f: "NAV",
    0x80: "IKE",
    0x81: "RCSC",
    0x9a: "HAC",
    0x9b: "MMR",
    0x9c: "CVM",
    0xa0: "FID",
    0xa4: "AB",
    0xa6: "GR",
    0xa7: "FHK",
    0xa8: "NAC",
    0xac: "EDC",
    0xb0: "SES",
    0xbb: "NAJ",
    0xbf: "Broadcast",
    0xc0: "MID",
    0xc8: "TEL",
    0xca: "TCU",
    0xd0: "LCM",
    0xda: "SMAD",
    0xe0: "IRIS",
    0xe7: "ANZV",
    0xe8: "RLS",
    0xea: "DSPC",
    0xed: "VID",
    0xf0: "BMBT",
    0xf1: "PIC",
    0xf5: "SZM",
    0xff: "Broadcast",
    0xfe: "I/K-Bus Tool"
}

BUS_COMMANDS = {
    0x01: "Device Ping",
    0x02: "Device Announce",
    # 0x03: "Bus Status Request",
    # 0x04: "Bus Status",
    # 0x05: "Backlight Control",
    # 0x06: "Identification",
    # 0x07: "Gong status",
    # 0x0c: "Vehicle control",
    0x10: "Ignition Status Request",
    0x11: "Ignition Status",
    0x12: "Sensor Status Request",
    0x13: "Sensor Status",
    0x14: "Coding Status Request",
    0x15: "Coding Status",
    0x16: "Odometer Request",
    0x17: "Odometer",
    0x18: "Speed/RPM",
    0x19: "Temperature",
    0x1a: "Check Control Message",
    0x1b: "Check Control Priority",
    # 0x1c: "Gong",
    0x1d: "Temperature Request",
    0x1f: "GPS Time & Date",
    0x20: "MID Button",
    0x21: "Menu Text",
    0x22: "Display Confirmation",
    0x23: "Title Text",
    0x24: "Update Title Text",
    # 0x27: "MID display request",
    # 0x28: "MID denied access",
    # 0x29: "Report MID display",
    0x2a: "BC Status",
    0x2b: "Phone LEDs",
    0x2c: "Phone Status",
    0x2d: "Phone Dial",
    0x31: "MID Soft Button",
    0x32: "Volume Control",
    # 0x33: "Part number status",
    0x34: "DSP Control",
    # 0x35: "Car memory response",
    0x36: "Tone Control",
    0x37: "Select/Tone Menu",
    0x38: "CDC Control",
    0x39: "CDC Status",
    0x3a: "Recirculating Air Control",
    0x3b: "MFL Button",
    0x3c: "DSP Preset Control",
    0x40: "BC Input",
    0x41: "BC Control",
    0x42: "BC Remote Settings",
    # 0x43: "Mono display",
    # 0x44: "E46 IKE text",
    0x45: "Radio UI Control",
    0x46: "Radio UI Request",
    0x47: "BM Button",
    0x48: "BM Button",
    0x49: "BM Dial",
    0x4a: "BM Media Control",
    0x4b: "BM Media Status",
    0x4e: "Audio Source",
    0x4f: "Video Source",
    0x50: "Check Control Request",
    0x51: "Check Control Status",
    0x52: "Check Control Relay",
    0x53: "Vehicle Data Request",
    0x54: "Vehicle Data",
    0x55: "Service Interval Data",
    # 0x56: "Light control status request",
    0x57: "Cluster Button",
    # 0x58: "Headlight wipe interval",
    0x59: "Light Sensor Status",
    0x5a: "Cluster Indicators Request",
    0x5b: "Cluster Indicators",
    0x5c: "Backlight Status",
    0x5d: "Backlight Status Request",
    # 0x5e: "LAM sensor",
    # 0x5f: "Info swap",
    0x60: "Suspension Control Request",
    0x61: "Suspension Control",
    0x62: "RDC/DWS Status",
    # 0x6d: "Mirror control",
    # 0x70: "Remote control central locking status",
    # 0x71: "Rain Sensor Status",
    # 0x72: "Check control remote central locking",
    0x73: "Key Status Request",
    0x74: "Key Status",
    0x75: "Wiper Status Request",
    0x76: "Visual Indicators",
    0x77: "Wiper Status",
    # 0x78: "Seat Memory",
    0x79: "Door Status Request",
    0x7a: "Door Status",
    0x7c: "Sunroof Status",
    0x7d: "Sunroof Control",
    0x83: "AC Compressor Status",
    0x86: "Aux Heat/Vent Status",
    0x87: "Aux Heat/Vent Status Request",
    0x92: "Heater Status",
    0x93: "Heater Status Request",
    # 0x9f: "Headphone Status",
    0xa1: "Current Position Request",
    0xa2: "Current Position",
    0xa3: "Current Location Request",
    0xa4: "Current Location",
    0xa5: "Screen Text",
    0xa6: "Special Indicators",
    0xa7: "TMC Data Request",
    0xa8: "TMC Data",
    0xa9: "BMW Assist Data",
    0xaa: "Navigation Control",
    0xab: "Navigation Status",
    0xd4: "NG-Radio Station List"
}


class BusFrame:
    source = None
    source_str = None
    length = None
    dest = None
    dest_str = None
    cmd = None
    cmd_str = None
    data = None
    data_hex = None
    checksum = None
    raw = None
    raw_hex = None

    def __init__(self, source, dest, cmd, data=None):
        if data is None:
            data = []

        self.length = len(data) + 3
        checksum_bytes = bytearray([source, self.length, dest, cmd])
        checksum_bytes.extend(data)

        self.checksum = 0
        for byte in checksum_bytes:
            self.checksum ^= byte

        self.source = source
        self.source_str = BUS_DEVICES.get(source, "Unknown")

        self.dest = dest
        self.dest_str = BUS_DEVICES.get(dest, "Unknown")

        self.cmd = cmd
        self.cmd_str = BUS_COMMANDS.get(cmd, "Unknown")

        self.data = bytearray(data)
        self.data_hex = self.data.hex(" ").upper()

        self.raw = copy(checksum_bytes)
        self.raw.append(self.checksum)
        self.raw_hex = self.raw.hex(" ").upper()

    @staticmethod
    def from_data(frame_data):
        return BusFrame(
            frame_data[0],
            frame_data[2],
            frame_data[3],
            bytearray(frame_data[4:-1])
        )

    def __str__(self):
        return decode_string(self.data)