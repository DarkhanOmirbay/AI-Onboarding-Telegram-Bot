from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

stop = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="STOP Q&A", callback_data="stop_qa")]]
)
department_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Development team(DEV)", callback_data="dep_dev")],
        [InlineKeyboardButton(text="Product team(PROD)", callback_data="dep_prod")],
        [InlineKeyboardButton(text="Customer care(CUSCARE)", callback_data="dep_cuscare")],
        [InlineKeyboardButton(text="Финансовый отдел", callback_data="dep_fin")],
        [InlineKeyboardButton(text="Government relations(GR)", callback_data="dep_gr")],
        [InlineKeyboardButton(text="HR", callback_data="dep_hr")],
        [InlineKeyboardButton(text="Коммерческий отдел", callback_data="dep_commercial")],
        [InlineKeyboardButton(text="Маркетинг", callback_data="dep_marketing")],
    ]
)
