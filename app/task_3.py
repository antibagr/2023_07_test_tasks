import re

from fontTools.ttLib import TTFont  # type: ignore[import]


def clear_string_with_ttf_font(text: str, ttf_chars: list[str]) -> str:
    escaped_chars = [re.escape(char) for char in ttf_chars]
    regex_pattern = f'[^{"|".join(escaped_chars)}]'
    cleared_text = re.sub(regex_pattern, "", text)
    return cleared_text


def get_ttf_chars(ttf_file_path: str) -> list[str]:
    font = TTFont(ttf_file_path)
    ttf_chars: list[str] = []
    for table in font["cmap"].tables:
        if table.isUnicode():
            ttf_chars.extend(chr(c) for c in table.cmap.keys())
    return ttf_chars


ttf_file_path = r"app\Nunito-Regular.ttf"
ttf_chars = get_ttf_chars(ttf_file_path)
text_with_invalid_chars = r"""编写一个函数，使用 re 模块清除附加字体中不可用的字符串。"""
cleared_text = clear_string_with_ttf_font(text_with_invalid_chars, ttf_chars)
assert cleared_text.strip() == "re"
