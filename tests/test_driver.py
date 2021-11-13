import pnrp
import inspect


def test_driver_basic():
    gvars = {}
    fchanges = [
        """
            a = 'hello'
        """, """
            a = 'hello'
            print(a)
            a *= 2
        """
    ]

    fchanges = [('run.py', inspect.cleandoc(x)) for x in fchanges]
    pnrp.driver(fchanges, gvars=gvars)

    assert gvars['a'] == 'hellohello'


def test_driver_syntax_error():
    """Should continue on after syntax errors"""
    gvars = {}
    fchanges = [
        """
            a = 'hello'
        """, """
            a = 'hello'
            b = # Syntax Error
            a = 'world'
            print(a)
        """, """
            a = 'hello'
            a = 'world'
            print(a)
        """
    ]

    fchanges = [('run.py', inspect.cleandoc(x)) for x in fchanges]
    pnrp.driver(fchanges, gvars=gvars)

    assert gvars['a'] == 'world'


def test_driver_exception():
    """Should continue on after exception"""
    gvars = {}
    fchanges = [
        """
            a = 'hello'
        """, """
            a = 'hello'
            raise 'foo'
            a = 'world'
        """, """
            a = 'hello'
            a = 'world'
        """
    ]

    fchanges = [('run.py', inspect.cleandoc(x)) for x in fchanges]
    pnrp.driver(fchanges, gvars=gvars)

    assert gvars['a'] != 'hello'
    assert gvars['a'] == 'world'
