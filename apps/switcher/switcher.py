# switcher.py
# Author: Oleksandr Teteria
# v1.0
# 25.02.2026
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import uos
import time
import machine

APPS_DIR = "apps"
IDX_FILE = "app_idx.txt"

BTN_PIN = 15          # GPIO 
DEBOUNCE_MS = 40

_btn = machine.Pin(BTN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

_pending = False
_last_irq_ms = 0

def _irq(_pin):
    global _pending, _last_irq_ms
    _pending = True
    _last_irq_ms = time.ticks_ms()

# IRQ лише ставить прапорець (без I/O і без reset)
_btn.irq(trigger=machine.Pin.IRQ_FALLING, handler=_irq)

def _list_apps():
    try:
        names = [n for n in uos.listdir(APPS_DIR) if n.endswith(".py")]
        names.sort()
        return tuple(f"{APPS_DIR}/{n}" for n in names)
    except OSError:
        return ()

APPS = _list_apps()

def _read_idx():
    try:
        with open(IDX_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def _write_idx(i):
    # атомарніше: temp -> rename
    tmp = IDX_FILE + ".tmp"
    with open(tmp, "w") as f:
        f.write(str(i))
    try:
        uos.remove(IDX_FILE)
    except:
        pass
    uos.rename(tmp, IDX_FILE)

def current_app_path():
    if not APPS:
        raise RuntimeError("No apps found in /apps")
    idx = _read_idx() % len(APPS)
    return APPS[idx]

def _advance_index():
    if not APPS:
        return
    i = _read_idx()
    i = (i + 1) % len(APPS)
    _write_idx(i)
    
def service():
    """
    Якщо була натиснута кнопка — збільшить індекс і зробить reset.
    """
    global _pending
    if not _pending:
        return

    # debounce: чекаємо, щоб минуло трохи часу після IRQ
    if time.ticks_diff(time.ticks_ms(), _last_irq_ms) < DEBOUNCE_MS:
        return

    # підтверджуємо, що кнопка реально натиснута
    if _btn.value() == 0:
        _advance_index()
        machine.reset()

    _pending = False

def sleep_ms(ms, step=10):
    """
    Заміна time.sleep_ms(), щоб кнопка відпрацьовувала під час затримок.
    """
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < ms:
        service()
        time.sleep_ms(step)
