from runtime.values import MK_NULL, MK_BOOL, MK_NUMBER
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.values import RuntimeVal

class Environment:
    parent : Environment | None
    variables : dict[str, RuntimeVal]
    constants : set[str]

    def __init__(self, parent: Environment | None):
        isGlobal = parent is None
        self.parent = parent
        self.variables = {}
        self.constants = set()

    def declVar(self, varName: str, value: RuntimeVal, constant: bool) -> RuntimeVal:
        if (self.variables.get(varName)):
            raise Exception(f"Variable {varName} already declared in this scope")

        self.variables[varName] = value

        if constant:
            self.constants.add(varName)

        return value

    def assignVar(self, varName: str, value: RuntimeVal) -> RuntimeVal:
        env = self.resolve(varName)
        if varName in env.constants:
            raise Exception(f"Cannot reassign variable {varName} as it was declared constant.")
        env.variables[varName] = value
        return value

    def lookupVar(self, varName: str) -> RuntimeVal:
        env = self.resolve(varName)
        return env.variables[varName]

    def resolve(self, varName: str) -> Environment:
        if self.variables.get(varName):
            return self

        if self.parent == None:
            raise Exception(f"Cannot resolve variable {varName} as it does not exist")

        return self.parent.resolve(varName)