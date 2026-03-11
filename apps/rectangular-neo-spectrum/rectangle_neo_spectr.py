import neopixel, time, random
import machine
from np_utils import *

import array
import math
import adc_dma, fastfft
import _thread


n = 16
m = 16

np = neopixel.NeoPixel(machine.Pin(20), n * m)

green = 0, 24, 0
green_ellow = 6, 10, 0
red = 16, 0, 0
orange = 12, 4, 0
blue = 0, 0, 16
blue_light = 0, 8, 8
magenta = 8, 0, 8
yellow = 12, 8, 0
teal = 0, 5, 3
white = 12, 20, 8
nothing = 0, 0, 0

rect_colors = (red, orange, yellow, green_ellow, green, blue_light, blue, magenta)

# ======================================
# Конфігурація ADC
# ======================================
SAMPLE_FREQ = 40_000  # Hz
ADC0 = 0              # (GPIO26)

# ===============================================================
# Конфігурація FFT, DSP
# ===============================================================

# для модуля MAX9814 (Gain=40dB), ≈ 39 Гц … 2.0 кГц
IND_BANDS = (2, 1, 1, 1, 2, 7, 13, 23)

NUM_BAND = 8 # кількість смуг
FFT_SIZE = 1024
# Опорна потужність повномасштабного синуса, берем за 0 dB (Standard AES17 Reference)
FS_RMS2 = 32767**2 / 2

# ===============================================================
# Динамічний масштаб та шумовий поріг(в "dB над шумовим порогом")
# ===============================================================
NOISE_THRESHOLD = (67, 72, 77, 80, 75, 72, 72, 71)

_scale_db = 20.0       # стартове значення 
SCALE_MIN_DB = 6.0     # не даємо масштабу впасти нижче
SCALE_DECAY_DB = 0.05  # release: на скільки dB/кадр зменшувати масштаб, якщо сигнал слабшає
HEADROOM_DB = 0.4      # “запас” зверху, щоб 8 не забивалось постійно
GAMMA = 1.8            # <1 піднімає тихі смуги, >1 “стискає” низ
# dB підсилення для кожної смуги (довжина = NUM_BAND)
BAND_GAIN_DB = (
    10, 5, 0, 0,
    0, 4, 10, 15
    )
# коефіцієнт для визначення домінантних частотних смуг
DOMINANCE_FACTOR = 1.2

# ======================================
# Cинхронізація
# ======================================
lock = _thread.allocate_lock()

# 1-слотовий обмін спектром (memoryview від fastfft)
spectr_front = None        # посилання на memoryview
spectr_busy  = False       # True: Core1 ще НЕ завершив роботу зі spectr_front


def band_dbfs(spec, i, j):
    # вертає значення dBFS для смуги частот (для діапазону бінів [i, j[ )
    # e = сума енергій бінів у смузі (очікується, що spec[k] >= 0)
    e = 0
    for k in range(i, j):
        e += spec[k]
    
    if e <= 0:
        return -120
   
    return 10.0 * math.log10((2.0 * e) / FS_RMS2)

def build_band_spectr(spec):
    ind = 1
    band_spectr = [0.0] * NUM_BAND

    for i, w in enumerate(IND_BANDS):
        adj = band_dbfs(spec, ind, ind + w)

        band_spectr[i] = adj + BAND_GAIN_DB[i] + NOISE_THRESHOLD[i]
        ind += w
    return band_spectr


def draw_rect(level, freq_level):
    np.fill((0, 0, 0))
    if level == 0:
        np.write()
        return

    # Отримуємо потужності
    powers = list(freq_level.values())
    mean_power = sum(powers) / len(powers)

    # Вибираємо домінантні смуги
    dominant_colors = [c for c, p in freq_level.items() if p >= DOMINANCE_FACTOR * mean_power]

    if dominant_colors:
        # Сортуємо домінанти за потужністю
        dominant_colors_sorted = sorted(dominant_colors, key=freq_level.get)
        n_dom = len(dominant_colors_sorted)

        for num in range(level):
            if n_dom >= level:
                color = dominant_colors_sorted[-level + num]
            else:
                # Якщо рівнів більше, ніж домінант, повторюємо останній домінант
                color = dominant_colors_sorted[num] if num < n_dom else dominant_colors_sorted[-1]

            for pix in rect_map[num]:
                np[pix] = color

    else:
        # стандартна логіка: сортування по потужності
        rect_colors_sorted = sorted(freq_level, key=freq_level.get)
        for num in range(level):
            for pix in rect_map[num]:
                np[pix] = rect_colors_sorted[num + 7 - level]

    np.write()
    
    
# rect_maps
rect_map = [
    tuple(xy_to_i(i, j, m) for i, j in koord_by_dot_rect_perimeter(n, m, num))
    for num in range(m // 2)
    ]

def build_peak_level(adj):
    global _scale_db

    if adj < 0.0:
        adj = 0.0

    target = adj + HEADROOM_DB

    if target > _scale_db:
        _scale_db = target
    else:
        _scale_db -= SCALE_DECAY_DB
        if _scale_db < target:
            _scale_db = target
        if _scale_db < SCALE_MIN_DB:
            _scale_db = SCALE_MIN_DB

    denom = _scale_db if _scale_db > 1e-6 else 1e-6

    x = adj / denom
    if x > 1.0:
        x = 1.0

    y = x ** GAMMA

    lvl = int(y * 8.0 + 0.5)
    if lvl > 8:
        lvl = 8

    return lvl

def core1_dsp_led_worker():
    global spectr_busy

    while True:
        # --- забрати спектр (memoryview) ---
        lock.acquire()
        if spectr_busy:
            spectr = spectr_front  # локальне посилання на memoryview
            lock.release()

            # --- DSP: смуги + AGC ---
            band_spectr = build_band_spectr(spectr)
            level = build_peak_level(sum(band_spectr))

            # --- render + np.write() ---
            color_level = {c: band for c, band in zip(rect_colors, band_spectr)}
            draw_rect(level, color_level)

            # --- дозволяємо Core0 робити наступний rfft ---
            lock.acquire()
            spectr_busy = False
            lock.release()

        else:
            lock.release()
            time.sleep_us(50)

# ---------------- Core0 main loop ----------------
def core0_main_loop():
    global spectr_front, spectr_busy

    while True:
        t0 = time.ticks_us()
        
        # 1) Захват ADC
        adc_dma.start(ADC0, SAMPLE_FREQ, FFT_SIZE)
        while adc_dma.busy():
            time.sleep_us(5)

        # отримуємо буфер (тут важливо НЕ робити close() до завершення FFT)
        buf, lvl = adc_dma.buffer_i16('auto', 10_000)

        # 2) Перед викликом rfft() чекаємо, поки Core1 завершив читання попереднього спектра
        while True:
            lock.acquire()
            busy = spectr_busy
            lock.release()
            if not busy: # Core1 вже завершив обробку
                break
            time.sleep_us(50)

        # 3) FFT (повертає memoryview на внутрішній буфер fastfft)
        spectr = fastfft.rfft(buf, True)

        # 4) Тепер можна закрити adc_dma (бо FFT вже прочитав buf)
        adc_dma.close()

        # 5) Публікація спектра для Core1
        lock.acquire()
        spectr_front = spectr
        spectr_busy = True
        lock.release()
        
        t1 = time.ticks_us()
        print(time.ticks_diff(t1, t0))


if __name__ == '__main__':
      
    _thread.start_new_thread(core1_dsp_led_worker, ())
    core0_main_loop()




