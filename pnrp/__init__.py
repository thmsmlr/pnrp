import os
import sys
import time
import importlib
import subprocess
import multiprocessing
import itertools

class ANSI:
    BLACK   = '\u001b[30m'
    RED     = '\u001b[31m'
    GREEN   = '\u001b[32m'
    YELLOW  = '\u001b[33m'
    BLUE    = '\u001b[34m'
    MAGENTA = '\u001b[35m'
    CYAN    = '\u001b[36m'
    WHITE   = '\u001b[37m'
    DIM     = '\u001b[2m'
    RESET   = '\u001b[0m'

prompt = lambda *args: print(ANSI.DIM + '>', *args, ANSI.RESET)

def sh(cmd):
    process = subprocess.Popen(cmd.split())
    output, error = process.communicate()
    return output

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


def driver(fpath, args):
    exprs_hist = []
    gvars, lvars = {}, {}
    for _ in filewatcher(fpath):
        file = open(fpath, 'r').read()
        modname, _ = fpath.rsplit('.', 1)

        # TODO: replace with proper AST parsing
        exprs = [x for x in file.split('\n') if x]
        diff_idx = next((idx for idx, (a,b) in enumerate(itertools.zip_longest(exprs, exprs_hist)) if a != b), -1)

        if diff_idx == -1:
            prompt('File saved, but no changed detected')
            continue
        elif not exprs_hist:
            prompt('Running', fpath)
            diff_idx = 0 # First run, go from start
        else:
            prompt(fpath, 'Changed!')

        for expr in exprs[diff_idx:]:
            code = compile(expr, modname, 'exec')
            exec(code, gvars, lvars)

        exprs_hist = exprs





def cli(fpath, args):
    driver(fpath, args)
