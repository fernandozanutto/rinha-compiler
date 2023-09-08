import json

from interpreter import Interpreter


def get_json_from_file(path: str):
    with open(path, 'r') as file:
        return json.load(file)


def run_test(file_path: str, expected_string: str):
    json_value = get_json_from_file(file_path)

    result = Interpreter(json_value).run()['value']
    success = str(result) == expected_string

    if success:
        print("Success running {} with result {}".format(file_path, expected_string))
    else:
        print("Fail running {} with result {} - expected {}".format(file_path, result, expected_string))


if __name__ == '__main__':
    run_test('./files/combination.json', '45')
    run_test('./files/fib.json', '55')
    run_test('./files/sum.json', '15')
