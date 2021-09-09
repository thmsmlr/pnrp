"""
Test the ast diffing engine to tell us which statements should be executed.
These tests are generally of the form,

    diff(curr_ast, next_ast) == statements to execute

"""

import ast
import inspect
import pnrp


def str2ast(x):
    return ast.parse(inspect.cleandoc(x)).body


def ast2str(x):
    return ast.unparse(x)


def test_nothing_to_run():
    curr_ast = str2ast("""
        a = 1
    """)
    next_ast = str2ast("""
        a = 1
    """)

    to_run = pnrp.exprs_to_run(curr_ast, next_ast)

    assert to_run == []


def test_run_everything_after():
    curr_ast = str2ast("""
        a = 1
    """)
    next_ast = str2ast("""
        a = 1
        b = 2
        c = 3
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("""
        b = 2
        c = 3
    """)


def test_run_everything_after_function():
    curr_ast = str2ast("""
        a = 1
    """)
    next_ast = str2ast(
        """
        a = 1
        def foo(x):
            return x + 1
        foo(a)
    """
    )

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc(
        """
        def foo(x):
            return x + 1
        foo(a)
    """
    )


def test_rerun_dependent_exprs():
    curr_ast = str2ast(
        """
        a = 1
        def foo(x):
            return x + 1
        foo(a)
    """
    )
    next_ast = str2ast(
        """
        a = 1
        def foo(x):
            return x + 2
        foo(a)
    """
    )

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc(
        """
        def foo(x):
            return x + 2
        foo(a)
    """
    )


def test_rerun_dependent_exprs_assign():
    curr_ast = str2ast(
        """
        a = 1
        def foo(x):
            return x + 1
        foo(a)
    """
    )
    next_ast = str2ast(
        """
        a = 2
        def foo(x):
            return x + 1
        foo(a)
    """
    )

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("""
        a = 2
        foo(a)
    """)


def test_rerun_grand_dependent_exprs_assign():
    curr_ast = str2ast(
        """
        a = 1
        b = 2
        c = a + b
        d = c + 1
        e = b + 1
    """
    )
    next_ast = str2ast(
        """
        a = 2
        b = 2
        c = a + b
        d = c + 1
        e = b + 1
    """
    )

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc(
        """
        a = 2
        c = a + b
        d = c + 1
    """
    )


def test_run_independent_new_exprs_only():
    curr_ast = str2ast("""
        a = 1
    """)
    next_ast = str2ast("""
        import time
        a = 1
        time.sleep(1)
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("""
        import time
        time.sleep(1)
    """)


def test_handles_all_assignments():
    curr_ast = str2ast("")
    next_ast = str2ast("""
        a = 1
        (a, b) = (2, 3)
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("""
        a = 1
        (a, b) = (2, 3)
    """)


def test_handles_print_delete_and_readd():
    curr_ast = str2ast("""
        a = 1
        print(a)
    """)
    next_ast = str2ast("""
        a = 2
        print(a)
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("""
        a = 2
        print(a)
    """)

    curr_ast = next_ast
    next_ast = str2ast("""
        a = 2
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("")

    curr_ast = next_ast
    next_ast = str2ast("""
        a = 2
        print(a)
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc("""
        print(a)
    """)


def test_handles_aug_assign():
    curr_ast = str2ast("""
        a = 1
        print(a)
    """)
    next_ast = str2ast("""
        a = 1
        print(a)
        a += 2
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs
                  ) == inspect.cleandoc("""
        a = 1
        print(a)
        a += 2
    """)


def test_handles_ann_assign():
    curr_ast = str2ast("""
        a = 1
        print(a)
    """)
    next_ast = str2ast("""
        a = 1
        print(a)
        a: int = 2
    """)

    exprs = pnrp.exprs_to_run(curr_ast, next_ast)

    assert ast2str(exprs) == inspect.cleandoc(
        """
        a = 1
        print(a)
        a: int = 2
    """
    )
