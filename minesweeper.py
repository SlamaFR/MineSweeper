import math
from random import randint
from time import time

from upemtk import *

CELL_SIZE = 30
BOARD_WIDTH = 30
BOARD_HEIGHT = 16
MINES = BOARD_HEIGHT * BOARD_WIDTH // 10
FRAMERATE = 50
BAR_HEIGHT = -1

DIGIT_COLORS = ["white", "blue", "green", "red", "purple", "brown", "teal", "black", "gray"]
RUNNING = True
START = True


def pixel_to_cell(x: int, y: int):
    return x // CELL_SIZE, y // CELL_SIZE


def cell_to_pixel(x: int, y: int):
    return (x + .5) * CELL_SIZE, (y + .5) * CELL_SIZE


def format_time(time_to_format: int):
    minutes = ("" if time_to_format // 60 >= 10 else "0") + str(time_to_format // 60)
    seconds = ("" if time_to_format % 60 >= 10 else "0") + str(time_to_format % 60)
    return minutes + ":" + seconds


def compute_text_size():
    global BAR_HEIGHT
    creer_fenetre(0, 0)
    BAR_HEIGHT = taille_texte('X')[1] + 19
    fermer_fenetre()


def build_grid():
    grid = list()
    for i in range(BOARD_HEIGHT):
        grid.append([0] * BOARD_WIDTH)
    return grid


def fill_grid(grid: list, amount: int, excluded: set):
    for _ in range(amount):
        x, y = randint(0, BOARD_WIDTH - 1), randint(0, BOARD_HEIGHT - 1)
        while grid[y][x] == -1 or (x, y) in excluded:
            x, y = randint(0, BOARD_WIDTH - 1), randint(0, BOARD_HEIGHT - 1)
        grid[y][x] = -1
    set_adjacent_count(grid)


def get_adjacent_cells(x: int, y: int):
    result = set()
    if x > 0:
        result.add((x - 1, y))
        if y > 0:
            result.add((x - 1, y - 1))
        if y < BOARD_HEIGHT - 1:
            result.add((x - 1, y + 1))
    if x < BOARD_WIDTH - 1:
        result.add((x + 1, y))
        if y > 0:
            result.add((x + 1, y - 1))
        if y < BOARD_HEIGHT - 1:
            result.add((x + 1, y + 1))
    if y > 0:
        result.add((x, y - 1))
    if y < BOARD_HEIGHT - 1:
        result.add((x, y + 1))
    return result


def count_adjacent_bombs(grid: list, adjacents: set):
    count = 0
    for (x, y) in adjacents:
        if grid[y][x] == -1:
            count += 1
    return count


def set_adjacent_count(grid: list):
    for y, row in enumerate(grid):
        for x, column in enumerate(row):
            if grid[y][x] != -1:
                grid[y][x] = count_adjacent_bombs(grid, get_adjacent_cells(x, y))


def draw_label(x: float, y: float, text: str, anchor: str = "center", outline: str = "black", bg: str = "white",
               fg: str = "black", size: int = 24, force_width: int = 0, force_height: int = 0, margin: int = 5):
    width = force_width or taille_texte(text, taille=size)[0]
    height = force_height or taille_texte(text, taille=size)[1]
    if anchor == "center":
        xa, ya, xb, yb = x - width / 2 - margin, y - height / 2 - margin, \
                         x + width / 2 + margin, y + height / 2 + margin
    elif anchor == "n":
        xa, ya, xb, yb = x - width / 2 - margin, y, \
                         x + width / 2 + margin, y + height + 2 * margin
    elif anchor == "s":
        xa, ya, xb, yb = x - width / 2 - margin, y - height - 2 * margin, \
                         x + width / 2 + margin, y
    elif anchor == "e":
        xa, ya, xb, yb = x - width - 2 * margin, y - height / 2 - margin, \
                         x, y + height / 2 + margin
    elif anchor == "w":
        xa, ya, xb, yb = x, y - height / 2 - margin, \
                         x + width + 2 * margin, y + height / 2 + margin
    elif anchor == "nw":
        xa, ya, xb, yb = x, y, \
                         x + width + 2 * margin, y + height + 2 * margin
    elif anchor == "ne":
        xa, ya, xb, yb = x - width - 2 * margin, y, \
                         x, y + height + 2 * margin
    elif anchor == "sw":
        xa, ya, xb, yb = x, y - height - 2 * margin, \
                         x + width + 2 * margin, y
    elif anchor == "se":
        xa, ya, xb, yb = x - width - 2 * margin, y - height - 2 * margin, \
                         x, y
    else:
        return
    rectangle(xa, ya, xb, yb, outline, bg)
    texte((xa + xb) / 2, (ya + yb) / 2, text, fg, ancrage="center",
          taille=size)
    return xa, ya, xb, yb


def draw_flag(x: int, y: int):
    thickness = CELL_SIZE / 20
    xt, yt = cell_to_pixel(x, y)
    ligne(xt, yt - CELL_SIZE / 3, xt, yt + CELL_SIZE / 3, epaisseur=thickness)
    ligne(xt - CELL_SIZE / 4, yt + CELL_SIZE / 3, xt + CELL_SIZE / 4, yt + CELL_SIZE / 3,
          epaisseur=thickness)
    polygone([(xt, yt - CELL_SIZE / 3), (xt - CELL_SIZE / 3, yt - CELL_SIZE / 6), (xt, yt)],
             remplissage='red', epaisseur=thickness)


def draw_cross(x: int, y: int, tag: str = None):
    xt, yt = cell_to_pixel(x, y)
    ligne(xt - CELL_SIZE / 3, yt - CELL_SIZE / 3, xt + CELL_SIZE / 3, yt + CELL_SIZE / 3, 'red', epaisseur=3, tag=tag)
    ligne(xt - CELL_SIZE / 3, yt + CELL_SIZE / 3, xt + CELL_SIZE / 3, yt - CELL_SIZE / 3, 'red', epaisseur=3, tag=tag)


def draw_mine(x: int, y: int):
    xt, yt = cell_to_pixel(x, y)
    for i in range(8):
        theta = i * (2 * math.pi) / 8
        ligne(xt, yt, xt + math.cos(theta) * (2 * CELL_SIZE / 5), yt + math.sin(theta) * (2 * CELL_SIZE / 5),
              couleur='#2c3e50', epaisseur=CELL_SIZE / 10)
    cercle(xt, yt, CELL_SIZE / 4, '#2c3e50', '#34495e', epaisseur=CELL_SIZE / 15)


def draw_board(grid: list, discovered: set, marked: set, unknown: set, playing: bool, losing_cell: tuple):
    for y, row in enumerate(grid):
        for x, column in enumerate(row):
            if (x, y) in discovered and column >= 0:
                xt, yt = cell_to_pixel(x, y)
                rectangle(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                          remplissage='white')
                if column > 0:
                    texte(xt, yt, column, ancrage='center', couleur=DIGIT_COLORS[column], taille=CELL_SIZE - 5)
            else:
                rectangle(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                          remplissage='red3' if losing_cell and (x, y) == losing_cell else 'lightgray')

            if playing:
                if (x, y) in marked:
                    draw_flag(x, y)

                if (x, y) in unknown:
                    xt, yt = cell_to_pixel(x, y)
                    texte(xt, yt, '?', ancrage='center', taille=CELL_SIZE - 5)
            else:
                if (x, y) in marked:
                    if column >= 0:
                        rectangle(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                                  remplissage='lightgray')
                        draw_mine(x, y)
                        draw_cross(x, y)
                    else:
                        draw_flag(x, y)
                elif column == -1:
                    draw_mine(x, y) if losing_cell else draw_flag(x, y)


def draw_bottom_bar(playing: bool, win: bool):
    rectangle(0, BOARD_HEIGHT * CELL_SIZE, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT,
              remplissage='black')
    if not playing:
        offset = 0
        xa, ya, xb, yb = draw_label(BOARD_WIDTH * CELL_SIZE - 5, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT - 5, 'Quitter',
                                    'se')
        offset += xb - xa + 5
        buttons[(xa, ya, xb, yb)] = lambda: set_running(False)
        xa, ya, xb, yb = draw_label(BOARD_WIDTH * CELL_SIZE - 5 - offset, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT - 5,
                                    'Rejouer', 'se')
        buttons[(xa, ya, xb, yb)] = lambda: set_start(True)
        offset += xb - xa + 5
        if not win:
            texte(BOARD_WIDTH * CELL_SIZE - 10 - offset, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT / 2, "Perdu !",
                  ancrage='e', couleur='red', taille=24)
        else:
            texte(BOARD_WIDTH * CELL_SIZE - 10 - offset, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT / 2, "Gagné !",
                  ancrage='e', couleur='green', taille=24)
    else:
        xa, ya, xb, yb = draw_label(BOARD_WIDTH * CELL_SIZE - 5, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT - 5, 'Quitter',
                                    'se')
        buttons[(xa, ya, xb, yb)] = lambda: set_running(False)


def draw_time(ticks: float):
    effacer('time')
    current_time = format_time(int(ticks))
    texte(10, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT / 2, current_time, ancrage='w', couleur='white',
          taille=24, tag='time')


def left_click(ev: tuple):
    x, y = abscisse(ev), ordonnee(ev)
    for (xa, ya, xb, yb), f in buttons.items():
        if xa <= x <= xb and ya <= y <= yb:
            f()


def mark(discovered: set, marked: set, unknown: set, ev: tuple):
    x, y = pixel_to_cell(abscisse(ev), ordonnee(ev))
    if not (0 <= x <= BOARD_WIDTH and 0 <= y <= BOARD_HEIGHT) or (x, y) in discovered:
        return
    if (x, y) not in marked and (x, y) not in unknown:
        marked.add((x, y))
    elif (x, y) in marked:
        marked.discard((x, y))
        unknown.add((x, y))
    elif (x, y) in unknown:
        unknown.discard((x, y))


def discover(grid: list, discovered: set, marked: set, unknown: set, x: int, y: int):
    if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT) or (x, y) in marked or (x, y) in unknown:
        return 0
    if grid[y][x] == -1:
        return -1
    if (x, y) not in discovered:
        discovered.update(explore(grid, x, y))
    if BOARD_WIDTH * BOARD_HEIGHT - MINES == len(discovered):
        return 1
    return 0


def explore(grid: list, x: int, y: int, area: set = None):
    if not area:
        area = set()

    if (x, y) in area:
        return

    area.add((x, y))

    if grid[y][x] > 0:
        return area

    if x > 0:
        explore(grid, x - 1, y, area)
        if y > 0:
            explore(grid, x - 1, y - 1, area)
        if y < BOARD_HEIGHT - 1:
            explore(grid, x - 1, y + 1, area)
    if x < BOARD_WIDTH - 1:
        explore(grid, x + 1, y, area)
        if y > 0:
            explore(grid, x + 1, y - 1, area)
        if y < BOARD_HEIGHT - 1:
            explore(grid, x + 1, y + 1, area)
    if y > 0:
        explore(grid, x, y - 1, area)
    if y < BOARD_HEIGHT - 1:
        explore(grid, x, y + 1, area)
    return area


def set_start(start: bool):
    global START
    START = start


def set_running(running: bool):
    global RUNNING
    RUNNING = running


def loop():
    creer_fenetre(BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE + BAR_HEIGHT, nom='Démineur',
                  evenements=['ClicGauche', 'ClicDroit', 'DoubleClicGauche'])

    grid = list()
    discovered = set()
    marked = set()
    unknown = set()
    playing = True
    win = False
    filled = False
    ticks = 0
    last_time = time()
    last_round_time = -1
    losing_cell = tuple()
    forbidden_move = tuple()

    while RUNNING:
        if START:
            set_start(False)
            grid.clear()
            discovered.clear()
            marked.clear()
            unknown.clear()
            playing = True
            win = False
            filled = False
            ticks = 0
            last_time = time()
            last_round_time = -1
            losing_cell = tuple()
            forbidden_move = tuple()

            grid = build_grid()

            draw_board(grid, discovered, marked, unknown, playing, losing_cell)
            draw_bottom_bar(playing, win)

        ev = donner_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            break
        elif ty == 'ClicGauche':
            left_click(ev)

        if playing:
            if ty == 'ClicDroit' and ticks > 0:
                mark(discovered, marked, unknown, ev)
            elif ty == 'ClicGauche' and ticks > 0:
                x, y = pixel_to_cell(abscisse(ev), ordonnee(ev))

                if not filled:
                    filled = True
                    excluded = get_adjacent_cells(x, y)
                    excluded.add((x, y))
                    fill_grid(grid, MINES, excluded)

                state = discover(grid, discovered, marked, unknown, x, y)
                if state != 0:
                    playing = False
                    if state == -1:
                        losing_cell = (x, y)
                    win = state == 1

            elif ty == 'DoubleClicGauche':
                x, y = pixel_to_cell(abscisse(ev), ordonnee(ev))

                if (x, y) in marked or (x, y) in unknown:
                    continue

                adjacent = get_adjacent_cells(x, y)
                if grid[y][x] == len(adjacent.intersection(marked)):
                    for (x, y) in adjacent.difference(marked):
                        state = discover(grid, discovered, marked, unknown, x, y)
                        if state != 0:
                            playing = False
                            if state == -1:
                                losing_cell = (x, y)
                            win = state == 1
                else:
                    forbidden_move = (ticks, (x, y))

            delta = (time() - last_time)
            ticks += delta
            last_time = time()

            if ty:
                buttons.clear()
                effacer_tout()
                draw_board(grid, discovered, marked, unknown, playing, losing_cell)
                draw_bottom_bar(playing, win)
                draw_time(ticks)
            elif int(ticks) % 60 != last_round_time:
                last_round_time = int(ticks) % 60
                draw_time(ticks)

            if forbidden_move:
                if ticks - forbidden_move[0] < .75:
                    x, y = forbidden_move[1]
                    draw_cross(x, y, tag='forbidden')
                else:
                    effacer('forbidden')
                    forbidden_move = tuple()

        attendre(1 / FRAMERATE)

    fermer_fenetre()


if __name__ == "__main__":
    buttons = dict()
    compute_text_size()
    loop()
