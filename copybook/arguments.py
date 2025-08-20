import argparse

PAPER_SIZES = {
    "a4": (794, 1123),
    "letter": (816, 1056),
    "legal": (816, 1344),
}


def parse_arguments():
    parser = argparse.ArgumentParser(description="Simple chinese copybook generator")
    parser.add_argument(
        "-p",
        "--page",
        type=str,
        default="letter",
        choices=["a4", "letter", "legal"],
        help="copybook page size",
    )
    parser.add_argument(
        "-g", "--grid", type=int, default=80, help="grid size of each character"
    )

    parser.add_argument(
        "--page-margin",
        type=int,
        default=20,
        help="Page margins (top/bottom/left/right)",
    )
    parser.add_argument(
        "--grid-spacing", type=int, default=5, help="Spacing between grids"
    )
    parser.add_argument(
        "--line-spacing", type=int, default=10, help="Extra spacing between lines"
    )
    parser.add_argument(
        "-m", "--margin", type=int, default=10, help="margin size between each grid"
    )
    parser.add_argument(
        "--font",
        type=str,
        default="TianYingZhangKaiShu",
        help="Font family for characters",
    )
    parser.add_argument(
        "--font-size", type=int, default=60, help="Font size for characters in pixels"
    )
    parser.add_argument(
        "--font-color",
        type=str,
        default="gray",
        help="Font color (default: %(default)s). Examples: red, blue, #FF0000, rgb(255,0,0)",
    )
    parser.add_argument(
        "--font-opacity",
        type=float,
        default=0.8,
        help="Font opacity/transparency (0.0-1.0, default: %(default)s). 0.0=transparent, 1.0=opaque",
    )
    parser.add_argument(
        "text_file",
        metavar="TEXT_FILE",
        help="Path to source file containing Chinese characters to practice",
    )
    parser.add_argument(
        "--include-punctuation",
        action="store_true",
        help="Include punctuation marks",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.grid <= 0:
        parser.error("Grid size must be positive")
    if args.page_margin < 0:
        parser.error("Page margin cannot be negative")
    if args.grid_spacing < 0:
        parser.error("Grid spacing cannot be negative")
    if args.line_spacing < 0:
        parser.error("Line spacing cannot be negative")
    if args.font_size <= 0:
        parser.error("Font size must be positive")
    if not 0.0 <= args.font_opacity <= 1.0:
        parser.error("Font opacity must be between 0.0 and 1.0")

    return args

