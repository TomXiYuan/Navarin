from frontend.abstractSyntaxTree import Stmt
from dataclasses import dataclass
from typing import Protocol, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.environment import Environment

ValueType = Literal["null", "number", "boolean", "function"]

class RuntimeVal(Protocol):
    type : ValueType

@dataclass
class NullVal(RuntimeVal):
    value: str = "null"
    type: ValueType = "null"

def MK_NULL() -> NullVal:
    return NullVal(type = "null", value = "null")

@dataclass
class NumberVal(RuntimeVal):
    value: int | float
    type: ValueType = "number"

def MK_NUMBER(value: int | float) -> NumberVal:
    return NumberVal(type = "number", value = value)

@dataclass
class BoolVal(RuntimeVal):
    value: bool
    type: ValueType = "boolean"

def MK_BOOL(value : bool) -> BoolVal:
    return BoolVal(type = "boolean", value = value)

@dataclass
class FuncVal(RuntimeVal):
    name: str
    parameters: list[str]
    declarationEnv: Environment
    body: list[Stmt]
    type: ValueType = "function"