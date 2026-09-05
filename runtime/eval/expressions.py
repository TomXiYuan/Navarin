from runtime.values import RuntimeVal, NumberVal, MK_NUMBER, MK_NULL
from frontend.abstractSyntaxTree import BinaryExpr, Identifier, AssignmentExpr
import runtime.interpreter as interpreter
from runtime.environment import Environment
from typing import cast

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

def evalIdentifier(ident: Identifier, env: Environment) -> RuntimeVal:
    val = env.lookupVar(ident.symbol)
    return val