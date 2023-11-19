# Binary operation calculator

### Info

Calculates the binary calculation table of the passed expression.

Operators:

    OR      = `|`
    XOR     = `^`
    AND     = `&`
    NOT     = `!`
    RPAREN  = `(`
    RPAREN  = `)`

Operator priority:

    1. `(`, `)`
    2. `!`
    3. `&`
    4. `^`
    5. `|`

Variables:

    any alphabetic characters and numbers without spaces
    exception the word "exit" if it is not in the expression

EBNF:

    expr        : expr_OR EOF
    expr_OR     : expr_XOR (OR expr_XOR)
    expr_XOR    : expr_AND (XOR expr_AND)
    expr_AND    : factor (AND factor)
    factor      : NOT factor | VAR | LPAREN expr_OR RPAREN

    VAR         : (alpha | number) VAR*
    OR          : `|`
    XOR         : `^`
    AND         : `&`
    NOT         : `!`
    RPAREN      : `(`
    RPAREN      : `)`
    EOF         : end-of-file

Сalculator diagram:

```
+-------+ Text   +-------+ Token  +--------+ AST    +------------+
| Input | -----> | Lexer | -----> | Parser | -----> | Сalculator |
+-------+        +-------+        +--------+        +------------+
```

### Prerequisites

Language version starting from Python 3.10+

```bash
$ python --version
Python 3.10.4
```

---

### Usage

```
$ python binary_operation_calculator.py
for exits write: exit

>>> !a
+---+ +-----+
| 1 | | 2   |
| a | | ! a |
+---+ +-----+
| 0 | |  1  |
| 1 | |  0  |
+---+ +-----+

>>> a & (b | !a)
+---+---+ +-----+---------+---------+
| 1 | 2 | | 3   | 4       | 5       |
| a | b | | ! a | b | [3] | a & [4] |
+---+---+ +-----+---------+---------+
| 0 | 0 | |  1  |    1    |    0    |
| 1 | 0 | |  0  |    0    |    0    |
| 0 | 1 | |  1  |    1    |    0    |
| 1 | 1 | |  0  |    1    |    1    |
+---+---+ +-----+---------+---------+

>>> a & b | !a
+---+---+ +-------+-----+-----------+
| 1 | 2 | | 3     | 4   | 5         |
| a | b | | a & b | ! a | [3] | [4] |
+---+---+ +-------+-----+-----------+
| 0 | 0 | |   1   |  0  |     1     |
| 1 | 0 | |   0   |  0  |     0     |
| 0 | 1 | |   1   |  0  |     1     |
| 1 | 1 | |   0   |  1  |     1     |
+---+---+ +-------+-----+-----------+

>>> exit

$
```

---

### Authors

* [Dmitry Volkov](https://github.com/d1mav0lk0v)

---

### Link

* [GitHub](https://github.com/d1mav0lk0v/binary_operation_calculator)

---