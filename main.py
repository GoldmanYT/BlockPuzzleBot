import logging
import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN
from consts import *
from game import Game


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(START_TEXT)


def get_game(update, context):
    if 'game' in context.user_data:
        return
    game_id = update.message.chat.id
    game = Game(game_id)
    context.user_data['game'] = game


async def game(update, context):
    get_game(update, context)
    game = context.user_data['game']
    reply_keyboard = [[f'/move {i} {j}' for i in range(1, game.w + 1)] for j in range(1, game.h + 1)]
    reply_keyboard.insert(0, ['/choose 1', '/choose 2', '/choose 3', '/back'])
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    file_name = game.get_image()
    await update.message.reply_photo(file_name, caption=GAME_START, reply_markup=markup)
    os.remove(file_name)


async def choose(update, context):
    get_game(update, context)
    args = context.args
    if not args:
        await update.message.reply_text(WRONG_FIGURE_NUMBER)
        return
    n_figure = args[0]
    if not n_figure.isdigit():
        await update.message.reply_text(WRONG_FIGURE_NUMBER)
        return
    n_figure = int(n_figure)
    if not (1 <= n_figure <= 3):
        await update.message.reply_text(WRONG_FIGURE_NUMBER)
        return
    game = context.user_data['game']
    if game.figures_to_place[n_figure - 1] == -1:
        await update.message.reply_text(WRONG_FIGURE_NUMBER)
        return
    game.i_figure = n_figure
    await update.message.reply_text(f'{SUCCESSFUL_CHOICE}{n_figure}')


async def move(update, context):
    get_game(update, context)
    args = context.args
    if not args:
        update.message.reply_text(WRONG_POS)
        return
    x, y = context.args[:2]
    if any(not i.isdigit() for i in (x, y)):
        await update.message.reply_text(WRONG_POS)
        return
    game = context.user_data['game']
    x, y = map(int, (x, y))
    if not all((1 <= x <= game.w, 1 <= y <= game.h)):
        await update.message.reply_text(WRONG_POS)
        return
    if game.i_figure is None:
        await update.message.reply_text(FIGURE_NOT_CHOSEN)
        return
    figure_placed = game.next_move(x, y)
    if not figure_placed:
        await update.message.reply_text(NOT_ENOUGH_SPACE)
        return
    file_name = game.get_image()
    await update.message.reply_photo(file_name, caption=SUCCESSFUL_MOVE)
    os.remove(file_name)
    if not game.get_state():
        await update.message.reply_text(f'GAME_END{game.score}')


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('back', start))
    application.add_handler(CommandHandler('game', game))
    application.add_handler(CommandHandler('choose', choose))
    application.add_handler(CommandHandler('move', move))
    
    application.run_polling()


if __name__ == '__main__':
    main()
