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

## Feature Comparison


|                  | Live Kernel  | Graphics Support | Multi-file Reloading | Bring your own Editor | Normal Execution Order |
|:----------------:|:------------:|:----------------:|:--------------------:|:---------------------:|:----------------------:|
| REPL             |       X      |                  |                      |                       |            X           |
| Jupyter Notebook |       X      |         X        |                      |                       |                        |
| PNRP             |       X      |         X        |           X          |           X           |            X           |


## TODO

- [ ] Multi-file / import support
- [ ] AST Based statement parsing
- [ ] AST Dependency based rerun
- [ ] Pretty printing
- [ ] Server / Client model ?? (to better support interactivity, interrupts, etc.)
