from frontend.parser import Parser
from runtime.resolver import Resolver
from runtime.interpreter import Interpreter
from runtime.environment import Environment
from frontend.abstractSyntaxTree import Identifier
import sys

def main():
    run()

def debug():
    parser = Parser()
    interpreter = Interpreter()
    env = Environment(parent = None)

    while(True):
        sourceCode = input("> ")
    
        if sourceCode.lower() == 'exit':
            sys.exit(0)

        program = parser.produceAST(sourceCode)
        interpreter.interpret(program)

def run():
    parser = Parser()
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    env = Environment(parent = None)

    with open("test.txt") as file:
        sourceCode = file.read() 
    
    program = parser.produceAST(sourceCode)
    resolver.resolveProgram(program)
    
    interpreter.locals = resolver.locals
    interpreter.interpret(program)

if __name__ == "__main__":
    main()