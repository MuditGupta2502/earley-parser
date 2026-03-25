#!/usr/bin/env python3
"""Generate a professional PDF submission for the Earley Parser Assignment."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
import os

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Earley_Parser_Report.pdf")
W, H = A4

NAVY    = colors.HexColor('#1B2A4A')
GOLD    = colors.HexColor('#C9A227')
STEEL   = colors.HexColor('#2E86AB')
LIGHT   = colors.HexColor('#F0F4F8')
STRIPE  = colors.HexColor('#E8EEF4')
DARKBG  = colors.HexColor('#2B2D42')
CODEFG  = colors.HexColor('#EDF2F4')
RED_ERR = colors.HexColor('#C0392B')
GREEN_OK= colors.HexColor('#1E8449')
MIDGRAY = colors.HexColor('#7F8C8D')
HEADBG  = colors.HexColor('#D6E4F0')

class HeaderFooterCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_chrome(num_pages)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)
    def _draw_chrome(self, num_pages):
        page = self._pageNumber
        if page == 1:
            self.setFillColor(NAVY)
            self.rect(0, H - 2.8*cm, W, 2.8*cm, stroke=0, fill=1)
            self.setFillColor(GOLD)
            self.rect(0, H - 2.85*cm, W, 0.12*cm, stroke=0, fill=1)
            self.setFont('Helvetica-Bold', 18)
            self.setFillColor(colors.white)
            self.drawString(2*cm, H - 1.5*cm, 'Earley Parser Assignment')
            self.setFont('Helvetica', 10)
            self.setFillColor(GOLD)
            self.drawString(2*cm, H - 2.1*cm, 'Computational Psycholinguistics  |  Assignment 5  |  March 2026')
        self.setStrokeColor(GOLD)
        self.setLineWidth(0.5)
        self.line(1.5*cm, 1.1*cm, W - 1.5*cm, 1.1*cm)
        self.setFont('Helvetica', 8)
        self.setFillColor(MIDGRAY)
        self.drawString(2*cm, 0.7*cm, 'Earley Parser  |  Computational Psycholinguistics  |  MuditGupta2502')
        self.drawRightString(W - 2*cm, 0.7*cm, f'Page {page} of {num_pages}')

styles = getSampleStyleSheet()
def S(name, **kw):
    return ParagraphStyle(name, parent=styles['Normal'], **kw)
h1 = S('H1', fontSize=14, spaceBefore=18, spaceAfter=6, fontName='Helvetica-Bold', textColor=NAVY)
h2 = S('H2', fontSize=11, spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold', textColor=STEEL)
body = S('Body', fontSize=9.5, leading=14.5, spaceAfter=5, alignment=TA_JUSTIFY)
note = S('Note', fontSize=8.5, leading=12, textColor=MIDGRAY, spaceAfter=3)
bold = S('Bold', fontSize=9.5, leading=14, fontName='Helvetica-Bold', spaceAfter=4)
mono = S('Mono', fontSize=8.5, leading=12, fontName='Courier', spaceAfter=4)
center = S('Center', fontSize=9.5, leading=13, alignment=TA_CENTER)
code_style = ParagraphStyle('Code', parent=styles['Code'],
    fontSize=8, leading=11, fontName='Courier',
    backColor=DARKBG, textColor=CODEFG,
    leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=6, borderPad=6)

def HR(col=GOLD, thick=0.8):
    return HRFlowable(width='100%', thickness=thick, color=col, spaceAfter=4, spaceBefore=2)
def Code(text):
    _sty = ParagraphStyle('_pcode', fontName='Courier', fontSize=8, leading=11,
                          textColor=CODEFG, spaceBefore=0, spaceAfter=0,
                          leftIndent=0, rightIndent=0)
    t = Table([[Preformatted(text, _sty)]], colWidths=[15.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARKBG),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, MIDGRAY),
    ]))
    return [t, Spacer(1, 4)]

def section_header(num, title, subtitle=None):
    inner = [[
        Paragraph(f'<font color="white"><b>{num}</b></font>', S('_Num',
            fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph(f'<font color="white"><b>{title}</b></font>' +
                  (f'<br/><font color="#C9A227" size="9">{subtitle}</font>' if subtitle else ''),
                  S('_Title', fontSize=13, fontName='Helvetica-Bold', textColor=colors.white))
    ]]
    t = Table(inner, colWidths=[1*cm, 14.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 2, GOLD),
    ]))
    return [t, Spacer(1, 6)]

def callout(text, color=GOLD, icon='*'):
    data = [[
        Table([[Paragraph(f'<b>{icon}</b>',
                          S('_ic', fontSize=12, fontName='Helvetica-Bold',
                            textColor=color, alignment=TA_CENTER))]],
              colWidths=[0.5*cm],
              style=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),0)]),
        Paragraph(text, S('_cb', fontSize=9.5, leading=14, spaceAfter=0))
    ]]
    t = Table(data, colWidths=[0.6*cm, 14.4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FDF9EE')),
        ('LINEAFTER', (0,0), (0,-1), 3, color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.3, MIDGRAY),
    ]))
    return [t, Spacer(1, 4)]

def tbl(data, col_widths=None, header=True, stripe=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8.5),
        ('GRID',      (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6E5')),
        ('BACKGROUND',(0,0), (-1,0), NAVY if header else STRIPE),
        ('FONTNAME',  (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTCOLOR', (0,0), (-1,0), colors.white if header else NAVY),
        ('ALIGN',     (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',    (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING',(0,0), (-1,-1), 6),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ]
    if stripe:
        for i in range(2, len(data), 2):
            cmds.append(('BACKGROUND', (0,i), (-1,i), STRIPE))
    t.setStyle(TableStyle(cmds))
    return t

def tbl_check(data, col_widths=None):
    t = Table(data, colWidths=col_widths)
    cmds = [
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8.5),
        ('GRID',      (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6E5')),
        ('BACKGROUND',(0,0), (-1,0), NAVY),
        ('FONTNAME',  (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',     (0,0), (-1,-1), 'LEFT'),
        ('ALIGN',     (-1,0), (-1,-1), 'CENTER'),
        ('VALIGN',    (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ]
    for i in range(1, len(data)):
        cmds.append(('BACKGROUND', (0,i), (-1,i),
                     colors.HexColor('#EAFAF1') if 'Y' in str(data[i][-1])
                     else colors.HexColor('#FDEDEC')))
    t.setStyle(TableStyle(cmds))
    return t

story = []

_gh_link = 'https://github.com/MuditGupta2502/earley-parser'
_gh_bar = Table(
    [[Paragraph(f'\u2665  GitHub Repository: <u><a href="{_gh_link}" color="#2E86AB">{_gh_link}</a></u>',
                S('_gh', fontSize=9, fontName='Helvetica-Bold', textColor=NAVY, spaceAfter=0))]],
    colWidths=[15.5*cm])
_gh_bar.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#D6E4F0')),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
    ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('BOX', (0,0), (-1,-1), 0.5, STEEL),
]))
story += [_gh_bar, Spacer(1, 0.2*cm)]

story += [
    Spacer(1, 0.3*cm),
    Paragraph('Probabilistic Context-Free Grammar Parsing', S('Sub',
        fontSize=12, textColor=STEEL, spaceAfter=6, fontName='Helvetica-Bold')),
    HR(GOLD, 1.5),
    Spacer(1, 0.3*cm),
]

meta = [
    ['Course',   'Computational Psycholinguistics'],
    ['Assignment', '5 - Earley Parser'],
    ['Student', 'Mudit Gupta  (MuditGupta2502)'],
    ['Date',    'March 2026'],
    ['GitHub',  'https://github.com/MuditGupta2502/earley-parser'],
    ['Files',   'parse.py (Q3)  /  parse2.py (Q4 - optimised)'],
]
meta_tbl = tbl([['Field', 'Value']] + meta, col_widths=[3.5*cm, 12*cm], header=True)
story += [meta_tbl, Spacer(1, 0.5*cm)]

score = [
    ['Question', 'Marks', 'Topic', 'Status'],
    ['Q1', '20', "Earley chart - 'time flies like an arrow'", 'Y Complete'],
    ['Q2', '10', 'Parse tree probabilities',                  'Y Complete'],
    ['Q3', '10', "Grammar + parser for PP-attachment sentence",'Y Complete'],
    ['Q4', '10', 'Correctness and efficiency explanation',     'Y Complete'],
]
score_tbl = tbl_check(score, col_widths=[1.5*cm, 1.5*cm, 10*cm, 2.5*cm])
story += [score_tbl, Spacer(1, 0.3*cm)]
story += callout(
    '<b>Autograder robustness:</b> The parser accepts any valid .gr / .sen pair. '
    'Tested on papa, english, arith, permissive, permissive2, wallstreet, and a custom unseen grammar. '
    'Arith weights match arith.par exactly; wallstreet sentence-1 weight = <b>34.22401</b>, '
    'sentence-2 = <b>104.90923</b> (matches Section D benchmark).',
    color=GREEN_OK, icon='OK')

story += [PageBreak()]
story += section_header('Q1', 'Earley Chart for "time flies like an arrow"', '20 marks')

story += [Paragraph('Grammar (Figure 1):', h2)]
gram_data = [
    ['Rule', 'Prob.'], ['S -> NP VP', '1.0'], ['NP -> N N', '0.25'],
    ['NP -> D N', '0.4'], ['NP -> N', '0.35'], ['VP -> V NP', '0.6'],
    ['VP -> V ADVP', '0.4'], ['ADVP -> ADV NP', '1.0'],
    ['N -> time', '0.4'], ['N -> flies', '0.2'], ['N -> arrow', '0.4'],
    ['D -> an', '1.0'], ['ADV -> like', '1.0'], ['V -> flies', '0.5'], ['V -> like', '0.5'],
]
story += [tbl(gram_data, col_widths=[8*cm, 2.5*cm]), Spacer(1, 0.3*cm)]

story += [
    Paragraph('Chart construction (probabilities ignored for Q1 - structural only):', h2),
    Paragraph('Positions: | time | flies | like | an | arrow |  columns 0-5', body),
    Paragraph('Items written as [LHS -> alpha * beta, i] where i = start column.', note),
    Spacer(1, 0.2*cm),
]

def col_table(col_num, word, items):
    title = f'Column {col_num}' + (f' - after scanning "{word}"' if word else ' - initial')
    hdr = [[Paragraph(f'<b>{title}</b>', S('_ch', fontSize=9, fontName='Helvetica-Bold',
                       textColor=colors.white)), '', '']]
    rows = [['#', 'Item', 'Operation']] + [[str(i+1), it, op] for i,(it,op) in enumerate(items)]
    full = hdr + rows
    t = Table(full, colWidths=[0.5*cm, 9.5*cm, 5.5*cm])
    cmds = [
        ('SPAN',       (0,0), (-1,0)),
        ('BACKGROUND', (0,0), (-1,0), STEEL),
        ('FONTCOLOR',  (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,1), (-1,1), NAVY),
        ('FONTCOLOR',  (0,1), (-1,1), colors.white),
        ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID',       (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6E5')),
        ('ALIGN',      (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME',   (0,2), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('LEFTPADDING',(0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
    ]
    for i in range(3, len(full), 2):
        cmds.append(('BACKGROUND', (0,i), (-1,i), STRIPE))
    t.setStyle(TableStyle(cmds))
    return [t, Spacer(1, 0.25*cm)]

story += col_table(0, None, [
    ('ROOT -> * S  [0]',     'initialise'),
    ('S -> * NP VP  [0]',    'PREDICT from ROOT->*S'),
    ('NP -> * N N  [0]',     'PREDICT from S->*NP VP'),
    ('NP -> * D N  [0]',     'PREDICT from S->*NP VP'),
    ('NP -> * N  [0]',       'PREDICT from S->*NP VP'),
    ('N -> * time  [0]',     'PREDICT from NP->*N N, NP->*N'),
    ('N -> * flies  [0]',    'PREDICT from NP->*N N, NP->*N'),
    ('N -> * arrow  [0]',    'PREDICT from NP->*N N, NP->*N'),
    ('D -> * an  [0]',       'PREDICT from NP->*D N'),
])

story += col_table(1, 'time', [
    ('N -> time *  [0]',        'SCAN (N->*time[0])'),
    ('NP -> N * N  [0]',        'ATTACH (N->time*[0], NP->*N N[0])'),
    ('NP -> N *  [0]',          'ATTACH (N->time*[0], NP->*N[0])'),
    ('S -> NP * VP  [0]',       'ATTACH (NP->N*[0], S->*NP VP[0])'),
    ('VP -> * V NP  [1]',       'PREDICT from S->NP*VP'),
    ('VP -> * V ADVP  [1]',     'PREDICT from S->NP*VP'),
    ('V -> * flies  [1]',       'PREDICT from VP->*V ...'),
    ('V -> * like  [1]',        'PREDICT from VP->*V ...'),
    ('N -> * time/flies/arrow  [1]', 'PREDICT (NP->N*N needs N@1)'),
])

story += col_table(2, 'flies', [
    ('N -> flies *  [1]',       'SCAN (N->*flies[1])'),
    ('V -> flies *  [1]',       'SCAN (V->*flies[1])'),
    ('NP -> N N *  [0]',        'ATTACH (N->flies*[1], NP->N*N[0])'),
    ('VP -> V * NP  [1]',       'ATTACH (V->flies*[1], VP->*V NP[1])'),
    ('VP -> V * ADVP  [1]',     'ATTACH (V->flies*[1], VP->*V ADVP[1])'),
    ('S -> NP * VP  [0]',       'ATTACH (NP->NN*[0], S->*NP VP[0])'),
    ('NP -> * N N/D N/N  [2]',  'PREDICT from VP->V*NP @2'),
    ('ADVP -> * ADV NP  [2]',   'PREDICT from VP->V*ADVP @2'),
    ('ADV -> * like  [2]',      'PREDICT from ADVP->*ADV NP'),
    ('V -> * flies/like  [2]',  'PREDICT (ambiguous S->NP*VP via NP->NN*)'),
])

story += col_table(3, 'like', [
    ('ADV -> like *  [2]',      'SCAN (ADV->*like[2])'),
    ('V -> like *  [2]',        'SCAN (V->*like[2])'),
    ('ADVP -> ADV * NP  [2]',   'ATTACH (ADV->like*[2], ADVP->*ADV NP[2])'),
    ('VP -> V * NP  [2]',       'ATTACH (V->like*[2], VP->*V NP[2])'),
    ('VP -> V * ADVP  [2]',     'ATTACH (V->like*[2], VP->*V ADVP[2])'),
    ('NP -> * N N/D N/N  [3]',  'PREDICT from ADVP->ADV*NP, VP->V*NP @3'),
    ('ADVP -> * ADV NP  [3]',   'PREDICT from VP->V*ADVP @3'),
    ('D -> * an  [3]',          'PREDICT from NP->*D N @3'),
    ('ADV -> * like  [3]',      'PREDICT from ADVP->*ADV NP @3'),
])

story += col_table(4, 'an', [
    ('D -> an *  [3]',          'SCAN (D->*an[3])'),
    ('NP -> D * N  [3]',        'ATTACH (D->an*[3], NP->*D N[3])'),
    ('N -> * time  [4]',        'PREDICT (NP->D*N needs N@4)'),
    ('N -> * flies  [4]',       'PREDICT'),
    ('N -> * arrow  [4]',       'PREDICT'),
])

story += col_table(5, 'arrow', [
    ('N -> arrow *  [4]',           'SCAN (N->*arrow[4])'),
    ('NP -> D N *  [3]',            'ATTACH (N->arrow*[4], NP->D*N[3])'),
    ('ADVP -> ADV NP *  [2]',       'ATTACH (NP->DN*[3], ADVP->ADV*NP[2])'),
    ('VP -> V NP *  [2]',           'ATTACH (NP->DN*[3], VP->V*NP[2])'),
    ('VP -> V ADVP *  [1]',         'ATTACH (ADVP->ADVNP*[2], VP->V*ADVP[1])'),
    ('S -> NP VP *  [0]  <- Parse1','ATTACH via VP->V NP*[2] + S->NP*VP[0]@col2'),
    ('S -> NP VP *  [0]  <- Parse2','ATTACH via VP->VADVP*[1] + S->NP*VP[0]@col1'),
    ('ROOT -> S *  [0]  ACCEPT',    'ATTACH best S*[0] -> ROOT->*S[0]'),
])

story += callout(
    '<b>Structural ambiguity:</b> Two complete S->NP VP*[0] items appear in column 5. '
    'Parse 1: "time flies" as compound NP, "like" as V. '
    'Parse 2 (best): "time" as NP, "flies" as V, "like an arrow" as ADVP. '
    'The Viterbi parser selects Parse 2 (weight = 7.802, lower is better).',
    color=STEEL, icon='i')

story += [PageBreak()]
story += section_header('Q2', 'Parse Tree Probabilities', '10 marks')

story += [Paragraph(
    'The sentence has exactly <b>two</b> parse trees due to lexical ambiguity: '
    '"flies" in {N, V} and "like" in {V, ADV}. '
    'Rule probabilities are used as weights: weight = -log2(prob); '
    'total weight of a tree = sum of all rule weights.', body)]

story += [Paragraph('Parse Tree 1 - "time flies" as compound NP; "like" as verb', h2)]
story += Code(
    '(ROOT\n'
    '  (S\n'
    '    (NP (N time) (N flies))          NP -> N N    [P=0.25]\n'
    '    (VP\n'
    '      (V like)                       VP -> V NP   [P=0.6]\n'
    '      (NP (D an) (N arrow)))))       NP -> D N    [P=0.4]'
)
p1_rows = [
    ['Rule', 'Prob.', '-log2(prob)'],
    ['ROOT -> S',   '1.0',  '0.0'],
    ['S -> NP VP',  '1.0',  '0.0'],
    ['NP -> N N',   '0.25', '2.0'],
    ['N -> time',   '0.4',  '1.322'],
    ['N -> flies',  '0.2',  '2.322'],
    ['VP -> V NP',  '0.6',  '0.737'],
    ['V -> like',   '0.5',  '1.0'],
    ['NP -> D N',   '0.4',  '1.322'],
    ['D -> an',     '1.0',  '0.0'],
    ['N -> arrow',  '0.4',  '1.322'],
    ['Total weight', '', '10.025'],
    ['P(Parse 1)', '', '2^-10.025 = approx 0.000965'],
]
story += [tbl(p1_rows, col_widths=[6*cm, 2*cm, 7.5*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph('Parse Tree 2 - "time" as NP; "flies" as V; "like an arrow" as ADVP  [BEST PARSE]', h2)]
story += Code(
    '(ROOT\n'
    '  (S\n'
    '    (NP (N time))                    NP -> N      [P=0.35]\n'
    '    (VP\n'
    '      (V flies)                      VP -> V ADVP [P=0.4]\n'
    '      (ADVP\n'
    '        (ADV like)                   ADVP -> ADV NP [P=1.0]\n'
    '        (NP (D an) (N arrow))))))'
)
p2_rows = [
    ['Rule', 'Prob.', '-log2(prob)'],
    ['ROOT -> S',      '1.0', '0.0'],
    ['S -> NP VP',     '1.0', '0.0'],
    ['NP -> N',        '0.35','1.515'],
    ['N -> time',      '0.4', '1.322'],
    ['VP -> V ADVP',   '0.4', '1.322'],
    ['V -> flies',     '0.5', '1.0'],
    ['ADVP -> ADV NP', '1.0', '0.0'],
    ['ADV -> like',    '1.0', '0.0'],
    ['NP -> D N',      '0.4', '1.322'],
    ['D -> an',        '1.0', '0.0'],
    ['N -> arrow',     '0.4', '1.322'],
    ['Total weight', '', '7.802  [BEST]'],
    ['P(Parse 2)', '', '2^-7.802 = approx 0.00449  [4.65x more likely]'],
]
story += [tbl(p2_rows, col_widths=[6*cm, 2*cm, 7.5*cm]), Spacer(1, 0.3*cm)]

story += callout(
    '<b>Conclusion:</b> Parse 2 is <b>4.65x more probable</b> than Parse 1 (lower weight wins). '
    'The Viterbi parser outputs Parse 2. '
    'Weight verified: python parse.py q1.gr q1.sen -> 7.802285...',
    color=GOLD, icon='*')

story += [PageBreak()]
story += section_header('Q3', 'Grammar for "the man shot the soldier with a gun"', '10 marks')

story += [Paragraph(
    'This sentence is <b>structurally ambiguous</b> due to PP-attachment. '
    '"with a gun" can attach to the <b>VP</b> (instrument - the man used a gun) '
    'or to the <b>NP</b> "the soldier" (possession - the soldier had a gun).', body)]

story += [Paragraph('Designed Grammar - q3.gr:', h2)]
story += Code(
    '1    ROOT  S\n'
    '1    S     NP VP\n'
    '0.3  NP    NP PP        # PP-attachment onto NP (reading B)\n'
    '0.7  NP    Det N\n'
    '0.6  VP    V NP\n'
    '0.4  VP    VP PP        # PP-attachment onto VP (reading A)\n'
    '1    PP    P NP\n'
    '1    Det   the\n'
    '1    Det   a\n'
    '0.33 N     man\n'
    '0.33 N     soldier\n'
    '0.34 N     gun\n'
    '1    V     shot\n'
    '1    P     with'
)

story += [Paragraph('Two Competing Readings:', h2)]
story += Code(
    'Reading A (VP-attachment - instrument, most likely):\n'
    '(ROOT (S (NP (Det the) (N man))\n'
    '         (VP (VP (V shot) (NP (Det the) (N soldier)))\n'
    '             (PP (P with) (NP (Det a) (N gun)))))\n\n'
    'Reading B (NP-attachment - possession):\n'
    '(ROOT (S (NP (Det the) (N man))\n'
    '         (VP (V shot)\n'
    '             (NP (NP (Det the) (N soldier))\n'
    '                 (PP (P with) (NP (Det a) (N gun)))))))'
)

story += [Paragraph('Probability Comparison:', h2)]
ab = [
    ['Component', 'Reading A  (VP->VP PP)', 'Reading B  (NP->NP PP)'],
    ['S -> NP VP',       '1.0',   '1.0'],
    ['NP -> Det N (man)','0.7',   '0.7'],
    ['N -> man',         '0.33',  '0.33'],
    ['VP structure',     'VP -> V NP  [0.6]', 'VP -> V NP  [0.6]'],
    ['V -> shot',        '1.0',   '1.0'],
    ['object NP',     'NP -> Det N  [0.7*0.33]', 'NP -> NP PP  [0.3]'],
    ['NP-PP attach',     'VP -> VP PP  [0.4]', 'already in NP->NP PP [0.3]'],
    ['P(Reading)',   'approx 0.000305', 'approx 0.000229'],
    ['Winner',      'VP-attachment (1.33x more likely)', '---'],
]
story += [tbl(ab, col_widths=[4*cm, 5.5*cm, 5.5*cm]), Spacer(1, 0.3*cm)]

story += callout(
    '<b>Verified by parser:</b> python parse.py q3.gr q3.sen outputs the VP-attachment reading '
    'with weight 8.3579. Both analyses are tracked in the chart; '
    'both S->NP VP*[0] completions appear in column 8.',
    color=GREEN_OK, icon='OK')

story += [Paragraph('Earley Chart Summary (8 words, columns 0-8):', h2)]
story += [Paragraph('| the | man | shot | the | soldier | with | a | gun |', mono)]
q3c = [
    ['Col.', 'Key items completed / predicted', 'Notes'],
    ['0', 'ROOT->*S, S->*NP VP, NP->*Det N, NP->*NP PP, Det->*the', 'init + predict all'],
    ['1 (the)', 'Det->the*[0],  NP->Det*N[0]', 'SCAN + ATTACH'],
    ['2 (man)', 'N->man*[1],  NP->Det N*[0],  S->NP*VP[0],\nVP->*V NP[2], VP->*VP PP[2], V->*shot[2]', 'both VP rules predicted'],
    ['3 (shot)', 'V->shot*[2],  VP->V*NP[2]', 'VP starts building'],
    ['4 (the)', 'Det->the*[3],  NP->Det*N[3]', 'inner NP starts'],
    ['5 (soldier)', 'N->soldier*[4],  NP->Det N*[3]\nNP->NP*PP[3]  <- ambiguity seed\nVP->V NP*[2] <- complete VP', 'both readings alive'],
    ['6 (with)', 'P->*with[5],  PP->*P NP[5]', 'PP predicts'],
    ['7 (a)', 'Det->a*[6],  NP->Det*N[6]', 'inner gun-NP starts'],
    ['8 (gun)', 'N->gun*[7],  NP->Det N*[6]\nPP->P NP*[5]\nVP->VP PP*[2]  <- Reading A\nNP->NP PP*[3] -> VP->V NP*[2]  <- Reading B\nS->NP VP*[0] (x2) <- BOTH PARSES\nROOT->S*[0]  ACCEPT', 'both parses found'],
]
story += [tbl(q3c, col_widths=[1.5*cm, 9*cm, 4.5*cm])]

story += [PageBreak()]
story += section_header('Q4', 'Implementation - Correctness and Efficiency', '10 marks')

story += [Paragraph('4.1  Correctness: Tracking the Best Derivation', h2)]
story += [Paragraph('Each chart item is an ItemWithParseInfo dataclass containing five fields:', body)]
fields = [
    ['Field',          'Type',    'Purpose'],
    ['rule',           'Rule',    'The grammar rule (lhs, rhs, weight = -log2 P)'],
    ['dot_position',   'int',     'How many RHS symbols have been matched'],
    ['start_position', 'int',     'Input position where this item started'],
    ['weight',         'float',   'Cumulative -log2 probability - LOWER is BETTER'],
    ['children',       'List',    'Ordered child items / tokens for tree reconstruction'],
]
story += [tbl(fields, col_widths=[3.5*cm, 2.5*cm, 9.5*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph('Viterbi re-enqueue in Agenda.push():', bold)]
story += Code(
    'item_key = (item.rule, item.dot_position, item.start_position)\n\n'
    'if item_key in self._index:\n'
    '    idx = self._index[item_key]\n'
    '    if item.weight < self._items[idx].weight:   # strictly cheaper\n'
    '        if idx < self._next:                    # already popped?\n'
    '            # Cheaper version arrived AFTER old one was processed.\n'
    '            # Re-enqueue so cheaper cost propagates via ATTACH.\n'
    '            self._items.append(item)\n'
    '            self._index[item_key] = len(self._items) - 1\n'
    '        else:\n'
    '            self._items[idx] = item             # replace in-place\n'
    '    # else: ignore heavier duplicate\n'
    'else:\n'
    '    self._items.append(item)                    # brand-new item\n'
    '    self._index[item_key] = len(self._items) - 1'
)
story += [Paragraph(
    'Without re-enqueue, a cheaper derivation arriving after the old item was popped would '
    'never propagate downstream. The Section D reading explicitly warns: '
    '"you must re-process this lower-weight version of Z." '
    'Our implementation handles this at O(1) by appending and updating the index pointer.', body)]

story += [Paragraph('4.2  Efficiency: O(n^2) Space and O(n^3) Time', h2)]
eff = [
    ['Operation',            'Naive',         'Our solution',           'Mechanism'],
    ['push() duplicate check','O(n) scan',    'O(1) expected',          '_index dict: (rule,dot,start)->idx'],
    ['ATTACH customer lookup','O(n) scan col','O(1) expected',          '_wants dict in parse2.py: symbol->list'],
    ['PREDICT deduplication', 'O(n) per NT',  'O(1) amortised',         '_predicted Set in parse2.py'],
    ['Beam pruning',          'none',          'O(k log k) per col',     'Agenda.prune(beam_width)'],
]
story += [tbl(eff, col_widths=[4*cm, 3*cm, 3*cm, 5.5*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph('Why O(1) push is necessary:', bold),
    Paragraph(
        'In the worst case O(n^2) chart cells each try to insert O(|G|) items. '
        'If each insert requires an O(n) linear scan for duplicates, total time becomes '
        'O(n^3 * |G|) - infeasibly slow for large grammars. With O(1) hash lookup the '
        'total insertion work is O(n^2 * |G|), keeping the algorithm within O(n^3).',
        body),
    Paragraph('Space complexity:', bold),
    Paragraph(
        'n+1 columns, each with at most O(|G|*n) distinct items. '
        'Total: O(n^2 * |G|) = O(n^2) for fixed grammar size.', body),
]

story += [Paragraph('4.3  parse2.py Additional Optimisations', h2)]
story += Code(
    '# 1. PREDICTION CACHING - never re-predict (symbol, position)\n'
    'self._predicted: Set[Tuple[str,int]] = set()\n'
    'def _predict_cached(self, sym, pos):\n'
    '    if (sym, pos) not in self._predicted:\n'
    '        self._predicted.add((sym, pos))\n'
    '        self._predict(sym, pos)\n\n'
    '# 2. O(1) CUSTOMER LOOKUP - _wants index per column\n'
    'def customers_for(self, symbol):\n'
    '    for idx in self._wants.get(symbol, []):\n'
    '        item = self._items[idx]\n'
    '        if self._index.get((item.rule,item.dot_position,\n'
    '                            item.start_position)) == idx:\n'
    '            yield item            # still the canonical copy\n\n'
    '# 3. BEAM PRUNING - trim low-prob items after each column\n'
    'def prune(self, beam_width):\n'
    '    unprocessed = self._items[self._next:]\n'
    '    unprocessed.sort(key=lambda x: x.weight)\n'
    '    self._items = self._items[:self._next] + unprocessed[:beam_width]'
)
story += callout(
    '<b>Section D compliance:</b> Section B.2 of the JHU reading describes the reprocessing '
    'requirement. Our Viterbi re-enqueue satisfies it. Section D.E.1 describes prediction caching; '
    'our _predicted set implements exactly this speedup.',
    color=STEEL, icon='i')

story += [PageBreak()]
story += section_header('V', 'Parser Verification and Test Results', 'All grammars')

story += [Paragraph('arith.gr - Weight Verification against arith.par', h2)]
story += [Paragraph(
    'The JHU handout (Section D) provides arith.par as a reference output. '
    'Our parser weights match exactly:', body)]
arith_d = [
    ['Input sentence',                   'Our weight',            'arith.par weight', 'Match?'],
    ['3',                                '8.455324334921691',     '8.455324334921691', 'Y'],
    ['3 *',                              'No parse',              'No parse (NONE)',   'Y'],
    ['3 * 5',                            '15.325693382592382',    '15.325693382592382','Y'],
    ['3 * 5 + 6 * { 5-3-2 } + sqrt{7}', '65.52713910236838',    '65.52713910236838', 'Y'],
]
story += [tbl_check(arith_d, col_widths=[5.5*cm, 4*cm, 4*cm, 1.5*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph('wallstreet.gr - Benchmark Weights (Section D)', h2)]
story += [Paragraph(
    'The JHU reading states: "For the first two sentences in wallstreet.sen, '
    'the lowest-weighted parses have weights of 34.22401 and 104.90923."', body)]
ws_bench = [
    ['Sentence', 'Expected', 'parse2.py output', 'Match?'],
    ['John is happy .', '34.22401', '34.22401061796059', 'Y'],
    ['The very biggest companies are not likely to go under .',
     '104.90923', '104.90922564708923', 'Y'],
]
story += [tbl_check(ws_bench, col_widths=[7*cm, 2.5*cm, 3.5*cm, 1.5*cm]), Spacer(1, 0.3*cm)]
story += callout(
    'Both wallstreet benchmarks match to the precision given in the JHU reading. '
    'All 9 wallstreet sentences parsed successfully using parse2.py. '
    'parse.py also parses all 9 but takes longer (~20 min on wallstreet due to O(n) scan per item).',
    color=GREEN_OK, icon='OK')

story += [Paragraph('permissive.gr / permissive2.gr - Ambiguous Grammars', h2)]
perm_d = [
    ['Input', 'permissive.gr (A->AA|x)', 'permissive2.gr (A,B interchangeable)'],
    ['x',        '(ROOT (A x))',        '(ROOT (A x))'],
    ['x x',      '(ROOT (A (A x) (A x)))',         '(ROOT (A (A x) (A x)))'],
    ['x x x',    '(ROOT (A (A (A x)(A x)) (A x)))', '(ROOT (A (A (A x)(A x)) (A x)))'],
    ['x x x x',  'left-branching Viterbi tree',     'left-branching Viterbi best'],
    ['x x x x x','left-branching Viterbi tree',     'left-branching Viterbi best'],
]
story += [tbl(perm_d, col_widths=[2*cm, 6.5*cm, 6.5*cm]), Spacer(1, 0.3*cm)]
story += [Paragraph(
    'A string of n x\'s has Catalan number C(n-1) parse trees. '
    'The parser returns only the single best Viterbi parse.', note)]

story += [Paragraph('papa.gr - Classic PP-attachment Grammar', h2)]
papa_d = [
    ['Input sentence',                     'Output'],
    ['Papa ate the caviar',                '(ROOT (S (NP Papa) (VP (V ate) (NP (Det the) (N caviar)))))  w=6.158'],
    ['Papa ate caviar',                    'NONE  (no Det-less NP rule in papa.gr)'],
    ['Papa ate the',                       'NONE  (incomplete NP)'],
    ['Papa ate the caviar with a spoon',   '(ROOT (S (NP Papa) (VP (VP (V ate) (NP (Det the) (N caviar))) (PP (P with) (NP (Det a) (N spoon))))))  w=10.217  [VP-attach wins]'],
    ['ate the caviar',                     'NONE  (no subject)'],
    ['the caviar ate a spoon',             '(ROOT (S (NP (Det the) (N caviar)) (VP (V ate) (NP (Det a) (N spoon)))))  w=5.158'],
    ['the caviar is pink',                 'NONE  (no copula / no colour adj in papa.gr)'],
]
story += [tbl(papa_d, col_widths=[5.5*cm, 10*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph('english.gr - Feature-Rich English Grammar (25 sentences)', h2)]
story += [Paragraph('All 25 sentences in english.sen parsed successfully. Notable features handled:', body)]
eng_feat = [
    ['Feature',                  'Example sentence',                        'Parse excerpt'],
    ['Morphological split',      'Joe love -s Jill .',                      '(VP (V (V love) -s) (NP Jill))'],
    ['Modals',                   'Papa would have eat -ed his sandwich -s .','(VP (Modal would) (VP (V have) ...))'],
    ['Complement clause',        'Jill say -s that Joe might sleep ...',    '(VP (VP (V say -s) (CP that (S ...))))'],
    ['Raising / control',        'Papa want -ed Joe to eat a pickle .',     '(VP (V want -ed) (NP Joe) (VP to eat ...))'],
    ['Adjective + copula',       'Papa is perplexed .',                     '(VP (V is) (Adj perplexed))'],
    ['NP coordination',          'the fine and blue woman and every man ...','(NP (NP ...) and (NP ...))'],
    ['Imperative',               'have a bonbon !',                         '(ROOT (VP (V have) (NP ...)) !)'],
    ['Nominal N-PP stacking',    'a bonbon on the spoon entice -s .',       '(NP (N (N bonbon) (PP on ...)))'],
]
story += [tbl(eng_feat, col_widths=[4*cm, 5*cm, 6.5*cm]), Spacer(1, 0.3*cm)]

story += [Paragraph('wallstreet.gr - Real WSJ PCFG (228 KB, 9 sentences)', h2)]
ws_d = [
    ['Sentence (abbreviated)', 'Best parse root structure'],
    ['John is happy .',
     '(S (NP (NPR John)) (VP (VBZ is) (ADJP-PRD happy)) .)'],
    ['The very biggest companies are not likely to go under .',
     '(S (NP DT ADJP NNS) (VP VBP RB ADVP VP) .)'],
    ['The market is wondering what General Motors has done .',
     '(S (NP ...) (VP ... (SBAR (WHNP what) (S ... VP)) ...))'],
    ['In recent years , pay surged as demand rose ...',
     '(S (PP In...) , (NP pay) (VP surged (SBAR as ... while ...)) .)'],
    ['caught off guard , Ford Motor Co. had no choice ...',
     '(S (S-ADV caught off guard) , (NP Ford ...) (VP had ...) .)'],
    ['data show that pay was flat for third consecutive quarter ...',
     '(S (NP data) (VP show (SBAR that (S VP ...))) .)'],
    ['running the combined companies ... is likely to pose ...',
     '(S (VP running (S ...)) , (VP is ... pose ...) .)'],
    ['a senior intelligence official said the administration ...',
     '(S (NP official) (VP said (SBAR (S ... VP ...))) .)'],
    ["`` It \'s very real ... \'\' this official said .",
     "(S (PUNC``) (S-TPC It's ...) , (PUNC'') official said .)"],
]
story += [tbl(ws_d, col_widths=[7.5*cm, 8*cm]), Spacer(1, 0.3*cm)]

story += [PageBreak()]
story += section_header('R', 'Robustness: Unseen Grammar Test', 'Autograder generalisation')

story += [Paragraph(
    'The assignment states: "The autograder will test your program on new grammars and '
    'sentences that you have not seen." To demonstrate generalisation, '
    'we designed unseen.gr - a "colours and objects" toy grammar not from '
    'the JHU dataset. The parser was run without any modifications.', body)]

story += [Paragraph('unseen.gr - Colours and Objects Grammar:', h2)]
story += Code(
    '1    ROOT  S\n'
    '0.6  S     NP VP\n'
    '0.4  S     NP VP PP        # adverbial PP\n'
    '0.5  NP    Name\n'
    '0.3  NP    Det N\n'
    '0.2  NP    Det Adj N\n'
    '0.6  VP    V NP\n'
    '0.4  VP    V               # intransitive\n'
    '1    PP    P NP\n'
    '# Lexical entries\n'
    '0.5  Name  Alice  |  0.5  Name  Bob\n'
    '0.5  Det   the    |  0.5  Det   a\n'
    '0.4  N     cat    |  0.3  N     robot    |  0.3  N     table\n'
    '0.5  V     likes  |  0.5  V     sees\n'
    '0.4  Adj   red    |  0.3  Adj   broken   |  0.3  Adj   small\n'
    '0.5  P     near   |  0.5  P     under'
)

story += [Paragraph('Results - python parse.py unseen.gr unseen.sen:', h2)]
un_d = [
    ['Input sentence',                       'Result',      'Parse',                         'Weight'],
    ['Alice likes the cat',                  'Y',
     '(ROOT (S (NP Alice) (VP likes (NP the cat))))', '8.533'],
    ['Bob sees a red robot',                 'Y',
     '(ROOT (S (NP Bob) (VP sees (NP a red robot))))', '10.855'],
    ['Alice likes Bob near the table',       'Y',
     '(ROOT (S (NP Alice) (VP likes (NP Bob)) (PP near (NP the table))))', '12.533'],
    ['the robot sees Alice',                 'Y',
     '(ROOT (S (NP the robot) (VP sees (NP Alice))))', '8.948'],
    ['Alice likes the small broken robot',   'N (no parse)',
     'Grammar has no Adj Adj N rule', '---'],
    ['a dog barks',                          'N (no parse)',
     'OOV words: "dog", "barks" not in grammar', '---'],
]
story += [tbl_check(un_d, col_widths=[4.5*cm, 1.8*cm, 5.7*cm, 1.8*cm]), Spacer(1, 0.3*cm)]

story += callout(
    '<b>Interpretation:</b> All in-vocabulary sentences covering S->NP VP and S->NP VP PP rules '
    'parse correctly with sensible weights. '
    'Failures are graceful and correct: the grammar deliberately omits NP->Det Adj Adj N '
    '(no stacked adjectives) and does not include "dog" or "barks". '
    'The parser prints NONE and continues without crashing.',
    color=GREEN_OK, icon='OK')

story += [Paragraph('Why this demonstrates autograder robustness:', h2)]
rob = [
    ['Scenario tested', 'Outcome'],
    ['Completely new nonterminals (Name, Adj, PP)',   'Y - Handled correctly'],
    ['New terminal vocabulary (Alice, Bob, cat, ...)',  'Y - Handled correctly'],
    ['S -> NP VP PP  (3-daughter rule)',               'Y - Parsed correctly'],
    ['Out-of-vocabulary word',                         'Y - Graceful failure (no crash)'],
    ['Grammar rule not present (Adj Adj N)',           'Y - Graceful failure (no crash)'],
    ['Equal-weight terminal alternatives (0.5|0.5)',   'Y - Consistent tie-breaking'],
    ['Mixed parses and no-parses in same .sen file',   'Y - Each sentence independent'],
]
story += [tbl(rob, col_widths=[9*cm, 6.5*cm])]

story += [PageBreak()]
story += section_header('S', 'Summary', 'Complete scorecard')

final = [
    ['Q', 'Marks', 'Topic', 'Key result'],
    ['Q1', '20', "Earley chart - 'time flies'",
     '6-column chart; 2 complete parses in col 5 (structural ambiguity shown)'],
    ['Q2', '10', 'Parse probabilities',
     'P1 = 0.000965 (w=10.025)  vs  P2 = 0.00449 (w=7.802)\nParse 2 wins (4.65x more probable); verified by parser output'],
    ['Q3', '10', 'PP-attachment grammar',
     'VP-attach P~0.000305 > NP-attach P~0.000229\nBoth readings found in chart column 8; VP reading output'],
    ['Q4', '10', 'Correctness + Efficiency',
     'Viterbi re-enqueue prevents missed cheaper derivations\nO(1) push (_index) + O(1) attach (_wants) + prediction cache'],
    ['R', '--', 'Robustness (unseen grammar)',
     'unseen.gr: 4/6 parse, 2/6 correct no-parse\narith weights match arith.par exactly; wallstreet benchmarks match'],
    ['Total','50','All problems solved',
     'Verified on 6 grammars: papa, english, arith, permissive, permissive2, wallstreet'],
]
story += [tbl(final, col_widths=[0.9*cm, 1.4*cm, 4.5*cm, 8.7*cm]), Spacer(1, 0.5*cm)]

story += [
    Paragraph('Files submitted:', bold),
    tbl([
        ['File', 'Purpose'],
        ['parse.py',       'Probabilistic Earley parser - primary submission (Q3)'],
        ['parse2.py',      'Optimised parser with O(1) attach + beam pruning (Q4)'],
        ['q1.gr / q1.sen', "Grammar + sentence for Q1/Q2 ('time flies like an arrow')"],
        ['q3.gr / q3.sen', "Grammar + sentence for Q3 ('the man shot the soldier with a gun')"],
        ['unseen.gr / unseen.sen', 'Custom grammar for robustness test'],
        ['REPORT.md',      'Markdown version of this report'],
        ['Earley_Parser_Report.pdf', 'This PDF submission'],
    ], col_widths=[5*cm, 10.5*cm]),
    Spacer(1, 0.5*cm),
    Paragraph('GitHub: https://github.com/MuditGupta2502/earley-parser', note),
]

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=3.0*cm, bottomMargin=1.8*cm,
    title='Earley Parser Assignment Report',
    author='MuditGupta2502',
)
doc.build(story, canvasmaker=HeaderFooterCanvas)
print(f'PDF written to: {OUTPUT}')