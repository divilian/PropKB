
import sys
import os
from copy import copy
import numpy as np
import logging

class Literal():
    varnums = set()
    def __init__(self, varnum, neg):
        # If neg=-1, this is a negated variable. If neg=1, it's positive.
        self.varnum = varnum
        Literal.varnums |= {varnum}
        self.neg = neg
    def negated_form_of(self):
        a_copy = copy(self)
        a_copy.neg = -self.neg
        return a_copy
    def __str__(self):
        if self.neg == -1:
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
        return " ∨ ".join(str(l) for l in list(self.lits))
    def remove_literal(self, lit):
        self.lits.remove(lit)
    def is_unit(self):
        return len(self.lits) == 1
    def contains_literal(self, lit):
        return lit in self.lits
    def contains_variable(self, varnum):
        return varnum in [ l.varnum for l in self.lits ]
    def polarity_of_variable(self, varnum):
        for lit in self.lits:
            if lit.varnum == varnum:
                return lit.neg

class KB():
    def __init__(self, filename):
        self.clauses = set()
        self.assignments = {}
        with open(filename, "r", encoding="utf-8") as f:
            for clause_line in [ l.strip() for l in f.readlines() ]:
                self.add_clause(Clause(clause_line))
    def add_clause(self, c):
        self.clauses |= {c}
    def remove_clause(self, c):
        self.clauses -= {c}
    def __str__(self):
        return " ∧ ".join(f"({c})" for c in list(self.clauses))

    def propagate_units(self):
        """
        For all "unit clauses" (only one literal) perform the obvious
        simplifications: auto-satisfy any clauses that match it, and remove
        its negation from any clauses that match its negation.
        """
        logging.info("propagate_units...")
        for unit_clause in [ c for c in self.clauses if c.is_unit() ]:
            logging.debug(f"Looking at unit_clause {unit_clause}...")
            the_lit = list(unit_clause.lits)[0]
            if the_lit.varnum in self.assignments:
                if the_lit.neg != (self.assignments[the_lit.varnum] == 1):
                    # Houston, we have a problem. We have at least two unit
                    # clauses with opposite polarity!
                    sys.exit("Houston, we have two incompatible unit clauses.")
            self.assignments[the_lit.varnum] = (the_lit.neg == 1)
            logging.debug(f"    propagate_units officially assigns "
                f"{the_lit.varnum} the value {the_lit.neg == 1}")
            self.remove_clause(unit_clause)

            # For every unit clause, we know that the value of its only literal
            # is trivially set in stone. So, if there's any other clause that
            # also has that literal, we can just get rid of it since it's
            # already satisfied.
            clauses_to_remove = []
            for c in self.clauses:
                if c.contains_literal(the_lit):
                    logging.debug(f"    Removing clause {c}")
                    clauses_to_remove += [c]
            for ctr in clauses_to_remove:
                self.remove_clause(ctr)

            # On the other hand, we also know that the negation of this literal
            # will *never* be true. So, remove that negation in any other
            # clause in which it occurs. If that gives an empty clause, we're
            # doomed.
            for c in self.clauses:
                negated_form = the_lit.negated_form_of()
                if c.contains_literal(negated_form):
                    logging.debug(f"    Removing literal {negated_form} from "
                        f"{c}...")
                    c.remove_literal(negated_form)

    #def elim_easy_doubles: TODO if the same literal appears twice in a clause
    # with the same polarity, remove all but one for convenience. If it appears
    # with *both* polarities, then the clause is trivially true.

    def pure_elim(self):
        """
        For any variable that appears with only one polarity, go ahead and set
        it to what it needs to be.
        """
        logging.info("pure_elim...")
        made_progress = False
        for varnum in Literal.varnums:
            logging.debug(f"  Looking at {varnum}...")
            cs = [ c for c in self.clauses if c.contains_variable(varnum) ]
            logging.debug(f"  cs is {[ str(c) for c in cs ]}")
            pols = { c.polarity_of_variable(varnum) for c in cs }
            if len(pols) == 0:
                # Must have been removed by propagate_units(). Never mind.
                pass
            if len(pols) == 1:
                # Great! It's pure. Eliminate it.
                logging.debug(f"  Variable {varnum} is pure!") 
                if list(pols)[0] == 1:
                    self.assignments[varnum] = True
                    logging.debug(f"  pure_elim() officially assigns {varnum} "
                        "the value True")
                else:
                    self.assignments[varnum] = False
                    logging.debug(f"  pure_elim() officially assigns {varnum} "
                        "the value False")
                for c in cs:
                    self.remove_clause(c)
                made_progress = True
        return made_progress

    def solve(self):
        self.propagate_units()
        # As long as we're making progress, keep pure_elim'ing.
        while self.pure_elim():
            pass
        if any([ len(c.lits) == 0 for c in self.clauses ]):
            # This is a contradiction! Return False.
            return False


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 3:
        sys.exit("Usage: sat kb_file clause.")

    filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.exit(f"No such file {filename}.")
    
    myKB = KB(sys.argv[1])
    clause = sys.argv[2]

    print(myKB)
    myKB.solve()
    print(myKB)
    print(f"The answer is: {myKB.assignments}")
