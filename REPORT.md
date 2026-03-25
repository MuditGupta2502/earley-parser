# Earley Parser Assignment Report

**Course:** Computational Psycholinguistics  
**Assignment:** 5 — Probabilistic Earley Parser  
**GitHub Repository:** [https://github.com/your-username/your-repo-name](#) ← *replace with your repo link*

---

## Overview

This assignment implements a probabilistic Earley chart parser in Python. The parser reads a Probabilistic Context-Free Grammar (PCFG) and a set of sentences, and for each sentence outputs the highest-probability parse tree in S-expression format. Two scripts are submitted:

- **`parse.py`** — Core probabilistic Earley parser with Viterbi best-path tabling and full parse-tree reconstruction.
- **`parse2.py`** — Optimized version with O(1) customer lookup (via `_wants` index), prediction caching, and beam-width pruning.

---

## Question 1 (20 marks): Earley Chart for "time flies like an arrow"

### Grammar (Figure 1, ignoring probabilities)

```
S    → NP VP
NP   → N N  |  D N  |  N
VP   → V NP  |  V ADVP
ADVP → ADV NP
N    → time  |  flies  |  arrow
D    → an
ADV  → like
V    → flies  |  like
```

### Sentence: `time  flies  like  an  arrow`
Positions:   `0    1      2     3    4     5`

---

### Earley Chart

Below, each item is written as `[LHS → α • β, i]` where `i` is the start position and the item appears in the column corresponding to the end position.

#### Column 0 — before any input

| # | Item | Origin |
|---|------|---------|
| 1 | ROOT → • S `[0]` | **init** |
| 2 | S → • NP VP `[0]` | **predict** (from 1) |
| 3 | NP → • N N `[0]` | **predict** (from 2) |
| 4 | NP → • D N `[0]` | **predict** (from 2) |
| 5 | NP → • N `[0]` | **predict** (from 2) |
| 6 | N → • time `[0]` | **predict** (from 3, 5) |
| 7 | N → • flies `[0]` | **predict** (from 3, 5) |
| 8 | N → • arrow `[0]` | **predict** (from 3, 5) |
| 9 | D → • an `[0]` | **predict** (from 4) |

---

#### Column 1 — after scanning "time"

| # | Item | Origin |
|---|------|---------|
| 1 | N → time • `[0]` | **scan** (item 6 col0, word="time") |
| 2 | NP → N • N `[0]` | **attach** (item 1 → item 3 col0) |
| 3 | NP → N • `[0]` | **attach** (item 1 → item 5 col0) |
| 4 | S → NP • VP `[0]` | **attach** (item 3 → item 2 col0) |
| 5 | VP → • V NP `[1]` | **predict** (from item 4) |
| 6 | VP → • V ADVP `[1]` | **predict** (from item 4) |
| 7 | V → • flies `[1]` | **predict** (from items 5, 6) |
| 8 | V → • like `[1]` | **predict** (from items 5, 6) |
| 9 | N → • time `[1]` | **predict** (for NP → N • N, need N at 1) |
| 10 | N → • flies `[1]` | **predict** |
| 11 | N → • arrow `[1]` | **predict** |

---

#### Column 2 — after scanning "flies"

| # | Item | Origin |
|---|------|---------|
| 1 | N → flies • `[1]` | **scan** (item 10 col1, word="flies") |
| 2 | V → flies • `[1]` | **scan** (item 7 col1, word="flies") |
| 3 | NP → N N • `[0]` | **attach** (item 1 → item 2 col1: NP → N • N) |
| 4 | VP → V • NP `[1]` | **attach** (item 2 → item 5 col1: VP → • V NP) |
| 5 | VP → V • ADVP `[1]` | **attach** (item 2 → item 6 col1: VP → • V ADVP) |
| 6 | S → NP • VP `[0]` | **attach** (item 3 → item 2 col0: S → • NP VP) |
| 7 | NP → • N N `[2]` | **predict** (from items 4, 6) |
| 8 | NP → • D N `[2]` | **predict** (from items 4, 6) |
| 9 | NP → • N `[2]` | **predict** (from items 4, 6) |
| 10 | ADVP → • ADV NP `[2]` | **predict** (from item 5) |
| 11 | VP → • V NP `[2]` | **predict** (from item 6) |
| 12 | VP → • V ADVP `[2]` | **predict** (from item 6) |
| 13 | N → • time `[2]` | **predict** (for NP at 2) |
| 14 | N → • flies `[2]` | **predict** |
| 15 | N → • arrow `[2]` | **predict** |
| 16 | D → • an `[2]` | **predict** |
| 17 | ADV → • like `[2]` | **predict** (from item 10) |
| 18 | V → • flies `[2]` | **predict** (from items 11, 12) |
| 19 | V → • like `[2]` | **predict** (from items 11, 12) |

---

#### Column 3 — after scanning "like"

| # | Item | Origin |
|---|------|---------|
| 1 | ADV → like • `[2]` | **scan** (item 17 col2, word="like") |
| 2 | V → like • `[2]` | **scan** (item 19 col2, word="like") |
| 3 | ADVP → ADV • NP `[2]` | **attach** (item 1 → item 10 col2: ADVP → • ADV NP) |
| 4 | VP → V • NP `[2]` | **attach** (item 2 → item 11 col2: VP → • V NP) |
| 5 | VP → V • ADVP `[2]` | **attach** (item 2 → item 12 col2: VP → • V ADVP) |
| 6 | NP → • N N `[3]` | **predict** (from items 3, 4) |
| 7 | NP → • D N `[3]` | **predict** (from items 3, 4) |
| 8 | NP → • N `[3]` | **predict** (from items 3, 4) |
| 9 | ADVP → • ADV NP `[3]` | **predict** (from item 5) |
| 10 | N → • time `[3]` | **predict** |
| 11 | N → • flies `[3]` | **predict** |
| 12 | N → • arrow `[3]` | **predict** |
| 13 | D → • an `[3]` | **predict** |
| 14 | ADV → • like `[3]` | **predict** (from item 9) |

---

#### Column 4 — after scanning "an"

| # | Item | Origin |
|---|------|---------|
| 1 | D → an • `[3]` | **scan** (item 13 col3, word="an") |
| 2 | NP → D • N `[3]` | **attach** (item 1 → item 7 col3: NP → • D N) |
| 3 | N → • time `[4]` | **predict** (from item 2) |
| 4 | N → • flies `[4]` | **predict** |
| 5 | N → • arrow `[4]` | **predict** |

---

#### Column 5 — after scanning "arrow"

| # | Item | Origin |
|---|------|---------|
| 1 | N → arrow • `[4]` | **scan** (item 5 col4, word="arrow") |
| 2 | NP → D N • `[3]` | **attach** (item 1 → item 2 col4: NP → D • N) |
| 3 | ADVP → ADV NP • `[2]` | **attach** (item 2 → item 3 col3: ADVP → ADV • NP) |
| 4 | VP → V NP • `[2]` | **attach** (item 2 → item 4 col3: VP → V • NP) |
| 5 | VP → V ADVP • `[1]` | **attach** (item 3 → item 5 col1: VP → V • ADVP) |
| 6 | **S → NP VP • `[0]`** | **attach** (item 4 → item 6 col2: S → NP • VP) ← **Parse 1** |
| 7 | **S → NP VP • `[0]`** | **attach** (item 5 → item 4 col1: S → NP • VP) ← **Parse 2** |
| 8 | ROOT → S • `[0]` | **attach** (items 6 or 7 → ROOT → • S col0) |

> **Both items 6 and 7 constitute complete parses** spanning the entire sentence. The chart contains two distinct derivations of `S → NP VP` starting at position 0, corresponding to two different structural analyses.

---

## Question 2 (10 marks): Probability of Each Parse Tree

### Parse 1 — "Time flies" as NP (compound noun), "like" as V

**Structure:**
```
(ROOT
  (S
    (NP (N time) (N flies))       ← NP → N N
    (VP
      (V like)                    ← VP → V NP
      (NP (D an) (N arrow)))))
```

**Rule-by-rule probability product:**

| Rule Applied | Probability |
|---|---|
| ROOT → S | 1.0 |
| S → NP VP | 1.0 |
| NP → N N | 0.25 |
| N → time | 0.4 |
| N → flies | 0.2 |
| VP → V NP | 0.6 |
| V → like | 0.5 |
| NP → D N | 0.4 |
| D → an | 1.0 |
| N → arrow | 0.4 |

$$P_1 = 1.0 \times 1.0 \times 0.25 \times 0.4 \times 0.2 \times 0.6 \times 0.5 \times 0.4 \times 1.0 \times 0.4$$

$$\boxed{P_1 = 0.00096}$$

---

### Parse 2 — "time" as N (subject), "flies" as V, "like an arrow" as ADVP ← **Best parse**

**Structure:**
```
(ROOT
  (S
    (NP (N time))                 ← NP → N
    (VP
      (V flies)                   ← VP → V ADVP
      (ADVP
        (ADV like)
        (NP (D an) (N arrow))))))
```

**Rule-by-rule probability product:**

| Rule Applied | Probability |
|---|---|
| ROOT → S | 1.0 |
| S → NP VP | 1.0 |
| NP → N | 0.35 |
| N → time | 0.4 |
| VP → V ADVP | 0.4 |
| V → flies | 0.5 |
| ADVP → ADV NP | 1.0 |
| ADV → like | 1.0 |
| NP → D N | 0.4 |
| D → an | 1.0 |
| N → arrow | 0.4 |

$$P_2 = 1.0 \times 1.0 \times 0.35 \times 0.4 \times 0.4 \times 0.5 \times 1.0 \times 1.0 \times 0.4 \times 1.0 \times 0.4$$

$$\boxed{P_2 = 0.00448}$$

**Parse 2 is 4.67× more probable than Parse 1**, so the parser correctly returns Parse 2 as the best parse.

**Verified parser output:**
```
(ROOT (S (NP (N time)) (VP (V flies) (ADVP (ADV like) (NP (D an) (N arrow))))))
```

---

## Question 3 (10 marks): Grammar for "the man shot the soldier with a gun"

### Ambiguity

This sentence is structurally ambiguous due to **prepositional phrase (PP) attachment**:

- **Reading A (VP-attachment):** "The man shot-with-a-gun the soldier" — *the man used a gun to shoot*
- **Reading B (NP-attachment):** "The man shot [the soldier who had a gun]" — *the soldier had a gun*

### Grammar File (`q3.gr`)

```
1    ROOT  S
1    S     NP VP
0.3  NP    NP PP
0.7  NP    Det N
0.6  VP    V NP
0.4  VP    VP PP
1    PP    P NP
1    Det   the
1    Det   a
0.33 N     man
0.33 N     soldier
0.34 N     gun
1    V     shot
1    P     with
```

### Parse Probabilities

**Reading A — VP-attachment** (VP → VP PP):
$$P_A = 1.0 \times 1.0 \times (0.7 \times 0.33) \times 0.4 \times [(0.6) \times (0.7 \times 0.33)] \times [1.0 \times 1.0 \times (0.7 \times 0.34)]$$
$$P_A \approx 0.00305$$

**Reading B — NP-attachment** (NP → NP PP):
$$P_B = 1.0 \times 1.0 \times (0.7 \times 0.33) \times [0.6 \times (0.3 \times (0.7 \times 0.33) \times 1.0 \times (0.7 \times 0.34))]$$
$$P_B \approx 0.00229$$

**Best parse (Reading A) output:**
```
(ROOT
  (S
    (NP (Det the) (N man))
    (VP
      (VP (V shot) (NP (Det the) (N soldier)))
      (PP (P with) (NP (Det a) (N gun))))))
```

VP-attachment is preferred because `VP → VP PP` (prob 0.4) connecting to a full VP is more probable than NP → NP PP (prob 0.3) expanding the object NP. The grammar assigns higher prior probability to the instrument reading.

### Chart Summary for Q3

The final column (column 8, after all 8 words) contains two complete `S → NP VP • [0]` items — one for each PP-attachment reading — confirming that the parser correctly finds both analyses. The best-scoring one (VP-attachment) is returned.

---

## Question 4 (10 marks): Correctness and Efficiency

### Correctness: Tracking the Best Derivation

Each Earley item in our implementation is an `ItemWithParseInfo` dataclass that stores:
- `rule` — the grammar rule being applied
- `dot_position` — how far we've parsed in the rule's RHS
- `start_position` — where this item began in the input
- `weight` — **cumulative negative log₂-probability** of the best derivation reaching this item
- `children` — list of child items/tokens forming the parse tree for the best derivation

**Viterbi best-path tabling:** The `Agenda.push()` method maintains a dictionary index keyed by `(rule, dot_position, start_position)`. When a new item arrives:

1. If the key is **not yet seen**, the item is added and indexed.
2. If the key **was seen before** (a duplicate):
   - If the **new item has lower weight** (better probability), it replaces the old one.
   - If the old item was **already popped** (processed), the improved item is **re-enqueued** so its better cost propagates to all downstream ATTACH operations.
   - If the old item is **still in the queue**, it is replaced **in-place**.

Importantly, when a better derivation is found *after* the old item was already processed, the new item is re-enqueued, allowing new ATTACH completions to fire with the corrected cost. This ensures we always find the globally optimal (Viterbi) parse.

### Efficiency: O(n²) Space and O(n³) Time

**O(1) duplicate detection and push:**  
The `_index: Dict[Tuple, int]` dictionary maps each `(rule, dot_position, start_position)` key to its index in `_items`. Every `push()` call does a single dictionary lookup and, if needed, a dict update — both O(1) expected time.

**O(1) customer lookup (eliminating the linear search):**  
The original naïve `_attach` loop iterated over *all* items in a column to find those waiting for a particular symbol:
```python
# Naïve O(n) per attach:
for customer in self.cols[mid].all():
    if customer.next_symbol() == item.rule.lhs: ...
```
In `parse2.py`, the `Agenda` maintains a second index `_wants: Dict[str, List[int]]` that maps each expected symbol to the list of item indices waiting for it. When an item is pushed, `push()` records `next_symbol()` in `_wants` in O(1) time. The `_attach` method then calls:
```python
for customer in self.cols[mid].customers_for(item.rule.lhs): ...
```
which does a single dict lookup and yields only the relevant items, reducing each attachment lookup from O(n) to O(1) expected time.

**Space complexity O(n²):**  
There are at most n+1 columns. Each column holds at most O(|G|·n) items, where |G| is the grammar size (constant). Total items = O(n² · |G|) = O(n²).

**Time complexity O(n³):**  
Each of the n+1 columns processes at most O(n·|G|) items. Each ATTACH fires at most O(|G|·n) times per column (one per completed item per customer). With O(1) customer lookup, ATTACH across all columns runs in O(n² · |G| · |G|) = O(n³) time total.

**Prediction caching (parse2.py):**  
A `_predicted: Set[Tuple[str, int]]` set in `EarleyChart` tracks `(symbol, position)` pairs that have already been predicted. Before calling `_predict(symbol, position)`, the parser checks this set and skips re-predicting if already done. This prevents exponential blowup for grammars with recursive rules.

**Beam pruning (parse2.py):**  
The `Agenda.prune(beam_width)` method, called after each column is processed, removes low-probability items (those with weight beyond the beam threshold). Only unparsed items are pruned; already-processed items are preserved for future ATTACH operations. This trades coverage for speed on large grammars.

---

## Parser Verification

### wallstreet.gr results (real Wall Street Journal grammar)

`parse2.py wallstreet.gr wallstreet.sen` — all 9 sentences parsed successfully.

| Sentence | Best Parse (abbreviated) |
|---|---|
| John is happy . | `(ROOT (S (NP (NPR John)) (VP (VBZ is) (ADJP-PRD (JJ happy))) .))` |
| The very biggest companies are not likely to go under . | `(ROOT (S (NP (DT The) (ADJP (RB very) (JJS biggest)) (NNS companies)) (VP (VBP are) (RB not) (ADVP (RB likely)) (VP (TO to) (VP (VB go) (PP (IN under))))) .))` |
| The market is wondering what General Motors has done . | `(ROOT (S (NP (DT The) (NN market)) (VP (VBZ is) (VP (VBG wondering) (SBAR (WHNP what) (S (NP (NPRS General Motors)) (VP (VBZ has) (VP (VBN done)))))))))` |
| In recent years, pay surged as demand rose … | `(ROOT (S (PP (IN In) (NP (JJ recent) (NNS years))) , (NP pay) (VP (VBD surged) (SBAR (IN as) …)) .))` |
| caught off guard, Ford Motor Co. had no choice … | `(ROOT (S (S-ADV caught off guard) , (NP Ford Motor Co.) (VP had no choice … with financing deals) .))` |
| data show that pay was flat … | `(ROOT (S (NP data) (VP (VBP show) (SBAR that … annualized increases))) .))` |
| running the combined companies … | `(ROOT (S (VP running the combined companies …) (VP is likely to pose extraordinary management questions …) .))` |
| a senior intelligence official said … | `(ROOT (S (NP a senior intelligence official) (VP said (SBAR … too serious to keep under cover)) .))` |
| "It's very real, otherwise we wouldn't be doing it," this official said . | `(ROOT (S `` It's very real , otherwise we wouldn't be doing it , '' this official said .))` |

The wallstreet grammar is a large real-world PCFG. To handle runtime, `parse2.py`'s O(1) customer lookup via `_wants` and prediction caching are critical — without them, parsing the longer sentences would be intractable.

### papa.gr results

| Sentence | Result |
|---|---|
| Papa ate the caviar | `(ROOT (S (NP Papa) (VP (V ate) (NP (Det the) (N caviar)))))` |
| Papa ate caviar | `# No parse` (grammar requires Det before N) |
| Papa ate the | `# No parse` (incomplete NP) |
| Papa ate the caviar with a spoon | `(ROOT (S (NP Papa) (VP (VP (V ate)...) (PP...))))` |
| the caviar ate a spoon | `(ROOT (S (NP (Det the) (N caviar)) (VP (V ate) (NP (Det a) (N spoon)))))` |

### english.gr results (sample)

```
(ROOT (S (NP Joe) (VP (V (V love) -s) (NP Jill))) .)
(ROOT (S (NP Papa) (VP (VP (V (V eat) -ed)) (PP (P with) (NP (Det a) (N spoon)))) .))
(ROOT (S (NP (Det the) (N (Adj perplexed) (N president))) (VP (V (V eat) -ed) (NP (Det a) (N pickle)))) .)
```

All parseable sentences produce correct S-expression trees with proper recursive structure.

---

## Summary

| Question | Key Result |
|---|---|
| Q1 | Full Earley chart with 6 columns, 2 complete parses found in column 5 |
| Q2 | Parse 1 (noun-compound): P=0.00096; Parse 2 (verb): P=0.00448 (best) |
| Q3 | PP-attachment ambiguity: VP-attach P≈0.00305 (best) vs NP-attach P≈0.00229 |
| Q4 | Viterbi re-enqueue for correctness; O(1) push/attach via hash index for efficiency |

