
import sys
import logging
import re
from copy import deepcopy
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
    tree = eliminate_equiv(tree)
    tree = eliminate_implies(tree)
    tree = eliminate_xors(tree)
    return tree

def eliminate_equiv(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "<=>":
            reverse = deepcopy(non_cnf_tree)
            tree.me = "=>"
            reverse.me = "=>"
            reverse.left, reverse.right = \
                eliminate_equiv(reverse.right), eliminate_equiv(reverse.left)
            return Node(left=tree, me="^", right=reverse)
        else:
            tree.left = eliminate_equiv(tree.left)
            tree.right = eliminate_equiv(tree.right)
            return tree
    else:
        return non_cnf_tree
        
def eliminate_xors(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "x":
            other = deepcopy(non_cnf_tree)
            tree.left = Node(None,"-",eliminate_xors(tree.left))
            tree.me = "^"
            tree.right = eliminate_xors(tree.right)
            other.left = eliminate_xors(other.left)
            other.me = "^"
            other.right = Node(None,"-",eliminate_xors(other.right))
            return Node(left=tree, me="v", right=other)
        else:
            tree.left = eliminate_equiv(tree.left)
            tree.right = eliminate_equiv(tree.right)
            return tree
    else:
        return non_cnf_tree
        
def eliminate_implies(non_cnf_tree):
    if type(non_cnf_tree) is Node:
        tree = deepcopy(non_cnf_tree)
        if tree.me == "=>":
            tree.left = Node(None,"-",eliminate_implies(tree.left))
            tree.me = "v"
            tree.right = eliminate_implies(tree.right)
            return tree
        else:
            tree.left = eliminate_equiv(tree.left)
            tree.right = eliminate_equiv(tree.right)
            return tree
    else:
        return non_cnf_tree
        

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
        elif token in ['x','⊕']:
            while ops and ops[-1] not in ['(','[','<=>','=>']:
                make_node(ops, operands)
            ops.append('x')
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

# TODO raise exception if "v" or "x" is used as a symbol
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
    
