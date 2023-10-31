
import sys
import logging
from sat import Literal, Clause

def convert_to_cnf(s):
    """
    Given a sentence (string) of propositional logic, return a set of Clause
    objects representing its equivalent in CNF.
    """
    stack = []
    return None

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) != 2:
        sys.exit("Usage: cnf.py sentence.")

    sentence = sys.argv[1]
    print(f"Converting {sentence}...")

    for c in convert_to_cnf(sentence):
        print(c)
    
