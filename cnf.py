
import sys
import logging
import re
from sat import Literal, Clause

class Node():
    def __init__(self, left=None, me=None, right=None):
        self.left = left
        self.me = me
        self.right = right
    def __repr__(self):
        retval = "Node("
        if self.left:
            retval += self.left.__repr__() + ","
        retval += self.me.__repr__()
        if self.right:
            retval += "," + self.right.__repr__()
        return retval + ")"

def convert_to_cnf(s):
    """
    Given a sentence (string) of propositional logic, return a set of Clause
    objects representing its equivalent in CNF.
    """
    tokens = tokenize(s)
    tree = parse(tokens)
    return tree
            

def make_node(operators, operands):
    right = operands.pop()
    if operators[-1] == '-':
        left = None
    else:
        left = operands.pop()
    operands.append(Node(left,operators.pop(),right))

def parse(tokens):
    logging.info(f"Parse {tokens}...")
    operands = []
    ops = []
    while tokens:
        token = tokens.pop(0)
        logging.debug(f"token is |{token}|, operators=|{ops}|, "
            f"operands=|{operands}|")
        if token in ['<=>','⇔']:
            while ops and ops[-1] not in ['(','[']:
                make_node(ops, operands)
            ops.append('<=>')
        elif token in ['=>','⇒']:
            while ops and ops[-1] not in ['(','[','<=>']:
                make_node(ops, operands)
            ops.append('=>')
        elif token in ['v','∨']:
            while ops and ops[-1] not in ['(','[','<=>','=>']:
                make_node(ops, operands)
            ops.append('v')
        elif token in ['^','∧']:
            while ops and ops[-1] not in ['(','[','<=>','=>','v']:
                make_node(ops, operands)
            ops.append('^')
        elif token in ['-','¬']:
            while ops and ops[-1] not in ['(','[','<=>','=>','v','^','∧']:
                make_node(ops, operands)
            ops.append('-')
        elif token in ['(','[']:
            ops.append(token)
        elif token in [')']:
            while ops and ops[-1] not in ['(']:
                make_node(ops, operands)
            ops.pop()
        elif token in [']']:
            while ops and ops[-1] not in ['[']:
                make_node(ops, operands)
            ops.pop()
        else:
            operands.append(token)

    # No more input tokens. Finish up everything left undone.
    while ops:
        make_node(ops, operands)

    return operands.pop()

def tokenize(s):
    """
    Given a sentence (string) of propositional logic, return a list of its
    tokens. Each token is a banana, a prop logic connective, or a symbol
    (string). Legal syntax includes:
        - () and [] for grouping
        - - or ¬ for "not"
        - ^ or ∧ for "and"
        - v or ∨ for "or"  (note that "v" is not a valid symbol name)
        - => or ⇒ for "implies"
        - <=> or ⇔ for "equiv"
        - x or ⊕ for "xor"  (note that "x" is not a valid symbol name)
    """
    return re.findall(r'\(|\)|\[|\]|\^|v|=>|<=>|x|-|¬|⇒|⇔|∧|∨|⊕|\w+', s)

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) != 2:
        sys.exit("Usage: cnf.py sentence.")

    sentence = sys.argv[1]
    print(f"Converting {sentence}...")

    tree = convert_to_cnf(sentence)
    print(tree)
    #for c in convert_to_cnf(sentence):
    #    print(c)
    
