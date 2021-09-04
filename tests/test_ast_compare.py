import ast
import inspect
import pnrp


def str2ast(x):
    return ast.parse(inspect.cleandoc(x))


def test_ast_compare_same():
    a = str2ast("""
        a = 1
    """)
    b = str2ast("""
        a = 1
    """)

    assert pnrp.compare_ast(a, b) == True


def test_ast_compare_same_recursive():
    a = str2ast("""
    def foo():
        a = 1
    """)
    b = str2ast("""
    def foo():
        a = 1
    """)

    assert pnrp.compare_ast(a, b) == True


def test_ast_compare_diff():
    a = str2ast("""
        a = 1
    """)
    b = str2ast("""
        b = 1
    """)

    assert pnrp.compare_ast(a, b) == False


def test_ast_compare_diff_top_level():
    a = str2ast("""
    def foo():
        a = 1
    """)
    b = str2ast("""
    def bar():
        a = 1
    """)

    assert pnrp.compare_ast(a, b) == False


def test_ast_compare_diff_top_nested():
    a = str2ast("""
    def foo():
        a = 1
    """)
    b = str2ast("""
    def foo():
        b = 1
    """)

    assert pnrp.compare_ast(a, b) == False
