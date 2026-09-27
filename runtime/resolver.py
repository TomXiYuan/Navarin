import logging
import sys

from frontend.abstractSyntaxTree import (
    BlockStmt,
    FuncDecl,
    IfStmt,
    Program,
    ReturnStmt,
    Expr,
    VarDecl,
    WhileStmt,
    Identifier,
    AssignmentExpr,
    BinaryExpr,
    UnaryExpr,
    FuncCallExpr
)
from runtime.interpreter import Interpreter

class Resolver:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.locals: dict[int, int] = {}
        self.nodeNames = {}

    def beginScope(self):
        self.scopes.append({})

    def endScope(self):
        self.scopes.pop()

    def declare(self, name: str):
        if not self.scopes:
            return
        # Grab the last scope
        scope = self.scopes[-1]
        if name in scope:
            logging.error(f"Variable '{name}' already declared in this scope.")
            sys.exit(1)
        scope[name] = False

    def define(self, name: str):
        if not self.scopes:
            return
        # Define variable in last scope
        self.scopes[-1][name] = True

    def resolveLocal(self, exprNode, name: str):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                dst = len(self.scopes) - 1 - i
                self.locals[id(exprNode)] = dst
                self.nodeNames[id(exprNode)] = name 
                return

    def resolveProgram(self, program: Program):
        for stmt in program.body:
            self.resolveStmt(stmt)

    def resolveBlockStmt(self, blockStmt: BlockStmt):
        self.beginScope()
        for stmt in blockStmt.body:
            self.resolveStmt(stmt)
        self.endScope()

    def resolveVarDecl(self, stmt: VarDecl):
        self.declare(stmt.identifier)
        if not stmt.value == None:
            self.resolveExpr(stmt.value)
        self.define(stmt.identifier)

    def resolveFuncDecl(self, stmt: FuncDecl):
        self.declare(stmt.identifier)
        self.define(stmt.identifier)

        self.beginScope() # Scope A: params
        for param in stmt.parameters:
            self.declare(param)
            self.define(param)
        self.resolveStmt(stmt.body) # stmt.body is a BlockStmt, resolveBlockStmt() pushes and pops scope B
        self.endScope() # Pops scope A

    def resolveIfStmt(self, stmt: IfStmt):
        self.resolveExpr(stmt.condition)
        self.resolveStmt(stmt.thenBlock)
        self.resolveStmt(stmt.elseBlock)

    def resolveWhileStmt(self, stmt: WhileStmt):
        self.resolveExpr(stmt.condition)
        self.resolveStmt(stmt.body)

    def resolveReturnStmt(self, stmt: ReturnStmt):
        if stmt.value:
            self.resolveExpr(stmt.value)

    def resolveStmt(self, stmt):
        match stmt:
            case BlockStmt():
                self.resolveBlockStmt(stmt)

            case VarDecl():
                self.resolveVarDecl(stmt)

            case FuncDecl():
                self.resolveFuncDecl(stmt)

            case IfStmt():
                self.resolveIfStmt(stmt)

            case WhileStmt():
                self.resolveWhileStmt(stmt)

            case ReturnStmt():
                self.resolveReturnStmt(stmt)

            case Expr():
                self.resolveExpr(stmt)

            case _:
                pass

    def resolveExpr(self, expr):
        match expr:
            case Identifier():
                self.resolveLocal(expr, expr.symbol)

            case AssignmentExpr():
                self.resolveExpr(expr.value)
                self.resolveExpr(expr.assigne)

            case BinaryExpr():
                self.resolveExpr(expr.left)
                self.resolveExpr(expr.right)

            case UnaryExpr():
                self.resolveExpr(expr.operand)
                
            case FuncCallExpr():
                self.resolveExpr(expr.callee)
                for arg in expr.args:
                    self.resolveExpr(arg)