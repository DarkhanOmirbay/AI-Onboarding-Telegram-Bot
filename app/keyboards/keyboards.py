from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

stop = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="STOP Q&A", callback_data="stop_qa")]]
)
