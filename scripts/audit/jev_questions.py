"""Prepare Jev's audit questions for Stoicheia's Books I to III, and their calibration set.

The questions compare Heath's enunciations with the Lean statements and their declared
scope; inspect citation and hypothesis use in individual proof units; ask whether the
representation bridges state the conditional connections; compare the commentary with
its named declarations and declared route; and inspect the Heath figures and captions.
Bridge dependency placement is supplied as context in bridge_placement but is not itself
adjudicated; a bridge-stated answer does not establish all of P13. A record whose
representations item is `pass` gets the bridges its connection rests on (`bundle`), and one
marked `n/a` none.
They do not check proofs in Lean, verify historical quotations, or inspect the figures
at a glance. Helper signatures expose their use, not the work inside their proofs.
Ten synthetic defect controls change generated rows only. Expectations report the
review records' claims and remain local, as do provenance, mutations and coverage.

Run from anywhere with Python 3.11 or later, using only the standard library, the
repository's heath.py and jev.py, imported by path, and a copy, word for word, of the
comment reader the scripts share, heath.py's `comment_end`:

    python3 scripts/audit/jev_questions.py --commit REV
    python3 scripts/audit/jev_questions.py --commit REV --check
    python3 scripts/audit/jev_questions.py --commit REV --out PATH --manifest PATH
    python3 scripts/audit/jev_questions.py --commit REV --calibration [--out DIR] [--check]
    python3 scripts/audit/jev_questions.py --restore-figures MANIFEST
    python3 scripts/audit/jev_questions.py --tally QUESTIONS RESULTS [--svg-width PIXELS]

Generation reads no credentials and sends nothing. Every evidence file is compared with
`git show REV:path`; every excerpt records its exact source slice and hash. Failure to read
the committed evidence, missing evidence, ambiguous names and differences from the revision
are errors. Evidence paths must be relative, without parent traversal or symlinks, and
resolve inside the repository. Both helpers' paths pass those checks and must name
regular files; their accepted code is read and compiled before any of it runs.
Each Lean file's header is read by a small parser following Lean 4.35's grammar, before any
masking:
an optional `module`, then imports in the four forms
`import`, `public import`, `meta import` and `public meta import`, each naming one module of
plain or «...» components and ending its line, with ordinary comments between the words. A
doc comment or any other word before an import, `prelude`, `import all`, a block comment
running on from an import's line, and any `import` after the header outside a «...» name are
refused. A private declaration is seen only in its own file. Every output path rejects
symlinks, evidence files, tracked files other than the default outputs, Git metadata,
protected paths independently of the index, and collisions with the others; an output may be
outside the repository, except that a calibration directory must be inside the repository and
outside its figures/ tree.
The outputs are assembled and validated before any is written, using temporary
files and replacement without following a final symlink.
The checks cover links and aliases present when it runs, not a concurrent writer racing
it in the same tree.
--commit REV --check regenerates twice in memory and compares the bytes with the files
on disk. The manifest stays beside this script's default output unless --manifest names
another, including when --out selects another questions file. States over 12,000 characters
are labelled locally, never shortened; option orders rotate independently for ordinary rows
and controls. Keep the input and manifest beside any later answers: the client does not
copy these local provenance fields into its results. An em dash, which Heath prints once in
III.16, is written as its JSON escape, so that no output holds the character.

--calibration writes the calibration set that docs/decisions/2026-10-25-jev-calibration-bar.md
specifies, with docs/decisions/2026-10-26-jev-calibration-rulings.md beside it, governing where
the two differ, in --out (a directory, by default beside the audit): for each of P11 to P15 a
file of 20 rows, 10 controls and 10 planted faults on the propositions the entry's hash rule
gives, refused unless the records give the entry's own table, as the rulings restate it; a
manifest; and, for each
figure a plant changes, a copy under calibration-books-I-III-figures/, which the row's asset
names by its path in the repository (figures/ is never touched). Each plant takes the kind
the entry's rule gives it, tested on the generated row, and the change this file writes for
it; a kind that cannot make a genuine fault on its base, named in this file's table by
docs/decisions/2026-10-26-jev-kind-not-applying.md, is passed over as a kind whose test fails
is. The copies are written beside the calibration set, where `jev.py run` loads them, but
are not committed as files, since scripts/check_paths.py admits no .svg under docs/: the
manifest, which is committed, carries each copy's exact text, and --restore-figures MANIFEST
writes the copies back to the paths it records. It reads no commit and no key and sends
nothing, and before writing any copy it refuses a text that does not hash to its recorded
hash, a path that is not one of the calibration's figure paths, and a different file already
there. --check compares every file byte for byte: the question files and the manifest always,
a copy whenever it is present. A plant's row and the manifest keep its state before the change
whole, and every entry it removes, beside their hashes; `jev.py run` sends none of them.
--tally reads one calibration file and the output `jev.py run` wrote for it, and exits 0 only
when the entry's bar is cleared. It refuses a file not of the calibration's exact shape, and a
line not as `jev.py run` writes it for that file: its labels, its input's hash and rows, the
fingerprint of the request built again from the row, its figures rendered at the width the run
was given (--svg-width, 700 by default, as for `jev.py run`), and an answer in both orders whose
`agrees` is whether the first is the expected one. A line with a status other than 200, or an
error, records a failed request. The fourth condition is `jev.py score <output> --bar 0.8`
itself.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'docs/reports/acceptance/jev/audit-books-I-III.jsonl'
MANIFEST = OUTPUT.with_name('audit-books-I-III-manifest.json')
# The calibration set's files: one of questions for each of P11 to P15, its manifest, and the
# figures its P15 plants change, each a copy of a committed figure, which the manifest carries
# in place of a committed file.
CALIBRATION = 'calibration-books-I-III'
CALIBRATION_DIR = OUTPUT.parent
CALIBRATION_FIGURES = CALIBRATION + '-figures'
LIMIT = 12000
# The books audited, with their propositions.
BOOKS = (('I', 48), ('II', 14), ('III', 37))


class Refusal(ValueError):
    """Evidence that cannot support a reproducible question set."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise Refusal(message)


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def escaped(text: str) -> str:
    """JSON text with every em dash written as its escape. Heath prints one in III.16, after
    "AE.", which the states quote exactly; the escape keeps the character out of the files the
    generator writes while the decoded text stays Heath's."""
    return text.replace('\u2014', '\\u2014')


def jsonl(rows: list[dict]) -> bytes:
    return ''.join(escaped(dumps(r)) + '\n' for r in rows).encode('utf-8')


def pretty(value: Any) -> bytes:
    return (escaped(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)) + '\n').encode('utf-8')


def sha(data: bytes | str) -> str:
    return 'sha256:' + hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def checked_path(path: Path) -> Path:
    """Reject symlinks throughout a path before resolving it, including missing leaves."""
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(mode), f'{path}: symlink component {current}')
    return path.resolve()


def evidence_path(path: str) -> Path:
    local = Path(path)
    require(not local.is_absolute() and '..' not in local.parts,
            f'{path}: evidence path must be relative with no .. component')
    resolved = checked_path(ROOT / local)
    require(resolved.is_relative_to(ROOT), f'{path}: evidence path resolves outside the repository')
    return resolved


def read_no_follow(path: Path) -> bytes:
    """Refuse a final symlink even if it appeared after the component checks."""
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        return stream.read()


HELPERS = (('jev_questions_heath', 'scripts/heath.py'),
           ('jev_questions_client', 'scripts/audit/jev.py'))


def _prepare_modules(helpers: tuple[tuple[str, str], ...]) -> list:
    checked = []
    for name, path in helpers:
        resolved = evidence_path(path)
        require(resolved.is_file(), f'{path}: helper module is missing or not a regular file')
        checked.append((name, path, resolved))
    return [(name, path, resolved, compile(read_no_follow(resolved), str(resolved), 'exec',
                                            dont_inherit=True))
            for name, path, resolved in checked]


def _execute_modules(code: list) -> list:
    result = []
    for name, path, resolved, compiled in code:
        spec = importlib.util.spec_from_file_location(name, resolved)
        require(spec is not None, f'cannot import {path}')
        loaded = importlib.util.module_from_spec(spec)
        sys.modules[name] = loaded
        exec(compiled, loaded.__dict__)
        result.append(loaded)
    return result


def helper_modules(helpers: tuple[tuple[str, str], ...]) -> list:
    """Check every helper's path, then read and compile each, before any helper runs."""
    return _execute_modules(_prepare_modules(helpers))


# The scripts' one reader of where a Lean comment ends is heath.py's `comment_end`
# (#206, #349). The generator must read the evidence commit's heath.py as a helper,
# which at an older commit has no reader, so it holds its own copy, word for word but
# for the name, which tests/test_negative_tests.py holds to heath's by its source and
# by what it reads (the coordinator's ruling of 23 October 05:20).
def shared_comment_end(src: str, i: int) -> int | None:
    """Where the comment that begins at `i`, with `--` or `/-`, ends, as Lean 4.35 reads
    it (`whitespace` and `finishCommentBlock` in Lean/Parser/Basic.lean): a `--` comment
    at the line feed that ends its line, or the end of `src`; a `/- … -/` block,
    docstrings and nested blocks among them, just past the `-/` that closes it, or None
    if none does. A block's body begins at its fourth character, after `/--` or `/-!`,
    and past the third of any other `/-`, which Lean passes over, so that `/-/- -/` is a
    whole comment and the `-/` of `/--/` closes nothing. `_read_code`, and so
    `read_lean` and `lean_comments`, and check_style's notes call this (#206). It uses
    nothing else of this file, so that a program that cannot import it holds a copy, word
    for word, which its tests hold to this one: the Jev generator, and risk.py from
    #349's second train."""
    if src.startswith("--", i):
        end = src.find("\n", i)
        return len(src) if end < 0 else end
    j, nested = i + 3, 1
    while j < len(src):
        pair = src[j:j + 2]
        nested += (pair == "/-") - (pair == "-/")
        j += 2 if pair in ("/-", "-/") else 1
        if not nested:
            return j
    return None


try:
    prepared_helpers = _prepare_modules(HELPERS)
    heath, jev = _execute_modules(prepared_helpers)
except (Refusal, OSError) as error:
    if __name__ != '__main__':
        raise
    raise SystemExit(f'refused: {error}') from None


class Evidence:
    def __init__(self, commit: str):
        require(re.fullmatch(r'[0-9a-f]{40}', commit), '--commit requires a full commit hash')
        self.commit = commit
        self.data: dict[str, bytes] = {}

    def read(self, path: str) -> str:
        if path not in self.data:
            raw = read_no_follow(evidence_path(path))
            try:
                result = subprocess.run(['git', 'show', f'{self.commit}:{path}'], cwd=ROOT,
                                        capture_output=True, check=False)
            except OSError as error:
                raise Refusal(f'git show could not read committed evidence for {path}: {error}') from error
            if result.returncode:
                reason = result.stderr.decode('utf-8', errors='replace')
                raise Refusal(f'git show failed for {path}: {reason.strip()}')
            require(result.stdout == raw, f'{path}: differs from evidence commit {self.commit}')
            self.data[path] = raw
        return self.data[path].decode('utf-8')

    def excerpt(self, source: dict, field: str, path: str, start: int, end: int,
                *, transformation: str | None = None) -> str:
        raw = self.read(path)
        require(0 <= start < end <= len(raw), f'{path}: invalid excerpt {start}:{end}')
        text = raw[start:end]
        entry = {'field': field, 'path': path, 'start': start, 'end': end,
                 'lines': [raw.count('\n', 0, start) + 1, raw.count('\n', 0, end - 1) + 1],
                 'sha256': sha(text)}
        if transformation:
            entry['transformation'] = transformation
        source['excerpts'].append(entry)
        return text

    def whole(self, source: dict, field: str, path: str) -> str:
        return self.excerpt(source, field, path, 0, len(self.read(path)))

    def unchanged(self) -> None:
        for path, raw in self.data.items():
            require(read_no_follow(evidence_path(path)) == raw, f'{path}: changed during generation')


# A small source lexer, not a Lean elaborator. Masking preserves offsets and line breaks.
# Strings, nested comments and balanced binders cannot terminate a signature.
# Lean 4.35's name characters (Init/Meta/Defs.lean, isIdFirst and isIdRest): a name begins
# with an ASCII letter, `_` or a letter-like character, and goes on with these, ASCII digits,
# `'`, `!`, `?` and subscripts. The ranges are written as `re` escapes, in Lean's hex values.
LETTER_LIKE = ('\\u03b1-\\u03ba\\u03bc-\\u03c9\\u0391-\\u039f\\u03a1\\u03a2\\u03a4-\\u03a9'
               '\\u03ca-\\u03fb\\u1f00-\\u1ffe\\u2100-\\u214f\\U0001d49c-\\U0001d59f'
               '\\u00c0-\\u00d6\\u00d8-\\u00f6\\u00f8-\\u00ff\\u0100-\\u017f')
SUBSCRIPTS = '\\u2080-\\u2089\\u2090-\\u209c\\u1d62-\\u1d6a\\u2c7c'
NAME_REST = 'A-Za-z_' + LETTER_LIKE + "0-9'!?" + SUBSCRIPTS
IDENT = '[A-Za-z_' + LETTER_LIKE + '][' + NAME_REST + ']*'
LEAN_NAME = re.compile(IDENT)
NAME = IDENT + r'(?:\.' + IDENT + r')*'
TOKEN = re.compile(NAME)
MODULE_COMPONENT = r'(?:' + IDENT + r'|«[^»\n]+»)'
MODULE_NAME = re.compile(MODULE_COMPONENT + r'(?:\.' + MODULE_COMPONENT + r')*')
MODULE_PART = re.compile(MODULE_COMPONENT)
KEYWORD_LEFT = r'(?<![' + NAME_REST + r'.«])'
KEYWORD_RIGHT = r'(?![' + NAME_REST + r'»])'
COMMAND = re.compile(
    r'^(?:@\[[^\n]*?\]\s*)?(?:(?:private|protected|noncomputable|unsafe)\s+)*'
    r'(theorem|lemma|def|abbrev|axiom|opaque|structure|class|inductive|instance|example|'
    r'namespace|section|end|open|variable|notation\S*|infix\S*|prefix\S*|'
    r'postfix\S*|attribute|set_option)\b', re.M)
# Lean 4.35's module header (Lean/Parser/Module/Syntax.lean) is an optional `module`, an
# optional `prelude`, then any number of imports, each `[public] [meta] import [all] M`. The
# generator reads the subset without `prelude` and `all`, each import ending its line.
HEADER_WORDS = frozenset({'module', 'prelude', 'public', 'meta', 'all', 'import'})
IMPORT_WORD = re.compile(KEYWORD_LEFT + 'import' + KEYWORD_RIGHT)
QUOTED_NAME = re.compile(r'«[^»\n]*»')
# A command that can declare a token: a notation whose words before `=>` hold a bar could make
# a bar an operator, and one whose token joins a name character to another, as `-x` does,
# could end a word where the patterns below see none; a macro, an elaborator or a binder
# predicate can give any syntax a meaning.
SYNTAX_WORD = re.compile(KEYWORD_LEFT
                         + r'(?:notation|infixl|infixr|infix|prefix|postfix'
                         + r'|(macro_rules|macro|elab_rules|elab|binder_predicate))'
                         + KEYWORD_RIGHT)
# A character of a name, to Lean or to the patterns' \w.
NAME_CHARACTER = re.compile(r'[\w' + NAME_REST + ']')
# The whitespace Lean reads between tokens (Lean/Parser/Basic.lean, `whitespace`, which refuses
# a tab and a carriage return), narrower than Python's: a no-break space may stand in a token.
WHITESPACE = ' \n'
# The tokens of Lean 4.35's token table (Lean.Parser.getTokenTable; toolchain 4.35.0, commit
# eb6cafb7) that begin with a letter or `_`: 282 of the 507 that the toolchain's `lean` lists
# on a scratch file importing Lean, Std and Lake (Lake.DSL adds none). Lean reads one as a
# keyword where it begins a name and is at least as long as the name, as `trace[` is.
KEYWORD_TOKENS = frozenset('''
    EStack⟨ Macro.trace[ Prop Sort StateRefT Type _ abbrev add_decl_doc assert!
    assert_not_exists assert_not_imported at attribute aux_def axiom bif
    binder_predicate binop% binop_lazy% binrel% binrel_no_prop% break
    builtin_cbv_simproc builtin_cbv_simproc_decl builtin_cbv_simproc_pattern%
    builtin_dsimproc builtin_dsimproc_decl builtin_grind_propagator builtin_initialize
    builtin_simproc builtin_simproc_decl builtin_simproc_pattern% by by? by_elab calc
    catch cbv_eval cbv_simproc cbv_simproc_decl cbv_simproc_pattern% class clear%
    coinductive coinductive_fixpoint continue date( datespec( datetime( dbg_trace
    debug_assert! decl_name% declare_bitwise_int_theorems declare_bitwise_uint_theorems
    declare_command_config_elab declare_command_config_elab_legacy declare_config_elab
    declare_config_elab_legacy declare_core_config_elab declare_eval_bin
    declare_eval_bin_bitwise declare_eval_bin_bool_pred declare_int_theorems
    declare_simp_like_tactic declare_sint_simprocs declare_syntax_cat
    declare_term_config_elab declare_uint_simprocs declare_uint_theorems decreasing_by
    def def_eval_config_item default_or_ofNonempty% deprecated_module deprecated_syntax
    deriving do docs_to_verso dsimproc dsimproc_decl elab elabToSyntax% elab_rules
    elab_stx_quot else end ensure_expected_type% ensure_type_of% estack⟨ eval_prec
    eval_prio exact?% example exists export extends f! finally for for_in% for_in'%
    forall from fun gen_injective_theorems% generalizing grind_annotated grind_pattern
    grind_propagator have haveI hiding hydrate_opaque_type idbg if import in include
    include_str inductive inductive_fixpoint inferInstanceAs infix infixl infixr
    init_grind_norm init_quot initialize instance json% leading_parser leftact% let letI
    let_delayed let_expr let_fun let_mvar% let_tmp let_λ local logNamedError
    logNamedErrorAt logNamedWarning logNamedWarningAt m! macro macro_rules match
    match_expr matches max_prec meta mod_cast monotonicity_by mut mutual namespace
    nat_lit no_error_if_unused% no_implicit_lambda% no_index nofun nomatch noncomputable
    nonempty_type nonrec norm_cast_add_elim notation offset( omit opaque open panic!
    partial partial_fixpoint postfix prefix println! private private_decl% protected
    public recall recall? recommended_spelling register_builtin_option
    register_error_explanation register_grind_attr register_label_attr
    register_linter_set register_option register_parser_alias register_simp_attr
    register_sym_dsimp register_sym_simp register_sym_simp_attr register_tactic_tag
    register_try?_tactic renaming repeat reportDbgIssue! reportEMatchIssue! reportIssue!
    reprove reset_grind_attrs% return rightact% run_cmd run_elab run_meta s!
    satisfies_binder_pred% scoped seal section sepBy( sepBy1( set_library_suggestions
    set_option show show_panel_widgets show_term show_term_elab simproc simproc_decl
    simproc_pattern% sorry struct_inst_default% structure suffices syntax tactic_alt
    tactic_extension tactic_name tactic_tag termination_by termination_by? test_extern
    then theorem throwError throwErrorAt throwNamedError throwNamedErrorAt time(
    timezone( trace[ trace_goal[ trailing_parser try type_of% unicode( unif_hint
    universe unless unlock_limits unop% unreachable! unsafe unseal until using using!
    value_of% variable wait_for_expected_type% wait_if_contains_mvar%
    wait_if_type_contains_mvar% wait_if_type_mvar% where while with with_annotate_term
    with_decl_name% with_weak_namespace without_expected_type zoned( Σ Σ' λ
'''.split())


def comment_end(src: str, i: int) -> int:
    """Return the end of the line comment or nested block comment that starts at i, as Lean
    reads it (`shared_comment_end`, heath.py's `comment_end` word for word)."""
    end = shared_comment_end(src, i)
    require(end is not None, 'unterminated Lean comment')
    return end


def string_literals(src: str, start: int, end: int) -> list[str]:
    """Return the contents of the strings that open in src[start:end], outside comments;
    start must stand outside every string and comment."""
    found = []
    i = start
    while i < end:
        if src.startswith(('--', '/-'), i):
            i = comment_end(src, i)
        elif src[i] == '"':
            j = i + 1
            while j < len(src) and src[j] != '"':
                j += 2 if src[j] == '\\' else 1
            found.append(src[i + 1:j])
            i = j + 1
        else:
            i += 1
    return found


def mask(src: str) -> tuple[str, list[tuple[int, int]]]:
    out = list(src)
    comments = []
    i = 0
    while i < len(src):
        start = i
        if src.startswith(('--', '/-'), i):
            i = comment_end(src, i)
            comments.append((start, i))
        elif src[i] == '"':
            i += 1
            while i < len(src):
                if src[i] == '\\':
                    i += 2
                elif src[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            else:
                raise Refusal('unterminated Lean string')
        else:
            i += 1
            continue
        for j in range(start, min(i, len(src))):
            if src[j] != '\n':
                out[j] = ' '
    return ''.join(out), comments


def assignment(clean: str, start: int, end: int) -> int | None:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{', '⟩': '⟨'}
    i = start
    while i < end:
        c = clean[i]
        if c in '([{⟨':
            stack.append(c)
        elif c in pairs:
            require(stack and stack.pop() == pairs[c], 'unbalanced declaration delimiters')
        elif clean.startswith(':=', i) and not stack:
            return i
        i += 1
    require(not stack, 'unclosed declaration delimiter')
    return None


def header_tokens(src: str, comments: list[tuple[int, int]]):
    """Yield the tokens of a Lean header as (text, start, end), before any masking.

    Whitespace and ordinary comments separate tokens; each comment is added to comments. A
    doc comment is one token, and so is a module name, read whole with its «...» components,
    so that nothing inside them is read as syntax. Any other character is a token by itself.
    At the end of the text the stream yields ('', len(src), len(src)) for ever.
    """
    i = 0
    while True:
        while i < len(src) and src[i] in ' \t\r\n':
            i += 1
        if i == len(src):
            yield '', i, i
            continue
        if src.startswith(('--', '/-'), i) and not src.startswith(('/--', '/-!'), i):
            end = comment_end(src, i)
            comments.append((i, end))
        elif src.startswith('/-', i):
            end = comment_end(src, i)
            yield src[i:end], i, end
        else:
            found = MODULE_NAME.match(src, i)
            end = found.end() if found else i + 1
            yield src[i:end], i, end
        i = end


def module_path(name: str) -> str | None:
    """Return the file a module name names, one folder per component, or None if a component
    could leave its folder."""
    parts = [part[1:-1] if part.startswith('«') else part for part in MODULE_PART.findall(name)]
    if any(part in ('.', '..') or '/' in part for part in parts):
        return None
    return '/'.join(parts) + '.lean'


def lean_source(path: str, raw: str) -> tuple[str, list[tuple[int, int]], list[tuple[str, int, int]]]:
    """Read a Lean file's header, then mask the file; return the masked text, its comments and
    its imports, each with its module's file and the span of its words to the end of its line.

    The header is an optional `module`, then any number of `[public] [meta] import M`, each
    ending its line, with ordinary comments between the words. As in Lean, an import is read
    only whole, so `public section` after the header ends it. An import naming anything but one
    module, and an `import` anywhere after the header unless within a whole «...» name, are
    refused: so is any other word before an import, `prelude`, `import all`, a doc comment
    among the imports or a block comment that opens on an import's line and closes on a later
    one. The header is blank in the masked text.
    """
    comments: list[tuple[int, int]] = []
    stream = header_tokens(raw, comments)
    tokens: list[tuple[str, int, int]] = []

    def token(k: int) -> tuple[str, int, int]:
        while len(tokens) <= k:
            tokens.append(next(stream))
        return tokens[k]

    k = 1 if token(0)[0] == 'module' else 0
    end = token(0)[2] if k else 0
    imports = []
    while True:
        j = k + (token(k)[0] == 'public')
        j += token(j)[0] == 'meta'
        if token(j)[0] != 'import':
            break
        name, _, end = token(j + 1)
        following = token(j + 2)
        newline = raw.find('\n', end)
        line_end = len(raw) if newline < 0 else newline + 1
        file = module_path(name) if MODULE_NAME.fullmatch(name) else None
        # A block comment opening on the import's line must close there, so that the
        # import's span ends outside it.
        require(file and name not in HEADER_WORDS
                and (not following[0] or '\n' in raw[end:following[1]])
                and not any(token(k)[1] <= a < line_end and raw.startswith('/-', a)
                            and '\n' in raw[a:b] for a, b in comments),
                f'{path}: unsupported import {raw[token(k)[1]:line_end].rstrip()!r}')
        imports.append((file, token(k)[1], line_end))
        k = j + 2
    rest, rest_comments = mask(raw[end:])
    clean = re.sub(r'[^\n]', ' ', raw[:end]) + rest
    # A whole «...» name is one identifier, so an `import` within it is no import.
    names = QUOTED_NAME.sub(lambda found: ' ' * len(found.group()), clean)
    later = IMPORT_WORD.search(names, end)
    if later:
        line_end = raw.find('\n', later.start())
        line = raw[raw.rfind('\n', 0, later.start()) + 1:len(raw) if line_end < 0 else line_end]
        raise Refusal(f'{path}: unsupported import {line!r}')
    comments = [c for c in comments if c[0] < end] + [(a + end, b + end) for a, b in rest_comments]
    return clean, comments, imports


@dataclass(frozen=True)
class Declaration:
    name: str
    path: str
    kind: str
    start: int
    keyword: int
    name_end: int
    end: int
    signature_end: int
    body: int
    namespace: str
    context: tuple[tuple[int, int], ...]
    opens: tuple[str, ...]


class Index:
    def __init__(self, evidence: Evidence):
        self.evidence = evidence
        self.decls: dict[str, Declaration] = {}
        self.clean: dict[str, str] = {}
        self.raw: dict[str, str] = {}
        self.imports: dict[str, list[tuple[str, int, int]]] = {}
        self.notation: list[tuple[str, int, int]] = []
        # A private declaration is seen only in its own file, as Lean reads it.
        self.private: set[str] = set()
        self.visible_cache: dict[str, set[str]] = {}
        for path in sorted((ROOT / 'Elements').rglob('*.lean')):
            self.add(relative(path))
        self.by_tail: dict[str, list[str]] = {}
        for name in self.decls:
            self.by_tail.setdefault(name.rsplit('.', 1)[-1], []).append(name)

    def add(self, path: str) -> None:
        raw = self.evidence.read(path)
        # Refused since the masking, which opened a comment with `/-` alone, ended `/--/` at
        # once where Lean's doc comment runs on to a later `-/`. The masking now reads it as
        # Lean does (`comment_end`, #206), and the refusal stands.
        require('/--/' not in raw, f'{path}: unsupported doc comment opening /--/')
        clean, comments, self.imports[path] = lean_source(path, raw)
        self.clean[path] = clean
        self.raw[path] = raw
        # Wherever one stands, local or scoped included. The bar is sought in the raw text, so
        # within the notation's strings; the `=>` in the masked text, so outside them. Each
        # string is a token, read without its spaces: it may be a name, or hold no character
        # of a name, as `‖` and `∠` do, and is refused otherwise.
        for found in SYNTAX_WORD.finditer(clean):
            require(not found.group(1), f'{path}: unsupported command {found.group()}')
            arrow = clean.find('=>', found.end())
            stop = len(raw) if arrow < 0 else arrow
            require('|' not in raw[found.start():stop],
                    f'{path}: unsupported {found.group()} with a bar')
            for atom in string_literals(raw, found.start(), stop):
                atom = atom.strip()
                # Lean reads a token whole, `/--+` too, where the masking opens a comment.
                require((LEAN_NAME.fullmatch(atom) or not NAME_CHARACTER.search(atom))
                        and '--' not in atom and '/-' not in atom,
                        f'{path}: unsupported {found.group()} token {atom!r}')
        commands = list(COMMAND.finditer(clean))
        namespace = ''
        frames: list[tuple[str, int, int]] = []
        contexts: list[tuple[int, int]] = []
        opens: list[str] = []
        for idx, match in enumerate(commands):
            kind = match.group(1)
            start = match.start()
            next_start = commands[idx + 1].start() if idx + 1 < len(commands) else len(raw)
            # A leading top-level comment belongs to the following command, not this one.
            stop = next_start
            for a, b in comments:
                if match.end() < a < next_start and raw[raw.rfind('\n', 0, a) + 1:a] == '':
                    if not clean[b:next_start].strip():
                        stop = min(stop, a)
            end = len(raw[:stop].rstrip())
            line_end = raw.find('\n', start)
            line_end = len(raw) if line_end < 0 else line_end
            if kind in ('namespace', 'section'):
                frames.append((namespace, len(contexts), len(opens)))
                if kind == 'namespace':
                    part = clean[match.end():line_end].strip()
                    namespace = namespace + '.' + part if namespace else part
                contexts.append((start, line_end))
                continue
            if kind == 'end':
                require(frames, f'{path}: unpaired namespace end')
                namespace, c, o = frames.pop()
                contexts, opens = contexts[:c], opens[:o]
                continue
            if kind in ('open', 'variable'):
                contexts.append((start, end))
                if kind == 'open':
                    opens.extend(TOKEN.findall(clean[match.end():end]))
                continue
            if kind.startswith(('notation', 'infix', 'prefix', 'postfix')):
                self.notation.append((path, start, end))
                continue
            if kind in ('example', 'attribute', 'set_option'):
                continue
            nm = re.match(r'\s+(' + NAME + r')', clean[match.end():end])
            if nm is None:
                require(kind == 'instance', f'{path}:{start}: unnamed {kind}')
                continue
            short = nm.group(1)
            name = short.removeprefix('_root_.') if short.startswith('_root_.') else namespace + '.' + short
            require(name not in self.decls, f'{path}: ambiguous declaration {name}')
            name_end = match.end() + nm.end()
            kw = match.start(1)
            doc_start = start
            for a, b in reversed(comments):
                if b <= start and raw[a:a + 3] == '/--' and not raw[b:start].strip():
                    doc_start = a
                    break
            if 'private' in clean[start:kw].split():
                self.private.add(name)
            assign = assignment(clean, name_end, end)
            sig_end = assign if assign is not None else end
            if assign is None and kind in ('def', 'abbrev'):
                eq = re.search(r'^\s+\|', clean[name_end:end], re.M)
                if eq:
                    sig_end = name_end + eq.start()
            self.decls[name] = Declaration(name, path, kind, doc_start, kw, name_end, end,
                                           len(raw[:sig_end].rstrip()),
                                           assign + 2 if assign is not None else end,
                                           namespace, tuple(contexts), tuple(opens))

    def visible(self, path: str, visiting: frozenset[str] = frozenset()) -> set[str]:
        if path in self.visible_cache:
            return self.visible_cache[path]
        require(path not in visiting, f'{path}: import cycle')
        result = {path}
        for imported, _, _ in self.imports[path]:
            if imported.startswith('Elements/'):
                require(imported in self.imports, f'{path}: missing import {imported}')
                result |= self.visible(imported, visiting | {path})
        self.visible_cache[path] = result
        return result

    def seen(self, name: str, consumer: Declaration) -> bool:
        """Whether `name` is a declaration the consumer's file can see: a private one is seen
        only in its own file (III.16's `sameSideOf_self` is Elements', not Circumferences')."""
        return name in self.decls and (name not in self.private
                                       or self.decls[name].path == consumer.path)

    def available_before(self, name: str, main: Declaration) -> bool:
        """Whether `name` is declared before `main`: in a file that `main`'s file imports, or
        above it in its own file. Anything else is a later declaration, never a premise."""
        d = self.get(name)
        return d.path in self.visible(main.path) and (d.path != main.path or d.keyword < main.keyword)

    def resolve(self, token: str, consumer: Declaration, *, required: bool = False,
                commentary: bool = False) -> str | None:
        # A dotted declaration opens its parent namespaces for its own type and body.
        # For example, fan.positions within Fitted.fan names Fitted.fan.positions.
        prefixes = consumer.name.split('.')[:-1]
        for n in range(len(prefixes), -1, -1):
            candidate = '.'.join(prefixes[:n] + [token])
            if self.seen(candidate, consumer):
                return candidate
        candidates = set()
        # An opened namespace is named from the root, from Elements, or from the consumer's
        # namespace or any enclosing it: `open Prop4 in` within Elements.BookI opens
        # Elements.BookI.Prop4.
        parts = consumer.namespace.split('.') if consumer.namespace else []
        scopes = {'', 'Elements.'} | {'.'.join(parts[:n]) + '.' for n in range(1, len(parts) + 1)}
        for opened in (*consumer.opens, *(['Elements', 'Elements.Tacit'] if commentary else [])):
            for prefix in sorted(scopes):
                candidate = prefix + opened + '.' + token
                if self.seen(candidate, consumer):
                    candidates.add(candidate)
        require(len(candidates) <= 1, f'{consumer.path}: ambiguous name {token}: {sorted(candidates)}')
        if candidates:
            return next(iter(candidates))
        if required:
            raise Refusal(f'{consumer.path}: unresolved name {token}')
        return None

    def get(self, name: str) -> Declaration:
        require(name in self.decls, f'unresolved declaration {name}')
        return self.decls[name]

    def quote(self, source: dict, field: str, name: str, *, full: bool = False,
              doc: bool = True) -> str:
        d = self.get(name)
        return self.evidence.excerpt(source, field, d.path, d.start if doc else d.keyword,
                                     d.end if full else d.signature_end)

    def context(self, source: dict, field: str, names: list[str]) -> dict:
        result = {}
        for name in sorted(set(names)):
            d = self.get(name)
            result[name] = [self.evidence.excerpt(source, field + '.' + name, d.path, a, b)
                            for a, b in d.context]
        return result

    def import_text(self, source: dict, field: str, path: str) -> str:
        spans = self.imports[path]
        if not spans:
            return ''
        return self.evidence.excerpt(source, field, path, spans[0][1], spans[-1][2])


REGISTRY = {
    'Words': 'Point Line Circle OnLine SameSide Between OnCircle InsideCircle Centre Collinear '
             'OppositeSides OutsideCircle LinesMeet LineMeetsCircle CirclesMeet',
    'Definitions': 'Triangle Parallel Equilateral Square IsAcute IsObtuse IsRightAngle Isosceles '
                   'RightAngledTriangle',
    'Phrases': 'AreParallel SameSideOf OppositeSidesOf OnRay InsideTriangle Parallelogram quadArea '
               'InOrder segments endOf OnFiniteLine OnOrInsideTriangle Corners triples Fitted '
               'Rectilineal Rectilineal.area Apart Apart.area',
    'DefinitionsII': 'Rectangle Contain rect sq',
    'DefinitionsIII': 'EqualCircles Touches TouchesInternally TouchesExternally CirclesTouch '
                      'Touching.Near TouchesInternallyAt TouchesExternallyAt CirclesTouchAt '
                      'WithinAngle MixedAngle MixedAngle.vertex MixedAngle.region '
                      'MixedAngle.WellFormed LocallyWithin NearVertex Surrounds NearVertexOpen '
                      'LocallyLess LocallyEqual MixedAngle.Exceeds MixedAngle.FallsShort CirclesCut '
                      'circumference angleAtCentre standing Arc Arc.Drawn OnSideOrLine OnArc '
                      'InSegment Arc.Less Arc.Semicircle Arc.Greater Arc.SameKind Arc.measure '
                      'Places Arc.Congruent Foot',
    'Magnitudes': 'Kind MagnitudeImpl Magnitude Length Angle Area len ang area rightAngle Magnitude.sum',
    # The restricted rule of superposition's meanings, which I.4's and I.8's records check: the
    # laws a derivation cites, as data, and what a law, and so a cited law, asserts.
    'Superposition/Syntax': 'Superposition.Letter Superposition.LineLetter Superposition.Law '
                            'Superposition.Cited Superposition.Cited.law',
    'Superposition/Semantics': 'Superposition.Val Superposition.Atom.Holds Superposition.Lit.Holds '
                               'Superposition.Metric.Holds Superposition.Law.Holds '
                               'Superposition.Cited.Holds',
    'Tacit/Superposition': 'primitives',
    # A rectilineal figure given by its outline (I.45, II.14): its contours, its region and the
    # area its divisions give.
    'Figures': 'Figures.sides Figures.Covers Figures.LoopBoundary Figures.SimpleLoop '
               'Figures.GoodRay Figures.RayCrosses Figures.crossingCount Figures.LoopInside '
               'Figures.LoopRegion Figures.CompatibleLoops Figures.Outline Figures.Outline.Boundary '
               'Figures.Outline.depth Figures.Outline.Inside Figures.Outline.Region Figures.Divides '
               'Figures.Outline.area',
}
# A group a run needs only when its book is audited, or when a bundle it supplies names one
# of its words; every group a run uses is checked whole. A commit before Book III's words, the
# rule of superposition's meanings or the outlines of figures is read with the groups it has.
REGISTRY_BOOK = {'DefinitionsIII': 'III'}
REGISTRY_BUNDLED = ('Superposition/Syntax', 'Superposition/Semantics', 'Tacit/Superposition',
                    'Figures')
# A group found in more than one file, each under Elements/Foundations/; any other is found in
# its own. #517 moves `primitives`, which the rule of superposition and Common Notion 4 for
# figures share, to a file of its own, so while the move lands it may stand in either; the
# move's contract names the new file alone.
REGISTRY_FILES = {'Tacit/Superposition': ('Tacit/Superposition', 'Superposition/Primitives')}


def registry_for(books: tuple[tuple[str, int], ...], bundled: set[str]) -> dict[str, str]:
    audited = {book for book, _ in books}
    return {file: words for file, words in REGISTRY.items()
            if (file not in REGISTRY_BOOK or REGISTRY_BOOK[file] in audited)
            and (file not in REGISTRY_BUNDLED or set(words.split()) & bundled)}


SYMBOLS = {'‖': 'len', '∠': 'ang', '△': 'area', '∟': 'rightAngle'}
# A parallelogram's area, `quadArea`, is measured by the diameter AC: the other diameter gives
# the same (`Parallelogram.quadArea_rotate`), a diameter bisects it (I.34), and it is the area
# of the parallelogram given by its outline, whose corners are a convex outline
# (`Parallelogram.convexOutline`, `Parallelogram.outline_area`).
PARALLELOGRAM_OUTLINE_BRIDGES = ['Elements.Parallelogram.convexOutline',
                                 'Elements.Parallelogram.outline_area']
AREA_BRIDGES = ['Elements.Parallelogram.cross', 'Elements.Parallelogram.quadArea_rotate',
                'Elements.BookI.Prop34', 'Elements.BookI.Prop34.bisect', *PARALLELOGRAM_OUTLINE_BRIDGES]
RECT_BRIDGES = ['Elements.Rectangle.congr', 'Elements.Rectangle.contained',
                'Elements.Rectangle.eq_rect', 'Elements.Square.eq_sq', 'Elements.Square.described']
FIGURE_BRIDGES = ['Elements.Fitted.triangle', 'Elements.Fitted.inside_pairwise',
                  'Elements.Rectilineal.toApart', 'Elements.Rectilineal.area_toApart',
                  'Elements.Fitted.fan']
# I.4's and I.8's records check the symbols' meanings, their renaming, soundness and the rule
# with named symbols, and the laws each cites, each law's meaning and its proof; I.8's, I.7's
# law with the bridge it is proved through, from SameSide to SameSideOf, too.
SUPERPOSITION_DEFINITIONS = ['Superposition.Val', 'Superposition.Atom.Holds',
                             'Superposition.Lit.Holds', 'Superposition.Metric.Holds', 'primitives',
                             'Superposition.Letter', 'Superposition.LineLetter', 'Superposition.Law',
                             'Superposition.Cited', 'Superposition.Cited.law',
                             'Superposition.Law.Holds', 'Superposition.Cited.Holds']
SUPERPOSITION_BRIDGES = ['Elements.Superposition.Atom.holds_map',
                         'Elements.Superposition.Lit.holds_map',
                         'Elements.Superposition.Metric.holds_map',
                         'Elements.Superposition.Derives.sound', 'Elements.Superposition.Rule.apply']
# The proofs of the laws each cites are the certificate's, read from its entry of facts.json
# (`Generator.cited_laws`), so that a law its Lean no longer cites leaves the row with it. The
# one bridge named here is no law's proof: holds_prop7, the proof facts.json gives for I.7's
# law, turns I.7's same side of a straight line into the same side of its two points through
# SameSideOf.of_line, which I.8's record checks too.
CITED_EXTRAS = {'I.4': [], 'I.8': ['Elements.SameSideOf.of_line']}
# I.45 and II.14 take a figure by its outline too (`Prop45.outline`, `Prop14.outline`): the
# outline's words, and Book Zero's bridges, that it has a division into triangles that lie
# apart, that every such division has one sum, the content theorem, and that this sum is the
# outline's area. I.45's record adds that the checked fan's figure is the one its corners
# bound (`Prop45.fan_boundary`).
OUTLINE_DEFINITIONS = REGISTRY['Figures'].split()
OUTLINE_BRIDGES = ['Elements.Figures.division_exists', 'Elements.Figures.Apart.area_eq_of_same_region',
                   'Elements.Figures.area_eq']
# What a record says its representations verdict rests on, which its row must supply as a
# bridge, a definition or one of the statements the row judges (`Generator.checked`). Every
# name a [representation] note gives in backticks is read from the record itself. These are
# the others: what the comment on I.4's and I.8's representations item says it checked, each
# law cited with its meaning and its proof, the proofs with CITED_EXTRAS read from facts.json
# (`Generator.record_checked`); what III.20's, III.21's and III.26's records say of the angle
# at the centre in words, not in backticks of a representation note; and, where the row's
# statements take a figure by its outline, the bridges I.45's and II.14's notes on the route
# and the passages give for it, with the region and the area of an outline they speak of.
RECORD_CHECKED = {
    'I.4': ('Elements.Superposition.Atom.Holds', 'Elements.Superposition.Lit.Holds',
            'Elements.Superposition.Metric.Holds', *SUPERPOSITION_BRIDGES,
            'Elements.Superposition.Cited.Holds', 'Elements.Superposition.Law.Holds',
            'Elements.Superposition.Cited.law'),
    'I.8': ('Elements.Superposition.Atom.Holds', 'Elements.Superposition.Lit.Holds',
            'Elements.Superposition.Metric.Holds', *SUPERPOSITION_BRIDGES,
            'Elements.Superposition.Cited.Holds', 'Elements.Superposition.Law.Holds',
            'Elements.Superposition.Cited.law'),
    # III.20's note: the angle at the centre "depends on neither the diameter, nor the centre"
    # (`angleAtCentre.diameter`), "nor the point naming the side" (`angleAtCentre.congr`).
    'III.20': ('Elements.BookIII.angleAtCentre.diameter', 'Elements.BookIII.angleAtCentre.congr'),
    # III.21's record has no representation note. Its route reads the angle at the centre as
    # ours: in the semicircle and the less segment it is "two right angles or more"
    # (`angleAtCentre`); where the centre F lies on A's side of BD, as in Euclid's figure, it is
    # the angle BFD of which BAD and BED "are halves" (`angleAtCentre.within`); "III.20 makes it
    # up from angles at the centre itself", the passage at "let BF, FD be joined" says, so that
    # "III.20 doubles BAD and BED in every segment" (`angleAtCentre.diameter`); the passage at
    # "Now, since the angle BFD is at the centre" gives its three sizes, the angle BFD, two right
    # angles and more (`angleAtCentre.size`); and, the passage at "Let ABCD be a circle" says,
    # it "reads only the side" (`angleAtCentre.congr`).
    'III.21': ('Elements.angleAtCentre', 'Elements.BookIII.angleAtCentre.within',
               'Elements.BookIII.angleAtCentre.congr', 'Elements.BookIII.angleAtCentre.diameter',
               'Elements.BookIII.angleAtCentre.size'),
    # III.26's note reads "Equal circumferences" as "equal in measure", and within the proof "the
    # angles at the centres standing on BKC and ELF are of any size (`angleAtCentre`)": our
    # measure of a circumference is its angle at the centre (`Prop20.circumference`).
    'III.26': ('Elements.BookIII.Prop20.circumference',),
}
# What a record's [representation] note names in backticks as context, a theorem proved after
# the proposition, which its row is not asked to supply: "a theorem proved after III.27 is not a
# bridge for it" (the coordinator's ruling of 29 October 2026, #674). III.27's note says its
# companion is stated in "the form in which III.29's companion `Prop29.of_measure` cites it", and
# that the two readings agree by `Arc.congruent_iff`, "proved after III.29, from it"; III.29's
# note names `Arc.congruent_iff` where "the two readings agree" too, and `Arc.measure_eq_iff`,
# "after III.29", which MEASURE_BRIDGES supplies, so it is not here. `Generator.checked` refuses
# an entry the note does not name in backticks, or one declared before the main theorem, as a
# bridge's placement is read (`Index.available_before`).
RECORD_LATER = {
    'III.27': ('Elements.BookIII.Prop29.of_measure', 'Elements.BookIII.Arc.congruent_iff'),
    'III.29': ('Elements.BookIII.Arc.congruent_iff',),
}
OUTLINE_CHECKED = {
    'I.45': ('Elements.Figures.Outline', 'Elements.Figures.Outline.Region',
             'Elements.Figures.Outline.area', *OUTLINE_BRIDGES, 'Elements.BookI.Prop45.fan_boundary',
             'Elements.BookI.Prop45.outline'),
    'II.14': ('Elements.Figures.Outline', 'Elements.Figures.Outline.Region',
              'Elements.Figures.Outline.area', *OUTLINE_BRIDGES, 'Elements.BookII.Prop14.outline',
              'Elements.BookII.Prop14.outline_side'),
}
# Book III. A segment is its circle, the ends of its base and a point naming its side (`Arc`);
# the angle in it is the same at every point of its arc [III. 21].
SEGMENT_DEFINITIONS = ['Arc', 'Arc.Drawn', 'OnArc', 'InSegment', 'OnSideOrLine']
SEGMENT_BRIDGES = ['Elements.BookIII.Prop21']
# A circumference is measured by the angle standing on it, taken twice, with no radius.
MEASURE_DEFINITIONS = ['circumference', 'standing', 'Arc', 'Arc.Drawn', 'Arc.measure', 'Arc.Less',
                       'Arc.Semicircle', 'Arc.Greater', 'Arc.SameKind', 'EqualCircles']
MEASURE_BRIDGES = ['Elements.BookIII.Circumference.eq', 'Elements.BookIII.Circumference.standing',
                   'Elements.BookIII.Circumference.centre', 'Elements.BookIII.Arc.measure_eq_iff']
# Equal segments and circumferences are read as ones that coincide (Common Notion 4). III.27's
# and III.29's main statements read them so too, but `Arc.congruent_iff`, which makes them, in
# equal circles, the circumferences equal in measure, is proved after both (`Arcs.lean` imports
# Prop29), so their rows get the words without it (RECORD_LATER).
CONGRUENCE_DEFINITIONS = ['Arc.Congruent', 'Places', 'OnArc', 'InSegment', 'OnSideOrLine']
CONGRUENCE_BRIDGES = ['Elements.BookIII.Arc.congruent_iff']
# Congruent circumferences "already lie in equal circles (`Prop24.image`,
# `Prop24.equalCircles`)", III.27's note says of its redundant hypothesis, and III.29's that
# "the congruence already gives the equal straight lines (`Prop24.image`), and the equal circles
# with them (`Prop24.equalCircles`)".
CONGRUENT_CIRCLE_BRIDGES = ['Elements.BookIII.Prop24.image', 'Elements.BookIII.Prop24.equalCircles']
# `Prop27`'s proof makes its circumferences "equal in measure, twice the angle standing on them,
# by III.24's companion `Prop24.equalMeasure`", III.27's note says.
CONGRUENT_MEASURE_BRIDGES = ['Elements.BookIII.Prop24.equalMeasure']
# III.29's proof takes "its equal angles from III.27, which `Prop27` states with the same
# congruence", and its companion "repeats the argument through III.27's companion
# `Prop27.of_measure`", as III.29's note says.
EQUAL_ANGLE_BRIDGES = ['Elements.BookIII.Prop27', 'Elements.BookIII.Prop27.of_measure']
# The kind of a segment, decided by where the centre lies, against two right angles.
KIND_BRIDGES = ['Elements.BookIII.Circumference.semicircle',
                'Elements.BookIII.Circumference.lt_semicircle',
                'Elements.BookIII.Circumference.gt_semicircle']
# An angle with a circumference is the region it opens near its vertex (III.16, III.18, III.31).
MIXED_DEFINITIONS = ['MixedAngle', 'MixedAngle.vertex', 'MixedAngle.region', 'MixedAngle.WellFormed',
                     'MixedAngle.Exceeds', 'MixedAngle.FallsShort', 'WithinAngle', 'LocallyWithin',
                     'LocallyLess', 'LocallyEqual', 'NearVertexOpen', 'Surrounds']
MIXED_BRIDGES = ['Elements.WithinAngle.locallyLess_iff', 'Elements.WithinAngle.locallyEqual_iff',
                 'Elements.MixedAngle.wellFormed_ofSegment']
# III.18's angle of contact, named by any straight line from the point of contact into the
# circle, is near that point the one the diameter names, as its record's note says.
CONTACT_BRIDGES = ['Elements.BookIII.Prop18.branch', 'Elements.BookIII.Prop18.contact_locallyEqual']
# Circles touching, read of the whole circles, are the same as touching read at the point of
# contact (Definition III.3, as Heath prefers it), for any two circles, as III.13's record says.
TOUCHING_BRIDGES = ['Elements.BookIII.Prop13.touchesInternally_iff',
                    'Elements.BookIII.Prop13.touchesExternally_iff',
                    'Elements.BookIII.Prop13.circlesTouch_iff']
# The angle at the centre standing on a circumference, of any size, our reading after Heath's
# notes (`angleAtCentre`), which III.20's, III.21's and III.26's records name. For III.20 and
# III.21 it is the angle BEC, E the centre, where E lies across the base from that
# circumference, as Euclid's angles at the centre are (`angleAtCentre.within`); it is the angles
# BEF and FEC together, for any diameter AEF with A and F on opposite sides of the base and F
# on the circumference's side, wherever the centre lies, on the base or beyond it too, for a
# semicircle or a less segment (`angleAtCentre.diameter`); and it reads only the side of the
# base that the point naming the circumference lies on (`angleAtCentre.congr`). III.20's representation note names the first
# and says the other two in words. III.21's record has no representation note: its route reads
# Euclid's argument in a segment of any size, the semicircle and the less segment among them,
# and its passages name `angleAtCentre.congr` and the three sizes of the angle at the centre,
# less than, equal to and greater than two right angles as the centre lies across the base, on
# it or beyond it (`angleAtCentre.size`). Our measure of a circumference is its angle at
# the centre (`Prop20.circumference`), which III.20's note names; it ties III.26's reading of
# equal circumferences as equal in measure to the angles at the centres its note names, and,
# with `Circumference.centre`, makes the angle at the centre the angle BGC where G lies across
# BC from K.
CENTRE_DEFINITIONS = ['angleAtCentre']
CENTRE_BRIDGES = ['Elements.BookIII.angleAtCentre.within', 'Elements.BookIII.angleAtCentre.congr',
                  'Elements.BookIII.angleAtCentre.diameter']
CENTRE_MEASURE_BRIDGES = ['Elements.BookIII.Prop20.circumference']
CENTRE_SIZE_BRIDGES = ['Elements.BookIII.angleAtCentre.size']
# A straight line's distance from the centre is the perpendicular to its foot (Definition III.4).
FOOT_BRIDGES = ['Elements.Foot.exists', 'Elements.Foot.unique']
RECTANGLE_BRIDGES = ['Elements.Rectangle.congr', 'Elements.Rectangle.contained',
                     'Elements.Rectangle.eq_rect']
SQUARE_BRIDGES = ['Elements.Square.eq_sq', 'Elements.Square.described']


def bundle(book: str, n: int, outline: bool = False,
           cited: list[str] = ()) -> tuple[list[str], list[str]]:
    """The definitions and bridges that connect the objects a record's representation item
    judges with Euclid's; `outline` when the statements take a figure by its outline; `cited`,
    for I.4 and I.8, the proofs of the laws their derivations cite (`Generator.cited_laws`).
    `Generator.bundle` supplies none where the record marks the item `n/a`."""
    definitions, bridges = [], []
    if (book, n) in [('I', 4), ('I', 8)]:
        definitions += SUPERPOSITION_DEFINITIONS
        bridges += SUPERPOSITION_BRIDGES + list(cited)
    if book == 'I' and (34 <= n <= 38 or 41 <= n <= 48):
        definitions += ['Parallelogram', 'quadArea']
        bridges += AREA_BRIDGES
        if n >= 46:
            definitions += ['Square']
            bridges += ['Elements.BookI.Prop46.square_eq']
    if book == 'II':
        definitions += ['Rectangle', 'Contain', 'rect', 'sq', 'Parallelogram', 'quadArea', 'Square']
        bridges += RECT_BRIDGES
    if (book, n) in [('I', 45), ('II', 14)]:
        definitions += ['Apart', 'Fitted', 'Rectilineal']
        bridges += FIGURE_BRIDGES
        if outline:
            definitions += OUTLINE_DEFINITIONS
            bridges += OUTLINE_BRIDGES + (['Elements.BookI.Prop45.fan_boundary'] if n == 45 else [])
    if (book, n) == ('II', 1):
        definitions += ['InOrder', 'segments', 'endOf', 'Magnitude.sum']
        bridges += ['Elements.InOrder.between_end', 'Elements.rect_self_left',
                    'Elements.rect_self_right', 'Elements.sq_self']
    if book == 'III':
        if n == 13:
            definitions += ['TouchesInternally', 'TouchesExternally', 'CirclesTouch',
                            'TouchesInternallyAt', 'TouchesExternallyAt', 'CirclesTouchAt']
            bridges += TOUCHING_BRIDGES
        if n == 14:
            definitions += ['Foot']
            bridges += FOOT_BRIDGES
        if n in (16, 18, 31):
            definitions += MIXED_DEFINITIONS
            bridges += MIXED_BRIDGES
        if n == 18:
            bridges += CONTACT_BRIDGES
        if n in (23, 24, 25, 30, 33, 34):
            definitions += SEGMENT_DEFINITIONS
            bridges += SEGMENT_BRIDGES
        if n == 34:
            bridges += ['Elements.Tacit.exists_centre']
        if n in (24, 25, 26, 27, 28, 29, 30):
            definitions += MEASURE_DEFINITIONS
            bridges += MEASURE_BRIDGES
        if n in (24, 26, 27, 28, 29, 30):
            definitions += CONGRUENCE_DEFINITIONS
        if n in (24, 26, 28, 30):
            bridges += CONGRUENCE_BRIDGES
        if n in (27, 29):
            bridges += CONGRUENT_CIRCLE_BRIDGES
        if n == 27:
            bridges += CONGRUENT_MEASURE_BRIDGES
        if n == 29:
            bridges += EQUAL_ANGLE_BRIDGES
        if n == 25:
            bridges += KIND_BRIDGES
        if n == 30:
            bridges += ['Elements.BookIII.Circumference.add']
        if n in (20, 21, 26):
            definitions += CENTRE_DEFINITIONS
        if n in (20, 21):
            bridges += CENTRE_BRIDGES
        if n in (20, 26):
            bridges += CENTRE_MEASURE_BRIDGES
        if n == 21:
            bridges += CENTRE_SIZE_BRIDGES
        if 35 <= n <= 37:
            definitions += ['Rectangle', 'Contain', 'rect', 'Parallelogram', 'quadArea']
            bridges += RECTANGLE_BRIDGES
            definitions += ['sq', 'Square']
            bridges += SQUARE_BRIDGES
    return list(dict.fromkeys(definitions)), list(dict.fromkeys(bridges))


def glossary(index: Index, source: dict, code: list[str], extra: list[str] = (),
             groups: dict[str, str] | None = None) -> dict:
    groups = REGISTRY if groups is None else groups
    registry = {name: 'Elements.' + name for words in groups.values() for name in words.split()}
    for file, words in groups.items():
        paths = [f'Elements/Foundations/{f}.lean' for f in REGISTRY_FILES.get(file, (file,))]
        for name in words.split():
            d = index.get(registry[name])
            require(d.path in paths, f'glossary registry moved: {name}')
    selected = set(extra)
    pending = '\n'.join(code)
    while True:
        clean = mask(pending)[0]
        tokens = set(TOKEN.findall(clean))
        found = {n for n in registry if any(t == n or t.endswith('.' + n) for t in tokens)}
        found |= {name for symbol, name in SYMBOLS.items() if symbol in clean}
        found |= {n + '.area' for n in ('Apart', 'Rectilineal') if n in selected | found}
        added = found - selected
        # Explicit selections must take part in the first dependency expansion too.
        if not added and not pending:
            break
        selected |= found
        text = '\n'.join(index.evidence.read(index.get(registry[n]).path)[index.get(registry[n]).keyword:
                          index.get(registry[n]).end] for n in sorted(selected))
        if text == pending:
            break
        pending = text
    definitions = {n: index.quote(source, 'definitions.' + n, registry[n], full=True) for n in sorted(selected)}
    notation = {}
    for path, a, b in index.notation:
        raw = index.evidence.read(path)[a:b]
        if any(n in selected for n in SYMBOLS.values() if n in TOKEN.findall(mask(raw)[0])):
            notation[f'{path}:{index.evidence.read(path).count(chr(10), 0, a) + 1}'] = index.evidence.excerpt(
                source, 'notation', path, a, b)
    return {'definitions': definitions, 'notation': notation,
            'definition_context': index.context(source, 'definition_context', [registry[n] for n in selected])}


class Calls:
    """Reconcile source calls with certificate dependency walks, without reading comments.

    Field calls collect every Elements declaration T.f whose type name T occurs in the
    unit or in a collected signature, repeating to closure. Namespace prefixes do not
    restrict these conservative candidates, and no receiver type is guessed. Constructors
    and named projections of a structure or a class are quoted through their enclosing
    declaration, which contains their exact signatures and docstrings. An inductive's
    constructors are each named after a `|` outside every bracket in the declaration, on a
    line that opens `  |`, several to a line as `| a | b | c`; there they are declared, not
    called. An inductive
    is read only in the plain forms `constructors` names, and refused otherwise. The
    glossary's supplied definitions also expose their underlying types, including
    AreParallel within Parallelogram.

    The fixed core/projection allowlist is: 1, 2, symm, trans, refl, mp, mpr, elim, left,
    right, ne, imp, inl, inr, resolve_left, resolve_right, map, Pairwise, mem_append,
    mem_cons, mem_cons_of_mem, mem_cons_self, mem_singleton, mem_singleton_self, not_mem_nil,
    mem_nil_iff, forall_mem_cons, cons_ne_nil, append_ne_nil_of_right_ne_nil, append_assoc,
    append_nil, nil_append, cons_append, pairwise_append, pairwise_singleton, byContradiction,
    epsilon_spec, and choose and choose_spec, which III.26's helpers take of an existence.
    These names exempt only fields with no project candidate; symm, for example, still
    collects every eligible geometric signature. Book III, the rule of superposition's
    soundness and Book Zero's area of an outline use some more of Lean's own names, each
    recognised whole and never by its last word (CORE_NAMES): And.intro, Iff.rfl,
    List.mem_map, List.map_congr_left, List.Pairwise.sublist, the Classical.epsilon and
    True.intro of III.26's helpers, and the List.nodup_cons of the area of a convex outline
    (Elements/Figure/Divisions.lean), written so, with a first word that names no declaration
    of the project; and the constructor of a structure or class the index holds, X.mk, with
    the equation Lean generates for it, X.mk.injEq, where X names that structure or class. So Missing.mk, Missing.rfl and a def's d.mk stay unresolved. Any
    remaining field is unresolved.
    """

    CORE_FIELDS = frozenset({
        '1', '2', 'symm', 'trans', 'refl', 'mp', 'mpr', 'elim', 'left', 'right', 'ne', 'imp',
        'inl', 'inr', 'resolve_left', 'resolve_right', 'map', 'Pairwise', 'mem_append',
        'mem_cons', 'mem_cons_of_mem', 'mem_cons_self', 'mem_singleton', 'mem_singleton_self',
        'not_mem_nil', 'mem_nil_iff', 'forall_mem_cons', 'cons_ne_nil',
        'append_ne_nil_of_right_ne_nil', 'append_assoc', 'append_nil', 'nil_append',
        'cons_append', 'pairwise_append', 'pairwise_singleton', 'byContradiction', 'epsilon_spec',
        'choose', 'choose_spec',
    })
    # Lean's own names, each exempt only when written whole, from a first word that names no
    # declaration of the project.
    CORE_NAMES = frozenset({'And.intro', 'Iff.rfl', 'List.mem_map', 'List.map_congr_left',
                            'List.Pairwise.sublist', 'Classical.epsilon', 'True.intro',
                            'List.nodup_cons'})
    REFERENCE = re.compile(r'(?:' + IDENT + r'|(?<=\.)[0-9]+)(?:\.(?:' + IDENT + r'|[0-9]+))*')
    CONSTRUCTOR_LINE = re.compile(r'^  \|[^\n]*', re.M)
    CONSTRUCTOR = re.compile(r'\|\s*(' + IDENT + ')')
    CLOSERS = {')': '(', ']': '[', '}': '{', '⟩': '⟨', '⦄': '⦃', '⟧': '⟦', '›': '‹'}
    # The plain forms, the only ones `constructors` reads from an inductive's name to the end
    # of its constructors: whitespace and name characters; a dot after a name character, a
    # bracket or a space, and before a name character; the brackets ( ) [ ] { } ⦃ ⦄ ⟨ ⟩; the
    # symbols : , → ∀ ∈ × + |; and no keyword but those of PLAIN_WORDS. A match is a word, to
    # be read against KEYWORD_TOKENS, or a dot or a character outside the plain forms.
    PLAIN_WORDS = frozenset({'Type', 'Prop', 'Sort', 'where', '_'})
    UNPLAIN = re.compile('(?P<word>' + LEAN_NAME.pattern + ')'
                         '|(?P<after>(?<![' + WHITESPACE + NAME_REST
                         + '()\\[\\]{}⦃⦄⟨⟩])\\.)|(?P<before>\\.(?![' + NAME_REST + ']))'
                         '|[^' + WHITESPACE + NAME_REST + '.()\\[\\]{}⦃⦄⟨⟩:,→∀∈×+|]')
    # The longest keyword token at a place, as Lean's token table reads it.
    KEYWORD = re.compile('|'.join(re.escape(token) for token in
                                  sorted(KEYWORD_TOKENS, key=lambda token: (-len(token), token))))
    # Words after which a `|` may begin an alternative or a pattern, as in
    # `| mk : Q <| match 0 with | Known.bar n => n | _ => 0`: of `fun`, `match` or
    # `match_expr`, of a `let`, `have`, `haveI`, `letI`, `let_fun`, `let_delayed` or `let_tmp`
    # by equations or of `let_expr`, of `matches`, of a tactic, of `do`, or of a computed field
    # after `with`. The plain forms hold none of them; a bar after one is refused first, with
    # that reason.
    ALTERNATIVES = re.compile(KEYWORD_LEFT
                              + r'(?:fun|match|match_expr|matches|let|let_expr|have|by'
                              + r'|do|with|haveI|letI|let_fun|let_delayed|let_tmp)'
                              + KEYWORD_RIGHT + '|λ')
    # A line that is blank, opens `  |` or opens with three spaces continues the constructors;
    # a line opening with a bar after fewer spaces is refused, not taken as their end.
    CONSTRUCTORS_END = re.compile(r'(?! *$|  \||   )', re.M)
    # A declaration's keyword, or `recall`, begins a command wherever it stands on its line,
    # and ends the constructors.
    COMMAND_WORD = re.compile(KEYWORD_LEFT
                              + r'(?:def|theorem|abbrev|instance|example|opaque|axiom'
                              + r'|structure|class|inductive|deriving|mutual|recall)'
                              + KEYWORD_RIGHT)
    # Three forms would make the masked text, or the words in it, other than Lean reads them.
    # A string, a char literal or a «...» name, whose brackets and bars the masking may misread,
    # and a `»`, which may end a «...» name Lean opened before the inductive.
    LITERAL = re.compile(r"[\"«»]|(?<![\w'₀-₉!?])'")
    # A number glued to a word or a quote, as in `0x5matches` or `0'a'`, where Lean ends the
    # number, so that a keyword after it would go unseen and a quote would open a char literal;
    # and a quote after a bare `!` or `?`, which opens one, as in `!'a'matches`.
    GLUED = re.compile(r"(?<![\w'₀-₉!?])(?:[0-9]+(?:[^\W\d]|['!?])|[!?]+')")
    # A dash or a slash after which the masking opens a comment, after anything but whitespace
    # or a name character: Lean may read it within a token, as in `\/-`, `//-` or a notation's
    # `+--`, and open no comment there. After whitespace too Lean reads a notation's `/--+`
    # whole; the index refuses every notation token holding `--` or `/-`.
    OPENER = re.compile('--|/-')
    # Two forms the plain forms leave out are refused first, with a reason of their own: a
    # word character Lean reads in no name, such as `²` or `ж` (but `λ`, which ALTERNATIVES
    # reads), a subscript that begins a word, as after `→ₑ`, and `#`, which begins Lean's
    # commands, each read whole, as `#where` is in `#wheredef`; and a dot glued to a symbol
    # before a word, as in `..matches` or `⊗.matches`, which the patterns take for a field.
    FOREIGN = re.compile('[^\\W' + NAME_REST + 'λ]|(?<![\\w\'!?])[' + SUBSCRIPTS + ']|#')
    DOT = re.compile('(?<=[^\\s\\w' + NAME_REST + '()\\[\\]{}⟨⟩⦃⦄⟦⟧‹›])\\.(?=\\w)')

    def __init__(self, index: Index, facts: dict):
        self.index = index
        self.facts = facts
        self.by_name = {'Elements.' + p['name']: p for p in facts.values()}
        self.cache: dict[tuple[str, tuple[str, ...]], tuple[list[dict], set[str]]] = {}
        self.unresolved: dict[str, set[str]] = {}
        self.types = {n for n, d in index.decls.items()
                      if d.kind in ('def', 'abbrev', 'opaque', 'axiom', 'structure', 'class',
                                    'inductive')}
        self.members: dict[str, set[str]] = {}
        for name, d in index.decls.items():
            if d.kind == 'inductive':
                found = [m.group(1) for m in self.constructors(index.clean[d.path], d)]
            elif d.kind in ('structure', 'class'):
                found = re.findall(r'^  (' + IDENT + r')(?![' + NAME_REST + '])',
                                   index.clean[d.path][d.name_end:d.end], re.M)
            else:
                continue
            for member in found:
                self.members.setdefault(member, set()).add(name)

    def constructors(self, clean: str, d: Declaration) -> list[re.Match]:
        """Return each constructor name of inductive d: the name after a `|` outside every
        bracket in the declaration, on a line that opens `  |`.

        The reader accepts only the plain forms main's inductives are written in, and refuses
        everything else. From the inductive's name to the end of its constructors, the masked
        text may hold only whitespace and name characters; a dot after a name character, a
        bracket or a space, and before a name character; the brackets ( ) [ ] { } ⦃ ⦄ ⟨ ⟩;
        the symbols : , → ∀ ∈ × + |; and no keyword Lean 4.35 reads (KEYWORD_TOKENS) but
        `Type`, `Prop`, `Sort`, `where` and `_`. An alternative or a pattern after a bar needs
        `=>` or a keyword, so in these forms each bar outside every bracket separates
        constructors or stands beside another, as in `||`, which separates none; any other
        bar is refused, as are constructors at four spaces or on the inductive's own line.

        So that the masked text, and the words in it, are those Lean reads, the
        declaration's raw text may hold no string, char literal, «...» name or `»`
        (LITERAL), no number glued to a word or a quote (GLUED), and no comment opening
        after anything but whitespace or a name character, where Lean may read the dash or
        slash within a token (OPENER); a comment in it may hold no `{`, and a line comment
        no `-/`, at which Lean, put within a comment, a «...» name or an interpolated string
        by something earlier such as `'"'`, would leave it; and the index refuses, in any
        file it reads, a doc comment opening `/--/`, and a notation token holding `--` or
        `/-`, which Lean reads whole where the masking opens a comment. Some forms outside
        the plain forms are refused first, with a reason of their own: those FOREIGN and
        DOT name, anywhere in the declaration, and a bar after a word ALTERNATIVES names.

        The constructors end before the first line outside every bracket that is not blank
        and opens neither `  |` nor three spaces, where a deriving clause or a command
        begins, and before a declaration's keyword or `recall` outside every bracket,
        wherever it stands on its line, as in `| mk def f`; what follows is read for uses.
        Brackets are counted from the name across lines, and an unbalanced one is refused.
        The index refuses a notation whose words before `=>` hold a bar, or whose token joins
        a name character to another, and every macro, elaborator and binder-predicate
        command; `scripts/check_fidelity.py`, not this generator, refuses in `Elements/` the
        attributes that make a declaration an elaborator or a parser, such as
        `@[term_elab k]`."""
        require(not self.LITERAL.search(self.index.raw[d.path], d.name_end, d.end),
                f'{d.path}: unsupported string, char literal or quoted name in {d.name}')
        require(not self.GLUED.search(clean, d.name_end, d.end),
                f'{d.path}: unsupported number or literal glued to a word in {d.name}')
        foreign = self.FOREIGN.search(clean, d.name_end, d.end)
        if foreign:
            raise Refusal(f'{d.path}: unsupported character {foreign.group()!r} in {d.name}')
        raw = self.index.raw[d.path]
        for found in self.OPENER.finditer(raw, d.name_end, d.end):
            before = raw[found.start() - 1]
            require(clean[found.start() - 1] != before or before in WHITESPACE
                    or NAME_CHARACTER.match(before),
                    f'{d.path}: unsupported comment glued to {before!r} in {d.name}')
        # Where the masking misread something before the inductive, as it reads '"', Lean may be
        # within a comment, a «...» name or an interpolated string at its keyword, and leave it
        # at `-/`, `»` or `{`. LITERAL refuses `»` and `"`; a comment here may hold no `{`, and a
        # line comment no `-/`, so Lean leaves none of them where the masking reads no code.
        i = d.name_end
        while i < d.end:
            if raw.startswith(('--', '/-'), i):
                end = comment_end(raw, i)
                require('{' not in raw[i:end] and not (raw[i] == '-' and '-/' in raw[i:end]),
                        f'{d.path}: unsupported {{ or -/ in a comment in {d.name}')
                i = end
            else:
                i += 1
        require(not self.DOT.search(clean, d.name_end, d.end),
                f'{d.path}: unsupported dot glued to a symbol in {d.name}')
        lines = {line.start(): line.end()
                 for line in self.CONSTRUCTOR_LINE.finditer(clean, d.name_end, d.end)}
        words = {found.start(): found.group()
                 for found in self.ALTERNATIVES.finditer(clean, d.name_end, d.end)}
        commands = {found.start() for found in self.COMMAND_WORD.finditer(clean, d.name_end, d.end)}
        found, stack, line_end, word, stop = [], [], -1, None, d.end
        for i in range(d.name_end, d.end):
            if not stack and clean[i - 1] == '\n' and self.CONSTRUCTORS_END.match(clean, i):
                require(not re.match(r' *\|', clean[i:]),
                        f'{d.path}: unsupported bar in an inductive, {d.name}')
                stop = i
                break
            line_end = lines.get(i, line_end)
            c = clean[i]
            if c in '([{⟨⦃⟦‹':
                stack.append(c)
            elif c in self.CLOSERS:
                require(stack and stack.pop() == self.CLOSERS[c],
                        f'{d.path}: unbalanced brackets in {d.name}')
            elif stack:
                continue
            elif i in commands:
                stop = i
                break
            elif i in words:
                word = word or words[i]
            elif c == '|' and clean[i - 1] not in '|<' and clean[i + 1:i + 2] not in ('|', '>'):
                # Off a constructor line, line_end is behind i and nothing matches.
                match = self.CONSTRUCTOR.match(clean, i, line_end)
                require(word is None, f'{d.path}: unsupported bar after {word!r} in {d.name}')
                require(match, f'{d.path}: unsupported bar in an inductive, {d.name}')
                found.append(match)
        require(not stack, f'{d.path}: unbalanced brackets in {d.name}')
        for unplain in self.UNPLAIN.finditer(clean, d.name_end, stop):
            if unplain.lastgroup == 'word':
                keyword = self.KEYWORD.match(clean, unplain.start(), stop)
                if (not keyword or keyword.end() < unplain.end()
                        or keyword.group() in self.PLAIN_WORDS):
                    continue
                what = f'the keyword {keyword.group()!r}'
            elif unplain.lastgroup == 'after':
                what = f'a dot after {clean[unplain.start() - 1]!r}'
            elif unplain.lastgroup == 'before':
                what = f'a dot before {clean[unplain.end():unplain.end() + 1]!r}'
            else:
                what = f'the character {unplain.group()!r}'
            raise Refusal(f'{d.path}: {d.name} holds {what}, outside the plain forms an '
                          'inductive may hold')
        return found

    def type_names(self, text: str, consumer: Declaration) -> set[str]:
        found = set()
        for token in TOKEN.findall(text):
            parts = token.split('.')
            for count in range(1, len(parts) + 1):
                name = self.index.resolve('.'.join(parts[:count]), consumer)
                if name in self.types:
                    found.add(name.rsplit('.', 1)[-1])
        return found

    def core(self, parts: list[str], k: int, target: str | None, consumed: int,
             after_expression: bool) -> bool:
        """Whether the k-th word of a reference is one of Lean's own: a word of CORE_FIELDS; the
        last word of a name of CORE_NAMES written whole, from a first word that names no
        declaration of the project; or `mk`, and `mk.injEq`, straight after the name of a
        structure or class the index holds."""
        if parts[k] in self.CORE_FIELDS:
            return True
        if target is None:
            return not after_expression and '.'.join(parts[:k + 1]) in self.CORE_NAMES
        indexed = self.index.decls[target].kind in ('structure', 'class')
        return indexed and (parts[consumed:k + 1] == ['mk'] or parts[consumed:k + 1] == ['mk', 'injEq'])

    def direct(self, name: str, signatures: tuple[str, ...] = ()) -> list[dict]:
        key = (name, signatures)
        if key in self.cache:
            calls, unresolved = self.cache[key]
            self.unresolved[name] = unresolved
            return calls
        d = self.index.get(name)
        clean = self.index.clean[d.path]
        visible = self.index.visible(d.path)
        calls = []
        fields = []

        def record(target: str, match: re.Match, resolution: str) -> None:
            calls.append({'name': target, 'token': match.group(), 'path': d.path,
                          'line': clean.count('\n', 0, match.start()) + 1,
                          'start': match.start(), 'end': match.end(),
                          'position': 'proof' if match.start() >= d.body else 'type',
                          'resolution': resolution})

        declared = ({found.start(1) for found in self.constructors(clean, d)}
                    if d.kind == 'inductive' else set())
        for match in self.REFERENCE.finditer(clean, d.name_end, d.end):
            if match.start() in declared:
                continue
            token = match.group()
            parts = token.split('.')
            after_expression = clean[match.start() - 1:match.start()] == '.'
            target, consumed = None, 0
            if not after_expression:
                for count in range(len(parts), 0, -1):
                    target = self.index.resolve('.'.join(parts[:count]), d)
                    if target:
                        consumed = count
                        break
            if target:
                called = self.index.get(target)
                require(called.path in visible, f'{d.path}: {target} is not imported')
                require(called.path != d.path or called.keyword <= d.keyword,
                        f'{d.path}: forward declaration use {target} in {name}')
                record(target, match, 'namespace')
            elif re.search(r'(?:^|\.)Prop\d+', token):
                raise Refusal(f'{d.path}: unresolved proposition call {token} in {name}')
            start = consumed if target else (0 if after_expression else 1)
            fields.extend((parts[k], match, self.core(parts, k, target, consumed, after_expression))
                          for k in range(start, len(parts)))

        type_names = self.type_names(clean[d.name_end:d.end], d)
        collected = set(signatures) | {name} | {c['name'] for c in calls}
        inspected = set()
        candidates: dict[str, set[str]] = {}
        while True:
            previous_types = set(type_names)
            for selected in sorted(collected - inspected):
                sd = self.index.get(selected)
                type_names |= self.type_names(self.index.clean[sd.path][sd.name_end:sd.signature_end], sd)
                inspected.add(selected)
            for words in REGISTRY.values():
                for word in words.split():
                    if word in type_names:
                        td = self.index.get('Elements.' + word)
                        type_names |= self.type_names(self.index.clean[td.path][td.name_end:td.end], td)
            added = set()
            for field, _, _ in fields:
                matches = {n for n in self.index.by_tail.get(field, [])
                           if n.rsplit('.', 2)[-2] in type_names}
                matches |= {n for n in self.members.get(field, set())
                            if n.rsplit('.', 1)[-1] in type_names}
                candidates[field] = matches
                added |= matches
            if added <= collected and type_names == previous_types:
                break
            collected |= added
        unresolved = set()
        for field, match, core in fields:
            for target in sorted(candidates[field]):
                record(target, match, 'field candidates via signature closure')
            if not candidates[field] and not core:
                unresolved.add(f'{name}:{clean.count(chr(10), 0, match.start()) + 1}: {match.group()} ({field})')
        calls = list({(c['start'], c['end'], c['name']): c for c in calls}.values())
        calls.sort(key=lambda c: (c['start'], c['name']))
        self.cache[key] = calls, unresolved
        self.unresolved[name] = unresolved
        return calls

    def unit(self, ref: str) -> dict:
        fact = self.facts[ref]
        name = 'Elements.' + fact['name']
        hints = tuple(sorted('Elements.' + s['name'] for s in fact['shared_steps']))
        inherited = {s['name']: s for entries in fact['inherited'].values() for s in entries}
        for short, step in inherited.items():
            require(self.index.get('Elements.' + short).path == step['file'],
                    f'{ref}: inherited helper path changed: {short}')
        for step in fact['shared_steps']:
            d = self.index.get('Elements.' + step['name'])
            require(d.path == step['file'], f'{ref}: shared step path changed: {step["name"]}')
        own_namespace = heath.parse_ref(ref).lean.split('.porism')[0]
        if fact['kind'] != 'proposition':
            own_namespace = heath.parse_ref(fact['of']).lean
        discovered: dict[str, list[dict]] = {}
        dependencies = set()
        signatures = set(hints) | {'Elements.' + n for n in inherited}
        signatures |= {'Elements.' + self.facts[r]['name'] for r in fact['cites']}
        owners = {name}
        shared_seen = set()
        while True:
            previous = (set(owners), set(signatures))
            for current in sorted(owners):
                found = self.direct(current, tuple(sorted(signatures)))
                discovered[current] = found
                signatures.update(call['name'] for call in found)
                for call in found:
                    target = call['name']
                    if target == name:
                        continue
                    if target in self.by_name:
                        dependencies.add(self.by_name[target]['ref'])
                    elif target.startswith(own_namespace + '.'):
                        owners.add(target)
                    elif target in hints:
                        shared_seen.add(target)
                        step = next(s for s in fact['shared_steps'] if 'Elements.' + s['name'] == target)
                        dependencies.update(step['brings_in'])
            if previous == (owners, signatures):
                break
        unresolved = sorted({token for owner in owners for token in self.unresolved[owner]})
        require(not unresolved, f'{ref}: unresolved names: {unresolved}')
        # All certificate steps must be accounted for in the reachable source, including
        # field notation. A mismatch is an extraction failure, never a passing audit.
        missing_steps = set(hints) - shared_seen
        require(not missing_steps, f'{ref}: certificate steps not resolved in source: {sorted(missing_steps)}')
        require(dependencies == set(fact['cites']),
                f'{ref}: source/certificate mismatch: source-only {sorted(dependencies - set(fact["cites"]))}; '
                f'certificate-only {sorted(set(fact["cites"]) - dependencies)}')
        return {'ref': ref, 'declaration': name, 'reachable_helpers': sorted(set(discovered) - {name}),
                'calls_found': [{'in': owner, **call} for owner, found in discovered.items() for call in found],
                'facts_cites': fact['cites'], 'facts_shared_steps': fact['shared_steps'],
                'facts_inherited_helpers': sorted('Elements.' + n for n in inherited),
                'source_cites': sorted(dependencies, key=lambda r: (heath.prop_key(r), r)),
                'unresolved_names': unresolved, 'row': None,
                'helper_bodies_audited': False}


def tables(e: Evidence, source: dict, path: str, record: dict, keys: tuple[str, ...]) -> dict:
    result = {}
    raw = e.read(path)
    for key in keys:
        if key not in record:
            continue
        found = re.search(r'^\[' + re.escape(key) + r'\]\s*\n', raw, re.M)
        require(found is not None, f'{path}: missing original [{key}]')
        following = re.search(r'^\[', raw[found.end():], re.M)
        end = found.end() + following.start() if following else len(raw)
        original = e.excerpt(source, 'record.' + key, path, found.start(), end,
                             transformation='tomllib table; statement fingerprint omitted' if key == 'statement'
                             else 'tomllib table')
        parsed = tomllib.loads(original)[key]
        require(parsed == record[key], f'{path}: table extraction mismatch for {key}')
        if key == 'statement':
            parsed.pop('fingerprint', None)
        result[key] = parsed
    return result


def terms(e: Evidence, source: dict, record: dict) -> dict:
    path = 'review/terms.toml'
    raw = e.read(path)
    valid = heath.load_terms()
    result = {}
    for tag in record.get('representation', {}).get('tags', []):
        require(tag in valid, f'{path}: unknown representation {tag}')
        found = re.search(r'^\[tag\.' + re.escape(tag) + r'\]\s*\n', raw, re.M)
        require(found is not None, f'{path}: missing tag {tag}')
        following = re.search(r'^\[', raw[found.end():], re.M)
        end = found.end() + following.start() if following else len(raw)
        text = e.excerpt(source, 'terms.' + tag, path, found.start(), end, transformation='tomllib table')
        result[tag] = tomllib.loads(text)['tag'][tag]
        require(result[tag] == valid[tag], f'{path}: changed term {tag}')
    return result


def heath_text(e: Evidence, source: dict, book: str, n: int, *, proof: bool = True,
               field: str = '') -> dict:
    path = relative(heath.heath_path(book, n))
    raw = e.read(path)
    _, enunciation, paragraphs = heath.read(book, n)
    matches = list(re.finditer(r'^\*([^\n]+)\*([^\n]*)$', raw, re.M))
    require(len(matches) == 1, f'{path}: expected one single-line italic enunciation')
    match = matches[0]
    result = {'enunciation': e.excerpt(source, field + 'enunciation', path, *match.span(1))}
    require(heath.normalize(result['enunciation'] + match.group(2)) == enunciation,
            f'{path}: enunciation mismatch')
    if match.group(2).strip():
        result['enunciation_reference'] = e.excerpt(source, field + 'enunciation_reference',
                                                   path, *match.span(2))
    if proof:
        start = match.end()
        while start < len(raw) and raw[start].isspace():
            start += 1
        result['heath_proof'] = e.excerpt(source, field + 'heath_proof', path, start, len(raw))
        checked = heath.HTML_COMMENT.sub('', raw[start:])
        require([heath.normalize(p) for p in checked.split('\n\n') if p.strip()] == paragraphs,
                f'{path}: proof extraction mismatch')
    if heath.bracketed(book, n):
        heading = re.search(r'^# \[.*$', raw, re.M)
        require(heading is not None, f'{path}: bracketed heading missing')
        result['heath_heading'] = e.excerpt(source, field + 'heath_heading', path, *heading.span())
    porism = heath.heath_porism(book, n)
    if porism:
        matches = [m for m in re.finditer(r'[^\n]+(?:\n(?!\n)[^\n]+)*', raw)
                   if heath.normalize(m.group()) == porism]
        require(len(matches) == 1, f'{path}: porism paragraph is not unique')
        result['heath_porism'] = e.excerpt(source, field + 'heath_porism', path, *matches[0].span())
    return result


def statement(index: Index, source: dict, ref: str, field: str) -> str:
    parsed = heath.parse_ref(ref)
    d = index.get(parsed.lean)
    if parsed.kind == 'proposition':
        span = heath.theorem_span(index.evidence.read(d.path), parsed.n)
        require(span and span.start == d.start and span.start <= d.keyword < span.end,
                f'{ref}: main theorem disagrees with heath.theorem_span')
    return index.quote(source, field, d.name, doc=False)


def caption(e: Evidence, source: dict, book: str, n: int) -> str:
    path = f'book/{book}/{n:02d}.md'
    raw = e.read(path)
    image = f'../../figures/{book}/{n:02d}.svg'
    require(raw.count(image) == 1, f'{path}: Heath image is not unique')
    start = raw.index(image)
    image_end = raw.find('</p>', start)
    require(image_end >= 0, f'{path}: image paragraph missing')
    tail = raw[image_end + 4:]
    found = re.match(r'\s*(<p[^>]*>\s*<em>.*?</em>\s*</p>)', tail, re.S)
    if found:
        return e.excerpt(source, 'caption', path, image_end + 4 + found.start(1),
                         image_end + 4 + found.end(1))
    return ''


SCOPE = {
    'type': 'choice',
    'instructions': "Does the Lean statement cover the enunciation? The enunciation is `enunciation`, Euclid's words in Heath's translation; the main Lean statement is `lean_statement`, with its porism and companions in `attached_statements`; `record` is what the review record says about the statement's scope. Judge these declarations together, including the porism when one is supplied, using the notation, definitions and representation qualifications given here.",
    'criteria': {
        'fully': "The Lean statements together prove every clause of `enunciation` and of the supplied porism for every configuration Euclid's words admit, in the stated representation. A hypothesis that only names what his words already presuppose, as that the corners of a triangle are not on one straight line, is not a restriction.",
        'restricted, exactly as the note says': "The Lean statements together leave out some configuration Euclid's words admit, or leave some clause without a formal conclusion, and `record` names every such restriction and omission.",
        'restricted beyond what the note says': 'The Lean statements together leave out some configuration Euclid\'s words admit, or leave some clause without a formal conclusion, that `record` does not name. A record whose scope is "full" names none.',
        'cannot tell': 'What is given here is not enough to decide.',
    },
}
CITATIONS = {
    'type': 'choice',
    'instructions': "Does every proposition called by the proof unit in `lean_proof` do work towards its conclusion or a substantive intermediate step of Euclid's argument? Also check for artificial hypothesis uses. Judge this unit's uses of the supplied helper signatures; helper bodies are outside this question. Heath's sentences stand as `--` lines and `cited` gives exact enunciations. In Lean, `have h : T := p` proves T by p and calls the result h; `obtain ⟨…⟩ := p` takes p apart into named pieces; `rw [h34, h37, …]` rewrites the goal by the equalities named. Follow uses through helper calls and tactics as well as explicit names. An anonymous binding or an unused hypothesis alone does not establish a defect. If both defects occur, choose `a dummy citation`.",
    'criteria': {
        'all do work': 'Every proposition call supports a later step or the conclusion, or establishes a substantive intermediate fact tied to a real sentence of Euclid. No hypothesis is mentioned merely to look used. With no proposition calls the citation part alone is vacuous; hypothesis use must still be inspected.',
        'a dummy citation': 'Some proposition call does no substantive work: its result neither supports the argument nor establishes a substantive intermediate fact, and merely supplies a citation while the step is done another way.',
        'an artificial hypothesis use': 'No dummy citation is established, but a hypothesis is mentioned only so that it looks used, and does no substantive work.',
        'cannot tell': 'What is given here is not enough to decide.',
    },
}
REPRESENTATION = {
    'type': 'choice',
    'instructions': "Do the supplied definitions and bridge signatures state the conditional connections between the represented objects named in `represented_objects` and Euclid's objects in `enunciation`, within the convention and limitations in `record` and `terms`? Check all hypotheses and conclusions. A definition may itself supply a connection; a choice definition alone does not prove that its choice represents a given object. `bridge_placement` distinguishes declarations available before the main theorem from explanatory declarations at or after it; the latter are not premises available to that proof. This question asks what the supplied declarations state, not whether each invocation meets its premises, whether a proof passes Lean or whether the bridges are placed correctly in the dependency order. A `bridge stated` answer alone therefore does not establish all of P13. A missing supplied bridge does not establish that none exists elsewhere.",
    'criteria': {
        'bridge stated': 'The supplied declarations state each needed conditional connection under the relevant hypotheses and within the disclosed convention.',
        'bridge missing or inadequate': 'A needed connection has no adequate declaration supplied, or its premises make it unavailable for the represented objects under discussion.',
        'no bridge required': 'The supplied material uses no representation requiring such a bridge; a tag may instead describe a change of hypotheses or scope.',
        'cannot tell': 'The supplied context is insufficient to judge the conditional connection or its intended hypotheses.',
    },
}
COMMENTARY = {
    'type': 'choice',
    'instructions': "Does what `commentary` says about the statement's scope, the route of the proof and the named Lean declarations agree with the supplied statements, declaration signatures and record? Judge the mathematical account under the disclosed conventions. Quotation accuracy, historical attribution and voice are outside this question. Signatures alone need not settle a claim about a proof's internal steps; choose `cannot tell` where the supplied evidence does not settle it.",
    'criteria': {
        'agrees': 'The commentary agrees with the supplied scope, declared route and named declarations.',
        'conflicts': 'A mathematical claim about the scope, route or a named declaration conflicts with the supplied evidence.',
        'cannot tell': 'What is given here is not enough to decide.',
    },
}
FIGURE = {
    'type': 'choice',
    'instructions': "Does the image named in `figure` agree with `heath_proof`, the main Lean statement and its own caption? Check the letters, incidence, betweenness, order and sides for the stage illustrated. A drawing need not depict every configuration of the theorem. For an impossible supposition in a reductio, allow only the specific incompatibility identified in the caption as belonging to that supposition. All other relationships must agree, and the caption's own claims must match the image. An ordinary error remains a defect even if disclosed. Judge geometry, not numerical accuracy measured from pixels.",
    'criteria': {
        'agrees': 'The letters and arrangement agree with the illustrated stage, and the caption describes the image accurately; only a specifically identified incompatibility of an impossible supposition is excepted.',
        'disagrees': 'A letter, geometric relationship or caption conflicts with the illustrated stage beyond that specific reductio exception.',
        'cannot tell': 'What is given here is not enough to decide.',
    },
}


class Generator:
    def __init__(self, commit: str, books: tuple[tuple[str, int], ...] = BOOKS):
        self.evidence = Evidence(commit)
        self.index = Index(self.evidence)
        self.books = books
        self.facts_data = json.loads(self.evidence.read('facts.json'))
        self.facts = {p['ref']: p for p in self.facts_data['propositions']}
        require(len(self.facts) == len(self.facts_data['propositions']), 'duplicate facts.json reference')
        self.calls = Calls(self.index, self.facts)
        self.rows: list[dict] = []
        self.coverage: dict[str, dict] = {}
        for path in ('scripts/heath.py', 'scripts/audit/jev.py', 'review/SCHEMA.md', 'Certificate/FIELDS.md'):
            self.evidence.read(path)
        bundled = {name for book, count in books for n in range(1, count + 1)
                   for name in self.bundle(book, n)[0]}
        self.registry = registry_for(books, bundled)

    def bundle(self, book: str, n: int) -> tuple[list[str], list[str]]:
        """The proposition's bundle, unless its record marks the representations item `n/a`;
        with the outline's, where a companion takes the figure by its outline."""
        record = tomllib.loads(self.evidence.read(f'review/{book}/{n:02d}.toml'))
        if record['review'].get('items', {}).get('representations') == 'n/a':
            return [], []
        ref = f'{book}.{n}'
        cited = self.cited_laws(ref) if ref in CITED_EXTRAS else []
        return bundle(book, n, f'{ref} outline' in self.facts[ref]['attached'], cited)

    def cited_laws(self, ref: str) -> list[str]:
        """The bridges of the laws that the derivation of `ref`, I.4 or I.8, cites: each proof
        of each law of its `cited_laws` in facts.json, in the certificate's order, with
        `Elements.` before it, and then its CITED_EXTRAS. A derivation whose entry names no law,
        or a law no proof, is refused, since its record checked each law with its proof."""
        laws = self.facts[ref].get('cited_laws')
        require(laws, f'{ref}: facts.json gives its derivation no cited_laws')
        proofs = []
        for law in laws:
            require(law.get('proofs'), f'{ref}: facts.json gives no proof of its law {law.get("law")}')
            proofs += ['Elements.' + proof['name'] for proof in law['proofs']]
        return list(dict.fromkeys(proofs + CITED_EXTRAS[ref]))

    def record_checked(self, ref: str) -> tuple[str, ...]:
        """RECORD_CHECKED's names for the record of `ref`, with, for I.4 and I.8, the bridges of
        the laws its derivation cites (cited_laws)."""
        cited = self.cited_laws(ref) if ref in CITED_EXTRAS else []
        return (*RECORD_CHECKED.get(ref, ()), *cited)

    def checked(self, ref: str, record: dict, state: dict) -> list[str]:
        """What the record says its representations verdict rests on that the row does not
        supply, as a bridge, a definition or one of the statements it judges: each name its
        [representation] note gives in backticks, and its names of RECORD_CHECKED, the laws
        it cites among them (record_checked), and, where the row's statements take a figure by
        its outline, OUTLINE_CHECKED. A name of RECORD_LATER, which the note names as a theorem
        proved after the proposition, is not asked of the row for the note's naming it; an entry
        there that the note does not name, or that is declared before the main theorem, is
        refused."""
        consumer = self.index.get(heath.parse_ref(ref).lean)
        names = []
        for token in re.findall(r'`([^`]+)`', record.get('representation', {}).get('note', '')):
            if re.fullmatch(NAME, token):
                name = self.index.resolve(token, consumer, commentary=True)
                require(name, f'{ref}: its record names {token}, which is no declaration')
                names.append(name)
        later = RECORD_LATER.get(ref, ())
        for name in later:
            require(name in names, f'{ref}: RECORD_LATER names {name}, which its record\'s '
                                   '[representation] note does not name')
            require(not self.index.available_before(name, consumer),
                    f'{ref}: RECORD_LATER names {name}, which is declared before {consumer.name}')
        names = [name for name in names if name not in later]
        names += self.record_checked(ref)
        if f'{ref} outline' in self.facts[ref]['attached']:
            names += OUTLINE_CHECKED.get(ref, ())
        supplied = set(state['bridges']) | {'Elements.' + name for name in state['definitions']}
        supplied |= {heath.parse_ref(a).lean for a in [ref, *state['attached_statements']]}
        return [name for name in dict.fromkeys(names) if name not in supplied]

    def source(self, book: str, n: int) -> dict:
        return {'commit': self.evidence.commit, 'heath': f'heath/{book}/{n:02d}.md',
                'lean': f'Elements/Book{book}/Prop{n:02d}.lean', 'record': f'review/{book}/{n:02d}.toml',
                'facts': 'facts.json', 'excerpts': []}

    def row(self, ref: str, item: int, suffix: str, source: dict, state: dict,
            question: dict, verdict: str | None, expectation: dict[str, str], key: str) -> dict:
        table, field = key.rsplit('.', 1)
        row = {'id': f'{item:02d}-{ref.replace(" ", "-").replace("Por.", "porism")}-{suffix}',
               'item': item, 'ref': ref, 'seeded': False, 'source': source,
               'why': f'{source["record"]} [{table}].{field} = {dumps(verdict)}; '
                      'the expectation reports the record\'s claim for this bounded question.',
               'state': state, 'question': copy.deepcopy(question)}
        if verdict in expectation:
            row['expected'] = expectation[verdict]
        else:
            row['expectation_unavailable'] = {'field': key, 'verdict': verdict}
        self.rows.append(row)
        return row

    def signatures(self, source: dict, names: list[str], field: str) -> dict:
        return {n: self.index.quote(source, field + '.' + n, n) for n in sorted(set(names))}

    def bridges(self, source: dict, book: str, n: int) -> tuple[dict, list[str], dict]:
        objects, names = self.bundle(book, n)
        # The evidence commit of the audit of Books I and II, of 19 October, holds no outline of
        # a parallelogram: its two bridges are supplied where the evidence declares them.
        names = [name for name in names if name not in PARALLELOGRAM_OUTLINE_BRIDGES
                 or name in self.index.decls]
        quoted = {name: self.index.quote(source, 'bridges.' + name, name,
                                        full=self.index.get(name).kind in ('def', 'abbrev'))
                  for name in sorted(set(names))}
        main = self.index.get(heath.parse_ref(f'{book}.{n}').lean)
        placement = {}
        # A bridge's body is read with the definitions the row supplies beside it, whose types
        # name its fields, as `v.pt` and `.A` in `Cited.holds_lenSymm` (`Calls.direct`).
        supplied = tuple(sorted('Elements.' + name for name in objects))
        for name in names:
            d = self.index.get(name)
            calls = self.calls.direct(name, supplied)
            prop_calls = [c for c in calls if re.search(r'\.Book[IVX]+\.Prop\d+', c['name'])]
            available = self.index.available_before(name, main)
            # These signatures explain a representation, and may be corollaries of
            # the consumer. They must never be misreported as available premises.
            placement[name] = {'path': d.path, 'line': self.index.clean[d.path].count('\n', 0, d.keyword) + 1,
                               'available_before_main': available,
                               'role': 'available declaration' if available else 'explanatory later declaration',
                               'body_proposition_calls': prop_calls}
            # A later book's bridge cannot justify an earlier book: a Book II bridge may
            # serve Book III, never Book I.
            order = [b for b, _ in BOOKS]
            for later in order[order.index(book) + 1:]:
                require(f'/Book{later}/' not in d.path,
                        f'{book}.{n}: a Book {later} bridge cannot justify Book {book}')
        extra = {'bridge_context': self.index.context(source, 'bridge_context', names),
                 'consumer_imports': self.index.import_text(source, 'consumer_imports', main.path),
                 'bridge_imports': {path: self.index.import_text(source, 'bridge_imports.' + path, path)
                                    for path in sorted({self.index.get(name).path for name in names})}}
        return quoted, objects, {'state': extra, 'placement': placement}

    def cited(self, source: dict, refs: list[str]) -> dict:
        result = {}
        for ref in sorted(set(refs), key=lambda r: (heath.prop_key(r), r)):
            p = heath.parse_ref(ref)
            result[ref] = heath_text(self.evidence, source, p.book, p.n, proof=False,
                                     field='cited.' + ref + '.')
        return result

    def proposition(self, book: str, n: int) -> None:
        e, index = self.evidence, self.index
        ref = f'{book}.{n}'
        fact = self.facts[ref]
        path = f'review/{book}/{n:02d}.toml'
        record = tomllib.loads(e.read(path))
        # load_review also reads Heath's text (including the porism) and, for
        # representation tags, the terms catalogue. Guard all three before the helper.
        e.read(relative(heath.heath_path(book, n)))
        e.read('review/terms.toml')
        heath.load_review(book, n)
        require(record['statement']['fingerprint'] == heath.review_fingerprint(self.facts_data, ref),
                f'{path}: stale statement fingerprint')
        lean = heath.lean_path(book, n)
        e.read(relative(lean))
        require(record['review']['lean'] == heath.file_hash(lean),
                f'{path}: stale Lean fingerprint')
        attached = sorted(fact['attached'], key=lambda r: (heath.prop_key(r), r))
        require(attached == fact['attached'], f'{ref}: attachment order differs from contract')
        require(set(attached) == {p['ref'] for p in self.facts.values() if p.get('of') == ref},
                f'{ref}: attachment coverage mismatch')
        require(set(record['statement'].get('companions', [])) ==
                {a for a in attached if self.facts[a]['kind'] == 'companion'},
                f'{ref}: record companions differ from facts.json')
        for target in [ref] + attached:
            require(heath.parse_ref(target).lean == 'Elements.' + self.facts[target]['name'],
                    f'{target}: declaration name differs from facts.json')
        verdicts = record['review'].get('items', {})
        coverage = {'rows': [], 'proof_units': [], 'commentary_non_declarations': []}
        self.coverage[ref] = coverage
        first = len(self.rows)

        source = self.source(book, n)
        state = {'proposition': ref, **heath_text(e, source, book, n),
                 'lean_statement': statement(index, source, ref, 'lean_statement'),
                 'attached_statements': {a: statement(index, source, a, 'attached_statements.' + a)
                                         for a in attached},
                 'record': tables(e, source, path, record, ('statement', 'representation', 'coverage')),
                 'terms': terms(e, source, record)}
        bridges, objects, bridge_info = self.bridges(source, book, n)
        if bridges:
            state['bridges'] = bridges
            state.update(bridge_info['state'])
        state.update(glossary(index, source,
                              [state['lean_statement'], *state['attached_statements'].values(), *bridges.values()],
                              objects, self.registry))
        state['statement_context'] = index.context(source, 'statement_context',
                                                    [heath.parse_ref(a).lean for a in [ref] + attached])
        self.row(ref, 9, 'scope', source, state, SCOPE, record['statement']['scope'],
                 {'full': 'fully', 'restricted': 'restricted, exactly as the note says',
                  'partial': 'restricted, exactly as the note says'}, 'statement.scope')

        for target in [ref] + attached:
            unit = self.calls.unit(target)
            coverage['proof_units'].append(unit)
            if target != ref and not unit['source_cites']:
                unit['omission_reason'] = 'Attachment calls no proposition or proposition-derived helper.'
                continue
            source = self.source(book, n)
            name = heath.parse_ref(target).lean
            signatures = {c['name'] for c in unit['calls_found'] if c['name'] != name}
            signatures |= {'Elements.' + self.facts[r]['name'] for r in unit['facts_cites']}
            signatures |= set(unit['reachable_helpers'])
            signatures |= set(unit['facts_inherited_helpers'])
            helpers = self.signatures(source, sorted(signatures), 'helper_signatures')
            state = {'proposition': ref, 'proof_unit': target, **heath_text(e, source, book, n),
                     'lean_proof': index.quote(source, 'lean_proof', name, full=True),
                     'helper_signatures': helpers,
                     'declaration_context': index.context(source, 'declaration_context', [name, *signatures])}
            heath_refs = heath.citations(heath.read(book, n)[2])
            state['cited'] = self.cited(source, [*heath_refs, *unit['facts_cites'], *unit['source_cites']])
            state['citation_origins'] = {'heath': sorted(heath_refs, key=lambda r: (heath.prop_key(r), r)),
                                         'certificate': unit['facts_cites'], 'source': unit['source_cites']}
            state.update(glossary(index, source, [state['lean_proof'], *helpers.values()],
                                  groups=self.registry))
            question = copy.deepcopy(CITATIONS)
            policy_path = 'docs/FORMALIZATION.md'
            policy = e.read(policy_path)
            anchor = 'A checked intermediate fact tied to a real sentence of Euclid is legitimate, even if the\n  final proof term could do without it.'
            require(policy.count(anchor) == 1, f'{policy_path}: policy quotation is not unique')
            start = policy.index(anchor)
            quoted = e.excerpt(source, 'question.instructions.policy', policy_path, start, start + len(anchor))
            question['instructions'] += '\n\n' + policy_path + ', section 5:\n' + quoted
            row = self.row(target, 10, 'citations', source, state, question, verdicts.get('passages'),
                           {'pass': 'all do work'}, 'review.items.passages')
            unit['row'] = row['id']
            for call in unit['calls_found']:
                call['row'] = row['id']
                call['evidence'] = 'body' if call['in'] == name else 'reachable helper signature only'

        source = self.source(book, n)
        bridges, objects, bridge_info = self.bridges(source, book, n)
        state = {'proposition': ref, **heath_text(e, source, book, n, proof=False),
                 'lean_statement': statement(index, source, ref, 'lean_statement'),
                 'attached_statements': {a: statement(index, source, a, 'attached_statements.' + a)
                                         for a in attached},
                 'record': tables(e, source, path, record, ('statement', 'representation')),
                 'terms': terms(e, source, record), 'represented_objects': objects, 'bridges': bridges,
                 'bridge_placement': bridge_info['placement'],
                 **bridge_info['state']}
        state.update(glossary(index, source,
                              [state['lean_statement'], *state['attached_statements'].values(), *bridges.values()],
                              objects, self.registry))
        state['statement_context'] = index.context(source, 'statement_context',
                                                    [heath.parse_ref(a).lean for a in [ref] + attached])
        coverage['bridge_placement'] = bridge_info['placement']
        # A record that passes its representations rests on bridges, which its row supplies;
        # one marked `n/a` rests on none (calibration bar, 25 October 2026).
        require((verdicts.get('representations') == 'pass') == bool(bridges),
                f'{ref}: representations {verdicts.get("representations")!r} with '
                f'{len(bridges)} bridges supplied')
        if verdicts.get('representations') == 'pass':
            missing = self.checked(ref, record, state)
            require(not missing, f'{ref}: the row does not supply what its record checked: {missing}')
        self.row(ref, 11, 'representation', source, state, REPRESENTATION, verdicts.get('representations'),
                 {'pass': 'bridge stated', 'fail': 'bridge missing or inadequate', 'n/a': 'no bridge required'},
                 'review.items.representations')

        source = self.source(book, n)
        mishnah = e.whole(source, 'commentary', f'mishnah/{book}/{n:02d}.md')
        named = []
        consumer = index.get(heath.parse_ref(ref).lean)
        for token in sorted(set(re.findall(r'`([^`]+)`', mishnah))):
            resolved = index.resolve(token, consumer, commentary=True) if re.fullmatch(NAME, token) else None
            if resolved:
                named.append(resolved)
            else:
                coverage['commentary_non_declarations'].append(token)
        declarations = self.signatures(source, named, 'named_declarations')
        state = {'proposition': ref, 'commentary': mishnah,
                 'heath_proof': heath_text(e, source, book, n)['heath_proof'],
                 'lean_proof': index.quote(source, 'lean_proof', consumer.name, full=True),
                 'record': tables(e, source, path, record, ('statement', 'route')),
                 'lean_statement': statement(index, source, ref, 'lean_statement'),
                 'attached_statements': {a: statement(index, source, a, 'attached_statements.' + a)
                                         for a in attached}, 'named_declarations': declarations,
                 'declaration_context': index.context(source, 'declaration_context',
                                                       [consumer.name, *named, *[heath.parse_ref(a).lean for a in attached]])}
        state.update(glossary(index, source,
                              [state['lean_statement'], *state['attached_statements'].values(),
                               state['lean_proof'], *declarations.values()], groups=self.registry))
        self.row(ref, 12, 'commentary', source, state, COMMENTARY, verdicts.get('commentary'),
                 {'pass': 'agrees'}, 'review.items.commentary')

        source = self.source(book, n)
        heath_state = heath_text(e, source, book, n)
        # R4 fixes this state's evidence narrowly; headings remain part of Heath's text.
        heath_state.pop('heath_porism', None)
        state = {**heath_state, 'lean_statement': statement(index, source, ref, 'lean_statement'),
                 'caption': caption(e, source, book, n), 'figure': f'JEV_HEATH_{book}_{n}'}
        row = self.row(ref, 13, 'figure', source, state, FIGURE, verdicts.get('figures'),
                       {'pass': 'agrees'}, 'review.items.figures')
        figure_path = f'figures/{book}/{n:02d}.svg'
        e.read(figure_path)
        source['figure'] = figure_path
        source['page'] = f'book/{book}/{n:02d}.md'
        row['assets'] = {state['figure']: figure_path}
        coverage['rows'] = [r['id'] for r in self.rows[first:]]

    def controls(self) -> None:
        originals = {r['id']: r for r in self.rows}
        counts: Counter = Counter()

        def control(rid: str, expected: str) -> dict:
            row = copy.deepcopy(originals[rid])
            counts[row['item']] += 1
            row['id'] += f'-seeded-{counts[row["item"]]}'
            row['seeded'] = True
            row['expected'] = expected
            row['why'] = 'Synthetic defect control; the mutation, not the record, determines the expectation.'
            row['mutation'] = {'base_id': rid, 'base_state_sha256': sha(dumps(row['state'])), 'changes': []}
            self.rows.append(row)
            parent = heath.parse_ref(row['ref']).parent
            self.coverage[parent]['rows'].append(row['id'])
            return row

        def change(row: dict, field: list[str], old: str, new: str) -> None:
            value = row
            for part in field[:-1]:
                value = value[part]
            text = value[field[-1]]
            require(isinstance(text, str), f'{row["id"]}: mutation field is not text: {field}')
            # Missing and repeated anchors are told apart (#350: I.40's went missing).
            require(text.count(old) == 1,
                    f'{row["id"]}: mutation anchor occurs {text.count(old)} times, not once: {old!r}')
            value[field[-1]] = text.replace(old, new)
            row['mutation']['changes'].append({'operation': 'replace', 'field': field, 'old': old, 'new': new,
                                               'before_sha256': sha(text), 'after_sha256': sha(value[field[-1]])})

        def remove(row: dict, field: list[str]) -> None:
            value = row
            for part in field[:-1]:
                value = value[part]
            old = value.pop(field[-1])
            row['mutation']['changes'].append({'operation': 'remove', 'field': field, 'old': old,
                                               'before_sha256': sha(old if isinstance(old, str) else dumps(old))})

        row = control('09-I.6-scope', 'restricted beyond what the note says')
        change(row, ['state', 'lean_statement'], '(hABC : Triangle A B C)',
               '(hABC : Triangle A B C) (hACBC : ‖A C‖ = ‖B C‖)')
        row = control('09-I.5-scope', 'restricted beyond what the note says')
        change(row, ['state', 'lean_statement'], ' ∧ ∠ C B D = ∠ B C E', '')
        row = control('10-I.41-citations', 'a dummy citation')
        change(row, ['state', 'lean_proof'], ':= by\n',
               ':= by\n  have unrelated := @Elements.BookI.Prop15\n')
        row['state']['helper_signatures']['Elements.BookI.Prop15'] = self.index.quote(
            row['source'], 'helper_signatures.Elements.BookI.Prop15', 'Elements.BookI.Prop15')
        row['state']['cited'].update(self.cited(row['source'], ['I.15']))
        row['state']['declaration_context'].update(self.index.context(
            row['source'], 'declaration_context', ['Elements.BookI.Prop15']))
        for origin in ('certificate', 'source'):
            old = row['state']['citation_origins'][origin]
            new = sorted([*old, 'I.15'], key=lambda r: (heath.prop_key(r), r))
            row['state']['citation_origins'][origin] = new
            row['mutation']['changes'].append({'operation': 'replace',
                                               'field': ['state', 'citation_origins', origin],
                                               'old': old, 'new': new,
                                               'before_sha256': sha(dumps(old)),
                                               'after_sha256': sha(dumps(new))})
        row['mutation']['added_evidence'] = [
            'Elements.BookI.Prop15', 'I.15',
            'citation_origins.certificate:I.15', 'citation_origins.source:I.15'
        ]
        row = control('10-I.41-citations', 'an artificial hypothesis use')
        change(row, ['state', 'lean_proof'], '(hE : Collinear A D E)',
               '(hE : Collinear A D E) (hAA : A = A)')
        change(row, ['state', 'lean_proof'], ':= by\n', ':= by\n  have unused := hAA\n')
        row = control('11-II.4-representation', 'bridge missing or inadequate')
        for name in list(row['state']['bridges']):
            remove(row, ['state', 'bridges', name])
            remove(row, ['state', 'bridge_context', name])
            remove(row, ['state', 'bridge_placement', name])
        remaining_paths = {self.index.get(name).path for name in row['state']['bridges']}
        for path in list(row['state']['bridge_imports']):
            if path not in remaining_paths:
                remove(row, ['state', 'bridge_imports', path])
        row = control('11-II.4-representation', 'bridge missing or inadequate')
        for name in row['state']['bridges']:
            d = self.index.get(name)
            raw = self.evidence.read(d.path)
            anchor = raw[d.keyword:d.name_end]
            change(row, ['state', 'bridges', name], anchor, anchor + ' (impossible : False)')
        for rid, wrong in [('13-I.37-figure', 'figures/I/01.svg'), ('13-II.4-figure', 'figures/I/31.svg')]:
            row = control(rid, 'disagrees')
            key = row['state']['figure']
            change(row, ['assets', key], row['assets'][key], wrong)
            self.evidence.read(wrong)
            row['source']['control_figure'] = wrong
        row = control('12-I.39-commentary', 'conflicts')
        change(row, ['state', 'commentary'],
               'equal triangles on opposite sides of BC need not make AD parallel to BC',
               'equal triangles on opposite sides of BC must make AD parallel to BC')
        row = control('12-I.40-commentary', 'conflicts')
        change(row, ['state', 'commentary'], 'with BC and CE meeting at C',
               'with BC and CE apart')
        require(dict(counts) == {9: 2, 10: 2, 11: 2, 13: 2, 12: 2}, 'control coverage changed')

    def audit(self) -> None:
        """Every row of the audit, with its controls, its options rotated and checked."""
        for book, count in self.books:
            for n in range(1, count + 1):
                self.proposition(book, n)
        self.controls()
        # Parents, numeric item, main unit before attachments, then controls of that item.
        self.rows.sort(key=lambda r: (heath.prop_key(heath.parse_ref(r['ref']).parent), r['item'],
                                      r['seeded'], heath.prop_key(r['ref']), r['ref'], r['id']))
        ordinals: Counter = Counter()
        seen: set[str] = set()
        for row in self.rows:
            criteria = list(row['question']['criteria'].items())
            offset = ordinals[row['seeded']] % len(criteria)
            ordinals[row['seeded']] += 1
            row['question']['criteria'] = dict(criteria[offset:] + criteria[:offset])
            row['option_rotation'] = offset
            row['state_characters'] = len(dumps(row['state']))
            row['long_context'] = row['state_characters'] > LIMIT
            problems = jev.check_row(row, row['id'], seen)
            require(not problems, '\n'.join(problems))
            require(not any(k in row['state'] for k in ('review', 'expected', 'why', 'source', 'long_context')),
                    f'{row["id"]}: local labels leaked into state')
            require('fingerprint' not in row['state'].get('record', {}).get('statement', {}),
                    f'{row["id"]}: fingerprint leaked into state')
            if row['item'] in (10, 13):
                require('record' not in row['state'], f'{row["id"]}: review record leaked')
            for excerpt in row['source']['excerpts']:
                raw = self.evidence.read(excerpt['path'])
                require(sha(raw[excerpt['start']:excerpt['end']]) == excerpt['sha256'],
                        f'{row["id"]}: source slice changed')
            # Every quoted source and every control asset has its original file hash.
            paths = {x['path'] for x in row['source']['excerpts']}
            paths |= {row['source'][k] for k in ('heath', 'lean', 'record', 'facts')}
            paths |= set(row.get('assets', {}).values())
            if 'page' in row['source']:
                paths.add(row['source']['page'])
            row['source']['files'] = {p: sha(self.evidence.read(p)) for p in sorted(paths)}

    def finish(self) -> tuple[bytes, bytes, dict]:
        self.audit()
        by_id = {r['id']: r for r in self.rows}
        for ref, coverage in self.coverage.items():
            coverage['unresolved_names'] = sorted({token for unit in coverage['proof_units']
                                                   for token in unit['unresolved_names']})
            coverage['rows'] = [r['id'] for r in self.rows if heath.parse_ref(r['ref']).parent == ref]
            coverage['states'] = {rid: {'characters': by_id[rid]['state_characters'],
                                       'long_context': by_id[rid]['long_context'],
                                       'seeded': by_id[rid]['seeded']} for rid in coverage['rows']}
        self.evidence.unchanged()
        counts = {str(item): {'not_seeded': sum(r['item'] == item and not r['seeded'] for r in self.rows),
                             'seeded': sum(r['item'] == item and r['seeded'] for r in self.rows)}
                  for item in range(9, 14)}
        by_book = {book: {str(item): sum(r['item'] == item and not r['seeded']
                                         and heath.parse_ref(r['ref']).book == book for r in self.rows)
                          for item in range(9, 14)} for book, _ in self.books}
        largest = max(self.rows, key=lambda r: r['state_characters'])
        unresolved = sorted({token for names in self.calls.unresolved.values() for token in names})
        require(not unresolved, f'unresolved names: {unresolved}')
        manifest = {'commit': self.evidence.commit,
                    'evidence_verification': 'all evidence bytes equal git show',
                    'state_size_measure': 'len(json.dumps(state, ensure_ascii=False, allow_nan=False))',
                    'long_context_threshold': LIMIT, 'rows': len(self.rows), 'rows_by_item': counts,
                    'rows_by_book': by_book, 'books': [book for book, _ in self.books],
                    'proof_units': sum(len(p['proof_units']) for p in self.coverage.values()),
                    'long_context_states': sum(r['long_context'] for r in self.rows),
                    'largest_state': {'id': largest['id'], 'characters': largest['state_characters']},
                    'unresolved_names': unresolved,
                    'core_projection_allowlist': sorted(Calls.CORE_FIELDS),
                    'core_names': sorted(Calls.CORE_NAMES),
                    'core_constructors': 'X.mk and X.mk.injEq, where X names a structure or class '
                                         'the index holds',
                    'coverage_limits': [
                        'Citation questions inspect one unit body and helper signatures, not helper bodies.',
                        'Reachable helper calls are reconciled locally; their bodies receive no independent question.',
                        'Representation questions inspect conditional statements, not premise discharge or kernel checks.',
                        'Representation rows supply dependency placement as context in bridge_placement, but do not '
                        'adjudicate it; a bridge-stated answer does not establish correct placement or all of P13.',
                        'Commentary questions exclude quotation accuracy, attribution and voice.',
                        'Figure questions inspect the Heath figure only.',
                        'Record expectations are claims to test, not independent findings.',
                        'Score controls and production rows separately by item, option order and long_context; '
                        'an order disagreement remains unresolved regardless of the client agreement bar.'
                    ], 'propositions': self.coverage,
                    'evidence_files': {p: sha(raw) for p, raw in sorted(self.evidence.data.items())}}
        rows_bytes = jsonl(self.rows)
        manifest['questions_sha256'] = sha(rows_bytes)
        manifest_bytes = pretty(manifest)
        require('\u2014' not in rows_bytes.decode() and '\u2014' not in manifest_bytes.decode(),
                'an evidence excerpt contains prohibited punctuation')
        return rows_bytes, manifest_bytes, manifest


# ---------------------------------------------------------------------------------------
# The calibration set, as docs/decisions/2026-10-25-jev-calibration-bar.md (the entry) fixes
# it: each question's clean and defect answers, the order of the propositions, the kinds of
# fault and the bar; with docs/decisions/2026-10-26-jev-calibration-rulings.md (the rulings),
# which stands beside it and governs where the two differ: P12 has three kinds of fault, and
# P13's list for Book III is restated; and with docs/decisions/2026-10-26-jev-kind-not-applying.md
# (the kind ruling): a kind that cannot make a genuine fault on its base does not apply to it.
# Every row is an audit row of the same commit: a control unchanged, a plant a copy with one
# fault planted in the generated row, never in a file of the edition.

ENTRY = 'docs/decisions/2026-10-25-jev-calibration-bar.md'
RULINGS = 'docs/decisions/2026-10-26-jev-calibration-rulings.md'
KIND_RULING = 'docs/decisions/2026-10-26-jev-kind-not-applying.md'
MODEL = 'jev-1.13.0'


@dataclass(frozen=True)
class Question:
    item: int
    suffix: str
    clean: str
    defects: tuple[str, ...]
    # The record's table and key whose value gives the clean answer, and that value.
    verdict: tuple[str, str]
    value: str


QUESTIONS = {
    'P11': Question(9, 'scope', 'fully', ('restricted, exactly as the note says',
                                          'restricted beyond what the note says'),
                    ('statement', 'scope'), 'full'),
    'P12': Question(10, 'citations', 'all do work', ('a dummy citation', 'an artificial hypothesis use'),
                    ('items', 'passages'), 'pass'),
    'P13': Question(11, 'representation', 'bridge stated', ('bridge missing or inadequate',),
                    ('items', 'representations'), 'pass'),
    'P14': Question(12, 'commentary', 'agrees', ('conflicts',), ('items', 'commentary'), 'pass'),
    'P15': Question(13, 'figure', 'agrees', ('disagrees',), ('items', 'figures'), 'pass'),
}
for _name, _question in QUESTIONS.items():
    _options = {9: SCOPE, 10: CITATIONS, 11: REPRESENTATION, 12: COMMENTARY, 13: FIGURE}[_question.item]
    require({_question.clean, *_question.defects} <= _options['criteria'].keys(),
            f'{_name}: an answer the entry names is not an option of the question')
# For each book, how many controls, and then how many plants.
SPLIT = (('I', 4), ('II', 2), ('III', 4))
# The entry's table, with P13's list for Book III as the rulings restate it: for each question
# and book, the controls, then the plants.
CALIBRATION_LISTS = {
    'P11': {'I': ('I.23 I.2 I.10 I.34', 'I.8 I.19 I.29 I.9'), 'II': ('II.5 II.4', 'II.9 II.8'),
            'III': ('III.9 III.31 III.16 III.34', 'III.37 III.11 III.36 III.28')},
    'P12': {'I': ('I.27 I.12 I.16 I.33', 'I.21 I.45 I.15 I.40'), 'II': ('II.14 II.1', 'II.5 II.7'),
            'III': ('III.4 III.22 III.7 III.6', 'III.37 III.31 III.24 III.36')},
    'P13': {'I': ('I.42 I.8 I.41 I.38', 'I.37 I.46 I.43 I.36'), 'II': ('II.14 II.1', 'II.8 II.6'),
            'III': ('III.18 III.33 III.24 III.26', 'III.37 III.28 III.27 III.36')},
    'P14': {'I': ('I.37 I.43 I.4 I.21', 'I.47 I.38 I.13 I.7'), 'II': ('II.8 II.11', 'II.1 II.10'),
            'III': ('III.31 III.22 III.29 III.28', 'III.25 III.20 III.4 III.14')},
    'P15': {'I': ('I.44 I.8 I.24 I.43', 'I.22 I.34 I.7 I.13'), 'II': ('II.2 II.14', 'II.5 II.10'),
            'III': ('III.17 III.21 III.6 III.33', 'III.1 III.22 III.19 III.15')},
}
BAR = {
    'entry': ENTRY, 'rulings': RULINGS, 'model': MODEL, 'order_check': True,
    'conditions': [
        'every row is answered, by jev-1.13.0, and no line of the final output records a failed request',
        'at least 9 of the 10 planted faults are found: Jev chose a defect answer in both orders',
        'at most 2 of the 10 controls are false alarms: Jev chose a defect answer in either order',
        '`python3 scripts/audit/jev.py score <output> --bar 0.8` exits 0: the first answer is the '
        'expected one on at least 16 of the 20 rows',
    ],
    'found_at_least': 9, 'false_alarms_at_most': 2, 'agreement_at_least': 0.8,
    'neither_clean_nor_defect': ['cannot tell', 'no bridge required'],
}


def ranking(question: str, ref: str) -> str:
    """The entry's order: SHA-256, in lower-case hexadecimal, of `jev-calibration <Pnn> <ref>`."""
    return hashlib.sha256(f'jev-calibration {question} {ref}'.encode('utf-8')).hexdigest()


# The kinds' tests, each code on the generated row: None when the kind applies, or why not.
OUTSIDE_QUOTES = re.compile(r'"[^"]*"')
COMPARISON = re.compile(r'\b(?:greater|less|equal|unequal|double|half)\b')
REFERENCE = re.compile(r'\b(?:XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\.\d+\b')
COVERS = re.compile(r'\b(?:statement|theorem|companion)s?\b')
FORM = re.compile(r'\b(?:reductio|contradiction|contrary|impossib\w*|absurd\w*|indirect(?:ly)?'
                  r'|direct(?:ly)?|suppos\w*)\b')
OPENERS, CLOSERS = '([{⟨⦃', ')]}⟩⦄'


def top_level(text: str):
    """Each character of `text` outside every bracket, with its place."""
    depth = 0
    for i, c in enumerate(text):
        if c in OPENERS:
            depth += 1
        elif c in CLOSERS:
            depth -= 1
        elif depth == 0:
            yield i, c


def clauses(statement: str) -> int:
    """How many clauses a statement's conclusion has: its conjuncts outside every bracket,
    after a leading run of `∀ …,` and `∃ …,` binders. An implication, an alternative or a
    binder among them makes the conclusion one clause."""
    colon = next((i for i, c in top_level(statement)
                  if c == ':' and not statement.startswith(':=', i)), None)
    require(colon is not None, 'a statement with no conclusion')
    text = statement[colon + 1:]
    while re.match(r'\s*[∀∃]', text):
        comma = next((i for i, c in top_level(text) if c == ','), None)
        if comma is None:
            return 1
        text = text[comma + 1:]
    found = [c for _, c in top_level(text)]
    if any(c in '→↔∨,' for c in found):
        return 1
    return found.count('∧') + 1


def body_calls_a_proposition(calibration: 'Calibration', row: dict) -> str | None:
    name = heath.parse_ref(row['ref']).lean
    calls = [c for c in calibration.generator.calls.direct(name)
             if c['position'] == 'proof' and c['name'] in calibration.generator.calls.by_name]
    return None if calls else "the unit's body calls no proposition"


def outside_quotes(text: str) -> str:
    """The commentary with every quotation blanked, its other characters where they stand."""
    return OUTSIDE_QUOTES.sub(lambda found: ' ' * len(found.group()), text)


def commentary_test(pattern: re.Pattern, what: str):
    def test(calibration: 'Calibration', row: dict) -> str | None:
        found = [m for m in pattern.findall(outside_quotes(row['state']['commentary']))
                 if m != row['ref']]
        return None if found else f'the commentary names {what} only within quotation marks, or not at all'
    return test


def names_a_declaration(calibration: 'Calibration', row: dict) -> str | None:
    """Kind 4's test: a declaration of the row's `named_declarations` named in the commentary
    outside quotation marks, as the row's own reading of the commentary resolves it."""
    consumer = calibration.index.get(heath.parse_ref(row['ref']).lean)
    for token in re.findall(r'`([^`]+)`', outside_quotes(row['state']['commentary'])):
        if (re.fullmatch(NAME, token) and calibration.index.resolve(token, consumer, commentary=True)
                in row['state']['named_declarations']):
            return None
    return 'the commentary names no declaration of the row outside quotation marks'


@dataclass(frozen=True)
class Kind:
    name: str
    expected: str
    test: Any = None


def bridges_at_least(count: int):
    def test(calibration: 'Calibration', row: dict) -> str | None:
        n = len(row['state']['bridges'])
        return None if n >= count else f'the row supplies {n} bridges'
    return test


KINDS = {
    'P11': (
        Kind("a hypothesis added that leaves out a configuration Euclid's words admit",
             'restricted beyond what the note says'),
        Kind('a clause of the conclusion removed', 'restricted beyond what the note says',
             lambda c, row: None if clauses(row['state']['lean_statement']) >= 2
             else 'the main conclusion has one clause'),
        Kind('a porism or companion removed whose clause the main statement does not carry',
             'restricted beyond what the note says',
             lambda c, row: None if row['state']['attached_statements']
             else 'the row has no attached statement'),
        Kind('an object Euclid leaves general fixed or narrowed', 'restricted beyond what the note says'),
    ),
    # The rulings drop the entry's fourth kind, an existing hypothesis mentioned in a step that
    # does no work: such a hypothesis may do substantive work elsewhere in its proof.
    'P12': (
        Kind('a call of an unrelated proposition whose result is not used', 'a dummy citation'),
        Kind('a call whose result is bound while the step it is for is done another way',
             'a dummy citation', body_calls_a_proposition),
        Kind('a hypothesis added and used only in a binding nothing uses',
             'an artificial hypothesis use'),
    ),
    'P13': (
        Kind('every supplied bridge removed', 'bridge missing or inadequate', bridges_at_least(1)),
        Kind('an impossible premise added to each bridge', 'bridge missing or inadequate',
             bridges_at_least(1)),
        Kind("a bridge's conclusion changed so that it no longer connects the represented object "
             "with Euclid's", 'bridge missing or inadequate', bridges_at_least(1)),
        Kind('a premise added that the represented objects cannot meet', 'bridge missing or inadequate',
             bridges_at_least(1)),
        Kind('the one bridge that a needed connection rests on removed, the others kept',
             'bridge missing or inadequate', bridges_at_least(2)),
    ),
    'P14': (
        Kind('a comparison in the commentary reversed', 'conflicts',
             commentary_test(COMPARISON, 'a comparison of magnitudes')),
        Kind('the proposition that a step of the route cites changed to another', 'conflicts',
             commentary_test(REFERENCE, 'another proposition')),
        Kind('the scope misstated, as a case said to be covered that the statement leaves out',
             'conflicts', commentary_test(COVERS, 'what the statement covers')),
        Kind("a named declaration's hypotheses or conclusion misstated", 'conflicts',
             names_a_declaration),
        Kind('the kind of route misstated, as direct for a reductio', 'conflicts',
             commentary_test(FORM, 'the form of the proof')),
    ),
    'P15': (
        Kind("another proposition's figure sent", 'disagrees'),
        Kind('two letters of the figure exchanged', 'disagrees'),
        Kind("a caption's claim made false of the figure", 'disagrees',
             lambda c, row: None if row['state']['caption'] else 'the caption is empty'),
        Kind('a point moved so that an incidence or an order the proof needs fails', 'disagrees'),
    ),
}
for _name, _kinds in KINDS.items():
    require(all(k.expected in QUESTIONS[_name].defects for k in _kinds),
            f'{_name}: a kind expects an answer that is not a defect answer')
# The kinds that do not apply to a plant's base although their tests pass, by
# docs/decisions/2026-10-26-jev-kind-not-applying.md (the kind ruling): a kind that cannot make
# a genuine fault on its base. Each is passed over before its test, with the reason given here.
# II.8's and III.36's rows supply the same five bridges, of Elements/BookII/Rectangles.lean.
OVERLAPPING_BRIDGES = ('no single supplied bridge carries a needed connection alone: '
                       '`Rectangle.eq_rect` and `Rectangle.contained` each give `rect`, and '
                       '`Square.eq_sq` and `Square.described` each give `sq`')
NOT_APPLYING = {
    ('P13', 'II.8', 5): OVERLAPPING_BRIDGES,
    ('P13', 'III.36', 5): OVERLAPPING_BRIDGES,
}


def check_not_applying() -> None:
    """Each entry of the kind ruling's table names a plant of its question's lists and a kind
    of that question, so that no entry stands for a base or a kind the calibration lacks."""
    for (question, ref, kind), reason in NOT_APPLYING.items():
        plants = {r for _, listed in CALIBRATION_LISTS.get(question, {}).values() for r in listed.split()}
        require(ref in plants and type(kind) is int and 1 <= kind <= len(KINDS[question])
                and isinstance(reason, str) and reason,
                f'{question} {ref}, kind {kind}: the table of {KIND_RULING} names no plant of '
                f"{question}'s lists, or no kind of {question}, or no reason; nothing is written")


@dataclass(frozen=True)
class Plant:
    """One plant: the kind the rule gives it, what is changed, and why its answer is the
    defect answer. The operations are written here, and reviewed with the generator:
    ('replace', field, old, new), each `old` occurring once; ('cite', ref), the evidence for
    a proposition call added; ('remove', names), bridges removed with their context, every
    bridge when names is None; ('premise', names, text), a premise added after each named
    bridge's name, every bridge's when None; ('asset', path), another committed figure sent;
    ('figure', name, [(old, new), ...]), a copy of the row's figure changed so."""
    kind: int
    what: str
    justification: str
    operations: tuple


FIGURE_SWAP = '\x00'


def swap(a: str, b: str) -> list[tuple[str, str]]:
    """The edits that exchange two letters of a figure, each label `<text …>X</text>`."""
    return [(f'>{a}</text>', f'>{FIGURE_SWAP}</text>'), (f'>{b}</text>', f'>{a}</text>'),
            (f'>{FIGURE_SWAP}</text>', f'>{b}</text>')]


AREA_PREMISE_NAME = 'h₀'
PLANTS = {
    # P11: each expects "restricted beyond what the note says".
    ('P11', 'I.8'): Plant(
        1, 'the hypothesis (hBAC : ∠ B A C = ∟) added to the main statement',
        "Euclid's I.8 takes any two triangles with three sides equal; the added hypothesis leaves "
        'out every triangle whose angle at A is not right. The record says the scope is full and '
        'names no restriction, so the statements are restricted beyond what the note says.',
        (('replace', ['state', 'lean_statement'], '(hBC : ‖B C‖ = ‖E F‖) :',
          '(hBC : ‖B C‖ = ‖E F‖) (hBAC : ∠ B A C = ∟) :'),)),
    ('P11', 'I.19'): Plant(
        4, 'the triangle narrowed from `Triangle A B C` to `RightAngledTriangle A B C`',
        'I.19 speaks of "any triangle"; the statement now takes only a triangle right-angled at A, '
        'so every other triangle is left out, a restriction the full-scope record does not name.',
        (('replace', ['state', 'lean_statement'], '(hABC : Triangle A B C)',
          '(hABC : RightAngledTriangle A B C)'),)),
    ('P11', 'I.29'): Plant(
        4, 'the transversal narrowed to one at right angles to AB: (hEGH : Between E G H ∧ ∠ E G B = ∟)',
        'I.29 takes any straight line falling on the parallels; the statement now takes only one '
        'falling at right angles, leaving out every oblique transversal, which the full-scope '
        'record does not name.',
        (('replace', ['state', 'lean_statement'], '(hEGH : Between E G H)',
          '(hEGH : Between E G H ∧ ∠ E G B = ∟)'),)),
    ('P11', 'I.9'): Plant(
        4, 'the given angle narrowed from `Triangle B A C` to `RightAngledTriangle A B C`',
        'I.9 bisects any given rectilineal angle; the statement now bisects only a right angle at '
        'A, leaving out every other angle, a restriction the record\'s note does not name.',
        (('replace', ['state', 'lean_statement'], '(hBAC : Triangle B A C)',
          '(hBAC : RightAngledTriangle A B C)'),)),
    ('P11', 'II.9'): Plant(
        1, 'the hypothesis (hCD : ‖C D‖ = ‖D B‖) added to the main statement',
        "II.9's straight line is cut into unequal segments at any D; the added hypothesis puts D "
        'at the middle of CB, leaving out every other point of section, which the note, D "on '
        'either side of C", does not name.',
        (('replace', ['state', 'lean_statement'], '(hDC : D ≠ C) :',
          '(hDC : D ≠ C) (hCD : ‖C D‖ = ‖D B‖) :'),)),
    ('P11', 'II.8'): Plant(
        4, 'the point of section narrowed to the middle: (hACB : Between A C B ∧ ‖A C‖ = ‖C B‖)',
        'II.8 cuts the straight line at random; the statement now cuts it only at its middle, '
        'leaving out every other point of section, which the record does not name.',
        (('replace', ['state', 'lean_statement'], '(hACB : Between A C B)',
          '(hACB : Between A C B ∧ ‖A C‖ = ‖C B‖)'),)),
    ('P11', 'III.37'): Plant(
        4, 'the cutting straight line narrowed to one through the centre',
        "III.37's straight line DCA cuts the circle anywhere; the statement now takes only one "
        'through the centre, leaving out every other, which the full-scope record does not name.',
        (('replace', ['state', 'lean_statement'], '(hDCA : Between D C A)',
          '(hDCA : Between D C A ∧ ∃ E : Point, Centre E ABC ∧ Between C E A)'),)),
    ('P11', 'III.11'): Plant(
        4, 'the inner circle narrowed to one through the centre F of the outer',
        'III.11 takes any two circles touching internally; the statement now takes only an inner '
        'circle passing through the centre of the outer, leaving out every other size, which the '
        'record does not name.',
        (('replace', ['state', 'lean_statement'], '(hG : Centre G ADE)',
          '(hG : Centre G ADE ∧ OnCircle F ADE)'),)),
    ('P11', 'III.36'): Plant(
        1, 'the hypothesis (hE : ∃ E : Point, Centre E ABC ∧ Between C E A) added',
        "III.36 takes DCA through the centre or not, and the record's note says the statement "
        'covers both; the added hypothesis leaves out every DCA not through the centre.',
        (('replace', ['state', 'lean_statement'], '(hDB : Touches D B ABC) :',
          '(hDB : Touches D B ABC) (hE : ∃ E : Point, Centre E ABC ∧ Between C E A) :'),)),
    ('P11', 'III.28'): Plant(
        2, "the second clause of the conclusion removed, the remaining circumferences' equality",
        'III.28 concludes that the greater circumferences are equal and the less too; the '
        'statement now concludes the greater only, so a clause of the enunciation has no formal '
        'conclusion, and no attached statement carries it; the full-scope record names no omission.',
        (('replace', ['state', 'lean_statement'],
          ' ∧\n      (circumference ABC A G B = circumference DEF D H E ∧\n'
          '        Arc.Congruent ⟨ABC, A, B, G⟩ ⟨DEF, D, E, H⟩)', ''),)),
    # P12.
    ('P12', 'I.21'): Plant(
        1, 'a call of I.15, `have h15 := @Prop15`, whose result nothing uses',
        "I.15, on vertical angles, has no part in I.21's argument, and its result h15 is never "
        'used: a call that only supplies a citation, a dummy citation.',
        (('replace', ['state', 'lean_proof'], '  obtain ⟨E, hBDE, hAEC⟩ := Prop21.through hD\n',
          '  obtain ⟨E, hBDE, hAEC⟩ := Prop21.through hD\n  have h15 := @Prop15\n'),
         ('cite', 'I.15'))),
    ('P12', 'I.45'): Plant(
        2, 'a call of I.30 for KF parallel to ML, `have h30 := @Prop30 K F M L G D`, bound and unused',
        'The step "KF is also ... parallel to ML [I. 30]" is done by `Prop30.parallel` on the '
        'straight lines; the added call of I.30 for those points is bound to h30 and never used, '
        'so it supplies a citation while the step is done another way: a dummy citation.',
        (('replace', ['state', 'lean_proof'], '  have hpar : AreParallel K F M L :=\n',
          '  have h30 := @Prop30 K F M L G D\n  have hpar : AreParallel K F M L :=\n'),)),
    ('P12', 'I.15'): Plant(
        3, 'the hypothesis (hAB : A ≠ B) added, used only in `have hB_A : B ≠ A := hAB.symm`',
        'The added hypothesis does no work: it is used only to make hB_A, which nothing uses, so '
        'it is mentioned only so that it looks used: an artificial hypothesis use.',
        (('replace', ['state', 'lean_proof'], '(hC : ¬ Collinear A B C) :',
          '(hC : ¬ Collinear A B C) (hAB : A ≠ B) :'),
         ('replace', ['state', 'lean_proof'],
          '  have hD_E : D ≠ E := ne_of_between (between_symm hCED)\n',
          '  have hD_E : D ≠ E := ne_of_between (between_symm hCED)\n  have hB_A : B ≠ A := hAB.symm\n'))),
    ('P12', 'I.40'): Plant(
        1, 'a call of I.15, `have h15 := @Prop15`, whose result nothing uses',
        "I.15, on vertical angles, has no part in I.40's argument, and its result h15 is never "
        'used: a call that only supplies a citation, a dummy citation.',
        (('replace', ['state', 'lean_proof'], '  have hBE : B ≠ E := ne_of_between_ends hBCE\n',
          '  have hBE : B ≠ E := ne_of_between_ends hBCE\n  have h15 := @Prop15\n'),
         ('cite', 'I.15'))),
    ('P12', 'II.5'): Plant(
        2, 'a call of I.34 on the parallelogram AH, `have h34 := BookI.Prop34 hDAKH`, bound and unused',
        'The step "AH is the rectangle AD, DB, for DH is equal to DB" is done by '
        '`Rectangle.of_right` and `eq_rect`, from the right angle HDA and DH equal to DB; the '
        "added call of I.34 on AH's sides and angles is bound to h34 and never used, so it "
        'supplies a citation while the step is done another way: a dummy citation.',
        (('replace', ['state', 'lean_proof'], '    have hAHrect : quadArea D A K H = rect A D D B :=\n',
          '    have h34 := BookI.Prop34 hDAKH\n    have hAHrect : quadArea D A K H = rect A D D B :=\n'),)),
    ('P12', 'II.7'): Plant(
        3, 'the hypothesis (hAC : A ≠ C) added, used only in `have hC_A : C ≠ A := hAC.symm`',
        'The added hypothesis does no work: it is used only to make hC_A, which nothing uses, so '
        'it is mentioned only so that it looks used: an artificial hypothesis use.',
        (('replace', ['state', 'lean_proof'], '(hACB : Between A C B) :',
          '(hACB : Between A C B) (hAC : A ≠ C) :'),
         ('replace', ['state', 'lean_proof'], '  have hAB : A ≠ B := ne_of_between_ends hACB\n',
          '  have hAB : A ≠ B := ne_of_between_ends hACB\n  have hC_A : C ≠ A := hAC.symm\n'))),
    ('P12', 'III.37'): Plant(
        1, 'a call of I.15, `have h15 := @BookI.Prop15`, whose result nothing uses',
        "I.15, on vertical angles, has no part in III.37's argument, and its result h15 is never "
        'used: a dummy citation.',
        (('replace', ['state', 'lean_proof'], '  -- I say that DB touches the circle ABC.\n',
          '  -- I say that DB touches the circle ABC.\n  have h15 := @BookI.Prop15\n'),
         ('cite', 'I.15'))),
    ('P12', 'III.31'): Plant(
        2, "a call of I.32 on the triangle ABC, with BA produced to F, `have h32' := @BookI.Prop32 C B "
        "A F`, bound and unused",
        'The step "the angle ABC is less than a right angle" is done by I.17 (`BookI.Prop17`), the '
        'angles ABC, BAC being less than two right angles and BAC right; the added call of I.32, '
        'which makes the three angles of the triangle ABC equal to two right angles and could give '
        "the step too, is bound to h32' and never used, so it supplies a citation while the step "
        'is done another way: a dummy citation.',
        (('replace', ['state', 'lean_proof'], '  -- the angle ABC is less than a right angle;\n',
          "  -- the angle ABC is less than a right angle;\n  have h32' := @BookI.Prop32 C B A F\n"),)),
    ('P12', 'III.24'): Plant(
        3, 'the hypothesis (hB_E : B ≠ E) added, used only in `have hE_B : E ≠ B := hB_E.symm`',
        'The added hypothesis does no work: it is used only to make hE_B, which nothing uses, so '
        'it is mentioned only so that it looks used: an artificial hypothesis use.',
        (('replace', ['state', 'lean_proof'], '(hsim : ∠ A E B = ∠ C F D) :',
          '(hsim : ∠ A E B = ∠ C F D) (hB_E : B ≠ E) :'),
         ('replace', ['state', 'lean_proof'],
          '  have hC_D : C ≠ D := (show Triangle C D F from hF_CD).ne₁₂\n',
          '  have hC_D : C ≠ D := (show Triangle C D F from hF_CD).ne₁₂\n  have hE_B : E ≠ B := hB_E.symm\n'))),
    ('P12', 'III.36'): Plant(
        1, 'a call of I.15, `have h15 := @BookI.Prop15`, whose result nothing uses',
        "I.15, on vertical angles, has no part in III.36's argument, and its result h15 is never "
        'used: a dummy citation.',
        (('replace', ['state', 'lean_proof'], "  have hDB' : D ≠ B := fun e => hD.2 (e ▸ hB)\n",
          "  have hDB' : D ≠ B := fun e => hD.2 (e ▸ hB)\n  have h15 := @BookI.Prop15\n"),
         ('cite', 'I.15'))),
    # P13: each expects "bridge missing or inadequate".
    ('P13', 'I.37'): Plant(
        1, 'every supplied bridge removed', 'With no bridge supplied, nothing states that '
        "`quadArea`, measured by one diameter, is the parallelogram's area whichever diameter cuts "
        'it, or that the diameter halves it: a needed connection has no declaration.',
        (('remove', None),)),
    ('P13', 'I.46'): Plant(
        2, f'the premise ({AREA_PREMISE_NAME} : False) added to each bridge',
        'Each bridge now needs a proof of False, so none can be used of any parallelogram or '
        'square: every connection is unavailable for the represented objects.',
        (('premise', None, f'({AREA_PREMISE_NAME} : False)'),)),
    ('P13', 'I.43'): Plant(
        3, "`Parallelogram.quadArea_rotate`'s and `Parallelogram.outline_area`'s conclusions made "
        '`quadArea A B C D = quadArea A B C D`',
        "`quadArea` measures a parallelogram by the diameter AC; the bridge that said the other "
        'diameter gives the same area, and the one that said the measure is the area of the '
        'parallelogram given by its outline, now conclude a triviality, so nothing states that the '
        "measure is the parallelogram's area whichever diameter is drawn.",
        (('replace', ['state', 'bridges', 'Elements.Parallelogram.quadArea_rotate'],
          'quadArea B C D A = quadArea A B C D', 'quadArea A B C D = quadArea A B C D'),
         ('replace', ['state', 'bridges', 'Elements.Parallelogram.outline_area'],
          '(singleOutline [A, B, C, D] (convex_loop_region h.convexOutline).1).area =',
          'quadArea A B C D ='))),
    ('P13', 'I.36'): Plant(
        4, '`Parallelogram.quadArea_rotate` and `Parallelogram.outline_area` given the premise '
        '(hAC : A = C)',
        "A parallelogram's opposite corners are distinct, so no parallelogram meets the premise; "
        'the bridge that the measure is the same whichever diameter is drawn, and the one that it '
        'is the area of the parallelogram given by its outline, are unavailable for every '
        'parallelogram.',
        # `quadArea_rotate` takes its corners from the file's variables; `outline_area` binds
        # them itself, so its premise follows its binders, where A and C are its corners.
        (('premise', ['Elements.Parallelogram.quadArea_rotate'], '(hAC : A = C)'),
         ('replace', ['state', 'bridges', 'Elements.Parallelogram.outline_area'],
          '(h : Parallelogram A B C D) :', '(h : Parallelogram A B C D) (hAC : A = C) :'))),
    ('P13', 'II.8'): Plant(
        1, 'every supplied bridge removed', 'With no bridge supplied, nothing connects '
        "`rect A B B C`, `sq A C` and `sq A D` with Euclid's rectangle contained by AB, BC, his "
        'square on AC and the square AEFD that II.8 describes on AD by I.46. `rect A B B C` is an '
        'area that Lean chooses by `Classical.epsilon` among those AB, BC contain (`Contain`), and '
        '`sq A C` and `sq A D` are `rect A C A C` and `rect A D A D`; no supplied declaration now '
        'states that a rectangle whose sides about a right angle are equal to AB, BC, or a square '
        'on AC or on AD, is equal to the area chosen, and a choice definition alone does not prove '
        'that its choice represents a given object: a needed connection has no declaration.',
        (('remove', None),)),
    ('P13', 'II.6'): Plant(
        1, 'every supplied bridge removed', 'With no bridge supplied, nothing connects a drawn '
        'rectangle or square with `rect` or `sq`, which Lean chooses by `Classical.epsilon`: a '
        'choice definition alone does not prove that its choice represents a given object.',
        (('remove', None),)),
    ('P13', 'III.37'): Plant(
        2, f'the premise ({AREA_PREMISE_NAME} : False) added to each bridge',
        'Each bridge now needs a proof of False, so none can be used of any rectangle or square: '
        '`rect A D D C` and `sq D B`, which Lean chooses by `Classical.epsilon`, are connected '
        'with nothing drawn.',
        (('premise', None, f'({AREA_PREMISE_NAME} : False)'),)),
    ('P13', 'III.28'): Plant(
        3, "`Circumference.eq`'s conclusion made `circumference α B K C = circumference α B K C`",
        '`circumference` is a choice (`Classical.epsilon`), twice the angle at some point of the '
        'circle on the other side of BC; the one bridge that said it is twice the angle at every '
        'such point now concludes a triviality. `Circumference.centre` measures only a '
        'circumference beyond which the centre lies, which the greater circumferences ACB, DFE '
        'are not, and `Arc.measure_eq_iff` and `Arc.congruent_iff` say only when two measures '
        'are equal; so nothing but the choice says what the greater circumferences measure, and '
        'the comparisons that say which circumference of each circle is the greater are '
        "connected with nothing of Euclid's.",
        (('replace', ['state', 'bridges', 'Elements.BookIII.Circumference.eq'],
          'circumference α B K C = ∠ B A C + ∠ B A C', 'circumference α B K C = circumference α B K C'),)),
    ('P13', 'III.27'): Plant(
        4, '`Circumference.standing` given the premise (hBC : B = C)',
        'The arms of an angle BAC at the circumference meet the circle at two distinct points B '
        'and C, so no angle of III.27 meets the premise; the one bridge that says the '
        'circumference on which BAC stands is twice that angle is unavailable for every angle, '
        'and `standing`, a choice (`Classical.epsilon`), is connected with no angle that '
        "Euclid's circumferences stand under.",
        (('premise', ['Elements.BookIII.Circumference.standing'], '(hBC : B = C)'),)),
    ('P13', 'III.36'): Plant(
        1, 'every supplied bridge removed', 'With no bridge supplied, nothing connects '
        "`rect A D D C` and `sq D B` with Euclid's rectangle contained by AD, DC and his square on "
        'the tangent DB. `rect A D D C` is an area that Lean chooses by `Classical.epsilon` among '
        'those AD, DC contain (`Contain`), and `sq D B` is `rect D B D B`; no supplied declaration '
        'now states that a rectangle whose sides about a right angle are equal to AD, DC, or a '
        'square on DB, is equal to the area chosen, and a choice definition alone does not prove '
        'that its choice represents a given object: a needed connection has no declaration.',
        (('remove', None),)),
    # P14: each expects "conflicts".
    ('P14', 'I.47'): Plant(
        1, '"the angles at B and C are less than right" made "greater than right"',
        "In a triangle right-angled at A the angles at B and C are less than a right angle (I.17), "
        'as the proof uses for `Prop47.within`; the commentary now says greater.',
        (('replace', ['state', 'commentary'], 'the angles at B and C are less than right',
          'the angles at B and C are greater than right'),)),
    ('P14', 'I.38'): Plant(
        2, '"which I.36 now makes equal" made "which I.35 now makes equal"',
        "The parallelograms GBCA and DEFH stand on equal bases BC, EF, and the proof cites I.36 "
        '(`Prop36`); the commentary now cites I.35, on one base.',
        (('replace', ['state', 'commentary'], 'which I.36 now makes equal',
          'which I.35 now makes equal'),)),
    ('P14', 'I.13'): Plant(
        3, 'the sentence "Our statement covers A on the straight line CD too, where AB lies along '
        'CD." added after "his one argument serves again."',
        'The statement takes A off the straight line CD (`hA : ¬ Collinear C D A`), as Euclid\'s '
        'straight line set up on CD makes angles with it; the commentary now says that the '
        'statement covers A on CD too, a case the statement leaves out.',
        (('replace', ['state', 'commentary'], 'and his one argument serves again.',
          'and his one argument serves again. Our statement covers A on the straight line CD too, '
          'where AB lies along CD.'),)),
    ('P14', 'I.7'): Plant(
        4, '"where neither does, D lies within the triangle ABC" made "lies outside"',
        "`Prop7.cases` concludes, among its four places, that D lies within the triangle ABC; the "
        'commentary now says that where neither separation holds D lies outside it.',
        (('replace', ['state', 'commentary'], 'where neither does, D lies within the triangle ABC',
          'where neither does, D lies outside the triangle ABC'),)),
    ('P14', 'II.1'): Plant(
        1, '"or by straight lines equal to them" made "unequal to them"',
        '`Rectangle.eq_rect` makes a drawn rectangle the rectangle contained by straight lines '
        'equal to its sides; the commentary now says unequal.',
        (('replace', ['state', 'commentary'], 'or by straight lines equal to them',
          'or by straight lines unequal to them'),)),
    ('P14', 'II.10'): Plant(
        1, 'the sentence on FEB and CEF reversed: CE within the angle FEB, so FEB greater than CEF, '
        'the whole greater than the part, and with EFD more than two right angles',
        'EB falls within the angle CEF, so FEB is less than CEF, the part less than the whole '
        '(Common Notion 5), and FEB, EFD are less than two right angles, as Heath\'s proof says '
        'and Postulate 5 needs; the commentary now says, consistently with itself, that CE falls '
        'within FEB, FEB is greater than CEF and FEB, EFD make more than two right angles.',
        (('replace', ['state', 'commentary'],
          'EB falls within the angle CEF, so FEB is less than CEF, the part less than the whole '
          '(Common Notion 5), and with EFD it makes less than the two right angles of I.29.',
          'CE falls within the angle FEB, so FEB is greater than CEF, the whole greater than the part '
          '(Common Notion 5), and with EFD it makes more than the two right angles of I.29.'),)),
    ('P14', 'III.25'): Plant(
        2, '"(I.17)" for the angle ABD made "(I.5)"',
        'The proof cites I.17 (`BookI.Prop17`) for the angle ABD less than a right angle; the '
        'commentary now cites I.5, on isosceles triangles, which ABD need not be.',
        (('replace', ['state', 'commentary'], 'is less than a right angle (I.17)',
          'is less than a right angle (I.5)'),)),
    ('P14', 'III.20'): Plant(
        3, '"Our III.20 reaches Heron\'s case all the same." made "Our III.20 keeps E on A\'s side '
        'of BC, as Euclid does."',
        'The statement (`Prop20`) names no centre and no side for it: its angle at the centre, '
        '`angleAtCentre`, stands on the circumference BC away from A wherever the centre lies, two '
        'right angles or more when E is on BC or beyond it, as the record says; the commentary now '
        "says the statement keeps E on A's side of BC.",
        (('replace', ['state', 'commentary'], "Our III.20 reaches Heron's case all the same.",
          "Our III.20 keeps E on A's side of BC, as Euclid does."),)),
    ('P14', 'III.4'): Plant(
        4, '`onRay_of_angle_eq` said to hold whether the other arms lie on one side of FE or on '
        'opposite sides of it',
        "`onRay_of_angle_eq` needs P and F on the same side of DE (`SameSideOf P F D E`); the "
        'commentary now says that it puts equal angles\' other arms along one ray even when they '
        'lie on opposite sides, where the arms are mirror images and lie along two rays.',
        (('replace', ['state', 'commentary'],
          'for on one side of FE equal angles at E have their other arms along one ray',
          'for equal angles at E have their other arms along one ray, whether those arms lie on '
          'one side of FE or on opposite sides of it'),)),
    ('P14', 'III.14'): Plant(
        1, '"is greater by I.20" made "is less by I.20"',
        'A diameter, two radii together, is greater than a straight line not through the centre '
        "(I.20), as the record's route says; the commentary now says less.",
        (('replace', ['state', 'commentary'], 'is greater by I.20 than', 'is less by I.20 than'),)),
    # P15: each expects "disagrees".
    ('P15', 'I.22'): Plant(
        1, "I.15's figure sent for I.22",
        "I.15's figure, two straight lines crossing at E, has none of I.22's circles or its "
        'triangle FKG, so its letters and arrangement conflict with the proof.',
        (('asset', 'figures/I/15.svg'),)),
    ('P15', 'I.34'): Plant(
        2, 'the letters A and B exchanged',
        'With A and B exchanged, the drawn diameter joins A and C, not B and C, and ACDB taken in '
        'order crosses itself, where the proof has BC the diameter of the parallelogram ACDB.',
        (('figure', 'I-34.svg', swap('A', 'B')),)),
    ('P15', 'I.7'): Plant(
        3, 'the caption\'s "AD crossing CB" made "AC crossing DB"',
        'In the image AD crosses CB, and AC does not cross DB; the caption now claims the other '
        'case.',
        (('replace', ['state', 'caption'], 'AD crossing CB', 'AC crossing DB'),)),
    ('P15', 'I.13'): Plant(
        4, 'B moved along CD beyond D, to (400, 200), so that the order is C, D, B: the straight '
        'line CD drawn on through D to B; AB and BE drawn from B, with E above B, so that BE is '
        "still at right angles to CD; B's label and every mark at B drawn there: the arcs of the "
        'angles CBA and ABD, from the direction of C, now also that of D, to that of A, and the '
        "mark of the right angle EBD, between the directions of D and E; D's label set below D, "
        'off the line now drawn through it; and the figure widened from 400 to 440, a width some '
        "of the edition's figures have, to hold B",
        'The proof takes B on CD between C and D (Between C B D, the hypothesis hCBD), so that AB '
        'makes with CD the two adjacent angles CBA, ABD, and BE, at right angles to CD, stands '
        'between BC and BD. With B beyond D, BC and BD are one ray: the angles CBA, ABD are one '
        'angle, together less than two right angles; A falls within the angle DBE, so that the '
        'angle DBA is not the two angles DBE, EBA together; and C and D are not on opposite sides '
        'of BE. Only that order fails: C, D and B are on one straight line, A is off it and BE is '
        'at right angles to it.',
        (('figure', 'I-13.svg', [
            ('viewBox="0 0 400 250"', 'viewBox="0 0 440 250"'),
            ('width="400" height="250"', 'width="440" height="250"'),
            ('<path d="M 176 200 A 24 24 0 0 1 184.57 181.61"',
             '<path d="M 376 200 A 24 24 0 0 1 377.82 190.84"'),
            ('<path d="M 178.15 173.95 A 34 34 0 0 1 234 200"',
             '<path d="M 368.57 187.02 A 34 34 0 0 0 366 200"'),
            ('<polyline points="210,200 210,190 200,190"',
             '<polyline points="390,200 390,190 400,190"'),
            ('x1="50" y1="200" x2="350" y2="200"', 'x1="50" y1="200" x2="400" y2="200"'),
            ('x1="200" y1="200" x2="93.94"', 'x1="400" y1="200" x2="93.94"'),
            ('x1="200" y1="200" x2="200" y2="45"', 'x1="400" y1="200" x2="400" y2="45"'),
            ('<circle cx="200" cy="200" r="2.6"/>', '<circle cx="400" cy="200" r="2.6"/>'),
            ('<circle cx="200" cy="45" r="2.6"/>', '<circle cx="400" cy="45" r="2.6"/>'),
            ('<text x="194" y="224">B</text>', '<text x="394" y="224">B</text>'),
            ('<text x="357" y="206">D</text>', '<text x="344" y="224">D</text>'),
            ('<text x="194" y="35">E</text>', '<text x="394" y="35">E</text>')]),)),
    ('P15', 'II.5'): Plant(
        1, "I.1's figure sent for II.5",
        "I.1's figure, two circles and an equilateral triangle, has none of II.5's square, "
        'rectangles or gnomon, so it conflicts with the proof.',
        (('asset', 'figures/I/01.svg'),)),
    ('P15', 'II.10'): Plant(
        2, 'the letters B and C exchanged',
        'With B and C exchanged, the point marked C is not the middle of AB, CE no longer stands '
        'at C, and B falls between A and C, where the proof bisects AB at C and adds BD beyond B.',
        (('figure', 'II-10.svg', swap('B', 'C')),)),
    ('P15', 'III.1'): Plant(
        3, 'the caption\'s "AB not through F" made "AB through F"',
        'In the image the centre F is off the straight line AB; the caption now claims that AB '
        'passes through F.',
        (('replace', ['state', 'caption'], 'AB not through F', 'AB through F'),)),
    ('P15', 'III.22'): Plant(
        4, 'D moved within the circle, to (186, 236)',
        'ABCD is to be a quadrilateral in the circle, its corners on the circumference; with D '
        'moved within the circle, D is no longer on it.',
        (('figure', 'III-22.svg', [
            ('91.925,237.135 179.162,278.177"', '91.925,237.135 186,236"'),
            ('x2="179.162" y2="278.177"', 'x2="186" y2="236"'),
            ('<circle cx="179.162" cy="278.177" r="2.6"/>', '<circle cx="186" cy="236" r="2.6"/>'),
            ('<text x="173" y="302">D</text>', '<text x="170" y="258">D</text>')]),)),
    ('P15', 'III.19'): Plant(
        1, "III.35's figure sent for III.19",
        "III.35's figure, two straight lines cutting one another within a circle, has no "
        "straight line touching the circle and no right angle at C, so it conflicts with the proof.",
        (('asset', 'figures/III/35.svg'),)),
    ('P15', 'III.15'): Plant(
        2, 'the letters H and K exchanged',
        'With H and K exchanged, H is the foot on FG and K the foot on BC, where the proof draws '
        'EH perpendicular to BC and EK to FG, and the caption says EH is less than EK.',
        (('figure', 'III-15.svg', swap('H', 'K')),)),
}
# Words that would mark a change as planted, or a row as a calibration row, if a change
# brought them into what is sent.
SIGN_WORDS = re.compile(r'(?i)\b(?:seeded|plant(?:s|ed)?|controls?|calibration|mutation|'
                        r'impossible|unused|unrelated|dummy|artificial|fault|wrong|fake|bogus)\b')
ROLE_WORDS = re.compile(r'(?i)\b(?:seeded|plant(?:s|ed)?|calibration|mutation|controls?)\b')
LOCAL_LABELS = ('review', 'expected', 'why', 'source', 'mutation', 'calibration', 'seeded',
                'long_context', 'option_rotation', 'state_characters')


def figure_copies(directory: Path) -> list[Path]:
    """Where the plants' changed figures are written, in the plant table's order."""
    return [directory / CALIBRATION_FIGURES / op[1] for plant in PLANTS.values()
            for op in plant.operations if op[0] == 'figure']


def calibration_outputs(directory: Path) -> list[Path]:
    return ([directory / f'{CALIBRATION}-{question}.jsonl' for question in QUESTIONS]
            + [directory / f'{CALIBRATION}-manifest.json'] + figure_copies(directory))


DEFAULT_OUTPUTS = (OUTPUT, MANIFEST, *calibration_outputs(CALIBRATION_DIR))


def calibration_layout(directory: Path) -> tuple[Path, str]:
    """A calibration directory and its figure folder under the repository, outside figures/."""
    resolved = checked_path(directory)
    require(resolved.is_relative_to(ROOT),
            f'{resolved}: calibration output directory must be inside the repository so its '
            'figures have repository-relative asset paths')
    figure_root = checked_path(ROOT / 'figures')
    figure_identity = file_identity(figure_root)
    parents = (resolved, *resolved.parents)
    require(not resolved.is_relative_to(figure_root)
            and (figure_identity is None
                 or figure_identity not in {file_identity(parent) for parent in parents}),
            f'{resolved}: calibration output directory must not be figures/ or one of its descendants')
    figures = (resolved.relative_to(ROOT) / CALIBRATION_FIGURES).as_posix()
    return resolved, figures


class Calibration:
    """The calibration set of one commit, from the audit's own rows of it."""

    def __init__(self, generator: Generator, directory: Path | None = None):
        require(generator.books == BOOKS, 'the calibration takes all three books')
        self.generator = generator
        self.evidence = generator.evidence
        self.index = generator.index
        self.directory, self.figure_directory = calibration_layout(
            CALIBRATION_DIR if directory is None else directory)
        # A generator whose audit is done, as finish() leaves it, is read as it is.
        if not generator.rows:
            generator.audit()
        self.audit = {row['id']: row for row in generator.rows if not row['seeded']}
        self.figures: dict[str, dict] = {}

    def record(self, ref: str) -> dict:
        p = heath.parse_ref(ref)
        return tomllib.loads(self.evidence.read(f'review/{p.book}/{p.n:02d}.toml'))

    def lists(self, question: str) -> dict[str, tuple[list[dict], list[dict]]]:
        """The entry's hash rule, from the records at the commit; refused if it gives other
        lists than the entry's table, with P13's list for Book III as the rulings restate it."""
        spec = QUESTIONS[question]
        result = {}
        for book, controls in SPLIT:
            eligible = []
            for n in range(1, dict(BOOKS)[book] + 1):
                ref = f'{book}.{n}'
                record = self.record(ref)
                table, key = spec.verdict
                value = record['statement'][key] if table == 'statement' else \
                    record['review'].get('items', {}).get(key)
                if record['review']['stage'] == 'full' and value == spec.value:
                    eligible.append({'ref': ref, 'book': book, 'hash': ranking(question, ref)})
            eligible.sort(key=lambda entry: entry['hash'])
            for rank, entry in enumerate(eligible, 1):
                entry['rank'] = rank
            require(len(eligible) >= 2 * controls, f'{question} Book {book}: too few eligible records')
            result[book] = (eligible[:controls], eligible[controls:2 * controls])
            computed = (' '.join(e['ref'] for e in result[book][0]),
                        ' '.join(e['ref'] for e in result[book][1]))
            require(computed == CALIBRATION_LISTS[question][book],
                    f"{question} Book {book}: the records give {computed[0]}; then {computed[1]}, "
                    f"not {CALIBRATION_LISTS[question][book][0]}; then "
                    f"{CALIBRATION_LISTS[question][book][1]}, the list of {ENTRY} as {RULINGS} "
                    'restates the lists; nothing is written, and the work stops for a ruling')
        return result

    def base(self, question: str, ref: str) -> dict:
        spec = QUESTIONS[question]
        rid = f'{spec.item:02d}-{ref}-{spec.suffix}'
        require(rid in self.audit, f'{question}: no audit row {rid}')
        row = copy.deepcopy(self.audit[rid])
        # P12's controls and plants are each the main theorem's row.
        require(row['ref'] == ref and row['item'] == spec.item, f'{rid}: not the main row')
        require(row.get('expected') == spec.clean,
                f'{rid}: the record gives {row.get("expected")!r}, not the clean answer')
        return row

    def kind(self, question: str, k: int, row: dict) -> tuple[int, list[dict]]:
        """The kind the k-th plant takes, counting round from the first, and why each kind
        passed over did not apply: a kind the kind ruling's table names for the row's
        proposition is passed over before its test, with the table's reason and the ruling."""
        kinds = KINDS[question]
        passed = []
        for step in range(len(kinds)):
            index = (k + step) % len(kinds)
            ruled = NOT_APPLYING.get((question, row['ref'], index + 1))
            if ruled is not None:
                passed.append({'kind': index + 1, 'name': kinds[index].name, 'reason': ruled,
                               'ruling': KIND_RULING})
                continue
            reason = kinds[index].test(self, row) if kinds[index].test else None
            if reason is None:
                return index + 1, passed
            passed.append({'kind': index + 1, 'name': kinds[index].name, 'reason': reason})
        raise Refusal(f'{question} {row["ref"]}: no kind of {ENTRY}, as {RULINGS} gives the kinds, '
                      f'applies ({passed}); nothing is written. By {KIND_RULING} the next base by the '
                      'hash rule replaces this one, and that replacement is recorded, in a dated entry '
                      "and the generator's lists, before anything is sent")

    def change(self, row: dict, field: list[str], old: str, new: str) -> None:
        value = row
        for part in field[:-1]:
            value = value[part]
        text = value[field[-1]]
        require(isinstance(text, str), f'{row["id"]}: {field} is not text')
        require(text.count(old) == 1,
                f'{row["id"]}: plant anchor occurs {text.count(old)} times, not once: {old!r}')
        value[field[-1]] = text.replace(old, new)
        row['mutation']['changes'].append({'operation': 'replace', 'field': field, 'old': old, 'new': new,
                                           'before_sha256': sha(text),
                                           'after_sha256': sha(value[field[-1]])})

    def remove(self, row: dict, field: list[str]) -> None:
        value = row
        for part in field[:-1]:
            value = value[part]
        old = value.pop(field[-1])
        row['mutation']['changes'].append({'operation': 'remove', 'field': field, 'old': old,
                                           'before_sha256': sha(old if isinstance(old, str) else dumps(old))})

    def cite(self, row: dict, ref: str) -> None:
        """The evidence an added proposition call brings, as the audit's control of I.41 adds it."""
        state, source = row['state'], row['source']
        name = 'Elements.' + self.generator.facts[ref]['name']
        require(name not in state['helper_signatures'], f'{row["id"]}: {ref} is already called')
        state['helper_signatures'][name] = self.index.quote(source, 'helper_signatures.' + name, name)
        state['helper_signatures'] = dict(sorted(state['helper_signatures'].items()))
        state['cited'].update(self.generator.cited(source, [ref]))
        state['cited'] = dict(sorted(state['cited'].items(), key=lambda i: (heath.prop_key(i[0]), i[0])))
        state['declaration_context'].update(self.index.context(source, 'declaration_context', [name]))
        state['declaration_context'] = dict(sorted(state['declaration_context'].items()))
        for origin in ('certificate', 'source'):
            old = state['citation_origins'][origin]
            new = sorted([*old, ref], key=lambda r: (heath.prop_key(r), r))
            state['citation_origins'][origin] = new
            row['mutation']['changes'].append({'operation': 'replace', 'field': ['state', 'citation_origins', origin],
                                               'old': old, 'new': new, 'before_sha256': sha(dumps(old)),
                                               'after_sha256': sha(dumps(new))})
        row['mutation']['changes'].append({'operation': 'add evidence', 'ref': ref, 'declaration': name,
                                           'fields': ['helper_signatures', 'cited', 'declaration_context']})

    def figure(self, row: dict, name: str, edits: list[tuple[str, str]]) -> None:
        key = row['state']['figure']
        original = row['assets'][key]
        text = self.evidence.read(original)
        for old, new in edits:
            require(text.count(old) == 1, f'{row["id"]}: figure anchor occurs {text.count(old)} times: {old!r}')
            text = text.replace(old, new)
        require(FIGURE_SWAP not in text, f'{row["id"]}: an exchange left its placeholder')
        data = text.encode('utf-8')
        path = f'{self.figure_directory}/{name}'
        require(path not in self.figures, f'{path}: written twice')
        self.figures[path] = {'from': original, 'from_sha256': sha(self.evidence.read(original)),
                              'sha256': sha(data), 'text': text, 'bytes': data}
        row['assets'][key] = path
        row['mutation']['changes'].append({'operation': 'figure copy', 'field': ['assets', key],
                                           'old': original, 'new': path, 'edits': [list(e) for e in edits],
                                           'before_sha256': self.figures[path]['from_sha256'],
                                           'after_sha256': self.figures[path]['sha256']})

    def asset_bytes(self, path: str) -> bytes:
        return self.figures[path]['bytes'] if path in self.figures else self.evidence.read(path).encode('utf-8')

    def widen(self, row: dict, question: str) -> None:
        """Definitions for the names a plant brings in, added beside the row's own."""
        state, source = row['state'], row['source']
        p = heath.parse_ref(row['ref'])
        if question == 'P11':
            code = [state['lean_statement'], *state['attached_statements'].values(),
                    *state.get('bridges', {}).values()]
            fresh = glossary(self.index, source, code, self.generator.bundle(p.book, p.n)[0],
                             self.generator.registry)
        elif question == 'P12':
            fresh = glossary(self.index, source, [state['lean_proof'], *state['helper_signatures'].values()],
                             groups=self.generator.registry)
        else:
            return
        for key in ('definitions', 'notation', 'definition_context'):
            added = sorted(set(fresh[key]) - set(state[key]))
            if added:
                state[key] = dict(sorted({**state[key], **{k: fresh[key][k] for k in added}}.items()))
                row['mutation']['changes'].append({'operation': 'add evidence', 'field': ['state', key],
                                                   'names': added})

    def plant(self, question: str, k: int, entry: dict) -> tuple[dict, dict]:
        row = self.base(question, entry['ref'])
        before = copy.deepcopy(row)
        kind, passed = self.kind(question, k, row)
        spec = PLANTS.get((question, entry['ref']))
        require(spec is not None and spec.kind == kind,
                f'{question} {entry["ref"]}: the rule of {ENTRY}, with the kinds {RULINGS} gives, '
                f'gives kind {kind}, and the generator holds '
                f'{"no change" if spec is None else "a change of kind " + str(spec.kind)} for it')
        kind_spec = KINDS[question][kind - 1]
        row['seeded'] = True
        row['expected'] = kind_spec.expected
        row['why'] = (f'A planted fault of kind {kind}, {kind_spec.name}; the change, not the '
                      'record, determines the expectation, and the manifest gives the reason.')
        # The row's state before the change, whole, beside its hash; local, as `mutation` is.
        row['mutation'] = {'base_id': row['id'], 'base_state_sha256': sha(dumps(row['state'])),
                           'base_state': copy.deepcopy(row['state']),
                           'kind': kind, 'kind_name': kind_spec.name, 'what': spec.what, 'changes': []}
        inserted = []
        for op in spec.operations:
            if op[0] == 'replace' and question == 'P14':
                # P14 leaves quotation out, so its fault stands outside quotation marks.
                text = row['state']['commentary']
                at = text.find(op[2])
                require(op[1] == ['state', 'commentary'] and '"' not in op[3]
                        and outside_quotes(text)[at:at + len(op[2])] == op[2],
                        f'{row["id"]}: the change is not to the commentary outside quotation marks')
            if op[0] == 'replace':
                self.change(row, op[1], op[2], op[3])
                inserted.append(op[3])
            elif op[0] == 'cite':
                self.cite(row, op[1])
            elif op[0] == 'remove':
                names = list(row['state']['bridges']) if op[1] is None else op[1]
                for name in names:
                    require(name in row['state']['bridges'], f'{row["id"]}: no bridge {name}')
                    for table in ('bridges', 'bridge_context', 'bridge_placement'):
                        self.remove(row, ['state', table, name])
                kept = {self.index.get(name).path for name in row['state']['bridges']}
                for path in list(row['state']['bridge_imports']):
                    if path not in kept:
                        self.remove(row, ['state', 'bridge_imports', path])
            elif op[0] == 'premise':
                names = list(row['state']['bridges']) if op[1] is None else op[1]
                binder = LEAN_NAME.match(op[2][1:]).group()
                for name in names:
                    text = row['state']['bridges'][name]
                    require(not re.search(r'(?<![\w.])' + re.escape(binder) + r'(?![\w\'])', text),
                            f'{row["id"]}: {binder} is already a name in {name}')
                    d = self.index.get(name)
                    anchor = self.evidence.read(d.path)[d.keyword:d.name_end]
                    self.change(row, ['state', 'bridges', name], anchor, anchor + ' ' + op[2])
                inserted.append(op[2])
            elif op[0] == 'asset':
                key = row['state']['figure']
                old = row['assets'][key]
                self.evidence.read(op[1])
                row['assets'][key] = op[1]
                row['source']['sent_figure'] = op[1]
                row['mutation']['changes'].append({'operation': 'replace', 'field': ['assets', key],
                                                   'old': old, 'new': op[1],
                                                   'before_sha256': sha(self.evidence.read(old)),
                                                   'after_sha256': sha(self.evidence.read(op[1]))})
            elif op[0] == 'figure':
                self.figure(row, op[1], op[2])
                inserted.extend(new for _, new in op[2])
            else:
                raise Refusal(f'{row["id"]}: unknown plant operation {op[0]}')
        self.widen(row, question)
        for text in inserted:
            found = SIGN_WORDS.search(text)
            if found:
                raise Refusal(f'{row["id"]}: the change carries the sign {found.group()!r}')
        # The change is in what the row sends: its state, its question or its images.
        sent = lambda r: (dumps(r['state']), dumps(r['question']),
                          [sha(self.asset_bytes(p)) for p in r.get('assets', {}).values()])
        require(sent(row) != sent(before), f'{row["id"]}: the plant changes nothing that is sent')
        row['mutation']['state_sha256'] = sha(dumps(row['state']))
        row['calibration'] = {'question': question, 'role': 'plant', 'book': entry['book'],
                              'rank': entry['rank'], 'hash': entry['hash'], 'kind': kind}
        return row, {'ref': entry['ref'], 'book': entry['book'], 'rank': entry['rank'],
                     'hash': entry['hash'], 'id': row['id'], 'kind': kind, 'kind_name': kind_spec.name,
                     'passed_over': passed, 'expected': kind_spec.expected, 'what': spec.what,
                     'justification': spec.justification,
                     'state_sha256_before': row['mutation']['base_state_sha256'],
                     'state_sha256_after': row['mutation']['state_sha256'],
                     'state_before': row['mutation']['base_state'],
                     'changes': row['mutation']['changes'],
                     'assets_before': before.get('assets', {}), 'assets': row.get('assets', {})}

    def control(self, question: str, entry: dict) -> tuple[dict, dict]:
        row = self.base(question, entry['ref'])
        row['calibration'] = {'question': question, 'role': 'control', 'book': entry['book'],
                              'rank': entry['rank'], 'hash': entry['hash']}
        return row, {'ref': entry['ref'], 'book': entry['book'], 'rank': entry['rank'],
                     'hash': entry['hash'], 'id': row['id'], 'expected': row['expected'],
                     'state_sha256': sha(dumps(row['state']))}

    def finish(self) -> tuple[dict[str, bytes], dict]:
        check_not_applying()
        files: dict[str, bytes] = {}
        questions = {}
        for question, spec in QUESTIONS.items():
            lists = self.lists(question)
            rows, controls, plants = [], [], []
            for book, _ in SPLIT:
                for entry in lists[book][0]:
                    row, summary = self.control(question, entry)
                    rows.append(row)
                    controls.append(summary)
            k = 0
            for book, _ in SPLIT:
                for entry in lists[book][1]:
                    row, summary = self.plant(question, k, entry)
                    rows.append(row)
                    plants.append(summary)
                    k += 1
            # Every kind the kind ruling's table names for this question is one a plant passed
            # over by it, so that no entry sits unused.
            ruled = {(question, p['ref'], x['kind']) for p in plants for x in p['passed_over'] if 'ruling' in x}
            unused = sorted({key for key in NOT_APPLYING if key[0] == question} - ruled)
            require(not unused, f'{question}: the table of {KIND_RULING} names {unused}, which no plant '
                                'reaches; nothing is written')
            # The propositions in the order of the books, controls and plants together.
            rows.sort(key=lambda r: heath.prop_key(r['ref']))
            seen: set[str] = set()
            for row in rows:
                row['state_characters'] = len(dumps(row['state']))
                row['long_context'] = row['state_characters'] > LIMIT
                problems = jev.check_row(row, row['id'], seen)
                require(not problems, '\n'.join(problems))
                require(not any(key in row['state'] for key in LOCAL_LABELS),
                        f'{row["id"]}: local labels leaked into state')
                # What run sends: the state, the question, each image by its reference. An
                # image's local path is not sent.
                sent = dumps([row['state'], row['question'], sorted(row.get('assets', {}))])
                sent += ''.join(self.asset_bytes(p).decode('utf-8') for p in row.get('assets', {}).values())
                found = ROLE_WORDS.search(sent)
                if found:
                    raise Refusal(f'{row["id"]}: {found.group()!r} in what is sent')
                require(question != 'P13' or row['state']['bridges'] or row['seeded'],
                        f'{row["id"]}: a control supplies no bridge')
                for excerpt in row['source']['excerpts']:
                    raw = self.evidence.read(excerpt['path'])
                    require(sha(raw[excerpt['start']:excerpt['end']]) == excerpt['sha256'],
                            f'{row["id"]}: source slice changed')
                paths = {x['path'] for x in row['source']['excerpts']}
                paths |= {row['source'][key] for key in ('heath', 'lean', 'record', 'facts')}
                paths |= {p for p in row.get('assets', {}).values() if p not in self.figures}
                if 'page' in row['source']:
                    paths.add(row['source']['page'])
                files_ = {p: sha(self.evidence.read(p)) for p in sorted(paths)}
                files_.update({p: self.figures[p]['sha256'] for p in row.get('assets', {}).values()
                               if p in self.figures})
                row['source']['files'] = dict(sorted(files_.items()))
            require(len(rows) == 20 and sum(r['seeded'] for r in rows) == 10,
                    f'{question}: {len(rows)} rows, {sum(r["seeded"] for r in rows)} planted')
            require(not {c['ref'] for c in controls} & {p['ref'] for p in plants},
                    f'{question}: a proposition is both a control and a plant')
            data = jsonl(rows)
            name = f'{CALIBRATION}-{question}.jsonl'
            files[name] = data
            questions[question] = {'file': name, 'item': spec.item, 'clean': spec.clean,
                                   'defects': list(spec.defects), 'kinds': [k.name for k in KINDS[question]],
                                   'controls': controls, 'plants': plants}
        for path, figure in self.figures.items():
            files[f'{CALIBRATION_FIGURES}/{Path(path).name}'] = figure['bytes']
        self.evidence.unchanged()
        unresolved = sorted({token for names in self.generator.calls.unresolved.values() for token in names})
        require(not unresolved, f'unresolved names: {unresolved}')
        manifest = {
            'commit': self.evidence.commit, 'entry': ENTRY, 'rulings': RULINGS, 'bar': BAR,
            'calibration_directory': self.directory.relative_to(ROOT).as_posix(),
            'evidence_verification': 'all evidence bytes equal git show',
            'hash_rule': 'SHA-256, lower-case hexadecimal, of the UTF-8 text "jev-calibration <Pnn> <ref>" '
                         'with no line feed, least first, among the propositions whose record is at '
                         'stage full and gives the clean answer (P13: representations pass)',
            'option_rotation': "each row keeps its audit row's rotation of the options",
            'ids': "each row keeps its audit row's id; the role is the local field `calibration`",
            'asset_paths': 'paths in the repository; a changed figure is a copy under '
                           f'{self.figure_directory}/, never figures/. '
                           'The copies are not committed as files, since scripts/check_paths.py '
                           'admits no .svg under docs/: `figures` carries each copy\'s exact text, '
                           'and python3 scripts/audit/jev_questions.py --restore-figures with this '
                           'manifest writes the copies back to their paths before jev.py run',
            'limits': [
                'P13 asks what the bridges state, not where they stand in the order of dependencies.',
                'P14 leaves out quotation, attribution and voice.',
                'P15 looks at Heath\'s figure only.',
                'Every P11 answer, and every P13 answer on a record marked n/a, is adjudicated whatever '
                'the calibration shows.',
            ],
            'files': {name: {'sha256': sha(data), 'rows': data.count(b'\n')}
                      for name, data in files.items() if name.endswith('.jsonl')},
            'figures': {path: {k: v for k, v in figure.items() if k != 'bytes'}
                        for path, figure in self.figures.items()},
            'questions': questions,
            'evidence_files': {p: sha(raw) for p, raw in sorted(self.evidence.data.items())},
        }
        files[f'{CALIBRATION}-manifest.json'] = pretty(manifest)
        # The manifest alone holds the bytes sent: each copy's text, read back from the
        # manifest's own bytes, is the copy and hashes to its recorded hash.
        carried = json.loads(files[f'{CALIBRATION}-manifest.json'])['figures']
        for path, figure in self.figures.items():
            data = carried[path]['text'].encode('utf-8')
            require(data == figure['bytes'] and sha(data) == carried[path]['sha256'],
                    f'{path}: the manifest does not carry the copy exactly')
        for name, data in files.items():
            require('\u2014' not in data.decode('utf-8'), f'{name}: prohibited punctuation')
        return files, manifest


# A line of `jev.py run`'s output (cmd_run): the row's labels, what it records of the run, the
# request's fingerprint, its latency and status; then, for an answer, the answering model, the
# answer in each order, the usage and whether the first answer is the expected one, with
# `model_differs` where the model is not the one asked for; or, for a failed request, its
# error, with the body of the reply where there is one.
RUN_FIELDS = frozenset({*jev.LABELS, 'time', 'model_requested', 'order_check', 'input_sha256',
                        'input_rows', 'request_sha256', 'latency_s', 'status'})
ANSWER_FIELDS = frozenset({'model', 'choice', 'probabilities', 'confidence', 'reversed', 'usage',
                           'agrees'})
# What a reply of status 200 whose answer is malformed may leave on its line before the error.
PARTIAL_FIELDS = frozenset({'model', 'choice', 'probabilities', 'confidence'})
RUN_TIME = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
FINGERPRINT = re.compile(r'[0-9a-f]{64}')
SHAPE_ERROR = 'the answer is not the shape TypeSafe documents ('
# The width `jev.py run` renders an SVG at, unless --svg-width says otherwise; --tally builds
# each request again at it, unless its own --svg-width says otherwise.
SVG_WIDTH = 700


def valid_run_time(value: Any) -> bool:
    if not isinstance(value, str) or not RUN_TIME.fullmatch(value):
        return False
    try:
        dt.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return False
    return True


def calibration_file(path: Path) -> tuple[str, list[dict], bytes]:
    """A calibration question file, as --calibration writes it, of exactly its shape: 20 rows of
    one question, 10 controls and 10 plants, each proposition once, on the entry's lists, each
    with its id, its rank's hash and an expected answer of its role."""
    data = read_no_follow(checked_path(path))
    rows = jev.read_rows(path)
    calibration = [row.get('calibration') for row in rows]
    require(all(isinstance(c, dict) for c in calibration), f'{path.name}: not a calibration question file')
    questions = [c.get('question') for c in calibration]
    require(all(isinstance(question, str) for question in questions),
            f'{path.name}: every calibration.question must be text')
    names = set(questions)
    require(len(names) == 1 and next(iter(names)) in QUESTIONS,
            f'{path.name}: rows of no question, or of more than one')
    name = next(iter(names))
    spec = QUESTIONS[name]
    roles = [c.get('role') for c in calibration]
    refs = [row.get('ref') for row in rows]
    require(all(isinstance(ref, str) for ref in refs), f'{path.name}: every ref must be text')
    require(len(rows) == 20 and roles.count('control') == 10 and roles.count('plant') == 10,
            f'{path.name}: {len(rows)} rows, {roles.count("control")} controls and '
            f'{roles.count("plant")} plants, not the 20 rows, 10 and 10, the entry fixes')
    require(len(set(refs)) == len(refs), f'{path.name}: a proposition is in two rows')
    for book, _ in SPLIT:
        for role, listed in zip(('control', 'plant'), CALIBRATION_LISTS[name][book]):
            got = {ref for ref, r in zip(refs, roles) if r == role and heath.parse_ref(ref).book == book}
            require(got == set(listed.split()),
                    f'{path.name}: Book {book} {role}s {sorted(got)}, not {listed}, the list of '
                    f'{ENTRY} as {RULINGS} restates the lists')
    for row, role in zip(rows, roles):
        require(row['item'] == spec.item and row['id'] == f'{spec.item:02d}-{row["ref"]}-{spec.suffix}'
                and row.get('seeded') is (role == 'plant')
                and row['calibration'].get('hash') == ranking(name, row['ref'])
                and (row.get('expected') == spec.clean if role == 'control'
                     else row.get('expected') in spec.defects),
                f'{path.name}: {row["id"]} is not a {role} row of {name}')
    return name, rows, data


def fingerprints(rows: list[dict], svg_width: int):
    """The SHA-256 of the request `jev.py run` sends for a row, with the order check, by its own
    `build` and `encode`, its images read from the repository, an SVG rendered at svg_width."""
    cache: dict[tuple[str, str], str] = {}

    def fingerprint(row: dict, model: str) -> str:
        if (row['id'], model) not in cache:
            try:
                body, _ = jev.build(row, model, True, ROOT, svg_width)
            except jev.Failure as error:
                raise Refusal(f'{row["id"]}: its request cannot be built again to check its '
                              f'fingerprint ({error}); a changed figure is written back with '
                              '--restore-figures') from None
            cache[row['id'], model] = hashlib.sha256(jev.encode(body)).hexdigest()
        return cache[row['id'], model]
    return fingerprint


def result_line(line: Any, row: dict, where: str, made: dict, fingerprint) -> bool:
    """Check one line of the output against what `jev.py run` writes for this row of this
    input, and return whether it records an answer; a request that failed, with a status other
    than 200 or an error, records none."""
    require(isinstance(line, dict) and RUN_FIELDS <= line.keys(), f'{where}: not a line that jev.py run writes')
    for key in jev.LABELS:
        require(line[key] == row[key] and type(line[key]) is type(row[key]),
                f'{where}: its {key} is not the row\'s; not a line that jev.py run wrote of this input')
    require(line['input_sha256'] == made['input_sha256'] and line['input_rows'] == made['input_rows']
            and type(line['input_rows']) is int,
            f'{where}: written for another input (input_sha256 {line["input_sha256"]!r}, '
            f'input_rows {line["input_rows"]!r})')
    require(line['order_check'] is True, f'{where}: asked without the order check')
    status = line['status']
    latency = line['latency_s']
    require(valid_run_time(line['time'])
            and isinstance(line['model_requested'], str) and line['model_requested'].strip()
            and type(latency) is float and math.isfinite(latency) and latency >= 0
            and (status is None or type(status) is int and 100 <= status <= 599),
            f'{where}: its time, model asked for, latency or status is not as jev.py run writes it')
    require(isinstance(line['request_sha256'], str) and FINGERPRINT.fullmatch(line['request_sha256'])
            and line['request_sha256'] == fingerprint(row, line['model_requested']),
            f'{where}: its request_sha256 is not that of the request jev.py run builds for this row '
            f'of this input with {line["model_requested"]!r}')
    if line['status'] != 200 or 'error' in line:
        extra = set(line) - RUN_FIELDS - {'error', 'body'} - (PARTIAL_FIELDS if line['status'] == 200 else set())
        require(not extra, f'{where}: a failed request with {sorted(extra)}; not a line that jev.py run writes')
        require('error' in line, f'{where}: a failed request without an error; not a line that jev.py run writes')
        error = line['error']
        if status == 200:
            partial = set(line) & PARTIAL_FIELDS
            require(partial in (set(), {'model'}, set(PARTIAL_FIELDS)),
                    f'{where}: its partial answer fields are not a stage jev.py run writes')
            if partial == {'model'}:
                require(not jev._model_id(line['model']),
                        f'{where}: its partial answer is not as jev.py run writes it')
            elif partial:
                require(jev._model_id(line['model']),
                        f'{where}: its partial answer is not as jev.py run writes it')
                reply = {'answers': {'q': {key: line[key]
                                           for key in ('choice', 'probabilities', 'confidence')}}}
                try:
                    first = jev.answer_of(reply, 'q', row['question'])
                except (ValueError, KeyError, TypeError, AttributeError, ArithmeticError,
                        RecursionError):
                    raise Refusal(f'{where}: its partial answer is not as jev.py run writes it') from None
                require(first == {key: line[key] for key in first},
                        f'{where}: its partial answer is not as jev.py run writes it')
            written = isinstance(error, str) and error.startswith(SHAPE_ERROR) and 'body' in line
        elif status:
            written = error == f'HTTP {status}'
        else:
            written = isinstance(error, str) and bool(error.strip())
        require(written and isinstance(line.get('body', ''), str),
                f'{where}: its error is not one jev.py run writes')
        return False
    extra = set(line) - RUN_FIELDS - ANSWER_FIELDS - {'model_differs'}
    require(ANSWER_FIELDS <= line.keys() and not extra,
            f'{where}: an answer without {sorted(ANSWER_FIELDS - line.keys())} or with {sorted(extra)}; '
            'not a line that jev.py run writes')
    question = row['question']
    backwards = {**question, 'criteria': dict(reversed(list(question['criteria'].items())))}
    reversed_ = line['reversed']
    require(isinstance(reversed_, dict) and set(reversed_) == {'choice', 'probabilities', 'confidence',
                                                                 'consistent'},
            f'{where}: its reversed asking is not one jev.py run writes')
    reply = {'answers': {'q': {k: line[k] for k in ('choice', 'probabilities', 'confidence')},
                         'q' + jev.REVERSED: {k: reversed_[k] for k in ('choice', 'probabilities',
                                                                       'confidence')}}}
    try:
        first = jev.answer_of(reply, 'q', question)
        second = jev.answer_of(reply, 'q' + jev.REVERSED, backwards)
    except ValueError as error:
        raise Refusal(f'{where}: its answer is not one jev.py run accepts ({error})') from None
    require(jev._model_id(line['model']) and first == {k: line[k] for k in first}
            and second == {k: reversed_[k] for k in second}
            and reversed_['consistent'] is (second['choice'] == first['choice']),
            f'{where}: its answer is not as jev.py run writes it')
    require(line['agrees'] is (line['choice'] == row['expected']),
            f'{where}: its agrees is not whether its first answer is the expected one')
    require(('model_differs' in line) is (line['model'] != line['model_requested'])
            and line.get('model_differs', True) is True,
            f'{where}: its model_differs is not as jev.py run writes it')
    return True


def tally(questions: Path, results: Path, svg_width: int = SVG_WIDTH) -> int:
    """Judge one calibration file's run against the entry's bar; reads no key, sends nothing.
    The question file must be of the calibration's exact shape and every line of the output as
    `jev.py run` writes it for that file, its request's fingerprint among what is checked, with
    its figures rendered at svg_width, the --svg-width the run was given; the fourth condition
    is `jev.py score` itself."""
    name, rows, data = calibration_file(questions)
    spec = QUESTIONS[name]
    made = {'input_sha256': hashlib.sha256(data).hexdigest(), 'input_rows': len(rows)}
    fingerprint = fingerprints(rows, svg_width)
    by_id = {row['id']: row for row in rows}
    answers: dict[str, dict] = {}
    answered: set[str] = set()
    for n, text in enumerate(read_no_follow(checked_path(results)).decode('utf-8').splitlines(), 1):
        if not text.strip():
            continue
        where = f'{results.name}:{n}'
        try:
            line = json.loads(text, parse_constant=jev._no_constant)
        except ValueError:
            raise Refusal(f'{where}: not JSON') from None
        require(isinstance(line, dict) and isinstance(line.get('id'), str),
                f'{where}: not a line that jev.py run writes')
        require(line['id'] in by_id, f'{where}: {line["id"]!r} is no row of {questions.name}')
        require(line['id'] not in answers, f'{where}: {line["id"]} is answered twice')
        if result_line(line, by_id[line['id']], where, made, fingerprint):
            answered.add(line['id'])
        answers[line['id']] = line
    print(f'{name} calibration: {questions.name}, {len(rows)} rows, input sha256 {made["input_sha256"]}')
    print(f'results: {results.name}, {len(answers)} lines, each as jev.py run writes it for this '
          'input, its request fingerprint included')
    found = alarms = agree = 0
    defect = set(spec.defects).__contains__
    for row in rows:
        role, line = row['calibration']['role'], answers.get(row['id'])
        if line is None:
            verdict, first, second = 'unanswered', '-', '-'
        elif row['id'] not in answered:
            verdict = 'failed request: ' + str(line['error'])
            first = second = '-'
        else:
            a, b = line['choice'], line['reversed']['choice']
            first = f'{a} ({line["confidence"]})'
            second = f'{b} ({line["reversed"]["confidence"]})'
            agree += line['agrees']
            if role == 'plant':
                verdict = 'found' if defect(a) and defect(b) else 'missed'
                found += verdict == 'found'
            else:
                verdict = 'false alarm' if defect(a) or defect(b) else 'clear'
                alarms += verdict == 'false alarm'
        print(f'  {row["id"]}: {role}; expected {row["expected"]!r}; first {first}; '
              f'reversed {second}; {verdict}')
    failed = len(answers) - len(answered)
    lines = [answers[rid] for rid in answered]
    models = sorted({str(line['model']) for line in lines})
    # The fourth condition is the client's own: `jev.py score <output> --bar 0.8`.
    score_output = io.StringIO()
    with contextlib.redirect_stdout(score_output), contextlib.redirect_stderr(score_output):
        scored = jev.main(['score', str(results), '--bar', str(BAR['agreement_at_least'])])
    conditions = [
        (len(answered) == len(rows) and not failed
         and all(line['model'] == MODEL and line['model_requested'] == MODEL for line in lines),
         f'{len(answered)} of {len(rows)} rows answered; {failed} failed requests; '
         f'models {", ".join(models) or "none"}'),
        (found >= BAR['found_at_least'], f'{found} of 10 planted faults found in both orders '
                                         f'(at least {BAR["found_at_least"]})'),
        (alarms <= BAR['false_alarms_at_most'], f'{alarms} of 10 controls false alarms '
                                                f'(at most {BAR["false_alarms_at_most"]})'),
        (scored == 0, f'jev.py score {results.name} --bar {BAR["agreement_at_least"]} exits {scored}; '
                      f'{agree} of {len(rows)} first answers as expected '
                      f'(at least {BAR["agreement_at_least"]:.0%})'),
    ]
    for n, (held, text) in enumerate(conditions, 1):
        print(f'{n}. {text}: {"holds" if held else "fails"}')
    cleared = all(held for held, _ in conditions)
    print(f'{name} {"clears" if cleared else "is under"} its bar.')
    return 0 if cleared else 1


def file_identity(path: Path) -> tuple[int, int] | None:
    try:
        info = path.stat()
    except FileNotFoundError:
        return None
    return info.st_dev, info.st_ino


def protected_paths() -> set[Path]:
    """Read the protected tuples without importing or running the push script."""
    policy = 'scripts/safe_push.py'
    try:
        tree = ast.parse(read_no_follow(evidence_path(policy)), filename=policy)
    except SyntaxError as error:
        raise Refusal(f'{policy}: cannot parse protected path lists: {error}') from error
    values: dict[str, tuple[str, ...]] = {}
    names = {'PROTECTED', 'PROTECTED_JUDGED'}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names):
            value = ast.literal_eval(node.value)
            require(isinstance(value, tuple) and value and all(isinstance(p, str) for p in value),
                    f'{policy}: protected paths must be nonempty tuples of strings')
            values[node.targets[0].id] = value
        elif (isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name)
              and node.target.id == 'PROTECTED'):
            require(isinstance(node.op, ast.Add) and isinstance(node.value, ast.Name)
                    and node.value.id in values and 'PROTECTED' in values,
                    f'{policy}: unsupported protected path extension')
            values['PROTECTED'] += values[node.value.id]
    require(names <= values.keys() and set(values['PROTECTED_JUDGED']) <= set(values['PROTECTED']),
            f'{policy}: missing protected path lists or extension')
    # Standing ownership and source restrictions in AGENTS.md and docs/WORKFLOW.md,
    # section 4, beyond the push policy.
    declared = ('AGENTS.md', 'Elements/Foundations/', 'Elements/Companions.lean',
                'docs/briefs/0002-decisions.md', 'docs/decisions/', 'docs/PROGRAM.md',
                'docs/program.toml', 'facts.json', 'book/', 'CERTIFICATE.md', 'GRAPH.md',
                'README.md', 'heath/')
    roots = {ROOT / '.git'}
    for name in (*values['PROTECTED'], *declared,
                 'scripts/audit/jev_questions.py', 'scripts/heath.py', 'scripts/audit/jev.py'):
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts and path.parts,
                f'{policy}: invalid protected path {name!r}')
        roots.add(ROOT / path)
    for arguments in (['--absolute-git-dir'], ['--path-format=absolute', '--git-common-dir']):
        result = subprocess.run(['git', 'rev-parse', *arguments], cwd=ROOT,
                                capture_output=True, check=False)
        require(result.returncode == 0,
                'cannot locate Git metadata: ' + result.stderr.decode('utf-8', errors='replace').strip())
        path = Path(os.fsdecode(result.stdout).rstrip('\n'))
        require(path.is_absolute(), 'Git metadata path must be absolute')
        roots.add(path)
    return roots | {path.resolve() for path in roots}


def protected_identities(roots: set[Path]) -> set[tuple[int, int]]:
    """Include untracked descendants so a hard link outside a protected tree is refused."""
    identities = set()

    def failed(error: OSError) -> None:
        raise error

    for root in roots:
        if any(root != parent and root.is_relative_to(parent) for parent in roots):
            continue
        identities.add(file_identity(root))
        if not root.is_dir():
            continue
        for directory, dirs, files in os.walk(root, onerror=failed):
            identities.update(file_identity(Path(directory) / name) for name in dirs + files)
    return identities - {None}


def output_paths(paths: list[Path], evidence_files: dict[str, str]) -> list[Path]:
    """Validate every destination before reading or writing any one."""
    resolved = [checked_path(path) for path in paths]
    identities = [file_identity(path) for path in resolved]
    # Treat names differing only in case as a collision even before either file exists,
    # so the same invocation is safe on both case-sensitive and case-insensitive volumes.
    for i, right in enumerate(resolved):
        for j, left in enumerate(resolved[:i]):
            same_name = (left.name.casefold() == right.name.casefold()
                         and file_identity(left.parent) is not None
                         and file_identity(left.parent) == file_identity(right.parent))
            require(left != right and not same_name
                    and not (identities[i] is not None and identities[i] == identities[j]),
                    f'questions and manifest destinations must differ: {left}, {right}')
    evidence = {evidence_path(path) for path in evidence_files}
    evidence_ids = {file_identity(path) for path in evidence} - {None}
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=False)
    require(result.returncode == 0,
            'cannot list tracked files: ' + result.stderr.decode('utf-8', errors='replace').strip())
    tracked = {ROOT / os.fsdecode(name) for name in result.stdout.split(b'\0') if name}
    protected = {path.resolve() for path in tracked if path not in DEFAULT_OUTPUTS}
    protected_names = {path.as_posix().casefold() for path in protected}
    protected_ids = {file_identity(path) for path in protected} - {None}
    for path, identity in zip(resolved, identities):
        require(path not in evidence and identity not in evidence_ids,
                f'{path}: destination would replace an evidence file')
        require(path.as_posix().casefold() not in protected_names and identity not in protected_ids,
                f'{path}: destination would replace a tracked input')
    roots = protected_paths()
    root_names = {path.as_posix().casefold() for path in roots}
    protected_ids = protected_identities(roots)
    for path in resolved:
        require(not any(parent.as_posix().casefold() in root_names
                        or file_identity(parent) in protected_ids
                        for parent in (path, *path.parents)),
                f'{path}: destination would replace a protected path or Git metadata')
    return resolved


def write_output(path: Path, data: bytes) -> None:
    """Replace the destination itself, never the target of a final symlink."""
    checked_path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f'.{path.name}.', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        checked_path(path)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def calibrate(args: argparse.Namespace) -> int:
    """Write, or with --check compare, the calibration set: its five question files, its
    manifest and its changed figures, in --out, a directory (by default beside the audit).
    --check compares a changed figure only when it is present: the copies are not committed,
    and the manifest, compared always, carries their text."""
    directory, _ = calibration_layout(CALIBRATION_DIR if args.out is None else args.out)
    first = Calibration(Generator(args.commit), directory).finish()
    second = Calibration(Generator(args.commit), directory).finish()
    require(first[0] == second[0], 'two generations differ')
    files, manifest = first
    # The figures first, the manifest last.
    names = sorted(files, key=lambda name: (not name.startswith(CALIBRATION_FIGURES),
                                            name.endswith('manifest.json'), name))
    paths = output_paths([directory / name for name in names], manifest['evidence_files'])
    destinations = list(zip(paths, (files[name] for name in names)))
    copies = [p for p, name in zip(paths, names) if name.startswith(CALIBRATION_FIGURES + '/')]
    if args.check:
        compared = [(p, data) for p, data in destinations if p not in copies or os.path.lexists(p)]
        different = [str(p) for p, data in compared
                     if not checked_path(p).is_file() or read_no_follow(p) != data]
        require(not different, 'generated files differ: ' + ', '.join(different))
    else:
        figures = checked_path(directory / CALIBRATION_FIGURES)
        if not figures.is_dir():
            figures.mkdir()
        for path, data in destinations:
            write_output(path, data)
    print(('Checked' if args.check else 'Wrote') + f' the calibration set of {manifest["commit"]}; '
          'two generations identical.')
    for question, entry in manifest['questions'].items():
        kinds = ', '.join(f'{p["ref"]} {p["kind"]}' for p in entry['plants'])
        print(f'{question}: {manifest["files"][entry["file"]]["rows"]} rows; controls '
              f'{", ".join(c["ref"] for c in entry["controls"])}; plants and kinds {kinds}.')
    print(f'Changed figures: {len(manifest["figures"])}, carried in the manifest'
          + (f'; {sum(os.path.lexists(p) for p in copies)} present and compared' if args.check else
             '; the copies are not committed, and --restore-figures writes them back')
          + f'. Evidence: {manifest["evidence_verification"]}.')
    return 0


def restore_figures(path: Path) -> int:
    """Write the changed figures a committed calibration manifest carries to the paths it
    records, beside the calibration set, where `jev.py run` loads them. It reads no commit and
    no key, and sends nothing. Every copy is checked before any is written: its text must hash
    to its recorded hash, its path must be one of the calibration's figure paths, and a file
    already there must hold its bytes; an identical file is left as it is."""
    def unique(pairs: list[tuple[str, Any]]) -> dict:
        keys = [key for key, _ in pairs]
        require(len(keys) == len(set(keys)), f'{path.name}: a key is repeated')
        return dict(pairs)

    manifest = json.loads(read_no_follow(checked_path(path)).decode('utf-8'), object_pairs_hook=unique)
    figures = manifest.get('figures') if isinstance(manifest, dict) else None
    layout = manifest.get('calibration_directory') if isinstance(manifest, dict) else None
    require(isinstance(figures, dict) and figures and isinstance(manifest.get('evidence_files'), dict)
            and isinstance(layout, str),
            f'{path.name}: not a calibration manifest with figures')
    local = Path(layout)
    require(not local.is_absolute() and '..' not in local.parts and local.as_posix() == layout,
            f'{layout}: calibration directory is not a repository-relative asset path')
    directory, _ = calibration_layout(ROOT / local)
    allowed = {relative(p): p for p in figure_copies(directory)}
    copies = []
    for name, figure in figures.items():
        require(name in allowed, f"{name}: not one of the calibration's figure paths")
        require(isinstance(figure, dict) and isinstance(figure.get('text'), str)
                and isinstance(figure.get('sha256'), str), f'{name}: no text and hash recorded')
        data = figure['text'].encode('utf-8')
        require(sha(data) == figure['sha256'],
                f'{name}: its text hashes to {sha(data)}, not its recorded {figure["sha256"]}')
        copies.append((allowed[name], data))
    paths = output_paths([p for p, _ in copies], manifest['evidence_files'])
    destinations = list(zip(paths, (data for _, data in copies)))
    different = [str(p) for p, data in destinations
                 if os.path.lexists(p) and (not checked_path(p).is_file() or read_no_follow(p) != data)]
    require(not different, 'files already there differ, and are not replaced: ' + ', '.join(different))
    written = 0
    for destination, data in destinations:
        if not os.path.lexists(destination):
            checked_path(destination.parent).mkdir(parents=True, exist_ok=True)
            write_output(destination, data)
            written += 1
    print(f'Restored the changed figures of {path.name}: {written} written, '
          f'{len(destinations) - written} already there and identical; each hashes to its recorded hash.')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--commit', help='the full commit hash the evidence is read from')
    parser.add_argument('--out', type=Path,
                        help='the questions file; with --calibration, the directory for its files')
    parser.add_argument('--manifest', type=Path, help="the audit's manifest (default beside its default output)")
    parser.add_argument('--check', action='store_true',
                        help='regenerate twice and compare with the files on disk; write nothing')
    parser.add_argument('--calibration', action='store_true', help='the calibration set, not the audit')
    parser.add_argument('--tally', nargs=2, type=Path, metavar=('QUESTIONS', 'RESULTS'),
                        help="judge a calibration file's run against the bar; reads no key, sends nothing")
    parser.add_argument('--svg-width', type=int, metavar='PIXELS',
                        help=f'with --tally, the --svg-width the run was given, at which each request '
                             f'is built again (default {SVG_WIDTH}, as for jev.py run)')
    parser.add_argument('--restore-figures', type=Path, metavar='MANIFEST',
                        help='write the changed figures a calibration manifest carries to the paths '
                             'it records; reads no commit or key, sends nothing')
    args = parser.parse_args(argv)
    try:
        if args.restore_figures:
            require(not (args.commit or args.out or args.manifest or args.check or args.calibration
                         or args.tally or args.svg_width is not None),
                    '--restore-figures takes its manifest and nothing else')
            return restore_figures(args.restore_figures)
        if args.tally:
            require(not (args.commit or args.out or args.manifest or args.check or args.calibration),
                    '--tally takes its two files, and --svg-width, and nothing else')
            return tally(*args.tally, SVG_WIDTH if args.svg_width is None else args.svg_width)
        require(args.svg_width is None, '--svg-width is for --tally alone')
        require(args.commit, '--commit REV is required')
        if args.calibration:
            require(args.manifest is None, '--calibration writes its manifest beside its files in --out')
            return calibrate(args)
        first = Generator(args.commit).finish()
        second = Generator(args.commit).finish()
        require(first[:2] == second[:2], 'two generations differ')
        rows, manifest_bytes, manifest = first
        paths = output_paths([OUTPUT if args.out is None else args.out,
                              MANIFEST if args.manifest is None else args.manifest],
                             manifest['evidence_files'])
        destinations = list(zip(paths, (rows, manifest_bytes)))
        if args.check:
            different = [str(p) for p, data in destinations
                         if not checked_path(p).is_file() or read_no_follow(p) != data]
            require(not different, 'generated files differ: ' + ', '.join(different))
        else:
            for path, data in destinations:
                write_output(path, data)
        print(('Checked' if args.check else 'Wrote') + f' {manifest["rows"]} rows; two generations identical.')
        for item, count in manifest['rows_by_item'].items():
            print(f'Item {item}: {count["not_seeded"]} not seeded, {count["seeded"]} seeded.')
        for book, count in manifest.get('rows_by_book', {}).items():
            print(f'Book {book}: ' + ', '.join(f'item {item} {n}' for item, n in count.items()) + '.')
        print(f'Proof units: {manifest["proof_units"]}; long_context states: {manifest["long_context_states"]}.')
        print(f'Largest state: {manifest["largest_state"]["characters"]} characters, {manifest["largest_state"]["id"]}.')
        print(f'Unresolved names: {len(manifest["unresolved_names"])}. Evidence: '
              + manifest['evidence_verification'] + '.')
        return 0
    except (Refusal, jev.Failure, heath.ReviewError, OSError, ValueError, KeyError) as error:
        print(f'refused: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
