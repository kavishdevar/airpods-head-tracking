import bluetooth
import logging

class ConnectionManager:
    INIT_CMD  = "00 00 04 00 01 00 02 00 00 00 00 00 00 00 00 00"
    START_CMD = "04 00 04 00 17 00 00 00 10 00 10 00 08 A1 02 42 0B 08 0E 10 02 1A 05 01 40 9C 00 00"
    STOP_CMD  = "04 00 04 00 17 00 00 00 10 00 11 00 08 7E 10 02 42 0B 08 4E 10 02 1A 05 01 00 00 00 00"

    def __init__(self, bt_addr="28:2D:7F:C2:05:5B", psm=0x1001, logger=None):
        self.bt_addr = bt_addr
        self.psm = psm
        self.logger = logger if logger else logging.getLogger(__name__)
        self.sock = None
        self.connected = False
        self.started = False

    def connect(self):
        self.logger.info(f"Connecting to {self.bt_addr} on PSM {self.psm:#04x}...")
        try:
            self.sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.sock.connect((self.bt_addr, self.psm))
            self.connected = True
            self.logger.info("Connected to AirPods.")
            self.sock.send(bytes.fromhex(self.INIT_CMD))
            self.logger.info("Initialization complete.")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.connected = False
        return self.connected

    def send_start(self):
        if not self.connected:
            self.logger.error("Not connected. Cannot send START command.")
            return False
        if not self.started:
            self.sock.send(bytes.fromhex(self.START_CMD))
            self.started = True
            self.logger.info("START command sent.")
        else:
            self.logger.info("START command has already been sent.")
        return True

    def send_stop(self):
        if self.connected and self.started:
            try:
                self.sock.send(bytes.fromhex(self.STOP_CMD))
                self.logger.info("STOP command sent.")
                self.started = False
            except Exception as e:
                self.logger.error(f"Error sending STOP command: {e}")
        else:
            self.logger.info("Cannot send STOP; not started or not connected.")

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
                self.logger.info("Disconnected from AirPods.")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
        self.connected = False
        self.started = False