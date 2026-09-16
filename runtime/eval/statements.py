from runtime.values import RuntimeVal, MK_NULL, FuncVal, BoolVal
import runtime.interpreter as interpreter
from frontend.abstractSyntaxTree import Program, VarDecl, FuncDecl, ReturnStmt, IfStmt, WhileStmt, BreakStmt
from runtime.environment import Environment
from dataclasses import dataclass
from typing import cast
import logging
import sys

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
    func = FuncVal(name=funcDecl.identifier, parameters = funcDecl.parameters, declarationEnv = env, body = funcDecl.body)
    return env.declVar(funcDecl.identifier, func, False)

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
        for stmt in ifStmt.thenBlock:
            interpreter.evaluate(stmt, ifEnv)
    else:
        for stmt in ifStmt.elseBlock:
            interpreter.evaluate(stmt, ifEnv)

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
            for stmt in whileStmt.body:
                interpreter.evaluate(stmt, whileEnv)
        except Break:
            return MK_NULL()

    return MK_NULL()

def evalBreakStmt(breakStmt: BreakStmt, env: Environment):
    raise Break()

@dataclass
class Return(Exception):
    Value: RuntimeVal

@dataclass
class Break(Exception):
    pass

