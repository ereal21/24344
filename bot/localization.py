LANGUAGES = {
    'en': {
        'hello': '👋 Hello, {user}!',
        'balance': '💰 Balance: {balance} EUR',
        'basket': '🛒 Basket: {items} item(s)',
        'overpay': '💳 Send the exact amount. Overpayments will be credited.',
        'shop': '🛍 Shop',
        'profile': '👤 Profile',
        'top_up': '💸 Top Up',
        'channel': '📢 Channel',
        'support': '🆘 Support',
        'language': '🌐 Language',
        'admin_panel': '🎛 Admin Panel',
        'choose_language': 'Please choose a language',
        'invoice_message': (
            '🧾 <b>Payment Invoice Created</b>\n\n'
            '<b>Amount:</b> <code>{amount}</code> {currency}\n'
            '🏦 <b>Payment Address:</b>\n<code>{address}</code>\n\n'
            '⏳ <b>Expires At:</b> {expires_at} LT\n'
            '⚠️ <b>Payment must be completed within 30 minutes of invoice creation.</b>\n\n'
            '❗️ <b>Important:</b> Send <u>exactly</u> this amount of {currency}.\n\n'
            '✅ <b>Confirmation is automatic via webhook after network confirmation.</b>'
        ),
        'cancel': 'Cancel',
        'cancel_payment': '❌ Cancel Payment',
        'payment_successful': '✅ Payment confirmed. Balance increased by {amount}€',
        'back_home': 'Back Home',
        'add_to_basket': 'Add to basket',
        'view_basket': 'View Basket',
        'clear_basket': 'Clear Basket',
        'pay_for_basket': 'Pay for basket',
        'basket_empty': 'Your basket is empty',
        'remove_item': 'Remove {item}',
        'invoice_cancelled': 'Payment failed/expired. Your items are no longer reserved.',
        'total_purchases': '📦 Total Purchases: {count}',
        'note': '⚠️ Note: No refunds. Please ensure you send the exact amount for payments, as underpayments will not be confirmed.',

        'choose_subcategory': '🏘️ Choose a district:',
        'select_product': '🏪 Select a product',


        'choose_subcategory': '🏘️ Choose a district:',
        'select_product': '🏪 Select a product',


    },
    'ru': {
        'hello': '👋 Привет, {user}!',
        'balance': '💰 Баланс: {balance} EUR',
        'basket': '🛒 Корзина: {items} шт.',
        'overpay': '💳 Отправьте точную сумму. Переплаты будут зачислены.',
        'shop': '🛍 Магазин',
        'profile': '👤 Профиль',
        'top_up': '💸 Пополнить',
        'channel': '📢 Канал',
        'support': '🆘 Поддержка',
        'language': '🌐 Язык',
        'admin_panel': '🎛 Админ панель',
        'choose_language': 'Пожалуйста, выберите язык',
        'invoice_message': (
            '🧾 <b>Создан инвойс на оплату</b>\n\n'
            '<b>Сумма:</b> <code>{amount}</code> {currency}\n'
            '🏦 <b>Адрес оплаты:</b>\n<code>{address}</code>\n\n'
            '⏳ <b>Действителен до:</b> {expires_at} LT\n'
            '⚠️ <b>Оплата должна быть выполнена в течение 30 минут после создания.</b>\n\n'
            '❗️ <b>Важно:</b> Отправьте <u>ровно</u> это количество {currency}.\n\n'
            '✅ <b>Подтверждение произойдет автоматически через вебхук после подтверждения сети.</b>'
        ),
        'cancel': 'Отмена',
        'cancel_payment': '❌ Отменить оплату',
        'payment_successful': '✅ Платёж подтверждён. Баланс пополнен на {amount}€',
        'back_home': 'Назад домой',
        'add_to_basket': 'Добавить в корзину',
        'view_basket': 'Посмотреть корзину',
        'clear_basket': 'Очистить корзину',
        'pay_for_basket': 'Оплатить корзину',
        'basket_empty': 'Ваша корзина пуста',
        'remove_item': 'Удалить {item}',
        'invoice_cancelled': 'Оплата не завершена/истекла. Ваши товары больше не зарезервированы.',
        'total_purchases': '📦 Всего покупок: {count}',
        'note': '⚠️ Возврат средств невозможен. Отправляйте точную сумму, недоплаты не подтверждаются.',

        'choose_subcategory': '🏘️ Выберите район:',
        'select_product': '🏪 Выберите товар',


        'choose_subcategory': '🏘️ Выберите район:',
        'select_product': '🏪 Выберите товар',

    },
    'zh': {
        'hello': '👋 你好, {user}!',
        'balance': '💰 余额: {balance} EUR',
        'basket': '🛒 购物车: {items} 件',
        'overpay': '💳 请发送准确金额，多余款项也会被记入。',
        'shop': '🛍 商店',
        'profile': '👤 个人信息',
        'top_up': '💸 充值',
        'channel': '📢 频道',
        'support': '🆘 支持',
        'language': '🌐 语言',
        'admin_panel': '🎛 管理面板',
        'choose_language': '请选择语言',
        'invoice_message': (
            '🧾 <b>生成支付账单</b>\n\n'
            '<b>金额:</b> <code>{amount}</code> {currency}\n'
            '🏦 <b>支付地址:</b>\n<code>{address}</code>\n\n'
            '⏳ <b>到期时间:</b> {expires_at} LT\n'
            '⚠️ <b>账单生成后请在30分钟内完成支付。</b>\n\n'
            '❗️ <b>重要:</b> 请发送<u>准确</u>数量的 {currency}.\n\n'
            '✅ <b>确认将在网络确认后自动完成。</b>'
        ),
        'cancel': '取消',
        'cancel_payment': '❌ 取消支付',
        'payment_successful': '✅ 支付成功，余额增加 {amount}€',
        'back_home': '返回首页',
        'add_to_basket': '加入购物车',
        'view_basket': '查看购物车',
        'clear_basket': '清空购物车',
        'pay_for_basket': '支付购物车',
        'basket_empty': '购物车为空',
        'remove_item': '移除 {item}',
        'invoice_cancelled': '支付失败或过期。商品已不再保留。',
        'total_purchases': '📦 已购商品: {count}',
        'note': '⚠️ 注意：概不退款。请确保发送准确金额，少于金额将不会确认。',

        'choose_subcategory': '🏘️ 选择地区:',
        'select_product': '🏪 选择商品',

        'choose_subcategory': '🏘️ 选择地区:',
        'select_product': '🏪 选择商品',


    },
    'es': {},
    'pt': {},
}

LANGUAGES['es'] = LANGUAGES['en'].copy()
LANGUAGES['pt'] = LANGUAGES['en'].copy()

def t(lang: str, key: str, **kwargs) -> str:
    lang_data = LANGUAGES.get(lang, LANGUAGES['en'])
    template = lang_data.get(key, '')
    return template.format(**kwargs)
