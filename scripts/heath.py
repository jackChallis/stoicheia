"""Read Heath's text (heath/<book>/NN.md) into enunciation + proof paragraphs, and keep
the small contracts the other scripts share:

* references: `parse_ref`, `prop_key` ("I.40", "III.1 Por.", "I.40 general");
* Heath's porisms: `heath_porisms`, `heath_porism`;
* the main theorem of a Lean file: `theorem_span`;
* fingerprints of statements, files and records: `fingerprint`, `review_fingerprint`,
  `file_hash`, `text_hash`;
* the review records, review/<book>/NN.toml: `load_review`, `validate_review`,
  `load_terms` (the schema is review/SCHEMA.md).

Shared by scaffold_book.py, check_fidelity.py and render.py. Standard library only.
Reading review records needs Python 3.11 or later, for tomllib; the rest runs on older
Pythons too. `python3 scripts/heath.py` checks the contracts against themselves: the
examples in review/SCHEMA.md, review/terms.toml and every review record present.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


def _toml():
    """tomllib, imported only where a record is read, so that the scripts which never
    read one still run on a Python older than 3.11."""
    try:
        import tomllib
    except ModuleNotFoundError:
        raise RuntimeError("reading review records needs Python 3.11 or later (tomllib)") from None
    return tomllib

ROOT = Path(__file__).resolve().parent.parent

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
CITATION = re.compile(r"\[([^\[\]]*?)\]")


def heath_path(book: str, n: int) -> Path:
    return ROOT / "heath" / book / f"{n:02d}.md"


def read(book: str, n: int):
    """Return (source_comment, enunciation, [proof paragraphs])."""
    raw = heath_path(book, n).read_text()
    source = ""
    m = HTML_COMMENT.match(raw.strip())
    if m:
        source = m.group(0)[4:-3].strip()
    text = HTML_COMMENT.sub("", raw)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    paras = [" ".join(p.split()) for p in paras if not p.startswith("# ")]
    enunciation = paras[0].replace("*", "").strip()
    return source, enunciation, paras[1:]


def bracketed(book: str, n: int) -> bool:
    """Is the whole proposition in Heath's square brackets, as III. 12 is? He prints the
    opening bracket before the heading ("[Proposition 12."), which `read` leaves out with
    the heading; the closing one follows "Q. E. D." and stays in the proof."""
    text = HTML_COMMENT.sub("", heath_path(book, n).read_text())
    return any(line.startswith("# [") for line in text.splitlines())


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]

# The books carried into Lean so far, and how many propositions each has.
# `Certificate/Facts.lean` keeps the same list.
BOOKS = {"I": 48, "II": 14, "III": 37}


def arabic(book: str) -> int:
    """The number of a book from its Roman numeral: "I" is 1, "II" is 2, "XIII" is 13."""
    return ROMAN.index(book) + 1


# What a reference names: a proposition ("I.40"), its porism ("III.1 Por."), or a
# companion theorem beside it ("I.40 general", for `Prop40.general`). This order is the
# third place of `prop_key`.
KINDS = ("proposition", "porism", "companion")

REF = re.compile(r"([IVX]+)\.\s*(\d+)(?:(?:,\s*|\s+)(Por\.)|\s+([A-Za-z_][\w']*))?")


class Ref(NamedTuple):
    """A reference taken apart: `parse_ref("III.1 Por.")` is
    `Ref(book="III", n=1, kind="porism", name="porism")`.

    `name` is the last part of the Lean declaration's name: None for the proposition
    itself (`Prop1`), "porism" for its porism (`Prop1.porism`), and the companion's own
    name for a companion ("general" for `Prop40.general`). `str()` gives the reference
    back in its one written form: "III.1", "III.1 Por.", "I.40 general"."""
    book: str
    n: int
    kind: str
    name: str | None

    def __str__(self) -> str:
        base = f"{self.book}.{self.n}"
        if self.kind == "porism":
            return f"{base} Por."
        if self.kind == "companion":
            return f"{base} {self.name}"
        return base

    @property
    def parent(self) -> str:
        """The proposition this belongs to: "III.1" for "III.1 Por." and for "III.1"."""
        return f"{self.book}.{self.n}"

    @property
    def lean(self) -> str:
        """The Lean declaration: "Elements.BookIII.Prop1.porism" for "III.1 Por."."""
        base = f"Elements.Book{self.book}.Prop{self.n}"
        return f"{base}.{self.name}" if self.name else base


def parse_ref(ref: str) -> Ref:
    """Take apart a reference: "I.40", "III.1 Por." or "I.40 general".

    Heath's spacing and comma are accepted too ("I. 4", "III. 1, Por."); `str()` of the
    result is the written form. A porism is always "Por.", never a companion called
    "porism". Raises ValueError on anything else."""
    m = REF.fullmatch(ref.strip())
    if not m:
        raise ValueError(f"not a reference: {ref!r} (expected one like 'I.40', "
                         "'III.1 Por.' or 'I.40 general')")
    book, num, porism, name = m.groups()
    if book not in ROMAN:
        raise ValueError(f"not a reference: {ref!r} ({book} is not a book of the Elements)")
    n = int(num)
    if n < 1:
        raise ValueError(f"not a reference: {ref!r} (propositions are numbered from 1)")
    if porism:
        return Ref(book, n, "porism", "porism")
    if name:
        if name.lower() in ("por", "porism"):
            raise ValueError(f"not a reference: {ref!r} (a porism is written "
                             f"'{book}.{n} Por.')")
        return Ref(book, n, "companion", name)
    return Ref(book, n, "proposition", None)


def prop_key(ref: "str | Ref"):
    """Sort references by book, then by number, then the proposition before its porism
    and its porism before its companions: I.3 before I.10, I.48 before II.1, IX before
    X, and III.1 before III.1 Por. before III.1 general.

    The key is (arabic(book), n, 0 | 1 | 2). Two companions of one proposition share a
    key: sort by `(prop_key(r), r)` for a fixed order among them."""
    r = ref if isinstance(ref, Ref) else parse_ref(ref)
    return (arabic(r.book), r.n, KINDS.index(r.kind))


def normalize(s: str) -> str:
    return " ".join(s.split())


def citations(paragraphs):
    """Propositions Euclid cites, e.g. {"I.4", "II.6"} from "[I. 4]", "[C.N. 1; II. 6]".

    A porism is cited with its proposition: "[III. 1, Por.]" cites III.1."""
    found = set()
    for p in paragraphs:
        for inner in CITATION.findall(p):
            for part in inner.split(";"):
                part = part.strip()
                m = re.fullmatch(r"([IVX]+)\.\s*(\d+)(?:,\s*Por\.)?", part)
                if m:
                    found.add(f"{m.group(1)}.{int(m.group(2))}")
    return found


# A justification in a bracket: a proposition ("I. 4"), or a postulate, definition or
# common notion, which a later book may cite with its book ("I. Post. 5", "I. Def. 15").
JUSTIFICATION = re.compile(
    r"(?:([IVX]+)\.\s*)?(Post\.|Def\.|C\.N\.)\s*(\d+)|([IVX]+)\.\s*(\d+)(?:,\s*Por\.)?")


def justifications(paragraphs):
    """Every bracketed justification Euclid gives: Post. 3, Def. 15, C.N. 1, I. 4 …

    A bracket may hold several, as "[C.N. 1; I. 30]" or "[Post. 4 and C.N. 1]".
    Book II cites Book I's Postulate 5 as "[I. Post. 5]". The postulates and common
    notions are Book I's alone, so that is Post. 5; definitions are numbered book by
    book, so "[I. Def. 15]" in a later book stays "I. Def. 15". A porism counts as its
    proposition: "[III. 16, Por.]" is III. 16.
    """
    found = []
    for p in paragraphs:
        for inner in CITATION.findall(p):
            for part in re.split(r";|\band\b", inner):
                m = JUSTIFICATION.fullmatch(" ".join(part.split()))
                if not m:
                    continue
                book, kind, num, pbook, pnum = m.groups()
                if pbook:
                    part = f"{pbook}. {int(pnum)}"
                elif book and kind == "Def.":
                    part = f"{book}. Def. {int(num)}"
                else:
                    part = f"{kind} {int(num)}"
                if part not in found:
                    found.append(part)
    return found


# Heath's porisms. A porism is a paragraph of the proof that opens "PORISM.", or
# "[PORISM." where Heath brackets it as probably interpolated (I.15).

PORISM = re.compile(r"\[?PORISM\.")


def heath_porism(book: str, n: int) -> str | None:
    """Heath's porism to proposition n of the book, the paragraph as he prints it (I.15's
    in his square brackets), or None if he prints none."""
    _, _, proof = read(book, n)
    return next((p for p in proof if PORISM.match(p)), None)


def heath_porisms() -> frozenset:
    """Every (book, n) in `BOOKS` whose proof in Heath has a porism paragraph: in Books
    I-III, ("I", 15), ("III", 1) and ("III", 16)."""
    return frozenset((book, n) for book, count in BOOKS.items()
                     for n in range(1, count + 1) if heath_porism(book, n))


# The main theorem of a proposition's Lean file.

class TheoremSpan(NamedTuple):
    """Where `theorem PropN` lies in the text `src` of its Lean file.

    `src[start:end]` is the whole declaration, from its docstring's `/--` to the next
    top-level declaration, the namespace's `end` or the end of the file;
    `src[body:end]` is what follows `theorem PropN` and the one blank after it: the
    statement and the proof; `doc` is the docstring's text, between `/--` and `-/`.
    Before `start` come the file's header and its helpers; from `end` on, the porism,
    the companions and anything else after the main theorem."""
    start: int
    body: int
    end: int
    doc: str


def theorem_span(src: str, n: int) -> TheoremSpan | None:
    """Find the documented `theorem PropN` in `src`; None if there is none."""
    m = re.search(r"/--((?:(?!-/).)*?)-/\s*theorem Prop%d\s" % n, src, re.S)
    if not m:
        return None
    # The theorem runs until the next top-level declaration or the namespace end.
    rest = src[m.end():]
    stop = re.search(r"^(end |theorem |lemma |def |structure |/--|/-!|@\[)", rest, re.M)
    end = m.end() + (stop.start() if stop else len(rest))
    return TheoremSpan(m.start(), m.end(), end, m.group(1))


def lean_path(book: str, n: int) -> Path:
    """The Lean file of a proposition, which also holds its porism and companions."""
    return ROOT / "Elements" / f"Book{book}" / f"Prop{n:02d}.lean"


# Fingerprints: "sha256:" and the first 16 hex digits of a SHA-256.

HASH = re.compile(r"sha256:[0-9a-f]{16}")


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()[:16]


def fingerprint(*statements: str) -> str:
    """A short hash of one or more printed statements, whitespace aside: each statement
    with its runs of whitespace made one space, joined by newlines."""
    return _sha("\n".join(normalize(s) for s in statements).encode())


def review_fingerprint(facts: dict, ref: str) -> str:
    """The `fingerprint` a review record of the proposition `ref` must carry: of the
    `statement` of its facts.json entry, then those of its `attached` entries (its
    porism, then its companions) in the order listed. A change to any of them is a
    change to what the record reviewed (Certificate/FIELDS.md, review/SCHEMA.md)."""
    by_ref = {p["ref"]: p for p in facts["propositions"]}
    entries = [by_ref[ref]] + [by_ref[a] for a in by_ref[ref].get("attached", [])]
    missing = [e["ref"] for e in entries if "statement" not in e]
    if missing:
        raise KeyError(f"facts.json has no `statement` for {', '.join(missing)}: rerun "
                       "`lake env lean Certificate/Facts.lean`")
    return fingerprint(*(e["statement"] for e in entries))


def file_hash(path) -> str:
    """A short hash of a file's exact bytes, in the form `fingerprint` uses. A review
    record's `lean` is the file_hash of `lean_path(book, n)`."""
    return _sha(Path(path).read_bytes())


def text_hash(source: str) -> str:
    """A review record's `text` stamp: a short hash of what the record says, read from
    `source`, its TOML. Every section counts but [review], which holds the stamps and the
    reviewer's account of the reading, and [statement] counts without its `fingerprint`,
    a stamp of the statements; so writing a stamp never changes the text it stamps.
    Comments, layout and the order of keys do not count: the record as TOML reads it is
    written as JSON with its keys sorted, and hashed. Raises ValueError when `source` is
    not valid TOML."""
    tomllib = _toml()
    try:
        record = tomllib.loads(source)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"not valid TOML: {e}") from None
    record.pop("review", None)
    if isinstance(record.get("statement"), dict):
        record["statement"].pop("fingerprint", None)
    return _sha(json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                           default=str).encode())


# The review records, review/<book>/NN.toml. review/SCHEMA.md says what each field
# means; this is the machine's half of it.

REVIEW = ROOT / "review"
NOTE_LIMIT = 160  # characters in [statement] note, shown in the page's field table
SHORT_LIMIT = 70  # characters in [statement] short, which stands beside the badge
SCOPES = ("full", "restricted", "partial")
ROUTES = ("euclid", "modified", "alternative")
PASSAGES = ("carried", "helper", "grouped", "case", "given", "different", "unformalized")
OVERLAPS = ("states", "gives", "step")  # [overlap] kind, the catalogue's three kinds
STAGES = ("exceptions", "full")
VERDICTS = ("pass", "fail", "n/a")
TAG_KINDS = ("scope", "representation")
COMMIT = re.compile(r"[0-9a-f]{7,40}")
WORD = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
# A name as a proof binds it, for a passage's `unused`: one Lean identifier, with no dots,
# as `hCHG_EHC` or `FC`, or `this`, the name of a `have` that gives none.
BOUND_NAME = re.compile(r"[^\W\d][\w'!?₀-₉]*")

_STR, _LIST, _TABLE, _NAMES, _BOOL = "string", "list", "table", "names", "boolean"
_WAYS = "ways"  # a list of combinations, each a list of axiom names
# Each section's keys, as (type, required). A "stamp" key is written by
# scripts/review_stamp.py, and required unless an unstamped record is asked for.
# [review] `text` is a stamp too, but not yet required: the records stamped before it
# gain it from `review_stamp.py --migrate-text`, or from a reader (docs/WORKFLOW.md,
# section 6), and it becomes "stamp" once every record carries it.
FIELDS = {
    "statement": {"scope": (_STR, True), "hypotheses": (_LIST, False),
                  "omitted": (_LIST, False), "note": (_STR, False),
                  "short": (_STR, False), "fingerprint": (_STR, "stamp"),
                  "companions": (_LIST, False)},
    "route": {"kind": (_STR, True), "note": (_STR, False)},
    "representation": {"tags": (_LIST, True), "note": (_STR, False)},
    "overlap": {"rule": (_STR, True), "also": (_LIST, False), "kind": (_STR, True),
                "ways": (_WAYS, False), "note": (_STR, False)},
    "coverage": {"checked": (_LIST, False), "explains": (_LIST, False),
                 "text_only": (_LIST, False)},
    "passage": {"at": (_STR, True), "kind": (_STR, True), "helper": (_STR, False),
                "note": (_STR, False), "unused": (_NAMES, False)},
    "figure": {"case": (_STR, False), "every_case": (_BOOL, False), "note": (_STR, False)},
    "review": {"stage": (_STR, True), "commit": (_STR, "stamp"), "lean": (_STR, "stamp"),
               "text": (_STR, False), "reviewer": (_STR, True), "run": (_STR, False),
               "items": (_TABLE, False)},
}
REQUIRED = ("statement", "route", "review")


class ReviewError(ValueError):
    """A review record (or review/terms.toml) that is missing, unreadable or breaks
    review/SCHEMA.md. `where` is the file, `problems` each fault found in it."""

    def __init__(self, where: str, problems: list[str]):
        self.where, self.problems = where, problems
        detail = problems[0] if len(problems) == 1 else "".join(f"\n  - {p}" for p in problems)
        super().__init__(f"{where}: {detail}")


def review_path(book: str, n: int) -> Path:
    return REVIEW / book / f"{n:02d}.toml"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_terms() -> dict:
    """review/terms.toml: the tags a record's [representation] may carry, as
    {tag: {"kind": "scope" | "representation", "meaning": "one line"}}, and, for a tag
    that changes how a whole statement is read, a few words to stand beside the badge,
    `badge`."""
    path = REVIEW / "terms.toml"
    tomllib = _toml()
    try:
        data = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise ReviewError(_rel(path), [str(e)]) from None
    tags = data.get("tag")
    if set(data) != {"tag"} or not isinstance(tags, dict) or not tags:
        raise ReviewError(_rel(path), ["expected [tag.<name>] tables and nothing else"])
    problems = []
    for name, t in tags.items():
        if not WORD.fullmatch(name):
            problems.append(f"tag {name!r}: a tag is lower-case words joined by hyphens")
        if not isinstance(t, dict) or not {"kind", "meaning"} <= set(t) <= {
                "kind", "meaning", "badge"}:
            problems.append(f"tag {name!r}: needs `kind` and `meaning`, may have `badge`, "
                            "and nothing else")
            continue
        if "badge" in t and (not isinstance(t["badge"], str) or not t["badge"].strip()
                             or "\n" in t["badge"] or len(t["badge"]) > SHORT_LIMIT):
            problems.append(f"tag {name!r}: `badge` is a few plain words on one line, at "
                            f"most {SHORT_LIMIT} characters")
        if t["kind"] not in TAG_KINDS:
            problems.append(f"tag {name!r}: `kind` is one of {', '.join(TAG_KINDS)}")
        if not isinstance(t["meaning"], str) or not t["meaning"].strip() or "\n" in t["meaning"]:
            problems.append(f"tag {name!r}: `meaning` is one line of plain words")
    if problems:
        raise ReviewError(_rel(path), problems)
    return tags


def _shape(record, require_stamp: bool) -> list[str]:
    """The faults of form: unknown or missing sections and keys, and wrong types."""
    problems = []
    bad = problems.append
    if not isinstance(record, dict):
        return ["a record is a TOML table"]
    for section in record:
        if section not in FIELDS:
            bad(f"unknown section [{section}] (the sections are: {', '.join(FIELDS)})")
    for section in REQUIRED:
        if section not in record:
            bad(f"[{section}] is missing")
    tables = []
    for section, fields in FIELDS.items():
        value = record.get(section)
        if value is None:
            continue
        if section == "passage":
            if isinstance(value, list) and all(isinstance(t, dict) for t in value):
                tables += [(f"[[passage]] {i}", t, fields) for i, t in enumerate(value, 1)]
            else:
                bad("passages are an array of tables: write each as [[passage]]")
        elif isinstance(value, dict):
            tables.append((f"[{section}]", value, fields))
        else:
            bad(f"[{section}] must be a table")
    for label, table, fields in tables:
        for key in table:
            if key not in fields:
                bad(f"{label}: unknown key `{key}` (the keys are: {', '.join(fields)})")
        for key, (kind, required) in fields.items():
            if key not in table:
                if required is True:
                    bad(f"{label}: `{key}` is missing")
                elif required == "stamp" and require_stamp:
                    bad(f"{label}: `{key}` is missing (scripts/review_stamp.py writes it)")
                continue
            v = table[key]
            if kind == _STR and not (isinstance(v, str) and v.strip()):
                bad(f"{label}: `{key}` must be a non-empty string")
            elif kind == _LIST and not (isinstance(v, list)
                                        and all(isinstance(x, str) and x.strip() for x in v)):
                bad(f"{label}: `{key}` must be a list of non-empty strings")
            elif kind == _TABLE and not isinstance(v, dict):
                bad(f"{label}: `{key}` must be a table")
            elif kind == _NAMES:
                if not (isinstance(v, list) and v and all(isinstance(x, str) for x in v)):
                    bad(f"{label}: `{key}` must be a non-empty list of names; leave it out "
                        "when there are none")
                    continue
                for x in v:
                    if x == "_" or not BOUND_NAME.fullmatch(x):
                        bad(f"{label}: `{key}`: {x!r} is not a name as a proof binds it: one "
                            "Lean identifier, as 'hAB_FC' or 'FC', or 'this' for a `have` "
                            "that gives no name")
                for x in sorted({x for x in v if v.count(x) > 1}):
                    bad(f"{label}: `{key}` lists {x!r} twice")
            elif kind == _BOOL and not isinstance(v, bool):
                bad(f"{label}: `{key}` must be true or false")
            elif kind == _WAYS and not (isinstance(v, list) and v and all(
                    isinstance(w, list) and w and all(isinstance(x, str) and x.strip()
                                                      for x in w) for w in v)):
                bad(f"{label}: `{key}` must be a non-empty list of combinations, each a "
                    "non-empty list of axiom names; leave it out when there are none")
    return problems


def validate_review(record: dict, book: str, n: int, *, require_stamp: bool = True,
                    where: str | None = None) -> dict:
    """Check a parsed review record of proposition n of the book against
    review/SCHEMA.md, and return it with the defaults filled in: [statement]
    hypotheses, omitted and companions, [coverage]'s three lists, `passage` and
    [review] items, each empty when not given. Raises ReviewError naming every fault.

    With require_stamp=False `fingerprint`, `commit` and `lean` may be absent, for
    scripts/review_stamp.py to write. `text`, also a stamp, may be absent either way, for
    now (see FIELDS). Whether the stamps are current (the fingerprint against facts.json,
    `lean` against the file, `text` against the record) is check_fidelity's business, not
    this function's."""
    where = where or _rel(review_path(book, n))
    problems = _shape(record, require_stamp)
    if problems:
        raise ReviewError(where, problems)
    bad = problems.append

    st, route, rv = record["statement"], record["route"], record["review"]
    for key in ("hypotheses", "omitted", "companions"):
        st.setdefault(key, [])
    if "coverage" in record:
        for key in FIELDS["coverage"]:
            record["coverage"].setdefault(key, [])
    record.setdefault("passage", [])
    rv.setdefault("items", {})

    def plain(s: str) -> str:
        return normalize(s.replace("*", ""))

    _, enunciation, proof = read(book, n)
    enunciation = plain(enunciation)
    porism = plain(heath_porism(book, n) or "")
    proof_text = plain(" ".join(proof))

    # [statement]
    scope = st["scope"]
    if scope not in SCOPES:
        bad(f"[statement]: `scope` is one of {', '.join(SCOPES)}, not {scope!r}")
    note = st.get("note", "")
    if scope in ("restricted", "partial") and not note:
        bad(f"[statement]: a {scope} statement needs a `note`, shown beside the badge")
    if len(note) > NOTE_LIMIT:
        bad(f"[statement]: `note` has {len(note)} characters; the limit is {NOTE_LIMIT}")
    if "\n" in note:
        bad("[statement]: `note` is one line")
    short = st.get("short", "")
    if scope in ("restricted", "partial") and not short:
        bad(f"[statement]: a {scope} statement needs a `short`, a few words shown beside "
            "the badge")
    if len(short) > SHORT_LIMIT:
        bad(f"[statement]: `short` has {len(short)} characters; the limit is {SHORT_LIMIT}")
    if "\n" in short or short.rstrip().endswith("."):
        bad("[statement]: `short` is a few words on one line, with no full stop")
    if short[:1].isupper() and not re.match(r"[A-Z]{2}|[A-Z]\b|Euclid", short):
        bad("[statement]: `short` begins with a small letter, since it follows a colon "
            "or a bracket")
    if scope == "full" and (st["hypotheses"] or st["omitted"]):
        bad("[statement]: a full statement has no `hypotheses` and no `omitted`")
    if scope == "restricted" and not st["hypotheses"]:
        bad("[statement]: a restricted statement lists its extra `hypotheses`")
    if scope == "restricted" and st["omitted"]:
        bad("[statement]: a statement with `omitted` clauses is partial, not restricted")
    if scope == "partial" and not st["omitted"]:
        bad("[statement]: a partial statement lists its `omitted` clauses")
    if scope == "partial" and "coverage" not in record:
        bad("a partial statement needs a [coverage] clause map")
    for q in st["omitted"]:
        if plain(q) not in enunciation and plain(q) not in porism:
            bad(f"[statement]: omitted {q!r} is not quoted from Heath's enunciation or porism")
    for c in st["companions"]:
        try:
            r = parse_ref(c)
        except ValueError as e:
            bad(f"[statement]: companions: {e}")
            continue
        if r.kind != "companion" or r.parent != f"{book}.{n}":
            bad(f"[statement]: companions: {c!r} is not a companion of {book}.{n} "
                f"(write '{book}.{n} <name>', as 'I.40 general')")
    if "fingerprint" in st and not HASH.fullmatch(st["fingerprint"]):
        bad("[statement]: `fingerprint` is 'sha256:' and 16 hex digits")

    # [route]
    if route["kind"] not in ROUTES:
        bad(f"[route]: `kind` is one of {', '.join(ROUTES)}, not {route['kind']!r}")
    elif route["kind"] != "euclid" and "note" not in route:
        bad(f"[route]: a {route['kind']} route needs a `note` saying how it differs")

    # [representation]
    if "representation" in record:
        tags = record["representation"]["tags"]
        terms = load_terms()
        if not tags:
            bad("[representation]: `tags` is empty; leave the section out instead")
        if len(set(tags)) != len(tags):
            bad("[representation]: a tag is listed twice")
        for t in tags:
            if t not in terms:
                bad(f"[representation]: tag {t!r} is not in review/terms.toml")
            elif terms[t]["kind"] == "scope" and scope == "full":
                bad(f"[representation]: tag {t!r} narrows the statement, but its scope is full")

    # [overlap]: `rule` with `also` is the first combination that contains the proposition,
    # and `ways` lists any further ones, each a different set of rules. Whether each is
    # an axiom, and proved in Audit/Overlaps.lean, is check_fidelity's business.
    if "overlap" in record:
        ov = record["overlap"]
        ways = ov.get("ways", [])
        if any(re.search(r"\s", r) for r in [ov["rule"]] + ov.get("also", []) + sum(ways, [])):
            bad("[overlap]: `rule`, `also` and `ways` name axioms as facts.json writes them, "
                "as 'Tacit.outside_of_between'")
        if ov["kind"] not in OVERLAPS:
            bad(f"[overlap]: `kind` is one of {', '.join(OVERLAPS)}, the overlap catalogue's "
                f"three kinds, not {ov['kind']!r}")
        elif ov["kind"] == "step" and "note" not in ov:
            bad("[overlap]: a rule that supplies a step needs a `note` saying which step, "
                "and in which proof")
        if ways and ov["kind"] == "step":
            bad("[overlap]: only rules that state the proposition or give it at once have "
                "further `ways`; a rule that supplies a step does not contain it")
        seen_ways = []
        combinations = [([ov["rule"]] + ov.get("also", []), "`rule` and `also`")]
        combinations += [(way, f"`ways` {i}") for i, way in enumerate(ways, 1)]
        for way, label in combinations:
            for x in sorted({x for x in way if way.count(x) > 1}):
                bad(f"[overlap]: {label} lists {x!r} twice")
            same = [j for j, s in enumerate(seen_ways) if s == frozenset(way)]
            if same:
                bad(f"[overlap]: {label} names the same rules as "
                    + ("`rule` and `also`" if same[0] == 0 else f"`ways` {same[0]}")
                    + "; each combination is a different set of rules")
            seen_ways.append(frozenset(way))

    # [coverage]
    if "coverage" in record:
        cov = record["coverage"]
        if not any(cov[k] for k in FIELDS["coverage"]):
            bad("[coverage]: the clause map is empty")
        for q in cov["text_only"]:
            if plain(q) not in enunciation and plain(q) not in proof_text:
                bad(f"[coverage]: text_only {q!r} is not quoted from Heath")

    # [figure]: `every_case` says only which words lead the caption, so the section still
    # needs a `case` or a `note`, and `every_case` the `case` that names the cases drawn.
    if "figure" in record:
        fig = record["figure"]
        if "case" not in fig and "note" not in fig:
            bad("[figure]: give its `case`, its `note`, or both; or leave the section out")
        if fig.get("every_case") and "case" not in fig:
            bad("[figure]: `every_case` needs the `case` that names the cases the figure "
                "draws, for the caption \"Drawn for every case: …\"")

    # [[passage]]
    seen = set()
    for i, p in enumerate(record["passage"], 1):
        label = f"[[passage]] {i}"
        kind = p["kind"]
        if kind not in PASSAGES:
            bad(f"{label}: `kind` is one of {', '.join(PASSAGES)}, not {kind!r}")
        elif kind != "carried" and "note" not in p:
            bad(f"{label}: a {kind} passage needs a `note`, shown on the page")
        if kind == "helper" and "helper" not in p:
            bad(f"{label}: a helper passage names its `helper`")
        if kind == "different" and route["kind"] == "euclid":
            bad(f"{label}: a passage argued another way changes Euclid's route: make the "
                "[route] modified (or alternative), or the passage another kind")
        if "helper" in p and re.search(r"\s", p["helper"]):
            bad(f"{label}: `helper` is one Lean name, as 'Prop1.middle'")
        at = plain(p["at"])
        found = proof_text.count(at)
        if found == 0:
            bad(f"{label}: `at` {p['at']!r} is not quoted from Heath's proof")
        elif found > 1:
            bad(f"{label}: `at` {p['at']!r} occurs {found} times in Heath's proof; "
                "quote enough words to name one place")
        if at in seen:
            bad(f"{label}: another passage is already `at` {p['at']!r}")
        seen.add(at)

    # [review]
    if rv["stage"] not in STAGES:
        bad(f"[review]: `stage` is one of {', '.join(STAGES)}, not {rv['stage']!r}")
    if "commit" in rv and not COMMIT.fullmatch(rv["commit"]):
        bad("[review]: `commit` is a git commit, 7 to 40 lower-case hex digits")
    if "lean" in rv and not HASH.fullmatch(rv["lean"]):
        bad("[review]: `lean` is 'sha256:' and 16 hex digits")
    if "text" in rv and not HASH.fullmatch(rv["text"]):
        bad("[review]: `text` is 'sha256:' and 16 hex digits")
    if rv["stage"] == "full" and ("run" not in rv or "," not in rv["reviewer"]):
        bad("[review]: a full review names its `run`, and its `reviewer` with a role, as "
            "'Claude Opus 5.5, records crew', so the reviewer can be told from the authors")
    for key, verdict in rv["items"].items():
        if not WORD.fullmatch(key):
            bad(f"[review]: items: {key!r} is not an item key (lower-case words and hyphens)")
        if verdict not in VERDICTS:
            bad(f"[review]: items: {key} is one of {', '.join(VERDICTS)}, not {verdict!r}")

    if problems:
        raise ReviewError(where, problems)
    return record


def load_review(book: str, n: int, *, require_stamp: bool = True) -> dict:
    """Read and check review/<book>/NN.toml; return it as a dict, defaults filled in
    (see `validate_review`), or raise ReviewError with the file and every fault."""
    path = review_path(book, n)
    if not path.exists():
        raise ReviewError(_rel(path), ["missing: every proposition has a review record "
                                       "(review/SCHEMA.md)"])
    tomllib = _toml()
    try:
        record = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ReviewError(_rel(path), [f"not valid TOML: {e}"]) from None
    return validate_review(record, book, n, require_stamp=require_stamp, where=_rel(path))


def _schema_examples():
    """The worked examples in review/SCHEMA.md: each ```toml block whose first line is a
    comment naming its record, "# review/III/16.toml"."""
    text = (REVIEW / "SCHEMA.md").read_text()
    for block in re.findall(r"```toml\n(.*?)```", text, re.S):
        m = re.match(r"# review/([IVX]+)/(\d+)\.toml\n", block)
        if m:
            yield m.group(1), int(m.group(2)), block


def _self_test() -> int:
    """Check the contracts against themselves; return the number of faults."""
    faults = []
    for text, want in [("I.40", ("I", 40, "proposition", None)),
                       ("III.1 Por.", ("III", 1, "porism", "porism")),
                       ("III. 1, Por.", ("III", 1, "porism", "porism")),
                       ("I.40 general", ("I", 40, "companion", "general")),
                       ("I. 4", ("I", 4, "proposition", None))]:
        if tuple(parse_ref(text)) != want:
            faults.append(f"parse_ref({text!r}) is {tuple(parse_ref(text))}, not {want}")
    for text in ("III.1 Por.", "I.40 general", "XIII.18"):
        if str(parse_ref(text)) != text:
            faults.append(f"str(parse_ref({text!r})) is {str(parse_ref(text))!r}")
    for text in ("I.40 porism", "Def. 15", "I.0", "Q.1", "I.40 Por"):
        try:
            parse_ref(text)
            faults.append(f"parse_ref({text!r}) should fail")
        except ValueError:
            pass
    order = ["I.3", "I.10", "I.15", "I.15 Por.", "I.40", "I.40 general", "I.48", "II.1",
             "III.1", "III.1 Por.", "IX.1", "X.1"]
    if sorted(reversed(order), key=prop_key) != order:
        faults.append(f"prop_key sorts {order} as {sorted(reversed(order), key=prop_key)}")
    early = {p for p in heath_porisms() if p[0] in ("I", "II", "III")}
    if early != {("I", 15), ("III", 1), ("III", 16)}:
        faults.append(f"heath_porisms() finds {sorted(early)} in Books I-III")
    try:
        load_terms()
    except ReviewError as e:
        faults.append(str(e))
    tomllib = _toml()
    examples = 0
    for book, n, block in _schema_examples():
        examples += 1
        try:
            example = validate_review(tomllib.loads(block), book, n,
                                      where=f"review/SCHEMA.md, the example for {book}.{n}")
        except (ReviewError, tomllib.TOMLDecodeError) as e:
            faults.append(str(e))
            continue
        # The examples' `text` stamps are the test values of text_hash.
        if example["review"].get("text") != text_hash(block):
            faults.append(f"review/SCHEMA.md, the example for {book}.{n}: its `text` is "
                          f"{example['review'].get('text', '(none)')}, but text_hash gives "
                          f"{text_hash(block)}")
    # [overlap] `kind`: required, one of the catalogue's three kinds, and "step" with its
    # note. A record with no kind is rejected, so no page words an overlap by a guess.
    for overlap, ok in [({"rule": "Tacit.circle_eq", "kind": "gives"}, True),
                        ({"rule": "Tacit.circle_eq", "kind": "states"}, True),
                        ({"rule": "Tacit.circle_eq"}, False),
                        ({"rule": "Tacit.angle_le_two_right", "kind": "step",
                          "note": "Metric 5 supplies I.13's upper bound on an angle in Prop47.within."}, True),
                        ({"rule": "Tacit.angle_le_two_right", "kind": "step"}, False),
                        ({"rule": "Tacit.circle_eq", "kind": "contains"}, False)]:
        record = {"statement": {"scope": "full"}, "route": {"kind": "euclid"},
                  "overlap": dict(overlap),
                  "review": {"stage": "exceptions", "reviewer": "Claude Opus 5.5"}}
        try:
            validate_review(record, "I", 7, require_stamp=False, where="a test record")
            if not ok:
                faults.append(f"validate_review accepts [overlap] {overlap}")
        except ReviewError as e:
            if ok:
                faults.append(str(e))
    # [overlap] `ways`: the further combinations that contain the proposition, for a rule
    # that states it or gives it at once, each a different set of rules from `rule` with
    # `also` and from each other. Whether Audit/Overlaps.lean proves each is
    # check_fidelity's business.
    first = {"rule": "Tacit.circle_eq", "also": ["Tacit.inside_not_on"], "kind": "gives"}
    crossing = ["Definition15", "Tacit.len_lt_of_inside", "Tacit.lt_irrefl"]
    radius = ["Definition15", "Tacit.inside_not_on", "Tacit.on_circle_of_len_eq"]
    for ways, change, ok in [
            ([crossing, radius], {}, True),
            ([crossing], {"kind": "states"}, True),
            ([["Tacit.circle_eq"]], {"also": []}, False),
            ([radius], {"kind": "step", "note": "The rules supply a step of III.5's proof."},
             False),
            ([["Tacit.inside_not_on", "Tacit.circle_eq"]], {}, False),
            ([radius, list(reversed(radius))], {}, False),
            ([radius + ["Definition15"]], {}, False),
            ([["Tacit.circle_eq", "Tacit.inside not_on"]], {}, False),
            ([], {}, False),
            ([[]], {}, False),
            (radius, {}, False),
            ([[""]], {}, False)]:
        record = {"statement": {"scope": "full"}, "route": {"kind": "euclid"},
                  "overlap": {**first, **change, "ways": ways},
                  "review": {"stage": "exceptions", "reviewer": "Claude Opus 5.5"}}
        try:
            validate_review(record, "III", 5, require_stamp=False, where="a test record")
            if not ok:
                faults.append(f"validate_review accepts [overlap] {record['overlap']}")
        except ReviewError as e:
            if ok:
                faults.append(str(e))
    # [[passage]] `unused`: a non-empty list of distinct names, each as a proof binds it.
    # Whether the Lean beneath binds them is check_fidelity's business.
    for unused, ok in [(["FC", "GB"], True), (["this"], True), (["hAB_FC'", "h₁"], True),
                       ([], False), ("FC", False), (["FC", "FC"], False), ([""], False),
                       (["_"], False), (["h FC"], False), (["hAB.1"], False),
                       (["2FC"], False), ([["FC"]], False)]:
        record = {"statement": {"scope": "full"}, "route": {"kind": "euclid"},
                  "passage": [{"at": "and let the straight lines FC, GB be joined",
                               "kind": "carried", "unused": unused}],
                  "review": {"stage": "exceptions", "reviewer": "Claude Opus 5.5"}}
        try:
            validate_review(record, "I", 5, require_stamp=False, where="a test record")
            if not ok:
                faults.append(f"validate_review accepts [[passage]] unused = {unused!r}")
        except ReviewError as e:
            if ok:
                faults.append(str(e))
    records = 0
    for book, count in BOOKS.items():
        for n in range(1, count + 1):
            if review_path(book, n).exists():
                records += 1
                try:
                    load_review(book, n)
                except ReviewError as e:
                    faults.append(str(e))
    for f in faults:
        print("  ✗ " + f)
    if not faults:
        print(f"✓ contracts: references, porisms, review/terms.toml, {examples} examples in "
              f"review/SCHEMA.md and {records} review records hold")
    return len(faults)


if __name__ == "__main__":
    sys.exit(1 if _self_test() else 0)
