# np_utils.py
import machine
import neopixel


def make_np(pin, n, m):
    # NeoPixel об'єкт
    return neopixel.NeoPixel(machine.Pin(pin), n * m)


def make_exit_pin(pin):
    return machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)


def exit_pressed(exit_pin):
    # PULL_UP: натиснуто = 0
    return exit_pin.value() == 0


def xy_to_i(i, j, m):
    # серпантин: парні ряди (0,2,4..) справа->ліво
    return m * i + j if (i % 2) else (m - j - 1 + m * i)


def np_clear(np):
    np.fill((0, 0, 0))
    np.write()


def np_write_matrix(np, mat, n, m):
    # mat[n][m] = (r,g,b)
    for i in range(n):
        base = m * i
        if i % 2:
            # зліва направо
            for j in range(m):
                np[base + j] = mat[i][j]
        else:
            # справа наліво
            for j in range(m):
                np[base + (m - 1 - j)] = mat[i][j]
    np.write()


def koord_by_dot_rect(n, m, dot_rect):
    """
    0 → 2х2, центр 
    1 → 4×4,
    ...
    4 → 10×10 (координати i,j у межах 3..12),
    dot_rect = None -> вся матриця.
    """
    if dot_rect is None:
        return [(i, j) for i in range(n) for j in range(m)]

    max_idx = (min(n, m) - 1) // 2
    if dot_rect < 0:
        dot_rect = 0
    if dot_rect > max_idx:
        dot_rect = max_idx

    margin = max_idx - dot_rect
    i0, i1 = margin, n - margin
    j0, j1 = margin, m - margin
    return [(i, j) for i in range(i0, i1) for j in range(j0, j1)]

def koord_by_dot_rect_perimeter(n, m, dot_rect):

    max_idx = (min(n, m) - 1) // 2

    if dot_rect < 0:
        dot_rect = 0
    if dot_rect > max_idx:
        dot_rect = max_idx

    margin = max_idx - dot_rect

    i0 = margin
    i1 = n - margin - 1
    j0 = margin
    j1 = m - margin - 1

    coords = []

    # верх
    for j in range(j0, j1 + 1):
        coords.append((i0, j))

    # низ
    for j in range(j0, j1 + 1):
        coords.append((i1, j))

    # ліва
    for i in range(i0 + 1, i1):
        coords.append((i, j0))

    # права
    for i in range(i0 + 1, i1):
        coords.append((i, j1))

    return coords


