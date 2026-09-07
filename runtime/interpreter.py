from runtime.values import RuntimeVal, NumberVal
from frontend.abstractSyntaxTree import Program, BinaryExpr, NumericLiteral, Stmt, Identifier, VarDeclaration, AssignmentExpr, FuncDeclaration, FuncCallExpr, ReturnStmt
from runtime.environment import Environment
from runtime.eval.expressions import evalBinaryExpr, evalIdentifier, evalAssignmentExpr, evalFuncCallExpr
from runtime.eval.statements import evalProgram, evalVarDeclaration, evalFuncDeclaration, evalReturnStmt
from typing import cast
import logging
import sys

def evaluate(astNode : Stmt, env: Environment) -> RuntimeVal:
    match astNode.type:
        case "NumericLiteral":
            return NumberVal(type = "number", value = cast(NumericLiteral, astNode).value)

        case "Identifier":
            return evalIdentifier(cast(Identifier, astNode), env)

        case "AssignmentExpr":
            return evalAssignmentExpr(cast(AssignmentExpr, astNode), env)

        case "BinaryExpr":
            return evalBinaryExpr(cast(BinaryExpr, astNode), env)

        case "Program":
            return evalProgram(cast(Program, astNode), env)

        case "VarDecl":
            return evalVarDeclaration(cast(VarDeclaration, astNode), env)

        case "FuncDecl":
            return evalFuncDeclaration(cast(FuncDeclaration, astNode), env)

        case "FuncCallExpr":
            return evalFuncCallExpr(cast(FuncCallExpr, astNode), env)

        case "ReturnStmt":
            return evalReturnStmt(cast(ReturnStmt, astNode), env)

        case _:
            logging.error(f"This AST node has not been setup for interpretation: {astNode}")
            sys.exit(1)