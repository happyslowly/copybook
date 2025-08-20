from copybook.arguments import PAPER_SIZES, parse_arguments
from copybook.book import create_book


def main():
    args = parse_arguments()
    create_book(args, PAPER_SIZES)


if __name__ == "__main__":
    main()

