import logging
import sys
from typing import cast

from frontend.abstractSyntaxTree import (
    AssignmentExpr,
    BinaryExpr,
    BlockStmt,
    BooleanLiteral,
    FuncCallExpr,
    FuncDecl,
    Identifier,
    IfStmt,
    BreakStmt,
    NullLiteral,
    NumericLiteral,
    Program,
    ReturnStmt,
    Stmt,
    Expr,
    UnaryExpr,
    VarDecl,
    WhileStmt
)
from runtime.environment import Environment
from runtime.eval.expressions import (
    evalAssignmentExpr,
    evalBinaryExpr,
    evalFuncCallExpr,
    evalIdentifier,
    evalUnaryExpr,
)
from runtime.eval.statements import (
    evalBlockStmt,
    evalBreakStmt,
    evalFuncDecl,
    evalIfStmt,
    evalProgram,
    evalReturnStmt,
    evalVarDecl,
    evalWhileStmt,
)
from runtime.values import RuntimeVal, MK_BOOL, MK_NULL, MK_NUMBER

class Interpreter:
    globalEnv: Environment
    locals: dict[int, int]

    def __init__(self):
        self.locals: dict[int, int] = {}
        self.globalEnv = Environment(None)

    def interpret(self, program: Program) -> RuntimeVal:
        return self.evaluate(program, self.globalEnv)

    def getGlobalVar(self, varName: str) -> RuntimeVal:
        return self.globalEnv.getVar(varName)

    def assignGlobalVar(self, varName: str, value: RuntimeVal) -> RuntimeVal:
        self.globalEnv.assignVar(varName, value)
        return value

    def evaluate(self, astNode: Stmt, env: Environment) -> RuntimeVal:
        match astNode:
            case NumericLiteral():
                return MK_NUMBER(value=astNode.value)

            case BooleanLiteral():
                return MK_BOOL(value=astNode.value)

            case NullLiteral():
                return MK_NULL()

            case Identifier():
                return evalIdentifier(astNode, env, self)

            case AssignmentExpr():
                return evalAssignmentExpr(astNode, env, self)

            case BinaryExpr():
                return evalBinaryExpr(astNode, env, self)

            case UnaryExpr():
                return evalUnaryExpr(astNode, env, self)

            case Program():
                return evalProgram(astNode, env, self)

            case VarDecl():
                return evalVarDecl(astNode, env, self)

            case FuncDecl():
                return evalFuncDecl(astNode, env, self)

            case FuncCallExpr():
                return evalFuncCallExpr(astNode, env, self)

            case ReturnStmt():
                return evalReturnStmt(astNode, env, self)

            case IfStmt():
                return evalIfStmt(astNode, env, self)

            case WhileStmt():
                return evalWhileStmt(astNode, env, self)

            case BreakStmt():
                return evalBreakStmt()

            case BlockStmt():
                return evalBlockStmt(astNode, env, self)

            case _:
                logging.error(f"This AST node has not been setup for interpretation: {astNode}")
                sys.exit(1)