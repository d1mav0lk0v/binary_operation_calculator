r"""Binary operation calculator.

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

+-------+ Text   +-------+ Token  +--------+ AST    +------------+
| Input | -----> | Lexer | -----> | Parser | -----> | Сalculator |
+-------+        +-------+        +--------+        +------------+

Example (1):
>>> !a
+---+ +-----+
| 1 | | 2   |
| a | | ! a |
+---+ +-----+
| 0 | |  1  |
| 1 | |  0  |
+---+ +-----+

Example (2):
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

Example (3):
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
"""


################################################################################
#                                                                              #
# IMPORTS AND CONSTANTS                                                        #
#                                                                              #
################################################################################


from operator import not_, and_, xor, or_


################################################################################
#                                                                              #
# TOKENS                                                                       #
#                                                                              #
################################################################################


class Token:
    # token type
    LPAREN  = "("
    RPAREN  = ")"
    VAR     = "variable"
    NOT     = "!"
    AND     = "&"
    XOR     = "^"
    OR      = "|"
    EOF     = "EOF"

    SINGLE_CHARACTER_TOKENS = "()!&^|"


    def __init__(self, token_type: str, value: str | None = None) -> None:
        self.type = token_type
        self.value = value


    def __str__(self) -> str:
        return f"Token({self.type}, {self.value})"


################################################################################
#                                                                              #
#  LEXER                                                                       #
#                                                                              #
################################################################################


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0


    def raise_exception(self, msg: str) -> None:
        raise Exception(f"{msg} in pos={self.pos}\n")


    def get_next_token(self) -> Token:
        # skip whitespaces
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

        # end of file
        if self.pos >= len(self.text):
            return Token(Token.EOF)

        # single character tokens
        if self.text[self.pos] in Token.SINGLE_CHARACTER_TOKENS:
            token = Token(self.text[self.pos])
            self.pos += 1
            return token

        # variables
        if self.text[self.pos].isalnum():
            variable = []
            while self.pos < len(self.text) and self.text[self.pos].isalnum():
                variable.append(self.text[self.pos])
                self.pos += 1
            return Token(Token.VAR, "".join(variable))

        self.raise_exception(f"Invalid character `{self.text[self.pos]}`")


################################################################################
#                                                                              #
# ABSTRACT SYNTAX TREE                                                         #
#                                                                              #
################################################################################


class BinaryOperator:
    def __init__(self, token, operator, left, right) -> None:
        self.token = token
        self.operator = operator
        self.left = left
        self.right = right


class UnaryOperator:
    def __init__(self, token, operator, expr) -> None:
        self.token = token
        self.operator = operator
        self.expr = expr


class Variable:
    def __init__(self, token: Token, variable_id: int) -> None:
        self.token = token
        self.id = variable_id


AST = BinaryOperator | UnaryOperator | Variable


################################################################################
#                                                                              #
# PARSER                                                                       #
#                                                                              #
################################################################################


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.variables = dict()


    def eat_token(self, token_type) -> None:
        if self.current_token.type != token_type:
            self.lexer.raise_exception(f"Invalid syntax, expected `{token_type}`")

        self.current_token = self.lexer.get_next_token()


    def factor(self) -> AST:
        """factor : NOT factor | VAR | LPAREN expr_OR RPAREN"""

        token = self.current_token

        if token.type == Token.NOT:
            self.eat_token(Token.NOT)
            return UnaryOperator(token, not_, self.factor())

        if token.type == Token.VAR:
            self.eat_token(Token.VAR)
            return Variable(token,
                self.variables.setdefault(token.value, len(self.variables)))

        if token.type == Token.LPAREN:
            self.eat_token(Token.LPAREN)
            node = self.expr_OR()
            self.eat_token(Token.RPAREN)
            return node

        self.lexer.raise_exception(f"Invalid syntax, expected `factor`")


    def expr_AND(self) -> AST:
        """expr_AND : factor (AND factor)"""

        node = self.factor()

        while self.current_token.type == Token.AND:
            token = self.current_token
            self.eat_token(Token.AND)
            node = BinaryOperator(token, and_, node, self.factor())

        return node


    def expr_XOR(self) -> AST:
        """expr_XOR : expr_AND (XOR expr_AND)"""

        node = self.expr_AND()

        while self.current_token.type == Token.XOR:
            token = self.current_token
            self.eat_token(Token.XOR)
            node = BinaryOperator(token, xor, node, self.expr_AND())

        return node


    def expr_OR(self) -> AST:
        """expr_OP : expr_XOR (OR expr_XOR)"""

        node = self.expr_XOR()

        while self.current_token.type == Token.OR:
            token = self.current_token
            self.eat_token(Token.OR)
            node = BinaryOperator(token, or_, node, self.expr_XOR())

        return node


    def expr(self) -> AST:
        """expr : expr_OR EOF"""
        
        node = self.expr_OR()
        self.eat_token(Token.EOF)

        return node


    def parse(self) -> AST:
        """
        expr        : expr_OR EOF
        expr_OR     : expr_XOR (OR expr_XOR)
        expr_XOR    : expr_AND (XOR expr_AND)
        expr_AND    : factor (AND factor)
        factor      : NOT factor | VAR | LPAREN expr_OR RPAREN
        """

        return self.expr()


################################################################################
#                                                                              #
# CALCULATOR                                                                   #
#                                                                              #
################################################################################


class Calculator:
    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.tree = self.parser.parse()


    def expr(self, verbose: bool = False) -> tuple[list[int], list[str]]:
        def visit(node: AST):
            if isinstance(node, BinaryOperator):
                exprs.append(
                    f"{visit(node.left)} {node.token.type} {visit(node.right)}"
                )
                return f"[{len(exprs)}]"

            if isinstance(node, UnaryOperator):
                exprs.append(
                    f"{node.token.type} {visit(node.expr)}"
                )
                return f"[{len(exprs)}]"

            if isinstance(node, Variable):
                return node.token.value

            raise Exception(f"AST error: invalid node type, node={node}\n")

        exprs = list(self.parser.variables.keys())

        if verbose:
            n = len(exprs)
            visit(self.tree)
            if n == len(exprs):
                exprs.extend(exprs)
        else:
            exprs.append("[result]")

        indices = list(range(1, len(exprs) + 1))

        return indices, exprs


    def result_iterator(self, verbose=False) -> tuple[list[bool], list[bool]]:
        def visit(node: AST):
            if isinstance(node, BinaryOperator):
                sub_result = node.operator(visit(node.right), visit(node.left))
                if verbose:
                    results.append(sub_result)
                return sub_result

            if isinstance(node, UnaryOperator):
                sub_result = node.operator(visit(node.expr))
                if verbose:
                    results.append(sub_result)
                return sub_result

            if isinstance(node, Variable):
                return values[node.id]

            raise Exception(f"AST error: invalid node type, node={node}\n")

        n = len(self.parser.variables)
        limit = 1 << n # big interger

        for mask in range(limit):
            values = [bool((mask >> i) & 1) for i in range(n)]

            results = []
            result = visit(self.tree)
            if not verbose or not results:
                results.append(result)

            yield values, results

        return None


    def result(self, verbose: bool = False) -> tuple[tuple]:
        return tuple(self.result_iterator(verbose))


################################################################################
#                                                                              #
# MAIN                                                                         #
#                                                                              #
################################################################################


def print_table(calc: Calculator, verbose: bool = False) -> None:
    indices, exprs = calc.expr(verbose)
    idx_sep = len(calc.parser.variables)

    sizes = tuple(max(len(str(i)), len(e)) for i, e in zip(indices, exprs))

    print(
        "+", 
        "-+-".join("-" * s for s in sizes[:idx_sep]),
        "+ +",
        "-+-".join("-" * s for s in sizes[idx_sep:]),
        "+",
        sep="-",
    )

    print("|", end="")
    for k, (i, s) in enumerate(zip(indices, sizes)):
        if k == idx_sep:
            print(" |", end="")
        print(f" {i:<{s}} |", end="")
    print()

    print("|", end="")
    for k, (e, s) in enumerate(zip(exprs, sizes)):
        if k == idx_sep:
            print(" |", end="")
        print(f" {e:<{s}} |", end="")
    print()

    print(
        "+", 
        "-+-".join("-" * s for s in sizes[:idx_sep]),
        "+ +",
        "-+-".join("-" * s for s in sizes[idx_sep:]),
        "+",
        sep="-",
    )

    for params, results in calc.result_iterator(verbose):
        print("|", end="")
        for p, s in zip(params, sizes[:idx_sep]):
            print(f" {int(p):^{s}} |", end="")
        print(" |", end="")

        for r, s in zip(results, sizes[idx_sep:]):
            print(f" {int(r):^{s}} |", end="")
        print()

    print(
        "+", 
        "-+-".join("-" * s for s in sizes[:idx_sep]),
        "+ +",
        "-+-".join("-" * s for s in sizes[idx_sep:]),
        "+",
        sep="-",
    )


def main():
    print("for exits write: exit")

    while True:
        print()
        try:
            text = input(">>> ").strip()
        except EOFError:
            break
        if not text:
            continue
        if text == "exit":
            print()
            break

        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            calculator = Calculator(parser)
            print_table(calculator, verbose=True)
        except Exception as exc:
            print(exc, end="")


if __name__ == "__main__":
    main()
