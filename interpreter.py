import copy
from typing import Self, cast

from ast_types import *

Env = dict[str]


class Closure(TypedDict):
    body: Term
    parameters: list[str]
    env: Env


Value = \
    ({'kind': "boolean", 'value': bool}
     | {'kind': "string", 'value': str}
     | {'kind': "number", 'value': int}
     | {'kind': "closure", 'value': Closure}
     | {'kind': "tuple", 'fst': Self, 'snd': Self})


def interpret_int(term: Int, env) -> dict:
    return {'kind': 'int', 'value': term['value']}


def interpret_str(term: Str, env) -> dict:
    return {'kind': 'string', 'value': term['value']}


def interpret_bool(term: Bool, env):
    return {'kind': 'boolean', 'value': term['value']}


def interpret_if(term: If, env):
    condition = interpret(term['condition'], env)
    return interpret(term['then'] if condition['value'] else term['otherwise'], env)


def interpret_tuple(term: Tuple, env):
    first = interpret(term['first'], env)
    second = interpret(term['second'], env)

    return {'kind': 'tuple', 'first': first, 'second': second}


def assert_tuple(term: Tuple):
    if term['kind'] != 'tuple':
        raise Exception("type error")


def interpret_first(term: First, env):
    tuple_value = interpret(term, env)
    assert_tuple(tuple_value)

    return cast(Tuple, tuple_value)['first']


def interpret_second(term, env):
    tuple_value = interpret(term, env)
    assert_tuple(tuple_value)

    return cast(Tuple, tuple_value)['second']


def convert_value_to_print(value: Value):
    if value['kind'] in ['boolean', 'string', 'number']:
        return str(value['value'])
    elif value['kind'] == 'closure':
        return "<#closure>"
    elif value['kind'] == 'tuple':
        return convert_value_to_print(value['first']) + ',' + convert_value_to_print(value['second'])


def interpret_print(term: Print, env):
    result = interpret(term['value'], env)
    print(convert_value_to_print(result))

    return result


def interpret_var(term: Var, env: dict):
    value = env.get(term['text'])

    if value is None:
        raise Exception('cannot find variable {}'.format(term['text']))

    return value


def interpret_let(term: Let, env: dict):
    new_env = copy.deepcopy(env)

    value = interpret(term['value'], new_env)

    new_env[term['name']['text']] = value

    return interpret(term['next'], new_env)


def interpret_call(term: Call, env: dict):
    func: Value = interpret(term['callee'], env)

    if func['kind'] != 'closure':
        raise Exception("type error: not closure")

    closure: Closure = func['value']

    if len(closure['parameters']) != len(term['arguments']):
        raise Exception("different args number")

    fun_env = copy.deepcopy(env)

    parameters = closure['parameters']

    for i in range(len(parameters)):
        fun_env[parameters[i]] = interpret(term['arguments'][i], env)

    return interpret(closure['body'], fun_env)


def interpret_binary_op(left: Value, right: Value, op: BinaryOp):
    binary_op_dict = {
        'Add': lambda l, r: l + r,
        'Sub': lambda l, r: l - r,
        'Mul': lambda l, r: l * r,
        'Div': lambda l, r: l / r,
        'Rem': lambda l, r: l % r,
        'Eq': lambda l, r: l == r,
        'Neq': lambda l, r: l != r,
        'Lt': lambda l, r: l < r,
        'Gt': lambda l, r: l > r,
        'Lte': lambda l, r: l <= r,
        'Gte': lambda l, r: l >= r,
        'And': lambda l, r: l and r,
        'Or': lambda l, r: l or r
    }

    operation = binary_op_dict[op]
    result = operation(left['value'], right['value'])

    if op in ['Eq', 'Neq', 'Lt', 'Gt', 'Lte', 'Gte', 'And', 'Or']:
        kind = 'boolean'
    elif op in ['Sub', 'Mul', 'Div', 'Rem']:
        kind = 'number'
    elif left['kind'] == 'number' and right['kind'] == 'number':
        kind = 'number'
    else:
        kind = 'string'

    return {
        'kind': kind,
        'value': result
    }


def interpret_binary(term: Binary, env: dict):
    left = interpret(term['lhs'], env)
    right = interpret(term['rhs'], env)

    return interpret_binary_op(left, right, term['op'])


def interpret_function(term: Function, env: dict):
    return {
        'kind': 'closure',
        'value': {'body': term['value'], 'env': env, 'parameters': list(map(lambda x: x['text'], term['parameters']))}
    }


def interpret(term: Term, env: Env):
    interpreter_dict = {
        'Int': interpret_int,
        'Str': interpret_str,
        'Call': interpret_call,
        'Binary': interpret_binary,
        'Function': interpret_function,
        'Let': interpret_let,
        'If': interpret_if,
        'Print': interpret_print,
        'First': interpret_first,
        'Second': interpret_second,
        'Bool': interpret_bool,
        'Tuple': interpret_tuple,
        'Var': interpret_var
    }

    kind = term['kind']

    return interpreter_dict[kind](term, env)


class Interpreter:
    def __init__(self, json_data):
        self.file: File = json_data

    def run(self):
        interpret(self.file['expression'], {})
