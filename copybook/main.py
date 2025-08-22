from copybook.arguments import parse_arguments
from copybook.book import create_book


def main():
    args = parse_arguments()
    create_book(args)


if __name__ == "__main__":
    main()
