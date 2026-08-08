MENU_COMMANDS: dict[str, str] = {
    '/start': 'запуск бота',
    '/help': 'помощь',
    '/settings': 'настройки',
}

LEXICON: dict[str, dict[str, str]] = {
    "ru": {
        "start": "Напиши название игры, а я дам тебе список региональных цен",
        "help": "Напиши название игры, а я дам тебе список региональных цен",
        "settings": "⚙️ Настройки:",
        "back:settings": "⬅️ Настройки",

        "find a game": "🔍 Найти игру",
        "wait": "⏳ Ожидайте...",
        "error": "❌ Не удалось получить информацию о ценах.",
        "inline_description": "Playstation Store",

        "regions": "🌍 Регионы",
        "regions_select": "Выберите регионы:",
        "region_removed": "Убран регион",
        "region_added": "Добавлен регион",
        "no_region": "НЕТ ВЫБРАННЫХ РЕГИОНОВ\n\nВыберите регионы в /settings",

        "language": "🗣 Язык / Language",

        "currency": "💰 Валюта",
        "currency_select": "Выберите валюту:",
        "currency_chosen": "Текущая валюта",
    },

    "en": {
        "start": "Enter the name of a game and I will show you regional prices",
        "help": "Enter the name of a game and I will show you regional prices",
        "settings": "⚙️ Settings:",
        "back:settings": "⬅️ Settings",

        "find a game": "🔍 Find a game",
        "wait": "⏳ Please wait...",
        "error": "❌ Failed to get price information.",
        "inline_description": "Playstation Store",

        "regions": "🌍 Regions",
        "regions_select": "Select regions:",
        "region_removed": "Region removed",
        "region_added": "Region added",
        "no_region": "NO REGIONS SELECTED\n\nSelect regions in /settings",

        "language": "🗣 Language / Язык",

        "currency": "💰 Currency",
        "currency_select": "Select currency:",
        "currency_chosen": "Current currency",
    },
}

CURRENCIES: dict[str, str] = {
    "USD": "🇺🇸 USD",
    "EUR": "🇪🇺 EUR",
    "BYN": "🇧🇾 BYN",
    "GEL": "🇬🇪 GEL",
    "RUB": "🇷🇺 RUB",
    "CZK": "🇨🇿 CZK",
    "UAH": "🇺🇦 UAH",
    "INR": "🇮🇳 INR",
    "KZT": "🇰🇿 KZT",
    "TRY": "🇹🇷 TRY",
}

LANGUAGES: dict[str, str] = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}
