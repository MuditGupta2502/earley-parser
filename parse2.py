#!/usr/bin/env python3
"""
Optimized probabilistic Earley parser.
Improvements over parse.py:
- Caches predictions to avoid redundant work
- Prunes low-probability items
- Better data structure usage
"""

from __future__ import annotations
import argparse
import logging
import math
import tqdm
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter
from typing import Counter as CounterType, Iterable, List, Optional, Dict, Tuple, Set

log = logging.getLogger(Path(__file__).stem)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("grammar", type=Path, help="Path to .gr file")
    parser.add_argument("sentences", type=Path, help="Path to .sen file")
    parser.add_argument("-s", "--start_symbol", type=str, default="ROOT")
    parser.add_argument("--progress", action="store_true", default=False)
    parser.set_defaults(logging_level=logging.INFO)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", dest="logging_level", action="store_const", const=logging.DEBUG)
    verbosity.add_argument("-q", "--quiet", dest="logging_level", action="store_const", const=logging.WARNING)
    parser.add_argument("--beam", type=int, default=0, help="Beam width for pruning (0=no pruning)")
    return parser.parse_args()


@dataclass(frozen=True)
class Rule:
    lhs: str
    rhs: Tuple[str, ...]
    weight: float = 0.0

    def __repr__(self) -> str:
        return f"{self.lhs} → {' '.join(self.rhs)}"


@dataclass(frozen=False)
class ItemWithParseInfo:
    rule: Rule
    dot_position: int
    start_position: int
    weight: float
    children: List = field(default_factory=list)

    def next_symbol(self) -> Optional[str]:
        if self.dot_position == len(self.rule.rhs):
            return None
        return self.rule.rhs[self.dot_position]

    def __repr__(self) -> str:
        DOT = "·"
        rhs = list(self.rule.rhs)
        rhs.insert(self.dot_position, DOT)
        dotted_rule = f"{self.rule.lhs} → {' '.join(rhs)}"
        return f"({self.start_position}, {dotted_rule}, w={self.weight:.2f})"

    def __hash__(self):
        return hash((self.rule, self.dot_position, self.start_position))

    def __eq__(self, other):
        if not isinstance(other, ItemWithParseInfo):
            return False
        return (self.rule == other.rule and 
                self.dot_position == other.dot_position and 
                self.start_position == other.start_position)


class Agenda:
    """Optimized agenda with pruning support."""

    def __init__(self, beam_width: int = 0) -> None:
        self._items: List[ItemWithParseInfo] = []
        self._index: Dict[Tuple, int] = {}
        self._next = 0
        self.beam_width = beam_width
        self._wants: Dict[str, List[int]] = {}

    def __len__(self) -> int:
        return len(self._items) - self._next

    def _add_to_wants(self, symbol: Optional[str], idx: int) -> None:
        if symbol is not None:
            if symbol not in self._wants:
                self._wants[symbol] = []
            self._wants[symbol].append(idx)

    def push(self, item: ItemWithParseInfo) -> None:
        """Add item with duplicate detection and weight-based replacement.

        Implements Viterbi best-path tabling: if an improved duplicate arrives
        after the old one was popped, enqueue the improved variant so downstream
        ATTACH operations receive the lower-cost result. Popped items are never
        removed from self._items to preserve all() iteration requirements.
        """
        item_key = (item.rule, item.dot_position, item.start_position)
        
        if item_key in self._index:
            idx = self._index[item_key]
            if item.weight < self._items[idx].weight:
                if idx < self._next:
                    # Item was already popped; append improved version for re-processing
                    self._items.append(item)
                    new_idx = len(self._items) - 1
                    self._index[item_key] = new_idx
                    self._add_to_wants(item.next_symbol(), new_idx)
                else:
                    # Item not yet popped; replace in-place with better weight
                    self._items[idx] = item
        else:
            self._items.append(item)
            new_idx = len(self._items) - 1
            self._index[item_key] = new_idx
            self._add_to_wants(item.next_symbol(), new_idx)

    def pop(self) -> ItemWithParseInfo:
        if len(self) == 0:
            raise IndexError
        item = self._items[self._next]
        self._next += 1
        return item

    def all(self) -> Iterable[ItemWithParseInfo]:
        return self._items

    def customers_for(self, symbol: str) -> Iterable[ItemWithParseInfo]:
        """O(1) lookup of active items waiting for a specific symbol."""
        if symbol in self._wants:
            for idx in self._wants[symbol]:
                item = self._items[idx]
                item_key = (item.rule, item.dot_position, item.start_position)
                if self._index.get(item_key) == idx:
                    yield item

    def prune(self) -> None:
        """Remove low-weight items if beam width is set.
        
        Prunes only unprocessed items (after self._next) to preserve the closed
        agenda (already-popped items) which other columns may still reference
        during attachment. This maintains Earley's correctness invariant while
        reducing chart size for large ambiguous grammars.
        """
        if self.beam_width <= 0 or len(self._items) <= self.beam_width:
            return
        
        # Sort unprocessed items by weight
        unprocessed = self._items[self._next:]
        if len(unprocessed) <= self.beam_width:
            return
        
        unprocessed.sort(key=lambda x: x.weight)

        # Keep only the best unprocessed items by weight.
        self._items = self._items[:self._next] + unprocessed[:self.beam_width]
        # Rebuild index for remaining items
        self._index.clear()
        self._wants.clear()
        for idx, item in enumerate(self._items):
            item_key = (item.rule, item.dot_position, item.start_position)
            self._index[item_key] = idx
            self._add_to_wants(item.next_symbol(), idx)


class Grammar:
    def __init__(self, start_symbol: str, *files: Path) -> None:
        self.start_symbol = start_symbol
        self._expansions: Dict[str, List[Rule]] = {}
        for file in files:
            self.add_rules_from_file(file)

    def add_rules_from_file(self, file: Path) -> None:
        with open(file, "r") as f:
            for line in f:
                line = line.split("#")[0].rstrip()
                if line == "":
                    continue
                _prob, lhs, _rhs = line.split("\t")
                prob = float(_prob)
                rhs = tuple(_rhs.split())
                rule = Rule(lhs=lhs, rhs=rhs, weight=-math.log2(prob))
                if lhs not in self._expansions:
                    self._expansions[lhs] = []
                self._expansions[lhs].append(rule)

    def expansions(self, lhs: str) -> Iterable[Rule]:
        return self._expansions.get(lhs, [])

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self._expansions


class EarleyChart:
    def __init__(self, tokens: List[str], grammar: Grammar, progress: bool = False, beam_width: int = 0) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.progress = progress
        self.beam_width = beam_width
        self.profile: CounterType[str] = Counter()
        self._predicted: Set[Tuple[str, int]] = set()  # Cache (nonterminal, position) pairs to avoid redundant PREDICT
        self.cols: List[Agenda]
        self._run_earley()
        self.best_root = self._find_best_parse()

    def accepted(self) -> bool:
        return self.best_root is not None

    def get_parse_tree(self):
        if self.best_root is None:
            return None
        return self._build_tree(self.best_root)

    def _find_best_parse(self) -> Optional[ItemWithParseInfo]:
        best = None
        for item in self.cols[-1].all():
            if (item.rule.lhs == self.grammar.start_symbol
                and item.next_symbol() is None
                and item.start_position == 0):
                if best is None or item.weight < best.weight:
                    best = item
        return best

    def _run_earley(self) -> None:
        self.cols = [Agenda(self.beam_width) for _ in range(len(self.tokens) + 1)]
        self._predict_cached(self.grammar.start_symbol, 0)

        for i, column in tqdm.tqdm(enumerate(self.cols),
                                   total=len(self.cols),
                                   disable=not self.progress):
            # Prune column before processing
            column.prune()
            
            while column:
                item = column.pop()
                next_sym = item.next_symbol()
                if next_sym is None:
                    self._attach(item, i)
                elif self.grammar.is_nonterminal(next_sym):
                    self._predict_cached(next_sym, i)
                else:
                    self._scan(item, i)

    def _predict_cached(self, nonterminal: str, position: int) -> None:
        """Use O(1) caching to avoid redundant predictions."""
        cache_key = (nonterminal, position)
        if cache_key in self._predicted:
            return

        self._predicted.add(cache_key)
        for rule in self.grammar.expansions(nonterminal):
            new_item = ItemWithParseInfo(rule=rule, dot_position=0, start_position=position,
                                        weight=rule.weight, children=[])
            self.cols[position].push(new_item)
            self.profile["PREDICT"] += 1

    def _scan(self, item: ItemWithParseInfo, position: int) -> None:
        if position < len(self.tokens) and self.tokens[position] == item.next_symbol():
            new_item = ItemWithParseInfo(
                rule=item.rule,
                dot_position=item.dot_position + 1,
                start_position=item.start_position,
                weight=item.weight,
                children=item.children + [self.tokens[position]]
            )
            self.cols[position + 1].push(new_item)
            self.profile["SCAN"] += 1

    def _attach(self, item: ItemWithParseInfo, position: int) -> None:
        mid = item.start_position
        for customer in self.cols[mid].customers_for(item.rule.lhs):
            new_cost = customer.weight + item.weight
            new_item = ItemWithParseInfo(
                rule=customer.rule,
                dot_position=customer.dot_position + 1,
                start_position=customer.start_position,
                weight=new_cost,
                children=customer.children + [item]
            )
            self.cols[position].push(new_item)
            self.profile["ATTACH"] += 1

    def _build_tree(self, item: ItemWithParseInfo):
        children_trees = []
        
        for child in item.children:
            if isinstance(child, str):
                children_trees.append(child)
            elif isinstance(child, ItemWithParseInfo):
                subtree = self._build_tree(child)
                children_trees.append(subtree)
        
        if not children_trees:
            return (item.rule.lhs, ())
        
        return (item.rule.lhs, tuple(children_trees))


def tree_to_string(tree):
    if tree is None:
        return ""
    
    label, children = tree
    
    if not children:
        return f"({label})"
    
    child_strs = []
    for child in children:
        if isinstance(child, str):
            child_strs.append(child)
        elif isinstance(child, tuple):
            child_strs.append(tree_to_string(child))
        else:
            child_strs.append(str(child))
    
    return f"({label} {' '.join(child_strs)})"


def main():
    args = parse_args()
    logging.basicConfig(level=args.logging_level)

    grammar = Grammar(args.start_symbol, args.grammar)

    with open(args.sentences) as f:
        for sentence in f.readlines():
            sentence = sentence.strip()
            if sentence != "":
                chart = EarleyChart(sentence.split(), grammar, progress=args.progress, beam_width=args.beam)
                
                if chart.accepted():
                    tree = chart.get_parse_tree()
                    print(tree_to_string(tree))
                    print(chart.best_root.weight)
                else:
                    print(f"# No parse for: {sentence}")
                
                if args.logging_level == logging.DEBUG:
                    log.debug(f"Profile: {chart.profile}")


if __name__ == "__main__":
    main()
