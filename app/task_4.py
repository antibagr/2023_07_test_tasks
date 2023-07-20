import logging

from aiogram import Bot, Dispatcher, executor, types  # type: ignore[import]
from aiogram.contrib.middlewares.logging import (  # type: ignore[import]
    LoggingMiddleware,
)
from aiogram.types import (  # type: ignore[import]
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

API_TOKEN = ""
STRIPE_PROVIDER_TOKEN = ""

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

main_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Profile", callback_data="open_profile")],
        [InlineKeyboardButton("Pop-up balance", callback_data="replenish_balance")],
    ]
)

profile_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Back", callback_data="back_to_main_menu")],
    ]
)

states = {}


@dp.message_handler(commands=["start"])
async def on_start(message: types.Message):
    await message.reply("HTML Clear Bot", reply_markup=main_menu_markup)


@dp.callback_query_handler(lambda c: c.data == "open_profile")
async def on_open_profile(callback_query: types.CallbackQuery):
    # TODO: Get user balance from db
    user_balance = 1000
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        f"Your balance: {user_balance} USD",
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=profile_markup,
    )


@dp.callback_query_handler(lambda c: c.data == "replenish_balance")
async def on_replenish_balance(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    states[callback_query.from_user.id] = "replenishing"

    await bot.send_invoice(
        callback_query.from_user.id,
        title="Balance Replenishment",
        description="Replenish your balance",
        payload="balance_replenish",
        provider_token=STRIPE_PROVIDER_TOKEN,
        start_parameter="balance_replenish",
        currency="USD",
        prices=[types.LabeledPrice("Balance Replenishment", 1000)],
    )


@dp.shipping_query_handler()
async def shipping(query: types.ShippingQuery):
    await bot.answer_shipping_query(query.id, ok=True)


@dp.pre_checkout_query_handler()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    # TODO: Save updated balance to db
    user_balance = 2000
    await bot.send_message(
        message.from_user.id,
        f"Your balance has been replenished. New balance: {user_balance} USD",
        reply_markup=main_menu_markup,
    )
    del states[message.from_user.id]


@dp.callback_query_handler(lambda c: c.data == "back_to_main_menu")
async def on_back_to_main_menu(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        "Back to the Main Menu!",
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=main_menu_markup,
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
