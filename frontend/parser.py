from frontend.abstractSyntaxTree import Stmt, Program, Expr, BinaryExpr, Identifier, NumericLiteral, VarDeclaration
from frontend.lexer import tokenize, Token, TokenType
import logging
import sys

class Parser:
    tokens: list[Token]

    def notEOF(self) -> bool:
        return self.tokens[0].type != TokenType.EOF

    def at(self):
        return self.tokens[0]

    def advance(self) -> Token:
        return self.tokens.pop(0)

    def expect(self, expectedType: TokenType, errorMessage: str) -> Token:
        if self.at().type == expectedType:
            return self.advance()
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
        # skip to parse an expression for now
        match(self.at().type):
            case TokenType.Let | TokenType.Const:
                return self.parseVarDecl()
            case _:
                return self.parseExpr()

    def parseVarDecl(self) -> Stmt:
        isConstant = self.advance().type == TokenType.Const
        identifier = self.expect(TokenType.Identifier, "Expected identifier name following let | const keywords.",).value

        if self.at().type == TokenType.EOS:
            self.advance()
            if isConstant:
                logging.error(f"Constant variable '{identifier}' must be initialized.")
                sys.exit(1)
            return VarDeclaration(type="VarDecl", constant=False, identifier=identifier)

        self.expect(TokenType.Equals, "Expected equals token following identifier in var declaration.")
        declaration = VarDeclaration(type="VarDecl", constant=isConstant, identifier=identifier, value=self.parseExpr())
        self.expect(TokenType.EOS, "Expected end of statement token following variable declaration.")
        return declaration

    def parseExpr(self) -> Expr:
        return self.parseAdditiveExpr()

    def parseAdditiveExpr(self) -> Expr:
        left = self.parseMultiplicativeExpr()

        while self.at().value == "+" or self.at().value == "-":
            operator = self.advance().value
            right = self.parseMultiplicativeExpr()
            left = BinaryExpr(type="BinaryExpr", left=left, right=right, operator=operator)

        return left

    def parseMultiplicativeExpr(self) -> Expr:
        left = self.parsePrimaryExpr()

        while self.at().value == "*" or self.at().value == "/" or self.at().value == "%":
            operator = self.advance().value
            right = self.parsePrimaryExpr()
            left = BinaryExpr(type="BinaryExpr", left=left, right=right, operator=operator)

        return left

    def parsePrimaryExpr(self) -> Expr:
        tk = self.at().type
        match tk:
            case TokenType.Identifier:
                return Identifier(type="Identifier", symbol=self.advance().value)
            
            case TokenType.Number:
                return NumericLiteral(type="NumericLiteral", value=float(self.advance().value))
            
            case TokenType.OpenParen:
                self.advance()
                value = self.parseExpr()
                self.expect(TokenType.CloseParen, "Unexpected token found inside parenthesised expression. Expected closing parenthesis.",)
                return value
            
            case _:
                logging.error(f"Unexpected token: {self.at().value}")
                sys.exit(1)
