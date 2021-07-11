# Pete and Repeat

Love the Python REPL?
Hate that you can't write real software in a Jupyter Notebook?
Well do I have the project for you.

<p align="center">
  <img width="600" src="https://raw.githubusercontent.com/thmsmlr/pnrp/master/assets/demo.svg">
</p>

Pete and Repeat (pnrp) brings all the goodness of the REPL and Jupyter Notebooks to your regular old Python projects.
It kind of works like [Observable](https://observablehq.com) but from the Python from the CLI.

To get started run,

```
 $ pip install pnrp
 $ python -m pnrp <my_script>.py
```

pnrp will run your script to completion just as the regular Python interpreter.
Instead of exiting though, it'll monitor every line of code executed for changes.
When a line of code changes, it will rerun **ONLY** the statements that have changed, or depend on lines that have changed.
We are able to do this by monitoring the files of any imported module, analyzing the AST of the code to be executed, and tracking dependencies between statements.

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
