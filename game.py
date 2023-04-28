from sqlite3 import connect
from random import sample
from PIL import Image, ImageDraw, ImageFont
from consts import *


class Game:
    def __init__(self, game_id):
        self.w, self.h = W, H
        self.figures = [
            ((1, 1, 1),
             (1, 1, 1),
             (1, 1, 1)),

            ((1, 1, 1),
             (1, 0, 0),
             (1, 0, 0)),

            ((1, 1, 1),
             (0, 0, 1),
             (0, 0, 1)),

            ((0, 0, 1),
             (0, 0, 1),
             (1, 1, 1)),

            ((1, 0, 0),
             (1, 0, 0),
             (1, 1, 1)),

            ((1, 1),
             (1, 1)),

            ((1, 1),
             (1, 0)),

            ((1, 1),
             (0, 1)),

            ((0, 1),
             (1, 1)),

            ((1, 0),
             (1, 1)),

            ((1, ), ),

            ((1, ), (1, )),

            ((1, ), (1, ), (1, )),

            ((1, ), (1, ), (1, ), (1, )),

            ((1, ), (1, ), (1, ), (1, ), (1, )),

            ((1, ),
             (1, )),

            ((1, ),
             (1, ),
             (1, )),

            ((1, ),
             (1, ),
             (1, ),
             (1, )),

            ((1, ),
             (1, ),
             (1, ),
             (1, ),
             (1, )),
        ]
        self.field = [[0] * self.w for _ in range(self.h)]
        self.i_figure = None
        self.combo = 0
        self.just_moves = 3
        self.id = game_id
        self.new_game()
        self.connection = connect('data/block_puzzle.db')
        cursor = self.connection.cursor()
        is_in_table = cursor.execute(f'SELECT * FROM games WHERE id = {self.id}').fetchone()
        if is_in_table:
            game_id, score, figure1, figure2, figure3, field = is_in_table
            self.score = score
            self.figures_to_place = [-1 if figure == -1 else self.figures[figure]
                                     for figure in (figure1, figure2, figure3)]
            for i_row, i in enumerate(range(0, self.h * self.w, self.w)):
                row = [int(j) for j in field[i:i + self.w]]
                self.field[i_row] = row
            if not self.get_state():
                self.new_game()
        else:
            cursor.execute(f'''
            INSERT INTO games VALUES ({self.id}, {self.score}, 
                                      {self.figures.index(self.figures_to_place[0])},
                                      {self.figures.index(self.figures_to_place[1])},
                                      {self.figures.index(self.figures_to_place[2])},
                                      "{'0' * self.w * self.h}")
            ''')
        is_in_table = cursor.execute(f'SELECT * FROM settings WHERE id = {self.id}').fetchone()
        if is_in_table:
            settings = is_in_table[1:]
            self.all_buttons_on_screen, *_ = settings
        else:
            cursor.execute(f'''
            INSERT INTO settings VALUES ({self.id}, 0)
            ''')
            self.all_buttons_on_screen = True
        self.connection.commit()

    def change_settings(self, settings):
        cursor = self.connection.cursor()
        self.all_buttons_on_screen, *_ = settings

        cursor.execute(f'''
        UPDATE settings
            SET all_buttons_on_screen = {self.all_buttons_on_screen}
        WHERE id = {self.id}
        ''')

        self.connection.commit()

    def new_game(self):
        self.field = [[0] * self.w for _ in range(self.h)]
        self.figures_to_place = []
        self.i_figure = None
        self.score = 0
        self.combo = 0
        self.just_moves = 3
        self.get_new_figures()

    def get_figure(self, figure):
        try:
            return self.figures.index(figure)
        except ValueError:
            return -1

    def save_game(self):
        cursor = self.connection.cursor()
        cursor.execute(f'''
        UPDATE games SET
            score = {self.score},
            figure1 = {self.get_figure(self.figures_to_place[0])},
            figure2 = {self.get_figure(self.figures_to_place[1])},
            figure3 = {self.get_figure(self.figures_to_place[2])},
            field = "{self.get_field()}"
        WHERE id = {self.id}
        ''')
        self.connection.commit()

    def next_move(self, x, y):
        x, y = x - 1, y - 1
        i_figure = self.i_figure - 1
        moves = self.get_moves().get(i_figure)
        if moves is None or (x, y) not in moves:
            return False
        reward = sum(sum(row) for row in self.figures_to_place[i_figure])
        score_gained = self.make_move(i_figure, x, y)
        if score_gained:
            if self.just_moves > 3:
                self.combo = 0
            else:
                self.combo += 1
            reward += (self.combo + 1) * 10
            self.just_moves = 0
        else:
            self.just_moves += 1
        self.score += reward
        if all(figure == -1 for figure in self.figures_to_place):
            self.get_new_figures()
        self.i_figure = None
        self.save_game()
        return True

    def make_move(self, i_figure, x0, y0):
        figure = self.figures_to_place[i_figure]
        w, h = len(figure[0]), len(figure)
        self.figures_to_place[i_figure] = -1
        for y in range(h):
            for x in range(w):
                if figure[y][x]:
                    self.field[y0 + y][x0 + x] = 1
        clear_rows = []
        clear_cols = []
        for y in range(self.h):
            if all(self.field[y]):
                clear_rows.append(y)
        for x in range(self.w):
            if all(self.field[y][x] for y in range(self.h)):
                clear_cols.append(x)
        for y in clear_rows:
            for x in range(self.w):
                self.field[y][x] = 0
        for x in clear_cols:
            for y in range(self.h):
                self.field[y][x] = 0
        return bool(clear_rows) or bool(clear_cols)

    def print_field(self):
        for row in self.field:
            print(' '.join('@' if col else 'O' for col in row))
        print()

    def get_new_figures(self):
        self.figures_to_place = sample(self.figures, k=3)

    def get_moves(self):
        all_moves = {}
        for i_figure, figure in enumerate(self.figures_to_place):
            if figure == -1:
                continue
            figure_moves = []
            w, h = len(figure[0]), len(figure)
            for y0 in range(self.h - h + 1):
                for x0 in range(self.w - w + 1):
                    can_place = True
                    for y in range(h):
                        for x in range(w):
                            if figure[y][x] and self.field[y0 + y][x0 + x]:
                                can_place = False
                                break
                        if not can_place:
                            break
                    if can_place:
                        figure_moves.append((x0, y0))
            if figure_moves:
                all_moves[i_figure] = figure_moves
        return all_moves

    def get_state(self):
        return any(moves for i_figure, moves in self.get_moves().items())

    def save_record(self, name):
        cursor = self.connection.cursor()
        is_in_table = cursor.execute(f'SELECT value FROM records WHERE id = {self.id}').fetchone()
        if is_in_table:
            record = is_in_table[0]
            cursor.execute(f'''
            UPDATE records SET
                name = "{name}",
                value = {max(self.score, record)}
            WHERE id = {self.id}
            ''')
        else:
            cursor.execute(f'''
            INSERT INTO records VALUES ({self.id}, "{name}", {self.score})
            ''')
        self.connection.commit()

    def get_field(self):
        return ''.join(''.join(str(i) for i in row) for row in self.field)

    def get_image(self):
        screen = Image.open('data/screen.png')
        block = Image.open('data/block.png')
        figure_block = Image.open('data/figure_block.png')

        image = Image.new('RGB', screen.size)
        image.paste(screen)

        font = ImageFont.truetype('data/arialbd.ttf', 30)
        draw = ImageDraw.Draw(image)
        draw.text(SCORE_POS, f'{self.score}', fill=SCORE_COLOR, anchor='mm', font=font)

        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    pos = FIELD_X0 + x * BLOCK_SIZE, FIELD_Y0 + y * BLOCK_SIZE
                    image.paste(block, pos)

        for i_figure, figure in enumerate(self.figures_to_place, -1):
            if figure == -1:
                continue
            x, y = FIGURE_X0 + i_figure * FIGURE_SIZE, FIGURE_Y0
            w, h = len(figure[0]), len(figure)
            x0, y0 = x - w * FIGURE_BLOCK_SIZE // 2, y - h * FIGURE_BLOCK_SIZE // 2
            for y, row in enumerate(figure):
                for x, col in enumerate(row):
                    if col:
                        pos = x0 + x * FIGURE_BLOCK_SIZE, y0 + y * FIGURE_BLOCK_SIZE
                        image.paste(figure_block, pos)

        file_name = f'res{self.id}.png'
        image.save(file_name)
        return file_name

    def get_records_image(self):
        screen = Image.open('data/records_screen.png')

        image = Image.new('RGB', screen.size)
        image.paste(screen)

        cursor = self.connection.cursor()
        result = cursor.execute('''SELECT name, value FROM records ORDER BY value DESC''').fetchmany(10)

        font = ImageFont.truetype('data/arialbd.ttf', 36)
        draw = ImageDraw.Draw(image)
        x, y = RECORDS_LIST_POS
        draw.multiline_text((x + DX, y + DY),
                            '\n'.join(f'{i}. {name}' for i, (name, value) in enumerate(result, 1)),
                            fill=RECORDS_BG_COLOR, font=font, spacing=24)
        draw.multiline_text((x, y),
                            '\n'.join(f'{i}. {name}' for i, (name, value) in enumerate(result, 1)),
                            fill=RECORDS_COLOR, font=font, spacing=24)
        x, y = RECORDS_SCORES_POS
        draw.multiline_text((x + DX, y + DY),
                            '\n'.join(f'{value}' for name, value in result),
                            fill=RECORDS_BG_COLOR, font=font, anchor='ra', align='right', spacing=24)
        draw.multiline_text((x, y),
                            '\n'.join(f'{value}' for name, value in result),
                            fill=RECORDS_COLOR, font=font, anchor='ra', align='right', spacing=24)

        file_name = f'records.png'
        image.save(file_name)
        return file_name
