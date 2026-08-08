import pandas as pd
import requests

from io import StringIO


URLS = [
    "https://en.wikipedia.org/wiki/List_of_PlayStation_4_games_(A%E2%80%93L)",
    "https://en.wikipedia.org/wiki/List_of_PlayStation_4_games_(M%E2%80%93Z)",
    "https://en.wikipedia.org/wiki/List_of_PlayStation_5_games",
]


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def parse_games():
    games = set()

    for url in URLS:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

        tables = pd.read_html(
            StringIO(response.text)
        )

        for table in tables:
            for column in table.columns:

                if "Title" in str(column):
                    for name in table[column]:
                        if isinstance(name, str):
                            games.add(name.strip())

    return games


def save_games(games, filename="games_list.txt"):
    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        for game in sorted(games):
            file.write(game + "\n")

    print(f"Saved {len(games)} game names to {filename}")


def main():
    games = parse_games()
    save_games(games)


if __name__ == "__main__":
    main()