import asyncio
import datetime
import os
from io import BytesIO
from urllib.parse import urlparse
import html

import qrcode

from aiogram import Dispatcher
from aiogram.types import (
    Message,
    CallbackQuery,
    ChatType,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from bot.database.methods import (
    select_max_role_id,
    create_user,
    check_role,
    check_user,
    get_all_categories,
    get_all_items,
    select_bought_items,
    get_bought_item_info,
    get_item_info,
    select_item_values_amount,
    get_user_balance,
    get_item_value,
    buy_item,
    add_bought_item,
    buy_item_for_balance,
    select_user_operations,
    select_user_items,
    check_user_referrals,
    start_operation,
    select_unfinished_operations,
    get_user_referral,
    finish_operation,
    update_balance,
    create_operation,
    bought_items_list,
    check_value,
    get_subcategories,
    get_category_parent,
    get_user_language,
    update_user_language,
    get_unfinished_operation,
)
from bot.utils.files import cleanup_item_file
from bot.handlers.other import get_bot_user_ids, get_bot_info
from bot.keyboards import (
    main_menu,
    categories_list,
    goods_list,
    subcategories_list,
    user_items_list,
    back,
    item_info,
    profile,
    rules,
    payment_menu,
    close,
    crypto_choice,
    crypto_invoice_menu,
    region_menu,
    region_submenu,
    region_items,
)
from bot.localization import t
from bot.logger_mesh import logger
from bot.misc import TgConfig, EnvKeys
from bot.misc.payment import quick_pay, check_payment_status
from bot.misc.nowpayments import create_payment, check_payment

# --- Custom shop constants ---
REGION_FLAGS = ["🇪🇺", "🇺🇸", "🇧🇷", "🇲🇽", "🇰🇷", "🇯🇵"]
RANK_TIERS = [
    "Iron",
    "Bronze",
    "Silver",
    "Gold",
    "Platinum",
    "Diamond",
    "Ascendant",
    "Immortal",
    "Radiant",
]
SKIN_RANGES = [
    "1-10",
    "11-20",
    "21-30",
    "31-40",
    "41-50",
    "51-80",
    "81-100",
    "101-150",
    "151-200",
    "200+",
]
# --------------------------------


def build_menu_text(user_obj, balance: float, purchases: int, lang: str) -> str:
    """Return main menu text. Greeting remains in English regardless of language."""
    mention = (
        f"<a href='tg://user?id={user_obj.id}'>{html.escape(user_obj.full_name)}</a>"
    )
    basket_count = len(TgConfig.BASKETS.get(user_obj.id, []))
    return (
        f"{t(lang, 'hello', user=mention)}\n"
        f"{t(lang, 'balance', balance=f'{balance:.2f}')}\n"
        f"{t(lang, 'basket', items=basket_count)}\n"
        f"{t(lang, 'total_purchases', count=purchases)}\n\n"
        f"{t(lang, 'note')}"
    )


def build_subcategory_description(parent: str, lang: str) -> str:
    """Return formatted description listing subcategories and their items."""
    lines = [f" {parent}", ""]
    for sub in get_subcategories(parent):
        lines.append(f"🏘️ {sub}:")
        goods = get_all_items(sub)
        for item in goods:
            info = get_item_info(item)
            amount = select_item_values_amount(item) if not check_value(item) else "∞"
            lines.append(f"    • {item} ({info['price']:.2f}€) - {amount}")
        lines.append("")
    lines.append(t(lang, "choose_subcategory"))
    return "\n".join(lines)


async def start(message: Message):
    bot, user_id = await get_bot_user_ids(message)

    if message.chat.type != ChatType.PRIVATE:
        return

    TgConfig.STATE[user_id] = None

    owner = select_max_role_id()
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    referral_id = message.text[7:] if message.text[7:] != str(user_id) else None
    user_role = owner if str(user_id) == EnvKeys.OWNER_ID else 1
    create_user(
        telegram_id=user_id,
        registration_date=formatted_time,
        referral_id=referral_id,
        role=user_role,
    )
    chat = TgConfig.CHANNEL_URL[13:]
    role_data = check_role(user_id)
    user_db = check_user(user_id)

    user_lang = user_db.language
    if not user_lang:
        lang_markup = InlineKeyboardMarkup(row_width=1)
        lang_markup.add(
            InlineKeyboardButton(
                "English \U0001f1ec\U0001f1e7", callback_data="set_lang_en"
            ),
            InlineKeyboardButton(
                "Русский \U0001f1f7\U0001f1fa", callback_data="set_lang_ru"
            ),
            InlineKeyboardButton(
                "\u4e2d\u6587 \U0001f1e8\U0001f1f3", callback_data="set_lang_zh"
            ),
            InlineKeyboardButton(
                "Espa\u00f1ol \U0001f1ea\U0001f1f8", callback_data="set_lang_es"
            ),
            InlineKeyboardButton(
                "Portugu\u00eas \U0001f1f5\U0001f1f9", callback_data="set_lang_pt"
            ),
        )
        await bot.send_message(
            user_id,
            f"{t('en', 'choose_language')} / {t('ru', 'choose_language')} / {t('zh', 'choose_language')}",
            reply_markup=lang_markup,
        )
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    balance = user_db.balance if user_db else 0
    purchases = select_user_items(user_id)
    markup = main_menu(role_data, chat, TgConfig.HELPER_URL, user_lang)
    text = build_menu_text(message.from_user, balance, purchases, user_lang)
    await bot.send_message(user_id, text, reply_markup=markup)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def back_to_menu_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user = check_user(call.from_user.id)
    user_lang = get_user_language(user_id) or "en"
    markup = main_menu(
        user.role_id, TgConfig.CHANNEL_URL, TgConfig.HELPER_URL, user_lang
    )
    purchases = select_user_items(user_id)
    text = build_menu_text(call.from_user, user.balance, purchases, user_lang)
    await bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def close_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )


async def shop_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    markup = region_menu(REGION_FLAGS)
    await bot.edit_message_text(
        "🌍 Shop categories",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def region_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    region_idx = int(call.data.split("_")[1])
    flag = REGION_FLAGS[region_idx]
    text = (
        f"{flag}\n" "🏠 🏆 Rank: Choose a district:\n" "🏠 🖼️ Skins: Choose a district:"
    )
    markup = region_submenu(region_idx)
    await bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def rank_menu_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    region_idx = int(call.data.split("_")[1])
    markup = region_items(region_idx, RANK_TIERS, f"reg_{region_idx}")
    await bot.edit_message_text(
        "Choose rank:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def skins_menu_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    region_idx = int(call.data.split("_")[1])
    markup = region_items(region_idx, SKIN_RANGES, f"reg_{region_idx}")
    await bot.edit_message_text(
        "Choose skins range:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def region_item_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    _, region_idx, item = call.data.split("_", 2)
    await bot.edit_message_text(
        f"Selected: {item}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=back(f"reg_{region_idx}"),
    )


async def navigate_categories(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    categories = get_all_categories()
    current_index = int(call.data.split("_")[1])
    max_index = len(categories) // 10
    if len(categories) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = categories_list(categories, current_index, max_index)
        await bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text="🏪 Shop categories",
            reply_markup=markup,
        )
    else:
        await bot.answer_callback_query(
            callback_query_id=call.id, text="❌ Page not found"
        )


async def dummy_button(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    await bot.answer_callback_query(callback_query_id=call.id, text="")


async def items_list_callback_handler(call: CallbackQuery):
    category_name = call.data[9:]
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    subcategories = get_subcategories(category_name)
    if subcategories:
        max_index = len(subcategories) // 10
        if len(subcategories) % 10 == 0:
            max_index -= 1
        markup = subcategories_list(subcategories, category_name, 0, max_index)
        lang = get_user_language(user_id) or "en"
        text = build_subcategory_description(category_name, lang)
        await bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
        )
    else:
        goods = get_all_items(category_name)
        max_index = len(goods) // 10
        if len(goods) % 10 == 0:
            max_index -= 1
        markup = goods_list(goods, category_name, 0, max_index)
        lang = get_user_language(user_id) or "en"
        await bot.edit_message_text(
            t(lang, "select_product"),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
        )


async def navigate_goods(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    category_name = call.data.split("_")[1]
    current_index = int(call.data.split("_")[2])
    goods = get_all_items(category_name)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = goods_list(goods, category_name, current_index, max_index)
        await bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text="🏪 Select a product",
            reply_markup=markup,
        )
    else:
        await bot.answer_callback_query(
            callback_query_id=call.id, text="❌ Page not found"
        )


async def navigate_subcategories(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    parent = call.data.split("_")[1]
    current_index = int(call.data.split("_")[2])
    subs = get_subcategories(parent)
    max_index = len(subs) // 10
    if len(subs) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = subcategories_list(subs, parent, current_index, max_index)
        await bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text="🏪 Choose a subcategory",
            reply_markup=markup,
        )
    else:
        await bot.answer_callback_query(
            callback_query_id=call.id, text="❌ Page not found"
        )


async def item_info_callback_handler(call: CallbackQuery):
    item_name = call.data[5:]
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    item_info_list = get_item_info(item_name)
    category = item_info_list["category_name"]
    quantity = "Quantity - unlimited"
    if not check_value(item_name):
        quantity = f"Quantity - {select_item_values_amount(item_name)}pcs."
    lang = get_user_language(user_id) or "en"
    markup = item_info(item_name, category, lang)
    await bot.edit_message_text(
        f"🏪 Item {item_name}\n"
        f'Description: {item_info_list["description"]}\n'
        f'Price - {item_info_list["price"]}€\n'
        f"{quantity}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Inline markup for Home button
def home_markup(lang: str = "en"):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(t(lang, "back_home"), callback_data="home_menu")
    )


async def add_to_basket_handler(call: CallbackQuery):
    item_name = call.data[len("addbasket_") :]
    bot, user_id = await get_bot_user_ids(call)
    basket = TgConfig.BASKETS.setdefault(user_id, [])
    basket.append(item_name)
    await call.answer("Added to basket")


async def view_basket_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    basket = TgConfig.BASKETS.get(user_id, [])
    lang = get_user_language(user_id) or "en"
    if not basket:
        await call.answer(t(lang, "basket_empty"), show_alert=True)
        return

    text_lines = [t(lang, "basket") + "\n"]
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, name in enumerate(basket):
        text_lines.append(f"{idx + 1}. {name}")
        markup.add(
            InlineKeyboardButton(
                t(lang, "remove_item", item=name), callback_data=f"remove_{idx}"
            )
        )
    markup.add(
        InlineKeyboardButton(t(lang, "clear_basket"), callback_data="clear_basket"),
        InlineKeyboardButton(t(lang, "pay_for_basket"), callback_data="pay_basket"),
    )
    await bot.edit_message_text(
        "\n".join(text_lines),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def remove_from_basket_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    idx = int(call.data.split("_")[1])
    basket = TgConfig.BASKETS.get(user_id, [])
    if 0 <= idx < len(basket):
        basket.pop(idx)
    await view_basket_handler(call)


async def clear_basket_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.BASKETS[user_id] = []
    lang = get_user_language(user_id) or "en"
    await call.answer(t(lang, "basket_empty"), show_alert=True)


async def pay_basket_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    basket = TgConfig.BASKETS.get(user_id, [])
    if not basket:
        await call.answer("Basket empty")
        return
    total_price = sum(get_item_info(name)["price"] for name in basket)
    balance = get_user_balance(user_id)
    if balance < total_price:
        await call.answer("Insufficient funds", show_alert=True)
        return
    for name in list(basket):
        fake_call = type(
            "Fake",
            (),
            {
                "data": f"buy_{name}",
                "from_user": call.from_user,
                "message": call.message,
            },
        )
        await buy_item_callback_handler(fake_call)
    TgConfig.BASKETS[user_id] = []


async def buy_item_callback_handler(call: CallbackQuery):
    item_name = call.data[4:]
    bot, user_id = await get_bot_user_ids(call)
    msg = call.message.message_id
    item_info_list = get_item_info(item_name)
    item_price = item_info_list["price"]
    user_balance = get_user_balance(user_id)

    if user_balance >= item_price:
        value_data = get_item_value(item_name)

        if value_data:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            new_balance = buy_item_for_balance(user_id, item_price)
            if os.path.isfile(value_data["value"]):
                with open(value_data["value"], "rb") as photo:
                    await bot.send_photo(
                        chat_id=call.message.chat.id,
                        photo=photo,
                        caption=f"✅ Item purchased. <b>Balance</b>: <i>{new_balance}</i>€",
                        parse_mode="HTML",
                        reply_markup=home_markup(get_user_language(user_id) or "en"),
                    )
                os.remove(value_data["value"])
                await bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=msg,
                    text="✅ Item purchased.",
                    reply_markup=back(f"item_{item_name}"),
                )
                buy_item(value_data["id"], value_data["is_infinity"])
                cleanup_item_file(value_data["value"])

            else:
                await bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=msg,
                    text=f'✅ Item purchased. <b>Balance</b>: <i>{new_balance}</i>€\n\n{value_data["value"]}',
                    parse_mode="HTML",
                    reply_markup=home_markup(get_user_language(user_id) or "en"),
                )
                buy_item(value_data["id"], value_data["is_infinity"])
            add_bought_item(
                value_data["item_name"],
                value_data["value"],
                item_price,
                user_id,
                formatted_time,
            )

            user_info = await bot.get_chat(user_id)
            logger.info(
                f"User {user_id} ({user_info.first_name})"
                f" bought 1 item of {value_data['item_name']} for {item_price}€"
            )
            return

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=msg,
            text="❌ Item out of stock",
            reply_markup=back(f"item_{item_name}"),
        )
        return

    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=msg,
        text="❌ Insufficient funds",
        reply_markup=back(f"item_{item_name}"),
    )


# Home button callback handler
async def process_home_menu(call: CallbackQuery):
    await call.message.delete()
    bot, user_id = await get_bot_user_ids(call)
    user = check_user(user_id)
    lang = get_user_language(user_id) or "en"
    markup = main_menu(user.role_id, TgConfig.CHANNEL_URL, TgConfig.HELPER_URL, lang)
    purchases = select_user_items(user_id)
    text = build_menu_text(call.from_user, user.balance, purchases, lang)
    await bot.send_message(user_id, text, reply_markup=markup)


async def bought_items_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    bought_goods = select_bought_items(user_id)
    goods = bought_items_list(user_id)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    markup = user_items_list(
        bought_goods, "user", "profile", "bought_items", 0, max_index
    )
    await bot.edit_message_text(
        "Your items:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def navigate_bought_items(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    goods = bought_items_list(user_id)
    bought_goods = select_bought_items(user_id)
    current_index = int(call.data.split("_")[1])
    data = call.data.split("_")[2]
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        if data == "user":
            back_data = "profile"
            pre_back = "bought_items"
        else:
            back_data = f"check-user_{data}"
            pre_back = f"user-items_{data}"
        markup = user_items_list(
            bought_goods, data, back_data, pre_back, current_index, max_index
        )
        await bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text="Your items:",
            reply_markup=markup,
        )
    else:
        await bot.answer_callback_query(
            callback_query_id=call.id, text="❌ Page not found"
        )


async def bought_item_info_callback_handler(call: CallbackQuery):
    item_id = call.data.split(":")[1]
    back_data = call.data.split(":")[2]
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    item = get_bought_item_info(item_id)
    await bot.edit_message_text(
        f'<b>Item</b>: <code>{item["item_name"]}</code>\n'
        f'<b>Price</b>: <code>{item["price"]}</code>€\n'
        f'<b>Purchase date</b>: <code>{item["bought_datetime"]}</code>\n'
        f'<b>Unique ID</b>: <code>{item["unique_id"]}</code>\n'
        f'<b>Value</b>:\n<code>{item["value"]}</code>',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="HTML",
        reply_markup=back(back_data),
    )


async def rules_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    rules_data = TgConfig.RULES

    if rules_data:
        await bot.edit_message_text(
            rules_data,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=rules(),
        )
        return

    await call.answer(text="❌ Rules were not added")


async def profile_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    user = call.from_user
    TgConfig.STATE[user_id] = None
    user_info = check_user(user_id)
    balance = user_info.balance
    operations = select_user_operations(user_id)
    overall_balance = 0

    if operations:

        for i in operations:
            overall_balance += i

    items = select_user_items(user_id)
    referral = TgConfig.REFERRAL_PERCENT
    markup = profile(referral, items)
    await bot.edit_message_text(
        text=f"👤 <b>Profile</b> — {user.first_name}\n🆔"
        f" <b>ID</b> — <code>{user_id}</code>\n"
        f"💳 <b>Balance</b> — <code>{balance}</code> €\n"
        f"💵 <b>Total topped up</b> — <code>{overall_balance}</code> €\n"
        f" 🎁 <b>Items purchased</b> — {items} pcs",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML",
    )


async def referral_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    referrals = check_user_referrals(user_id)
    referral_percent = TgConfig.REFERRAL_PERCENT
    await bot.edit_message_text(
        f"💚 Referral system\n"
        f"🔗 Link: https://t.me/{await get_bot_info(call)}?start={user_id}\n"
        f"Number of referrals: {referrals}\n"
        f"📔 The referral system allows you to earn money without investment. "
        f"Just share your referral link and you will receive"
        f" {referral_percent}% of your referrals top-ups to your bot balance.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=back("profile"),
    )


async def replenish_balance_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    message_id = call.message.message_id

    # proceed if NowPayments API key is configured
    if EnvKeys.NOWPAYMENTS_API_KEY:
        TgConfig.STATE[f"{user_id}_message_id"] = message_id
        TgConfig.STATE[user_id] = "process_replenish_balance"
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=message_id,
            text="💰 Enter the top-up amount:",
            reply_markup=back("back_to_menu"),
        )
        return

    # fallback if API key missing
    await call.answer("❌ Top-up is not configured.")


async def process_replenish_balance(message: Message):
    bot, user_id = await get_bot_user_ids(message)

    text = message.text
    message_id = TgConfig.STATE.get(f"{user_id}_message_id")
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if not text.isdigit() or int(text) < 5 or int(text) > 10000:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text="❌ Invalid top-up amount. "
            "The amount must be between 5€ and 10 000€",
            reply_markup=back("replenish_balance"),
        )
        return

    TgConfig.STATE[f"{user_id}_amount"] = text
    markup = crypto_choice()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=f"💵 Top-up amount: {text}€. Choose payment method:",
        reply_markup=markup,
    )


async def pay_yoomoney(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    amount = TgConfig.STATE.pop(f"{user_id}_amount", None)
    if not amount:
        await call.answer(text="❌ Invoice not found")
        return

    fake = type("Fake", (), {"text": amount, "from_user": call.from_user})
    label, url = quick_pay(fake)
    sleep_time = int(TgConfig.PAYMENT_TIME)
    lang = get_user_language(user_id) or "en"
    markup = payment_menu(url, label, lang)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"💵 Top-up amount: {amount}€.\n"
        f"⌛️ You have {int(sleep_time / 60)} minutes to pay.\n"
        f'<b>❗️ After payment press "Check payment"</b>',
        reply_markup=markup,
    )
    start_operation(user_id, amount, label, call.message.message_id)
    await asyncio.sleep(sleep_time)
    info = get_unfinished_operation(label)
    if info:
        _, _, _ = info
        status = await check_payment_status(label)
        if status not in ("paid", "success"):
            finish_operation(label)
            await bot.send_message(user_id, t(lang, "invoice_cancelled"))


async def crypto_payment(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    currency = call.data.split("_")[1]
    amount = TgConfig.STATE.pop(f"{user_id}_amount", None)
    if not amount:
        await call.answer(text="❌ Invoice not found")
        return

    payment_id, address, pay_amount = create_payment(float(amount), currency)

    sleep_time = int(TgConfig.PAYMENT_TIME)
    lang = get_user_language(user_id) or "en"
    expires_at = (
        datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)
    ).strftime("%H:%M")
    markup = crypto_invoice_menu(payment_id, lang)
    text = t(
        lang,
        "invoice_message",
        amount=pay_amount,
        currency=currency,
        address=address,
        expires_at=expires_at,
    )

    # Generate QR code for the address
    qr = qrcode.make(address)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    sent = await bot.send_photo(
        chat_id=call.message.chat.id,
        photo=buf,
        caption=text,
        parse_mode="HTML",
        reply_markup=markup,
    )
    start_operation(user_id, amount, payment_id, sent.message_id)
    await asyncio.sleep(sleep_time)
    info = get_unfinished_operation(payment_id)
    if info:
        _, _, _ = info
        status = await check_payment(payment_id)
        if status not in ("finished", "confirmed", "sending"):
            finish_operation(payment_id)
            await bot.send_message(user_id, t(lang, "invoice_cancelled"))


async def checking_payment(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    message_id = call.message.message_id
    label = call.data[6:]
    info = get_unfinished_operation(label)

    if info:
        user_id_db, operation_value, _ = info
        payment_status = await check_payment_status(label)
        if payment_status is None:
            payment_status = await check_payment(label)

        if payment_status in ("success", "paid", "finished", "confirmed", "sending"):
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            referral_id = get_user_referral(user_id)
            finish_operation(label)

            if referral_id and TgConfig.REFERRAL_PERCENT != 0:
                referral_percent = TgConfig.REFERRAL_PERCENT
                referral_operation = round((referral_percent / 100) * operation_value)
                update_balance(referral_id, referral_operation)
                await bot.send_message(
                    referral_id,
                    f"✅ You received {referral_operation}€ "
                    f"from your referral {call.from_user.first_name}",
                    reply_markup=close(),
                )

            create_operation(user_id, operation_value, formatted_time)
            update_balance(user_id, operation_value)
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=message_id,
                text=f"✅ Balance topped up by {operation_value}€",
                reply_markup=back("profile"),
            )
        else:
            await call.answer(text="❌ Payment was not successful")
    else:
        await call.answer(text="❌ Invoice not found")


async def cancel_payment(call: CallbackQuery):

    bot, user_id = await get_bot_user_ids(call)
    invoice_id = call.data.split("_", 1)[1]
    lang = get_user_language(user_id) or "en"
    if get_unfinished_operation(invoice_id):
        finish_operation(invoice_id)
        await bot.edit_message_text(
            t(lang, "invoice_cancelled"),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back("replenish_balance"),
        )
    else:
        await call.answer(text="❌ Invoice not found")


async def check_sub_to_channel(call: CallbackQuery):

    bot, user_id = await get_bot_user_ids(call)
    invoice_id = call.data.split("_", 1)[1]
    lang = get_user_language(user_id) or "en"
    if get_unfinished_operation(invoice_id):
        finish_operation(invoice_id)
        await bot.edit_message_text(
            t(lang, "invoice_cancelled"),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back("replenish_balance"),
        )
    else:
        await call.answer(text="❌ Invoice not found")


async def change_language(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    current_lang = get_user_language(user_id) or "en"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            "English \U0001f1ec\U0001f1e7", callback_data="set_lang_en"
        ),
        InlineKeyboardButton(
            "Русский \U0001f1f7\U0001f1fa", callback_data="set_lang_ru"
        ),
        InlineKeyboardButton(
            "\u4e2d\u6587 \U0001f1e8\U0001f1f3", callback_data="set_lang_zh"
        ),
        InlineKeyboardButton(
            "Espa\u00f1ol \U0001f1ea\U0001f1f8", callback_data="set_lang_es"
        ),
        InlineKeyboardButton(
            "Portugu\u00eas \U0001f1f5\U0001f1f9", callback_data="set_lang_pt"
        ),
    )
    await bot.edit_message_text(
        t(current_lang, "choose_language"),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


async def set_language(call: CallbackQuery, first_time=False):
    bot, user_id = await get_bot_user_ids(call)
    lang_code = call.data.split("_")[-1]
    update_user_language(user_id, lang_code)
    await call.message.delete()
    role = check_role(user_id)
    chat = TgConfig.CHANNEL_URL[13:]
    user = check_user(user_id)
    balance = user.balance if user else 0
    markup = main_menu(role, chat, TgConfig.HELPER_URL, lang_code)
    purchases = select_user_items(user_id)
    text = build_menu_text(call.from_user, balance, purchases, lang_code)

    # Only send the video if it's the first time (after /start)
    if first_time:
        await bot.send_chat_action(user_id, "upload_video")
        caption = t(lang_code, "welcome_video_caption") or "Welcome to the bot! 👋"
        await bot.send_video(user_id, open(r"E:\a\Untitled.mp4", "rb"), caption=caption)

    # Always send the menu (as a new message)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=markup)


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])

    dp.register_callback_query_handler(
        shop_callback_handler, lambda c: c.data == "shop"
    )
    dp.register_callback_query_handler(
        region_callback_handler, lambda c: c.data.startswith("reg_")
    )
    dp.register_callback_query_handler(
        rank_menu_handler, lambda c: c.data.startswith("rank_")
    )
    dp.register_callback_query_handler(
        skins_menu_handler, lambda c: c.data.startswith("skin_")
    )
    dp.register_callback_query_handler(
        region_item_handler, lambda c: c.data.startswith("vitem_")
    )
    dp.register_callback_query_handler(dummy_button, lambda c: c.data == "dummy_button")
    dp.register_callback_query_handler(
        profile_callback_handler, lambda c: c.data == "profile"
    )
    dp.register_callback_query_handler(
        rules_callback_handler, lambda c: c.data == "rules"
    )
    dp.register_callback_query_handler(
        replenish_balance_callback_handler, lambda c: c.data == "replenish_balance"
    )
    dp.register_callback_query_handler(
        referral_callback_handler, lambda c: c.data == "referral_system"
    )
    dp.register_callback_query_handler(
        bought_items_callback_handler, lambda c: c.data == "bought_items"
    )
    dp.register_callback_query_handler(
        back_to_menu_callback_handler, lambda c: c.data == "back_to_menu"
    )
    dp.register_callback_query_handler(
        close_callback_handler, lambda c: c.data == "close"
    )
    dp.register_callback_query_handler(
        change_language, lambda c: c.data == "change_language"
    )
    dp.register_callback_query_handler(
        set_language, lambda c: c.data.startswith("set_lang_")
    )

    dp.register_callback_query_handler(
        navigate_categories, lambda c: c.data.startswith("categories-page_")
    )
    dp.register_callback_query_handler(
        navigate_subcategories, lambda c: c.data.startswith("subcategories-page_")
    )
    dp.register_callback_query_handler(
        navigate_bought_items, lambda c: c.data.startswith("bought-goods-page_")
    )
    dp.register_callback_query_handler(
        navigate_goods, lambda c: c.data.startswith("goods-page_")
    )
    dp.register_callback_query_handler(
        bought_item_info_callback_handler, lambda c: c.data.startswith("bought-item:")
    )
    dp.register_callback_query_handler(
        items_list_callback_handler, lambda c: c.data.startswith("category_")
    )
    dp.register_callback_query_handler(
        item_info_callback_handler, lambda c: c.data.startswith("item_")
    )
    dp.register_callback_query_handler(
        add_to_basket_handler, lambda c: c.data.startswith("addbasket_")
    )
    dp.register_callback_query_handler(
        view_basket_handler, lambda c: c.data == "view_basket"
    )
    dp.register_callback_query_handler(
        remove_from_basket_handler, lambda c: c.data.startswith("remove_")
    )
    dp.register_callback_query_handler(
        clear_basket_handler, lambda c: c.data == "clear_basket"
    )
    dp.register_callback_query_handler(
        pay_basket_handler, lambda c: c.data == "pay_basket"
    )
    dp.register_callback_query_handler(
        buy_item_callback_handler, lambda c: c.data.startswith("buy_")
    )
    dp.register_callback_query_handler(pay_yoomoney, lambda c: c.data == "pay_yoomoney")
    dp.register_callback_query_handler(
        crypto_payment, lambda c: c.data.startswith("crypto_")
    )
    dp.register_callback_query_handler(
        cancel_payment, lambda c: c.data.startswith("cancel_")
    )
    dp.register_callback_query_handler(
        checking_payment, lambda c: c.data.startswith("check_")
    )
    dp.register_callback_query_handler(
        process_home_menu, lambda c: c.data == "home_menu"
    )

    dp.register_message_handler(
        process_replenish_balance,
        lambda c: TgConfig.STATE.get(c.from_user.id) == "process_replenish_balance",
    )
