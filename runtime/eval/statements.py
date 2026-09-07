from runtime.values import RuntimeVal, MK_NULL, FunctionValue, NullVal
import runtime.interpreter as interpreter
from frontend.abstractSyntaxTree import Program, VarDeclaration, FuncDeclaration, ReturnStmt
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

def evalFuncDeclaration(funcDeclaration: FuncDeclaration, env: Environment) -> RuntimeVal:
    func = FunctionValue(name=funcDeclaration.identifier, parameters = funcDeclaration.parameters, declarationEnv = env, body = funcDeclaration.body)
    return env.declareVar(funcDeclaration.identifier, func, False)

def evalReturnStmt(stmt: ReturnStmt, env: Environment) -> RuntimeVal:
    value = interpreter.evaluate(stmt.value, env) if stmt.value is not None else MK_NULL()
    return value


