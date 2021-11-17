import pnrp
import inspect


def test_runstate_simple():
    gvars = {}
    states = []
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
    pnrp.driver(fchanges, gvars=gvars, flush_runstate=lambda xs: states.append('\n'.join(xs)))

    # Expected States represents too loops through
    #    change, run, complete
    #    change, run, complete
    expected_states = inspect.cleandoc(
        """
    ~
    ---
    >>
    ---
    .
    ---
    ~
    ~
    ~
    ---
    >>
    ~
    ~
    ---
    ~
    >>
    ~
    ---
    ~
    ~
    >>
    ---
    .
    .
    .
    """
    ).split('---')
    expected_states = [inspect.cleandoc(x) for x in expected_states]

    assert gvars['a'] == 'hellohello'
    assert states == expected_states
