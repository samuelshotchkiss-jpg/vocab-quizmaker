"""context_quiz.py -- the quiz that prints each word in a line of the Latin it came from.

The classic quiz asks for twenty headwords in two columns and fits on one side of a sheet. This
one asks for the same words with the poetry around them, which does not fit in a column: ten to a
page, one column, up to two pages -- a single double-sided sheet.

    1.  accedo, accedere, accessi, accessum   ______________________________

        accedet fatis matris miserabilis infans,
        et nondum nato funeris auctor eris,
        cumque parente sua frater morietur Iuli, (Ovid, Her. 7.135)

THE CONTEXT IS NOT COMPUTED HERE, and it could not be. Which of a word's occurrences a student
should meet depends on what the class has been taught and in what order, which lives in the Latin
Vocab Toolkit's quiz ledger; the macronized spelling comes from a Morpheus pipeline. So this app
receives the context ready-made, as JSON on the clipboard, exactly as it already receives word
lists as TSV -- `python engine/cycles.py quiz --clipboard` in the toolkit. See `parse_payload`
for the shape.

WHY A SEPARATE MODULE. The classic quiz works; the point of this file is that adding the new one
cannot break it. `vocab-quizmaker.py` keeps its own layout untouched and calls in here for the
other. It also means this half can be run, and its PDF looked at, without a Qt display.

BOLD NEEDS A REGISTERED FACE. The classic quiz never set a word in bold, so registering the
regular Times face was enough. `<b>` in a Paragraph resolves through a FAMILY, so without
`registerFontFamily` ReportLab quietly draws bold as regular -- and the headword and the word in
the poem, the two things the student must be able to find, are exactly what is bold here. The
base-14 PDF Times is not a substitute: it has no macrons, which is why the app loads a TTF at all.
"""
from __future__ import annotations

import json
import os
import platform
import re

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

FORMAT = "latin-vocab-context-quiz"

# --- page geometry ------------------------------------------------------------
PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
ITEMS_PER_PAGE = 10
MAX_PAGES = 2

NUM_W = 22          # the "1." gutter
CTX_INDENT = 14     # the poetry sits inside the headword
HEAD_SIZE = 11
CTX_SIZE = 9.5
CTX_LEADING = 11.5
ANSWER_MIN = 150    # an answer line shorter than this is not worth writing on
ANSWER_GAP = 14     # between the end of the headword and the start of its line
HEAD_TO_CTX = 6     # headword baseline to the first line of poetry
MAX_ITEM_GAP = 26   # do not let four items drift to the corners of an empty page

_TAG = re.compile(r"<[^>]+>")
_ENTITY = {"&amp;": "&", "&lt;": "<", "&gt;": ">"}


def plain(markup: str) -> str:
    """The text without its tags -- for measuring, never for drawing."""
    out = _TAG.sub("", markup or "")
    for k, v in _ENTITY.items():
        out = out.replace(k, v)
    return out


# --- the payload --------------------------------------------------------------

def parse_payload(text: str):
    """The toolkit's context-quiz JSON, or None if this is not that.

    Returns the list of items, each a dict with `latin` (the headword), `english`, `context`
    (a list of lines of poetry, the quizzed word wrapped in <b>), and `citation`. Everything is
    already in ReportLab's mini-HTML dialect, rendered by the toolkit -- the same arrangement as
    the survey app, which is sent HTML rather than being taught the markup rules.

    SNIFFS rather than being told, so one Import button keeps serving both formats: a TSV word
    list does not start with '{', and JSON that is not ours is refused by name.
    """
    s = (text or "").strip()
    if not s.startswith("{"):
        return None
    try:
        data = json.loads(s)
    except ValueError:
        return None
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        return None
    items = data.get("items") or []
    for i, it in enumerate(items):
        if not it.get("latin") or not it.get("context"):
            raise ValueError(f"item {i + 1} has no headword or no context")
    return items


# --- fonts --------------------------------------------------------------------

_FACES = {  # suffix -> (Windows file, macOS file)
    "": ("times.ttf", "Times New Roman.ttf"),
    "-Bold": ("timesbd.ttf", "Times New Roman Bold.ttf"),
    "-Italic": ("timesi.ttf", "Times New Roman Italic.ttf"),
    "-BoldItalic": ("timesbi.ttf", "Times New Roman Bold Italic.ttf"),
}
_DIRS = {
    "Windows": ["C:\\Windows\\Fonts"],
    "Darwin": ["/System/Library/Fonts/Supplemental", "/Library/Fonts"],
}


def register_family(base: str) -> str:
    """Make `<b>` and `<i>` real for `base`, and say which font name to draw with.

    The regular face is already registered by the app; this adds the others where the files
    exist and maps the family. A missing bold face degrades to regular -- visibly worse, but a
    quiz that prints is better than one that raises, and `missing_faces` reports it.
    """
    if base == "Helvetica":          # a base-14 family ReportLab already knows about
        return base
    for suffix, names in _FACES.items():
        name = base + suffix
        if name in pdfmetrics.getRegisteredFontNames():
            continue
        for d in _DIRS.get(platform.system(), []):
            for fn in names:
                path = os.path.join(d, fn)
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont(name, path))
                    except Exception:                     # noqa: BLE001 - a font is not fatal
                        pass
                    break
            if name in pdfmetrics.getRegisteredFontNames():
                break
    have = pdfmetrics.getRegisteredFontNames()
    pick = lambda s: (base + s) if (base + s) in have else base   # noqa: E731
    pdfmetrics.registerFontFamily(base, normal=base, bold=pick("-Bold"),
                                  italic=pick("-Italic"), boldItalic=pick("-BoldItalic"))
    return base


def missing_faces(base: str) -> list[str]:
    have = pdfmetrics.getRegisteredFontNames()
    return [base + s for s in ("-Bold", "-Italic") if s and (base + s) not in have]


# --- layout -------------------------------------------------------------------

def _styles(font: str):
    head = ParagraphStyle("CtxHead", fontName=font, fontSize=HEAD_SIZE,
                          leading=HEAD_SIZE * 1.2)
    ctx = ParagraphStyle("CtxLine", fontName=font, fontSize=CTX_SIZE, leading=CTX_LEADING)
    return head, ctx


def _item_flowables(item, styles, width):
    """(headword paragraph, [context paragraphs], headword width) for one word."""
    head_style, ctx_style = styles
    head = Paragraph(f"<b>{item['latin']}</b>", head_style)
    lines = list(item.get("context") or [])
    cit = item.get("citation")
    if cit and lines:
        # The citation rides on the END of the last line rather than taking a line of its own:
        # it is a label on the quotation, and ten of them in a column would read as content.
        #
        # DO NOT ITALICIZE IT HERE. The citation arrives already marked up, and the italic
        # belongs to the TITLE OF THE WORK alone -- not the author's abbreviation, not the book
        # and line numbers, and not these parentheses. Wrapping the lot in <i> is what this line
        # used to do, and it printed (Ovid, Met. 8.186) entirely in italic: a citation style the
        # teacher would mark down, modelled ten times a page in front of the class.
        lines[-1] = f"{lines[-1]} ({cit})"
    ctx = [Paragraph(l, ctx_style) for l in lines]
    head_w = pdfmetrics.stringWidth(plain(item["latin"]), _bold_name(head_style.fontName),
                                    HEAD_SIZE)
    return head, ctx, head_w


def _bold_name(base: str) -> str:
    name = base + "-Bold"
    return name if name in pdfmetrics.getRegisteredFontNames() else base


def _measure(head, ctx, width):
    """Height of one item once everything has been wrapped to `width`."""
    h = head.wrap(width - NUM_W, PAGE_H)[1]
    for p in ctx:
        h += p.wrap(width - NUM_W - CTX_INDENT, PAGE_H)[1]
    return h + HEAD_TO_CTX


def build(path, items, title, font, name_line=True):
    """Write the PDF. `items` is what will be printed -- the caller does the sampling."""
    cap = ITEMS_PER_PAGE * MAX_PAGES
    if len(items) > cap:
        raise ValueError(f"{len(items)} items is more than {cap}: the context quiz is "
                         f"{ITEMS_PER_PAGE} to a page and at most {MAX_PAGES} pages")
    font = register_family(font)
    styles = _styles(font)
    c = canvas.Canvas(str(path), pagesize=letter)
    content_w = PAGE_W - 2 * MARGIN
    x_num = MARGIN
    x_text = MARGIN + NUM_W

    pages = [items[i:i + ITEMS_PER_PAGE] for i in range(0, len(items), ITEMS_PER_PAGE)] or [[]]
    for page_no, page_items in enumerate(pages):
        y = _header(c, title, font, first=(page_no == 0), name_line=name_line)
        prepared = [_item_flowables(it, styles, content_w) for it in page_items]
        heights = [_measure(h, cx, content_w) for h, cx, _w in prepared]
        room = y - (MARGIN + 18)
        slack = room - sum(heights)
        gap = min(MAX_ITEM_GAP, slack / max(1, len(prepared) - 1)) if len(prepared) > 1 else 0
        gap = max(gap, 0)

        for i, ((head, ctx, head_w), h) in enumerate(zip(prepared, heights)):
            n = page_no * ITEMS_PER_PAGE + i + 1
            c.setFont(font, HEAD_SIZE)
            c.drawString(x_num, y - HEAD_SIZE, f"{n}.")
            head.drawOn(c, x_text, y - head.height)

            # the answer line, on the headword's own row when there is room for a usable one
            base_y = y - head.height + 2
            start = x_text + head_w + ANSWER_GAP
            if head.height <= HEAD_SIZE * 1.3 and (MARGIN + content_w) - start >= ANSWER_MIN:
                c.setLineWidth(0.5)
                c.line(start, base_y, MARGIN + content_w, base_y)
            y -= head.height + HEAD_TO_CTX

            for p in ctx:
                p.drawOn(c, x_text + CTX_INDENT, y - p.height)
                y -= p.height
            y -= gap

        c.setFont(font, 8)
        c.drawCentredString(PAGE_W / 2, MARGIN / 2, "Generated automatically by VocabQuizMaker")
        c.showPage()
    c.save()
    return len(pages)


def _header(c, title, font, first: bool, name_line: bool) -> float:
    """Draw the page header; return the y the first item starts at."""
    top = PAGE_H - MARGIN
    if first:
        c.setFont(font, 18)
        c.drawString(MARGIN, top, title)
        if name_line:
            c.setFont(font, 12)
            c.drawRightString(PAGE_W - MARGIN, top, "Nōmen mihi est: _________________")
            c.drawRightString(PAGE_W - MARGIN, top - 20, "Diēs: __________________")
        rule = top - (40 if name_line else 12)
    else:
        c.setFont(font, 10)
        c.drawString(MARGIN, top, title)
        rule = top - 12
    c.setLineWidth(0.5)
    c.line(MARGIN, rule, PAGE_W - MARGIN, rule)
    return rule - 18
