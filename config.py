from abc import ABC
from typing import Final


class TgConfig(ABC):
    STATE: Final = {}
    BASKETS: Final = {}
    CHANNEL_URL: Final = 'https://t.me/NBAXSHOP'
    HELPER_URL: Final = '@nbaxox'
    GROUP_ID: Final = -988765433
    REFERRAL_PERCENT = 5
    PAYMENT_TIME: Final = 1800
    RULES: Final = 'insert your rules here'
