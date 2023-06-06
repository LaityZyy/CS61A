import operator
import sys
import os

from pair import *
from scheme_utils import *
from ucb import main, trace

import scheme_forms

##############
# Eval/Apply #
##############


def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.                                     在环境env里找一下expr

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # BEGIN Problem 1/2
    "*** YOUR CODE HERE ***"
    # Evaluate atoms             （就一个东西，数字啊加减乘除啊变量啊之类的，那找一下返回就行了）
    if scheme_symbolp(expr):     #如果他是一个变量啊,就是说他绑定了一个值，去Frame里找一下
        return env.lookup(expr)
    elif self_evaluating(expr):  #数字啊加减乘除啊，直接就能返回的东西，那直接返回
        return expr
    
    # All non-atomic expressions are lists (combinations) （是个组合，那就得费劲搞一下了）
    if not scheme_listp(expr):    #传进来的东西错了
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest
    if scheme_symbolp(first) and first in scheme_forms.SPECIAL_FORMS:#如果开头是那几种特殊的    if cond cons list define ......
        return scheme_forms.SPECIAL_FORMS[first](rest, env)          #特殊处理
    else:
        #否则就是加减乘除或一些函数一些常规的了
        operator = scheme_eval(first, env)                 #看一下是什么运算
        validate_procedure(operator)                       #错误检查  看看谁不是有效的Scheme运算                   
        oprands = rest.map(lambda x: scheme_eval(x, env))  #求一下后面的，然后应用operator
        return scheme_apply(operator, oprands, env)
    # END Problem 1/2


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    # BEGIN Problem 1/2
    "*** YOUR CODE HERE ***"
    validate_procedure(procedure)        #看一下是不是有效的运算
    if not isinstance(env, Frame):
        assert False, "Not a Frame: {}".format(env)  #env必须得是一个框架
    if isinstance(procedure, BuiltinProcedure):  #内置的运算，好，太好了
        arg = []           #args是一个链表，不好操作，我们把它变成一个数组
        while args is not nil:
            arg.append(args.first)
            args = args.rest
        try:
            if procedure.need_env:                    #可能有的运算和当前框架有关吧
                return procedure.py_func(*arg, env)
            else:
                return procedure.py_func(*arg)
        except TypeError as err:
            raise SchemeError('incoeeect number of arguments: {0}'.format(procedure))
    elif isinstance(procedure, LambdaProcedure):    #是一个lambda
        env_new = procedure.env.make_child_frame(procedure.formals, args)         #lambda嘛，他得开一个新Frame   formals是他需要的参数    args是给的值，在新框架中会绑定好
        return eval_all(procedure.body, env_new)                                  #body 就是具体的计算方法了
    elif isinstance(procedure, MuProcedure):                                      #还不知道是什么，牛？离谱，再看吧
        env_new = env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, env_new)
    else:
        assert False, "Unexpected procedure: {}".format(procedure)
    # END Problem 1/2


def eval_all(expressions, env):
    """Evaluate each expression in the Scheme list EXPRESSIONS in
    Frame ENV (the current environment) and return the value of
    the last.
    
    太抽象了，加一些例子吧

    >>> eval_all(read_line("(1)"), create_global_frame())
    1
    >>> eval_all(read_line("(1 2)"), create_global_frame())
    2
    >>> x = eval_all(read_line("((print 1) 2)"), create_global_frame())
    1
    >>> x
    2
    >>> eval_all(read_line("((define x 2) x)"), create_global_frame())
    2

    看了例子也看不懂啊。。。。。。！！！！！！

    大概就是对环境里的一些东西做操作，然后返回最后一个
    """
    if expressions is nil:
        return None
    
    while expressions.rest is not nil:
        eval_res = scheme_eval(expressions.first, env)
        expressions = expressions.rest
    eval_res = scheme_eval(expressions.first, env, tail = True)
    return eval_res


##################
# Tail Recursion #
##################


#这个尾递归就是说如果tail = True，那就用尾递归的方法求值

#他有什么好处呢？就是递归的时候扔一些Frame避免爆栈

#常见的方法就是把当前的计算结果传下去而不是等之后的过来

# Make classes/functions for creating tail recursive programs here!
# BEGIN Problem EC
"*** YOUR CODE HERE ***"

class Unevaluated:
    """An expression and an environment in which it is to be evaluated."""

    def __init__(self, expr, env):
        """Expression EXPR to be evaluated in Frame ENV"""
        self.expr = expr
        self.env = env

# END Problem EC


def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not Unevaluated.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    validate_procedure(procedure)
    # BEGIN
    val = scheme_apply(procedure, args, env)
    if isinstance(val, Unevaluated):
        return scheme_eval(val.expr, val.env)
    else:
        return val
    # END



def optimize_tail_call(unoptimized_scheme_eval):
    """Return a properly tail recursive version of an eval function"""
    def optimized_eval(expr, env, tail = False):
        """Evaluate Scheme expression EXPR in Frame ENV. If TAIL,
        return an Unevaluated containing an expression for further evaluation.
        """
        if tail and not scheme_symbolp(expr) and not self_evaluating(expr):
            return Unevaluated(expr, env)
        
        result = Unevaluated(expr, env)

        while isinstance(result, Unevaluated):
            result = unoptimized_scheme_eval(result.expr,result.env)
        return result
    return optimized_eval



################################################################
# Uncomment the following line to apply tail call optimization #
################################################################


scheme_eval = optimize_tail_call(scheme_eval)



class MacroProcedure(LambdaProcedure):
    """A macro: a special form that operates on its unevaluated operands to
    create an expression that is evaluated in place of a call."""

    def apply_macro(self, operands, env):
        """Apply this macro to the operand expressions."""
        return complete_apply(self, operands, env)