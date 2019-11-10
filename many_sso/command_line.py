from argparse import ArgumentParser
from .hello import hello


def build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('--message', '-m', type=str, default='hello world')
    parser.add_argument('--count', '-c', type=int, default=1)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    hello(message=args.message, count=args.count)
