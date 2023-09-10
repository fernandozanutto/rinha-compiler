import copy
from typing import cast

from ast_types import *

Env = dict[str]


class Closure(TypedDict):
    body: Term
    parameters: list[str]
    env: Env


class BaseValue(TypedDict):
    kind: str


class StringValue(BaseValue):
    value: str


class BooleanValue(BaseValue):
    value: bool


class IntValue(BaseValue):
    value: int


class ClosureValue(BaseValue):
    value: Closure


class TupleValue(BaseValue):
    first: BaseValue
    second: BaseValue


Value = TupleValue | ClosureValue | BooleanValue | IntValue | StringValue


def interpret_int(term: Int, _) -> IntValue:
    return {'kind': 'int', 'value': term['value']}


def interpret_str(term: Str, _) -> StringValue:
    return {'kind': 'string', 'value': term['value']}


def interpret_bool(term: Bool, _) -> BooleanValue:
    return {'kind': 'boolean', 'value': term['value']}


def interpret_if(term: If, env: Env) -> Value:
    condition = interpret(term['condition'], env)
    return interpret(term['then'] if condition['value'] else term['otherwise'], env)


def interpret_tuple(term: Tuple, env: Env) -> TupleValue:
    first = interpret(term['first'], env)
    second = interpret(term['second'], env)

    return {'kind': 'tuple', 'first': first, 'second': second}


def assert_tuple(term: TupleValue):
    if term['kind'] != 'tuple':
        raise RuntimeError("term is not a tuple: {}".format(term))


def interpret_first(term: First, env: Env) -> Value:
    tuple_value = interpret(term, env)
    assert_tuple(tuple_value)

    return cast(Value, cast(TupleValue, tuple_value)['first'])


def interpret_second(term: Second, env: Env) -> Value:
    tuple_value = interpret(term, env)
    assert_tuple(tuple_value)

    return cast(Value, cast(TupleValue, tuple_value)['second'])


def convert_value_to_print(value: Value) -> str:
    if value['kind'] == 'boolean':
        return 'true' if value['value'] else 'false'

    elif value['kind'] in ['string', 'int']:
        return str(value['value'])

    elif value['kind'] == 'closure':
        return "<#closure>"

    elif value['kind'] == 'tuple':
        first_value = cast(Value, value['first'])
        second_value = cast(Value, value['second'])
        return "({}, {})".format(convert_value_to_print(first_value), convert_value_to_print(second_value))


def interpret_print(term: Print, env: Env) -> Value:
    result = interpret(term['value'], env)
    print(convert_value_to_print(result))

    return result


def interpret_var(term: Var, env: Env) -> Value:
    value = env.get(term['text'])

    if value is None:
        raise Exception('cannot find variable {}'.format(term['text']))

    return value


def interpret_let(term: Let, env: Env) -> Value:
    new_env = copy.deepcopy(env)

    value = interpret(term['value'], new_env)

    new_env[term['name']['text']] = value

    return interpret(term['next'], new_env)


def assert_closure(value: Value) -> Closure:
    if value['kind'] != 'closure':
        raise Exception("type error: not closure")

    return cast(Closure, value['value'])


def interpret_call(term: Call, env: Env) -> Value:
    func = interpret(term['callee'], env)

    closure = assert_closure(func)

    if len(closure['parameters']) != len(term['arguments']):
        raise Exception("different args number")

    fun_env = copy.deepcopy(env)

    parameters = closure['parameters']

    for i in range(len(parameters)):
        fun_env[parameters[i]] = interpret(term['arguments'][i], env)

    return interpret(closure['body'], fun_env)


def add_values(left: Value, right: Value) -> Value:
    if left['kind'] in ['closure', 'tuple', 'boolean'] or right['kind'] in ['closure', 'tuple', 'boolean']:
        raise RuntimeError("Cannot ADD types {} and {}".format(left['kind'], right['kind']))

    if left['kind'] == 'string' and right['kind'] == 'string':
        return {'kind': 'string', 'value': left['value'] + right['value']}

    elif left['kind'] == 'int' and right['kind'] == 'int':
        return {'kind': 'int', 'value': left['value'] + right['value']}

    else:
        return {'kind': 'string', 'value': str(left['value']) + str(right['value'])}


binary_op_dict = {
    'Sub': lambda l, r: l - r,
    'Mul': lambda l, r: l * r,
    'Div': lambda l, r: l // r,
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


def interpret_binary_op(left: Value, right: Value, op: BinaryOp) -> Value:
    if op == 'Add':
        return add_values(left, right)

    if op != 'Add' and left['kind'] != right['kind']:
        raise RuntimeError(
            "Invalid operator {} for arguments with types {} and {}".format(op, left['kind'], right['kind']))

    if op in ['Sub', 'Mul', 'Div', 'Rem'] and left['kind'] != 'int':
        raise RuntimeError(
            "Invalid operator {} for arguments with types {} and {}".format(op, left['kind'], right['kind']))

    if op in ['Eq', 'Neq'] and left['kind'] not in ['string', 'int']:
        raise RuntimeError(
            "Invalid operator {} for arguments with types {} and {}".format(op, left['kind'], right['kind']))

    if op in ['Lt', 'Gt', 'Lte', 'Gte'] and left['kind'] != 'int':
        raise RuntimeError(
            "Invalid operator {} for arguments with types {} and {}".format(op, left['kind'], right['kind']))

    if op in ['And', 'Or'] and left['kind'] != 'boolean':
        raise RuntimeError(
            "Invalid operator {} for arguments with types {} and {}".format(op, left['kind'], right['kind']))

    operation = binary_op_dict[op]
    result = operation(left['value'], right['value'])

    kind = ''
    if op in ['Eq', 'Neq', 'Lt', 'Gt', 'Lte', 'Gte', 'And', 'Or']:
        kind = 'boolean'
    elif op in ['Sub', 'Mul', 'Div', 'Rem']:
        kind = 'int'

    return {
        'kind': kind,
        'value': result
    }


def interpret_binary(term: Binary, env: Env) -> Value:
    left = interpret(term['lhs'], env)
    right = interpret(term['rhs'], env)

    return interpret_binary_op(left, right, term['op'])


def interpret_function(term: Function, env: Env) -> Value:
    return {
        'kind': 'closure',
        'value': {'body': term['value'], 'env': env, 'parameters': list(map(lambda x: x['text'], term['parameters']))}
    }


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


def interpret(term: Term, env: Env) -> Value:
    kind = term['kind']
    return interpreter_dict[kind](term, env)


class Interpreter:
    def __init__(self, json_data):
        self.file: File = json_data

    def run(self):
        return interpret(self.file['expression'], {})
