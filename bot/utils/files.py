import os
import re


def sanitize_name(name: str) -> str:
    """Sanitize item or category name for filesystem paths."""
    return re.sub(r"\W+", "_", name)


def ensure_item_folder(item_name: str) -> str:
    folder = os.path.join('assets', 'uploads', sanitize_name(item_name))
    os.makedirs(folder, exist_ok=True)
    return folder


def get_next_file_path(item_name: str, extension: str = 'jpg') -> str:
    folder = ensure_item_folder(item_name)
    existing = [f for f in os.listdir(folder) if f.endswith(f'.{extension}')]
    numbers = [int(os.path.splitext(f)[0]) for f in existing if os.path.splitext(f)[0].isdigit()]
    next_num = max(numbers) + 1 if numbers else 1
    return os.path.join(folder, f'{next_num}.{extension}')


def cleanup_item_file(file_path: str) -> None:
    """Remove file and clean up its folder if empty."""
    if os.path.isfile(file_path):
        os.remove(file_path)
        folder = os.path.dirname(file_path)
        if os.path.isdir(folder) and not os.listdir(folder):
            os.rmdir(folder)


def ensure_lines_folder(item_name: str) -> str:
    """Return folder path for storing text-line inventory for ``item_name``."""
    folder = os.path.join("assets", "lines", sanitize_name(item_name))
    os.makedirs(folder, exist_ok=True)
    return folder


def ensure_lines_file(item_name: str) -> str:
    """Return path to the inventory text file for the given item.

    The file ``lines.txt`` is created inside ``assets/lines/<item>/`` where
    ``<item>`` is a sanitized version of the item name. All directories are
    created if necessary.
    """
    folder = ensure_lines_folder(item_name)
    return os.path.join(folder, "lines.txt")

def ensure_lines_file(item_name: str) -> str:
    """Return path to the inventory text file for the given item.

    The file is created inside ``assets/lines`` and named using a sanitized
    version of ``item_name``.  All directories are created if necessary.
    """
    folder = os.path.join("assets", "lines")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{sanitize_name(item_name)}.txt")



def pop_line_from_file(item_name: str) -> str | None:
    """Pop and return the first non-empty line from the item's text file.

    If the file does not exist or contains no lines, ``None`` is returned.
    The popped line is removed from the file.
    """
    path = ensure_lines_file(item_name)
    if not os.path.isfile(path):
        return None

    with open(path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        # Remove empty lines and preserve newline characters for remaining lines
        lines = [ln for ln in lines if ln.strip()]
        if not lines:
            # Truncate file if it only contained empty lines
            f.seek(0)
            f.truncate()
            return None
        first = lines.pop(0).rstrip("\n")
        f.seek(0)
        f.truncate()
        f.writelines([ln if ln.endswith("\n") else ln + "\n" for ln in lines])
    return first
