import argparse

from moneypype.etl import run, _default_source


def main() -> None:
    parser = argparse.ArgumentParser(description="moneypype CLI")
    parser.add_argument(
        "source", help="input file name", default=_default_source(), nargs="?"
    )

    args = parser.parse_args()

    data = run(args.source)
    print(data)
