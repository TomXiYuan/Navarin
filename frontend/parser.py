from frontend.abstractSyntaxTree import NodeType, Stmt, Program, Expr, BinaryExpr, Identifier, NumericLiteral, VarDecl, AssignmentExpr, FuncDecl, FuncCallExpr, ReturnStmt, UnaryExpr
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
        program: Program = Program(type = NodeType.PROGRAM, body = [])

        while self.notEOF():
            program.body.append(self.parseStmt())
        
        return program

    def parseStmt(self) -> Stmt:
        match(self.at().type):
            case TokenType.VAR | TokenType.CONST:
                return self.parseVarDecl()
            case TokenType.FUNC:
                return self.parseFuncDecl()
            case TokenType.RETURN:
                return self.parseReturnStmt()
            #case TokenType.IF:
                #return self.parseIfStmt()
            case _:
                return self.parseExpr()

    def parseVarDecl(self) -> Stmt:
        isConstant = self.consume().type == TokenType.CONST
        identifier = self.expect(TokenType.IDENTIFIER, "Expected identifier name following let | const keywords.",).value

        if self.at().type == TokenType.EOS:
            self.consume()
            if isConstant:
                logging.error(f"Constant variable '{identifier}' must be initialized.")
                sys.exit(1)
            return VarDecl(type=NodeType.VARIABLE_DECLARATION, constant=False, identifier=identifier)

        self.expect(TokenType.EQUALS, "Expected Equals token following identifier in var declaration.")
        value = self.parseAssignmentExpr()
        self.expect(TokenType.EOS, "Expected end of statement token following variable declaration.")
        varDeclaration = VarDecl(type=NodeType.VARIABLE_DECLARATION, constant=isConstant, identifier=identifier, value=value)
        return varDeclaration

    def parseFuncDecl(self) -> Stmt:
        self.consume() # Consume func keyword
        identifier = self.expect(TokenType.IDENTIFIER, "Expected Identifier token following func keyword.").value
        args = self.parseArguments()
        params: list[str] = []

        for arg in args:
            if arg.type != NodeType.IDENTIFIER:
                raise Exception(f"Inside function declaration expected parameters to be of token type Identifier.")
            params.append(cast(Identifier, arg).symbol)

        self.expect(TokenType.OPEN_BRACE, "Expected function body following declaration.")
        body: list[Stmt] = []

        while (self.at().type != TokenType.EOF and self.at().type != TokenType.CLOSE_BRACE):
            body.append(self.parseStmt())

        self.expect(TokenType.CLOSE_BRACE, "Closing brace expected inside function declaration")
        func = FuncDecl(identifier = identifier, parameters = params, body = body, type = NodeType.FUNCTION_DECLARATION)
        return func

    def parseArguments(self) -> list[Expr]:
        self.expect(TokenType.OPEN_PAREN, "Expected OpenParen token following function name.")
        args = [] if self.at().type == TokenType.CLOSE_PAREN else self.parseArgumentList();
        self.expect(TokenType.CLOSE_PAREN, "Missing closing parenthesis inside arguments list");
        return args

    def parseArgumentList(self) -> list[Expr]:
        args : list[Expr] = [self.parseAssignmentExpr()]
        while (self.at().type == TokenType.COMMA and self.consume()):
            args.append(self.parseAssignmentExpr())
        return args

    def parseReturnStmt(self) -> Stmt:
        self.consume() # Consume return keyword
        value = None

        if self.at().type != TokenType.EOS:
            value = self.parseAssignmentExpr()

        self.expect(TokenType.EOS, "Expected EOS token following return statement.")
        return ReturnStmt(type=NodeType.RETURN_STATEMENT, value=value)

    def parseExpr(self) -> Expr:
        expr = self.parseAssignmentExpr()
        # Exprs must consume a EOS if they are acting as a statement
        self.expect(TokenType.EOS, "Expected EOS token after expression statement.")
        return expr
        
    def parseAssignmentExpr(self) -> Expr:
        left = self.parseLogicExpr()

        if self.at().type == TokenType.EQUALS:
            self.consume()
            # Use parseAssignmentExpr() instead of parseAdditiveExpr() 
            # allows for right-associative chained assignments (e.g., x = y = 3.14)
            right = self.parseAssignmentExpr()

            if left.type != NodeType.IDENTIFIER:
                logging.error(f"Invalid assignment target: expected Identifier, got {left.type}")
                sys.exit(1)

            left = AssignmentExpr(left, right, type = NodeType.ASSIGNMENT_EXPRESSION)

        return left

    def parseBinaryExpr(self, downstreamParser, operators: set[str]) -> Expr:
        left = downstreamParser()
        while self.notEOF() and self.at().value in operators:
            operator = self.consume().value
            right = downstreamParser()
            left = BinaryExpr(type=NodeType.BINARY_EXPRESSION, left=left, right=right, operator=operator)
        return left

    def parseLogicExpr(self) -> Expr:
        return self.parseBinaryExpr(self.parseComparisonExpr, {"&&", "||"})

    def parseComparisonExpr(self) -> Expr:
        return self.parseBinaryExpr(self.parseAdditiveExpr, {">", "<", ">=", "<=", "=="})
        
    def parseAdditiveExpr(self) -> Expr:
        return self.parseBinaryExpr(self.parseMultiplicativeExpr, {"+", "-"})

    def parseMultiplicativeExpr(self) -> Expr:
        return self.parseBinaryExpr(self.parseUnaryExpr, {"*", "/", "%"})

    def parseUnaryExpr(self) -> Expr:
        #Prefix
        if self.at().type == TokenType.UNARY_OPERATOR:
            operator = self.consume().value
            operand = self.parseFuncCallExpr()
            return UnaryExpr(operand, operator, isPrefix= True, type=NodeType.UNARY_EXPRESSION)

        expr = self.parseFuncCallExpr()

        #Postfix
        if self.at().type == TokenType.UNARY_OPERATOR:
            operator = self.consume().value
            return UnaryExpr(expr, operator, isPrefix= False, type=NodeType.UNARY_EXPRESSION)

        return expr

    def parseFuncCallExpr(self) -> Expr:
        expr = self.parsePrimaryExpr()

        if self.at().type == TokenType.OPEN_PAREN:
            caller = cast(Expr, expr)
            expr = FuncCallExpr(caller=caller, args=self.parseArguments(), type= NodeType.FUNCTION_CALL_EXPRESSION)

        return cast(Expr, expr)

    def parsePrimaryExpr(self) -> Expr:
        tk = self.at().type
        match tk:
            case TokenType.IDENTIFIER:
                return Identifier(type=NodeType.IDENTIFIER, symbol=self.consume().value)
            
            case TokenType.NUMBER:
                return NumericLiteral(type=NodeType.NUMERIC_LITERAL, value=float(self.consume().value))
            
            case TokenType.OPEN_PAREN:
                self.consume()
                value = self.parseExpr()
                self.expect(TokenType.CLOSE_PAREN, "Unexpected token found inside parenthesised expression. Expected closing parenthesis.",)
                return value

            case _:
                logging.error(f"Unexpected token: {self.at().value}")
                sys.exit(1)
