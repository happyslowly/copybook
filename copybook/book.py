import os

from jinja2 import Environment, FileSystemLoader

PUNCT_POSITION = {
    "left": ["‘", "“", "「", "『", "（", "〔", "【", "《"],
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
        "…",
        "—",
        "–",
        "～",
    ],
}

CONNECTED_PUNCT = ["—", "…", "～"]


def load_file(text_file: str) -> list[str]:
    char_list = []
    try:
        with open(text_file, "r", encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                char_list.extend([c for c in list(line) if c])
    except FileNotFoundError:
        print(f"Error: File '{text_file}' not found.")
        exit(1)
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
        if char not in punct_rules:
            result.append([char, None, None])
            continue
        position = punct_rules[char]
        if position == "left" and i + 1 < len(char_list):
            next_char = char_list[i + 1]
            result.append([next_char, char, None])
            char_list[i + 1] = None
        if position == "right" and result:
            result[-1][2] = char
    return result


def load_template():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(module_dir, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    return env.get_template("standard.j2")


def calculate_page_dimensions(args, number_of_characters, page_height):
    page_margin = args.page_margin
    grid_spacing = args.grid_spacing
    line_spacing = args.line_spacing

    available_width = args.width - 2 * page_margin
    available_height = page_height - 2 * page_margin
    cols_per_page = available_width // (args.grid + grid_spacing)
    rows_per_page = available_height // (args.grid + line_spacing)
    characters_per_page = cols_per_page * rows_per_page
    number_of_pages = 1 + (number_of_characters - 1) // characters_per_page

    return {
        "cols_per_page": cols_per_page,
        "rows_per_page": rows_per_page,
        "characters_per_page": characters_per_page,
        "number_of_pages": number_of_pages,
        "page_margin": page_margin,
        "grid_spacing": grid_spacing,
        "line_spacing": line_spacing,
    }


def generate_y_positions(
    page_height, number_of_pages, rows_per_page, page_margin, grid, line_spacing
):
    y_positions = []
    for page_num in range(number_of_pages):
        page_offset = page_num * page_height
        for row in range(rows_per_page):
            y = page_offset + page_margin + row * (grid + line_spacing)
            y_positions.append(y)
    return y_positions


def create_book(args, paper_sizes):
    char_list = attach_punctuation(group_connect_punct(load_file(args.text_file)))
    print(char_list)
    number_of_characters = len(char_list)
    width, page_height = paper_sizes[args.page]

    # Add width to args for calculation
    args.width = width

    # Calculate page dimensions
    page_info = calculate_page_dimensions(args, number_of_characters, page_height)

    # Generate y positions
    y_positions = generate_y_positions(
        page_height,
        page_info["number_of_pages"],
        page_info["rows_per_page"],
        page_info["page_margin"],
        args.grid,
        page_info["line_spacing"],
    )

    # Calculate x positions
    x_positions = [
        page_info["page_margin"] + col * (args.grid + page_info["grid_spacing"])
        for col in range(page_info["cols_per_page"])
    ]

    height = page_info["number_of_pages"] * page_height

    data = {
        "width": width,
        "height": height,
        "grid": args.grid,
        "x_positions": x_positions,
        "y_positions": y_positions,
        "text_list": char_list,
        "font": args.font,
        "font_size": args.font_size,
        "font_color": args.font_color,
        "font_opacity": args.font_opacity,
    }

    try:
        with open("book.svg", "w", encoding="utf-8") as fout:
            fout.write(load_template().render(data))
    except Exception as e:
        print(f"Error writing SVG file: {e}")
        exit(1)
