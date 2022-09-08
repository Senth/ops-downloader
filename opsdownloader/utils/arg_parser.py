import argparse


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints out helpful messages.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Turn on debug messages. This automatically turns on --verbose as well.",
    )

    return parser.parse_args()
