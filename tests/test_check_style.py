#!/usr/bin/env python3
"""The cases of scripts/check_style.py: how its rules read a phrase, TeX, and a letter.

    python3 -I tests/test_check_style.py        # no Lean, no network

Each case is a short text, or a small figure, with the finding its rule should make of
it, put to the script's own patterns and functions:

* the phrase cases: each wording rule finds its phrase however a line or a comment wraps
  it, and not across a blank line (save S2's and S7's), inside a quotation or in one of
  Heath's `--` lines; and S3 still finds an "I" after "Book" when anything but one space
  stands between them;
* the TeX cases: S10 allows `$…$` only in a paragraph that opens
  "**The modern way.**", with balanced delimiters and no shape known to break on
  GitHub; TeX outside such a span still fails, in the modern way as elsewhere;
* the ink cases: S20 judges a letter on an angle's wedge, a filled path, by the wedge's
  fill, within its three ends and beyond its chord out to its arc, and not beyond the
  arc; however the wedge is spelled (an absolute arc, a relative arc, a cubic curve), and
  wherever a transform moves it;
* the modern cases: S24 and S25 read a figure of the modern way against its Euclid's
  figure's letters and its paragraph's names, which `modern_names` takes from TeX and
  from plain words alike, save the letters of English (A's, e.g. however its full stops
  are spelled and spaced, the p of Heath's page and the letters of a Roman page number,
  the article "a") and what a reader does not see, in a comment or in code; a letter
  beside a letter of any script or a mark is in its word; emphasis or an invisible
  character that would let a letter of one word stand alone is refused; the paragraph
  selection keeps its source offsets and indentation.
* the wording cases: render.py names the rules of an overlap that a proof leaves unused
  as "does not use" for one, "neither … nor" for two and "none of" for more; says under
  the enunciation how many combinations an overlap's `ways` gives, and in a few words
  what the proof rests on among their rules, and names each combination, with the rules
  the proof rests on, in the Overlap row and the book's summary, beside overlaps worded
  as before; and words III.24's application of one segment to another by `placement`
  only from what its facts.json entry shows, read afresh for each root;
* the figure cases: render.py's caption under Euclid's figure says "Drawn for one case"
  before the case the record's [figure] names, or "Drawn for every case" where the record
  says `every_case`, and heath.py refuses an `every_case` that is not true or false, or
  that has no `case` for the caption to name;
* the clearance cases: S26 finds a stroke through a letter, or nearer it than 2 less half
  its width (given as an attribute or inherited), and not one clear of it;
  reads a stroke of none as no stroke and a dashed one whole; closes a path's stroke only
  where a Z closes it, a polygon's always and a polyline's never; finds a circle or an
  ellipse through a letter and not one round it, a dot beside it, a dot or a short stroke
  wholly within it, and each of the canvas's four edges; leaves out a circle of no radius,
  a rect of no width and a line of no length with butt caps, and follows a rect's rounded
  corners for the admitted radius spellings; follows a transform, of a stroke or of the
  letter, taking a width and a radius at the most it stretches them; measures a letter
  upright or italic, and at its size, as its figure sets it, and places it by its anchor
  and the whole label's advance; reads admitted decimal widths alike, mitre joins with
  inherited stroke-linejoin and the default limit of 4, and round caps on single-point
  closed subpaths. Offsets, explicit mitre limits and square caps require refusal.
  Both figure entry points require its findings.
  And it finds a letter drawn twice, or twice in one of
  several figures side by side, or across the cut between them, and reads A and A′ as two
  letters; and it names a line dashed by itself or by its group as a dashed line.
* the input cases: both complete figure checks refuse elements, attributes, numbers,
  transforms, keywords and path commands outside main's SVG language before measuring,
  and an arc that SVG draws as no arc (its ends one point, or a radius of 0), while every
  choice of an arc's two flags draws;
  cases using CSS, scale transforms, units, exponents or other excluded features require
  their exact refusal, separately from admitted geometry cases. Point labels require an
  effective supported Georgia declaration; effective
  strokes and bold weights, unmeasured label characters and incomplete ellipse radii fail.
  Numeric inputs and cubic subdivision
  are bounded; non-finite geometry and decoder failures report the figure and leave
  subsequent figures checked. Cubic subdivision includes its chord error, and malformed
  lists take linear time;
* the upright cases: S15 and S20 fail an italic letter planted in a copy of Euclid's figure
  and of the figure at a glance, one letter or every one, as the figures were drawn until
  21 October, and D15 lists nothing;
* the scope cases (#66): which texts of a review record the rules read, and on which
  lines; the docstring render.py shows, found again in its file; S12's reading of a
  `name : type`; S22's reading of letters in backticks, one code span at a time; and the
  reach of 19 October, whose findings in a file of REACH_PENDING are reported only for the
  rules the file is listed for, while every other finding in that file still fails, and
  whose rules are reported as done one by one, as each is left with no finding;
* the acceptance case: check_acceptance.py sorts a style finding in a review record to
  its proposition's P9, the item for the record's notes, and every other as before;
* the conflict-marker cases: S23 reads tracked UTF-8 text and copies without Git,
  refuses each marker kind even in Markdown fences and comments, allows setext headings
  over ordinary paragraphs but refuses possible reference definitions throughout a block,
  raises on traversal errors and skips symlinks; S12 keeps Git's index.

CI's `check` job runs this file just before check_style.py, and scripts/safe_push.py runs
it in the same place (docs/WORKFLOW.md, section 8), so a case read wrongly stops the
checks before the style check's findings are read. When a rule is found reading a phrase,
TeX or a letter wrongly, its fix comes with a case here that the old rule fails (WORKFLOW,
section 8, "A guard defect gets a regression"). Python 3.11 or later; standard library.
"""

from __future__ import annotations

import io
import json
import math
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from collections import defaultdict
from contextlib import ExitStack, redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_style as style  # noqa: E402
import heath  # noqa: E402
import render  # noqa: E402
import negative_tests as plants  # noqa: E402

# ---------------------------------------------------------------------------------------
# The phrase cases. (D7 once let "Lean\ncannot" through, in a docstring.)

PHRASE_CASES = [   # (rule, its search, the text as the rule reads it, a finding?)
    ("D7", style.LEAN_CANNOT.search, "as if picking it up. Lean\ncannot move a figure", True),
    ("D7", style.LEAN_CANNOT.search, "the note says Lean\n  -- cannot move it", True),
    ("D7", style.LEAN_CANNOT.search, "> what Lean\n> can't do", True),
    ("D7", style.LEAN_CANNOT.search, "Lean  can not", True),
    ("D7", style.LEAN_CANNOT.search, "what Lean\n\ncannot", False),
    ("D7", style.LEAN_CANNOT.search, "Leancannot", False),
    ("S2", style.CREW.search, "the first\n  -- mate", True),
    ("S2", style.CREW.search, "the first\n\nmate", True),
    ("S3", style.FIRST_PERSON.search, "as I\nthink", True),
    ("S3", style.FIRST_PERSON.search, "as I\n  -- would say", True),
    ("S3", style.FIRST_PERSON.search, "Book I was proved", False),
    ("S3", style.FIRST_PERSON.search, "Books I have read", False),
    ("S3", style.FIRST_PERSON.search, "Book I\nwas proved", False),
    ("S3", style.FIRST_PERSON.search, "in Book  I was", True),
    ("S3", style.FIRST_PERSON.search, "in Book\tI was", True),
    ("S3", style.FIRST_PERSON.search, "in Book\nI was", True),
    ("S3", style.FIRST_PERSON.search, "the Book\n  -- I would say", True),
    ("S3", style.FIRST_PERSON.search, "Books\n> I have", True),
    ("S3", style.FIRST_PERSON.search, "the eBook I have", True),
    ("S4", style.HEDGE.search, "strictly\nspeaking", True),
    ("S4", style.HEDGE.search, "it is worth\n   noting", True),
    ("S5", style.EUCLID_CITES.search, "Euclid\ncites I.3", True),
    ("S5", style.EUCLID_CITES.search, "I.1 to I.28 never\n  -- need it", True),
    ("S6", style.TACIT.search, "a tacit\nassumption", True),
    ("S7", style.DEFINITION.search, "by Definition\n15", True),
    ("S7", style.DEFINITION.search, "by Definition\n\n15", True),
    ("S9", style.ITALIC_LETTER.search, "the line *AB, CD*", True),
    ("S9", style.ITALIC_LETTER.search, "the line *AB,\nCD*", True),
    ("S9", style.ITALIC_LETTER.search, "> the line *AB\n> CD*", True),
    ("S9", style.ITALIC_LETTER.search, "the line *AB,\n\nCD*", False),
    ("D10", style.DEFINITION.search, "by Def.\n  -- 15", True),
    ("D8", style.NO_CITATION.search, "gives no\ncitation", True),
    ("D9", style.POSTULATE_5.search, "the parallel\npostulate", True),
    ("S11", style.REFRAINS[0][0].search, "the certificate\nrecords", True),
    ("S11", style.RETIRED_LEADS.search, "**What it\nrests on.**", True),
    ("S11", style.proclus_under_i31, "Proclus puts it under I.31.", True),
    ("S11", style.proclus_under_i31, "Proclus puts it under\nI.31.", True),
    ("S11", style.proclus_under_i31, "As Proclus says, it falls\n> under\n> I.31.", True),
    ("S11", style.proclus_under_i31, "Proclus puts it under\n\nI.31.", False),
    ("S11", style.proclus_under_i31, "Proclus says so. It falls under\nI.31.", False),
    # Read as the Lean notes are read (Heath's `--` lines out of scope), and as the prose
    # is read (quotations and code blanked first).
    ("D7", style.LEAN_CANNOT.search,
     style.notes_text("/-- We build it, for Lean\ncannot move a figure. -/\n"
                      "theorem T : True := trivial\n"), True),
    ("D7", style.LEAN_CANNOT.search,
     style.notes_text("theorem T : True := by\n  -- Lean\n  -- cannot\n  trivial\n"), False),
    ("D7", style.LEAN_CANNOT.search,
     style.blank_quotes(style.blank_code('He wrote "what Lean\ncannot" once.')), False),
    ("S3", style.FIRST_PERSON.search,
     style.blank_quotes(style.blank_code('as I "so" think')), True),
]

# ---------------------------------------------------------------------------------------
# The TeX cases: mishnahs on both sides of S10's modern-way boundary.

MW = style.MODERN_WAY + " "
TEX_CASES = [   # (a mishnah, as S10 reads it, a finding?)
    (MW + r"Then $e^{i\theta}$ turns B through $\theta$.", False),
    (MW + r"Put $\mathrm{A}$ at $0$; the angle is $\pi/2$, and $a_1 + b_1$ is real.", False),
    (MW + r"It is $\frac{e^{i\gamma}-e^{i\alpha}}{e^{i\beta}-e^{i\alpha}}$, and ($x$) too.", False),
    (MW + r"For $0 \lt b \lt a$, $a\thinspace b$ and $\lbrace x \rbrace$ hold.", False),
    ("**A lead.** Plain words.\n\n" + MW + r"It is $z \mapsto e^{i\theta} z$.", False),
    ("Plain words, with θ and π and (a + b)², and no lead.", False),
    (MW + r"Then $z^\ast$ and $w^\ast$ are conjugates.", False),
    (MW + r"Then $x_{1}^{2}$ and $a_{n}$ are terms.", False),
    (MW + r"Then $\theta_1$ and $\vec{u_1}$ are given.", False),
    (MW + "Then $x$ holds, and the modulus\n|z| is one, so $y$ is too.", False),
    (MW + "Then $x$ holds, and the sum is\n2. So $y$ is two.", False),
    (MW + "Then $x$ holds, as Lean's\n#check shows for $y$ too.", False),
    (r"**A lead.** Then $e^{i\theta}$ turns it.", True),
    (r"Then e^{iθ} turns it, in a paragraph with no lead.", True),
    (MW + r"Then e^{iθ} turns it.", True),
    (MW + r"Then \theta turns it.", True),
    (MW + r"Then $e^{i\theta}$ turns it, and \pi is half a turn.", True),
    (MW + r"Then $e^{i\theta}$ and $x turn it.", True),
    (MW + r"Then $e^{i\theta$ turns it.", True),
    (MW + r"Then $e^{i\theta}}{$ turns it.", True),
    (MW + r"Then $$x^2$$ is a square.", True),
    (MW + r"Then $ x $ is padded.", True),
    (MW + "Then $x +\ny$ crosses a line.", True),
    (MW + r"Then the$x$ is glued before.", True),
    (MW + r"Then $x$s is glued after.", True),
    (MW + r'Then "$x$" is quoted.', True),
    (MW + r"Then $\{x\}$ loses its backslashes.", True),
    (MW + r"Then $a\,b$ loses its backslash.", True),
    (MW + r"Then $a < b$ is escaped twice.", True),
    (MW + r"Then $z^*$ and $w^*$ are read as emphasis.", True),
    (MW + r"Then $a*b*c$ is read as emphasis.", True),
    (MW + r"Then $\vec{u}_{1}$ and $\vec{v}_{2}$ are read as emphasis.", True),
    (MW + r"Then $x^{2}_{1}$ has its subscript after a brace.", True),
    (MW + r"Then $x~y$ is read as strikethrough.", True),
    (MW + r"Then $a`b$ holds a backtick.", True),
    ("**A lead.** A paragraph.\n" + MW + r"Then $x$ is in the lead's paragraph.", True),
    (MW + "Plain words.\n\nThen $x$ is in the next paragraph.", True),
    (MW + "Then $x$ holds.\n- and $y$ in a list item.", True),
    (MW + "Then $x$ holds.\n# $y$ a heading", True),
    (MW + "Then $x$ holds.\n+ and $y$ in a list item.", True),
    (MW + "Then $x$ holds.\n1) and $y$ in a list item.", True),
    (MW + "Then $x$ holds.\n> and $y$ in a quotation.", True),
    (MW + "Then $x$ holds.\n| $y$ | z |\n| --- | --- |", True),
    (r"**The modern way** without its full stop: $x$.", True),
]

# ---------------------------------------------------------------------------------------
# The ink cases: a letter on an angle's wedge, read as S20 reads a figure's letters.
# (S20 once read no paths, and let a black letter on a blue wedge through.)

INK_WEDGES = (   # a quarter wedge of radius 34 at (200, 150), below and right of it
    "M200,150 L234,150 A34,34 0 0,1 200,184 Z",
    "m200,150 l34,0 a34,34 0 0,1 -34,34 z",
    "M200,150 H234 C234,168.78 218.78,184 200,184 Z",
)
BLUE_WEDGE = '<path d="{wedge}" fill="#1f5aa6"/>'
YELLOW_ON_RED = ('<polygon points="150,100 300,100 300,250 150,250" fill="#d0312d"/>'
                 '<path d="{wedge}" fill="#f2b705"/>')
MOVED_WEDGE = '<g transform="translate(-100,20)"><path d="{wedge}" fill="#1f5aa6"/></g>'
WITHIN, ON_ARC, BEYOND = (215.0, 160.0), (221.2, 171.2), (226.9, 176.9)
MOVED = (121.2, 191.2)   # ON_ARC, where MOVED_WEDGE stands
IDEA_INK, IDEA_INK_ON_DARK = style.IDEA_INK, style.IDEA_INK_ON_DARK   # #222222, #fbf7ee

INK_CASES = [   # (what is drawn under the letter, its glyph's middle, its ink, a finding?)
    (BLUE_WEDGE, WITHIN, IDEA_INK, True),
    (BLUE_WEDGE, WITHIN, IDEA_INK_ON_DARK, False),
    (BLUE_WEDGE, ON_ARC, IDEA_INK, True),
    (BLUE_WEDGE, ON_ARC, IDEA_INK_ON_DARK, False),
    (BLUE_WEDGE, BEYOND, IDEA_INK, False),
    (BLUE_WEDGE, BEYOND, IDEA_INK_ON_DARK, True),
    (YELLOW_ON_RED, ON_ARC, IDEA_INK, False),
    (YELLOW_ON_RED, ON_ARC, IDEA_INK_ON_DARK, True),
    (MOVED_WEDGE, MOVED, IDEA_INK, True),
    (MOVED_WEDGE, MOVED, IDEA_INK_ON_DARK, False),
    (MOVED_WEDGE, ON_ARC, IDEA_INK, False),
]


def ink_finding(drawn: str, x: float, y: float, ink: str) -> bool:
    """Whether S20 finds fault with a letter A in `ink`, its glyph's middle at (x, y), on
    a parchment canvas with `drawn` under it."""
    size = style.IDEA_LETTER_SIZE
    root = ET.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
        f'<rect width="400" height="300" fill="#fbf7ee"/>{drawn}'
        f'<text x="{x}" y="{y + 0.35 * size}" text-anchor="middle" font-size="{size}" '
        f'font-style="italic" fill="{ink}">A</text></svg>')
    return any(style.ink_fault(root, eff, style.letter_centre(own, eff, m, "A"), "A")
               for el, own, eff, m, _ in style.placed(root) if style.tag(el) == "text")


# ---------------------------------------------------------------------------------------
# The modern cases: a figure of the modern way, read as S24 and S25 read it, against the
# letters its Euclid's figure draws and the names its paragraph uses.

MODERN_PARAGRAPH = (style.MODERN_WAY + r" Put $\mathrm{A} = (0, 0)$, $\mathrm{B} = (c, 0)$ "
                    r"and $\mathrm{C} = (0, b)$, and write $a$ for BC. Then $\vec{u}$ "
                    r"turns through $\theta$, and $\tfrac{1}{2}bc$ is the area; with h a "
                    "height, (a + b)² is plain.")
NAMES_CASES = [   # (a paragraph, names it must give, names it must not)
    (MODERN_PARAGRAPH, {"a", "b", "c", "u", "θ", "h"}, {"v", "e", "r", "t", "f", "m"}),
    (style.MODERN_WAY + r" The point $\mathrm{A} + i\mathrm{(B - A)}$ is D.", {"i"}, {"m", "r"}),
    (style.MODERN_WAY + " With AC = a and CB = b, the square is (a + b)².", {"a", "b"}, {"c"}),
    (style.MODERN_WAY + r" Its breadth is $q/(a\sin\theta)$.", {"q", "a", "θ"}, {"s", "n"}),
    (style.MODERN_WAY + r" With $\nu$ and $\vartheta$ and ϕ.", {"ν", "θ", "φ"}, {"n", "u"}),
    (style.MODERN_WAY + r" Let $a_{\text{side {length}}}$ be given.", {"a"}, {"g", "s", "l"}),
    (style.MODERN_WAY + r" On a base FG, A's side and Euclid’s turn a $\theta$, e.g. one, "
     "i.e. two; E.g. three.", {"θ"}, {"a", "s", "e", "g", "i"}),
    (style.MODERN_WAY + " Twice it is 2a, a² is its square, a/2 its half and\na − 1 less.",
     {"a"}, set()),
    # The letters of e.g. and i.e. with a full stop escaped, or a space after the first,
    # and the p of Heath's page, are no names; a p before anything but a page's number
    # is one (#172).
    (style.MODERN_WAY + r" One, e\.g\. two, i\.e\. three; e. g. four, i. e. five.",
     set(), {"e", "g", "i"}),
    (style.MODERN_WAY + " As Heath says (vol. 1, p. 383; vol. 2, pp. 63–64), p\\. 384 and"
     "\np.\n385.", set(), {"p"}),
    (style.MODERN_WAY + " Its side is p. Then (vol. 1, p. 383) it is twice q.",
     {"p", "q"}, set()),
    # A letter beside a letter of any script or a mark is in its word, whatever the reader
    # takes it for; spaces after a stop are one space to the reader; and a Roman page
    # number's letters are no names, nor its p (#172).
    (style.MODERN_WAY + " The éxponent, the eхponent with a Cyrillic х, déjà vu, "
     "2πr and aⁿ.", {"π"}, {"e", "d", "j", "r", "a"}),
    (style.MODERN_WAY + " One, e.  g. two, i.\n  e. three; Heath's preface (vol. 1, p. ix; "
     "pp. v–vii, p\\. x) and p. ivy.", {"p"}, {"e", "g", "i", "v", "x"}),
]
LEAN_NAME = "`Elements.BookI.prop05_converse`"
COMMENT_PARAGRAPH = (style.MODERN_WAY + " Put $b$ here <!--\nnotes x and y\n--> "
                     "and $c$ there.")
CODE_PARAGRAPH = style.MODERN_WAY + " Put $b$ here `k\nx` and $c$ there."
PAGE_NAMES_CASES = [   # (a mishnah, names its modern way gives, names it must not)
    (style.MODERN_WAY + f" Put $a$ here, as Lean says in\n{LEAN_NAME}\nwith $b = c$.",
     {"a", "b", "c"}, set()),
    (style.MODERN_WAY + " Put $a$ here <!-- crew: label x and y later --> and so on.",
     {"a"}, {"x", "y"}),
    (style.MODERN_WAY + " Put $a$ here, as `$z$` and `k` say.", {"a"}, {"z", "k"}),
    (COMMENT_PARAGRAPH, {"b", "c"}, {"x", "y"}),
    (CODE_PARAGRAPH, {"b", "c"}, {"k", "x"}),
    (CODE_PARAGRAPH.replace("`", "``"), {"b", "c"}, {"k", "x"}),
    (style.MODERN_WAY + " Put $b$ here `<!--` and $c$ there <!-- x -->.",
     {"b", "c"}, {"x"}),
    (style.MODERN_WAY + " Put $b$ here <!-- `x` --> and $c$ there.",
     {"b", "c"}, {"x"}),
    (style.MODERN_WAY + " Put $b$ here `k\nx and $c$ there.", {"b", "c", "k", "x"}, set()),
    # The modern figure uses the same link and code parsing as S12 and S22: a backtick
    # in a link's target cannot hide a visible name, and an invalid link hides nothing.
    (style.MODERN_WAY + " Put $b$ here [link](https://example.test/x/`) and $c$ there `k`.",
     {"b", "c"}, {"k", "x"}),
    (style.MODERN_WAY + " Put $b$ here [x](/my $z$) and $c$ there.",
     {"b", "c", "z"}, set()),
    (style.MODERN_WAY + " Put $b$ here [x](<https://example.test/$z$>) and $c$ there.",
     {"b", "c"}, {"z"}),
]
SPAN_CASES = [   # (a mishnah, the paragraph modern_span finds, or None)
    (style.MODERN_WAY + f" Put $a$ here, as Lean says in\n{LEAN_NAME}\nwith $b = c$.\n\nAfter.",
     style.MODERN_WAY + " Put $a$ here, as Lean says in\n" + " " * len(LEAN_NAME)
     + "\nwith $b = c$."),
    ("Before.\n\n" + style.MODERN_WAY + " x.\n\nAfter.", style.MODERN_WAY + " x."),
    ("Before.\n \n" + style.MODERN_WAY + " x.\n \nAfter.", style.MODERN_WAY + " x."),
    ("Before.\n\n  " + style.MODERN_WAY + " x.", style.MODERN_WAY + " x."),
    (style.MODERN_WAY + " x.\n# A heading", style.MODERN_WAY + " x."),
    ("<!--\n\n" + style.MODERN_WAY + " x.\n\n-->", None),
    ("```\n" + style.MODERN_WAY + " x.\n```", None),
    ("**A lead.** No modern way here.", None),
    ("    " + style.MODERN_WAY + " Put $b$ here.", None),
    ("\t" + style.MODERN_WAY + " Put $b$ here.", None),
    (COMMENT_PARAGRAPH + "\n\nAfter $z$.",
     style.MODERN_WAY + " Put $b$ here     \n             \n    and $c$ there."),
    (CODE_PARAGRAPH + "\n\nAfter $z$.",
     style.MODERN_WAY + " Put $b$ here   \n   and $c$ there."),
]
# These expectations are source slices, before comments or code are masked. The renderer
# must insert after that whole slice, and the figure rules must select the same one.
SOURCE_SPAN_CASES = [   # (the text before, the paragraph or None, the text after)
    ("", None, "    " + style.MODERN_WAY + " Put $b$ here."),
    ("Before.\n\n", None, "    " + style.MODERN_WAY + " Put $b$ here."),
    ("Before.\n\n   ", COMMENT_PARAGRAPH, "\n\nAfter $z$."),
    ("", COMMENT_PARAGRAPH, "\n# Next"),
    ("Before.\n\n", CODE_PARAGRAPH, "\n\nAfter $z$."),
    ("", CODE_PARAGRAPH, "\n- Next"),
    ("# Before\n", style.MODERN_WAY + " Put $b$ here.", "\n> Next"),
    ("<!-- before\n\nnotes\n-->\n", style.MODERN_WAY + " Put $b$ here.", "\n<div>Next</div>"),
    ("    Some code.\n", style.MODERN_WAY + " Put $b$ here.", "\n<!-- Next -->"),
    ("", style.MODERN_WAY + " Put $b$ here.\n    With $c$ there.", "\n1. Next"),
    ("", style.MODERN_WAY + " Put $b$ here.\n2. With $c$ there.", "\n~~~\ncode\n~~~"),
    ("", style.MODERN_WAY + " Put $b$ here.\n<span>With $c$ there.</span>", "\n\nAfter."),
    ("", style.MODERN_WAY + " Put $b$ here.", "\n| Next |\n| --- |\n| $z$ |"),
    ("Before.\n", None, style.MODERN_WAY + " Put $b$ here."),
    ("", None, style.MODERN_WAY + " Put $b$ here.\n===\n"),
    ("~~~\n\n", None, style.MODERN_WAY + " Put $b$ here.\n~~~"),
    ("````\n```\n\n", None, style.MODERN_WAY + " Put $b$ here.\n````"),
    ("```\n\n", None, style.MODERN_WAY + " Put $b$ here."),
    ("<div>\n\n", style.MODERN_WAY + " Put $b$ here.", "\n\nAfter."),
    ("<div>\n", None, style.MODERN_WAY + " Put $b$ here.\n</div>"),
    ("<span>\n", None, style.MODERN_WAY + " Put $b$ here.\n</span>"),
    # The shared block parser recognises tables by both rows and keeps a line with
    # mismatched columns, or a backtick in a fence's info string, in its paragraph.
    ("", style.MODERN_WAY + " Put $b$ here.", "\nNext\n| --- |\n| $z$ |"),
    ("", style.MODERN_WAY + " Put $b$ here.\n| Next | two |\n| --- |\nWith $c$ there.",
     "\n\nAfter."),
    ("", style.MODERN_WAY + " Put $b$ here.\n```bad`info\nWith $c$ there.",
     "\n\nAfter."),
    # A fence inside raw HTML is inert. The next top-level paragraph is still found,
    # while a modern lead inside a quotation, list item or table is not a paragraph.
    ("<div>\n```\n\n", style.MODERN_WAY + " Put $b$ here.", "\n\nAfter."),
    ("<script>\n```\n</script>\n", style.MODERN_WAY + " Put $b$ here.", "\n\nAfter."),
    ("", None, "> " + style.MODERN_WAY + " Put $b$ here.\n"),
    ("", None, "- " + style.MODERN_WAY + " Put $b$ here.\n"),
    ("", None, style.MODERN_WAY + " Put $b$ here.\n| --- |\n"),
]
HEATHS = {"A", "B", "C"}
NAMES = style.modern_names(MODERN_PARAGRAPH)
MODERN_GOOD = ('<title>I.47: the modern way</title>'
               '<rect width="400" height="300" rx="10" fill="#fbf7ee"/>'
               '<line x1="40" y1="250" x2="360" y2="250" stroke="#3b2f2f" stroke-width="1.6"/>'
               '<polygon points="60,250 300,250 60,60" fill="#e9dcc0" fill-opacity="0.55" '
               'stroke="#a0522d" stroke-width="2.4"/>'
               '<g font-family="Georgia, serif" font-size="17" fill="#3b2f2f">'
               '<text x="50" y="270">A</text><text x="300" y="270">B</text>'
               '<text x="50" y="55">C</text>'
               '<text x="180" y="270" font-style="italic">c</text>'
               '<text x="200" y="140" font-style="italic">a² = b² + c²</text>'
               '<text x="70" y="290">(0, 0)</text></g>')
MODERN_CASES = [   # (a figure's inside, the title's ref, the finding wanted: rule, or None)
    (MODERN_GOOD, "I.47", None),
    (MODERN_GOOD, "I.48", "S24"),
    (MODERN_GOOD.replace("</title>", "</title><desc>A caption.</desc>"), "I.47", "S24"),
    (MODERN_GOOD.replace('fill="#e9dcc0"', 'fill="#f2b705"'), "I.47", "S24"),
    (MODERN_GOOD.replace('stroke-width="1.6"', 'stroke-width="0.8"'), "I.47", "S24"),
    (MODERN_GOOD.replace(">C<", ">D<"), "I.47", "S25"),
    (MODERN_GOOD.replace('<text x="50" y="270">A', '<text x="50" y="270" font-style="italic">A'),
     "I.47", "S25"),
    (MODERN_GOOD.replace('font-style="italic">c<', '>c<'), "I.47", "S25"),
    (MODERN_GOOD.replace(">c<", ">x<"), "I.47", "S25"),
    (MODERN_GOOD.replace(">c<", ">BC<"), "I.47", "S25"),
    (MODERN_GOOD.replace(">c<", ">c<tspan>₁</tspan><"), "I.47", "S25"),
    (MODERN_GOOD.replace(">c<", ">c∫<"), "I.47", "S25"),
    (MODERN_GOOD.replace('font-size="17"', 'font-size="14"'), "I.47", "S25"),
    (MODERN_GOOD.replace(' fill="#3b2f2f">', '>'), "I.47", "S24"),
    (MODERN_GOOD + '<polyline points="1,1 9,9 1,9" stroke="#8c7b62" stroke-width="1.3"/>',
     "I.47", "S24"),
    (MODERN_GOOD.replace(">a² = b² + c²<", ">a² =\n   b² + c²<"), "I.47", None),
    (MODERN_GOOD.replace(">c<", ">ϑ<"), "I.47", None),
    (MODERN_GOOD.replace(">c<", ">ν<"), "I.47", "S25"),
]


def modern_rules(inside: str, ref: str, heaths=HEATHS, names=NAMES,
                 viewbox="0 0 400 300") -> set[str]:
    """The rules S24 and S25 find broken in a figure of the modern way."""
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">'
                         f"{inside}</svg>")
    return {rule for rule, _ in style.modern_findings(root, ref, heaths, names)}


# ---------------------------------------------------------------------------------------
# The clearance cases: strokes and dots beside a letter, read as S26 reads a figure.
# (S26 is new: Argon's second review of the book-III release found seven letters of
# Euclid's figures crossed by strokes, and no rule then measured how near they came. A
# first review of S26 found it took a stroke's width at a transform's mean stretch, read a
# rect's rounded corners as square, drew a circle of no radius, placed an anchored label
# with a prime by its capital alone, and counted a letter drawn twice in one of several
# figures side by side as once in each; a second found a radius spelled 5e1 read as none,
# and a line of no length with butt caps read as drawn. Their admitted geometry or exact
# allow-list refusal has a case below. An
# independent review then found no case for an ellipse, a polyline, a dot or a stroke
# wholly within a letter, the canvas's right, top and foot, a letter's size or transform,
# or a prime, so that S26 could lose any of them and every case still pass; those cases
# are below too.)

LINE = '<line x1="100" y1="{y}" x2="200" y2="{y}" stroke="#3b2f2f" stroke-width="1.6"/>'
UPRIGHT_STROKE = '<line x1="{x}" y1="90" x2="{x}" y2="104" stroke="#3b2f2f" stroke-width="1.6"/>'
CLEAR_CASES = [   # (what is drawn beside a letter at (150, 100), at 17; the letter, its
                  # font-style and text-anchor; a finding?)
    (LINE.format(y=90), "A", "italic", "start", True),       # through the letter
    (LINE.format(y=110), "A", "italic", "start", False),     # 9 below its baseline
    (LINE.format(y=101.5), "A", "italic", "start", True),    # 1.5 below it: 0.7, less the width
    (LINE.format(y=101.5), "A", "normal", "start", True),
    (LINE.format(y=102.5), "A", "italic", "start", True),    # 2.5 below it: 1.7
    (LINE.format(y=103.5), "A", "italic", "start", False),   # 3.5 below it: 2.7
    ('<g stroke="#3b2f2f" stroke-width="4"><line x1="100" y1="103.5" x2="200" y2="103.5"/>'
     '</g>', "A", "italic", "start", True),                  # a width inherited: 1.5
    ('<line x1="100" y1="90" x2="200" y2="90" stroke="none"/>', "A", "italic", "start", False),
    ('<line x1="100" y1="90" x2="200" y2="90" stroke="#3b2f2f" stroke-dasharray="2 5"/>',
     "A", "italic", "start", True),
    ('<path d="M110,94 V150 H200 V94" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", False),
    ('<path d="M110,94 V150 H200 V94 Z" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", True),
    ('<circle cx="155" cy="94" r="30" fill="none" stroke="#8c7b62"/>',
     "A", "italic", "start", False),
    ('<circle cx="155" cy="94" r="6" fill="none" stroke="#8c7b62"/>',
     "A", "italic", "start", True),
    ('<ellipse cx="155" cy="94" rx="20" ry="4" fill="none" stroke="#8c7b62"/>',
     "A", "italic", "start", True),                          # an ellipse through it
    ('<ellipse cx="155" cy="94" rx="40" ry="30" fill="none" stroke="#8c7b62"/>',
     "A", "italic", "start", False),                         # and one round it
    ('<polyline points="140,94 170,94 170,140" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", True),                          # a polyline through it
    ('<polyline points="110,94 110,150 200,150 200,94" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", False),                         # open: no side along 94
    ('<polygon points="110,94 110,150 200,150 200,94" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", True),                          # closed: a side along 94
    # Wholly within an upright H, 4 or more from its hull's sides: a dot, a short stroke.
    ('<circle cx="157" cy="94" r="1" fill="#3b2f2f"/>', "H", "normal", "start", True),
    ('<line x1="155" y1="93" x2="158" y2="93" stroke="#3b2f2f" stroke-width="0.5"/>',
     "H", "normal", "start", True),
    ('<circle cx="155" cy="94" r="0" fill="none" stroke="#8c7b62"/>',
     "A", "italic", "start", False),                         # no radius: SVG draws nothing
    ('<circle cx="155" cy="94" r="0" fill="none" stroke="#8c7b62" stroke-linecap="round"/>',
     "A", "italic", "start", False),                         # whatever its caps
    ('<rect x="155" y="80" width="0" height="30" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", False),                         # no width: SVG draws nothing
    ('<rect x="150" y="100" width="100" height="100" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", True),                          # its corner at the letter
    ('<rect x="150" y="100" width="100" height="100" rx="50" fill="none" stroke="#3b2f2f"/>',
     "A", "italic", "start", False),                         # a circle, 12.9 clear
    ('<line x1="155" y1="94" x2="155" y2="94" stroke="#3b2f2f"/>',
     "A", "italic", "start", False),                         # no length, butt caps: nothing
    ('<line x1="155" y1="94" x2="155" y2="94" stroke="#3b2f2f" stroke-linecap="round"/>',
     "A", "italic", "start", True),                          # no length, round caps: a dot
    ('<circle cx="156" cy="104" r="2.6" fill="#3b2f2f"/>', "A", "italic", "start", True),
    ('<circle cx="156" cy="108" r="2.6" fill="#3b2f2f"/>', "A", "italic", "start", False),
    (LINE.format(y=114), "A", "italic", "start", False),
    ('<g transform="translate(0,-20)">' + LINE.format(y=114) + '</g>',
     "A", "italic", "start", True),
    # An E's top right corner stands 1.7 further right italic than upright.
    ('<line x1="163.5" y1="84" x2="163.5" y2="90" stroke="#3b2f2f" stroke-width="1.6"/>',
     "E", "italic", "start", True),
    ('<line x1="163.5" y1="84" x2="163.5" y2="90" stroke="#3b2f2f" stroke-width="1.6"/>',
     "E", "normal", "start", False),
    # Anchored at its middle or its end, the letter stands left of x; a prime after it
    # moves it further, by the prime's advance, 5.5 at 17.
    (UPRIGHT_STROKE.format(x=145), "A", "italic", "middle", True),
    (UPRIGHT_STROKE.format(x=145), "A", "italic", "start", False),
    (UPRIGHT_STROKE.format(x=135), "A", "italic", "end", True),
    (UPRIGHT_STROKE.format(x=135), "A", "italic", "start", False),
    (UPRIGHT_STROKE.format(x=132), "A′", "italic", "end", True),
    (UPRIGHT_STROKE.format(x=132), "A", "italic", "end", False),
]
CLEAR_REFUSAL_CASES = [   # (excluded drawing, element, attribute, value)
    ('<line x1="100" y1="103.5" x2="200" y2="103.5" '
     'style="stroke:#3b2f2f;stroke-width:4"/>',
     "line", "style", "stroke:#3b2f2f;stroke-width:4"),
    ('<rect x="150" y="100" width="100" height="100" rx="5e1" fill="none" '
     'stroke="#3b2f2f"/>', "rect", "rx", "5e1"),
    ('<g transform="scale(1,4)"><line x1="100" y1="26" x2="200" y2="26" '
     'stroke="#3b2f2f" stroke-width="1.6"/></g>', "g", "transform", "scale(1,4)"),
    ('<g transform="scale(1,4)"><circle cx="156" cy="26.25" r="1" '
     'fill="#3b2f2f"/></g>', "g", "transform", "scale(1,4)"),
]
EDGE_CASES = [   # (a letter A's x and y; a finding?)
    (1, 100, True),         # by the left edge
    (390, 100, True),       # by the right: it ends at 400.9
    (150, 13, True),        # by the top: its apex at 1.1
    (150, 299, True),       # by the foot: 1 above it
    (150, 100, False),
]
TWICE_CASES = [   # (the x of each letter A, at y 100; the cuts between figures side by
                  # side; a finding?)
    ((150,), (), False),
    ((60, 180), (), True),
    ((60, 300), (200,), False),         # once in each of two figures
    ((60, 120, 300), (200,), True),     # twice in the first
    ((60,), (64,), True),               # across the cut
]


def s26_findings(drawn: str, letters: str, cuts: tuple[float, ...] = ()) -> list[str]:
    """S26's findings on a parchment canvas with `drawn` and `letters` on it."""
    root = ET.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" font-family="Georgia">'
        f'<rect width="400" height="300" fill="#fbf7ee"/>{drawn}{letters}</svg>')
    before = len(style.failures)
    style.one_letter_one_point(style.ROOT / "figures" / "case.svg", root, cuts)
    found = [msg for rule, _, _, msg in style.failures[before:] if rule == "S26"]
    del style.failures[before:]
    return found


def letter(s: str, x: float = 150, y: float = 100, font_style: str = "italic",
           anchor: str = "start", size: float = 17) -> str:
    return (f'<text x="{x}" y="{y}" font-size="{size:g}" font-style="{font_style}" '
            f'text-anchor="{anchor}">{s}</text>')


def figure_fixture(idea: bool):
    """A fixed canvas, three labels and a short stroke for the complete figure checks."""
    ink, size = ("#222222", 14) if idea else ("#3b2f2f", 17)
    title = "I.1 at a glance" if idea else "Euclid I.1: three labels"
    desc = "<desc>A short stroke [black].</desc>" if idea else ""
    cx, cy = (200, 52) if idea else (194, 54)
    ex, ey = (363, 155.6) if idea else (353, 156)
    anchor = "middle" if idea else "start"
    return ET.fromstring(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" font-family="Georgia">'
        f'<title>{title}</title>{desc}'
        '<rect width="400" height="300" rx="10" fill="#fbf7ee"/>'
        f'<line x1="145" y1="150" x2="165" y2="150" stroke="{ink}" stroke-width="1.6"/>'
        f'<g fill="{ink}">'
        + letter("A", x=132, y=172, font_style="normal", size=size, anchor=anchor)
        + letter("C", x=cx, y=cy, font_style="normal", size=size, anchor=anchor)
        + letter("E", x=ex, y=ey, font_style="normal", size=size, anchor=anchor)
        + '</g></svg>')


def svg_sub(parent, name, attrib=None, **extra):
    qualified = name if name.startswith("{") else style.SVG + name
    return ET.SubElement(parent, qualified, {} if attrib is None else attrib, **extra)


def svg_element(markup):
    root = ET.fromstring(markup)
    for el in root.iter():
        if not el.tag.startswith("{"):
            el.tag = style.SVG + el.tag
    return root


def figure_findings(root, idea: bool):
    """Both complete checks, with a fixed figure and its fixed set of Heath's letters."""
    path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
    with patch.object(style, "svg_root", return_value=root), \
            patch.object(style, "drawn_letters", return_value={"A", "C", "E"}), \
            patch.object(style, "heath_letters", return_value={"A", "C", "E"}), \
            patch.object(style, "failures", []), \
            patch.object(style, "reports", defaultdict(list)):
        if idea:
            style.check_idea(path, "I.1", True)
        else:
            style.check_euclid(path, "I.1")
        return list(style.failures)


def figure_run(first, idea: bool, reference: bytes | None = None):
    """Parse a bad figure, then a distinct collision, through the production file loop.
    `reference` instead puts bad bytes in the Euclid figure read by an idea's S20."""
    with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
        root = Path(tmp)
        folder = root / "figures" / "I"
        folder.mkdir(parents=True)
        suffix = "-idea.svg" if idea else ".svg"
        path = folder / ("01" + suffix)
        raw = first if isinstance(first, bytes) else ET.tostring(first)
        path.write_bytes(raw)
        if idea:
            (folder / "01.svg").write_bytes(
                reference if reference is not None else ET.tostring(figure_fixture(False)))
            (folder / "02.svg").write_bytes(ET.tostring(figure_fixture(False)))
        second = figure_fixture(idea)
        e = next(el for el in second.iter() if style.text_of(el) == "E")
        e.set("x", "0")
        e.set("text-anchor", "end")
        (folder / ("02" + suffix)).write_bytes(ET.tostring(second))
        stack.enter_context(patch.object(style, "ROOT", root))
        stack.enter_context(patch.object(style, "books_with_pages", return_value=["I"]))
        stack.enter_context(patch.object(style, "heath_letters", return_value={"A", "C", "E"}))
        stack.enter_context(patch.object(style, "failures", []))
        stack.enter_context(patch.object(style, "reports", defaultdict(list)))
        stack.enter_context(patch.object(style, "italic_figures",
                                        defaultdict(lambda: defaultdict(list))))
        style.check_figures(True)
        return list(style.failures)


PLACE_CASES = [   # (what is drawn; the letters, as markup; a finding?)
    # At 17 an A's apex stands 1.3 from a line at 86, its width taken off; at 14, 3.4.
    (LINE.format(y=86), letter("A"), True),
    (LINE.format(y=86), letter("A", size=14), False),
    # A transform on the letter moves it: up 20, onto the line at 90.
    (LINE.format(y=90), '<g transform="translate(0,-20)">' + letter("A", y=120) + "</g>",
     True),
    (LINE.format(y=90), letter("A", y=120), False),
    # A and A′ name two points, each drawn once; A′ drawn twice is a repeat.
    ("", letter("A", x=60) + letter("A′", x=300), False),
    ("", letter("A′", x=60) + letter("A′", x=300), True),
]

KIND_CASES = [   # (a line drawn through a letter A at (150, 100); what S26 calls it)
    ('<line x1="100" y1="90" x2="200" y2="90" stroke="#3b2f2f" stroke-dasharray="2 5"/>',
     "a dashed line"),
    ('<g stroke-dasharray="2 5"><line x1="100" y1="90" x2="200" y2="90" stroke="#3b2f2f"/>'
     '</g>', "a dashed line"),                               # dashed by its group
    ('<line x1="100" y1="90" x2="200" y2="90" stroke="#3b2f2f" stroke-dasharray="none"/>',
     "a line"),                                              # none: drawn solid
]


# ---------------------------------------------------------------------------------------
# The scope cases (#66). (S7 and S12 once skipped the review notes, the reports, the front
# pages and the rendered docstrings, and let "Definition 8" and `hnearer` onto the pages.)

SAMPLE_RECORD = """# review/I/99.toml: a comment no page shows, `hX : T` and Definition 8 in it
[statement]
scope = "restricted"
hypotheses = ["the arms not in one straight line (`hX : ¬ Collinear A B C`)"]
note = "As Definition 8 asks."
short = "arms not in one straight line"

[[passage]]
at = "as Definition 8 says"
kind = "helper"
helper = "Prop9.apart"
note = "By \\"Definition 15\\" in quotation marks, and `Prop9.apart`."

[figure]
case = "D on the side of Definition 3"
"""

SAMPLE_TACIT = """/-! The transfer rules: Definition 15 here is in no page. -/
namespace Elements.Tacit
/-- A point at the radius is on the circle
(the half Definition 15 does not give). -/
axiom on_circle : True
end Elements.Tacit
"""


def note_lines(raw: str, rule, *, names: bool = False) -> list[int]:
    """The lines of the review notes of `raw` in which `rule` finds something, read as
    check_text reads a note for S7 (outside quotations and square brackets), or, with
    `names`, in which S12 finds a name."""
    out = []
    for note in style.review_texts(raw):
        read = style.SQUARE.sub(style._blank, style.blank_quotes(style.blank_code(
            style.straighten(note.text))))
        m = None if names else rule.search(read)
        if names:
            out.extend(note.line_at(use.at) for use in style.lean_name_occurrences(note.text))
        elif m:
            out.append(note.line_at(m.start()))
    return out


SAMPLE_TOML_EDGES = """[statement]
scope = "restricted" # "As Definition 8 says." in a comment
note = \"\"\"
The first line,
then Definition 8.\"\"\"
short = "As Definition 8 says."
hypotheses = ["one\\nDefinition 9"]
"""

SAMPLE_TOML_MORE = """[statement]
note = \"\"\"Note

that one is \\
  given.\"\"\"
short = \"\"\"As Definition 8 says, "so\"\"\"\"\"
"""

SAMPLE_TOML_DUPLICATES = """[statement]
scope = "partial"
omitted = ["Definition 8"]
note = "Definition 8"
hypotheses = [
  "Definition 8",
  "Definition 8",
]
short = "partial"

[[passage]]
at = "Definition 8"
kind = "helper"
helper = "Prop1.first"
note = "Definition 8"

[[passage]]
at = "Definition 8"
kind = "helper"
helper = "Prop1.second"
note = "Definition 8"
"""


def lean_note_findings(src: str, rendered=(), lines: bool = False) -> list:
    """The failures and reports of check_lean_notes on a Lean source, as a file of the
    foundations, with `rendered` its rendered docstrings, (axiom, doc) each, or, with
    `lines`, each failure as (rule, line); the script's own lists are left as they were."""
    saved = (list(style.failures), dict(style.reports))
    try:
        style.failures.clear()
        style.reports.clear()
        docs = []
        for name, doc in rendered:
            line = next(k for k, l in enumerate(src.splitlines(), 1) if f"axiom {name}" in l)
            span = style.docstring_span(src, line, doc)
            docs.append(style.Rendered(name, *span, doc))
        style.check_lean_notes(style.ROOT / "Elements" / "Foundations" / "Sample.lean", src,
                               docs)
        if lines:
            return sorted((r, line) for r, _, line, _ in style.failures)
        return sorted([r for r, *_ in style.failures] + [r for r in style.reports])
    finally:
        style.failures[:] = saved[0]
        style.reports.clear()
        style.reports.update(saved[1])


def s12_asks(texts, audit_built: bool):
    """What s12_plan asks of Lean: the names of its old groups and of its new ones, the
    audit lemmas left unchecked and the words of NOT_DECLARED in use."""
    old, new, unchecked, used = style.s12_plan(texts, audit_built)
    return (sorted(n for g in old.values() for n in g), sorted(n for g in new.values() for n in g),
            unchecked, sorted(used))


MISHNAH = style.ROOT / "mishnah" / "I" / "99.md"
CATALOGUE = style.REPORTS_DIR / "overlaps.md"


def s22(text: str) -> list[str]:
    """What S22 finds in a text: each code span of letters alone."""
    return [style.flat(m.group(1))
            for m in style.LETTERS_IN_CODE.finditer(style.letter_spans(text))]


def main_named_records() -> list[style.NamedText]:
    """The records main gives S12, with other checks replaced by stubs."""
    captured = []

    def remember(texts):
        captured.extend(texts)
        return 0, []

    with ExitStack() as stack:
        for name in ("check_text", "check_mishnah", "check_reading", "check_intros",
                     "check_figures"):
            stack.enter_context(patch.object(style, name))
        stack.enter_context(patch.object(style, "check_lean_notes", return_value=[]))
        stack.enter_context(patch.object(style, "rendered_docstrings", return_value={}))
        stack.enter_context(patch.object(style, "check_lean_names", side_effect=remember))
        stack.enter_context(patch.object(style, "reach_done", return_value=[]))
        stack.enter_context(patch.object(style.shutil, "which", return_value="lake"))
        stack.enter_context(patch.object(sys, "argv", ["check_style.py"]))
        with redirect_stdout(StringIO()):
            style.main()
    return captured


def main_named_texts() -> dict[Path, str]:
    """The paths and namespaces main gives S12."""
    return {text.path: text.opens for text in main_named_records()}


def failure_lines(text: str, rule: str) -> list[int]:
    """The lines at which check_text fails `rule` in a prose text."""
    saved = (list(style.failures), dict(style.reports), set(style.reach_found))
    try:
        style.failures.clear()
        style.reports.clear()
        style.reach_found.clear()
        style.check_text(MISHNAH, text, {"prose"})
        return [line for found, _, line, _ in style.failures if found == rule]
    finally:
        style.failures[:] = saved[0]
        style.reports.clear()
        style.reports.update(saved[1])
        style.reach_found.clear()
        style.reach_found.update(saved[2])


def lean_failure(text: str, line_at=None) -> list[tuple[int, bool]]:
    """The line and binder hint of an S12 failure returned by Lean for `text`."""
    saved = (list(style.failures), dict(style.reports), style.subprocess.run)

    def reject(args, **_):
        probe = Path(args[-1])
        line = next(k for k, value in enumerate(probe.read_text().splitlines(), 1)
                    if value.startswith("#check"))
        return SimpleNamespace(returncode=1, stdout="",
                               stderr=f"{probe.name}:{line}:1: error: unknown identifier")

    try:
        style.failures.clear()
        style.reports.clear()
        style.subprocess.run = reject
        named = style.NamedText(MISHNAH, text, "Elements", held=True, line_at=line_at)
        old, _, _, _ = style.s12_plan([named], False)
        style.lean_probe(old, ["Elements"])
        return [(line, "Hypotheses in words" in message)
                for rule, _, line, message in style.failures if rule == "S12"]
    finally:
        style.failures[:] = saved[0]
        style.reports.clear()
        style.reports.update(saved[1])
        style.subprocess.run = saved[2]


def review_s12_failures(raw: str) -> list[tuple[int, str]]:
    """The S12 failures after known names in reader-visible review fields pass Lean."""
    saved = (list(style.failures), dict(style.reports), set(style.reach_found),
             style.subprocess.run)
    path = style.ROOT / "review" / "I" / "99.toml"
    try:
        style.failures.clear()
        style.reports.clear()
        style.reach_found.clear()
        notes = style.review_texts(raw)
        named = [style.NamedText(path, note.text, style.book_opens("I"),
                                 line_at=note.line_at,
                                 hypothesis=note.key == "statement.hypotheses")
                 for note in notes]
        _, new, _, _ = style.s12_plan(named, False)
        style.subprocess.run = lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout="", stderr="")
        style.lean_probe(new, ["Elements"])
        return [(line, message) for rule, _, line, message in style.failures if rule == "S12"]
    finally:
        style.failures[:] = saved[0]
        style.reports.clear()
        style.reports.update(saved[1])
        style.reach_found.clear()
        style.reach_found.update(saved[2])
        style.subprocess.run = saved[3]


def spans_of(src: str, line: int, doc: str) -> str | None:
    """The text of the docstring `docstring_span` finds above line `line`, or None."""
    span = style.docstring_span(src, line, doc)
    return src[span[0]:span[1]] if span else None


SCOPE_CASES = [   # (rule, its reading, the text, what it should give)
    ("S12", style.lean_names, "(`hBCE : Between B C E`)", ["hBCE"]),
    ("S12", style.lean_names, "(`h₁ : Triangle A₁ A₂ A₄`)", ["h₁"]),
    ("S12", style.lean_names, "as in I.5 (`Prop5.base`)", ["Prop5.base"]),
    ("S12", style.lean_names, "(`Between B C E`)", []),
    ("S12", style.lean_names, "(`∠ A B C`)", []),
    ("S12", style.lean_names, "`x := 1`", []),
    ("S12", style.lean_names, "(`hBCE:Between B C E`, `hBCE' : P`)", ["hBCE", "hBCE'"]),
    ("S12", style.lean_names, "`a :: l`", []),
    ("S12", style.lean_names, "the edition at `https://example.org/x`", []),
    ("S12", style.lean_names, r"`not\` `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "`x\n2. y` `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "`x\n01. y` `Missing.name`", []),
    ("S12", style.lean_names, "`x\n1. \n` `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "[x](https://example.test/`) visible `Missing.name`",
     ["Missing.name"]),
    ("S12", style.lean_names, "[x](/my `Missing.name`)", ["Missing.name"]),
    ("S12", style.lean_names, "[x]( \"a `Missing.name` b\")", ["Missing.name"]),
    ("S12", style.lean_names, r"[x](a\ `Missing.name`)", ["Missing.name"]),
    ("S12", style.lean_names, "[x](/u (a(b `Missing.name`))", ["Missing.name"]),
    ("S22", s22, "[x](/my `AB`)", ["AB"]),
    ("S12", style.lean_names, "[x](<https://example.test/`>) visible `Missing.name`",
     ["Missing.name"]),
    ("S12", style.lean_names, "[x](<bad<url `Missing.name`>)", ["Missing.name"]),
    ("S12", style.lean_names, "[x](/my \"title`\") visible `Missing.name`",
     ["Missing.name"]),
    ("S12", style.lean_names, "[x]: https://example.test/`\nvisible `Missing.name`",
     ["Missing.name"]),
    ("S12", style.lean_names, "Foo\n[x]: /baz`\nvisible `Missing.name`", ["visible"]),
    ("S12", style.lean_names, "[x]: /baz extra`\nvisible `Missing.name`", ["visible"]),
    ("S12", style.lean_names,
     "[x]: /one\n[y]: https://example.test/`\nvisible `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "[x]: /url\n \"title `Missing.name`\"", []),
    ("S12", style.lean_names, "[x]: /url\n 'title `Missing.name`'", []),
    ("S12", style.lean_names, "[x]: /url\n (title `Missing.name`)", []),
    ("S12", style.lean_names,
     "[x]: /url\n \"title `Missing.name`\" trailing", ["Missing.name"]),
    ("S12", style.lean_names, r"[x]: a\ `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "<https://example.test/`> visible `Missing.name`",
     ["Missing.name"]),
    ("S12", style.lean_names, r"\<https://x/`Missing.name`>", ["Missing.name"]),
    ("S12", style.lean_names, r"\\<https://x/`Missing.name`>", []),
    ("S12", style.lean_names, "``[x](url`)`` `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "[x `](url`) visible `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "[see `foo](bar)` and `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "`[` x](<u`Missing.name`>)", ["Missing.name"]),
    ("S12", style.lean_names,
     "[outer [inner](url)](bad `Missing.name`)", ["Missing.name"]),
    ("S12", style.lean_names,
     "[outer [inner](url)](bad`Missing.name`)", ["Missing.name"]),
    ("S12", style.lean_names,
     "![outer [inner](url)](bad`Missing.name`)", []),
    ("S12", style.lean_names,
     "[outer ![inner](url)](bad`Missing.name`)", []),
    ("S22", lambda t: [content for _, _, content in style.markdown_code_spans(t)],
     "[see `foo](bar)` and `Missing.name`", ["foo](bar)", "Missing.name"]),
    ("S22", s22, "[`AB](x)` `CD`", ["CD"]),
    ("S12", style.lean_names, "`Missing.name'`", ["Missing.name'"]),
    ("S12", style.lean_names, "`Missing'.name'`", ["Missing'.name'"]),
    ("S12", style.lean_names, "'the `foo` 's", ["foo"]),
    ("S12", style.lean_names, "`Missing.name\n1. `", []),
    ("S12", style.lean_names, "2. `Missing.name\n3. `", []),
    ("S12", style.lean_names,
     "<!-- old: `Missing.name` --> visible `Prop5.base`", ["Prop5.base"]),
    ("S12", style.lean_names, "<!-- old: `Missing.name`", []),
    ("S12", style.lean_names, "`<!--` visible `Prop5.base`", ["Prop5.base"]),
    ("S12", style.lean_names,
     "> <!-- old:\n> `Missing.name`\nvisible `Prop5.base`", ["Prop5.base"]),
    ("S12", style.lean_names,
     "- <!-- old:\n  `Missing.name`\nvisible `Prop5.base`", ["Prop5.base"]),
    ("S12", lean_failure,
     "<!-- `Missing.name : T` -->\nvisible `Missing.name`", [(2, False)]),
    ("S12", lambda text: lean_failure(text, lambda at: 40 + style.line_of(text, at)),
     "<!-- `Missing.name` -->\nvisible `Missing.name : T`", [(42, True)]),
    ("S12", lean_failure,
     "> <!-- old:\n> `Missing.name : T`\nvisible `Missing.name`", [(3, False)]),
    # A comment and a code span are read in source order: the first to open hides the
    # other's markers inside it.
    ("S12", style.lean_names, "Prefix <!-- `old --> visible `Missing.name`", ["Missing.name"]),
    ("S12", lean_failure, "Prefix <!-- `old -->\nvisible `Missing.name`", [(2, False)]),
    ("S12", style.lean_names, "`<!--` visible `Prop5.base` -->", ["Prop5.base"]),
    ("S12", style.lean_names, "a <!-- `x` --> b `Prop5.base` <!-- `Missing.name` -->",
     ["Prop5.base"]),
    ("S12", style.lean_names, "an unclosed <!-- `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "\\<!-- `Missing.name` -->", ["Missing.name"]),
    ("S12", style.lean_names, "> a <!-- x\n> `y` --> `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "text <!-- a\n\n`b` --> `Missing.name`", ["b", "Missing.name"]),
    ("S7", lambda t: failure_lines(t, "S7"), "Prefix <!-- `old --> Definition 8 `x`", [1]),
    ("S22", lambda t: failure_lines(t, "S22"), "Before <!-- `x -->\n`AB`", [2]),
    ("S7", lambda t: failure_lines(t, "S7"), "<!-- hidden\n--> Definition 8", [2]),
    ("S22", style.blank_html_comments, "> a <!-- x\n> `y` --> `AB`",
     "> a       \n>         `AB`"),
    # A comment's quotation is no string; a multi-line string starts below its quotes;
    # an escaped line break in a one-line string reads as a space.
    ("S7", lambda raw: note_lines(raw, style.DEFINITION), SAMPLE_TOML_EDGES, [5, 6, 7]),
    ("S7", lambda raw: [note.text for note in style.review_texts(raw)
                        if note.key == "statement.hypotheses"], SAMPLE_TOML_EDGES,
     ["one\nDefinition 9"]),
    # A line break after a backslash, and quotation marks before the closing three.
    ("S4", lambda raw: note_lines(raw, style.HEDGE), SAMPLE_TOML_MORE, []),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION), SAMPLE_TOML_MORE, [6]),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION), SAMPLE_TOML_DUPLICATES,
     [4, 6, 7, 15, 21]),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION),
     '[statement]\nnote = """\\\nDefinition 3."""\n', [3]),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION),
     '[statement]\nnote = """before \\\n  Definition 8"""\n', [3]),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION),
     "[statement]\nnote = '''\nbefore\nDefinition 9'''\n", [4]),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION),
     '[statement]\nnote = "before\\nDefinition 10"\n', [2]),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION),
     "[statement]\nnote = 'Definition 11'\n", [2]),
    ("S7", lambda raw: style.review_texts(raw), "statement = 1\nfigure = [1]\n", []),
    ("S7", lambda raw: style.review_texts(raw, terms=True), "tag = 1\n", []),
    # The mishnah is asked as before: every name, with Elements alone.
    ("S12", lambda ts: s12_asks(ts, False),
     [style.NamedText(MISHNAH, "`direct_axioms`, `Audit.x`, `hX : T`", "E", held=True)],
     (["Audit.x", "direct_axioms", "hX"], [], [], ["direct_axioms"])),
    ("S12", lambda ts: s12_asks(ts, False),
     [style.NamedText(CATALOGUE, "`direct_axioms`, `Audit.x`, `Prop5.base`", "E")],
     ([], ["Prop5.base"], ["Audit.x"], ["direct_axioms"])),
    ("S12", lambda ts: s12_asks(ts, True),
     [style.NamedText(CATALOGUE, "`Audit.x`", "E")], ([], ["Audit.x"], [], [])),
    # Every rule of the Lean notes reads all of them, the rendered docstrings among them,
    # and S6 and S7 read a rendered docstring as the pages show it.
    ("S4", lean_note_findings, "/- Note -/\n/-- that it lies on a line. -/\naxiom a : True\n",
     ["S4"]),
    ("S4", lambda src: lean_note_findings(src, [("a", "that it lies on a line.")]),
     "/- Note -/\n/-- that it lies on a line. -/\naxiom a : True\n", ["S4"]),
    ("S6", lambda src: lean_note_findings(src, [("a", "A tacit assumption.")]),
     "/-- A tacit\n\nassumption. -/\naxiom a : True\n", ["S6"]),
    ("D10", lean_note_findings, "/-- A tacit\nassumption. -/\naxiom a : True\n", ["D10"]),
    ("D10", lambda src: lean_note_findings(src, [("a", "assumption here.")]),
     "/- A tacit -/\n/-- assumption here. -/\naxiom a : True\n", ["D10"]),
    ("D10", lambda src: lean_note_findings(src, [("a", "Apply `Definition 8`.")]),
     "/-- Apply `Definition\n8`. -/\naxiom a : True\n", []),
    ("S7", lambda src: lean_note_findings(src, [("a", "As Definition 8 says.")]),
     "/-- As Definition\n8 says. -/\naxiom a : True\n", ["S7"]),
    ("D10", lambda src: lean_note_findings(src, [("a", "A point exists.")]),
     "/- A tacit -/\n/-- A point exists. -/\naxiom a : True\n/- assumption -/\n", []),
    ("S7", lambda src: lean_note_findings(src, [("r", "A point at the radius is on the circle "
                                                     "(Definition 15).")], lines=True),
     "namespace Elements.Tacit\n/-- A point at the radius\nis on the circle (Definition 15). -/"
     "\naxiom r : True\n", [("S7", 3)]),
    ("S22", lean_note_findings, "/- `x -/\n/- `AB` -/\n", ["S22"]),
    ("D4", lambda t: style.lean_names(t, binders=False), "(`hBCE : Between B C E`)", []),
    ("S7", lambda raw: note_lines(raw, style.DEFINITION), SAMPLE_RECORD, [5, 15]),
    ("S12", lambda raw: note_lines(raw, None, names=True), SAMPLE_RECORD, [4, 12]),
    ("S7", lambda raw: [note.key for note in style.review_texts(raw)], SAMPLE_RECORD,
     ["statement.hypotheses", "statement.note", "statement.short", "passage.note",
      "figure.case"]),
    ("S7", lambda raw: style.review_texts("not = [toml"), "", []),
    ("S7", lambda src: spans_of(src, 5, "A point at the radius is on the circle (the half "
                                "Definition 15 does not give)."), SAMPLE_TACIT,
     " A point at the radius is on the circle\n(the half Definition 15 does not give). "),
    ("S7", lambda src: spans_of(src, 5, "Another docstring."), SAMPLE_TACIT, None),
    ("S7", lambda src: spans_of(src, 2, "On one line."), "namespace Elements.Tacit\n"
     "/-- On one line. -/ axiom one : True\n", " On one line. "),
    ("S7", lambda src: spans_of(src, 2, "The transfer rules: Definition 15 here is in no "
                                "page."), SAMPLE_TACIT, None),
    ("S22", s22, "the straight line `PQ` and the circle `ABCD`", ["PQ", "ABCD"]),
    ("S22", s22, "`AB, CD` and `A′B′` and `A₁A₂`", ["AB, CD", "A′B′", "A₁A₂"]),
    ("S22", s22, "a lone letter `P`, the Lean's variable, and `M₁`", ["P", "M₁"]),
    ("S22", s22, "the copy `G E C'` of ABC", ["G E C'"]),
    ("S22", s22, "`∠ A B C`, `Prop5.base`, `Centre E ABCD`, `B ≠ C`, `hAB`", []),
    ("S22", s22, "`x` AB `y`", []),
    ("S22", s22, "`AB,CD` and ``AB`CD`` and `A\nB`", ["AB,CD", "A B"]),
    ("S22", s22, "the straight lines `AB,\nCD`", ["AB, CD"]),
    ("S22", s22, "> `AB,\n> CD`", ["AB, CD"]),
    ("S22", s22, "> `AB,\nCD`", ["AB, CD"]),
    ("S22", s22, "- `AB,\n  CD`", ["AB, CD"]),
    ("S22", lambda t: [content for _, _, content in style.markdown_code_spans(t)],
     "` AB,\nCD `", ["AB, CD"]),
    ("S22", lambda t: failure_lines(t, "S22"), "Before\n`AB,\nCD`", [2]),
    ("S22", lambda t: failure_lines(t, "S22"), "Before\n> `AB,\nCD`", [2]),
    ("S7", lambda t: failure_lines(t, "S7"),
     "plain `Definition\n8` text\nDefinition 9", [3]),
    ("S22", s22, "`AB\n# `CD`", ["CD"]),
    ("S22", s22, "# `AB\n`CD`", ["CD"]),
    ("S22", s22, "> `AB,\n# CD`", []),
    ("S22", s22, "`AB\n\n`EF`", ["EF"]),
    ("S22", s22, "\\`X and `AB`", ["AB"]),
    ("S22", s22, "```\n`AB`\n```\n`CD`", ["CD"]),
    ("S22", s22, "~~~\n`AB`\n~~~\n`CD`", ["CD"]),
    ("S12", style.lean_names, "    `Missing.name`", []),
    ("S12", style.lean_names, "\t`Missing.name`", []),
    ("S12", style.lean_names, "paragraph\n    `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "- paragraph\n      `Missing.name`", ["Missing.name"]),
    ("S12", style.lean_names, "- paragraph\n\n      `Missing.name`", []),
    ("S12", style.lean_names, ">     `Missing.name`", []),
    ("S12", style.lean_names, "> paragraph\n>     `Missing.name`", ["Missing.name"]),
    ("S22", s22, "> ```\n> `CD`\nordinary `AB`", ["AB"]),
    ("S22", lambda t: failure_lines(t, "S22"),
     "> ```\n> `CD`\nordinary `AB`", [3]),
    ("S22", s22, "> ```\n> hidden\n- `AB,\n- CD`", []),
    ("S22", s22, "- ```\n  `CD`\nordinary `AB`", ["AB"]),
    ("S22", s22, "H |\n--- |\n`AB\nCD`", []),
    ("S12", style.lean_names, "H |\n--- |\n`Missing.name\n`", []),
    ("S22", lambda t: [content for _, _, content in style.markdown_code_spans(t)],
     "A | B\n--- | ---\n`AB \\| CD` | `EF`", [r"AB \| CD", "EF"]),
    ("S22", lambda t: failure_lines(t, "S22"),
     "A | B\n--- | ---\nplain | `AB`", [3]),
    ("S12", style.lean_names,
     "A | B\n--- | ---\nok | ok | `Missing.name`", []),
    ("S12", style.lean_names,
     "A | B\n--- | ---\nok | `Missing.name` | ignored", ["Missing.name"]),
    ("S12", style.lean_names,
     "A | B\n--- | ---\n[x]: `Missing.name` | ok", ["Missing.name"]),
    ("S7", style.is_catalogue, style.REPORTS_DIR / "overlaps.md", True),
    ("S7", style.is_catalogue, style.REPORTS_DIR / "gaps-book-II.md", True),
    ("S7", style.is_catalogue, style.REPORTS_DIR / "gaps-book-I-supplement.md", True),
    ("S7", style.is_report, style.REPORTS_DIR / "read-through-01.md", True),
    ("S7", style.is_report, style.REPORTS_DIR / "gaps-book-II.md", False),
    ("S7", style.is_report, style.REPORTS_DIR / "outside-review-02.md", False),
    ("S7", style.is_report, style.REPORTS_DIR / "crew" / "voyage-01.md", False),
]


def reach_run(path, text: str, scopes: set[str], pending: str | None, new: bool, read):
    """What `read()` gives after check_text on `text`, as the file `path`, with that file
    listed in REACH_PENDING for the rules `pending`, or not listed; the script's own lists
    are left as they were."""
    saved = (list(style.failures), dict(style.reports), set(style.reach_found),
             dict(style.REACH_PENDING))
    try:
        style.failures.clear()
        style.reports.clear()
        style.reach_found.clear()
        style.REACH_PENDING.clear()
        if pending:
            style.REACH_PENDING[style.rel(path)] = (pending, "a test")
        style.check_text(path, text, scopes, new=new)
        return read()
    finally:
        style.failures[:] = saved[0]
        style.reports.clear()
        style.reports.update(saved[1])
        style.reach_found.clear()
        style.reach_found.update(saved[2])
        style.REACH_PENDING.clear()
        style.REACH_PENDING.update(saved[3])


def findings(path, text: str, scopes: set[str], *, pending: str | None, new: bool = False):
    """The failures and the D16 reports of check_text on `text`, as the file `path`, with
    that file listed in REACH_PENDING for the rules `pending`, or not listed."""
    return reach_run(path, text, scopes, pending, new, lambda: (
        sorted(r for r, *_ in style.failures),
        sorted(m.split(":")[0] for _, _, m in style.reports.get("D16", []))))


GAPS = style.REPORTS_DIR / "gaps-book-I.md"
REACH_TEXT = "As Definition 15 says \u2014 and `PQ`."
RECORD = style.ROOT / "review" / "I" / "99.toml"
ALL = "S1 S7 S22"
REACH_CASES = [   # (file, scopes, a new text?, the rules it is listed for, (failures, D16))
    # A gap catalogue was held to S1 before, and is still; S7 and S22 are the reach.
    (GAPS, {"catalogue"}, False, ALL, (["S1"], ["S22", "S7"])),
    (GAPS, {"catalogue"}, False, None, (["S1", "S22", "S7"], [])),
    # A review note is new: while its file is listed for every rule, every finding is
    # reported.
    (RECORD, {"review"}, True, ALL, ([], ["S1", "S22", "S7"])),
    (RECORD, {"review"}, True, None, (["S1", "S22", "S7"], [])),
    # The prose was held to all three before (S22 aside), listed or not.
    (style.ROOT / "mishnah" / "I" / "99.md", {"prose"}, False, ALL, (["S1", "S7"], ["S22"])),
    # A file listed for some rules is held at once to every other rule of the reach.
    (GAPS, {"catalogue"}, False, "S7", (["S1", "S22"], ["S7"])),
    (RECORD, {"review"}, True, "S12", (["S1", "S22", "S7"], [])),
    (style.ROOT / "Elements" / "Foundations" / "Sample.lean", {"lean"}, False, "S22",
     (["S1"], ["S22"])),
]
GAPS_REL = style.rel(GAPS)
DONE_CASES = [   # (a text of the gap catalogue, the rules it is listed for, --no-lean?, done)
    # Listed for two rules, with a finding of one: the other is done, and the entry is not.
    (REACH_TEXT, "S7 S12", False, [(GAPS_REL, ["S12"], False)]),
    # No finding of a rule it is listed for: the entry is done, though an em dash fails.
    ("Plain words \u2014 and more.", "S7 S22", False, [(GAPS_REL, ["S7", "S22"], True)]),
    # Under --no-lean S12 found nothing, so it is never done; S7 and S22 still are.
    ("Plain words.", "S12", True, []),
    ("Plain words.", "S22", True, [(GAPS_REL, ["S22"], True)]),
    ("Plain words.", "S7 S12", True, [(GAPS_REL, ["S7"], False)]),
]


# ---------------------------------------------------------------------------------------

class Phrases(unittest.TestCase):
    """The phrase cases, each put to its rule's search."""

    def test_phrase_cases(self):
        for rule, search, text, want in PHRASE_CASES:
            with self.subTest(rule=rule, text=text):
                self.assertEqual(bool(search(text)), want,
                                 f"{rule} {'misses' if want else 'wrongly finds'} {text!r}")

    test_phrase_cases.__doc__ = (f"The wording rules read {len(PHRASE_CASES)} wrapped and "
                                 "unwrapped phrases rightly")


class Tex(unittest.TestCase):
    """The TeX cases, each read as S10 reads a mishnah."""

    def test_tex_cases(self):
        for text, want in TEX_CASES:
            with self.subTest(text=text):
                self.assertEqual(bool(style.tex_findings(text)), want,
                                 f"S10 {'misses' if want else 'wrongly finds'} {text!r}")

    test_tex_cases.__doc__ = (f"S10 reads {len(TEX_CASES)} mishnahs on either side of "
                              "the modern way's $…$ rightly")


class Ink(unittest.TestCase):
    """The ink cases, each with each spelling of the wedge."""

    def test_ink_cases(self):
        for under, (x, y), ink, want in INK_CASES:
            for wedge in INK_WEDGES:
                drawn = under.format(wedge=wedge)
                with self.subTest(drawn=drawn, at=(x, y), ink=ink):
                    self.assertEqual(ink_finding(drawn, x, y, ink), want,
                                     f"S20 {'misses' if want else 'wrongly finds'} a letter "
                                     f"in {ink} at ({x:g}, {y:g}) on {drawn}")

    test_ink_cases.__doc__ = (f"S20 reads the ink of {len(INK_CASES) * len(INK_WEDGES)} "
                              "letters on angles' wedges rightly")


class Modern(unittest.TestCase):
    """The modern cases: the names a paragraph gives, and a figure of the modern way read
    against them and against its Euclid's figure's letters."""

    def test_companion_reader_refuses_internal_dtd(self):
        source = ET.tostring(figure_fixture(False))
        raw = b'<!DOCTYPE svg [<!ENTITY label "A">]>' + source.replace(b">A<", b">&label;<")
        self.assertIn(b">&label;<", raw)
        with tempfile.TemporaryDirectory() as tmp, patch.object(style, "failures", []):
            path = Path(tmp) / "01.svg"
            for encoding in ("utf-8", "utf-16", "utf-32-le", "utf-32-be"):
                with self.subTest(encoding=encoding):
                    path.write_bytes(raw.decode("ascii").encode(encoding))
                    self.assertIsNone(style.modern_drawn_letters(path))
                    with patch.object(ET, "XMLParser", side_effect=AssertionError("parser built")):
                        self.assertIsNone(style.modern_drawn_letters(path))
            self.assertEqual(style.failures, [])

    def test_companion_letter_keeps_internal_newline(self):
        euclid = (style.ROOT / "figures/I/01.svg").read_text(encoding="utf-8")
        modern = (style.ROOT / "figures/I/01-modern.svg").read_text(encoding="utf-8")
        paragraph = (style.ROOT / "mishnah/I/01.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            figures = root / "figures/I"
            figures.mkdir(parents=True)
            mishnah = root / "mishnah/I"
            mishnah.mkdir(parents=True)
            (mishnah / "01.md").write_text(paragraph, encoding="utf-8")
            path = figures / "01-modern.svg"
            path.write_text(modern.replace(">A<", ">A′<"), encoding="utf-8")
            for letter, expected in (
                    ("A′", []),
                    ("A\n′", [("S25", "letter A′ is not one Euclid's figure draws "
                               "(B, C, D, E)")])):
                with self.subTest(letter=letter):
                    (figures / "01.svg").write_text(
                        euclid.replace(">A<", f">{letter}<"), encoding="utf-8")
                    with patch.object(style, "ROOT", root), \
                            patch.object(style, "fail") as fail:
                        style.check_modern(path, "I.1")
                    self.assertEqual(
                        [(r, message) for r, _, _, message in
                         (call.args for call in fail.call_args_list)], expected)

    def test_modern_depth_is_bounded_before_recursive_helpers(self):
        self.assertEqual(self.check_refused_modern(
            MODERN_GOOD + "<g>" * 16 + "</g>" * 16), [])
        for depth in (17, 1100):
            with self.subTest(depth=depth):
                findings = self.check_refused_modern(
                    MODERN_GOOD + "<g>" * depth + "</g>" * depth)
                self.assertEqual(findings, [
                    ("S24", "modern figure nesting exceeds 16 levels below <svg>")])
        root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">'
                             + "<g>" * 1100 + "</g>" * 1100 + "</svg>")
        with patch.object(style, "walk", side_effect=AssertionError("recursive walk")):
            self.assertEqual(style.modern_svg_findings(root), [
                ("S24", "modern figure nesting exceeds 16 levels below <svg>")])

    def test_modern_text_requires_effective_font_family(self):
        bare = MODERN_GOOD.replace(' font-family="Georgia, serif"', "")
        findings = self.check_refused_modern(bare)
        self.assertEqual(len(findings), 6)
        self.assertTrue(all(r == "S25" and "font-family" in m for r, m in findings),
                        findings)
        for family in ("Georgia", "Georgia, serif", "Georgia, 'Times New Roman', serif"):
            for where in ("root", "group", "text"):
                with self.subTest(family=family, where=where):
                    attrs = f'font-family="{family}"'
                    body = (bare.replace("<g ", f"<g {attrs} ") if where == "group" else
                            bare.replace("<text ", f"<text {attrs} ") if where == "text"
                            else bare)
                    self.assertEqual(self.check_refused_modern(
                        body, root_attributes=attrs if where == "root" else ""), [])
        # A declaration on a sibling does not supply the unstyled text's family.
        findings = self.check_refused_modern(
            MODERN_GOOD + '<text font-size="17" fill="#3b2f2f">A</text>')
        self.assertEqual(len(findings), 1)
        self.assertIn("font-family", findings[0][1])
        self.assertEqual(self.check_refused_modern(
            MODERN_GOOD + '<text fill="#3b2f2f"> \t\r\n</text>'), [])

    def test_modern_character_references_are_refused_without_granting_names(self):
        for reference in ("&#x3c0;", "&#X3C0;", "&#960;", "&pi;", "&alpha;",
                          r"\&#x3c0;", r"\\&#x3c0;"):
            for name in ("x", "c", "π"):
                with self.subTest(reference=reference, name=name):
                    findings = self.check_refused_modern(
                        MODERN_GOOD.replace(">c<", f">{name}/3<"),
                        paragraph=MODERN_PARAGRAPH + " The turning angle is "
                        + reference + "/3.")
                    self.assertTrue(any(r == "S25" and "character reference" in m
                                        for r, m in findings), findings)
                    self.assertTrue(any(r == "S25" and f"{name} is no name" in m
                                        for r, m in findings), findings)
        # Literal π supplies π, and neither letter of a hexadecimal spelling.
        for name in ("π", "x", "c"):
            findings = self.check_refused_modern(
                '<title>I.47: the modern way</title>'
                '<text font-family="Georgia" font-size="17" font-style="italic" '
                f'fill="#3b2f2f">{name}/3</text>',
                paragraph=MW + "The turning angle is π/3.")
            self.assertEqual(findings, [] if name == "π" else [
                ("S25", f"<text>{name}/3</text>: {name} is no name of the page's modern way")])

    def test_modern_text_checks_raw_space_characters(self):
        for space in ("\u0085", "\u00a0", "\u1680", "\u2003", "\u2028", "\u2029",
                      "\u202f", "\u205f", "\u3000"):
            for old, new in ((">A<", f">{space}A{space}<"),
                             (">c<", f">c{space}/{space}3<"),
                             (">c<", f">{space}<")):
                with self.subTest(space=repr(space), text=new):
                    findings = self.check_refused_modern(MODERN_GOOD.replace(old, new))
                    self.assertTrue(any(r == "S25" and "holds" in m and repr(space) in m
                                        for r, m in findings), findings)
        for space in (" ", "\t", "\r", "\n", " \t\r\n "):
            with self.subTest(space=repr(space)):
                self.assertEqual(self.check_refused_modern(MODERN_GOOD.replace(
                    ">A<", f">{space}A{space}<").replace(">c<", f">c{space}/{space}3<")), [])

    def test_modern_intraword_emphasis_is_refused(self):
        for word in ("e*x*ponent", "e**x**ponent", "e***x***ponent",
                     "e[*x*](/reference)ponent"):
            for name in ("e", "x"):
                with self.subTest(word=word, name=name):
                    findings = self.check_refused_modern(
                        MODERN_GOOD.replace(">c<", f">{name}<"),
                        paragraph=MODERN_PARAGRAPH + " The " + word + " is positive.")
                    self.assertTrue(any(r == "S25" and "intraword emphasis" in m
                                        for r, m in findings), findings)
                    self.assertTrue(any(r == "S25" and f"{name} is no name" in m
                                        for r, m in findings), findings)
        for words in ("The *exponent* is positive.", "The **exponent** is positive.",
                      "The name *x* is given.", "The name **x** is given."):
            with self.subTest(words=words):
                self.assertEqual(style.modern_markup_findings(MW + words), [])
                self.assertEqual(style.modern_names(style.modern_paragraph(MW + words)),
                                 {"x"} if "name" in words else set())

    def test_modern_emphasis_through_punctuation_is_refused(self):
        for emphasis in ("*", "**", "***", "_", "__", "___"):
            for word, name in (
                    (f"A'{emphasis}s{emphasis}", "s"),
                    (f"A’{emphasis}s{emphasis}", "s"),
                    (f"{emphasis}A{emphasis}'s", "s"),
                    (f"{emphasis}A{emphasis}’s", "s"),
                    (f"e.{emphasis}g{emphasis}.", "g"),
                    (f"{emphasis}e{emphasis}.g.", "g"),
                    (f"i.{emphasis}e{emphasis}.", "e"),
                    (f"{emphasis}i{emphasis}.e.", "e"),
                    # Emphasis on both sides of the stop or the apostrophe, and a stop
                    # escaped, as Markdown shows it, a full stop (#172).
                    (f"{emphasis}e{emphasis}.{emphasis}g{emphasis}.", "e"),
                    (f"{emphasis}e{emphasis}.{emphasis}g{emphasis}.", "g"),
                    (f"{emphasis}i{emphasis}.{emphasis}e{emphasis}.", "i"),
                    (f"{emphasis}A{emphasis}'{emphasis}s{emphasis}", "s"),
                    (f"{emphasis}A{emphasis}’{emphasis}s{emphasis}", "s"),
                    (f"{emphasis}e{emphasis}\\.{emphasis}g{emphasis}\\.", "e"),
                    (f"e\\.{emphasis}g{emphasis}\\.", "g"),
                    (f"{emphasis}e{emphasis}\\.g\\.", "g")):
                with self.subTest(word=word):
                    findings = self.check_refused_modern(
                        MODERN_GOOD.replace(">c<", f">{name}<"),
                        paragraph=MODERN_PARAGRAPH + " Consider " + word)
                    self.assertTrue(any(r == "S25" and "intraword emphasis" in m
                                        for r, m in findings), findings)
                    self.assertTrue(any(r == "S25" and f"{name} is no name" in m
                                        for r, m in findings), findings)
        for words in ("The name *x*.", "The name _x_.", "The name '*x*'.",
                      "The name '_x_'.", "The name *x*. *Then* it is given."):
            with self.subTest(words=words):
                self.assertEqual(self.check_refused_modern(
                    MODERN_GOOD.replace(">c<", ">x<"),
                    paragraph=MODERN_PARAGRAPH + " " + words), [])

    def test_modern_invisible_characters_are_refused(self):
        # A format character (Unicode's Cf) shows nothing, so the reader sees one word,
        # e.g. or exponent, where the names would find a letter standing alone (#172);
        # nor do the rest of Unicode's default-ignorable characters, a Hangul filler (a
        # letter to Unicode), a variation selector or the grapheme joiner (marks to it).
        for invisible in ("​", "‍", "­", "⁠", "﻿", "ᅟ", "ㅤ", "ﾠ",
                          "️", "\U000e0100", "͏", "᠋"):
            for word, name in ((f"e{invisible}.g.", "g"), (f"e{invisible}xponent", "e")):
                with self.subTest(invisible=repr(invisible), word=word):
                    findings = self.check_refused_modern(
                        MODERN_GOOD.replace(">c<", f">{name}<"),
                        paragraph=MODERN_PARAGRAPH + " Consider the " + word + ".")
                    self.assertTrue(any(r == "S25" and "invisible character" in m
                                        and f"U+{ord(invisible):04X}" in m
                                        for r, m in findings), findings)
                    self.assertTrue(any(r == "S25" and f"{name} is no name" in m
                                        for r, m in findings), findings)
        # In code, which a reader sees as code and the names do not read, it is not refused.
        self.assertEqual(self.check_refused_modern(
            paragraph=MODERN_PARAGRAPH + " Code `e​.g.` here."), [])

    def test_modern_arcs_draw_as_arcs(self):
        # SVG omits an arc whose ends are one point and draws one with a radius of 0 as a
        # straight line (F.6.2), so the modern figures' language refuses both (#172).
        for value in ("M 0 0 A 0 1 0 0 0 2 2", "M 0 0 A 1 0 0 0 0 2 2",
                      "M 0 0 A -0 1 0 0 0 2 2", "M 2 2 A 1 1 0 0 0 2 2",
                      "M 0 0 L 2 2 A 1 1 0 1 1 2 2",
                      "M 0 0 A 1 1 0 0 0 2 2 L 3 3 A 1 1 0 0 1 3.0 3"):
            with self.subTest(path=value):
                findings = self.check_refused_modern(
                    MODERN_GOOD + f'<path d="{value}" fill="none"/>')
                self.assertTrue(any(r == "S24" and " d " in m and "<path>" in m
                                    for r, m in findings), findings)
        for value in ("M 0 0 A 1 1 0 1 1 9 0", "M 0 0 L 2 2 A 1 1 0 0 0 0 0 z"):
            with self.subTest(path=value):
                self.assertEqual(self.check_refused_modern(
                    MODERN_GOOD + f'<path d="{value}" fill="none"/>'), [])

    def test_modern_nested_svg_is_refused(self):
        for content in ('<line x2="20" stroke="#3b2f2f" stroke-width="1.6"/>',
                        '<text font-size="17" fill="#3b2f2f">A</text>'):
            with self.subTest(content=content):
                findings = self.check_refused_modern(
                    MODERN_GOOD + '<svg width="400" height="300" viewBox="0 0 40 30">'
                    + content + '</svg>')
                self.assertTrue(any(r == "S24" and "<svg>" in m for r, m in findings),
                                findings)

    def test_modern_marker_attributes_match_main(self):
        attributes = dict(id="head", viewBox="0 0 10 10", refX="9", refY="5",
                          markerWidth="5", markerHeight="5", orient="auto-start-reverse")
        for key, values in (
                ("markerUnits", ("strokeWidth",)),
                ("markerWidth", ("50", "5.0")),
                ("markerHeight", ("50", "5.0")),
                ("viewBox", ("0 0 1 1", "0 0 10.0 10")),
                ("refX", ("90", "9.0")), ("refY", ("50", "5.0")),
                ("orient", ("0",)), ("width", ("5",))):
            for value in values:
                with self.subTest(key=key, value=value):
                    changed = attributes | {key: value}
                    attrs = " ".join(f'{k}="{v}"' for k, v in changed.items())
                    findings = self.check_refused_modern(
                        MODERN_GOOD + f'<defs><marker {attrs}>'
                        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#8c7b62"/>'
                        '</marker></defs>')
                    self.assertTrue(any(r == "S24" and key in m and "<marker>" in m
                                        for r, m in findings), findings)

    def test_modern_markers_refuse_strokes_and_text(self):
        line = '<path d="M 0 0 L 10 5 L 0 10 z" fill="#8c7b62"/>'
        ink = 'stroke="#3b2f2f" stroke-width="1.6"'
        cases = [
            (line.replace("/>", f" {ink}/>"), ""),
            (f'<g {ink}>{line}</g>', ""),
            (line, ink),
            ('<g><text font-size="17" fill="#3b2f2f">A</text></g>', ""),
        ]
        for content, inherited in cases:
            with self.subTest(content=content, inherited=inherited):
                findings = self.check_refused_modern(
                    MODERN_GOOD + f'<defs {inherited}><marker id="head" '
                    'viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" '
                    'markerHeight="5" orient="auto-start-reverse">'
                    + content + '</marker></defs>')
                self.assertTrue(any(r == "S24" and "<marker>" in m for r, m in findings),
                                findings)

    def test_inline_links_preserve_visible_names_and_articles(self):
        cases = (
            ("a point reached", "[a point](../../book/I/01.md) reached", set()),
            ("a point reached", "[a](../../book/I/01.md) point reached", set()),
            ("AC = a", "AC = [a](../../book/I/01.md)", {"a"}),
            ("a + b", "[a + b](../../book/I/01.md)", {"a", "b"}),
            ("exponent", "e[x](../../book/I/01.md)ponent", set()),
            ("axis", "[a](../../book/I/01.md)xis", set()),
        )
        for plain, linked, expected in cases:
            for words in (plain, linked):
                with self.subTest(words=words):
                    paragraph = MW + words + "."
                    findings = self.check_refused_modern(
                        '<title>I.47: the modern way</title>'
                        '<text font-family="Georgia" font-size="17" font-style="italic" '
                        'fill="#3b2f2f">a</text>',
                        paragraph=paragraph)
                    self.assertEqual(findings, [] if "a" in expected else [
                        ("S25", "<text>a</text>: a is no name of the page's modern way")])
                    self.assertEqual(style.modern_names(style.modern_paragraph(paragraph)),
                                     expected)

    def test_modern_encoding_failures_continue(self):
        document = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
                    + MODERN_GOOD + '</svg>')
        for declaration, encoding in (("unknown-encoding", "utf-8"), ("UTF-7", "utf-7"),
                                       ("UTF-16", "utf-16"), ("UTF-16", "utf-16-le"),
                                       ("ISO-8859-1", "iso-8859-1")):
            with self.subTest(declaration=declaration, encoding=encoding):
                body = (document.replace("²", "2") if encoding == "utf-16-le" else
                        document.replace("</svg>", "<!-- café --></svg>"))
                source = f'<?xml version="1.0" encoding="{declaration}"?>' + body
                findings = self.check_refused_modern(figure_bytes=source.encode(encoding))
                self.assertTrue(any(r == "S24" and "encoding" in m for r, m in findings),
                                findings)

    def test_modern_dtd_and_entity_declarations_are_refused(self):
        document = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
                    + MODERN_GOOD + '</svg>')
        cases = (
            ('<!DOCTYPE svg [<!ENTITY title "I.47: the modern way">]>',
             document.replace("I.47: the modern way", "&title;")),
            ('<!DOCTYPE svg SYSTEM "figure.dtd">', document),
        )
        for declaration, body in cases:
            with self.subTest(declaration=declaration):
                findings = self.check_refused_modern(
                    figure_bytes=(declaration + body).encode("utf-8"))
                self.assertEqual(findings, [
                    ("S24", "unsupported DTD or entity declaration in a modern figure")])

    def test_modern_figure_is_read_once_as_bytes(self):
        opened = []
        original_open = io.open

        def record_open(file, mode="r", *args, **kwargs):
            if str(file).endswith("47-modern.svg") and "r" in mode:
                opened.append(mode)
            return original_open(file, mode, *args, **kwargs)

        with patch("builtins.open", side_effect=record_open), \
                patch("io.open", side_effect=record_open):
            self.assertEqual(self.check_refused_modern(), [])
        self.assertEqual(opened, ["rb"])

    def test_encoding_exceptions_from_checker_propagate(self):
        for error in (LookupError("checker defect"),
                      UnicodeDecodeError("utf-8", b"\xff", 0, 1, "checker defect"),
                      ValueError("checker defect")):
            for checker in ("modern_svg_findings", "modern_findings"):
                with self.subTest(error=type(error).__name__, checker=checker):
                    with patch.object(style, checker, side_effect=error):
                        with self.assertRaisesRegex(type(error), "checker defect"):
                            self.check_refused_modern()

    def test_names(self):
        for text, given, not_given in NAMES_CASES:
            with self.subTest(text=text):
                names = style.modern_names(text)
                self.assertLessEqual(given, names, f"modern_names misses {given - names}")
                self.assertFalse(names & not_given, f"modern_names wrongly gives {names & not_given}")

    def test_page_names(self):
        for text, given, not_given in PAGE_NAMES_CASES:
            with self.subTest(text=text):
                names = style.modern_names(style.modern_paragraph(text))
                self.assertLessEqual(given, names, f"the page's names miss {given - names}")
                self.assertFalse(names & not_given, f"the page wrongly gives {names & not_given}")

    def test_modern_cases(self):
        for inside, ref, want in MODERN_CASES:
            with self.subTest(figure=inside, ref=ref):
                found = modern_rules(inside, ref)
                if want is None:
                    self.assertEqual(found, set(), f"S24 and S25 wrongly find {found}")
                else:
                    self.assertIn(want, found, f"{want} misses a fault in {inside!r}")

    def test_font_style_presentation_under_italic_parent(self):
        letter = '<text x="50" y="270">A</text>'
        for element in ("text", "g"):
            for value in ("", " \t\n ", "normal"):
                with self.subTest(element=element, value=value):
                    if element == "text":
                        label = letter.replace("<text ", f'<text font-style="{value}" ')
                    else:
                        label = f'<g font-style="{value}">{letter}</g>'
                    inside = MODERN_GOOD.replace(
                        letter, f'<g font-style="italic">{label}</g>')
                    self.assertEqual(modern_rules(inside, "I.47"), {"S25"})

    def test_modern_gate_elements(self):
        for element in ("use", "image", "foreignObject", "switch", "animate", "set",
                        "symbol", "filter", "linearGradient", "script", "unknown"):
            with self.subTest(element=element):
                findings = self.check_refused_modern(MODERN_GOOD + f"<{element}/>")
                self.assertTrue(any("<" + element + ">" in m for _, m in findings), findings)
        for namespace in ("", "urn:other"):
            with self.subTest(namespace=namespace):
                findings = self.check_refused_modern(
                    MODERN_GOOD + f'<g xmlns="{namespace}"/>')
                self.assertTrue(any("<" in m and "g>" in m for _, m in findings), findings)

    def test_modern_gate_attributes_and_no_css(self):
        for attribute, value in (("display", "none"), ("visibility", "hidden"),
                                 ("opacity", "0"), ("class", "hidden"), ("href", "#head"),
                                 ("onload", "void(0)"), ("font-weight", "normal"),
                                 ("style", "fill: #3b2f2f; font-size: 17")):
            with self.subTest(attribute=attribute):
                findings = self.check_refused_modern(
                    root_attributes=f'{attribute}="{value}"')
                self.assertTrue(any(attribute in m and "<svg>" in m for _, m in findings),
                                findings)
        # Even a formerly supported style must be refused before the presentation walk.
        root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg" '
                             'viewBox="0 0 400 300" style="fill: #3b2f2f">'
                             + MODERN_GOOD + '</svg>')
        with patch.object(style, "style_of", side_effect=AssertionError("CSS was read")):
            self.assertTrue(style.modern_findings(root, "I.47", HEATHS, NAMES))

    def test_modern_gate_numeric_attributes(self):
        for attribute in ("x", "y", "x1", "x2", "y1", "y2", "cx", "cy", "r", "rx", "ry",
                          "width", "height", "fill-opacity", "markerWidth", "markerHeight",
                          "refX", "refY", "font-size", "stroke-width"):
            for value in ("17px", "17e0", ".17", "17.", " 17", "17 ", "1 7", "1_7",
                          "１７", "NaN", "Infinity", "inherit", "initial"):
                with self.subTest(attribute=attribute, value=value):
                    findings = self.check_refused_modern(
                        root_attributes=f'{attribute}="{value}"')
                    self.assertTrue(any(attribute in m and "<svg>" in m for _, m in findings),
                                    findings)
        # A long failing token guards the linear scan against ambiguous digit regexes.
        value = "1" * 100000 + "!"
        self.assertIsNone(style.modern_number(value))
        self.assertIsNone(style.modern_number("9" * 1000))
        for value in ("0", "-0", "+17", "0017", "17.0", "-0.55"):
            with self.subTest(value=value):
                self.assertEqual(style.modern_number(value), float(value))

    def test_modern_gate_number_lists(self):
        for attribute, values in (
                ("points", ("1e1,2 3,4", "1,2,3", "1,2, 3,4", "1,2 3", "1,2 rubbish")),
                ("viewBox", ("0 0 4e2 300", "0 0 400. 300", "0,,0,400,300")),
                ("stroke-dasharray", ("5px 4", "5e0 4", "5,,4", "5,", "5 -4", "5 4x"))):
            for value in values:
                with self.subTest(attribute=attribute, value=value):
                    kwargs = ({"viewbox": value} if attribute == "viewBox" else
                              {"root_attributes": f'{attribute}="{value}"'})
                    findings = self.check_refused_modern(**kwargs)
                    self.assertTrue(any(attribute in m and "<svg>" in m for _, m in findings),
                                    findings)
        for value in ("M 0 0 L 1e1 2", "M 0 0 h 10", "M 0 0 A 1 1 0 2 0 2 2",
                      "M 0 0 L 10 2 trailing"):
            with self.subTest(path=value):
                findings = self.check_refused_modern(
                    MODERN_GOOD + f'<path d="{value}" fill="none"/>')
                self.assertTrue(any(" d " in m and "<path>" in m for _, m in findings), findings)

    def test_modern_gate_transforms(self):
        for value in ("translate(1 2)", "scale(1)", "matrix(1 0 0 1 0 0)", "skewX(0)",
                      "rotate(1)", "rotate(1,2,3)", "rotate(1e0 2 3)", "rotate(.1 2 3)",
                      "rotate(1 2 3) ", "rotate(1 2 3) rotate(0 0 0)", "rotate(1 2 3)x"):
            with self.subTest(value=value):
                findings = self.check_refused_modern(
                    root_attributes=f'transform="{value}"')
                self.assertTrue(any("transform" in m and "<svg>" in m for _, m in findings),
                                findings)
        self.assertEqual(self.check_refused_modern(
            root_attributes='transform="rotate(-26.565051 190.538699 202.827398)"'), [])

    def test_modern_gate_keywords_and_colours(self):
        for attribute, other in (("fill", "#3B2F2F"), ("stroke", "currentColor"),
                                  ("font-family", "serif"), ("font-style", "oblique"),
                                  ("text-anchor", "end"), ("stroke-linejoin", "bevel"),
                                  ("markerUnits", "userspaceonuse"), ("orient", "auto"),
                                  ("marker-end", "url(#elsewhere)"), ("id", "elsewhere")):
            for value in (other, "inherit", "initial", "unset", "revert", "revert-layer"):
                with self.subTest(attribute=attribute, value=value):
                    findings = self.check_refused_modern(
                        root_attributes=f'{attribute}="{value}"')
                    self.assertTrue(any(attribute in m and "<svg>" in m for _, m in findings),
                                    findings)
        for attribute, value in (("text-anchor", "start"),
                                 ("stroke-dasharray", "5 4")):
            with self.subTest(attribute=attribute, value=value):
                self.assertEqual(self.check_refused_modern(
                    root_attributes=f'{attribute}="{value}"'), [])
        for attribute, value in (("fill", "black"), ("stroke", "none"),
                                 ("font-style", "normal"), ("stroke-linejoin", "miter"),
                                 ("markerUnits", "strokeWidth"), ("orient", "0"),
                                 ("marker-end", "none"), ("stroke-dasharray", "none")):
            with self.subTest(attribute=attribute, value=value):
                findings = self.check_refused_modern(
                    root_attributes=f'{attribute}="{value}"')
                self.assertTrue(any(attribute in message for _, message in findings), findings)

    def test_serialized_attribute_references_are_refused_before_xml_normalisation(self):
        for attribute, value in (("font-family", "&#71;eorgia"),
                                 ("font-style", "&#105;talic"),
                                 ("text-anchor", "&#x6d;iddle")):
            with self.subTest(attribute=attribute, value=value):
                findings = self.check_refused_modern(
                    root_attributes=f'{attribute}="{value}"')
                self.assertEqual(findings, [
                    ("S24", "unsupported character reference in a serialized attribute value")])
        self.assertEqual(self.check_refused_modern(
            MODERN_GOOD.replace(">c<", ">c &lt; 3<")), [])

    def test_modern_title_is_unique_and_direct(self):
        cases = (
            MODERN_GOOD + "<title>I.47: the modern way</title>",
            MODERN_GOOD + "<g><title>wrong</title></g>",
            MODERN_GOOD.replace("<title>I.47: the modern way</title>",
                                "<g><title>I.47: the modern way</title></g>"),
        )
        for inside in cases:
            with self.subTest(inside=inside):
                findings = self.check_refused_modern(inside)
                self.assertTrue(any(rule == "S24" and "exactly one directly" in message
                                    for rule, message in findings), findings)

    def test_no_paragraph_and_no_figure(self):
        self.assertIn("S24", modern_rules(MODERN_GOOD, "I.47", names=None))
        self.assertIn("S24", modern_rules(MODERN_GOOD, "I.47", heaths=None))
        for text, want in SPAN_CASES:
            with self.subTest(text=text):
                self.assertEqual(style.modern_paragraph(text), want)

    def test_malformed_modern_svg_is_s24(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-modern.svg"
            path.write_text("<svg>")
            with patch.object(style, "fail") as fail:
                self.assertIsNone(style.svg_root(path))
                fail.assert_called_once()
                self.assertEqual(fail.call_args.args[:3], ("S24", path, 0))
                self.assertIn("not well-formed SVG", fail.call_args.args[3])

    def test_canvas_widths(self):
        for width, valid in (("399", False), ("400", True), ("420", True),
                             ("440", True), ("441", False), ("invalid", False),
                             (".", False), ("400..0", False), ("400px", False),
                             ("nan", False), ("inf", False), ("1e999", False)):
            with self.subTest(width=width):
                found = modern_rules(MODERN_GOOD, "I.47", viewbox=f"0 0 {width} 300")
                self.assertEqual(found, set() if valid else {"S24"})
        for viewbox in ("0 0 400", "invalid 0 400 300", "0 0 400 invalid"):
            with self.subTest(viewbox=viewbox):
                self.assertEqual(modern_rules(MODERN_GOOD, "I.47", viewbox=viewbox),
                                 {"S24"})

    def test_canvas_heights(self):
        for height, valid in (("0", False), ("-0", False), ("-1", False),
                              ("-300", False), (".5", False), ("0.5", True), ("300", True)):
            with self.subTest(height=height):
                findings = self.check_refused_modern(viewbox=f"0 0 400 {height}")
                if valid:
                    self.assertEqual(findings, [])
                else:
                    message_part = "malformed or unsupported viewBox" if height == ".5" else "viewBox height"
                    self.assertTrue(any(r == "S24" and message_part in message
                                        for r, message in findings), findings)

    def test_explicit_root_dimensions_must_be_positive(self):
        for attribute in ("width", "height"):
            for value in ("0", "-0", "0.0", "-0.0", "-1", "-290"):
                with self.subTest(attribute=attribute, value=value):
                    attributes = {"width": "400", "height": "290"}
                    attributes[attribute] = value
                    findings = self.check_refused_modern(
                        viewbox="0 0 400 290",
                        root_attributes=" ".join(f'{key}="{v}"'
                                                 for key, v in attributes.items()))
                    self.assertEqual(findings, [
                        ("S24", f"root {attribute} {value!r}, not positive")])

    def test_positive_or_omitted_root_dimensions_are_allowed(self):
        for width in (None, "0.5", "400"):
            for height in (None, "0.5", "290"):
                with self.subTest(width=width, height=height):
                    self.assertEqual(self.check_refused_modern(
                        viewbox="0 0 400 290",
                        root_attributes=" ".join(
                            f'{key}="{value}"' for key, value in
                            (("width", width), ("height", height)) if value is not None)), [])

    def test_presentation_lengths_use_plain_decimals(self):
        letter = '<text x="50" y="270">A</text>'
        for attribute, size, parent, rule in (("font-size", "17", "40", "S25"),
                                               ("stroke-width", "2", "20", "S24")):
            values = [(value, True) for value in
                      (size, size + ".0", "+" + size)]
            values += [(value, False) for value in
                       (size + "px", size + ".0px", f".{size}e{len(size)}", size + "e0px",
                        size + ".", size + ".px", size + ".e0", size + "em",
                        size + "%", size + " px", size + "e", "", "\u00a0" + size)]
            for element in ("text", "g"):
                for inherited in (False, True):
                    for value, valid in values:
                        with self.subTest(attribute=attribute, element=element,
                                          inherited=inherited, value=value):
                            declaration = f'{attribute}="{value}"'
                            label = (letter.replace("<text ", f"<text {declaration} ")
                                     if element == "text"
                                     else f"<g {declaration}>{letter}</g>")
                            ink = 'stroke="#3b2f2f"' if attribute == "stroke-width" else ""
                            ancestor = f'{attribute}="{parent}"' if inherited else ""
                            inside = MODERN_GOOD.replace(
                                letter, f"<g {ink} {ancestor}>{label}</g>")
                            findings = self.check_refused_modern(inside)
                            if valid:
                                self.assertEqual(findings, [])
                            else:
                                self.assertTrue(any(r == rule and attribute in message
                                                    for r, message in findings), findings)

    def test_malformed_presentation_lengths_cannot_be_overridden(self):
        for attribute, value, rule in (("font-size", "17.", "S25"),
                                      ("stroke-width", "2.px", "S24")):
            with self.subTest(attribute=attribute):
                findings = self.check_refused_modern(
                    root_attributes=f'{attribute}="{value}"')
                self.assertTrue(any(r == rule and attribute in message
                                    for r, message in findings), findings)

    def test_font_family_and_weight_presentation(self):
        letter = '<text x="50" y="270">A</text>'
        for attribute, allowed, refused in (
                ("font-family", ("Georgia", "Georgia, serif",
                                 "Georgia, 'Times New Roman', serif"),
                 ("Arial", "serif", "Georgia, monospace")),
                ("font-weight", (), ("normal", "bold", "bolder", "400", "700"))):
            values = [(value, True) for value in allowed]
            values += [(value, False) for value in
                       refused + ("initial", "inherit", "unset", "revert", "", " \t\n ")]
            for element in ("svg", "g", "text"):
                for value, valid in values:
                    with self.subTest(attribute=attribute, element=element, value=value):
                        declaration = f'{attribute}="{value}"'
                        inside, root_attributes = MODERN_GOOD, ""
                        if element == "svg":
                            root_attributes = declaration
                        elif element == "g":
                            inside = inside.replace(letter, f"<g {declaration}><g>{letter}</g></g>")
                        else:
                            inside = inside.replace(letter, letter.replace(
                                "<text ", f"<text {declaration} "))
                        findings = self.check_refused_modern(
                            inside, root_attributes=root_attributes)
                        if valid:
                            self.assertEqual(findings, [])
                        else:
                            self.assertTrue(any(r == "S24" and attribute in message
                                                and f"<{element}>" in message
                                                for r, message in findings), findings)

    def test_malformed_numbers_report_the_file_and_continue(self):
        cases = [
            ("0 0 invalid 300", MODERN_GOOD, "S24", "viewBox"),
            ("0 0 400 300", MODERN_GOOD.replace('stroke-width="1.6"',
                                               'stroke-width="."'), "S24", "stroke-width"),
            ("0 0 400 300", MODERN_GOOD.replace('font-size="17"',
                                               'font-size="17..0"'), "S25", "font-size"),
        ]
        for value in ("rotate(1e999)", "rotate(nan)", "rotate(.)", "rotate(17..0)",
                      "rotate(1, 2)", "translate(1,)", "scale(1e308) scale(1e308)",
                      "rotate(1) rubbish", "unknown(1)"):
            cases.append(("0 0 400 300",
                          MODERN_GOOD.replace(">A<", f' transform="{value}">A<'),
                          "S24", "transform"))
        for attribute in ("x", "y", "fill-opacity"):
            for value in ("1e999", ".", "17..0"):
                cases.append(("0 0 400 300",
                              MODERN_GOOD.replace(">A<", f' {attribute}="{value}">A<')
                              .replace('x="50" ', '').replace('y="270"', ''),
                              "S24", attribute))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            figures = root / "figures" / "I"
            figures.mkdir(parents=True)
            mishnah = root / "mishnah" / "I"
            mishnah.mkdir(parents=True)
            for n in ("47", "48"):
                (mishnah / f"{n}.md").write_text(MODERN_PARAGRAPH)
            first, following = (figures / f"{n}-modern.svg" for n in ("47", "48"))
            following.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
                + MODERN_GOOD.replace("I.47", "I.48").replace(">c<", ">x<") + "</svg>")
            for viewbox, inside, rule, attribute in cases:
                with self.subTest(attribute=attribute):
                    first.write_text(
                        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">'
                        + inside + "</svg>")
                    with patch.object(style, "ROOT", root), \
                            patch.object(style, "modern_drawn_letters", return_value=HEATHS), \
                            patch.object(style, "fail") as fail:
                        style.check_modern(first, "I.47")
                        style.check_modern(following, "I.48")
                    findings = [call.args for call in fail.call_args_list]
                    self.assertTrue(any(r == rule and path == first and attribute in message
                                        for r, path, _, message in findings), findings)
                    self.assertTrue(any(r == "S25" and path == following
                                        and "x is no name" in message
                                        for r, path, _, message in findings), findings)

    def check_refused_modern(self, inside=MODERN_GOOD, paragraph=MODERN_PARAGRAPH,
                            prefix="", root_attributes="", viewbox="0 0 400 300",
                            figure_bytes=None):
        """Read two real files, keeping the following figure's independent finding."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            figures = root / "figures" / "I"
            figures.mkdir(parents=True)
            mishnah = root / "mishnah" / "I"
            mishnah.mkdir(parents=True)
            first, following = (figures / f"{n}-modern.svg" for n in ("47", "48"))
            for n, body, words in (("47", inside, paragraph),
                                    ("48", MODERN_GOOD.replace("I.47", "I.48")
                                     .replace(">c<", ">x<"), MODERN_PARAGRAPH)):
                (mishnah / f"{n}.md").write_text(words)
                (figures / f"{n}-modern.svg").write_text(
                    (prefix if n == "47" else "")
                    + '<svg xmlns="http://www.w3.org/2000/svg" '
                    + (f'viewBox="{viewbox}" {root_attributes}>' if n == "47"
                       else 'viewBox="0 0 400 300">')
                    + body + "</svg>")
            if figure_bytes is not None:
                first.write_bytes(figure_bytes)
            with patch.object(style, "ROOT", root), \
                    patch.object(style, "modern_drawn_letters", return_value=HEATHS), \
                    patch.object(style, "fail") as fail:
                style.check_modern(first, "I.47")
                style.check_modern(following, "I.48")
            findings = [call.args for call in fail.call_args_list]
            self.assertTrue(any(r == "S25" and path == following and "x is no name" in message
                                for r, path, _, message in findings), findings)
            return [(r, message) for r, path, _, message in findings if path == first]

    def test_processing_instruction_rules_stay_separate(self):
        for prefix in ('<?note figure?>', '<?xml version="1.0"?>'):
            with self.subTest(prefix=prefix):
                self.assertEqual(self.check_refused_modern(prefix=prefix), [])
        self.assertEqual(self.check_refused_modern(
            prefix='<?xml-stylesheet href="figure.css" type="text/css"?>'),
            [("S24", "unsupported stylesheet reference in a modern figure")])

    def test_unsupported_svg_presentation_is_refused(self):
        cases = [
            (MODERN_GOOD + '<style>text { fill: #ff0000; font-size: 100px; '
             'font-style: italic; stroke-width: 50px; }</style>', "", "<style>"),
            (MODERN_GOOD, '<?xml-stylesheet href="figure.css" type="text/css"?>', "stylesheet"),
            (MODERN_GOOD.replace(">A<", ' style="@import url(figure.css)">A<'), "", "@import"),
            (MODERN_GOOD.replace(">A<", ' style="font: italic 32px serif">A<'), "", "font"),
            (MODERN_GOOD.replace(">A<", ' style="letter-spacing: 30px">A<'), "", "letter-spacing"),
            (MODERN_GOOD.replace(">A<", ' style="font-size 32px">A<'), "", "style"),
            (MODERN_GOOD.replace(">A<", '><a font-size="100" font-style="italic">A</a><'),
             "", "<a>"),
            (MODERN_GOOD.replace(">A<", '><textPath href="#guide" font-size="9" '
             'font-style="italic">A</textPath><')
             + '<path id="guide" d="M 50 270 L 300 270" fill="none"/>', "", "<textPath>"),
        ]
        for inside, prefix, message in cases:
            with self.subTest(message=message):
                findings = self.check_refused_modern(inside, prefix=prefix)
                self.assertTrue(any(r == "S24" and message in m for r, m in findings), findings)
        styled = MODERN_GOOD.replace(">A<", ' style="font-size: 17px; fill: #3b2f2f">A<')
        self.assertEqual(modern_rules(styled, "I.47"), {"S24"})

    def test_mixed_indentation_keeps_columns_and_offsets(self):
        paragraph = MW + "Put $b$ here."
        for indent in (" \t", "  \t", "   \t", "\t ", " \t "):
            for before in ("", "Before.\n\n"):
                with self.subTest(indent=indent, before=before):
                    text = before + indent + paragraph
                    self.assertIsNone(style.modern_span(text))
                    self.assertIsNone(style.modern_paragraph(text))
                    self.assertIn("S24", {r for r, _ in self.check_refused_modern(paragraph=text)})
            text = "Before.\n\n  " + paragraph + "\n" + indent + "With $c$ there."
            self.assertEqual(style.modern_span(text), (len("Before.\n\n  "), len(text)))
            self.assertEqual(style.modern_names(style.modern_paragraph(text)), {"b", "c"})

    def test_inline_html_and_reference_syntax_are_refused(self):
        for inline in ("e<span>x</span>ponent", "si<!-- notation -->n",
                       '<span data-note="x">the side</span>', "<?note x?>",
                       "<!NOTE x>", "<![CDATA[x]]>", "[the side][x]", "[x][]", "[x]"):
            with self.subTest(inline=inline):
                findings = self.check_refused_modern(paragraph=MW + "Put $b$ in " + inline + ".")
                self.assertTrue(any(r == "S25" and "unsupported" in m for r, m in findings),
                                findings)
        for definition in ("[x]: /reference\n", "[x]:\n /reference\n",
                           "[x]:\n\t/reference\n"):
            for before in (True, False):
                paragraph = MW + "Put $b$ on [the side][x]."
                text = definition + paragraph if before else paragraph + "\n\n" + definition
                with self.subTest(definition=definition, before=before):
                    findings = self.check_refused_modern(paragraph=text)
                    self.assertTrue(any(r == "S25" and "reference definition" in m
                                        for r, m in findings), findings)
                    self.assertNotIn("S24", {r for r, _ in findings})
        for definition in ("[unused]: /reference\n\n", ""):
            text = definition + MODERN_PARAGRAPH + "\n\n[elsewhere]: /reference"
            self.assertEqual(self.check_refused_modern(paragraph=text), [])
        for code in ("`[x]`", "`` [x] ``"):
            text = MODERN_PARAGRAPH + " Literal " + code + ".\n\n[x]: /reference"
            self.assertEqual(self.check_refused_modern(paragraph=text), [])
        findings = self.check_refused_modern(
            paragraph="[unused]: /reference\n" + MODERN_PARAGRAPH)
        self.assertTrue(any(r == "S25" and "reference definition" in m
                            for r, m in findings), findings)
        for inline in ("[the side](/reference)", "`<span>`", "`<!-- notation -->`",
                       "`<?note x?>`", "`<!NOTE x>`", "`<![CDATA[x]]>`",
                       r"\<?note x?>", r"\<!NOTE x>", r"\<!\[CDATA\[x\]\]>"):
            self.assertEqual(self.check_refused_modern(paragraph=MODERN_PARAGRAPH + " " + inline),
                             [])

    def test_all_repository_modern_figures_pass(self):
        required = (
            "I/01-modern.svg",
            "I/02-modern.svg",
            "I/05-modern.svg",
            "I/06-modern.svg",
            "I/07-modern.svg",
            "I/09-modern.svg",
            "I/11-modern.svg",
            "I/12-modern.svg",
            "I/13-modern.svg",
            "I/14-modern.svg",
            "I/15-modern.svg",
            "I/16-modern.svg",
            "I/19-modern.svg",
            "I/20-modern.svg",
            "I/21-modern.svg",
            "I/22-modern.svg",
            "I/24-modern.svg",
            "I/27-modern.svg",
            "I/31-modern.svg",
            "I/34-modern.svg",
            "I/35-modern.svg",
            "I/37-modern.svg",
            "I/43-modern.svg",
            "I/44-modern.svg",
            "II/03-modern.svg",
            "II/04-modern.svg",
            "II/07-modern.svg",
            "II/09-modern.svg",
            "II/11-modern.svg",
            "II/14-modern.svg",
        )
        paths = sorted((style.ROOT / "figures").glob("*/*-modern.svg"))
        for relative in required:
            with self.subTest(path=relative):
                self.assertIn(style.ROOT / "figures" / relative, paths)
        with patch.object(style, "fail") as fail:
            for path in paths:
                style.check_modern(path, style.ref_of(path))
        self.assertEqual(fail.call_args_list, [])

    def test_checker_errors_are_not_input_findings(self):
        with patch.object(style, "modern_findings", side_effect=ValueError("checker defect")):
            with self.assertRaisesRegex(ValueError, "checker defect"):
                self.check_refused_modern()
        with patch.object(style, "transform_of", side_effect=ValueError("checker defect")):
            with self.assertRaisesRegex(ValueError, "checker defect"):
                self.check_refused_modern(MODERN_GOOD.replace(">A<", ' transform="rotate(1 50 270)">A<'))

    def test_text_strokes(self):
        for inherited in (False, True):
            for width, valid in (("1.2", True), ("3.2", True), ("1.1", False),
                                 ("20", False), (".", False)):
                with self.subTest(inherited=inherited, width=width):
                    ink = f'stroke="#3b2f2f" stroke-width="{width}"'
                    label = (f'<g {ink}><text x="50" y="270">A</text></g>' if inherited
                             else f'<text x="50" y="270" {ink}>A</text>')
                    inside = MODERN_GOOD.replace('<text x="50" y="270">A</text>', label)
                    self.assertEqual(modern_rules(inside, "I.47"), set() if valid else {"S24"})

    def test_html_attributes_supply_no_names(self):
        for inline, expected in (
                ('<span data-note="x">the side</span>', {"b"}),
                ('<span data-note="x">c</span>', {"b", "c"}),
                ('<span data-note="x > y">c</span>', {"b", "c"}),
                ('<span\n data-note="x">c</span>', {"b", "c"}),
                ('<span data-note="`x">c</span> and `k`', {"b", "c"}),
                ('<span data-note="<!-- x -->">c</span>', {"b", "c"})):
            text = MW + "Put $b$ on " + inline + "."
            with self.subTest(inline=inline):
                names = style.modern_names(style.modern_paragraph(text))
                self.assertEqual(names, expected)
                figure = ('<title>I.47: the modern way</title>'
                          '<text font-family="Georgia" font-size="17" fill="#3b2f2f" '
                          'font-style="italic">x</text>')
                self.assertEqual(modern_rules(figure, "I.47", names=names), {"S25"})
        escaped = MW + r'Put $b$ on \<span data-note="x">c\</span>.'
        self.assertIn("x", style.modern_names(style.modern_paragraph(escaped)))

    def test_reference_link_names(self):
        cases = [
            ("[this reference][x]", "\n\n[x]: /reference", {"b"}),
            ("[c][x]", "\n\n[x]: /reference", {"b", "c"}),
            ("[c][ X ]", "\n\n[x]: /reference", {"b", "c"}),
            ("[this reference][x]", "", {"b", "x"}),
            ("[this reference][x]", "\n\n```\n[x]: /reference\n```", {"b", "x"}),
            ("[this reference][x]", "\n\n<!--\n[x]: /reference\n-->", {"b", "x"}),
            ("[this reference][x]", "\n\n<div>\n[x]: /reference\n</div>", {"b", "x"}),
            ("[x][] and [c]", "\n\n[x]: /reference\n[c]: /reference", {"b", "x", "c"}),
            ("[c][x] and [d][y]", "\n\n[x]: /reference\n[y]: /reference", {"b", "c", "d"}),
        ]
        for link, definitions, expected in cases:
            text = MW + "Put $b$ on " + link + "." + definitions
            with self.subTest(text=text):
                names = style.modern_names(style.modern_paragraph(text))
                self.assertEqual(names, expected)
                figure = ('<title>I.47: the modern way</title>'
                          '<text font-family="Georgia" font-size="17" fill="#3b2f2f" '
                          'font-style="italic">x</text>')
                self.assertEqual(modern_rules(figure, "I.47", names=names),
                                 set() if "x" in expected else {"S25"})

    def test_leading_reference_definitions_preserve_source_offsets(self):
        paragraph = MW + "Put $b$ on [the side][x]."
        for before in ("[x]: /reference\n", "[x]: /reference\n  'a title'\n",
                       "Before.\n\n[x]: /reference\n[y]: /elsewhere\n  "):
            text = before + paragraph + "\n\nAfter."
            with self.subTest(before=before):
                self.assertEqual(style.modern_span(text),
                                 (len(before), len(before) + len(paragraph)))
                names = style.modern_names(style.modern_paragraph(text))
                self.assertEqual(names, {"b"})
                self.assertNotIn("S24", modern_rules(MODERN_GOOD, "I.47", names=names))
        self.assertIsNone(style.modern_span("[x]: invalid destination\n" + paragraph))

    def test_table_with_nonbreaking_spaces_supplies_no_modern_name(self):
        figure = ('<title>I.47: the modern way</title>'
                  '<text font-family="Georgia" font-size="17" fill="#3b2f2f" '
                  'font-style="italic">x</text>')
        paragraph = MW + "Put $a$ here."
        for delimiter in ("| --- |", "|\t---\t|", "|\u00a0---\u00a0|",
                          "\u00a0| --- |\u00a0"):
            with self.subTest(delimiter=delimiter):
                text = paragraph + "\n| Header |\n" + delimiter + "\n| $x$ |"
                self.assertEqual(self.check_refused_modern(figure, paragraph=text), [
                    ("S25", "<text>x</text>: x is no name of the page's modern way")])
                self.assertEqual(style.modern_span(text), (0, len(paragraph)))
                self.assertEqual(style.modern_names(style.modern_paragraph(text)), {"a"})

    def test_immediate_nonbreaking_space_delimiter_leaves_no_modern_paragraph(self):
        figure = ('<title>I.47: the modern way</title>'
                  '<text font-family="Georgia" font-size="17" fill="#3b2f2f">A</text>')
        for delimiter in ("| --- |", "|\t---\t|", "|\u00a0---\u00a0|",
                          "\u00a0| --- |\u00a0"):
            with self.subTest(delimiter=delimiter):
                text = MW + "Put $a$ here.\n" + delimiter + "\n| $x$ |"
                self.assertEqual(self.check_refused_modern(figure, paragraph=text), [
                    ("S24", "the page's mishnah has no paragraph opening "
                     "**The modern way.** for the figure to stand under")])
                self.assertIsNone(style.modern_span(text))
                self.assertIsNone(style.modern_paragraph(text))

    def test_source_spans(self):
        for before, paragraph, after in SOURCE_SPAN_CASES:
            text = before + (paragraph or "") + after
            with self.subTest(text=text):
                want = (len(before), len(before) + len(paragraph)) if paragraph else None
                self.assertEqual(style.modern_span(text), want)
                selected = style.modern_paragraph(text)
                names = style.modern_names(selected) if selected is not None else None
                findings = modern_rules(MODERN_GOOD, "I.47", names=names)
                self.assertEqual("S24" in findings, paragraph is None)

    def test_render_placement(self):
        count, faults = render.modern_figure_self_check()
        self.assertEqual(count, len(render.MODERN_FIGURE_CASES))
        self.assertEqual(faults, [])

    def test_render_page(self):
        """Exercise the page caller too, which must preserve leading code indentation."""
        mishnah = render.ROOT / "mishnah" / "I" / "47.md"
        figure = render.ROOT / "figures" / "I" / "47-modern.svg"
        read_text, exists = Path.read_text, Path.exists
        facts, docs, records = render.load_facts(), render.load_axiom_docs(), render.load_records()
        count, titles = render.BOOKS["I"]
        for source, want_figure in [("Ordinary commentary.", False), ("", False),
                                    ("**The modern way** Put $b$ here.", False),
                                    ("    " + style.MODERN_WAY + " Put $b$ here.", False),
                                    (COMMENT_PARAGRAPH, True), (CODE_PARAGRAPH, True)]:
            def read(path, *args, **kwargs):
                return source + "\n" if path == mishnah else read_text(path, *args, **kwargs)

            with self.subTest(source=source), patch.object(Path, "read_text", read), \
                    patch.object(Path, "exists", lambda path: path == figure or exists(path)):
                if not want_figure:
                    with self.assertRaises(SystemExit) as error:
                        render.page("I", 47, count, titles, facts, docs, records)
                    self.assertEqual(str(error.exception),
                                     "I.47: figures/I/47-modern.svg exists but the mishnah "
                                     "has no paragraph 'The modern way'")
                    continue
                page = render.page("I", 47, count, titles, facts, docs, records)
                self.assertIn(source, page)
                marker = '<p align="center"><img src="../../figures/I/47-modern.svg"'
                self.assertEqual(marker in page, want_figure)
                if want_figure:
                    self.assertIn(source + "\n\n" + marker, page)

    def test_render_page_without_mishnah(self):
        mishnah = render.ROOT / "mishnah" / "I" / "47.md"
        figure = render.ROOT / "figures" / "I" / "47-modern.svg"
        exists = Path.exists
        facts, docs, records = render.load_facts(), render.load_axiom_docs(), render.load_records()
        count, titles = render.BOOKS["I"]
        for has_figure in (False, True):
            def present(path):
                if path == mishnah:
                    return False
                if path == figure:
                    return has_figure
                return exists(path)

            with self.subTest(has_figure=has_figure), patch.object(Path, "exists", present):
                if has_figure:
                    with self.assertRaises(SystemExit) as error:
                        render.page("I", 47, count, titles, facts, docs, records)
                    self.assertEqual(str(error.exception),
                                     "I.47: figures/I/47-modern.svg exists but the mishnah "
                                     "has no paragraph 'The modern way'")
                else:
                    page = render.page("I", 47, count, titles, facts, docs, records)
                    self.assertIn("_Commentary to come._", page)
                    self.assertNotIn("47-modern.svg", page)

    def test_render_page_normalizes_mishnah_without_modern_figure(self):
        mishnah = render.ROOT / "mishnah" / "I" / "01.md"
        figure = render.ROOT / "figures" / "I" / "01-modern.svg"
        read_text, exists = Path.read_text, Path.exists
        facts, docs, records = render.load_facts(), render.load_axiom_docs(), render.load_records()
        count, titles = render.BOOKS["I"]

        def read(path, *args, **kwargs):
            if path == mishnah:
                return " Ordinary commentary.\n"
            return read_text(path, *args, **kwargs)

        def present(path):
            return False if path == figure else exists(path)

        with patch.object(Path, "read_text", read), patch.object(Path, "exists", present):
            page = render.page("I", 1, count, titles, facts, docs, records)
        self.assertIn("\n\nOrdinary commentary.\n\n", page)
        self.assertNotIn("\n\n Ordinary commentary.\n\n", page)

    def test_render_without_modern_figure(self):
        figure = render.ROOT / "figures" / "I" / "01-modern.svg"
        exists = Path.exists
        with patch.object(Path, "exists", lambda path: path != figure and exists(path)):
            for source in ("", "Ordinary commentary.", "    " + style.MODERN_WAY,
                           COMMENT_PARAGRAPH):
                with self.subTest(source=source):
                    self.assertEqual(render.with_modern_figure(source, "I", 1), source)

    test_modern_cases.__doc__ = (f"S24 and S25 read {len(MODERN_CASES)} figures of the "
                                 "modern way rightly")


class Wording(unittest.TestCase):
    """render.py's words that facts.json decides: which of an overlap's rules the proof
    uses, and III.24's application of one segment to another by `placement`."""

    def test_overlap_use_names_the_unused_rules_plainly(self):
        four = {"rule": "Tacit.a", "also": ["Tacit.b", "Tacit.c", "Tacit.d"], "kind": "gives"}
        rules = render.overlap_rules(four)
        for used, want in [
                (rules, "our proof rests on all these rules"),
                ([], "our proof does not use any of these rules"),
                (rules[:3], "of these rules, our proof rests on `a`, `b` and `c`, and does not "
                            "use `d`"),
                (rules[:2], "of these rules, our proof rests on `a` and `b`, and uses neither "
                            "`c` nor `d`"),
                (rules[:1], "of these rules, our proof rests on `a` and uses none of `b`, `c` "
                            "and `d`")]:
            with self.subTest(used=used):
                self.assertEqual(render.overlap_use({"axioms": used}, four), want)
        two = {"rule": "Tacit.a", "also": ["Tacit.b"], "kind": "gives"}
        self.assertEqual(render.overlap_use({"axioms": ["Tacit.b"]}, two),
                         "of these rules, our proof rests on `b` and does not use `a`")

    # III.5's three combinations, as Audit/Overlaps.lean proves them and III.5's note
    # orders them, crossing before radius, and what its proof rests on among their rules
    # (#293).
    WAYS = {"rule": "Tacit.circle_eq", "also": ["Tacit.inside_not_on"], "kind": "gives",
            "ways": [["Definition15", "Tacit.len_lt_of_inside", "Tacit.lt_irrefl"],
                     ["Definition15", "Tacit.inside_not_on", "Tacit.on_circle_of_len_eq"]]}
    PROOF = {"status": "proved", "axioms": ["Definition15", "Tacit.centre_inside",
                                            "Tacit.inside_not_on", "Tacit.lt_irrefl"]}
    EACH = ("in three ways: `circle_eq` and `inside_not_on` together, of which our proof "
            "rests on `inside_not_on` and does not use `circle_eq`; `Definition15`, "
            "`len_lt_of_inside` and `lt_irrefl` together, of which our proof rests on "
            "`Definition15` and `lt_irrefl`, and does not use `len_lt_of_inside`; and "
            "`Definition15`, `inside_not_on` and `on_circle_of_len_eq` together, of which our "
            "proof rests on `Definition15` and `inside_not_on`, and does not use "
            "`on_circle_of_len_eq`")
    LINE = ("our axioms already contain it in three ways, and our proof rests on some of the "
            "rules of each")

    @staticmethod
    def record(overlap, n=5):
        return heath.validate_review(
            {"statement": {"scope": "full"}, "route": {"kind": "euclid"},
             "overlap": json.loads(json.dumps(overlap)),
             "review": {"stage": "exceptions", "reviewer": "Claude Opus 5.5"}},
            "III", n, require_stamp=False, where="a test record")

    def test_overlap_ways_are_each_named_with_their_use(self):
        """Each combination of `ways`, the first one first, with the rules our proof rests
        on: all of them, some (each rule used and unused named) or none."""
        self.assertEqual(render.overlap_contains_ways(self.PROOF, self.WAYS, "it"),
                         f"our axioms already contain it {self.EACH}")
        tacit = {"rule": "Tacit.a", "also": ["Tacit.b"], "kind": "states",
                 "ways": [["Tacit.c"], ["Tacit.a", "Tacit.c", "Tacit.d"]]}
        for axioms, want in [
                ([], "our tacit rules contain it too, in three ways: `a` and `b` together, of "
                     "which our proof uses neither; `c`, which our proof does not use; and `a`, "
                     "`c` and `d` together, of which our proof uses none"),
                (["Tacit.a", "Tacit.b", "Tacit.c", "Tacit.d"],
                 "our tacit rules already contain it in three ways: `a` and `b` together, of "
                 "which our proof rests on both; `c`, on which our proof rests; and `a`, `c` "
                 "and `d` together, of which our proof rests on all three"),
                (["Tacit.c"],
                 "our tacit rules already contain it in three ways: `a` and `b` together, of "
                 "which our proof uses neither; `c`, on which our proof rests; and `a`, `c` "
                 "and `d` together, of which our proof rests on `c` and uses neither `a` nor "
                 "`d`")]:
            with self.subTest(axioms=axioms):
                self.assertEqual(render.overlap_contains_ways({"axioms": axioms}, tacit, "it"),
                                 want)

    def test_the_line_counts_the_ways_and_says_their_use_in_a_few_words(self):
        """Under the enunciation, how many combinations contain the proposition, and whether
        the proof rests on all, some or none of the rules of each, or, where that differs,
        of each by its place; no rule is named there."""
        self.assertEqual(render.overlap_ways_line(self.PROOF, self.WAYS), self.LINE)
        tacit = {"rule": "Tacit.a", "also": ["Tacit.b"], "kind": "states",
                 "ways": [["Tacit.c"], ["Tacit.a", "Tacit.c", "Tacit.d"]]}
        for axioms, want in [
                ([], "our tacit rules contain it too, in three ways, though this proof uses "
                     "none of their rules"),
                (["Tacit.a", "Tacit.b", "Tacit.c", "Tacit.d"],
                 "our tacit rules already contain it in three ways, and our proof rests on all "
                 "the rules of each"),
                (["Tacit.c"],
                 "our tacit rules already contain it in three ways, and our proof rests on none "
                 "of the rules of the first, all the rules of the second and some of the rules "
                 "of the third")]:
            with self.subTest(axioms=axioms):
                self.assertEqual(render.overlap_ways_line({"axioms": axioms}, tacit), want)
        for k, word in [(1, "first"), (3, "third"), (10, "tenth"), (11, "11th"), (12, "12th"),
                        (13, "13th"), (21, "21st"), (22, "22nd"), (23, "23rd"), (24, "24th"),
                        (101, "101st"), (111, "111th"), (112, "112th")]:
            with self.subTest(k=k):
                self.assertEqual(render.ordinal_word(k), word)

    def test_overlap_ways_on_the_page_and_in_the_summary(self):
        """The line under the enunciation counts the combinations, and the Overlap row and
        the book's summary name each; a record with no `ways` is worded as before, beside
        one that has."""
        record = self.record(self.WAYS)
        self.assertTrue(render.in_lean_line(self.PROOF, record, "III", 5).endswith(
            f" · Euclid's argument · {self.LINE} (see Overlap)"))
        lead = ("Three ways: `circle_eq` and `inside_not_on`; `Definition15`, `len_lt_of_inside` "
                "and `lt_irrefl`; and `Definition15`, `inside_not_on` and "
                "`on_circle_of_len_eq`. ")
        use = (" Of the first way's rules, our proof rests on `inside_not_on` and does not "
               "use `circle_eq`. Of the second way's rules, our proof rests on `Definition15` "
               "and `lt_irrefl`, and does not use `len_lt_of_inside`. Of the third way's "
               "rules, our proof rests on `Definition15` and `inside_not_on`, and does not use "
               "`on_circle_of_len_eq`. See [the overlap catalogue]"
               "(../../docs/reports/overlaps.md). |")
        for note, said in [(None, "Each way's rules together already contain this proposition."),
                           ("Three short proofs.", "Three short proofs.")]:
            with self.subTest(note=note):
                ov = dict(self.WAYS, **({"note": note} if note else {}))
                table = render.field_table("III", 5, self.PROOF, self.record(ov), [], {})
                row = next(r for r in table.splitlines() if r.startswith("| Overlap |"))
                self.assertEqual(row, "| Overlap | " + lead + said + use)
        records = {"III.2": self.record({"rule": "Tacit.outside_of_between", "kind": "gives"}, 2),
                   "III.5": record,
                   "III.6": self.record({"rule": "Tacit.circle_eq", "kind": "gives",
                                         "also": ["Tacit.centre_inside", "Tacit.inside_not_on"]},
                                        6)}
        facts = {"III.2": {"axioms": []}, "III.5": self.PROOF, "III.6": self.PROOF}
        self.assertEqual(
            render.overlap_sentences(["III.2", "III.5", "III.6"], facts, records,
                                     lambda rs: ", ".join(f"[{r}]" for r in rs), ""),
            "In [III.2] one of our tacit rules contains the proposition too, but our proof "
            "never uses that rule. "
            f"In [III.5] our axioms already contain the proposition {self.EACH}. "
            "In [III.6] three of our tacit rules together already contain the proposition; "
            "of these rules, our proof rests on `centre_inside` and `inside_not_on`, and does "
            "not use `circle_eq`. [The overlap catalogue](docs/reports/overlaps.md) gives each.")

    @staticmethod
    def facts(direct=(), brings=("I.4", "I.8"), step="BookIII.placement"):
        """A facts.json in which III.24's proof has the shared step `step`, citing
        `brings`, and calls on superposition itself where `direct` says so."""
        sup = "Tacit.superposition"
        return {"propositions": [
            {"ref": "III.24", "axioms": [sup], "direct_axioms": list(direct),
             "shared_steps": [{"name": step, "brings_in": list(brings)}]},
            {"ref": "I.4", "axioms": [sup], "direct_axioms": [sup]},
            {"ref": "I.8", "axioms": [sup], "direct_axioms": [sup]},
            {"ref": "I.26", "axioms": [sup], "direct_axioms": []},
            {"ref": "I.5", "axioms": [], "direct_axioms": []}]}

    def test_placement_is_worded_from_facts(self):
        """The line on III.24 names only what its facts.json entry shows, read afresh for
        each root."""
        head = (" Euclid's III.24 applies one segment to another, and so does our proof of "
                "it, by `placement`")
        through = ", which uses superposition only through the propositions it cites"
        old = render.SUPERPOSITION_NOTE["III"]
        for facts, want in [
                (self.facts(), head + through + ", I.4 and I.8 among them."),
                (self.facts(brings=("I.8", "I.26")), head + through + ", I.8 among them."),
                (self.facts(brings=("I.26",)), head + through + "."),
                (self.facts(brings=("I.5",)), head + "."),
                (self.facts(direct=("Tacit.superposition",)), head + "."),
                (self.facts(step="BookIII.other"), old)]:
            with self.subTest(facts=facts), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                (root / "facts.json").write_text(json.dumps(facts))
                with patch.object(render, "ROOT", root):
                    self.assertEqual(render.content_wording().get(old, old), want)


class LeanPartsNames(unittest.TestCase):
    """The declarations a page lists before and after the main theorem are read from the
    Lean's code, not its comments: a docstring of train C6c's III.13 wrapped so that a line
    began "lemma beside III.13", and its page listed a lemma `beside` that the file never
    declared."""

    SRC = (
        "namespace Elements.BookIII\nopen Tacit\n\n"
        "/-- A helper, whose docstring wraps so that a line begins\n"
        "theorem with a word that declares nothing. -/\n"
        "theorem Prop99.helper : True := trivial\n\n"
        "/-- **III.99**, the main theorem. -/\n"
        "theorem Prop99 : True := trivial\n\n"
        "/-- A lemma beside III.99, whose docstring wraps so that a line begins\n"
        "lemma beside III.99, its first clause alone. -/\n"
        "theorem Prop99.first : True := trivial\n"
        "/- a comment /- nested -/\n"
        "def not_declared -/\n"
        "theorem Prop99.second : True := trivial\n\n"
        "end Elements.BookIII\n")

    def parts(self, src):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            path = root / "Prop99.lean"
            path.write_text(src)
            with patch.object(render, "ROOT", root), \
                    patch.object(render.heath, "lean_path", lambda book, n: path):
                return render.lean_parts("III", 99)

    def test_names_in_comments_are_not_declarations(self):
        parts = self.parts(self.SRC)
        self.assertEqual(parts.before_names, ["Prop99.helper"])
        self.assertEqual(parts.after_names, ["Prop99.first", "Prop99.second"])
        self.assertIn("lemma beside III.99", parts.after)

    def test_a_heading_alone_goes_with_the_main_theorem(self):
        # Before the theorem, only a section heading whose second line begins "def": it
        # declares nothing, so it is shown with the main theorem, not as a helper.
        src = self.SRC.replace(
            "/-- A helper, whose docstring wraps so that a line begins\n"
            "theorem with a word that declares nothing. -/\n"
            "theorem Prop99.helper : True := trivial\n\n",
            "/-! ## The proposition\n"
            "def is not a declaration here. -/\n\n")
        parts = self.parts(src)
        self.assertEqual((parts.before, parts.before_names), ("", []))
        self.assertTrue(parts.main.startswith("/-! ## The proposition"))


class FigureCaption(unittest.TestCase):
    """The caption under Euclid's figure, from the review record's [figure]: "Drawn for
    one case" before its `case`, or "Drawn for every case" where `every_case` says the
    figure draws them all, as III.25's draws Euclid's three side by side."""

    CASE = "the angle ABD greater than, equal to and less than the angle BAD"

    def test_the_caption_says_one_case_or_every_case(self):
        for figure, want in [
                ({"case": "A outside the circle."}, "Drawn for one case: A outside the circle."),
                ({"case": "A outside the circle", "every_case": False},
                 "Drawn for one case: A outside the circle."),
                ({"case": self.CASE, "every_case": True}, f"Drawn for every case: {self.CASE}."),
                ({"case": self.CASE + ".", "every_case": True, "note": "N."},
                 f"Drawn for every case: {self.CASE}. N."),
                ({"every_case": True, "note": "N."}, "N.")]:
            with self.subTest(figure=figure):
                self.assertEqual(render.figure_note({"figure": figure}), want)

    @staticmethod
    def load(figure: str) -> dict:
        """load_review on a record of III.25 whose [figure] is `figure`, in a tree of its
        own that holds Heath's text of III.25 and that record."""
        text = heath.heath_path("III", 25).read_text()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "heath" / "III").mkdir(parents=True)
            (root / "heath" / "III" / "25.md").write_text(text)
            (root / "review" / "III").mkdir(parents=True)
            (root / "review" / "III" / "25.toml").write_text(
                '[statement]\nscope = "full"\n\n[route]\nkind = "euclid"\n\n'
                f'[figure]\n{figure}\n\n[review]\nstage = "exceptions"\nreviewer = "a test"\n')
            with patch.object(heath, "ROOT", root), \
                    patch.object(heath, "REVIEW", root / "review"):
                return heath.load_review("III", 25, require_stamp=False)

    def test_a_record_reads_every_case_with_its_case(self):
        for figure, want in [(f'case = "{self.CASE}"\nevery_case = true',
                              f"Drawn for every case: {self.CASE}."),
                             (f'case = "{self.CASE}"\nevery_case = false',
                              f"Drawn for one case: {self.CASE}.")]:
            with self.subTest(figure=figure):
                self.assertEqual(render.figure_note(self.load(figure)), want)

    def test_a_record_refuses_every_case_without_its_case_or_not_true_or_false(self):
        for figure, want in [
                ('every_case = true\nnote = "N."', "`every_case` needs the `case`"),
                ("every_case = true", "`every_case` needs the `case`"),
                ("every_case = false", "give its `case`, its `note`, or both"),
                (f'case = "{self.CASE}"\nevery_case = "yes"', "`every_case` must be true or false"),
                (f'case = "{self.CASE}"\nevery_case = 1', "`every_case` must be true or false")]:
            with self.subTest(figure=figure):
                with self.assertRaises(heath.ReviewError) as caught:
                    self.load(figure)
                self.assertEqual(caught.exception.where, "review/III/25.toml")
                self.assertTrue(any(want in p for p in caught.exception.problems),
                                caught.exception.problems)


def svg_refusal(kind, attr=None, value=None):
    """The diagnostic expected when a case is outside the declared input language."""
    what = f"<{kind}>" + (f" {attr} {value!r}" if attr is not None else "")
    return f"{what} is outside S26's SVG allow-list"


def pi_refusal(target, data):
    instruction = target + (f" {data}" if data else "")
    return f"processing instruction {instruction!r} is outside S26's SVG allow-list"


def text_refusal(payload):
    return f"<text> payload {payload!r} is outside S26's SVG allow-list"


DTD_CASES = (
    ('<!DOCTYPE svg [<!ENTITY family "Georgia">]>', '&family;'),
    ('<!DOCTYPE svg [<!ENTITY first "Geor"><!ENTITY family "&first;gia">]>', '&family;'),
    ('<!DOCTYPE svg SYSTEM "x.dtd">', 'Georgia'),
    ('<!DOCTYPE svg PUBLIC "figure" "x.dtd">', 'Georgia'),
    ('<!DOCTYPE svg [<!ENTITY % family "Georgia">]>', 'Georgia'),
    ('<!DOCTYPE svg>', 'Georgia'),
)
DTD_REFERENCE_CASES = (
    ('<!DOCTYPE svg SYSTEM "x.dtd" [<!ENTITY family "Georgia">]>', '&family;', 'A'),
    ('<!DOCTYPE svg PUBLIC "figure" "x.dtd" [<!ENTITY family "Georgia">]>', '&family;', 'A'),
    ('<!DOCTYPE svg [<!ENTITY label "A">]>', 'Georgia', '&label;'),
    ('''<!DOCTYPE svg [<!ENTITY % labels "<!ENTITY label 'A'>">%labels;]>''',
     'Georgia', '&label;'),
    ('<!DOCTYPE svg>', '&missing;', 'A'),
    ('<!DOCTYPE svg>', 'Georgia', '&missing;'),
)
DTD_REFUSAL = "DTD or entity declaration is outside S26's SVG allow-list"


def dtd_figure(idea, declaration, family):
    return declaration.encode("ascii") + ET.tostring(figure_fixture(idea)).replace(
        b'font-family="Georgia"', f'font-family="{family}"'.encode("ascii"))


class SvgGate(unittest.TestCase):
    """The closed SVG input language, through both complete figure checks."""

    def assert_refused(self, root, idea, *names):
        found = [f for f in figure_findings(root, idea) if f[0] == "S26"]
        path = "figures/I/01-idea.svg" if idea else "figures/I/01.svg"
        self.assertTrue(found, (idea, names))
        self.assertTrue(all(f[1:3] == (path, 0) for f in found), found)
        for name in names:
            self.assertTrue(any(name in f[3] for f in found), (name, found))

    def assert_continued(self, found, idea, message, first_path=None, rule="S26"):
        suffix = "-idea.svg" if idea else ".svg"
        first_path = first_path or "figures/I/01" + suffix
        self.assertTrue(any(r == rule and p == first_path and message in msg
                            for r, p, _, msg in found), found)
        self.assertTrue(any(r == "S26" and p == "figures/I/02" + suffix
                            and "letter E" in msg and "canvas's edge" in msg
                            for r, p, _, msg in found), found)

    def test_nesting_depth_and_continuation(self):
        """Refuse excessive nesting before recursion, then check the next figure."""
        for idea in (False, True):
            for depth in (17, 1100):
                with self.subTest(idea=idea, depth=depth):
                    # Build bytes directly: ElementTree's serialiser is recursive too.
                    raw = (b'<svg xmlns="http://www.w3.org/2000/svg">'
                           + b"<g>" * depth + b"</g>" * depth + b"</svg>")
                    self.assert_continued(figure_run(raw, idea), idea,
                                          "nesting exceeds 16 levels below the root")

    def test_nesting_depth_boundary(self):
        for idea in (False, True):
            with self.subTest(idea=idea):
                root = figure_fixture(idea)
                parent = root
                for _ in range(16):
                    parent = svg_sub(parent, style.SVG + "g")
                self.assertEqual(figure_findings(root, idea), [])
                svg_sub(parent, style.SVG + "g")
                self.assertEqual(figure_findings(root, idea), [
                    ("S26", "figures/I/01" + ("-idea.svg" if idea else ".svg"), 0,
                     "SVG nesting exceeds 16 levels below the root")])

    def test_svg_namespace_at_both_entry_points(self):
        """The root and every descendant belong to the SVG namespace."""
        for idea in (False, True):
            path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
            root = figure_fixture(idea)
            root.tag = "svg"
            self.assertEqual(figure_findings(root, idea), [
                ("S26", path, 0, "<svg> root is not an SVG-namespaced <svg> in "
                 "S26's SVG allow-list")])

            root = figure_fixture(idea)
            label = next(el for el in root.iter() if style.text_of(el) == "A")
            label.tag = "text"
            self.assertEqual(figure_findings(root, idea), [
                ("S26", path, 0, "<text> is outside S26's SVG namespace")])

            self.assertEqual(figure_findings(figure_fixture(idea), idea), [])

    def test_nonrendering_descendants_at_both_entry_points(self):
        """Metadata is text-only, and text and drawn elements are leaves."""
        for idea in (False, True):
            path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
            for kind in ("title", "desc", "text", "line"):
                with self.subTest(idea=idea, parent=kind):
                    root = figure_fixture(idea)
                    if kind == "desc":
                        parent = next((el for el in root if style.tag(el) == "desc"), None)
                        if parent is None:
                            parent = svg_sub(root, "desc")
                    else:
                        parent = next(el for el in root.iter() if style.tag(el) == kind)
                    child = svg_sub(parent, "text" if kind in ("title", "desc") else "g")
                    if style.tag(child) == "text":
                        child.text = "A"
                    self.assertEqual([f for f in figure_findings(root, idea) if f[0] == "S26"], [
                        ("S26", path, 0, f"<{kind}> may not contain element children in "
                         "S26's SVG allow-list")])

    def test_stroked_labels(self):
        for idea in (False, True):
            for placement in ("own", "group", "root"):
                with self.subTest(idea=idea, placement=placement):
                    root = figure_fixture(idea)
                    e = next(el for el in root.iter() if style.text_of(el) == "E")
                    group = next(el for el in root.iter() if e in list(el))
                    e.attrib.update(x="150", y="100", **{"font-size": "17",
                                         "font-style": "normal", "text-anchor": "start"})
                    ink = "#222222" if idea else "#3b2f2f"
                    svg_sub(root, "line", {"x1": "145", "y1": "103.5", "x2": "170",
                                  "y2": "103.5", "stroke": ink, "stroke-width": "1.6"})
                    target = {"own": e, "group": group, "root": root}[placement]
                    target.attrib.update(stroke=ink, **{"stroke-width": "1.6"})
                    self.assert_refused(root, idea, "letter E", "stroke")
                    # An explicit reset overrides every ancestor.
                    for el in root.iter():
                        if style.tag(el) == "text":
                            el.set("stroke", "none")
                    self.assertEqual([f for f in figure_findings(root, idea) if f[0] == "S26"], [])

    def test_point_labels_need_visible_fill(self):
        """Direct and inherited fill none fail; explicit visible fill overrides it."""
        for idea in (False, True):
            path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
            ink = "#222222" if idea else "#3b2f2f"

            root = figure_fixture(idea)
            label = next(el for el in root.iter() if style.text_of(el) == "E")
            label.set("fill", "none")
            self.assertEqual(figure_findings(root, idea), [
                ("S26", path, 0, "letter E has effective fill 'none': outside S26's SVG "
                 "allow-list")])

            root = figure_fixture(idea)
            group = next(el for el in root.iter()
                         if style.tag(el) == "g" and any(style.tag(child) == "text"
                                                         for child in el))
            group.set("fill", "none")
            self.assertEqual(figure_findings(root, idea), [
                ("S26", path, 0, f"letter {s} has effective fill 'none': outside S26's SVG "
                 "allow-list") for s in ("A", "C", "E")])

            for label in group:
                label.set("fill", ink)
            self.assertEqual(figure_findings(root, idea), [])

    def test_bold_labels_and_numerals(self):
        for idea in (False, True):
            for placement in ("own", "group", "root"):
                with self.subTest(idea=idea, placement=placement):
                    root = figure_fixture(idea)
                    e = next(el for el in root.iter() if style.text_of(el) == "E")
                    group = next(el for el in root.iter() if e in list(el))
                    e.attrib.update(x="150", y="100", **{"font-size": "17",
                                         "font-style": "normal", "text-anchor": "start"})
                    svg_sub(root, "line", {"x1": "163.6", "y1": "80", "x2": "163.6",
                                  "y2": "105", "stroke-width": "1.6",
                                  "stroke": "#222222" if idea else "#3b2f2f"})
                    target = {"own": e, "group": group, "root": root}[placement]
                    target.set("font-weight", "bold")
                    self.assert_refused(root, idea, "letter E", "font-weight")
                    for el in root.iter():
                        if style.tag(el) == "text":
                            el.set("font-weight", "normal")
                    # Main's bold numerical annotations remain allowed, inherited too.
                    for content in ("9", "16", "25"):
                        attrs = {"x": "250", "y": "230"}
                        if placement == "own":
                            attrs["font-weight"] = "bold"
                        svg_sub(target if placement != "own" else group, "text", attrs).text = content
                    self.assertEqual([f for f in figure_findings(root, idea) if f[0] == "S26"], [])

    def test_unicode_capitals_are_refused_and_checking_continues(self):
        """Both figure entry points refuse unmeasured capitals and reach the next file."""
        for idea in (False, True):
            for payload in ("Α", "Ａ"):
                with self.subTest(idea=idea, payload=payload):
                    root = figure_fixture(idea)
                    svg_sub(root, "text", {"x": "250", "y": "230",
                                  "fill": "#222222" if idea else "#3b2f2f"}).text = payload
                    found = figure_run(root, idea)
                    path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                    self.assertEqual([f for f in found if f[1] == path],
                                     [("S26", path, 0, text_refusal(payload))])
                    self.assert_continued(found, idea, text_refusal(payload))

    def test_missing_label_font_family(self):
        """A default font cannot borrow Georgia's clearance at either entry point."""
        for idea in (False, True):
            for missing in (("A", "C", "E"), ("E",)):
                with self.subTest(idea=idea, missing=missing):
                    root = figure_fixture(idea)
                    del root.attrib["font-family"]
                    for el in root.iter():
                        if style.tag(el) == "text" and style.text_of(el) not in missing:
                            el.set("font-family", "Georgia")
                    # E clears this stroke by 2.04 in Georgia; a default font can differ.
                    x = "355.33" if idea else "349.85"
                    svg_sub(root, "line", {
                        "x1": x, "x2": x, "y1": "138", "y2": "160",
                        "stroke": "#222222" if idea else "#3b2f2f", "stroke-width": "1.6"})
                    path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                    self.assertEqual(figure_findings(root, idea), [
                        ("S26", path, 0, f"letter {s} has effective font-family None: "
                         "outside S26's SVG allow-list") for s in missing])

    def test_supported_label_font_families(self):
        """Main's three Georgia declarations work on the root, a group or each label."""
        for idea in (False, True):
            for family in ("Georgia", "Georgia, serif", "Georgia, 'Times New Roman', serif"):
                for placement in ("root", "group", "own"):
                    with self.subTest(idea=idea, family=family, placement=placement):
                        root = figure_fixture(idea)
                        del root.attrib["font-family"]
                        labels = [el for el in root.iter() if style.tag(el) == "text"]
                        group = next(el for el in root.iter() if labels[0] in list(el))
                        targets = {"root": [root], "group": [group], "own": labels}[placement]
                        for target in targets:
                            target.set("font-family", family)
                        x = "355.33" if idea else "349.85"
                        svg_sub(root, "line", {
                            "x1": x, "x2": x, "y1": "138", "y2": "160",
                            "stroke": "#222222" if idea else "#3b2f2f", "stroke-width": "1.6"})
                        self.assertEqual(figure_findings(root, idea), [])

    def test_unsupported_label_font_families(self):
        for idea in (False, True):
            for family in ("", "serif", "Times New Roman", "Arial, Georgia", "Georgia, sans-serif"):
                for placement in ("root", "group", "own"):
                    with self.subTest(idea=idea, family=family, placement=placement):
                        root = figure_fixture(idea)
                        e = next(el for el in root.iter() if style.text_of(el) == "E")
                        group = next(el for el in root.iter() if e in list(el))
                        target = {"root": root, "group": group, "own": e}[placement]
                        target.set("font-family", family)
                        path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                        self.assertEqual(figure_findings(root, idea), [
                            ("S26", path, 0, svg_refusal(style.tag(target), "font-family", family))])

    def test_raw_label_content(self):
        for idea in (False, True):
            for char in ("\u00a0", "\u2002", "\u2003", "\u202f", "\u3000", "\u200b", "\u0301"):
                for content in (char + "E", "E" + char, "E" + char + "′"):
                    with self.subTest(idea=idea, content=content):
                        root = figure_fixture(idea)
                        e = next(el for el in root.iter() if style.text_of(el) == "E")
                        e.text = content
                        self.assert_refused(root, idea, "<text>", "payload")
            for content in (" E ", "\tE\t", "\rE\r", "\nE\n", " \t\r\nE \t\r\n"):
                with self.subTest(idea=idea, content=content):
                    root = figure_fixture(idea)
                    next(el for el in root.iter() if style.text_of(el) == "E").text = content
                    self.assertEqual(figure_findings(root, idea), [])

    def test_explicit_ellipse_radii(self):
        for idea in (False, True):
            for missing in ("rx", "ry", "both"):
                for fill in ("none", "#222222" if idea else "#3b2f2f"):
                    with self.subTest(idea=idea, missing=missing, fill=fill):
                        root = figure_fixture(idea)
                        e = next(el for el in root.iter() if style.text_of(el) == "E")
                        e.attrib.update(x="150", y="100", **{"font-size": "17",
                                             "font-style": "normal", "text-anchor": "start"})
                        ellipse = svg_sub(root, "ellipse", {"cx": "150", "cy": "100",
                                     "rx": "8", "ry": "8", "fill": fill, "stroke-width": "1.6",
                                     "stroke": "#222222" if idea else "#3b2f2f"})
                        for attr in (("rx", "ry") if missing == "both" else (missing,)):
                            del ellipse.attrib[attr]
                        self.assert_refused(root, idea, "<ellipse>", "rx", "ry")

    def test_numeric_bounds_and_continuation(self):
        for idea in (False, True):
            for big in ("10000.1", "-10000.1", "9" * 308, "0." + "0" * 330 + "1"):
                for attr, value in (("x1", big), ("r", big), ("stroke-width", big),
                                    ("points", f"0 0 {big} 100"),
                                    ("viewBox", f"0 0 {big} 300"),
                                    ("stroke-dasharray", f"1 {big}"),
                                    ("transform", f"translate({big},0)"),
                                    ("d", f"M150 100 C{big} 100 {big} 100 160 100"),
                                    ("d", f"M150 100 A{big} 8 0 0 1 160 100")):
                    with self.subTest(idea=idea, attr=attr, value=value[:40]):
                        root = figure_fixture(idea)
                        shape = svg_sub(root, "path", {"fill": "none",
                                              "stroke": "#222222" if idea else "#3b2f2f",
                                              "stroke-width": "1.6"})
                        shape.set(attr, value)
                        self.assert_refused(root, idea, attr, "allow-list")
                        self.assert_continued(figure_run(root, idea), idea, "allow-list")
            root = figure_fixture(idea)
            svg_sub(root, "line", {"x1": "-10000", "x2": "10000", "stroke": "none"})
            self.assertEqual(figure_findings(root, idea), [])

    def test_curve_limits_and_continuation(self):
        for idea in (False, True):
            root = figure_fixture(idea)
            svg_sub(root, "path", {"d": "M100 100 C100 200 200 200 200 100",
                          "stroke": "#222222" if idea else "#3b2f2f", "fill": "none",
                          "stroke-width": "1.6"})
            # Exhaust the budget on a small curve to exercise the failure path quickly.
            for depth in (0, 1):
                with self.subTest(idea=idea, depth=depth), \
                        patch.object(style, "CURVE_MAX_DEPTH", depth, create=True):
                    self.assert_continued(figure_run(root, idea), idea, "subdivision limit")
            distance = style.point_gap
            for bad in (float("inf"), float("nan")):
                def nonfinite(p, a, b):
                    return bad if p == (100.0, 200.0) else distance(p, a, b)
                with self.subTest(idea=idea, intermediate=bad), \
                        patch.object(style, "point_gap", side_effect=nonfinite):
                    self.assert_continued(figure_run(root, idea), idea, "non-finite")

    def test_arc_arithmetic_and_continuation(self):
        for idea in (False, True):
            for radius in ("0." + "0" * 309 + "1", "0." + "0" * 160 + "1"):
                for fill in ("none", "#222222" if idea else "#3b2f2f"):
                    with self.subTest(idea=idea, radius=radius, fill=fill):
                        root = figure_fixture(idea)
                        svg_sub(root, "path", {
                            "d": f"M100 100 A{radius} 1 0 0 1 200 100", "fill": fill,
                            "stroke": "#222222" if idea else "#3b2f2f", "stroke-width": "1.6"})
                        self.assert_continued(figure_run(root, idea), idea, "non-finite")

    def test_tiny_ellipse_fill(self):
        # Squaring these finite ratios used to overflow in S20's fill measurement.
        root = figure_fixture(True)
        ellipse = ET.Element(style.SVG + "ellipse", {
            "cx": "20", "cy": "20", "rx": "0." + "0" * 160 + "1",
            "ry": "1", "fill": "#222222"})
        root.insert(1, ellipse)
        self.assertEqual(figure_findings(root, True), [])
        ellipse.set("rx", "0." + "0" * 309 + "1")
        self.assert_continued(figure_run(root, True), True, "non-finite")

    def test_encoding_failures_and_continuation(self):
        for idea in (False, True):
            for encoding in ("unknown-encoding", "shift_jis"):
                raw = f'<?xml version="1.0" encoding="{encoding}"?><svg/>'.encode("ascii")
                with self.subTest(idea=idea, encoding=encoding):
                    self.assert_continued(figure_run(raw, idea), idea, "not well-formed SVG",
                                          rule="S14" if idea else "S15")
        # The second parse site reads Euclid's figure while checking an idea's letters.
        for encoding in ("unknown-encoding", "shift_jis"):
            raw = f'<?xml version="1.0" encoding="{encoding}"?><svg/>'.encode("ascii")
            self.assert_continued(figure_run(figure_fixture(True), True, reference=raw), True,
                                  "not well-formed SVG", first_path="figures/I/01.svg", rule="S15")
        # Expat versions differ in which decoder failures they produce.
        parse = style.parse_svg
        for idea in (False, True):
            def decode_failure(path, *args, **kwargs):
                if Path(path).name == ("01-idea.svg" if idea else "01.svg"):
                    raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
                return parse(path, *args, **kwargs)
            with patch.object(style, "parse_svg", side_effect=decode_failure):
                self.assert_continued(figure_run(figure_fixture(idea), idea), idea,
                                      "not well-formed SVG", rule="S14" if idea else "S15")

    def test_stylesheet_processing_instructions_and_continuation(self):
        target = "xml-stylesheet"
        data = 'type="text/css" href="data:text/css,line{stroke-width:20}"'
        expected = pi_refusal(target, data)
        for idea in (False, True):
            with self.subTest(idea=idea):
                raw = (f'<?xml version="1.0"?>\n<?{target} {data}?>\n'.encode("ascii")
                       + ET.tostring(figure_fixture(idea)))
                found = figure_run(raw, idea)
                path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                self.assertEqual([f for f in found if f[1] == path], [("S26", path, 0, expected)])
                self.assert_continued(found, idea, expected)

    def test_dtd_refusal_and_continuation(self):
        for idea in (False, True):
            for declaration, family in DTD_CASES:
                for encoding in ("utf-8", "utf-16"):
                    with self.subTest(idea=idea, declaration=declaration, encoding=encoding):
                        raw = dtd_figure(idea, declaration, family).decode("ascii").encode(encoding)
                        found = figure_run(raw, idea)
                        path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                        self.assertEqual([f for f in found if f[1] == path],
                                         [("S26", path, 0, DTD_REFUSAL)])
                        self.assert_continued(found, idea, DTD_REFUSAL)

    def test_dtd_references_and_continuation(self):
        for idea in (False, True):
            for declaration, family, label in DTD_REFERENCE_CASES:
                with self.subTest(idea=idea, declaration=declaration, family=family, label=label):
                    raw = dtd_figure(idea, declaration, family).replace(
                        b">A<", f">{label}<".encode("ascii"))
                    found = figure_run(raw, idea)
                    path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                    self.assertEqual([f for f in found if f[1] == path],
                                     [("S26", path, 0, DTD_REFUSAL)])
                    self.assert_continued(found, idea, DTD_REFUSAL)
                    with tempfile.TemporaryDirectory() as tmp, patch.object(style, "failures", []):
                        copy = Path(tmp) / "01.svg"
                        copy.write_bytes(raw)
                        self.assertIsNone(style.drawn_letters(copy))
                        self.assertEqual(style.failures, [])

    def test_dtd_markup_anywhere_and_continuation(self):
        # The byte guard deliberately refuses declaration markers inside comments too.
        for idea in (False, True):
            body = ET.tostring(figure_fixture(idea))
            for declaration in (b"<!DOCTYPE svg>", b'<!ENTITY label "A">'):
                for comment in (False, True):
                    markup = b"<!-- " + declaration + b" -->" if comment else declaration
                    for place in ("before", "inside", "after"):
                        raw = {"before": markup + body,
                               "inside": body.replace(b">", b">" + markup, 1),
                               "after": body + markup}[place]
                        for encoding in ("utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
                            with self.subTest(idea=idea, declaration=declaration, comment=comment,
                                              place=place, encoding=encoding):
                                found = figure_run(raw.decode("ascii").encode(encoding), idea)
                                path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                                self.assertEqual([f for f in found if f[1] == path],
                                                 [("S26", path, 0, DTD_REFUSAL)])
                                self.assert_continued(found, idea, DTD_REFUSAL)

    def test_undeclared_references_without_dtd_and_continuation(self):
        for idea in (False, True):
            for family, label in (("&missing;", "A"), ("Georgia", "&missing;")):
                with self.subTest(idea=idea, family=family, label=label):
                    raw = dtd_figure(idea, "", family).replace(b">A<", f">{label}<".encode("ascii"))
                    found = figure_run(raw, idea)
                    path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                    errors = [f for f in found if f[1] == path]
                    rule = "S14" if idea else "S15"
                    self.assertEqual(len(errors), 1, errors)
                    self.assertEqual(errors[0][:3], (rule, path, 0))
                    self.assertIn("not well-formed SVG: undefined entity", errors[0][3])
                    self.assert_continued(found, idea, "undefined entity", rule=rule)

    def test_dtd_refusal_with_python_parser(self):
        """Use the real fallback in isolation, including a temporary copy of I.1."""
        code = """
import runpy
import sys
import unittest
sys.modules['_elementtree'] = None
ns = runpy.run_path(sys.argv[1])
style = ns['style']
assert sys.flags.isolated
assert hasattr(style.ET.XMLParser(), 'parser'), 'not the pure-Python parser'
case = ns['SvgGate']()
for idea in (False, True):
    suffix = '-idea.svg' if idea else '.svg'
    source = (style.ROOT / 'figures' / 'I' / ('01' + suffix)).read_bytes()
    raw = b'<!DOCTYPE svg [<!ENTITY family "Georgia">]>' + source.replace(
        b'font-family="Georgia, \\'Times New Roman\\', serif"', b'font-family="&family;"')
    assert b'font-family="&family;"' in raw
    found = ns['figure_run'](raw, idea)
    path = 'figures/I/01' + suffix
    case.assertEqual([f for f in found if f[1] == path], [('S26', path, 0, ns['DTD_REFUSAL'])])
    case.assert_continued(found, idea, ns['DTD_REFUSAL'])
names = (
    'test_dtd_refusal_and_continuation',
    'test_dtd_references_and_continuation',
    'test_dtd_markup_anywhere_and_continuation',
    'test_dtd_in_euclid_reference_is_reported_once_and_continues',
    'test_drawn_letters_refuses_dtd',
    'test_dtd_refusal_precedes_internal_subset',
    'test_svg_root_source_refuses_declarations_before_parser',
    'test_undeclared_references_without_dtd_and_continuation',
    'test_character_references_keep_the_resolved_value_gate',
    'test_xml_declarations_and_comments_are_admitted',
)
suite = unittest.TestSuite(ns['SvgGate'](name) for name in names)
suite.addTest(ns['Modern']('test_companion_reader_refuses_internal_dtd'))
suite.addTest(ns['Modern']('test_companion_letter_keeps_internal_newline'))
result = unittest.TextTestRunner().run(suite)
sys.exit(not result.wasSuccessful())
"""
        result = subprocess.run([sys.executable, "-I", "-c", code, str(Path(__file__).resolve())],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_dtd_in_euclid_reference_is_reported_once_and_continues(self):
        for declaration, family in DTD_CASES:
            with self.subTest(declaration=declaration):
                raw = dtd_figure(False, declaration, family)
                found = figure_run(figure_fixture(True), True, reference=raw)
                path = "figures/I/01.svg"
                self.assertEqual([f for f in found if f[1] == path],
                                 [("S26", path, 0, DTD_REFUSAL)])
                self.assert_continued(found, True, DTD_REFUSAL, first_path=path)

    def test_drawn_letters_refuses_dtd(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "01.svg"
            for declaration, family in DTD_CASES:
                with self.subTest(declaration=declaration):
                    path.write_bytes(dtd_figure(False, declaration, family))
                    self.assertIsNone(style.drawn_letters(path))

    def test_dtd_refusal_precedes_internal_subset(self):
        # Refuse even before any declaration or reference in the subset is read.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "01.svg"
            path.write_bytes(b"<!DOCTYPE svg [")
            with self.assertRaises(ET.ParseError) as raised:
                style.parse_svg(path)
            self.assertEqual(str(raised.exception), DTD_REFUSAL)

    def test_svg_root_source_refuses_declarations_before_parser(self):
        path = style.ROOT / "figures/I/01-modern.svg"
        for declaration in (b"<!DOCTYPE svg [", b'<!ENTITY label "A">'):
            for encoding in ("utf-8", "utf-16", "utf-32-le", "utf-32-be"):
                with self.subTest(declaration=declaration, encoding=encoding), \
                        patch.object(style, "failures", []), \
                        patch.object(ET, "XMLParser", side_effect=AssertionError("parser built")), \
                        patch.object(Path, "read_bytes", side_effect=AssertionError("file reread")):
                    raw = declaration.decode("ascii").encode(encoding)
                    self.assertIsNone(style.svg_root(path, raw))
                    self.assertEqual(style.failures,
                                     [("S26", "figures/I/01-modern.svg", 0, DTD_REFUSAL)])

    def test_character_references_keep_the_resolved_value_gate(self):
        for idea in (False, True):
            for family in (b"&#71;eorgia", b"&#x47;eorgia", b"&#83;erif"):
                with self.subTest(idea=idea, family=family):
                    raw = ET.tostring(figure_fixture(idea)).replace(
                        b'font-family="Georgia"', b'font-family="' + family + b'"')
                    raw = raw.replace(b">A<", b">&#65;<")
                    found = figure_run(raw, idea)
                    path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                    expected = [("S26", path, 0, svg_refusal("svg", "font-family", "Serif"))] \
                        if family == b"&#83;erif" else []
                    self.assertEqual([f for f in found if f[1] == path], expected)

    def test_xml_declarations_and_comments_are_admitted(self):
        for idea in (False, True):
            with self.subTest(idea=idea):
                body = ET.tostring(figure_fixture(idea)).replace(b">", b"><!-- figure -->", 1)
                found = figure_run(b'<?xml version="1.0"?>\n' + body, idea)
                path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                self.assertFalse([f for f in found if f[1] == path], found)
                next_path = "figures/I/02" + ("-idea.svg" if idea else ".svg")
                self.assertTrue(any(r == "S26" and p == next_path and "canvas's edge" in msg
                                    for r, p, _, msg in found), found)

    def test_malformed_euclid_figure_is_reported_once(self):
        bad_figures = (
            b"<svg>",
            b'<?xml version="1.0" encoding="unknown-encoding"?><svg/>',
        )
        for raw in bad_figures:
            with self.subTest(raw=raw):
                found = figure_run(figure_fixture(True), True, reference=raw)
                first = [f for f in found if f[0] == "S15" and f[1] == "figures/I/01.svg"]
                self.assertEqual(len(first), 1, found)
                self.assertIn("not well-formed SVG", first[0][3])
                self.assert_continued(found, True, "not well-formed SVG",
                                      first_path="figures/I/01.svg", rule="S15")

    def test_checker_errors_are_not_decoder_failures(self):
        for idea in (False, True):
            for error in (LookupError("checker defect"), ValueError("checker defect"),
                          UnicodeDecodeError("utf-8", b"\xff", 0, 1, "checker defect")):
                for function in ("supported_svg", "glyph_hull"):
                    with self.subTest(idea=idea, error=type(error).__name__, function=function), \
                            patch.object(style, function, side_effect=error):
                        with self.assertRaises(type(error)):
                            figure_run(figure_fixture(idea), idea)
            # getroot runs after the parser's exception boundary, too.
            with patch.object(ET, "parse") as parse:
                parse.return_value.getroot.side_effect = ValueError("checker defect")
                with self.assertRaisesRegex(ValueError, "checker defect"):
                    figure_run(figure_fixture(idea), idea)

    def test_nested_svg(self):
        for idea in (False, True):
            root = figure_fixture(idea)
            svg_sub(root, "svg", {"viewBox": "0 0 400 300"})
            self.assert_refused(root, idea, "<svg>")

    def test_numeric_ranges(self):
        for idea in (False, True):
            for attr in ("r", "rx", "ry", "width", "height", "font-size", "stroke-width"):
                with self.subTest(idea=idea, attr=attr):
                    root = figure_fixture(idea)
                    svg_sub(root, "rect", {attr: "-0.1"})
                    self.assert_refused(root, idea, attr)
            for attr in ("fill-opacity", "stroke-opacity"):
                for value in ("-0.1", "1.1"):
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        svg_sub(root, "g", {attr: value})
                        self.assert_refused(root, idea, attr)
            for attr, values in (
                    ("viewBox", ("0 0 400", "0 0 400 300 1", "0 0 0 300", "0 0 400 0",
                                 "0 0 -1 300", "0 0 400 -1")),
                    ("points", ("10 20 30",)),
                    ("stroke-dasharray", ("-1 2", "1 -2"))):
                for value in values:
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        root.set(attr, value)
                        self.assert_refused(root, idea, attr)

    def test_dasharray_requires_a_positive_component(self):
        for idea in (False, True):
            path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
            for value in ("0", "0 0", "0.0", "0, 0.00"):
                with self.subTest(idea=idea, value=value):
                    root = figure_fixture(idea)
                    group = svg_sub(root, "g", {"stroke-dasharray": value})
                    self.assertEqual(
                        [f for f in figure_findings(root, idea) if f[0] == "S26"],
                        [("S26", path, 0,
                          svg_refusal(style.tag(group), "stroke-dasharray", value))])
            for value in ("none", "1", "0 2", "1, 2 3,4"):
                with self.subTest(idea=idea, value=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "g", {"stroke-dasharray": value})
                    self.assertEqual(
                        [f for f in figure_findings(root, idea) if f[0] == "S26"], [])

    def test_zero_opacity_on_shapes_and_ancestor_groups(self):
        """Invisible paint is refused where set, while main's positive values remain."""
        for idea in (False, True):
            for attr in ("fill-opacity", "stroke-opacity"):
                for placement in ("shape", "group"):
                    for value in ("0", "0.0"):
                        with self.subTest(idea=idea, attr=attr, placement=placement,
                                          value=value):
                            root = figure_fixture(idea)
                            parent = root if placement == "shape" else svg_sub(root, "g")
                            shape = svg_sub(parent, "circle", {
                                "cx": "250", "cy": "230", "r": "10", "fill": "none"})
                            target = shape if placement == "shape" else parent
                            target.set(attr, value)
                            path = "figures/I/01" + ("-idea.svg" if idea else ".svg")
                            self.assertEqual(figure_findings(root, idea), [
                                ("S26", path, 0, svg_refusal(style.tag(target), attr, value))])
                for value in ("0.1", "0.55", "1"):
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        group = svg_sub(root, "g", {attr: value})
                        svg_sub(group, "circle", {
                            "cx": "250", "cy": "230", "r": "10", "fill": "none"})
                        self.assertEqual(figure_findings(root, idea), [])

    def test_exact_keywords_and_whitespace(self):
        for idea in (False, True):
            for attr, word in (("font-weight", "normal"), ("font-style", "normal"),
                               ("text-anchor", "start"), ("font-family", "Georgia"),
                               ("stroke-linecap", "butt"), ("stroke-linejoin", "miter"),
                               ("fill", "none"), ("stroke", "none"), ("stroke-dasharray", "none")):
                for value in (word.upper(), " " + word, word + " ", "\t" + word,
                              word + "\n", "\u00a0" + word):
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        svg_sub(root, "g", {attr: value})
                        self.assert_refused(root, idea, attr)
            for space in ("\u00a0", "\u2003", "\v", "\f"):
                for attr, value in (("x1", space + "10"), ("x1", "10" + space),
                                    ("points", f"0{space}0"), ("viewBox", f"0 0{space}400 300"),
                                    ("stroke-dasharray", f"1{space}2"),
                                    ("transform", f"translate(0{space}0)"),
                                    ("d", f"M100{space}100 L200 100")):
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        svg_sub(root, "g", {attr: value})
                        self.assert_refused(root, idea, attr)
            root = figure_fixture(idea)
            svg_sub(root, "line", {"x1": " \t\r\n10 \t\r\n",
                          "stroke-dasharray": "1,\t2\r\n3 4"})
            self.assertEqual(figure_findings(root, idea), [])

    def test_arc_flags_and_close_arguments(self):
        for idea in (False, True):
            paths = ["M100 100 Z 200 100", "M100 100 Z 0",
                     "M100 100 A10 -10 0 0 0 120 100"]
            for flag in ("2", "-1", "0.0", "1.0", "+1", "01"):
                paths += [f"M100 100 A10 10 0 {flag} 0 120 100",
                          f"M100 100 A10 10 0 0 {flag} 120 100"]
            for value in paths:
                with self.subTest(idea=idea, d=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "path", {"d": value})
                    self.assert_refused(root, idea, "<path>", "d")

    def test_arcs_that_draw_no_arc(self):
        """SVG's implementation notes (F.6.2) omit an arc whose ends are one point, and draw
        one with a radius of 0 as a straight line; S26 refuses both, wherever the path
        stands when the arc begins (#172)."""
        for idea in (False, True):
            for value, why in (
                    ("M100 100 A10 10 0 0 1 100 100", "draws nothing"),
                    ("M100 100 A10 10 0 1 0 100.0 100", "draws nothing"),
                    ("M100 100 L120 100 A10 10 0 0 1 120 100", "draws nothing"),
                    ("M100 100 H120 V110 A10 10 0 0 1 120 110", "draws nothing"),
                    ("M100 100 L120 100 Z A10 10 0 0 1 100 100", "draws nothing"),
                    ("M90 90 100 100 A10 10 0 0 1 100 100", "draws nothing"),
                    ("M100 100 C110 90 120 90 130 100 A10 10 0 0 1 130 100", "draws nothing"),
                    ("M100 100 A10 10 0 0 1 120 100 10 10 0 0 1 120 100", "draws nothing"),
                    ("M100 100 A0 10 0 0 1 100 100", "draws nothing"),
                    ("M100 100 A0 10 0 0 1 120 100", "straight line"),
                    ("M100 100 A10 0 0 1 1 120 100", "straight line"),
                    ("M100 100 A-0 10 0 0 1 120 100", "straight line"),
                    ("M100 100 L120 100 A0.0 0 0 0 1 140 100", "straight line")):
                with self.subTest(idea=idea, d=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "path", {"d": value})
                    self.assert_refused(root, idea, "<path>", "d", why)
            for value in ("M100 100 A10 10 0 0 1 100.5 100", "M100 100 A1 1 0 1 1 120 100",
                          "M100 100 L120 100 A10 10 0 0 1 100 100",
                          "M100 100 L120 100 Z A10 10 0 0 1 120 100",
                          "M90 90 100 100 A10 10 0 0 1 90 90"):
                with self.subTest(idea=idea, d=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "path", {"d": value})
                    self.assertEqual([f for f in figure_findings(root, idea) if f[0] == "S26"], [])

    def test_arc_flags_always_draw(self):
        """Why S26 need not refuse a choice of the large-arc and sweep flags: two distinct
        ends and positive radii, enlarged when they cannot reach the ends (F.6.6), lie on
        two ellipses, or on one when the radii only just reach; each choice of the flags
        takes one arc of them, from the one end to the other (F.6.5). On one ellipse both
        arcs are halves and the large-arc flag changes nothing."""
        # (the radii, whether they reach the ends with room to spare): 1 is enlarged to
        # 10, and 10 only just reaches the ends, 20 apart.
        for rx, ry, ample in ((1, 1, False), (10, 10, False), (30, 5, True), (12, 40, True)):
            arcs = {}
            for large in (0, 1):
                for sweep in (0, 1):
                    with self.subTest(rx=rx, ry=ry, large=large, sweep=sweep):
                        points = style.arc_points(100, 100, rx, ry, 0, large, sweep, 120, 100)
                        self.assertEqual(points[-1], (120, 100))
                        # The sweep flag takes the side of the chord: in SVG's y, which
                        # runs down, 1 above it and 0 below.
                        self.assertEqual({y < 100 for _, y in points[:-1]}, {sweep == 1})
                        arcs[large, sweep] = points
            for sweep in (0, 1):
                with self.subTest(rx=rx, ry=ry, sweep=sweep):
                    small, large_arc = arcs[0, sweep], arcs[1, sweep]
                    if ample:
                        self.assertGreater(len(large_arc), len(small))
                    else:
                        self.assertEqual(len(large_arc), len(small))
                        for p, q in zip(small, large_arc):
                            self.assertAlmostEqual(math.dist(p, q), 0, places=9)

    def test_supported_spellings_and_continuation(self):
        for idea in (False, True):
            root = figure_fixture(idea)
            for transform in ("translate(+0,-0)", "translate(0 0)",
                              "rotate(0 150 100)", "rotate(0,150,100)"):
                group = svg_sub(root, "g", {"transform": transform, "font-style": "normal",
                                      "font-weight": "normal", "text-anchor": "start",
                                      "stroke-linecap": "butt", "stroke-linejoin": "miter"})
                svg_sub(group, "polyline", {"points": "10,20 30,40", "stroke-dasharray": "none"})
                svg_sub(group, "line", {"x1": "+10.00", "y1": "-0", "stroke-width": "0",
                              "stroke-dasharray": "1, 2   3,4"})
            self.assertEqual([f for f in figure_findings(root, idea) if f[0] == "S26"], [])
            svg_sub(root, "image")
            svg_sub(root, "g", {"style": "fill:none", "unknown": "bad"})
            self.assert_refused(root, idea, "<image>", "style", "unknown")
            self.assertEqual(figure_findings(figure_fixture(idea), idea), [])

    def test_elements_and_attributes(self):
        for idea in (False, True):
            for name in ("style", "use", "image", "foreignObject", "animate", "tspan",
                         "defs", "marker", "unknown", "{urn:other}line"):
                with self.subTest(idea=idea, element=name):
                    root = figure_fixture(idea)
                    svg_sub(root, name)
                    self.assert_refused(root, idea, f"<{name}>")
            for name in ("style", "class", "id", "onclick", "filter", "clip-path",
                         "mask", "vector-effect", "dx", "dy", "fill-rule",
                         "stroke-miterlimit", "unknown", "{urn:other}x"):
                with self.subTest(idea=idea, attribute=name):
                    root = figure_fixture(idea)
                    svg_sub(root, "g", {name: "none"})
                    self.assert_refused(root, idea, "<g>", name)

    def test_plain_decimals_and_lists(self):
        for idea in (False, True):
            for attr in ("x1", "stroke-width", "fill-opacity", "stroke-opacity", "font-size"):
                for value in ("0 px", "1px", "1e2", ".5", "1.", "1 2", "1,2",
                              "--1", "+", "", "NaN", "inf", "١", "9" * 400):
                    with self.subTest(idea=idea, attr=attr, value=value[:30]):
                        root = figure_fixture(idea)
                        svg_sub(root, "line", {attr: value})
                        self.assert_refused(root, idea, "<line>", attr)
            for attr in ("points", "viewBox", "stroke-dasharray"):
                for value in ("0 0 400x 300", "0 0 4e2 300", "0 0 .4 300", "0,,0",
                              ",0 0", "0 0,", "0 0px", "0;0", "0 0 inherit", ""):
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        root.set(attr, value)
                        self.assert_refused(root, idea, "<svg>", attr)

    def test_transforms(self):
        for idea in (False, True):
            for value in ("translate(-80px,0)", "translate(-80,0,0)",
                          "translate(-80,0)junk", "translate(-80,0) rotate(0)",
                          "translate(-80)", "translate(-80,,0)", "translate(-8e1,0)",
                          "translate(-80 0", "translate(-80,0))", "translate(-80;0)",
                          "translate()", "rotate(0)", "rotate(0 1)", "rotate(0 1 2 3)",
                          "scale(1)", "scale(1,2)", "matrix(1 0 0 1 0 0)", "skewX(0)", ""):
                with self.subTest(idea=idea, transform=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "line", {"x1": "352", "y1": "150.8", "x2": "364",
                                  "y2": "150.8", "stroke": "#222222" if idea else "#3b2f2f",
                                  "stroke-width": "1.6", "transform": value})
                    self.assert_refused(root, idea, "<line>", "transform")

    def test_css_coordinates_and_paths(self):
        for idea in (False, True):
            for kind, attrs in (
                    ("line", {"x1": "352", "y1": "150.8", "x2": "364", "y2": "150.8",
                              "style": "y1:210px;y2:210px"}),
                    ("path", {"d": "M352 150.8 L364 150.8",
                              "style": "d:path('M352 210 L364 210')"}),
                    ("text", {"style": "y:220px"})):
                with self.subTest(idea=idea, kind=kind):
                    root = figure_fixture(idea)
                    if kind == "text":
                        el = next(e for e in root.iter() if style.text_of(e) == "E")
                    else:
                        el = svg_sub(root, kind, {
                            "stroke": "#222222" if idea else "#3b2f2f", "stroke-width": "1.6"})
                    el.attrib.update(attrs)
                    self.assert_refused(root, idea, f"<{kind}>", "style")

    def test_whitespace_width(self):
        for idea in (False, True):
            for placement in ("attribute", "style", "inherited"):
                with self.subTest(idea=idea, placement=placement):
                    root = figure_fixture(idea)
                    parent = svg_sub(root, "g") if placement == "inherited" else root
                    line = svg_sub(parent, "line", {
                        "x1": "352", "y1": "150.8", "x2": "364", "y2": "150.8",
                        "stroke": "#222222" if idea else "#3b2f2f"})
                    target = parent if placement == "inherited" else line
                    attr = "style" if placement == "style" else "stroke-width"
                    target.set(attr, "stroke-width:0 px" if placement == "style" else "0 px")
                    self.assert_refused(root, idea, f"<{style.tag(target)}>", attr)

    def test_keywords(self):
        for idea in (False, True):
            for attr in ("text-anchor", "stroke-linecap", "stroke-linejoin", "font-style",
                         "font-weight", "font-family", "fill", "stroke", "stroke-dasharray"):
                for value in ("inherit", "initial", "unset", "revert", "revert-layer", "unknown"):
                    with self.subTest(idea=idea, attr=attr, value=value):
                        root = figure_fixture(idea)
                        svg_sub(root, "g", {attr: value})
                        self.assert_refused(root, idea, "<g>", attr)
            for attr, value in (("stroke-linecap", "square"), ("stroke-linejoin", "bevel"),
                                ("font-style", "oblique"), ("font-weight", "700")):
                with self.subTest(idea=idea, attr=attr, value=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "g", {attr: value})
                    self.assert_refused(root, idea, attr)

    def test_explicit_inheritance(self):
        for idea in (False, True):
            for attr, value, shape in (
                    ("text-anchor", "middle", '<line x1="145" y1="85" x2="145" y2="105"/>'),
                    ("stroke-linejoin", "miter", '<polyline points="130,160 155,103 180,160"/>')):
                with self.subTest(idea=idea, attribute=attr):
                    root = figure_fixture(idea)
                    group = svg_sub(root, "g", {attr: value, "stroke-width": "1.6",
                                          "stroke": "#222222" if idea else "#3b2f2f"})
                    drawn = svg_element(shape)
                    group.append(drawn)
                    e = next(el for el in root.iter() if style.tag(el) == "text"
                             and style.text_of(el) == "E")
                    e.attrib.update(x="150", y="100", **{"font-size": "17", "font-style": "normal",
                                                        "text-anchor": "start"})
                    if attr == "text-anchor":
                        next(el for el in root.iter() if e in list(el)).remove(e)
                        group.append(e)
                    target = e if attr == "text-anchor" else drawn
                    target.set(attr, "inherit")
                    self.assert_refused(root, idea, attr)
                    target.set(attr, value)
                    found = [f[3] for f in figure_findings(root, idea) if f[0] == "S26"]
                    self.assertTrue(any("letter E" in f for f in found), found)

    def test_paths(self):
        for idea in (False, True):
            for value in ("M100 100 Q150 50 200 100", "M100 100 S150 50 200 100",
                          "M100 100 T200 100", "m100 100 l100 0", "M100 100 a1 1 0 0 0 1 1",
                          "M100 100 R200 100", "M100 100 L200", "L100 100", "M100px 100",
                          "M1e2 100 L200 100", "M100 100 A10 10 0 2 0 120 100",
                          "M100 100 A-10 10 0 0 0 120 100", "M100 100 L200 100 junk"):
                with self.subTest(idea=idea, d=value):
                    root = figure_fixture(idea)
                    svg_sub(root, "path", {"d": value})
                    self.assert_refused(root, idea, "<path>", "d")

    def test_bezier_clearance(self):
        # The quadratic in the review, and its exact cubic degree elevation.
        paths = ("M100,182.5507421875 Q150,27.8632421875 200,173.1757421875",
                 "M100,182.5507421875 C133.33333333333334,79.4257421875 "
                 "166.66666666666666,76.3007421875 200,173.1757421875",
                 # Its minimum at t = 0.5173 falls between subdivision points;
                 # exact clearance 1.99999 requires subtracting the chord error.
                 "M100,183.079777 C133.33333333333334,79.619777 "
                 "166.66666666666666,76.159777 200,172.699777")
        for idea in (False, True):
            for d in paths:
                with self.subTest(idea=idea, d=d):
                    root = figure_fixture(idea)
                    svg_sub(root, "path", {"d": d, "fill": "none", "stroke-width": "1.6",
                                  "stroke": "#222222" if idea else "#3b2f2f"})
                    e = next(el for el in root.iter() if style.tag(el) == "text"
                             and style.text_of(el) == "E")
                    e.attrib.update(x="150", y="100", **{"font-size": "17", "font-style": "normal",
                                                        "text-anchor": "start"})
                    if "Q" in d:
                        self.assert_refused(root, idea, "<path>", "d")
                    else:
                        found = [f[3] for f in figure_findings(root, idea) if f[0] == "S26"]
                        self.assertTrue(any("letter E" in f and "from a path" in f for f in found), found)
                        root[-1].set("transform", "translate(0,0.1)")
                        self.assertEqual([f for f in figure_findings(root, idea) if f[0] == "S26"], [])

    def test_long_malformed_lists(self):
        # A subprocess bounds even the old parser's quadratic failure time.
        code = f"""
import runpy
ns = runpy.run_path({str(Path(__file__).resolve())!r})
for idea in (False, True):
    for attr in ('points', 'viewBox', 'stroke-dasharray'):
        root = ns['figure_fixture'](idea)
        root.set(attr, '0 0 ' + '9' * 32000 + 'x 300')
        found = ns['figure_findings'](root, idea)
        assert any(f[0] == 'S26' and attr in f[3] for f in found), found
"""
        subprocess.run([sys.executable, "-I", "-c", code], check=True, timeout=2,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class Clearance(unittest.TestCase):
    """The clearance cases, and a letter drawn more than once."""

    def test_curve_join_figure_entry_points(self):
        """True curve tangents put mitres near E; round joins clear it."""
        paths = (
            # The reviewer's cubic; its last control point is almost its endpoint.
            "M150 90 C150 95 149.9999 100 150 100 L141.339746 105",
            # Reversed, and with one or both endpoint controls coincident.
            "M141.339746 105 L150 100 C149.9999 100 150 95 150 90",
            "M150 90 C149.9999 100 150 100 150 100 L141.339746 105",
            "M141.339746 105 L150 100 C150 100 149.9999 100 150 90",
            "M140 100 C150 100 150 100 150 100 L141.339746 105",
            "M141.339746 105 L150 100 C150 100 150 100 140 100",
            # An arc with the same end tangent, reversed, rotated and enlarged.
            "M140 90 A10 10 0 0 0 150 100 L141.339746 105",
            "M141.339746 105 L150 100 A10 10 0 0 1 140 90",
            "M140 80 A20 10 90 0 0 150 100 L141.339746 105",
            "M150 98 A0.1 0.1 0 0 0 150 100 L141.339746 105",
            # The outgoing segment can itself be a curve.
            "M140 90 A10 10 0 0 0 150 100 C147 101.7320508 144 105 141.339746 105",
            # Z supplies a segment, and joins the last segment to the first.
            "M141.339746 105 L140 90 A10 10 0 0 0 150 100 Z",
            "M150 100 C150 100 149.9999 100 150 90 L141.339746 105 Z",
            # A directionless segment does not break a join.
            "M150 90 C150 95 149.9999 100 150 100 L150 100 "
            "C150 100 150 100 150 100 L141.339746 105",
        )
        for idea in (False, True):
            for d in paths:
                for join in (None, "miter", "round"):
                    with self.subTest(idea=idea, d=d, join=join):
                        root = figure_fixture(idea)
                        curve = svg_sub(root, "path", {
                            "d": d, "fill": "none",
                            "stroke": "#222222" if idea else "#3b2f2f",
                            "stroke-width": "1.6"})
                        if join is not None:
                            curve.set("stroke-linejoin", join)
                        e = next(el for el in root.iter()
                                 if style.tag(el) == "text" and style.text_of(el) == "E")
                        for label in root.iter():
                            if style.tag(label) == "text":
                                label.set("font-style", "normal")
                        e.attrib.update(x="154.3" if idea and "A" in d else "154.2", y="99.4",
                                        **{"text-anchor": "start", "font-family": "Georgia"})
                        found = figure_findings(root, idea)
                        if join == "round":
                            self.assertEqual(found, [])
                        else:
                            self.assertEqual(len(found), 1, found)
                            self.assertEqual(found[0][0], "S26")
                            self.assertIn("letter E", found[0][3])
                            self.assertIn("from a path, under 2", found[0][3])
        # Nor does an omitted arc, whose ends are one point: it is measured as the path
        # without it, the last case above. The figure entry points refuse it, since SVG
        # draws nothing for it (#172).
        omitted = ("M150 90 C150 95 149.9999 100 150 100 L150 100 "
                   "C150 100 150 100 150 100 A10 10 0 0 0 150 100 L141.339746 105")
        for join in (None, "miter", "round"):
            with self.subTest(d=omitted, join=join):
                linejoin = "" if join is None else f' stroke-linejoin="{join}"'
                measured = [
                    list(style.strokes(style.ROOT / "figures" / "case.svg", ET.fromstring(
                        f'<svg stroke="#3b2f2f" stroke-width="1.6" fill="none"{linejoin}>'
                        f'<path d="{d}"/></svg>')))
                    for d in (omitted, paths[-1])]
                self.assertTrue(measured[0])
                self.assertEqual(measured[0], measured[1])
        for idea in (False, True):
            with self.subTest(idea=idea, d=omitted):
                root = figure_fixture(idea)
                svg_sub(root, "path", {"d": omitted, "fill": "none", "stroke-width": "1.6",
                                       "stroke": "#222222" if idea else "#3b2f2f"})
                found = figure_findings(root, idea)
                self.assertTrue(any(f[0] == "S26" and "<path> d" in f[3]
                                    and "draws nothing" in f[3] for f in found), found)

    def test_curve_subdivisions_have_no_joins(self):
        """A single curve has no joins at its sampled chords, nor across a moveto."""
        shapes = (
            '<path d="M100 100 C100 50 150 50 150 100"/>',
            '<path d="M140 90 A10 10 0 0 0 150 100"/>',
            '<rect x="100" y="100" width="50" height="50" rx="10"/>',
            '<path d="M100 100 C100 50 150 50 150 100 M150 100 L140 110"/>',
        )
        for shape in shapes:
            with self.subTest(shape=shape):
                root = ET.fromstring(
                    '<svg stroke="#3b2f2f" stroke-width="1.6" fill="none">'
                    + shape + '</svg>')
                pieces = list(style.strokes(style.ROOT / "figures" / "case.svg", root))
                self.assertTrue(any(len(run) > 3 for _, run, _ in pieces), pieces)
                self.assertTrue(all(half is not None for _, _, half in pieces),
                                "flattening or moveto introduced a filled join")

    def test_width_spellings(self):
        """Plain widths keep their clearance; CSS, units and exponents are refused."""
        for width in ("3", "3e0", "+3", "3px", "+3e0px"):
            for placement in ("attribute", "style", "inherited"):
                with self.subTest(width=width, placement=placement):
                    attrs = f'stroke-width="{width}"'
                    if placement == "style":
                        attrs = f'style="stroke-width:{width}"'
                    drawn = (f'<line x1="145" y1="103" x2="165" y2="103" '
                             f'stroke="#222222" {attrs if placement != "inherited" else ""}/>')
                    if placement == "inherited":
                        drawn = f'<g {attrs}>{drawn}</g>'
                    want = ["letter A at (150, 100) stands 1.5 from a line, under 2: move it clear"]
                    if placement == "style":
                        want = [svg_refusal("line", "style", f"stroke-width:{width}")]
                    elif width not in ("3", "+3"):
                        want = [svg_refusal("g" if placement == "inherited" else "line",
                                            "stroke-width", width)]
                    self.assertEqual(s26_findings(drawn, letter("A", font_style="normal", size=14)),
                                     want)

    def test_text_offsets(self):
        """Coordinates and translations place the capital; unused offsets and scales fail."""
        drawn = '<line x1="150" y1="92" x2="160" y2="92" stroke="#222222" stroke-width="2"/>'
        for transform in ("", 'transform="translate(25,20)"',
                          'transform="translate(25,20) scale(2,1.5)"'):
            for position, want in (
                    ('x="150" y="100"', True),
                    ('x="150" y="120" dy="-20"', True),
                    ('x="130" y="100" dx="+2e1"', True),
                    ('x="130" y="120" dx="20" dy="-20"', True),
                    ('x="150" y="120"', False),
                    ('x="150" y="100" dy="20"', False),
                    ('x="170" y="100"', False),
                    ('x="150" y="100" dx="20"', False)):
                with self.subTest(transform=transform, position=position):
                    text = f'<text {position} font-size="14" font-style="normal">A</text>'
                    found = s26_findings(f'<g {transform}>{drawn}{text}</g>', "")
                    refused = []
                    if "scale" in transform:
                        refused.append(svg_refusal("g", "transform", "translate(25,20) scale(2,1.5)"))
                    for attr, value in ET.fromstring(text).attrib.items():
                        if attr in ("dx", "dy"):
                            refused.append(svg_refusal("text", attr, value))
                    if refused:
                        self.assertEqual(found, refused)
                    else:
                        self.assertEqual(bool(found), want, found)

    def test_stroke_joins(self):
        """A mitre reaches H and a round join clears it; unused join syntax is refused."""
        shapes = (
            '<polyline points="130,160 155,104 180,160" {attrs}/>',
            '<polyline points="180,160 155,104 130,160" {attrs}/>',
            '<polyline points="130,160 155,104 155,104 180,160" {attrs}/>',
            '<path d="M130 160 L155 104 L180 160" {attrs}/>',
            '<path d="M155 104 L180 160 L130 160 Z" {attrs}/>',
            '<polygon points="155,104 180,160 130,160" {attrs}/>',
        )
        for shape in shapes:
            for join, want in (("", True), ('stroke-linejoin="miter"', True),
                               ('stroke-linejoin="round"', False),
                               ('stroke-linejoin="bevel"', False),
                               ('stroke-miterlimit="2"', False),
                               ('stroke-miterlimit="+3e0"', True)):
                for inherited in (False, True):
                    with self.subTest(shape=shape, join=join, inherited=inherited):
                        attrs = f'stroke="#222222" stroke-width="3" fill="none" {join}'
                        drawn = (f'<g {attrs}>{shape.format(attrs="")}</g>' if inherited
                                 else shape.format(attrs=attrs))
                        found = s26_findings(drawn, letter("H", font_style="normal"))
                        refused = [svg_refusal("g" if inherited else style.tag(ET.fromstring(drawn)),
                                               k, v) for k, v in ET.fromstring(f"<g {join}/>").attrib.items()
                                   if k == "stroke-miterlimit" or v == "bevel"]
                        if refused:
                            self.assertEqual(found, refused)
                        else:
                            self.assertEqual(bool(found), want, found)
                            if want:
                                self.assertIn("stands 0.3 from", found[0])

    def test_square_caps(self):
        """Unused square caps, CSS and scales fail; supported round and butt caps clear H."""
        shapes = (
            '<line x1="163.2" y1="102.5" x2="183.2" y2="102.5" {attrs}/>',
            '<line x1="183.2" y1="102.5" x2="163.2" y2="102.5" {attrs}/>',
            '<polyline points="163.2,102.5 163.2,102.5 183.2,102.5" {attrs}/>',
            '<path d="M163.2 102.5 L183.2 102.5" {attrs}/>',
            '<line x1="163.2" y1="102.5" x2="163.2" y2="102.5" {attrs}/>',
            '<path d="M163.2 102.5 L163.2 102.5" {attrs}/>',
            '<path d="M163.2 102.5 Z" {attrs}/>',
            '<path d="M250 200 L260 200 M163.2 102.5 Z" {attrs}/>',
        )
        for shape in shapes:
            for cap in ("square", "round", "butt"):
                for placement in ("attribute", "style", "inherited"):
                    for transform in ("", "rotate(30,150,100)",
                                      "translate(10,10) scale(1.1,1.2)"):
                        with self.subTest(shape=shape, cap=cap, placement=placement,
                                          transform=transform):
                            caps = (f'style="stroke-linecap:{cap}"' if placement == "style"
                                    else f'stroke-linecap="{cap}"')
                            attrs = 'stroke="#222222" stroke-width="3" fill="none"'
                            drawn = (f'<g {caps}>{shape.format(attrs=attrs)}</g>'
                                     if placement == "inherited"
                                     else shape.format(attrs=f"{attrs} {caps}"))
                            group_transform = f' transform="{transform}"' if transform else ""
                            found = s26_findings(
                                f'<g{group_transform}>{drawn}'
                                + letter("H", font_style="normal", size=14) + '</g>', "")
                            refused = []
                            if "scale" in transform:
                                refused.append(svg_refusal("g", "transform", transform))
                            kind = "g" if placement == "inherited" else style.tag(ET.fromstring(drawn))
                            if placement == "style":
                                refused.append(svg_refusal(kind, "style", f"stroke-linecap:{cap}"))
                            elif cap == "square":
                                refused.append(svg_refusal(kind, "stroke-linecap", cap))
                            self.assertEqual(found, refused)

    def test_square_cap_boundaries(self):
        """Unused square caps are refused on open, closed and empty subpaths alike."""
        shape = ('<line x1="163.2" y1="102.5" x2="183.2" y2="102.5" '
                 'style="stroke-linecap:{cap}"/>')
        for drawn, want in (
                (shape.format(cap="round"), False),
                (shape.format(cap="butt"), False),
                ('<g stroke-linecap="butt">' + shape.format(cap="square") + '</g>', True),
                ('<path d="M163.2 102.5"/>', False),
                ('<path d="M163.2 102.5 L183.2 102.5 L183.2 122.5 Z"/>', False),
                ('<path d="M163.2 102.5 L183.2 102.5 L183.2 122.5 L163.2 102.5"/>', True),
                ('<polygon points="163.2,102.5 183.2,102.5 183.2,122.5"/>', False)):
            with self.subTest(drawn=drawn):
                found = s26_findings(
                    '<g stroke="#222222" stroke-width="3" stroke-linecap="square" '
                    f'stroke-linejoin="round" fill="none">{drawn}</g>',
                    letter("H", font_style="normal", size=14))
                refused = [svg_refusal("g", "stroke-linecap", "square")]
                for el in ET.fromstring(drawn).iter():
                    if "style" in el.attrib:
                        refused.append(svg_refusal(style.tag(el), "style", el.get("style")))
                self.assertEqual(found, refused)

    def test_square_caps_idea(self):
        """The reviewer's square cap is refused by the complete idea-figure check."""
        for cap in ("square", "round", "butt"):
            with self.subTest(cap=cap):
                root = ET.fromstring(
                    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" '
                    'font-family="Georgia">'
                    '<title>I.1 at a glance</title><desc>A straight line [black].</desc>'
                    '<text x="150" y="100" font-size="14" font-style="normal" '
                    'fill="#222222">H</text>'
                    '<line x1="163.2" y1="102.5" x2="183.2" y2="102.5" '
                    f'stroke="#222222" stroke-width="3" stroke-linecap="{cap}"/></svg>')
                with patch.object(style, "svg_root", return_value=root), \
                        patch.object(style, "drawn_letters", return_value={"H"}), \
                        patch.object(style, "failures", []), \
                        patch.object(style, "reports", defaultdict(list)):
                    style.check_idea(style.ROOT / "figures" / "I" / "01-idea.svg", "I.1", True)
                    want = [("S26", svg_refusal("line", "stroke-linecap", "square"))] \
                        if cap == "square" else []
                    self.assertEqual([(r, m) for r, _, _, m in style.failures], want)

    def test_zero_length_subpaths(self):
        """A closed point with round caps is drawn like a zero-length line."""
        for cap in ("butt", "round"):
            for shape in (
                    '<line x1="156" y1="94" x2="156" y2="94" {attrs}/>',
                    '<path d="M156 94 Z" {attrs}/>',
                    '<path d="M156 94 L156 94" {attrs}/>',
                    '<path d="M156 94 Z M250 200 L260 200" {attrs}/>',
                    '<path d="M250 200 L260 200 M156 94 Z" {attrs}/>'):
                with self.subTest(cap=cap, shape=shape):
                    drawn = shape.format(attrs=f'stroke="#222222" stroke-width="3" '
                                         f'stroke-linecap="{cap}" fill="none"')
                    found = s26_findings(drawn, letter("A", font_style="normal", size=14))
                    self.assertEqual(bool(found), cap == "round", found)
        # A moveto alone has no drawing command, so even round caps paint nothing.
        self.assertEqual(s26_findings(
            '<path d="M156 94" stroke="#222222" stroke-width="3" stroke-linecap="round"/>',
            letter("A", font_style="normal", size=14)), [])

    def test_join_boundaries(self):
        """Joins respect open ends and a hull wholly inside; CSS and scales are refused."""
        shape = ('<polyline points="130,160 155,104 180,160" stroke="#222222" '
                 'stroke-width="3" fill="none" {attrs}/>')
        for drawn, want in (
                ('<path d="M155 104 L180 160 L130 160 L155 104" stroke="#222222" '
                 'stroke-width="3" fill="none"/>', False),
                ('<g stroke-linejoin="round">'
                 + shape.format(attrs='style="stroke-linejoin:miter"') + '</g>', True),
                ('<g stroke-linejoin="miter">'
                 + shape.format(attrs='style="stroke-linejoin:round"') + '</g>', False),
                ('<polyline points="-95,960 155,400 405,960" stroke="#222222" '
                 'stroke-width="300" fill="none"/>', True)):
            with self.subTest(drawn=drawn):
                found = s26_findings(drawn, letter("H", font_style="normal"))
                refused = [svg_refusal(style.tag(el), "style", el.get("style"))
                           for el in ET.fromstring(drawn).iter() if "style" in el.attrib]
                if refused:
                    self.assertEqual(found, refused)
                else:
                    self.assertEqual(bool(found), want, found)
        found = s26_findings('<g transform="translate(25,10) scale(2)">'
                             + shape.format(attrs="") + letter("H", font_style="normal")
                             + '</g>', "")
        self.assertEqual(found, [svg_refusal("g", "transform", "translate(25,10) scale(2)")])

    def test_figure_entry_points(self):
        """Both production figure checks require S26's clearance finding."""
        for idea in (True, False):
            with self.subTest(idea=idea):
                ink, size = ("#222222", 14) if idea else ("#3b2f2f", 17)
                title = "I.1 at a glance" if idea else "Euclid I.1: a triangle"
                desc = "<desc>A straight line [black].</desc>" if idea else ""
                root = ET.fromstring(
                    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" '
                    f'font-family="Georgia">'
                    f'<title>{title}</title>{desc}'
                    f'<line x1="145" y1="103" x2="165" y2="103" '
                    f'stroke="{ink}" stroke-width="3"/>'
                    f'<g fill="{ink}">{letter("A", font_style="normal", size=size)}</g></svg>')
                with patch.object(style, "svg_root", return_value=root), \
                        patch.object(style, "drawn_letters", return_value={"A"}), \
                        patch.object(style, "heath_letters", return_value={"A"}), \
                        patch.object(style, "failures", []), \
                        patch.object(style, "reports", defaultdict(list)):
                    path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
                    if idea:
                        style.check_idea(path, "I.1", True)
                    else:
                        style.check_euclid(path, "I.1")
                    self.assertEqual(
                        [(rule, msg) for rule, _, _, msg in style.failures],
                        [("S26", "letter A at (150, 100) stands 1.5 from a line, "
                          "under 2: move it clear")])

    def test_use_figure_entry_points(self):
        """Both complete figure checks refuse references they do not follow."""
        for idea in (True, False):
            for use in ("", '<use href="#pointA" x="200"/>',
                        '<g><use xmlns:xlink="http://www.w3.org/1999/xlink" '
                        'xlink:href="#pointA" x="200"/></g>'):
                with self.subTest(idea=idea, use=use):
                    ink, size = ("#222222", 14) if idea else ("#3b2f2f", 17)
                    title = "I.1 at a glance" if idea else "Euclid I.1: a point"
                    desc = "<desc>A point [black].</desc>" if idea else ""
                    root = ET.fromstring(
                        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">'
                        f'<title>{title}</title>{desc}'
                        f'<text id="pointA" x="60" y="100" font-size="{size}" '
                        f'font-style="normal" fill="{ink}">A</text>{use}</svg>')
                    with patch.object(ET, "parse", return_value=ET.ElementTree(root)), \
                            patch.object(Path, "read_text", return_value="A"), \
                            patch.object(style, "failures", []), \
                            patch.object(style, "reports", defaultdict(list)):
                        name = "01-idea.svg" if idea else "01.svg"
                        path = style.ROOT / "figures" / "I" / name
                        if idea:
                            style.check_idea(path, "I.1", True)
                        else:
                            style.check_euclid(path, "I.1")
                        messages = [svg_refusal("text", "id", "pointA")]
                        if use:
                            messages.append(svg_refusal("use"))
                        want = [("S26", f"figures/I/{name}", 0, msg) for msg in messages]
                        self.assertEqual(style.failures, want)

    def test_text_children_figure_entry_points(self):
        """Positioned descendants cannot borrow the parent's clear position."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for child in ("", '<tspan x="150" y="155">A</tspan>',
                          '<tspan x="150" y="150">A</tspan>', '<tspan>A</tspan>',
                          '<a>A</a>'):
                with self.subTest(idea=idea, child=child):
                    root = figure_fixture(idea)
                    if child:
                        a = next(el for el in root.iter()
                                 if style.tag(el) == "text" and style.text_of(el) == "A")
                        a.text = None
                        a.append(svg_element(child))
                    want = [("S26", str(path.relative_to(style.ROOT)), 0,
                             "<text> may not contain element children in S26's SVG allow-list")] \
                        if child else []
                    self.assertEqual(figure_findings(root, idea), want)
            for y in ("150", "155"):
                with self.subTest(idea=idea, flat_y=y):
                    root = figure_fixture(idea)
                    a = next(el for el in root.iter()
                             if style.tag(el) == "text" and style.text_of(el) == "A")
                    a.attrib.update(x="150", y=y)
                    self.assertTrue(any(r == "S26" and "letter A" in msg
                                        for r, _, _, msg in figure_findings(root, idea)))

    def test_text_lists_figure_entry_points(self):
        """All four text coordinates must place one label, including dx and dy."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for attr in ("x", "y", "dx", "dy"):
                for suffix in ("", " 270", ",270", " +2.7e2"):
                    with self.subTest(idea=idea, attr=attr, suffix=suffix):
                        root = figure_fixture(idea)
                        a = next(el for el in root.iter()
                                 if style.tag(el) == "text" and style.text_of(el) == "A")
                        a.set(attr, a.get(attr, "0") + suffix)
                        want = [("S26", str(path.relative_to(style.ROOT)), 0,
                                 svg_refusal("text", attr, a.get(attr)))] \
                            if suffix or attr in ("dx", "dy") else []
                        self.assertEqual(figure_findings(root, idea), want)

    def test_text_payloads_figure_entry_points(self):
        """Only one Heath letter or an ASCII integer is admitted as figure text."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for text in ("AA", "A B", "A=2", "Angle A", "lowercase", "Α", "Ａ",
                         "2", "9", "16", "25"):
                for x in ("120", "120 270"):
                    with self.subTest(idea=idea, text=text, x=x):
                        root = figure_fixture(idea)
                        ink = "#222222" if idea else "#3b2f2f"
                        root.append(svg_element(
                            f'<text x="{x}" y="220" fill="{ink}">{text}</text>'))
                        want = []
                        if " " in x:
                            want.append(svg_refusal("text", "x", x))
                        if text not in ("2", "9", "16", "25"):
                            want.append(text_refusal(text))
                        expected = [("S26", str(path.relative_to(style.ROOT)), 0, msg)
                                    for msg in want]
                        self.assertEqual(figure_findings(root, idea), expected)

    def test_stroke_widths_figure_entry_points(self):
        """Unsupported widths fail explicitly; 3pt's equivalent 4 fails clearance."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for width in (None, "1", "1px", "4", "4px", "3pt", "3em", "3%",
                          "bad", "", "1..5", "1e999"):
                for placement in ("attribute", "style", "inherited"):
                    with self.subTest(idea=idea, width=width, placement=placement):
                        root = figure_fixture(idea)
                        ink, y = ("#222222", 55.5) if idea else ("#3b2f2f", 57.5)
                        line = svg_sub(root, "line", x1="194", y1=str(y), x2="206",
                                             y2=str(y), stroke=ink)
                        if width is not None:
                            if placement == "inherited":
                                root.remove(line)
                                group = svg_sub(root, "g", {"stroke-width": width})
                                group.append(line)
                            else:
                                line.set("style" if placement == "style" else "stroke-width",
                                         f"stroke-width:{width}" if placement == "style" else width)
                        found = [f for f in figure_findings(root, idea) if f[0] == "S26"]
                        if width == "4" and placement != "style":
                            self.assertEqual(len(found), 1, found)
                            self.assertIn("letter C", found[0][3])
                            self.assertIn("from a line, under 2", found[0][3])
                        else:
                            messages = []
                            if width is not None and placement == "style":
                                messages.append(svg_refusal("line", "style", f"stroke-width:{width}"))
                            elif width not in (None, "1"):
                                messages.append(svg_refusal("g" if placement == "inherited" else "line",
                                                            "stroke-width", width))
                            want = [("S26", str(path.relative_to(style.ROOT)), 0, m) for m in messages]
                            self.assertEqual(found, want)

    def test_vector_effect_figure_entry_points(self):
        """A scaled non-scaling stroke is refused in either presentation spelling."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for effect in (None, "non-scaling-stroke", "none"):
                for placement in ("attribute", "style"):
                    with self.subTest(idea=idea, effect=effect, placement=placement):
                        root = figure_fixture(idea)
                        ink, y = ("#222222", "111") if idea else ("#3b2f2f", "115")
                        line = svg_sub(root, "line", x1="388", y1=y, x2="412", y2=y,
                                             stroke=ink, transform="scale(.5)",
                                             attrib={"stroke-width": "4"})
                        if effect is not None:
                            line.set("style" if placement == "style" else "vector-effect",
                                     f"vector-effect:{effect}" if placement == "style" else effect)
                        found = [f for f in figure_findings(root, idea) if f[0] == "S26"]
                        messages = [svg_refusal("line", "transform", "scale(.5)")]
                        if effect is not None:
                            attr = "style" if placement == "style" else "vector-effect"
                            messages.append(svg_refusal("line", attr, line.get(attr)))
                        want = [("S26", str(path.relative_to(style.ROOT)), 0, m) for m in messages]
                        self.assertEqual(found, want)

    def test_sagitta_figure_entry_points(self):
        """Curved chords must not hide a clearance just below 2."""
        shapes = {
            "circle": '<circle cx="250" cy="150" r="100"/>',
            "ellipse": '<ellipse cx="250" cy="150" rx="100" ry="100"/>',
            "transformed ellipse":
                '<ellipse cx="500" cy="150" rx="200" ry="100" transform="scale(.5,1)"/>',
            "path": '<path d="M350 150 A100 100 0 1 0 150 150 A100 100 0 1 0 350 150"/>',
            "relative path": '<path d="M350 150 a100 100 0 1 0 -200 0 a100 100 0 1 0 200 0"/>',
            "grown path": '<path d="M350 150 A1 1 0 1 0 150 150 A1 1 0 1 0 350 150"/>',
            "transformed path": '<path transform="scale(.5,1)" '
                'd="M700 150 A200 100 0 1 0 300 150 A200 100 0 1 0 700 150"/>',
            "rect": '<rect x="150" y="50" width="200" height="200" rx="100"/>',
            "transformed rect": '<rect x="300" y="50" width="400" height="200" '
                'rx="200" ry="100" transform="scale(.5,1)"/>',
        }
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for shape, markup in shapes.items():
                for near in (False, True):
                    with self.subTest(idea=idea, shape=shape, near=near):
                        root = figure_fixture(idea)
                        curve = svg_sub(root, "g", {
                            "fill": "none", "stroke": "#222222" if idea else "#8c7b62",
                            "stroke-width": "3" if idea else "1.3"})
                        curve.append(svg_element(markup))
                        e = next(el for el in root.iter()
                                 if style.tag(el) == "text" and style.text_of(el) == "E")
                        e.attrib.update(x="268.13", y=("47.49" if idea else "49.12")
                                        if near else "47")
                        found = figure_findings(root, idea)
                        if shape.startswith("transformed") or shape == "relative path":
                            attr = "d" if shape == "relative path" else "transform"
                            self.assertEqual(found, [("S26", str(path.relative_to(style.ROOT)), 0,
                                svg_refusal(style.tag(curve[0]), attr, curve[0].get(attr)))])
                        elif near:
                            self.assertEqual(len(found), 1, found)
                            self.assertEqual(found[0][:3],
                                             ("S26", str(path.relative_to(style.ROOT)), 0))
                            self.assertIn("letter E", found[0][3])
                            kind = style.tag(curve[0])
                            self.assertIn(f"from {'an' if kind == 'ellipse' else 'a'} {kind}",
                                          found[0][3])
                            self.assertIn("under 2", found[0][3])
                        else:
                            self.assertEqual(found, [])

    def test_path_chord_error_is_local_to_each_subpath(self):
        """A remote large arc cannot widen a separate straight subpath's measure."""
        remote = "M-10000 -9000 A10000 10000 0 0 1 -9000 -10000 "
        for y, want in ((103.5, False), (101.5, True)):
            local = f"M100 {y} H200"
            for d in (local, remote + local):
                with self.subTest(y=y, remote=d != local):
                    found = s26_findings(
                        f'<path d="{d}" fill="none" stroke="#3b2f2f" '
                        'stroke-width="1.6"/>', letter("A"))
                    self.assertEqual(bool(found), want, found)
                    if want:
                        self.assertEqual(len(found), 1, found)
                        self.assertIn("letter A at (150, 100)", found[0])
                        self.assertIn("a path", found[0])

    def test_percentage_coordinates_figure_entry_points(self):
        """Percentages cannot conceal a line through E at either entry point."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for percentage in (False, True):
                with self.subTest(idea=idea, percentage=percentage):
                    root = figure_fixture(idea)
                    line = svg_sub(root, "line", {
                        "x1": "88%" if percentage else "352",
                        "x2": "91%" if percentage else "364",
                        "y1": "50.2667%" if percentage else "150.8",
                        "y2": "50.2667%" if percentage else "150.8",
                        "stroke": "#222222" if idea else "#3b2f2f", "stroke-width": "1.6"})
                    found = [f for f in figure_findings(root, idea) if f[0] == "S26"]
                    if percentage:
                        self.assertEqual(found, [
                            ("S26", str(path.relative_to(style.ROOT)), 0,
                             svg_refusal("line", attr, line.get(attr))) for attr in ("x1", "x2", "y1", "y2")])
                    else:
                        self.assertEqual(len(found), 1, found)
                        self.assertIn("letter E", found[0][3])
                        self.assertIn("meets a line", found[0][3])

    def test_lengths_figure_entry_points(self):
        """Every measured scalar length rejects units and malformed numbers by file."""
        shapes = {
            "line": ("x1", "y1", "x2", "y2", "stroke-width"),
            "circle": ("cx", "cy", "r"),
            "ellipse": ("cx", "cy", "rx", "ry"),
            "rect": ("x", "y", "width", "height", "rx", "ry"),
            "text": ("x", "y", "dx", "dy", "font-size"),
        }
        invalid = ("88%", "3pt", "3em", "3ex", "3rem", "3cm", "3mm", "3in", "3pc",
                   "3vh", "3vw", "bad", "", "1..5", "1e", "px", "NaN", "inf", "1e999")
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for kind, attrs in shapes.items():
                for attr in attrs:
                    for value in invalid:
                        for placement in ("attribute", "style", "inherited") \
                                if attr in ("stroke-width", "font-size") else ("attribute", "style"):
                            with self.subTest(idea=idea, kind=kind, attr=attr, value=value,
                                              placement=placement):
                                root = figure_fixture(idea)
                                el = svg_sub(root, kind, {
                                    "fill": "none",
                                    "stroke": "#222222" if idea else "#3b2f2f"})
                                if kind == "text":
                                    el.text = "A"
                                target = el
                                if placement == "inherited":
                                    root.remove(el)
                                    target = svg_sub(root, "g")
                                    target.append(el)
                                target.set("style" if placement == "style" else attr,
                                           f"{attr}:{value}" if placement == "style" else value)
                                found = [f for f in figure_findings(root, idea) if f[0] == "S26"]
                                self.assertIn(
                                    ("S26", str(path.relative_to(style.ROOT)), 0,
                                     svg_refusal(style.tag(target),
                                                 "style" if placement == "style" else attr,
                                                 f"{attr}:{value}" if placement == "style" else value)), found)

    def test_length_spellings_figure_entry_points(self):
        """Plain signed decimals agree; former unit and exponent spellings are refused."""
        for idea in (False, True):
            for spec, suffix in (("+.6f", ""), ("+.6e", ""), ("+.6e", "px"), ("+.6f", "px")):
                with self.subTest(idea=idea, spec=spec, suffix=suffix):
                    root = figure_fixture(idea)
                    messages = []
                    for el in root.iter():
                        for attr in ("x", "y", "x1", "y1", "x2", "y2", "width", "height",
                                     "rx", "font-size", "stroke-width"):
                            if attr in el.attrib:
                                value = format(float(el.get(attr)), spec) + suffix
                                el.set(attr, value)
                                if spec.endswith("e") or suffix:
                                    messages.append(svg_refusal(style.tag(el), attr, value))
                    self.assertCountEqual([m for _, _, _, m in figure_findings(root, idea)], messages)

    def test_coordinate_sequences_figure_entry_points(self):
        """Point lists and the canvas cannot hide units or drop malformed coordinates."""
        for idea in (False, True):
            path = style.ROOT / "figures" / "I" / ("01-idea.svg" if idea else "01.svg")
            for kind, attr in (("polyline", "points"), ("polygon", "points"), ("svg", "viewBox")):
                for value in ("0 0 400% 300", "0 0 3pt 300", "0 0 bad 300",
                              "0 0 1..5 300", "0 0 1e999 300", "0 0 400", ""):
                    with self.subTest(idea=idea, kind=kind, value=value):
                        root = figure_fixture(idea)
                        el = root if kind == "svg" else svg_sub(
                            root, kind, {"stroke": "#222222" if idea else "#3b2f2f"})
                        el.set(attr, value)
                        found = [f for f in figure_findings(root, idea) if f[0] == "S26"]
                        self.assertEqual(found, [
                            ("S26", str(path.relative_to(style.ROOT)), 0,
                             svg_refusal(kind, attr, value))])

    def test_clearance_cases(self):
        for drawn, s, font_style, anchor, want in CLEAR_CASES:
            with self.subTest(drawn=drawn, letter=s, style=font_style, anchor=anchor):
                found = s26_findings(drawn, letter(s, font_style=font_style, anchor=anchor))
                self.assertFalse(any("SVG allow-list" in message for message in found), found)
                self.assertEqual(bool(found), want,
                                 f"S26 {'misses' if want else 'wrongly finds'} a stroke "
                                 f"near {font_style} {s}, anchored at its {anchor}: "
                                 f"{drawn}: {found}")

    test_clearance_cases.__doc__ = (f"S26 reads {len(CLEAR_CASES)} strokes and dots beside "
                                    "a letter rightly")

    def test_clearance_refusal_cases(self):
        for drawn, kind, attr, value in CLEAR_REFUSAL_CASES:
            with self.subTest(drawn=drawn):
                self.assertEqual(s26_findings(drawn, letter("A")),
                                 [svg_refusal(kind, attr, value)])

    test_clearance_refusal_cases.__doc__ = (
        f"S26 refuses {len(CLEAR_REFUSAL_CASES)} excluded clearance spellings exactly")

    def test_edge_cases(self):
        for x, y, want in EDGE_CASES:
            with self.subTest(at=(x, y)):
                found = s26_findings("", letter("A", x=x, y=y))
                self.assertEqual(bool(found), want,
                                 f"S26 {'misses' if want else 'wrongly finds'} the canvas's "
                                 f"edge near a letter at ({x:g}, {y:g}): {found}")

    test_edge_cases.__doc__ = f"S26 reads {len(EDGE_CASES)} letters by the canvas's edge rightly"

    def test_place_cases(self):
        for drawn, letters, want in PLACE_CASES:
            with self.subTest(drawn=drawn, letters=letters):
                found = s26_findings(drawn, letters)
                self.assertEqual(bool(found), want,
                                 f"S26 {'misses' if want else 'wrongly finds'} a finding on "
                                 f"{letters} beside {drawn or 'nothing'}: {found}")

    test_place_cases.__doc__ = (f"S26 reads {len(PLACE_CASES)} letters by their size, their "
                                "transform and their primes rightly")

    def test_kind_cases(self):
        for drawn, kind in KIND_CASES:
            with self.subTest(drawn=drawn):
                found = s26_findings(drawn, letter("A"))
                self.assertEqual(found, [f"letter A at (150, 100) meets {kind}"],
                                 f"S26 does not call {drawn} {kind}: {found}")

    test_kind_cases.__doc__ = (f"S26 names {len(KIND_CASES)} lines through a letter, dashed "
                               "or not, rightly")

    def test_twice_cases(self):
        for xs, cuts, want in TWICE_CASES:
            with self.subTest(at=xs, cuts=cuts):
                found = s26_findings("", "".join(letter("A", x=x) for x in xs), cuts)
                self.assertEqual(bool(found), want,
                                 f"S26 {'misses' if want else 'wrongly finds'} a letter "
                                 f"drawn at x {xs}, cut at {cuts}: {found}")

    test_twice_cases.__doc__ = (f"S26 reads {len(TWICE_CASES)} figures drawing a letter "
                                "once or more rightly")


class Upright(unittest.TestCase):
    """The upright cases: an italic letter planted in a copy of each of I.1's figures."""

    def test_italic_letter_fails(self):
        """S15 and S20 fail an italic letter, one or every one, and D15 lists nothing."""
        folder = style.ROOT / "figures" / "I"
        euclid = (folder / "01.svg").read_text(encoding="utf-8")
        idea = (folder / "01-idea.svg").read_text(encoding="utf-8")
        plants = (   # (where font-style="italic" goes, the letters it sets italic)
            ("<text ", "A"),                    # on the first letter alone
            ("<svg ", "A, B, C, D, E"),         # on the root, so every letter inherits it
        )
        for name, rule in (("01.svg", "S15"), ("01-idea.svg", "S20")):
            for at, letters in ((None, None),) + plants:
                with self.subTest(figure=name, at=at), \
                        tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
                    root = Path(tmp)
                    copies = root / "figures" / "I"
                    copies.mkdir(parents=True)
                    for copy, raw in (("01.svg", euclid), ("01-idea.svg", idea)):
                        if copy == name and at is not None:
                            raw = raw.replace(at, at + 'font-style="italic" ', 1)
                        (copies / copy).write_text(raw, encoding="utf-8")
                    stack.enter_context(patch.object(style, "ROOT", root))
                    stack.enter_context(patch.object(style, "books_with_pages",
                                                     return_value=["I"]))
                    stack.enter_context(patch.object(style, "failures", []))
                    reports = stack.enter_context(patch.object(style, "reports",
                                                               defaultdict(list)))
                    stack.enter_context(patch.object(style, "italic_figures",
                                                     defaultdict(lambda: defaultdict(list))))
                    style.check_figures(True)
                    self.assertEqual(style.failures, [] if at is None else [
                        (rule, f"figures/I/{name}", 0, f"letter(s) {letters} italic: Heath's "
                         "letters are upright (STYLE, section 4)")])
                    self.assertNotIn("D15", reports)


class Scopes(unittest.TestCase):
    """The scope cases: the texts the rules read since #66, and how they read them."""

    def test_scope_cases(self):
        for rule, read, text, want in SCOPE_CASES:
            with self.subTest(rule=rule, text=text):
                self.assertEqual(read(text), want, f"{rule} reads {text!r} wrongly")

    test_scope_cases.__doc__ = (f"The new scopes read {len(SCOPE_CASES)} records, docstrings, "
                                "names and letters rightly")

    def test_review_hypothesis_binders_are_words(self):
        """A known declaration cannot make binder syntax pass in a hypothesis field."""
        raw = ('[statement]\n'
               'note = "The postulate is `Postulate5`."\n'
               'hypotheses = ["the condition (`Postulate5 : P`)"]\n')
        found = review_s12_failures(raw)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][0], 3)
        self.assertIn("write the hypothesis in words", found[0][1])

    def test_review_hypothesis_fields_reach_s12(self):
        """Main retains which reader-visible review strings are hypotheses."""
        actual = sorted((str(text.path), text.text) for text in main_named_records()
                        if text.hypothesis)
        expected = sorted((str(path), note.text) for path in style.review_files()
                          for note in style.review_texts(path.read_text(encoding="utf-8"))
                          if note.key == "statement.hypotheses")
        self.assertEqual(actual, expected)

    def test_reports_reach_s12(self):
        """Every eligible ordinary report is among the texts main gives S12."""
        named = main_named_texts()
        self.assertEqual({path: named.get(path) for path in style.report_files()},
                         {path: style.every_book_opens() for path in style.report_files()})

    def test_report_token_classification(self):
        """Reports distinguish declarations from syntax, files and explicitly named objects."""
        vocabulary = ({"axiom", "native_decide", "implemented_by"},
                      {"Elements", "Elements.BookIII"})
        cases = [
            ("`NOTICE:59-60`, `README:17`, `references.bib:9` and `references.bib`", []),
            ("`NOTICE` and `README`", ["NOTICE", "README"]),
            ("The file `NOTICE`, the `README` page and the script `check_fidelity`.", []),
            ("The files `NOTICE` and `README`.", []),
            ("It passes `check_fidelity`.", ["check_fidelity"]),
            ("The declaration `README` is missing.", ["README"]),
            ("The declaration `README.md` is missing.", ["README.md"]),
            ("The declaration `grind` is missing.", ["grind"]),
            ("`Squares.lean` is a nested repository file.", []),
            ("The theorem `Squares.lean` is missing.", ["Squares.lean"]),
            ("The declaration `references.bib`, the `NOTICE` theorem and the files "
             "`README`, `check_fidelity`.", ["NOTICE", "references.bib"]),
            ("The declarations `Elements` and `axiom`.", ["Elements", "axiom"]),
            ("`NOTICE : Point` and `README : Point`", ["NOTICE", "README"]),
            ("`axiom`, `native_decide`, `implemented_by`", []),
            ("`Elements` and `Elements.BookIII`", []),
            ("The namespace `Example.Geometry`. Later, `Example.Geometry`.", []),
            ("The namespace `Example.Geometry`. Then `Example.geometry`.", ["Example.geometry"]),
            ("<!-- namespace `Missing.name` -->\n`Missing.name`", ["Missing.name"]),
            ("The tactics\n`external_step` / `external_finish`.", []),
            ("`external_step` and `Exceeds.nearVertexOpen`",
             ["Exceeds.nearVertexOpen", "external_step"]),
            ("Internet Archive scans: vol. 4 (a supplement) is `another_scan_04`.", []),
            ("An Internet Archive scan `another_scan_04`.", []),
            ("`another_scan_04` is a name to check.", ["another_scan_04"]),
            ("The revision read at `abcdef1`.", []),
            ("`abcdef1`", ["abcdef1"]),
            ("- **Revision:** `d95125f0`.", []),
            ("`d95125f0`", ["d95125f0"]),
            ("- **Revision:** `not_a_commit`.", ["not_a_commit"]),
            ("Read the proof of `decafed`.", ["decafed"]),
            ("Reviewed the proof of `decafed`.", ["decafed"]),
            ("Verification of `decafed` remains incomplete.", ["decafed"]),
            ("The record has stage `full`, with a `helper` passage.", []),
            ("`full` and `helper`", ["full", "helper"]),
            ("The `axiom_modules` field of `facts.json`.", []),
            ("The record's `helper : Point`.", ["helper"]),
            ("The `Example.` family and `Example.missing`.", ["Example.missing"]),
            ("A tactic `external_step`.\n\nA declaration `external_step`.", ["external_step"]),
        ]
        path = style.REPORTS_DIR / "sample.md"
        for raw, want in cases:
            with self.subTest(raw=raw):
                named = style.NamedText(path, raw, style.every_book_opens())
                old, new, unchecked, _ = style.s12_plan([named], True, vocabulary)
                self.assertFalse(old)
                self.assertFalse(unchecked)
                self.assertEqual(sorted(n for g in new.values() for n in g), want)

    def test_explicit_declaration_does_not_use_exemption(self):
        """An explicit declaration use is checked rather than satisfying NOT_DECLARED."""
        path = style.REPORTS_DIR / "sample.md"
        named = style.NamedText(path, "The declaration `grind` is missing.",
                                style.every_book_opens())
        _, new, _, used = style.s12_plan([named], True, ({"grind"}, set()))
        self.assertEqual(sorted(n for group in new.values() for n in group), ["grind"])
        self.assertNotIn("grind", used)

    def test_only_page_axioms_have_rendered_docstrings(self):
        """Rendered-docstring scope follows the axioms shown on proposition pages."""
        shown = {doc.name for docs in style.rendered_docstrings().values() for doc in docs}
        self.assertIn("Tacit.add_assoc", shown)
        self.assertNotIn("Tacit.exists_point_inside_circle", shown)

    def test_report_classification_keeps_mishnah_enforcement(self):
        """The report's syntax and namespace classification cannot excuse a mishnah name."""
        raw = "`axiom` and `Elements` and `NOTICE` and `grind` and `Unknown.name`."
        named = style.NamedText(MISHNAH, raw, style.book_opens("I"), held=True)
        old, new, _, _ = style.s12_plan([named], True, ({"axiom"}, {"Elements"}))
        self.assertEqual(sorted(n for g in old.values() for n in g),
                         ["Elements", "NOTICE", "Unknown.name", "axiom", "grind"])
        self.assertFalse(new)

    def test_report_vocabulary_failure_is_not_pending(self):
        """A failed syntax query fails S12 itself, even when its report is pending."""
        path = style.REPORTS_DIR / "sample.md"
        with ExitStack() as stack:
            stack.enter_context(patch.object(style, "failures", []))
            stack.enter_context(patch.object(style, "lean_short", []))
            stack.enter_context(patch.object(style, "REACH_PENDING",
                                             {style.rel(path): ("S12", "a test")}))
            stack.enter_context(patch.object(style.subprocess, "run", return_value=
                SimpleNamespace(returncode=1, stdout="", stderr="could not import Elements")))
            named = style.NamedText(path, "`Missing.name`", style.every_book_opens())
            self.assertEqual(style.report_vocabulary([named]), (set(), set()))
            self.assertEqual(len(style.failures), 1)
            self.assertEqual(style.failures[0][:2], ("S12", style.rel(style.SCRIPT)))
            self.assertTrue(style.lean_short)
            self.assertFalse(style.reach_done())

    def test_report_pending_names_and_error_limit(self):
        """A report's unknown name fails without S12 pending, including after 100 errors."""
        path = style.REPORTS_DIR / "sample.md"

        def reject(args, **_):
            self.assertIn("-DmaxErrors=0", args)
            probe = Path(args[-1])
            errors = [f"{probe.name}:{k}:1: error: unknown identifier"
                      for k, line in enumerate(probe.read_text().splitlines(), 1)
                      if line.startswith("#check")]
            return SimpleNamespace(returncode=1, stdout="\n".join(errors), stderr="")

        for pending, want_fail, want_defer in ((None, 1, 0), ("S7", 1, 0), ("S12", 0, 1)):
            with self.subTest(pending=pending), ExitStack() as stack:
                stack.enter_context(patch.object(style, "failures", []))
                stack.enter_context(patch.object(style, "reports", defaultdict(list)))
                stack.enter_context(patch.object(style, "reach_found", set()))
                stack.enter_context(patch.object(style, "REACH_PENDING",
                    {style.rel(path): (pending, "a test")} if pending else {}))
                stack.enter_context(patch.object(style.subprocess, "run", side_effect=reject))
                named = style.NamedText(path, "A name:\n`Exceeds.nearVertexOpen`.",
                                       style.every_book_opens())
                _, groups, _, _ = style.s12_plan([named], False)
                self.assertEqual(style.lean_probe(groups, ["Elements"]), 1)
                self.assertEqual(len(style.failures), want_fail)
                self.assertEqual(len(style.reports.get("D16", [])), want_defer)
                if want_fail:
                    self.assertEqual(style.failures[0][:3], ("S12", style.rel(path), 2))
                else:
                    self.assertEqual(style.reports["D16"][0][:2], (style.rel(path), 2))
                    self.assertFalse(style.reach_done())

        with ExitStack() as stack:
            stack.enter_context(patch.object(style, "failures", []))
            stack.enter_context(patch.object(style, "reports", defaultdict(list)))
            stack.enter_context(patch.object(style, "reach_found", set()))
            stack.enter_context(patch.object(style, "REACH_PENDING",
                                             {style.rel(path): ("S12", "a test")}))
            stack.enter_context(patch.object(style.subprocess, "run", side_effect=reject))
            raw = " ".join(f"`Missing.name{k:03}`" for k in range(105))
            later = style.REPORTS_DIR / "later.md"
            named = [style.NamedText(path, raw, style.every_book_opens()),
                     style.NamedText(later, "`ZMissing.later`", style.every_book_opens())]
            _, groups, _, _ = style.s12_plan(named, False)
            self.assertEqual(style.lean_probe(groups, ["Elements"]), 106)
            self.assertEqual(len(style.reports["D16"]), 105)
            self.assertEqual(len(style.failures), 1)
            self.assertEqual(style.failures[0][:3], ("S12", style.rel(later), 1))

    def test_reach_cases(self):
        for path, scopes, new, pending, want in REACH_CASES:
            with self.subTest(path=style.rel(path), pending=pending):
                self.assertEqual(findings(path, REACH_TEXT, scopes, pending=pending, new=new),
                                 want)

    test_reach_cases.__doc__ = (f"The reach of 19 October is reported in a listed file for "
                                f"the rules it is listed for, and all else fails, in "
                                f"{len(REACH_CASES)} cases")

    def test_done_cases(self):
        for text, pending, no_lean, want in DONE_CASES:
            with self.subTest(text=text, pending=pending, no_lean=no_lean):
                self.assertEqual(reach_run(GAPS, text, {"catalogue"}, pending, False,
                                           lambda: style.reach_done(no_lean)), want)

    test_done_cases.__doc__ = (f"A rule of a listed file with no finding of it left is "
                               f"reported as done, and the entry once all its rules are, in "
                               f"{len(DONE_CASES)} more reach cases")

    def test_done_without_lean(self):
        """S12 is not reported done when Lean could not be run, as without `lake`"""
        name = style.NamedText(GAPS, "`Unknown.name`", "Elements")
        use = style.NameUse(name, 0, False)
        saved = (os.environ.get("PATH"), list(style.lean_short))
        try:
            with tempfile.TemporaryDirectory() as empty:
                os.environ["PATH"] = empty   # no `lake` to be found
                style.lean_short.clear()
                done = reach_run(GAPS, "Plain words.", {"catalogue"}, "S7 S12", False, lambda: (
                    style.lean_probe({"Elements": {"Unknown.name": [use]}}, ["Elements"]),
                    sorted(r for r, *_ in style.failures), style.reach_done(False)))
        finally:
            if saved[0] is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = saved[0]
            style.lean_short[:] = saved[1]
        self.assertEqual(done, (0, ["S12"], [(GAPS_REL, ["S7"], False)]))


class ConflictMarkers(unittest.TestCase):
    """Raw text, including fences, and the boundary between separators and headings."""

    def test_edges_with_and_without_labels(self):
        for char, kind in (("<", "opening"), ("|", "base"), (">", "closing")):
            for ending in ("", " ours", " ", "\r", " ours\r"):
                with self.subTest(char=char, ending=ending):
                    text = "A paragraph.\n" + char * 7 + ending + "\n"
                    self.assertEqual(style.conflict_markers(text, markdown=True), [(2, kind)])

    def test_exact_edge_width_and_boundary(self):
        for char in "<|>":
            for line in (char * 6, char * 8, char * 8 + " ours", char * 7 + "ours",
                         char * 7 + "\tours", " " + char * 7 + " ours"):
                with self.subTest(line=line):
                    self.assertEqual(style.conflict_markers(line, markdown=False), [])

    def test_middle_between_edges_after_paragraph(self):
        for ending in ("", "  ", "\r", " \t\r"):
            with self.subTest(ending=ending):
                text = "\n".join(("<" * 7 + " ours", "A paragraph.", "=" * 7 + ending,
                                  "The other side.", ">" * 7 + " theirs"))
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(1, "opening"), (3, "middle"), (5, "closing")])

    def test_diff3_block(self):
        text = "\n".join(("<" * 7, "Ours.", "|" * 7, "Base.", "=" * 7,
                          "Theirs.", ">" * 7))
        self.assertEqual(style.conflict_markers(text, markdown=True),
                         [(1, "opening"), (3, "base"), (5, "middle"), (7, "closing")])

    def test_nested_conflicts_keep_the_outer_block_open(self):
        text = "\n".join(("<" * 7 + " outer", "<" * 7 + " inner", "=" * 7,
                          ">" * 7 + " inner", "Outer text", "=" * 7,
                          ">" * 7 + " outer"))
        self.assertEqual(style.conflict_markers(text, markdown=True), [
            (1, "opening"), (2, "opening"), (3, "middle"), (4, "closing"),
            (6, "middle"), (7, "closing"),
        ])

    def test_middle_needs_both_edges_to_override_setext(self):
        for text, expected in (
            ("\n".join(("<" * 7, "A heading", "=" * 7)), [(1, "opening")]),
            ("\n".join(("A heading", "=" * 7, ">" * 7)), [(3, "closing")]),
            ("\n".join(("<" * 7, ">" * 7, "A heading", "=" * 7)),
             [(1, "opening"), (2, "closing")]),
        ):
            with self.subTest(text=text):
                self.assertEqual(style.conflict_markers(text, markdown=True), expected)

    def test_lone_middle_in_non_markdown(self):
        for ending in ("", " ", "\r"):
            with self.subTest(ending=ending):
                self.assertEqual(style.conflict_markers("Text.\n" + "=" * 7 + ending,
                                                       markdown=False), [(2, "middle")])

    def test_setext_headings_of_any_length(self):
        for width in (1, 6, 7, 8, 80):
            for paragraph in ("A heading", "A paragraph\ncontinued", "#hashtag",
                              "#" * 7 + " is paragraph text"):
                with self.subTest(width=width, paragraph=paragraph):
                    self.assertEqual(style.conflict_markers(
                        paragraph + "\n" + "=" * width + " \r\n", markdown=True), [])

    def test_middle_after_completed_setext_heading(self):
        for char in "=-":
            for width in (1, 3, 7, 8):
                with self.subTest(char=char, width=width):
                    text = "Heading\n   " + char * width + " \t\n" + "=" * 7
                    self.assertEqual(style.conflict_markers(text, markdown=True),
                                     [(3, "middle")])

    def test_middle_in_comment_blocks(self):
        for indent in ("", " ", "   "):
            for ending in ("", "\n-->"):
                with self.subTest(indent=indent, ending=ending):
                    text = indent + "<!--\nComment text\n" + "=" * 7 + ending
                    self.assertEqual(style.conflict_markers(text, markdown=True),
                                     [(3, "middle")])
        for comment in ("<!-- one line -->", "<!--\ncomment\n-->"):
            text = comment + "\n" + "=" * 7
            self.assertEqual(style.conflict_markers(text, markdown=True),
                             [(text.count("\n") + 1, "middle")])

    def test_comment_fences_do_not_escape_the_comment(self):
        for fence in ("```", "~~~~"):
            for gap in ("", "\n"):
                with self.subTest(fence=fence, gap=gap):
                    text = "<!--\n" + fence + "\n-->\n" + gap + "Heading\n" + "=" * 7
                    self.assertEqual(style.conflict_markers(text, markdown=True), [])
        for char, kind in (("<", "opening"), ("|", "base"), ("=", "middle"),
                           (">", "closing")):
            text = "<!--\n```\nComment text\n" + char * 7 + "\n-->"
            self.assertEqual(style.conflict_markers(text, markdown=True), [(4, kind)])

    def test_comment_openers_in_fences_do_not_escape_the_fence(self):
        text = "\n".join(("```", "<!--", "```", "Heading", "=" * 7))
        self.assertEqual(style.conflict_markers(text, markdown=True), [])

    def test_middle_in_html_blocks(self):
        for html in ("<div>", "<div>\nbody", "<div>\nbody\n</div>",
                     "<script>\ncode\n</script>", "<?instruction?>", "<!DOCTYPE html>",
                     "<![CDATA[text]]>", '<x title="a>b">', "<source src=x",
                     "<div\fclass=x>", "<x\vtitle=y>"):
            with self.subTest(html=html):
                text = html + "\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(text.count("\n") + 1, "middle")])

    def test_form_feed_does_not_end_html_or_reference_blocks(self):
        for prefix in ("<div>", "[label]: /url"):
            with self.subTest(prefix=prefix):
                text = prefix + "\n\f\nText\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(4, "middle")])

    def test_html_block_termination_restores_paragraph_headings(self):
        for html in ("<div>\nbody\n</div>", "<script>\ncode\n</script>"):
            with self.subTest(html=html):
                text = html + "\n\nHeading\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])

    def test_any_raw_closing_tag_ends_a_raw_html_block(self):
        for html in ("<script>\n</style>", "<pre>\n</SCRIPT>", "<style>\nx</textarea> y",
                     "<textarea>\n</Pre>", "<style>body</pre>"):
            with self.subTest(html=html):
                text = html + "\nHeading\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])
        for html in ("<script>\n</div>", "<pre>\n</scripts>", "<style>\n</ style>"):
            with self.subTest(html=html):
                text = html + "\nHeading\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(text.count("\n") + 1, "middle")])

    def test_self_closing_literal_content_tags_remain_paragraph_text(self):
        for tag in ("<script/>", "<PRE/>", "<Style/>", "<textarea/>", "   <pre/>",
                    "<script/> \t"):
            with self.subTest(tag=tag):
                self.assertEqual(style.conflict_markers(tag + "\n" + "=" * 7,
                                                       markdown=True), [])
        for tag in ("<scripts/>", "<prefix/>", "<stylesheet/>", "<textareas/>",
                    "</script>", "</PRE>", "<script>", "<style />", "<pre\vtitle='x'/>",
                    "<div/>", "<x/>"):
            with self.subTest(tag=tag):
                self.assertEqual(style.conflict_markers(tag + "\n" + "=" * 7,
                                                       markdown=True), [(2, "middle")])

    def test_html_blocks_keep_exact_width_and_edge_detection(self):
        for width in (6, 8):
            self.assertEqual(style.conflict_markers("<div>\n" + "=" * width,
                                                   markdown=True), [])
        text = "<div>\n" + "<" * 7 + " ours\n" + ">" * 7 + " theirs"
        self.assertEqual(style.conflict_markers(text, markdown=True),
                         [(2, "opening"), (3, "closing")])

    def test_inline_html_remains_paragraph_text(self):
        for paragraph in ('Text <x title="a>b">', '<x title="a>b"> trailing'):
            with self.subTest(paragraph=paragraph):
                self.assertEqual(style.conflict_markers(
                    paragraph + "\n" + "=" * 7, markdown=True), [])

    def test_middle_after_gfm_table_delimiter_and_rows(self):
        for table in ("| A | B |\n| --- | --- |",
                      "A | B\n--- | ---\nleft | right\nnext | row",
                      "| A | B |\n| --- | --- |\nplain"):
            with self.subTest(table=table):
                text = table + "\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(text.count("\n") + 1, "middle")])

    def test_table_delimiters_trim_only_spaces_and_tabs(self):
        for control in ("\f", "\v"):
            for table in (f"A | B\n--- | {control}---", f"A | B\n---{control} | ---",
                          f"| A | B |\n| --- | --- |{control}"):
                with self.subTest(table=table):
                    self.assertEqual(style.conflict_markers(
                        table + "\n" + "=" * 7, markdown=True), [])
        for table in ("A | B\n--- | \t---", "A | B\n---\t | ---",
                      "| A | B |\n| --- | --- | \t"):
            with self.subTest(table=table):
                self.assertEqual(style.conflict_markers(
                    table + "\n" + "=" * 7, markdown=True), [(3, "middle")])

    def test_gfm_table_termination_restores_paragraph_headings(self):
        table = "| A | B |\n| --- | --- |\nplain\n"
        for boundary in ("\n", "# Boundary\n", "---\n", "> quote\n\n", "- item\n\n",
                         "```\ncode\n```\n", "<div>\nbody\n\n"):
            with self.subTest(boundary=boundary):
                text = table + boundary + "Heading\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])

    def test_gfm_tables_keep_exact_width_and_edge_detection(self):
        table = "| A | B |\n| --- | --- |\n"
        for width in (6, 8):
            self.assertEqual(style.conflict_markers(table + "=" * width, markdown=True), [])
        text = table + "|" * 7 + " base\n" + ">" * 7
        self.assertEqual(style.conflict_markers(text, markdown=True),
                         [(3, "base"), (4, "closing")])

    def test_multiline_reference_definition_taints_the_block(self):
        for definition in ("[\nfoo\n]: /url", "  [\nfoo\n]:", "[\nfo\\]o\n]: /url"):
            with self.subTest(definition=definition):
                text = definition + "\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(text.count("\n") + 1, "middle")])

    def test_multiline_reference_candidate_resets_or_remains_paragraph_text(self):
        for prefix in ("[\nfoo\n\n", "[\nfoo\n] not a definition\n"):
            with self.subTest(prefix=prefix):
                self.assertEqual(style.conflict_markers(
                    prefix + "Heading\n" + "=" * 7, markdown=True), [])

    def test_multiline_reference_keeps_exact_middle_width(self):
        definition = "[\nfoo\n]: /url\n"
        for width in (6, 8):
            with self.subTest(width=width):
                self.assertEqual(style.conflict_markers(
                    definition + "=" * width, markdown=True), [])

    def test_middle_after_indented_code(self):
        for indent in ("    ", "\t", "  \t"):
            for prefix in ("", "Paragraph\n\n"):
                with self.subTest(indent=indent, prefix=prefix):
                    text = prefix + indent + "code\n" + "=" * 7
                    self.assertEqual(style.conflict_markers(text, markdown=True),
                                     [(text.count("\n") + 1, "middle")])

    def test_indented_continuation_is_still_a_paragraph(self):
        for indent in ("    ", "\t", "  \t"):
            with self.subTest(indent=indent):
                text = "Heading\n" + indent + "continued\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])

    def test_middle_after_link_reference_definition(self):
        for indent in ("", " ", "   "):
            for destination in ("destination", "<somewhere>", 'destination "Title"'):
                with self.subTest(indent=indent, destination=destination):
                    text = indent + "[label]: " + destination + "\n" + "=" * 7
                    self.assertEqual(style.conflict_markers(text, markdown=True),
                                     [(2, "middle")])
        self.assertEqual(style.conflict_markers(
            "[\\ ]: /url\n" + "=" * 7, markdown=True), [(2, "middle")])
        self.assertEqual(style.conflict_markers(
            "[\u00a0]: /url\n" + "=" * 7, markdown=True), [(2, "middle")])
        text = "[label]: destination\nHeading\ncontinued\n" + "=" * 7
        self.assertEqual(style.conflict_markers(text, markdown=True), [(4, "middle")])

    def test_reference_shape_inside_paragraph_refuses_middle(self):
        text = "Heading\n[label]: destination\n" + "=" * 7
        self.assertEqual(style.conflict_markers(text, markdown=True), [(3, "middle")])

    def test_reference_definition_bypasses_through_scanner(self):
        definitions = ("[label]:\n /url", '[label]: /url\n "Title"',
                       r"[la\]bel]: /url")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "definition.md"
            for definition in definitions:
                with self.subTest(definition=definition):
                    path.write_text(definition + "\n" + "=" * 7 + "\n")
                    with patch.object(style, "ROOT", root), \
                            patch.object(style, "failures", []):
                        style.check_conflict_markers()
                        self.assertEqual(style.failures, [
                            ("S23", "definition.md", definition.count("\n") + 2,
                             "middle merge-conflict marker"),
                        ])

    def test_possible_reference_definition_taints_whole_block(self):
        for indent in ("", " ", "  ", "   "):
            for label in ("label", r"la\[bel", r"la\]bel", r"la\[b\]el", r"label\\"):
                for prefix in ("", "Heading\n"):
                    with self.subTest(indent=indent, label=label, prefix=prefix):
                        text = (prefix + indent + "[" + label + "]:\n /url\n"
                                '"Title"\ncontinued\n' + "=" * 7)
                        self.assertEqual(style.conflict_markers(text, markdown=True),
                                         [(text.count("\n") + 1, "middle")])

    def test_doubtful_reference_heading_uses_eight_equals(self):
        # Extra words make paragraph text, but refusal is the deliberate price
        # of treating every possible definition prefix conservatively.
        for width in (1, 6, 7, 8, 80):
            with self.subTest(width=width):
                text = "[label]: destination extra words\n" + "=" * width
                expected = [(2, "middle")] if width == 7 else []
                self.assertEqual(style.conflict_markers(text, markdown=True), expected)

    def test_middle_after_block_quote_or_list_item_is_refused(self):
        for start in ("> quote", "- item", "* item", "+ item", "1. item", "12) item",
                      "0. item", "2.", "*", "+ \t", "Para\n\n2. item", "Para\n\n*",
                      "Para\n> quote", "Para\n>", "Para\n- item", "Para\n*\tx",
                      "Para\n1. item", "Para\n01) item", "Para\n2. item\n- x"):
            with self.subTest(start=start):
                text = start + "\n" + "=" * 7
                line = text.count("\n") + 1
                self.assertEqual(style.conflict_markers(text, markdown=True), [(line, "middle")])
                self.assertEqual(style.conflict_markers(start + "\n" + "=" * 8, markdown=True), [])
        for text in ("-item\n", "1.5 metres\n", "*emphasis* here\n"):
            with self.subTest(paragraph=text):
                self.assertEqual(style.conflict_markers(text + "=" * 7, markdown=True), [])

    def test_list_items_that_cannot_interrupt_continue_the_paragraph(self):
        for line in ("2. item", "12) item", "0. item", "*", "+", "* \t", "+ ", "1.",
                     "1)  ", "01.", "2.", "2. item\n3. item"):
            with self.subTest(line=line):
                text = "Heading\n" + line + "\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])

    def test_list_items_holding_only_control_whitespace_continue_the_paragraph(self):
        for marker in ("*", "-", "+", "1.", "1)", "01."):
            for content in (" \f", " \v", "\t\f", " \v \f\t"):
                with self.subTest(marker=marker, content=content):
                    text = "Heading\n" + marker + content + "\n" + "=" * 7
                    self.assertEqual(style.conflict_markers(text, markdown=True), [])
        for line in ("* \fx", "- \vitem", "1. \f1", "1) \v \fx"):
            with self.subTest(line=line):
                text = "Heading\n" + line + "\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(3, "middle")])

    def test_setext_and_thematic_lines_precede_list_items(self):
        for line in ("-", "- ", "-\t", "* * *", "- - -", "_ _ _"):
            with self.subTest(line=line):
                text = "Heading\n" + line + "\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True),
                                 [(3, "middle")])

    def test_reference_definition_stops_at_block_boundary(self):
        for boundary in ("\n", "<!-- comment -->\n", "<!--\ncomment\n-->\n",
                         "```\ncode\n```\n", "# Heading\n", "---\n",
                         "Heading\n" + "=" * 8 + "\n"):
            with self.subTest(boundary=boundary):
                text = "[label]: /url\n" + boundary + "Heading\ncontinued\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])

    def test_brackets_without_reference_prefix_remain_paragraph_text(self):
        for line in ("[label] text", "[label] : /url", r"\[label]: /url",
                     "Text [label]: /url", "[unescaped[bracket]: /url"):
            with self.subTest(line=line):
                self.assertEqual(style.conflict_markers(line + "\n" + "=" * 7,
                                                       markdown=True), [])

    def test_lone_middle_without_paragraph(self):
        for previous in ("", "  ", "#", "## A heading", "   ### Heading",
                         "---", "* * *", "___"):
            with self.subTest(previous=previous):
                self.assertEqual(style.conflict_markers(previous + "\n" + "=" * 7,
                                                       markdown=True), [(2, "middle")])
        self.assertEqual(style.conflict_markers("=" * 7, markdown=True), [(1, "middle")])

    def test_middle_after_each_marker(self):
        for char, kind in (("<", "opening"), ("|", "base"), (">", "closing"),
                           ("=", "middle")):
            with self.subTest(char=char):
                self.assertEqual(style.conflict_markers(char * 7 + "\n" + "=" * 7,
                                                       markdown=True),
                                 [(1, kind), (2, "middle")])

    def test_other_equals_lines(self):
        for line in ("=" * 6, "=" * 8, "=" * 7 + " label", " " + "=" * 7):
            with self.subTest(line=line):
                self.assertEqual(style.conflict_markers(line, markdown=False), [])

    def test_markers_in_fences(self):
        for fence in ("```", "~~~~"):
            for char, kind in (("<", "opening"), ("|", "base"), ("=", "middle"),
                               (">", "closing")):
                with self.subTest(fence=fence, char=char):
                    text = "\n".join((fence + "text", "A code line.", char * 7, fence))
                    self.assertEqual(style.conflict_markers(text, markdown=True), [(3, kind)])

    def test_middle_at_fence_boundaries(self):
        for text, line in (
            ("\n".join(("```text", "=" * 7, "```")), 2),
            ("\n".join(("~~~", "code", "~~~", "=" * 7)), 4),
            ("\n".join(("````", "```", "paragraph", "=" * 7)), 4),
            ("\n".join(("~~~", "```", "paragraph", "=" * 7)), 4),
        ):
            with self.subTest(text=text):
                self.assertEqual(style.conflict_markers(text, markdown=True), [(line, "middle")])
        self.assertEqual(style.conflict_markers(
            "\n".join(("```", "code", "```", "A heading", "=" * 7)), markdown=True), [])
        self.assertEqual(style.conflict_markers("```not`a fence\n" + "=" * 7,
                                               markdown=True), [])

    def test_fence_closing_tail_uses_spaces_and_tabs_only(self):
        for tail in ("", " ", "\t", " \t"):
            with self.subTest(tail=repr(tail)):
                text = "```\ncode\n```" + tail + "\nHeading\n" + "=" * 7
                self.assertEqual(style.conflict_markers(text, markdown=True), [])
        text = "```\n```\v\nText\n" + "=" * 7
        self.assertEqual(style.conflict_markers(text, markdown=True), [(4, "middle")])

    def test_lines_are_counted_by_newlines(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                text = "Text with Unicode separators \u2028 and \u2029 here." + newline
                text += "|" * 7 + " base" + newline
                self.assertEqual(style.conflict_markers(text, markdown=True), [(2, "base")])
        text = "First\r\nSecond\r" + ">" * 7 + " last\n"
        self.assertEqual(style.conflict_markers(text, markdown=True), [(3, "closing")])

    def test_raw_files_and_binary_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = ("|" * 7 + " base\n").encode()
            for name, data in {
                "notes.md": b"<!--\n" + marker + b"-->\n",
                "image.bin": marker,  # The bytes decide, not the extension.
                "nul.txt": marker + b"\0",
                "non-utf8.txt": marker + b"\xff",
                "heading.MD": b"Heading\n" + ("=" * 7).encode(),
            }.items():
                (root / name).write_bytes(data)
            with patch.object(style, "ROOT", root), patch.object(style, "failures", []):
                style.check_conflict_markers()
                self.assertEqual(sorted(style.failures), [
                    ("S23", "image.bin", 1, "base merge-conflict marker"),
                    ("S23", "notes.md", 2, "base merge-conflict marker"),
                ])

    def test_copy_walk_omits_build_and_cache_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.txt").write_text("text")
            for folder in (".lake", "model/.lake", "build", "dist", "_build",
                           "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                           ".tox", ".venv", "venv", "node_modules"):
                path = root / folder
                path.mkdir(parents=True, exist_ok=True)
                (path / "ignored.txt").write_text("<" * 7)
            self.assertEqual(list(style.repository_files(root)), [root / "source.txt"])

    def test_git_list_is_nul_delimited_and_unpruned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ["tracked.txt", "line\nbreak.txt", "build/tracked.txt"]
            for name in names + ["untracked.txt"]:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("text")
            listing = SimpleNamespace(stdout=("\0".join(names) + "\0").encode())
            with patch.object(Path, "exists", return_value=True), \
                    patch.object(style.subprocess, "run", return_value=listing) as run:
                self.assertEqual(list(style.repository_files(root)), [root / name for name in names])
                run.assert_called_once_with(["git", "ls-files", "-z"], cwd=root,
                                            capture_output=True, check=True)

    def test_no_git_executable_in_a_checkout_stops_the_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.txt").write_text("text")
            with patch.object(Path, "exists", return_value=True), \
                    patch.object(style.subprocess, "run", side_effect=FileNotFoundError):
                with self.assertRaises(FileNotFoundError):
                    list(style.repository_files(root))

    def test_git_failure_is_not_an_empty_scan(self):
        with patch.object(Path, "exists", return_value=True), \
                patch.object(style.subprocess, "run",
                             side_effect=style.subprocess.CalledProcessError(128, "git")):
            with self.assertRaises(style.subprocess.CalledProcessError):
                list(style.repository_files(style.ROOT))

    def test_walk_error_names_the_unread_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blocked = root / "docs" / "briefs"
            blocked.mkdir(parents=True)
            (blocked / "marker.md").write_text("|" * 7)
            scandir = os.scandir

            def unreadable(path):
                if Path(path) == blocked:
                    raise PermissionError(13, "Permission denied", str(path))
                return scandir(path)

            with patch.object(style, "ROOT", root), \
                    patch.object(style.os, "scandir", side_effect=unreadable):
                with self.assertRaisesRegex(OSError, str(blocked)):
                    style.check_conflict_markers()

    def test_symlinks_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "copy"
            root.mkdir()
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "marker.md").write_text("|" * 7)
            links = [root / "file.md", root / "folder", root / "missing.md"]
            for link, target in zip(links, (outside / "marker.md", outside,
                                           outside / "missing.md")):
                link.symlink_to(target)
            (root / "ordinary.md").write_text("|" * 7)
            for tracked in (False, True):
                with self.subTest(tracked=tracked), ExitStack() as stack:
                    stack.enter_context(patch.object(style, "ROOT", root))
                    stack.enter_context(patch.object(style, "failures", []))
                    if tracked:
                        stack.enter_context(patch.object(style, "repository_files",
                            return_value=links + [root / "ordinary.md"]))
                    style.check_conflict_markers()
                    self.assertEqual(style.failures,
                        [("S23", "ordinary.md", 1, "base merge-conflict marker")])

    def test_marker_copy_does_not_dereference_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, copy = Path(tmp) / "source", Path(tmp) / "copy"
            source.mkdir()
            copy.mkdir()
            outside = Path(tmp) / "outside"
            outside.write_text("|" * 7)
            (source / "link.md").symlink_to(outside)
            (source / "missing.md").symlink_to(Path(tmp) / "missing")
            (source / "ordinary.md").write_text("A paragraph.")
            with patch.object(plants, "ROOT", source):
                plants.copy_marker_files(copy, ["link.md", "missing.md", "ordinary.md"])
            self.assertEqual((copy / "ordinary.md").read_text(), "A paragraph.")
            for name in ("link.md", "missing.md"):
                path = copy / name
                self.assertTrue(path.is_symlink() or not path.exists())


class TrackedFiles(unittest.TestCase):
    """S12 has no filesystem fallback, and importing the check needs no Git."""

    def test_git_index_ignores_untracked_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Bogus.missing").write_text("untracked")
            listing = SimpleNamespace(returncode=0, stdout="docs/kept.md\0", stderr="")
            with patch.object(style, "ROOT", root), \
                    patch.object(style.subprocess, "run", return_value=listing) as run:
                self.assertEqual(style.tracked_file_index(),
                    (frozenset({"docs/kept.md"}), frozenset({"kept.md"})))
                run.assert_called_once_with(["git", "ls-files", "-z"], cwd=root,
                                            capture_output=True, text=True)

    def test_git_failure_without_metadata_still_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Bogus.missing").write_text("untracked")
            listing = SimpleNamespace(returncode=128, stdout="", stderr="not a git repository")
            with patch.object(style, "ROOT", root), \
                    patch.object(style.subprocess, "run", return_value=listing):
                with self.assertRaisesRegex(RuntimeError, "could not list tracked files"):
                    style.tracked_file_index()

    def test_import_does_not_build_the_git_index(self):
        with patch.object(style.subprocess, "run", side_effect=FileNotFoundError) as run:
            runpy.run_path(str(style.SCRIPT), run_name="style_import_probe")
            run.assert_not_called()

    def test_report_classification_cannot_use_the_fallback_walk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Bogus.missing").write_text("untracked")
            named = style.NamedText(root / "report.md", "`Bogus.missing`",
                                   style.every_book_opens())
            occurrence, = style.lean_name_occurrences(named.text, all_uses=True)
            listing = SimpleNamespace(returncode=128, stdout="", stderr="not a git repository")
            with patch.object(style, "ROOT", root), \
                    patch.object(style, "TRACKED_FILE_INDEX", None), \
                    patch.object(style.subprocess, "run", return_value=listing):
                with self.assertRaisesRegex(RuntimeError, "could not list tracked files"):
                    style.report_non_declaration(named, occurrence, (set(), set()))
                self.assertIsNone(style.TRACKED_FILE_INDEX)


class Acceptance(unittest.TestCase):
    """How check_acceptance.py assigns the style check's findings to items and pages."""

    def test_modern_figure_owners(self):
        import check_acceptance as acceptance
        for path, want in [
            ("figures/I/01-modern.svg", "I.1"),
            ("./figures/II/14-modern.svg", "II.14"),
            ("figures/III/37-modern.svg", "III.37"),
            ("figures/I/00-modern.svg", None),
            ("figures/II/15-modern.svg", None),
            ("figures/IV/01-modern.svg", None),
            ("figures/I/01-modern-extra.svg", None),
        ]:
            with self.subTest(path=path):
                self.assertEqual(acceptance.owner(path), want)

    def test_modern_findings_are_figures_and_backticks_are_style(self):
        import check_acceptance as acceptance
        out = "\n".join([
            "  ✗ S24 figures/I/01-modern.svg: a wrong title",
            "  ✗ S25 figures/II/14-modern.svg: an unknown name",
            "  ✗ S22 mishnah/I/02.md:3: letters in backticks",
        ])
        with patch.object(acceptance, "failures", {}), \
                patch.object(acceptance, "run", return_value=SimpleNamespace(
                    returncode=1, stdout=out, stderr="")):
            acceptance.check_style_rules()
            self.assertEqual(sorted(acceptance.failures),
                             [("I.1", "P8"), ("I.2", "P9"), ("II.14", "P8")])

    def test_review_record_findings_are_style(self):
        """A record's finding is its proposition's P9, whatever its rule; others as before"""
        import check_acceptance as acceptance
        out = "\n".join([
            "  ✗ S8 review/I/05.toml:7: a curly quotation mark",
            "  ✗ S9 review/I/06.toml:3: a styled letter",
            "  ✗ S8 mishnah/I/07.md:2: a curly quotation mark",
            "  ✗ S13 figures/I/08.svg: a letter not Heath's",
            "  ✗ S12 mishnah/I/09.md:4: an unknown name",
            "  ✗ S26 figures/I/10.svg: a letter meets a line",
        ])
        with ExitStack() as stack:
            stack.enter_context(patch.object(acceptance, "failures", {}))
            stack.enter_context(patch.object(acceptance, "run", return_value=SimpleNamespace(
                returncode=1, stdout=out, stderr="")))
            acceptance.check_style_rules()
            self.assertEqual(sorted(acceptance.failures),
                             [("I.10", "P8"), ("I.5", "P9"), ("I.6", "P9"),
                              ("I.7", "P7"), ("I.8", "P8"), ("I.9", "P9")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
