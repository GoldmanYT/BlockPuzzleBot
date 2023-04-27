import logging
import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from consts import *
from game import Game

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def get_menu_buttons():
    reply_keyboard = [[GAME], [SETTINGS], [RECORDS], [HELP]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    return markup


def get_game_buttons(game, figures=True):
    if figures:
        reply_keyboard = [[FIGURES[i] if figure != -1 else NO_FIGURE
                           for i, figure in zip(range(len(FIGURES)), game.figures_to_place)]]
        if game.all_buttons_on_screen:
            reply_keyboard.extend([[f'{i}{j}' if game.i_figure is not None and
                                    (i - 1, j - 1) in game.get_moves().get(game.i_figure - 1, []) else NO_MOVE
                                    for i in range(1, W + 1)] for j in range(1, H + 1)])
        reply_keyboard.append([BACK])
    else:
        reply_keyboard = [[f'{i}{j}' if game.i_figure is not None and
                           (i - 1, j - 1) in game.get_moves().get(game.i_figure - 1, []) else NO_MOVE
                           for i in range(1, W + 1)] for j in range(1, H + 1)] + [[BACK_TO_FIGURES]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    return markup


async def send_field_photo(update, game, caption, markup):
    file_name = game.get_image()
    await update.message.reply_photo(file_name, caption=caption, reply_markup=markup)
    os.remove(file_name)


async def save_record(update, game):
    name = update.message.chat.first_name
    game.save_record(name)
    if not game.get_state():
        markup = get_menu_buttons()
        await update.message.reply_text(f'{GAME_END}{game.score}', reply_markup=markup)
        game.new_game()


async def message(update, context):
    get_game(update, context)
    game = context.user_data['game']
    text = update.message.text

    if text == GAME:
        markup = get_game_buttons(game)
        await send_field_photo(update, game, GAME_START, markup)

    elif text == SETTINGS:
        reply_keyboard = [[TURN_OFF_ALL_BUTTONS if game.all_buttons_on_screen else TURN_ON_ALL_BUTTONS], [BACK]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text(SETTING_SHOWED, reply_markup=markup)

    elif text == TURN_OFF_ALL_BUTTONS:
        settings = [False]
        game.change_settings(settings)
        reply_keyboard = [[TURN_ON_ALL_BUTTONS], [BACK]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text(SETTING_SAVED, reply_markup=markup)

    elif text == TURN_ON_ALL_BUTTONS:
        settings = [True]
        game.change_settings(settings)
        reply_keyboard = [[TURN_OFF_ALL_BUTTONS], [BACK]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text(SETTING_SAVED, reply_markup=markup)

    elif text == RECORDS:
        reply_keyboard = [[BACK]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        file_name = game.get_records_image()
        await update.message.reply_photo(file_name, caption=RECORDS_SHOWED, reply_markup=markup)
        os.remove(file_name)

    elif text == HELP:
        reply_keyboard = [[BACK]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text(HELP_TEXT, reply_markup=markup)

    elif text == BACK:
        markup = get_menu_buttons()
        await update.message.reply_text(START_TEXT, reply_markup=markup)

    elif text in (FIGURE1, FIGURE2, FIGURE3):
        i_figure = (FIGURE1, FIGURE2, FIGURE3).index(text)
        reply_text = f'{SUCCESSFUL_CHOICE}{i_figure + 1}'
        if game.figures_to_place[i_figure] == -1:
            reply_text = WRONG_FIGURE_NUMBER
        else:
            game.i_figure = i_figure + 1
        if not game.all_buttons_on_screen and game.figures_to_place[i_figure] != -1:
            markup = get_game_buttons(game, figures=False)
            await update.message.reply_text(reply_text, reply_markup=markup)
        else:
            markup = get_game_buttons(game)
            await update.message.reply_text(reply_text, reply_markup=markup)

    elif text == BACK_TO_FIGURES:
        reply_keyboard = [[FIGURE1, FIGURE2, FIGURE3], [BACK]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await send_field_photo(update, game, SELECT_FIGURE, markup)

    elif len(text) == 2 and all(i in '12345678' for i in text):
        markup = get_game_buttons(game)
        if game.i_figure is None:
            await update.message.reply_text(FIGURE_NOT_CHOSEN, reply_markup=markup)
            return
        x, y = map(int, text)
        figure_placed = game.next_move(x, y)
        if not figure_placed:
            await update.message.reply_text(NOT_ENOUGH_SPACE)
            return
        markup = get_game_buttons(game)
        await send_field_photo(update, game, SUCCESSFUL_MOVE, markup)

    elif text == NO_FIGURE:
        await update.message.reply_text(WRONG_FIGURE_NUMBER)

    elif text == NO_MOVE:
        await update.message.reply_text(NOT_ENOUGH_SPACE)

    await save_record(update, game)


async def start(update, context):
    markup = get_menu_buttons()
    await update.message.reply_text(START_TEXT, reply_markup=markup)


def get_game(update, context):
    if 'game' in context.user_data:
        return
    game_id = update.message.chat.id
    game = Game(game_id)
    context.user_data['game'] = game


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT, message))

    application.run_polling()


if __name__ == '__main__':
    main()
