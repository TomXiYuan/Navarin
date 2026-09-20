import logging
import sys
from dataclasses import dataclass

from runtime.values import RuntimeVal, FuncVal, BoolVal, MK_NULL
import runtime.interpreter as interpreter
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

def evalProgram(program: Program, env: Environment) -> RuntimeVal:
    lastEvaluated: RuntimeVal = MK_NULL()
    for stmt in program.body:
        lastEvaluated = interpreter.evaluate(stmt, env)
    return lastEvaluated

def evalVarDecl(varDecl: VarDecl, env: Environment) -> RuntimeVal:
    value : RuntimeVal
    if varDecl.value:
        value = interpreter.evaluate(varDecl.value, env)
    else:
        value = MK_NULL()
    
    return env.declVar(varDecl.identifier, value, varDecl.constant)

def evalFuncDecl(funcDecl: FuncDecl, env: Environment) -> RuntimeVal:
    funcVal = FuncVal(name=funcDecl.identifier, params = funcDecl.parameters, declEnv = env, body = funcDecl.body)
    return env.declVar(funcDecl.identifier, funcVal, False)

def evalReturnStmt(returnStmt: ReturnStmt, env: Environment):
    value = MK_NULL()
    if returnStmt.value != None:
        value = interpreter.evaluate(returnStmt.value, env) 
    raise Return(value)

def evalIfStmt(ifStmt: IfStmt, env: Environment) -> RuntimeVal:
    conditionVal = interpreter.evaluate(ifStmt.condition, env)
    # Condition must be a boolean type
    if not isinstance(conditionVal, BoolVal):
        logging.error(f"Expected boolean value in if condition, got {conditionVal}")
        sys.exit(1)

    ifEnv = Environment(env)
    if(conditionVal.value):
        interpreter.evaluate(ifStmt.thenBlock, ifEnv)
    else:
        interpreter.evaluate(ifStmt.elseBlock, ifEnv)

    return MK_NULL()

def evalWhileStmt(whileStmt: WhileStmt, env: Environment) -> RuntimeVal:
    whileEnv = Environment(env)
    while True:
        conditionVal = interpreter.evaluate(whileStmt.condition, whileEnv)

        if not isinstance(conditionVal, BoolVal):
            logging.error(f"Expected boolean value in loop condition, got {conditionVal}")
            sys.exit(1)

        if not conditionVal.value:
            break

        try:
            interpreter.evaluate(whileStmt.body, whileEnv)
        except Break:
            return MK_NULL()

    return MK_NULL()

def evalBreakStmt():
    raise Break()

def evalBlockStmt(blockStmt: BlockStmt, env: Environment) -> RuntimeVal:
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