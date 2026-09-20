from frontend.parser import Parser
from runtime.interpreter import evaluate
from runtime.environment import Environment
import sys

def main():
    run()

def debug():
    parser = Parser()
    env = Environment(parent = None)

    while(True):
        sourceCode = input("> ")
    
        if sourceCode.lower() == 'exit':
            sys.exit(0)

        program = parser.produceAST(sourceCode)
        evaluate(program, env)

def run():
    parser = Parser()
    env = Environment(parent = None)

    with open("test.txt") as file:
        sourceCode = file.read() 
    
    program = parser.produceAST(sourceCode)
    evaluate(program, env)

if __name__ == "__main__":
    main()