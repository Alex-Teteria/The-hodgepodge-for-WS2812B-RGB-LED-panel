# Micropython driver for the DS3231 RTC Module (simple version)
# The MIT License (MIT)
# Copyright (c) 2026 Oleksandr Teteria

from machine import Pin, I2C


class DS3231:
    """ DS3231 RTC simple driver."""

    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr

    @staticmethod
    def bcd2dec(b):
        return (b >> 4) * 10 + (b & 0x0F)

    @staticmethod
    def dec2bcd(d):
        return ((d // 10) << 4) | (d % 10)

    def datetime(self):
        data = self.i2c.readfrom_mem(self.addr, 0x00, 7)

        ss = self.bcd2dec(data[0] & 0x7F)
        mm = self.bcd2dec(data[1])
        hh = self.bcd2dec(data[2] & 0x3F)
        wd = self.bcd2dec(data[3])
        dd = self.bcd2dec(data[4])
        mo = self.bcd2dec(data[5] & 0x1F)
        yy = self.bcd2dec(data[6]) + 2000

        return (yy, mo, dd, wd, hh, mm, ss, 0)

    def set_datetime(self, dt):
        yy, mo, dd, wd, hh, mm, ss, _ = dt

        buf = bytearray(7)
        buf[0] = self.dec2bcd(ss)
        buf[1] = self.dec2bcd(mm)
        buf[2] = self.dec2bcd(hh)
        buf[3] = self.dec2bcd(wd)
        buf[4] = self.dec2bcd(dd)
        buf[5] = self.dec2bcd(mo)
        buf[6] = self.dec2bcd(yy - 2000)

        self.i2c.writeto_mem(self.addr, 0x00, buf)



if __name__ == '__main__':
    # Example of use
    
    from machine import Pin, I2C
    from ds3231_simple import DS3231

    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)

    rtc = DS3231(i2c)

    print(rtc.datetime())


