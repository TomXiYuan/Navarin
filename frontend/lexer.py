from enum import IntEnum, auto
from dataclasses import dataclass
import logging
import sys

class TokenType(IntEnum):
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()
    
    # Grouping and Operators
    EQUALS = auto()
    EOS = auto()
    COMMA = auto()
    COLON = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_BRACE = auto()   # {
    CLOSE_BRACE = auto()  # }
    BINARY_OPERATOR = auto()
    UNARY_OPERATOR = auto()
    LOGIC_OPERATOR = auto()
    
    # Keywords
    VAR = auto()
    CONST = auto()
    FUNC = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    
    # End of file
    EOF = auto()

# Constants should also be UPPER_CASE
KEYWORDS = {
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE
}

SINGLE_CHARS = {
    "(": TokenType.OPEN_PAREN,
    ")": TokenType.CLOSE_PAREN,
    "{": TokenType.OPEN_BRACE,
    "}": TokenType.CLOSE_BRACE,

    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    ";": TokenType.EOS,

    "+": TokenType.BINARY_OPERATOR,
    "-": TokenType.BINARY_OPERATOR,
    "*": TokenType.BINARY_OPERATOR,
    "/": TokenType.BINARY_OPERATOR,
    "%": TokenType.BINARY_OPERATOR,

    "=": TokenType.EQUALS,

    "<": TokenType.BINARY_OPERATOR,
    ">": TokenType.BINARY_OPERATOR,

    "!": TokenType.UNARY_OPERATOR
}

DOUBLE_CHARS = {
    "<=": TokenType.BINARY_OPERATOR,
    ">=": TokenType.BINARY_OPERATOR,
    "==": TokenType.BINARY_OPERATOR,
    "!=": TokenType.BINARY_OPERATOR,

    "++": TokenType.UNARY_OPERATOR,
    "--": TokenType.UNARY_OPERATOR,

    "&&": TokenType.LOGIC_OPERATOR,
    "||": TokenType.LOGIC_OPERATOR,
}

DOUBLE_CHAR_STARTS = {pair[0] for pair in DOUBLE_CHARS}
SKIPPABLE = {" ", "\t", "\r", "\n"}
EOS_CHARS = {";"}

@dataclass(frozen=True)
class Token:
    value: str
    type: TokenType

def create_token(value: str, type: TokenType) -> Token:
    return Token(value=value, type=type)

def is_skippable(string: str) -> bool:
    return string in SKIPPABLE

def tokenize(source_code: str) -> list[Token]:
    tokens: list[Token] = []
    src: list[str] = list(source_code)
    
    while len(src) > 0:
        char: str = src.pop(0)
        
        if is_skippable(char):
            continue
            
        if char in EOS_CHARS:
            if not tokens or tokens[-1].type != TokenType.EOS:
                tokens.append(Token(";", TokenType.EOS))
                
        elif char in SINGLE_CHARS or char in DOUBLE_CHAR_STARTS:
            doubleChar = char + (src[0] if src else "")
            if doubleChar in DOUBLE_CHARS:
                src.pop(0)
                tokens.append(Token(doubleChar, DOUBLE_CHARS[doubleChar]))
            elif char in SINGLE_CHARS:
                tokens.append(Token(char, SINGLE_CHARS[char]))
            else:
                logging.error(f"Unexpected character: {char}")
                sys.exit(1)

         # Build number tokens   
        elif char.isdigit():
            num_value = char
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                num_value += src.pop(0)
            tokens.append(create_token(num_value, TokenType.NUMBER))

        # Build identifier tokens
        elif char.isalpha() or char == "_":
            id_value = char
            while len(src) > 0 and src[0].isalpha():
                id_value += src.pop(0)
            # Check if the identifier is a keyword
            token_type = KEYWORDS[id_value] if id_value in KEYWORDS else TokenType.IDENTIFIER
            tokens.append(create_token(id_value, token_type))
            
        else:
            logging.error(f"Unexpected character: {char}")
            sys.exit(1)
            
    tokens.append(create_token("EndOfFile", TokenType.EOF))
    return tokens
