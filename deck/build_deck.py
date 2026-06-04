"""Build the Phase One capstone defence deck from template.pptx.

Academic deck mirroring the report's chapter structure, theory-forward:
Introduction, Related Work and the Research Gap, Theoretical Foundations,
Proposed Solution, Implementation and Evaluation, Conclusion and Future Work.
Foundations and Proposed Solution carry the weight. Conceptual diagrams and
prose carry the argument; exploratory charts and live screenshots appear only
as evidence in the implementation section. Voice and vocabulary follow
report/CONVENTION.md (third person, no em dash, no product names).

Templates: T1 title (dark) · T2 outline (light) · T3 divider (dark) ·
T4 visual-dominant (light) · T5 split text+visual (light) · T6 anchor
(visual + stacked stat cards) · T7 close (dark).
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAG = os.path.join(ROOT, "report", "images", "diagrams")
FIG  = os.path.join(ROOT, "report", "images", "figures")
LOGO = os.path.join(ROOT, "report", "images", "logos")
SHOT = ROOT  # legacy live-prototype screenshots live at repo root
SHOTS = os.path.join(ROOT, "report", "images", "screenshots")  # demo captures
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

# ---- palette ----------------------------------------------------------------
NAVY   = RGBColor(0x1F, 0x3A, 0x5F)
BLUE   = RGBColor(0x2E, 0x75, 0xB6)
ICE    = RGBColor(0xCA, 0xDC, 0xFC)
ACCENT = RGBColor(0xE0, 0x7B, 0x2B)   # focal orange (Knaflic single accent)
REJECT = RGBColor(0xC0, 0x39, 0x2B)   # red for the integrity-fail callout
GREEN  = RGBColor(0x2E, 0x7D, 0x32)
CARD   = RGBColor(0xF2, 0xF6, 0xFB)
CARD2  = RGBColor(0xE7, 0xEF, 0xF8)
GREYTX = RGBColor(0x44, 0x4E, 0x5C)   # darkened for projection contrast
LINE   = RGBColor(0xA6, 0xB7, 0xCC)   # darker border for definition at distance
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
DARK   = RGBColor(0x14, 0x1A, 0x24)
REDTNT = RGBColor(0xFB, 0xEC, 0xEA)
FONT   = "Calibri"

SW, SH = 13.333, 7.5

prs = Presentation(os.path.join(ROOT, "template.pptx"))

# delete the demo slides cleanly (drop rels so parts are not serialized)
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.get(RID))
    sldIdLst.remove(sldId)

LAYOUTS = {l.name: l for l in prs.slide_masters[0].slide_layouts}

# ---- low-level helpers ------------------------------------------------------
def _set_text(tf, text, size, color, bold=False, align=PP_ALIGN.LEFT,
              font=FONT, anchor=None, italic=False, line_spacing=None):
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    r = p.add_run(); r.text = text
    f = r.font
    f.size = Pt(size); f.bold = bold; f.italic = italic
    f.name = font; f.color.rgb = color
    if anchor is not None:
        tf.vertical_anchor = anchor
    return p

def textbox(slide, l, t, w, h, text, size, color, bold=False,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
            line_spacing=None):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    _set_text(tf, text, size, color, bold, align, anchor=anchor,
              italic=italic, line_spacing=line_spacing)
    return tb

def add_lines(tb, lines):
    """lines = list of (text,size,color,bold,italic). First uses para0."""
    tf = tb.text_frame; tf.word_wrap = True
    for i, (text, size, color, bold, italic) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(6)
        r = p.add_run(); r.text = text
        f = r.font
        f.size = Pt(size); f.bold = bold; f.italic = italic
        f.name = FONT; f.color.rgb = color
    return tb

def bullets(slide, l, t, w, h, items, anchor=MSO_ANCHOR.TOP, space=7):
    """Template-style bullet list: round bullet in the brand blue, hanging
    indent so wrapped lines align under the text, big legible runs.
    items = list of (text, size, color, bold, italic, bulleted)."""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    for i, (text, size, color, bold, italic, bulleted) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(space)
        pPr = p._p.get_or_add_pPr()
        if bulleted:
            pPr.set('marL', str(Inches(0.30)))
            pPr.set('indent', str(Inches(-0.30)))
            buClr = pPr.makeelement(qn('a:buClr'), {})
            buClr.append(buClr.makeelement(qn('a:srgbClr'), {'val': '2E75B6'}))
            buFont = pPr.makeelement(qn('a:buFont'), {'typeface': FONT})
            buChar = pPr.makeelement(qn('a:buChar'), {'char': '•'})
            pPr.append(buClr); pPr.append(buFont); pPr.append(buChar)
        else:
            pPr.append(pPr.makeelement(qn('a:buNone'), {}))
        r = p.add_run(); r.text = text
        f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic
        f.name = FONT; f.color.rgb = color
    return tb

def rrect(slide, l, t, w, h, fill, line=None, line_w=1.0,
          shape=MSO_SHAPE.RECTANGLE, shadow=False):
    sp = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    return sp

def leftbar(slide, l, t, h, color=ACCENT, w=0.07):
    """Thin solid accent rule on the left edge of a block, the deck's one motif."""
    return rrect(slide, l, t, w, h, color, shape=MSO_SHAPE.RECTANGLE)

def shape_text(sp, lines, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
               mtop=0.04, mbot=0.04, mlr=0.08):
    tf = sp.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(mlr); tf.margin_right = Inches(mlr)
    tf.margin_top = Inches(mtop); tf.margin_bottom = Inches(mbot)
    for i, (text, size, color, bold, italic) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = text
        f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic
        f.name = FONT; f.color.rgb = color

def card_block(slide, x, y, w, h, accent, fill, lines, mlr=0.28,
               anchor=MSO_ANCHOR.MIDDLE, line=None, line_w=1.0):
    """Flat card: background rect + left accent rule + a PLAIN textbox overlay.
    Card text lives in a real textbox (not the autoshape) so it wraps in every
    renderer; the autoshape carries only the fill."""
    rrect(slide, x, y, w, h, fill, line=line, line_w=line_w)
    if accent is not None:
        leftbar(slide, x, y, h, accent, w=0.09)
    tb = slide.shapes.add_textbox(Inches(x + mlr), Inches(y),
                                  Inches(w - mlr - 0.14), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    for i, (text, size, color, bold, italic) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(2)
        r = p.add_run(); r.text = text
        f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic
        f.name = FONT; f.color.rgb = color
    return tb

def fit_image(slide, path, bl, bt, bw, bh):
    """Place image fitted within box (bl,bt,bw,bh) inches, preserving AR, centered."""
    iw, ih = Image.open(path).size
    ar = iw / ih
    box_ar = bw / bh
    if ar > box_ar:
        w = bw; h = bw / ar
    else:
        h = bh; w = bh * ar
    l = bl + (bw - w) / 2
    t = bt + (bh - h) / 2
    return slide.shapes.add_picture(path, Inches(l), Inches(t),
                                    Inches(w), Inches(h))

# ---- template helpers -------------------------------------------------------
def body_slide(title, tsize=27):
    """T4/T5 base: clean light slide, action title in the placeholder."""
    s = prs.slides.add_slide(LAYOUTS["Title and Content"])
    title_ph = s.placeholders[0]
    title_ph.text_frame.text = title
    r = title_ph.text_frame.paragraphs[0].runs[0]
    r.font.bold = True; r.font.color.rgb = NAVY; r.font.size = Pt(tsize)
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 1:
            ph._element.getparent().remove(ph._element)
    return s

def content_slide(title, subtitle=None):
    s = body_slide(title)
    if subtitle:
        textbox(s, 0.6, 1.55, SW - 1.2, 0.4, subtitle.upper(), 13, BLUE,
                bold=True, italic=False)
    return s


def _source(s, cite):
    """Small source citation in the bottom-right corner (theory slides)."""
    textbox(s, 6.5, 7.18, 6.23, 0.28, cite, 9, GREYTX, italic=True,
            align=PP_ALIGN.RIGHT)

def dark_slide():
    """Blank dark full-bleed slide, no decoration."""
    s = prs.slides.add_slide(LAYOUTS["Title and Content"])
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    rrect(s, 0, 0, SW, SH, DARK, shape=MSO_SHAPE.RECTANGLE)
    return s

# T4 — visual-dominant
def visual_slide(title, subtitle, img, caption=None, top=1.85, h=4.85):
    s = content_slide(title, subtitle)
    fit_image(s, img, 0.6, top, SW - 1.2, h)
    if caption:
        textbox(s, 0.6, top + h + 0.05, SW - 1.2, 0.32, caption, 11, GREYTX,
                align=PP_ALIGN.CENTER)
    return s

# T5 — split text (left) + visual (right)
def split_slide(title, subtitle, img, lines, img_box=(4.8, 1.85, 8.05, 5.05)):
    s = content_slide(title, subtitle)
    tb = textbox(s, 0.6, 2.0, 3.95, 4.6, "", 16, NAVY)
    add_lines(tb, lines)
    fit_image(s, img, *img_box)
    return s

# T6 — anchor: visual left + stacked stat cards right
def anchor_slide(title, subtitle, img, cards):
    s = content_slide(title, subtitle)
    fit_image(s, img, 0.6, 1.95, 8.0, 4.75)
    y = 2.25
    for tag, big, sub, color, tint, ln in cards:
        card_block(s, 8.85, y, 3.9, 1.95, ln, tint,
                   [(tag, 14, color, True, False),
                    (big, 26, color, True, False),
                    (sub, 12.5, GREYTX, False, True)], mlr=0.26)
        y += 2.2

# T3 — section divider
def divider(num, name, blurb):
    """Branded section divider on the template's dark title layout."""
    s = prs.slides.add_slide(LAYOUTS["3_Title Slide"])
    s.placeholders[0].text_frame.text = f"{num}  ·  {name}"
    s.placeholders[1].text_frame.text = blurb
    # Institutional logos — top centre, matching template slide 2 exactly
    fit_image(s, os.path.join(LOGO, "vnu_logo.png"), 4.44, -0.11, 2.71, 1.77)
    fit_image(s, os.path.join(LOGO, "bk_logo.png"),  7.16,  0.19, 1.13, 1.08)
    return s

# =============================================================================
# SLIDE 1 — Title (template-branded: VNU + BK logos, footer, pale triangles)
# =============================================================================
s = prs.slides.add_slide(LAYOUTS["2_Title Slide"])
# University logos, top center (BK left, VNU right)
fit_image(s, os.path.join(LOGO, "bk_logo.png"), 5.35, 0.45, 1.05, 0.95)
fit_image(s, os.path.join(LOGO, "vnu_logo.png"), 6.65, 0.56, 1.75, 0.72)
title_ph = s.placeholders[0]
title_ph.text_frame.word_wrap = True
title_ph.text_frame.text = \
    "Studying and Developing Tools to Help Analyze and Visualize Bus Data"
tr = title_ph.text_frame.paragraphs[0].runs[0]
tr.font.bold = True; tr.font.color.rgb = NAVY; tr.font.size = Pt(30)
tr.font.name = FONT

sub_ph = s.placeholders[1]
stf = sub_ph.text_frame; stf.word_wrap = True
sub_lines = [
    ("An analytical and visualization platform for the "
     "Ho Chi Minh City bus network", 16, BLUE, False, True),
    ("", 6, NAVY, False, False),
    ("Huynh Thanh Duy  ·  2252114", 15, NAVY, True, False),
    ("Advisor: Assoc. Prof. Thoai Nam", 14, GREYTX, False, False),
    ("Capstone Defence  ·  Phase One  ·  June 2026", 13, GREYTX, False, True),
]
for i, (text, size, color, bold, italic) in enumerate(sub_lines):
    p = stf.paragraphs[0] if i == 0 else stf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic
    f.name = FONT; f.color.rgb = color

# =============================================================================
# SLIDE 2 — Agenda (T2)
# =============================================================================
s = body_slide("Outline")
agenda = [
    ("1", "Introduction",                          "Motivation, the problem, and the existing tooling"),
    ("2", "Bus and Ticket Data",                   "A dynamic record, its structure, and what it supports"),
    ("3", "Interactive Visualization",             "Each stakeholder's decision, and the interactive views that answer it"),
    ("4", "Data Architecture & Analysis Pipeline", "How the data is stored, analysed, and served to the charts live"),
    ("5", "Implementation and Future Work",        "What is built, and the next phase"),
]
cols = [0.6, 5.2, 9.8]
rows = [2.25, 4.6]
cw = 3.75
for i, (num, name, blurb) in enumerate(agenda):
    cx = cols[i % 3]; cy = rows[i // 3]
    b = rrect(s, cx, cy, 0.62, 0.62, ACCENT, shape=MSO_SHAPE.OVAL)
    shape_text(b, [(num, 22, WHITE, True, False)])
    leftbar(s, cx + 0.82, cy + 0.05, 0.52, NAVY, w=0.04)
    textbox(s, cx + 0.98, cy + 0.0, cw - 0.98, 0.66, name, 16, NAVY,
            bold=True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx, cy + 0.78, cw, 0.9, blurb, 12.5, GREYTX, italic=True)

# =============================================================================
# PART 1 — INTRODUCTION
# =============================================================================
divider("01", "Introduction", "Motivation, the problem, objectives, and scope.")

# Motivation — measured: an important, data-rich network worth understanding.
s = content_slide(
    "HCMC's bus network is data-rich but has no analytical tool",
    "Introduction · motivation")
textbox(s, 0.6, 2.0, 6.0, 0.3, "WHY THIS MATTERS", 12, ACCENT, bold=True)
bullets(s, 0.6, 2.45, 6.0, 3.7, [
    ("Ho Chi Minh City's bus network is the city's primary mass-transit "
     "mode, serving millions of trips, and since 2024 it also feeds the new "
     "Metro Line 1", 15.5, NAVY, False, False, True),
    ("It produces rich operational data continuously: fare collection and "
     "vehicle telemetry, with reference tables for routes, stops and "
     "operators", 15.5, NAVY, False, False, True),
    ("Analyzed and visualized well, that data can help the people who ride, "
     "operate and oversee the network make better-informed decisions", 15.5,
     NAVY, False, False, True),
], space=12)
textbox(s, 0.6, 6.15, 6.0, 0.7,
        "Turning that data into accessible analysis and visualization is the "
        "aim of this work.", 14.5, BLUE, italic=True)
fit_image(s, os.path.join(SHOT, "report", "images", "screenshots",
          "hcm_bus_network.jpg"), 6.95, 2.05, 5.85, 4.35)
textbox(s, 6.95, 6.5, 5.85, 0.3,
        "Route 53, Ben Thanh to Suoi Tien. Source: Lao Dong.",
        10.5, GREYTX, align=PP_ALIGN.CENTER, italic=True)

# The assigned problem decomposed top-down, with objectives and scope.
s = content_slide(
    "The problem, objectives, and scope",
    "Introduction · problem, objectives and scope")
fit_image(s, os.path.join(DIAG, "deck_problem_tree.png"), 0.6, 1.98, 12.13, 3.0)
rrect(s, 0.6, 5.12, 12.13, 0.018, LINE)
textbox(s, 0.6, 5.27, 5.6, 0.32, "OBJECTIVES", 12, ACCENT, bold=True)
bullets(s, 0.6, 5.62, 5.65, 1.8, [
    ("Survey existing tools and research", 12.5, NAVY, False, False, True),
    ("Specify a complete, justified design", 12.5, NAVY, False, False, True),
    ("Demonstrate feasibility with a prototype", 12.5, NAVY, False, False, True),
    ("Plan the Phase-Two build", 12.5, NAVY, False, False, True),
], space=5)
textbox(s, 6.55, 5.27, 3.0, 0.32, "IN SCOPE", 12, BLUE, bold=True)
bullets(s, 6.55, 5.62, 3.05, 1.8, [
    ("Architecture, evaluated and selected", 12, NAVY, False, False, True),
    ("Schema and pipeline, built", 12, NAVY, False, False, True),
    ("Dashboard and interaction, designed", 12, NAVY, False, False, True),
    ("A partial prototype, benchmarked", 12, NAVY, False, False, True),
], space=5)
textbox(s, 9.85, 5.27, 2.9, 0.32, "OUT OF SCOPE", 12, REJECT, bold=True)
bullets(s, 9.85, 5.62, 2.9, 1.8, [
    ("Real-time monitoring", 12.5, GREYTX, False, False, True),
    ("Per-passenger journeys", 12.5, GREYTX, False, False, True),
    ("Exact financials (no cost data)", 12.5, GREYTX, False, False, True),
    ("Live occupancy (no alightings)", 12.5, GREYTX, False, False, True),
], space=5)

# --- Slide 3 of Introduction: existing tools vs the analytical gap (matrix) -
s = content_slide(
    "Existing tools cover routing or a single view; the analytical suite is "
    "missing",
    "Introduction · existing tools and the gap")
textbox(s, 0.6, 1.92, 12.13, 0.36,
        "Five routing apps (BusMap, GoBus!, MultiGo, VinBus, MCPT) and one "
        "research demo (bus.dev.tris.vn) exist; each covers a single capability.",
        14, NAVY)

capW = 4.7
colX = [5.45, 7.95, 10.45]
colW = 2.38
cols = ["Routing apps", "tris.vn demo", "This work"]
hy = 2.55
textbox(s, 0.6, hy, capW, 0.5, "CAPABILITY", 12.5, GREYTX, bold=True,
        anchor=MSO_ANCHOR.MIDDLE)
for i, c in enumerate(cols):
    hl = (i == 2)
    rrect(s, colX[i], hy, colW, 0.5, ACCENT if hl else CARD2,
          line=(ACCENT if hl else LINE), line_w=1.4)
    textbox(s, colX[i], hy, colW, 0.5, c, 13, WHITE if hl else NAVY,
            bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
matrix = [
    ("Real-time trip routing", [1, 0, 0]),
    ("Spatial coverage view",  [0, 1, 1]),
    ("Reliability / QoS",       [0, 0, 1]),
    ("Revenue and operations",  [0, 0, 1]),
    ("School-aware ridership",  [0, 0, 1]),
    ("Cross-source GPS + AFC",  [0, 0, 1]),
    ("All three stakeholders",  [0, 0, 1]),
]
ry = 3.18
rh = 0.535
for name, marks in matrix:
    textbox(s, 0.6, ry, capW, rh, name, 14, NAVY, anchor=MSO_ANCHOR.MIDDLE)
    for i, m in enumerate(marks):
        cx = colX[i] + colW/2
        cyc = ry + rh/2
        if m:
            col = ACCENT if i == 2 else GREEN
            rrect(s, cx-0.17, cyc-0.17, 0.34, 0.34, col, shape=MSO_SHAPE.OVAL)
            textbox(s, cx-0.17, cyc-0.18, 0.34, 0.34, "✓", 13, WHITE,
                    bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        else:
            rrect(s, cx-0.13, cyc-0.13, 0.26, 0.26, None, line=LINE,
                  line_w=1.3, shape=MSO_SHAPE.OVAL)
    rrect(s, 0.6, ry + rh, 12.23, 0.012, CARD2)
    ry += rh
# highlight the "This work" column band
rrect(s, colX[2]-0.04, hy, colW+0.08, ry-hy+0.02, None, line=ACCENT, line_w=1.8)
textbox(s, 0.6, ry + 0.06, 12.13, 0.4,
        "The analytical rows, reliability, revenue, school-aware ridership and "
        "cross-source integration, are unbuilt for the HCMC network.",
        12.5, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# =============================================================================
# PART 2 — BUS AND TICKET DATA
# =============================================================================
divider("02", "Bus and Ticket Data",
        "A dynamic record, its structure, and what it supports.")

# --- ER-table helpers (shared by the two record slides) --------------------
def _ertable(s, x, y, w, name, fields, accent=NAVY):
    h = 0.46 + len(fields) * 0.32
    rrect(s, x, y, w, h, WHITE, line=accent, line_w=2.0)
    rrect(s, x, y, w, 0.46, accent)
    textbox(s, x, y + 0.08, w, 0.32, name, 13, WHITE, bold=True,
            align=PP_ALIGN.CENTER)
    for i, (fld, key) in enumerate(fields):
        fy = y + 0.46 + i * 0.32
        if i:
            rrect(s, x + 0.05, fy, w - 0.10, 0.006, CARD2)
        textbox(s, x + 0.16, fy + 0.03, w - 0.7, 0.28, fld, 12, NAVY)
        if key:
            textbox(s, x + w - 0.62, fy + 0.04, 0.5, 0.26, key,
                    10, ACCENT if key == "PK" else BLUE, bold=True,
                    align=PP_ALIGN.RIGHT)
    return (x, y, w, h)

def _erlink(s, b1, b2, label=None):
    x1, y1, w1, h1 = b1; x2, y2, w2, h2 = b2
    if x2 >= x1 + w1:
        ax, ay, bx, by = x1 + w1, y1 + h1/2, x2, y2 + h2/2
    elif x1 >= x2 + w2:
        ax, ay, bx, by = x1, y1 + h1/2, x2 + w2, y2 + h2/2
    else:
        ax, ay, bx, by = x1 + w1/2, y1 + h1, x2 + w2/2, y2
    cn = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                Inches(ax), Inches(ay), Inches(bx), Inches(by))
    cn.line.color.rgb = BLUE; cn.line.width = Pt(1.8); cn.shadow.inherit = False
    if label:
        textbox(s, (ax + bx)/2 - 0.65, (ay + by)/2 - 0.20, 1.3, 0.26, label,
                10, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# --- Slide · the ticket record (full AFC schema, ER diagram) ---------------
s = content_slide(
    "Each fare transaction records fare class, time, location, and payment",
    "Bus and ticket data \u00b7 the ticket record")
textbox(s, 0.6, 1.9, 12.13, 0.36,
        "Twelve tables: a boarding fact and its payment, linked through trips, "
        "routes and operators to stops, vehicles, drivers and student riders.",
        14, NAVY)
fit_image(s, os.path.join(DIAG, "deck_erd_afc_mmd.png"), 0.3, 2.18, 12.73, 5.18)
textbox(s, 0.6, 7.06, 12.13, 0.3,
        "All twelve tables, with primary and foreign keys; full column "
        "inventories are in the appendix.",
        11.5, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# --- Slide \u00b7 the GPS record (full GPS schema, ER diagram) ------------------
s = content_slide(
    "Vehicle telemetry is structured into trips, stop timing, and a schedule",
    "Bus and ticket data \u00b7 the GPS record")
textbox(s, 0.6, 1.9, 12.13, 0.36,
        "Ten tables: raw pings are segmented into trips, each linked to its "
        "route, schedule, stops, vehicle and driver.",
        14, NAVY)
fit_image(s, os.path.join(DIAG, "deck_erd_gps_mmd.png"), 0.3, 2.18, 12.73, 5.18)
textbox(s, 0.6, 7.06, 12.13, 0.3,
        "All ten tables, with primary and foreign keys; full column inventories "
        "are in the appendix.",
        11.5, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# --- Slide · what each record answers on its own ---------------------------
s = content_slide(
    "Each record independently answers a distinct class of questions",
    "Bus and ticket data · what the data can tell, by source")

def _panel10(x, head, tint, items):
    rrect(s, x, 1.98, 5.95, 4.52, CARD, line=LINE, line_w=1.1)
    rrect(s, x, 1.98, 5.95, 0.55, tint)
    textbox(s, x, 2.02, 5.95, 0.4, head, 14, WHITE, bold=True,
            align=PP_ALIGN.CENTER)
    iy = 2.74
    for q, gloss, fld in items:
        textbox(s, x + 0.28, iy, 3.55, 0.32, q, 15, NAVY, bold=True)
        textbox(s, x + 0.28, iy + 0.34, 4.4, 0.28, gloss, 12, GREYTX,
                italic=True)
        textbox(s, x + 5.95 - 2.0, iy + 0.04, 1.73, 0.28, fld, 10.5, BLUE,
                align=PP_ALIGN.RIGHT)
        iy += 0.73

_panel10(0.6, "THE TICKET RECORD  ·  answers on its own", BLUE, [
    ("Who rides", "the full-fare, student and free mix", "ticket_type"),
    ("What it earns", "fares collected, at any level", "payments"),
    ("When the city rides", "the daily and weekly peaks", "time_created"),
    ("Where people board", "boarding hot-spots and dead stops", "stations"),
    ("How the market splits", "riders and routes across operators", "companies"),
])
_panel10(6.78, "THE GPS RECORD  ·  answers on its own",
         RGBColor(0x33, 0x4E, 0x6F), [
    ("How buses move", "their paths, and where they slow", "gps_extracted"),
    ("Run and stop timing", "travel time, arrival, how long they hold",
     "gps_trips · stop_times"),
    ("How regular service is", "the real gaps against the plan", "schedules"),
    ("The network's shape", "line length, stop order, hours", "routes"),
    ("Fleet in service", "which vehicles work which routes", "vehicles"),
])

textbox(s, 0.6, 6.68, 12.13, 0.4,
        "Apart, that is the ceiling for each; matched together they answer "
        "what neither can alone (next).",
        12, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# --- Slide 11 · the join and what it unlocks -------------------------------
s = content_slide(
    "Joined at route × hour × day-type, the two records support analyses "
    "neither allows alone",
    "Bus and ticket data · joining the two records")

def _srcbox(x, y, w, h, head, sub, col):
    rrect(s, x, y, w, h, WHITE, line=col, line_w=1.6)
    textbox(s, x, y + 0.19, w, 0.3, head, 12, NAVY, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, x, y + 0.50, w, 0.3, sub, 9.5, GREYTX, italic=True,
            align=PP_ALIGN.CENTER)

_srcbox(0.7, 2.5, 2.5, 0.95, "THE TICKET RECORD",
        "fares · riders · when · where", BLUE)
_srcbox(0.7, 4.0, 2.5, 0.95, "THE GPS RECORD",
        "movement · timing · plan", RGBColor(0x33, 0x4E, 0x6F))
# merge junction into the matched grain
rrect(s, 3.2, 2.964, 0.37, 0.022, NAVY)
rrect(s, 3.2, 4.464, 0.37, 0.022, NAVY)
rrect(s, 3.557, 2.964, 0.022, 1.522, NAVY)
rrect(s, 3.557, 3.714, 0.34, 0.022, NAVY)
rrect(s, 3.86, 3.645, 0.16, 0.17, NAVY,
      shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90
rrect(s, 4.02, 3.05, 2.28, 1.35, CARD2, line=ACCENT, line_w=2.2)
textbox(s, 4.02, 3.32, 2.28, 0.3, "MATCHED AT", 10.5, ACCENT, bold=True,
        align=PP_ALIGN.CENTER)
textbox(s, 4.02, 3.66, 2.28, 0.4, "route × hour × day-type", 12.5, NAVY,
        bold=True, align=PP_ALIGN.CENTER)
textbox(s, 0.7, 5.4, 5.55, 0.9,
        "Joined on route_no only. The two windows do not share a clock, so the "
        "match is at the aggregate grain, never event to event.",
        11, GREYTX, italic=True)

rrect(s, 6.5, 2.2, 0.014, 4.25, LINE)

textbox(s, 6.8, 2.06, 6.0, 0.3, "ONLY THE TWO TOGETHER ANSWER", 12, ACCENT,
        bold=True)
_combo = [
    ("Does the service match the riding?",
     "are buses where, and when, people actually ride"),
    ("Crowding, without occupancy",
     "many boardings weighed against the few trips run"),
    ("What a route is worth",
     "what it earns set against the service it costs to run"),
    ("Coverage versus use",
     "served-but-empty stops, and busy-but-starved corridors"),
]
cy = 2.52
for q, g in _combo:
    rrect(s, 6.8, cy, 5.95, 0.84, CARD, line=LINE, line_w=1.2)
    leftbar(s, 6.8, cy, 0.84, ACCENT, w=0.06)
    textbox(s, 7.05, cy + 0.11, 5.6, 0.32, q, 14.5, NAVY, bold=True)
    textbox(s, 7.05, cy + 0.47, 5.6, 0.3, g, 12, GREYTX, italic=True)
    cy += 0.97

# (Slide 12 structural-limits cut: covered by scope + the schema slides)


# =============================================================================
# PART 3 — INTERACTIVE VISUALIZATION
# =============================================================================
divider("03", "Interactive Visualization",
        "Three stakeholders, the decisions they face, and the interactive views "
        "that answer them.")

# ---- stakeholder-slide helpers (native infographic, transparent) ----------
def _stepper(slide, active):
    labels = ["Passenger", "Operating company", "Authority"]
    x0, gap, y, r = 7.7, 1.72, 1.52, 0.12
    for i, lab in enumerate(labels):
        cx = x0 + i*gap
        if i < 2:
            rrect(slide, cx + 2*r, y + r - 0.012, gap - 2*r, 0.024, LINE)
        on = (i == active)
        node = rrect(slide, cx, y, 2*r, 2*r, ACCENT if on else WHITE,
                     line=(ACCENT if on else LINE), line_w=1.5,
                     shape=MSO_SHAPE.OVAL)
        shape_text(node, [(str(i+1), 10.5, WHITE if on else GREYTX, True, False)])
        textbox(slide, cx - 0.6, y + 2*r + 0.02, 1.45, 0.24, lab, 9.5,
                NAVY if on else GREYTX, bold=on, align=PP_ALIGN.CENTER)

def _rider(slide, cx, cy, dashed=False, bag=False):
    head = rrect(slide, cx - 0.14, cy - 0.62, 0.28, 0.28, None, line=NAVY,
                 line_w=2.0, shape=MSO_SHAPE.OVAL)
    body = rrect(slide, cx - 0.34, cy - 0.34, 0.68, 0.5, None, line=NAVY,
                 line_w=2.0, shape=MSO_SHAPE.OVAL)
    if dashed:
        for sp in (head, body):
            ln = sp.line._get_or_add_ln()
            ln.append(ln.makeelement(qn('a:prstDash'), {'val': 'dash'}))
    if bag:
        rrect(slide, cx + 0.2, cy - 0.04, 0.16, 0.13, None, line=NAVY,
              line_w=1.6)

def _viewchip(slide, x, y, w, glyph, label, big=False):
    """The view a want resolves to, in plain words: the chart-type glyph (its
    shape) + what you would actually see. No chart jargon on the slide — which
    chart is chosen follows the chart-choice method in the backup."""
    g = 0.52 if big else 0.46
    fit_image(slide, os.path.join(DIAG, "glyph_%s.png" % glyph), x, y + 0.02,
              g, g - 0.02)
    tx = x + g + 0.14
    textbox(slide, tx, y, w - (g + 0.14), 0.52, label, 12.5 if big else 11,
            BLUE, bold=True)

# --- Slide · the passenger (WHO / WHAT / WHY, native infographic) -----------
s = content_slide(
    "A passenger evaluates six trip attributes; two are observable only "
    "after travel",
    "Interactive visualization · 01 · the passenger")
_stepper(s, 0)

# WHO — two riders gathered into one want
textbox(s, 0.6, 2.2, 3.2, 0.3, "THE RIDERS", 12, GREYTX, bold=True)
_rider(s, 1.15, 3.5, dashed=False, bag=True)
textbox(s, 1.75, 3.25, 2.3, 0.3, "Routine rider", 16, NAVY, bold=True)
textbox(s, 1.75, 3.54, 1.7, 0.3, "the same trip, daily", 12, GREYTX,
        italic=True)
_rider(s, 1.15, 5.6, dashed=True, bag=False)
textbox(s, 1.75, 5.35, 2.4, 0.3, "Occasional rider", 16, NAVY, bold=True)
textbox(s, 1.75, 5.64, 1.7, 0.3, "an unfamiliar one-off", 12, GREYTX,
        italic=True)
rrect(s, 3.55, 3.15, 0.02, 2.6, LINE)                       # brace
textbox(s, 3.0, 4.3, 1.1, 0.3, "each wants", 11, GREYTX, italic=True,
        align=PP_ALIGN.CENTER)
arr = rrect(s, 3.65, 4.48, 0.5, 0.02, GREYTX)               # arrow shaft
rrect(s, 4.1, 4.42, 0.14, 0.14, GREYTX, shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90

# WHAT — six wants, split by knowability
textbox(s, 4.5, 2.2, 6.0, 0.3, "A TRIP THAT IS", 12, GREYTX, bold=True)
rrect(s, 4.45, 2.6, 8.25, 1.8, None, line=LINE, line_w=1.5)
textbox(s, 4.7, 2.74, 8.0, 0.3,
        "KNOWABLE BEFORE THE TRIP  ·  A ROUTING APP ALREADY SHOWS IT", 11.5,
        GREYTX, bold=True)
for i, q in enumerate(["possible", "quick", "cheap", "easy"]):
    qx = 4.78 + (i % 2) * 3.1; qy = 3.22 + (i // 2) * 0.46
    rrect(s, qx, qy + 0.04, 0.08, 0.08, None, line=GREYTX, line_w=1.4,
          shape=MSO_SHAPE.OVAL)
    textbox(s, qx + 0.2, qy - 0.06, 2.6, 0.3, q, 16, NAVY)
textbox(s, 4.7, 4.08, 7.5, 0.3, "from the route, the schedule and the fare",
        12.5, GREYTX, italic=True)
rrect(s, 4.45, 4.6, 8.25, 2.08, None, line=ACCENT, line_w=1.8)
leftbar(s, 4.45, 4.6, 2.08, ACCENT, w=0.06)
textbox(s, 4.7, 4.73, 8.0, 0.3,
        "SEEN ONLY AFTER YOU RIDE — AND THE VIEW THAT SURFACES IT", 11, ACCENT,
        bold=True)
# Comfortable -> a crowding heatmap (a value across hour × route)
textbox(s, 4.7, 5.2, 2.6, 0.42, "Comfortable", 22, NAVY, bold=True)
textbox(s, 4.7, 5.64, 2.6, 0.26, "how full it gets", 11.5, GREYTX, italic=True)
textbox(s, 7.18, 5.24, 0.4, 0.4, "→", 17, ACCENT, align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE)
_viewchip(s, 7.72, 5.32, 4.85, "heatmap", "how busy it gets, hour by hour",
          big=True)
# Dependable -> the spread of arrival times
textbox(s, 4.7, 5.94, 2.6, 0.42, "Dependable", 22, NAVY, bold=True)
textbox(s, 4.7, 6.38, 2.6, 0.26, "whether it turns up", 11.5, GREYTX,
        italic=True)
textbox(s, 7.18, 5.98, 0.4, 0.4, "→", 17, ACCENT, align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE)
_viewchip(s, 7.72, 6.06, 4.85, "box", "how much arrival times vary",
          big=True)

# WHY -> speaker notes (spoken, not on the slide), consistent with the others
s.notes_slide.notes_text_frame.text = (
    "WHY: four of the six are easy to find out before the trip, the route, the "
    "schedule, the fare. The two that actually decide whether the trip was "
    "worth it, comfort and dependability, are the ones you only learn by "
    "riding, one bad trip at a time. Those are the two the record can surface "
    "in advance.")

def _bus(slide, cx, cy):
    rrect(slide, cx-0.5, cy-0.22, 1.0, 0.44, None, line=NAVY, line_w=2.2,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    for i in range(3):
        rrect(slide, cx-0.4+i*0.29, cy-0.13, 0.21, 0.14, None, line=NAVY,
              line_w=1.3)
    rrect(slide, cx-0.32, cy+0.16, 0.16, 0.16, None, line=NAVY, line_w=1.8,
          shape=MSO_SHAPE.OVAL)
    rrect(slide, cx+0.16, cy+0.16, 0.16, 0.16, None, line=NAVY, line_w=1.8,
          shape=MSO_SHAPE.OVAL)

# --- Slide · the operating company (WHO / WHAT, native infographic) ---------
s = content_slide(
    "An operator improves revenue and cost by analysing its full "
    "operation",
    "Interactive visualization · 02 · the operating company")
_stepper(s, 1)

# WHO — one actor and its goal
textbox(s, 0.6, 2.15, 3.4, 0.3, "THE OPERATOR", 12, GREYTX, bold=True)
_bus(s, 1.4, 3.05)
textbox(s, 0.6, 3.5, 3.4, 0.3, "The operating company", 16, NAVY, bold=True)
textbox(s, 0.6, 3.79, 3.4, 0.3, "Phuong Trang, VinBus, a cooperative", 12,
        GREYTX, italic=True)
rrect(s, 0.6, 4.25, 3.05, 0.78, None, line=ACCENT, line_w=1.6)
leftbar(s, 0.6, 4.25, 0.78, ACCENT, w=0.05)
textbox(s, 0.82, 4.36, 2.8, 0.3, "more revenue, less cost", 14.5, NAVY,
        bold=True)
textbox(s, 0.82, 4.66, 2.8, 0.3, "the single business goal", 11.5, GREYTX,
        italic=True)
textbox(s, 0.6, 5.25, 3.4, 0.5, "reached by reading the whole business:", 12.5,
        GREYTX, italic=True)
rrect(s, 3.78, 4.0, 0.42, 0.02, GREYTX)
rrect(s, 4.16, 3.94, 0.13, 0.13, GREYTX,
      shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90

# WHAT — six lenses, each resolving to the view that reads it (recipe applied)
lenses = [
    ("Riders", "who rides, and how they pay",
     "stream", "the fare mix over time"),
    ("Riding", "where and when people ride",
     "heatmap", "busy hours across routes"),
    ("Money", "what each route and time earns",
     "scatter", "what each route earns vs wastes"),
    ("Operations", "reliability, empty runs, fleet use",
     "scatter", "how reliably each route runs"),
    ("Position", "how its routes do against rivals",
     "scatter", "its routes against rivals"),
    ("Openings", "busy routes under-served",
     "scatter", "busy routes left under-served"),
]
gx, gy, bw, bh, hg, vg = 4.4, 2.33, 2.66, 1.74, 0.16, 0.2
for i, (name, desc, glyph, label) in enumerate(lenses):
    x = gx + (i % 3)*(bw+hg); y = gy + (i//3)*(bh+vg)
    rrect(s, x, y, bw, bh, None, line=LINE, line_w=1.5)
    textbox(s, x+0.22, y+0.14, bw-0.4, 0.34, name, 14.5, NAVY, bold=True)
    textbox(s, x+0.22, y+0.5, bw-0.42, 0.3, desc, 10.5, GREYTX, italic=True)
    rrect(s, x+0.22, y+0.9, bw-0.44, 0.013, LINE)
    _viewchip(s, x+0.22, y+1.04, bw-0.4, glyph, label)
textbox(s, 4.4, 6.12, 8.3, 0.4,
        "Each want maps to the simplest chart that answers it — the "
        "chart-choice method is in the backup.", 10.5, NAVY, italic=True)

# WHY -> speaker notes (spoken, not on the slide)
s.notes_slide.notes_text_frame.text = (
    "WHY: a bus operator sees what it runs and what it costs clearly, but not "
    "who actually rides, where the real riding sits, how riders pay, or how its "
    "routes compare to the rivals on the same corridor. Its biggest, most "
    "expensive calls, where to deploy buses and which routes to keep, drop or "
    "bid for, turn on exactly that missing half of its own business.")

def _institution(slide, cx, cy):
    rrect(slide, cx-0.45, cy-0.46, 0.9, 0.26, None, line=NAVY, line_w=2.0,
          shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    rrect(slide, cx-0.45, cy-0.17, 0.9, 0.055, None, line=NAVY, line_w=1.6)
    for i in range(4):
        rrect(slide, cx-0.36+i*0.225, cy-0.08, 0.06, 0.32, None, line=NAVY,
              line_w=1.5)
    rrect(slide, cx-0.48, cy+0.25, 0.96, 0.07, None, line=NAVY, line_w=1.8)

# --- Slide · the authority (WHO / WHAT, native infographic) -----------------
s = content_slide(
    "The authority needs a network-wide, longitudinal view to anticipate "
    "service failures",
    "Interactive visualization · 03 · the authority")
_stepper(s, 2)

# WHO — the public bus-system manager and its job
textbox(s, 0.6, 2.15, 3.4, 0.3, "THE AUTHORITY", 12, GREYTX, bold=True)
_institution(s, 1.4, 3.0)
textbox(s, 0.6, 3.5, 3.4, 0.3, "The public-transport authority", 16, NAVY,
        bold=True)
textbox(s, 0.6, 3.79, 3.4, 0.3, "the city's bus-system manager", 12,
        GREYTX, italic=True)
rrect(s, 0.6, 4.25, 3.05, 0.78, None, line=ACCENT, line_w=1.6)
leftbar(s, 0.6, 4.25, 0.78, ACCENT, w=0.05)
textbox(s, 0.82, 4.36, 2.8, 0.3, "serve the whole city", 14.5, NAVY, bold=True)
textbox(s, 0.82, 4.66, 2.8, 0.3, "the public job, not profit", 11.5, GREYTX,
        italic=True)
textbox(s, 0.6, 5.25, 3.4, 0.5, "by watching the network:", 12.5, GREYTX,
        italic=True)

# WHAT — seven lenses; each names a comparison and resolves to a view
def _lensbox(x, y, w, h, name, glyph, label, accent=False, wide=False):
    rrect(s, x, y, w, h, None, line=(ACCENT if accent else LINE),
          line_w=(1.7 if accent else 1.4))
    if accent:
        leftbar(s, x, y, h, ACCENT, w=0.05)
    if wide:
        textbox(s, x+0.22, y, 2.7, h, name, 14, NAVY, bold=True,
                anchor=MSO_ANCHOR.MIDDLE)
        _viewchip(s, x+3.0, y+(h-0.5)/2, w-3.3, glyph, label)
    else:
        textbox(s, x+0.2, y+0.1, w-0.34, 0.3, name, 13.5, NAVY, bold=True)
        _viewchip(s, x+0.2, y+0.46, w-0.34, glyph, label)

WX, WW = 4.4, 8.3
bw = (WW - 2*0.16) / 3
# lead group: over time (accent)
textbox(s, WX, 2.12, WW, 0.28,
        "OVER TIME  ·  what only a whole-network view shows", 11.5, ACCENT,
        bold=True)
for i, (n, g, lb) in enumerate([
        ("Ridership trend", "timeline", "ridership over time"),
        ("Sudden drops", "timeline", "daily ridership, with alert bands"),
        ("Forecast", "timeline", "the weeks ahead, projected")]):
    _lensbox(WX + i*(bw+0.16), 2.42, bw, 1.0, n, g, lb, accent=True)
# spatial group
textbox(s, WX, 3.58, WW, 0.28, "ACROSS THE CITY", 11.5, GREYTX, bold=True)
for i, (n, g, lb) in enumerate([
        ("Coverage", "map", "coverage across the map"),
        ("Stops", "map", "busy stops against dead ones"),
        ("Route load", "scatter", "crowded against near-empty routes")]):
    _lensbox(WX + i*(bw+0.16), 3.88, bw, 1.0, n, g, lb)
# operators (one wide)
textbox(s, WX, 5.04, WW, 0.28, "ACROSS COMPANIES", 11.5, GREYTX, bold=True)
_lensbox(WX, 5.34, WW, 0.8, "The companies", "scatter",
         "how riders split across companies", wide=True)
textbox(s, WX, 6.24, WW, 0.34,
        "Each want maps to the simplest chart that answers it — the "
        "chart-choice method is in the backup.", 10.5, NAVY, italic=True)

# WHY -> speaker notes
s.notes_slide.notes_text_frame.text = (
    "WHY: the authority is who the public and the city government complain to "
    "when the bus system fails, no service in my area, falling ridership, empty "
    "buses wasting money, a holiday breakdown. Its job is to get ahead of those "
    "complaints, but it sees the network only through fragmented operator "
    "reports. The one view it lacks, and the one this offers, is the whole "
    "network at every level and over time.")

# =============================================================================
# PART 4 — DATA ARCHITECTURE AND ANALYSIS PIPELINE
# =============================================================================
divider("04", "Data Architecture and Analysis Pipeline",
        "How the data is stored, analysed, and served to the charts live.")

# --- Slide · the system at a glance (high-level overview) ------------------
s = content_slide(
    "Data is loaded into one warehouse, transformed periodically, and "
    "queried live",
    "Data architecture · the system at a glance")

BY, BH = 3.15, 1.35          # the component row
CY = BY + BH / 2             # its centreline

def _box(x, w, label, emph=False):
    rrect(s, x, BY, w, BH, CARD2 if emph else WHITE,
          line=(ACCENT if emph else NAVY), line_w=(2.4 if emph else 1.6))
    textbox(s, x, BY + (BH - 0.5) / 2, w, 0.5, label,
            17 if emph else 15, NAVY, bold=True, align=PP_ALIGN.CENTER)

def _arr(xa, xb, y, label, above=True, color=NAVY):
    """Horizontal arrow pointing from xa toward xb; verb label above/below."""
    hw, hh = 0.15, 0.17
    if xb > xa:                                    # rightward
        rrect(s, xa, y - 0.011, (xb - hw) - xa, 0.022, color)
        rrect(s, xb - hw, y - hh / 2, hw, hh, color,
              shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90
    else:                                          # leftward
        rrect(s, xb + hw, y - 0.011, xa - (xb + hw), 0.022, color)
        rrect(s, xb, y - hh / 2, hw, hh, color,
              shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 270
    lo, hi = min(xa, xb), max(xa, xb)
    ly = y - 0.40 if above else y + 0.11
    textbox(s, lo - 0.12, ly, (hi - lo) + 0.24, 0.3, label,
            11, color, italic=True, align=PP_ALIGN.CENTER)

# "the system" container around the two components we built
rrect(s, 3.95, 2.45, 6.65, 2.78, None, line=LINE, line_w=1.4)
textbox(s, 9.30, 2.52, 1.20, 0.28, "the system", 9.5, GREYTX, bold=True,
        align=PP_ALIGN.RIGHT)

# the four components (nouns only)
_box(0.70, 1.95, "SOURCE")
_box(4.30, 2.45, "WAREHOUSE", emph=True)
_box(7.90, 2.35, "DASHBOARD")
_box(10.95, 1.85, "USER")

# the transform loop on the warehouse (its own SQL does the work, on a basis)
rrect(s, 4.48, 2.60, 0.40, 0.40, ACCENT, shape=MSO_SHAPE.CIRCULAR_ARROW)
textbox(s, 4.95, 2.62, 3.60, 0.32, "transforms itself in SQL · on a basis", 11,
        ACCENT, italic=True, align=PP_ALIGN.LEFT)

# the arrows (verbs)
_arr(2.65, 4.30, CY, "pushes raw", above=True)
textbox(s, 0.70, 4.56, 1.95, 0.3, "↻  new data, daily", 10.5, ACCENT,
        italic=True, align=PP_ALIGN.CENTER)
_arr(6.75, 7.90, CY - 0.20, "serves", above=True)
_arr(7.90, 6.75, CY + 0.22, "queries", above=False)
_arr(10.25, 10.95, CY - 0.20, "shows", above=True)
_arr(10.95, 10.25, CY + 0.22, "explores", above=False)

textbox(s, 0.6, 5.62, 12.13, 0.7,
        "The source keeps pushing new data; the warehouse re-derives its "
        "metrics in SQL, on a basis; and every interaction queries the live "
        "store, so the user always reads the current state.",
        13.5, NAVY, italic=True, align=PP_ALIGN.CENTER)

# --- Slide · the Medallion (Bronze raw · Silver star · Gold aggregates) -----
s = content_slide(
    "The warehouse has three tiers: raw records, a conformed star schema, "
    "and chart-level aggregates",
    "Data architecture · the Medallion")

BRONZE_C = RGBColor(0xA8, 0x7B, 0x46)
SILVER_C = RGBColor(0x7E, 0x8A, 0x9E)
GOLD_C   = ACCENT

PT, PB = 2.02, 6.18                       # panel top / bottom
def _panel(x, w, tint, name, role):
    rrect(s, x, PT, w, PB - PT, CARD, line=LINE, line_w=1.0)
    rrect(s, x, PT, w, 0.60, tint)
    textbox(s, x, PT + 0.05, w, 0.30, name, 14, WHITE, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, x, PT + 0.33, w, 0.24, role, 9.5, WHITE, italic=True,
            align=PP_ALIGN.CENTER)

def _chip(x, y, w, label, h=0.40, fill=WHITE, line=NAVY, tcol=NAVY,
          sz=10.5, bold=False):
    rrect(s, x, y, w, h, fill, line=line, line_w=1.1)
    textbox(s, x, y + (h - 0.25) / 2, w, 0.25, label, sz, tcol, bold=bold,
            align=PP_ALIGN.CENTER)

def _sline(x1, y1, x2, y2):
    cn = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    cn.line.color.rgb = LINE; cn.line.width = Pt(1.1)
    cn.shadow.inherit = False

def _step(xc, label):                     # transform chevron in a panel gap
    t = rrect(s, xc - 0.17, 3.98, 0.34, 0.32, NAVY,
              shape=MSO_SHAPE.ISOSCELES_TRIANGLE); t.rotation = 90
    textbox(s, xc - 0.62, 4.36, 1.24, 0.5, label, 9.5, GREYTX, italic=True,
            align=PP_ALIGN.CENTER)

BX, BW = 0.45, 2.95                       # Bronze panel
SX, SVW = 4.30, 4.55                      # Silver panel (SVW, not SW: SW is the slide width)
GX, GW = 9.75, 3.10                       # Gold panel
_panel(BX, BW, BRONZE_C, "BRONZE", "raw, as delivered")
_panel(SX, SVW, SILVER_C, "SILVER", "conformed star schema")
_panel(GX, GW, GOLD_C,   "GOLD",   "analysis aggregations")

# Bronze — the raw source files
for i, lbl in enumerate(["fare taps (AFC)", "GPS pings", "timetables",
                          "stops · routes", "schools · operators"]):
    _chip(BX + 0.30, 2.92 + i * 0.56, BW - 0.60, lbl)
textbox(s, BX, 5.84, BW, 0.28, "the source files, never rewritten", 9.5,
        GREYTX, italic=True, align=PP_ALIGN.CENTER)

# Silver — the star schema (lines first, then fact, then dimensions)
cx, cy = SX + SVW / 2, 4.12
dims = [("route", 6.575, 3.05), ("fare class", 8.07, 3.58),
        ("hour", 8.07, 4.66), ("school", 6.575, 5.18),
        ("stop", 5.08, 4.66), ("calendar", 5.08, 3.58)]
for _, dx, dy in dims:
    _sline(cx, cy, dx, dy)
rrect(s, cx - 0.70, cy - 0.27, 1.40, 0.54, NAVY)
textbox(s, cx - 0.70, cy - 0.14, 1.40, 0.30, "boardings", 12, WHITE, bold=True,
        align=PP_ALIGN.CENTER)
for lbl, dx, dy in dims:
    _chip(dx - 0.66, dy - 0.20, 1.32, lbl, fill=ICE, line=SILVER_C)
textbox(s, SX, 5.82, SVW, 0.30,
        "one fact, conformed dimensions · reconciled on route · calendar tags Tết",
        9.5, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# Gold — the aggregation tables, by grain
for i, lbl in enumerate(["network × day", "route × hour", "route × day",
                          "stop × hour", "stop totals", "school ↔ route",
                          "hub stats"]):
    _chip(GX + 0.27, 2.88 + i * 0.46, GW - 0.54, lbl, h=0.36, line=GOLD_C)

# the two SQL transform steps
_step(3.85, "clean &\nconform")
_step(9.30, "aggregate")

textbox(s, 0.6, 6.42, 12.13, 0.5,
        "Bronze stays raw; every new day flows Bronze → Silver → Gold in SQL, "
        "so Gold is always current.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# --- Slide · the analysis, records into charts -----------------------------
s = content_slide(
    "Six transformations convert the records into the metrics the charts display",
    "Data architecture · the analysis pipeline")

# endpoints: the records (left) and the charts (right)
def _endbox(x, head, sub):
    rrect(s, x, 2.5, 1.7, 3.18, CARD2, line=NAVY, line_w=1.6)
    textbox(s, x, 3.86, 1.7, 0.32, head, 12, NAVY, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, x, 4.2, 1.7, 0.3, sub, 9.5, GREYTX, italic=True,
            align=PP_ALIGN.CENTER)
_endbox(0.45, "THE RECORDS", "ticket + GPS")
_endbox(11.18, "THE CHARTS", "the dashboard")

def _bridge_arr(x1, x2):
    y = 4.09
    rrect(s, x1, y - 0.012, (x2 - 0.16) - x1, 0.024, NAVY)
    rrect(s, x2 - 0.16, y - 0.095, 0.16, 0.19, NAVY,
          shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90
_bridge_arr(2.15, 2.65)
_bridge_arr(10.70, 11.18)

textbox(s, 2.65, 2.12, 8.05, 0.28, "THE ANALYSIS  ·  six named methods", 11,
        ACCENT, bold=True, align=PP_ALIGN.CENTER)

def _tcard(x, y, w, h, verb, formula, gloss, out):
    rrect(s, x, y, w, h, CARD, line=LINE, line_w=1.3)
    leftbar(s, x, y, h, ACCENT, w=0.06)
    textbox(s, x + 0.18, y + 0.12, w - 0.3, 0.3, verb, 13.5, NAVY, bold=True)
    textbox(s, x + 0.18, y + 0.45, w - 0.26, 0.3, formula, 9.5, ACCENT,
            bold=True)
    textbox(s, x + 0.18, y + 0.75, w - 0.3, 0.3, gloss, 10.5, GREYTX,
            italic=True)
    textbox(s, x + 0.18, y + h - 0.33, w - 0.3, 0.28, out, 11, BLUE, bold=True)

T = [
    ("Count and sum", "SQL GROUP BY aggregates",
     "boardings tallied every way", "ridership, revenue, the pulse"),
    ("Score reliability", "arrival spread + headway (QoS)",
     "how tightly buses keep time", "a route's reliability"),
    ("Service vs riding", "join at route × hour × day-type",
     "buses run against boardings", "crowding and gaps"),
    ("Map and bin", "H3 hex-bins + Voronoi catchments",
     "boardings placed in space", "coverage and access"),
    ("Forecast", "AutoETS, AIC-selected",
     "the ridership curve, extended", "the next two weeks"),
    ("Concentration", "HHI = Σ share²",
     "one number for the market", "market structure"),
]
tcw, tch, tgx, tgy = 2.55, 1.5, 0.20, 0.16
tx0, ty0 = 2.65, 2.5
for i, (v, f, g, o) in enumerate(T):
    x = tx0 + (i % 3) * (tcw + tgx)
    y = ty0 + (i // 3) * (tch + tgy)
    _tcard(x, y, tcw, tch, v, f, g, o)

textbox(s, 0.6, 5.86, 12.13, 0.6,
        "Each is a named, standard method run in the warehouse; together they "
        "turn the records into every chart the dashboard shows.",
        12.5, NAVY, italic=True, align=PP_ALIGN.CENTER)

s.notes_slide.notes_text_frame.text = (
    "Methods behind each, for Q&A (citations in the report): "
    "1 Count & sum = the Gold group-by aggregates. "
    "2 Reliability = arrival spread + headway adherence, QoS-1/2/3 "
    "(Chawuthai & Srisakaokul 2023). "
    "3 Service vs riding = the cross-source match at route x hour x day-type. "
    "4 Map = H3 hexagonal binning + Voronoi stop catchments. "
    "5 Look ahead = AutoETS, an ETS state-space model selected by AIC "
    "(statsforecast). "
    "6 Market structure = Herfindahl-Hirschman Index, HHI = sum of squared "
    "operator shares. "
    "Difference-in-differences (free-fare lift) and archetype clustering are "
    "in the backup slides.")

# --- Slide · the serve path, two clocks ------------------------------------
s = content_slide(
    "With the analysis precomputed in Gold, each interaction is a single "
    "read",
    "Data architecture · the serve path")

SBY, SBH = 3.45, 1.05
def _sbox(x, w, head, sub, emph=False):
    rrect(s, x, SBY, w, SBH, CARD2 if emph else WHITE,
          line=(ACCENT if emph else NAVY), line_w=(2.2 if emph else 1.6))
    textbox(s, x, SBY + 0.20, w, 0.32, head, 12.5, NAVY, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, x, SBY + 0.56, w, 0.30, sub, 9.5, GREYTX, italic=True,
            align=PP_ALIGN.CENTER)

def _sarrow(x1, x2, top=None, bot=None):
    y = SBY + SBH / 2
    rrect(s, x1, y - 0.011, (x2 - 0.16) - x1, 0.022, NAVY)
    rrect(s, x2 - 0.16, y - 0.09, 0.16, 0.18, NAVY,
          shape=MSO_SHAPE.ISOSCELES_TRIANGLE).rotation = 90
    if top:
        textbox(s, x1, y - 0.42, x2 - x1, 0.28, top, 10, ACCENT, italic=True,
                align=PP_ALIGN.CENTER)
    if bot:
        textbox(s, x1, y + 0.14, x2 - x1, 0.24, bot, 9.5, GREYTX, italic=True,
                align=PP_ALIGN.CENTER)

rrect(s, 6.85, 2.35, 0.014, 2.75, LINE)
textbox(s, 1.2, 2.45, 5.2, 0.3, "THE SLOW CLOCK", 13, BLUE, bold=True)
textbox(s, 1.2, 2.74, 5.2, 0.26, "the analysis runs offline, on a basis", 10,
        GREYTX, italic=True)
textbox(s, 7.05, 2.45, 5.4, 0.3, "THE FAST CLOCK", 13, ACCENT, bold=True)
textbox(s, 7.05, 2.74, 5.4, 0.26, "a filter, hover or click, instant", 10,
        GREYTX, italic=True)

_sbox(1.2, 2.5, "THE ANALYSIS", "the six transformations")
_sarrow(3.7, 5.6, "writes", "offline, on a basis")
_sbox(5.6, 2.5, "GOLD", "chart-ready metrics", emph=True)
_sarrow(8.1, 10.0, "read", "instant")
_sbox(10.0, 2.6, "A CHART", "what the user sees")

textbox(s, 0.6, 5.6, 12.13, 0.9,
        "Interaction feels instant because the heavy work is already done, and "
        "a new day just re-runs the slow clock, so the chart is always current.",
        13.5, NAVY, italic=True, align=PP_ALIGN.CENTER)

# =============================================================================
# PART 5 — IMPLEMENTATION AND FUTURE WORK
# =============================================================================
divider("05", "Implementation and Future Work",
        "What is built, and the next phase.")

# --- Slide · the running system (the hub) ----------------------------------
s = content_slide(
    "A running server-rendered application reads the warehouse and renders the charts",
    "Implementation · the running system")
fit_image(s, os.path.join(SHOTS, "demo_hub_c.png"), 0.45, 2.0, 12.43, 4.95)
textbox(s, 0.6, 7.04, 12.13, 0.4,
        "Everything on screen is the warehouse and the analysis, rendered, none "
        "of it exists without the full pipeline behind it.",
        13.5, NAVY, italic=True, align=PP_ALIGN.CENTER)

# --- Slide · the theme cards (the hub's editorial card sections) ------------
s = content_slide(
    "Below the hero, the hub is six scrollable theme cards",
    "Implementation · the theme cards")
fit_image(s, os.path.join(SHOTS, "demo_hub_cards.png"), 0.6, 1.72, 12.13, 5.3)
textbox(s, 0.6, 7.08, 12.13, 0.4,
        "Each editorial section is one of the six theme cards; you scroll the hub "
        "and open any one.",
        11.5, NAVY, italic=True, align=PP_ALIGN.CENTER)

# --- Slides · the interaction, working (one big proof capture each) --------
# (1) filter — the flexible filter bar (every field re-queries live)
s = content_slide(
    "A flexible filter bar re-queries the warehouse on every field",
    "Implementation · interaction · filter")
fit_image(s, os.path.join(SHOTS, "demo_filter_proof.png"), 0.6, 1.8, 12.13, 5.0)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "Change any field and the chart re-queries the warehouse, live.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# (2) hover — a value on any point
s = content_slide(
    "Hover any point for its value",
    "Implementation · interaction · hover")
fit_image(s, os.path.join(SHOTS, "demo_hover_proof.png"), 0.6, 1.8, 12.13, 5.0)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "Each chart is a live query; a hover surfaces a value at any point.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# (3) click — the entity-detail panel
s = content_slide(
    "Click any entity to open its full detail panel",
    "Implementation · interaction · click")
fit_image(s, os.path.join(SHOTS, "demo_interaction_panel_c.png"),
          0.6, 1.8, 12.13, 5.0)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "A single click opens any entity in a full detail panel.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# --- Slides · one complete data story (the Tet scrollytelling, beat by beat)
# (1) the opening beat — the drop
s = content_slide(
    "The Tết story opens on a −84% collapse",
    "Implementation · the Tết story · 1 of 3")
fit_image(s, os.path.join(SHOTS, "demo_story_tet_drop.png"), 0.6, 1.8, 12.13, 5.0)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "One chart pins in place; the opening beat sets the scene.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# (2) the turn — the pinned chart re-encodes by fare class
s = content_slide(
    "Scroll, and the pinned chart shows students vanishing first",
    "Implementation · the Tết story · 2 of 3")
fit_image(s, os.path.join(SHOTS, "demo_story_tet_fareclass.png"),
          0.6, 1.8, 12.13, 5.0)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "The same pinned chart re-encodes itself as the reader scrolls on.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# (3) the takeaway — the recap and call to action
s = content_slide(
    "It closes on the recovery: nine days low, back by 23 February",
    "Implementation · the Tết story · 3 of 3")
fit_image(s, os.path.join(SHOTS, "demo_story_tet_bongo.png"),
          0.6, 1.8, 12.13, 5.0)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "The closing beat lands the takeaway and points the reader onward.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

# --- Slide · Phase 1 in review (objectives set vs delivered) ---------------
s = content_slide(
    "The four objectives set for Phase 1 are met",
    "Implementation · Phase 1 in review")
textbox(s, 0.6, 1.95, 12.13, 0.36,
        "The introduction set four objectives for Phase 1; each one is now "
        "delivered.", 14, NAVY)
objs = [
    ("Survey the existing tools and research",
     "Five tools and the research base surveyed; the analytical gap identified"),
    ("Specify a complete, justified design",
     "Architecture evaluated and selected; a 20-chart catalogue and the "
     "interaction model specified"),
    ("Demonstrate feasibility with a prototype",
     "A running system: nine canvases across three themes, one Story, and a "
     "measured performance benchmark"),
    ("Plan the Phase 2 build",
     "A month-by-month schedule with a two-wave user study, on the next slide"),
]
oy, oh, ogp = 2.5, 0.95, 0.13
for i, (head, body) in enumerate(objs):
    y = oy + i * (oh + ogp)
    rrect(s, 0.6, y, 12.13, oh, CARD, line=LINE, line_w=1.1)
    leftbar(s, 0.6, y, oh, GREEN, w=0.09)
    cd = 0.5
    rrect(s, 0.92, y + (oh - cd) / 2, cd, cd, GREEN, shape=MSO_SHAPE.OVAL)
    textbox(s, 0.92, y + (oh - cd) / 2 - 0.01, cd, cd, "✓", 20, WHITE, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 1.68, y + 0.13, 9.0, 0.34, head, 16, NAVY, bold=True)
    textbox(s, 1.68, y + 0.5, 9.2, 0.36, body, 12.5, GREYTX, italic=True)
    rrect(s, 11.05, y + (oh - 0.42) / 2, 1.45, 0.42,
          RGBColor(0xEB, 0xF6, 0xEE), line=GREEN, line_w=1.2)
    textbox(s, 11.05, y + (oh - 0.42) / 2, 1.45, 0.42, "DELIVERED", 11, GREEN,
            bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# --- Slide · the road ahead (Phase 2, native Gantt — general, 14 weeks) ----
s = content_slide(
    "Phase 2 completes the build in about fourteen weeks",
    "Future work · the road ahead")
gx0, gx1 = 4.55, 12.85
GW = gx1 - gx0
def _wx(w): return gx0 + GW * (w / 14.0)
gtop, ry0, rh = 2.55, 3.2, 0.5
tasks = [
    ("Clean and finish the warehouse",       1, 3, False),
    ("Wire the remaining charts",            4, 11, False),
    ("Place the schools on the map",         4, 6, False),
    ("Roll the filter bar out to every chart", 5, 8, True),
    ("Build the rest of the stories",        11, 13, False),
    ("Load full GPS, then test with users",  13, 14, True),
]
cbot = ry0 + len(tasks)*rh
# month group headers
for nm, a, b in [("Month 1", 0, 4), ("Month 2", 4, 8), ("Month 3", 8, 12),
                 ("Weeks 13–14", 12, 14)]:
    rrect(s, _wx(a)+0.02, gtop, _wx(b)-_wx(a)-0.04, 0.34, CARD2)
    textbox(s, _wx(a), gtop+0.03, _wx(b)-_wx(a), 0.28, nm, 11, NAVY,
            bold=True, align=PP_ALIGN.CENTER)
# weekly gridlines
for w in range(15):
    rrect(s, _wx(w), gtop+0.4, 0.008, cbot-(gtop+0.4), LINE)
# bars (general tasks; the two headline additions in accent)
for i, (lbl, a, b, acc) in enumerate(tasks):
    y = ry0 + i*rh
    textbox(s, 0.5, y, 3.95, rh, lbl, 12.5, NAVY, bold=acc,
            anchor=MSO_ANCHOR.MIDDLE)
    rrect(s, _wx(a)+0.03, y+0.1, _wx(b)-_wx(a)-0.06, rh-0.22,
          ACCENT if acc else BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
# week numbers under the chart
for w in range(1, 15):
    textbox(s, _wx(w-1), cbot+0.06, _wx(w)-_wx(w-1), 0.2, str(w), 8.5, GREYTX,
            align=PP_ALIGN.CENTER)
textbox(s, 0.5, cbot+0.46, 12.33, 0.4,
        "About fourteen weeks at one developer; the filter-bar rollout and a "
        "two-wave user study are the headline additions.",
        12.5, NAVY, italic=True, align=PP_ALIGN.CENTER)

# =============================================================================
# CLOSE (T7)
# =============================================================================
s = dark_slide()
leftbar(s, 0.95, 2.78, 1.45, ACCENT, w=0.1)
textbox(s, 1.3, 2.7, 11.0, 1.2, "Thank you.  Questions welcome.", 40, WHITE, bold=True)
tb = textbox(s, 1.32, 4.0, 11.0, 1.4, "", 16, ICE)
add_lines(tb, [
    ("Huynh Thanh Duy  ·  2252114", 16, ICE, False, False),
    ("Advisor: Assoc. Prof. Thoai Nam", 16, ICE, False, False),
])

# =============================================================================
# BACKUP A — THEORETICAL FOUNDATIONS
# chart selection · perception · interaction · storytelling · analytical methods
# =============================================================================

# --- Slide · choosing the chart — the abstract principle, not the charts ----
s = content_slide(
    "Backup: from a need, to a comparison, to a chart type",
    "Visualization · choosing the chart")
# the three-step recipe (the principle)
def _rstep(x, w, lbl, focal=False):
    rrect(s, x, 2.16, w, 0.82, CARD2 if focal else CARD,
          line=ACCENT if focal else LINE, line_w=1.6 if focal else 1.2)
    textbox(s, x, 2.16, w, 0.82, lbl, 14.5, NAVY, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
_rstep(0.7, 2.8, "a want")
textbox(s, 3.52, 2.28, 0.42, 0.5, "→", 20, ACCENT, align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE)
_rstep(4.05, 4.1, "the comparison it makes", focal=True)
textbox(s, 8.18, 2.28, 0.42, 0.5, "→", 20, ACCENT, align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE)
_rstep(8.65, 4.1, "the chart the eye reads best")
# concrete examples — each comparison picks the chart that reads it best
textbox(s, 0.7, 3.18, 12.0, 0.26, "FOR EXAMPLE — THE COMPARISON PICKS THE CHART",
        10.5, GREYTX, bold=True)
def _ex(x, y, glyph, comparison, chart):
    rrect(s, x, y, 3.85, 1.18, None, line=LINE, line_w=1.3)
    fit_image(s, os.path.join(DIAG, "glyph_%s.png" % glyph),
              x+0.16, y+0.2, 0.9, 0.78)
    textbox(s, x+1.22, y+0.22, 2.55, 0.28, comparison.upper(), 10, GREYTX,
            bold=True)
    textbox(s, x+1.22, y+0.51, 2.6, 0.4, chart, 15.5, NAVY, bold=True)
ex = [
    ("box", "a spread", "Box plot"),
    ("timeline", "a trend over time", "Line chart"),
    ("scatter", "a relationship", "Scatter"),
    ("stream", "a changing mix", "Streamgraph"),
    ("heatmap", "across two categories", "Heatmap"),
    ("map", "across the map", "Map"),
]
for i, (g, comp, chrt) in enumerate(ex):
    x = 0.7 + (i % 3)*(3.85+0.22); y = 3.52 + (i//3)*(1.18+0.16)
    _ex(x, y, g, comp, chrt)
textbox(s, 0.7, 6.5, 12.0, 0.4,
        "Name the comparison first (task abstraction), then pick the chart the "
        "eye reads most accurately for it (graphical perception).",
        12, NAVY, italic=True, align=PP_ALIGN.CENTER)
_source(s, "Munzner 2014 · Cleveland & McGill 1984")
s.notes_slide.notes_text_frame.text = (
    "Grounding for Q&A (in the report's bibliography): naming the comparison "
    "before the chart is task abstraction (Munzner, 2014); choosing the chart "
    "whose channel the eye reads most accurately is graphical perception "
    "(Cleveland and McGill, 1984).")

# --- Slide · why these, not those (the perceptual ladder) -------------------
s = content_slide(
    "Backup: chart choice follows perceptual accuracy",
    "Visualization · why these, not those")
_source(s, "Cleveland & McGill, 1984")
textbox(s, 0.6, 2.0, 9.0, 0.28,
        "HOW ACCURATELY THE EYE READS A VALUE",
        11.5, GREYTX, bold=True)
# accepted channels carry no example here (their charts are shown elsewhere);
# the rejected channels show an actual mini chart so the audience sees the flaw
ladder = [
    ("Position", NAVY, WHITE, [], "Box plot · Timeline · Scatter",
     "kept", GREEN),
    ("Length", BLUE, WHITE, [], "Streamgraph", "kept", GREEN),
    ("Angle / slope", RGBColor(0x6F, 0x9B, 0xD1), WHITE, ["radar"], "Radar",
     "rejected", REJECT),
    ("Area", RGBColor(0x9F, 0xBF, 0xE2), NAVY, ["pie", "donut"], "Pie · Donut",
     "rejected", REJECT),
    ("Colour", ICE, NAVY, [], "Heatmap · Map", "kept", GREEN),
]
ly, lh, lgap = 2.46, 0.68, 0.12
ex_x, ex_w = 8.4, 2.55
textbox(s, 0.62, ly-0.26, 3.0, 0.22, "MOST ACCURATE", 10, GREEN, bold=True)
for i, (nm, fill, tcol, examples, charts, tag, tagc) in enumerate(ladder):
    y = ly + i*(lh+lgap)
    bar = rrect(s, 0.6, y, 4.2, lh, fill)
    shape_text(bar, [(nm, 15, tcol, True, False)], align=PP_ALIGN.LEFT, mlr=0.24)
    textbox(s, 5.0, y, 5.9, lh, charts, 16, NAVY if tagc == GREEN else REJECT,
            bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if examples:
        eh = lh - 0.05
        gap = 0.2
        total = len(examples)*eh + (len(examples)-1)*gap
        sx = ex_x + (ex_w - total)/2
        for g in examples:
            fit_image(s, os.path.join(DIAG, "glyph_%s.png" % g),
                      sx, y+0.02, eh, eh)
            sx += eh + gap
    tint = RGBColor(0xEB, 0xF6, 0xEE) if tagc == GREEN else REDTNT
    rrect(s, 11.35, y+lh/2-0.2, 1.4, 0.4, tint, line=tagc, line_w=1.0)
    textbox(s, 11.35, y+lh/2-0.2, 1.4, 0.4, tag, 11, tagc, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
textbox(s, 0.62, ly+5*(lh+lgap)-0.04, 3.0, 0.22, "LEAST ACCURATE", 10, GREYTX,
        bold=True)
textbox(s, 0.6, 6.9, 12.13, 0.4,
        "Each value rides a channel the eye reads well; pie, donut, radar and "
        "3-D spend the worst channels on the only thing they show.",
        12.5, NAVY, italic=True, align=PP_ALIGN.CENTER)
s.notes_slide.notes_text_frame.text = (
    "Grounding for Q&A (in the report's bibliography): the accuracy ranking is "
    "Cleveland and McGill (1984), position and length decoded most accurately, "
    "angle and area least. It is also why the heatmap and map colour trade-off "
    "is acceptable, colour carries a pattern, not a precise comparison.")

# --- Slide · Stories (the second mode: tell, not explore) ------------------
s = content_slide(
    "Backup: scrollytelling pins one chart and guides the reader",
    "Visualization · stories")
_source(s, "Segel & Heer, 2010")

# left: the two modes over the same data
textbox(s, 0.6, 2.2, 3.4, 0.3, "TWO MODES, SAME DATA", 12, GREYTX, bold=True)
rrect(s, 0.6, 2.62, 3.35, 1.55, None, line=LINE, line_w=1.5)
textbox(s, 0.82, 2.76, 3.0, 0.3, "EXPLORE", 14, NAVY, bold=True)
textbox(s, 0.82, 3.1, 3.0, 0.9,
        "the reader drives, looking up whatever they want", 12.5, GREYTX,
        italic=True)
rrect(s, 0.6, 4.42, 3.35, 1.55, None, line=ACCENT, line_w=1.8)
leftbar(s, 0.6, 4.42, 1.55, ACCENT, w=0.06)
textbox(s, 0.82, 4.56, 3.0, 0.3, "TELL", 14, ACCENT, bold=True)
textbox(s, 0.82, 4.9, 3.0, 0.9,
        "the author drives, walking the reader through one finding", 12.5, NAVY,
        italic=True)

# right: the mechanic — one chart, three scroll states
textbox(s, 4.4, 2.2, 8.3, 0.3,
        "ONE CHART, PINNED · IT TRANSFORMS AS YOU SCROLL", 12, GREYTX, bold=True)
states = [("story1", "open on the whole", "the scene"),
          ("story2", "highlight one beat", "the turn"),
          ("story3", "land the takeaway", "the point")]
pw = 2.55
for i, (g, cap, sub) in enumerate(states):
    px = 4.4 + i*(pw+0.33)
    rrect(s, px, 2.62, pw, 2.6, None, line=LINE, line_w=1.4)
    b = rrect(s, px+0.18, 2.8, 0.34, 0.34, NAVY, shape=MSO_SHAPE.OVAL)
    shape_text(b, [(str(i+1), 13, WHITE, True, False)])
    fit_image(s, os.path.join(DIAG, "glyph_%s.png" % g), px+0.55, 3.08, 1.6, 1.1)
    textbox(s, px+0.15, 4.4, pw-0.3, 0.3, cap, 13, NAVY, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, px+0.15, 4.71, pw-0.3, 0.3, sub, 11, GREYTX, italic=True,
            align=PP_ALIGN.CENTER)
    if i < 2:
        textbox(s, px+pw, 3.5, 0.33, 0.4, "→", 18, GREYTX,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

textbox(s, 0.6, 6.7, 12.13, 0.4,
        "The chart never changes type; only what it points at changes, step by "
        "step, from the scene to the takeaway.",
        13, NAVY, italic=True, align=PP_ALIGN.CENTER)

s.notes_slide.notes_text_frame.text = (
    "Grounding for Q&A: this is the author-driven end of the narrative "
    "visualization spectrum (Segel and Heer, 2010); the dashboard is the "
    "reader-driven end. A Story is a guided walk through one finding, for an "
    "audience that will not explore the dashboard itself.")

# B11 — theory: Quality of Service (native three-axis cards)
s = content_slide("Backup: three independent reliability measures",
                  "Theory · Quality of Service")
_source(s, "Chawuthai & Srisakaokul, 2023")
textbox(s, 0.6, 1.95, 12.13, 0.34,
        "Reliability is not one number; it splits into three independent axes, "
        "each with its own measure.", 14, NAVY)
qos = [
    ("QoS-1", "Completion", "Did the trip finish?",
     "share of trips that ran start to end",
     "Low → trips cut short or cancelled.", GREEN),
    ("QoS-2", "On-path", "On the planned route?",
     "share of pings within 50 m of the route",
     "Low → the bus diverted off its path.", BLUE),
    ("QoS-3", "On-schedule", "On time at each stop?",
     "share of arrivals within 5 min of plan",
     "Low → chronically early or late.", ACCENT),
]
cw2, cgap = 3.93, 0.17
for i, (tag, name, q, formula, meaning, col) in enumerate(qos):
    x = 0.6 + i*(cw2+cgap)
    rrect(s, x, 2.46, cw2, 3.82, CARD, line=LINE, line_w=1.1)
    rrect(s, x, 2.46, cw2, 0.8, col)
    textbox(s, x, 2.53, cw2, 0.4, tag, 21, WHITE, bold=True, align=PP_ALIGN.CENTER)
    textbox(s, x, 2.95, cw2, 0.26, name.upper(), 10.5, WHITE, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, x+0.24, 3.42, cw2-0.48, 0.5, q, 14.5, NAVY, bold=True,
            align=PP_ALIGN.CENTER)
    textbox(s, x+0.24, 4.02, cw2-0.48, 0.24, "HOW IT IS MEASURED", 9, col,
            bold=True, align=PP_ALIGN.CENTER)
    rrect(s, x+0.32, 4.3, cw2-0.64, 0.6, WHITE, line=col, line_w=1.3)
    textbox(s, x+0.28, 4.3, cw2-0.56, 0.6, formula, 13, NAVY, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rrect(s, x+0.6, 5.12, cw2-1.2, 0.01, LINE)
    textbox(s, x+0.24, 5.26, cw2-0.48, 0.9, meaning, 12, GREYTX, italic=True,
            align=PP_ALIGN.CENTER)
textbox(s, 0.6, 6.55, 12.13, 0.4,
        "They are independent: a bus can finish every trip (QoS-1 high) and stay "
        "on its route (QoS-2 high) yet still arrive late at every stop (QoS-3 low).",
        11.5, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# B13 — theory: visual storytelling (the four moves, each explained)
s = content_slide("Backup: the four moves that declutter a chart",
                  "Theory · visual storytelling")
_source(s, "Knaflic, 2015")
fit_image(s, os.path.join(DIAG, "foundations_declutter.png"), 5.65, 2.15, 7.2, 4.3)
textbox(s, 5.65, 6.5, 7.2, 0.3,
        "SAME DATA — CLUTTERED (LEFT)  →  FOCUSED (RIGHT)", 10.5, GREYTX,
        bold=True, align=PP_ALIGN.CENTER)
moves = [
    ("Declutter", "remove non-data ink: gridlines, borders, legends, "
     "redundant labels"),
    ("Focus", "one accent colour on the element the story points at; the rest "
     "fades to grey"),
    ("Annotate", "label directly on the mark, not in a legend; flag the value "
     "that matters"),
    ("Narrate", "the title states the finding, not the variable name"),
]
my = 2.12
for i, (mv, desc) in enumerate(moves):
    rrect(s, 0.55, my, 4.85, 0.96, CARD, line=LINE, line_w=1.0)
    leftbar(s, 0.55, my, 0.96, ACCENT, w=0.07)
    n = rrect(s, 0.76, my+0.28, 0.4, 0.4, ACCENT, shape=MSO_SHAPE.OVAL)
    shape_text(n, [(str(i+1), 14, WHITE, True, False)])
    textbox(s, 1.36, my+0.12, 3.9, 0.32, mv, 15, NAVY, bold=True)
    textbox(s, 1.36, my+0.45, 3.96, 0.5, desc, 11.5, GREYTX, italic=True)
    my += 1.08
textbox(s, 0.55, 6.52, 4.9, 0.5,
        "Each move lowers cognitive load: the eye finds the point pre-attentively "
        "instead of scanning.", 10.5, NAVY, italic=True)

# B15 — theory: analytical methods (each: what it is for + how it works)
s = content_slide("Backup: five analytical methods — the why and the how",
                  "Theory · analytical methods")
_source(s, "Hirschman 1945 · Hyndman 2008 · Nielsen 1993")
# each method: name (what) · WHY it is used · HOW it is computed
methods = [
    ("MoSCoW prioritisation",
     "not everything can ship at once, so scope must be ranked",
     "tag every requirement Must / Should / Could / Won't"),
    ("Pareto principle",
     "a few items carry most of the total",
     "rank them and show only the vital top few, not all"),
    ("Exponential-smoothing forecast",
     "to project a series into the near future",
     "weight recent points more, learn the weekly pattern, draw a band"),
    ("Market concentration (HHI)",
     "is a market competitive, or run by a few operators?",
     "add up each operator's share squared — 0 to 10,000; higher = fewer players"),
    ("Response-time limits",
     "an interface has to feel instant to stay usable",
     "0.1 s feels instant · 1 s keeps flow · 10 s loses attention"),
]
my, rh, rgp = 2.04, 0.92, 0.085
for name, why, how in methods:
    rrect(s, 0.6, my, 12.13, rh, CARD, line=LINE, line_w=1.0)
    leftbar(s, 0.6, my, rh, ACCENT, w=0.06)
    textbox(s, 0.92, my, 4.25, rh, name, 14.5, NAVY, bold=True,
            anchor=MSO_ANCHOR.MIDDLE)
    rrect(s, 5.18, my+0.16, 0.02, rh-0.32, LINE)   # divider
    textbox(s, 5.42, my+0.17, 0.7, 0.26, "WHY", 9.5, ACCENT, bold=True)
    textbox(s, 6.12, my+0.16, 6.5, 0.3, why, 12, NAVY)
    textbox(s, 5.42, my+0.51, 0.7, 0.26, "HOW", 9.5, BLUE, bold=True)
    textbox(s, 6.12, my+0.5, 6.5, 0.3, how, 12, GREYTX, italic=True)
    my += rh + rgp

# B16 — theory: causal analysis (lead with what it is FOR, then the estimator)
s = content_slide("Backup: causal analysis with difference-in-differences",
                  "Theory · causal analysis")
_source(s, "Card & Krueger, 1994")
textbox(s, 0.55, 1.95, 12.2, 0.6,
        "What it is for: measuring whether an intervention caused an outcome — "
        "separating its real effect from the trend that would have happened "
        "anyway.", 13.5, NAVY)
fit_image(s, os.path.join(DIAG, "foundations_did.png"), 4.7, 2.78, 8.1, 3.88)
textbox(s, 4.7, 6.7, 8.1, 0.28, "TREATED vs CONTROL · BEFORE vs AFTER", 10,
        GREYTX, bold=True, align=PP_ALIGN.CENTER)
textbox(s, 0.55, 2.74, 3.9, 0.3, "THE METHOD", 11, ACCENT, bold=True)
bullets(s, 0.55, 3.14, 3.95, 1.7, [
    ("Treated = the units the intervention affected", 12.5, GREYTX, False,
     False, True),
    ("Control = comparable units it did not", 12.5, GREYTX, False, False,
     True),
    ("Compare each group's before→after change", 12.5, NAVY, False, False, True),
], space=9)
rrect(s, 0.55, 4.96, 3.9, 1.12, CARD2, line=ACCENT, line_w=1.4)
leftbar(s, 0.55, 4.96, 1.12, ACCENT, w=0.07)
textbox(s, 0.8, 5.05, 3.5, 0.24, "THE EFFECT", 9.5, ACCENT, bold=True)
ftb = textbox(s, 0.8, 5.32, 3.5, 0.7, "", 14, NAVY)
add_lines(ftb, [("treated's change − control's change", 13.5, NAVY, True, False),
                ("the part the shared trend cannot explain", 10.5, GREYTX,
                 False, True)])
textbox(s, 0.55, 6.28, 3.9, 0.8,
        "No clean control? a matched set forms a synthetic counterfactual.",
        11, GREYTX, italic=True)


# =============================================================================
# BACKUP B — EVIDENCE FOR LIKELY Q&A
# =============================================================================
# E1 — three architecture candidates (the measured selection)
s = content_slide("Backup: three architecture candidates",
                  "Evaluation · architecture selection")
cx = [0.6, 5.0, 7.4, 9.7]; cw = [4.4, 2.4, 2.3, 3.03]
hdr = ["Candidate", "Integrity", "Warm load", "Verdict"]
hy = 2.15
rrect(s, 0.6, hy, 12.13, 0.56, NAVY)
for i, c in enumerate(hdr):
    textbox(s, cx[i]+0.18, hy, cw[i]-0.2, 0.56, c, 13, WHITE, bold=True,
            anchor=MSO_ANCHOR.MIDDLE)
rows = [
    ("Star-schema over raw views", "+17.9 % inflation", "n/a",
     "Rejected", "integrity fail", REJECT, False),
    ("Plain Medallion (Gold built on read)", "lossless", "5,517 ms",
     "Rejected", "too slow", REJECT, False),
    ("Medallion + materialised Gold", "lossless · 17,883,623", "920 ms",
     "Selected", "fast + correct", GREEN, True),
]
ry0 = hy + 0.62; rh = 0.92
for j, (cand, integ, load, verdict, why, col, sel) in enumerate(rows):
    y = ry0 + j*(rh+0.1)
    rrect(s, 0.6, y, 12.13, rh, RGBColor(0xEB,0xF6,0xEE) if sel else
          (CARD if j % 2 else WHITE), line=(GREEN if sel else LINE),
          line_w=(1.8 if sel else 1.0))
    if sel:
        leftbar(s, 0.6, y, rh, GREEN, w=0.08)
    textbox(s, cx[0]+0.18, y, cw[0]-0.2, rh, cand, 13.5, NAVY, bold=sel,
            anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx[1]+0.18, y, cw[1]-0.2, rh, integ, 12,
            REJECT if "inflation" in integ else NAVY, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx[2]+0.18, y, cw[2]-0.2, rh, load, 12, NAVY,
            anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, cx[3]+0.18, y+0.16, cw[3]-0.2, 0.34, verdict, 14, col, bold=True)
    textbox(s, cx[3]+0.18, y+0.5, cw[3]-0.2, 0.3, why, 10.5, GREYTX, italic=True)
textbox(s, 0.6, ry0+3*(rh+0.1)+0.05, 12.13, 0.5,
        "Inmon CIF and Data Vault were also weighed and dropped: with no "
        "audit-history need and one downstream consumer, their overhead buys "
        "nothing here.", 12, GREYTX, italic=True)

# E2 — three integrity bugs fixed in Silver
s = content_slide("Backup: three integrity bugs fixed in Silver",
                  "Architecture · Silver integrity")
bx = [0.6, 3.5, 8.9]; bw = [2.9, 5.4, 3.83]
hy = 2.15
rrect(s, 0.6, hy, 12.13, 0.56, NAVY)
for i, c in enumerate(["Bug", "Cause", "Fix"]):
    textbox(s, bx[i]+0.18, hy, bw[i]-0.2, 0.56, c, 13, WHITE, bold=True,
            anchor=MSO_ANCHOR.MIDDLE)
bugs = [
    ("Duplicate trips", "ticket_trips.trip_id has 4,051 dupes",
     "dim_trip GROUP BY"),
    ("Route key split", "3 route_ids carry leading-zero route_no variants",
     "dim_route 1:1 ROW_NUMBER"),
    ("Stop double-count", "19 stops within 500 m of 2 universities",
     "dim_school_stop closest-uni-wins"),
]
ry0 = hy + 0.62; rh = 0.74
for j, (bug, cause, fix) in enumerate(bugs):
    y = ry0 + j*(rh+0.1)
    rrect(s, 0.6, y, 12.13, rh, CARD if j % 2 else WHITE, line=LINE, line_w=1.0)
    textbox(s, bx[0]+0.18, y, bw[0]-0.2, rh, bug, 13, NAVY, bold=True,
            anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, bx[1]+0.18, y, bw[1]-0.2, rh, cause, 12, GREYTX,
            anchor=MSO_ANCHOR.MIDDLE)
    ck = rrect(s, bx[2]+0.04, y+rh/2-0.1, 0.2, 0.2, GREEN, shape=MSO_SHAPE.OVAL)
    textbox(s, bx[2]+0.04, y+rh/2-0.11, 0.2, 0.2, "✓", 10, WHITE, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, bx[2]+0.32, y, bw[2]-0.34, rh, fix, 11.5, NAVY,
            anchor=MSO_ANCHOR.MIDDLE)
ry = ry0 + 3*(rh+0.1) + 0.06
rrect(s, 0.6, ry, 12.13, 0.8, RGBColor(0xEB,0xF6,0xEE), line=GREEN, line_w=1.4)
leftbar(s, 0.6, ry, 0.8, GREEN, w=0.08)
textbox(s, 0.92, ry+0.13, 11.6, 0.34, "Bronze → Gold is arithmetically lossless",
        14.5, GREEN, bold=True)
textbox(s, 0.92, ry+0.46, 11.6, 0.28,
        "agg_hub_kpis.boardings = 17,883,623, exactly the raw count",
        11.5, GREYTX, italic=True)

# E3 — performance self-audit (headline accented)
s = content_slide("Backup: performance self-audit",
                  "Evaluation · performance self-audit")
perf = [
    ("Total page serving cost · Silver only", "5,517.9 ms", False, None),
    ("Total page serving cost · Silver + Gold", "920.8 ms", True, "6.0× faster"),
    ("Median chart-endpoint latency", "31.1 ms", False, None),
    ("Endpoints within the 100 ms budget", "9 of 11", True, "N1 gate"),
    ("Slowest · Voronoi isochrone (scipy-bound)", "311.4 ms", False, None),
]
ry, rh, rgp = 2.2, 0.7, 0.14
for i, (m, v, acc, tag) in enumerate(perf):
    y = ry + i*(rh+rgp)
    rrect(s, 0.6, y, 12.13, rh, RGBColor(0xFF,0xF1,0xEB) if acc else
          (CARD2 if i % 2 else CARD), line=(ACCENT if acc else LINE),
          line_w=(1.6 if acc else 1.0))
    if acc:
        leftbar(s, 0.6, y, rh, ACCENT, w=0.07)
    textbox(s, 0.92, y, 7.5, rh, m, 14.5, NAVY, bold=acc,
            anchor=MSO_ANCHOR.MIDDLE)
    if tag:
        textbox(s, 8.2, y, 2.3, rh, tag, 11.5, ACCENT, bold=True, italic=True,
                align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 10.6, y, 2.13, rh, v, 16 if acc else 14.5,
            ACCENT if acc else NAVY, bold=True, align=PP_ALIGN.RIGHT,
            anchor=MSO_ANCHOR.MIDDLE)
textbox(s, 0.6, ry+5*(rh+rgp)+0.02, 12.13, 0.4,
        "Materialising Gold cuts the full chart-catalogue serving cost about "
        "sixfold; 9 of 11 endpoints clear the 100 ms warm-render budget (N1).",
        12, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# E4 — GPS / AFC data windows (two-window timeline)
s = content_slide("Backup: GPS and AFC come from different years",
                  "Data · the two source windows")
ax0, ax1, ayv = 1.3, 12.5, 3.7
rrect(s, ax0, ayv, ax1-ax0, 0.02, LINE)
def _mx(mo): return ax0 + (ax1-ax0)*(mo/15.0)
for mo, lab in [(0,"Jan"),(3,"Apr"),(6,"Jul"),(9,"Oct"),(12,"Jan"),(14,"Mar")]:
    rrect(s, _mx(mo), ayv-0.06, 0.012, 0.12, LINE)
    textbox(s, _mx(mo)-0.4, ayv+0.08, 0.8, 0.24, lab, 9.5, GREYTX,
            align=PP_ALIGN.CENTER)
textbox(s, _mx(0)-0.1, ayv+0.34, 3.0, 0.3, "2025", 12, GREYTX, bold=True)
textbox(s, _mx(12)-0.1, ayv+0.34, 2.0, 0.3, "2026", 12, GREYTX, bold=True)
gx0, gx1 = _mx(2.6), _mx(4.3)
rrect(s, gx0, ayv-0.62, gx1-gx0, 0.5, BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
textbox(s, gx0-1.5, ayv-1.3, 4.6, 0.4, "GPS telemetry", 13, BLUE, bold=True,
        align=PP_ALIGN.CENTER)
textbox(s, gx0-1.5, ayv-0.96, 4.6, 0.3, "≈ 50 days · 2025", 10.5, GREYTX,
        italic=True, align=PP_ALIGN.CENTER)
fx0, fx1 = _mx(12), _mx(15)
rrect(s, fx0, ayv-0.62, fx1-fx0, 0.5, RGBColor(0x33,0x4E,0x6F),
      shape=MSO_SHAPE.ROUNDED_RECTANGLE)
textbox(s, fx0-0.7, ayv-1.3, 3.6, 0.4, "AFC fares", 13,
        RGBColor(0x33,0x4E,0x6F), bold=True, align=PP_ALIGN.CENTER)
textbox(s, fx0-0.7, ayv-0.96, 3.6, 0.3, "~17.8 M rows · Jan–Mar 2026", 10.5,
        GREYTX, italic=True, align=PP_ALIGN.CENTER)
gapc = (gx1+fx0)/2
rrect(s, gx1, ayv-0.37, fx0-gx1, 0.014, REJECT)
textbox(s, gapc-1.6, ayv-0.78, 3.2, 0.3, "no overlap", 11, REJECT, bold=True,
        italic=True, align=PP_ALIGN.CENTER)
ty = 4.75
rrect(s, 0.6, ty, 12.13, 0.95, RGBColor(0xFF,0xF1,0xEB), line=ACCENT, line_w=1.5)
leftbar(s, 0.6, ty, 0.95, ACCENT, w=0.08)
textbox(s, 0.92, ty+0.15, 11.6, 0.34,
        "Different years, so there is no timestamp-level join", 15, NAVY,
        bold=True)
textbox(s, 0.92, ty+0.51, 11.6, 0.34,
        "Cross-source analysis is matched at route × hour-of-day × day-type, "
        "the aggregate-profile level, never event to event.", 12, GREYTX,
        italic=True)
textbox(s, 0.6, 6.0, 12.13, 0.5,
        "GPS speed is ~50% null; Phase 2 ingests the full 50-day GPS to unlock "
        "Quality of Service and the city-wide speed grid.", 11.5, BLUE,
        italic=True, align=PP_ALIGN.CENTER)

# E5 — Tet 2026 case study (the proof of value)
anchor_slide(
    "Backup: the Tết 2026 shock",
    "Evaluation · case study",
    os.path.join(SHOT, "card5_pulse_v3.png"),
    [("Trough, 16 February", "−84 %", "33,176 boardings on the worst day",
      REJECT, REDTNT, REJECT),
     ("Nine-day window", "−57 % mean", "14 to 22 February; baseline returns "
      "by 23 February", ACCENT, CARD, BLUE)])

# E6 — the full Silver star schema (for the "draw your dimensional model" ask)
s = content_slide("Backup: the Silver star schema in full",
                  "Architecture · dimensional model")
cx, cy = 6.65, 4.16
DCX = [1.70, 4.18, 6.65, 9.12, 11.60]
dims = [
    ("route", DCX[0], 2.36), ("fare class", DCX[1], 2.36),
    ("hour", DCX[2], 2.36), ("calendar", DCX[3], 2.36),
    ("stop", DCX[4], 2.36),
    ("school", DCX[0], 5.96), ("school ↔ stop", DCX[1], 5.96),
    ("trip", DCX[2], 5.96), ("company", DCX[3], 5.96),
    ("payment", DCX[4], 5.96),
    ("vehicle", 1.35, 4.16), ("promotion", 11.95, 4.16),
]
for _, dx, dy in dims:                       # spokes first, under the boxes
    _sline(cx, cy, dx, dy)
rrect(s, cx - 1.05, cy - 0.34, 2.10, 0.68, NAVY)
textbox(s, cx - 1.05, cy - 0.29, 2.10, 0.34, "boardings", 15, WHITE, bold=True,
        align=PP_ALIGN.CENTER)
textbox(s, cx - 1.05, cy + 0.05, 2.10, 0.24, "fact · one row = one boarding",
        8.5, ICE, align=PP_ALIGN.CENTER)
for lbl, dx, dy in dims:
    _chip(dx - 0.98, dy - 0.23, 1.96, lbl, h=0.46, fill=ICE, line=SILVER_C)
textbox(s, 0.6, 6.55, 12.13, 0.32,
        "One central fact at the grain of a single boarding; twelve conformed "
        "dimensions — any chart sums the fact, grouped by a few of them.",
        11.5, NAVY, italic=True, align=PP_ALIGN.CENTER)
textbox(s, 0.6, 6.93, 12.13, 0.26,
        "Two secondary facts — gps_trips and stop_visits — share these same "
        "conformed dimensions.", 10, GREYTX, italic=True, align=PP_ALIGN.CENTER)

# =============================================================================
out = os.path.join(ROOT, "report", "capstone_defence.pptx")
prs.save(out)
print("Saved", out, "with", len(prs.slides._sldIdLst), "slides")
