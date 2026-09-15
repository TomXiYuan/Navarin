from runtime.values import RuntimeVal, MK_NULL, FuncVal, BoolVal
import runtime.interpreter as interpreter
from frontend.abstractSyntaxTree import Program, VarDecl, FuncDecl, ReturnStmt, IfStmt
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
    val = interpreter.evaluate(ifStmt.condition, env)
    if not isinstance(val, BoolVal):
        logging.error(f"Expected boolean value, got {val}")
        sys.exit(1)

    boolVal = cast(BoolVal, val)
    ifEnv = Environment(env)

    if(boolVal.value):
        for stmt in ifStmt.thenBlock:
            interpreter.evaluate(stmt, ifEnv)
    else:
        for stmt in ifStmt.elseBlock:
            interpreter.evaluate(stmt, ifEnv)

    return MK_NULL()


@dataclass
class Return(Exception):
    Value: RuntimeVal



