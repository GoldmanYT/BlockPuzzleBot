# MESSAGE CONSTS
START_TEXT = '''Я бот, позволяющий играть в Block Puzzle.
Для начала игры напишите /game'''

GAME_START = '''Вы начали игру.
Выберать фигуру: /choose <номер фигуры>
Поставить фигуру: /move <номер столбца> <номер строки>'''

FIGURE_NOT_CHOSEN = 'Не выбрана фигура'
WRONG_FIGURE_NUMBER = 'Неверный номер фигуры'
SUCCESSFUL_CHOICE = 'Выбрана фигура №'

WRONG_POS = 'Неверные координаты фигуры'
NOT_ENOUGH_SPACE = 'Недостаточно места для установки фигуры'
SUCCESSFUL_MOVE = 'Успешная установка фигуры'

GAME_END = 'Нет ходов. Ваш результат: '

# IMAGE CONSTS
BLOCK_SIZE = 63
FIELD_X0, FIELD_Y0 = 62, 137

FIGURE_SIZE = 161
FIGURE_BLOCK_SIZE = 27
FIGURE_X0, FIGURE_Y0 = 314, 762

SCORE_POS = 312, 64
SCORE_COLOR = 255, 255, 255
