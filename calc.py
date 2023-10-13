from dataclasses import dataclass
import math
import random
from multimethod import multimeta
from rich import print
import sly

from graphviz import Digraph


class Visitor(metaclass=multimeta):
  ...


# =====================================================================
# Arbol de Sintaxis Abstracto
#

@dataclass
class Node:
  def accept(self, v:Visitor, *args, **kwargs):
    return v.visit(self, *args, **kwargs)

@dataclass
class Expression(Node):
  ...

@dataclass
class Number(Expression):
  value : int

@dataclass
class Binary(Expression):
  op    : str
  left  : Expression
  right : Expression

@dataclass
class Factorial(Expression):
    expr: Expression

@dataclass
class FunctionCall(Expression):
    func_name: str
    expr: Expression

@dataclass
class Assignment(Node):
  variable: str
  expr: Expression

  def accept(self, v: Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

@dataclass
class Variables:
  _vars = {'pi': math.pi, 'e': math.e}

  @classmethod
  def get(cls, name):
      return cls._vars.get(name)

  @classmethod
  def set(cls, name, value):
      cls._vars[name] = value

# =====================================================================
# Evalua la expression aritmentica
#
class Eval(Visitor):
  @classmethod
  def eval(cls, n:Node):
    vis = cls()
    return n.accept(vis)

  def visit(self, n:Number):
    return n.value
  
  def visit(self, n:Binary):
    left  = n.left.accept(self)
    right = n.right.accept(self)

    if n.op == '^':
      return left ** right
    else:
      return eval(f'{left} {n.op} {right}')
    
  def visit(self, n: Factorial):
      expr_val = n.expr.accept(self)
      return math.factorial(expr_val)

  def visit(self, n: FunctionCall):
    if n.func_name == 'sin':
        return math.sin(n.expr.accept(self))
    elif n.func_name == 'cos':
        return math.cos(n.expr.accept(self))
    elif n.func_name == 'asin':
        return math.asin(n.expr.accept(self))
    elif n.func_name == 'acos':
        return math.acos(n.expr.accept(self))
    elif n.func_name == 'atan':
        return math.atan(n.expr.accept(self))
    elif n.func_name == 'log':
        return math.log(n.expr.accept(self))
    elif n.func_name == 'random':
        return random.random()

  def visit(self, n: Assignment):
        value = n.expr.accept(self)
        Variables.set(n.variable, value)
        return value


# =====================================================================
# Dibuja el AST
#
class Dot(Visitor):
  node_defaults = {
    'shape' : 'box',
    'color' : 'cyan',
    'style' : 'filled',
  }
  edge_defaults = {
    'arrowhead' : 'none',
  }

  def __init__(self):
    self.dot = Digraph('AST')
    self.dot.attr('node', **self.node_defaults)
    self.dot.attr('edge', **self.edge_defaults)
    self.seq = 0
  
  def __str__(self):
    return self.dot.source
  
  def __repr__(self):
    return self.dot.source

  def name(self):
    self.seq += 1
    return f'n{self.seq:02d}'

  @classmethod
  def render(cls, n:Node):
    dot = cls()
    n.accept(dot)
    return dot.dot
  
  def visit(self, n:Number):
    name = self.name()
    self.dot.node(name, label=f'{n.value}')
    return name
  
  def visit(self, n:Binary):
    name = self.name()
    left  = n.left.accept(self)
    right = n.right.accept(self)
    self.dot.node(name, label=f'{n.op}', shape='circle', color='bisque')
    self.dot.edge(name, left)
    self.dot.edge(name, right)
    return name
  
  def visit(self, n:Assignment):
    name = self.name()
    self.dot.node(name, label=f'Assignment\nVariable: {n.variable}')
    expr_name = n.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name

  def visit(self, n:FunctionCall):
    name = self.name()
    self.dot.node(name, label=f'FunctionCall\nFunction: {n.func_name}')
    expr_name = n.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name


# =====================================================================
# Analizador léxico
#
class Lexer(sly.Lexer):
  tokens = {
    NUMBER,
    FUNCTION,
    CONSTANT,
    IDENTIFIER
  }
  literals = '+-*/()$%^!=;'
  
  ignore = ' \t'
  
  @_(r'\d+')
  def NUMBER(self, t):
    t.value = int(t.value)
    return t
  
  @_(r'(sin|cos|asin|acos|atan|log|random)')
  def FUNCTION(self, t):
      return t

  @_(r'pi|e')  # Agrega aquí tus constantes
  def CONSTANT(self, t):
      constant_value = Variables.get(t.value)
      if constant_value is not None:
          t.type = 'NUMBER'
          t.value = constant_value
      return t
  
  @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
  def IDENTIFIER(self, t):
      return t  # Mantén el identificador tal como está

# =====================================================================
# Analizador sintáctico
#
class Parser(sly.Parser):
  debugfile='calc.txt'
  
  tokens = Lexer.tokens

  @_("IDENTIFIER '=' expr ';'")
  def assignment(self, p):
    return Assignment(p.IDENTIFIER, p.expr)
  
  @_("term '+' expr", "term '-' expr")
  def expr(self, p):
    return Binary(p[1], p.term, p.expr)

  @_("term")
  def expr(self, p):
    return p.term

  @_("factor '*' term", "factor '/' term", "factor '%' term", "factor '^' term")
  def term(self, p):
    return Binary(p[1], p.factor, p.term)
  
  @_("factor '!'")
  def term(self, p):
    return Factorial(p.factor)

  @_("factor")
  def term(self, p):
    return p.factor

  @_("NUMBER")
  def factor(self, p):
    return Number(p.NUMBER)
  
  @_("FUNCTION '(' ')'")
  def factor(self, p):
      return FunctionCall(p.FUNCTION, None)

  @_("FUNCTION '(' term ')'")
  def factor(self, p):
      return FunctionCall(p.FUNCTION, p.term)
  
  @_("FUNCTION '(' expr ')'")
  def factor(self, p):
      return FunctionCall(p.FUNCTION, p.expr)
  
  @_("CONSTANT")
  def factor(self, p):
      return Number(p.CONSTANT.value)
   
  @_("'(' expr ')'")
  def factor(self, p):
    return p.expr
  
  

 
code = 'x = 4 + e;'
 
lex = Lexer()
pas = Parser()
 
ast = pas.parse(lex.tokenize(code))
 
dot = Dot.render(ast)
print(dot)

print(Eval.eval(ast))