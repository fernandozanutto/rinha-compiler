import json
import argparse


def main():
    parser = argparse.ArgumentParser(description='Rinha interpreter made with Python.')
    parser.add_argument('json_path',
                        metavar='json_path',
                        type=str,
                        help='path to json AST')

    args = parser.parse_args()

    print(f'Hi, {args.json_path}')


if __name__ == '__main__':
    main()
