import os
import sys
import time
import importlib
import subprocess
import multiprocessing
import itertools
import ast
import traceback
import difflib

from typing import List


class ANSI:
    BLACK = '\u001b[30m'
    RED = '\u001b[31m'
    GREEN = '\u001b[32m'
    YELLOW = '\u001b[33m'
    BLUE = '\u001b[34m'
    MAGENTA = '\u001b[35m'
    CYAN = '\u001b[36m'
    WHITE = '\u001b[37m'
    DIM = '\u001b[2m'
    RESET = '\u001b[0m'


prompt = lambda *args: print(ANSI.DIM + '>', *args, ANSI.RESET)
eprint = lambda *args: print(*args, file=sys.stderr)


def filewatcher(fpath):
    fullfpath = os.path.join(os.getcwd(), fpath)
    mtime = None
    while True:
        try:
            nmtime = os.stat(fullfpath).st_mtime
        except:
            continue

        if mtime != nmtime:
            mtime = nmtime

            if os.path.exists(fullfpath):
                yield fullfpath

        time.sleep(0.5)


def compare_ast(node1, node2):
    if type(node1) != type(node2):
        return False
    elif isinstance(node1, ast.AST):
        for kind, var in vars(node1).items():
            if kind not in ('lineno', 'col_offset', 'ctx'):
                var2 = vars(node2).get(kind)
                if not compare_ast(var, var2):
                    return False
        return True
    elif isinstance(node1, list):
        if len(node1) != len(node2):
            return False
        for i in range(len(node1)):
            if not compare_ast(node1[i], node2[i]):
                return False
        return True
    else:
        return node1 == node2


def exprs_to_run(curr_ast: List['Expression'], next_ast: List['Expression']):
    """Return the minimal list of statements to run to get the execution
    of curr_ast to match a clean execution of next_ast.

    For each expression that has changed, we see which global variables it changes via
    assignment, then recursively apply that logic to every unchanged statment that uses
    the changes variables.

    This culminates in a list of expressions that have been directly changed, or are
    affected by a changed expression.

    WARNING: This does not account for mutations or side effects. It encourages you
    to write simple code. Any side-effectful code should be wrapped in a function to
    scope it's side effects. Local mutation is okay!

    We will support an escape hatch to explicitly rerun side effectful code.
    """
    # Calculate the new or changed statements to be run
    changed_exprs = []
    curr_code_exprs = [ast.unparse(x) for x in curr_ast]
    next_code_exprs = [ast.unparse(x) for x in next_ast]
    diff = difflib.SequenceMatcher(a=curr_code_exprs, b=next_code_exprs)
    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        if tag == 'replace':
            changed_exprs.append(next_ast[j1:j2])
        if tag == 'insert':
            changed_exprs.append(next_ast[j1:j2])

    changed_exprs = [x for slst in changed_exprs for x in slst]

    def extract_assignments(expr):
        if isinstance(expr, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return [expr.name]
        elif isinstance(expr, (ast.Assign,)):
            return [extract_assignments(sexpr) for sexpr in expr.targets]
        elif isinstance(expr, (ast.Name,)):
            return expr.id
        elif isinstance(expr, (ast.List, ast.Tuple)):
            return [extract_assignments(sexpr) for sexpr in expr.elts]

        return []

    # Extract the global variables that will change directly
    # as a result of the code changes
    changed_names = set()
    for expr in changed_exprs:
        changed_names |= set(extract_assignments(expr))

    # Select every expression that either directly changed itself
    # or, depends on a global variable that was changed, recursively.
    exprs = []
    for expr in next_ast:
        if expr in changed_exprs:
            exprs.append(expr)
            continue

        co = compile(ast.unparse(expr), '<string>', 'exec')
        names = set(co.co_names)
        if names & changed_names:
            exprs.append(expr)
            changed_names |= set(extract_assignments(expr))

    return exprs


def driver(fpath, args):
    curr_ast = []
    gvars, lvars = {}, {}
    for _ in filewatcher(fpath):
        srccode = open(fpath, 'r').read()
        modname, _ = fpath.rsplit('.', 1)

        next_ast = ast.parse(srccode).body
        exprs = exprs_to_run(curr_ast, next_ast)

        if not exprs:
            prompt('File saved, but nothing to run')
            continue

        prompt(fpath, 'Changed!')

        for expr in exprs:
            exprstr = ast.get_source_segment(srccode, expr)
            code = compile(exprstr, modname, 'exec')
            try:
                exec(code, gvars)
            except:
                traceback.print_exc()
                break

        curr_ast = next_ast


def cli(fpath, args):
    driver(fpath, args)
