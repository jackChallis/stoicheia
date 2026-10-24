# Review records

Every proposition has a review record, `review/<book>/NN.toml` (`review/I/40.toml`,
`review/III/16.toml`). It says what the fidelity check cannot. The check makes sure the
Lean quotes Heath word for word; the record says whether the Lean statement means what
Euclid's enunciation means, and how each passage of his argument appears in the Lean.
The page shows it under the enunciation, before the reader meets the green check.

A record is tied to what its reviewer read by three hashes: one of the statements, one of
the Lean file, and one of the record's own text. When any of them changes, the record has
to be read again. Python reads the records with `tomllib` (Python 3.11 or later), and
`heath.load_review(book, n)` checks each against this page. The record's tags come from
[terms.toml](terms.toml).

Where to begin: with Heath's enunciation and the Lean statement, each read on its own,
before any commentary about how they agree. "None" is a perfectly good answer for an
exception, and most records are short.

## Two stages

- **`exceptions`** (brief 0005, stage 1). Every departure is declared: the statement's
  scope, the route, the representation, an overlap with an axiom, and every passage that
  the Lean does not plainly carry beneath it. Each run of `--` lines with no Lean under
  it must be declared as a passage, and a `/- … -/` remark ends a run: a remark may stand
  above a run's first sentence, between its last sentence and its Lean, or under the Lean,
  while one between two sentences that share one step of Lean leaves the first with none,
  so move the remark or declare that sentence (III.16 declares "But DA is equal to DH").
- **`full`** (stage 5). Every substantive passage is classified as well.

## The sections

`[statement]`, `[route]` and `[review]` are required; the others appear only when they
have something to say. Unknown sections and keys are faults, so a misspelling is caught.

### `[statement]`: what the theorem proves

| Key | Type | Required | Meaning |
|---|---|---|---|
| `scope` | `"full"`, `"restricted"` or `"partial"` | yes | How much of the enunciation the theorem proves, with the companions listed below. |
| `hypotheses` | list of strings | when restricted | Each extra hypothesis that excludes a case Euclid's words admit, in words, as [STYLE](../docs/STYLE.md), section 1, "Hypotheses in words", says. |
| `omitted` | list of strings | when partial | Each clause with no formal conclusion, quoted exactly from Heath's enunciation or porism. |
| `note` | string, one line, at most 160 characters | unless full | What the theorem proves, in plain words, shown in the page's field table. |
| `short` | string, one line, at most 70 characters, no full stop | unless full | The same in a few words, shown beside the badge: "bases that meet end to end". It follows a colon or a bracket, so it begins with a small letter. |
| `fingerprint` | `"sha256:"` and 16 hex digits | stamp | The statements this record reviewed (below). |
| `companions` | list of references | no | Companion theorems counted in the scope, as `"I.40 general"`. |

- **full**: every clause of the enunciation, and of the porism if there is one, for every
  configuration Euclid's words admit, in the meaning the representation gives them. A
  statement that leaves out one of Euclid's hypotheses, and so claims more, is still
  full (tag it `hypothesis-dropped`). So is a statement that takes one placing of the
  figure, when a proved equality carries it to every other: I.47's squares stand outward,
  as Euclid describes them, and squares on one straight line are equal whichever side
  they stand on (`Prop46.square_eq`). Cases a commentator adds beyond Euclid's words, as
  Proclus's for I.43, are commentary, not scope.
- **restricted**: every clause is proved, but only under extra hypotheses that exclude
  configurations Euclid's words admit. `hypotheses` lists them. Hypotheses that only name
  what his words already presuppose, as that a triangle's corners are not on one
  straight line, are not listed.
- **partial**: some clause has no formal conclusion. `omitted` quotes it, and the record
  needs a `[coverage]` clause map. A partial statement may have extra hypotheses too.

Items about the porism begin "Porism:". When `companions` are listed, `scope` describes
the main theorem together with them, and the note says which declaration covers what.

The **fingerprint** is `heath.review_fingerprint(facts, ref)`: a hash of the `statement`
that facts.json prints for the theorem, followed by those of everything attached to it,
its porism and then its companions ([Certificate/FIELDS.md](../Certificate/FIELDS.md)).
If it no longer matches, a statement changed after the review.

### `[route]`: whose argument the Lean follows

| Key | Type | Required | Meaning |
|---|---|---|---|
| `kind` | `"euclid"`, `"modified"` or `"alternative"` | yes | See below. |
| `note` | string | unless euclid | How the route differs from Euclid's. |

- **euclid**: the Lean follows Euclid's argument. Helpers, groupings and cases he leaves
  to the reader do not change the route; they are declared as passages. Nor does a case
  that is trivial, or lies beyond his statement, which the Lean takes as well: it is
  declared as a passage (`case`, `helper` or `given`).
- **modified**: Euclid's argument, with a step done materially differently: another
  construction, or one of his steps, or a real case within his statement, argued another
  way (III.8, whose last step compares the angles at the centre by I.24).
- **alternative**: a different proof altogether, labelled as one on the page (III.24's
  proof by the radii, once stage 3 gives Euclid's own).

### `[representation]`: how Euclid's objects are put into Lean

| Key | Type | Required | Meaning |
|---|---|---|---|
| `tags` | list of tags from [terms.toml](terms.toml) | yes | Every term that applies, scope tags included. |
| `note` | string | no | What the representation means for this proposition. |

A tag of kind `scope` may appear only when the statement is restricted or partial.

### `[overlap]`: a rule that contains the proposition, or supplies a step of a proof of it

| Key | Type | Required | Meaning |
|---|---|---|---|
| `rule` | string | yes | The axiom, named as facts.json names it: `"Tacit.outside_of_between"`. |
| `also` | list of strings | no | Any further axioms that contain the proposition, or supply its step, only together with `rule`, as III.6 needs `"Tacit.centre_inside"`. |
| `ways` | list of lists of strings | no | For `states` and `gives` alone: the further combinations of axioms that contain the proposition, each a list of names as `also` is; `rule` with `also` is the first (below). |
| `kind` | `"states"`, `"gives"` or `"step"` | yes | The kind of the proposition's row in the catalogue (below). |
| `note` | string | for `step` | What follows for the page: the proof reconstructs Euclid's reasoning within our foundations, and does not establish the rule. For a step, which step the rule carries, and in which proof. |

The catalogue of overlaps, with their audit lemmas, is
[docs/reports/overlaps.md](../docs/reports/overlaps.md). Each of its rows is one of three
kinds, and `kind` names the row's kind in the catalogue's words:

- **states**: the rule, read for the proposition's figure, is its statement, or says more
  (historically, III.2 and Circle 2, before that rule became a theorem).
- **gives**: the proposition follows from the rule at once, in a short proof from at most
  three rules that cites no proposition, any other rules only drawing or naming the figure
  (III.2 from Circle 3, III.5 and III.6).
- **step**: inside some proof, the rule carries a step that is the proposition's content,
  or a case of it, and does not give the proposition at once (as for I.13, a consequence of
  which, Metric 5, carries a step of I.47's proof).

More than one combination of rules may contain a proposition: `Audit/Overlaps.lean`
proves III.5 from Diagram-segment 2 with Generalities 4, and twice more from Definition
I.15 with two other rules. `rule` with `also` names the first combination, and `ways`
names each further one, as a list of axioms named as facts.json names them, in the order
of the record's note:

```toml
ways = [
  ["Definition15", "Tacit.len_lt_of_inside", "Tacit.lt_irrefl"],
  ["Definition15", "Tacit.inside_not_on", "Tacit.on_circle_of_len_eq"],
]
```

Only a rule that states the proposition or gives it at once has `ways`, since a rule that
supplies a step does not contain it. Each combination is a different set of rules from the
first and from every other, and names no rule twice. For an overlap that states or gives
the proposition, every combination, the first among them, is one that
`Audit/Overlaps.lean` proves it from: some theorem of the file's section "Rules that state
a proposition, give it at once, or supply its step" has the proposition's own type
(`type_of% @Elements.BookIII.Prop5`), and the `#guard_msgs` pin of its `#print axioms`
gives exactly those rules, less Lean's own `propext`, `Classical.choice` and `Quot.sound`.
`Audit.I_7`, a circular derivation through I.7's own corollary, proves no overlap, and
is left out. The check refuses the whole file, naming the line, for each of these forms:
an import outside `Elements`; a `variable`, `include` or `export`, or a command that
declares a token (`notation`, `infix`, `infixl`, `infixr`, `prefix`, `postfix`, `syntax`,
`binder_predicate` or `declare_simp_like_tactic`), before the section's end; a
namespace, or a declaration by `theorem`, `def` or another word the scan reads (a
constructor among them), with a name it reads that has a part `Elements`, or a part in
«…» that holds a dot, which the check cannot tell from a longer name; or a theorem of
the section whose type is written as a proposition's own, other than `Audit.I_7`, whose
full name, as the scan reads it, is the name it reads for another declaration of the
file. `macro`, `elab` and their
`_rules` are refused by the source scan, in `Audit/` and `Elements/` alike. The scan
reads the file's text, not Lean's elaboration of it, and trusts the modules of
`Elements` the file imports: it refuses the forms above, but a text it does not
recognise as one of them may still make a theorem's type read otherwise than Lean
elaborates it. It is a guard against honest slips, not a proof; the full cure, a
follow-up, is for Lean itself to report each audit theorem's type and axioms.

The page words its overlap by the kind, in the line under the enunciation and in the
book's summary, which also heads the book's index, its section of CERTIFICATE.md and its
row of README.md. A rule that states the proposition or gives it at once "contains" it;
a rule that supplies a step "supplies a step of a proof of it", and is never said to
contain it. Each says too whether our proof rests on all, some or none of the named
rules, from facts.json's `axioms`; when it uses some but not all, each rule used and
each unused is named. The table's Overlap row names the rules and gives the record's
`note` word for word (with no note, it says by the kind that the rules contain the
proposition, or supply a step of a proof of it); it adds the account of which rules our
proof rests on only when the proof uses some but not all. Where an overlap has `ways`,
the line under the enunciation says in a few words how many combinations contain the
proposition, and whether our proof rests on all, some or none of the rules of each ("our
axioms already contain it in three ways, and our proof rests on some of the rules of
each"); where that differs from one to another, it takes each by its place. The summary
and the table name every combination, the first one first, and say of each, as of a
single one, which of its rules our proof rests on: in the summary, whether it rests on
all of its rules, some (naming each rule used and each unused) or none; in the table,
for each combination the proof uses only in part, each rule used and each unused. Every
`[overlap]` names its kind, and one that does not is a fault, so no page words an
overlap by a guess.

### `[coverage]`: the clause map

Required when the statement is partial, and shown before the Lean.

| Key | Type | Meaning |
|---|---|---|
| `checked` | list of strings | The claims the Lean proves, in plain words. |
| `explains` | list of strings | Results the Lean proves that carry Euclid's argument for the clauses it leaves out. |
| `text_only` | list of strings | The claims kept only in Heath's text and the commentary, each quoted exactly from Heath. |

### `[[passage]]`: how a passage of the proof appears in the Lean

One table for each passage declared, in the order of the proof.

| Key | Type | Required | Meaning |
|---|---|---|---|
| `at` | string | yes | The passage's first words, quoted exactly from Heath's proof, enough of them to occur there once. For a run of `--` lines with no Lean beneath it, the run's first words. |
| `kind` | see below | yes | How the Lean carries the passage. |
| `helper` | a Lean name | for `helper` | The declaration that does the work: `"Prop1.middle"`. In a carried passage, the proposition's porism or one of its companions, proved on its own, written in one of three ways: `"Prop16.porism"`, `"BookIII.Prop16.porism"` or `"Elements.BookIII.Prop16.porism"`. |
| `note` | string | unless carried | One or two plain sentences, shown on the page under "How the Lean follows the text". |
| `unused` | list of names | no | The bindings this passage declares as standing for Euclid's words and not used again, each as the proof writes it: `"FC"`, `"hCHG_EHC"`, or `"this"` for a `have` that gives no name. For the citation sweep and reviewers; the page does not show it. |

- **carried**: the Lean beneath carries out the inference or construction. Declared only
  where that needs saying, as for a step proved as its own theorem, which the passage
  names as its `helper`: the proposition's porism, or one of its companions. Nothing else
  is carried this way: a lemma or another proposition that does a step makes a `helper`
  passage.
- **helper**: a lemma supplies a step Euclid takes for granted; the note says which step.
- **grouped**: several sentences carried by one argument, or a "similarly" by one lemma.
- **case**: a case Euclid's figure leaves aside, or leaves to the reader, which the Lean
  takes as well, in the same argument or in a step of its own (II.14's ED the greater,
  III.2's AB through the centre); the note says how.
- **given**: what the passage does is already given, by the statement or by how our
  objects are put into Lean, so no Lean is needed beneath it (I.5's D and E, which come
  with the statement); the note says what gives it.
- **different**: the Lean argues this passage another way; the note says how. A
  passage argued another way changes Euclid's route, so its record's route is
  `modified` or `alternative`, never `euclid`.
- **unformalized**: the passage has no formal counterpart; the note says why.

The page lists the passages under "How the Lean follows the text", each led by a plain
word for its kind: "Done by `Prop6.less`", "Carried together", "A further case",
"Already given", "Argued another way", "Left in Euclid's words", or, for a porism or a
companion proved on its own, "Proved separately, as `Prop16.porism`". The sentence above
the list names such a step by the kind of theorem that proves it: "where a porism is
proved as a theorem of its own", or "where a companion is proved as a theorem of its
own", or, for several, "where a porism and two companions are proved as theorems of their
own". It counts theorems, not passages: a companion that carries two passages is one
companion.

`unused` is for `scripts/sweep_citations.py`, which lists every binding of a proof that
nothing uses ([FORMALIZATION](../docs/FORMALIZATION.md), section 5). Where a sentence of
Euclid's stands over one, as over I.5's joins, the passage whose `at` begins a sentence
of that run of `--` lines declares it by name, and nothing else does: not a note, nor a
`#` comment. `unused` is a key, which the records' `text` stamp will cover once
[#77](https://github.com/jackChallis/stoicheia/issues/77) lands; TOML does not read a
comment, so that stamp would never see one change. `heath.load_review` checks that
`unused` lists distinct names, each one Lean identifier; `scripts/check_fidelity.py`,
that the Lean beneath the run binds each, so a declaration cannot outlive its binding.
The page does not show the key, but it does show the passage: one added only to hold
`unused` is listed under "How the Lean follows the text", led by "Carried", as every
passage is.

```toml
[[passage]]
at = "and let the straight lines FC, GB be joined"
kind = "carried"
note = "The Lean joins FC and GB by Postulate 1, as Euclid asks; no later step uses them."
unused = ["FC", "GB"]
```

### `[figure]`

| Key | Type | Required | Meaning |
|---|---|---|---|
| `case` | string | no | The case the figure shows, when the theorem covers several, or, with `every_case`, the cases it draws. The caption names it. |
| `every_case` | boolean | no | True when the figure draws every case the theorem covers, side by side or on one figure, as III.25's draws Euclid's three: the caption then reads "Drawn for every case: …" rather than "Drawn for one case: …". Needs a `case`. |
| `note` | string | no | Where our drawing of Euclid's figure places a point otherwise than Heath's, as the Lean does; shown under the figure (docs/STYLE.md, section 7). |

The section needs a `case` or a `note`, or both, and is left out when it has neither.

### `[review]`: who read it, and what they read

| Key | Type | Required | Meaning |
|---|---|---|---|
| `stage` | `"exceptions"` or `"full"` | yes | See "Two stages". |
| `commit` | git commit, 7 to 40 hex digits | stamp | The commit whose files the record was last confirmed against: the reviewer's reading, or a later reading of each changed file against the record (docs/WORKFLOW.md, section 6). |
| `lean` | `"sha256:"` and 16 hex digits | stamp | `heath.file_hash` of `Elements/Book<book>/PropNN.lean`, which holds the theorem, its helpers, porism and companions. |
| `text` | `"sha256:"` and 16 hex digits | stamp | `heath.text_hash` of the record itself: what it says, without its `[review]` table and fingerprint. A record stamped before it may lack it for now (below). |
| `reviewer` | string | yes | Who reviewed it: a person's name, or the model, as `"Claude Opus 5.5"`. From stage `full`, the model and its role, as `"Claude Opus 5.5, records crew"`, so that a reader can tell the reviewer from the proofs' authors. |
| `run` | string | from stage `full` | The run the review was made in: the brief and stage, and the workflow, as `"brief 0005 stage 5, workflow wf_…"`. |
| `items` | table | no | Acceptance items, each `"pass"`, `"fail"` or `"n/a"`. |

`items` may be omitted or empty at either stage. `heath.load_review` checks each key's
syntax and the three verdict values, but neither requires items nor limits keys to the
acceptance checklist; `scripts/check_fidelity.py` adds no such requirement.
`scripts/check_acceptance.py` rejects other keys (P2) and fails missing verdicts (P11 to
P16). The keys and conditions for a verdict to count are in
[docs/ACCEPTANCE.md](../docs/ACCEPTANCE.md#recording-a-review-item), "Recording a review
item".

## Stamps

`fingerprint`, `commit`, `lean` and `text` are stamps: `scripts/review_stamp.py` writes
them, so nobody computes a hash by hand. Keep each on a line of its own, `key = "value"`,
so the script can rewrite it in place. Before stamping, `heath.load_review(book, n,
require_stamp=False)` reads a record without them.

`text` covers the record's own words, so that an edit to a note, a scope or a passage
makes the record stale as surely as a change to the Lean. It is `heath.text_hash` of the
record as TOML reads it, with `[review]` set aside, which holds the stamps and the
reviewer's account of the reading, and with `fingerprint` set aside, which stamps the
statements: so writing a stamp never changes the text it stamps. Comments, layout and the
order of keys are not part of the text; every key and value of the other sections is.
`[review]`'s own `stage`, `reviewer`, `run` and `items` are not part of the text: a change to them
after the stamp is not caught by `text`, and is seen only by whoever reviews the pull
request.

A record stamped before `text` was introduced may lack it until it gains it as
[WORKFLOW](../docs/WORKFLOW.md), section 6, says; `scripts/check_fidelity.py` names each
record without it in a note. Once every record carries `text`, it is required like the
other stamps.

## What the machine checks

`heath.load_review` raises a `ReviewError` naming the file and every fault it finds:

- the sections and keys are known, the required ones present, each of its type;
- `scope`, `route.kind`, passage `kind`, `[overlap]` `kind` and `stage` take only the
  values above; an `[overlap]` names its `kind`, and one of the kind `step` has a `note`;
- an `[overlap]`'s `ways` is a list of combinations, each a list of axiom names, in an
  overlap of the kind `states` or `gives` alone; each combination is a different set of
  rules from `rule` with `also` and from every other; and no combination, `rule` with
  `also` among them, names a rule twice;
- a restricted statement lists `hypotheses` and has no `omitted`; a partial one lists
  `omitted` and has `[coverage]`; a full one has neither; both kinds need a `note`;
- `note` is one line of at most 160 characters;
- `omitted` and `text_only` are quoted from Heath, and each passage's `at` occurs exactly
  once in his proof (whitespace aside), and no two passages share it;
- `companions` are companions of this proposition; tags are in terms.toml, with no
  scope tag on a full statement;
- a modified or alternative route has a `note`, as does every passage not carried; a
  helper passage names its `helper`; a passage argued another way (`different`) is not
  under a route of `euclid`;
- a passage's `unused` lists distinct names, each one Lean identifier, or `this`;
- a restricted or partial statement has a `short`;
- a record at stage `full` names its `run`, and its `reviewer` names a role;
- stamps have their form.

`python3 scripts/heath.py` checks the worked examples below and every record present.
`scripts/check_fidelity.py` adds what needs facts.json and the Lean files: that every
proposition has a record, that the stamps are current (if not, that its statement, its
Lean file or its record "has changed since it was reviewed"), and that every run of `--`
lines with no Lean beneath it is declared. It holds an `[overlap]` to them too: each rule
it names, in `rule`, `also` or `ways`, is an axiom in facts.json, and, for the kinds
`states` and `gives`, each combination is one that `Audit/Overlaps.lean` proves the
proposition from, as `[overlap]` says above, read from the file's text, whose pins
`lake build Audit` checks. A fault names the record, the combination and the rules that
the file proves the proposition from, or why the check refuses the file, naming the line
of any form it refuses there.
`scripts/render.py` reads a carried passage's `helper` as the porism or a companion
facts.json attaches to the proposition, and stops, naming the proposition and the helper,
on any other.

`scripts/check_style.py` reads as "Review notes" the statement's `note`, `short` and
`hypotheses`, the route, representation, overlap and passage notes, the figure's `case`
and `note`, and the clause map's `checked` and `explains`. It also reads each tag's
`meaning` and `badge` in `review/terms.toml`. S1 to S9 and S22 check their prose; S12 asks Lean
about names in backticks, except the non-declarations listed in `NOT_DECLARED`.
[STYLE](../docs/STYLE.md#8-checks), section 8, gives the rules and explains which findings
`REACH_PENDING` reports without failing.

## Worked examples

These two show the shape of a record; they are not the records themselves, which live in
`review/III/16.toml` and `review/I/40.toml`. Their stamps were computed at commit
d040117, and serve as test values: at that commit, `heath.review_fingerprint` gives
`sha256:9fd59073303dbcdc` for III.16 (its statement, then III.16 Por.'s) and
`sha256:5ea666d96871b7f8` for I.40. Their `text` is `heath.text_hash` of each example as
printed here, which `python3 scripts/heath.py` checks.

III.16 is partial: the clause about the angle of the semicircle and the horn-like angle
is not stated, its porism is proved on its own, and one run of sentences has no Lean
beneath it.

```toml
# review/III/16.toml
[statement]
scope = "partial"
omitted = [
  "the angle of the semicircle is greater, and the remaining angle less, than any acute rectilineal angle",
]
note = "Proves that AE falls outside the circle and that no other straight line can be interposed; the clause map below shows what stays in Euclid's words."
short = "the angle clauses stay in Euclid's words"
fingerprint = "sha256:9fd59073303dbcdc"

[route]
kind = "euclid"

[representation]
tags = ["mixed-angles-omitted"]
note = "Our angles are made by two straight lines, so an angle contained by a straight line and a circumference has no Lean counterpart."

[coverage]
checked = [
  "Every point of AE other than A is outside the circle.",
  "Every other straight line through A has a point within the circle, so none can be interposed between AE and the circumference.",
  "Porism: AE touches the circle (III.16 Por.).",
]
explains = [
  "The second claim is what Euclid proves the angle clauses by. A rectilineal angle between them would need a straight line interposed.",
]
text_only = [
  "the angle of the semicircle is greater, and the remaining angle less, than any acute rectilineal angle",
]

[[passage]]
at = "Similarly we can prove that neither will it fall on the circumference"
kind = "grouped"
note = "One step shows that no point of AE but A is on the circle; it gives both \"not within\" and \"not on the circumference\"."

[[passage]]
at = "I say further that the angle of the semicircle"
kind = "unformalized"
note = "Euclid's argument for the two angle clauses, which the clause map above accounts for."

[[passage]]
at = "PORISM. From this it is manifest"
kind = "carried"
helper = "Prop16.porism"
note = "Proved as its own theorem, with its own certificate entry, III.16 Por."

[review]
stage = "exceptions"
commit = "d040117"
lean = "sha256:061379c1f0411141"
text = "sha256:47c9097b39a8fcc7"
reviewer = "Claude Opus 5.5"
```

At d040117, I.40 was restricted: the theorem took the two bases end to end.

```toml
# review/I/40.toml
[statement]
scope = "restricted"
hypotheses = ["the bases BC and CE meet at C (`Between B C E`)"]
note = "Proved for equal bases that meet end to end, as BC and CE; Euclid's bases may lie anywhere on one straight line."
short = "bases that meet end to end"
fingerprint = "sha256:5ea666d96871b7f8"

[route]
kind = "euclid"

[representation]
tags = ["adjacent-bases"]

[figure]
case = "the bases BC and CE meeting at C, as in Heath's figure"

[review]
stage = "exceptions"
commit = "d040117"
lean = "sha256:5f353abf9022b4fd"
text = "sha256:39fcf9b00f4bf715"
reviewer = "Claude Opus 5.5"
```

Stage 2 has added `Prop40.general`; [I.40's current record](I/40.toml) has full scope and
lists `"I.40 general"`, `"I.40 join"` and `"I.40 special"` as companions. The example above
remains the fixture from commit d040117.
