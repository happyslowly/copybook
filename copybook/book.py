import os

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4, legal, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PAPER_SIZES = {
    "a4": A4,
    "letter": letter,
    "legal": legal,
}

PUNCT_POSITION = {
    "left": [
        "‘",
        "“",
        "「",
        "『",
        "（",
        "〔",
        "【",
        "《",
        "—",
        "…",
        "～",
        "'",
        '"',
        "(",
        "[",
        "{",
        "-",
    ],
    "right": [
        "’",
        "”",
        "」",
        "』",
        "）",
        "〕",
        "】",
        "》",
        "。",
        "，",
        "、",
        "；",
        "：",
        "？",
        "！",
        "'",
        '"',
        ")",
        "]",
        "}",
        ".",
        ",",
        ";",
        ":",
        "?",
        "!",
    ],
}

CONNECTED_PUNCT = ["—", "…", "～", "－", "-"]


def load_file(text_file: str) -> list[str]:
    char_list = []
    try:
        with open(text_file, "r", encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                char_list.extend([c for c in list(line) if c.strip()])
    except Exception as e:
        print(f"Error reading file '{text_file}': {e}")
        exit(1)
    return char_list


def group_connect_punct(char_list):
    result = []
    i = 0
    while i < len(char_list):
        char = char_list[i]
        if char in CONNECTED_PUNCT:
            sequence = char
            j = i + 1
            while j < len(char_list) and char_list[j] == char:
                sequence += char
                j += 1
            result.append(sequence)
            i = j
        else:
            result.append(char)
            i += 1
    return result


def attach_punctuation(char_list):
    punct_rules = {char: pos for pos, chars in PUNCT_POSITION.items() for char in chars}
    result = []  # [char, left_punct, right_punct]
    for i, char in enumerate(char_list):
        if not char:
            continue
        # use char[0] because of connected punct
        if char[0] not in punct_rules:
            result.append([char, None, None])
            continue
        position = punct_rules[char[0]]
        if position == "left" and i + 1 < len(char_list):
            next_char = char_list[i + 1]
            result.append([next_char, char, None])
            char_list[i + 1] = None
        if position == "right" and result:
            result[-1][2] = char
    return result


def find_font_file(font_name: str) -> str:
    search_paths = [
        f"/System/Library/Fonts/{font_name}.ttf",
        f"/System/Library/Fonts/{font_name}.ttc",
        f"/System/Library/Fonts/{font_name}.otf",
        f"/Library/Fonts/{font_name}.ttf",
        f"/Library/Fonts/{font_name}.ttc",
        f"/Library/Fonts/{font_name}.otf",
        f"{os.path.expanduser('~')}/Library/Fonts/{font_name}.ttf",
        f"{os.path.expanduser('~')}/Library/Fonts/{font_name}.ttc",
        f"{os.path.expanduser('~')}/Library/Fonts/{font_name}.otf",
    ]

    for path in search_paths:
        if os.path.exists(path):
            return path
    raise ValueError(f"Font `{font_name}` not found")


def setup_chinese_font(font_name: str) -> str:
    font_path = find_font_file(font_name)
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    return font_name


def create_pdf_canvas(filename: str, page_size: tuple) -> canvas.Canvas:
    return canvas.Canvas(filename, pagesize=page_size)


def calculate_page_dimensions(args, number_of_characters, width, page_height):
    page_margin = args.page_margin
    grid_spacing = args.grid_spacing
    line_spacing = args.line_spacing

    available_width = width - 2 * page_margin
    available_height = page_height - 2 * page_margin
    cols_per_page = int(available_width // (args.grid + grid_spacing))
    rows_per_page = int(available_height // (args.grid + line_spacing))
    characters_per_page = cols_per_page * rows_per_page
    number_of_pages = (
        1 + (number_of_characters - 1) // characters_per_page
        if characters_per_page > 0
        else 1
    )

    return {
        "cols_per_page": cols_per_page,
        "rows_per_page": rows_per_page,
        "characters_per_page": characters_per_page,
        "number_of_pages": number_of_pages,
        "page_margin": page_margin,
        "grid_spacing": grid_spacing,
        "line_spacing": line_spacing,
    }


def draw_grid(c: canvas.Canvas, x: float, y: float, grid_size: float):
    c.setStrokeColor(Color(0, 0, 0, 1))
    c.setLineWidth(1)
    c.rect(x, y, grid_size, grid_size)

    c.setStrokeColor(Color(0.5, 0.5, 0.5, 1))
    c.setLineWidth(0.5)
    c.setDash([0.5, 2])

    c.line(x + grid_size / 2, y, x + grid_size / 2, y + grid_size)
    c.line(x, y + grid_size / 2, x + grid_size, y + grid_size / 2)
    c.line(x, y, x + grid_size, y + grid_size)
    c.line(x + grid_size, y, x, y + grid_size)

    c.setDash([])


def calculate_grid_position(
    page_info: dict, args, page_height: float, row: int, col: int
) -> tuple[float, float]:
    x = page_info["page_margin"] + col * (args.grid + page_info["grid_spacing"])
    y = (
        page_height
        - page_info["page_margin"]
        - row * (args.grid + page_info["line_spacing"])
        - args.grid
    )
    return x, y


def draw_character(
    c: canvas.Canvas, font_name: str, args, x: float, y: float, character: str
):
    c.setFillColor(Color(0.5, 0.5, 0.5, args.font_opacity))
    c.setFont(font_name, args.font_size)

    text_width = c.stringWidth(character, font_name, args.font_size)
    text_x = x + (args.grid - text_width) / 2
    text_y = y + args.grid / 2 - args.font_size / 3
    c.drawString(text_x, text_y, character)


def draw_punctuation(
    c: canvas.Canvas,
    font_name: str,
    args,
    x: float,
    y: float,
    left_punct: str,
    right_punct: str,
):
    punct_size = args.font_size // 4
    c.setFont(font_name, punct_size)

    if left_punct:
        c.drawString(x + args.grid // 15, y + args.grid // 10, left_punct)

    if right_punct:
        c.drawString(x + args.grid * 8 // 10, y + args.grid // 10, right_punct)


def create_book(args):
    char_list = attach_punctuation(group_connect_punct(load_file(args.text_file)))
    number_of_characters = len(char_list)
    page_size = PAPER_SIZES[args.page]
    width, page_height = page_size

    page_info = calculate_page_dimensions(
        args, number_of_characters, width, page_height
    )

    output_file = getattr(args, "output", "book.pdf")
    if not output_file.endswith(".pdf"):
        output_file += ".pdf"

    try:
        c = create_pdf_canvas(output_file, page_size)
        font_name = setup_chinese_font(args.font)

        char_index = 0
        for page_num in range(page_info["number_of_pages"]):
            if page_num > 0:
                c.showPage()

            for row in range(page_info["rows_per_page"]):
                if char_index >= len(char_list):
                    break
                for col in range(page_info["cols_per_page"]):
                    x, y = calculate_grid_position(
                        page_info, args, page_height, row, col
                    )
                    draw_grid(c, x, y, args.grid)

                    if char_index >= len(char_list):
                        continue

                    character_data = char_list[char_index]
                    main_char, left_punct, right_punct = character_data

                    draw_character(c, font_name, args, x, y, main_char)
                    draw_punctuation(c, font_name, args, x, y, left_punct, right_punct)

                    char_index += 1

        c.save()
    except Exception as e:
        print(f"Error writing PDF file: {e}")
        exit(1)
