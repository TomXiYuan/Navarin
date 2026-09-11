from runtime.values import RuntimeVal, NumberVal, FuncVal, BoolVal, MK_NUMBER, MK_NULL, MK_BOOL
from frontend.abstractSyntaxTree import NodeType, BinaryExpr, Identifier, AssignmentExpr, FuncCallExpr, UnaryExpr
from runtime.eval.statements import Return
import runtime.interpreter as interpreter
from runtime.environment import Environment
from typing import cast
import logging
import sys
import operator as op
import copy

NUMERIC_OPS = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
    "%": op.mod,
}

COMPARISON_OPS = {
    "<": op.lt,
    ">": op.gt,
    "<=": op.le,
    ">=": op.ge,
    "==": op.eq,
}

LOGICAL_OPS = {"&&", "||"}
UNARY_NUMERIC_OPS = {"++", "--"}

def evalBinaryExpr(expr: BinaryExpr, env: Environment) -> RuntimeVal:
    operator = expr.operator

    # Short circuit
    if operator in LOGICAL_OPS:
        return evalLogicalBinaryExpr(expr, env)

    leftHand = interpreter.evaluate(expr.left, env)
    rightHand = interpreter.evaluate(expr.right, env)

    if operator in NUMERIC_OPS:
        return evalNumericBinaryExpr(cast(NumberVal, leftHand), cast(NumberVal, rightHand), operator)

    elif operator in COMPARISON_OPS:
        return evalComparisonExpr(cast(NumberVal, leftHand), cast(NumberVal, rightHand), operator)

    logging.error(f"Unknown operator: {operator}")
    sys.exit(1)

def evalLogicalBinaryExpr(binop: BinaryExpr, env: Environment) -> BoolVal:
    left = interpreter.evaluate(binop.left, env)

    if not isinstance(left, BoolVal):
        logging.error(f"Left-hand side of '{binop.operator}' must be a boolean, got {left.type}")
        sys.exit(1)

    if binop.operator == "&&":
        if not left.value:
            return MK_BOOL(False)

        right = interpreter.evaluate(binop.right, env)
        if not isinstance(right, BoolVal):
            logging.error(f"Right-hand side of '{binop.operator}' must be a boolean, got {right.type}")
            sys.exit(1)
        return MK_BOOL(right.value)

    if binop.operator == "||":
        if left.value:
            return MK_BOOL(True)

        right = interpreter.evaluate(binop.right, env)
        if not isinstance(right, BoolVal):
            logging.error(f"Right-hand side of '{binop.operator}' must be a boolean, got {right.type}")
            sys.exit(1)
        return MK_BOOL(right.value)

    logging.error(f"Unknown logical operator: {binop.operator}")
    sys.exit(1)

def evalNumericBinaryExpr(leftHand: NumberVal, rightHand: NumberVal, operator: str) -> NumberVal:
    if operator in ("/", "%") and rightHand.value == 0:
        operation = "divide" if operator == "/" else "modulo"
        logging.error(f"Cannot {operation} by zero")
        sys.exit(1)

    result = NUMERIC_OPS[operator](leftHand.value, rightHand.value)
    return MK_NUMBER(result)

def evalComparisonExpr(leftHand: NumberVal, rightHand: NumberVal, operator: str) -> BoolVal:
    result = COMPARISON_OPS[operator](leftHand.value, rightHand.value)
    return MK_BOOL(result)

def evalUnaryExpr(expr: UnaryExpr, env: Environment) -> RuntimeVal:
    operator = expr.operator

    if operator == "!":
        operand = interpreter.evaluate(expr.operand, env)
        if not isinstance(operand, BoolVal):
            logging.error(f"Type mismatch: '!' requires a boolean, got {operand.type}")
            sys.exit(1)
        return MK_BOOL(not operand.value)

    if operator in UNARY_NUMERIC_OPS:
        if expr.operand.type != NodeType.IDENTIFIER:
            logging.error(f"Invalid operand for '{operator}': expected Identifier, got {expr.operand.type}")
            sys.exit(1)

        varName = cast(Identifier, expr.operand).symbol
        current = env.lookupVar(varName)

        if not isinstance(current, NumberVal):
            logging.error(f"Type mismatch: '{operator}' requires a number, got {current.type}")
            sys.exit(1)

        oldValue = MK_NUMBER(current.value)
        newValue = MK_NUMBER(current.value + 1 if operator == "++" else current.value - 1)
        env.assignVar(varName, newValue)

        return newValue if expr.isPrefix else oldValue

    logging.error(f"Unknown unary operator: {operator}")
    sys.exit(1)

def evalAssignmentExpr(node: AssignmentExpr, env : Environment) -> RuntimeVal:
    if node.assigne.type != NodeType.IDENTIFIER:
        raise Exception(f"Invalid LHS inside assignment expression: {node.assigne}")

    varName = cast(Identifier, node.assigne).symbol
    return env.assignVar(varName, interpreter.evaluate(node.value, env))

def evalIdentifier(identifier: Identifier, env: Environment) -> RuntimeVal:
    val = env.lookupVar(identifier.symbol)
    return val

def evalFuncCallExpr(funcCall: FuncCallExpr, env: Environment) -> RuntimeVal:
    funcVal = cast(FuncVal, env.lookupVar(cast(Identifier, funcCall.caller).symbol))
    funcEnv = Environment(env)

    params = funcVal.parameters
    if len(funcCall.args) != len(params):
        logging.error(f"Function expected {len(params)} argument(s), got {len(funcCall.args)}.")
        sys.exit(1)
    
    for i in range(len(params)):
        paramName: str = params[i]
        paramArg = funcCall.args[i]
        funcEnv.declVar(paramName, interpreter.evaluate(paramArg, env), False)

    try:
        for stmt in funcVal.body:
            interpreter.evaluate(stmt, funcEnv)
    except Return as returnSignal:
        return returnSignal.Value

    return MK_NULL()