REGIONS = {
    "🇺🇸 USA": {
        "region": "en-us",
        "currency": "USD"
    },
    "🇮🇳 India": {
        "region": "en-in",
        "currency": "INR"
    },
    "🇯🇵 Japan": {
        "region": "ja-jp",
        "currency": "JPY"
    },
    "🇹🇷 Turkey": {
        "region": "en-tr",
        "currency": "TRY"
    },
    "🇬🇧 UK": {
        "region": "en-gb",
        "currency": "GBP"
    },
    "🇩🇪 Germany": {
        "region": "de-de",
        "currency": "EUR"
    },
    "🇧🇷 Brazil": {
        "region": "pt-br",
        "currency": "BRL"
    },
    "🇫🇷 France": {
        "region": "fr-fr",
        "currency": "EUR"
    },
    "🇲🇽 Mexico": {
        "region": "es-mx",
        "currency": "USD"  # MXN изменить 20,08,26
    },
    "🇨🇦 Canada": {
        "region": "en-ca",
        "currency": "CAD"
    },
}

MENU_COMMANDS: dict[str, str] = {
    '/start': 'запуск бота',
    '/help': 'помощь',
    '/settings': 'настройки',
}

LEXICON_RU: dict[str, str] = {
    "start": 'Напиши название игры, а я дам тебе список региональных цен',
    "help": 'Напиши название игры, а я дам тебе список региональных цен',
    "find a game": "🔍 Найти игру",
    "wait": "⏳ Ожидайте...",
    "error": "❌ Не удалось получить информацию о ценах."
}
