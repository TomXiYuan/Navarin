from frontend.abstractSyntaxTree import BlockStmt
from dataclasses import dataclass
from typing import Callable, Protocol, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    from runtime.environment import Environment

class ValueType(Enum):
    NUMBER_VAL = auto()
    BOOLEAN_VAL = auto()
    NULL_VAL = auto()
    FUNCTION_VAL = auto()
    NATIVE_FUNCTION_VAL = auto()

class RuntimeVal(Protocol):
    type : ValueType

@dataclass
class NullVal(RuntimeVal):
    value: None
    type: ValueType = ValueType.NULL_VAL

    def __str__(self):
        return "null"

    def __repr__(self):
        return "<NullVal>"

def MK_NULL() -> NullVal:
    return NullVal(type = ValueType.NULL_VAL, value = None)

@dataclass
class IntVal(RuntimeVal):
    value: int
    type: ValueType = ValueType.NUMBER_VAL

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"<IntVal: {self.value}>"

@dataclass
class FloatVal(RuntimeVal):
    value: float
    type: ValueType = ValueType.NUMBER_VAL

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"<FloatVal: {self.value}>"

def MK_NUMBER(value: int | float) -> IntVal | FloatVal:
    if isinstance(value, int):
        return IntVal(value=value)
    return FloatVal(value=value)

@dataclass
class BoolVal(RuntimeVal):
    value: bool
    type: ValueType = ValueType.BOOLEAN_VAL

    def __str__(self):
        return str(self.value).lower()

    def __repr__(self):
        return f"<BoolVal: {self.value}>"

def MK_BOOL(value : bool) -> BoolVal:
    return BoolVal(type=ValueType.BOOLEAN_VAL, value=value)

@dataclass
class FuncVal(RuntimeVal):
    name: str
    params: list[str]
    declEnv:'Environment'
    body: BlockStmt
    type: ValueType = ValueType.FUNCTION_VAL

    def __str__(self):
        params = ", ".join(self.params)
        return f"fn {self.name}({params}) {{ ... }}"

    def __repr__(self):
        return f"<FuncVal> {self.name}"

def MK_FUNC(name:str, params: list[str], declEnv: 'Environment', body: BlockStmt):
    return FuncVal(
        type=ValueType.FUNCTION_VAL, 
        name=name,
        params=params, 
        declEnv=declEnv, 
        body=body
    )

@dataclass
class NativeFuncVal(RuntimeVal):
    name: str
    call: Callable[[list['RuntimeVal'], 'Environment'], 'RuntimeVal']
    type: ValueType = ValueType.NATIVE_FUNCTION_VAL

    def __str__(self):
        return f"<native fn {self.name}>"

    def __repr__(self):
        return f"<NativeFuncVal> {self.name}"
    
NativeCallable = Callable[[list['RuntimeVal'], 'Environment'], 'RuntimeVal']
def MK_NATIVE_FUNC(name: str, call: NativeCallable) -> NativeFuncVal:
    return NativeFuncVal(
        type=ValueType.NATIVE_FUNCTION_VAL,
        name=name,
        call=call,
    )