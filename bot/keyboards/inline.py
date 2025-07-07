from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.localization import t
from bot.database.methods import get_category_parent


def main_menu(
    role: int, channel: str = None, helper: str = None, lang: str = "en"
) -> InlineKeyboardMarkup:
    """
    Return main menu markup according to requested layout:
     • shop / top_up
     • profile / language
     • (optional) channel & support side-by-side
    """
    # first two rows
    inline_keyboard = [
        [
            InlineKeyboardButton(t(lang, "shop"), callback_data="shop"),
            InlineKeyboardButton(t(lang, "top_up"), callback_data="replenish_balance"),
        ],
        [
            InlineKeyboardButton(t(lang, "profile"), callback_data="profile"),
            InlineKeyboardButton(t(lang, "language"), callback_data="change_language"),
        ],
    ]

    # build combined row for channel & support
    row = []
    if channel:
        row.append(
            InlineKeyboardButton(t(lang, "channel"), url=f"https://t.me/{channel}")
        )
    if helper:
        row.append(
            InlineKeyboardButton(
                t(lang, "support"), url=f"https://t.me/{helper.lstrip('@')}"
            )
        )
    if row:
        inline_keyboard.append(row)

    if role > 1:
        inline_keyboard.append(
            [InlineKeyboardButton(t(lang, "admin_panel"), callback_data="console")]
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def categories_list(
    list_items: list[str], current_index: int, max_index: int
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10 : (current_index + 1) * 10]
    for name in page_items:
        markup.add(InlineKeyboardButton(text=name, callback_data=f"category_{name}"))
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(
                text="◀️", callback_data=f"categories-page_{current_index - 1}"
            ),
            InlineKeyboardButton(
                text=f"{current_index + 1}/{max_index + 1}",
                callback_data="dummy_button",
            ),
            InlineKeyboardButton(
                text="▶️", callback_data=f"categories-page_{current_index + 1}"
            ),
        ]
        markup.row(*buttons)
    markup.add(InlineKeyboardButton("🛒 View Basket", callback_data="view_basket"))
    markup.add(InlineKeyboardButton("🔙 Back to menu", callback_data="back_to_menu"))
    return markup


def goods_list(
    list_items: list[str], category_name: str, current_index: int, max_index: int
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10 : (current_index + 1) * 10]
    for name in page_items:
        markup.add(InlineKeyboardButton(text=name, callback_data=f"item_{name}"))
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"goods-page_{category_name}_{current_index - 1}",
            ),
            InlineKeyboardButton(
                text=f"{current_index + 1}/{max_index + 1}",
                callback_data="dummy_button",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"goods-page_{category_name}_{current_index + 1}",
            ),
        ]
        markup.row(*buttons)
    markup.add(InlineKeyboardButton("🛒 View Basket", callback_data="view_basket"))
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data="shop"))
    return markup


def subcategories_list(
    list_items: list[str], parent: str, current_index: int, max_index: int
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10 : (current_index + 1) * 10]
    for name in page_items:
        markup.add(InlineKeyboardButton(text=name, callback_data=f"category_{name}"))
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"subcategories-page_{parent}_{current_index - 1}",
            ),
            InlineKeyboardButton(
                text=f"{current_index + 1}/{max_index + 1}",
                callback_data="dummy_button",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"subcategories-page_{parent}_{current_index + 1}",
            ),
        ]
        markup.row(*buttons)
    back_parent = get_category_parent(parent)
    back_data = "shop" if back_parent is None else f"category_{back_parent}"
    markup.add(InlineKeyboardButton("🛒 View Basket", callback_data="view_basket"))
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data=back_data))
    return markup


def user_items_list(
    list_items: list,
    data: str,
    back_data: str,
    pre_back: str,
    current_index: int,
    max_index: int,
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    page_items = list_items[current_index * 10 : (current_index + 1) * 10]
    for item in page_items:
        markup.add(
            InlineKeyboardButton(
                text=item.item_name, callback_data=f"bought-item:{item.id}:{pre_back}"
            )
        )
    if max_index > 0:
        buttons = [
            InlineKeyboardButton(
                text="◀️", callback_data=f"bought-goods-page_{current_index - 1}_{data}"
            ),
            InlineKeyboardButton(
                text=f"{current_index + 1}/{max_index + 1}",
                callback_data="dummy_button",
            ),
            InlineKeyboardButton(
                text="▶️", callback_data=f"bought-goods-page_{current_index + 1}_{data}"
            ),
        ]
        markup.row(*buttons)
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data=back_data))
    return markup


def item_info(item_name: str, category_name: str, lang: str) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(
                t(lang, "add_to_basket"), callback_data=f"addbasket_{item_name}"
            )
        ],
        [InlineKeyboardButton(t(lang, "view_basket"), callback_data="view_basket")],
        [InlineKeyboardButton("💰 Buy", callback_data=f"buy_{item_name}")],
        [InlineKeyboardButton("🔙 Go back", callback_data=f"category_{category_name}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def profile(referral_percent: int, user_items: int = 0) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("💸 Top up balance", callback_data="replenish_balance")]
    ]
    if referral_percent != 0:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    "🎲 Referral system", callback_data="referral_system"
                )
            ]
        )
    if user_items != 0:
        inline_keyboard.append(
            [InlineKeyboardButton("🎁 Purchased items", callback_data="bought_items")]
        )
    inline_keyboard.append(
        [InlineKeyboardButton("🔙 Back to menu", callback_data="back_to_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def rules() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("🔙 Back to menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def console() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("🏪 Manage shop", callback_data="shop_management")],
        [InlineKeyboardButton("👥 Manage users", callback_data="user_management")],
        [InlineKeyboardButton("📢 Send broadcast", callback_data="send_message")],
        [InlineKeyboardButton("🔙 Back to menu", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def user_management(
    admin_role: int, user_role: int, admin_manage: int, items: int, user_id: int
) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(
                "💸 Top up balance User", callback_data=f"fill-user-balance_{user_id}"
            )
        ]
    ]
    if items > 0:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    "🎁 Purchased items", callback_data=f"user-items_{user_id}"
                )
            ]
        )
    if admin_role >= admin_manage and admin_role > user_role:
        if user_role == 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        "⬆️ Assign admin", callback_data=f"set-admin_{user_id}"
                    )
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        "⬇️ Remove admin", callback_data=f"remove-admin_{user_id}"
                    )
                ]
            )
    inline_keyboard.append(
        [InlineKeyboardButton("🔙 Go back", callback_data="user_management")]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def user_manage_check(user_id: int) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("✅ Yes", callback_data=f"check-user_{user_id}")],
        [InlineKeyboardButton("🔙 Go back", callback_data="user_management")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def shop_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("📦 Goods management", callback_data="goods_management")],
        [
            InlineKeyboardButton(
                "🗂️ Category management", callback_data="categories_management"
            )
        ],
        [InlineKeyboardButton("📝 Logs", callback_data="show_logs")],
        [InlineKeyboardButton("📊 Statistics", callback_data="statistics")],
        [InlineKeyboardButton("🔙 Go back", callback_data="console")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def goods_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("➕ Add item", callback_data="item-management")],
        [InlineKeyboardButton("✏️ Update item", callback_data="update_item")],
        [InlineKeyboardButton("🗑️ Delete item", callback_data="delete_item")],
        [
            InlineKeyboardButton(
                "🛒 Purchased items info", callback_data="show_bought_item"
            )
        ],
        [InlineKeyboardButton("🔙 Go back", callback_data="shop_management")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def item_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("🆕 Create item", callback_data="add_item")],
        [
            InlineKeyboardButton(
                "➕ Add to existing item", callback_data="update_item_amount"
            )
        ],
        [InlineKeyboardButton("🔙 Go back", callback_data="goods_management")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def categories_management() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("📁 Add category", callback_data="add_category")],
        [InlineKeyboardButton("📂 Add subcategory", callback_data="add_subcategory")],
        [InlineKeyboardButton("✏️ Update category", callback_data="update_category")],
        [InlineKeyboardButton("🗑️ Delete category", callback_data="delete_category")],
        [InlineKeyboardButton("🔙 Go back", callback_data="shop_management")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def close() -> InlineKeyboardMarkup:
    inline_keyboard = [[InlineKeyboardButton("Hide", callback_data="close")]]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def check_sub(channel_username: str) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton("Subscribe", url=f"https://t.me/{channel_username}")],
        [InlineKeyboardButton("Check", callback_data="sub_channel_done")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def back(callback: str) -> InlineKeyboardMarkup:
    inline_keyboard = [[InlineKeyboardButton("🔙 Go back", callback_data=callback)]]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def payment_menu(url: str, label: str, lang: str) -> InlineKeyboardMarkup:
    """Return markup for fiat payment invoices."""
    inline_keyboard = [
        [InlineKeyboardButton("✅ Pay", url=url)],
        [InlineKeyboardButton("🔄 Check payment", callback_data=f"check_{label}")],
        [
            InlineKeyboardButton(
                t(lang, "cancel_payment"), callback_data=f"cancel_{label}"
            )
        ],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def crypto_invoice_menu(invoice_id: str, lang: str) -> InlineKeyboardMarkup:
    """Return markup for crypto invoice."""
    inline_keyboard = [
        [
            InlineKeyboardButton(
                t(lang, "cancel_payment"), callback_data=f"cancel_{invoice_id}"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def crypto_choice() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton("ETH", callback_data="crypto_ETH"),
            InlineKeyboardButton("SOL", callback_data="crypto_SOL"),
        ],
        [
            InlineKeyboardButton("BTC", callback_data="crypto_BTC"),
            InlineKeyboardButton("XRP", callback_data="crypto_XRP"),
        ],
        [InlineKeyboardButton("LTC", callback_data="crypto_LTC")],
        [InlineKeyboardButton("🔙 Go back", callback_data="replenish_balance")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def reset_config(key: str) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(f"Reset {key}", callback_data=f"reset_{key}")],
        [InlineKeyboardButton("🔙 Go back", callback_data="settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def question_buttons(question: str, back_data: str) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=f"{question}_yes"),
            InlineKeyboardButton("❌ No", callback_data=f"{question}_no"),
        ],
        [InlineKeyboardButton("🔙 Go back", callback_data=back_data)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def region_menu(flags: list[str]) -> InlineKeyboardMarkup:
    """Return markup listing regions as flag buttons."""
    markup = InlineKeyboardMarkup()
    for idx, flag in enumerate(flags):
        markup.add(InlineKeyboardButton(text=flag, callback_data=f"reg_{idx}"))
    markup.add(InlineKeyboardButton("🛒 View Basket", callback_data="view_basket"))
    markup.add(InlineKeyboardButton("🔙 Back to menu", callback_data="back_to_menu"))
    return markup


def region_submenu(region_key: int) -> InlineKeyboardMarkup:
    """Return submenu markup for selected region."""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏆 Rank", callback_data=f"rank_{region_key}"))
    markup.add(InlineKeyboardButton("🖼️ Skins", callback_data=f"skin_{region_key}"))
    markup.add(InlineKeyboardButton("🛒 View Basket", callback_data="view_basket"))
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data="shop"))
    return markup


def region_items(
    region_key: int, items: list[str], back_cb: str
) -> InlineKeyboardMarkup:
    """Return markup listing items for a region and category."""
    markup = InlineKeyboardMarkup()
    for item in items:
        markup.add(
            InlineKeyboardButton(text=item, callback_data=f"vitem_{region_key}_{item}")
        )
    markup.add(InlineKeyboardButton("🛒 View Basket", callback_data="view_basket"))
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data=back_cb))
    return markup
