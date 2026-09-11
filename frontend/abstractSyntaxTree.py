from typing import Literal, Protocol
from dataclasses import dataclass
from enum import StrEnum, auto

class NodeType(StrEnum):
    # Statements
    PROGRAM = auto()
    VARIABLE_DECLARATION = auto()
    FUNCTION_DECLARATION = auto()
    RETURN_STATEMENT = auto()

    # Expressions
    FUNCTION_CALL_EXPRESSION = auto()
    ASSIGNMENT_EXPRESSION = auto()
    NUMERIC_LITERAL = auto()
    IDENTIFIER = auto()
    BINARY_EXPRESSION = auto()
    UNARY_EXPRESSION = auto()

class Stmt(Protocol):
    type: NodeType

@dataclass
class Program(Stmt):
    body: list[Stmt]
    type: NodeType = NodeType.PROGRAM

@dataclass 
class VarDecl(Stmt):
    constant : bool
    identifier : str
    value: Expr | None = None
    type: NodeType = NodeType.VARIABLE_DECLARATION

@dataclass
class FuncDecl(Stmt):
    identifier : str
    parameters: list[str]
    body : list[Stmt]
    type : NodeType = NodeType.FUNCTION_DECLARATION

@dataclass
class ReturnStmt(Stmt):
    value: Expr | None
    type : NodeType = NodeType.RETURN_STATEMENT

@dataclass
class IfStmt(Stmt):
    condition: Expr
    thenBranch : Stmt
    elseBranch: Stmt

class Expr(Stmt):
    type: NodeType

@dataclass
class FuncCallExpr(Expr):
    caller : Expr
    args : list[Expr]
    type: NodeType = NodeType.FUNCTION_CALL_EXPRESSION

@dataclass
class AssignmentExpr(Expr):
    assigne : Expr
    value : Expr
    type: NodeType = NodeType.ASSIGNMENT_EXPRESSION

@dataclass
class BinaryExpr(Expr):
    left: Expr
    right: Expr
    operator: str
    type: NodeType = NodeType.BINARY_EXPRESSION

@dataclass
class UnaryExpr(Expr):
    operand: Expr
    operator: str
    isPrefix: bool
    type: NodeType = NodeType.UNARY_EXPRESSION

@dataclass
class Identifier(Expr):
    symbol: str
    type: NodeType = NodeType.IDENTIFIER

@dataclass
class NumericLiteral(Expr):
    value: int | float
    type: NodeType = NodeType.NUMERIC_LITERAL
