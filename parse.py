#!/usr/bin/env python3
"""
Probabilistic Earley parser that reconstructs the highest-probability parse of each sentence.
Extended from the recognizer to track probabilities and build parse trees.
"""

from __future__ import annotations
import argparse
import logging
import math
import tqdm
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter
from typing import Counter as CounterType, Iterable, List, Optional, Dict, Tuple

log = logging.getLogger(Path(__file__).stem)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "grammar", type=Path, help="Path to .gr file containing a PCFG'"
    )
    parser.add_argument(
        "sentences", type=Path, help="Path to .sen file containing tokenized input sentences"
    )
    parser.add_argument(
        "-s",
        "--start_symbol", 
        type=str,
        help="Start symbol of the grammar (default is ROOT)",
        default="ROOT",
    )

    parser.add_argument(
        "--progress", 
        action="store_true",
        help="Display a progress bar",
        default=False,
    )

    # for verbosity of logging
    parser.set_defaults(logging_level=logging.INFO)
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", dest="logging_level", action="store_const", const=logging.DEBUG
    )
    verbosity.add_argument(
        "-q", "--quiet",   dest="logging_level", action="store_const", const=logging.WARNING
    )

    return parser.parse_args()


class EarleyChart:
    """A chart for Earley's algorithm with probabilistic parsing."""
    
    def __init__(self, tokens: List[str], grammar: Grammar, progress: bool = False) -> None:
        """Create the chart based on parsing `tokens` with `grammar`.  
        `progress` says whether to display progress bars as we parse."""
        self.tokens = tokens
        self.grammar = grammar
        self.progress = progress
        self.profile: CounterType[str] = Counter()

        self.cols: List[Agenda]
        self._run_earley()
        self.best_root = self._find_best_parse()

    def accepted(self) -> bool:
        """Was the sentence accepted?"""
        return self.best_root is not None

    def get_parse_tree(self):
        """Reconstruct and return the parse tree from the best ROOT item."""
        if self.best_root is None:
            return None
        return self._build_tree(self.best_root)

    def _find_best_parse(self) -> Optional[ItemWithParseInfo]:
        """Find the best (lowest cost) complete ROOT item spanning the entire sentence."""
        best = None
        for item in self.cols[-1].all():
            if (item.rule.lhs == self.grammar.start_symbol
                and item.next_symbol() is None
                and item.start_position == 0):
                if best is None or item.weight < best.weight:
                    best = item
        return best

    def _run_earley(self) -> None:
        """Fill in the Earley chart with probabilities."""
        self.cols = [Agenda() for _ in range(len(self.tokens) + 1)]
        self._predict(self.grammar.start_symbol, 0)

        for i, column in tqdm.tqdm(enumerate(self.cols),
                                   total=len(self.cols),
                                   disable=not self.progress):
            log.debug("")
            log.debug(f"Processing items in column {i}")
            while column:
                item = column.pop()
                next = item.next_symbol()
                if next is None:
                    log.debug(f"{item} => ATTACH")
                    self._attach(item, i)
                elif self.grammar.is_nonterminal(next):
                    log.debug(f"{item} => PREDICT")
                    self._predict(next, i)
                else:
                    log.debug(f"{item} => SCAN")
                    self._scan(item, i)

    def _predict(self, nonterminal: str, position: int) -> None:
        """Start looking for this nonterminal at the given position."""
        for rule in self.grammar.expansions(nonterminal):
            new_item = ItemWithParseInfo(rule=rule, dot_position=0, start_position=position, 
                                        weight=rule.weight, children=[])
            self.cols[position].push(new_item)
            log.debug(f"\tPredicted: {new_item} in column {position}")
            self.profile["PREDICT"] += 1

    def _scan(self, item: ItemWithParseInfo, position: int) -> None:
        """Attach the next word to this item that ends at position."""
        if position < len(self.tokens) and self.tokens[position] == item.next_symbol():
            new_item = ItemWithParseInfo(
                rule=item.rule,
                dot_position=item.dot_position + 1,
                start_position=item.start_position,
                weight=item.weight,
                children=item.children + [self.tokens[position]]
            )
            self.cols[position + 1].push(new_item)
            log.debug(f"\tScanned to get: {new_item} in column {position+1}")
            self.profile["SCAN"] += 1

    def _attach(self, item: ItemWithParseInfo, position: int) -> None:
        """Attach this complete item to its customers in previous columns."""
        mid = item.start_position
        for customer in self.cols[mid].all():
            if customer.next_symbol() == item.rule.lhs:
                new_cost = customer.weight + item.weight
                new_item = ItemWithParseInfo(
                    rule=customer.rule,
                    dot_position=customer.dot_position + 1,
                    start_position=customer.start_position,
                    weight=new_cost,
                    children=customer.children + [item]
                )
                self.cols[position].push(new_item)
                log.debug(f"\tAttached to get: {new_item} in column {position}")
                self.profile["ATTACH"] += 1

    def _build_tree(self, item: ItemWithParseInfo):
        """Build parse tree from item, where children are already stored."""
        children_trees = []
        
        for child in item.children:
            if isinstance(child, str):
                # Terminal (word) - leaf node
                children_trees.append(child)
            elif isinstance(child, ItemWithParseInfo):
                # Nonterminal - recursively build subtree
                subtree = self._build_tree(child)
                children_trees.append(subtree)
        
        if not children_trees:
            # No children (shouldn't happen normally)
            return (item.rule.lhs, ())
        
        # For a rule A -> b1 b2 b3, we build (A (tree_b1) (tree_b2) (tree_b3))
        # But if all are terminals, we get (A b1 b2 b3)
        return (item.rule.lhs, tuple(children_trees))


class Agenda:
    """An agenda of items for Earley's algorithm with duplicate detection and weight tracking."""

    def __init__(self) -> None:
        self._items: List[ItemWithParseInfo] = []
        self._index: Dict[Tuple, int] = {}  # maps item key to index
        self._next = 0

    def __len__(self) -> int:
        return len(self._items) - self._next

    def push(self, item: ItemWithParseInfo) -> None:
        """Add item. For duplicates, keep the lower-weight variant.

        Implements Viterbi best-path tabling: if the previous variant was already
        popped (idx < self._next), enqueue the improved variant so its lower cost
        can propagate through downstream ATTACH operations. The new entry will be
        processed when encountered in column iteration, updating all dependent states.
        """
        item_key = (item.rule, item.dot_position, item.start_position)
        
        if item_key in self._index:
            idx = self._index[item_key]
            existing = self._items[idx]
            # Keep improved item and ensure it will be processed.
            if item.weight < existing.weight:
                if idx < self._next:
                    # Item was already popped; append improved version for re-processing
                    self._items.append(item)
                    self._index[item_key] = len(self._items) - 1
                else:
                    # Item not yet popped; replace in-place with better weight
                    self._items[idx] = item
        else:
            self._items.append(item)
            self._index[item_key] = len(self._items) - 1

    def pop(self) -> ItemWithParseInfo:
        """Dequeue the next unprocessed item."""
        if len(self) == 0:
            raise IndexError
        item = self._items[self._next]
        self._next += 1
        return item

    def all(self) -> Iterable[ItemWithParseInfo]:
        """Return all items that have ever been pushed."""
        return self._items

    def __repr__(self):
        next = self._next
        return f"{self.__class__.__name__}({self._items[:next]}; {self._items[next:]})"


class Grammar:
    """Represents a weighted context-free grammar."""
    def __init__(self, start_symbol: str, *files: Path) -> None:
        """Create a grammar with the given start symbol."""
        self.start_symbol = start_symbol
        self._expansions: Dict[str, List[Rule]] = {}
        for file in files:
            self.add_rules_from_file(file)

    def add_rules_from_file(self, file: Path) -> None:
        """Add rules to this grammar from a file."""
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
        """Return all rules with a given lhs."""
        return self._expansions[lhs]

    def is_nonterminal(self, symbol: str) -> bool:
        """Is symbol a nonterminal?"""
        return symbol in self._expansions


@dataclass(frozen=True)
class Rule:
    """A grammar rule with lhs, rhs, and weight."""
    lhs: str
    rhs: Tuple[str, ...]
    weight: float = 0.0

    def __repr__(self) -> str:
        return f"{self.lhs} → {' '.join(self.rhs)}"


@dataclass(frozen=False)
class ItemWithParseInfo:
    """An Earley item with probability and parse tree children."""
    rule: Rule
    dot_position: int
    start_position: int
    weight: float
    # Children: Each element is either a string (terminal) or an ItemWithParseInfo (nonterminal)
    children: List = field(default_factory=list)

    def next_symbol(self) -> Optional[str]:
        """What's the next unprocessed symbol?"""
        assert 0 <= self.dot_position <= len(self.rule.rhs)
        if self.dot_position == len(self.rule.rhs):
            return None
        else:
            return self.rule.rhs[self.dot_position]

    def __repr__(self) -> str:
        DOT = "·"
        rhs = list(self.rule.rhs)
        rhs.insert(self.dot_position, DOT)
        dotted_rule = f"{self.rule.lhs} → {' '.join(rhs)}"
        return f"({self.start_position}, {dotted_rule}, w={self.weight:.2f})"

    def __hash__(self):
        """Hash based on the item structure, not children."""
        return hash((self.rule, self.dot_position, self.start_position))

    def __eq__(self, other):
        """Equality based on item structure, not children."""
        if not isinstance(other, ItemWithParseInfo):
            return False
        return (self.rule == other.rule and 
                self.dot_position == other.dot_position and 
                self.start_position == other.start_position)


def tree_to_string(tree):
    """Convert parse tree to pretty string representation."""
    if tree is None:
        return ""
    
    label, children = tree
    
    if not children:
        return f"({label})"
    
    # Format as (Label child1 child2 ...)
    child_strs = []
    for child in children:
        if isinstance(child, tuple) and child[0] == 'WORD':
            # Terminal
            child_strs.append(child[1])
        elif isinstance(child, tuple):
            # Nonterminal
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
                log.debug("="*70)
                log.debug(f"Parsing sentence: {sentence}")
                chart = EarleyChart(sentence.split(), grammar, progress=args.progress)
                
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
