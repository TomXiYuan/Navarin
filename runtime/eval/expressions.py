import logging
import sys
import operator as op

from runtime.values import (
    RuntimeVal, 
    IntVal, 
    FloatVal, 
    FuncVal,
    NativeFuncVal, 
    BoolVal, 
    MK_NUMBER, 
    MK_NULL, 
    MK_BOOL
)
from frontend.abstractSyntaxTree import (
    BinaryExpr, 
    Identifier, 
    AssignmentExpr, 
    FuncCallExpr, 
    UnaryExpr
)
from runtime.eval.statements import Return, evalBlockStmt
import runtime.interpreter as interpreter
from runtime.environment import Environment

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
UNARY_NUMERIC_OPS = {"++", "--", "+", "-"}

def evalBinaryExpr(expr: BinaryExpr, env: Environment) -> RuntimeVal:
    operator = expr.operator

    # Short circuit
    if operator in LOGICAL_OPS:
        return evalLogicalBinaryExpr(expr, env)

    left = interpreter.evaluate(expr.left, env)
    right = interpreter.evaluate(expr.right, env)

    if isinstance(left, IntVal | FloatVal) and isinstance(right, IntVal | FloatVal):
        return evalNumericBinaryExpr(left, right, operator)

    logging.error(f"Cannot perform binary operation between {left.type} and {right.type}.")
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

def evalNumericBinaryExpr(left: IntVal | FloatVal, right: IntVal | FloatVal, operator: str) -> RuntimeVal:
    if operator in ("/", "%") and right.value == 0:
        operation = "divide" if operator == "/" else "modulo"
        logging.error(f"Cannot {operation} by zero")
        sys.exit(1)

    if operator in NUMERIC_OPS:
        result = NUMERIC_OPS[operator](left.value, right.value)
        return MK_NUMBER(result)

    if operator in COMPARISON_OPS:
        result = COMPARISON_OPS[operator](left.value, right.value)
        return MK_BOOL(result)

    logging.error(f"Operator '{operator}' is not supported between numbers")
    sys.exit(1)

def evalUnaryExpr(expr: UnaryExpr, env: Environment) -> RuntimeVal:
    operator = expr.operator

    if operator == "!":
        operandVal = interpreter.evaluate(expr.operand, env)
        if not isinstance(operandVal, BoolVal):
            logging.error(f"Type mismatch: '!' requires a boolean, got {operandVal.type}")
            sys.exit(1)
        return MK_BOOL(not operandVal.value)

    operandVal = interpreter.evaluate(expr.operand, env)

    if operator in ("+", "-"):
        if not isinstance(operandVal, IntVal | FloatVal):
            logging.error(f"Type mismatch: '{operator}' requires a number, got {operandVal.type}")
            sys.exit(1)
            
        if operator == "+":
            return MK_NUMBER(operandVal.value)
        elif operator == "-":
            return MK_NUMBER(-operandVal.value)

    if operator in ("++", "--"):
        # Operators ++ and -- can only be used on variables
        if not isinstance(expr.operand, Identifier):
            logging.error(f"Invalid operand for '{operator}': expected Identifier, got {expr.operand.type}")
            sys.exit(1)

        varName = expr.operand.symbol
        
        if not isinstance(operandVal, IntVal | FloatVal):
            logging.error(f"Type mismatch: '{operator}' requires a number, got {operandVal.type}")
            sys.exit(1)

        oldVal = MK_NUMBER(operandVal.value)
        
        if operator == "++":
            newVal = MK_NUMBER(operandVal.value + 1)
        else:
            newVal = MK_NUMBER(operandVal.value - 1)
        
        env.assignVar(varName, newVal)

        return newVal if expr.isPrefix else oldVal

    logging.error(f"Unknown unary operator: {operator}")
    sys.exit(1)


def evalAssignmentExpr(expr: AssignmentExpr, env : Environment) -> RuntimeVal:
    if not isinstance(expr.assigne, Identifier):
        raise Exception(f"Invalid LHS inside assignment expression: {expr.assigne}")

    varName = expr.assigne.symbol
    return env.assignVar(varName, interpreter.evaluate(expr.value, env))

def evalIdentifier(identifier: Identifier, env: Environment) -> RuntimeVal:
    val = env.lookupVar(identifier.symbol)
    return val

def evalFuncCallExpr(funcCall: FuncCallExpr, env: Environment) -> RuntimeVal:
    args = [interpreter.evaluate(arg, env) for arg in funcCall.args]
    calleeVal = interpreter.evaluate(funcCall.callee, env)

    if isinstance(calleeVal, NativeFuncVal):
        return calleeVal.call(args, env)

    if isinstance(calleeVal, FuncVal):
        funcVal = calleeVal
        funcEnv = Environment(funcVal.declEnv)

        params = funcVal.params
        if len(args) != len(params):
            logging.error(f"Function expected {len(params)} argument(s), got {len(args)}.")
            sys.exit(1)

        for i in range(len(params)):
            funcEnv.declVar(params[i], args[i], False)

        try:
            evalBlockStmt(funcVal.body, funcEnv)
        except Return as returnSignal:
            return returnSignal.value

        return MK_NULL()

    logging.error(f"Cannot call value that is not a function: {calleeVal}")
    sys.exit(1)