#!/usr/bin/env python3
"""Generate the PDF submission report for the Earley Parser Assignment."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "Earley_Parser_Report.pdf")

# ── Styles ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle('Title2', parent=styles['Title'],
    fontSize=20, spaceAfter=8, textColor=colors.HexColor('#1a1a2e'))

h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=14, spaceBefore=16, spaceAfter=6,
    textColor=colors.HexColor('#16213e'),
    borderPad=4)

h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=12, spaceBefore=12, spaceAfter=4,
    textColor=colors.HexColor('#0f3460'))

body = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, leading=15, spaceAfter=6, alignment=TA_JUSTIFY)

code = ParagraphStyle('Code', parent=styles['Code'],
    fontSize=8.5, leading=12, fontName='Courier',
    backColor=colors.HexColor('#f4f4f4'),
    leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4)

note = ParagraphStyle('Note', parent=styles['Normal'],
    fontSize=9, leading=13, textColor=colors.HexColor('#555555'),
    leftIndent=10, spaceAfter=4)

bold = ParagraphStyle('Bold', parent=styles['Normal'],
    fontSize=10, leading=14, spaceAfter=4)

def HR():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor('#cccccc'), spaceAfter=6)

def Code(text):
    return Preformatted(text, code)

def tbl(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eaf6')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    t.setStyle(TableStyle(style))
    return t


# ── Build Story ─────────────────────────────────────────────────────────────
story = []

# Title page
story += [
    Spacer(1, 1.5*cm),
    Paragraph("Earley Parser Assignment", title_style),
    Paragraph("Probabilistic Context-Free Grammar Parsing", h2),
    Spacer(1, 0.3*cm),
    Paragraph("Course: Computational Psycholinguistics &nbsp;&nbsp;|&nbsp;&nbsp; "
              "Assignment 5 &nbsp;&nbsp;|&nbsp;&nbsp; March 2026", body),
    Paragraph("GitHub Repository: <u>https://github.com/MuditGupta2502/earley-parser</u>", note),
    HR(),
    Spacer(1, 0.5*cm),
]

story += [
    Paragraph("Language: Python 3.8+", note),
    Paragraph("Files submitted: parse.py (Q3), parse2.py (Q4 – optimised)", note),
    Paragraph("Test grammars: papa.gr, english.gr, arith.gr, permissive.gr, permissive2.gr, wallstreet.gr", note),
    Spacer(1, 1*cm),
]

# ── Q1 ───────────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += [
    Paragraph("Question 1 (20 marks): Earley Chart for 'time flies like an arrow'", h1),
    HR(),
    Paragraph("Grammar (Figure 1, probabilities ignored for chart construction):", h2),
]

grammar_rules = [
    ["Rule", "Probability"],
    ["S → NP VP",     "1.0"],
    ["NP → N N",      "0.25"],
    ["NP → D N",      "0.4"],
    ["NP → N",        "0.35"],
    ["VP → V NP",     "0.6"],
    ["VP → V ADVP",   "0.4"],
    ["ADVP → ADV NP", "1.0"],
    ["N → time",      "0.4"],
    ["N → flies",     "0.2"],
    ["N → arrow",     "0.4"],
    ["D → an",        "1.0"],
    ["ADV → like",    "1.0"],
    ["V → flies",     "0.5"],
    ["V → like",      "0.5"],
]
story += [tbl(grammar_rules, col_widths=[9*cm, 3*cm]), Spacer(1, 0.3*cm)]

story += [
    Paragraph("Sentence positions:", body),
    Code("  time  flies   like    an   arrow\n"
         "0      1       2       3    4      5"),
    Spacer(1, 0.3*cm),
    Paragraph("Items are written as [LHS → α • β, i] where i is the start position.", note),
    Spacer(1, 0.3*cm),
]

# Column tables
def col_table(items):
    data = [["#", "Item", "Operation"]] + [
        [str(i+1), it, op] for i,(it,op) in enumerate(items)
    ]
    return tbl(data, col_widths=[0.6*cm, 10*cm, 5.5*cm])

story += [Paragraph("Column 0 — before any input", h2)]
story += [col_table([
    ("ROOT → • S  [0]",       "init"),
    ("S → • NP VP  [0]",      "predict (ROOT→•S)"),
    ("NP → • N N  [0]",       "predict (S→•NP VP)"),
    ("NP → • D N  [0]",       "predict (S→•NP VP)"),
    ("NP → • N  [0]",         "predict (S→•NP VP)"),
    ("N → • time  [0]",       "predict (NP→•N N, NP→•N)"),
    ("N → • flies  [0]",      "predict (NP→•N N, NP→•N)"),
    ("N → • arrow  [0]",      "predict (NP→•N N, NP→•N)"),
    ("D → • an  [0]",         "predict (NP→•D N)"),
]), Spacer(1, 0.3*cm)]

story += [Paragraph("Column 1 — after scanning \"time\"", h2)]
story += [col_table([
    ("N → time •  [0]",       "SCAN  (N→•time, word=time)"),
    ("NP → N • N  [0]",       "ATTACH (N→time•[0] → NP→•N N[0])"),
    ("NP → N •  [0]",         "ATTACH (N→time•[0] → NP→•N[0])"),
    ("S → NP • VP  [0]",      "ATTACH (NP→N•[0] → S→•NP VP[0])"),
    ("VP → • V NP  [1]",      "predict (S→NP•VP)"),
    ("VP → • V ADVP  [1]",    "predict (S→NP•VP)"),
    ("V → • flies  [1]",      "predict (VP→•V NP, VP→•V ADVP)"),
    ("V → • like  [1]",       "predict (VP→•V NP, VP→•V ADVP)"),
    ("N → • time  [1]",       "predict (NP→N•N needs N at 1)"),
    ("N → • flies  [1]",      "predict"),
    ("N → • arrow  [1]",      "predict"),
]), Spacer(1, 0.3*cm)]

story += [Paragraph("Column 2 — after scanning \"flies\"", h2)]
story += [col_table([
    ("N → flies •  [1]",      "SCAN  (N→•flies[1], word=flies)"),
    ("V → flies •  [1]",      "SCAN  (V→•flies[1], word=flies)"),
    ("NP → N N •  [0]",       "ATTACH (N→flies•[1] → NP→N•N[0])"),
    ("VP → V • NP  [1]",      "ATTACH (V→flies•[1] → VP→•V NP[1])"),
    ("VP → V • ADVP  [1]",    "ATTACH (V→flies•[1] → VP→•V ADVP[1])"),
    ("S → NP • VP  [0]",      "ATTACH (NP→NN•[0] → S→•NP VP[0])"),
    ("NP → • N N  [2]",       "predict (VP→V•NP, S→NP•VP)"),
    ("NP → • D N  [2]",       "predict"),
    ("NP → • N  [2]",         "predict"),
    ("ADVP → • ADV NP  [2]",  "predict (VP→V•ADVP)"),
    ("VP → • V NP  [2]",      "predict (S→NP•VP at col 2)"),
    ("VP → • V ADVP  [2]",    "predict"),
    ("N → • time/flies/arrow  [2]","predict (for NP at 2)"),
    ("D → • an  [2]",         "predict"),
    ("ADV → • like  [2]",     "predict (ADVP→•ADV NP)"),
    ("V → • flies/like  [2]", "predict (VP→•V NP/ADVP)"),
]), Spacer(1, 0.3*cm)]

story += [Paragraph("Column 3 — after scanning \"like\"", h2)]
story += [col_table([
    ("ADV → like •  [2]",     "SCAN  (ADV→•like[2], word=like)"),
    ("V → like •  [2]",       "SCAN  (V→•like[2], word=like)"),
    ("ADVP → ADV • NP  [2]",  "ATTACH (ADV→like•[2] → ADVP→•ADV NP[2])"),
    ("VP → V • NP  [2]",      "ATTACH (V→like•[2] → VP→•V NP[2])"),
    ("VP → V • ADVP  [2]",    "ATTACH (V→like•[2] → VP→•V ADVP[2])"),
    ("NP → • N N  [3]",       "predict (ADVP→ADV•NP, VP→V•NP)"),
    ("NP → • D N  [3]",       "predict"),
    ("NP → • N  [3]",         "predict"),
    ("N → • time/flies/arrow  [3]","predict"),
    ("D → • an  [3]",         "predict"),
    ("ADV → • like  [3]",     "predict (from VP→V•ADVP)"),
    ("ADVP → • ADV NP  [3]",  "predict"),
]), Spacer(1, 0.3*cm)]

story += [Paragraph("Column 4 — after scanning \"an\"", h2)]
story += [col_table([
    ("D → an •  [3]",         "SCAN  (D→•an[3], word=an)"),
    ("NP → D • N  [3]",       "ATTACH (D→an•[3] → NP→•D N[3])"),
    ("N → • time  [4]",       "predict (NP→D•N needs N at 4)"),
    ("N → • flies  [4]",      "predict"),
    ("N → • arrow  [4]",      "predict"),
]), Spacer(1, 0.3*cm)]

story += [Paragraph("Column 5 — after scanning \"arrow\"  ← Final column", h2)]
story += [col_table([
    ("N → arrow •  [4]",            "SCAN  (N→•arrow[4], word=arrow)"),
    ("NP → D N •  [3]",             "ATTACH (N→arrow•[4] → NP→D•N[3])"),
    ("ADVP → ADV NP •  [2]",        "ATTACH (NP→DN•[3] → ADVP→ADV•NP[2])"),
    ("VP → V NP •  [2]",            "ATTACH (NP→DN•[3] → VP→V•NP[2])"),
    ("VP → V ADVP •  [1]",          "ATTACH (ADVP→ADVNP•[2] → VP→V•ADVP[1])"),
    ("S → NP VP •  [0]  ← PARSE 1","ATTACH (VP→VNPADVP•[2] → S→NP•VP[0] col2)"),
    ("S → NP VP •  [0]  ← PARSE 2","ATTACH (VP→VADVP•[1] → S→NP•VP[0] col1)"),
    ("ROOT → S •  [0]  ✓ ACCEPT",   "ATTACH (best S•[0] → ROOT→•S[0])"),
])]

story += [
    Spacer(1, 0.3*cm),
    Paragraph(
        "<b>Structural ambiguity:</b> Two complete S → NP VP • [0] items appear in column 5, "
        "corresponding to two different parse trees for the same sentence.",
        body),
]

# ── Q2 ───────────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += [
    Paragraph("Question 2 (10 marks): Probability of Each Parse Tree", h1),
    HR(),
    Paragraph(
        "The sentence has exactly <b>two</b> parse trees due to lexical ambiguity "
        "(\"flies\" can be N or V; \"like\" can be V or ADV).", body),
]

story += [Paragraph("Parse Tree 1 — \"time flies\" as compound NP, \"like\" as verb", h2)]
story += [
    Code('(ROOT\n'
         '  (S\n'
         '    (NP (N time) (N flies))      NP → N N\n'
         '    (VP\n'
         '      (V like)                   VP → V NP\n'
         '      (NP (D an) (N arrow)))))'),
]
p1_data = [
    ["Rule", "Probability"],
    ["ROOT → S",    "1.0"],
    ["S → NP VP",   "1.0"],
    ["NP → N N",    "0.25"],
    ["N → time",    "0.4"],
    ["N → flies",   "0.2"],
    ["VP → V NP",   "0.6"],
    ["V → like",    "0.5"],
    ["NP → D N",    "0.4"],
    ["D → an",      "1.0"],
    ["N → arrow",   "0.4"],
    ["PRODUCT", "1.0 × 1.0 × 0.25 × 0.4 × 0.2 × 0.6 × 0.5 × 0.4 × 1.0 × 0.4"],
    ["= P₁", "0.00096"],
]
story += [tbl(p1_data, col_widths=[5*cm, 11*cm]), Spacer(1, 0.4*cm)]

story += [Paragraph("Parse Tree 2 — \"time\" as singular NP, \"flies\" as verb, \"like an arrow\" as ADVP  ← Best parse", h2)]
story += [
    Code('(ROOT\n'
         '  (S\n'
         '    (NP (N time))                NP → N\n'
         '    (VP\n'
         '      (V flies)                  VP → V ADVP\n'
         '      (ADVP\n'
         '        (ADV like)\n'
         '        (NP (D an) (N arrow))))))'),
]
p2_data = [
    ["Rule", "Probability"],
    ["ROOT → S",    "1.0"],
    ["S → NP VP",   "1.0"],
    ["NP → N",      "0.35"],
    ["N → time",    "0.4"],
    ["VP → V ADVP", "0.4"],
    ["V → flies",   "0.5"],
    ["ADVP → ADV NP", "1.0"],
    ["ADV → like",  "1.0"],
    ["NP → D N",    "0.4"],
    ["D → an",      "1.0"],
    ["N → arrow",   "0.4"],
    ["PRODUCT", "1.0 × 1.0 × 0.35 × 0.4 × 0.4 × 0.5 × 1.0 × 1.0 × 0.4 × 1.0 × 0.4"],
    ["= P₂  ★ BEST", "0.00448"],
]
story += [tbl(p2_data, col_widths=[5*cm, 11*cm]), Spacer(1, 0.4*cm)]

story += [
    Paragraph(
        "<b>Conclusion:</b> Parse 2 (verb interpretation) is <b>4.67× more probable</b> "
        "than Parse 1.  The parser's verified output:", body),
    Code("(ROOT (S (NP (N time)) (VP (V flies) (ADVP (ADV like) (NP (D an) (N arrow))))))"),
    Spacer(1, 0.3*cm),
    Paragraph(
        "The Viterbi parser correctly selects Parse 2 as it corresponds to the "
        "lowest negative log-probability weight tree.", body),
]

# ── Q3 ───────────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += [
    Paragraph("Question 3 (10 marks): Grammar for \"the man shot the soldier with a gun\"", h1),
    HR(),
    Paragraph(
        "This sentence is <b>structurally ambiguous</b> due to PP-attachment. "
        "The prepositional phrase 'with a gun' can attach either to the VP "
        "(instrument reading) or to the NP 'the soldier' (possession reading).",
        body),
]

story += [Paragraph("Designed Grammar (q3.gr):", h2)]
story += [Code(
    "1    ROOT  S\n"
    "1    S     NP VP\n"
    "0.3  NP    NP PP          # recursive NP for PP-attachment ambiguity\n"
    "0.7  NP    Det N\n"
    "0.6  VP    V NP\n"
    "0.4  VP    VP PP          # VP-level PP attachment\n"
    "1    PP    P NP\n"
    "1    Det   the\n"
    "1    Det   a\n"
    "0.33 N     man\n"
    "0.33 N     soldier\n"
    "0.34 N     gun\n"
    "1    V     shot\n"
    "1    P     with"
)]

story += [Paragraph("PP-Attachment Ambiguity — Two Readings:", h2)]

read_a = [
    ["Reading A: VP-attachment  (instrument reading — the man used a gun to shoot)"],
    ["(ROOT\n  (S\n    (NP (Det the) (N man))\n    (VP\n      (VP (V shot) (NP (Det the) (N soldier)))\n      (PP (P with) (NP (Det a) (N gun))))))"],
]
story += [
    Code(
        "(ROOT\n"
        "  (S\n"
        "    (NP (Det the) (N man))\n"
        "    (VP\n"
        "      (VP (V shot) (NP (Det the) (N soldier)))\n"
        "      (PP (P with) (NP (Det a) (N gun))))))   ← VP-attachment"
    ),
    Code(
        "(ROOT\n"
        "  (S\n"
        "    (NP (Det the) (N man))\n"
        "    (VP\n"
        "      (V shot)\n"
        "      (NP\n"
        "        (NP (Det the) (N soldier))\n"
        "        (PP (P with) (NP (Det a) (N gun)))))))  ← NP-attachment"
    ),
]

story += [Paragraph("Parse Probability Calculations:", h2)]
pa_data = [
    ["Parse A: VP-attachment  (VP → VP PP)", "Calculation", "Value"],
    ["ROOT → S",         "1.0",                               "1.0"],
    ["S → NP VP",        "1.0",                               "1.0"],
    ["NP → Det N",       "0.7",                               "0.7"],
    ["Det → the",        "1.0",                               "1.0"],
    ["N → man",          "0.33",                              "0.33"],
    ["VP → VP PP",       "0.4",                               "0.4"],
    ["  VP → V NP",      "0.6",                               "0.6"],
    ["  V → shot",       "1.0",                               "1.0"],
    ["  NP → Det N",     "0.7",                               "0.7"],
    ["  Det → the",      "1.0",                               "1.0"],
    ["  N → soldier",    "0.33",                              "0.33"],
    ["PP → P NP",        "1.0",                               "1.0"],
    ["  P → with",       "1.0",                               "1.0"],
    ["  NP → Det N",     "0.7",                               "0.7"],
    ["  Det → a",        "1.0",                               "1.0"],
    ["  N → gun",        "0.34",                              "0.34"],
    ["TOTAL P(A)", "1×1×0.7×0.33×0.4×0.6×0.7×0.33×1×0.7×0.34",
     "≈ 0.000305"],
]
story += [tbl(pa_data, col_widths=[5*cm, 8.5*cm, 2.5*cm]), Spacer(1, 0.3*cm)]

pb_data = [
    ["Parse B: NP-attachment  (NP → NP PP)", "Calculation", "Value"],
    ["ROOT → S",         "1.0",   "1.0"],
    ["S → NP VP",        "1.0",   "1.0"],
    ["NP → Det N",       "0.7",   "0.7"],
    ["N → man",          "0.33",  "0.33"],
    ["VP → V NP",        "0.6",   "0.6"],
    ["  V → shot",       "1.0",   "1.0"],
    ["  NP → NP PP",     "0.3",   "0.3"],
    ["    NP → Det N",   "0.7",   "0.7"],
    ["    N → soldier",  "0.33",  "0.33"],
    ["    PP → P NP",    "1.0",   "1.0"],
    ["    P → with",     "1.0",   "1.0"],
    ["    NP → Det N",   "0.7",   "0.7"],
    ["    N → gun",      "0.34",  "0.34"],
    ["TOTAL P(B)", "1×1×0.7×0.33×0.6×0.3×0.7×0.33×1×0.7×0.34",
     "≈ 0.000229"],
]
story += [tbl(pb_data, col_widths=[5*cm, 8.5*cm, 2.5*cm]), Spacer(1, 0.3*cm)]

story += [
    Paragraph(
        "<b>Best parse:</b> Reading A (VP-attachment) with P ≈ 0.000305 wins over "
        "Reading B (NP-attachment) with P ≈ 0.000229.  "
        "VP-attachment wins because VP → VP PP (0.4) combined with the "
        "simpler NP object is more probable than NP → NP PP (0.3).",
        body),
]

story += [Paragraph("Earley Chart Summary for Q3 (8 words, columns 0–8):", h2)]
story += [
    Paragraph(
        "The key columns are summarised below. Positions:", body),
    Code(
        "  the  man  shot  the  soldier  with  a   gun\n"
        "0    1    2     3     4        5     6   7    8"
    ),
]

q3_chart = [
    ["Column", "Key complete/partial items", "Note"],
    ["0", "ROOT→•S, S→•NP VP, NP→•Det N, NP→•NP PP, Det→•the/a, ...", "init+predict"],
    ["1 (the)", "Det→the•, NP→Det•N", "scan+attach"],
    ["2 (man)", "N→man•, NP→Det N•[0], S→NP•VP[0],\nVP→•V NP[2], VP→•VP PP[2], V→•shot[2]", "scan+attach+predict"],
    ["3 (shot)", "V→shot•[2], VP→V•NP[2]", "scan+attach"],
    ["4 (the)", "Det→the•[3], NP→Det•N[3]", "scan+attach"],
    ["5 (soldier)", "N→soldier•[4], NP→Det N•[3],\nNP→NP•PP[3] (ambiguity seed),\nVP→V NP•[2] (complete VP)", "both NP readings alive"],
    ["6 (with)", "P→•with[5], PP→•P NP[5]", "predict"],
    ["7 (a)", "Det→a•[6], NP→Det•N[6]", "scan+attach"],
    ["8 (gun) ✓", "N→gun•[7], NP→Det N•[6], PP→P NP•[5],\n"
                  "VP→VP PP•[2] ← Reading A,\n"
                  "NP→NP PP•[3] → VP→V NP•[2] ← Reading B,\n"
                  "S→NP VP•[0] ← BOTH PARSES\nROOT→S•[0] ✓ ACCEPT",
     "both parses found"],
]
story += [tbl(q3_chart, col_widths=[1.8*cm, 9*cm, 5.2*cm])]

# ── Q4 ───────────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += [
    Paragraph("Question 4 (10 marks): Implementation — Correctness and Efficiency", h1),
    HR(),
]

story += [
    Paragraph("4.1  Correctness: Tracking the Best Derivation", h2),
    Paragraph(
        "Each Earley item is an <b>ItemWithParseInfo</b> dataclass containing:", body),
]
fields = [
    ["Field", "Type", "Purpose"],
    ["rule",          "Rule",            "The grammar rule being applied"],
    ["dot_position",  "int",             "How far into the rule's RHS we have matched"],
    ["start_position","int",             "Where in the input this item started"],
    ["weight",        "float",           "Cumulative negative log₂-probability of best derivation reaching this item"],
    ["children",      "List",            "Ordered list of child items/tokens forming the best parse tree"],
]
story += [tbl(fields, col_widths=[3.5*cm, 3*cm, 9.5*cm]), Spacer(1, 0.3*cm)]

story += [
    Paragraph("<b>Viterbi best-path tabling in Agenda.push():</b>", bold),
    Paragraph(
        "Every item is indexed in a dictionary keyed by "
        "(rule, dot_position, start_position). When a new item arrives:", body),
    Code(
        "item_key = (item.rule, item.dot_position, item.start_position)\n\n"
        "if item_key in self._index:\n"
        "    idx = self._index[item_key]\n"
        "    if item.weight < self._items[idx].weight:   # strictly better\n"
        "        if idx < self._next:                    # already popped?\n"
        "            # Re-enqueue improved item so cheaper cost propagates\n"
        "            self._items.append(item)\n"
        "            self._index[item_key] = len(self._items) - 1\n"
        "        else:\n"
        "            self._items[idx] = item             # replace in-place\n"
        "else:\n"
        "    self._items.append(item)                    # new item\n"
        "    self._index[item_key] = len(self._items) - 1"
    ),
    Paragraph(
        "The critical case is when a cheaper derivation arrives <i>after</i> the old "
        "item was already popped and processed. In that case the improved item is "
        "<b>re-enqueued</b>, so the ATTACH operation fires again with the lower cost, "
        "updating all downstream items. Without this step, the parser would silently "
        "output a sub-optimal parse.", body),
]

story += [
    Paragraph("4.2  Efficiency: O(n²) Space and O(n³) Time", h2),
]

eff_rows = [
    ["Operation", "Naïve complexity", "Our solution", "How"],
    ["push() / duplicate check",
     "O(n) linear scan",
     "O(1) expected",
     "_index dict: maps (rule, dot, start) → list index"],
    ["ATTACH customer lookup",
     "O(n) iterate cols[mid].all()",
     "O(1) expected",
     "_wants dict in parse2.py: maps next_symbol → item indices"],
    ["PREDICT deduplication",
     "O(n) per nonterminal",
     "O(1)",
     "_predicted Set in parse2.py: tracks (symbol, position) pairs"],
    ["Beam pruning",
     "—",
     "Configurable",
     "Agenda.prune(beam_width) keeps top-k unprocessed items"],
]
story += [tbl(eff_rows, col_widths=[3.5*cm, 3.5*cm, 3*cm, 6*cm]), Spacer(1, 0.3*cm)]

story += [
    Paragraph("<b>Why O(1) push is necessary:</b>", bold),
    Paragraph(
        "In the worst case, each of the O(n²) chart cells may attempt to insert "
        "O(|G|) items, where |G| is the grammar size. If each insert requires an "
        "O(n) linear scan to find duplicates, the total time becomes O(n³ · |G|) — "
        "which in practice grows too fast for sentences of length ≥15 with large "
        "grammars like wallstreet.gr. With O(1) hash-based lookup, the total "
        "insertion work is O(n² · |G|), keeping the algorithm within O(n³) time.", body),
    Paragraph("<b>Space complexity:</b>", bold),
    Paragraph(
        "There are at most n+1 columns. Each column stores at most O(|G| · n) "
        "distinct items (bounded by the number of grammar rules times the number "
        "of possible start positions). Total space = O(n² · |G|) = <b>O(n²)</b> "
        "for fixed grammar size.", body),
    Paragraph("<b>Time complexity:</b>", bold),
    Paragraph(
        "PREDICT: O(|G|) per (symbol, position) pair, O(n|G|) per column, O(n²|G|) total. "
        "SCAN: O(n|G|) total. "
        "ATTACH: O(1) per lookup (via _wants), O(n²|G|²) in the worst case but "
        "practically O(n³) as each rule combination fires at most once per column triple. "
        "Overall: <b>O(n³)</b> for fixed grammar.", body),
]

story += [
    Paragraph("4.3  parse2.py Additional Optimisations", h2),
    Code(
        "# 1. Prediction caching — never re-predict same (symbol, position)\n"
        "self._predicted: Set[Tuple[str, int]] = set()\n\n"
        "def _predict_cached(self, symbol, position):\n"
        "    if (symbol, position) not in self._predicted:\n"
        "        self._predicted.add((symbol, position))\n"
        "        self._predict(symbol, position)\n\n"
        "# 2. O(1) customer lookup — _wants index in Agenda\n"
        "def customers_for(self, symbol):\n"
        "    for idx in self._wants.get(symbol, []):\n"
        "        item = self._items[idx]\n"
        "        if self._index.get((item.rule,item.dot_position,item.start_position)) == idx:\n"
        "            yield item\n\n"
        "# 3. Beam pruning — trim low-prob items after each column\n"
        "def prune(self, beam_width):\n"
        "    unprocessed = self._items[self._next:]\n"
        "    unprocessed.sort(key=lambda x: x.weight)\n"
        "    self._items = self._items[:self._next] + unprocessed[:beam_width]"
    ),
]

# ── Verification ─────────────────────────────────────────────────────────────
story += [PageBreak()]
story += [
    Paragraph("Parser Verification — Test Results", h1),
    HR(),
]

story += [Paragraph("arith.gr — Arithmetic Expression Grammar", h2)]
arith_data = [
    ["Input", "Output"],
    ["3", "(ROOT (EXPR (TERM (FACTOR (Num 3)))))"],
    ["3 *", "# No parse  (incomplete expression — correct)"],
    ["3 * 5", "(ROOT (EXPR (TERM (TERM (FACTOR (Num 3))) * (FACTOR (Num 5)))))"],
    ["3 * 5 + 6 * { 5 - 3 - 2 } + sqrt { 7 }",
     "(ROOT (EXPR (EXPR (EXPR (TERM (TERM (FACTOR 3)) * (FACTOR 5)))\n"
     "            + (TERM (TERM (FACTOR 6)) * (FACTOR { … })))\n"
     "            + (TERM (FACTOR sqrt { … }))))"],
]
story += [tbl(arith_data, col_widths=[5*cm, 11*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph("permissive.gr — Highly Ambiguous Grammar (A → A A | x)", h2)]
perm_data = [
    ["Input", "Output (best/Viterbi parse)"],
    ["x",       "(ROOT (A x))"],
    ["x x",     "(ROOT (A (A x) (A x)))"],
    ["x x x",   "(ROOT (A (A (A x) (A x)) (A x)))"],
    ["x x x x", "(ROOT (A (A (A (A x) (A x)) (A x)) (A x)))"],
    ["x x x x x","(ROOT (A (A (A (A (A x) (A x)) (A x)) (A x)) (A x)))"],
]
story += [tbl(perm_data, col_widths=[3*cm, 13*cm]), Spacer(1, 0.3*cm)]
story += [Paragraph(
    "The permissive grammar is maximally ambiguous — a string of n x's has the "
    "Catalan number Cₙ₋₁ of parse trees (1, 1, 2, 5, 14, 42, …). The parser "
    "correctly returns the single best (Viterbi) parse for each input without "
    "enumerating all parses.", body)]

story += [Paragraph("papa.gr — Classic PP-attachment Grammar", h2)]
papa_data = [
    ["Input", "Output"],
    ["Papa ate the caviar",
     "(ROOT (S (NP Papa) (VP (V ate) (NP (Det the) (N caviar)))))"],
    ["Papa ate caviar",       "# No parse  (grammar requires Det before N)"],
    ["Papa ate the",          "# No parse  (incomplete NP)"],
    ["Papa ate the caviar with a spoon",
     "(ROOT (S (NP Papa) (VP (VP (V ate) (NP (Det the) (N caviar)))\n"
     "                       (PP (P with) (NP (Det a) (N spoon))))))"],
    ["the caviar ate a spoon",
     "(ROOT (S (NP (Det the) (N caviar)) (VP (V ate) (NP (Det a) (N spoon)))))"],
]
story += [tbl(papa_data, col_widths=[5*cm, 11*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph("english.gr — Feature-Rich English Grammar", h2)]
story += [
    Paragraph(
        "english.gr is a manually crafted grammar with morphological splitting (love -s, eat -ed, go -ing), "
        "modal verbs, complement clauses (CP), adjectives, and coordination. "
        "All 25 sentences in english.sen were parsed successfully.", body),
]
eng_data = [
    ["Input sentence", "Best parse (abbreviated)"],
    ["Joe love -s Jill .",
     "(ROOT (S (NP Joe) (VP (V (V love) -s) (NP Jill))) .)"],
    ["he love -s her .",
     "(ROOT (S (NP he) (VP (V (V love) -s) (NP her))) .)"],
    ["him love -s she .",
     "(ROOT (S (NP him) (VP (V (V love) -s) (NP she))) .)"],
    ["Papa sleep -s with a spoon .",
     "(ROOT (S (NP Papa) (VP (VP (V (V sleep) -s)) (PP (P with) (NP (Det a) (N spoon))))) .)"],
    ["Papa eat -ed with a spoon .",
     "(ROOT (S (NP Papa) (VP (VP (V (V eat) -ed)) (PP (P with) (NP (Det a) (N spoon))))) .)"],
    ["Papa sleep -s every bonbon with a spoon .",
     "(ROOT (S (NP Papa) (VP (V (V sleep) -s) (NP (Det every) (N (N bonbon) (PP ... with a spoon))))) .)"],
    ["Papa eat -ed every bonbon with a spoon .",
     "(ROOT (S (NP Papa) (VP (V (V eat) -ed) (NP (Det every) (N (N bonbon) (PP ... with a spoon))))) .)"],
    ["have a bonbon !",
     "(ROOT (VP (V have) (NP (Det a) (N bonbon))) !)  [ROOT → VP ! rule]"],
    ["a bonbon on the spoon entice -s .",
     "(ROOT (S (NP (Det a) (N (N bonbon) (PP (P on) ...spoon))) (VP (V (V entice) -s))) .)"],
    ["a bonbon on the spoon entice -0 .",
     "(ROOT (S (NP ...) (VP (V (V entice) -0))) .)"],
    ["the bonbon -s on the spoon entice -0 .",
     "(ROOT (S (NP (Det the) (N (N (N bonbon) -s) (PP on the spoon))) (VP (V (V entice) -0))) .)"],
    ["Joe kiss -ed every chief of staff .",
     "(ROOT (S (NP Joe) (VP (V (V kiss) -ed) (NP (Det every) (N chief of staff)))) .)"],
    ["Jill say -s that Joe might sleep on the floor !",
     "(ROOT (S (NP Jill) (VP (VP (V say -s) (CP that (S (NP Joe) (VP (Modal might) (VP sleep))))) (PP on the floor))) !)"],
    ["the perplexed president eat -ed a pickle .",
     "(ROOT (S (NP (Det the) (N (Adj perplexed) (N president))) (VP (V (V eat) -ed) (NP (Det a) (N pickle)))) .)"],
    ["Papa is perplexed .",
     "(ROOT (S (NP Papa) (VP (V is) (Adj perplexed))) .)"],
    ["Papa is chief of staff .",
     "(ROOT (S (NP Papa) (VP (V is) (N chief of staff))) .)"],
    ["Papa want -ed a sandwich .",
     "(ROOT (S (NP Papa) (VP (V (V want) -ed) (NP (Det a) (N sandwich)))) .)"],
    ["Papa want -ed to eat a sandwich .",
     "(ROOT (S (NP Papa) (VP (V (V want) -ed) (VP (V to (V eat)) (NP (Det a) (N sandwich))))) .)"],
    ["Papa want -ed Joe to eat a pickle .",
     "(ROOT (S (NP Papa) (VP (V (V want) -ed) (NP Joe) (VP (V to (V eat)) (NP (Det a) (N pickle))))) .)"],
    ["Papa want -ed a pickle to eat Joe .",
     "(ROOT (S (NP Papa) (VP (V (V want) -ed) (NP (Det a) (N pickle)) (VP (V to (V eat)) (NP Joe)))) .)"],
    ["Papa would have eat -ed his sandwich -s .",
     "(ROOT (S (NP Papa) (VP (Modal would) (VP (V have) (VP (V (V eat) -ed) (NP (Det his) (N (N sandwich) -s)))))) .)"],
    ["every sandwich was go -ing to have been delicious .",
     "(ROOT (S (NP (Det every) (N sandwich)) (VP (V was) (VP (V go -ing) (VP (V to (V have)) (VP (V been) (Adj delicious)))))) .)"],
    ["the fine and blue woman and every man must have eat -ed two sandwich -s and sleep -ed on the floor .",
     "(ROOT (S (NP (NP the fine-and-blue woman) and (NP every man)) (VP (Modal must) (VP (V have) (VP eat-ed two sandwiches and sleep-ed on the floor)))) .)"],
]
story += [tbl(eng_data, col_widths=[6.5*cm, 9.5*cm]), Spacer(1, 0.3*cm)]
story += [
    Paragraph(
        "<b>Notable features:</b> The grammar handles morphological decomposition (V → V -s etc.), "
        "raising/control constructions (want-ed Joe to eat), modals (would/might/must), "
        "complement clauses (say -s that ...), adjectives in predicative position (is perplexed), "
        "and coordination (fine and blue woman and every man). "
        "All 25 sentences parsed correctly.", body),
]

story += [Paragraph("permissive2.gr — Two-Nonterminal Ambiguous Grammar", h2)]
story += [
    Paragraph(
        "permissive2.gr extends permissive.gr with two interchangeable nonterminals (A and B). "
        "Both A and B can generate 'x' directly (weight 0.2 each) and can be combined from pairs of A/B symbols. "
        "ROOT can start with either A or B (0.5 each). This creates even greater structural ambiguity.", body),
    Code(
        "0.5  ROOT  A     # root can be A ..."
        "\n0.5  ROOT  B     # ... or B"
        "\n0.2  A     A A  |  A     A B  |  A     B A  |  A     B B"
        "\n0.2  B     A A  |  B     A B  |  B     B A  |  B     B B"
        "\n0.2  A     x"
        "\n0.2  B     x"
    ),
]
perm2_data = [
    ["Input", "Output (Viterbi best parse)"],
    ["x",           "(ROOT (A x))"],
    ["x x",         "(ROOT (A (A x) (A x)))"],
    ["x x x",       "(ROOT (A (A (A x) (A x)) (A x)))"],
    ["x x x x",     "(ROOT (A (A (A (A x) (A x)) (A x)) (A x)))"],
    ["x x x x x",   "(ROOT (A (A (A (A (A x) (A x)) (A x)) (A x)) (A x)))"],
]
story += [tbl(perm2_data, col_widths=[3*cm, 13*cm]), Spacer(1, 0.3*cm)]
story += [
    Paragraph(
        "The parser consistently resolves the A/B tie in favour of A (alphabetically first / "
        "encountered first in grammar order) and uses the same left-branching Viterbi structure "
        "as permissive.gr. The grammar is semantically equivalent to permissive.gr for the "
        "terminal 'x' — it demonstrates that the parser correctly handles grammars "
        "with multiple interchangeable nonterminals and equal-weight tie-breaking.", body),
]

story += [Paragraph("wallstreet.gr — Real WSJ Grammar (9 sentences, all parsed)", h2)]
ws_data = [
    ["Sentence", "Best parse (abbreviated)"],
    ["John is happy .",
     "(ROOT (S (NP John) (VP (VBZ is) (ADJP-PRD happy)) .))"],
    ["The very biggest companies are not likely to go under .",
     "(ROOT (S (NP (DT The) (ADJP very biggest) (NNS companies))\n"
     "         (VP (VBP are) (RB not) (ADVP likely) (VP to go under)) .))"],
    ["The market is wondering what General Motors has done .",
     "(ROOT (S (NP The market) (VP is (VP wondering\n"
     "         (SBAR what (S (NP Gen. Motors) (VP has done))))) .))"],
    ["In recent years, pay surged as demand rose …",
     "(ROOT (S (PP In recent years) , (NP pay)\n"
     "         (VP surged (SBAR as demand rose while workers left …)) .))"],
    ["caught off guard, Ford Motor Co. had no choice … with financing deals .",
     "(ROOT (S (S-ADV caught off guard) , (NP Ford Motor Co.)\n"
     "         (VP had no choice … with financing deals) .))"],
    ["… It's very real, … this official said .",
     "(ROOT (S '' It's very real … '' this official said .))"],
]
story += [tbl(ws_data, col_widths=[6*cm, 10*cm]), Spacer(1, 0.3*cm)]
story += [Paragraph(
    "The wallstreet grammar (228 KB, real WSJ PCFG) parsed all 9 sentences "
    "correctly using parse2.py. The most complex sentence (~50 words) required "
    "deep recursion with VP, SBAR, and NP nesting — all handled correctly by "
    "the Viterbi Earley algorithm.", body)]

# ── Summary ──────────────────────────────────────────────────────────────────
story += [PageBreak()]
story += [
    Paragraph("Summary", h1),
    HR(),
]
summary_data = [
    ["Q", "Marks", "Topic", "Key Result"],
    ["1", "20",
     "Earley chart for\n'time flies like an arrow'",
     "6-column chart constructed; 2 complete parses\nfound in column 5"],
    ["2", "10",
     "Parse probabilities",
     "P(Parse 1)=0.00096 (noun);  P(Parse 2)=0.00448 (verb)\nParse 2 is the best parse (4.67× more probable)"],
    ["3", "10",
     "Grammar for\n'the man shot the soldier with a gun'",
     "PP-attachment ambiguity captured;\nVP-attach P≈0.000305 (best) > NP-attach P≈0.000229"],
    ["4", "10",
     "Correctness &\nEfficiency",
     "Viterbi re-enqueue for correctness;\nO(1) push via _index; O(1) attach via _wants;\nprediction caching; beam pruning (parse2.py)"],
    ["Total", "50", "", "All problems solved; parser verified on 6 grammars\n(arith, permissive, permissive2, papa, english, wallstreet)"],
]
story += [tbl(summary_data, col_widths=[0.8*cm, 1.5*cm, 4.5*cm, 9.2*cm])]

story += [
    Spacer(1, 1*cm),
    Paragraph("Files submitted:", bold),
    Code(
        "parse.py       – Probabilistic Earley parser (Q3)\n"
        "parse2.py      – Optimised parser with O(1) attach + beam pruning (Q4)\n"
        "q1.gr / q1.sen – Grammar + sentence for Q1/Q2\n"
        "q3.gr / q3.sen – Grammar + sentence for Q3\n"
        "REPORT.md      – This report in Markdown\n"
        "Earley_Parser_Report.pdf  – This PDF submission\n"
        "\nGrammars tested: papa.gr, english.gr, arith.gr,\n"
        "                 permissive.gr, permissive2.gr, wallstreet.gr"
    ),
]

# ── Build PDF ────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="Earley Parser Assignment Report",
    author="Student",
)
doc.build(story)
print(f"PDF written to: {OUTPUT}")
