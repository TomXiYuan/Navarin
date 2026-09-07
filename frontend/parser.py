from frontend.abstractSyntaxTree import Stmt, Program, Expr, BinaryExpr, Identifier, NumericLiteral, VarDeclaration, AssignmentExpr, FuncDeclaration, FuncCallExpr, ReturnStmt
from frontend.lexer import tokenize, Token, TokenType
from typing import cast
import logging
import sys

class Parser:
    tokens: list[Token]

    def __init__(self) -> None:
        self.tokens: list[Token] = []

    def notEOF(self) -> bool:
        return self.tokens[0].type != TokenType.EOF

    def at(self):
        return self.tokens[0]

    def consume(self) -> Token:
        return self.tokens.pop(0)

    def expect(self, expectedType: TokenType, errorMessage: str) -> Token:
        if self.at().type == expectedType:
            return self.consume()
        else:
            logging.error(f"Parser Error: {errorMessage} - expected {expectedType}, got {self.at().type}")
            sys.exit(1)

    def produceAST(self, sourceCode: str) -> Program:
        self.tokens = tokenize(sourceCode)
        program: Program = Program(type = "Program", body = [])

        while self.notEOF():
            program.body.append(self.parseStmt())
        
        return program

    def parseStmt(self) -> Stmt:
        match(self.at().type):
            case TokenType.Var | TokenType.Const:
                return self.parseVarDecl()
            case TokenType.Func:
                return self.parseFuncDecl()
            case TokenType.Return:
                return self.parseReturnStmt()
            case _:
                return self.parseExpr()

    def parseVarDecl(self) -> Stmt:
        isConstant = self.consume().type == TokenType.Const
        identifier = self.expect(TokenType.Identifier, "Expected identifier name following let | const keywords.",).value

        if self.at().type == TokenType.EOS:
            self.consume()
            if isConstant:
                logging.error(f"Constant variable '{identifier}' must be initialized.")
                sys.exit(1)
            return VarDeclaration(type="VarDecl", constant=False, identifier=identifier)

        self.expect(TokenType.Equals, "Expected Equals token following identifier in var declaration.")
        value = self.parseAssignmentExpr()
        self.expect(TokenType.EOS, "Expected end of statement token following variable declaration.")
        varDeclaration = VarDeclaration(type="VarDecl", constant=isConstant, identifier=identifier, value=value)
        return varDeclaration

    def parseFuncDecl(self) -> Stmt:
        self.consume() # Consume func keyword
        identifier = self.expect(TokenType.Identifier, "Expected Identifier token following func keyword.").value
        args = self.parseArguments()
        params: list[str] = []

        for arg in args:
            if arg.type != "Identifier":
                raise Exception(f"Inside function declaration expected parameters to be of token type Identifier.")
            params.append(cast(Identifier, arg).symbol)

        self.expect(TokenType.OpenBrace, "Expected function body following declaration.")
        body: list[Stmt] = []

        while (self.at().type != TokenType.EOF and self.at().type != TokenType.CloseBrace):
            body.append(self.parseStmt())

        self.expect(TokenType.CloseBrace, "Closing brace expected inside function declaration")
        func = FuncDeclaration(identifier = identifier, parameters = params, body = body, type = "FuncDecl")
        return func

    def parseArguments(self) -> list[Expr]:
        self.expect(TokenType.OpenParen, "Expected OpenParen token following function name.")
        args = [] if self.at().type == TokenType.CloseParen else self.parseArgumentList();
        self.expect(TokenType.CloseParen, "Missing closing parenthesis inside arguments list");

        return args

    def parseArgumentList(self) -> list[Expr]:
        args : list[Expr] = [self.parseAssignmentExpr()]
        while (self.at().type == TokenType.Comma and self.consume()):
            args.append(self.parseAssignmentExpr())
        return args

    def parseReturnStmt(self) -> Stmt:
        self.consume()  # Consume return keyword
        value = None

        if self.at().type != TokenType.EOS:
            value = self.parseAdditiveExpr()

        self.expect(TokenType.EOS, "Expected EOS token following return statement.")
        return ReturnStmt(type="ReturnStmt", value=value)

    def parseExpr(self) -> Expr:
        expr = self.parseAssignmentExpr()
        # Expressions must consume a EOS if they are acting as a statement
        self.expect(TokenType.EOS, "Expected EOS token after expression statement.")
        return expr
        
    def parseAssignmentExpr(self) -> Expr:
        left = self.parseAdditiveExpr()

        if self.at().type == TokenType.Equals:
            self.consume()
            # Use parseAssignmentExpr() instead of parseAdditiveExpr() 
            # allows for right-associative chained assignments (e.g., x = y = 3.14)
            right = self.parseAssignmentExpr()

            if left.type != "Identifier":
                logging.error(f"Invalid assignment target: expected Identifier, got {left.type}")
                sys.exit(1)

            left = AssignmentExpr(left, right, type = "AssignmentExpr")

        return left

    def parseBinaryExpr(self, downstreamParser, operators: set[str]) -> Expr:
        left = downstreamParser()
        while self.notEOF() and self.at().value in operators:
            operator = self.consume().value
            right = downstreamParser()
            left = BinaryExpr(type="BinaryExpr", left=left, right=right, operator=operator)
        return left
        
    def parseAdditiveExpr(self) -> Expr:
        return self.parseBinaryExpr(self.parseMultiplicativeExpr, {"+", "-"})

    def parseMultiplicativeExpr(self) -> Expr:
        return self.parseBinaryExpr(self.parseFuncCallExpr, {"*", "/", "%"})

    def parseFuncCallExpr(self) -> Expr:
        expr = self.parsePrimaryExpr()

        if self.at().type == TokenType.OpenParen:
            # Wrap expression into function call
            caller = cast(Expr, expr)
            expr = FuncCallExpr(caller=caller, args=self.parseArguments(), type="FuncCallExpr")

        return cast(Expr, expr)

    def parsePrimaryExpr(self) -> Expr:
        tk = self.at().type
        match tk:
            case TokenType.Identifier:
                return Identifier(type="Identifier", symbol=self.consume().value)
            
            case TokenType.Number:
                return NumericLiteral(type="NumericLiteral", value=float(self.consume().value))
            
            case TokenType.OpenParen:
                self.consume()
                value = self.parseExpr()
                self.expect(TokenType.CloseParen, "Unexpected token found inside parenthesised expression. Expected closing parenthesis.",)
                return value

            case _:
                logging.error(f"Unexpected token: {self.at().value}")
                sys.exit(1)
