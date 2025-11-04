from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

stop = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="STOP Q&A", callback_data="stop_qa")]]
)
