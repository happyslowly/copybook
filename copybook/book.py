import os

from jinja2 import Environment, FileSystemLoader


def load_template():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(module_dir, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    return env.get_template("standard.j2")


def load_file(text_file: str, include_punctuation: bool) -> list[str]:
    def is_chinese_char(char):
        return "\u4e00" <= char <= "\u9fff"

    text_list = []
    try:
        with open(text_file, "r", encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                text_list.extend(
                    [
                        c
                        for c in list(line)
                        if c and (is_chinese_char(c) or include_punctuation)
                    ]
                )
    except FileNotFoundError:
        print(f"Error: File '{text_file}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error reading file '{text_file}': {e}")
        exit(1)
    return text_list


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
    text_list = load_file(args.text_file, args.include_punctuation)
    number_of_characters = len(text_list)
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
        "text_list": text_list,
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
