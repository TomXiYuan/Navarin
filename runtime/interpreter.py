from runtime.values import RuntimeVal, NumberVal
from frontend.abstractSyntaxTree import Program, BinaryExpr, NumericLiteral, Stmt, Identifier, VarDeclaration, AssignmentExpr
from runtime.environment import Environment
from runtime.eval.expressions import evalBinaryExpr, evalIdentifier, evalAssignmentExpr
from runtime.eval.statements import evalProgram, evalVarDeclaration
from typing import cast
import logging
import sys

def evaluate(astNode : Stmt, env: Environment) -> RuntimeVal:
    match astNode.type:
        case "NumericLiteral":
            return NumberVal(type = "number", value = cast(NumericLiteral, astNode).value)

        case "Identifier":
            return evalIdentifier(cast(Identifier, astNode), env)

        case "BinaryExpr":
            return evalBinaryExpr(cast(BinaryExpr, astNode), env)

        case "Program":
            return evalProgram(cast(Program, astNode), env)

        case "VarDecl":
            return evalVarDeclaration(cast(VarDeclaration, astNode), env)

        case "AssignmentExpr":
            return evalAssignmentExpr(cast(AssignmentExpr, astNode), env)
        
        case _:
            logging.error(f"This AST node has not been setup for interpretation: {astNode}")
            sys.exit(1)