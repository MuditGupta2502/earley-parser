# Earley Parser — Computational Psycholinguistics Assignment 5

Probabilistic Earley parser implementing a Viterbi-based PCFG chart parser.  
Adapted from [Prof. Jason Eisner's JHU NLP HW4](https://www.cs.jhu.edu/~jason/465/hw-parse/).

## Files

| File | Description |
|---|---|
| `parse.py` | Probabilistic Earley parser (Q3 submission) |
| `parse2.py` | Optimised parser — O(1) attach via `_wants` index, prediction caching, beam pruning (Q4) |
| `q1.gr` / `q1.sen` | Grammar + sentence for Q1/Q2 (*time flies like an arrow*) |
| `q3.gr` / `q3.sen` | Grammar + sentence for Q3 (*the man shot the soldier with a gun*) |
| `REPORT.md` | Full report (Markdown) |
| `Earley_Parser_Report.pdf` | PDF submission |

## Usage

```bash
python parse.py <grammar.gr> <sentences.sen>
python parse2.py <grammar.gr> <sentences.sen>   # optimised version
```

### Examples

```bash
python parse.py papa.gr papa.sen
python parse.py english.gr english.sen
python parse2.py wallstreet.gr wallstreet.sen
```

## Algorithm

- **PREDICT / SCAN / ATTACH** Earley operations on a chart of agenda columns  
- **Viterbi best-path**: weights are negative log₂-probabilities; lower = better  
- **Duplicate handling**: `_index` dict gives O(1) push; Viterbi re-enqueue propagates cheaper derivations  
- **parse2.py optimisations**: `_wants` dict for O(1) customer lookup in ATTACH; `_predicted` set for PREDICT deduplication; `Agenda.prune(beam_width)` for beam search

## Complexity

| | Space | Time |
|---|---|---|
| Earley (parse.py) | O(n²) | O(n³) |
| Earley (parse2.py) | O(n²) | O(n³) with lower constants |

## Test Grammars

Verified on: `papa.gr`, `english.gr`, `arith.gr`, `permissive.gr`, `permissive2.gr`, `wallstreet.gr` (all 9 WSJ sentences).
