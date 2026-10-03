[![Run on Repl.it](https://repl.it/badge/github/phillipjohnson/text-adventure-tut)](https://repl.it/github/phillipjohnson/text-adventure-tut)
Overview
-------
This project was developed as a response to the large number of beginning Python developer who want to learn how to write a text adventure.

Although there are many approaches, this project is designed to be expandable with "pluggable" elements.

Tutorial
--------
For an in-depth tutorial, please see [How to Write a Text Adventure in Python](http://letstalkdata.com/2014/08/how-to-write-a-text-adventure-in-python/).

Tests
-----
The `tests/` directory contains parametrized tests that record the final state
of scripted input sequences (victory path, failure path, repeated visits,
illegal actions and item pickup rules) for the main map and the mini levels in
`tests/maps/`. Run them from the repository root with:

    python3 -m pytest tests/
