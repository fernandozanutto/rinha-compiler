from typing import TypedDict, Literal


class Term(TypedDict):
    kind: Literal[
        'Int',
        'Str',
        'Call',
        'Binary',
        'Function',
        'Let',
        'If',
        'Print',
        'First',
        'Second',
        'Bool',
        'Tuple',
        'Var'
    ]


class Loc(TypedDict):
    start: int
    end: int
    filename: str


class Parameter(TypedDict):
    text: str
    location: Loc


class File(TypedDict):
    name: str
    expression: Term
    location: Loc


class If(Term):
    condition: Term
    then: Term
    otherwise: Term
    location: Loc


class Let(Term):
    name: Parameter
    value: Term
    next: Term
    location: Loc


class Str(Term):
    value: str
    location: Loc


class Bool(Term):
    value: bool
    location: Loc


class Int(Term):
    value: int
    location: Loc


BinaryOp = Literal[
    'Add', 'Sub', 'Mul', 'Div', 'Rem', 'Eq', 'Neq', 'Lt', 'Gt', 'Lte', 'Gte', 'And', 'Or'
]


class Binary(Term):
    lhs: Term
    op: BinaryOp
    rhs: Term
    location: Loc


class Call(Term):
    callee: Term
    arguments: list[Term]
    location: Loc


class Function(Term):
    parameters: list[Parameter]
    value: Term
    location: Loc


class Print(Term):
    value: Term
    location: Loc


class First(Term):
    value: Term
    location: Loc


class Second(First):
    pass


class Tuple(Term):
    first: Term
    second: Term
    location: Loc


class Var(Term):
    text: str
    location: Loc
