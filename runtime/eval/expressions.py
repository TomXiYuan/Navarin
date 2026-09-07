from runtime.values import RuntimeVal, NumberVal, FunctionValue, MK_NUMBER, MK_NULL
from frontend.abstractSyntaxTree import Expr, BinaryExpr, Identifier, AssignmentExpr, FuncCallExpr
import runtime.interpreter as interpreter
from runtime.environment import Environment
from typing import cast
import logging
import sys

def evalBinaryExpr(binop: BinaryExpr, env: Environment) -> RuntimeVal:
    leftHand = interpreter.evaluate(binop.left, env)
    rightHand = interpreter.evaluate(binop.right, env)

    if leftHand.type == "number" and rightHand.type == "number":
        return evalNumericBinaryExpr(cast(NumberVal, leftHand), cast(NumberVal, rightHand), binop.operator)

    return MK_NULL()

def evalNumericBinaryExpr(leftHand: NumberVal, rightHand: NumberVal, operator: str) -> NumberVal:
    result = 0
    if operator == "+":
        result = leftHand.value + rightHand.value
    elif operator == "-":
        result = leftHand.value - rightHand.value
    elif operator == "*":
        result = leftHand.value * rightHand.value
    elif operator == "/":
        # TODO: Division by zero check
        result = leftHand.value / rightHand.value
    elif operator == "%":
        result = leftHand.value % rightHand.value

    return MK_NUMBER(result)

def evalAssignmentExpr(node: AssignmentExpr, env : Environment) -> RuntimeVal:
    if node.assigne.type != "Identifier":
        raise Exception(f"Invalid LHS inside assignment expression: {node.assigne}")

    varName = cast(Identifier, node.assigne).symbol
    return env.assignVar(varName, interpreter.evaluate(node.value, env))

def evalIdentifier(identifier: Identifier, env: Environment) -> RuntimeVal:
    val = env.lookupVar(identifier.symbol)
    return val

def evalFuncCallExpr(funcCall: FuncCallExpr, env: Environment) -> RuntimeVal:
    funcVal = cast(FunctionValue, env.lookupVar(cast(Identifier, funcCall.caller).symbol))
    funcEnv = Environment(env)

    parameters = funcVal.parameters
    if len(funcCall.args) != len(parameters):
        logging.error(
            f"Function expected {len(parameters)} argument(s), got {len(funcCall.args)}."
        )
        sys.exit(1)
    
    for i in range(len(parameters)):
        parameterName: str = parameters[i]
        parameterArg: Expr = funcCall.args[i]
        funcEnv.declareVar(parameterName, interpreter.evaluate(parameterArg, env), False)

    result: RuntimeVal = funcVal

    for stmt in funcVal.body:
        if stmt.type == "ReturnStmt":
            return interpreter.evaluate(stmt, funcEnv)
        result = interpreter.evaluate(stmt, funcEnv)

    return result