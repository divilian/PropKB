
import sys
import os
import random
import numpy as np
from pprint import pprint

if __name__ == "__main__":

    if len(sys.argv) != 5:
        sys.exit("Usage: prob_gen.py numVars numClauses numLitsPerClause "
            "numfilename.")
    
    num_vars = int(sys.argv[1])
    num_clauses = int(sys.argv[2])
    num_lits_per_clause = int(sys.argv[3])
    if num_lits_per_clause > num_vars:
        sys.exit("Can't have more lits per clause than variables!")
    filename = sys.argv[4]

    if os.path.isfile(filename):
        sys.exit(f"{filename} exists! Cowardly quitting.")

    # Create solution.
    assignments = { varnum: np.random.choice([False,True], size=1)[0]
        for varnum in range(1,num_vars+1) }

    with open(filename, "w", encoding="utf-8") as f:
        for _ in range(num_clauses):
            num_lits = int(np.random.randint(
                num_lits_per_clause-3, num_lits_per_clause+1))
            guar = np.random.choice(range(1,num_vars+1), size=1)[0]
            if assignments[guar]:
                clause = np.array([ guar ])
            else:
                clause = np.array([ -guar ])
            extras = np.random.choice(
                list(set(range(1,num_vars+1)) - {guar}),
                replace=False, size=num_lits-1)
            signs = np.random.choice([1,-1], size=num_lits-1)
            extras *= signs
            clause = np.concatenate([clause,extras])
            random.shuffle(clause)
            print(" ".join([ str(l) for l in clause ]), file=f)
    print("One solution is:")
    pprint(assignments)

