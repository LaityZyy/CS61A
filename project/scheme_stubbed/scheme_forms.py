from scheme_eval_apply import *
from scheme_utils import *
from scheme_classes import *
from scheme_builtins import *

#################
# Special Forms #
#################

"""
How you implement special forms is up to you. We recommend you encapsulate the
logic for each special form separately somehow, which you can do here.
"""


# Each of the following do_xxx_form functions takes the cdr of a special form as
# its first argument---a Scheme list representing a special form without the
# initial identifying symbol (if, lambda, quote, ...). Its second argument is
# the environment in which the form is to be evaluated.


# BEGIN PROBLEM 1/2/3
"*** YOUR CODE HERE ***"

def do_define_form(expressions, env):
    """Evaluate a define form
        比如
        [x 2]
        就是把2给x
    """

    validate_form(expressions, 2) #确保expressions是一个长度至少为二的list
    signature = expressions.first
    if scheme_symbolp(signature):   #第一种情况就是说简单的赋值
        validate_form(expressions, 2, 2)    #确保正好长度为二
        env.define(signature, scheme_eval(expressions.rest.first, env)) #绑定一下
        return signature
    elif isinstance(signature, Pair):   #来函数了
        #比如    (define (f x y) (+ x y))
        symbol, formals, body = signature.first, signature.rest, expressions.rest                   #symbol就是名字  formals是形参  body是动作
        env.define(symbol, do_lambda_form(Pair(formals, body), env)) #绑定，并变成lambda形式，我们所有的函数最后都变成lambda的形式
        return symbol
    else:
        #啥也不是，出错了
        bad_signature = signature.first if isinstance(signature, Pair) else signature
        raise SchemeError('no-symbol: {0}'.format(bad_signature))
    

def do_quote_form(expressions, env):
    """Evaluate a quote form"""

    validate_form(expressions, 1, 1)
    return expressions.first           #很简洁，但是比太好想吧


def do_begin_form(expressions, env):
    """
    我理解的就是对所有东西都算一遍但是只要最后一个，就完美契合了eval_all
    """
    validate_form(expressions, 1)
    return eval_all(expressions, env)


def do_lambda_form(expression, env):
    """无需多言"""
    validate_form(expression, 2)     #至少两个的list，那必然，一个形参，一个动作
    formals = expression.first       #形参
    validate_formals(formals)        #参数不要撞车，不然有歧义
    body = expression.rest
    return LambdaProcedure(formals, body, env)      #lambda是一个操作的东西嘛，所以用procedure

def do_if_form(expressions, env):
    validate_form(expressions, 2, 3)    #if是这样的
    if is_scheme_true(scheme_eval(expressions.first, env)):
        return scheme_eval(expressions.rest.first, env, tail = True)
    elif len(expressions) == 3:   #他得有第三个参数才能执行啊
        return scheme_eval(expressions.rest.rest.first, env, tail = True)


def do_and_form(expressions, env):
    if expressions is nil:
        return True
    while expressions is not nil:       #为啥要循环，可能是这样的 a and b and c......
        res = scheme_eval(expressions.first, env, True if expressions.rest is nil else False)
        if is_scheme_false(res):
            return res
        expressions = expressions.rest
    return res


def do_or_form(expressions, env):
    if expressions is nil:
        return False
    while expressions is not nil:       #为啥要循环，可能是这样的 a and b and c......
        res = scheme_eval(expressions.first, env, True if expressions.rest is nil else False)
        if is_scheme_true(res):
            return res
        expressions = expressions.rest
    return res


def do_cond_form(expressions, env):
    """
        什么时候条件为真就返回
    """
    #挺清晰的，不用注释
    while expressions is not nil:
        clause = expressions.first
        validate_form(clause, 1)
        if clause.first == 'else':
            test = True
            if expressions.rest != nil:
                raise SchemeError('else must be last')
        else:
            test = scheme_eval(clause.first, env)
        if is_scheme_true(test):
            if clause.rest != nil:
                test = eval_all(clause.rest, env)
            return test
        expressions = expressions.rest


def do_let_form(expressions, env):
    """
    let大概就是先赋值，再计算
    """
    validate_form(expressions, 2)
    let_env = make_let_frame(expressions.first, env)            #那我们就得做一个let_env      first是这种（x 2）
    return eval_all(expressions.rest, let_env)                 #rest就是一堆操作，要实施在let_env上

def make_let_frame(bindings, env):
    """Create a child frame of Frame ENV that contains the definitions given in
    BINDINGS. The Scheme list BINDINGS must have the form of a proper bindings
    list in a let expression: each item must be a list containing a symbol
    and a Scheme expression."""
    #我们肯定是要调用env的make_child_frame
    #那就需要把bindings搞成两个数组!!!!!!

    if not scheme_listp(bindings):
        raise SchemeError('bad bindings list in let form')
    names, vals = nil, nil
    while bindings is not nil:
        bind = bindings.first
        validate_form(bind, 2, 2)
        symbol, exp = bind.first, bind.rest.first
        names = Pair(symbol, names)
        vals = Pair(scheme_eval(exp, env), vals)
        bindings = bindings.rest
    validate_formals(names)
    return env.make_child_frame(names, vals)


def do_define_macro(expressions, env):
    """Evaluate a define-macro form.

    >>> env = create_global_frame()
    >>> do_define_macro(read_line("((f x) (car x))"), env)
    'f'
    >>> scheme_eval(read_line("(f (1 2))"), env)
    1
    """
    # BEGIN PROBLEM OPTIONAL_1
    "*** YOUR CODE HERE ***"
    validate_form(expressions,2) # Checks that expressions is a list of length at least 2
    target = expressions.first # ((f x) (car x)) -> (f x)
    if isinstance(target, Pair) and scheme_symbolp(target.first):
        f_name = target.first # (f x) -> f
        validate_formals(target.rest)
        f_function = LambdaProcedure(target.rest,expressions.rest,env)
        env.define(f_name, f_function)
        return f_name
    else:
        bad_target = target.first if isinstance(target,Pair) else target
        raise SchemeError('non-symbol: {0}'.format(bad_target))
    # END PROBLEM OPTIONAL_1




def do_mu_form(expressions, env):
    """
    他就是动态的作用域
    查找值的时候他的父框架是调用它的那个，而不知他被定义的地方，这时候能规避一些未定义的行为
    其他的跟lambda一样
    """
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    return MuProcedure(formals, expressions.rest)



# END PROBLEM 1/2/3


def do_quasiquote_form(expressions, env):
    """Evaluate a quasiquote form with parameters EXPRESSIONS in
    Frame ENV."""
    def quasiquote_item(val, env, level):
        """Evaluate Scheme expression VAL that is nested at depth LEVEL in
        a quasiquote form in Frame ENV."""
        if not scheme_pairp(val):
            return val
        if val.first == 'unquote':
            level -= 1
            if level == 0:
                expressions = val.rest
                validate_form(expressions, 1, 1)
                return scheme_eval(expressions.first, env)
        elif val.first == 'quasiquote':
            level += 1

        return val.map(lambda elem: quasiquote_item(elem, env, level))

    validate_form(expressions, 1, 1)
    return quasiquote_item(expressions.first, env, 1)


def do_unquote(expressions, env):
    raise SchemeError('unquote outside of quasiquote')



SPECIAL_FORMS = {
    'and': do_and_form,
    'begin': do_begin_form,
    'cond': do_cond_form,
    'define': do_define_form,
    'if': do_if_form,
    'lambda': do_lambda_form,
    'let': do_let_form,
    'or': do_or_form,
    'quote': do_quote_form,
    'define-macro': do_define_macro,
    'quasiquote': do_quasiquote_form,
    'unquote': do_unquote,
    'mu': do_mu_form,
}