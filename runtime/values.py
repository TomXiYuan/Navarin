from typing import Protocol, Literal
from dataclasses import dataclass

ValueType = Literal["null", "number", "boolean"]

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