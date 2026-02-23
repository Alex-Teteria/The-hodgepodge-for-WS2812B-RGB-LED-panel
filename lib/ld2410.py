# HLK-LD2410 (Microwave-based human/object presence sensor)
# Author: Alex Teteria
# v1.0
# 23.02.2026
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

from machine import Pin
import utime

REPORT_HEADER = b"\xf4\xf3\xf2\xf1"
REPORT_TERMINATOR = b"\xf8\xf7\xf6\xf5"

STATE_NO_TARGET = 0
STATE_MOVING_TARGET = 1
STATE_STATIONARY_TARGET = 2
STATE_COMBINED_TARGET = 3
TARGET_NAME = ["no_target", "moving_target", "stationary_target", "combined_target"]

# Константи командного протоколу (якщо ще не додавали)
CMD_HEADER = b"\xfd\xfc\xfb\xfa"
CMD_TERMINATOR = b"\x04\x03\x02\x01"

class LD2410:
    def __init__(self, uart, *, led_pin=None, flush_on_read=False):
        """
        uart: вже налаштований machine.UART(...)
        led_pin: опційно Pin номер для індикації
        flush_on_read: чи чистити буфер перед читанням кадру (інколи корисно, інколи шкодить)
        """
        self.uart = uart
        self.flush_on_read = flush_on_read
        self.led = Pin(led_pin, Pin.OUT) if led_pin is not None else None

        self.meas = {
            "state": STATE_NO_TARGET,
            "moving_distance": 0,
            "moving_energy": 0,
            "stationary_distance": 0,
            "stationary_energy": 0,
            "detection_distance": 0,
        }

    @staticmethod
    def _print_bytes(data):
        if not data:
            print("<no data>")
            return
        print("hex:", " ".join("{:02x}".format(b) for b in data))

    def _serial_flush(self):
        while self.uart.any():
            self.uart.read()

    def _read_exact(self, n, timeout_ms=100):
        start = utime.ticks_ms()
        buf = bytearray()
        while len(buf) < n:
            if utime.ticks_diff(utime.ticks_ms(), start) > timeout_ms:
                return None
            chunk = self.uart.read(n - len(buf))
            if chunk:
                buf.extend(chunk)
            else:
                utime.sleep_ms(1)
        return bytes(buf)

    def _find_header(self):
        window = bytearray()
        while True:
            b = self.uart.read(1)
            if not b:
                return False
            window += b
            if len(window) > 4:
                window = window[-4:]
            if bytes(window) == REPORT_HEADER:
                return True

    def _parse_report_basic(self, frame):
        # frame очікується повний, з заголовком і термінатором
        if len(frame) < 23:
            return None
        if frame[0:4] != REPORT_HEADER:
            return None
        if frame[-4:] != REPORT_TERMINATOR:
            return None
        if frame[7] != 0xAA:
            return None

        self.meas["state"] = frame[8]
        self.meas["moving_distance"] = frame[9] + (frame[10] << 8)
        self.meas["moving_energy"] = frame[11]
        self.meas["stationary_distance"] = frame[12] + (frame[13] << 8)
        self.meas["stationary_energy"] = frame[14]
        self.meas["detection_distance"] = frame[15] + (frame[16] << 8)
        return self.meas

    def read_report(self, *, print_hex=False):
        """
        Читає один report кадр (basic/eng за довжиною).
        Повертає словник meas або None.
        """
        if self.flush_on_read:
            self._serial_flush()

        if not self._find_header():
            return None

        # length (2 bytes, little-endian)
        ln = self._read_exact(2, timeout_ms=50)
        if not ln:
            return None
        payload_len = ln[0] + (ln[1] << 8)

        rest = self._read_exact(payload_len + 4, timeout_ms=150)  # + terminator
        if not rest:
            return None

        frame = REPORT_HEADER + ln + rest

        if print_hex:
            self._print_bytes(frame)

        # Basic кадр зазвичай має payload_len == 0x0d (13)
        # Engineering може бути 0x23 (35) і довший кадр треба парсити окремо
        if payload_len == 0x0d:
            m = self._parse_report_basic(frame)
        else:
            # поки що просто повернемо None або можна зберегти raw frame
            m = None

        if self.led is not None:
            if m and (m["state"] in (STATE_MOVING_TARGET, STATE_COMBINED_TARGET)):
                self.led.value(1)
            else:
                self.led.value(0)

        return m
    
    def probe(self, sleep_ms=60):
        # flush (найпростіший)
        while self.uart.any():
            self.uart.read()

        # команда "read firmware": A0 00
        frame = CMD_HEADER + b"\x02\x00" + b"\xA0\x00" + CMD_TERMINATOR
        self.uart.write(frame)

        utime.sleep_ms(sleep_ms)
        data = self.uart.read()

        if not data:
            return False

        # дуже проста перевірка "щось схоже на відповідь"
        i = data.find(CMD_HEADER)
        if i < 0:
            return False
        j = data.find(CMD_TERMINATOR, i + 4)
        return j >= 0
    
    
if __name__ == '__main__':
    from machine import UART, Pin
    import time

    # ТУТ налаштовуємо інтерфейс:
    uart = UART(1, baudrate=256000, tx=Pin(8), rx=Pin(9), timeout=20)

    sensor = LD2410(uart, led_pin=25, flush_on_read=False)
    
    if not sensor.probe():
        raise RuntimeError("LD2410 не відповідає (не підключено/не той UART/піні/baud)")
    print("LD2410 підключено")
    
    while True:
        m = sensor.read_report(print_hex=False)
        if m:
            print(m)   # або ваша логіка
        time.sleep_ms(50)
    
