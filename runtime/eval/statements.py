from runtime.values import RuntimeVal, NullVal, MK_NULL
import runtime.interpreter as interpreter
from frontend.abstractSyntaxTree import Program, VarDeclaration, Expr
from runtime.environment import Environment

def evalProgram(program: Program, env: Environment) -> RuntimeVal:
    lastEvaluated: RuntimeVal = MK_NULL()
    for stmt in program.body:
        lastEvaluated = interpreter.evaluate(stmt, env)
    return lastEvaluated

def evalVarDeclaration(varDeclaration: VarDeclaration, env: Environment) -> RuntimeVal:
    value : RuntimeVal
    if varDeclaration.value:
        value = interpreter.evaluate(varDeclaration.value, env)
    else:
        value = MK_NULL()
    
    return env.declareVar(varDeclaration.identifier, value, varDeclaration.constant)

