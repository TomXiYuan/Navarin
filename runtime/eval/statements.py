import logging
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from runtime.values import (
    RuntimeVal, 
    FuncVal, 
    BoolVal, 
    MK_NULL
)
from frontend.abstractSyntaxTree import (
    Program, 
    VarDecl, 
    FuncDecl, 
    ReturnStmt, 
    IfStmt, 
    WhileStmt, 
    BlockStmt
)
from runtime.environment import Environment

if TYPE_CHECKING:
    from runtime.interpreter import Interpreter

def evalProgram(program: Program, env: Environment, interpreter: Interpreter) -> RuntimeVal:
    lastEvaluated: RuntimeVal = MK_NULL()
    for stmt in program.body:
        lastEvaluated = interpreter.evaluate(stmt, env)
    return lastEvaluated

def evalVarDecl(varDecl: VarDecl, env: Environment, interpreter: Interpreter) -> RuntimeVal:
    value : RuntimeVal
    if varDecl.value:
        value = interpreter.evaluate(varDecl.value, env)
    else:
        value = MK_NULL()
    return env.declVar(varDecl.identifier, value, varDecl.constant)

def evalFuncDecl(funcDecl: FuncDecl, env: Environment, interpreter: Interpreter) -> RuntimeVal:
    funcVal = FuncVal(name=funcDecl.identifier, params = funcDecl.parameters, declEnv = env, body = funcDecl.body)
    return env.declVar(funcDecl.identifier, funcVal, False)

def evalReturnStmt(returnStmt: ReturnStmt, env: Environment, interpreter: Interpreter):
    value = MK_NULL()
    if returnStmt.value != None:
        value = interpreter.evaluate(returnStmt.value, env) 
    raise Return(value)

def evalIfStmt(ifStmt: IfStmt, env: Environment, interpreter: Interpreter) -> RuntimeVal:
    conditionVal = interpreter.evaluate(ifStmt.condition, env)
    # Condition must be a boolean type
    if not isinstance(conditionVal, BoolVal):
        logging.error(f"Expected boolean value in if condition, got {conditionVal}")
        sys.exit(1)

    if(conditionVal.value):
        interpreter.evaluate(ifStmt.thenBlock, env)
    else:
        interpreter.evaluate(ifStmt.elseBlock, env)

    return MK_NULL()

def evalWhileStmt(whileStmt: WhileStmt, env: Environment, interpreter: Interpreter) -> RuntimeVal:
    while True:
        conditionVal = interpreter.evaluate(whileStmt.condition, env)

        if not isinstance(conditionVal, BoolVal):
            logging.error(f"Expected boolean value in loop condition, got {conditionVal}")
            sys.exit(1)

        if not conditionVal.value:
            break

        try:
            interpreter.evaluate(whileStmt.body, env)
        except Break:
            return MK_NULL()

    return MK_NULL()

def evalBreakStmt():
    raise Break()

def evalBlockStmt(blockStmt: BlockStmt, env: Environment, interpreter: Interpreter) -> RuntimeVal:
    blockEnv = Environment(parent=env)
    for stmt in blockStmt.body:
        interpreter.evaluate(stmt, blockEnv)
    return MK_NULL()

@dataclass
class Return(Exception):
    value: RuntimeVal

@dataclass
class Break(Exception):
    pass