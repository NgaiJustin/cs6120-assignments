"""
Bril type definitions.

Constructed based on Bril syntax specified here
https://capra.cs.cornell.edu/bril/lang/syntax.html
"""

from typing import TypedDict, Union

Type = Union[None, str, dict[str, "Type"]]
Literal = Union[bool, int]


class Instruction(TypedDict, total=False):
    op: str
    dest: str
    type: Type
    args: list[str]
    funcs: list[str]
    label: str  # for labels
    labels: list[str]  # for jmp and br
    value: Literal


class Argument(TypedDict):
    name: str
    type: Type


class Function(TypedDict, total=False):
    name: str
    args: list[Argument]
    type: Type
    instrs: list[Instruction]


class Program(TypedDict):
    functions: list[Function]
