from enum import IntEnum, auto
from dataclasses import dataclass
import logging
import sys

class TokenType(IntEnum):
    # Literals
    Number = auto()
    Identifier = auto()
    String = auto()

    # Grouping and Operators
    Equals = auto()
    EOS = auto()
    OpenParen = auto()
    CloseParen = auto()
    BinaryOperator = auto()

    # Keywords
    Let = auto()
    Const = auto()

    # End of file
    EOF = auto()

KEYWORDS = {
    "let": TokenType.Let,
    "const": TokenType.Const
}

@dataclass
class Token():
    value: str
    type: TokenType

def token(value: str, type: TokenType) -> Token:
    return Token(value=value, type=type)

def isSkippable(string: str) -> bool:
    return string in [" ", "\t"]

def tokenize(sourceCode: str) -> list[Token]:
    tokens: list[Token] = []
    src = list(sourceCode)

    while len(src) > 0:
        value = src.pop(0)
        if value == "(":
            tokens.append(token(value, TokenType.OpenParen))
        elif value == ")":
            tokens.append(token(value, TokenType.CloseParen))
        elif value in ["+", "-", "*", "/", "%"]:
            tokens.append(token(value, TokenType.BinaryOperator))
        elif value == "=":
            tokens.append(token(value, TokenType.Equals))
        elif value == ";" or value == "\n":
            tokens.append(token(value, TokenType.EOS))
        else:
            # Handle multi-character tokens

            # Build number tokens
            if value.isdigit():
                numValue = value
                while len(src) > 0 and src[0].isdigit():
                    numValue += src.pop(0)
                tokens.append(token(numValue, TokenType.Number))
            # Build identifier tokens
            elif value.isalpha():
                idValue = value
                while len(src) > 0 and src[0].isalpha():
                    idValue += src.pop(0)
                # Check if the identifier is a keyword
                if idValue in KEYWORDS:
                    tokens.append(token(idValue, KEYWORDS[idValue]))
                else:
                    tokens.append(token(idValue, TokenType.Identifier))
            elif isSkippable(value):
                continue
            else:
                logging.error(f"Unexpected character: {value}")
                sys.exit(1)

    tokens.append(token("EndOfFile", TokenType.EOF))
    return tokens