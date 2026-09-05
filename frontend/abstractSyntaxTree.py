from typing import Literal, Protocol
from dataclasses import dataclass

NodeType = Literal[
    # Statements
    "Program",
    "VarDecl",

    # Expressions
    "AssignmentExpr",
    "NumericLiteral",
    "Identifier",
    "BinaryExpr"
]

class Stmt(Protocol):
    type: NodeType

@dataclass
class Program(Stmt):
    body: list[Stmt]
    type: NodeType = "Program"

@dataclass 
class VarDeclaration(Stmt):
    constant : bool
    identifier : str
    value: Expr | None = None
    type: NodeType = "VarDecl"

class Expr(Stmt):
    type: NodeType

@dataclass
class AssignmentExpr(Expr):
    assigne : Expr
    value : Expr
    type: NodeType = "AssignmentExpr"

@dataclass
class BinaryExpr(Expr):
    left: Expr
    right: Expr
    operator: str
    type: NodeType = "BinaryExpr"

@dataclass
class Identifier(Expr):
    symbol: str
    type: NodeType = "Identifier"

@dataclass
class NumericLiteral(Expr):
    value: int | float
    type: NodeType = "NumericLiteral"
