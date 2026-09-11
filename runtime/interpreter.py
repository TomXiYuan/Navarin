from runtime.values import RuntimeVal, NumberVal
from frontend.abstractSyntaxTree import NodeType, Stmt, Program, BinaryExpr, Identifier, NumericLiteral, VarDecl, AssignmentExpr, FuncDecl, FuncCallExpr, ReturnStmt, UnaryExpr
from runtime.environment import Environment
from runtime.eval.expressions import evalAssignmentExpr, evalIdentifier, evalBinaryExpr, evalUnaryExpr, evalFuncCallExpr
from runtime.eval.statements import evalProgram, evalVarDecl, evalFuncDecl, evalReturnStmt
from typing import cast
import logging
import sys

def evaluate(astNode : Stmt, env: Environment) -> RuntimeVal:
    match astNode.type:
        case NodeType.NUMERIC_LITERAL:
            return NumberVal(type = "number", value = cast(NumericLiteral, astNode).value)

        case NodeType.IDENTIFIER:
            return evalIdentifier(cast(Identifier, astNode), env)

        case NodeType.ASSIGNMENT_EXPRESSION:
            return evalAssignmentExpr(cast(AssignmentExpr, astNode), env)

        case NodeType.BINARY_EXPRESSION:
            return evalBinaryExpr(cast(BinaryExpr, astNode), env)

        case NodeType.UNARY_EXPRESSION:
            return evalUnaryExpr(cast(UnaryExpr, astNode), env)

        case NodeType.PROGRAM:
            return evalProgram(cast(Program, astNode), env)

        case NodeType.VARIABLE_DECLARATION:
            return evalVarDecl(cast(VarDecl, astNode), env)

        case NodeType.FUNCTION_DECLARATION:
            return evalFuncDecl(cast(FuncDecl, astNode), env)

        case NodeType.FUNCTION_CALL_EXPRESSION:
            return evalFuncCallExpr(cast(FuncCallExpr, astNode), env)

        case NodeType.RETURN_STATEMENT:
            return evalReturnStmt(cast(ReturnStmt, astNode), env)

        case _:
            logging.error(f"This AST node has not been setup for interpretation: {astNode}")
            sys.exit(1)