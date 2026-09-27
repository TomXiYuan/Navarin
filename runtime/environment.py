from typing import TYPE_CHECKING
from runtime.builtins import setupGlobalEnv

if TYPE_CHECKING:
    from runtime.values import RuntimeVal

class Environment:
    parent : Environment | None
    variables : dict[str, RuntimeVal]
    constants : set[str]

    def __init__(self, parent: Environment | None):
        self.parent = parent
        self.variables = {}
        self.constants = set()

        if parent == None:
            setupGlobalEnv(self)

    def declVar(self, varName: str, value: RuntimeVal, constant: bool) -> RuntimeVal:
        if (self.variables.get(varName)):
            raise Exception(f"Variable {varName} already declared in this scope")

        self.variables[varName] = value

        if constant:
            self.constants.add(varName)

        return value

    def ancestor(self, distance: int) -> 'Environment':
        env: Environment = self
        for _ in range(distance):
            if env.parent is None:
                raise Exception(
                    f"Resolver/interpreter scope mismatch: tried to walk {distance} "
                    f"scopes up, but ran out of parent environments early."
                )
            env = env.parent
        return env

    def getAt(self, distance: int, name: str) -> 'RuntimeVal':
        return self.ancestor(distance).variables[name]

    def assignAt(self, distance: int, name: str, value: 'RuntimeVal'):
        self.ancestor(distance).variables[name] = value

    def getVar(self, name: str) -> RuntimeVal:
        return self.variables[name]

    def assignVar(self, name: str, value: RuntimeVal):
        self.variables[name] = value

    # def assignVar(self, varName: str, value: RuntimeVal) -> RuntimeVal:
    #     env = self.resolve(varName)
    #     if varName in env.constants:
    #         raise Exception(f"Cannot reassign variable {varName} as it was declared constant.")
    #     env.variables[varName] = value
    #     return value

    # def lookupVar(self, varName: str) -> RuntimeVal:
    #     env = self.resolve(varName)
    #     return env.variables[varName]

    # def resolve(self, varName: str) -> Environment:
    #     if self.variables.get(varName):
    #         return self

    #     if self.parent == None:
    #         raise Exception(f"Cannot resolve variable {varName} as it does not exist")

    #     return self.parent.resolve(varName)