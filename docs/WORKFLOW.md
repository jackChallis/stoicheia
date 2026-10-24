# Workflow

How work on Stoicheia is assigned, owned, reviewed, integrated and released, by people and
agents working in parallel. The rules live here. [PROGRAM.md](PROGRAM.md) holds the state
of the work, its costs and the lessons behind these rules; [FORMALIZATION.md](FORMALIZATION.md)
and [STYLE.md](STYLE.md) say what a good result is. The task, handback and review forms are
in [templates/proposition.md](templates/proposition.md), and the orders for a fleet in
[templates/orders.md](templates/orders.md). This page follows Astra's
[draft guide](reports/outside-review-01-guide.md), sections 4 and 10 to 13, adapted to how
Books I–III were made.

## 1. Roles

Roles are responsibilities, not headcount. A small task does not need five agents, and one
contributor may hold several roles, save one: nobody reviews a claim they wrote.

| Role | Responsible for |
|---|---|
| Owner | The repository's owner. Every public action but landing a checked pull request (tags, releases and their notes, the GitHub description, anything sent outside the repository), and the foundation decisions, made with the coordinator. |
| Coordinator | The plan, the baseline, and the decisions delegated to the role: approving statements and brief corrections, the files of the foundations, `Certificate/axioms.lock`, the decisions record ([0002-decisions.md](briefs/0002-decisions.md), the decisions page, and the dated entries of `docs/decisions/`), PROGRAM.md, CI, and opening and merging pull requests, through `scripts/safe_push.py` alone (section 10, "Landing work: pull requests"). |
| Statement and representation owner | A book's brief and each proposition's statement: vocabulary, hypotheses, conclusions, cases, and the exceptions allowed. |
| Proof contributor | The assigned declarations with their helpers, porisms and companions, and how the Lean corresponds to the text. |
| Edition contributor | Commentary, figures, source notes and further reading, written against the brief and reconciled with the finished proof. |
| Independent reviewer | The changed claims, read against the source, the argument and the rendered page, with findings and their severity. |
| Integrator | Merging a wave's branches, resolving conflicts, regenerating and committing the generated edition, validating the integrated revision, and keeping the companions list (section 4). |

A fresh context helps a reviewer, but a different model name does not by itself make a
review independent: the reviewer must not have written, prompted or edited the claim.

### How the crew fills the roles

Books I–III were made by a crew of agents, as the README's "How it was made" tells, and
their logs are in `docs/reports/crew/`:

- **The captain**, the main Claude session working with the owner, is the coordinator,
  and the integrator at the end of a wave unless it names one.
- **A first mate**, one for each book or stretch, owns its statements and representations:
  it writes the brief, states every proposition with `sorry`, tests the statements with
  scratch proofs, and writes the orders. After the voyage it reviews each proof for
  faithfulness and merges its bosuns' work.
- **Sailors** are proof contributors, one proposition each. From the third voyage they were
  OpenAI Codex sailors, two to a proposition: one at Codex's usual reasoning setting and one
  at its highest. A sailor proves the proposition, draws Euclid's figure, and drafts the
  mishnah and the reading line.
- **A bosun** runs a proposition's two sailors, builds both proofs, keeps the one that reads
  more like Euclid, and may take a piece of the other (a figure, a mishnah, a reading line).
  It commits for them, since a Codex sandbox cannot write to `.git`.
- **Ships' captains**, one for each ship of a fleet, are edition reviewers: they read every
  page for the common voice and edit it, and change nothing in the mathematics.
- **Transcribers** carry Heath's text from the scans; **artists** draw the figures at a
  glance; **inspectors** audit a finished book; **adversarial verifiers** challenge
  statements before proofs, and review records after.
- **Range enforcers, blind readers and a polisher** keep one voice (section 7).
- **An independent audit** comes from a model family that wrote none of the work (Jev, from
  brief 0005's stage 6), and **a cold outside reading** from three reviewers of three model
  families, scoring by the [review rubric](RUBRIC.md): at present Claude Opus 5.5
  (Anthropic), GPT-6 Astra through Codex (OpenAI) and Gemini 4 Argon (Google).

## 2. Briefs before proofs

A proof is only as good as the statement it proves, and every other contributor relies on
that statement. So statements and representations are settled first.

1. **The book's brief** (`docs/briefs/`) settles the vocabulary, the representations and
   their bridge theorems, the construction inputs, the shared ground, the conventions and
   the exceptions expected. The coordinator approves it before any statement is written. A
   new word is a definition in the foundations, owned by the coordinator, and joins
   `Certificate/axioms.lock` with a decisions entry once a statement uses it; a new axiom
   is a foundation decision ([FORMALIZATION.md](FORMALIZATION.md), section 1).
2. **Each proposition's statement** is written with `sorry`, under Heath's sentences
   (`scripts/scaffold_book.py`), with a proposition brief
   ([template](templates/proposition.md)) for anything not routine: the declaration, its
   meaning in plain words, its coverage, cases, construction data, representation, route and
   dependencies. A new book's statements are scaffolded in `Elements/`; a statement that a
   stage of [brief 0005](briefs/0005-astra-review.md), or of a later brief, adds or changes
   is written first in the `Staging` library instead ([`Staging.lean`](../Staging.lean)),
   with `sorry` where its proof is due, and is challenged and approved there before any
   proof is assigned. When it is proved, it leaves `Staging/` for its home in `Elements/`
   (save a fact proved in place, below), and its staged copy, with any staged check that
   names the old statement, is deleted in the same change, so that no name is declared
   twice and `lake build Staging` still passes. Where staged files live, what they import
   and what they are named is in [FORMALIZATION.md](FORMALIZATION.md), section 6.

   **What proofs `Staging/` may hold** (this is the rule's one home). A staged statement's
   own proof waits for its brief's approval. Before that, `Staging/` may hold two kinds of
   proof: a proof that derives one staged statement from others, which tests their
   interfaces (today's statement derived from a companion, "Nothing is lost" in the
   [orders](templates/orders.md), is one; a companion derived from a wider one is another);
   and the proofs of a prototype the coordinator has approved. A derivation from a stub
   proves nothing until the stub is proved, and says so in its docstring or its brief.
   After its brief is approved, a staged fact whose proof rests on no stub may be proved in
   place. It waits in `Staging/` until the definitions it uses reach the foundations and
   the task its brief names for its home moves it there, its staged copy deleted in that
   change: the one case in which a proved statement stays in `Staging/`.
3. **It is challenged** by readers who did not write it (Book III's statements answered
   twenty-six challenges before its voyage), and **tested** by scratch proofs where the route
   is in doubt. Scratch proofs are committed unbuilt in `docs/reports/crew/scratch-<book>/`,
   and retired once the book is proved; the history keeps them.
4. **The coordinator approves it,** and it is frozen.
5. **Only then are proofs assigned.**

A reviewed brief is reused while the statement, representation and route stay the same. An
editorial task needs only its baseline, its owned files, the change asked for and the checks
to run.

**Prototype each new foundation.** Before a fleet sails on a new kind of object, one hard
statement is proved by hand: V.18's fourth proportional for Book V, VII.16 without
borrowing commutativity for Book VII, X.1 for Book X, one solid statement for Books XI–XIII.
Book IV's interfaces (arcs, segments, construction inputs) are settled before its
statements.

### Correcting a frozen brief

Frozen means that others may rely on an interface. It does not mean that a wrong one must
survive. A proposed correction carries:

- the case that fails, or the discrepancy;
- the current declaration;
- the proposed declaration;
- the reason;
- the consumers it affects.

The coordinator decides within the authority delegated to the role, records the
correction in a new revision of the brief or a new decision entry,
`docs/decisions/<YYYY-MM-DD>-<slug>.md` (section 10, "Decision entries"), naming each
statement it changes (the pre-flight looks for that new line: section 10, "Landing work:
pull requests"), and tells the contributors affected. Useful independent work goes on
meanwhile.

A changed statement or representation makes stale every proof, commentary, figure and
review that rests on it, its consumers' included; the review records' fingerprints show
which. A changed proof of the same type can still change its route and its certificate.

## 3. Waves

Work moves in dependency waves:

1. Fix the baseline: the commit, the toolchain, the instructions in force, the scope, and any
   failures already present.
2. Settle the representations and statements the next group of propositions needs.
3. Approve the briefs, and publish the signatures of shared helpers as statements with
   `sorry`.
4. Assign disjoint work, and record what is pending.
5. Land shared changes before their consumers, then integrate the group.
6. Review the integrated proofs, commentary, figures and certificate.
7. Close what was pending, and describe the state of the edition accurately.

A proof may be written against an unfinished earlier theorem whose statement is stable. Its
handback names that dependency, and it stays provisional (`proved-pending`) until the
dependency closure is complete. Stage 1 of [brief 0005](briefs/0005-astra-review.md) ran in
four waves: a contracts commit (the field list and the record schema), owners of disjoint
files working in parallel, the renderers, and an integrator followed by blind readers.

## 4. Files and ownership

- **One writer per file** during a wave. Each contributor works in a branch or worktree of
  their own, from a named baseline, with their own build outputs. In a shared tree,
  contributors take disjoint files and agree before running commands that write common
  outputs.
- **Each wave's orders name the owner of every file being changed.** Anything else is asked
  of its owner through the handback, never edited in passing.
- **Standing owners.** The coordinator owns `Elements/Foundations/` (every `Definitions*`
  file included), `Certificate/axioms.lock`, the toolchain and its dependencies
  (`lean-toolchain`, `lakefile.toml`, `lake-manifest.json`), the decisions page and
  `docs/decisions/`, the folder of decision entries, PROGRAM.md with `docs/program.toml`,
  and the CI workflow, and may hand the lock, the decisions page and `docs/decisions/`,
  PROGRAM.md and the CI workflow to a wave's integrator. The integrator
  owns the generated edition: `facts.json`, `book/`, `CERTIFICATE.md`, `GRAPH.md`,
  README.md's rows between the `<!-- scope:… -->` markers, PROGRAM.md's status table
  between the `<!-- status -->` markers and inline `count:` values in tracked Markdown,
  which `render.py` fills; the rest of README.md has an owner of its own, named in the
  orders. Section 8's first command block, between the `<!-- checks -->` markers of this
  page, is generated too, from the registry of checks in `checks/`, and travels with the
  change to the registry that moves it. The integrator also owns the companions list,
  `Elements/Companions.lean`, which the certificate reads and checks, and adds a
  companion's entry in the commit that moves the companion beside its proposition, so
  that the listing travels with the proof and its record's stamp
  ([FORMALIZATION](FORMALIZATION.md), section 2). Each wave names owners
  for Book Zero and the shared helper modules, `heath/`, the scripts, `Certificate/Facts.lean`,
  the review records, the reading list and bibliography, and the book briefs.
- **Ask for a shared lemma with a proposed type:** its purpose, a proof or a plan, where it
  may live in the dependency order, and who will use it
  ([template](templates/proposition.md)). That is far easier to integrate than "something
  about circles".
- **Generated files.** Contributors may render previews; only the integrator commits the
  generated edition, including inline `count:` values in tracked Markdown, regenerated
  from the integrated sources. This avoids merging separately generated copies of the
  same pages.
- **Commit by name** (`git add` the files you own), never `git add -A` in a tree others use.
  Do not push, open, merge or approve a pull request, or rebase a shared branch: the
  coordinator lands work, as pull requests (section 10, "Landing work: pull requests").

## 5. Proving in parallel: a voyage

A voyage is one stretch of a book, run as a workflow:

- **The orders** are written from [templates/orders.md](templates/orders.md), once for the
  stretch, and every sailor follows them word for word. They open with a note on what the
  user's latest relayed message means for the task, so that a short message ("continue",
  "ignore") is read as it was meant: a relayed "Ignore" once made a fleet stand down. They
  carry the voice of [STYLE.md](STYLE.md) into every prompt, and point to STYLE, section 1,
  for the line between the crew and the reader, rather than restate it.
- **Best of two.** Each proposition goes to two Codex sailors working independently, at the
  usual and the highest reasoning setting. The bosun builds both, keeps the proof that
  follows Euclid more closely, and may take a piece of the other. The highest setting has won
  most often, but the choice is made on the proof, not the setting.
- **Faithfulness.** The first mate reviews each kept proof: the statement unchanged, Euclid's
  route, every run of `--` lines carried or declared, no dummy citations or artificial
  hypothesis uses, Heath's letters in the figure, and the record entries the handback
  proposes.
- **The voice.** Ships' captains read every page and edit it in the common voice; an edit
  pass changes nothing in the mathematics.
- **The log.** The integrator merges the branches (their files do not overlap),
  regenerates, validates (section 8), and logs the voyage in
  `docs/reports/crew/voyage-NN.md`: a table of each proposition (which proof was kept, each
  sailor's minutes and tokens, faithful or not, how closely it reads as Euclid, the edits
  made), what the voyage showed, the axioms added, and the gaps found.

PROGRAM.md records the agents, tokens and hours each kind of step has taken.

## 6. Reviewing

**Begin from the source.** A reviewer reads Heath and the formal statement, each on its own,
before the author's account of how they agree; then the argument, helpers included; then the
rendered page.

**Review records are tied to a commit.** Every proposition has a record,
`review/<book>/NN.toml` ([schema](../review/SCHEMA.md)). `scripts/review_stamp.py` stamps it
with a fingerprint of the statements reviewed, a hash of the Lean file, a hash of the
record's own text without its `[review]` table and fingerprint, and the commit whose files
the record was last confirmed against. When any of the three no longer matches,
`check_fidelity.py` reports that the statement, the Lean file or the record has changed
since it was reviewed, and the record is read again. At the stage `exceptions` a record
declares every departure; at the stage `full` it classifies every substantive passage. The
record's `reviewer` names who read it; from the stage `full` it names the model or person
and the role, and `run` names the brief, stage and workflow, so that a reader can tell the
reviewer from the authors of the proof.

**Stamps.** A stamp says that a record has been read against the files as they now are.

- The reviewer stamps, after reading, with the commit whose files were read:
  `python3 scripts/review_stamp.py --commit <commit> III.16`. Commit the change first,
  then stamp; the script checks that the commit is in the history of HEAD, and that the
  Lean file and the record at that commit are as they are now, the record's `[review]`
  table and fingerprint aside.
- The integrator re-stamps only after reading each changed file against its record, and
  then stamps with the commit read. A record the integrator cannot confirm goes back to the
  records' owner.
- On a contributor's branch, "changed since it was reviewed" is expected whenever a Lean
  file under a record changes, even by a comment, and whenever the record's own text is
  edited. The contributor lists the records made stale in the handback (form 3, "Records
  made stale"), and never runs `review_stamp.py` on a record they did not review.
- The records stamped before the `text` stamp was introduced gain it by
  `python3 scripts/review_stamp.py --migrate-text`, which writes `text` alone, and only
  for a record whose own stamp commit is in the history of HEAD and whose text at that
  commit is its text now: what was read is then what the record says, so it records no
  new reading. It reads the records' history, so it runs in a full clone. A record whose
  text it cannot confirm is listed as needing a reader, who reads it and stamps it as
  above. A stamp commit absent from the clone or abbreviated ambiguously is a problem, and
  so, for a record without `text`, is one a shallow clone cannot place in the history of
  HEAD: the command exits 1 without listing that record for a reader. Fetch missing
  history and run it again; for an ambiguous id, a reader identifies the intended commit
  without guessing, reads the record and stamps it as above with enough of the id to name
  that commit alone; then run it again. The migration may be run again at any time, as at
  landing, after the branches that change records. Until every record carries `text`,
  `check_fidelity.py` names those without it in a note.

**What a reviewer of the Lean looks for:**

- the statement unchanged, or its change approved;
- coverage, by the questions of [FORMALIZATION.md](FORMALIZATION.md), section 2;
- Euclid's route, or a departure labelled where it happens;
- every run of `--` lines carried, or declared in the record;
- dummy citations: calls whose result is unused, made only to match one of Heath's
  references;
- artificial hypothesis uses: `have _ := h…` and the like;
- helpers that conceal a whole conclusion;
- later citations, lemma placement, imports, and Book Zero importing no proposition.

`python3 scripts/sweep_citations.py` lists the candidates for the dummy citations, the
artificial hypothesis uses and the concealing helpers, and marks those the record already
declares ([FORMALIZATION.md](FORMALIZATION.md), section 5). The reviewer judges each: a
step a sentence of Euclid's stands over stays, and is declared by naming its binding in
the `unused` of the passage over it ([review/SCHEMA.md](../review/SCHEMA.md)), which no
note and no `#` comment can do; any other is fixed, deleted or its part cleared with `-`.

For the page, the reviewer's checklist is in [STYLE.md](STYLE.md), section 8; figures are
checked as geometry.

**Findings** name the revision reviewed, the place, the defect, its severity (section 9) and
the correction required. A review is never summed up as a general approval, and a check not
made is said to be not made.

**Refreshing.** When a statement, definition or shared helper changes, find its consumers
and refresh their reviews. When only a local proof changes, check whether its route,
dependencies, commentary or figure changed. Unchanged work need not be audited again.

## 7. One voice

Ships' captains enforcing a few pages each do not, between them, make one voice. These do:

- **Range enforcers** read a book, or a long range of it, straight through against
  [STYLE.md](STYLE.md), and mend drift in register: the commentary turning into a ledger,
  refrains, leads that are labels.
- **Blind readers** are given pages mixed from every book, are not told who wrote what, and
  listen for a second hand, in the commentary and in the Lean notes alike; they report
  findings by page and line.
- **A polisher** works through the readers' findings, makes the edits, and writes the log
  (`docs/reports/crew/voice-NN.md`), with counts as the measure of the pass.
- **A read-through** comes before a release or a consolidation: readers go through the
  pages as visitors would, and checkers test what the project says about itself
  ([read-through-01](reports/read-through-01.md)).

## 8. Validation on the integrated revision

This section is the one home of the commands; every other page links here and keeps only
the subset its reader runs. The evidence belongs to the revision being delivered.
`.github/workflows/ci.yml` runs on `pull_request` and `merge_group`, and can be called by
another workflow. It no longer runs on branch pushes. The main push's
`.github/workflows/post-merge.yml` calls it after the merge.

| Run | Tree checked | Main used by the acceptance comparison |
|---|---|---|
| Local pre-flight | The exact committed head, in temporary worktrees | The pre-flight runs no acceptance comparison |
| Pull request CI | GitHub's proposed merge of the pull request into main | That merge's first parent; the event's base if the checkout is the head itself |
| Merge group CI | The group's head: main plus the queued pull requests ahead, in order | The event's group base |
| Post-merge integration | The main push's exact `after` commit | The main tip before the push, `before` |

The merge group's run checks the exact combined tree that the queue will merge. A
pre-flight or a pull request run alone cannot check the interaction with trains queued
ahead. On the integrated revision, run exactly what CI's `check` job runs, in its order
(`python3 scripts/run_checks.py --job check` runs it so, as CI does):

<!-- checks -->
```sh
export PATH=$HOME/.elan/bin:$PATH
lake build
lake build Audit
lake build Staging
lake env lean Certificate/Facts.lean
python3 -I tests/test_certificate.py
python3 scripts/sweep_citations.py --self-test
python3 scripts/sweep_citations.py
python3 scripts/check_kernel.py --self-test
python3 scripts/heath.py
python3 scripts/check_fidelity.py
python3 -I tests/test_check_style.py
python3 -I tests/test_release_gate.py
python3 -I tests/test_jev_models.py
python3 scripts/audit/jev.py self-test
python3 -I tests/test_screen.py
python3 -I tests/test_acceptance_limits.py
python3 -I tests/test_check_superposition_pins.py
python3 -I scripts/check_superposition_pins.py
python3 scripts/check_style.py
python3 scripts/render.py
git status --porcelain                 # prints nothing
python3 scripts/check_queue.py --tree .
python3 scripts/check_links.py
```
<!-- /checks -->

**The registry of checks.** That block is generated: each of its commands is a file of
its own in [`checks/`](../checks/README.md), and `render.py` writes the block from them,
in the order of their `order` fields. The same files are CI's `check` job, which runs
`python3 scripts/run_checks.py --job check` after its setup, each check a named group of
its log, stopping at the first that fails; and they are the pre-flight's sequence
(section 10, step 4), which reads origin/main's copy of them out of Git, never the copy of
the commit it checks ([the decision](decisions/2026-10-22-check-registry.md)). So CI runs
the pull request's registry, as it runs the pull request's own workflow, while the
pre-flight runs main's. CI's `check` job is a required check of the pull request, so a
train that changes the registry does change checks that judge it there; three things keep
that safe. Every train that touches `checks/` is R3 or above, so its pre-flight runs
main's whole registry on it, in both passes, whatever its CI runs. The change is
protected: each registry file it adds, removes or changes is named in a decision entry,
and the pull request carries `security-review`. And the change judges later trains only
once it has merged. To add a check, add one file to `checks/`
([its README](../checks/README.md) says what a file holds), run `render.py`, and commit
the file with the regenerated block; to remove one, or change its command, job or order,
change its file. `checks/` is a protected path and a check input (section 10), of class
R3, and neither `scripts/safe_push.py` nor the CI workflow changes with it. The registry's
reader, `scripts/registry.py`, and its runner, `scripts/run_checks.py`, are R5, with the
landing tool and CI: main's reader decides the pre-flight's sequence, and the runner is
CI's `check` job. The reader stays one self-contained file of the standard library, since
the pre-flight runs it alone, out of Git; step 3 of the pre-flight runs the commit's own
reader so, and refuses the commit when it cannot read the commit's registry, before a
broken reader can merge.

Review the generated differences and commit them with their sources, so that regenerating
leaves them unchanged and the `git status` line prints nothing. That line reads the whole
worktree, as the pre-flight's does: a file that any command above leaves changed or new,
generated page or not, fails it, so the sequence runs on a committed revision. More jobs
run on their own, each in isolation: CI's `risk`, which classifies the change (below);
`negative`, `model`, `formal-model`, `acceptance` and `queue-integrity`, more of CI's on
each pull request, `negative` and `formal-model` of them by the class `risk` gives; and
on a cadence, in the `safe-push-tests` workflow (below), the shards of `safe-push-shards`
and the `safe-push-tests` job, which gives the verdict on them, and `negative-tests` and
`formal-model-kernel`, which run on main the commands of CI's `negative` and
`formal-model` jobs. Below, the first commands are those of CI's `negative`, `model` and
`formal-model` jobs, and so of the cadence's two; the next two run the acceptance job's
tests and checklist without its CI comparison, and the last three run the tests the
shards run, whole and then one shard as the cadence runs it; the commands of `risk` are
under "Which jobs run for which class", after the block, and those of `queue-integrity`
after that:

```sh
python3 scripts/negative_tests.py      # CI's `negative` job, after lake build and Facts.lean
python3 -I tests/model/run.py --fast   # CI's `model` job, which needs no Lean
python3 -I tests/model/results_check.py   # the `model` job's second step: results/ are current
grep -v '^#' model/lock.sha256 | shasum -a 256 -c - && (cd model && lake exe cache get && lake build)
python3 scripts/check_model_kernel.py --self-test && python3 scripts/check_model_kernel.py
                                       # CI's `formal-model` job: the formal model, with Mathlib,
                                       # then its compiled proofs replayed by Lean's kernel
python3 -I tests/test_check_acceptance.py   # CI's `acceptance` job: the comparison tests
# After lake build, lake build Audit and Facts.lean, the checklist run:
python3 scripts/check_acceptance.py --output "${RUNNER_TEMP:-/tmp}/acceptance/report.md" --json "${RUNNER_TEMP:-/tmp}/acceptance/verdicts.json"
python3 -m pip install -r scripts/requirements-test_safe_push.txt
python3 scripts/test_safe_push.py      # every test the shards run, in one run: no Lean
python3 scripts/test_safe_push.py --shard 3/8 --ran "${RUNNER_TEMP:-/tmp}/ran-3.json"   # the third shard of eight, as the cadence runs it
```

`RUNNER_TEMP` supplies GitHub Actions' temporary directory; the fallback writes under
`/tmp` when the command is run locally.

**Which jobs run for which class.** CI's first job, `risk`, computes the change's risk
class, from R0 (docs) to R5 (the landing tool and CI), from the files it changes:
`scripts/risk.py`, the one source of the classes, gives each file the class of the first
rule of its table that matches it, R5 when none does, and the change the highest of its
files' classes. The job runs main's copy of the script, never the change's own, so a
change cannot lower its own class by editing it. A pull request into main is classified
so, exactly, from GitHub's merge commit (a checkout that is not that merge of its head is
R5). CI runs on a pull request's events, on a merge group, and after each push to main
through the post-merge workflow's call, which runs under the push's event; never on the
push of another branch or of a tag, so each commit of a pull request runs once
([the decision](decisions/2026-10-22-checks-by-risk.md)), and of CI's runs the merge gate
waits for the pull request's alone. A pull request whose run starts with the `release`
label, a pull request into another branch, a push to main (the post-merge workflow's
call), a merge group and any other event are R5: a merge group's run is R5 by the job's
last case, whatever its entries change, so every job runs in full on every group. The
label is read from the event that started the run, and `git safe-push` adds a pull
request's labels after it pushes, so a label given with that push counts from the next
push; main's run after the merge runs every job in full; and the merge gate holds a
release until the full pre-flight has run on its head and a run of the `safe-push-tests`
workflow there has passed each of its jobs, the shards among them, but `report` ([section
10, "Landing work: pull requests"](#landing-work-pull-requests), step 4). `check`, `model`, `acceptance`,
`queue-integrity` and `queue-gaps` run for every class, with no `needs: risk`:
`queue-integrity` runs its offline cases on every pull request and its judge on every
group, and `queue-gaps` does its work on merge groups only. `negative` runs in full for
R3, R4 and R5.
`formal-model` runs in full for R4 and R5, the classes of every change to `model/`, to
`Certificate/axioms.lock` and to `scripts/check_model_kernel.py`, and for a change of any
class to a file of the main package that the formal model imports, directly or through
others: `risk` reads them from the model's import lines, at both ends of the change, so
the set follows the imports as they change. It reads them by a narrow grammar and fails
closed: while a file among them has a header it cannot read cleanly (a module part `«.»`,
`«..»` or `«»`, a letter or symbol past ASCII, an `import` with no module after it),
or imports a module for which the tree holds no file at the usual `A/B.lean` path, the
module roots `Check`, `Model`, `Mathlib`, `Lean`, `Init` and `Std` excepted, or while the
tree holds a `.gitattributes` anywhere (which can make the text Lean reads differ from the
text Git holds), `formal-model` runs in full for every change, and `risk`'s log names the
file. Thus a header that Lean reads otherwise, or a main-package source layout the narrow
reader does not know, can only widen the set.
For a lower class, and for `formal-model` a change that touches none of the model's
inputs, each job passes at once and says why, since the `safe-push-tests` workflow runs
both on main every six hours and a red run there holds the release ([the
decision](decisions/2026-10-22-risk-lanes.md)). Each fails, and is never skipped, when
`risk` does not succeed, for GitHub accepts a skipped required check. `python3
scripts/risk.py --paths <file>...` gives files' classes up front; `python3 scripts/risk.py
. origin/main` a branch's class, and whether the formal model runs; and `python3
scripts/risk.py --model-inputs HEAD` the files the model imports, then any among them
whose header or imports it cannot read or resolve.

**What runs for each class, at each stage.** A change's class sets what its pre-flight
and its pull request's CI run. What runs after the merge, on the cadence and for a release
does not depend on the class, and is set out after the table. The times are those of
#290, a records train, on GitHub, and of the pre-flights `git safe-push` logged on 22
October ([the decision](decisions/2026-10-22-checks-by-risk.md)):

| Stage | R0 to R2 | R3 | R4 and R5 |
|---|---|---|---|
| Pre-flight ([section 10](#landing-work-pull-requests), step 2) | steps 1 to 3, the scans and the guards, 10 to 30 seconds; step 4 left to CI | steps 1 to 4, step 4 being this section's sequence and the negative tests, 9 to 19 minutes, and twice that when a check input changes | as R3 |
| CI on the pull request | `check` (3.5 to 6.5 minutes), `model` and `acceptance` (4.5 minutes); `negative` passes at once, and `formal-model` too unless the change touches its inputs | as R0 to R2, and `negative` in full (15.5 minutes) | as R3, and `formal-model` in full (8 minutes) |

Main's run after each merge, the post-merge workflow's call, is R5, and runs every job in
full: `negative` and `formal-model` beside `check`, `model` and `acceptance`, which runs on
every event CI runs on. The cadence, the
`safe-push-tests` workflow, runs on main every six hours, whatever landed: the safe_push
tests, in eight shards side by side (in one job they took 72 to 78 minutes, and 137 on the
slow run cited below), the negative tests in full, and the formal model's build and kernel
re-check. A release runs three
things at its own head: the full
pre-flight, since its label makes it R5; its pull request's CI, in full when its run
starts with the label; and a run of the `safe-push-tests` workflow, whose jobs, the shards
among them, must each pass, but `report` ([section 10](#landing-work-pull-requests), step
4). So the negative tests check
a change of R0 to R2 only once it has landed, on main: a break they would have caught
shows within six hours, and holds the release until its repair lands.

The full `acceptance` job runs only in CI. Its ratchet before the consolidation release,
the switch to the full gate at that release, the reports and the executable definitions
are in [ACCEPTANCE, "In CI"](ACCEPTANCE.md#in-ci), the account of how CI runs the
[acceptance checklist](ACCEPTANCE.md).

The separate `release-gate` workflow runs its job only on pull requests labelled
`release`, reading the open issues labelled `blocks-release` with `python3
scripts/check_release_gate.py`; ordinary pull requests skip it. It runs main's copy of the
script, from the base commit, but GitHub takes the workflow file itself from the pull
request, which could change it, so the job only shows the hold: the authority is the merge
gate, which reads the issues again when the coordinator merges (section 10).

The `safe-push-tests` workflow, `.github/workflows/safe-push-tests.yml`, runs
`python3 scripts/test_safe_push.py`, the tests of the gate every pull request lands through
(section 10), on a cadence of its own: every six hours on main, and on demand
(`workflow_dispatch`), never on a pull request. The owner, 22 October 2026: "I'm fine that
this needs to run on a cadence and blocks release but every run no. And it has to be fast"
([the decision](decisions/2026-10-22-suite-on-cadence.md)). The tests run in shards, and
the job named `safe-push-tests` gives the verdict on them (below). On the same triggers the
workflow runs two more jobs, as CI's `negative` and `formal-model` jobs run them:
`negative-tests`, the build and the negative tests in full, and `formal-model-kernel`, the
formal model's build and its kernel re-check, neither sharing a required check's name. A red
run on main, any of the three jobs failed, cancelled or timed out, opens one issue labelled
`blocks-release`, or adds the run to the one already open, with the run's link, the jobs
that were red and the tests of `scripts/test_safe_push.py` that failed, read from every
shard's log, so the release waits for it until the issue is closed, with a link to a later
green run; that is done by the `report` job, the only one with leave to write issues, which
runs no code of the repository. For now a red run holds the release alone (whether trains
of tooling hold as well while the cadence is red is left to a later part of #274): trains
of every class go on landing while the issue is open, each by its own class, and so does
the repair, which is a train like any other, classed by its files (a repair to a check is
R3, to a proof R2, and takes that lane). The issue is closed with a link to a later run on
main in which all three jobs are green, and the release waits for that. The suite's tests
read the whole tree, content as well as code: the check inputs safe_push guards, the
workflows, this page, whose first command block they compare with the registry's render,
the registry itself, which they hold to safe_push's reading of it and the `check` job to
its one step, and content such as `heath/I/01.md`, the decisions page,
`docs/briefs/book-I.md`, `docs/program.toml`, `docs/reading.md` and `facts.json`, over
which they run `check_fidelity.py` and `render.py`; so any change can break them, and the
next run shows it. They need Git with the whole history and the pinned PyYAML, but no Lean
and no network; `FullChecks`, the one test that needs Lean, is skipped without
`STOICHEIA_SLOW_TESTS=1`, there as anywhere. Every job but `report` reads the repository
with no other permission, and its checkout keeps no token.

**The shards.** In one job, on the cadence, the whole suite took 72 to 78 minutes on
GitHub's runners, and 137 on a slow one; on as slow a runner it reached the job's limit,
then 150 minutes, and was cancelled there
([the decision of 23 October](decisions/2026-10-23-cadence-timeout.md)). So the workflow
runs it as eight shards side by side (#233,
[the decision](decisions/2026-10-24-safe-push-shards.md)): the `safe-push-shards` job's
matrix runs `python3 scripts/test_safe_push.py --shard K/N --ran FILE` for each K from 1
to N, N being written once in the workflow, in the matrix, whose `strategy.job-total`
each shard is given as N; each shard may take 60 minutes, and none stops the others when
it fails. Every test
runs in exactly one shard: `--shard` lists the tests with unittest's own loader, so that a
new test is never missed, and deals them out by the seconds each took on a GitHub runner,
kept in `scripts/test_safe_push_times.json`, the heaviest first, each to the shard with the
least time so far. The times were read from the CI run of #239 on 21 October, when the
suite had 288 tests; a test the file does not name, one added or renamed since, weighs their
median, and each shard's log names it. The proof is built from what the shards ran, not
from the dealing. Each shard writes the tests it ran, each with its outcome, to the file
`--ran` names, and keeps it as an artifact, a test having failed or not, for 35 days; and
it keeps its log, from which the report takes the tests that failed. Whether a later
attempt of the run can fetch a list an earlier attempt kept is GitHub's to say, and
nothing relies on it: a run re-run with "re-run all jobs" is judged afresh, and one re-run
with "re-run failed jobs", whose proof may not see the other shards' earlier lists, then
stays red, for the proof never passes on lists it cannot see. Then
the `safe-push-tests` job, which needs the shards and runs whatever they did, checks out
the commit they ran, as they did, fetches every list and runs
`python3 scripts/test_safe_push.py --cover DIR`, which lists the tests with unittest's
loader at that commit, reads N from the matrix, and fails, naming each, on a test no shard
ran, a test run twice, a shard that left no list (as one that stops before its end leaves
none), a test the loader does not list, and a test that did not pass. Its verdict is green
only when two things hold, each judged on its own: GitHub's result for the matrix is
success, which it is only when every shard succeeded; and the proof passed. A shard that
failed, was cancelled, stopped at its time limit or was skipped, or a list missing, makes
the job red, never skipped, and the run red with it. Both are needed: should a later
attempt see a list an earlier one kept, that list stays when, in a rerun of all the jobs,
its shard is cancelled before it keeps a new one, so the proof alone could pass; and the
matrix's result says nothing of which tests ran. To run one shard as the cadence does, give its
number and the count, as in `python3 scripts/test_safe_push.py --shard 3/8`; without
`--shard` the whole suite runs.

`scripts/safe_push.py` runs the commands for `check`, `model` and `negative` above on the
head commit of every pull request of R3 to R5 (section 10): those of `check` as
origin/main's registry lists them, so a change to them is a change to `checks/` alone; those
of `model` and `negative` from lists of its own, so a change to them is made there too, and
in the CI workflow, but for `python3 -I tests/model/results_check.py`, which only CI's
`model` job runs until the command joins safe_push's `MODEL_JOB`. For R0 to R2 it leaves
them to CI, which runs those of
`check` and `model` on the pull request before the merge. It leaves the `formal-model`
job to CI on purpose, since it fetches
Mathlib's prebuilt files ([model/README.md](../model/README.md#the-ci-job)), the
`acceptance` job, since it builds main beside the pull request, and the `safe-push-tests`
job, whose full suite would hold up every pre-flight. Its merge gate refuses when any
reported check fails, is cancelled or is still running, apart from the `release-gate` job
of the "Release gate" workflow on an ordinary pull request, even if a run remains from
before its `release` label was removed. It requires a passing run of each of the five
checks that main's ruleset requires, `check`, `model`, `negative`, `formal-model` and
`acceptance`, the names in its `REQUIRED_CHECKS`: a required check that is missing, or
whose every run was skipped, holds the merge. `safe-push-tests` runs on no pull request,
so it holds no merge, unless it is dispatched on a pull request's branch; a red run of it
holds the release instead, and a release's merge needs a green run of it at the release's
own head. GitHub uses the ruleset when merging. The workflow no longer
runs on branch pushes, and `acceptance` runs on every event it does run on; GitHub would
still accept a skipped job even when it is required ([GitHub
documentation](https://docs.github.com/en/pull-requests/reference/status-checks)). The
merge gate does not count a skipped run as a pass, so it waits for the pull request's own
run of `acceptance` to pass. The ruleset and the remaining merge requirements are in
[section 10, "Landing work: pull requests"](#landing-work-pull-requests).

On pull requests and post-merge main runs, `queue-integrity` installs the pinned YAML
parser with which the offline cases read `ci.yml`, then runs the offline cases in
`tests/test_check_queue.py`, `tests/test_check_train.py` and `tests/test_auto_revert.py`,
each with `python3 -I`; on a merge group it installs nothing, so the Python that runs the
judge holds nothing a group names. Locally, install the parser in a virtual environment
outside the tree (a system Python may refuse the install, and `python3 -I` does not see a
user install), then run what CI runs:

```sh
python3 -m venv "${TMPDIR:-/tmp}/stoicheia-queue" && . "${TMPDIR:-/tmp}/stoicheia-queue/bin/activate"
python3 -m pip install -r scripts/requirements-test_safe_push.txt   # CI's `queue-integrity` job
python3 -I tests/test_check_queue.py
python3 -I tests/test_check_train.py
python3 -I tests/test_auto_revert.py
```

On a merge group `queue-integrity` is the queue's judge: it takes `scripts/` from the
group's base and runs that `check_queue.py` with the event's head, base and repository,
running none of the group's scripts and building and rendering nothing, though GitHub
runs the group's own copy of this workflow file (section 10 says what must hold it).
`queue-gaps` waits for acceptance and, on a merge group, chooses the tests of what the
group changes in a step that holds the job's token, to read GitHub, and runs none of them
(`--gaps --plan`); its last step, which holds no token, runs them (`--run-plan`).
Section 10 gives the rules. The `check` job renders the same group and checks the pages
are current, and its `check_queue.py --tree .` step, which the pre-flight runs too,
checks the decisions page line by line as section 10's rule (d) describes; conflict
markers in tracked text are S23's, in `scripts/check_style.py`. The train and queue
checks need Git 2.42 or later (`merge-tree --write-tree` came in 2.38, its
`--merge-base` in 2.40 and `--attr-source` in 2.42); with an older Git they refuse every
train and group as unreadable.

- **Negative tests run in isolation.** `python3 scripts/negative_tests.py` plants breaks in
  the source and builds them, so it runs in a disposable worktree or its own CI job, never
  beside other contributors' builds in a shared tree. Each break is a plant, a file of its
  own, `scripts/negative/<name>.py`, its name lower-case letters, digits and underscores,
  beginning with a letter: its description as the module docstring (what it plants, which
  check must refuse it and what that check must say); `import negative_tests as nt`,
  through which it reaches the shared helpers (`nt.ROOT`, `nt.replace_once`,
  `nt.expect_failure` and the others); `BUILDS`, True only when it runs `lake build`; and
  `def plant() -> None:`, which plants the change, in the real files or a copy of them,
  runs the check and puts everything back in `finally`. To add a plant, add one such file;
  no other file of the suite is edited, for there is no number to choose and no list to
  edit. The suite lists the folder and runs the plants that do not run `lake build`, by
  name, before those that do, by name, each named with its file and timed. Run one alone
  with `python3 scripts/negative_tests.py --plant <name>`, which keeps the check that the
  work tree returns to its entry Git status, and closes by saying how many of the plants it
  ran. The suite fails, naming the file, on a file that does not load, on a file that
  changes a name of the runner or of the modules it shares as it loads or as its plant
  runs, on a `plant()` that changes the failures or refusals recorded before it, on a
  `plant()` that raises `SystemExit`, after which the run goes on, and on a plant whose
  change no check refuses; the names are looked at once more after the closing check of
  the tree, where a change fails the run with no file to name. That last guard catches a plant that runs no check, or returns before its
  first; it does not catch one that calls `nt.refused` with no check behind it, nor one
  that drops some of its cases, so review still reads each plant's cases. The guards
  catch a mistake, not a file written to deceive: a plant's file runs in the runner's
  process with its full power, so the security review reads each plant's file as code of
  the runner. They do not see a shared object changed in place other than those two lists
  (a helper's `__code__` replaced, a dict of a helper module changed), nor a process ended
  by `os._exit` or a signal, which is not caught in process and leaves with the status it
  chooses; review reads each plant's file for them. Like any file under `scripts/`, a
  plant's file is a protected path ([section 10](#landing-work-pull-requests)): the pull
  request that adds, changes or deletes one names it, by its whole path, in a new decision
  entry ("Decision entries", in section 10), carries the label `security-review` and
  records a `/security-review`.
- **The model tests read the lock.** `tests/model/laws.toml` names a law for each axiom of
  `Certificate/axioms.lock`, and `tests/model/lock.sha256` pins the lock's hash, so a
  change to an axiom fails the `model` job until the model follows it, in the same pull
  request: [MODEL.md, "Changing the axioms"](../tests/model/MODEL.md#changing-the-axioms),
  says how.
- **The model's results name their harness.** Each file in `tests/model/results/` names
  the commit it was written at, with the harness files as committed, and the hash of the
  harness that wrote it (`HARNESS` in `tests/model/run.py`), and MODEL.md's counts name
  the same commit. `tests/model/results_check.py`, which is not a file of the harness,
  fails when the harness now hashes otherwise, when a run read harness files other than
  its commit's, when the runs' output is what `run.py` refuses to write, or when
  `summary.txt` and the counts are not what `--write` makes of the runs' output. So a pull
  request that changes a harness file commits the change, runs
  `python3 -I tests/model/run.py --full --write` on it (about eight minutes) and commits
  what it writes, in the same pull request; its decisions entry names each file the run
  changes. `--write` runs from a copy of the harness taken out of git at the commit, so
  what it writes is that commit's harness's. Apart from its self-test, which runs `run.py`
  on a made-up harness of its own, the check runs no harness, so it cannot tell a header
  written by hand from a run's, and the output records no exit status, which only
  `--write` sees; the security review, which every change under `tests/` gets, reads the
  results' diff.
- **The citation sweep reads the build.** `python3 scripts/sweep_citations.py` elaborates
  a copy of each file of `Elements/` with Lean's unused-variables linter and its tactic
  analysis on, and reads every entry's proof term, so it needs `lake build` and
  facts.json; `Staging` and `Audit` it reads when named, after their builds, though the
  linter passes over any declaration with a `sorry` in it, even one that never runs, so a
  staged statement gives no hit until its proof arrives; outside Staging, a file with
  `sorry` or `admit` in its code is refused. Its `--self-test` plants each kind of hit,
  and controls that must pass, in Lean outside the tree. CI's `check` job runs both sweep
  commands for every risk class, after `test_certificate.py` and before the whole-worktree
  cleanliness check; the sweep there only lists, and the release gate (section 10, step
  10) runs it with `--fail-on-undeclared`.
- **Staging builds; it is not proved.** `lake build Staging` checks that the statements
  staged before their proofs (section 2), each with `sorry` where its proof is due, still
  build against the library they import. It builds every file under `Staging/`, whether or
  not the root `Staging.lean` imports it. Their `sorry` warnings are expected and do not
  fail it; nothing the certificate reads imports them.
- **A contributor's subset.** Working on a proof, run the full `lake build` first (the
  certificate imports all of `Elements`), then `Certificate/Facts.lean`, `check_fidelity.py`
  and `check_style.py`; a stale record is expected (section 6), and the pages are the
  integrator's.
- **A guard defect gets a regression.** When a certificate or check defect is fixed, add a
  focused test that shows the defect would now be caught (a negative test, an entry in
  `tests/certificate_expectations.json`, or, for the style check's reading of a phrase or
  of a figure, a case in `tests/test_check_style.py`). Tests that only repeat a trivial
  prose change are not added. `CommentReaderTests` in `tests/test_negative_tests.py` holds
  the cases for the Lean-comment reader shared by the fidelity check, the style check and
  the Jev question generator; `negative_tests.py` runs that file before it plants faults.
- **The certificate's cases need built foundations.**
  `python3 -I tests/test_certificate.py` checks C.N. 4 detection directly, through helpers
  and through transformers, with negative controls for derivations that supply no step,
  while keeping the axiom fields unchanged. It rejects reached helpers from
  `Staging.Hidden`, and from a `Lean.Hidden` compiled outside the Lean toolchain, while
  allowing unused imports from foreign modules and reached declarations of the
  toolchain's own. It reads `construction_rules` from a fixture's own axioms, one for each
  case of the [definition](FORMALIZATION.md#construction-rules), counted or not as it says,
  and `cited_laws` from entries that cite laws through one shared theorem or law by law,
  each law with its proofs and the construction rules beneath them; a proof reached only
  through another entry is not found, and a law named with no proof found fails the run.
  Without Lean, it reads the forms of `tests/certificate_expectations.json` as
  `check_fidelity.py` does, and an expectation that is malformed, unmet or asks nothing
  fails. It needs the
  foundation modules built by `lake build`, with the Lean tools on `PATH`. CI's `check`
  job and the pre-flight run it immediately after `Certificate/Facts.lean` on the revision
  delivered.
- **The style check's cases run before it.** `tests/test_check_style.py` puts the readings
  of `scripts/check_style.py` that [STYLE.md](STYLE.md), section 8, names to short texts
  and small figures, including S20's ink and S26's clearance and repeated letters, each
  with the finding the rule should make, and needs no Lean.
  It runs before the script, so a rule that reads a case wrongly stops the checks
  before the script's findings are read. The script does not run them itself: whoever
  changes it runs the file too.
- **The release gate's cases need no Lean and no network.**
  `python3 -I tests/test_release_gate.py`, immediately after the style check's cases,
  checks the unfinished work section, the issues' state and labels, pagination and
  unreadable replies, and that an ordinary pull request skips the release hold; fixtures
  and stand-ins supply every reply.
- **The Jev client's model check needs no key and no network.**
  `python3 -I tests/test_jev_models.py`, immediately after the release gate's cases, checks
  that `scripts/audit/jev.py` refuses an answer without its model's identifier when it
  runs, scores and resumes, with in-process replies standing in for the service.
- **Three more sets of cases follow, each with no Lean.**
  `python3 scripts/audit/jev.py self-test` runs every command of the Jev client against a
  stand-in for the service on this machine, with a key it makes up, and needs no network
  and no key; it checks, among other things, that the key appears in no output.
  `python3 -I tests/test_screen.py` puts the overlap screen's own functions
  (`Audit/screen.py`) to small inputs: the tries it makes and its reading of Lean's logs.
  The screen itself needs Lean, takes minutes, and is not run by CI.
  `python3 -I tests/test_acceptance_limits.py` checks the limitations that acceptance item
  P3 allows against [ACCEPTANCE's table](ACCEPTANCE.md#the-limitations-allowed), and P3
  itself on review records varied in memory. The Jev question generator's tests,
  `python3 -I tests/test_jev_questions.py`, are not in the sequence, for one of them
  checks out a commit of 19 October, `39ae65c2`, which the `check` job's checkout, one
  commit deep, does not hold. Two more of them now fail at any depth, on main too, at the
  I.40 mutation anchor; their repair is card #350. The file can join a job with the whole
  history once those failures are repaired.
- **The restriction's theorems are pinned by their statements.**
  `python3 -I scripts/check_superposition_pins.py` checks that every theorem and definition
  brief 0009's section "The restriction theorem" names has a statement pin in
  `Audit/Superposition.lean`, under its full name in `Elements.Superposition`, its one
  namespace (a pin of the same name in another, such as `Elements.BookI`, does not count):
  an `info:` docstring, a bare `#guard_msgs in`, then `#check` for a theorem, or `#print`
  for a definition, since `#check` shows only a definition's type. The two definitions the
  section names, `Rule.Figure` and `Interpretation.Embedding`, are held to `#print` by name:
  each counts as pinned only by its `#print` pin, which it must have, and a `#check` pin of
  either is refused with its line, whatever it prints. A `#print` pin shows one level and
  does not pin the definitions its body or fields name, so each of the two must also open
  its print as Lean's does today, `Rule.Figure` with `def` and `Interpretation.Embedding`
  with `structure`: `Embedding` cannot become a `def` that names a new structure, though
  `Rule.Figure`'s body could still name a new definition. Any other `#check` pin is refused
  with its line when Lean's print of its type, in the docstring, ends in a sort or opens a
  binder with an arrow, as in `{P : Type} →`, where a proposition has `∀`: either shows a
  definition. These signs are only a backstop for a definition the section names later,
  since a sort spelt through a name, as in `id Type`, prints as written and shows neither.
  A theorem's pin must use `#check @`: a `#print` whose Lean header says `theorem`,
  including after attributes or declaration modifiers, is refused with its line, as is an
  unrecognized printer header. `Placed`, `Val.place` and `Metric.names`, which theorems the
  section names read, must have `#print` pins too. A statement pin whose docstring holds
  `⋯` or `[...]`, where Lean
  cut its print short, is refused with its line, wherever the option that cut it was set;
  an option that hides part of a print with no mark, such as `pp.piBinderTypes false`,
  could be set only outside the file, in the lakefile, a protected file, so that protection
  holds it off, not this check. A pin inside a line, block, nested or module comment, which
  Lean never runs, never counts, and is refused with its line wherever the script reads it
  as a pin (one with an inner comment between quotation marks can escape the refusal, and
  still counts for nothing); ordinary comments remain allowed. The file may hold nothing but its leading imports, ordinary comments and pins
  (a docstring, a bare `#guard_msgs in`, then `#check @`, `#print` or `#print axioms`);
  anything else is
  refused with its line, such as a `set_option` of any kind (some shorten what Lean
  prints), a namespace (a theorem in it can take a pinned name), any declaration, `#eval`,
  `#exit` or a `#guard_msgs` with options. `Audit.lean` must import the file, or
  `lake build Audit` does not run its pins. That build checks that each pin is what Lean
  prints; the script checks that the pins exist and that nothing in the file changes what
  they print or name, so that a theorem the brief names cannot be weakened under the same
  name with only its axioms pinned, or with only a pin of that name in another namespace,
  nor any of the five definitions above changed under a pin of its type alone. Its cases,
  `python3 -I tests/test_check_superposition_pins.py`, need no Lean and run first.
- **Counts in prose.** A count a script knows exactly goes between count markers and is
  rendered; the surrounding prose stays human ([STYLE](STYLE.md), section 4).
  `check_fidelity.py` refuses stale values before rendering; `tests/test_generated_counts.py`
  tests the counts and markers without Lean. Count markers do not overlap README.md's
  generated scope regions or PROGRAM.md's generated status region. `negative_tests.py` runs
  the tests before planting; its `--counts-only` option runs the count plant,
  `scripts/negative/count_markers.py`, and the file-only regressions without a build.
- **Decision entries are checked before anything is written.** `render.py` refuses a bad
  file in `docs/decisions/` (section 10, "Decision entries") before it writes, so CI's
  `check` job and the pre-flight refuse it. `tests/test_decision_entries.py` tests those
  refusals without Lean, and `negative_tests.py` runs it after the count regressions,
  before planting, with `--counts-only` too.
- **The risk classes are tested without Lean.** `tests/test_risk.py` checks the table of
  `scripts/risk.py`: the first rule that matches wins, a path no rule names is R5, and a
  change takes its highest class. It runs `--diff` on a repository of its own (an empty
  diff, a workflow changed, a path with a space, a path with a line break, printed escaped
  so that no path can start a line of CI's log, a file moved, a submodule moved) and
  `--audit` over this repository's tracked files, every one of which a rule must name. It
  tests the formal model's inputs: the forms of a Lean header the classifier reads, those
  it cannot read and imports it cannot resolve, each of which then runs the model for
  every change; the files a model imports, directly, through another, or deleted by the
  change, on a repository of its own; and this repository's,
  `Elements/BookI/Prop07.lean` among them, whose every header and import it reads.
  `negative_tests.py` runs it after the decision entry regressions, before planting, with
  `--counts-only` too.
- **The lock is written again as it is committed.** `check_fidelity.py --write-lock`, run
  on the committed `facts.json`, must give back `Certificate/axioms.lock` byte for byte, its
  header included, for `model/lock.sha256` and `tests/model/lock.sha256` pin its bytes.
  `tests/test_axiom_lock.py` tests that without Lean, and `negative_tests.py` runs it after
  the risk class regressions, before planting, with `--counts-only` too.
- **Record the revision and the outcome** of each command. A command not run is not a
  passing check. A build that passed on a contributor's branch is evidence about that
  branch; if integration changes the mathematics, the dependencies or a public description,
  the affected checks and reviews are run again.
- **Keep it proportionate.** A wording correction needs the source and editorial checks; a
  changed representation may need many consumers checked.
- No `lake update` or `lake clean` in a shared tree.

## 9. Release criteria and severity

The acceptance checklist ([ACCEPTANCE.md](ACCEPTANCE.md#where-the-older-criteria-went))
incorporates the criteria below. A proposition meets these criteria when:

1. its reviewed brief and its final formal statements agree;
2. every substantive clause, and its porism, is proved or exactly qualified;
3. the intended cases are covered, and construction inputs and outputs are right;
4. each representation it relies on has the correspondence results its claims need;
5. the route shown is accurate, and every exception is visible;
6. the dependency closure, the axiom boundaries and the certificate cover every formal claim
   published;
7. quotations and attributions are checked, and the commentary explains this proposition
   accurately;
8. changed figures and the page have been inspected;
9. the required checks pass on the integrated revision;
10. a reviewer other than the author has assessed the changed mathematical claims, and the
    record names the reviewer and the commit.

**Severity** decides what must be corrected:

- **Blocking:** an invalid or wrongly scoped formal claim presented as full; an unresolved
  dependency presented as closed; an unapproved change to the foundations; a materially
  false certificate.
- **Material:** an unmarked alternative argument; a hidden omission of a clause; an
  unsupported claim about a representation; a misleading figure; a wrong quotation or
  attribution.
- **Editorial:** repetition, awkward prose, excess detail, or inconsistent formatting that
  does not change the meaning.

Blocking and material findings are resolved before the affected claim is presented as
complete. A score may sum up a review; it cannot cancel a defect. A few deliberate
limitations can stand in an excellent edition when each is stated plainly where it occurs. An
accepted limitation names a deliberate boundary; it never stands in for a defect nobody has
looked into.

## 10. How a book is made and released

1. **Ground.** Heath's text is transcribed from the scans and checked against the page
   images; the scripts and the certificate are taught the new book.
2. **The brief**, its definitions and its ground lemmas, approved (section 2).
3. **Statements** with `sorry`, each with its review record at the stage `exceptions`
   ([schema](../review/SCHEMA.md)): the statement's scope, the route expected, the
   representation and every exception known, written by the statement's owner; then
   scratch proofs, challenges to the statements and their records, and the orders.
4. **Voyages:** fleets prove the book in parallel (section 5). Book III's thirty-seven
   propositions took two fleets of four ships.
5. **Close-out:** the figures at a glance, the gap catalogue, the book's introduction, the
   reading lines, a decisions entry, the scratch proofs retired, and the logs.
6. **One voice** (section 7).
7. **Review records** completed: each record written in step 3 is read again against its
   finished proof (section 6), and every one reaches the stage `full` before acceptance.
   Books I, II and III are at `full` in all their records (Book III's are #29).
8. **The page read-through and the stale-content audit.** Before every release or
   consolidation, readers go through the rendered pages as visitors, as section 7 requires.
   Separately, before every release and at the end of each programme stage, the coordinator
   assigns an independent reviewer a stale-content audit: every hand-written repository
   file, the wiki pages and open issues, oldest untouched first. Generated output is
   excluded only from this audit, because it is regenerated; it remains part of the page
   read-through. Dated history (crew logs and dated review responses) records its day and
   is not brought up to date.
   Keep a dated report under `docs/reports/`, naming the revision read and indexing the
   files by last change; each finding gives `file:line` (or wiki page/issue), the stale
   text, evidence on main, what it should say, and its train or pull request.
   Separate claims false now from those queued work will make false: fixes belong in
   the train or pull request that makes them true; future findings are checklist rows
   for that work, not edits now. Wiki and issue reading is read-only; changes need the
   owner's OK.
   Each finding falls in one of four tiers, which say when it is fixed:
   - **Tier 0, defects:** a merge-conflict marker, a broken link, the owner's name, a
     claim the Lean contradicts, a failing check. Never on main: fixed at once, and
     refused by a check wherever a check can see it.
   - **Tier 1, generated facts:** counts, status tables, the acceptance report, the
     certificate. Never written by hand: generated from their source, and refused when
     stale.
   - **Tier 2, reader prose:** true at release. Fixed in the train that changes the fact,
     or at the latest in the release's own pull request.
   - **Tier 3, working records:** briefs, reports, issues and the tracker. Dated: a record
     that later work overtakes gains a dated status note, never a quiet rewrite, and the
     issues and the tracker are kept current.
9. **Acceptance:** from brief 0005's stage 6, the checklist passes in CI with no failures,
   the independent audit agrees, and a cold outside reading passes the gate of the
   [review rubric](RUBRIC.md). The switch from the ratchet to the full gate is described in
   [ACCEPTANCE, "In CI"](ACCEPTANCE.md#in-ci).
10. **Release.** A release waits for its gate: both the page read-through and the
    stale-content audit of step 8 on the release candidate, with every Tier 0 to 2 finding
    from the audit fixed in the release's pull request and every Tier 3 record given its
    status note; no open issue labelled `blocks-release`
    (unfinished work, a prototype or a provisional answer may be on main only as such an
    issue, and holds every release until it closes); the citation sweep, `python3
    scripts/sweep_citations.py --fail-on-undeclared`, passing on the release candidate,
    with each hit fixed or declared in its record; and the wiki refreshed, so that it is
    reasonably correct as of its date, as its pages say, and is not expected to be more
    current than that. The hold is checked by `python3 scripts/check_release_gate.py`, by
    the `release-gate` job on the release's pull request, and by `git safe-push --merge`,
    which refuses a pull request labelled `release` while any issue or pull request
    labelled `blocks-release` is open, or when GitHub cannot be read. That merge also
    needs the full pre-flight of the release's head, which its label makes R5, and a green
    run of the `safe-push-tests` workflow at that exact head, each of its jobs passed, the
    shards among them, but `report`
    (`gh workflow run safe-push-tests.yml --ref <branch>`; section 8), the head's copy of
    that workflow being origin/main's: a change to it lands first, in a pull request of
    its own. The `release-gate` job runs on the
    pull request's events, not the issues', so once the last blocker closes it is run
    again (or `release` removed and given again) before `--merge`, which counts its failed
    run on a release pull request. Before that `--merge`, and after every other change the
    release's pull request carries, two generated accounts are made again at its head, and
    what they write is committed to it. The model's full run,
    `python3 -I tests/model/run.py --full --write`, writes `tests/model/results/` and
    MODEL.md's counts. After `lake build`, the overlap screen,
    `python3 -I Audit/screen.py OUTDIR --write`, runs on the candidate's statements and
    rules and writes `Audit/screen-run.toml`. Before it replaces that record, it checks the
    build again, after every try and retry, and reads the commit and the inputs again; a
    failed check leaves the record as it was. Checks at the two ends of a run cannot show
    that nothing changed and changed back in between. Then
    [overlaps.md](reports/overlaps.md) and the screen's docstring record the revision
    screened, the number of statements in `facts.json` and what closed. Then
    `python3 -I tests/model/results_check.py` and
    `python3 -I Audit/screen.py --check-current` both pass: CI runs the first on every pull
    request, and the coordinator runs the second on the head that `--merge` merges and
    again just before the tag, and the pull request quotes the screen's closing lines. The
    screen's check needs no Lean, but any change to the library makes it fail, and only a
    run, with Lean and about an hour and a half of processor time, may make it pass again;
    so it is a release step, not one of CI's. The check reads the record, not the run, so
    it cannot tell a record written by hand from a run's, and the security review reads the
    run's closing lines, which the pull request quotes. `Audit/` and `tests/` are
    protected, so the release's decisions entry names each file the runs and their records
    change: the ten files of `tests/model/results/`, `tests/model/MODEL.md`,
    `Audit/screen-run.toml` and `Audit/screen.py`. Then the notes are drafted from the
    generated summaries, the owner approves them, and the tag (`book-I`, `book-II`, …) is
    made.
    `python3 scripts/check_release_gate.py` runs once more just before the tag, since the
    hold rests on the labels. PROGRAM.md is brought up to date: the status board, the
    lessons, the costs.

A released book is not frozen. Its tag keeps the released text, and main carries the
corrections and the common voice, as Books I and II have since their tags.

### Landing work: pull requests

Work reaches main only as a pull request, merged with a merge commit. On GitHub, a ruleset
on main requires a pull request and the checks `check`, `model`, `negative`,
`formal-model` and `acceptance` (the last two added on 20 October 2026), and blocks force
pushes and deletion. When the owner enables the merge queue, the owner adds
`queue-integrity` and `queue-gaps` to those required checks; the queue is off until then,
and the coordinator holds the setup steps below. Locally, the pre-push hook refuses
every push to main. Agents
never open, merge or approve a pull request: the coordinator does. The account cannot
approve its own pull requests, so a merge is gated by the checks and by the review
findings recorded in the pull request, not by approvals. Tags, releases, release notes,
the GitHub description and anything sent outside the repository still need the owner's
OK, and stay manual.

**One coherent change per pull request,** that a reviewer can hold in mind: a stretch of
proofs, a wording pass, a guard. A check is never changed in the same pull request as the
code it checks: the check lands first, on its own, and the code follows it. The pre-flight
holds to this: when a check fails with origin/main's copies, the pull request may change
nothing else the checks judge (step 4, below). A change to what `render.py` writes is not
a check change in this sense, since the pages it regenerates show it; a change to what it
accepts, such as its check of `docs/program.toml`, is. Each pull request carries a label
for its kind, `tooling`, `text`, `lean` or `docs`, and the pre-flight and the merge refuse
one without; stage work carries its stage's label as well (`stage-2` to `stage-6` of
brief 0005), and a change to a protected path carries `security-review`. A pull request
opens as a draft (unless `--ready` is given), and is marked ready when its reviews are
done; `--merge` refuses a draft.

**Unfinished work may land on main, with its issue.** Each piece, a prototype, a
provisional answer, a restricted or partial scope awaiting a proof, a deferred page, a
test not yet in CI, anything a disclosure calls "to come", has an open issue labelled
`blocks-release`, named as `#N` in the pull request's "Unfinished work" section; when
there is none, the section says "None". Each list item names at least one issue. These
issues hold the release until they are closed, as the owner's rule of
[20 October 2026](briefs/0002-decisions.md#20-october-2026) says. The release lands
through a pull request labelled `release`; `git safe-push --label release` creates that
label, with its description, the first time it is given, as it does the others.

**Trains.** Since every pull request must be up to date with main before it merges, and
nearly every one touches the generated pages, reviewed branches can land together, as a
train (the owner, 18 October 2026). A train is a branch `train/<area>-<n>` that gathers
reviewed branches as merge commits, each member already one coherent change with its own
checks and reviews, so history keeps each change whole. Each member brings its decision
entries as files of its own ("Decision entries", below), so they merge side by side,
untouched; the coordinator resolves the decisions page only for a member opened before
entry files that added its entry there, and regenerates the pages once. The train passes
the pre-flight of its combined head and CI once, and merges as one pull request, whose
body lists each branch with its reviews (the `Members` table below) and the issue it
closes. Once the owner turns the merge queue on, several trains may enter it together
(below). A train never carries a check change together with content that check judges:
trains of checks and trains of content are separate, and this rule refuses the
combination even when origin/main's checks pass. A branch that fails the train's
pre-flight leaves the train.

The train's `--body-file`, required on a dry run and on every update too, has the usual
pull request sections and two more, `Members` and `What is new`. `Members` is a table
with the columns `Branch`, `Head`, `/code-review`, `/security-review` and `/no-mistakes`,
one row per member. `Head` is 12 to 40 lower-case hexadecimal digits naming the member
head merged. Each `/code-review` and `/security-review` cell names the commit its review
read, by 7 to 40 lower-case hexadecimal digits that a reader sees (not in an HTML tag or
comment, or a link's destination), with the findings, and that commit must
be one of the member's own: the member's head, or an ancestor of it not on origin/main,
named unambiguously by digits that begin its name (as `git rev-parse --verify
<digits>^{commit}` resolves them; a ref whose name is hex digits does not count). Other
digits in the cell, a coordinator's commit or a run's, may stand beside it. A cell that
is only a placeholder ("not run", "awaiting review", "skipped" and their like) refuses,
and so does one that holds, anywhere, in any case and beside the member's commit too,
"pending", "TBD", "to come", "not needed" or "N/A" ("Pending items: none" among them);
a finding that merely begins with another placeholder's words ("To do so, ...", "Later
commits ...") does not. `/security-review` may instead say "Not required", and only
if no protected path changed, read against every merge base of
the member with origin/main; a member that changes a protected path must name its
commit there, and its cell may not say "Not required" anywhere, in any case or
spelling. Beyond that, the cells are the coordinator's words: the check reads that a
review of the member is named and that some visible verdict or findings stand beyond the
commit name and its punctuation or markup. It imposes no verdict vocabulary or prose
length. `/no-mistakes` says
`passed at <head>` for that same member head, or `not run: <reason>`, with at least
five words giving the reason.

`What is new` says `None.` or gives bullet lines of these forms:

```text
- check: scripts/check_queue.py
- check: tests/test_check_queue.py
- rule: trains go through the merge queue
- propositions: I.5, II.3
- foundations: Elements/Foundations/Plane.lean
```

Every changed file under `scripts/`, `tests/` and `.github/` needs a `check:` line.
Every changed proposition, whether in its Lean, review record, Heath text, commentary
or figures, is named under `propositions:`. Every changed file under
`Elements/Foundations/` or `model/`, and `Certificate/axioms.lock`, needs a
`foundations:` line. More may be declared; an omission refuses. Rule prose is written
by the coordinator, since a file diff cannot derive it.

At the pre-flight, origin/main's `scripts/check_train.py` reads the train's own
first-parent chain and checks that each member was merged exactly once and has exactly
one row; that each of the train's merges has two parents and adds or resolves nothing
outside the generated files (README.md and PROGRAM.md only between their markers) and
the decisions page; that the train's own commits change only those; and that the
evidence, separation of checks from content, and declarations hold. Git's automatic
merge, to which each of the train's merges is compared, reads merge attributes from
origin/main, never from the checkout or a member's `.gitattributes`: a member's
`merge=union` cannot make a resolution by hand count as automatic. A member's own
history, a merge of main into it with its resolution included, is the member's, judged
by its reviews. Decisions here are the page and, when origin/main's tree has a
`docs/decisions/` directory (tooling/decision-entries brings it), the Markdown decision
entry files directly under it; while origin/main has none, an entry file is refused like
any other path. A merge of main needs no member row, but its tree is checked too.
While origin/main has no `scripts/check_train.py`, every train is refused, one that
adds the checker too: no commit's own copy ever judges it, so the checker lands first,
as an ordinary pull request. An unreadable checker or a refused train stops the
pre-flight. `--body-file` is read once, as UTF-8, before the checks: the train check,
the dry run's body and the body posted are that same text. `--merge` runs the train
check again, in both modes, on the pull request's current body, and refuses if a later
read of the body, by the gates, by the merge's own read or by the last gates before the
merge, differs from the text checked.

**Building a train that passes.** Start the train from origin/main, never from a
member. Merge each member once, at its final head, after its reviews and `/no-mistakes`
have run on that head; if a member moves, build the train again from origin/main rather
than merging the member a second time. A merge of origin/main into the train is
allowed, and its tree is checked like the members' merges. The train itself resolves
and adds nothing beyond the generated pages and the decisions page. A conflict between
members, or between a member and origin/main, and a review record's stamp of a member's
change, are made in a branch that contains the sides it resolves or stamps: merge
origin/main, or the other member, into the member, resolve or stamp there, and review
that head, with its own `/no-mistakes`; the train then merges it, with one row (a
member it contains may still be merged before it, with its own row). A branch from
origin/main cannot hold them: a resolution made there conflicts again when
the train merges it beside the members, and `scripts/review_stamp.py` stamps a record
with the hashes of the files in the checkout it runs in, refusing a `--commit` whose Lean
file differs. A stamp or an edit that stands alone, touching no file a member changes,
may come from origin/main: a branch of its own, with its own reviews and its own
`Members` row, merged like the others.
Then regenerate and commit the generated pages, and write the body: `Members`, one row
for each member merge, with the head merged; and `What is new`, covering at least what
`derive_new` in `scripts/check_train.py` gives for origin/main to the train's head,
which this prints, with the rule lines the coordinator writes:

```sh
python3 -I -c 'import sys; from pathlib import Path; sys.path.insert(0, "scripts")
import check_train; print(check_train.derive_new(Path("."), "origin/main", "HEAD"))'
```

`git safe-push --branch train/<area>-<n> --body-file <path> --dry-run` then runs the
same train check as the push.

**Splitting a train by risk.** A train takes the highest class among its files, and its
class sets its checks (section 8, "What runs for each class, at each stage"): one script,
workflow or foundation file in a train of records makes the whole train R3 or above, and
its pre-flight the full one. So the coordinator gathers branches by class: docs, text,
records and proofs (R0 to R2) in trains of their own, which land in minutes, and checks,
foundations, the landing tool and CI (R3 to R5) in others, which take the full pre-flight
and the longer CI. A branch whose files fall on both sides is split in two, as a check
change already lands apart from the content it judges, the check first.
`python3 scripts/risk.py --paths <file>...` gives a file's class before the work
starts, and `python3 scripts/risk.py . origin/main` a branch's.

**Adding a check.** A check of CI's `check` job is one file in `checks/` (section 8, "The
registry of checks", and [the folder's README](../checks/README.md)). The train that adds
one carries that file, section 8's command block as `render.py` regenerates it, and a
decision entry naming the file in a sentence of its own; it is R3, and touches neither
`scripts/safe_push.py` nor the CI workflow, so trains that each add a check no longer edit
those two files, and a conflict in the block they both regenerate is settled by rendering
it again. Removing a check, or changing its command, job or order, is a change to
its one file, named the same way. The train's CI runs the train's own registry, the new
check with it, while its pre-flight runs origin/main's whole registry, without it, in both
passes: the check joins the pre-flight at its merge, and judges the trains after it
there. A command of another
job (`model`, `negative`, `formal-model`, `acceptance`) is still a step of the CI workflow
and, where the pre-flight runs it, a line of `scripts/safe_push.py`.

**The merge queue.** The queue is off until the owner turns it on ("Turning it on",
below). Its judge, `scripts/check_queue.py`, landed first, in a pull request of its own,
so that the change that brought in the post-merge workflow, the automatic revert and
`safe_push.py`'s queue mode was reviewed against it
([20 October 2026](briefs/0002-decisions.md#20-october-2026)). That change landed as an
ordinary pull request, which the judge does not see: it runs only on merge groups. CI
runs on `merge_group` as well as on pull requests, so that every required check reports
on a group; without that, every group would time out and leave the queue.

Once the queue is on, GitHub makes a group for each queued train: main plus the trains
ahead of it, then that train, in queue order. Several passing entries can be batched
into a push to main. CI runs the integration checks on each group and the
`queue-integrity` job runs `scripts/check_queue.py`, taken with the scripts beside it
from the group's base, main, never from the group, in a job that runs none of the
group's scripts (it builds and renders nothing): a train's scripts cannot change the
checker that judges it, and the job fails while main has none. It refuses an unreadable
input, record or GitHub answer. But GitHub runs the group's own copy of the workflow
file, so the judge's verdict, and any check of the pre-flight's evidence added to it,
counts only while the group's `.github/workflows/ci.yml` still calls it: a group that
changed the job's step would pass unjudged. So the protection of `.github/`, `scripts/`
and `tests/`, and the authenticity of the pre-flight's evidence, must be held by
something a group cannot change: a ruleset requiring code-owner review, with a
`CODEOWNERS` file naming the owner for those paths; a required workflow pinned to main,
if the account offers one; or a status posted by an App that runs main's code. The
queue must not be turned on until one exists; the owner chooses which. Its four rules
are:

- **(a) No change overwritten.** Each train's change is reverted from the group tree and
  applied again, by three-way merges, and the result must be the group's tree on every
  path the rule covers: so a later train that restores, removes or re-adds what an
  earlier one changed is caught, as well as one that alters it. When a train has more
  than one merge base with the group's base, after criss-cross merges, each is used, and
  each must preserve the group. Generated files are checked by regeneration instead. For
  the decisions page, every line the train adds must remain in the group's page in the
  same order.
- **(b) Nothing unchecked.** Each entry has one visible pre-flight block naming exactly
  its head, the base it was compared against and the harness: the main commit whose
  `scripts/safe_push.py` ran it (the pre-flight names its base as its harness; the judge
  also accepts a later main commit). The
  base must be the newest commit of the group base's first-parent chain that the head
  contains, which is what safe_push records (origin/main's tip when the pre-flight
  ran), so an old base cannot be named for a head built on a newer main; the harness
  commit must be that base or a later commit of the same chain, never an older one.
  `--merge` holds the body's block to this same rule, read on main as it finds it,
  before it takes the block as current (step 4, below). The
  block must name the harness commit's blob, give a passing verdict, and show every full
  check that harness runs, by its own `CHECKS` and `NEGATIVE` lists, with no failure; a
  block written before the `Verdict` line existed does not pass, so its pull request
  needs a fresh pre-flight. A block that left the full checks to CI passes in their
  place only for a train of R0 to R2: the `LOW_CLASSES` of its harness must hold the
  class it names, and two diffs, each classed by main's `scripts/risk.py` with the
  train's labels, must be R0 to R2 and change no check input and no protected path but
  judged content: the block's own, from its base to its head, and what the entry's merge
  brings into the group, from the merge's first parent, as CI's risk job classes a pull
  request's merge commit. The group's own CI run is classed R5, so every check runs on
  the group before it merges. The block is a declaration: anyone who can edit the pull
  request's body can type one, and the judge checks it for consistency with the
  repository, not as proof that a pre-flight ran. Its authenticity must be held by
  something a group cannot change, as above, before the queue is turned on. A `train/`
  entry's Members table is matched again to its actual member merges with
  `check_train.py`, against the pull request's current body. The queue does not repeat
  member review. An automatic revert has the narrowly checked exception below.
- **(c) Batching in order.** From the group's base to its head, the first-parent chain
  consists of two-parent merges whose trees are exactly their automatic merges.
  An already merged prefix must be held by main; the rest must be the queue's entries
  from position one through this group's last entry, in order. A skipped train, added
  merge content, squash or rebase refuses. If a queue merge has no standard pull
  request subject, its second parent must uniquely identify a queued head; that
  fallback is not allowed for the already merged prefix.
- **(d) A clean tree.** The decisions page has no repeated dated heading. The check reads
  lines, not the page as it renders, so it can only over-approximate: a line that could
  render as a level-one or level-two heading counts, in code, HTML and every container
  too; its text must be plain; every year in it must stand in a date the check reads; and
  no date may stand in two such headings. Each line is read in time linear in its
  length. In full:
  - Lines end at a line feed, a carriage return or both, as in CommonMark, and a byte
    order mark that opens the page is skipped. A line of spaces and tabs is blank; a line
    that holds anything else, a `>` among them, is not. Each line is read without its
    leading whitespace and its container markers, taken off again and again: block quote
    markers (`>`); list markers (`-`, `*` or `+`, or digits followed by `.` or `)`, each
    followed by whitespace or the line's end); GFM's task markers (`[ ]`, `[x]` or `[X]`,
    followed by whitespace or the line's end); and GFM's footnote markers (`[^label]:`).
  - A line that then begins with one or two `#` followed by a space, a tab or its end is
    a heading. Its text is what follows, without the spaces and tabs around it and
    without a closing run of `#` after a space or a tab.
  - A line that is then a run of `=` or of `-`, of any length from one, as in CommonMark
    (a lone `-` among them), with whitespace after it, underlines a heading when one or
    more lines that are not blank stand above it. Its text is every line back to the
    previous blank line, each read as above, joined by spaces, with the line's list
    numbers and footnote markers before it: a list number that cannot open a list inside
    a paragraph (any but a 1 followed by text) is the paragraph's own text, so `Notes`,
    `20. October 2026` and `===` make the heading "Notes 20. October 2026". So a later
    underline's text holds an earlier one's: two headings underlined in one stretch of
    lines need a blank line between them.
  - Every heading's text is plain: ASCII letters, digits, spaces and `. , : ; ' ( ) - /`
    only. Any other character (`<`, `&`, `[`, `*`, `_`, a backtick, `\`, `#`, `=`, a
    tab, any character outside ASCII) refuses the page, naming the line: the page writes
    its section headings plainly.
  - A heading is dated when its text contains a date: three neighbouring words, a day of
    one or two digits (with `st`, `nd`, `rd` or `th`, or without), a month by its English
    name or its first three letters (or `Sept`), in any case, and a year of four digits,
    day first or month first; or the year, month and day in numbers, as `2026-10-20`.
    Two dated headings with the same date refuse the page, naming both.
  - Every year in a heading's text, four digits from 1900 to 2199 standing apart from
    other digits, must be the year of such a date, read within the year's own line (a
    heading's text may begin at any of its lines), and a year in a list number or
    footnote marker never is. Any other refuses the page, naming the line: so a date
    written in a way the check does not read (`20/10/2026`, `the 20th of October 2026`,
    `2026 October 20`) refuses rather than passes, and so does a heading of a year or a
    month alone (`October 2026`).
  - An HTML `<h1>` or `<h2>` tag anywhere in the page, code included, refuses: the page
    quotes such a tag only in prose, as character references (`&lt;h2&gt;`), since a
    code span shows a reference as written.
  - That rendering the group changes no generated file is the `check` job's, on the same
    group, and conflict markers are S23's of `scripts/check_style.py`, in the same job.

Every merge the judge computes reads merge attributes from the group's base, main,
never from the group's checkout. And judging a group, it reads every file from Git's
objects, the decisions page among them (its blob, a regular file), never from the
checkout, which the group's own attributes shape (`working-tree-encoding` or a
`filter`, say). So an entry's `.gitattributes` cannot change what is judged: it can
shape only the checkout, and no verdict reads the checkout. `--tree` reads the
page in the checkout it is given, so it refuses as unreadable (exit 2) a page to which
Git gives an attribute that can change how a checkout writes it: `working-tree-encoding`,
`filter`, `ident`, `text`, `eol` or `crlf`, set, unset or with a value.

Every entry other than an automatic revert must have its head in this repository, and no
bot, the revert App's above all, may have written it: trains are written, named and
queued by people. Of an entry still in the queue, no bot may have put it there, last
edited its body or last renamed it (the last rename is read from its timeline; the title
goes into main's merge commit); of one already merged, the merged prefix of the group,
the judge reads only its head's repository and who wrote it, since GitHub's queue no
longer lists it and its own group judged it when it merged. GraphQL names a bot by a
login without the "[bot]" that REST adds, so the actor's type is read, not its login.
And while an issue labelled `main-red` is open, an entry in the queue lands only as
main's fix: its body must declare, as `--merge` reads it, every open `main-red` issue
and no other ("Out of a red main", below), or the judge refuses it.

**The gaps of what is new.** In the `queue-gaps` job, `check_queue.py --gaps` takes the
union of the entries' derived changes and their declarations. A changed
`tests/test_*.py` runs with `python3 -I`, and a changed `scripts/test_*.py` runs itself;
a changed `scripts/<name>.py` runs its existing `tests/test_<name>.py` or
`scripts/test_<name>.py` tests. The safe_push test command is
`python3 scripts/test_safe_push.py`. A file the group deletes asks for no test; when an
entry has more than one merge base, it asks for the tests of what it changes against
any of them, and a deletion excuses a test only if it is a deletion against all. Each
selected command runs once, and a failure fails the job. Changed propositions have
their acceptance items printed from the acceptance artifact, as a report of the
verdict already judged there. Declared rules are printed for the reader. Foundations
need no extra run here, since `model` and `formal-model` run on every group.

The tests are the group's own code, and on Linux a process can read its parent's
environment (`/proc/<ppid>/environ`), so no test runs in a step that holds the token.
The step that holds the job's token, to read GitHub, runs main's
`check_queue.py --gaps --plan <file>`, which chooses the tests, prints the reports above
and writes the chosen commands to a new file, running none of them. The next step
installs main's pinned YAML parser, which the queue's tests import, from
`scripts/requirements-test_safe_push.txt` at the group's base, with
`python3 -I -m pip` run from the runner's temporary directory, so that nothing in the
group's checkout can run in pip's place; it comes after the token's last step, since
what pip installs could run in any later Python. The last step declares no token, and
neither does any step after the choosing: it runs main's
`check_queue.py --run-plan <file> --head <sha>`, which reads no GitHub, checks that the
plan is for that head and that the checkout is that head, unchanged, runs only
commands of the forms above, for files of that checkout, and refuses to run any test
while a variable whose name holds `TOKEN` is in its environment. `--gaps` without
`--plan`, run by hand, refuses the same way.

This split keeps the token out of the tests' environment, files, caches and artifacts.
It does not keep it out of the job: the runner process holds the job's token until the
job ends, and every step runs beneath it, so a test that can read the runner's memory (a
hosted runner gives its steps `sudo`) could read the token there. So `queue-gaps`' token
is read-only by design: its permissions are contents, pull requests, actions and issues,
each read only, and the token ends with the job.

**Auto-eject.** With GitHub's "only merge non-failing pull requests" setting, a train
merges only when its own group passed. If a group fails, GitHub removes its last
train and rebuilds the groups after it without that train. Thus an earlier passing
train need not wait for a broken later one, and the later groups are tested again
without the rejected change.

**Auto-revert.** `.github/workflows/post-merge.yml` reruns integration on each main push.
If it fails, the workflow takes `scripts/auto_revert.py` from the previous main, the
push's `before` commit, but only when the post-merge run on `before` itself passed;
otherwise it opens the issue alone and says why. It runs the script in Python's
isolated mode, importing no code from the failed checkout. The `auto-revert`
environment must allow main alone and hold `STOICHEIA_REVERT_APP_ID` and
`STOICHEIA_REVERT_APP_KEY`. The script reverts each merge in the push's first-parent
chain, newest first, reading merge attributes from `before`, never from the tree it
reverts (`git --attr-source`, which needs Git 2.42 or later), pushes `revert/<after12>`
with the job's own token, and opens and enqueues one pull request, its head pinned, with
that App's installation token. A push that holds a commit other than a two-parent merge
is not reverted: the issue says so. A revert that changes `.github/workflows/` cannot be
pushed with the job's token, so it is left to the coordinator, and the issue says so.
If main has moved on since the failed push, it reverts nothing and leaves the issue,
since a later push's own run then decides. A push that GitHub records as a plain pull
request merge, rather than a push or a queue merge, is reverted and enqueued by the App
like any other; but the judge finds the failed push only among the pushes and queue
merges GitHub records for main, so it refuses that revert, which leaves the queue, and
the issue stays open for the coordinator, who lands the revert by hand as a red main's
fix (below). The pull request carries `auto-revert`, the reverted requests' kind labels,
`security-review` when a protected path changes, a `Failed run: <id>` line and
`Reverts: <sha>` lines; the script pushes to no branch but `revert/<12 hex>`. The App
lets that pull request trigger CI; a pull request opened with `GITHUB_TOKEN` would
not trigger it.

The decisions record, the decisions page with the entries in `docs/decisions/` that
tooling/decision-entries brings, is history, only ever added to, so a revert never
removes a decision's text: after the reverts, in a commit of its own, the script puts
`docs/decisions/` and the decisions page back as they were at the failed push's tip, as
the advice for a revert by hand that tooling/decision-entries brings restores both from
origin/main. Everything else is the exact revert. A path the failed push's tip lacks
stays absent, so without the folder only the page is kept.

A link on the kept record can outlive what it names: the page links to a file the
reverted push added, say, or to a heading of a page it changed, and the revert takes
that away. The revert's own `check_links.py` step would then fail, and the queue eject
it. So before it pushes, the script reads every relative link of the kept page and of
the kept Markdown files under `docs/decisions/`, as `scripts/check_links.py` reads and
resolves them (its reading copied, since the script imports no repository code), and if
one that resolves at the failed push's tip would not resolve in the revert, it pushes
nothing: it records the issue only, names the links and says to revert by hand. A
revert made by hand meets the same links. `python3 scripts/check_links.py`, which the
pre-flight runs, names them, and each is mended in the revert's own pull request,
keeping the decision's words (a link to the file as it stood at the failed push's tip,
say), before it lands.

The workflow records an issue with `GITHUB_TOKEN`, labelled `blocks-release` and
`main-red`, naming the trains, their merge commits, the failed jobs and the run. It
does this before attempting the revert. Without the App credentials, it records the
issue and the pause, with no revert. Unreadable history or a conflicting revert also
leaves an issue; if the previous main has no readable script, or the failed jobs cannot
be read, the workflow's own fallback opens the issue without running repository code.

The queue accepts a revert without an ordinary pre-flight only from the configured
App bot (`STOICHEIA_REVERT_BOT`), on a `revert/` branch with the `auto-revert` label,
when its named run is a failed post-merge run of a push to main, its branch is
`revert/` and that push's first 12 hexadecimal digits, and an open issue labelled
`main-red` names the run on its own `Run:` line, by this repository's address for the
run (a run of another repository, or an address elsewhere in the issue, names nothing).
The push, its `before` and `after` read from GitHub's record of pushes to main, must be
two-parent merges only, and the merges the revert names must be exactly those, newest
first. The revert's one merge base with main must be the push's tip, `after`, and
`after..head` exactly the reverts and at most one keep commit, with no merge: one
commit for each named merge, in that order, whose tree is that merge reverted onto the
last (merge attributes read from `before`, as the script reads them), then, only where
the reverts changed the decisions record, one commit whose tree keeps
`docs/decisions/` and the decisions page as at `after`, as above. Nothing else may
differ, so a revert that takes a train's lines off the page, or changes it in any other
way, refuses, and so does one built on a later main, or through any other commit. The
commits' messages are not read. The job that clears `main-red` runs no repository code
at all.

The revert job is one of the named run's own jobs, so the revert's group can be judged
while that run is still in progress. The judge then reads the run again every 15
seconds, for up to 10 minutes, and judges it once GitHub reports it completed: a run
that concluded failure admits the revert, under the rules above, and any other
conclusion refuses it. A run still not completed after 10 minutes refuses it too, so
the revert leaves the queue and the issue stays open; the coordinator then lands the
revert as a red main's fix (below). A revert that takes away a pass the acceptance
ratchet recorded (a train that brought a record to full, say) fails `acceptance` in its
own group, which compares it with the failed push, and a revert by hand fails it in its
own CI just the same; then the coordinator fixes main forward, or re-runs a run that
failed by chance, instead of reverting. Comparing a verified revert with main as it was
before the reverted merge is a change to the acceptance check of its own, which lands
after the queue (#245).

Two limits are stated rather than closed. The workflow that holds the App's key is read
from main, so code that has landed there could take the key. A key taken that way still
writes nothing to the repository's contents (the App only reads them; the revert job's
own token, which lasts as long as the job, pushes the revert branch), so it makes no
branch, tag or release; it is no ruleset's bypass actor; and it lands nothing but the
revert above, since the queue refuses any other entry a bot wrote, queued, last edited
or last renamed. The revert's own title and body are the App's words, which a taken key
could choose; the judge reads the body's `Reverts:` and `Failed run:` lines and the
tree, not the rest. It can still open, label and edit pull requests, and take entries
out of the queue. Reverting such a change does
not take the key back: the owner makes a new key. And the pre-flight block
in a pull request body is evidence the coordinator's harness wrote, which anyone who can
edit the body could imitate; the queue checks it for the head and the harness, and
`git safe-push --merge` remains the way trains are queued.

Landing through `--merge` pauses while an open `main-red` issue exists or the latest
completed post-merge run at main's tip concluded anything other than success, neutral
or skipped. A tip with no completed run is not itself marked red; unreadable health
answers refuse. The queue's judge holds the same pause for trains already queued, or
queued without `--merge`: in a group judged while an issue labelled `main-red` is open,
it refuses every entry but the automatic revert and a declared fix (below), so the rest
leave the queue. A group the judge passed before the issue opened, during the post-merge
run, can still merge, since the judge runs once for each build of a group. It reads the
open issues only, not the post-merge runs. Successful integration clears `main-red` only
after confirming that the successful commit is still main's tip, and only from an issue
whose exact `After: <40 hex>` line names that commit or one of its ancestors. An issue
with a missing or unreadable line, or one naming another commit, keeps the label; the
issue stays open with `blocks-release` for the coordinator. The clear reads main again
before each removal. Main has moved on only when its tip, read afresh, is readable and
another commit: then the clear job, like `auto_revert.py --clear --after`, changes no
further label and passes, naming that commit and its post-merge run, which decides, or
saying that no run for it can be read yet. So a run whose integration passed is never
marked failed for main's moving. A clear that fails at main's own tip still fails, as
does one that cannot read the tip.

**Out of a red main.** While main is red, `--merge` lands only its fix. With the queue
off, or without the revert App, only a merge moves main's tip, so the fix comes through
`--merge` like any pull request, and its body declares it: on a line of its own, where
GitHub shows it (not in a comment or a code block), `Fixes main-red: #<n>`, or
`Fixes main-red: #<n>, #<m>` for several, naming every open `main-red` issue once and no
other. The declaration lifts the pause for that pull request alone. Every other gate
holds: its own CI must pass, as every merge's must, and in queue mode its group's too;
main's health is shown as a note, not as ok, in the summary. A declaration that names
too few issues or too many, names one twice, or is not in that form, refuses, and so
does more than one such line. A failed run with no open `main-red` issue leaves nothing
to declare: the coordinator labels its issue `main-red` again first. The fix may be a
revert made by hand, as for a train that changed `.github/workflows/`; it keeps the
decisions record, and mends each link on it that the revert would break, as
`check_links.py` names them ("Auto-revert", above). Once it is on
main, its own post-merge run decides: a passing run at the new tip clears `main-red`,
and a failing one is a failed push like any other.

**Turning it on.** The queue remains off until the owner enables it, and not before the
owner has chosen the authenticated source for the pre-flight's evidence that rule (b)
asks for. The coordinator holds these steps: add the merge queue rule for main, keep
merge commits and enable "only merge non-failing pull requests"; require `check`,
`model`, `negative`, `formal-model`, `acceptance`, `queue-integrity` and `queue-gaps`;
set the queue's status check timeout to 150 minutes: `acceptance`'s limit of 60 minutes,
then `queue-gaps`' of 75, which starts only once `acceptance` ends, and 15 for waiting
on runners. `queue-gaps` may run the tests of `safe_push.py`, `check_queue.py` and
`check_train.py` in one group, near 40 minutes as measured off GitHub, and its choosing
step, like `queue-integrity` (limit 20 minutes), may wait up to 10 minutes for a
revert's run to complete before it judges the revert (above): a shorter timeout ejects
sound slow groups, and every automatic revert whose run is still in progress. These
numbers are measured again on the queue's trial, and `QUEUE_TIMEOUT` in `safe_push.py`,
how long `--merge` follows an entry, is twice the status check timeout, for one rebuild
behind a group that fails. Then install the revert App for this repository with contents
read, and pull requests and merge queues write (a train that changed
`.github/workflows/` cannot be pushed by the job's token, and is reverted by hand); add
the rulesets that keep branches other than `revert/**` and tags to the owner; restrict
the `auto-revert` environment to main and put the App credentials there, not in
repository secrets; set the repository variable `STOICHEIA_REVERT_BOT` to its bot login
as REST spells it, `<the App's slug>[bot]`. With the queue off, `--merge` follows the
direct merge path below. The issue and the pause still apply if the App has not been set
up.

**Decision entries.** A new decision is a file of its own in `docs/decisions/`, so that
pull requests queued together do not collide at the end of
[the decisions page](briefs/0002-decisions.md), as they did while each added its entry
there. The page's entry of 20 October 2026, "Decision entries, one file each", brought
the rule: a decision written after that entry landed goes in an entry file. A pull
request opened before it landed may keep the entry it added to the page, whose new lines
count as any new line of the page does (step 3, below). The page's entries stay where
they are. An entry is read where it is, as a page of its own: nothing assembles it into
another page, and GitHub lists the folder in name order, which is date order
([the folder's README](decisions/README.md)). To write one, the coordinator:

1. names it `docs/decisions/<YYYY-MM-DD>-<slug>.md`: the day of the decision, a valid
   date no earlier than 20 October 2026, when the entries began, then a short name of
   lower-case letters and digits joined by hyphens, as
   `docs/decisions/2026-10-21-entry-files.md`;
2. writes the entry as the page's entries are written (`- **A title (area).** The
   decision, and why.`), with no date heading, since the name carries the date, and
   names each file, statement and lock it approves in a sentence of its own, never on a
   line or in a list repeated from an older entry or the page, for such a line counts
   for nothing (step 3, below); it may hold headings, as any page may, and its relative
   links resolve from `docs/decisions/`, as `../WORKFLOW.md` or
   `../../scripts/render.py`;
3. keeps out of it a count marker, and any character that could hide a copy of an older
   entry: a control character but a tab and a line feed (a carriage return among them,
   so lines end in a line feed alone), a format character (Unicode's Cf, as a zero-width
   space, a soft hyphen or a byte-order mark), a line or paragraph separator, Unicode's
   other default-ignorable characters (as a variation selector or a Hangul filler), a
   character that renders blank though Unicode counts it neither white space nor
   default-ignorable (a fixed list, since Unicode has no property for a blank glyph: the
   Braille pattern blank, U+2800, the musical symbol null notehead, U+1D159, and the
   Khitan small script filler, U+16FE4), and a code point Unicode keeps for private use
   or leaves unassigned (its Co and Cn); and saves it as UTF-8;
4. runs `python3 scripts/render.py`, which checks the folder before it writes anything,
   refusing, with the file's name, its unprintable characters written as escapes, a
   link, a folder or any file but the README and entries, a folder spelled otherwise on
   disk (as `docs/Decisions/`, or `docs/deciſions/` with a long s, which a Mac finds and
   Git does not), an entry whose name or characters break steps 1 and 3, a count marker
   in any file there, a README holding a character step 3 keeps out, and an empty entry;
   it passes over a file Git ignores by a rule of the root's `.gitignore`, of
   `.git/info/exclude` or of the user's own excludes file, as Finder's `.DS_Store`,
   which Git never commits, but never one that a nested `.gitignore`, which a commit
   could add, ignores; it stops if Git cannot say which files those are; and it writes
   nothing into the folder, so the pull request carries the entry alone, beside the
   change it records.

An entry is dated history, never edited: the pre-flight refuses a push that modifies,
deletes or renames an entry origin/main holds (step 3, below), and a correction is a new
entry, in words of its own, naming the entry it corrects. An entry that copies another,
or the page, in part or whole, is not refused for it, but the lines that step 3's
comparison finds copied approve nothing. A revert keeps the record too: after
`git revert --no-commit -m 1 <merge>`, the coordinator restores `docs/decisions/` and
the decisions page as origin/main has them
(`git restore --source=origin/main --staged --worktree --` with those two paths), then
adds an entry recording the revert and why, naming each protected file, statement and
lock the revert changes in a sentence of its own, as any entry must, and commits; the
advice `--merge` prints when main is not what was checked gives these commands. The
folder's README is no entry: it may be edited, and approves nothing; once added, it is
never deleted, so that origin/main always holds the folder; and it is UTF-8 text holding
none of the characters step 3 keeps out of an entry, which `render.py` and the
pre-flight both check.

```sh
sh scripts/install_hooks.sh                        # from a checkout of origin/main: once per
                                                   # clone, and after the hook or launcher changes
git safe-push --branch <name> --dry-run            # every check; nothing pushed
git safe-push --branch <name> --label <kind>       # the pre-flight, the push, a draft pull request
git safe-push --branch <name>                      # after a fix: again, on the new head
gh pr ready <n>                                    # when the reviews are done
git safe-push --merge <n> --dry-run                # the gates, and no merge
git safe-push --merge <n>                          # the gates, then queue or direct merge
```

For `train/*`, add `--body-file <path>` to every `--branch` command above.

`git safe-push` is a launcher that `install_hooks.sh` puts outside the tracked tree
(`scripts/hooks/safe-push`, copied to `.git/stoicheia/safe-push`, with the alias): it
fetches origin and runs origin/main's `scripts/safe_push.py`, whatever the checkout holds,
so a branch cannot judge itself; it copies that harness out of git, and the harness reads
git, both with git's replacement objects off (#256): git reads a replacement
(`refs/replace/`, or a ref under `GIT_REPLACE_REF_BASE`) in place of the object it
replaces, but a push sends the original. `python3 scripts/safe_push.py` from a checkout
runs that checkout's copy, which hands over to origin/main's when it differs; that
protection holds only while the copy run is one that hands over, so the launcher is the
way in. While origin/main's copy predates running from origin/main, the launcher runs the
checkout's, and says so. The launcher and the pre-push hook run Python 3.11 or later:
`STOICHEIA_PYTHON` when it is set, else the first of `python3.14`, `python3.13`,
`python3.12`, `python3.11` and `python3` that is; without one, they refuse.

1. **A branch.** The change is committed on a branch from origin/main. Before a push,
   it must contain the current origin/main. If main moved, merge it into the branch,
   never rebase onto it: review records stamp the branch's commits, and a rebase would
   orphan the stamps. With the queue off this still holds at the merge; with the queue
   on, the group checks a head alongside the changes that reached main or queued ahead
   since its pre-flight.
2. **The pre-flight.** `git safe-push --branch <name>` checks the exact commit (HEAD, or
   `--commit <sha>`), then pushes it to that branch, never to main and never forced, and
   opens the pull request onto main, or updates the open one. It reads the commit alone,
   through git and a fresh temporary worktree, so a dirty working tree makes no
   difference; and it is origin/main's copy of the harness (by the launcher, or by a
   checkout's copy handing over, which replaces its own process with origin/main's), so
   that a branch cannot weaken the harness that judges it. It stops, saying why, at the
   first step that fails:
   1. *Preconditions.* The commit exists; `git fetch origin`; origin/main is an ancestor
      of the commit, so a direct merge at that base holds exactly the tree checked; the
      branch, if origin has it, is an ancestor of the commit too; the branch is not main;
      the branch name and the title, which are public, hold nothing the secret scan
      refuses. No tag or release is made. The installed hook and launcher are compared
      with origin/main's copies, and a difference is noted.
   2. *Secrets.* Every line, file and commit message the push adds is scanned for private
      keys, API-key-like tokens, Authorization headers with values, `.env` and key
      files, and the owner's private paths, an agent's scratchpad paths among them; each
      commit's author and committer are scanned for private paths and for identities git
      made up from the machine's name; and so is each commit's own change, since the push
      publishes the history (a secret taken out again by a later commit, or a key file
      renamed, is still found). Lines are read alone and run together, so a value split
      over two lines is found; base64 that decodes to text is read through; a symlink may
      not point out of the repository. Whether a file is text or binary is read from its
      bytes, never from `.gitattributes`: a NUL anywhere makes it binary, and a binary
      file is read whole, its printable runs and its runs of UTF-16 text, wherever they
      stand, as lines. A false positive goes in `scripts/safe_push_allow.toml` on
      origin/main, in a pull request of its own: one file, one rule, a part of the line,
      and the flagged value itself, pinned (held in that part, or named by its SHA-256),
      to an entry, with its reason; so the entry excuses that value alone. A broad entry
      is refused, a commit's message or identity cannot be allowed, and an entry added by
      the push itself does not count. An allowed finding is noted in the pull request by
      its place, its rule, its value's SHA-256 and the reason, never by its line. The
      scan reads what the push sends: every git command `safe_push.py` runs itself, the
      scan's among them, reads with git's replacement objects off, whatever the caller's
      environment holds (#256), its `git status` check among them. The programs it runs
      as checks are started with no `GIT_*` variable but `GIT_NO_REPLACE_OBJECTS`, which
      is present under the launcher or after a hand-over and otherwise only if the caller
      set it, so that a check finds its repository by its working directory (#355). No
      command `safe_push.py` runs itself, git's or another's, gets one of the caller's
      variables that tie git to one repository (`GIT_DIR`, `GIT_INDEX_FILE`,
      `GIT_WORK_TREE` and the rest that `git rev-parse --local-env-vars` lists), but
      `GIT_NO_REPLACE_OBJECTS` as above, so that a hook's variables never send its git to
      the hook's repository or index: each command finds its repository by its working
      directory too, the hand-over's included (#357). The harness sets one itself, the
      temporary `GIT_INDEX_FILE` of the main-checks cache's base tree. The launcher behind
      `git safe-push` unsets the same variables before its first git command, so a
      caller's `GIT_DIR` cannot make it fetch another repository's origin and run that
      repository's harness (#359).
      `check_acceptance.py`, the only check that reads git's objects for its verdict, is
      #237's.
   3. *Invariant guards,* against origin/main, in the temporary worktree:
      - no statement changed (facts.json's `statement`, and the Lean source of the
        theorem, its porism and its companions, to its own `:=`, whitespace aside) unless
        the push adds a new line to `docs/briefs/`, a brief's revision or a decisions
        entry, or to a dated entry in `docs/decisions/`, that names the proposition
        (section 2);
      - `Certificate/axioms.lock` unchanged unless
        [0002-decisions.md](briefs/0002-decisions.md) or a dated entry gains a new line
        mentioning the lock;
      - no protected path changed unless 0002-decisions.md or a dated entry gains a new
        line naming each file changed (below);
      - every change to `heath/` carries a comment naming a scan leaf of its own pages, as
        origin/main's copy of the file lists them ([STYLE.md](STYLE.md), section 5);
      - no review record stale (`check_fidelity.py`, on the commit as committed);
      - the generated pages current (`render.py`, on the commit as committed, changes
        nothing, and refuses no decision entry);
      - the commit's registry of checks readable as a later pre-flight will read it once
        the commit is origin/main's: by the commit's own `scripts/registry.py`, taken out
        of Git and run alone from a temporary directory, reading the commit's `checks/`
        out of Git, its checks' names held as step 4 holds them (`render.py` and CI load
        the reader from `scripts/` and read the worktree, so a reader that leans on a
        module beside it would pass them both); skipped only while the commit holds
        neither the registry nor its reader;
      - no whole directory of `Elements/`, `heath/`, `review/`, `figures/` or `mishnah/`
        deleted unless the decisions page or a dated entry gains a new line naming it, as
        a protected file is named (below), with a full stop after it only when its
        mention holds a slash, so that "the figures." names nothing, though `figures/.`
        does;
      - `docs/decisions/` holding regular files alone, its README and dated entries, each
        entry named and written as "Decision entries", above, says (a valid date, from
        20 October 2026 to the day after the earlier of the commit's committer date,
        which the pusher sets, and the runner's own date, a day's grace for time zones,
        and UTF-8 text holding none of the characters kept out there), and the README,
        when the push adds or changes it, UTF-8 text holding none of them either; no path
        the push changes spelled otherwise than `docs/decisions/` where a Mac's file
        system reads it as that folder (its first two names in Unicode's NFD form,
        casefolded, as `docs/Decisions/`, or `docs/deciſions/` with a long s, which Git's
        own case-blind matching misses); and no entry origin/main holds modified, deleted
        or renamed: Git's rename detection (every file there a source, with no limit)
        finds a move with edits. Each path a refusal names is printed with its
        unprintable characters written as escapes. An entry that copies another is not
        refused for it, though Git's copy detection would call it a copy; the lines the
        comparison below finds copied count for nothing. The README may be edited, never
        deleted once added, and approves nothing.

      For each of these, the push must add a mention: an old line that already named the
      thing, edited in place, does not count. A line added to the decisions page is
      compared with nothing, and any new line there counts, as it did before the entries
      began; its mentions, though, are read by the same rules as an entry's, which are new
      for the page too: where a mention may start (as "Protected paths", below, says), a
      directory named by a link or the root's anchor, as a file is, and a directory's full
      stop. A line of a dated entry counts only in an entry the push adds, and only when
      it holds a word; when no line of the decisions page or of any file under
      `docs/decisions/` at origin/main matches it, each read as a skeleton (in Unicode's
      NFKC form, casefolded, each Cyrillic or Greek letter that looks like a Latin one
      read as that letter, and every space separator, and each of the characters that
      render blank, the Braille pattern blank, the null notehead, the Khitan filler and
      the Hangul fillers, read as a space, the whitespace collapsed inside the line and at
      its ends: the page may hold those, though no entry may); and when none of its words
      lies in a run of 12 or more consecutive words, so read across lines, that the page
      or one file under `docs/decisions/` at origin/main holds too. So a copy of an older
      entry, re-wrapped, re-spaced, in capitals or in those look-alike letters, renews
      nothing, kept beside its original or not. That is all the comparison catches: a copy
      with a word put in after every eleventh, one reworded throughout, or one in
      look-alike letters of another script reads as an entry in words of its own, and only
      the reviews can tell it from one. Each run of consecutive lines that count is read
      on its own: words are never joined across a blank line or a line that does not
      count, though a name wrapped from one line that counts to the next still counts, as
      on the page. A guard that refuses names each line of an entry the push adds that did
      not count and in which its own reading finds a mention of something it found no new
      line naming, and why: a line the record holds already, or one in a run of 12 or more
      words the record holds too; so it never names a code fence, or another line that
      names nothing it asks for. While a push refuses anything under `docs/decisions/`,
      entries supply no new line at all, and the guards' refusals say so; so a rename, or
      a deletion and re-addition of an entry, renews no approval.

      For `train/*`, step "3. train" then runs origin/main's train checker against the
      committed head and the supplied body, as described above.
   4. *The full checks* of section 8, by the change's risk class
      ([the decision](decisions/2026-10-22-checks-by-risk.md)). First the class, R0 to
      R5, as origin/main's copy of `scripts/risk.py` gives it for `git diff
      origin/main...<commit>`: read out of Git and run from a temporary directory, never
      the commit's own copy, so that a change cannot lower its own class by editing the
      classifier. A pull request labelled `release`, given with `--label` or on the open
      pull request (read in step 1, before the checks), is R5: a label can only raise the
      class. An origin/main with no `scripts/risk.py`, and any failure to compute the
      class, is R5 too. The class and why are this step's first line, which the pull
      request's summary shows, and the record keeps it. For R0, R1 and R2 the rest of this
      step is skipped: CI runs the rest of section 8's sequence on the pull request before
      the merge, and `--merge` waits for CI green, while the negative tests run on main
      after the merge and on the cadence, as section 8 says; one line says so. Such a
      change touches no
      check input and no protected path but the judged content named below, so no check
      change can need keeping apart; should origin/main's classifier ever class one that
      does R0 to R2, the full checks run, and a note says why. For R3, R4 and R5, the full
      checks of section 8 in that worktree, and `negative_tests.py` in a
      second, each step timed. The `check` job's checks are those of origin/main's
      registry, `checks/`, read out of Git by origin/main's `scripts/registry.py`, which
      runs from a temporary directory: never the pull request's registry or reader, so a
      train cannot add, drop or change a check its pre-flight runs. The pre-flight holds
      the checks' names itself: only the check that `git status --porcelain` prints
      nothing bears that name, and every other is named by its command's words, so that
      no command bears a name whose failure is passed over as stale pages (below). A step
      line says how many checks run and whose registry they come from. While origin/main
      holds no registry (the train that brings it), the lists built into `safe_push.py`
      stand in for it, until a follow-up card removes them; a registry at origin/main
      that cannot be read, or whose reader fails or gives no check, refuses the
      pre-flight. The check scripts and what they expect (`scripts/`,
      `tests/`, `Certificate/`, `review/SCHEMA.md`, `review/terms.toml`, the registry,
      `checks/`, and since #249 `docs/ACCEPTANCE.md`, whose table of the limitations
      allowed `tests/test_acceptance_limits.py` ties to `check_acceptance.py`) are
      origin/main's
      copies; when the pull request changes any of them, the checks run again with its own
      copies, which must pass. A check that fails with origin/main's copies is noted in
      the pull request for the security review, and refuses the pull request if it also
      changes what the checks judge (anything but the guides and briefs, the generated
      pages, a review record's stamp, and the protected paths other than `Audit/`,
      `Audit.lean`, `model/Model/Audit.lean`, `model/Model.lean` and the model's build
      files): the check change goes first, in a pull request of its own. Two kinds of
      failure are only noted. Pages gone stale under origin/main's `render.py`, or
      `facts.json` rewritten by origin/main's
      certificate, show the generator's change in the pages' diff; a failure of
      `render.py` itself, its check of `docs/program.toml` among them, is a verdict. And
      the values pinned to the edition move with the content they pin (a re-proof that
      changes an expected count, a new word in the lock, an axiom added):
      `tests/certificate_expectations.json`, `Certificate/axioms.lock`,
      `tests/model/lock.sha256`, the model's law names in `tests/model/laws.toml`, and its
      account of the laws, `tests/model/MODEL.md` and `tests/model/results/`, which
      `tests/model/results_check.py` holds to the present harness (section 8), as
      `check_fidelity.py` holds MODEL.md's count markers to what they count. A count
      between count markers ([STYLE](STYLE.md), section 4) in the Markdown of a check input under
      `Certificate/` or `tests/`, or in `review/SCHEMA.md`, such as
      `Certificate/FIELDS.md`'s count of the lock's words, is such a value too:
      `render.py` generates its value and `check_fidelity.py` refuses a stale one, so a
      change to that Markdown counts as a pinned value while nothing else in it changes
      (the same markers stand, by name and in order, as origin/main's
      `scripts/generated_counts.py` reads them, and every other byte and the file's mode
      are as they were). MODEL.md's prose moves with the laws, but its markers are held
      the same way: a change to it counts as a pinned value only while the same markers
      stand, by name and in order, the file's mode is as it was and both sides read; a
      marker added, removed, renamed or reordered is a check change. When pinned values
      are the only check inputs a pull request changes, origin/main's failure is noted,
      and its own copies must pass. The expectations are checked one way only, each for
      what it says, so they count as pinned values only
      while every one of origin/main's stays, by its `ref`, `field` and `law` (a `ref` or a
      `law` added or dropped is another expectation), with its `includes` and `excludes`
      the same or grown and only the values of `count.is` and `equals` changed (new
      expectations are fine); an expectation dropped or loosened is a check change. A law
      of the model moves only with its axiom: a line of `laws.toml`,
      and the law's code in `tests/model/search.py` and `tests/model/hyperbolic.py`, the
      two harnesses that check every law, count as pinned values only where the same pull
      request adds, removes or restates that axiom's entry in the lock, the law's code
      keeps to itself (a function `_` under its one decorator `@axiom('<name>', …)`, which
      uses only what an allow-list in `scripts/safe_push.py` names: its own parameters and
      the names it binds, the helpers, builtins, `math` functions, other names and
      attributes that its harness's laws already use, each in the role they use it in, and
      plain syntax; and changes no container but one it made in its own body, through the
      name it gave it), and nothing else in the harness changes but its comments and
      docstring. The laws that stay keep their order; a law changed while its axiom stands
      is a check change. The pre-flight reads the law's code, does not run it, and refuses
      whatever the list does not name, so reflection (a frame, a module reached through
      another, a lookup by string) has no way in; the security review reads the law as
      well. A law still shares the random numbers with the laws after it, and how many it
      draws moves which configurations they see, never what they check. A law that needs
      what the list lacks waits for the list to grow, in a pull request of its own. Check
      code changed with judged content is kept apart, pinned values or not. The guards'
      two checks in step 3 run the same way.

      *origin/main's pass, cached* (#224). With `--main-checks-cache`, origin/main's pass
      of step 4, both its loops, the checks and the negative tests, is kept in
      `~/.cache/stoicheia/main-checks/` and reused when the same trees come again, as
      they do when the coordinator's dry run of a train is followed by its push, at one
      head against one main. Only the runs that land a train pass the flag (the
      coordinator ruled): the coordinator's dry run of the train and its push. It serves
      only a change of R3 to R5, whose step 4 runs in full, landed from a branch not
      named `train/*`, as a `batch/*` landing is (a `train/*` branch's train check runs
      in the harness's own process, so it has no cache): for R0 to R2, which leave step
      4 to CI, the flag reads, writes and makes nothing, and sets no sandbox. Step 3's
      pass and the commit's own pass run every time; on a hit, the commit's own pass
      builds what the skipped pass would have built. An entry's name is the SHA-256 of its
      key, which the harness computes, taking nothing from the tree as code: origin/main's
      commit; the tree the pass runs on (the commit's, with origin/main's copies of the
      check inputs it changes), and the commit's own tree, which `git status` and
      `git ls-files` compare it with; the harness's blob; the toolchain
      (`lean-toolchain`, `lean --version`, `lake --version`, the `lean` elan resolves);
      the Python, the platform, Git, the checks' `PATH`, `LANG`, `LANGUAGE`, and the
      variables whose names begin `STOICHEIA_`, `LEAN`, `LAKE`, `PYTHON` or `LC_`, but
      the harness's own, which no check reads (`STOICHEIA_HARNESS`, `STOICHEIA_PUSH_LOG`,
      `STOICHEIA_PYTHON`), and the terminal's (`LC_TERMINAL`, `LC_TERMINAL_VERSION`); and
      the lists of checks. An entry is used only when it is a
      regular file of the user's, mode 0600, its key is this run's and hashes to its
      name, its digest matches it, its harness is the one running, its written time is a
      valid `YYYY-MM-DD HH:MM UTC`, and its steps are that pass's, each once and in order,
      each "ok" or "note", with a time a step could take and text the run can write and
      print; otherwise, when it is larger than 16 MiB (and so never read), or when it
      cannot be read at all, the pass runs again, the run says why, and the entry is
      written afresh. A hit is
      reported, for the pull request's record, and its steps carry their recorded
      outcomes, notes as notes, so `keep_apart` judges them as it would have; a note
      points to the copy of its log the run writes. The directory must be a real one,
      owned by the user, mode 0700, reached through no symbolic link, and on the device
      of the directory above it. Once the class is read by origin/main's `risk.py`, the
      harness loads origin/main's count-marker reader and its dependencies, and retains
      it for that repository and base. Both happen outside the sandbox but before any of
      the commit's code; the cache is then opened, and from then on every command the
      pre-flight starts runs under macOS's `sandbox-exec`, with a profile under which no
      command may write the directory, nor rename or change a directory above it (which
      would carry the cache away), and the harness starts no process but through it and
      imports no module but a builtin, each other it needs being imported when it starts.
      A `train/*` branch has no cache: its train check loads origin/main's
      `check_train.py` into the harness after the commit's code has run (#383), so the
      flag sets no sandbox for it, and the run goes on as without the flag.
      Where the sandbox cannot be had (not macOS, no
      `sandbox-exec`, already inside a sandbox, or a profile that does not stop a write to
      the directory or the one above it), there is no cache that run, and the pre-flight
      is otherwise unchanged.
      The digest is no signature, and the sandbox stops only this: the commands a
      flagged run starts writing the cache directly. It does not stop a run without the
      flag, a ship's own dry run among them, which starts its commands with no sandbox,
      nor a flagged run of a `train/*` branch, which sets none; nor anything code run as
      the same user does outside a flagged run; nor anything a
      flagged run's code leaves for a later command to run before its sandbox starts: the
      launcher in `.git/stoicheia/`, `alias.safe-push` in `.git/config`, a program
      earlier on the `PATH`, the harness copy in `~/.cache/stoicheia/harness/`, a module
      in the harness's own directory, which Python searches first, or in Python's standard
      library (the user's own under Homebrew), or Python's start-up files. That is the
      exposure the `--merge` step-4 record already
      has, a local file any code run as the user can write. A profile that allows writes
      only where the checks need them, or a cache owned by another Unix user, could
      narrow it; either is for the owner to decide.
   5. *The push and the pull request.* First the pull request is settled: our open one
      for the branch (a fork's pull request of the same name is never touched), or a new
      one. Its body is `--body-file`, or is generated from the
      [template](../.github/pull_request_template.md): the commits, the statements
      changed, the review records touched and re-stamped, the protected paths, the
      generated files (README.md and PROGRAM.md only when the text between their markers
      changes), and the pre-flight's summary, every step with its outcome and time. Each
      of these parts stands between markers of its own, each marker on a line of its own,
      and on an update without `--body-file` each is written afresh for the new head,
      while the coordinator's words, outside the markers, stay: a marker quoted in them
      (in a code span, say) is not one. The body is scanned before anything is pushed;
      the label for its kind, given or on the open pull request, was settled in step 1,
      before the checks. Then the branch is pushed, and the pull request opened as a
      draft with `gh pr create --base main --draft` (or `gh pr edit` of the open one; `--ready`
      opens it ready, or marks the open one ready), with the labels given and
      `security-review` when a protected path changes. Then its CI is followed to its
      conclusion, judged as the merge judges it (step 4): a `release-gate` run left from
      an earlier `release` label is waited for, never counted. Once `git push` succeeds,
      an interruption, a failure to follow CI or a refusal is reported as "pushed; CI not
      followed", exit 3, never as a refusal before the push.
3. **Reviews,** recorded in the pull request, in the template's table: `/code-review`
   always; `/security-review` when a protected path changes; `/no-mistakes` before the
   merge, run without its push and pull request steps, since `git safe-push` alone
   pushes and opens pull requests. Each blocking or material finding (section 9) is
   resolved, and the pull request says how. A fix is a new commit on the branch, and the
   pre-flight runs again.
4. **The merge.** `git safe-push --merge <n>` reads main's effective rules; an unreadable
   answer refuses. A `merge_queue` rule selects queue mode. In either mode it checks
   main's health (a red main admits only its fix: "Out of a red main", above) and runs
   the secret scan and guards on the pull request's head again, every time. With the
   queue off, the base is current origin/main, which the head must contain. With the
   queue on, the base is the newest commit of current origin/main's first-parent chain
   that the head contains, which is what its pre-flight recorded, so the head need not
   contain the intervening main changes. It is not the head's merge base with main,
   which lies off the chain when a member was merged on its own before its train: so
   `--merge`'s own checks, its train check and the queue's judge (rule (b), above)
   compare against one base. The
   pre-flight's record is a local file, which code the pre-flight ran (a commit's
   checks, Lean at elaboration) could have written, so it stands in only for the full
   checks, which CI runs as well, and only for this head and base with the running
   origin/main harness's blob, and never for a head that changes the checks (`scripts/`,
   `tests/`, `Certificate/`, `review/SCHEMA.md`, `review/terms.toml`) or any protected
   path, since CI runs a head's own copies and its own workflow, and only the pre-flight
   runs origin/main's on it; otherwise they run again too. A record that left them to CI
   for its class stands in only while the class, recomputed then by origin/main's
   classifier for that head against that base, is still R0 to R2; otherwise step 4 runs
   again, by the class. The body must already carry
   the summary of this head, its base and harness held to the queue's judge's rule
   (rule (b), above), read on current origin/main, in both modes: the base the newest
   commit of main's first-parent chain that the head contains, which is what the
   pre-flight records, and the harness that base or a later commit of the chain (with
   the queue off, both are main's tip); for a train, with its train step passing. So a
   summary the judge would refuse is never taken as current, and one it would accept
   is, its base the one the merge checks against, even when the head's merge base with
   main lies off main's chain. Every other part safe_push wrote must be up to
   date; a body edited in GitHub's page, which keeps CRLF line ends, is up to date when
   it differs from those parts by line ends alone. `--merge` never writes the
   pull request body: when one of those parts is stale, it refuses before writing, and
   the coordinator runs the pre-flight to refresh the body before starting a fresh merge
   attempt. It merges only when those pass; CI on that head is green, subject to the
   ruleset and the local check judgement described in
   [section 8](#8-validation-on-the-integrated-revision); no box marked **Required** in
   its checklist is unticked, nor one marked **Required if protected** when a protected
   path changes, and none of the template's
   required boxes is missing (origin/main's template, or the head's while origin/main
   has none; the pre-flight's notes, such as a check that failed with origin/main's
   copies, are shown beside the checklist); the coordinator has written "What and why",
   "Unfinished work" (once the template in force has that section),
   each review's commit and findings in the Reviews table (the security review's when a
   protected path changes) and "Needs the owner's OK". Boxes and other sections count
   where GitHub shows them, by CommonMark's rules; "Unfinished work" is read as raw text,
   so that nothing GitHub hides or shows differently can stand in for it. The body holds
   the line `## Unfinished work` once, at the left edge, where GitHub shows it as a
   heading (not in a comment, an HTML block, code or a part safe_push writes), and no
   other line whose letters, with tags and entities taken out, begin "unfinished work"
   or are just "unfinished" (in a comment or code too, so not even a sentence may start
   with those words); a heading disguised on purpose, in another alphabet or in crafted
   markup, is for the reviews to find, as a false "None" is. The section runs to the
   template's next heading. Taking out the template's own comment for it, where it
   stands on lines of its own, it is plain ASCII with no markup (no links, code, HTML,
   other comments, headings or entities): "None", with an optional full stop, or a list,
   each item `- ` or `* ` at the left edge, wrapped with two to five spaces, naming one
   or more issues as tokens `#N` (perhaps in parentheses, or before punctuation); any
   other `#`, or `GH-N`, is refused. Each
   issue is open with `blocks-release`, not a pull request, and of this repository by
   GitHub's canonical address for it, so a rename is allowed and a transfer is not;
   the section is read again before the merge, and refused if it changed meanwhile.
   A pull request labelled `release` has no open issue or pull request labelled
   `blocks-release`; label comparisons ignore case. It merges only on a record of the
   full pre-flight of its head, never one that left step 4 to CI (otherwise `--merge`
   refuses at once, saying to run the pre-flight again, which the label makes R5), and
   only with a green run of `.github/workflows/safe-push-tests.yml` at that exact head:
   completed and successful, its jobs `safe-push-tests`, `negative-tests` and
   `formal-model-kernel` each there and passed (safe_push's `SUITE_JOBS`), and every other
   job passed, the shards of `safe-push-shards` among them, but `report`, which runs only
   for a red run on main (#301). A run at the head
   runs the head's copy of that workflow, which could drop a job, so the head's copy must
   be origin/main's: a release that changes it is refused, and the change lands first, in
   a pull request of its own. Malformed pull request labels refuse
   the release gate and retain every CI check. Both issue gates read from
   GitHub and fail closed on a failed read, malformed JSON or missing fields; the
   release gate makes no issue-list read for an ordinary pull request. The title and
   the branch name, which go into main's merge commit, hold
   nothing the secret scan refuses; it carries a label for its kind, and
   `security-review` when a protected path changes; and it is not a draft. These gates
   hold in both modes; in queue mode they are read when the pull request is queued, and
   the queue does not read the release hold again before it merges (the owner's OK
   before the tag still holds a release).

   **Queue on:** main's health is checked again at its current tip, and the head is
   enqueued with GraphQL `enqueuePullRequest`, `expectedHeadOid` pinned to the checked
   head. The script follows the entry to a merge or removal from the queue. A merge
   succeeds only when origin/main holds the named two-parent merge with the checked
   head as its second parent. Its tree includes the trains ahead, checked by the
   group's CI; it need not equal the pull request head's tree. An ejection is exit 1,
   with the last observed group's checks when readable. An unreadable verdict,
   interruption or timeout after the enqueue was attempted is exit 3,
   "queued; verdict not followed", with no revert advised. A dry run enqueues nothing.

   **Queue off:** main must still be the checked base, and its health is checked again.
   Then `gh pr merge --merge --delete-branch --match-head-commit <head>`, with the merge
   commit's subject and body given (GitHub's own words: the owner GitHub names for the
   head, never the one in origin's URL, which names the old owner after a transfer, and
   refused when GitHub names none an account could have; the branch name, scanned; and
   the title, scanned; a branch renamed since the merge first read the pull request is
   refused, as a head moved is), so main holds exactly what was scanned: a merge commit,
   never a squash or a rebase, and the branch deleted. Whatever gh's exit, GitHub is then
   asked whether the pull request merged before anything is said: gh can fail after
   merging, and can exit 0 without merging, when a merge queue or auto-merge takes the
   pull request to merge later. Once gh is asked to merge, the script says nothing merged
   only when GitHub says the pull request is open or closed after gh failed, and reports
   success only when GitHub says merged and origin/main holds the merge commit GitHub
   names by its full object name. gh exiting 0 with the pull request not merged, a merge
   commit GitHub does not name or origin/main does not hold, an interruption before
   GitHub answers, or GitHub not to be asked, or answering with no state of its own, is
   reported as "merge state unknown", exit 3, with no revert advised, since nothing on
   main is known to be the merge. Afterwards the merge commit is checked to join the base
   and the head checked, with the head's tree; if it does not, the script prints how to
   revert it in a pull request of its own, with the merged pull request's label for its
   kind, keeping the decisions record ("Decision entries", above), and reverts nothing
   itself.
5. **Generated files** are regenerated from the integrated sources and committed by the
   integrator (section 4), so the pull request that changes their sources carries them.

**Protected paths.** `scripts/` (the hook and the launcher included), `.github/`,
`Certificate/` (the lock included), `tests/`, `review/SCHEMA.md`, `review/terms.toml`,
`.gitattributes`, `.gitignore` (a rule added there hides untracked files from
`git status`, and so from the check that the generated pages are current), the
toolchain files (`lakefile.toml`, `lakefile.lean`, which Lake reads in preference to
`lakefile.toml` and runs, `lean-toolchain`, `lake-manifest.json`), and, since 18 October
(#96), `Audit/`, the audit lemmas whose pinned axiom lists back the overlap catalogue's
claims, with `Audit.lean`, the root that decides which of them `lake build Audit` checks,
and the formal model's build files (`model/lakefile.toml`, `model/lakefile.lean`,
`model/lean-toolchain`, `model/lake-manifest.json`, and `model/lock.sha256`, the hash of
the lock the model was last checked against). Since 19 October, `model/Model/Audit.lean`
and `model/Model.lean` join them, because they pin the model's proofs to `propext`,
`Classical.choice` and `Quot.sound` with `Elements` absent, and include that audit in the
build. Since 22 October (#229), `checks/`, the registry of CI's `check` job, joins them,
so that a check added or removed, or with its command, job or order changed, is named
file by file; it is a check input too (step 4, above). Since 22 October (#249),
`docs/ACCEPTANCE.md` joins them, a check input as well: its table of the limitations
allowed and `check_acceptance.py`'s `ALLOWED_LIMITS`, which
`tests/test_acceptance_limits.py` ties together, change in one pull request, a check
change. A change to any of them needs a new line in the decisions page or a dated entry
in `docs/decisions/` naming each file changed, by its whole path (from the root, or by a
relative link that resolves from the folder of the file that names it, `docs/briefs/`
for the page and `docs/decisions/` for an entry, to exactly that path: for
`model/Model/Audit.lean`, `../../model/Model/Audit.lean` counts, but
`../model/Model/Audit.lean`, `../../../model/Model/Audit.lean` and
`./model/Model/Audit.lean` do not; a line naming `tests/model/lock.sha256` does not name
`model/lock.sha256`; and a mention counts only where it starts the text or follows
whitespace, `(`, `<`, `[`, a backtick, a quotation mark, an apostrophe or `*`, so that
`~/model/lock.sha256` or a URL ending in the path names nothing), the label
`security-review`, and a `/security-review` recorded in the pull request; weakening a
check stays a decision of the owner's ([FORMALIZATION.md](FORMALIZATION.md), section 1).
`Audit/`, `Audit.lean`,
`model/Model/Audit.lean`, `model/Model.lean` and the model's build files are content the
checks judge, not checks, so they stay judged when a check fails with origin/main's copies
(step 4).

**A pull request from a fork** is not merged by `--merge`: the coordinator brings its
commits to a branch of origin with the pre-flight, which opens a pull request of its own,
and closes the fork's with a link to it.

The summary is printed and appended to `~/.cache/stoicheia/pushes.log`, outside the
repository, with each step's full output beside it in `logs/`, and the pre-flight's record
in `preflight/`, which `--branch` and `--merge` write and only `--merge` reads (step 4,
above); origin/main's harness, when it runs in place of another copy, is written to
`harness/`, named by its blobs; and, with `--main-checks-cache`, origin/main's pass of
step 4 in `main-checks/`. `sh scripts/install_hooks.sh` installs the launcher and the
pre-push hook: the hook refuses every push to main, scans a push to any other branch (its
name included) with origin/main's copy of the secret scan (`safe_push.py --scan-push`),
copied out of git and run with git's replacement objects off (#256), whichever remote it
goes to (another remote's main is never run, and without origin/main's copy the push is
refused), and refuses to push or delete a tag. With the
owner's OK for a tag, it is pushed by name, `STOICHEIA_TAG_PUSH=<tag> git push origin
refs/tags/<tag>`, and the hook still scans the commits it points to and an annotated
tag's message. An installed hook or launcher takes a change to its source in
`scripts/hooks/`, #256's among them, only when `sh scripts/install_hooks.sh` is run again
from a checkout of origin/main; until then the pre-flight notes that the installed copy
differs from origin/main's (when origin/main's harness is what runs).
`python3 -m pip install -r scripts/requirements-test_safe_push.txt`, followed in the same
Python environment by `python3 scripts/test_safe_push.py`, installs the pinned YAML parser
and plants a bad commit for each guard, gate and edge case on a throwaway clone, with a
stand-in for gh, and checks that each is refused and a good one proposed and merged. Its
cases include unfinished work left unwritten, closed or unlabelled issues, open labelled
issues, the release held by an open blocker or an unreadable reply, and an ordinary pull
request merging without reading the blockers;
`STOICHEIA_SLOW_TESTS=1` adds one run of the full checks, Lean and all. The
`safe-push-tests` workflow runs the tests, in eight shards and without that run, every six
hours on main and on demand (section 8).
