<h1 align="center">Pete and Repeat</h1>

<p align="center">
  Love the Python REPL?</br>
  Hate that you can't write real software in a Jupyter Notebook?</br>
  Well do I have the project for you.</br>
</p>

<p align="center">
  <img width="600" src="https://raw.githubusercontent.com/thmsmlr/pnrp/master/assets/demo.svg">
</p>

Pete and Repeat (pnrp) brings all the goodness of the REPL and Jupyter Notebooks to your regular old Python projects.
It kind of works like [Observable](https://observablehq.com) but for Python from the CLI.

To get started run,

```
 $ pip install pnrp
 $ python -m pnrp <my_script>.py
```

pnrp will run your script to completion just as the regular Python interpreter.
Instead of exiting though, it'll monitor every line of code executed for changes.
When a line of code changes, it will rerun **ONLY** the statements that have changed, and their dependent statements.
We are able to do this by monitoring the files of any imported module, analyzing the AST of the code to be executed, and tracking dependencies between statements.
This is of course no silver bullet, Python is a highly dynamic language and there are situations when this won't work.
That is why we'll provide you an escape hatch to rerun from specific points in your script onward.

## How it works, by example

Suppose we have a python program

```python
# Script at time t

data = open('some-big-file.txt', 'r').read()
print(len(data))
```

We then modify the script,

```python
# Script at time t+1
import re

expr = re.compile('Pete (and)? repeat')

data = open('some-big-file.txt', 'r').read()
lines = data.split('\n')
print(len([x for x in lines if expr.match(x)]))
```

Rerunning the script normally would cause our machine to reread `some-big-file.txt` on each iteration.
With pnrp, we intelligently look at your code to see that line 6 is unaltered so we cache the computation and only run the lines that were changed.


## Feature Comparison


|                  | Live Kernel  | Graphics Support | Multi-file Reloading | Bring your own Editor | Normal Execution Order |
|:----------------:|:------------:|:----------------:|:--------------------:|:---------------------:|:----------------------:|
| REPL             |       X      |                  |                      |                       |            X           |
| Jupyter Notebook |       X      |         X        |                      |                       |                        |
| PNRP             |       X      |         X        |           X          |           X           |            X           |


## TODO

- [ ] Multi-file / import support
- [X] AST Based statement parsing
- [X] AST Dependency based rerun
- [ ] Explore [`sys.settrace`](https://docs.python.org/3/library/sys.html#sys.settrace) for code dependencies
- [ ] Pretty printing
- [ ] Server / Client model ?? (to better support interactivity, interrupts, etc.)
