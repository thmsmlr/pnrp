import os
import os.path
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
HOME_DIR = os.path.expanduser('~/.pnrp')


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
                yield fullfpath, open(fullfpath, 'r').read()

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
    curr_code_exprs = [ast.dump(x, include_attributes=False) for x in curr_ast]
    next_code_exprs = [ast.dump(x, include_attributes=False) for x in next_ast]
    diff = difflib.SequenceMatcher(a=curr_code_exprs, b=next_code_exprs)
    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        if tag == 'replace':
            changed_exprs.append(next_ast[j1:j2])
        if tag == 'insert':
            changed_exprs.append(next_ast[j1:j2])

    changed_exprs = [x for slst in changed_exprs for x in slst]

    def extract_assignments(expr):
        """Given an expression, extract all the top-level variable reassignments
        that occur. A list of all assignment syntax can be found at

        https://docs.python.org/3/library/ast.html#abstract-grammar
        """
        if isinstance(expr, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return [expr.name]
        elif isinstance(expr, (ast.Assign,)):
            return [expr for sexpr in expr.targets for expr in extract_assignments(sexpr)]
        elif isinstance(expr, (ast.AugAssign, ast.AnnAssign)):
            return extract_assignments(expr.target)
        elif isinstance(expr, (ast.Name,)):
            return expr.id
        elif isinstance(expr, (ast.List, ast.Tuple)):
            return [expr for sexpr in expr.elts for expr in extract_assignments(sexpr)]

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

        wexpr = ast.Module(body=[expr], type_ignores=[])
        co = compile(wexpr, '<string>', 'exec')
        names = set(co.co_names)
        if names & changed_names:
            exprs.append(expr)
            changed_names |= set(extract_assignments(expr))

    return exprs


def flush_runstate(run_state):
    """Write out the runstate so code editors can read it and
    present the results inline with the code"""
    with open(f'{HOME_DIR}/runstate', 'w') as f:
        f.write('\n'.join(run_state))


def driver(fchanges, gvars=None, flush_runstate=flush_runstate):
    curr_ast = []
    gvars = {} if gvars is None else gvars

    for fpath, srccode in fchanges:
        modname, _ = fpath.rsplit('.', 1)

        # Parse new code, determine which statements to run
        try:
            next_ast = ast.parse(srccode).body
        except SyntaxError:
            traceback.print_exc()
            continue

        exprs = exprs_to_run(curr_ast, next_ast)

        # Print out the state of what needs to be run
        run_state = ['.'] * (srccode.count('\n') + 1)
        for expr in exprs:
            num_lines = 1 + (expr.end_lineno - expr.lineno)
            run_state[expr.lineno - 1:expr.end_lineno] = ['~'] * num_lines  # Mark cahnged

        flush_runstate(run_state)

        # Run the changed expressions
        if not exprs:
            prompt('File saved, but nothing to run')
            curr_ast = next_ast
        else:
            prompt(fpath, 'Changed!')

            for expr in exprs:
                num_lines = 1 + (expr.end_lineno - expr.lineno)
                try:
                    wexpr = ast.Module(body=[expr], type_ignores=[])
                    code = compile(wexpr, modname, 'exec')
                    run_state[expr.lineno - 1:expr.end_lineno] = ['>>'] * num_lines  # Mark running
                    flush_runstate(run_state)
                    exec(code, gvars)
                    run_state[expr.lineno - 1:expr.end_lineno] = ['~'] * num_lines  # Mark complete
                except Exception:
                    run_state[expr.lineno - 1:expr.end_lineno] = ['x'] * num_lines  # Mark failed
                    flush_runstate(run_state)
                    traceback.print_exc()
                    break
            else:
                curr_ast = next_ast
                run_state = ['.'] * (srccode.count('\n') + 1)  # Mark all complete
                flush_runstate(run_state)


def cli(fpath, args):
    del sys.argv[0]
    # Ensure we have a homedir setup
    os.makedirs(HOME_DIR, exist_ok=True)
    driver(filewatcher(fpath))
