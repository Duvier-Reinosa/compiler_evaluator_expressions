# Calculator with Lexer, Parser, and Evaluator

This Python program is a basic calculator that can handle single-line mathematical expressions. It features a lexer, parser, and evaluator, and it utilizes the visitor pattern for abstract syntax tree (AST) traversal. Additionally, it offers a convenient way to visualize the AST using the Graphviz extension for Visual Studio Code.

## Table of Contents

- [Usage](#usage)
  - [Adding Code](#adding-code)
  - [Running the Program](#running-the-program)
  - [Visualizing the AST](#visualizing-the-ast)
- [How It Works](#how-it-works)
- [Dependencies](#dependencies)
- [Graphviz Extension](#graphviz-extension)
- [License](#license)

## Usage

### Adding Code

To use the calculator, follow these steps:

1. Open the `calc.py` file in your code editor.

2. Locate the `code` variable within the file.

3. Assign your mathematical expression as a string to the `code` variable. For example:

```python
code = 'x = 4 + e;'
