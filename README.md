# ProbKB

A fully-functional (but probably not scalable) propositional logic knowledge
base engine for use in student AI programs (like Wumpus World).


## Getting started

All you really need are the `PropKB.py` and `cnf.py` files somewhere Python can
find them.


## Creating a knowledge base

The `KB` class in the `PropKB.py` file is the only thing you will care about or
use. Each instantiation of a `KB` object creates a new propositional logic
knowledge base, starting either from scratch or with the contents of a file.
There are two kinds of files `KB` accepts:

* General `.kb` files with arbitrary propositional logic sentences (see below).
* Simplified `.cnf` files with clauses already in conjunctive normal form (see
below).

To create an empty knowledge base, just do this:

```
myKB = KB()
```

To create a knowledge base whose initial contents are contained in one of the
above two types of files, do one of these:

```
myKB = KB("myInitialContents.kb")
myKB = KB("myInitialContents.cnf")
```

### File format: `.kb` files

Each line of a plain-text `.kb` file is expected to be a propositional logic
statement, with the following specifics:

* Variable names can be any sequence of letters/numbers, in any case, but _not_
just the plain letter "`v`" or the plain letter "`x`" (these are operators).
* Two kinds of nesting parentheses can be used for convenience: "`()`" and
"`[]`". There's no precedence between the two, and they can be arbitrarily
nested.
* For unary "**not**," use "`-`" or "`¬`".
* For binary "**and**," use "`^`" or "`∧`".
* For binary "**or**," use "`v`" or "`∨`" (note that "`v`" is *not* a valid
symbol name).
* For binary "**xor**," use "`x`" or "`⊕`" (note that "`x`" is *not* a valid
symbol name).
* For binary "**implies**," use "`=>`" or "`⇒`".
* For binary "**equiv**," use "`<=>`" or "`⇔`".

Example:
```
[(relaxed v excited) ^ awake] => happy
-relaxed
excited ^ awake <=> thrilled
asleep x awake
excited => -asleep
```

### File format: `.cnf` files

Each line of a plain-text `.cnf` file is expected to represent one clause in
[CNF](https://en.wikipedia.org/wiki/Conjunctive_normal_form). The clause should
be space-separated and be composed only of literals (variables or their
negations.)

Example:
```
-relaxed happy -awake
-relaxed
awake asleep
-excited -asleep
awake -awake
-awake -asleep
-awake happy -excited
thrilled -awake -excited
asleep -asleep
awake -thrilled
excited -thrilled
```

(This happens to be equivalent to the `.kb` file contained above, only in CNF.)


---

## `KB` methods

You can call these methods on a `KB` object:

---
### `.tell(fact)`

Add a new statement of propositional logic to the knowledge base. Note: the
class is *not* smart enough (?) to detect a logical inconsistency and report
it. So if you `.tell()` the KB something that contradicts what it already
knows, the object can from that point behave erratically. (If you want, you
could `.ask()` before you `.tell()`, and make sure `.ask()` gives you a `True`
or `"IDK"`.)

Example:
```
myKB.tell("WrittenByUrsulaLaGuin => riveting ^ thoughtProvoking")
```

**The syntax for all propositional logic statements is the same as that
described in the "File format: `.kb` files" section, above.**


---
### `.retract(fake_news)`

Remove the passed non-fact from the KB. This isn't as easy as it sounds, and
won't always work if the exact negation of the fake news wasn't directly
previously inserted, but rather derived from previous facts.

Example:
```
myKB.retract("IraqHasWMDs")
```

---
### `.ask(hypothesis)`

Propose a statement of logic to the knowledge base, and receive an answer of
`True`, `False`, or `"IDK"`. (The first two are booleans, the last is a
string.) The KB will use resolution on the CNF version of the statements it's
previously created to tell you whether your statement is guaranteed to be true,
guaranteed to be false, or unknown (neither true nor false can be ruled out).

Example:
```
myKB.ask("riveting v (expensive x outOfDate)")
"IDK"
```

---
### `.can_prove(hypothesis)`

Same as `.ask()`, but only tests the hypothesis "one way." In other words,
instead of determining whether it can be proven true, false, or neither, it
only tests whether it can be proven true. Returns a boolean.

Example:
```
myKB.can_prove("riveting v (expensive x outOfDate)")
False
```

---
### `.get_solution()`

If possible, returns a sample solution (dictionary with assignments of booleans
to variables) that satisfies this knowledge base. If no such solution is
possible (*i.e.* if the KB contains a logical contradiction), returns `False`.

Example:
```
myKB.get_solution()
{'relaxed': False,
 'happy': False,
 'thrilled': True,
 'awake': True,
 'excited': True,
 'asleep': True}
```

Note that this by no means returns the *only* solution; indeed, just about any
KB you pick up off the street will have many possible solutions.


---
### `.is_equiv(anotherKB)`

Exhaustively tries every set of assignments to variables with both this KB and
the other KB passed as an argument, looking to see whether each assignment
satisfies (is consistent with) each KB. Returns `True` only if they have
identical answers for every assignment.

Example:
```
myKB.is_equiv(myKB)
True
myKB.is_equiv(someCompletelyDifferentKB)
False   (maybe)
```

---
### `.audit()`

Return a dictionary whose keys are the variables of this KB, and whose values
are either `True`, `False`, or `"IDK"` (don't know).

Example:
```
myKB.audit()
{'excited': 'IDK',
 'thrilled': 'IDK',
 'awake': 'IDK',
 'happy': 'IDK',
 'satisfied': False,
 'asleep': 'IDK'}
```
---

## Command-line interface

Finally, if you run `PropKB.py` as a "main," you can instantiate and experiment
with a KB interactively. If you pass no arguments, it will start with an empty
KB; otherwise, it will load from one of the two types of files (distinguished
by their file extensions "`.kb`" or "`.cnf`".)

Each command in the interactive prompt should begin with the word `tell`,
`ask`, or `vars`.

Example:
```
$ python PropKB.py 
Created empty KB.
ask/tell/vars (done): tell [(relaxed v excited) ^ awake] => happy
Updated KB.
ask/tell/vars (done): vars
Vars: awake,excited,happy,relaxed
ask/tell/vars (done): ask awake
IDK
ask/tell/vars (done): tell -happy
Updated KB.
ask/tell/vars (done): ask awake
IDK
ask/tell/vars (done): tell relaxed
Updated KB.
ask/tell/vars (done): ask awake
False
ask/tell/vars (done): done
$
```

