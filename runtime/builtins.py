from runtime.values import RuntimeVal, MK_NATIVE_FUNC, MK_NULL
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from runtime.environment import Environment

def nativePrint(args: list[RuntimeVal], env: 'Environment') -> RuntimeVal:
    for arg in args:
        print(f"{arg}", end="")
    return MK_NULL()

def nativePrintln(args: list[RuntimeVal], env: 'Environment') -> RuntimeVal:
    for arg in args:
        print(f"{arg}")
    return MK_NULL()

def setupGlobalEnv(env: 'Environment') -> None:
    env.declVar("print", MK_NATIVE_FUNC("print", nativePrint), constant=True)
    env.declVar("println", MK_NATIVE_FUNC("println", nativePrintln), constant=True)