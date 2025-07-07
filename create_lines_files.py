import os
from bot.database import Database
from bot.database.models import Goods
from bot.utils.files import ensure_lines_file


def main() -> None:
    session = Database().session
    items = session.query(Goods.name).all()
    if not items:
        print("No products found in database")
        return
    for name, in items:
        path = ensure_lines_file(name)
        if not os.path.isfile(path):
            open(path, "a", encoding="utf-8").close()
            print(f"Created {path}")
        else:
            print(f"Exists {path}")


if __name__ == "__main__":
    main()
