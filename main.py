from frontend.parser import Parser
from runtime.interpreter import evaluate
from runtime.environment import Environment
from runtime.values import NumberVal, MK_NUMBER, MK_BOOL, MK_NULL
import sys

def main():
    parser = Parser()
    env = Environment(parent = None)

    env.declareVar("x", MK_NUMBER(100), False)
    env.declareVar("true", MK_BOOL(True), False)
    env.declareVar("false", MK_BOOL(False), False)
    env.declareVar("null", MK_NULL(), False)
    
    while(True):
        sourceCode = input("Enter source code (or 'exit' to quit): ")
        sourceCode += '\n'

        if sourceCode.lower() == 'exit':
            sys.exit(0) 

        program = parser.produceAST(sourceCode)

        result = evaluate(program, env)
        print(result)

if __name__ == "__main__":
    main()