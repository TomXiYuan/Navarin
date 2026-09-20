from enum import Enum, auto
from dataclasses import dataclass
import logging
import sys

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
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
    OPERATOR = auto()
    
    # Keywords
    VAR = auto()
    CONST = auto()
    FUNC = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    BREAK = auto()
    FOR = auto()
    TRUE = auto()
    FALSE = auto()
    
    # End of file
    EOF = auto()

KEYWORDS = {
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "for": TokenType.FOR,

    "true": TokenType.BOOLEAN,
    "false": TokenType.BOOLEAN,
    "null": TokenType.NULL
}

SINGLE_CHARS = {
    "(": TokenType.OPEN_PAREN,
    ")": TokenType.CLOSE_PAREN,
    "{": TokenType.OPEN_BRACE,
    "}": TokenType.CLOSE_BRACE,

    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    ";": TokenType.EOS,

    "+": TokenType.OPERATOR,
    "-": TokenType.OPERATOR,
    "*": TokenType.OPERATOR,
    "/": TokenType.OPERATOR,
    "%": TokenType.OPERATOR,

    "<": TokenType.OPERATOR,
    ">": TokenType.OPERATOR,

    "!": TokenType.OPERATOR,

    "=": TokenType.EQUALS
}

DOUBLE_CHARS = {
    "<=": TokenType.OPERATOR,
    ">=": TokenType.OPERATOR,
    "==": TokenType.OPERATOR,
    "!=": TokenType.OPERATOR,

    "++": TokenType.OPERATOR,
    "--": TokenType.OPERATOR,

    "&&": TokenType.OPERATOR,
    "||": TokenType.OPERATOR,
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
            numValue = char
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                numValue += src.pop(0)
            tokens.append(create_token(numValue, TokenType.NUMBER))

        # Build identifier tokens
        elif char.isalpha() or char == "_":
            idValue = char
            while len(src) > 0 and src[0].isalnum():
                idValue += src.pop(0)
            # Check if the identifier is a keyword
            tokenType = KEYWORDS[idValue] if idValue in KEYWORDS else TokenType.IDENTIFIER
            tokens.append(create_token(idValue, tokenType))
            
        else:
            logging.error(f"Unexpected character: {char}")
            sys.exit(1)
            
    tokens.append(create_token("EndOfFile", TokenType.EOF))
    return tokens