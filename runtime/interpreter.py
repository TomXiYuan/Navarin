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
    NodeType,
    NullLiteral,
    NumericLiteral,
    Program,
    ReturnStmt,
    Stmt,
    UnaryExpr,
    VarDecl,
    WhileStmt,
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

def evaluate(astNode : Stmt, env: Environment) -> RuntimeVal:
    match astNode.type:
        case NodeType.NUMERIC_LITERAL:
            return MK_NUMBER(value=cast(NumericLiteral, astNode).value)

        case NodeType.BOOLEAN_LITERAL:
            return MK_BOOL(value=cast(BooleanLiteral, astNode).value)

        case NodeType.NULL_LITERAL:
            return MK_NULL()

        case NodeType.BOOLEAN_LITERAL:
            return MK_NULL(value=cast(NullLiteral, astNode).value)

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

        case NodeType.IF_STATEMENT:
            return evalIfStmt(cast(IfStmt, astNode), env)

        case NodeType.WHILE_STATEMENT:
            return evalWhileStmt(cast(WhileStmt, astNode), env)

        case NodeType.BREAK_STATEMENT:
            return evalBreakStmt()

        case NodeType.BLOCK_STATEMENT:
            return evalBlockStmt(cast(BlockStmt, astNode), env)

        case _:
            logging.error(f"This AST node has not been setup for interpretation: {astNode}")
            sys.exit(1)