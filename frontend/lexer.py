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
    Comma = auto()
    Colon = auto()
    OpenParen = auto()
    CloseParen = auto()
    OpenBrace = auto() # {
    CloseBrace = auto() # }
    BinaryOperator = auto()

    # Keywords
    Var = auto()
    Const = auto()
    Func = auto()
    Return = auto()

    # End of file
    EOF = auto()

KEYWORDS = {
    "var": TokenType.Var,
    "const": TokenType.Const,
    "func": TokenType.Func,
    "return": TokenType.Return
}

SINGLECHARS = {
    "(": TokenType.OpenParen,
    ")": TokenType.CloseParen,
    "{": TokenType.OpenBrace,
    "}": TokenType.CloseBrace,
    ":": TokenType.Colon,
    ",": TokenType.Comma,
    ";": TokenType.EOS,
    "+": TokenType.BinaryOperator,
    "-": TokenType.BinaryOperator,
    "*": TokenType.BinaryOperator,
    "/": TokenType.BinaryOperator,
    "%": TokenType.BinaryOperator,
    "=": TokenType.Equals
}

SKIPPABLE = {" ", "\t", "\r", "\n"}
EOS = {";"}

@dataclass (frozen=True)
class Token():
    value: str
    type: TokenType

def token(value: str, type: TokenType) -> Token:
    return Token(value=value, type=type)

def isSkippable(string: str) -> bool:
    return string in SKIPPABLE

def tokenize(sourceCode: str) -> list[Token]:
    tokens: list[Token] = []
    src = list(sourceCode)

    while len(src) > 0:
        char = src.pop(0)

        if isSkippable(char): continue

        if char in EOS:
            # Only append EOS if the last token isn't already an EOS
            if not tokens or tokens[-1].type != TokenType.EOS:
                tokens.append(Token(";", TokenType.EOS))

        elif char in SINGLECHARS:
            tokens.append(Token(char, SINGLECHARS[char]))

        # Build number tokens
        elif char.isdigit():
            numValue = char
            while len(src) > 0 and (src[0].isdigit() or src[0] == "."):
                numValue += src.pop(0)
            tokens.append(token(numValue, TokenType.Number))

        # Build identifier tokens
        elif char.isalpha() or char == "_":
            idValue = char
            while len(src) > 0 and src[0].isalpha():
                idValue += src.pop(0)
            # Check if the identifier is a keyword
            tokenType = KEYWORDS[idValue] if idValue in KEYWORDS else TokenType.Identifier
            tokens.append(token(idValue, tokenType))

        else:
            logging.error(f"Unexpected character: {char}")
            sys.exit(1)

    tokens.append(token("EndOfFile", TokenType.EOF))
    return tokens