import argparse
import json
from interpreter import Interpreter


def main():
    parser = argparse.ArgumentParser(description='Rinha interpreter made with Python.')
    parser.add_argument('json_path',
                        metavar='json_path',
                        type=str,
                        help='path to json AST')

    args = parser.parse_args()

    with open(args.json_path, 'r') as file:
        decoded_json = json.load(file)

        Interpreter(decoded_json).run()


if __name__ == '__main__':
    main()
