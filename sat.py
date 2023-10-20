
import sys
import os
from copy import copy
import numpy as np

class Literal():
    def __init__(self, varnum, neg):
        self.varnum = varnum
        self.neg = neg
    def negated_form_of(selg):
        a_copy = copy(self)
        a_copy.neg = -self.neg
        return a_copy
    def __str__(self):
        if self.neg:
            return "¬" + str(self.varnum)
        else:
            return str(self.varnum)
    def __hash__(self):
        return self.varnum
    def __eq__(self, other):
        return self.varnum == other.varnum  and  self.neg == other.neg

class Clause():
    def __init__(self, string):
        self.lits = { Literal(abs(int(v)), np.sign(int(v)))
            for v in string.split(" ") }
    def __str__(self):
    def remove_lit(self, lit):
        return " ∨ ".join(str(l) for l in list(self.lits))
        self.lits.remove(lit)
    def is_unit(self):
        return len(self.lits) == 1
    def contains(self, lit):
        return lit in self.lits

class KB():
    def __init__(self):
        self.clauses = set()
    def add_clause(self, c):
        self.clauses |= {c}
    def remove_clause(self, c):
        self.clauses -= {c}
    def __str__(self):
        return " ∧ ".join(f"({c})" for c in list(self.clauses))


def propagate_units(kb):
    for unit_clause in [ c for c in kb.clauses if c.is_unit() ]:
        the_lit = list(unit_clause.lits)[0]
        kb.remove_clause(unit_clause)

        # For every unit clause, we know that the value of its only literal is
        # trivially set in stone. So, if there's any other clause that also has
        # that literal, we can just get rid of it since it's already satisfied.
        clauses_to_remove = []
        for c in kb.clauses:
            if c.contains(the_lit):
                clauses_to_remove += [c]
        for ctr in clauses_to_remove:
            kb.remove(ctr)

        # On the other hand, we also know that the negation of this literal
        # will *never* be true. So, remove that negation in any other clause in
        # which it occurs. If that gives an empty clause, we're doomed.
        for c in kb.clauses:
            negated_form = the_lit.negated_form_of()
            if c.contains(negated_form):
                c.remove(negated_form)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: sat kb_file clause.")

    filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.exit(f"No such file {filename}.")
    
    clause = sys.argv[2]

    with open(filename, "r", encoding="utf-8") as f:
        clause_lines = [ l.strip() for l in f.readlines() ]

    myKB = KB()

    for clause_line in clause_lines:
        myKB.add_clause(Clause(clause_line))
