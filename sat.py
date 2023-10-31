
import sys
import os
from copy import copy, deepcopy
import numpy as np
import logging
from pprint import pprint

class Literal():
    vars = set()
    def __init__(self, varstring):
        if varstring[0] == "-":
            self.neg = True
            self.var = varstring[1:]
        else:
            self.neg = False
            self.var = varstring
        Literal.vars |= {self.var}
    def negated_form_of(self):
        a_copy = copy(self)
        a_copy.neg = not self.neg
        return a_copy
    def __str__(self):
        if self.neg:
            return "¬" + str(self.var)
        else:
            return str(self.var)
    def __repr__(self):
        return f"Literal({'¬' if self.neg else ''}{self.var})"
    def __hash__(self):
        return self.var.__hash__()
    def __eq__(self, other):
        return self.var == other.var  and  self.neg == other.neg

class Clause():
    def __init__(self):
        self.lits = set()
    @classmethod
    def parse(cls, string):
        retval = cls()
        retval.lits = { Literal(v) for v in string.split(" ") }
        return retval
    def add_literal(self, lit):
        self.lits.add(lit)
    def remove_literal(self, lit):
        self.lits.remove(lit)
    def is_unit(self):
        return len(self.lits) == 1
    def contains_literal(self, lit):
        return lit in self.lits
    def contains_variable(self, var):
        return var in [ l.var for l in self.lits ]
    def polarity_of_variable(self, var):
        for lit in self.lits:
            if lit.var == var:
                return lit.neg
    def __str__(self):
        return " ∨ ".join(str(l) for l in list(self.lits))
    def __repr__(self):
        return f"Clause({self.lits})"

class KB():
    def __init__(self, filename):
        self.clauses = set()
        with open(filename, "r", encoding="utf-8") as f:
            for clause_line in [ l.strip() for l in f.readlines() ]:
                if not clause_line.startswith("#"):
                    self.add_clause(Clause.parse(clause_line))
    def add_clause(self, c):
        self.clauses |= {c}
    def remove_clause(self, c):
        self.clauses -= {c}

    def propagate_units(self, remaining_clauses, assignments):
        """
        For all "unit clauses" (only one literal) perform the obvious
        simplifications: auto-satisfy any clauses that match it, and remove
        its negation from any clauses that match its negation.
        """
        logging.info("propagate_units...")
        while remaining_clauses:
            nrc = len(remaining_clauses)
            i = 0
            while i < nrc and not list(remaining_clauses)[i].is_unit():
                i += 1
            if i == nrc:
                logging.debug(f"Continue ({i})")
                break
            else:
                unit_clause = list(remaining_clauses)[i]
                logging.debug(f"Looking at unit_clause {unit_clause}...")
                the_lit = list(unit_clause.lits)[0]
                if the_lit.var in assignments:
                    if the_lit.neg != (not assignments[the_lit.var]):
                        # Houston, we have a problem. We have at least two unit
                        # clauses with opposite polarity!
                        sys.exit("Houston, we have two incompatible unit clauses.")
                assignments[the_lit.var] = not the_lit.neg
                logging.debug(f"    propagate_units officially assigns "
                    f"{the_lit.var} the value {not the_lit.neg}")
                remaining_clauses -= {unit_clause}

                # For every unit clause, we know that the value of its only
                # literal is trivially set in stone. So, if there's any other
                # clause that also has that literal, we can just get rid of it
                # since it's already satisfied.
                clauses_to_remove = []
                for c in remaining_clauses:
                    if c.contains_literal(the_lit):
                        logging.debug(f"    Removing clause {c}")
                        clauses_to_remove += [c]
                for ctr in clauses_to_remove:
                    remaining_clauses -= {ctr}

                # On the other hand, we also know that the negation of this
                # literal will *never* be true. So, remove that negation in any
                # other clause in which it occurs. If that gives an empty
                # clause, we're doomed.
                for c in remaining_clauses:
                    negated_form = the_lit.negated_form_of()
                    if c.contains_literal(negated_form):
                        logging.debug(f"    Removing lit {negated_form} from "
                            f"{c}...")
                        c.remove_literal(negated_form)
            continue

    #def elim_easy_doubles: TODO if the same literal appears twice in a clause
    # with the same polarity, remove all but one for convenience. If it appears
    # with *both* polarities, then the clause is trivially true.

    def pure_elim(self, remaining_clauses, assignments):
        """
        For any variable that appears with only one polarity, go ahead and set
        it to what it needs to be.
        """
        logging.info("pure_elim...")
        made_progress = False
        for vn in Literal.vars:
            logging.debug(f"  Looking at {vn}...")
            cs = [ c for c in remaining_clauses if c.contains_variable(vn) ]
            logging.debug(f"  cs is {[ str(c) for c in cs ]}")
            pols = { c.polarity_of_variable(vn) for c in cs }
            if len(pols) == 0:
                # Must have been removed by propagate_units(). Never mind.
                pass
            if len(pols) == 1:
                # Great! It's pure. Eliminate it.
                logging.debug(f"  Variable {vn} is pure!") 
                if list(pols)[0] == 1:
                    assignments[vn] = True
                    logging.debug(f"  pure_elim() officially assigns {vn} "
                        "the value True")
                else:
                    assignments[vn] = False
                    logging.debug(f"  pure_elim() officially assigns {vn} "
                        "the value False")
                for c in cs:
                    remaining_clauses -= {c}
                made_progress = True
        return made_progress

    def solve_rec(self, remaining_clauses, assignments):
        self.propagate_units(remaining_clauses, assignments)
        # As long as we're making progress, keep pure_elim'ing.
        while self.pure_elim(remaining_clauses, assignments):
            pass
        if any([ len(c.lits) == 0 for c in remaining_clauses ]):
            # This is a contradiction! Return False.
            return False
        remaining_vars = Literal.vars - set(assignments.keys())
        if len(remaining_vars) == 0:
            return assignments
        var_to_try = list(remaining_vars)[0]
        assignments_try_true = deepcopy(assignments)
        assignments_try_true[var_to_try] = True
        result = self.solve_rec(remaining_clauses, assignments_try_true)
        if result:
            return result
        assignments_try_false = deepcopy(assignments)
        assignments_try_true[var_to_try] = False
        result = self.solve_rec(remaining_clauses, assignments_try_true)
        if result:
            return result
        return False

    def get_solution(self):
        """
        If possible, return a sample solution (set of assignments to variables)
        that satisfies this knowledge base. Otherwise, return False.
        """
        remaining_clauses = deepcopy(self.clauses)
        assignments = {}
        return self.solve_rec(remaining_clauses, assignments)

    def can_prove(self, hypothesis):
        """
        Return True if the hypothesis passed (a Literal) is guaranteed to be
        true by this knowledge base, and False otherwise.
        TODO: permit arbitrary expressions as hypotheses.
        """
        if type(hypothesis) is str:
            hypothesis = Literal(hypothesis)
        neg_hypo = hypothesis.negated_form_of()
        neg_hypo_clause = Clause()
        neg_hypo_clause.add_literal(neg_hypo)
        remaining_clauses = deepcopy(self.clauses)
        remaining_clauses |= {neg_hypo_clause}
        assignments = {}
        if self.solve_rec(remaining_clauses, assignments):
            return False, assignments
        else:
            return True, assignments

    def __str__(self):
        return " ∧ ".join(f"({c})" for c in list(self.clauses))
    def __repr__(self):
        return f"KB({self.clauses})"

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) != 3:
        sys.exit("Usage: sat kb_file clause.")

    filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.exit(f"No such file {filename}.")
    
    myKB = KB(sys.argv[1])
    clause = sys.argv[2]

    print(f"Solving {myKB}...")
    provable, assignments = myKB.can_prove(clause)
    if provable:
        print(f"Yes, {clause} is guaranteed true!")
    else:
        print(f"No, {clause} cannot be proven.")
    pprint(assignments)
