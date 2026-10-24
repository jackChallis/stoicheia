#!/usr/bin/env python3
"""Tests for scripts/safe_push.py, on a throwaway clone with a bare origin.

    python3 -m pip install -r scripts/requirements-test_safe_push.txt
    python3 scripts/test_safe_push.py        # no Lean, no network; timing in WORKFLOW section 8
    python3 scripts/test_safe_push.py --shard 3/8   # one of the cadence's eight shards (#233)
    python3 scripts/test_safe_push.py --shard 3/8 --ran ran-3.json   # and the list of what it ran
    python3 scripts/test_safe_push.py --cover DIR   # every test ran once, by the lists in DIR
    python3 scripts/test_safe_push.py --times-from-log run.log   # the times, from a CI run's log
    STOICHEIA_SLOW_TESTS=1 python3 scripts/test_safe_push.py FullChecks   # Lean, minutes

The clone is made with `git clone --local --no-hardlinks` of this repository into a temporary
directory: a bare `origin.git` and a working clone of it. Origin's main is this
checkout's HEAD with this checkout's copies of the harness (scripts/safe_push.py, its
hook, its allow-list, its tests) and of the pull request template committed on top, so
that origin/main's harness, which safe_push runs, is the one under test. GitHub is
played by a stand-in for gh (STOICHEIA_TEST_GH): pull requests kept in a JSON file, their
checks set by each test, merged into the bare origin with a merge commit. Each test plants
one commit and runs safe_push.py against that origin:

- each guard refuses its bad commit: a secret, a statement changed without a decision,
  the axiom lock changed without one, a commit that is not a fast-forward, a change to
  heath/ with no leaf named, a whole directory deleted, and a protected path changed
  without a decisions entry naming it;
- a good commit passes, by a dry run and then the pre-flight, from a dirty working tree:
  pushed to its branch, never to main, and its pull request opened with the template's
  body and the pre-flight's summary; then updated, keeping the coordinator's words;
- --branch runs the full checks even when a dry run or the candidate wrote a record;
- --merge refuses a draft, an unticked or missing required box, red or missing CI, and a
  protected change without its label; reruns the pre-flight for a head it has not seen;
  and merges with a merge commit, deleting the branch, its subject naming the owner
  GitHub names for the head (issue #41); and believes gh's exit 0 only once GitHub says
  the pull request merged and origin/main holds the merge commit GitHub names, the merge
  state otherwise unknown, with no revert advised (issue #42);
- trains require a body, read once, and run main's train module; while main has none,
  every train is refused, one adding its own copy too; a body changed during a merge's
  checks refuses the merge; queue rules and main health fail closed, a red main admits
  only the fix its body declares, and a queued head is pinned, followed to merge or
  ejection, and checked on main;
- unfinished work must be written as None or with issues open and labelled blocks-release;
  closed or unlabelled issues and unreadable replies refuse the merge; a release pull
  request waits for every open blocker, while an ordinary pull request never reads that
  list; both None and an open labelled issue pass;
- the pre-push hook refuses every push to main and scans a push to any other branch;
- the review's findings: the harness and the check scripts are origin/main's, an
  allow-list entry the push adds does not count, the heath/ leaves are origin/main's, an
  interruption after the push is "pushed; CI not followed", scratchpad paths and
  machine-made identities are refused, .gitattributes cannot hide a file, and a broad
  allow-list entry is refused;
- the second review's notes: an interruption (Ctrl-C, or SIGTERM to the process alone)
  after the push of a run handed over to origin/main's harness is still exit 3; the
  launcher (`git safe-push`) runs origin/main's copy even when the checkout's never hands
  over, and STOICHEIA_HARNESS is checked; UTF-16 text after 8 KB of prose or binary junk
  is found; an allow-list entry excuses its own value alone, in a binary file too, and
  never a commit message; --merge runs the scan and the guards again whatever the record
  says, and shows its notes; a fork's pull request of the same name is left alone; the
  title, the branch name and an open pull request's body are scanned before the push;
  lakefile.lean and .gitignore are protected; a recased source comment names no leaf; a
  hand edit to PROGRAM.md is not a generated change; an allowed tag is still scanned;
  and an installed hook that differs from origin/main's is noted;
- the final review's findings: values pinned to the edition move with their content,
  while check code with content is kept apart, in step 4's own wiring too; a crash of
  origin/main's render.py is a verdict, and a check failing its own pass refuses; the
  gates read the head's template while origin/main has none, and only what GitHub shows;
  a refusal after the push is exit 3, and a failing `gh pr merge` is believed only when
  nothing merged; every part safe_push wrote in the body is refreshed; the title and the
  branch name are scanned before the merge, whose message is the one scanned, and the
  hook scans a ref's name; an allowed finding's note holds no flagged line, and the home
  directory is written as ~; the hook and the launcher find a Python 3.11 or later; CI
  that appears late is still followed; main moving after the gates, or under the merge;
  a pull request the merge may not merge; the re-run that takes its kind from the open
  pull request; and step 4's notes carried to the merge;
- the re-reviews' findings: an expectation of the certificate dropped or loosened is a
  check change, kept apart, while one moved with its content is a pinned value; a marker
  quoted in the coordinator's words is not one, so an update keeps every word; the gates
  read the body by CommonMark's rules, so a `<!--` in code hides nothing, and a box
  counts only as a list item GitHub shows; a branch renamed before the merge is refused;
  a merge that happened, or may have, is never exit 1; the allow-list test reads the
  committed list through load_allowlist, and the dry-run refusals name the step that
  refused; and the stand-in for gh refuses a second pull request for a head, as gh does,
  while ours is found whatever owner GitHub names for its head;
- issue #95: the tests of an interruption after the push read no wall clock (DRIVER's
  clock, standing still and then leaping an hour at each reading), and DRIVER runs the
  harness committed at BASE, so that neither the machine's load nor a change to this
  checkout's harness while the tests run can move their outcome;
- the model's laws (issue #40): an axiom added in one pull request with its entry in the
  lock, the lock's hash, its line of tests/model/laws.toml, its law's code in search.py
  and hyperbolic.py and the model's account lands as content, and the model's ties hold
  on it; while a law loosened beside it, a helper or tolerance of the harness changed
  (hidden in a comment by a coding cookie, too), two laws of a harness reordered, a line
  of laws.toml moved without its axiom, a new law's code that uses what its allow-list
  does not name (a global, a frame, a lookup by string, a print, the end of the run) or
  changes a shared container under a second name, or laws.toml or the lock deleted, is a
  check change, kept apart; the pre-flight treats an axiom restated or removed with its
  law as content too, while structured.py and exhaustive.py, which name some laws, must
  drop or re-key such a law first; every law of the two harnesses keeps to the
  allow-list, and each entry of the list is one a law needs; and a harness of the model
  that stops before its last line, with status 0, fails the model's run;
- the protected paths of issue #96: Audit/, Audit.lean, model/Model/Audit.lean,
  model/Model.lean and the formal model's build files are refused without a decisions
  entry naming them, a protected path is named only whole (a line naming
  tests/model/lock.sha256 names no model/lock.sha256), and those
  paths stay what the checks judge, so a check change is still kept apart from them;
- the decision entries of docs/decisions/, each a page of its own: a new line in an
  entry the push adds approves as one on the page does, a link there resolving from
  docs/decisions/ for a protected path and a deleted directory alike, its words never
  joined across a blank line or a line that does not count; an entry is only added, so
  a rename or a deletion and re-addition, with edits or without, renews no approval, and
  is refused, as is a copy with carriage returns, zero-width spaces, Braille blanks or
  null noteheads in it; a copy (re-wrapped, re-spaced, reworded in a word, in capitals,
  or with Cyrillic letters for Latin ones) renews no approval, though it is not refused
  for being one, and an entry with a Greek word in it approves as any does; a guard that
  refuses names each line of an entry that did not count and names what it asks for,
  and why, a list of files repeated from the page or from an older entry among them, and
  never a code fence or another line that names nothing it asks for; a short entry
  sharing a line with an older one is an entry, though Git calls it a copy; the folder's
  README may be edited, never deleted, and approves nothing, and is refused, added or
  changed, when it is no UTF-8 text or holds a character an entry may not; a link, a
  name spelled otherwise (a long s among the spellings, wherever it lies) or a file of
  any other name is refused, its path printed with escapes, and so is an entry dated
  before 20 October 2026 or after the day after the earlier of its commit's committer
  date and the machine's own; in an entry and on the page, a mention of a file or a
  directory starts the text or follows whitespace or an opening mark, so that a longer
  path, a home folder's, a drive's or a URL's, names nothing, and every form the guards
  counted before that starts so still counts; a directory whose mention holds a slash
  may end a sentence, but "the figures." names no figures/; the page, deleted, refuses a
  protected change rather than crashing; the revert that safe_push advises keeps the
  record and passes the guards, its entry naming each file in a sentence of its own, and
  restores only what origin/main holds; an abbreviated commit name is as wide as Git
  makes it here;
- the count markers of T1 (#177): a new word in the lock, with Certificate/FIELDS.md's
  count of the words moved with it, lands as content, origin/main's failure noted and the
  commit's own pass holding the count to the lock; while that page changed beyond the
  values between its count markers (a line, a byte beside a marker, a marker added,
  removed or renamed, the file deleted or its mode changed) is a check change, kept apart;
  so is prose between two markers, the markers swapped, a page added, a page either side
  cannot read, a symbolic link, or origin/main's reader missing or not loading; a count
  moved to a value the lock does not give is refused by the commit's own
  check_fidelity.py; a count moved in scripts/, or in code under tests/, is never a pinned
  value; and the markers are read by origin/main's reader, never the commit's;
- the model's page (#187): an axiom added with its law, tests/model/MODEL.md's account
  and its counts moved with it, lands as content, its prose free to move; while a count
  marker of the page added, removed, renamed or reordered, or the page deleted, made executable or
  left unreadable, is a check change, kept apart;
- checks scaled to risk (#292, #301): an R1 commit (a line in a review record) and an R2
  one (a proof file, its record stamped) leave step 4 to CI, with their class reported
  and recorded and every guard run; an R3 commit touching a check, and commits of prose
  with a script or a workflow, take the full path; the commit's own classifier, made to
  class every file R0, does not lower its class, which origin/main's gives; origin/main
  with no classifier, a classifier that fails or prints no class, Git failing and
  unreadable labels are R5; the label release, given or on the open pull request, is R5;
  a classifier at origin/main that disagrees with the check inputs is overruled by them;
  --merge takes a record that left step 4 to CI while the class is still low, and a
  release only on the full pre-flight of its head and with a green run of
  safe-push-tests there, every job passed (none, red, running, at another head, a job
  failed or skipped, or GitHub unreadable each refuse);
- the registry of checks (#229), one file per check of CI's `check` job in checks/: each
  rule of its reader, broken, refuses the whole registry with the file named, from the
  worktree and from Git; section 8's block is its render and CI's `check` job its setup
  and one run of it (any other step, condition or override refused, as before); a train
  that removes a check or empties one changes nothing the pre-flight runs, which is
  origin/main's registry by origin/main's reader, never the commit's or the worktree's;
  origin/main's registry unreadable, or its reader failing, refuses, and with no registry
  at origin/main the lists built in stand in; run_checks.py stops at the first check that
  fails and fails an `empty` check that prints anything; one file more is one check more
  for safe_push, render.py and run_checks.py, and a copy of the tree with one file more
  and its block rendered agrees as the tree does, the harness unchanged and its built-in
  lists pinned to the tests' own; safe_push holds the checks' names itself, the `empty`
  check alone bearing its name and every command named by its words; step 3 reads the
  commit's own registry with the commit's own reader, alone, and refuses a reader that
  works only beside a module of its own; and an entry removed without a decisions entry
  naming it is refused, and with content it would judge, kept apart;
- replacement objects (#256), which git reads in place of the objects they replace while
  a push sends the originals: a token behind a clean stand-in, by `git replace` or in a
  folder GIT_REPLACE_REF_BASE names, is refused by the pre-push hook and by the
  pre-flight's scan, and so it is, by `git replace`, with core.useReplaceRefs=true in the
  clone's config; a commit whose message holds a token, behind a clean commit, and a
  stand-in for origin/main's allow-list that would allow a token are refused by the
  pre-flight; a stand-in for origin/main's safe_push.py is not what the hook runs, the
  launcher copies out, or the hand-over compares; and a clean push beside a replacement
  passes, each test removing what it planted;
- the main-checks cache of #224 (--main-checks-cache): the tree its key names is the one
  base_copies lays down; the key moves with origin/main, either tree, the harness, the
  toolchain, a STOICHEIA_, LEAN, LAKE, PYTHON or LC_ variable but the terminal's, LANG
  and LANGUAGE, and the lists of checks; a miss writes an entry only once origin/main's
  pass has finished, and a hit runs none of it, reports its outcomes as recorded, notes
  included, each note pointing to this run's copy of its log, and is kept apart as a
  miss is; a note made ok, another key's entry, a step missing, extra, out of order or
  of an unknown outcome, a step's seconds an integer of 400 digits, a lone surrogate in a
  step's log, a malformed written time, an entry of a tebibyte (sparse, never read), any
  error at all in reading an entry, an entry or a directory that is a link or of the
  wrong mode, are each refused and the pass recomputed; a directory on another device
  than the one above it is not used; without the flag nothing is read or written, the
  directory not even made, nor with it for a change of R0 to R2; without a sandbox there
  is no cache, nor with a trial whose write fails otherwise than by the sandbox's
  refusal; classification finishes before origin/main's count-marker reader is loaded
  and retained, then the sandbox is activated before commit checks start, and their
  child runs through the sandbox; with platform's caches emptied, no
  process starts but the sandbox while the key is computed and the pass missed and hit;
  in a fresh interpreter, the allow-list is parsed, step 4 is missed and hit, no process
  starts but the sandbox and no module but a builtin is imported once the sandbox is set
  (and the watch refuses a module imported late, and on macOS plistlib, as environment()
  imported it once); the retained count-marker reader cannot be replaced by a module a
  sandboxed child plants beside the harness; the same watch covers a flagged dry run and
  push of an R3 commit; and on macOS a command run there cannot write the cache, nor
  rename a directory above it, and a profile without the rules above the cache is caught;
  and a flagged train/* branch, however written, gets no cache and no sandbox while its
  train check still runs, and the train check refuses under a sandbox (#383);
- and the edge cases, each refused: (1) a credential split over two lines; (2) one
  base64-encoded; (3) a key file added under a name later renamed, a secret taken out
  again within the push, and files renamed to .pem, .key and .env names; (4) symlinks
  into private directories or out of the repository; (5) a statement changed on a
  re-wrapped line, a decision naming another proposition, an old brief line edited in
  place, and a statement's text after a binder's `:=`; (6) the axiom lock changed with a
  decision silent on it, a mention outside the decisions page, or an old line edited;
  (7) stale or hand-edited generated pages; (8) a commit behind origin/main or with an
  unrelated history, and origin/main moving during the checks or at the push; (9) the
  hook given HEAD:main, main, refs/heads/main, --mirror, a forced refspec and tags;
  (10) a dry run, which never pushes, calls no gh, and leaves no worktree or temporary
  file, on success, on a refusal or when interrupted.

The long checks of step 4 (the build and the rest) are skipped by the internal flag
`--_test-skip-checks`, used here and nowhere else; safe_push honours it only against a
local origin, and with it calls only the gh stand-in. A commit of R0 to R2 skips them by
its class instead, as it would without the flag, and its skip line says so. The checks
the guards run themselves (check_fidelity.py and render.py on the commit as committed)
still run. The opt-in FullChecks test runs step 4 for real, once, on a good commit of
R3, as a dry run of the pre-flight. Python 3.11 or later; PyYAML at the version pinned
beside this file, and git.

The cadence workflow, .github/workflows/safe-push-tests.yml, runs the suite as N shards
side by side, `--shard K/N` for each K, N written once, in its matrix (#233): the tests
are listed by unittest's own loader and dealt out by the seconds each took on a GitHub
runner, kept in test_safe_push_times.json beside this file, so that each test runs in
exactly one shard; a test missing there weighs their median. Each shard writes the tests
it ran, with their outcomes (`--ran FILE`), and `--cover DIR` proves from those lists that
every test the loader lists ran once and passed. `--times-from-log` writes the times file
from a CI run's log. Without --shard the whole suite runs.
"""

from __future__ import annotations

import ast
import base64
import contextlib
import copy
import datetime
import fnmatch
import hashlib
import io
import itertools
import json
import os
import platform
import re
import shlex
import shutil
import signal
import stat
import statistics
import subprocess
import sys
import tempfile
import textwrap
import unicodedata
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import yaml

HERE = Path(__file__).resolve().parent
SAFE_PUSH = HERE / "safe_push.py"
INSTALL_HOOKS = HERE / "install_hooks.sh"
SOURCE = HERE.parent
sys.path.insert(0, str(HERE))
import registry  # noqa: E402
import safe_push  # noqa: E402
import review_stamp  # noqa: E402

TMP: Path
ORIGIN: Path
WORK: Path
LOG: Path
BASE: str
GH: Path
GH_STATE: Path
UNDER_TEST: Path      # the harness committed at BASE, which DRIVER runs (setUpModule)
TEST_PATH = os.environ.get("PATH", "")
BRANCH = "test-pr"
DECISIONS = "docs/briefs/0002-decisions.md"
# The files of the harness under test, committed on top of HEAD as origin's main: among
# them the registry of checks and its reader, which step 4 reads at origin/main.
HARNESS_FILES = ("scripts/safe_push.py", "scripts/heath.py", "scripts/test_safe_push.py",
                 "scripts/hooks/pre-push", "scripts/hooks/safe-push", "scripts/install_hooks.sh",
                 "scripts/safe_push_allow.toml", ".github/pull_request_template.md",
                 "scripts/check_release_gate.py", "tests/test_release_gate.py",
                 "tests/certificate_expectations.json", "tests/model/hyperbolic.py",
                 "scripts/risk.py", "scripts/registry.py",
                 *sorted(f"checks/{p.name}" for p in (HERE.parent / "checks").glob("*")
                         if p.is_file() and p.name != ".DS_Store"))


@dataclass(frozen=True)
class WorkflowStep:
    name: str
    uses: str | None
    inputs: tuple[tuple[str, object], ...]
    run: tuple[str, ...]
    environment: tuple[tuple[str, object], ...]
    has_condition: bool
    has_continue_on_error: bool
    continue_on_error: object
    has_shell_override: bool
    has_working_directory: bool


@dataclass(frozen=True)
class WorkflowCheckJob:
    steps: tuple[WorkflowStep, ...]
    environment: tuple[tuple[str, object], ...]
    unmodeled_settings: tuple[str, ...]
    has_condition: bool
    has_continue_on_error: bool
    continue_on_error: object
    has_dependencies: bool
    has_shell_override: bool
    has_working_directory: bool


CHECK_JOB_SETTINGS = frozenset({"runs-on", "steps", "if", "continue-on-error", "needs",
                                "defaults", "env"})


def default_run_settings(mapping: dict, place: str) -> frozenset[str]:
    defaults = mapping.get("defaults")
    if defaults is None:
        return frozenset()
    if not isinstance(defaults, dict):
        raise AssertionError(f"{place} defaults are not a mapping")
    run = defaults.get("run")
    if run is None:
        return frozenset()
    if not isinstance(run, dict):
        raise AssertionError(f"{place} run defaults are not a mapping")
    return frozenset(run)


def mapping_items(mapping: dict, key: str, place: str) -> tuple[tuple[str, object], ...]:
    value = mapping.get(key)
    if value is None:
        return ()
    if not isinstance(value, dict):
        raise AssertionError(f"{place} {key} is not a mapping")
    return tuple(sorted((str(name), item) for name, item in value.items()))


def normalized_check_job(source: str) -> WorkflowCheckJob:
    try:
        workflow = yaml.safe_load(source)
    except yaml.YAMLError as exc:
        raise AssertionError(f"CI workflow is not valid YAML: {exc}") from exc
    if not isinstance(workflow, dict) or not isinstance(workflow.get("jobs"), dict):
        raise AssertionError("CI workflow has no jobs mapping")
    job = workflow["jobs"].get("check")
    if not isinstance(job, dict):
        raise AssertionError("CI workflow has no check job")
    raw_steps = job.get("steps")
    if not isinstance(raw_steps, list):
        raise AssertionError("CI check job has no steps list")
    steps = []
    for index, step in enumerate(raw_steps, 1):
        if not isinstance(step, dict):
            raise AssertionError(f"CI check step {index} is not a mapping")
        name = step.get("name", "")
        if not isinstance(name, str):
            raise AssertionError(f"CI check step {index} has a non-string name")
        place = f"CI check step {name or index}"
        uses = step.get("uses")
        if uses is not None and not isinstance(uses, str):
            raise AssertionError(f"{place} has a non-string uses value")
        run = step.get("run")
        if run is None:
            commands = ()
        elif isinstance(run, str):
            commands = tuple(line.strip() for line in run.splitlines() if line.strip())
        else:
            raise AssertionError(f"{place} has a non-string run value")
        steps.append(WorkflowStep(
            name=name or str(index),
            uses=uses,
            inputs=mapping_items(step, "with", place),
            run=commands,
            environment=mapping_items(step, "env", place),
            has_condition="if" in step,
            has_continue_on_error="continue-on-error" in step,
            continue_on_error=step.get("continue-on-error"),
            has_shell_override="shell" in step,
            has_working_directory="working-directory" in step,
        ))
    defaults = (default_run_settings(workflow, "CI workflow") |
                default_run_settings(job, "CI check job"))
    return WorkflowCheckJob(
        steps=tuple(steps),
        environment=(mapping_items(workflow, "env", "CI workflow") +
                     mapping_items(job, "env", "CI check job")),
        unmodeled_settings=tuple(sorted(str(key) for key in job
                                        if key not in CHECK_JOB_SETTINGS)),
        has_condition="if" in job,
        has_continue_on_error="continue-on-error" in job,
        continue_on_error=job.get("continue-on-error"),
        has_dependencies="needs" in job,
        has_shell_override="shell" in defaults,
        has_working_directory="working-directory" in defaults,
    )


# The whole worktree, as safe_push's step "git status --porcelain is empty" reads it: the
# generated pages and every other file a check might leave changed or new. The registry
# writes it as an entry with `empty = true`, which run_checks.py runs with no pathspec.
FRESHNESS_COMMAND = "git status --porcelain"
RENDER_COMMAND = "python3 scripts/render.py"
# CI's `check` job after its setup: one step, running the registry's checks of the job
# (#229), each as the pull request's registry lists it.
RUN_CHECKS = "python3 scripts/run_checks.py --job check"
# The one step of CI's `model` job that safe_push's MODEL_JOB leaves out, until the
# command joins it (#378; WORKFLOW, section 8).
CI_ONLY_MODEL = ["python3 -I tests/model/results_check.py"]
# Each setup action, with the inputs it may take and the value each must have (ANY_VALUE:
# any). The checkout may only leave its token out of the checkout's git config
# (persist-credentials: false, the boolean itself): that changes no commit and no file
# the checks read, and takes a power away; any other value, or any other input, is
# unmodeled.
ANY_VALUE = object()
SETUP_ACTIONS = {"actions/checkout@v5": {"persist-credentials": False},
                 "actions/setup-python@v5": {"python-version": ANY_VALUE}}
ELAN_INSTALL = (
    "curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh"
    " | sh -s -- -y --default-toolchain none",
    'echo "$HOME/.elan/bin" >> "$GITHUB_PATH"',
)


def is_modeled_setup(step: WorkflowStep) -> bool:
    if step.uses is None:
        return step.run == ELAN_INSTALL
    allowed = SETUP_ACTIONS.get(step.uses)
    return not step.run and allowed is not None and all(
        name in allowed and (allowed[name] is ANY_VALUE or value is allowed[name])
        for name, value in step.inputs)


def enforced_check_commands(job: WorkflowCheckJob) -> list[str]:
    """The commands CI's `check` job runs after its modelled setup, which must be the run
    of the registry's checks alone, once (RUN_CHECKS): no other step, no condition, no
    failure suppressed, and no shell, working directory or environment of its own."""
    if job.unmodeled_settings:
        raise AssertionError(f"CI check job has unmodeled settings {list(job.unmodeled_settings)}")
    if job.has_condition:
        raise AssertionError("CI check job has an if condition")
    if job.has_continue_on_error and job.continue_on_error is not False:
        raise AssertionError("CI check job can continue on error")
    if job.has_dependencies:
        raise AssertionError("CI check job has dependencies")
    if job.has_shell_override:
        raise AssertionError("CI check job has a default shell override")
    if job.has_working_directory:
        raise AssertionError("CI check job has a default working directory")
    if job.environment:
        raise AssertionError("CI check job has an environment override")
    setup_order = (*SETUP_ACTIONS, None)  # The actions, then the elan install.
    setup_index = 0
    commands = []
    for step in job.steps:
        if step.has_condition:
            raise AssertionError(f"CI check step {step.name!r} has an if condition")
        if step.has_continue_on_error and step.continue_on_error is not False:
            raise AssertionError(f"CI check step {step.name!r} can continue on error")
        if step.has_shell_override:
            raise AssertionError(f"CI check step {step.name!r} has a shell override")
        if step.has_working_directory:
            raise AssertionError(f"CI check step {step.name!r} has a working directory")
        if step.environment:
            raise AssertionError(f"CI check step {step.name!r} has an environment override")
        if is_modeled_setup(step):
            if commands:
                raise AssertionError(f"CI check step {step.name!r} is setup after the first check")
            if setup_index == len(setup_order) or step.uses != setup_order[setup_index]:
                raise AssertionError("CI check setup sequence differs from the required prefix")
            setup_index += 1
            continue
        if step.uses is not None or RUN_CHECKS not in step.run:
            raise AssertionError(f"CI check step {step.name!r} is neither the run of the "
                                 "registry's checks nor the modelled setup")
        if setup_index != len(setup_order):
            raise AssertionError("CI check setup prefix is incomplete before the first check")
        if step.run != (RUN_CHECKS,):
            raise AssertionError(f"CI check step {step.name!r} has an unsupported run body")
        commands.append(RUN_CHECKS)
    if commands != [RUN_CHECKS]:
        raise AssertionError("CI check job does not run the registry's checks exactly once")
    return commands


def with_branch(args) -> tuple:
    """The pre-flight for BRANCH, labelled `docs`, unless the arguments say otherwise."""
    if {"--branch", "--merge", "--scan-push"} & set(args):
        return tuple(args)
    return ("--branch", BRANCH, *args) + (() if "--label" in args else ("--label", "docs"))


def git(cwd, *args, env=None, check=True) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {cwd}:\n{r.stdout}{r.stderr}")
    return r.stdout


def short_sha(sha: str) -> str:
    """A commit's short form as Git gives it in the clone under test (WORK), which is how
    safe_push writes it (`git log --format=%h`). Git sets the width, seven digits or more
    as the object count grows, or as core.abbrev says, so a test reads it here and never
    assumes it (issue #178)."""
    return git(WORK, "log", "-1", "--format=%h", sha).strip()


def clean_env() -> dict:
    env = dict(os.environ, STOICHEIA_PUSH_LOG=str(LOG), STOICHEIA_TEST_GH=str(GH),
               STOICHEIA_FAKE_GH_STATE=str(GH_STATE), STOICHEIA_FAKE_GH_ORIGIN=str(ORIGIN),
               STOICHEIA_PYTHON=sys.executable, PATH=TEST_PATH)
    for name in ("STOICHEIA_SAFE_PUSH", "STOICHEIA_HARNESS", "STOICHEIA_TAG_PUSH",
                 "STOICHEIA_FAKE_GH_KILL", "STOICHEIA_FAKE_GH_MERGE", "STOICHEIA_TEST_CI_POLL",
                 "STOICHEIA_TEST_CI_APPEAR", "STOICHEIA_TEST_CLOCK",
                 # Git's replacement objects (#256): a test that plants one names it itself.
                 "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE"):
        env.pop(name, None)
    return env


# Planted secrets are built when the tests run, so that this file passes the scan itself.
TOKEN = base64.b64encode(hashlib.sha256(b"a planted token").digest()).decode()
PRIVATE_DIR = "/" + "Users" + "/someone/" + "Down" + "loads/notes.txt"
KEY_HEADER = "-----BEGIN " + "RSA PRIVATE" + " KEY-----"
GH_TOKEN = "gh" + "p_" + hashlib.sha256(b"a planted GitHub token").hexdigest()[:36]
HEXKEY = hashlib.sha256(b"a planted hex key").hexdigest()
TILDE_DOWNLOADS = "~/" + "Down" + "loads"
PRIVATE_SCANS = "../../" + "secret" + "s2026/scans"
FOLDED_HOME = "-" + "Users" + "-someone"
SCRATCHPAD = "/private" + "/tmp/" + "claude" + "-501/" + FOLDED_HOME + "/0123/scratchpad/x.txt"

PASSING = [{"name": n, "bucket": "pass", "state": "SUCCESS", "workflow": "CI"}
           for n in ("check", "model", "negative", "formal-model", "acceptance")]
# A green run of the safe-push-tests workflow, as GitHub's API gives it, with its jobs: the
# stand-in for gh gives it at every head unless a test says otherwise, as it gives PASSING
# (a release's merge gate asks for one at its head, #301). `report` runs only for a red
# run on main, so a green one skips it. The shards are jobs of the run too, named as GitHub
# names a matrix's jobs (#233).
SUITE_JOBS = [{"name": n, "status": "completed", "conclusion": "success"}
              for n in ("safe-push-tests", "negative-tests", "formal-model-kernel",
                        *(f"safe-push-shards ({k})" for k in range(1, 9)))] + \
    [{"name": "report", "status": "completed", "conclusion": "skipped"}]
GREEN_SUITE = {"id": 501, "status": "completed", "conclusion": "success", "jobs": SUITE_JOBS}

# Judges the runs of a passing --fast run made by hand, then the same with the structured
# run's last line dropped; prints the two lists of failures.
JUDGE_RUNS = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import run


def made(key, script, laws, head='', tail=''):
    r = run.Run(key, script)
    r.code, r.err, r.twice, r.laws = 0, '', set(), laws
    r.derived = {name: (5000, 7, 0) for name in run.PROPERTIES} if key == 'structured' else {}
    r.out = head + ''.join(f'{n} {t} {h} {c}\n' for n, (t, h, c) in laws.items()) + tail
    return r


def runs(structured_tail):
    met = {law: (2000, 5, 0) for law in run.LAWS}
    hyperbolic = {law: (300, 5, 3 if law in run.EXPECTED_TO_FAIL else 0) for law in run.LAWS}
    return [made('search-seed1', 'search.py', met,
                 tail=f'axioms checked: {len(met)}  total counterexamples: 0\n'),
            made('structured', 'structured.py', {run.LAWS[0]: (5000, 7, 0)},
                 tail=structured_tail + 'never met: []\n'),
            made('mutations', 'mutations.py', {}, tail='15/15 mutations caught\n'),
            made('grid_check', 'grid_check.py', {}, tail='failures 0 Counter()\n'),
            made('angle_check', 'angle_check.py', {},
                 tail='triple incidence grid failures: 0 []\nfloat failures: {}\n'),
            made('hyperbolic', 'hyperbolic.py', hyperbolic, head='self-test: passed\n',
                 tail=f'axioms checked: {len(hyperbolic)}  counterexamples to the other axioms: 0\n')]


print(json.dumps([run.judge(runs('structured total counterexamples: 0\n')),
                  run.judge(runs(''))]))
'''

# A stand-in for gh: pull requests in a JSON file; checks as each test sets them; a merge
# made in the bare origin with a merge commit, as GitHub makes it.
FAKE_GH = r'''#!@PYTHON@
import json, os, re, subprocess, sys, time

STATE = os.environ["STOICHEIA_FAKE_GH_STATE"]
ORIGIN = os.environ["STOICHEIA_FAKE_GH_ORIGIN"]


def load():
    with open(STATE) as f:
        return json.load(f)


def save(s):
    with open(STATE, "w") as f:
        json.dump(s, f, indent=1)


def head_of(branch):
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "refs/heads/" + branch],
                       cwd=ORIGIN, capture_output=True, text=True)
    return r.stdout.strip()


def opt(args, name):
    return args[args.index(name) + 1] if name in args else None


def opts(args, name):
    return [args[i + 1] for i, a in enumerate(args) if a == name]


def fields(pr, wanted):
    # A fork's pull request has a head of its own, never origin's branch of that name.
    fork = pr.get("isCrossRepository", False)
    head = pr.get("forkHead", "") if fork else \
        (head_of(pr["headRefName"]) or pr.get("mergedHead", ""))
    full = dict(pr, headRefOid=head, labels=[{"name": n} for n in pr["labels"]],
                isCrossRepository=fork,
                headRepositoryOwner=pr.get("headRepositoryOwner", {"login": "test"}))
    if pr.get("omit_labels"):
        del full["labels"]
    elif "raw_labels" in pr:
        full["labels"] = pr["raw_labels"]
    return {k: full[k] for k in wanted.split(",") if k in full}


def kill_on_watch():
    """STOICHEIA_FAKE_GH_KILL=<pid file>:<signal>: while following CI, signal the
    process the pid file names, as a Ctrl-C or a supervisor's timeout would, and go on
    watching until killed."""
    spec = os.environ.get("STOICHEIA_FAKE_GH_KILL")
    if not spec:
        return
    pidfile, signum = spec.rsplit(":", 1)
    for _ in range(100):
        if os.path.exists(pidfile) and open(pidfile).read().strip():
            break
        time.sleep(0.1)
    os.kill(int(open(pidfile).read()), int(signum))
    time.sleep(60)


def queue_merge(s, pr):
    """Make the queue's automatic merge in the local origin."""
    sha, base = head_of(pr["headRefName"]), head_of("main")
    tree = subprocess.run(["git", "merge-tree", "--write-tree", base, sha], cwd=ORIGIN,
                          capture_output=True, text=True, check=True).stdout.splitlines()[0]
    env = dict(os.environ, GIT_AUTHOR_NAME="GitHub", GIT_AUTHOR_EMAIL="noreply@github.com",
               GIT_COMMITTER_NAME="GitHub", GIT_COMMITTER_EMAIL="noreply@github.com")
    second = base if s.get("queue_result") == "wrong-parent" else sha
    oid = subprocess.run(["git", "commit-tree", tree, "-p", base, "-p", second,
                          "-m", "Merge pull request #%d" % pr["number"]], cwd=ORIGIN,
                         env=env, capture_output=True, text=True, check=True).stdout.strip()
    if s.get("queue_result") != "off-main":
        subprocess.run(["git", "update-ref", "refs/heads/main", oid, base], cwd=ORIGIN,
                       check=True)
    pr.update(state="MERGED", mergedHead=sha, mergeQueueEntry=None,
              mergeCommit=None if s.get("queue_result") == "no-commit" else {"oid": oid})


def release_api(path):
    """The release gate's reads (the repository, blocks-release issues, one issue, the
    safe-push-tests runs at a head and a run's jobs), which the release tests answer;
    every other API read goes to api()."""
    return path == "repos/test/stoicheia" or "labels=blocks-release" in path \
        or re.fullmatch(r"repos/test/stoicheia/issues/\d+", path) is not None \
        or path.startswith("repos/test/stoicheia/actions/workflows/safe-push-tests.yml/") \
        or path.startswith("repos/test/stoicheia/actions/runs/")


def api(s, args):
    """REST pages and GraphQL queue responses, with each fault supplied by a test."""
    endpoint = args[1]
    if endpoint.endswith("/rules/branches/main"):
        print(json.dumps(s.get("rules", [[]])))
        return s.get("rules_exit", 0)
    if "/issues?" in endpoint and "labels=main-red" in endpoint:
        print(json.dumps(s.get("main_red_issues", [[]])))
        return s.get("main_red_issues_exit", 0)
    if "/actions/workflows/post-merge.yml/runs?" in endpoint:
        if s.get("runs_404"):
            print(json.dumps({"message": "Not Found", "status": "404"}))
            print("gh: Not Found (HTTP 404)", file=sys.stderr)
            return 1
        print(json.dumps(s.get("runs", [{"total_count": 0, "workflow_runs": []}])))
        return s.get("runs_exit", 0)
    if "/check-runs?" in endpoint:
        print(json.dumps(s.get("group_checks", [{"total_count": 1, "check_runs": [
            {"name": "queue-integrity", "status": "completed", "conclusion": "failure"}]}])))
        return 0
    if endpoint != "graphql":
        print("fake gh: unknown API endpoint", file=sys.stderr)
        return 1
    values = dict(value.split("=", 1) for value in opts(args, "-f") + opts(args, "-F"))
    query = values.get("query", "")
    pr = s["prs"][0]
    sha = head_of(pr["headRefName"]) or pr.get("mergedHead")
    if "enqueuePullRequest" in query:
        if "expectedHeadOid:$head" not in query or values.get("head") != sha \
                or values.get("id") != "PR_1":
            print(json.dumps({"errors": [{"message": "head moved or missing pin"}]}))
            return 1
        pr["mergeQueueEntry"] = {"id": "MQ_1", "headCommit": {"oid": sha}}
        s["enqueued"] = True
        save(s)
        entry = dict(pr["mergeQueueEntry"], pullRequest={"id": "PR_1", "headRefOid": sha})
        print(json.dumps({"data": {"enqueuePullRequest": {"mergeQueueEntry": entry}}}))
        return 0
    if s.get("enqueued"):
        outcome = s.get("queue_result", "merged")
        if outcome == "ejected":
            pr["mergeQueueEntry"] = None
        elif outcome == "unknown":
            print(json.dumps({"data": {"repository": None}}))
            return 0
        elif outcome != "waiting":
            queue_merge(s, pr)
        save(s)
    view = fields(pr, "state,headRefOid,headRefName,baseRefName,mergeCommit,mergeQueueEntry")
    # GitHub's GraphQL gives every field asked for, null when there is none.
    view.setdefault("mergeCommit", None)
    view.setdefault("mergeQueueEntry", None)
    view["id"] = "PR_1"
    print(json.dumps({"data": {"repository": {"pullRequest": view}}}))
    return 0


def main(argv):
    s = load()
    s["calls"].append(argv)
    save(s)
    args = list(argv)
    if "-R" in args:
        i = args.index("-R")
        del args[i:i + 2]
    cmd = args[:2]
    if cmd == ["auth", "status"]:
        return 0
    if args[0] == "api" and not release_api(args[-1]):
        return api(s, args)
    if args[0] == "api":
        path = args[-1]
        # The runs of safe-push-tests at a head, and a run's jobs: "suite_runs" maps a head
        # (or "*", any other) to its runs, each with its jobs; a run's own "head_sha", when
        # it has one, stands for a run at another head; "suite_read_fail" fails the read.
        if path.startswith("repos/test/stoicheia/actions/"):
            if s.get("suite_read_fail"):
                return 1
            suite = s.get("suite_runs", {})
            m = re.fullmatch(r"repos/test/stoicheia/actions/workflows/safe-push-tests\.yml/"
                             r"runs\?head_sha=([0-9a-f]+)&per_page=100", path)
            if m:
                found = [dict({k: v for k, v in r.items() if k != "jobs"},
                              head_sha=r.get("head_sha", m.group(1)),
                              path=".github/workflows/safe-push-tests.yml")
                         for r in suite.get(m.group(1), suite.get("*", []))]
                print(json.dumps({"total_count": len(found), "workflow_runs": found}))
                return 0
            m = re.fullmatch(r"repos/test/stoicheia/actions/runs/(\d+)/jobs\?per_page=100",
                             path)
            for run in (r for listed in suite.values() for r in listed):
                if m and run["id"] == int(m.group(1)):
                    print(json.dumps({"total_count": len(run["jobs"]), "jobs": run["jobs"]}))
                    return 0
            return 1
        if path == "repos/test/stoicheia":
            print(s.get("repository_output", json.dumps({
                "url": "https://api.github.com/repos/test/stoicheia"})))
            return 1 if s.get("repository_read_fail") else 0
        if s.get("issue_read_fail"):
            # Even valid stdout on a failed read must not pass either gate.
            print("[]")
            return 1
        if "issue_output" in s:
            print(s["issue_output"])
            return 0
        issues = s.get("issues", [])
        if path == "repos/test/stoicheia/issues?labels=blocks-release&state=open&per_page=100":
            if "--paginate" not in args:
                return 2
            found = [i for i in issues if i["state"].lower() == "open" and
                     "blocks-release" in [(v.get("name") if isinstance(v, dict) else v).lower()
                                         for v in i["labels"]]]
            # Two concatenated pages, as gh api --paginate prints them.
            print(json.dumps(found[:1]))
            print(json.dumps(found[1:]))
            return 0
        if path.startswith("repos/test/stoicheia/issues/"):
            number = int(path.rsplit("/", 1)[1])
            issue = next((i for i in issues if i["number"] == number), None)
            if issue is not None:
                print(json.dumps(issue))
                return 0
        return 1
    if cmd == ["label", "list"]:
        print(json.dumps([{"name": n} for n in s["labels"]]))
        return 0
    if cmd == ["label", "create"]:
        s["labels"].append(args[2])
        save(s)
        return 0
    if cmd == ["pr", "list"]:
        found = [p for p in s["prs"] if p["headRefName"] == opt(args, "--head")
                 and p["state"] == "OPEN"]
        print(json.dumps([fields(p, opt(args, "--json")) for p in found]))
        return 0
    if cmd == ["pr", "create"]:
        # As GitHub: one open pull request for a head (origin's branch) and a base.
        head, base = opt(args, "--head"), opt(args, "--base")
        same = [p for p in s["prs"] if p["state"] == "OPEN" and p["headRefName"] == head
                and p["baseRefName"] == base and not p.get("isCrossRepository")]
        if same:
            print('a pull request for branch "%s" into branch "%s" already exists:\n%s'
                  % (head, base, same[0]["url"]), file=sys.stderr)
            return 1
        n = len(s["prs"]) + 1
        labels = opts(args, "--label")
        if any(n_ not in s["labels"] for n_ in labels):
            print("could not add label: not found", file=sys.stderr)
            return 1
        with open(opt(args, "--body-file")) as f:
            body = f.read()
        s["prs"].append({"number": n, "title": opt(args, "--title"), "body": body,
                         "headRefName": opt(args, "--head"), "baseRefName": opt(args, "--base"),
                         "isDraft": "--draft" in args, "labels": labels, "state": "OPEN",
                         "url": "https://github.invalid/test/stoicheia/pull/%d" % n})
        save(s)
        print(s["prs"][-1]["url"])
        return 0
    n = int(args[2]) if len(args) > 2 and args[2].isdigit() else None
    pr = next((p for p in s["prs"] if p["number"] == n), None)
    if pr is None:
        print("fake gh: no such pull request: %s" % argv, file=sys.stderr)
        return 1
    if cmd == ["pr", "view"]:
        if opt(args, "--json") == "labels" and s.get("label_read_fail"):
            print(json.dumps({"labels": [{"name": "release"}]}))
            return 1
        # "rename": {"views": n, "to": name}: after n views, the branch is renamed on
        # GitHub, its head kept, as a rename in GitHub's page would leave it.
        rename = s.get("rename")
        if rename:
            rename["seen"] = rename.get("seen", 0) + 1
            if rename["seen"] > rename["views"] and pr["headRefName"] != rename["to"]:
                head = head_of(pr["headRefName"])
                subprocess.run(["git", "update-ref", "refs/heads/" + rename["to"], head],
                               cwd=ORIGIN, check=True)
                subprocess.run(["git", "update-ref", "-d", "refs/heads/" + pr["headRefName"]],
                               cwd=ORIGIN, check=True)
                pr["headRefName"] = rename["to"]
            save(s)
        # "late_label": {"views": n, "label": name}: after n views, the pull request carries
        # the label, as one given while --merge runs would leave it.
        late = s.get("late_label")
        if late:
            late["seen"] = late.get("seen", 0) + 1
            if late["seen"] > late["views"] and late["label"] not in pr["labels"]:
                pr["labels"].append(late["label"])
            save(s)
        # "reread_body": the body GitHub gives the merge's own read of the body alone,
        # as an edit made between the gates and that read would leave it.
        if opt(args, "--json") == "body" and "reread_body" in s:
            pr["body"] = s["reread_body"]
            save(s)
        if opt(args, "--json") == "body" and "after_body" in s:
            s.update(s.pop("after_body"))
            save(s)
        # "relabel": the labels GitHub gives the merge's own read of the labels alone, as
        # a label given between the gates and the merge would leave them.
        if opt(args, "--json") == "labels" and "relabel" in s:
            pr["labels"] = s["relabel"]
            save(s)
        print(json.dumps(fields(pr, opt(args, "--json"))))
        return 0
    if cmd == ["pr", "edit"]:
        if opt(args, "--body-file"):
            with open(opt(args, "--body-file")) as f:
                pr["body"] = f.read()
        if opt(args, "--title"):
            pr["title"] = opt(args, "--title")
        for label in opts(args, "--add-label"):
            if label not in s["labels"]:
                print("'%s' not found" % label, file=sys.stderr)
                return 1
            if label not in pr["labels"]:
                pr["labels"].append(label)
        save(s)
        return 0
    if cmd == ["pr", "ready"]:
        pr["isDraft"] = "--undo" in args
        save(s)
        return 0
    if cmd == ["pr", "checks"]:
        sha = head_of(pr["headRefName"])
        checks = s["checks"].get(sha, s["checks"]["*"])
        if "--watch" not in args:
            # Real gh, until CI registers on a new head: nothing on stdout, exit 1.
            asked = s.setdefault("asked", {})
            asked[sha] = asked.get(sha, 0) + 1
            save(s)
            if asked[sha] <= s.get("nochecks", 0):
                print("no checks reported on the '%s' branch" % pr["headRefName"],
                      file=sys.stderr)
                return 1
        if "--watch" in args:
            if "watch_labels" in s:
                pr["labels"] = s["watch_labels"]
            if "watch_raw_labels" in s:
                pr["raw_labels"] = s["watch_raw_labels"]
            if s.get("watch_omit_labels"):
                pr["omit_labels"] = True
            save(s)
            kill_on_watch()
            return 0 if all(c["bucket"] == "pass" for c in checks) else 1
        print(json.dumps(checks))
        return 0
    if cmd == ["pr", "merge"]:
        # STOICHEIA_FAKE_GH_MERGE: "fail-before" refuses; "fail-after" merges and then
        # fails, as gh does when it cannot delete the branch; "main-first:<sha>" moves
        # main to <sha> first, as another merge landing at that moment would;
        # "flag:<path>" makes the file <path> once merged. Three exit 0 with no merge on
        # main that GitHub vouches for (issue #42): "queue" merges nothing, as gh does
        # when a merge queue or auto-merge takes the pull request to merge later;
        # "off-main" says merged, naming a merge commit that main does not hold
        # ("off-main:<ref>" puts it on <ref>, so that a fetch brings it, and only main's
        # history can show it is not the merge); and "no-commit" merges, but GitHub names
        # no merge commit.
        how = os.environ.get("STOICHEIA_FAKE_GH_MERGE", "")
        if "--merge" not in args or "--squash" in args or "--rebase" in args:
            return 1
        if how == "fail-before":
            print("GraphQL: Base branch was modified", file=sys.stderr)
            return 1
        sha = head_of(pr["headRefName"])
        if opt(args, "--match-head-commit") != sha:
            print("head moved", file=sys.stderr)
            return 1
        if how == "queue":
            print("Pull request #%d will be added to the merge queue for main when ready" % n)
            return 0
        if how.startswith("main-first:"):
            subprocess.run(["git", "update-ref", "refs/heads/main", how.split(":", 1)[1]],
                           cwd=ORIGIN, check=True)
        main = subprocess.run(["git", "rev-parse", "refs/heads/main"], cwd=ORIGIN,
                              capture_output=True, text=True, check=True).stdout.strip()
        env = dict(os.environ, GIT_AUTHOR_NAME="GitHub", GIT_AUTHOR_EMAIL="noreply@github.com",
                   GIT_COMMITTER_NAME="GitHub", GIT_COMMITTER_EMAIL="noreply@github.com")
        message = ["-m", opt(args, "--subject") or "Merge pull request #%d" % n]
        if opt(args, "--body"):
            message += ["-m", opt(args, "--body")]
        merge = subprocess.run(["git", "commit-tree", sha + "^{tree}", "-p", main, "-p", sha,
                                *message], cwd=ORIGIN, env=env,
                               capture_output=True, text=True, check=True).stdout.strip()
        if how.startswith("off-main:"):
            subprocess.run(["git", "update-ref", how.split(":", 1)[1], merge], cwd=ORIGIN,
                           check=True)
        elif how != "off-main":
            subprocess.run(["git", "update-ref", "refs/heads/main", merge, main], cwd=ORIGIN,
                           check=True)
        if "--delete-branch" in args and how != "fail-after":
            subprocess.run(["git", "update-ref", "-d", "refs/heads/" + pr["headRefName"]],
                           cwd=ORIGIN, check=True)
        pr["state"], pr["mergedHead"] = "MERGED", sha
        pr["mergeCommit"] = None if how == "no-commit" else {"oid": merge}
        save(s)
        if how.startswith("flag:"):
            open(how.split(":", 1)[1], "w").close()
        if how == "fail-after":
            print("failed to delete remote branch %s: connection reset" % pr["headRefName"],
                  file=sys.stderr)
            return 1
        return 0
    print("fake gh: not understood: %s" % argv, file=sys.stderr)
    return 2


sys.exit(main(sys.argv[1:]))
'''


def reset_gh() -> None:
    GH_STATE.write_text(json.dumps({"prs": [], "labels": ["release", "blocks-release"],
                                    "issues": [], "checks": {"*": PASSING},
                                    "suite_runs": {"*": [GREEN_SUITE]}, "calls": []}))


def hermetic_git() -> None:
    """The test process's git, and every process it starts, reads no variable of git's
    that the runner set and no global or system configuration (#360). Run under a hook,
    the runner's GIT_DIR and GIT_INDEX_FILE named the hook's repository, and the module's
    own git (setUpModule's clone, config and commit among it) acted on that repository;
    a global core.hooksPath could reach them too, running its hooks on the tests' commits
    and taking install_hooks.sh's hooks where it points. Each test that needs a variable
    of git's (a replacement's GIT_REPLACE_REF_BASE, a hook's GIT_DIR) sets it itself."""
    for name in [name for name in os.environ if name.startswith("GIT_")]:
        del os.environ[name]
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull


# The line setUpModule prints when it is done: GitHub stamps each line of a CI log with its
# time, and --times-from-log measures the setup up to this one (#233).
SETUP_DONE = "setUpModule is done: the throwaway clone and its bare origin are ready."


def setUpModule():
    global TMP, ORIGIN, WORK, LOG, BASE, GH, GH_STATE, UNDER_TEST, TEST_PATH
    hermetic_git()
    if sys.platform == "darwin" and shutil.which("git") == "/usr/bin/git":
        # The system shim leaves xcrun_db in TMPDIR. Use the selected Git directly so
        # that dry-run cleanup still requires an empty temporary directory.
        selected = subprocess.run(["xcrun", "--find", "git"], capture_output=True,
                                  text=True, check=True).stdout.strip()
        TEST_PATH = str(Path(selected).parent) + os.pathsep + TEST_PATH
    TMP = Path(tempfile.mkdtemp(prefix="stoicheia-safe-push-test-"))
    ORIGIN, WORK, LOG = TMP / "origin.git", TMP / "work", TMP / "cache" / "pushes.log"
    GH, GH_STATE = TMP / "fake-gh", TMP / "fake-gh.json"
    GH.write_text(FAKE_GH.replace("@PYTHON@", sys.executable))
    GH.chmod(0o755)
    reset_gh()
    common = git(SOURCE, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    head = git(SOURCE, "rev-parse", "HEAD").strip()
    # Copy the objects: a sandbox may read the source repository but refuse hard links
    # to its files. All commits and ref changes stay in the temporary clone.
    git(TMP, "clone", "--quiet", "--bare", "--local", "--no-hardlinks", common, str(ORIGIN))
    git(ORIGIN, "update-ref", "refs/heads/main", head)
    git(ORIGIN, "symbolic-ref", "HEAD", "refs/heads/main")
    git(TMP, "clone", "--quiet", "--local", str(ORIGIN), str(WORK))
    git(WORK, "config", "user.name", "safe_push test")
    git(WORK, "config", "user.email", "safe-push-test@example.invalid")
    git(WORK, "config", "commit.gpgsign", "false")
    git(WORK, "checkout", "--quiet", "--detach", head)
    for rel in HARNESS_FILES:
        if (SOURCE / rel).exists():
            (WORK / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / rel, WORK / rel)
            git(WORK, "add", "--", rel)
    if git(WORK, "status", "--porcelain").strip():
        git(WORK, "commit", "-q", "-m", "The harness under test")
        git(WORK, "push", "--quiet", "--no-verify", "origin", "HEAD:refs/heads/main")
    BASE = git(WORK, "rev-parse", "HEAD").strip()
    # DRIVER runs the harness as BASE holds it, from a directory of its own, as a hand-over
    # runs origin/main's: had it run this checkout's copy, a change to that copy while the
    # tests run would make it hand over to origin/main's, out of DRIVER's reach (#95).
    UNDER_TEST = TMP / "harness-under-test"
    UNDER_TEST.mkdir()
    for name in ("safe_push.py", "heath.py"):
        (UNDER_TEST / name).write_bytes(subprocess.run(
            ["git", "show", f"{BASE}:scripts/{name}"], cwd=WORK, capture_output=True,
            check=True).stdout)
    train = safe_push.show_bytes(WORK, BASE, "scripts/check_train.py")
    if train is not None:
        (UNDER_TEST / "check_train.py").write_bytes(train)
    git(WORK, "fetch", "--quiet", "origin")
    r = subprocess.run(["sh", str(INSTALL_HOOKS)], cwd=WORK, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    print(SETUP_DONE, file=sys.stderr, flush=True)


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


class Clone(unittest.TestCase):
    """Each test starts from origin/main at BASE, a clean clone, no branch on origin but
    main, and no pull request."""

    def setUp(self):
        git(ORIGIN, "update-ref", "refs/heads/main", BASE)
        for ref in git(ORIGIN, "for-each-ref", "--format=%(refname)", "refs/heads/").split():
            if ref != "refs/heads/main":
                git(ORIGIN, "update-ref", "-d", ref)
        git(WORK, "fetch", "--quiet", "--prune", "origin")
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        git(WORK, "clean", "-fdq")
        reset_gh()

    def text(self, path: str) -> str:
        return (WORK / path).read_text()

    def replaced(self, path: str, old: str, new: str) -> str:
        text = self.text(path)
        self.assertEqual(text.count(old), 1, f"{path}: expected one {old!r}")
        return text.replace(old, new)

    def commit(self, message: str, write: dict | None = None, remove=(), env=None) -> str:
        for path, text in (write or {}).items():
            (WORK / path).parent.mkdir(parents=True, exist_ok=True)
            if isinstance(text, bytes):
                (WORK / path).write_bytes(text)
            else:
                (WORK / path).write_text(text)
            git(WORK, "add", "--", path)
        for path in remove:
            git(WORK, "rm", "-r", "-q", "--", path)
        git(WORK, "commit", "-q", "-m", message, env=env)
        return git(WORK, "rev-parse", "HEAD").strip()

    def new_base(self, message: str, write: dict) -> str:
        """A commit on origin's main, as a merged pull request would leave it."""
        sha = self.commit(message, write)
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{sha}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        return sha

    def safe_push(self, *args, env=None, script=SAFE_PUSH) -> subprocess.CompletedProcess:
        """safe_push.py under the internal test flag; the pre-flight for BRANCH unless the
        arguments name --branch, --merge or --scan-push."""
        args = with_branch(args)
        return subprocess.run([sys.executable, str(script), "--_test-skip-checks", *args],
                              cwd=WORK, env=env or clean_env(), capture_output=True, text=True)

    def origin_main(self) -> str:
        return git(ORIGIN, "rev-parse", "refs/heads/main").strip()

    def origin_branch(self, name: str = BRANCH) -> str | None:
        r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{name}"],
                           cwd=ORIGIN, capture_output=True, text=True)
        return r.stdout.strip() or None

    def guard(self, out: str, name: str) -> str | None:
        """The outcome a step's line reports: "ok", "FAIL", "note", or None if absent."""
        m = re.search(r"^\s+(ok|FAIL|note)\s+%s:" % re.escape(name), out, re.M)
        return m.group(1) if m else None

    def step(self, out: str, name: str) -> str | None:
        """A step's outcome, whether or not its line carries a detail after a colon."""
        m = re.search(r"^\s+(ok|FAIL|skip|note)\s+%s(:|\s+\(|$)" % re.escape(name), out, re.M)
        return m.group(1) if m else None

    def merges(self) -> list[list[str]]:
        """The `gh pr merge` calls the stand-in for gh has had."""
        return [c for c in self.gh_state()["calls"] if c[:2] == ["pr", "merge"]]

    def assertRefused(self, r, *wanted):
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("REFUSED", out)
        for w in wanted:
            self.assertIn(w, out)
        self.assertEqual(self.origin_main(), BASE, "a refused push moved origin/main")
        self.assertIsNone(self.origin_branch(), "a refused push pushed the branch")
        return out

    def decision(self, line: str) -> dict:
        return {DECISIONS: self.text(DECISIONS) + f"\n- **A decision for the test.** {line}\n"}

    def gh_state(self) -> dict:
        return json.loads(GH_STATE.read_text())

    def set_gh(self, change) -> None:
        state = self.gh_state()
        change(state)
        GH_STATE.write_text(json.dumps(state))

    # Issue #256: git reads a replacement object in place of the object it replaces, while
    # a push sends the original. REPLACE_REFS: git's own folder of replacements, and the
    # tests' own, which GIT_REPLACE_REF_BASE names in its place.
    REPLACE_REFS = ("refs/replace/", "refs/stand-ins/")
    CLEAN_NOTES = "Some notes.\n"

    def blob(self, text: str) -> str:
        """A blob holding `text`, written to WORK's objects."""
        return subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=WORK, input=text,
                              capture_output=True, text=True, check=True).stdout.strip()

    def stand_in(self, original: str, text: str, base: str = "refs/replace/") -> dict:
        """A blob holding `text` put in place of the blob `original` (replace_object)."""
        return self.replace_object(original, self.blob(text), base)

    def replace_object(self, original: str, replacement: str,
                       base: str = "refs/replace/") -> dict:
        """The object `replacement` put in place of `original` for git's reading in WORK:
        by `git replace` under refs/replace/, or by a ref of the test's own under `base`.
        The environment a git command needs to read it is returned: nothing more for
        refs/replace/, GIT_REPLACE_REF_BASE for another folder. Clone.setUp removes no
        replacement, so the ref is removed when the test ends, and WORK and origin are then
        checked to hold none."""
        if not getattr(self, "replacements_checked", False):
            self.replacements_checked = True
            self.addCleanup(self.assertNoReplacements)
        self.addCleanup(git, WORK, "update-ref", "-d", base + original, check=False)
        if base == "refs/replace/":
            git(WORK, "replace", original, replacement)
            return {}
        git(WORK, "update-ref", base + original, replacement)
        return {"GIT_REPLACE_REF_BASE": base}

    def assertNoReplacements(self) -> None:
        for repo in (WORK, ORIGIN):
            left = git(repo, "for-each-ref", "--format=%(refname)", *self.REPLACE_REFS)
            self.assertEqual(left, "", f"replacement refs left in {repo}")

    def replace_refs_on_in_config(self) -> None:
        """core.useReplaceRefs=true in WORK's own config, removed when the test ends, and
        WORK's config then checked to hold none. Git from 2.19 to 2.41 lets it turn
        replacements back on despite GIT_NO_REPLACE_OBJECTS; from 2.42 the variable wins,
        so there a test that uses this passes with either the variable or the harness's
        `-c core.useReplaceRefs=false` alone."""
        def remove() -> None:
            git(WORK, "config", "--local", "--unset-all", "core.useReplaceRefs", check=False)
            left = git(WORK, "config", "--local", "--get-all", "core.useReplaceRefs",
                       check=False)
            self.assertEqual(left, "", "core.useReplaceRefs left in WORK's config")
        self.addCleanup(remove)
        git(WORK, "config", "--local", "core.useReplaceRefs", "true")

    def assertStandsIn(self, rev: str, path: str, text: str, env: dict) -> None:
        """git, as the planted environment has it, reads `text` at `rev`:`path`: so the
        stand-in is live, and a scan that reads it would pass what the push sends."""
        shown = git(WORK, "show", f"{rev}:{path}", env=dict(clean_env(), **env))
        self.assertEqual(shown, text, "git does not read the stand-in")

    def hidden_token(self, base: str = "refs/replace/") -> tuple[str, str, dict]:
        """A commit adding a token to docs/notes.md, the token's blob replaced by a clean
        one (stand_in): the commit, the token's blob, and the environment that reads the
        stand-in."""
        bad = self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        blob = git(WORK, "rev-parse", f"{bad}:docs/notes.md").strip()
        env = self.stand_in(blob, self.CLEAN_NOTES, base)
        self.assertStandsIn(bad, "docs/notes.md", self.CLEAN_NOTES, env)
        return bad, blob, env


class Accepts(Clone):
    def test_good_commit_dry_run_then_push_from_a_dirty_tree(self):
        first, rest = self.text("heath/I/01.md").split("\n", 1)
        heath = first + "\n<!-- Checked against the page image, scan leaf n261. -->\n" + rest
        sha = self.commit("A good commit", {
            "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n",
            "heath/I/01.md": heath,
        })
        # Nothing is read from the working tree: a change there, and an untracked file
        # holding a secret, are neither checked nor pushed.
        (WORK / "README.md").write_text(self.text("README.md") + "\nUncommitted.\n")
        (WORK / "notes.txt").write_text(f"api_token = '{TOKEN}'\n")
        tags = git(ORIGIN, "tag", "--list")

        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("dry run", out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertIsNone(self.origin_branch())
        for name in ("commit", "fast-forward", "harness", "secrets", "statements", "axiom lock",
                     "protected paths", "heath/", "directories", "review records"):
            self.assertEqual(self.guard(out, name), "ok", f"{name}:\n{out}")
        self.assertIn("leaf n261", out)

        r = self.safe_push()                       # HEAD, by default, to the branch
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.origin_main(), BASE, "the pre-flight pushed to main")
        self.assertEqual(self.origin_branch(), sha)
        for name in ("git push", "tags", "pull request", "CI"):
            self.assertEqual(self.guard(out, name), "ok", f"{name}:\n{out}")
        self.assertEqual(git(ORIGIN, "tag", "--list"), tags, "a tag was made")
        self.assertNotIn("Uncommitted", git(ORIGIN, "show", f"{sha}:README.md"))
        self.assertEqual(len(git(WORK, "worktree", "list").splitlines()), 1,
                         "a temporary worktree was left behind")
        log = LOG.read_text()
        self.assertIn(f"dry run {sha[:12]}", log)
        self.assertIn(f"push {sha[:12]}", log)
        # The pull request: onto main, from the branch, with the template's body.
        (pr,) = self.gh_state()["prs"]
        self.assertEqual((pr["headRefName"], pr["baseRefName"], pr["title"]),
                         (BRANCH, "main", "A good commit"))
        body = pr["body"]
        self.assertIn(f"<!-- safe_push:preflight begin sha={sha} base={BASE} harness={BASE} -->",
                      body)
        self.assertIn("## Checklist", body)
        self.assertIn("- [ ] **Required:**", body)
        self.assertIn(f"`{short_sha(sha)}` A good commit", body)
        self.assertIn("| 3. statements | ok |", body)
        self.assertNotIn("<!-- safe_push: commits -->", body)
        self.assertNotIn(str(Path.home()), body, "a private path in the public body")

    def test_nothing_to_push(self):
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Nothing to push", r.stdout)


class Preconditions(Clone):
    def test_unknown_commit(self):
        self.assertRefused(self.safe_push("--commit", "0123456789abcdef0123456789abcdef01234567"),
                           "is not a commit")

    def test_not_a_fast_forward(self):
        side = self.commit("Someone else's commit", {
            "docs/reading.md": self.text("docs/reading.md") + "\nTheirs.\n"})
        git(WORK, "push", "--quiet", "origin", f"{side}:refs/heads/side")   # not main
        git(ORIGIN, "update-ref", "refs/heads/main", side)
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        mine = self.commit("Mine", {"docs/reading.md": self.text("docs/reading.md") + "\nMine.\n"})
        r = self.safe_push("--commit", mine)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("not a fast-forward", out)
        self.assertEqual(self.guard(out, "fast-forward"), "FAIL", out)
        self.assertEqual(self.origin_main(), side)

    def test_internal_flag_needs_a_local_origin(self):
        url = git(WORK, "remote", "get-url", "origin").strip()
        git(WORK, "remote", "set-url", "origin", "https://github.com/example/none.git")
        try:
            self.assertRefused(self.safe_push(), "only against a local origin")
        finally:
            git(WORK, "remote", "set-url", "origin", url)


class Secrets(Clone):
    def test_secrets_refused(self):
        self.commit("Plant secrets", {
            "docs/notes.md": f"Some notes.\napi_token = \"{TOKEN}\"\nsee {PRIVATE_DIR}\n",
            "deploy/.env": "PLAIN=1\n",
            "deploy/server.pem": "not really a certificate\n",
            "deploy/id": f"{KEY_HEADER}\nMIIEow\n",
        })
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertEqual(self.guard(out, "secrets"), "FAIL", out)
        for rule in ("key, token or secret", "private path", ".env file", "key file",
                     "private key"):
            self.assertIn(rule, out)
        self.assertNotIn(TOKEN, out, "the report repeats the secret")

    def test_secret_in_a_commit_message_refused(self):
        self.commit(f"Notes from {PRIVATE_DIR}", {
            "docs/reading.md": self.text("docs/reading.md") + "\nA line.\n"})
        self.assertRefused(self.safe_push(), "message", "private path")

    def test_secret_behind_a_replacement_refused(self):
        # Issue #256: the token's blob replaced by a clean one, by `git replace` and then by
        # a folder GIT_REPLACE_REF_BASE names; the push would send the token, so the
        # pre-flight's scan reads it, and step 2 refuses. Each subtest starts as setUp starts
        # a test, so that one whose push went through cannot fail the next at its branch.
        for base in self.REPLACE_REFS:
            with self.subTest(base=base):
                self.setUp()
                _, blob, env = self.hidden_token(base)
                try:
                    if base != "refs/replace/":
                        self.assertEqual(git(WORK, "for-each-ref", "refs/replace/"), "")
                    out = self.assertRefused(self.safe_push(env=dict(clean_env(), **env)),
                                             "REFUSED: the secret scan found 1 possible secret")
                    self.assertEqual(self.guard(out, "secrets"), "FAIL", out)
                    self.assertIn("docs/notes.md", out)
                    self.assertNotIn(TOKEN, out, "the report repeats the secret")
                finally:
                    git(WORK, "update-ref", "-d", base + blob)
        # A commit whose message holds a token (in its body: step 1 reads the subject),
        # replaced by one with the same subject, tree and parent and no body: the push
        # would send the token's message, so step 2 refuses it.
        with self.subTest(replaced="a commit"):
            self.setUp()
            bad = self.commit(f"Notes\n\napi_token = \"{TOKEN}\"", {
                "docs/reading.md": self.text("docs/reading.md") + "\nA line.\n"})
            clean = git(WORK, "commit-tree", f"{bad}^{{tree}}", "-p", BASE, "-m",
                        "Notes").strip()
            self.replace_object(bad, clean)
            try:
                self.assertEqual(git(WORK, "log", "-1", "--format=%B", bad,
                                     env=clean_env()).strip(), "Notes")
                out = self.assertRefused(self.safe_push(), "message", "key, token or secret")
                self.assertNotIn(TOKEN, out, "the report repeats the secret")
            finally:
                git(WORK, "update-ref", "-d", f"refs/replace/{bad}")
        # origin/main's allow-list replaced by one with an entry that allows the token by
        # its SHA-256: the scan reads origin/main's own, which allows nothing, and refuses.
        with self.subTest(replaced="origin/main's allow-list"):
            self.setUp()
            path = safe_push.ALLOWLIST
            theirs = git(WORK, "rev-parse", f"refs/remotes/origin/main:{path}").strip()
            allowing = self.text(path) + "\n" + self.ALLOW
            self.stand_in(theirs, allowing)
            try:
                self.assertStandsIn("refs/remotes/origin/main", path, allowing, {})
                self.commit("A flagged line", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
                out = self.assertRefused(self.safe_push(),
                                         "REFUSED: the secret scan found 1 possible secret")
                self.assertNotIn("A fixture for the test", out)
            finally:
                git(WORK, "update-ref", "-d", f"refs/replace/{theirs}")

    def test_secret_behind_a_replacement_turned_on_in_config_refused(self):
        # The same with core.useReplaceRefs=true in the clone's config, which git from 2.19
        # to 2.41 let override GIT_NO_REPLACE_OBJECTS: run() sets it false on git's command
        # line, which git reads last (Hook has the hook's twin of this test).
        self.replace_refs_on_in_config()
        self.hidden_token()
        out = self.assertRefused(self.safe_push(),
                                 "REFUSED: the secret scan found 1 possible secret")
        self.assertNotIn(TOKEN, out, "the report repeats the secret")

    # The value is pinned by its SHA-256: written here, it would be flagged in turn.
    ALLOW = ('[[allow]]\npath = "docs/notes.md"\nmatch = "api_token"\n'
             'rule = "key, token or secret"\n'
             f'sha256 = "{hashlib.sha256(TOKEN.encode()).hexdigest()}"\n'
             'reason = "A fixture for the test, not a real token."\n')

    def test_allow_list_with_a_reason(self):
        # origin/main's allow-list counts: the entry lands in a pull request of its own.
        self.new_base("Allow a fixture", {"scripts/safe_push_allow.toml": self.ALLOW})
        self.commit("A flagged line, allowed", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "secrets"), "ok", out)
        self.assertIn("A fixture for the test", out)

    def test_allow_list_without_a_reason_refused(self):
        allow = self.ALLOW.replace('reason = "A fixture for the test, not a real token."\n', "")
        main = self.new_base("Allow a fixture, with no reason",
                             {"scripts/safe_push_allow.toml": allow})
        self.commit("A flagged line", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("has no reason", out)
        self.assertEqual(self.origin_main(), main)
        self.assertIsNone(self.origin_branch())


SIGNATURE_OLD = "theorem Prop1 (A B : Point) (hAB : A ≠ B) (P : Point) :"
SIGNATURE_NEW = "theorem Prop1 (A B : Point) (hAB : A ≠ B) (Q : Point) :"


class Statements(Clone):
    def test_lean_statement_changed_without_a_decision_refused(self):
        self.commit("Change I.1's statement", {"Elements/BookI/Prop01.lean": self.replaced(
            "Elements/BookI/Prop01.lean", SIGNATURE_OLD, SIGNATURE_NEW)})
        out = self.assertRefused(self.safe_push(), "I.1: the Lean statement changed")
        self.assertEqual(self.guard(out, "statements"), "FAIL", out)

    def test_facts_statement_changed_without_a_decision_refused(self):
        facts = json.loads(self.text("facts.json"))
        old = next(p["statement"] for p in facts["propositions"] if p["ref"] == "III.1 Por.")
        new = old.replace("Elements.Collinear D C G", "Elements.Collinear D G C")
        self.assertNotEqual(old, new)
        text = self.replaced("facts.json", json.dumps(old, ensure_ascii=False),
                             json.dumps(new, ensure_ascii=False))
        self.commit("Change III.1 Por.'s statement", {"facts.json": text})
        out = self.assertRefused(self.safe_push(), "III.1 Por.: facts.json's statement changed")
        self.assertEqual(self.guard(out, "statements"), "FAIL", out)

    def test_statement_changed_with_a_decision_passes_the_guard(self):
        changes = {"Elements/BookI/Prop01.lean": self.replaced(
            "Elements/BookI/Prop01.lean", SIGNATURE_OLD, SIGNATURE_NEW)}
        changes.update(self.decision("I.1 names its side point Q."))
        self.commit("Change I.1's statement, with a decision", changes)
        out = self.assertRefused(self.safe_push())
        self.assertEqual(self.guard(out, "statements"), "ok", out)
        self.assertIn("named in the docs/briefs/ lines added", out)
        # The Lean file changed, so I.1's review record is stale, and that is refused too.
        self.assertEqual(self.guard(out, "review records"), "FAIL", out)
        self.assertIn("I.1", out)


class Lock(Clone):
    LOCK = "Certificate/axioms.lock"

    def weakened(self) -> dict:
        line = '"Postulate1" = "∀ (A B : Elements.Point), Ne A B → Exists'
        return {self.LOCK: self.replaced(self.LOCK, line, line.replace("Ne A B → ", ""))}

    def test_lock_changed_without_a_decision_refused(self):
        self.commit("Weaken Postulate 1 in the lock", self.weakened())
        out = self.assertRefused(self.safe_push(), "axioms.lock changed")
        self.assertEqual(self.guard(out, "axiom lock"), "FAIL", out)

    def test_lock_changed_with_a_decision_passes_the_guard(self):
        changes = self.weakened()
        changes.update(self.decision("The axiom lock gains a weaker Postulate 1."))
        self.commit("Weaken Postulate 1 in the lock, with a decision", changes)
        out = self.assertRefused(self.safe_push())
        self.assertEqual(self.guard(out, "axiom lock"), "ok", out)


class Heath(Clone):
    WORD = ("equilateral triangle.*", "equilateral triangle*.")   # I.1's enunciation

    def test_heath_changed_without_a_leaf_refused(self):
        self.commit("Edit a Heath word", {"heath/I/01.md": self.replaced("heath/I/01.md",
                                                                         *self.WORD)})
        out = self.assertRefused(self.safe_push(), "heath/I/01.md")
        self.assertEqual(self.guard(out, "heath/"), "FAIL", out)

    def test_heath_changed_naming_another_pages_leaf_refused(self):
        text = self.replaced("heath/I/01.md", *self.WORD)
        text = text.replace("# Proposition 1", "<!-- Checked, scan leaf n999. -->\n# Proposition 1")
        self.commit("Edit a Heath word, naming a leaf of another page", {"heath/I/01.md": text})
        out = self.assertRefused(self.safe_push(), "not one of its own pages' leaves")
        self.assertEqual(self.guard(out, "heath/"), "FAIL", out)

    def test_heath_changed_naming_its_leaf_passes_the_guard(self):
        text = self.replaced("heath/I/01.md", *self.WORD)
        text = text.replace("# Proposition 1", "<!-- Checked, scan leaf n261. -->\n# Proposition 1")
        self.commit("Edit a Heath word, naming its leaf", {"heath/I/01.md": text})
        out = self.safe_push("--dry-run")
        self.assertEqual(self.guard(out.stdout, "heath/"), "ok", out.stdout)

    def test_heath_file_deleted_refused(self):
        self.commit("Delete a Heath file", remove=["heath/I/48.md"])
        self.assertRefused(self.safe_push(), "heath/I/48.md: deleted")

    def test_source_comment_widened_by_the_change_refused(self):
        # Finding 3: the leaves allowed are origin/main's; a change that adds n999 to the
        # file's own source comment, and then names n999, is refused.
        text = self.replaced("heath/I/01.md", *self.WORD)
        text = text.replace("scan leaves n261–n262;", "scan leaves n261–n262, n999;")
        text = text.replace("# Proposition 1", "<!-- Checked, scan leaf n999. -->\n# Proposition 1")
        self.commit("Edit a Heath word, widening the source comment", {"heath/I/01.md": text})
        out = self.assertRefused(self.safe_push(), "not one of its own pages' leaves",
                                 "origin/main's copy")
        self.assertEqual(self.guard(out, "heath/"), "FAIL", out)

    def test_source_comment_recased_does_not_name_a_leaf(self):
        # Review note 10: the source comment is the file's first, known by its place; with
        # "Source:" written "source:", it still lists the leaves and checks none.
        text = self.replaced("heath/I/01.md", *self.WORD).replace("<!-- Source:", "<!-- source:")
        self.commit("Edit a Heath word, and recase the source comment", {"heath/I/01.md": text})
        out = self.assertRefused(self.safe_push(), "no comment in the change naming the scan leaf")
        self.assertEqual(self.guard(out, "heath/"), "FAIL", out)


class Directories(Clone):
    def test_directory_deleted_without_a_decision_refused(self):
        self.commit("Delete a directory", remove=["mishnah/intro"])
        out = self.assertRefused(self.safe_push(), "mishnah/intro/")
        self.assertEqual(self.guard(out, "directories"), "FAIL", out)

    def test_directory_deleted_with_a_decision_passes_the_guard(self):
        self.commit("Delete a directory, with a decision",
                    self.decision("The introductions in `mishnah/intro/` move."),
                    remove=["mishnah/intro"])
        r = self.safe_push("--dry-run")
        self.assertEqual(self.guard(r.stdout, "directories"), "ok", r.stdout)


class Hook(Clone):
    def push(self, refspec, **env) -> subprocess.CompletedProcess:
        e = clean_env()
        e.update(env)
        return subprocess.run(["git", "push", "origin", refspec], cwd=WORK, env=e,
                              capture_output=True, text=True)

    def test_hook_refuses_pushes_to_main_that_safe_push_did_not_check(self):
        # Every push to main is refused now, the commit checked or not: main changes only
        # by a pull request's merge commit.
        sha = self.commit("A commit", {"docs/reading.md": self.text("docs/reading.md") + "\nX.\n"})
        r = self.push(f"{sha}:refs/heads/main")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("git safe-push --branch <name> --label <kind>", r.stderr)
        r = self.push(f"{sha}:refs/heads/main", STOICHEIA_SAFE_PUSH=sha)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refusing a push to main", r.stderr)
        r = self.push(":refs/heads/main", STOICHEIA_SAFE_PUSH=sha)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refusing to delete main", r.stderr)
        self.assertEqual(self.origin_main(), BASE)
        r = self.push(f"{sha}:refs/heads/a-branch")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("the secret scan of the push to refs/heads/a-branch", r.stdout + r.stderr)

    def test_hook_scans_a_push_to_any_branch(self):
        # Finding 2: the same secret scan on every branch, not just main.
        bad = self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        for ref in ("refs/heads/feature", "refs/heads/someone/else"):
            with self.subTest(ref=ref):
                r = self.push(f"{bad}:{ref}")
                self.assertNotEqual(r.returncode, 0, r.stderr)
                self.assertIn(f"pre-push: refusing the push to {ref}", r.stderr)
                self.assertIsNone(self.origin_branch(ref.removeprefix("refs/heads/")))
        self.assertNotIn(TOKEN, r.stdout + r.stderr, "the hook repeats the secret")

    def test_hook_never_runs_another_remotes_main(self):
        # Security review: a push to another remote (a contributor's fork, fetched) is
        # scanned with origin/main's copy, never with the copy on that remote's main.
        other = TMP / "other.git"
        git(TMP, "clone", "--quiet", "--bare", str(ORIGIN), str(other))
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        marker = TMP / "other-ran"
        payload = self.replaced("scripts/safe_push.py", "def scan_push_main(",
                                "def scan_push_main(*a):\n"
                                f"    open({str(marker)!r}, 'w').close()\n"
                                "    return 0\n\n\ndef _unused(")
        theirs = self.commit("A fork's main, with its own scan", {"scripts/safe_push.py": payload})
        git(WORK, "push", "--quiet", "--no-verify", str(other), f"{theirs}:refs/heads/main")
        git(WORK, "remote", "add", "other", str(other))
        self.addCleanup(git, WORK, "remote", "remove", "other", check=False)
        git(WORK, "fetch", "--quiet", "other")
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        bad = self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = subprocess.run(["git", "push", "other", f"{bad}:refs/heads/feature"], cwd=WORK,
                           env=clean_env(), capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pre-push: refusing the push to refs/heads/feature", r.stderr)
        self.assertFalse(marker.exists(), "the hook ran the other remote's safe_push.py")

    def test_hook_refuses_without_origin_mains_scan(self):
        # No fallback to the working tree's copy: without origin/main's scan, no push.
        text = self.text("scripts/safe_push.py").replace("--scan-push", "--scan-gone")
        self.new_base("A main whose harness has no --scan-push", {"scripts/safe_push.py": text})
        sha = self.commit("A good commit", {
            "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"})
        r = self.push(f"{sha}:refs/heads/a-branch")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("origin/main has no scripts/safe_push.py with", r.stderr)
        self.assertIsNone(self.origin_branch("a-branch"))

    def test_hook_scans_the_ref_name(self):
        # A branch's name is published with it: one the scan flags is refused, its commits
        # clean or not.
        sha = self.commit("A commit", {"docs/reading.md": self.text("docs/reading.md") + "\nX.\n"})
        name = "secret" + "s2026-notes"
        r = self.push(f"{sha}:refs/heads/{name}")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("its name holds what the secret scan refuses", r.stderr)
        self.assertIsNone(self.origin_branch(name))

    def test_hook_scans_with_origin_mains_copy(self):
        # A branch that empties its own copy of the scan is still scanned by origin/main's.
        lame = self.replaced("scripts/safe_push.py", "def scan_push_main(",
                             "def scan_push_main(*a):\n    return 0\n\n\ndef _unused(")
        bad = self.commit("Disable the scan, and plant a token", {
            "scripts/safe_push.py": lame, "docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = self.push(f"{bad}:refs/heads/feature")
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("pre-push: refusing the push to refs/heads/feature", r.stderr)

    def refused_behind_a_replacement(self, base: str) -> None:
        bad, _, env = self.hidden_token(base)
        r = self.push(f"{bad}:refs/heads/feature", **env)
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pre-push: refusing the push to refs/heads/feature: the secret scan "
                      "found 1 possible secret", r.stderr)
        self.assertIsNone(self.origin_branch("feature"))
        self.assertNotIn(TOKEN, r.stdout + r.stderr, "the hook repeats the secret")

    def test_hook_reads_past_a_replacement(self):
        # Issue #256: the token's blob replaced by a clean one with `git replace`. git shows
        # the stand-in, but the push sends the token; the hook's scan reads the token.
        self.refused_behind_a_replacement("refs/replace/")

    def test_hook_reads_past_a_replace_ref_base(self):
        # The same, the stand-in in a folder of refs that GIT_REPLACE_REF_BASE names in the
        # push's environment, with nothing in refs/replace/.
        self.refused_behind_a_replacement("refs/stand-ins/")
        self.assertEqual(git(WORK, "for-each-ref", "refs/replace/"), "")

    def test_hook_reads_past_a_replacement_turned_on_in_config(self):
        # The first, with core.useReplaceRefs=true in the clone's config, which git from
        # 2.19 to 2.41 let override GIT_NO_REPLACE_OBJECTS: the hook's git calls and the
        # scan's set it false on git's command line, which git reads last.
        self.replace_refs_on_in_config()
        self.refused_behind_a_replacement("refs/replace/")

    def test_hook_runs_origin_mains_scan_not_its_replacement(self):
        # origin/main's safe_push.py replaced by a copy whose scan passes everything: the
        # hook copies out origin/main's own, which refuses the token.
        lame = self.replaced("scripts/safe_push.py", "def scan_push_main(",
                             "def scan_push_main(*a):\n    return 0\n\n\ndef _unused(")
        theirs = git(WORK, "rev-parse", "refs/remotes/origin/main:scripts/safe_push.py").strip()
        env = self.stand_in(theirs, lame)
        self.assertStandsIn("refs/remotes/origin/main", "scripts/safe_push.py", lame, env)
        bad = self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = self.push(f"{bad}:refs/heads/feature")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pre-push: refusing the push to refs/heads/feature", r.stderr)
        self.assertIsNone(self.origin_branch("feature"))

    def test_hook_passes_a_clean_push_beside_a_replacement(self):
        # A replacement the push has no part in leaves a clean push alone; and one whose
        # stand-in holds a token, for a blob the push sends clean, is not what is read.
        sha = self.commit("A good commit", {
            "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"})
        pushed = git(WORK, "rev-parse", f"{sha}:docs/reading.md").strip()
        unrelated = git(WORK, "rev-parse", f"{BASE}:README.md").strip()
        for name, blob, text in (
                ("clean-beside", unrelated, "A stand-in for the README.\n"),
                ("clean-under", pushed, f"api_token = \"{TOKEN}\"\n")):
            with self.subTest(blob=name):
                env = self.stand_in(blob, text)
                try:
                    r = self.push(f"{sha}:refs/heads/{name}", **env)
                    self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                    self.assertIn(f"the secret scan of the push to refs/heads/{name}",
                                  r.stdout + r.stderr)
                    self.assertEqual(self.origin_branch(name), sha)
                finally:
                    git(WORK, "update-ref", "-d", f"refs/replace/{blob}")


# --------------------------------------------------------------------------------------
# The edge cases: each planted commit is refused (or, for the dry run, behaves as stated).


def hooks_dir() -> Path:
    out = git(WORK, "rev-parse", "--git-path", "hooks").strip()
    return Path(out) if os.path.isabs(out) else WORK / out


def with_text(record: str, value: str) -> str:
    """A review record with `text = "value"` as the first line of its [review] table, so
    within [review] whether or not [review.items] follows it."""
    assert record.count("[review]\n") == 1, "a record with one [review] table"
    return record.replace("[review]\n", f'[review]\ntext = "{value}"\n', 1)


class Edge(Clone):
    def flagged(self, out: str, path: str) -> bool:
        """Does the secret scan's report name a finding in `path`: "path: rule",
        "path:3: rule", "path:2-3: rule", each perhaps with "(in commit <sha>)"?"""
        where = r"^\s+%s(:\d+(-\d+)?)?( \(in commit [0-9a-f]+\))?: " % re.escape(path)
        return re.search(where, out, re.M) is not None

    def assertFlagged(self, out: str, *paths: str):
        self.assertEqual(self.guard(out, "secrets"), "FAIL", out)
        for path in paths:
            self.assertTrue(self.flagged(out, path), f"{path} not flagged:\n{out}")

    def swap_hook(self, script: str) -> None:
        """Put `script` in place of the installed pre-push hook until the test ends."""
        hook = hooks_dir() / "pre-push"
        saved = hook.read_text()
        hook.write_text(script)
        hook.chmod(0o755)
        self.addCleanup(lambda: (hook.write_text(saved), hook.chmod(0o755)))

    def side_commit(self) -> str:
        """Someone else's commit on top of BASE, in origin (on a side branch), not on main."""
        side = self.commit("Someone else's commit", {
            "docs/reading.md": self.text("docs/reading.md") + "\nTheirs.\n"})
        git(WORK, "push", "--quiet", "origin", f"{side}:refs/heads/side")
        self.addCleanup(lambda: git(ORIGIN, "update-ref", "-d", "refs/heads/side", check=False))
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        return side

    def good_commit(self, line: str = "A line for the test.") -> str:
        return self.commit("A good commit", {
            "docs/reading.md": self.text("docs/reading.md") + f"\n{line}\n"})

    def regenerated_commit(self, message: str, changes: dict) -> str:
        """The changes, with the pages render.py regenerates from them, committed."""
        for rel, text in changes.items():
            (WORK / rel).parent.mkdir(parents=True, exist_ok=True)
            (WORK / rel).write_text(text)
            git(WORK, "add", "--", rel)
        r = subprocess.run([sys.executable, "scripts/render.py"], cwd=WORK,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        git(WORK, "add", "-u")
        return self.commit(message)


class BranchChecks(Edge):
    """Step 4 runs small commands in its two worktrees; the guards and gh stand-in run
    as usual. Only preconditions uses test mode, to require a local origin and fake gh."""

    DRIVER = r"""
import sys
sys.path.insert(0, sys.argv[1])
import safe_push
real_preconditions = safe_push.preconditions
def preconditions(repo, commit, branch, dry_run, test_mode, rep, title=None):
    return real_preconditions(repo, commit, branch, dry_run, True, rep, title)
safe_push.preconditions = preconditions
# The fixture's main holds the registry, so step 4's sequence is read from it, as usual,
# and its step line kept; the small command runs in its place.
real_check_list = safe_push.check_list
def check_list(ctx, rep):
    real_check_list(ctx, rep)
    return [("test full checks", [sys.executable, "-c", "print('checked')"])]
safe_push.check_list = check_list
safe_push.NEGATIVE = [("test negative checks", [sys.executable, "-c", "print('checked')"])]
sys.exit(safe_push.main(sys.argv[2:]))
"""

    def good_commit(self, line: str = "A line for the test.") -> str:
        # R3 by scripts/risk.py, a line in the guide to the checks, as FullChecks: an R0 to
        # R2 commit's pre-flight leaves step 4 to CI (RiskPreflight), and these tests pin
        # what a pre-flight that runs step 4 records.
        return self.commit("A good commit", {
            "docs/WORKFLOW.md": self.text("docs/WORKFLOW.md") + f"\n{line}\n"})

    def preflight(self, *args):
        return subprocess.run([sys.executable, "-c", self.DRIVER, str(UNDER_TEST),
                               *with_branch(args)], cwd=WORK, env=clean_env(),
                              capture_output=True, text=True)

    def checked(self):
        sha = self.good_commit()
        r = self.preflight("--dry-run")
        self.assertRanChecks(r)
        self.assertIsNone(self.origin_branch())
        self.assertEqual(self.gh_state()["calls"], [])
        path = LOG.parent / "preflight" / f"{sha}-{BASE}.json"
        record = json.loads(path.read_text())
        self.assertIs(record["full"], True)
        self.assertEqual(record["harness_blob"],
                         git(WORK, "rev-parse", f"{BASE}:scripts/safe_push.py").strip())
        return sha, path, record

    def assertRanChecks(self, r):
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        for name in ("test full checks", "test negative checks"):
            self.assertEqual(self.step(out, name), "ok", out)
        self.assertIsNone(self.step(out, "full local checks"), out)
        return out

    def test_dry_run_then_push_runs_full_checks_again(self):
        sha, path, record = self.checked()
        out = self.assertRanChecks(self.preflight())
        for name in ("commit", "fetch", "fast-forward", "harness", "secrets", "statements",
                     "axiom lock", "protected paths", "heath/", "directories",
                     "review records", "generated pages"):
            self.assertEqual(self.guard(out, name), "ok", f"{name}:\n{out}")
        self.assertEqual(self.origin_branch(), sha)
        self.assertEqual(self.origin_main(), BASE)
        saved = json.loads(path.read_text())
        self.assertIs(saved["full"], True)
        self.assertRanChecks(self.preflight())
        self.assertNotIn("full local checks: skip", self.gh_state()["prs"][0]["body"])

    def test_forged_record_does_not_supply_full_checks(self):
        sha, path, record = self.checked()
        record["steps"] = [["4", "invented check", "ok", 0.0]]
        record["time"] = "invented time"
        path.write_text(json.dumps(record))
        self.assertRanChecks(self.preflight())
        self.assertEqual(self.origin_branch(), sha)
        self.assertNotIn("invented check", self.gh_state()["prs"][0]["body"])

    def test_dry_run_always_runs_the_checks(self):
        self.checked()
        self.assertRanChecks(self.preflight("--dry-run"))
        self.assertIsNone(self.origin_branch())
        self.assertEqual(self.gh_state()["calls"], [])


class SplitSecrets(Edge):
    """(1) A credential-like value split over two added lines."""

    def test_value_split_over_two_lines_refused(self):
        half = len(TOKEN) // 2
        self.commit("A token split over lines", {
            # the key word on one line, its value on the next
            "docs/notes.md": f"Some notes.\napi_token =\n    \"{TOKEN}\"\n",
            # a string continued in parentheses
            "scripts/settings.py": f'API_TOKEN = (\n    "{TOKEN[:half]}"\n    "{TOKEN[half:]}"\n)\n',
            # a value broken at the wrap, neither part long enough alone
            "docs/wrapped.txt": f"token: {HEXKEY[:18]}\n       {HEXKEY[18:]}\n",
            # a shell string continued with a backslash
            "docs/continued.sh": f'export GITHUB_TOKEN="{HEXKEY[:12]}\\\n{HEXKEY[12:]}"\n',
        })
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/notes.md", "scripts/settings.py", "docs/wrapped.txt",
                           "docs/continued.sh")
        self.assertNotIn(TOKEN, out, "the report repeats the secret")
        self.assertNotIn(TOKEN[half:], out, "the report repeats half of the secret")


class EncodedSecrets(Edge):
    """(2) A credential-like value base64-encoded in a text file."""

    def test_base64_encoded_credentials_refused(self):
        def b64(s: str) -> str:
            return base64.b64encode(s.encode()).decode()
        assignment = f'api_token = "{TOKEN}"'
        # base64 lines of 76 columns hold 57 bytes: the token starts on the first line, with
        # too little of it there for the token rule, and ends on the second.
        prefix = "A note, padded so that the wrap cuts the token: "
        self.assertTrue(23 < len(prefix) < 57 < len(prefix) + len(GH_TOKEN))
        wrapped = base64.encodebytes((prefix + GH_TOKEN + " and more after it.\n").encode())
        self.commit("Encoded credentials", {
            "docs/blob.txt": f"config: {b64(assignment)}\n",
            "docs/key.txt": b64(f"{KEY_HEADER}\nMIIEowIBAAKCAQEA\n") + "\n",
            "docs/value.txt": f"value = {b64(GH_TOKEN)}\n",
            "docs/wrapped.txt": wrapped.decode(),          # 76 columns, cut mid-token
        })
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/blob.txt", "docs/key.txt", "docs/value.txt",
                           "docs/wrapped.txt")
        self.assertIn("base64", out)
        self.assertNotIn(b64(assignment), out, "the report repeats the encoded secret")


class RenamedSecrets(Edge):
    """(3) A credential file under a renamed path; a file renamed to a key file's name."""

    def test_credential_file_added_then_renamed_refused(self):
        self.commit("Add a key file", {"deploy/server.key": "not really a key\n"})
        git(WORK, "mv", "deploy/server.key", "deploy/server.txt")
        git(WORK, "commit", "-q", "-m", "Rename it to something plain")
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "deploy/server.key")
        self.assertIn("key file", out)

    def test_existing_files_renamed_to_key_names_refused(self):
        renames = {"docs/examples.md": "docs/examples.pem", "docs/reading.md": "docs/reading.key",
                   "docs/references.bib": "docs/.env"}
        for old, new in renames.items():
            git(WORK, "mv", old, new)
        git(WORK, "commit", "-q", "-m", "Rename three files")
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, *renames.values())

    def test_secret_added_and_removed_within_the_push_refused(self):
        # The push carries every commit, so a secret in the history is published even
        # when a later commit of the same push takes it out again.
        self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n",
                                      "deploy/.env": "PLAIN=1\n"})
        self.commit("Take it out again", remove=["docs/notes.md", "deploy/.env"])
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/notes.md", "deploy/.env")
        self.assertIn("in commit", out)


class Symlinks(Edge):
    """(4) A symlink added that points into a private directory, or out of the repository."""

    def link(self, links: dict) -> None:
        for path, target in links.items():
            os.symlink(target, WORK / path)
            git(WORK, "add", "--", path)

    def test_symlink_into_a_private_directory_refused(self):
        links = {"docs/inbox": TILDE_DOWNLOADS, "docs/scans": PRIVATE_SCANS,
                 "docs/notes": PRIVATE_DIR, "docs/elsewhere": "../../../elsewhere/notes.txt",
                 "docs/etc": "/etc/hosts"}
        self.link(links)
        git(WORK, "commit", "-q", "-m", "Links out of the repository")
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, *links)

    def test_symlink_within_the_repository_passes_the_scan(self):
        self.link({"docs/readme": "../README.md"})
        git(WORK, "commit", "-q", "-m", "A link within the repository")
        r = self.safe_push("--dry-run")
        self.assertEqual(self.guard(r.stdout, "secrets"), "ok", r.stdout + r.stderr)


SIGNATURE_WRAPPED = "theorem Prop1 (A B : Point)\n    (hAB : A ≠ B)\n    (P : Point) :"


class DisguisedStatements(Edge):
    """(5) A statement change made to look like whitespace; a decision naming another
    proposition."""

    LEAN = "Elements/BookI/Prop01.lean"

    def changed(self, new: str) -> dict:
        return {self.LEAN: self.replaced(self.LEAN, SIGNATURE_OLD, new)}

    def assertStatementRefused(self, ref="I.1"):
        out = self.assertRefused(self.safe_push(), f"{ref}: the Lean statement changed")
        self.assertEqual(self.guard(out, "statements"), "FAIL", out)
        return out

    def test_rewrap_alone_passes_the_statement_guard(self):
        self.commit("Re-wrap I.1's statement", self.changed(SIGNATURE_WRAPPED))
        r = self.safe_push("--dry-run")
        self.assertEqual(self.guard(r.stdout, "statements"), "ok", r.stdout)

    def test_hypothesis_changed_on_a_rewrapped_line_refused(self):
        self.commit("Re-wrap I.1's statement", self.changed(
            SIGNATURE_WRAPPED.replace("A ≠ B", "B ≠ A")))
        self.assertStatementRefused()

    def test_binder_changed_on_a_rewrapped_line_refused(self):
        self.commit("Re-wrap I.1's statement", self.changed(
            SIGNATURE_WRAPPED.replace("(P : Point)", "{P : Point}")))
        self.assertStatementRefused()

    def test_decision_naming_a_different_proposition_refused(self):
        changes = self.changed(SIGNATURE_NEW)
        changes.update(self.decision(
            "I.10, II.1 and III.1 keep their statements; `BookI.Prop10` and\n  I. 11 change."))
        self.commit("Change I.1's statement, with a decision about others", changes)
        self.assertStatementRefused()

    def test_old_brief_line_edited_does_not_approve_a_change(self):
        # A line of a brief that already named I.1, edited in place, is not a decision
        # about I.1's new statement.
        changes = self.changed(SIGNATURE_NEW)
        brief = "docs/briefs/0003-book-II.md"
        changes[brief] = self.replaced(brief, "System E's rules, as I.1 does);",
                                       "System E's rules, just as I.1 does);")
        self.commit("Change I.1's statement, touching an old line naming it", changes)
        self.assertStatementRefused()

    def test_change_after_an_inner_assignment_compared(self):
        # The statement runs to its own `:=`, not to the first one in a binder or comment.
        src = ("/-- A test statement. -/\n"
               "theorem Prop7 (A B : Point) (h : A ≠ B := by decide) -- a := b\n"
               "    (P : Point) :\n    A = B := by\n  sorry\n")
        statement = safe_push.source_statement(src, 7, None)
        for old, new in (("A = B := by", "B = A := by"), ("(P : Point)", "{P : Point}")):
            other = safe_push.source_statement(src.replace(old, new), 7, None)
            self.assertNotEqual(statement, other, f"{old} -> {new} not seen")
        self.assertTrue(statement.endswith("A = B"), statement)


class LockDecisions(Edge):
    """(6) An axioms.lock change with a decisions entry that does not mention the lock."""

    LOCK = "Certificate/axioms.lock"
    DECISIONS = DECISIONS

    def weakened(self) -> dict:
        line = '"Postulate1" = "∀ (A B : Elements.Point), Ne A B → Exists'
        return {self.LOCK: self.replaced(self.LOCK, line, line.replace("Ne A B → ", ""))}

    def assertLockRefused(self):
        out = self.assertRefused(self.safe_push(), "axioms.lock changed")
        self.assertEqual(self.guard(out, "axiom lock"), "FAIL", out)

    def test_decision_not_mentioning_the_lock_refused(self):
        changes = self.weakened()
        changes.update(self.decision("Postulate 1 no longer asks for two distinct points."))
        self.commit("Weaken Postulate 1, with a decision silent on the lock", changes)
        self.assertLockRefused()

    def test_lock_mentioned_outside_the_decisions_page_refused(self):
        changes = self.weakened()
        brief = "docs/briefs/book-I.md"
        changes[brief] = self.text(brief) + "\nThe axiom lock changes (axioms.lock).\n"
        self.commit("Weaken Postulate 1 in axioms.lock (the axiom lock)", changes)
        self.assertLockRefused()

    def test_old_decisions_line_mentioning_the_lock_edited_refused(self):
        changes = self.weakened()
        changes[self.DECISIONS] = self.replaced(
            self.DECISIONS, "(../../Certificate/axioms.lock) holds the",
            "(../../Certificate/axioms.lock) keeps the")
        self.commit("Weaken Postulate 1, touching an old line on the lock", changes)
        self.assertLockRefused()


class GeneratedPages(Edge):
    """(7) A commit whose generated pages are stale: render.py would change them."""

    READING = "reading/I/01.md"

    def test_stale_generated_pages_refused(self):
        self.commit("Further reading, pages not regenerated", {
            self.READING: self.text(self.READING) + "- A line of further reading for the test.\n"})
        out = self.assertRefused(self.safe_push(), "book/I/01.md")
        self.assertEqual(self.guard(out, "generated pages"), "FAIL", out)

    def test_generated_page_edited_by_hand_refused(self):
        page = "book/I/01.md"
        self.commit("Edit a generated page by hand", {page: self.text(page) + "\nBy hand.\n"})
        out = self.assertRefused(self.safe_push(), page)
        self.assertEqual(self.guard(out, "generated pages"), "FAIL", out)

    def test_regenerated_pages_pass(self):
        (WORK / self.READING).write_text(self.text(self.READING)
                                         + "- A line of further reading for the test.\n")
        r = subprocess.run([sys.executable, "scripts/render.py"], cwd=WORK,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        git(WORK, "add", "-u")
        git(WORK, "commit", "-q", "-m", "Further reading, pages regenerated")
        r = self.safe_push("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "generated pages"), "ok", r.stdout)


# Runs safe_push in a subprocess with `guards`, `gates` or `watch_checks` wrapped, so that
# something happens at a chosen moment: origin's main moves, or an interruption.
DRIVER = r"""
import json, os, re, subprocess, sys
sys.path.insert(0, sys.argv[1])
import safe_push
action, origin, target = sys.argv[2], sys.argv[3], sys.argv[4]
class Clock:
    # STOICHEIA_TEST_CLOCK: a stand-in for safe_push's clock, time.time and time.sleep, by
    # which it times its steps and its waits (datetime, which only stamps the log and the
    # pre-flight's record, stays).
    # It never reads the wall clock and never waits. "still": time stands, but for the
    # sleeps; "leap": each reading is an hour after the last, past every deadline safe_push
    # keeps within a few readings (the queue's, of five hours, within five), as on a
    # machine so loaded that each step takes an hour.
    def __init__(self, leap):
        self.now, self.leap = 1e9, leap
    def time(self):
        self.now += self.leap
        return self.now
    def sleep(self, seconds):
        self.now += seconds
if os.environ.get("STOICHEIA_TEST_CLOCK"):
    safe_push.time = Clock({"still": 0.0, "leap": 3600.0}[os.environ["STOICHEIA_TEST_CLOCK"]])
real_guards, real_watch = safe_push.guards, safe_push.watch_checks
real_gates, real_refreshed = safe_push.gates, safe_push.refreshed
def gates(ctx, number, rep, record=None):
    result = real_gates(ctx, number, rep, record)
    if action == "move-at-merge" and record is not None:
        subprocess.run(["git", "update-ref", "refs/heads/main", target], cwd=origin, check=True)
    return result
def guards(*args, **kwargs):
    result = real_guards(*args, **kwargs)
    if action == "move":
        subprocess.run(["git", "update-ref", "refs/heads/main", target], cwd=origin, check=True)
    elif action == "interrupt":
        raise KeyboardInterrupt("a test interruption")
    elif action == "edit-train-body":
        # The pull request's body edited on GitHub while the train check runs.
        path = os.environ["STOICHEIA_FAKE_GH_STATE"]
        with open(path) as f:
            state = json.load(f)
        state["prs"][0]["body"] += "\nAn edit made during the checks.\n"
        with open(path, "w") as f:
            json.dump(state, f, indent=1)
    return result
def watch_checks(*args, **kwargs):
    if action == "watch-interrupt":
        raise KeyboardInterrupt("a test interruption")
    if action == "watch-fail":
        raise RuntimeError("gh went away")
    return real_watch(*args, **kwargs)
def refreshed(body, parts):
    result = real_refreshed(body, parts)
    if action == "edit-after-unfinished-comparison":
        path = os.environ["STOICHEIA_FAKE_GH_STATE"]
        with open(path) as f:
            state = json.load(f)
        current = state["prs"][0]["body"]
        state["prs"][0]["body"] = re.sub(
            r"(## Unfinished work\n).*?(?=\n## )",
            lambda m: m.group(1) + "\n- Prototype #38\n", current, count=1, flags=re.S)
        with open(path, "w") as f:
            json.dump(state, f, indent=1)
        return result.replace("<!-- safe_push:commits end -->",
                              "\n<!-- safe_push:commits end -->", 1)
    return result
real_gh_json, real_gh_run = safe_push.gh_json, safe_push.gh_run
def gh_json(ctx, *args):
    # The look at GitHub after `gh pr merge`, interrupted or failing.
    if "state,mergeCommit" in args and action == "merge-view-interrupt":
        raise KeyboardInterrupt("a test interruption")
    if "state,mergeCommit" in args and action == "merge-view-fail":
        raise safe_push.Refusal("`gh pr view` failed: a test failure")
    if "state,mergeCommit" in args and action == "merge-view-empty":
        return {}
    # "merge-view-json:<JSON>": GitHub's answer, as odd as a test needs it.
    if "state,mergeCommit" in args and action.startswith("merge-view-json:"):
        return json.loads(action.split(":", 1)[1])
    return real_gh_json(ctx, *args)
def gh_run(ctx, *args):
    r = real_gh_run(ctx, *args)
    if action == "merge-interrupt" and args[:2] == ("pr", "merge"):
        raise KeyboardInterrupt("a test interruption")
    return r
safe_push.guards = guards
safe_push.gates = gates
safe_push.watch_checks = watch_checks
safe_push.refreshed = refreshed
safe_push.gh_json = gh_json
safe_push.gh_run = gh_run
sys.exit(safe_push.main(sys.argv[5:]))
"""


class Ancestry(Edge):
    """(8) A commit that is not a descendant of origin/main; origin/main moving between
    the check and the push."""

    def drive(self, action: str, target: str, *args, env=None) -> subprocess.CompletedProcess:
        args = with_branch(args)
        return subprocess.run([sys.executable, "-c", DRIVER, str(UNDER_TEST), action, str(ORIGIN),
                               target, "--_test-skip-checks", *args], cwd=WORK,
                              env=env or clean_env(), capture_output=True, text=True)

    def test_commit_behind_origin_main_refused(self):
        newer = self.good_commit()
        git(WORK, "push", "--quiet", "origin", f"{newer}:refs/heads/side")
        self.addCleanup(lambda: git(ORIGIN, "update-ref", "-d", "refs/heads/side", check=False))
        git(ORIGIN, "update-ref", "refs/heads/main", newer)
        r = self.safe_push("--commit", BASE)      # an ancestor of origin/main: a rewind
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("not a fast-forward", out)
        self.assertEqual(self.origin_main(), newer)

    def test_unrelated_history_refused(self):
        def cleanup():
            git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
            git(WORK, "branch", "-q", "-D", "unrelated", check=False)
        git(WORK, "checkout", "--quiet", "--orphan", "unrelated")
        self.addCleanup(cleanup)
        git(WORK, "rm", "-r", "-q", "--cached", ".")
        (WORK / "only.txt").write_text("A history of its own.\n")
        git(WORK, "add", "only.txt")
        git(WORK, "commit", "-q", "-m", "An unrelated root")
        orphan = git(WORK, "rev-parse", "HEAD").strip()
        r = self.safe_push("--commit", orphan)
        out = self.assertRefused(r, "not a fast-forward")
        self.assertEqual(self.guard(out, "fast-forward"), "FAIL", out)

    def test_origin_main_moves_during_the_checks_refused(self):
        side = self.side_commit()
        mine = self.good_commit()
        r = self.drive("move", side)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("moved", out)
        self.assertEqual(self.origin_main(), side, "the push went ahead over the new main")
        self.assertNotEqual(self.origin_main(), mine)
        self.assertIsNone(self.origin_branch(), "the branch was pushed over the new main")

    def test_origin_main_moves_at_the_push_refused(self):
        # Between safe_push's last look at origin and the push of the branch: the hook
        # runs inside `git push`, after git has read origin's refs. The branch goes up,
        # but the merge is refused: the head no longer holds main, so the tree checked is
        # not the tree a merge would make.
        side = self.side_commit()
        mine = self.good_commit()
        real = TMP / "real-pre-push"
        shutil.copy(HERE / "hooks" / "pre-push", real)
        self.swap_hook(f'#!/bin/sh\ngit -C "{ORIGIN}" update-ref refs/heads/main {side}\n'
                       f'exec sh "{real}" "$@"\n')
        r = self.safe_push()
        self.assertEqual(self.origin_branch(), mine, r.stdout + r.stderr)
        self.assertEqual(self.origin_main(), side)
        self.set_gh(lambda s: s["prs"][0].update(body=s["prs"][0]["body"].replace("- [ ]", "- [x]")))
        r = self.safe_push("--merge", "1")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("is not an ancestor", out)
        self.assertEqual(self.origin_main(), side, "the merge went ahead over the new main")


class HookRefspecs(Edge):
    """(9) The pre-push hook: every spelling of a push to main, a forced one, and a tag."""

    def push(self, *args, **env) -> subprocess.CompletedProcess:
        e = clean_env()
        e.update(env)
        return subprocess.run(["git", "push", *args], cwd=WORK, env=e, capture_output=True,
                              text=True)

    def tag(self, name: str, *args) -> None:
        git(WORK, "tag", *args, name)
        self.addCleanup(lambda: git(WORK, "tag", "-d", name, check=False))
        self.addCleanup(lambda: git(ORIGIN, "update-ref", "-d", f"refs/tags/{name}",
                                    check=False))

    def test_every_spelling_of_a_push_to_main_refused(self):
        sha = self.good_commit()
        git(WORK, "branch", "-f", "main", sha)
        self.addCleanup(lambda: git(WORK, "branch", "-f", "main", BASE))
        for args in (["origin", "HEAD:main"], ["origin", "refs/heads/main"], ["origin", "main"],
                     ["origin", f"{sha}:refs/heads/main"], ["origin", "+HEAD:main"],
                     ["--force", "origin", "HEAD:main"], ["--mirror", "origin"]):
            with self.subTest(args=args):
                r = self.push(*args)
                self.assertNotEqual(r.returncode, 0, r.stderr)
                self.assertIn("pre-push: refusing", r.stderr)
                self.assertEqual(self.origin_main(), BASE)

    def test_forced_push_refused_even_of_the_commit_checked(self):
        side = self.side_commit()
        git(ORIGIN, "update-ref", "refs/heads/main", side)
        mine = self.good_commit()                 # not a descendant of origin's main
        git(WORK, "fetch", "--quiet", "origin")
        r = self.push("origin", f"+{mine}:refs/heads/main", STOICHEIA_SAFE_PUSH=mine)
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("refusing a push to main", r.stderr)
        self.assertEqual(self.origin_main(), side)

    def test_tag_push_refused(self):
        sha = self.good_commit()
        self.addCleanup(lambda: git(ORIGIN, "update-ref", "-d", "refs/heads/stoicheia-test-tagged",
                                    check=False))
        self.tag("stoicheia-test-light")
        self.tag("stoicheia-test-annotated", "-a", "-m", "An annotated tag for the test")
        for args, env in ((["origin", "stoicheia-test-light"], {}),
                          (["origin", "refs/tags/stoicheia-test-light"], {}),
                          (["--tags", "origin"], {}),
                          (["--follow-tags", "origin", "HEAD:refs/heads/stoicheia-test-tagged"],
                           {}),
                          (["origin", "stoicheia-test-light"], {"STOICHEIA_SAFE_PUSH": sha})):
            with self.subTest(args=args, env=env):
                r = self.push(*args, **env)
                self.assertNotEqual(r.returncode, 0, r.stderr)
                self.assertIn("pre-push: refusing to push or delete the tag", r.stderr)
                self.assertEqual(git(ORIGIN, "tag", "--list", "stoicheia-test-*"), "")
                self.assertEqual(git(ORIGIN, "branch", "--list", "stoicheia-test-*"), "")
        # Deleting a tag on origin is refused too.
        r = self.push("origin", f"{sha}:refs/heads/stoicheia-test-tagged")   # a branch passes
        self.assertEqual(r.returncode, 0, r.stderr)
        git(ORIGIN, "update-ref", "refs/tags/stoicheia-test-light", sha)
        r = self.push("origin", ":refs/tags/stoicheia-test-light")
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("stoicheia-test-light", git(ORIGIN, "tag", "--list"))
        # With the owner's OK, a tag is pushed by name.
        git(ORIGIN, "update-ref", "-d", "refs/tags/stoicheia-test-light")
        r = self.push("origin", "stoicheia-test-light", STOICHEIA_TAG_PUSH="stoicheia-test-light")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("the secret scan of the push to refs/tags/stoicheia-test-light",
                      r.stdout + r.stderr)

    def test_allowed_tag_still_scanned(self):
        # Review note 12: the owner's OK for a tag does not publish an unscanned commit, nor
        # an annotated tag's message holding a private path.
        self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        self.tag("stoicheia-test-secret")
        r = self.push("origin", "refs/tags/stoicheia-test-secret",
                      STOICHEIA_TAG_PUSH="stoicheia-test-secret")
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("pre-push: refusing the push to refs/tags/stoicheia-test-secret", r.stderr)
        self.assertNotIn(TOKEN, r.stdout + r.stderr)
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        self.good_commit()
        self.tag("stoicheia-test-message", "-a", "-m", f"Notes in {PRIVATE_DIR}")
        r = self.push("origin", "refs/tags/stoicheia-test-message",
                      STOICHEIA_TAG_PUSH="stoicheia-test-message")
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("its message holds what the secret scan refuses", r.stderr)
        self.assertEqual(git(ORIGIN, "tag", "--list", "stoicheia-test-*"), "")


class DryRun(Edge):
    """(10) --dry-run never pushes, calls no gh, and leaves no worktree, on success or
    failure."""

    LOCK = LockDecisions.LOCK
    weakened = LockDecisions.weakened

    def run_dry(self, *args, driver=None) -> tuple[subprocess.CompletedProcess, Path]:
        tmp = Path(tempfile.mkdtemp(prefix="dry-run-tmp-", dir=TMP))
        calls = TMP / "pre-push-calls"
        calls.unlink(missing_ok=True)
        real = TMP / "real-pre-push"
        shutil.copy(HERE / "hooks" / "pre-push", real)
        self.swap_hook(f'#!/bin/sh\necho called >> "{calls}"\nexec sh "{real}" "$@"\n')
        env = clean_env()
        env["TMPDIR"] = str(tmp)
        refs = git(ORIGIN, "for-each-ref")
        if driver:
            r = subprocess.run([sys.executable, "-c", DRIVER, str(UNDER_TEST), driver, str(ORIGIN),
                                BASE, "--_test-skip-checks", "--dry-run", *args], cwd=WORK,
                               env=env, capture_output=True, text=True)
        else:
            r = self.safe_push("--dry-run", *args, env=env)
        out = r.stdout + r.stderr
        self.assertEqual(git(ORIGIN, "for-each-ref"), refs, f"origin's refs changed:\n{out}")
        self.assertFalse(calls.exists(), f"git push was run:\n{out}")
        self.assertEqual(self.gh_state()["calls"], [], f"gh was called:\n{out}")
        self.assertEqual(len(git(WORK, "worktree", "list").splitlines()), 1,
                         f"a temporary worktree was left behind:\n{out}")
        admin = Path(git(WORK, "rev-parse", "--git-common-dir").strip())
        admin = admin if admin.is_absolute() else WORK / admin
        self.assertEqual(list((admin / "worktrees").glob("*")) if (admin / "worktrees").exists()
                         else [], [], "worktree metadata was left behind")
        self.assertEqual(list(tmp.iterdir()), [], "temporary files were left behind")
        return r, tmp

    def test_dry_run_on_success(self):
        self.good_commit()
        r, _ = self.run_dry()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would push", r.stdout)

    def test_dry_run_refused_in_the_guards(self):
        # Refused by the axiom lock's guard, not by an earlier step.
        self.commit("Weaken Postulate 1 in the lock", self.weakened())
        r, _ = self.run_dry()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "secrets"), "ok", out)
        self.assertEqual(self.guard(out, "axiom lock"), "FAIL", out)
        self.assertIn("REFUSED: the invariant guards refused: axiom lock", out)

    def test_dry_run_refused_in_the_secret_scan(self):
        # Refused by the secret scan, which names the planted file.
        self.commit("Plant a token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r, _ = self.run_dry()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertFlagged(out, "docs/notes.md")
        self.assertIn("REFUSED: the secret scan found 1 possible secret", out)

    def test_dry_run_interrupted(self):
        self.good_commit()
        r, _ = self.run_dry(driver="interrupt")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("Interrupted", r.stdout)


# --------------------------------------------------------------------------------------
# A: the pre-flight's pull request, and --merge


def boxes_ticked(body: str) -> str:
    return body.replace("- [ ] **Required", "- [x] **Required")


def ticked(body: str) -> str:
    """The body as the coordinator completes it: the sections written, the boxes ticked."""
    body = body.replace("## What and why\n", "## What and why\n\nA change for the test.\n", 1)
    body = body.replace("## Unfinished work\n", "## Unfinished work\n\nNone\n", 1)
    for review in ("/code-review", "/security-review", "/no-mistakes"):
        body = body.replace(f"| {review} | | |", f"| {review} | abc1234 | None. |")
    body = body.replace("## Needs the owner's OK\n", "## Needs the owner's OK\n\nNothing.\n", 1)
    return boxes_ticked(body)


class PullRequests(Edge):
    def test_branch_main_refused(self):
        sha = self.good_commit()
        for name in ("main", "refs/heads/main", "Main", "HEAD"):
            with self.subTest(name=name):
                self.assertRefused(self.safe_push("--branch", name), f"--branch {name}")
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(git(ORIGIN, "for-each-ref", "--format=%(refname)", "refs/heads/"),
                         "refs/heads/main\n")
        self.assertNotEqual(sha, BASE)

    def test_direct_push_to_main_refused(self):
        self.good_commit()
        for args in ([], ["--commit", "HEAD"]):
            with self.subTest(args=args):
                r = subprocess.run([sys.executable, str(SAFE_PUSH), "--_test-skip-checks", *args],
                                   cwd=WORK, env=clean_env(), capture_output=True, text=True)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("no longer pushes to main", r.stdout)
                self.assertIn("--branch <name>", r.stdout)
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(self.gh_state()["calls"], [])

    def test_usage_errors(self):
        for args in (["--merge", "1", "--branch", "x"], ["--title", "T"],
                     ["--branch", "x", "--label", "nonsense"], ["--branch", "x", "--body-file",
                                                                 str(TMP / "none.md")]):
            with self.subTest(args=args):
                r = subprocess.run([sys.executable, str(SAFE_PUSH), *args], cwd=WORK,
                                   env=clean_env(), capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_update_keeps_the_coordinators_words(self):
        first = self.good_commit()
        r = self.safe_push("--label", "docs")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (pr,) = self.gh_state()["prs"]
        self.assertTrue(pr["isDraft"])
        self.assertEqual(pr["labels"], ["docs"])
        self.assertIn(f"sha={first}", pr["body"])
        # The coordinator writes the reviews in; a fix lands on the branch, and the
        # pre-flight runs again: the summary is replaced, and nothing else.
        words = "| /code-review | abc1234 | One material finding, resolved in the fix. |"
        self.set_gh(lambda s: s["prs"][0].update(
            body=s["prs"][0]["body"].replace("| /code-review | | |", words)))
        second = self.good_commit("A second line, the fix.")
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("#1 updated", out)
        (pr,) = self.gh_state()["prs"]
        self.assertIn(words, pr["body"])
        self.assertIn(f"sha={second}", pr["body"])
        self.assertNotIn(f"sha={first}", pr["body"])
        self.assertEqual(pr["body"].count("safe_push:preflight begin"), 1)
        self.assertEqual(self.origin_branch(), second)

    def test_update_refreshes_the_generated_parts(self):
        # The final review: every part safe_push wrote is written afresh on an update (the
        # commits, the statements changed, the records), and the coordinator's words stay.
        self.good_commit()
        self.assertEqual(self.safe_push().returncode, 0)
        words = "A change for the test, in the coordinator's words."
        self.set_gh(lambda s: s["prs"][0].update(body=s["prs"][0]["body"].replace(
            "## What and why\n", f"## What and why\n\n{words}\n", 1)))

        def part(body, heading, after):
            return body[body.index(f"## {heading}"):body.index(f"## {after}")]
        body = self.gh_state()["prs"][0]["body"]
        self.assertIn("None.", part(body, "Statements changed", "Review records"))
        self.assertIn("None.", part(body, "Review records", "Protected paths"))
        # The fix: I.1's statement changes, with a decision naming it, and its record is
        # re-stamped.
        lean, record = "Elements/BookI/Prop01.lean", "review/I/01.toml"
        new_lean = self.replaced(lean, SIGNATURE_OLD, SIGNATURE_NEW)
        stamped = re.sub(r'(?m)^lean = "[^"]*"',
                         f'lean = "{safe_push.heath._sha(new_lean.encode())}"', self.text(record))
        stamped = re.sub(r'(?m)^commit = "[^"]*"', 'commit = "abc1234"', stamped)
        changes = {lean: new_lean, record: stamped}
        changes.update(self.decision("I.1 names its side point Q."))
        second = self.regenerated_commit("I.1 names its side point Q", changes)
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        body = self.gh_state()["prs"][0]["body"]
        self.assertIn(words, body)
        statements = part(body, "Statements changed", "Review records")
        self.assertIn("I.1 (the Lean statement changed), named in the docs/briefs/ lines added",
                      statements)
        self.assertNotIn("None.", statements)
        self.assertIn("`review/I/01.toml`: re-stamped at `abc1234`",
                      part(body, "Review records", "Protected paths"))
        self.assertIn(f"`{short_sha(second)}` I.1 names its side point Q", body)
        for name in ("commits", "statements", "records", "protected", "generated", "preflight"):
            self.assertEqual(body.count(f"<!-- safe_push:{name} begin"), 1, name)

    def test_update_keeps_the_words_around_a_quoted_marker(self):
        # The re-review: a marker the coordinator quotes in "What and why", before the part
        # it names, is not a marker. The update refreshes safe_push's parts and leaves every
        # word and section of the coordinator's in place.
        self.good_commit()
        self.assertEqual(self.safe_push().returncode, 0)
        words = ("Moves the records: safe_push writes them after "
                 "`<!-- safe_push:records begin -->`.\n\nMore of the coordinator's reasoning.")
        approval = "I.1: the decisions entry of 18 October."

        def edit(s):
            body = s["prs"][0]["body"].replace("## What and why\n",
                                               f"## What and why\n\n{words}\n", 1)
            s["prs"][0]["body"] = body.replace("## Statements changed\n",
                                               f"## Statements changed\n\n{approval}\n", 1)
        self.set_gh(edit)
        before = self.gh_state()["prs"][0]["body"]
        second = self.good_commit("A second line, the fix.")
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        body = self.gh_state()["prs"][0]["body"]
        for text in (words, approval):
            self.assertIn(text, body)
        self.assertEqual(re.findall(r"(?m)^## .*$", body), re.findall(r"(?m)^## .*$", before))
        self.assertIn(f"`{short_sha(second)}` A good commit", body)
        self.assertIn(f"sha={second}", body)
        for name in ("commits", "statements", "records", "protected", "generated", "preflight"):
            self.assertEqual(len(re.findall(rf"(?m)^<!-- safe_push:{name} begin", body)), 1,
                             name)

    def test_update_creates_a_label_the_open_pull_request_now_needs(self):
        # A later commit changes a protected path: the label security-review is made before
        # `gh pr edit --add-label` asks for it (gh refuses a label that does not exist).
        self.good_commit()
        self.assertEqual(self.safe_push().returncode, 0)
        path = "scripts/check_style.py"
        change = {path: self.text(path) + "\n# A comment for the test.\n"}
        change.update(self.decision(f"A comment in `{path}`, for the test."))
        self.commit("A protected change on the open branch", change)
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("security-review", self.gh_state()["prs"][0]["labels"])

    def test_ci_followed_when_its_checks_appear_late(self):
        # Real gh says "no checks reported" (stderr, exit 1) until CI registers on a new
        # head: the pre-flight waits for them, then follows and judges them.
        self.good_commit()
        self.set_gh(lambda s: s.update(nochecks=2))
        env = clean_env()
        env["STOICHEIA_TEST_CI_POLL"] = "0"
        r = self.safe_push(env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "CI"), "ok", out)
        asked = [c for c in self.gh_state()["calls"] if c[:2] == ["pr", "checks"]
                 and "--watch" not in c]
        self.assertGreaterEqual(len(asked), 4, asked)     # twice none, then found, then judged
        # When none ever appear: CI not followed, exit 3.
        self.good_commit("A second line, the fix.")
        self.set_gh(lambda s: s.update(nochecks=10 ** 6))
        env.update(STOICHEIA_TEST_CI_POLL="0.2", STOICHEIA_TEST_CI_APPEAR="1")
        r = self.safe_push(env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("no checks appeared", out)

    def test_body_file(self):
        self.good_commit()
        body = TMP / "body.md"
        body.write_text("A body of my own.\n\n<!-- safe_push: commits -->\n\n"
                        "<!-- safe_push: preflight -->\n")
        r = self.safe_push("--title", "My title", "--body-file", str(body))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (pr,) = self.gh_state()["prs"]
        self.assertEqual(pr["title"], "My title")
        self.assertTrue(pr["body"].startswith("A body of my own."))
        self.assertIn("Commits (", pr["body"])
        self.assertIn("safe_push:preflight begin", pr["body"])

    def test_branch_with_commits_this_one_lacks_refused(self):
        theirs = self.good_commit("Their line.")
        git(WORK, "push", "--quiet", "origin", f"{theirs}:refs/heads/{BRANCH}")
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        self.good_commit("My line.")
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("has commits", out)
        self.assertEqual(self.origin_branch(), theirs, "the branch was forced")

    def test_a_forks_pull_request_of_the_same_name_is_left_alone(self):
        # Review note 7: `gh pr list --head` matches a fork's branch of the same name; the
        # pre-flight opens a pull request of its own, and never edits the stranger's.
        sha = self.good_commit()
        stranger = {"number": 1, "title": "A stranger's", "body": "A stranger's body.\n",
                    "headRefName": BRANCH, "baseRefName": "main", "isDraft": False,
                    "labels": [], "state": "OPEN", "isCrossRepository": True,
                    "headRepositoryOwner": {"login": "stranger"}, "forkHead": "f" * 40,
                    "url": "https://github.invalid/test/stoicheia/pull/1"}
        self.set_gh(lambda s: s["prs"].append(stranger))
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("#2 opened", out)
        theirs, ours = self.gh_state()["prs"]
        self.assertEqual((theirs["body"], theirs["labels"]), (stranger["body"], []))
        self.assertIn(f"sha={sha}", ours["body"])
        edits = [c for c in self.gh_state()["calls"] if c[:2] == ["pr", "edit"]]
        self.assertEqual(edits, [], "the stranger's pull request was edited")

    def test_our_pull_request_found_whatever_owner_github_names(self):
        # The no-mistakes review: after a rename or a transfer, which GitHub redirects,
        # origin's URL names the old owner, and GitHub the new one as the head's. Our pull
        # request (the head a branch of origin itself) is still found and updated, never
        # opened a second time.
        self.good_commit()
        self.assertEqual(self.safe_push().returncode, 0)
        self.set_gh(lambda s: s["prs"][0].update(headRepositoryOwner={"login": "new-owner"}))
        for args, line in ((("--label", "docs"), "A second line, the fix."),
                           (("--branch", BRANCH), "A third line, its kind from the open one.")):
            with self.subTest(args=args):
                sha = self.good_commit(line)
                r = self.safe_push(*args)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 0, out)
                self.assertIn("#1 updated", out)
                (pr,) = self.gh_state()["prs"]
                self.assertIn(f"sha={sha}", pr["body"])
        self.assertIn("kind label: on #1", out)
        creates = [c for c in self.gh_state()["calls"] if c[:2] == ["pr", "create"]]
        self.assertEqual(len(creates), 1, creates)

    def test_public_names_scanned_before_the_push(self):
        # Review note 9: the title is posted, and the branch name pushed as a ref.
        self.good_commit()
        self.assertRefused(self.safe_push("--title", f"Notes from {PRIVATE_DIR}"),
                           "a public name", "the title")
        name = "secret" + "s2026-notes"
        out = self.assertRefused(self.safe_push("--branch", name), "the branch name")
        self.assertIsNone(self.origin_branch(name), out)
        self.assertEqual(self.gh_state()["calls"], [])

    def test_open_pull_requests_body_scanned_before_the_push(self):
        first = self.good_commit()
        self.assertEqual(self.safe_push().returncode, 0)
        self.set_gh(lambda s: s["prs"][0].update(body=s["prs"][0]["body"]
                                                 + f"\nSee {PRIVATE_DIR}.\n"))
        self.good_commit("A second line, the fix.")
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("the pull request's body holds what the secret scan refuses", out)
        self.assertEqual(self.origin_branch(), first, "the fix was pushed before the body "
                         "was checked")

    def test_hand_edit_to_program_md_is_not_a_generated_change(self):
        # Review note 11: README.md and PROGRAM.md are generated only between markers.
        path = "docs/PROGRAM.md"
        self.commit("A lesson, by hand", {path: self.replaced(
            path, "## 6. Cost and time", "- **A lesson for the test.**\n\n## 6. Cost and time")})
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        body = Path(re.search(r"the body it would post: (\S+)", out).group(1)).read_text()
        generated = body[body.index("## Generated files"):body.index("## Needs the owner's OK")]
        self.assertIn("None.", generated)
        self.assertNotIn("PROGRAM.md", generated)

    def test_ci_failing_after_the_push(self):
        sha = self.good_commit()
        failing = [dict(c, bucket="fail", state="FAILURE") if c["name"] == "negative" else c
                   for c in PASSING]
        self.set_gh(lambda s: s["checks"].update({sha: failing}))
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("CI did not pass", out)
        self.assertIn("failing: negative", out)
        self.assertEqual(self.origin_main(), BASE)

    def stale_release_check(self, bucket):
        sha = self.good_commit()
        check = {"name": "release-gate", "workflow": "Release gate", "bucket": bucket,
                 "state": "FAILURE" if bucket == "fail" else "IN_PROGRESS"}
        self.set_gh(lambda s: s["checks"].update({sha: PASSING + [check]}))
        return sha

    def test_watcher_ignores_failed_stale_release_check(self):
        self.stale_release_check("fail")
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "CI"), "ok", r.stdout)

    def test_watcher_ignores_pending_stale_release_check(self):
        self.stale_release_check("pending")
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "CI"), "ok", r.stdout)

    def test_watcher_keeps_release_check_for_given_and_carried_labels(self):
        self.stale_release_check("fail")
        r = self.safe_push("--label", "release", "--label", "tooling")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("failing: release-gate", r.stdout)
        self.set_gh(lambda s: s["prs"][0].update(labels=["tooling", "Release"]))
        r = self.safe_push()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("failing: release-gate", r.stdout)

    def test_watcher_keeps_release_check_when_label_is_added_during_watch(self):
        self.stale_release_check("fail")
        self.set_gh(lambda s: s.update(watch_labels=["docs", "release"]))
        r = self.safe_push()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("failing: release-gate", r.stdout)

    def test_watcher_ignores_release_check_when_label_is_removed_during_watch(self):
        self.stale_release_check("fail")
        self.set_gh(lambda s: s.update(watch_labels=["docs"]))
        r = self.safe_push("--label", "docs", "--label", "release")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "CI"), "ok", r.stdout)

    def test_watcher_refuses_unreadable_final_labels_without_exemption(self):
        self.stale_release_check("fail")
        self.set_gh(lambda s: s.update(watch_raw_labels=None))
        r = self.safe_push()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("the pull request's labels are unreadable", r.stdout)
        self.assertIn("failing: release-gate", r.stdout)

    def test_watcher_refuses_failed_final_label_read_without_exemption(self):
        self.stale_release_check("fail")
        self.set_gh(lambda s: s.update(label_read_fail=True))
        r = self.safe_push()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("the pull request's labels could not be read", r.stdout)
        self.assertIn("failing: release-gate", r.stdout)


class Merge(Edge):
    def unfinished_body(self, text):
        self.set_gh(lambda s: s["prs"][0].update(body=re.sub(
            r"(## Unfinished work\n).*?(?=\n## )", lambda m: m.group(1) + "\n" + text + "\n",
            ticked(s["prs"][0]["body"]), count=1, flags=re.S)))

    def blocker(self, **changes):
        issue = {"number": 38, "title": "Finish the prototype", "state": "open",
                 "labels": [{"name": "blocks-release"}],
                 "repository_url": "https://api.github.com/repos/test/stoicheia",
                 "html_url": "https://github.invalid/test/stoicheia/issues/38"}
        return dict(issue, **changes)

    def test_unfinished_work_unwritten_refused(self):
        self.opened()
        self.unfinished_body("")
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
        self.assertIn("Unfinished work must say None", out)
        self.assertEqual(self.merges(), [])

    def test_unfinished_work_closed_and_unlabelled_refused(self):
        self.opened()
        self.unfinished_body("- Prototype #38\n- Deferred page #39")
        self.set_gh(lambda s: s.update(issues=[
            self.blocker(state="closed"), self.blocker(number=39, labels=[])]))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
        self.assertIn("#38 is closed", out)
        self.assertIn("#39 lacks the label blocks-release", out)
        self.assertEqual(self.merges(), [])

    def test_release_label_given_after_the_gates_refused(self):
        # An ordinary pull request passes the gates; "release" is then given before the
        # merge, with a blocker open: the labels are read again, and nothing merges.
        self.opened()
        self.unfinished_body("None")
        labels = self.gh_state()["prs"][0]["labels"]
        self.set_gh(lambda s: s.update(issues=[self.blocker()],
                                       relabel=list(labels) + ["release"]))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("labels changed after the gates read them", out)
        self.assertEqual(self.merges(), [])

    def test_final_gates_refuse_a_blocker_opened_after_body_refresh(self):
        self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: (s["prs"][0]["labels"].append("release"),
                               s.update(after_body={"issues": [self.blocker()]})))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("FAIL  release:", out)
        self.assertIn("#38: Finish the prototype", out)
        self.assertEqual(self.merges(), [])

    def test_final_gates_refuse_an_unreadable_blocker_reply(self):
        self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: (s["prs"][0]["labels"].append("release"),
                               s.update(after_body={"issue_read_fail": True})))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("FAIL  release:", out)
        self.assertIn("release issues unreadable", out)
        self.assertEqual(self.merges(), [])

    def test_final_gates_refuse_a_named_issue_changed_after_body_refresh(self):
        self.opened()
        self.unfinished_body("- Prototype #38")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        for issue, reason in ((self.blocker(state="closed"), "#38 is closed"),
                              (self.blocker(labels=[]), "lacks the label blocks-release")):
            with self.subTest(reason=reason):
                self.set_gh(lambda s: s.update(after_body={"issues": [issue]}))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("FAIL  unfinished work:", out)
                self.assertIn(reason, out)
                self.assertEqual(self.merges(), [])
                self.set_gh(lambda s: s.update(issues=[self.blocker()]))

    def test_final_gates_refuse_release_ci_changed_after_body_refresh(self):
        sha = self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: s["prs"][0]["labels"].append("release"))
        for bucket, state in (("pending", "IN_PROGRESS"), ("fail", "FAILURE")):
            with self.subTest(bucket=bucket):
                check = {"name": "release-gate", "workflow": "Release gate",
                         "bucket": bucket, "state": state}
                self.set_gh(lambda s: s.update(after_body={
                    "checks": {"*": PASSING, sha: PASSING + [check]}}))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("FAIL  CI:", out)
                self.assertIn("release-gate", out)
                self.assertEqual(self.merges(), [])
                self.set_gh(lambda s: s.update(checks={"*": PASSING, sha: PASSING}))

    def test_unfinished_work_changed_after_the_gates_refused(self):
        self.opened()
        self.unfinished_body("None")
        body = self.gh_state()["prs"][0]["body"]
        self.set_gh(lambda s: s.update(reread_body=body.replace(
            "\nNone\n", "\n- Deferred page to come\n", 1)))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("changed after the gates read it", out)
        self.assertEqual(self.merges(), [])

    def test_merge_never_overwrites_a_concurrent_unfinished_edit(self):
        self.opened()
        body = ticked(self.gh_state()["prs"][0]["body"])
        concurrent = re.sub(
            r"(## Unfinished work\n).*?(?=\n## )",
            lambda m: m.group(1) + "\n- Prototype #38\n", body, count=1, flags=re.S)
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        before = len([c for c in self.gh_state()["calls"]
                      if c[:2] == ["pr", "edit"] and "--body-file" in c])
        r = self.driven_merge("edit-after-unfinished-comparison")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "body"), "FAIL", out)
        self.assertIn("run `git safe-push --branch test-pr`", out)
        self.assertEqual(self.gh_state()["prs"][0]["body"], concurrent)
        after = len([c for c in self.gh_state()["calls"]
                     if c[:2] == ["pr", "edit"] and "--body-file" in c])
        self.assertEqual(after, before)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_body_edited_in_github_s_page_with_crlf_merges(self):
        # GitHub keeps a body edited in its page with CRLF line ends, and the parts are
        # written afresh with LF: parts that differ by line ends alone are up to date.
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(
            body=ticked(s["prs"][0]["body"]).replace("\n", "\r\n")))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertNotEqual(self.guard(out, "body"), "FAIL", out)
        self.assertEqual(git(ORIGIN, "rev-parse", "main^2").strip(), sha)
        self.assertIn("\r\n", self.gh_state()["prs"][0]["body"])

    def test_crlf_body_with_a_stale_part_is_still_refused(self):
        self.opened()
        end = "<!-- safe_push:commits end -->"
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"]).replace(
            end, "- `0123456789ab` A commit no longer on the branch\n" + end, 1)
            .replace("\n", "\r\n")))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "body"), "FAIL", out)
        self.assertIn("run `git safe-push --branch test-pr`", out)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_refresh_that_would_change_unfinished_work_refused(self):
        # The statements part's end marker moved past "## Review records": writing the
        # parts afresh would swallow the section, so the gates, reading its heading as
        # GitHub shows it without the parts safe_push writes, refuse it before any write.
        self.opened()
        self.unfinished_body("None")
        def move(s):
            body = s["prs"][0]["body"]
            end = "<!-- safe_push:statements end -->\n"
            body = body.replace(end, "", 1).replace("## Review records\n",
                                                    "## Review records\n" + end, 1)
            s["prs"][0]["body"] = body
        self.set_gh(move)
        def edits():
            return [c for c in self.gh_state()["calls"] if c[:2] == ["pr", "edit"]
                    and "--body-file" in c]
        before = len(edits())
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
        self.assertIn("must be one GitHub shows", out)
        self.assertEqual(len(edits()), before)      # the body was not written
        self.assertEqual(self.merges(), [])

    def test_unfinished_work_open_labelled_issue_merges(self):
        self.opened()
        self.unfinished_body("- Prototype #38")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "unfinished work"), "ok", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_unfinished_work_read_failure_refused(self):
        self.opened()
        self.unfinished_body("- Prototype #38")
        self.set_gh(lambda s: s.update(issue_read_fail=True))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("#38 unreadable", out)
        self.assertEqual(self.merges(), [])

    def test_wrapped_unfinished_item_merges(self):
        self.opened()
        self.unfinished_body("- Prototype awaiting a proof,\n  tracked by #38.")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "unfinished work"), "ok", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_unfinished_markup_and_fragments_refuse_the_merge(self):
        self.opened()
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        cases = (
            ("- Prototype [section](#38)", "bracket"),
            ("- Prototype https://example.invalid/page?x=#38", "URL"),
            ("- Prototype #38, see WWW.GITHUB.COM/example/edition/issues/39", "URL"),
            ("- Prototype #38 example.org/ticket/39", "URL"),
            ("- Prototype #38 fooGH-39", "write the issue as #N on its own"),
            ("- _Prototype_ #38", "emphasis"),
            ("- Prototype `code\n  #38`", "backtick"),
            ("- ```\n  #38\n  ```", "backtick"),
            ('- Prototype <span title="#38">later</span>', "HTML"),
            ("[prototype]: https://github.com/test/stoicheia/issues/38", "bracket"),
            ("> - Prototype #38\n> - Deferred page to come", "block quote"),
            ("- Prototype #38\n  - Deferred page", "nested list"),
            ("1. Prototype #38", "plain list"),
            ("None\n<div><ul><li>Deferred page</li></ul></div>", "HTML"),
            ("None\n```\n- Deferred page to come\n```", "backtick"),
            ("None\n~~~\n- Deferred page to come\n~~~", "tilde"),
            ("None\n<!-- safe_push:custom begin -->\n- Prototype with no issue\n"
             "<!-- safe_push:custom end -->", "a comment other than the template's own"),
            ("-     Prototype #38", "plain list"),
            ("-\tPrototype #38", "tab"),
        )
        for text, reason in cases:
            with self.subTest(text=text):
                self.unfinished_body(text)
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
                self.assertIn(reason, out)
                self.assertEqual(self.merges(), [])
                self.assertEqual(self.origin_main(), BASE)

    def test_unfinished_ipv4_url_refuses_the_merge(self):
        self.opened()
        self.unfinished_body("- Prototype #38 192.0.2.1/ticket/39")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
        self.assertIn("URL", out)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_unfinished_hostname_port_url_refuses_the_merge(self):
        self.opened()
        self.unfinished_body("- Prototype #38 localhost:8080/ticket/39")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
        self.assertIn("URL", out)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_duplicate_unfinished_sections_refuse_the_merge(self):
        self.opened()
        self.unfinished_body("None\n\n## Unfinished work ##\n- Deferred page")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
        self.assertIn("exactly one", out)
        self.assertEqual(self.merges(), [])

    def test_hidden_unfinished_heading_refuses_the_merge(self):
        # The one raw heading, and the section after it saying None, where GitHub shows
        # no heading: in a comment, code, an HTML block or a part safe_push writes.
        self.opened()
        body = ticked(self.gh_state()["prs"][0]["body"])
        for before, after in (("<!--", "-->"), ("```", "```"), ("~~~", "~~~"),
                              ("<div>", "</div>"),
                              ("<!-- safe_push:custom begin -->",
                               "<!-- safe_push:custom end -->")):
            hidden = re.sub(r"## Unfinished work\n.*?(?=## Review records\n)",
                            lambda m: f"{before}\n## Unfinished work\nNone\n"
                                      f"## Review records\n{after}\n\n",
                            body, count=1, flags=re.S)
            with self.subTest(before=before):
                self.set_gh(lambda s: s["prs"][0].update(body=hidden))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
                self.assertIn("must be one GitHub shows", out)
                self.assertEqual(self.merges(), [])
                self.assertEqual(self.origin_main(), BASE)

    def test_fence_opened_in_a_safe_push_part_refuses_the_merge(self):
        # The section moved to the end, after a part safe_push writes that opens a fence:
        # GitHub shows the part, so the fence hides the heading and the section after it,
        # whether it runs to the end or a longer fence closes it after them.
        self.opened()
        body = re.sub(r"## Unfinished work\n.*?(?=## Review records\n)", "",
                      ticked(self.gh_state()["prs"][0]["body"]), count=1, flags=re.S)
        for closer in ("", "````\n"):
            hidden = body.rstrip("\n") + "\n\n" + (
                "<!-- safe_push:custom begin -->\n```\n<!-- safe_push:custom end -->\n"
                "## Unfinished work\nNone\n## Review records\n" + closer)
            with self.subTest(closer=closer):
                self.set_gh(lambda s: s["prs"][0].update(body=hidden))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
                self.assertIn("must be one GitHub shows", out)
                self.assertEqual(self.merges(), [])
                self.assertEqual(self.origin_main(), BASE)

    def test_unfinished_heading_after_closed_comment_code_and_html_merges(self):
        self.opened()
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        self.unfinished_body("- Prototype #38")
        self.set_gh(lambda s: s["prs"][0].update(body=s["prs"][0]["body"].replace(
            "## Unfinished work\n", "<!--\nA note.\n-->\n```\ncode\n```\n<div>\nA note.\n"
            "</div>\n\n## Unfinished work\n", 1)))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "unfinished work"), "ok", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_unreadable_labels_refuse_release_without_stale_check_exemption(self):
        sha = self.opened()
        self.unfinished_body("None")
        self.set_gh(lambda s: s["checks"].update({sha: PASSING + [
            {"name": "release-gate", "workflow": "Release gate", "bucket": "fail"}]}))
        for labels in ([{"name": "tooling"}, {}], None, "missing"):
            with self.subTest(labels=labels):
                def set_labels(s):
                    pr = s["prs"][0]
                    pr.pop("raw_labels", None)
                    pr.pop("omit_labels", None)
                    if labels == "missing":
                        pr["omit_labels"] = True
                    else:
                        pr["raw_labels"] = labels
                self.set_gh(set_labels)
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("the pull request's labels are unreadable", out)
                self.assertEqual(self.guard(out, "release"), "FAIL", out)
                self.assertEqual(self.guard(out, "CI"), "FAIL", out)
                self.assertEqual(self.merges(), [])

    def test_transferred_or_unbound_unfinished_issue_refuses_the_merge(self):
        self.opened()
        self.unfinished_body("- Prototype #38")
        missing = self.blocker()
        del missing["repository_url"]
        for issue, reason in (
                (self.blocker(repository_url="https://api.github.com/repos/test/other"),
                 "another repository"), (missing, "repository_url")):
            with self.subTest(issue=issue):
                self.set_gh(lambda s: s.update(issues=[issue]))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "unfinished work"), "FAIL", out)
                self.assertIn(reason, out)
                self.assertEqual(self.merges(), [])

    def test_canonical_repository_read_failure_refuses_the_merge(self):
        self.opened()
        self.unfinished_body("- Prototype #38")
        self.set_gh(lambda s: s.update(issues=[self.blocker()]))
        for reply in ({"repository_read_fail": True}, {"repository_output": "{}"},
                      {"repository_output": "{"}):
            with self.subTest(reply=reply):
                self.set_gh(lambda s: (s.pop("repository_read_fail", None),
                                       s.pop("repository_output", None), s.update(reply)))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("repository unreadable", out)
                self.assertEqual(self.merges(), [])

    def test_release_label_case_holds_the_merge_for_blockers_and_bad_reads(self):
        self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: s["prs"][0]["labels"].append("Release"))
        for reply, reason in (
                ({"issues": [self.blocker(labels=[{"name": "BLOCKS-RELEASE"}])]},
                 "#38: Finish the prototype"),
                ({"issue_output": "{"}, "release issues unreadable")):
            with self.subTest(reply=reply):
                self.set_gh(lambda s: s.update(reply))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "release"), "FAIL", out)
                self.assertIn(reason, out)
                self.assertEqual(self.merges(), [])

    def removed_release_label_merges(self, bucket):
        sha = self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: s["prs"][0]["labels"].append("release"))
        check = {"name": "release-gate", "workflow": "Release gate", "bucket": bucket,
                 "state": "FAILURE" if bucket == "fail" else "IN_PROGRESS"}
        self.set_gh(lambda s: s["checks"].update({sha: PASSING + [check]}))
        r = self.merge()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "CI"), "FAIL", r.stdout)
        self.assertEqual(self.merges(), [])
        self.set_gh(lambda s: s["prs"][0]["labels"].remove("release"))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "CI"), "ok", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_removed_release_label_with_failing_check_merges(self):
        self.removed_release_label_merges("fail")

    def test_removed_release_label_with_pending_check_merges(self):
        self.removed_release_label_merges("pending")

    def test_ordinary_pull_request_still_judges_every_other_check(self):
        sha = self.opened()
        self.unfinished_body("None")
        for name, workflow in (("release-gate", "CI"), ("other", "Release gate")):
            with self.subTest(name=name, workflow=workflow):
                check = {"name": name, "workflow": workflow, "bucket": "fail", "state": "FAILURE"}
                self.set_gh(lambda s: s["checks"].update({sha: PASSING + [check]}))
                r = self.merge()
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertEqual(self.guard(r.stdout, "CI"), "FAIL", r.stdout)
                self.assertEqual(self.merges(), [])

    def test_release_waits_for_all_open_blockers_then_merges(self):
        self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: s["prs"][0]["labels"].append("release"))
        self.set_gh(lambda s: s.update(issues=[
            self.blocker(), self.blocker(number=39, title="Finish the page",
                                        pull_request={})]))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "release"), "FAIL", out)
        self.assertIn("#38: Finish the prototype", out)
        self.assertIn("#39: Finish the page", out)
        self.assertEqual(self.merges(), [])
        self.set_gh(lambda s: s.update(issues=[]))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "release"), "ok", r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_release_issue_read_failures_refused(self):
        self.opened_r3()
        self.unfinished_body("None")
        self.set_gh(lambda s: s["prs"][0]["labels"].append("release"))
        for reply in ({"issue_read_fail": True}, {"issue_output": "[]\n{"},
                      {"issue_output": '[{"number": 38}]'}):
            with self.subTest(reply=reply):
                self.set_gh(lambda s: (s.pop("issue_read_fail", None),
                                       s.pop("issue_output", None), s.update(reply)))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "release"), "FAIL", out)
                self.assertIn("release issues unreadable", out)
                self.assertEqual(self.merges(), [])

    def test_ordinary_pull_request_never_reads_open_blockers(self):
        self.opened()
        self.unfinished_body("None")
        self.set_gh(lambda s: s.update(issues=[self.blocker()], issue_read_fail=True))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "unfinished work"), "ok", r.stdout)
        self.assertEqual(self.step(r.stdout, "release"), "skip", r.stdout)
        # The merge's only reads of the API are main's rules, whether main is red (its
        # open main-red issues and the post-merge runs at its tip): none of them is a
        # read of the release's blockers.
        allowed = ("repos/test/stoicheia/rules/branches/main",
                   "repos/test/stoicheia/issues?state=open&labels=main-red&per_page=100",
                   "repos/test/stoicheia/actions/workflows/post-merge.yml/runs?branch=main"
                   "&head_sha=")
        reads = [c for c in json.loads(GH_STATE.read_text())["calls"] if c[0] == "api"]
        self.assertTrue(reads)
        self.assertEqual([c for c in reads if not c[1].startswith(allowed)], [])
        self.assertEqual(len(self.merges()), 1)

    def opened(self, *args, ready=True, **write) -> str:
        sha = self.good_commit() if not write else self.commit("A change", write)
        r = self.safe_push(*args, *(("--ready",) if ready else ()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return sha

    def opened_r3(self, *args, ready=True) -> str:
        """Opened as `opened` opens it, its commit R3 by scripts/risk.py: a line in
        docs/WORKFLOW.md, the guide to the checks, which no guard protects. Its pre-flight
        takes step 4's full path (under the internal test flag, its skip), as a release
        needs, and leaves a record of the full checks; good_commit's, R0, would leave the
        full checks to CI (docs/decisions/2026-10-22-checks-by-risk.md)."""
        return self.opened(*args, ready=ready, **{"docs/WORKFLOW.md": (
            self.text("docs/WORKFLOW.md") + "\nA line for the test.\n")})

    def merge(self, *args) -> subprocess.CompletedProcess:
        return self.safe_push("--merge", "1", *args)

    def test_merge_waits_for_the_gates(self):
        sha = self.opened(ready=False)
        self.assertTrue(self.gh_state()["prs"][0]["isDraft"], "a new pull request is a draft")
        failing = [dict(c, bucket="pending", state="IN_PROGRESS") for c in PASSING]
        self.set_gh(lambda s: s["checks"].update({sha: failing}))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        for gate in ("draft", "checklist", "sections", "CI"):
            self.assertEqual(self.guard(out, gate), "FAIL", f"{gate}:\n{out}")
        self.assertIn("unticked: Required:", out)
        self.assertIn("still running", out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(self.origin_branch(), sha)

    def test_merge_with_a_merge_commit(self):
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        r = self.merge("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would merge", r.stdout)
        self.assertEqual(self.origin_main(), BASE)
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        main = self.origin_main()
        self.assertEqual(git(ORIGIN, "rev-list", "--parents", "-n", "1", main).split()[1:],
                         [BASE, sha], "not a merge commit of main and the head")
        self.assertIsNone(self.origin_branch(), "the branch was not deleted")
        merges = self.merges()
        self.assertEqual(len(merges), 1)
        self.assertIn("--merge", merges[0])
        self.assertIn(sha, merges[0])               # --match-head-commit
        self.assertFalse({"--squash", "--rebase", "--admin", "--auto"} & set(merges[0]))
        self.assertEqual(self.guard(out, "main"), "ok", out)
        # The merge commit's message is the one scanned: GitHub's subject, and the title.
        subject = f"Merge pull request #1 from test/{BRANCH}"
        self.assertIn("--subject", merges[0])
        self.assertIn("--body", merges[0])
        self.assertEqual(merges[0][merges[0].index("--subject") + 1], subject)
        self.assertEqual(merges[0][merges[0].index("--body") + 1], "A good commit")
        self.assertEqual(git(ORIGIN, "log", "-1", "--format=%B", main).strip(),
                         f"{subject}\n\nA good commit")

    def test_merge_subject_names_the_owner_github_names(self):
        # Issue #41: after a transfer or a rename, which GitHub redirects, origin's URL names
        # the old owner, and GitHub the new one for the head. The merge commit's subject is
        # GitHub's own words, so it names the owner GitHub reports; when GitHub names none,
        # the gates refuse, before gh is asked to merge.
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        # None, or an answer no account could have (the review of 19 October): each is
        # refused by the gate, never a traceback, and never a subject.
        for owner in (None, "new-owner", {"login": True}, {"login": ""},
                      {"login": "new-owner/x"}, {"login": "new owner"}):
            with self.subTest(owner=owner):
                self.set_gh(lambda s: s["prs"][0].update(headRepositoryOwner=owner))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "subject"), "FAIL", out)
                self.assertIn("GitHub names no owner for #1's head", out)
                self.assertNotIn("Traceback", out)
                self.assertEqual(self.merges(), [])
                self.assertEqual(self.origin_main(), BASE)
        self.set_gh(lambda s: s["prs"][0].update(headRepositoryOwner={"login": "new-owner"}))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        subject = f"Merge pull request #1 from new-owner/{BRANCH}"
        self.assertEqual(self.guard(out, "subject"), "ok", out)
        self.assertIn(subject, out)
        (call,) = self.merges()
        self.assertEqual(call[call.index("--subject") + 1], subject)
        main = self.origin_main()
        self.assertEqual(git(ORIGIN, "rev-parse", f"{main}^2").strip(), sha)
        self.assertEqual(git(ORIGIN, "log", "-1", "--format=%s", main).strip(), subject)

    def test_missing_required_box_refused(self):
        self.opened()
        drop = "- [ ] **Required:** Nothing public goes out without the owner's OK.\n"

        def edit(s):
            body = s["prs"][0]["body"]
            assert drop in body
            s["prs"][0]["body"] = ticked(body.replace(drop, ""))
        self.set_gh(edit)
        out = self.merge().stdout
        self.assertIn("missing from the body: Required: Nothing public", out)
        self.assertEqual(self.origin_main(), BASE)

    def test_new_head_needs_a_fresh_preflight_before_merge(self):
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        newer = self.good_commit("A line pushed by hand.")
        git(WORK, "push", "--quiet", "origin", f"{newer}:refs/heads/{BRANCH}")
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn(f"none of {newer[:12]}", out)
        self.assertEqual(self.guard(out, "body"), "FAIL", out)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), newer)
        self.assertIn(f"sha={newer}", self.gh_state()["prs"][0]["body"])

    def test_merge_runs_the_scan_and_the_guards_again(self):
        # Review note 6: the pre-flight's record stands in for the full checks alone.
        self.opened_r3()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        out = self.merge("--dry-run").stdout
        self.assertIn("the full checks are not repeated", out)
        for name in ("secrets", "statements", "protected paths", "heath/", "review records"):
            self.assertEqual(self.guard(out, name), "ok", f"{name}:\n{out}")

    def test_forged_record_does_not_skip_the_scan_or_the_guards(self):
        # A record in the local store, as code the pre-flight ran could write it, for a
        # head pushed by hand that plants a token and edits Heath with no leaf named.
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        bad = self.commit("A head pushed by hand", {
            "docs/notes.md": f"api_token = \"{TOKEN}\"\n",
            "heath/I/01.md": self.replaced("heath/I/01.md", *Heath.WORD)})
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{bad}:refs/heads/{BRANCH}")
        harness = safe_push.blob_id(SAFE_PUSH.read_bytes())
        record = {"sha": bad, "base": BASE, "branch": BRANCH, "full": True,
                  "time": "forged", "harness": "origin/main's", "harness_blob": harness,
                  "steps": [["2", "secrets", "ok", 0.1], ["4", "lake build", "ok", 1.0]],
                  "notes": [], "protected": [], "statements": []}
        path = LOG.parent / "preflight" / f"{bad}-{BASE}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "secrets"), "FAIL", out)
        self.assertEqual(self.origin_main(), BASE)
        # A record of another harness stands in for nothing: the full checks run again.
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        record.update(harness_blob="0" * 40, sha=self.good_commit("Another line."))
        git(WORK, "push", "--quiet", "--no-verify", "origin",
            f"+{record['sha']}:refs/heads/{BRANCH}")
        (LOG.parent / "preflight" / f"{record['sha']}-{BASE}.json").write_text(json.dumps(record))
        r = self.merge("--dry-run")
        self.assertIn("is not of the full checks by origin/main's harness", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "body"), "FAIL", r.stdout)

    def test_record_never_stands_in_for_a_head_that_changes_the_checks(self):
        # CI runs a head's own copies of the checks, so only the pre-flight finds that
        # origin/main's fail on it: the merge does not let a record stand in for that.
        self.opened(**{"scripts/notes_check.py": "print('a new check')\n",
                       **self.decision("`scripts/notes_check.py` is added for the test.")})
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        r = self.merge("--dry-run")
        self.assertIn("so the full checks run again, not the record", r.stdout,
                      r.stdout + r.stderr)

    def test_record_never_stands_in_for_a_head_that_changes_the_workflow(self):
        self.opened(**{".github/workflows/ci.yml": self.text(".github/workflows/ci.yml")
                       + "# A comment for the test.\n",
                       **self.decision("`.github/workflows/ci.yml` is changed for the test.")})
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        r = self.merge("--dry-run")
        self.assertIn("so the full checks run again, not the record", r.stdout,
                      r.stdout + r.stderr)

    def test_bad_new_head_refused_at_the_merge(self):
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        bad = self.commit("Edit a Heath word by hand", {"heath/I/01.md": self.replaced(
            "heath/I/01.md", *Heath.WORD)})
        git(WORK, "push", "--quiet", "origin", f"{bad}:refs/heads/{BRANCH}")
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "heath/"), "FAIL", out)
        self.assertEqual(self.origin_main(), BASE)

    def test_protected_change_needs_its_label(self):
        path = "scripts/check_style.py"
        change = {path: self.text(path) + "\n# A comment for the test.\n"}
        change.update(self.decision(f"A comment in `{path}`, for the test."))
        self.opened(**change)
        (pr,) = self.gh_state()["prs"]
        self.assertIn("security-review", pr["labels"])
        self.assertIn(f"`{path}`", pr["body"])
        # Without the label, or with the security review's box unticked, no merge.
        self.set_gh(lambda s: s["prs"][0].update(labels=[], body=ticked(s["prs"][0]["body"])))
        out = self.merge().stdout
        self.assertIn("lacks the label security-review", out)
        self.set_gh(lambda s: s["prs"][0].update(
            labels=["security-review", "tooling"],
            body=s["prs"][0]["body"].replace("- [x] **Required if protected:**",
                                             "- [ ] **Required if protected:**")))
        out = self.merge().stdout
        self.assertIn("unticked: Required if protected:", out)
        self.assertEqual(self.origin_main(), BASE)
        self.set_gh(lambda s: s["prs"][0].update(body=s["prs"][0]["body"].replace(
            "- [ ] **Required if protected:**", "- [x] **Required if protected:**")))
        r = self.merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


    def test_ready_marks_the_open_draft_ready(self):
        self.opened(ready=False)
        self.good_commit("A second line, the fix.")
        r = self.safe_push("--ready")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.gh_state()["prs"][0]["isDraft"])

    def test_kind_label_needed(self):
        # Code review: a label for its kind, at the pre-flight (nothing pushed without
        # one) and at the merge.
        self.good_commit()
        out = self.assertRefused(self.safe_push("--branch", BRANCH, "--label", "stage-2"),
                                 "no label for its kind")
        self.assertNotIn("4. The full local checks", out, "the label is settled first")
        r = self.safe_push("--branch", BRANCH, "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.guard(r.stdout, "kind label"), "note", r.stdout)
        self.assertEqual(self.gh_state()["prs"], [], out)
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(labels=["stage-2"],
                                                 body=ticked(s["prs"][0]["body"])))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "kind label"), "FAIL", out)
        self.assertEqual(self.origin_main(), BASE)

    def test_sections_written_before_the_merge(self):
        # Code review: the template complete, not only its boxes ticked.
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=boxes_ticked(s["prs"][0]["body"])))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "sections"), "FAIL", out)
        for problem in ('not written: the section "What and why"',
                        "not written: the review /code-review",
                        "not written: the review /no-mistakes",
                        'not written: the section "Needs the owner\'s OK"'):
            self.assertIn(problem, out)
        self.assertNotIn("the review /security-review", out)   # nothing protected changes
        self.assertEqual(self.origin_main(), BASE)

    def test_gates_read_the_heads_template_while_main_has_none(self):
        # PR #1's own case: origin/main has no template yet, and the head brings it. The
        # gates read the head's, as the body was made from it: a box deleted and the
        # sections unwritten are refused.
        template = ".github/pull_request_template.md"
        text = self.text(template)
        git(WORK, "rm", "-q", "--", template)
        git(WORK, "commit", "-q", "-m", "A main without the template")
        main = git(WORK, "rev-parse", "HEAD").strip()
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{main}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        changes = {template: text}
        changes.update(self.decision(f"`{template}` comes back, for the test."))
        self.opened(**changes)
        drop = "- [ ] **Required:** Nothing public goes out without the owner's OK.\n"
        self.set_gh(lambda s: s["prs"][0].update(
            body=boxes_ticked(s["prs"][0]["body"].replace(drop, ""))))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "checklist"), "FAIL", out)
        self.assertIn("missing from the body: Required: Nothing public", out)
        self.assertEqual(self.guard(out, "sections"), "FAIL", out)
        self.assertIn('not written: the section "What and why"', out)
        self.assertEqual(self.origin_main(), main)
        self.assertEqual(self.merges(), [])

    def test_title_and_branch_name_scanned_before_the_merge(self):
        # Both go into main's merge commit for good: a title edited on GitHub, or a branch
        # pushed by hand, holding what the scan refuses, is refused at the merge.
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        saved = self.gh_state()["prs"][0]
        name = "secret" + "s2026-notes"
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{sha}:refs/heads/{name}")
        for change in ({"title": f"Notes from {PRIVATE_DIR}"}, {"headRefName": name}):
            with self.subTest(change=change):
                self.set_gh(lambda s: s["prs"][0].update(change))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "public names"), "FAIL", out)
                self.set_gh(lambda s: s["prs"].__setitem__(0, saved))
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_branch_renamed_meanwhile_refused(self):
        # The re-review: the merge commit's subject names the branch, so the gates refuse a
        # branch renamed on GitHub since the merge first read it, as a moved head is.
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        self.set_gh(lambda s: s.update(rename={"views": 1, "to": "renamed-branch"}))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("#1 changed meanwhile", out)
        self.assertIn("branch renamed-branch", out)
        self.assertEqual(self.origin_branch("renamed-branch"), sha, "the head moved too")
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_gh_failing_is_believed_only_if_nothing_merged(self):
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        env = clean_env()
        env["STOICHEIA_FAKE_GH_MERGE"] = "fail-before"
        r = self.safe_push("--merge", "1", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("nothing was merged (#1 is OPEN)", out)
        self.assertEqual(self.origin_main(), BASE)
        # gh fails after the merge (in deleting the branch): merged, and main checked.
        env["STOICHEIA_FAKE_GH_MERGE"] = "fail-after"
        r = self.safe_push("--merge", "1", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "gh pr merge"), "note", out)
        self.assertIn("but GitHub says #1 is merged", out)
        self.assertEqual(self.guard(out, "main"), "ok", out)
        self.assertEqual(self.guard(out, "branch"), "note", out)
        self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)

    def driven_merge(self, action: str, env=None) -> subprocess.CompletedProcess:
        """--merge 1 of the open pull request, its body completed, with DRIVER's `action`
        playing what GitHub or a signal does after the merge is asked of gh."""
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        return subprocess.run([sys.executable, "-c", DRIVER, str(UNDER_TEST), action, str(ORIGIN),
                               BASE, "--_test-skip-checks", "--merge", "1"], cwd=WORK,
                              env=env or clean_env(), capture_output=True, text=True)

    def test_interrupted_after_gh_exits_0_is_unknown(self):
        # The re-review made an interruption after gh's exit 0 exit 3, never exit 1. Since
        # issue #42, gh's exit 0 is no merge until GitHub says so, so an interruption while
        # GitHub is asked is exit 3 with the merge state unknown, not "merged".
        sha = self.opened()
        r = self.driven_merge("merge-view-interrupt")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("Interrupted once `gh pr merge` was run: the merge may have happened",
                      out)
        self.assertNotIn("; merged", out)
        self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)
        self.assertIn("merge state unknown (interrupted", LOG.read_text().splitlines()[-1])

    def test_gh_exiting_0_github_unasked_is_unknown(self):
        # Issue #42: gh exits 0, and GitHub cannot be asked whether the pull request merged.
        # gh's exit 0 alone is no merge, so the merge state is unknown, exit 3, though here
        # it did merge; the run says to look before anything else.
        sha = self.opened()
        r = self.driven_merge("merge-view-fail")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertEqual(self.guard(out, "gh pr merge"), "FAIL", out)
        self.assertIn("The merge may have happened: `gh pr merge` exited 0, and GitHub could "
                      "not be asked whether #1 merged", out)
        self.assertNotIn("REFUSED", out)
        self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)
        self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_github_giving_no_state_is_unknown(self):
        # Issue #42: after gh failed, GitHub answers with no state for the pull request.
        # That says nothing of the merge, so it is no "nothing was merged", exit 1: the
        # merge state is unknown, exit 3.
        self.opened()
        env = clean_env()
        env["STOICHEIA_FAKE_GH_MERGE"] = "fail-before"
        r = self.driven_merge("merge-view-empty", env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("`gh pr merge` failed, and GitHub could not be asked whether #1 merged "
                      "(it gave no state for #1)", out)
        self.assertNotIn("nothing was merged", out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_github_giving_a_state_of_no_pull_request_is_unknown(self):
        # The review of 19 October: gh fails after merging, and GitHub answers with a state
        # that is none of OPEN, CLOSED and MERGED. That says nothing of the merge, so it is
        # no "nothing was merged", exit 1: the merge state is unknown, exit 3.
        for answer in ('{"state": true}', '{"state": "SQUASHED"}', '[]'):
            with self.subTest(answer=answer):
                self.setUp()
                sha = self.opened()
                env = clean_env()
                env["STOICHEIA_FAKE_GH_MERGE"] = "fail-after"
                r = self.driven_merge(f"merge-view-json:{answer}", env)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertIn("`gh pr merge` failed, and GitHub could not be asked whether #1 "
                              "merged", out)
                self.assertNotIn("nothing was merged", out)
                self.assertNotIn("Traceback", out)
                self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)
                self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_merge_commit_github_names_by_no_full_object_name_is_unknown(self):
        # The review of 19 October: GitHub says merged, and names its merge commit by
        # something that is no full object name. Nothing on main is known to be the merge,
        # so the merge state is unknown, exit 3, with no revert advised, and nothing is
        # fetched or judged as the merge first: never a traceback, never "merged".
        for commit in ('{"oid": 123}', '"abc"', '{"oid": "abc123"}', '{"oid": null}'):
            with self.subTest(commit=commit):
                self.setUp()
                sha = self.opened()
                r = self.driven_merge(
                    'merge-view-json:{"state": "MERGED", "mergeCommit": %s}' % commit)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertEqual(self.guard(out, "main"), "FAIL", out)
                self.assertIn("The merge state is unknown: GitHub says #1 is merged, but it "
                              "names no merge commit", out)
                self.assertNotIn("Traceback", out)
                self.assertNotIn("git revert", out)
                self.assertNotIn("Merged, but", out)
                self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)
                self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_gh_exiting_0_without_merging_is_unknown(self):
        # Issue #42: with a merge queue or auto-merge on, `gh pr merge` exits 0 having only
        # queued the pull request. GitHub says it is still open, so the merge state is
        # unknown, exit 3, and no revert is advised: it would name origin/main's last
        # commit, which is not this merge.
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        env = clean_env()
        env["STOICHEIA_FAKE_GH_MERGE"] = "queue"
        r = self.safe_push("--merge", "1", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertEqual(self.guard(out, "gh pr merge"), "FAIL", out)
        self.assertIn("The merge state is unknown: `gh pr merge` exited 0, but GitHub says #1 "
                      "is OPEN, not merged", out)
        self.assertIn("will be added to the merge queue", out)
        self.assertIsNone(self.step(out, "main"), out)
        self.assertNotIn("git revert", out)
        self.assertNotIn("REFUSED", out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(self.origin_branch(), sha)
        self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_merge_commit_github_names_must_be_on_main(self):
        # Issue #42: GitHub says merged, but names no merge commit, or one origin/main does
        # not hold. Nothing on main is known to be this merge, so the merge state is
        # unknown, exit 3, and no revert is advised, for it would name origin/main's last
        # commit in place of the merge. A merge commit main does not hold is refused
        # whether or not a fetch brings it: on a merge queue's branch, say, it is a merge
        # of the base and the head with the head's tree, and only main's history tells.
        queued = "refs/heads/gh-readonly-queue/main/pr-1"
        off = "as its merge commit, which origin/main ("
        for how, why in (("off-main", off), (f"off-main:{queued}", off),
                         ("no-commit", "names no merge commit")):
            with self.subTest(how=how):
                self.setUp()
                self.opened()
                self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
                env = clean_env()
                env["STOICHEIA_FAKE_GH_MERGE"] = how
                r = self.safe_push("--merge", "1", env=env)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertEqual(self.guard(out, "gh pr merge"), "ok", out)
                self.assertEqual(self.guard(out, "main"), "FAIL", out)
                self.assertIn("The merge state is unknown: GitHub says #1 is merged, but it "
                              "names ", out)
                self.assertIn(why, out)
                self.assertNotIn("git revert", out)
                self.assertNotIn("Merged, but", out)
                self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])
                if how.startswith("off-main:"):
                    oid = self.gh_state()["prs"][0]["mergeCommit"]["oid"]
                    self.assertEqual(git(WORK, "cat-file", "-t", oid).strip(), "commit",
                                     "the fetch did not bring the merge commit GitHub names")

    def test_merge_github_cannot_be_asked_about_is_unknown(self):
        # gh fails after merging, and GitHub cannot be asked: the merge may have happened,
        # exit 3, never "refused" with exit 1, which says nothing merged.
        sha = self.opened()
        env = clean_env()
        env["STOICHEIA_FAKE_GH_MERGE"] = "fail-after"
        r = self.driven_merge("merge-view-fail", env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("The merge may have happened: `gh pr merge` failed, and GitHub could "
                      "not be asked whether #1 merged", out)
        self.assertNotIn("REFUSED", out)
        self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)
        self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_interrupted_while_gh_merges_is_unknown(self):
        # An interruption once gh has been asked to merge, before it is known whether it
        # did: the merge may have happened, exit 3.
        sha = self.opened()
        r = self.driven_merge("merge-interrupt")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("the merge may have happened", out)
        self.assertEqual(git(ORIGIN, "rev-parse", "refs/heads/main^2").strip(), sha)
        self.assertIn("merge state unknown", LOG.read_text().splitlines()[-1])

    def test_failed_fetch_after_the_merge_is_not_success(self):
        # Origin stops answering right after the merge: main is not checked, and the run
        # says so (exit 3) rather than judging a stale origin/main.
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        flag = TMP / "merged"
        flag.unlink(missing_ok=True)
        self.addCleanup(lambda: flag.unlink(missing_ok=True))
        bindir = Path(tempfile.mkdtemp(prefix="bin-", dir=TMP))
        (bindir / "git").write_text(
            '#!/bin/sh\nfor a in "$@"; do\n'
            f'    if [ "$a" = fetch ] && [ -e "{flag}" ]; then\n'
            '        echo "fatal: unable to access origin: Connection reset" >&2\n'
            '        exit 128\n    fi\ndone\n'
            f'exec "{shutil.which("git")}" "$@"\n')
        (bindir / "git").chmod(0o755)
        env = clean_env()
        env["PATH"] = f"{bindir}{os.pathsep}{env['PATH']}"
        env["STOICHEIA_FAKE_GH_MERGE"] = f"flag:{flag}"
        r = self.safe_push("--merge", "1", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertEqual(self.guard(out, "main"), "FAIL", out)
        self.assertIn("not checked: `git fetch origin` failed", out)
        self.assertIn("main could not be checked", out)
        self.assertNotIn("git revert", out)

    def test_main_moving_after_the_gates_refused(self):
        # --match-head-commit pins the head, not the base: origin/main moving after the
        # gates, before `gh pr merge`, is refused, and gh is never asked to merge.
        side = self.side_commit()
        self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        r = subprocess.run([sys.executable, "-c", DRIVER, str(UNDER_TEST), "move-at-merge",
                            str(ORIGIN), side, "--_test-skip-checks", "--merge", "1"],
                           cwd=WORK, env=clean_env(), capture_output=True, text=True)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("origin/main moved", out)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), side)
        self.assertIsNotNone(self.origin_branch())

    def test_main_moving_under_the_merge_advises_a_revert(self):
        # Another merge lands between the last look at main and GitHub's merge: the merge
        # commit does not join the base checked, so the run says how to revert it.
        side = self.side_commit()
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        env = clean_env()
        env["STOICHEIA_FAKE_GH_MERGE"] = f"main-first:{side}"
        r = self.safe_push("--merge", "1", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertEqual(self.guard(out, "main"), "FAIL", out)
        self.assertIn("Merged, but main is not what was checked", out)
        merge = self.origin_main()
        self.assertEqual(git(ORIGIN, "rev-list", "--parents", "-n", "1", merge).split()[1:],
                         [side, sha])
        self.assertIn(f"git revert --no-commit -m 1 {merge}", out)
        self.assertIn("git restore --source=origin/main --staged --worktree -- docs/decisions/ "
                      f"{DECISIONS}", out)
        self.assertIn(f"git safe-push --branch revert-{merge[:12]} --label docs", out)

    def test_merge_refuses_a_pull_request_it_may_not_merge(self):
        sha = self.opened()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        saved = self.gh_state()["prs"][0]
        onto = "does not propose a branch of origin onto main"
        for change, why in (({"state": "CLOSED"}, "is not open"),
                            ({"state": "MERGED"}, "is not open"),
                            ({"baseRefName": "next"}, onto),
                            # a fork's head, here as after `gh pr checkout <n>`
                            ({"isCrossRepository": True, "forkHead": sha,
                              "headRepositoryOwner": {"login": "stranger"}}, onto)):
            with self.subTest(change=change):
                self.set_gh(lambda s: s["prs"][0].update(change))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn(why, out)
                self.set_gh(lambda s: s["prs"].__setitem__(0, saved))
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_step_4_notes_reach_the_merge(self):
        # When the pre-flight's record stands in for step 4 at the merge, its step-4 notes
        # (a check that failed with origin/main's copies) are shown beside the checklist.
        sha = self.opened_r3()
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        path = LOG.parent / "preflight" / f"{sha}-{BASE}.json"
        record = json.loads(path.read_text())
        note = ["python3 scripts/check_links.py (origin/main's checks)", "full output in a log"]
        record["notes"].append(note)
        path.write_text(json.dumps(record))
        r = self.merge("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("the full checks are not repeated", out)
        self.assertEqual(self.guard(out, "pre-flight notes"), "note", out)
        self.assertIn(f"{note[0]}: {note[1]}", out[out.index("pre-flight notes"):])

    def test_rerun_takes_the_kind_from_the_open_pull_request(self):
        # The documented re-run after a fix, `--branch <name>` with no --label.
        self.opened(ready=False)
        second = self.good_commit("A second line, the fix.")
        r = self.safe_push("--branch", BRANCH)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "kind label"), "ok", out)
        self.assertIn("kind label: on #1", out)
        self.assertIn("#1 updated", out)
        self.assertEqual(self.origin_branch(), second)
        # With no label for its kind on the open one, the re-run is refused before the push.
        self.set_gh(lambda s: s["prs"][0].update(labels=["stage-2"]))
        self.good_commit("A third line.")
        r = self.safe_push("--branch", BRANCH)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("the pull request has no label for its kind", out)
        self.assertEqual(self.origin_branch(), second)


# --------------------------------------------------------------------------------------
# B: the review's findings, each with a planted commit


class Trains(Edge):
    """The train checker is main's public function, including through a hand-over."""

    def body_file(self) -> Path:
        path = TMP / "train-body.md"
        path.write_text("A train body for the test.\n")
        return path

    def without_checker(self) -> str:
        base = self.commit("Main before the train checker", remove=("scripts/check_train.py",))
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{base}:refs/heads/main")
        return base

    def test_train_requires_body_file(self):
        self.good_commit()
        for branch in ("train/tooling-1", "refs/heads/train/tooling-1"):
            with self.subTest(branch=branch):
                r = self.safe_push("--branch", branch, "--label", "tooling")
                self.assertRefused(r, "a train/* branch requires --body-file")
                self.assertIsNone(self.origin_branch("train/tooling-1"))

    def test_main_without_train_module_refuses(self):
        if safe_push.show_bytes(WORK, BASE, "scripts/check_train.py") is not None:
            base = self.commit("Main before the train checker", remove=("scripts/check_train.py",))
            git(WORK, "push", "--quiet", "--no-verify", "origin", f"{base}:refs/heads/main")
        self.good_commit()
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(self.body_file()), "--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.step(out, "train"), "FAIL")
        self.assertIn("origin/main has no scripts/check_train.py", out)
        self.assertIsNone(self.origin_branch("train/docs-1"))

    def test_train_adding_its_own_checker_is_refused_while_main_has_none(self):
        # No bootstrap: a commit's own check_train.py never judges the commit.
        base = self.without_checker()
        self.commit("Introduce the train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return []\n",
            **self.decision("scripts/check_train.py: the train checker is introduced.")})
        r = self.safe_push("--branch", "train/tooling-1", "--label", "tooling",
                           "--body-file", str(self.body_file()))
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.step(out, "train"), "FAIL", out)
        self.assertIn("origin/main has no scripts/check_train.py, so no train can be "
                      "checked", out)
        self.assertNotIn("bootstrap", out)
        self.assertNotIn("4. The full local checks", out)
        self.assertIsNone(self.origin_branch("train/tooling-1"))
        self.assertEqual(self.origin_main(), base)

    def test_main_checker_refusal_exception_and_early_exit_refuse(self):
        cases = (("return ['planted refusal']", "planted refusal"),
                 ("return None", "unreadable problem list"),
                 ("raise RuntimeError('broken checker')", "broken checker"),
                 ("raise SystemExit(0)", "train check refused"))
        for statement, message in cases:
            with self.subTest(statement=statement):
                self.setUp()
                base = self.new_base("Main's train checker", {
                    "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                              f"    {statement}\n"})
                self.good_commit()
                r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                                   "--body-file", str(self.body_file()))
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.step(out, "train"), "FAIL", out)
                self.assertIn(message, out)
                self.assertNotIn("4. The full local checks", out)
                self.assertEqual(self.origin_main(), base)
                self.assertIsNone(self.origin_branch("train/docs-1"))

    def test_merge_checks_current_train_body_in_both_modes_with_or_without_record(self):
        for queued in (False, True):
            for cached in (False, True):
                with self.subTest(queued=queued, cached=cached):
                    self.setUp()
                    base = self.new_base("Main's train checker", {
                        "scripts/check_train.py":
                            "def check_train(repo, base, sha, body):\n"
                            "    return [] if 'Good train body.' in body else ['bad body']\n"})
                    sha = self.good_commit()
                    body = self.body_file()
                    body.write_text(self.text(safe_push.TEMPLATE) + "\nGood train body.\n")
                    r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                                       "--body-file", str(body), "--ready")
                    self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                    self.set_gh(lambda s: s["prs"][0].update(
                        body=ticked(s["prs"][0]["body"]).replace("Good train body.", "Bad.")))
                    self.set_gh(lambda s: s.update(
                        rules=[[{"type": "merge_queue"}]] if queued else [[]]))
                    if not cached:
                        (LOG.parent / "preflight" / f"{sha}-{base}.json").unlink()
                    r = self.safe_push("--merge", "1")
                    out = r.stdout + r.stderr
                    self.assertEqual(r.returncode, 1, out)
                    self.assertEqual(self.step(out, "train"), "FAIL", out)
                    self.assertIn("bad body", out)
                    self.assertEqual(self.origin_main(), base)
                    self.assertEqual(self.merges(), [])
                    self.assertFalse(any("enqueuePullRequest" in arg
                                         for call in self.gh_state()["calls"] for arg in call))

    def test_renamed_train_without_checker_is_refused_at_merge(self):
        base = self.without_checker()
        sha = self.good_commit()
        r = self.safe_push("--ready")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        git(ORIGIN, "update-ref", "refs/heads/train/docs-1", sha)
        self.set_gh(lambda s: s["prs"][0].update(
            headRefName="train/docs-1", body=ticked(s["prs"][0]["body"])))
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.set_gh(lambda s: s.update(
                    rules=[[{"type": "merge_queue"}]] if queued else [[]]))
                r = self.safe_push("--merge", "1")
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.step(out, "train"), "FAIL", out)
                self.assertIn("origin/main has no scripts/check_train.py", out)
                self.assertEqual(self.origin_main(), base)
                self.assertEqual(self.merges(), [])

    def test_renamed_train_adding_its_own_checker_is_refused_at_merge_in_both_modes(self):
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.setUp()
                base = self.without_checker()
                sha = self.commit("Introduce the train checker", {
                    "scripts/check_train.py":
                        "def check_train(repo, base, sha, body):\n"
                        "    return []\n",
                    **self.decision("scripts/check_train.py: the new checker.")})
                body = self.body_file()
                body.write_text(self.text(safe_push.TEMPLATE) + "\nGood train body.\n")
                r = self.safe_push("--label", "tooling", "--body-file", str(body), "--ready")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                git(ORIGIN, "update-ref", "refs/heads/train/tooling-1", sha)
                self.set_gh(lambda s: s["prs"][0].update(
                    headRefName="train/tooling-1", body=ticked(s["prs"][0]["body"])))
                self.set_gh(lambda s: s.update(
                    rules=[[{"type": "merge_queue"}]] if queued else [[]]))
                r = self.safe_push("--merge", "1")
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.step(out, "train"), "FAIL", out)
                self.assertIn("origin/main has no scripts/check_train.py", out)
                self.assertEqual(self.origin_main(), base)
                self.assertEqual(self.merges(), [])

    def test_renamed_train_needs_a_summary_with_its_train_step_in_both_modes(self):
        # A branch renamed train/ after its pre-flight has a summary with no train step:
        # --merge, which never writes the body, refuses it as out of date, so the record
        # of the merge shows the train check that a fresh pre-flight runs.
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.setUp()
                base = self.new_base("Main's train checker", {
                    "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                              "    return []\n"})
                sha = self.good_commit()
                r = self.safe_push("--ready")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertNotIn("| 3. train |", self.gh_state()["prs"][0]["body"])
                git(ORIGIN, "update-ref", "refs/heads/train/docs-1", sha)
                self.set_gh(lambda s: s["prs"][0].update(
                    headRefName="train/docs-1", body=ticked(s["prs"][0]["body"])))
                self.set_gh(lambda s: s.update(
                    rules=[[{"type": "merge_queue"}]] if queued else [[]]))
                r = self.safe_push("--merge", "1")
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.step(out, "train"), "ok", out)
                self.assertEqual(self.guard(out, "body"), "FAIL", out)
                self.assertIn("run `git safe-push --branch train/docs-1`", out)
                self.assertEqual(self.origin_main(), base)
                self.assertEqual(self.merges(), [])
                self.assertFalse(any("enqueuePullRequest" in arg
                                     for call in self.gh_state()["calls"] for arg in call))

    def test_unreadable_main_train_module_refuses(self):
        # origin/main's check_train.py as a link is not a regular file: the harness,
        # which compares it, refuses before anything runs.
        (WORK / "scripts/check_train.py").unlink()
        os.symlink("safe_push.py", WORK / "scripts/check_train.py")
        git(WORK, "add", "--", "scripts/check_train.py")
        base = self.commit("Main's train module as a link")
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{base}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        self.good_commit()
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(self.body_file()), "--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("origin/main's scripts/check_train.py is not a regular file", out)
        self.assertEqual(self.origin_main(), base)

    def test_only_a_different_train_module_hands_over(self):
        base = self.new_base("Main's train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return ['main checker ran']\n"})
        self.good_commit()
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(self.body_file()), "--dry-run")
        out = r.stdout + r.stderr
        self.assertIn("safe_push.py, heath.py or check_train.py differs from origin/main's: "
                      "running origin/main's in its place", out)
        self.assertEqual(self.step(out, "harness"), "ok", out)
        self.assertEqual(self.step(out, "train"), "FAIL", out)
        self.assertIn("main checker ran", out)
        self.assertEqual(self.origin_main(), base)

    def test_harness_variable_checks_the_train_module_too(self):
        self.new_base("Main's train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return []\n"})
        self.good_commit()
        env = clean_env()
        env["STOICHEIA_HARNESS"] = "origin/main"
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(self.body_file()), "--dry-run", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("copy of safe_push.py, heath.py or check_train.py is not "
                      "origin/main's", out)

    def test_unreadable_body_file_refuses_before_the_checks(self):
        self.new_base("Main's train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return []\n"})
        self.good_commit()
        body = self.body_file()
        body.write_bytes(b"Not UTF-8: \xff\n")
        for branch in ("train/docs-1", "docs/body"):
            with self.subTest(branch=branch):
                r = self.safe_push("--branch", branch, "--label", "docs",
                                   "--body-file", str(body))
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("could not read --body-file", out)
                self.assertNotIn("4. The full local checks", out)
                self.assertIsNone(self.origin_branch(branch))

    GOOD_BODY_CHECKER = ("def check_train(repo, base, sha, body):\n"
                         "    return [] if 'Good train body.' in body else ['bad body']\n")

    def opened_train(self) -> str:
        """An open, ready train pull request whose body main's checker accepts."""
        base = self.new_base("Main's train checker",
                             {"scripts/check_train.py": self.GOOD_BODY_CHECKER})
        self.good_commit()
        body = self.body_file()
        body.write_text(self.text(safe_push.TEMPLATE) + "\nGood train body.\n")
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(body), "--ready")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        return base

    def assertMergeRefusedForChangedBody(self, r, base: str) -> None:
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.step(out, "train"), "ok", out)
        self.assertIn("the train's body changed during the checks: run --merge again", out)
        self.assertEqual(self.origin_main(), base)
        self.assertEqual(self.merges(), [])

    def test_body_edited_during_the_merge_checks_refuses(self):
        # The gates' read after the checks sees an edit made while the train check ran.
        # The driven harness carries main's train module, so that it is origin/main's
        # and runs in place, with the driver's stand-ins, rather than handing over.
        base = self.opened_train()
        harness = TMP / "harness-with-train"
        harness.mkdir(exist_ok=True)
        for name in ("safe_push.py", "heath.py"):
            shutil.copy2(UNDER_TEST / name, harness / name)
        (harness / "check_train.py").write_text(self.GOOD_BODY_CHECKER)
        r = subprocess.run([sys.executable, "-c", DRIVER, str(harness), "edit-train-body",
                            str(ORIGIN), "", "--_test-skip-checks", "--merge", "1"],
                           cwd=WORK, env=clean_env(), capture_output=True, text=True)
        self.assertNotIn("running origin/main's in its place", r.stdout + r.stderr)
        self.assertMergeRefusedForChangedBody(r, base)

    def test_body_edited_before_the_merge_s_own_read_refuses(self):
        base = self.opened_train()
        self.set_gh(lambda s: s.update(reread_body=s["prs"][0]["body"] + "\nAn edit.\n"))
        self.assertMergeRefusedForChangedBody(self.safe_push("--merge", "1"), base)

    def test_body_edited_before_the_final_gates_refuses(self):
        base = self.opened_train()
        self.set_gh(lambda s: s.update(after_body={"prs": [
            dict(s["prs"][0], body=s["prs"][0]["body"] + "\nAn edit.\n")]}))
        self.assertMergeRefusedForChangedBody(self.safe_push("--merge", "1"), base)

    def test_origin_train_failure_refuses_even_if_candidate_passes(self):
        base = self.new_base("Main's train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return ['planted train refusal']\n"})
        self.commit("A candidate checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return []\n",
            **self.decision("scripts/check_train.py: the proposed checker.")})
        r = self.safe_push("--branch", "train/tooling-1", "--label", "tooling",
                           "--body-file", str(self.body_file()))
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.step(out, "train"), "FAIL")
        self.assertIn("planted train refusal", out)
        self.assertEqual(self.origin_main(), base)
        self.assertIsNone(self.origin_branch("train/tooling-1"))
        self.assertNotIn("4. The full local checks", out)

    def test_main_train_function_receives_the_checked_commit_and_body(self):
        base = self.new_base("Main's train checker", {
            "scripts/check_train.py":
                "from pathlib import Path\n"
                "def check_train(repo, base, sha, body):\n"
                "    if not isinstance(repo, Path) or len(base) != 40 or len(sha) != 40:\n"
                "        return ['wrong train arguments']\n"
                "    if body != 'A train body for the test.\\n':\n"
                "        return ['wrong train body']\n"
                "    return []\n"})
        sha = self.good_commit()
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(self.body_file()))
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.step(out, "train"), "ok")
        self.assertEqual(self.origin_main(), base)
        self.assertEqual(self.origin_branch("train/docs-1"), sha)

    def test_unreadable_train_result_refuses(self):
        base = self.new_base("An unreadable train checker result", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return None\n"})
        self.good_commit()
        r = self.safe_push("--branch", "train/docs-1", "--label", "docs",
                           "--body-file", str(self.body_file()), "--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("unreadable problem list", out)
        self.assertEqual(self.origin_main(), base)

    def test_changed_body_is_checked_again_before_push(self):
        base = self.new_base("Main's train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return [] if body == 'Good.\\n' else ['bad body']\n"})
        sha = self.good_commit()
        body = self.body_file()
        body.write_text("Good.\n")
        args = ("--branch", "train/docs-1", "--label", "docs", "--body-file", str(body))
        r = self.safe_push(*args, "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        path = LOG.parent / "preflight" / f"{sha}-{base}.json"
        self.assertTrue(path.is_file())
        body.write_text("Bad.\n")
        r = self.safe_push(*args)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.step(out, "train"), "FAIL", out)
        self.assertIn("bad body", out)
        self.assertNotIn("4. The full local checks", out)
        self.assertIsNone(self.origin_branch("train/docs-1"))
        self.assertEqual(self.origin_main(), base)

    def test_a_flagged_train_runs_uncached_and_still_checks_its_train(self):
        # #224 after #383: with --main-checks-cache, a train/* branch, however written,
        # gets no cache and no sandbox, since its train check loads main's check_train.py
        # into the harness after the commit's code has run; the train check still runs,
        # in a process with no sandbox and no cache.
        marker = TMP / "flagged-train.txt"
        checker = ("import sys\n"
                   "def check_train(repo, base, sha, body):\n"
                   "    m = sys.modules['__main__']\n"
                   f"    open({str(marker)!r}, 'a').write(repr((m.SANDBOX, m.CACHE)) + '\\n')\n"
                   "    return []\n")
        for branch in ("train/tooling-1", "refs/heads/train/tooling-1"):
            with self.subTest(branch=branch):
                self.setUp()
                marker.unlink(missing_ok=True)
                self.new_base("Main's train checker", {"scripts/check_train.py": checker})
                path = "scripts/check_links.py"
                change = {path: self.text(path) + "\n# A comment for the test.\n"}
                change.update(self.decision(f"A comment in `{path}`, for the test."))
                self.commit("A comment in a check", change)
                # The log's directory resolved: dir_problem refuses a symlink above it.
                root = Path(os.path.realpath(tempfile.mkdtemp(prefix="flagged-train-",
                                                              dir=TMP)))
                env = clean_env()
                env["STOICHEIA_PUSH_LOG"] = str(root / "pushes.log")
                r = self.safe_push("--branch", branch, "--label", "tooling", "--body-file",
                                   str(self.body_file()), "--dry-run", "--main-checks-cache",
                                   env=env)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 0, out)
                self.assertEqual(self.step(out, "main-checks cache"), "note", out)
                self.assertIn("a train/* branch's train check", out)
                self.assertEqual(self.guard(out, "train"), "ok", out)
                self.assertEqual(marker.read_text(), "(None, None)\n", out)
                self.assertFalse((root / "main-checks").exists(), out)


class Queue(Edge):
    """A stand-in queue, with no network and a deterministic clock for the timeout."""

    def opened(self, queued=True) -> str:
        sha = self.good_commit()
        r = self.safe_push("--ready")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        self.set_gh(lambda s: s.update(rules=[[{"type": "merge_queue"}]] if queued else [[]]))
        return sha

    def enqueues(self) -> list[list[str]]:
        return [c for c in self.gh_state()["calls"] if c[:2] == ["api", "graphql"]
                and any("enqueuePullRequest" in arg for arg in c)]

    def run_entry(self, outcome="merged") -> subprocess.CompletedProcess:
        self.set_gh(lambda s: s.update(queue_result=outcome))
        env = dict(clean_env(), STOICHEIA_TEST_CLOCK="leap")
        return subprocess.run([sys.executable, "-c", DRIVER, str(UNDER_TEST), "queue",
                               str(ORIGIN), "", "--_test-skip-checks", "--merge", "1"],
                              cwd=WORK, env=env, capture_output=True, text=True)

    def assertNoLanding(self, r, *messages):
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        for message in messages:
            self.assertIn(message, out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.enqueues(), [])

    def test_queue_pins_head_and_reports_verified_merge(self):
        sha = self.opened()
        r = self.run_entry()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("merged #1", out)
        self.assertEqual(self.merges(), [])
        self.assertEqual(len(self.enqueues()), 1)
        self.assertIn(f"head={sha}", self.enqueues()[0])
        self.assertTrue(any("expectedHeadOid:$head" in a for a in self.enqueues()[0]))
        self.assertEqual(git(ORIGIN, "rev-parse", "main^2").strip(), sha)
        self.assertEqual(self.guard(out, "main"), "ok")

    def test_queue_checks_a_head_behind_main_against_its_merge_base(self):
        sha = self.opened()
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        main = self.new_base("Main advanced", {"docs/queue-test.md": "Another change.\n"})
        r = self.run_entry()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        # The pre-flight's record of this head and base stands in: for this R0 head, one
        # that left the full checks to CI (#329); either kind makes the step "ok".
        self.assertEqual(self.guard(out, "pre-flight"), "ok", out)
        self.assertIn(f"{sha[:12]} checked against origin/main {BASE[:12]} (", out)
        self.assertEqual(git(ORIGIN, "rev-list", "--parents", "-n", "1", "main").split()[1:],
                         [main, sha])
        self.assertNotEqual(git(ORIGIN, "rev-parse", "main^{tree}").strip(),
                            git(ORIGIN, "rev-parse", f"{sha}^{{tree}}").strip())
        # --merge never writes the body: the pre-flight's block of this head and base stays,
        # by a harness that was main, which the queue's judge accepts too.
        self.assertIn(f"sha={sha} base={BASE} harness={BASE} -->",
                      self.gh_state()["prs"][0]["body"])
        self.assertNotIn(main, self.gh_state()["prs"][0]["body"])

    def test_queue_checks_against_main_s_chain_when_a_member_merged_first(self):
        # A member of the head merged on its own before it, so the head's merge base with
        # main is that member, off main's first-parent chain. The merge compares against
        # the newest commit of the chain that the head contains, the pre-flight's base and
        # the judge's, so the pre-flight's record of that base stands in.
        member = self.commit("A member merged on its own", {
            "docs/queue-member.md": "A member's change.\n"})
        sha = self.opened()
        tree = git(WORK, "merge-tree", "--write-tree", BASE, member).splitlines()[0]
        main = git(WORK, "commit-tree", tree, "-p", BASE, "-p", member, "-m",
                   "Merge pull request #5 from owner/member").strip()
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{main}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        self.assertEqual(git(WORK, "merge-base", "--all", sha, main).split(), [member])
        r = self.run_entry()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn(f"2 commits onto origin/main {BASE[:12]}", out)
        self.assertIn(f"{sha[:12]} checked against origin/main {BASE[:12]}", out)
        # The record stands in, for this R0 head one that left the full checks to CI (#329).
        self.assertEqual(self.guard(out, "pre-flight"), "ok", out)
        self.assertEqual(git(ORIGIN, "rev-list", "--parents", "-n", "1", "main").split()[1:],
                         [main, sha])
        self.assertIn(f"sha={sha} base={BASE} harness={BASE} -->",
                      self.gh_state()["prs"][0]["body"])

    def test_queue_compares_the_installed_hook_with_current_main(self):
        # A queued head is checked against an older main, but the installed hook and
        # launcher are compared with current main's copies.
        self.opened()
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        hook = "scripts/hooks/pre-push"
        self.new_base("Main's hook gains a line", {
            hook: self.text(hook) + "\n# A later hook revision for the test.\n"})
        r = self.safe_push("--merge", "1", "--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(self.guard(out, "pre-push hook"), "note", out)
        self.assertIn("differs from origin/main's scripts/hooks/pre-push", out)

    def test_queue_reads_main_s_current_template(self):
        # In queue mode the head is judged against its merge base, but the template in
        # force is current main's: a required box main added since binds the merge.
        self.opened()
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        template = ".github/pull_request_template.md"
        self.new_base("Main's template gains a box", {
            template: self.text(template)
            + "- [ ] **Required:** A box main added after the branch.\n"})
        r = self.run_entry()
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        self.assertIn("A box main added after the branch", out)
        self.assertEqual(self.enqueues(), [])

    def test_queue_records_new_harness_separately_from_merge_base(self):
        sha = self.opened()
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        main = self.new_base("Main's harness advanced", {
            "scripts/safe_push.py": self.text("scripts/safe_push.py") +
                                    "\n# A later harness revision for the test.\n"})
        r = self.safe_push("--merge", "1")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("is not of the full checks by origin/main's harness", out)
        self.assertEqual(len(self.enqueues()), 1)
        record = json.loads((LOG.parent / "preflight" / f"{sha}-{BASE}.json").read_text())
        self.assertEqual(record["base"], BASE)
        self.assertEqual(record["harness_sha"], main)
        blob = git(WORK, "rev-parse", f"{main}:scripts/safe_push.py").strip()
        self.assertEqual(record["harness_blob"], blob)
        # --merge never writes the body: the pre-flight's block, by the harness that was
        # main then, stays; the queue's judge reads that harness's checks.
        body = self.gh_state()["prs"][0]["body"]
        self.assertIn(f"sha={sha} base={BASE} harness={BASE} -->", body)
        old_blob = git(WORK, "rev-parse", f"{BASE}:scripts/safe_push.py").strip()
        self.assertIn(f"origin/main's `scripts/safe_push.py` (blob `{old_blob[:12]}`)", body)
        self.assertEqual(body.count("safe_push:preflight begin"), 1)
        self.assertEqual(git(ORIGIN, "rev-parse", "main^2").strip(), sha)

    def test_queue_train_uses_main_checker_after_its_merge_base(self):
        # A renamed branch had its pre-flight before main acquired the new checker.
        sha = self.opened()
        git(WORK, "checkout", "--quiet", "--detach", BASE)
        main = self.new_base("Main's later train checker", {
            "scripts/check_train.py": "def check_train(repo, base, sha, body):\n"
                                      "    return ['later main checker refused']\n"})
        git(ORIGIN, "update-ref", "refs/heads/train/docs-1", sha)
        self.set_gh(lambda s: s["prs"][0].update(headRefName="train/docs-1"))
        r = self.safe_push("--merge", "1")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("later main checker refused", out)
        self.assertEqual(self.step(out, "train"), "FAIL", out)
        self.assertEqual(self.enqueues(), [])
        self.assertEqual(self.origin_main(), main)

    def test_queue_dry_run_does_not_enqueue(self):
        self.opened()
        r = self.safe_push("--merge", "1", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would enqueue", r.stdout)
        self.assertEqual(self.enqueues(), [])
        self.assertEqual(self.origin_main(), BASE)

    def test_ejected_reports_group_checks(self):
        self.opened()
        r = self.run_entry("ejected")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("ejected #1", out)
        self.assertIn("queue-integrity: failure", out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(len(self.enqueues()), 1)

    def test_timeout_is_exit_3(self):
        self.opened()
        r = self.run_entry("waiting")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("queued; verdict not followed", out)
        self.assertIn("timed out", out)
        self.assertEqual(self.origin_main(), BASE)

    def test_unreadable_verdict_is_exit_3(self):
        self.opened()
        r = self.run_entry("unknown")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 3, out)
        self.assertIn("queued; verdict not followed", out)
        self.assertNotIn("git revert", out)

    def test_named_merge_must_be_on_main_with_the_head_as_second_parent(self):
        for outcome, why in (
                ("wrong-parent", "does not have the checked head as second parent"),
                ("off-main", "origin/main does not hold the merge commit GitHub names for #1"),
                ("no-commit", "GitHub names no full merge commit for queued #1")):
            with self.subTest(outcome=outcome):
                self.setUp()
                self.opened()
                r = self.run_entry(outcome)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertIn("queued; verdict not followed", out)
                self.assertIn(why, out)
                self.assertNotIn("git revert", out)

    def test_queue_off_keeps_direct_merge(self):
        sha = self.opened(queued=False)
        r = self.safe_push("--merge", "1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(self.merges()), 1)
        self.assertEqual(self.enqueues(), [])
        self.assertEqual(git(ORIGIN, "rev-parse", "main^2").strip(), sha)
        self.assertIsNone(self.origin_branch())

    def test_unreadable_rules_refuse(self):
        self.opened()
        pages = "unreadable main rules: expected pages of entries"
        typed = "unreadable main rules: each rule must name its type"
        for rules, why in ((None, "did not give a readable JSON answer"), ([], pages),
                           ({}, pages),
                           ([[{"type": "merge_queue"}, None]], typed), ([[{}]], typed),
                           ([[{"type": "merge_queue", "parameters": None}]], typed)):
            with self.subTest(rules=rules):
                self.set_gh(lambda s: s.update(rules=rules))
                self.assertNoLanding(self.safe_push("--merge", "1"), "REFUSED", why)
        self.set_gh(lambda s: s.update(rules=[[]], rules_exit=1))
        self.assertNoLanding(self.safe_push("--merge", "1"), "could not read GitHub")

    def test_main_red_issue_refuses_in_both_modes(self):
        self.opened()
        issue = {"number": 12, "state": "open", "labels": [{"name": "main-red"}]}
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.set_gh(lambda s: s.update(
                    rules=[[{"type": "merge_queue"}]] if queued else [[]],
                    main_red_issues=[[], [issue]]))
                self.assertNoLanding(self.safe_push("--merge", "1"), "main is red", "#12")
        calls = [c for c in self.gh_state()["calls"] if "/issues?" in c[1]]
        self.assertTrue(calls)
        self.assertTrue(all("--paginate" in c and "--slurp" in c for c in calls))

    def test_every_main_red_entry_is_validated(self):
        self.opened()
        issue = {"number": 12, "state": "open", "labels": [{"name": "main-red"}]}
        for invalid in (None, {}, dict(issue, number=True), dict(issue, state="closed"),
                        dict(issue, labels=[None]), dict(issue, labels=[])):
            with self.subTest(entry=invalid):
                self.set_gh(lambda s: s.update(main_red_issues=[[issue], [invalid]]))
                self.assertNoLanding(self.safe_push("--merge", "1"), "unreadable main-red")

    def run_page(self, conclusion="failure", number=1, **fields) -> dict:
        entry = dict(id=number, run_number=number, run_attempt=1, head_sha=BASE,
                     head_branch="main", status="completed", conclusion=conclusion)
        entry.update(fields)
        return {"total_count": 1, "workflow_runs": [entry]}

    def test_failed_post_merge_refuses_in_both_modes(self):
        self.opened()
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.set_gh(lambda s: s.update(
                    rules=[[{"type": "merge_queue"}]] if queued else [[]],
                    runs=[self.run_page()]))
                self.assertNoLanding(self.safe_push("--merge", "1"), "main is red",
                                     "post-merge run", "concluded failure")
        calls = [c for c in self.gh_state()["calls"] if "/runs?" in c[1]]
        self.assertTrue(all(f"head_sha={BASE}" in c[1] for c in calls))

    def test_latest_completed_post_merge_run_is_used(self):
        self.opened()
        page = self.run_page("success", number=2)
        page["workflow_runs"] += self.run_page()["workflow_runs"]
        page["workflow_runs"] += self.run_page(None, number=3, status="in_progress")["workflow_runs"]
        page["total_count"] = 3
        self.set_gh(lambda s: s.update(runs=[page]))
        r = self.safe_push("--merge", "1", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("run 2 concluded success", r.stdout)

    def test_no_post_merge_run_yet_is_not_red(self):
        self.opened()
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.set_gh(lambda s: s.update(
                    rules=[[{"type": "merge_queue"}]] if queued else [[]]))
                r = self.safe_push("--merge", "1", "--dry-run")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("no completed post-merge run at main's tip", r.stdout)
                self.assertEqual(self.origin_main(), BASE)
                self.assertEqual(self.merges(), [])
                self.assertEqual(self.enqueues(), [])

    def test_missing_workflow_is_not_red(self):
        base = self.commit("Main without the post-merge workflow",
                           remove=(".github/workflows/post-merge.yml",))
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{base}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        self.opened()
        self.set_gh(lambda s: s.update(runs_404=True))
        r = self.safe_push("--merge", "1", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("no post-merge workflow", r.stdout)

    def test_unreadable_post_merge_answers_refuse(self):
        self.opened()
        for pages in ({}, [], [None], [self.run_page(None)],
                      [self.run_page(head_sha="f" * 40)]):
            with self.subTest(pages=pages):
                self.set_gh(lambda s: s.update(runs=pages))
                self.assertNoLanding(self.safe_push("--merge", "1"), "unreadable post-merge")
        self.set_gh(lambda s: s.update(runs=[self.run_page("success")], runs_exit=1))
        self.assertNoLanding(self.safe_push("--merge", "1"), "could not read GitHub")

    def test_workflow_present_on_main_makes_404_a_refusal(self):
        base = self.new_base("Main has the post-merge workflow", {
            ".github/workflows/post-merge.yml": "name: post-merge\n"})
        self.opened()
        self.set_gh(lambda s: s.update(runs_404=True))
        r = self.safe_push("--merge", "1")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("could not read GitHub", out)
        self.assertNotIn("no post-merge workflow", out)
        self.assertEqual(self.origin_main(), base)
        self.assertEqual(self.enqueues(), [])

    def test_post_merge_pages_must_agree_and_cover_their_count(self):
        self.opened()
        run = self.run_page("success")["workflow_runs"][0]
        unfinished = dict(run, id=2, run_number=2, status="in_progress", conclusion="failure")
        cases = (([{"total_count": 2, "workflow_runs": [run]},
                   {"total_count": 3, "workflow_runs": []}], "the count changed between pages"),
                 ([{"total_count": 2, "workflow_runs": [run, run]}], "a run appears twice"),
                 ([{"total_count": 2, "workflow_runs": [run]}],
                  "the pages do not cover the reported count"),
                 ([{"total_count": 2, "workflow_runs": [run, unfinished]}],
                  "unreadable unfinished post-merge run conclusion"))
        for pages, message in cases:
            with self.subTest(message=message):
                self.set_gh(lambda s: s.update(runs=pages))
                self.assertNoLanding(self.safe_push("--merge", "1"), message)

    RED = {"number": 12, "state": "open", "labels": [{"name": "main-red"}]}

    def declare_fix(self, line: str = "Fixes main-red: #12") -> None:
        """The coordinator's words in the body gain the declaration, where GitHub shows it."""
        self.set_gh(lambda s: s["prs"][0].update(body=s["prs"][0]["body"].replace(
            "A change for the test.\n", f"A change for the test.\n\n{line}\n", 1)))

    def test_red_main_admits_its_declared_fix_in_both_modes(self):
        # With the queue off only a merge moves main's tip, so a red main's fix must land
        # through --merge: its body says what it fixes, and its own CI must pass.
        for queued in (False, True):
            with self.subTest(queued=queued):
                self.setUp()
                sha = self.opened(queued)
                self.declare_fix()
                self.set_gh(lambda s: s.update(main_red_issues=[[self.RED]],
                                               runs=[self.run_page()]))
                r = self.run_entry() if queued else self.safe_push("--merge", "1")
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 0, out)
                self.assertEqual(self.guard(out, "main health"), "note", out)
                self.assertIn("main is red: open main-red issues #12; post-merge run 1", out)
                self.assertIn("this pull request declares it fixes them", out)
                self.assertEqual(git(ORIGIN, "rev-parse", "main^2").strip(), sha)
                self.assertEqual(len(self.enqueues()), 1 if queued else 0)
                self.assertEqual(len(self.merges()), 0 if queued else 1)

    def test_red_main_refuses_a_fix_not_declared_exactly(self):
        cases = (("Fixes main-red: #13", "not every open main-red issue"),
                 ("Fixes main-red: #12, #13", "not every open main-red issue"),
                 ("Fixes main-red: #12, #12", "unreadable main-red fix"),
                 ("Fixes main-red: 12", "unreadable main-red fix"),
                 ("Fixes main-red: #12\n\nFixes main-red: #12", "unreadable main-red fix"),
                 ("<!-- Fixes main-red: #12 -->", "Only its fix lands"),
                 ("```\nFixes main-red: #12\n```", "Only its fix lands"))
        self.opened()
        body = self.gh_state()["prs"][0]["body"]
        for queued in (False, True):
            for line, message in cases:
                with self.subTest(queued=queued, line=line):
                    self.set_gh(lambda s: s["prs"][0].update(body=body))
                    self.declare_fix(line)
                    self.set_gh(lambda s: s.update(
                        rules=[[{"type": "merge_queue"}]] if queued else [[]],
                        main_red_issues=[[self.RED]]))
                    self.assertNoLanding(self.safe_push("--merge", "1"), message)

    def test_a_failed_run_with_no_open_issue_admits_no_fix(self):
        self.opened(queued=False)
        self.declare_fix()
        self.set_gh(lambda s: s.update(runs=[self.run_page()]))
        self.assertNoLanding(self.safe_push("--merge", "1"), "main is red", "concluded failure",
                             "no open main-red issue names it")

    def test_a_declared_fix_still_needs_its_own_ci(self):
        sha = self.opened(queued=False)
        self.declare_fix()
        failing = [dict(c, bucket="fail", state="FAILURE") if c["name"] == "check" else c
                   for c in PASSING]
        self.set_gh(lambda s: s.update(main_red_issues=[[self.RED]], runs=[self.run_page()]))
        self.set_gh(lambda s: s["checks"].update({sha: failing}))
        r = self.safe_push("--merge", "1")
        self.assertNoLanding(r, "the merge gates refused: CI")
        self.assertEqual(self.guard(r.stdout + r.stderr, "main health"), "note")


def in_prose(text: str, change) -> str:
    """`text` with `change` made to its prose alone, its code spans as they were."""
    return "`".join(change(part) if i % 2 == 0 else part
                    for i, part in enumerate(text.split("`")))


class DecisionEntries(Clone):
    """Dated entry files supply new mentions to every decision guard; being history, they
    are only ever added, beside the folder's README, which approves nothing; a line counts
    only when the record holds nothing like it, read as safe_push.skeleton reads it, its
    words never joined across a line that does not count; and a guard that refuses names
    each line of an entry that did not count and names what it asks for, and why."""

    ENTRY = "docs/decisions/2026-10-20-test.md"
    MOVED = "docs/decisions/2026-10-21-moved.md"
    README = "docs/decisions/README.md"
    PATH = "scripts/check_style.py"
    # Its first line names all four things the guards protect; the rest is long enough
    # that a move with a word of that line changed is still most of the file, as Git's
    # rename detection measures it. (Its words date from when a copy was refused for
    # being one.)
    OLD = (f"- **An earlier decision for the test.** It names `{PATH}`, "
           "`Certificate/axioms.lock`, I.1 and `mishnah/test/`.\n"
           "  It gives its reasons at some length, so that a copy of it with one word\n"
           "  changed is still most of the file, as Git's copy detection measures one,\n"
           "  and is found as a copy: an entry is history, added once and never moved,\n"
           "  copied or changed, and a correction is a new entry in words of its own.\n")
    NEW = (f"- **A new decision for the test.** It names `{PATH}`, "
           "`Certificate/axioms.lock`, I.1 and `mishnah/test/` afresh.\n")
    RESPACED = OLD.replace(" It names ", " It  names\t").replace(".\n", ". \n")
    SPACED_THROUGH = "".join("\t" + "  ".join(line.split()) + " \n"
                             for line in OLD.splitlines())
    REWORDED = OLD.replace("earlier", "revised")
    # The same words wrapped at another width, so that no line is one of the original's.
    REWRAPPED = textwrap.fill(" ".join(OLD.split()), 41) + "\n"
    CARRIAGE = OLD.replace("\n", "\r")
    ZERO_WIDTH = "".join(line[:2] + "\u200b" + line[2:] + "\n" for line in OLD.splitlines())
    # The prose of the earlier entry, its code spans as they were, so that each still names
    # what the earlier entry names: in capitals; with the Cyrillic letters U+0430, U+0435
    # and U+043E for the Latin a, e and o, which look the same; with the Braille pattern
    # blank (U+2800), which looks like a space and is none to str.split, for its spaces;
    # and with the musical symbol null notehead (U+1D159), which renders blank, put in after
    # each word's first letter, as the security re-review wrote it.
    CAPITALS = in_prose(OLD, str.upper)
    CYRILLIC = in_prose(OLD, lambda s: s.translate(str.maketrans("aeo", "\u0430\u0435\u043e")))
    BRAILLE = in_prose(OLD, lambda s: s.replace(" ", "\u2800"))
    NOTEHEADS = in_prose(OLD, lambda s: re.sub(r"\b(\w)", "\\1\U0001d159", s))
    # An entry of its own words, with a Greek word in it.
    GREEK = ("- **\u03a3\u03c4\u03bf\u03b9\u03c7\u03b5\u1fd6\u03b1, a new decision for the "
             f"test.** It names `{PATH}`, "
             "`Certificate/axioms.lock`, I.1 and `mishnah/test/` afresh.\n")
    LOCK_LINE = "- **A new line for the test.** The axiom lock gains a comment.\n"
    # What each kind writes at MOVED, and whether it removes the earlier entry.
    MOVES = {"rename": (OLD, True), "rename re-spaced": (RESPACED, True),
             "rename reworded": (REWORDED, True), "rename and add": (OLD + NEW, True),
             "copy": (OLD, False), "copy re-spaced": (SPACED_THROUGH, False),
             "copy reworded": (REWORDED, False), "copy re-wrapped": (REWRAPPED, False),
             "copy re-wrapped and add": (REWRAPPED + "\n" + LOCK_LINE, False),
             "copy with carriage returns": (CARRIAGE, False),
             "copy with zero-width spaces": (ZERO_WIDTH, False),
             "copy in capitals": (CAPITALS, False), "copy in Cyrillic": (CYRILLIC, False),
             "copy with Braille blanks": (BRAILLE, False),
             "copy with null noteheads": (NOTEHEADS, False),
             "page copy": (OLD, False), "readme copy": (OLD, False),
             "undated copy": (OLD, False), "new": (NEW, False), "new in Greek": (GREEK, False)}
    # What each of the four guards asks for, as a line of OLD, and of each copy of it, names
    # it (the lock is a protected file too): a refusal names a line that did not count only
    # when it names one of those.
    ASKS = {"guard_protected": (PATH, "Certificate/axioms.lock"), "guard_lock": ("axioms.lock",),
            "guard_statements": ("I.1",), "guard_directories": ("mishnah/test/",)}

    def four_guards(self):
        """The guards that ask for a new line in the decisions record, with their
        arguments."""
        return ((safe_push.guard_protected, ()), (safe_push.guard_lock, ()),
                (safe_push.guard_statements, (WORK,)), (safe_push.guard_directories, ()))

    def protected_writes(self):
        """A change to each thing the four guards protect, but a directory."""
        return {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
            safe_push.LOCK: self.text(safe_push.LOCK) + "\n# A comment for the test.\n",
            "Elements/BookI/Prop01.lean": self.replaced(
                "Elements/BookI/Prop01.lean", SIGNATURE_OLD, SIGNATURE_NEW),
        }

    def restart(self, rev=None):
        """Back to `rev` (BASE by default), as a test starts."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", rev or BASE)
        git(WORK, "clean", "-fdq")

    def decision_change(self, kind):
        """Plant an earlier decision, then change each thing the four guards protect, with
        the decisions record changed as `kind` says."""
        source = {"page copy": DECISIONS, "readme copy": self.README,
                  "undated copy": "docs/decisions/notes.md"}.get(kind, self.ENTRY)
        base = self.commit("Record an earlier decision", {
            source: self.text(DECISIONS) + "\n" + self.OLD if source == DECISIONS else self.OLD,
            "mishnah/test/note.md": "A note.\n",
        })
        writes = self.protected_writes()
        remove = ["mishnah/test"]
        if kind.startswith("delete and re-add"):
            self.commit("Remove the earlier entry", remove=[self.ENTRY])
            writes[self.ENTRY] = self.RESPACED if kind.endswith("re-spaced") else self.OLD
        elif kind == "edit":
            writes[self.ENTRY] = self.REWORDED
        elif kind == "edit and add":
            writes[self.ENTRY] = self.OLD + self.NEW
        else:
            text, gone = self.MOVES[kind]
            writes[self.MOVED] = text.encode()
            if gone:
                remove.append(self.ENTRY)
        sha = self.commit("Change the guarded files", writes, remove=remove)
        return base, sha

    def check_guard(self, guard, base, sha, *args):
        rep = safe_push.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            guard(WORK, base, sha, *args, rep)
        return rep

    def check_decision_change(self, kind, outcome, entries="ok", why=None, uncounted=None):
        """The four guards' outcome, and the outcome of the guard of the entries, with what
        it says when it refuses. `uncounted`, when given, maps each line of the entry `kind`
        writes at MOVED that did not count to why: a guard's refusal names each of those
        lines that names what the guard asks for (ASKS), with why, and no other line of the
        entry, so never a line that names nothing it asks for."""
        base, sha = self.decision_change(kind)
        lines = self.MOVES[kind][0].splitlines() if uncounted else []
        for guard, args in self.four_guards():
            with self.subTest(guard=guard.__name__):
                rep = self.check_guard(guard, base, sha, *args)
                self.assertEqual(rep.steps[-1].outcome, outcome, rep.steps)
                if outcome == "FAIL":
                    detail = rep.failed()[0].detail
                    self.assertIn("no new line", detail)
                    if uncounted:
                        asks = self.ASKS[guard.__name__]
                        named = [n for n in uncounted
                                 if any(ask in lines[n - 1] for ask in asks)]
                        self.assertTrue(named and len(named) < len(lines), (asks, lines))
                        for n, reason in uncounted.items():
                            if n in named:
                                self.assertIn(f"\n  {self.MOVED}:{n}: {reason}", detail)
                            else:
                                self.assertNotIn(f"{self.MOVED}:{n}:", detail)
                    if entries == "FAIL":
                        self.assertIn("no line of an entry counts while the guard of the "
                                      "decision entries refuses", rep.failed()[0].detail)
                else:
                    self.assertFalse(rep.failed(), rep.steps)
        rep = self.check_guard(safe_push.guard_entries, base, sha)
        self.assertEqual([(s.name, s.outcome) for s in rep.steps],
                         [("decision entries", entries)], rep.steps)
        if why:
            self.assertIn(why, rep.steps[-1].detail)
            self.assertIn("a correction is a new entry", rep.steps[-1].detail)

    def test_rename_renews_no_approval(self):
        self.check_decision_change("rename", "FAIL", "FAIL",
                                   f"{self.MOVED}: renamed from {self.ENTRY}")

    def test_rename_with_interior_whitespace_renews_no_approval(self):
        self.check_decision_change("rename re-spaced", "FAIL", "FAIL",
                                   f"{self.MOVED}: renamed from {self.ENTRY}")

    def test_rename_with_a_word_changed_renews_no_approval(self):
        self.check_decision_change("rename reworded", "FAIL", "FAIL",
                                   f"{self.MOVED}: renamed from {self.ENTRY}")

    def test_rename_with_a_new_naming_line_is_refused(self):
        self.check_decision_change("rename and add", "FAIL", "FAIL",
                                   f"{self.MOVED}: renamed from {self.ENTRY}")

    def every_line(self, why, text=OLD):
        """Each line of `text`, written at MOVED, by its number, with `why`."""
        return {n: why for n in range(1, len(text.splitlines()) + 1)}

    # A copy is not refused for being one (an entry may share words with an older one),
    # but its copied lines count for nothing, and a refusal names each of them that names
    # what the guard asks for: OLD's first line, never its four lines of reasons.

    def test_copy_renews_no_approval(self):
        self.check_decision_change("copy", "FAIL",
                                   uncounted=self.every_line(safe_push.IN_RECORD))

    def test_copy_with_a_word_changed_renews_no_approval(self):
        self.check_decision_change("copy reworded", "FAIL", uncounted={
            **self.every_line(safe_push.IN_RECORD), 1: safe_push.IN_RUN})

    def test_copy_with_its_whitespace_changed_renews_no_approval(self):
        # Every line differs; but every line, its whitespace collapsed, is an old one.
        self.check_decision_change("copy re-spaced", "FAIL",
                                   uncounted=self.every_line(safe_push.IN_RECORD))

    def test_re_wrapped_copy_renews_no_approval(self):
        # No line is an old one; but every word lies in a run of twelve the old entry holds.
        self.assertFalse(set(self.REWRAPPED.splitlines()) & set(self.OLD.splitlines()))
        self.check_decision_change("copy re-wrapped", "FAIL", uncounted=self.every_line(
            safe_push.IN_RUN, self.REWRAPPED))

    def test_look_alike_copies_renew_no_approval(self):
        # The copy in capitals, or with Cyrillic letters in its prose, each still naming
        # every thing the earlier entry names, reads as the earlier entry: NFKC, the
        # look-alike letters read as Latin ones, and casefolded.
        for kind, text in (("copy in capitals", self.CAPITALS),
                           ("copy in Cyrillic", self.CYRILLIC)):
            with self.subTest(kind=kind):
                self.restart()
                self.assertNotEqual(text, self.OLD)
                self.assertFalse(set(text.splitlines()) & set(self.OLD.splitlines()))
                self.assertIn(f"`{self.PATH}`", text)
                self.check_decision_change(kind, "FAIL",
                                           uncounted=self.every_line(safe_push.IN_RECORD))

    def test_copies_with_characters_that_render_blank_are_refused(self):
        # The copy with Braille blanks for its spaces, or with null noteheads in its words,
        # renders as the earlier entry does; Unicode counts neither character white space
        # nor default-ignorable, so each is refused by name, as a zero-width space is.
        for kind, char in (("copy with Braille blanks", "U+2800"),
                           ("copy with null noteheads", "U+1D159")):
            with self.subTest(kind=kind):
                self.restart()
                self.assertIn(f"`{self.PATH}`", self.MOVES[kind][0])
                self.check_decision_change(kind, "FAIL", "FAIL",
                                           f"{self.MOVED}:1: {char}, {safe_push.HIDDEN}")

    def test_entry_with_a_greek_word_passes(self):
        self.check_decision_change("new in Greek", "ok")

    def test_re_wrapped_copy_beside_a_new_line_renews_only_that_line(self):
        base, sha = self.decision_change("copy re-wrapped and add")
        outcomes = {guard.__name__: self.check_guard(guard, base, sha, *args).steps[-1].outcome
                    for guard, args in self.four_guards()}
        self.assertEqual(outcomes, {"guard_protected": "FAIL", "guard_lock": "ok",
                                    "guard_statements": "FAIL", "guard_directories": "FAIL"})
        rep = self.check_guard(safe_push.guard_entries, base, sha)
        self.assertEqual(rep.steps[-1].outcome, "ok", rep.steps)

    def test_copy_with_carriage_returns_is_refused(self):
        # Git reads the copy as one new line; render.py would read the old entry's lines.
        self.check_decision_change("copy with carriage returns", "FAIL", "FAIL",
                                   f"{self.MOVED}:1: U+000D, a character an entry or the "
                                   "README may not hold")

    def test_copy_with_zero_width_spaces_is_refused(self):
        self.check_decision_change("copy with zero-width spaces", "FAIL", "FAIL",
                                   f"{self.MOVED}:1: U+200B, a character an entry or the "
                                   "README may not hold")

    def test_copy_from_the_page_renews_no_approval(self):
        self.check_decision_change("page copy", "FAIL",
                                   uncounted=self.every_line(safe_push.IN_RECORD))

    def test_copy_from_the_folder_readme_renews_no_approval(self):
        self.check_decision_change("readme copy", "FAIL",
                                   uncounted=self.every_line(safe_push.IN_RECORD))

    def test_copy_from_an_undated_file_renews_no_approval(self):
        self.check_decision_change("undated copy", "FAIL",
                                   uncounted=self.every_line(safe_push.IN_RECORD))

    def test_delete_and_re_add_renews_no_approval(self):
        self.check_decision_change("delete and re-add", "FAIL")

    def test_delete_and_re_add_with_interior_whitespace_renews_no_approval(self):
        self.check_decision_change("delete and re-add re-spaced", "FAIL", "FAIL",
                                   f"{self.ENTRY}: changed")

    def test_old_entry_edited_in_place_renews_no_approval(self):
        self.check_decision_change("edit", "FAIL", "FAIL", f"{self.ENTRY}: changed")

    def test_old_entry_with_a_new_naming_line_is_refused(self):
        self.check_decision_change("edit and add", "FAIL", "FAIL", f"{self.ENTRY}: changed")

    def test_new_entry_beside_an_old_one_passes(self):
        self.check_decision_change("new", "ok")

    # Words that name a proposition and mention the axiom lock only when joined across a
    # line: "III." and "16", as the security review found them, and "I." and "1".
    SPLIT = ("- **Timing (tooling).** The queue now waits for Book {1}.\n{0}"
             "{2} checks run in the second pass. Nothing in it touches an axiom\n{0}"
             "lock or key; those stay as they were.\n")
    STATEMENTS = {"III.16": ("Elements/BookIII/Prop16.lean", "theorem Prop16 {A B D E : Point}",
                             "theorem Prop16 {A B D E X : Point}"),
                  "I.1": ("Elements/BookI/Prop01.lean", SIGNATURE_OLD, SIGNATURE_NEW)}

    def test_words_are_never_joined_across_a_blank_or_an_old_line(self):
        # The book and the number, "axiom" and "lock", in lines kept apart by a blank line,
        # or by a line the record holds, are in hunks of their own; in consecutive lines
        # they are one mention, as a name wrapped on the page is.
        old = "## 15 October 2026\n"
        self.assertIn("\n" + old, self.text(DECISIONS))
        for ref, (path, before, after) in self.STATEMENTS.items():
            book, number = ref.split(".")
            for between, outcome in (("", "ok"), ("\n", "FAIL"), (old, "FAIL"),
                                     ("\n" + old + "\n", "FAIL")):
                with self.subTest(ref=ref, between=between):
                    self.restart()
                    lock = self.text(safe_push.LOCK) + "\n# A comment for the test.\n"
                    sha = self.commit("Name a statement and the lock across lines", {
                        path: self.replaced(path, before, after), safe_push.LOCK: lock,
                        self.ENTRY: self.SPLIT.format(between, book, number),
                    })
                    rep = self.check_guard(safe_push.guard_statements, BASE, sha, WORK)
                    self.assertEqual(rep.steps[-1].outcome, outcome, rep.steps)
                    self.assertRegex(rep.steps[-1].detail,
                                     rf"{re.escape(ref)}(: | \()the Lean statement changed")
                    rep = self.check_guard(safe_push.guard_lock, BASE, sha)
                    self.assertEqual(rep.steps[-1].outcome, outcome, rep.steps)
                    self.assertFalse(self.check_guard(safe_push.guard_entries, BASE, sha).failed())

    def test_entry_lines_split_at_every_line_that_does_not_count(self):
        record = safe_push.Record({"an old line"},
                                  {" ".join(f"w{n}" for n in range(i, i + 12))
                                   for i in range(20)})
        quoted = " ".join(f"w{n}" for n in range(3, 15))
        text = (f"new one\nnew two\n\n  An  OLD line \nnew three\nhalf {quoted} and more\n"
                "new four\n")
        lines = safe_push.entry_lines(self.ENTRY, text, record)
        self.assertEqual([[(a.line, a.text) for a in h.added] for h in lines.runs],
                         [[(1, "new one"), (2, "new two")], [(5, "new three")],
                          [(7, "new four")]])
        self.assertTrue(all(h.path == self.ENTRY and h.removed == [] for h in lines.runs))
        self.assertEqual([str(u) for u in lines.uncounted],
                         [f"{self.ENTRY}:4: {safe_push.IN_RECORD}",
                          f"{self.ENTRY}:6: {safe_push.IN_RUN}"])
        self.assertEqual([u.text for u in lines.uncounted],
                         ["  An  OLD line ", f"half {quoted} and more"])

    def test_skeleton(self):
        # NFKC, the Cyrillic and Greek look-alikes read as Latin letters (capital Eta as H,
        # small eta as n; the lunate sigmas, which NFKC makes sigmas, as C and c), casefolded,
        # and every space separator, the Braille blank, the null notehead, the Khitan filler
        # and the Hangul fillers read as spaces: an entry may hold none of those five, but
        # the decisions page may.
        line = safe_push.record_line
        self.assertEqual(line("\ufb01ve\u00a0\u3000 words\t"), "five words")
        self.assertEqual(line("A\u2800B\u1680C\u2003D\u3164E\u202fF"), "a b c d e f")
        self.assertEqual(line("A\U0001d159B\U00016fe4C"), "a b c")
        self.assertTrue(all(safe_push.invisible(c) for c in safe_push.BLANKS))
        self.assertEqual(line("\u0397\u0435ll\u043e \u03b7\u03bft \u03f9\u03f2 \U0001d6c2"),
                         "hello not cc a")
        self.assertEqual(line("IT NAMES `Scripts/X.py`"), line("it names `scripts/x.py`"))
        # A Greek word: its look-alikes read as Latin letters, its other letters as they
        # are, casefolded; casefolding its iota with perispomeni gives an iota, read as i.
        self.assertEqual(line("\u03a3\u03c4\u03bf\u03b9\u03c7\u03b5\u1fd6\u03b1"),
                         "\u03c3\u03c4oix\u03b5i\u0342a")
        # Every letter the table reads is Cyrillic or Greek, and is read as a Latin one.
        for code, latin in safe_push.LOOK_ALIKES.items():
            with self.subTest(char=hex(code)):
                self.assertRegex(unicodedata.name(chr(code)), r"^(CYRILLIC|GREEK) ")
                self.assertRegex(unicodedata.name(latin), r"^LATIN (CAPITAL|SMALL) LETTER ")

    def test_entries_guard_runs_in_the_pre_flight(self):
        self.new_base("An earlier decision", {self.ENTRY: self.OLD})
        self.commit("Move the earlier decision", {self.MOVED: self.OLD}, remove=[self.ENTRY])
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("REFUSED", out)
        self.assertEqual(self.guard(out, "decision entries"), "FAIL", out)
        self.assertIn(f"{self.MOVED}: renamed from {self.ENTRY}", out)

    def planted(self, files: dict, mode="100644") -> str:
        """A commit on HEAD holding `files` at exactly the paths given, made without the
        working tree, so that no file system that ignores case can respell them."""
        env = dict(os.environ, GIT_INDEX_FILE=str(TMP / "planted-index"))
        head = git(WORK, "rev-parse", "HEAD").strip()
        git(WORK, "read-tree", head, env=env)
        for path, text in files.items():
            blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=WORK,
                                  input=text, capture_output=True, text=True,
                                  check=True).stdout.strip()
            git(WORK, "update-index", "--add", "--cacheinfo", f"{mode},{blob},{path}", env=env)
        tree = git(WORK, "write-tree", env=env).strip()
        return git(WORK, "commit-tree", tree, "-p", head, "-m", "Planted", env=env).strip()

    def test_entry_changes_reads_every_kind_of_change(self):
        base = self.commit("Earlier entries", {
            self.ENTRY: self.OLD, "docs/decisions/2026-10-19-kept.md": self.NEW,
            "docs/decisions/2026-10-19-mode.md": "- A decision whose mode changes.\n",
            self.README: "# Decision entries\n",
        })
        (WORK / "docs/decisions/2026-10-19-mode.md").chmod(0o755)
        self.commit("Change them", {
            "docs/decisions/2026-10-22-fresh.md": "- A fresh decision for the test.\n",
            "docs/decisions/2026-02-30-bad-date.md": "- A decision with a bad date.\n",
            "docs/decisions/notes.md": "- Notes for the test.\n",
            "docs/decisions/sub/2026-10-22-deeper.md": "- A decision in a folder.\n",
            "docs/decisions/2026-10-22-empty.md": " \n",
            "docs/decisions/2026-10-22-latin.md": b"- A decision \xff.\n",
            "docs/decisions/2026-10-22-hidden.md": "- A fresh\u2060 decision.\n",
            "docs/decisions/2026-10-19-mode.md": "- A decision whose mode changes.\n",
            self.README: "# Decision entries\n\nEach decision is a file.\n",
        }, remove=[self.ENTRY])
        sha = self.planted({"docs/Decisions/2026-10-22-case.md": "- A decision, recased.\n"})
        refused, added = safe_push.entry_changes(WORK, base, sha)
        self.assertEqual(sorted(refused), sorted([
            "docs/Decisions/2026-10-22-case.md: spelled otherwise than docs/decisions/, "
            "which Git and GitHub tell apart by case",
            "docs/decisions/2026-02-30-bad-date.md: neither the README nor an entry named "
            "<YYYY-MM-DD>-<slug>.md with a valid date",
            "docs/decisions/2026-10-19-mode.md: changed",
            "docs/decisions/2026-10-22-empty.md: holds no text",
            "docs/decisions/2026-10-22-hidden.md:1: U+2060, a character an entry or the "
            "README may not hold (a control character but a tab and a line feed, a format "
            "character, a line or paragraph separator, another default-ignorable one, one "
            "that renders blank, or a private-use or unassigned code point)",
            "docs/decisions/2026-10-22-latin.md: not UTF-8 text",
            "docs/decisions/notes.md: neither the README nor an entry named "
            "<YYYY-MM-DD>-<slug>.md with a valid date",
            "docs/decisions/sub/2026-10-22-deeper.md: neither the README nor an entry named "
            "<YYYY-MM-DD>-<slug>.md with a valid date",
            f"{self.ENTRY}: deleted"]))
        self.assertEqual(list(added), ["docs/decisions/2026-10-22-fresh.md"])

    def test_paths_a_mac_reads_as_the_folder_are_refused(self):
        # A Mac's file system compares names in NFD form, casefolded, and finds each of
        # these under docs/decisions/; Git and GitHub do not. A long s (U+017F) casefolds to
        # an s, which Git's :(icase) does not see, so a .gitignore planted there could hide
        # an entry from render.py on a Mac, as the security re-review found. Each is
        # refused, wherever in the path the respelling lies; a folder of another name is not.
        misspelled = ("docs/deciſions/2026-10-22-long-s.md",
                      "docs/deciſions/.gitignore", "docſ/decisions/2026-10-22-docs.md",
                      "docs/decisionſ/2026-10-22-last.md",
                      "DOCS/DECISIONS/2026-10-22-capitals.md")
        apart = ("docs/decisions-old/2026-10-22-apart.md", "docs/decision/2026-10-22-apart.md",
                 "docs/deciſions-old/2026-10-22-apart.md")
        sha = self.planted({**{path: "- A decision for the test.\n" for path in misspelled},
                            **{path: "- A note for the test.\n" for path in apart}})
        refused, added = safe_push.entry_changes(WORK, BASE, sha)
        self.assertEqual(sorted(refused), sorted(
            f"{path}: spelled otherwise than docs/decisions/, which Git and GitHub tell apart "
            "by case" for path in misspelled))
        self.assertEqual(added, {})
        rep = self.check_guard(safe_push.guard_entries, BASE, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)

    def test_refused_paths_are_printed_with_escapes(self):
        # A path holding an escape sequence, a bell or a bidirectional mark is named with
        # each written as an escape, so that a refusal gives a terminal nothing to act on.
        sha = self.planted({"docs/decisions/2026-10-22-\x1b[31mred.md": "- A decision.\n",
                            "docs/decisions/notes\u202e.md": "- Notes.\n",
                            "docs/Decisions/\x07bell.md": "- A decision, recased.\n"})
        rep = self.check_guard(safe_push.guard_entries, BASE, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
        detail = rep.steps[-1].detail
        for shown in ("docs/decisions/2026-10-22-\\x1b[31mred.md: neither the README",
                      "docs/decisions/notes\\u202e.md: neither the README",
                      "docs/Decisions/\\x07bell.md: spelled otherwise"):
            self.assertIn(shown, detail)
        self.assertEqual([c for c in detail if not c.isprintable() and c != "\n"], [])

    def test_readme_is_utf8_text_with_no_hidden_character(self):
        # Added or changed, the README is read as an entry is read: one that is no UTF-8
        # text would stop every later push that reads the record (the security
        # re-review's case), and one holding a character an entry may not hold could hide
        # what it says. Each is refused, by its line.
        bare, held = self.readme_bases()
        for start, text, why in (
                (bare, b"# Decision entries \xff\n", f"{self.README}: not UTF-8 text"),
                (held, "# Decision entries\n\nEach\u200b decision.\n".encode(),
                 f"{self.README}:3: U+200B, {safe_push.HIDDEN}"),
                (held, "# Decision\U0001d159 entries\n".encode(),
                 f"{self.README}:1: U+1D159, {safe_push.HIDDEN}")):
            with self.subTest(why=why):
                self.restart(start)
                sha = self.commit("The README for the test", {self.README: text})
                rep = self.check_guard(safe_push.guard_entries, start, sha)
                self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
                self.assertIn(why, rep.steps[-1].detail)

    def readme_bases(self) -> tuple[str, str]:
        """A commit with no README in the folder, and one with a README, as a regular file:
        BASE is one of them, as it holds a README or not."""
        if (WORK / self.README).is_file():
            return self.commit("No README for the entries", remove=[self.README]), BASE
        return BASE, self.commit("A README for the entries",
                                 {self.README: "# Decision entries\n"})

    def readme_status(self, start: str, sha: str) -> str:
        """How Git reads the README's change from `start` to `sha`: A, M, T or D."""
        return git(WORK, "diff", "--name-status", "--no-renames", start, sha, "--",
                   self.README).split()[0]

    def test_readme_may_be_edited_never_deleted_and_approves_nothing(self):
        # Once added, the README stays, so that origin/main always holds the folder that
        # the advised revert restores; added or edited, it approves nothing.
        bare, held = self.readme_bases()
        for change, status in (("added", "A"), ("edited", "M"), ("deleted", "D")):
            with self.subTest(change=change):
                start = bare if change == "added" else held
                self.restart(start)
                writes = {self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n"}
                remove = [self.README] if change == "deleted" else []
                if change != "deleted":
                    writes[self.README] = f"# Decision entries\n\n`{self.PATH}` changes.\n"
                sha = self.commit(f"The README {change}", writes, remove=remove)
                self.assertEqual(self.readme_status(start, sha), status)
                rep = self.check_guard(safe_push.guard_entries, start, sha)
                if change == "deleted":
                    self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
                    self.assertIn(f"{self.README}: deleted (the README, once added, stays)",
                                  rep.steps[-1].detail)
                else:
                    self.assertEqual(rep.steps[-1].outcome, "ok", rep.steps)
                    self.assertEqual(rep.steps[-1].detail, "no entry added")
                rep = self.check_guard(safe_push.guard_protected, start, sha)
                self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
                self.assertIn(f"naming them: {self.PATH}", rep.failed()[0].detail)

    def test_readme_link_refused(self):
        # A link added where there was no README, or put in the README's place, is refused
        # as a link, though the README may change.
        bare, held = self.readme_bases()
        for start, status in ((bare, "A"), (held, "T")):
            with self.subTest(status=status):
                self.restart(start)
                path = WORK / self.README
                path.unlink(missing_ok=True)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to("../../" + self.PATH)
                git(WORK, "add", "--", self.README)
                sha = self.commit("A link for the README")
                self.assertEqual(self.readme_status(start, sha), status)
                rep = self.check_guard(safe_push.guard_entries, start, sha)
                self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
                self.assertIn(f"{self.README}: not a regular file (mode 120000)",
                              rep.steps[-1].detail)

    def test_unreadable_base_record_refuses(self):
        base, sha = self.decision_change("new")
        original_git = safe_push.git

        def unreadable(repo, *args, **kwargs):
            if args[:2] == ("cat-file", "blob") and not args[2].startswith(sha):
                raise safe_push.Refusal("cannot read the base decision blob")
            return original_git(repo, *args, **kwargs)

        with mock.patch.object(safe_push, "git", side_effect=unreadable):
            with self.assertRaisesRegex(safe_push.Refusal, "cannot read the base decision"):
                safe_push.decision_hunks(WORK, base, sha)

    def test_undecodable_base_record_refuses(self):
        base = self.commit("An unreadable earlier entry", {self.ENTRY: b"\xff\n"})
        sha = self.protected_change(f"`{self.PATH}` changes.",
                                    "docs/decisions/2026-10-20-new.md")
        with self.assertRaisesRegex(safe_push.Refusal, "could not decode the decisions record"):
            safe_push.decision_hunks(WORK, base, sha)

    def protected_change(self, mention, entry=ENTRY):
        return self.commit("Name a protected change in an entry", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
            entry: mention + "\n",
        })

    def test_new_entry_names_a_protected_path(self):
        sha = self.protected_change(f"`{self.PATH}` changes.")
        rep = self.check_guard(safe_push.guard_protected, BASE, sha)
        self.assertFalse(rep.failed(), rep.steps)
        self.assertEqual(rep.steps[-1].outcome, "ok")
        self.assertIn(f"each named in {DECISIONS} or docs/decisions/: {self.PATH};",
                      rep.steps[-1].detail)
        self.assertEqual(self.text(DECISIONS), safe_push.show(WORK, BASE, DECISIONS))
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha), [])

    def test_editing_an_old_entry_line_adds_no_mention(self):
        base = self.commit("An earlier decision", {self.ENTRY: f"`{self.PATH}` changes.\n"})
        sha = self.protected_change(f"`{self.PATH}` changes again.")
        rep = self.check_guard(safe_push.guard_protected, base, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL")
        self.assertIn(f"naming them: {self.PATH}", rep.failed()[0].detail)

    def test_relative_entry_links_resolve_from_the_entry_folder(self):
        for prefix, outcome in (("../../", "ok"), ("./../../", "ok"),
                                ("../", "FAIL"), ("../../../", "FAIL"), ("./", "FAIL")):
            with self.subTest(prefix=prefix):
                base = git(WORK, "rev-parse", "HEAD").strip()
                sha = self.protected_change(f"[the file]({prefix}{self.PATH}) changes.",
                                            f"docs/decisions/2026-10-20-case-{len(prefix)}-"
                                            f"{outcome.lower()}.md")
                rep = self.check_guard(safe_push.guard_protected, base, sha)
                self.assertEqual(rep.steps[-1].outcome, outcome, rep.steps)

    def test_readme_and_undated_files_supply_no_approval(self):
        for name in ("README.md", "notes.md", "2026-02-30-test.md", "0000-01-01-test.md"):
            with self.subTest(name=name):
                base = git(WORK, "rev-parse", "HEAD").strip()
                sha = self.protected_change(f"`{self.PATH}` changes.",
                                            f"docs/decisions/{name}")
                rep = self.check_guard(safe_push.guard_protected, base, sha)
                self.assertEqual(rep.steps[-1].outcome, "FAIL")
                self.assertIn(f"naming them: {self.PATH}", rep.failed()[0].detail)

    LATE = ("dated after {}, the day after the earlier of {}'s committer date and this "
            "machine's date")

    def check_entry_dates(self, committed, machine, cases):
        """Each of `cases`, an entry's name and why it is refused (None when it is not),
        committed with the committer date `committed`, on a machine whose date is
        `machine`: the guard of the entries, and the protected-paths guard the entry
        names a file for."""
        env = dict(os.environ, GIT_COMMITTER_DATE=committed)
        with mock.patch.object(safe_push, "today", lambda: machine):
            for name, why in cases:
                with self.subTest(name=name):
                    self.restart()
                    entry = f"docs/decisions/{name}"
                    sha = self.commit("Name a protected change in a dated entry", {
                        self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
                        entry: f"`{self.PATH}` changes.\n",
                    }, env=env)
                    self.assertEqual(safe_push.committed_on(WORK, sha),
                                     datetime.date.fromisoformat(committed[:10]))
                    entries = self.check_guard(safe_push.guard_entries, BASE, sha)
                    protected = self.check_guard(safe_push.guard_protected, BASE, sha)
                    if why is None:
                        self.assertEqual([(s.outcome, s.detail) for s in entries.steps],
                                         [("ok", f"added: {entry}")])
                        self.assertFalse(protected.failed(), protected.steps)
                    else:
                        self.assertEqual(entries.steps[-1].outcome, "FAIL", entries.steps)
                        self.assertIn(f"{entry}: {why.format(sha[:12])}",
                                      entries.steps[-1].detail)
                        self.assertEqual(protected.steps[-1].outcome, "FAIL", protected.steps)
                        self.assertIn("no line of an entry counts while the guard of the "
                                      "decision entries refuses", protected.failed()[0].detail)

    def test_entry_dates_run_from_the_first_entry_to_the_day_after_the_commit(self):
        # An entry is dated from 20 October 2026, the day the entries began, to the day after
        # its commit's committer date, read on the committer's own calendar, when this
        # machine's date is later: committed at 23:30 on 25 October at UTC-11, which is
        # 26 October at UTC, an entry may be dated 26 October, and no later.
        early = "dated before 2026-10-20, the day the entries began"
        late = self.LATE.format("2026-10-26", "{}")
        self.check_entry_dates("2026-10-25T23:30:00-11:00", datetime.date(2026, 10, 30), (
            ("2026-10-20-first.md", None), ("2026-10-26-next-day.md", None),
            ("2026-10-19-early.md", early), ("1900-01-01-old.md", early),
            ("2026-10-27-later.md", late), ("9999-12-31-last-word.md", late)))

    def test_entry_dates_run_to_the_day_after_this_machines_date_too(self):
        # The pusher sets the committer date. Committed as of 1 January 2099, as in the
        # security re-review's case, an entry is still dated no later than the day after
        # this machine's date, 25 October 2026 here: 26 October, and no later.
        late = self.LATE.format("2026-10-26", "{}")
        self.check_entry_dates("2099-01-01T12:00:00+00:00", datetime.date(2026, 10, 25), (
            ("2026-10-26-next-day.md", None), ("2026-10-27-later.md", late),
            ("2099-01-01-future.md", late)))

    def test_symlink_entry_supplies_no_approval(self):
        path = WORK / self.ENTRY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to("../../" + self.PATH)
        git(WORK, "add", "--", self.ENTRY)
        sha = self.commit("A link is not a decision entry", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
        })
        rep = self.check_guard(safe_push.guard_protected, BASE, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL")
        self.assertIn(f"naming them: {self.PATH}", rep.failed()[0].detail)
        rep = self.check_guard(safe_push.guard_entries, BASE, sha)
        self.assertIn(f"{self.ENTRY}: not a regular file (mode 120000)", rep.steps[-1].detail)

    def test_lock_named_in_an_entry_passes(self):
        sha = self.commit("Name the lock in an entry", {
            safe_push.LOCK: self.text(safe_push.LOCK) + "\n# A comment for the test.\n",
            self.ENTRY: "`Certificate/axioms.lock` gains a comment.\n",
        })
        for guard in (safe_push.guard_lock, safe_push.guard_protected):
            with self.subTest(guard=guard.__name__):
                rep = self.check_guard(guard, BASE, sha)
                self.assertFalse(rep.failed(), rep.steps)
                self.assertEqual(rep.steps[-1].outcome, "ok")

    def test_lock_mentioned_only_in_an_edited_old_entry_is_refused(self):
        base = self.commit("An earlier lock decision", {
            self.ENTRY: "`Certificate/axioms.lock` gains a comment.\n",
        })
        sha = self.commit("Edit the old decision", {
            safe_push.LOCK: self.text(safe_push.LOCK) + "\n# A comment for the test.\n",
            self.ENTRY: "`Certificate/axioms.lock` gains another comment.\n",
        })
        rep = self.check_guard(safe_push.guard_lock, base, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL")
        self.assertIn("no new line", rep.failed()[0].detail)

    def test_statement_named_in_an_entry_passes(self):
        path = "Elements/BookI/Prop01.lean"
        sha = self.commit("Name a statement change in an entry", {
            path: self.replaced(path, SIGNATURE_OLD, SIGNATURE_NEW),
            self.ENTRY: "I.1 changes its statement.\n",
        })
        rep = self.check_guard(safe_push.guard_statements, BASE, sha, WORK)
        self.assertFalse(rep.failed(), rep.steps)
        self.assertIn("I.1 (the Lean statement changed)", rep.steps[-1].detail)
        self.assertIn("named in the docs/decisions/ lines added", rep.steps[-1].detail)

    def test_deleted_directory_named_in_an_entry_passes(self):
        base = self.commit("A directory for the test", {"mishnah/test/note.md": "A note.\n"})
        sha = self.commit("Name a directory deletion in an entry", {
            self.ENTRY: "`mishnah/test/` is removed.\n",
        }, remove=["mishnah/test"])
        rep = self.check_guard(safe_push.guard_directories, base, sha)
        self.assertFalse(rep.failed(), rep.steps)
        self.assertIn("mishnah/test/", rep.steps[-1].detail)

    def deleted_directory(self, text, source=ENTRY, earlier=None):
        """The directories guard on the deletion of mishnah/test/, with `text` added to
        `source`, an entry or the page, from a base holding the directory and, when given,
        `earlier` as an entry at ENTRY."""
        self.restart()
        write = {"mishnah/test/note.md": "A note.\n"}
        if earlier is not None:
            write[self.ENTRY] = earlier
        base = self.commit("A directory for the test", write)
        if source == DECISIONS:
            text = self.text(DECISIONS) + "\n" + text
        sha = self.commit("Delete the directory", {source: text}, remove=["mishnah/test"])
        return self.check_guard(safe_push.guard_directories, base, sha)

    def test_deleted_directory_linked_from_an_entry_resolves_from_its_folder(self):
        # A link resolves from the folder of the file that holds it, as for a protected
        # path; the directory counts only whole, never a longer path's tail or head.
        for mention, outcome in (("[removed](../../mishnah/test/)", "ok"),
                                 ("[removed](../../mishnah/test)", "ok"),
                                 ("[removed](./../../mishnah/test/)", "ok"),
                                 ("[removed](/mishnah/test/)", "ok"),
                                 ("`mishnah/test/`", "ok"),
                                 ("[removed](../mishnah/test/)", "FAIL"),
                                 ("[removed](../../../mishnah/test/)", "FAIL"),
                                 ("[removed](./mishnah/test/)", "FAIL"),
                                 ("[removed](../../tests/mishnah/test/)", "FAIL"),
                                 ("[removed](../../mishnah/test/note.md)", "FAIL"),
                                 ("`tests/mishnah/test/`", "FAIL"),
                                 ("`mishnah/test/note.md`", "FAIL"),
                                 ("`mishnah/tests/`", "FAIL"),
                                 ("`mishnah/test-old/`", "FAIL")):
            with self.subTest(mention=mention):
                rep = self.deleted_directory(f"- **A deletion for the test.** {mention}.\n")
                self.assertEqual(rep.steps[-1].outcome, outcome, rep.steps)
                if outcome == "FAIL":
                    self.assertIn("no new line", rep.failed()[0].detail)
                    self.assertIn("mishnah/test/", rep.failed()[0].detail)
        rep = self.deleted_directory("- **A deletion for the test.** "
                                     "[removed](../../mishnah/test/).\n", DECISIONS)
        self.assertFalse(rep.failed(), rep.steps)

    # Lines naming a path, `{}` standing for it, and whether they name it: a mention starts
    # the text or follows whitespace or one of ( < [ ` " ' *, after no other character, so
    # that a home folder's path, a drive's, a URL's or another longer one names nothing
    # (the security re-review's forms among them); the forms origin/main counted that
    # start so still count. No path ends a sentence here, so that only where its mention
    # starts decides.
    STARTS = (("{} goes.", "ok"), ("It goes: `{}` now.", "ok"), ("It goes ({}) now.", "ok"),
              ("[{}](https://example.com) goes.", "ok"), ("It goes: <{}> now.", "ok"),
              ('It goes: "{}" now.', "ok"), ("It goes: '{}' now.", "ok"),
              ("It goes: *{}* now.", "ok"), ("It goes: **{}** now.", "ok"),
              ("It goes:\t{} now.", "ok"),
              ("It goes: ~/{} now.", "FAIL"), ("It goes: C:/{} now.", "FAIL"),
              ("It goes: @/{} now.", "FAIL"), ("It goes: https://example.com/~/{} now.", "FAIL"),
              ("It goes: https://example.com/{} now.", "FAIL"), ("It goes: x+{} now.", "FAIL"),
              ("It goes: x:{} now.", "FAIL"), ("It goes: _{}_ now.", "FAIL"),
              ("It goes: x_{} now.", "FAIL"))

    def mention_outcome(self, kind, line, source=ENTRY):
        """The outcome of the files guard ("file": PATH changed) or of the directories guard
        ("directory": mishnah/test/ deleted), with `line` added to `source`, an entry or the
        page."""
        if kind == "directory":
            return self.deleted_directory(line + "\n", source).steps[-1].outcome
        self.restart()
        text = self.text(DECISIONS) + "\n" + line + "\n" if source == DECISIONS else line + "\n"
        sha = self.commit("Name the file", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n", source: text})
        return self.check_guard(safe_push.guard_protected, BASE, sha).steps[-1].outcome

    def test_a_mention_starts_the_text_or_follows_a_space_or_an_opening_mark(self):
        for kind, path in (("file", self.PATH), ("directory", "mishnah/test/")):
            for form, outcome in self.STARTS:
                for source in (self.ENTRY, DECISIONS):
                    with self.subTest(kind=kind, form=form, source=source):
                        line = "- **A mention for the test.** " + form.format(path)
                        if form.startswith("{}"):
                            line = form.format(path)
                        self.assertEqual(self.mention_outcome(kind, line, source), outcome)

    def test_a_directory_may_end_a_sentence(self):
        # As a file may, when its mention holds a slash: its full stop after it, with its
        # closing slash or without; but not a full stop with another, or with a slash, after
        # it.
        for line, outcome in (("The folder removed is mishnah/test.", "ok"),
                              ("The folder removed is mishnah/test/.", "ok"),
                              ("The folder removed is mishnah/test..", "FAIL"),
                              ("The folder removed is mishnah/test./", "FAIL"),
                              ("The folder removed is mishnah/test.md.", "FAIL")):
            for source in (self.ENTRY, DECISIONS):
                with self.subTest(line=line, source=source):
                    self.assertEqual(self.mention_outcome("directory", "- " + line, source),
                                     outcome)

    def test_a_bare_top_level_directory_ends_no_sentence(self):
        # A directory at the root named bare is a word of prose too: "the figures." names
        # no figures/, as origin/main's guards read it (the security re-review's case); its
        # closing slash, the root's anchor or a link before the full stop names it, and so
        # does the bare name with no full stop after it.
        for line, outcome in (("Nothing changes in the figures.", "FAIL"),
                              ("Nothing changes in figures.", "FAIL"),
                              ("The folder removed is figures/.", "ok"),
                              ("The folder removed is /figures.", "ok"),
                              ("The folder removed is [it](../../figures).", "ok"),
                              ("The folder removed is figures, all of it.", "ok")):
            for source in (self.ENTRY, DECISIONS):
                with self.subTest(line=line, source=source):
                    self.restart()
                    text = "- " + line + "\n"
                    if source == DECISIONS:
                        text = self.text(DECISIONS) + "\n" + text
                    sha = self.commit("Delete the figures", {source: text}, remove=["figures"])
                    rep = self.check_guard(safe_push.guard_directories, BASE, sha)
                    self.assertEqual(rep.steps[-1].outcome, outcome, rep.steps)
                    if outcome == "FAIL":
                        self.assertIn("naming them: figures/", rep.failed()[0].detail)

    def test_deleted_directory_needs_a_new_line_of_an_added_entry(self):
        # The earlier entry names the directory by a link that resolves; a copy of its
        # line, re-spaced or not, the entry edited in place, or the line left as it was,
        # renews nothing.
        earlier = "- **An earlier deletion for the test.** [removed](../../mishnah/test/).\n"
        for case, source, text in (
                ("copied", self.MOVED, earlier),
                ("copied and re-spaced", self.MOVED, earlier.replace(" [", " \t [")),
                ("edited in place", self.ENTRY, earlier.replace("earlier", "revised")),
                ("unchanged", self.MOVED, "- **A new decision for the test.** It names "
                                          "nothing.\n")):
            with self.subTest(case=case):
                rep = self.deleted_directory(text, source, earlier)
                self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
                self.assertIn("no new line", rep.failed()[0].detail)
        rep = self.deleted_directory("- **A later deletion for the test.** In words of its "
                                     "own, [the folder](../../mishnah/test/) goes.\n",
                                     self.MOVED, earlier)
        self.assertFalse(rep.failed(), rep.steps)

    def test_page_text_counts_wherever_it_stands(self):
        # No part of the page is generated: a line appended at its end names the file.
        sha = self.commit("Name a protected change on the page", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
            DECISIONS: self.text(DECISIONS) + f"\n- `{self.PATH}` changes.\n",
        })
        rep = self.check_guard(safe_push.guard_protected, BASE, sha)
        self.assertFalse(rep.failed(), rep.steps)
        self.assertIn(f"each named in {DECISIONS}: {self.PATH};", rep.steps[-1].detail)

    def test_page_deleted_with_a_protected_change_is_refused(self):
        # The page's removed lines name the file by a link resolved from the page's folder,
        # though the deleted page's hunks have no path.
        base = self.commit("A page line naming the file by a link", {
            DECISIONS: self.text(DECISIONS) + f"\n- [The file](../../{self.PATH}) changes.\n",
        })
        sha = self.commit("Delete the page", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
        }, remove=[DECISIONS])
        rep = self.check_guard(safe_push.guard_protected, base, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
        self.assertIn(f"naming them: {self.PATH}", rep.failed()[0].detail)

    def protected_refusal(self, files, text, entry=ENTRY):
        """guard_protected's refusal of a commit that gives each of `files` a comment and
        adds `entry` holding `text`."""
        writes = {path: self.text(path) + "\n# A comment for the test.\n" for path in files}
        sha = self.commit("Change protected files, with an entry", {**writes, entry: text})
        rep = self.check_guard(safe_push.guard_protected, BASE, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
        self.assertIn(f"naming them: {', '.join(sorted(files))} (", rep.failed()[0].detail)
        return rep.failed()[0].detail

    def test_files_listed_a_line_each_as_on_the_page_are_named_in_the_refusal(self):
        # The re-review's first case: an entry lists its protected files one to a line, as
        # the page's entry for #184 does. Those lines stand on the page already, so they
        # name nothing, and the refusal says which lines did not count, and why. The same
        # names in a sentence of the entry's own count.
        files = ("scripts/safe_push.py", "scripts/check_release_gate.py")
        for path in files:
            self.assertIn(f"\n  `{path}`,\n", self.text(DECISIONS))
        detail = self.protected_refusal(files, "- **The release gate, for the test "
                                        "(tooling).** Each file gains a comment. The "
                                        "protected files changed are:\n"
                                        + "".join(f"  `{path}`,\n" for path in files))
        self.assertIn("lines of the entries added that did not count", detail)
        self.assertIn("in a sentence of its own, never on a line or in a list repeated from "
                      "an older entry", detail)
        for n in (2, 3):
            self.assertIn(f"\n  {self.ENTRY}:{n}: {safe_push.IN_RECORD}", detail)
        self.assertNotIn(f"{self.ENTRY}:1:", detail)
        self.restart()
        sha = self.commit("Change them, with an entry naming them in a sentence", {
            **{path: self.text(path) + "\n# A comment for the test.\n" for path in files},
            self.ENTRY: f"- **The release gate, for the test (tooling).** `{files[0]}` and "
                        f"`{files[1]}` each gain a comment.\n"})
        rep = self.check_guard(safe_push.guard_protected, BASE, sha)
        self.assertFalse(rep.failed(), rep.steps)

    def test_files_listed_after_an_older_entrys_words_are_named_in_the_refusal(self):
        # The re-review's second case: a revert of #184 whose entry lists its seven
        # protected files in #184's order, after the words #184's entry uses, wrapped
        # otherwise: twelve words in a row that the page holds, so no line holding one of
        # them counts.
        listed = (".github/pull_request_template.md", ".github/workflows/ci.yml",
                  ".github/workflows/release-gate.yml", "scripts/safe_push.py",
                  "scripts/check_release_gate.py", "scripts/test_safe_push.py",
                  "tests/test_release_gate.py")
        text = textwrap.fill(
            "- **#184 reverted, for the test (tooling).** It undoes the release hold. The "
            "protected files changed are: " + ", ".join(f"`{path}`" for path in listed) + ".",
            72, subsequent_indent="  ", break_long_words=False) + "\n"
        self.assertFalse(set(text.splitlines()) & set(self.text(DECISIONS).splitlines()))
        changed = ("scripts/check_release_gate.py", "tests/test_release_gate.py")
        detail = self.protected_refusal(changed, text)
        # Named: each line that did not count and names a file changed. Not named: the
        # lines that did not count and name only files the push leaves alone.
        lines = text.splitlines()
        holding = [n for n, line in enumerate(lines, 1)
                   if any(f"`{path}`" in line for path in changed)]
        others = [n for n, line in enumerate(lines, 1) if "`" in line and n not in holding]
        self.assertTrue(holding and others, lines)
        for n in holding:
            self.assertIn(f"\n  {self.ENTRY}:{n}: {safe_push.IN_RUN}", detail)
        for n in others:
            self.assertNotIn(f"{self.ENTRY}:{n}:", detail)

    def test_refusal_names_no_line_that_names_nothing_asked_for(self):
        # The re-review's case: an entry whose code fences, and a line of output between
        # them, are lines the record holds already. They did not count, but name nothing a
        # guard asks for, so no refusal names them; the line copied from the earlier
        # entry that names the file changed is named. The lock changed too, which no line
        # names: its refusal names no line of the entry at all.
        base = self.commit("An earlier decision with a fence", {
            self.ENTRY: "- **An earlier decision for the test.** It names one file:\n"
                        f"  `{self.PATH}`, which gains a comment.\n"
                        "  ```text\n  a line of output for the test\n  ```\n"})
        sha = self.commit("A protected change with a fence", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
            safe_push.LOCK: self.text(safe_push.LOCK) + "\n# A comment for the test.\n",
            self.MOVED: "- **A new decision for the test, in words of its own.** It changes "
                        "this one:\n"
                        f"  `{self.PATH}`, which gains a comment.\n"
                        "```text\na line of output for the test\n```\n"})
        refused, entries = safe_push.entry_changes(WORK, base, sha)
        self.assertEqual(refused, [])
        self.assertEqual([str(u) for u in entries[self.MOVED].uncounted],
                         [f"{self.MOVED}:{n}: {safe_push.IN_RECORD}" for n in (2, 3, 4, 5)])
        rep = self.check_guard(safe_push.guard_protected, base, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
        detail = rep.failed()[0].detail
        self.assertIn(f"\n  {self.MOVED}:2: {safe_push.IN_RECORD}", detail)
        for n in (1, 3, 4, 5):
            self.assertNotIn(f"{self.MOVED}:{n}:", detail)
        rep = self.check_guard(safe_push.guard_lock, base, sha)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
        self.assertNotIn(self.MOVED, rep.failed()[0].detail)
        self.assertNotIn("lines of the entries added", rep.failed()[0].detail)

    def test_short_entry_sharing_a_line_with_an_older_one_is_an_entry(self):
        # Two routine entries, alike but for the proposition and sharing a line: Git's copy
        # detection calls the second a copy of the first, but it is an entry of its own,
        # accepted; its lines that copy the first count for nothing, and are named.
        older = "docs/decisions/2026-10-21-iii-31.md"
        newer = "docs/decisions/2026-10-21-iii-32.md"
        shared = "  Its record is stamped, as WORKFLOW, section 6, asks of a review done.\n"
        base = self.commit("III.31 checked", {older: "- **III.31 checked (text).**\n" + shared})
        sha = self.commit("III.32 checked", {newer: "- **III.32 checked (text).**\n" + shared})
        status, *paths = git(WORK, "diff", "--name-status", "-C", "-C", base, sha).split()
        self.assertEqual((status[0], paths), ("C", [older, newer]))
        rep = self.check_guard(safe_push.guard_entries, base, sha)
        self.assertEqual([(s.outcome, s.detail) for s in rep.steps],
                         [("ok", f"added: {newer}")])
        refused, entries = safe_push.entry_changes(WORK, base, sha)
        self.assertEqual((refused, list(entries)), ([], [newer]))
        self.assertEqual([str(u) for u in entries[newer].uncounted],
                         [f"{newer}:1: {safe_push.IN_RUN}", f"{newer}:2: {safe_push.IN_RECORD}"])

    def test_advised_revert_keeps_the_record_and_passes_the_guards(self):
        # A merged pull request that adds an entry listing its protected files a line each,
        # appends to the page and changes the files, reverted as revert_advice says: the
        # revert's entry names each file in a sentence of its own, and passes; a list
        # repeated from the merge's entry names nothing, and the refusal says so.
        other = "scripts/check_links.py"
        feature = self.commit("A change with its entry", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
            other: self.text(other) + "\n# A comment for the test.\n",
            self.ENTRY: "- **A change for the test.** Two files gain a comment. The protected "
                        f"files changed are:\n  `{self.PATH}`,\n  `{other}`.\n",
            DECISIONS: self.text(DECISIONS) + "\n- **A page line for the test.** It stays.\n",
        })
        self.restart()
        git(WORK, "merge", "--quiet", "--no-ff", "--no-edit", feature)
        merge = git(WORK, "rev-parse", "HEAD").strip()
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{merge}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        branch = f"revert-{merge[:12]}"
        self.addCleanup(lambda: git(WORK, "branch", "-D", branch, check=False))
        self.addCleanup(self.restart)
        ctx = safe_push.Context(WORK, merge, BASE, 1, "", None, {})
        advice = safe_push.revert_advice(ctx, "tooling")
        entry = f"docs/decisions/{datetime.date.today().isoformat()}-revert-{merge[:12]}.md"
        lines = [line.strip() for line in advice.splitlines()[1:]]
        self.assertEqual(lines, [
            f"git switch -c {branch} origin/main",
            f"git revert --no-commit -m 1 {merge}",
            f"git restore --source=origin/main --staged --worktree -- docs/decisions/ "
            f"{DECISIONS}",
            f"# write {entry}: the revert and why, naming each protected file, statement",
            "# and lock that it changes, as an entry of any change must, each in a sentence",
            "# of the entry's own, never on a line or in a list repeated from an older entry",
            f"git add -- {entry}",
            "git commit --no-edit",
            f"git safe-push --branch {branch} --label tooling"])
        for line in lines[:-1]:
            if line.startswith("# write "):
                (WORK / entry).write_text(f"- **The merge reverted, for the test.** "
                                          f"Reverting it takes the comment out of "
                                          f"`{self.PATH}`, and out of `{other}` too.\n")
            elif not line.startswith("#"):
                git(WORK, *shlex.split(line)[1:])
        for path in (self.PATH, other):
            self.assertEqual(self.text(path), safe_push.show(WORK, BASE, path))
        for path in (DECISIONS, self.ENTRY):
            self.assertEqual(self.text(path), safe_push.show(WORK, merge, path))
        self.assertIn("Revert", git(WORK, "log", "-1", "--format=%s"))
        head = git(WORK, "rev-parse", "HEAD").strip()
        for guard, args in self.four_guards() + ((safe_push.guard_entries, ()),):
            with self.subTest(guard=guard.__name__):
                rep = self.check_guard(guard, merge, head, *args)
                self.assertFalse(rep.failed(), rep.steps)
        # The revert's entry written as the merge's lists the files: those lines name nothing.
        listed = self.commit("The revert's entry as a list", {
            entry: "- **The merge reverted, for the test.** The protected files changed "
                   f"are:\n  `{self.PATH}`,\n  `{other}`.\n"})
        rep = self.check_guard(safe_push.guard_protected, merge, listed)
        self.assertEqual(rep.steps[-1].outcome, "FAIL", rep.steps)
        self.assertIn(f"naming them: {other}, {self.PATH} (", rep.failed()[0].detail)
        for n in (2, 3):
            self.assertIn(f"\n  {entry}:{n}: {safe_push.IN_RECORD}", rep.failed()[0].detail)
        # Without restoring the record, the revert deletes the merge's entry: refused.
        self.restart(merge)
        git(WORK, "revert", "--no-edit", "-m", "1", merge)
        bare = git(WORK, "rev-parse", "HEAD").strip()
        rep = self.check_guard(safe_push.guard_entries, merge, bare)
        self.assertIn(f"{self.ENTRY}: deleted", rep.failed()[0].detail)

    def test_advised_revert_restores_only_what_origin_main_holds(self):
        # A main with no docs/decisions/, as before its README was added: the advice
        # restores the page alone, since git restore stops at a path its source lacks, and,
        # followed, passes the guards. That main is made in the test's own clone by
        # removing whatever the folder holds there, the README and any entries, so the
        # test holds however many entries the repository has.
        self.advised_revert_without_entries()

    def test_advised_revert_restores_only_what_origin_main_holds_with_entries(self):
        # The same, from a baseline whose folder holds an entry besides the README, as main
        # does once a pull request has added its first entry file.
        self.commit("An entry in the baseline, for the test", {
            "docs/decisions/2026-10-21-baseline-for-the-test.md":
                "- **An entry in the baseline, for the test.** It names nothing.\n"})
        self.advised_revert_without_entries()

    def advised_revert_without_entries(self):
        held = git(WORK, "ls-files", "-z", "--", safe_push.ENTRIES).split("\0")
        held = sorted(p for p in held if p)
        self.assertIn(self.README, held)
        start = self.commit("No folder of entries yet", remove=held)
        self.assertEqual(git(WORK, "ls-files", "--", safe_push.ENTRIES).strip(), "")
        self.assertFalse((WORK / safe_push.ENTRIES).exists())
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{start}:refs/heads/main")
        feature = self.commit("A change named on the page", {
            self.PATH: self.text(self.PATH) + "\n# A comment for the test.\n",
            DECISIONS: self.text(DECISIONS) + f"\n- **A change for the test.** `{self.PATH}` "
                                              "gains a comment.\n",
        })
        self.restart(start)
        git(WORK, "merge", "--quiet", "--no-ff", "--no-edit", feature)
        merge = git(WORK, "rev-parse", "HEAD").strip()
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{merge}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        branch = f"revert-{merge[:12]}"
        self.addCleanup(lambda: git(WORK, "branch", "-D", branch, check=False))
        self.addCleanup(self.restart)
        advice = safe_push.revert_advice(safe_push.Context(WORK, merge, start, 1, "", None, {}),
                                         "tooling")
        entry = f"docs/decisions/{datetime.date.today().isoformat()}-revert-{merge[:12]}.md"
        lines = [line.strip() for line in advice.splitlines()[1:]]
        self.assertIn(f"git restore --source=origin/main --staged --worktree -- {DECISIONS}",
                      lines)
        for line in lines[:-1]:
            if line.startswith("# write "):
                (WORK / entry).parent.mkdir(parents=True, exist_ok=True)
                (WORK / entry).write_text(f"- **The merge reverted, for the test.** Reverting "
                                          f"it takes the comment out of `{self.PATH}`.\n")
            elif not line.startswith("#"):
                git(WORK, *shlex.split(line)[1:])
        self.assertEqual(self.text(self.PATH), safe_push.show(WORK, start, self.PATH))
        self.assertEqual(self.text(DECISIONS), safe_push.show(WORK, merge, DECISIONS))
        head = git(WORK, "rev-parse", "HEAD").strip()
        for guard, args in self.four_guards() + ((safe_push.guard_entries, ()),):
            with self.subTest(guard=guard.__name__):
                rep = self.check_guard(guard, merge, head, *args)
                self.assertFalse(rep.failed(), rep.steps)


class ProtectedPaths(Edge):
    """(1) The guards and the check scripts are origin/main's; a protected path changes
    only with a decisions entry naming it, and the label."""

    RETAINED_AXIOM = "Tacit.line_unique"

    def test_protected_change_without_a_decision_refused(self):
        for path in ("scripts/check_style.py", ".github/workflows/ci.yml",
                     "tests/model/MODEL.md", "review/terms.toml", ".gitattributes",
                     ".gitignore", "lakefile.lean", "Audit/Overlaps.lean", "Audit.lean",
                     "model/Model/Audit.lean", "model/Model.lean",
                     "model/lakefile.toml", "model/lakefile.lean", "model/lean-toolchain",
                     "model/lake-manifest.json", "model/lock.sha256"):
            with self.subTest(path=path):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                old = self.text(path) if (WORK / path).exists() else ""
                self.commit(f"Touch {path}", {path: old + "\n# for the test\n"})
                out = self.assertRefused(self.safe_push(), "protected paths", path)
                self.assertEqual(self.guard(out, "protected paths"), "FAIL", out)

    def test_decision_naming_another_file_does_not_count(self):
        changes = {"scripts/check_style.py": self.text("scripts/check_style.py") + "\n# x\n"}
        changes.update(self.decision("A comment in `scripts/check_links.py`."))
        self.commit("Touch check_style.py, naming check_links.py", changes)
        self.assertRefused(self.safe_push(), "naming them: scripts/check_style.py")

    def test_decision_naming_a_longer_path_does_not_count(self):
        # #96: a protected path is named whole. A line naming tests/model/lock.sha256 does
        # not name model/lock.sha256, nor one naming model/lakefile.toml the root's
        # lakefile.toml, nor one naming model/lean-toolchain the root's lean-toolchain; and
        # at the other end, a line naming Audit.lean.orig does not name Audit.lean.
        for path, other in (("model/lock.sha256", "tests/model/lock.sha256"),
                            ("lakefile.toml", "model/lakefile.toml"),
                            ("lean-toolchain", "model/lean-toolchain"),
                            (".gitignore", "model/.gitignore"),
                            ("Audit.lean", "Audit.lean.orig"),
                            ("model/Model/Audit.lean", "tests/model/Model/Audit.lean"),
                            ("model/Model/Audit.lean", "model/Model/Audit.lean.orig"),
                            ("model/Model.lean", "tests/model/Model.lean"),
                            ("model/Model.lean", "model/Model.lean.orig"),
                            ("model/lakefile.toml", "model/lakefile.toml.bak"),
                            ("lakefile.toml", "/model/lakefile.toml")):
            with self.subTest(path=path):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                changes = {path: self.text(path) + "\n# for the test\n"}
                changes.update(self.decision(f"`{other}` is named, for the test."))
                self.commit(f"Touch {path}, naming {other}", changes)
                out = self.assertRefused(self.safe_push(), f"naming them: {path}")
                self.assertEqual(self.guard(out, "protected paths"), "FAIL", out)

    def test_decision_naming_the_path_by_a_relative_link_counts(self):
        # From the decisions page, docs/briefs/, a link reaches the root through ../../. A
        # path that ends a sentence, its period after it, is named whole too.
        for path, line in (
                ("model/lock.sha256", "[the model's hash](../../model/lock.sha256) is renewed."),
                ("model/lock.sha256", "[the model's hash](/model/lock.sha256) is renewed."),
                ("Audit/Overlaps.lean", "`Audit/Overlaps.lean` gains a lemma."),
                ("model/Model/Audit.lean",
                 "[the model's audit](../../model/Model/Audit.lean) changes."),
                ("model/Model.lean", "[the model's root](../../model/Model.lean) changes."),
                (".gitignore", "[the rule](../../.gitignore) is added."),
                ("Audit.lean", "The audit's root is Audit.lean.")):
            with self.subTest(path=path):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                changes = {path: self.text(path) + "\n-- for the test\n"}
                changes.update(self.decision(line))
                self.commit(f"Touch {path}, naming it", changes)
                out = self.safe_push("--dry-run").stdout
                self.assertEqual(self.guard(out, "protected paths"), "ok", out)
                self.assertIn(f"each named in {DECISIONS}: {path};", out)

    def test_decision_relative_link_must_resolve_from_decisions_page(self):
        # A protected judged file and a check both need their actual path named.
        for path in ("model/Model/Audit.lean", "scripts/check_style.py"):
            for mention, outcome in (
                    (f"[file](../{path})", "FAIL"),
                    (f"[file](../../../{path})", "FAIL"),
                    (f"[file](./{path})", "FAIL"),
                    (f"[file](../../{path})", "ok"),
                    (f"[file](./../../{path})", "ok"),
                    (f"[file](.././../{path})", "ok"),
                    (f"[file](/{path})", "ok"),
                    (f"`{path}`", "ok"),
                    (path, "ok")):
                with self.subTest(path=path, mention=mention):
                    git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                    changes = {path: self.text(path) + "\n# for the test\n"}
                    changes.update(self.decision(f"{mention} changes."))
                    sha = self.commit("Touch a protected file with a path mention", changes)
                    rep, out = safe_push.Report(), io.StringIO()
                    with contextlib.redirect_stdout(out):
                        files = safe_push.guard_protected(WORK, BASE, sha, rep)
                    self.assertEqual(files, [path])
                    self.assertEqual(self.guard(out.getvalue(), "protected paths"),
                                     outcome, out.getvalue())

    def test_audit_and_the_models_audit_and_build_files_stay_judged(self):
        # #96: Audit/, Audit.lean, the model's audit and its root, and the model's build
        # files are protected, yet still what the checks judge, so a check change stays
        # apart from them (keep_apart); the rest of the protected paths and the guides
        # are not judged.
        judged = ["Audit.lean", "Audit/Overlaps.lean", "model/Model.lean",
                  "model/Model/Audit.lean", "model/README.md",
                  "model/lake-manifest.json", "model/lakefile.lean", "model/lakefile.toml",
                  "model/lean-toolchain", "model/lock.sha256"]
        apart = ["scripts/check_links.py", "lakefile.toml", "lean-toolchain", ".gitignore",
                 "tests/model/lock.sha256", "docs/WORKFLOW.md"]
        sha = self.commit("Touch protected and judged files", {
            p: (self.text(p) if (WORK / p).exists() else "") + "\n-- for the test\n"
            for p in judged + apart})
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha), judged)
        for p in judged + apart:
            self.assertEqual(safe_push.is_protected(p), p != "model/README.md"
                             and p != "docs/WORKFLOW.md", p)

    def test_weakened_check_with_the_code_it_would_catch_refused(self):
        # The commit makes check_fidelity.py pass whatever it finds, and changes a Lean
        # file under a review record: origin/main's copy finds the record stale, and the
        # commit changes what the checks judge as well as a check, so it is refused (the
        # spec review: noting it was not enough). The pages are regenerated: PROGRAM.md's
        # status table counts the stale record.
        path = "scripts/check_fidelity.py"
        lean = "Elements/BookI/Prop01.lean"
        changes = {path: self.replaced(path, 'if __name__ == "__main__":\n',
                                       'if __name__ == "__main__":\n    sys.exit(0)\n'),
                   lean: self.text(lean) + "\n-- A comment for the test.\n"}
        changes.update(self.decision(f"`{path}` is changed for the test."))
        self.regenerated_commit("Weaken check_fidelity.py", changes)
        out = self.assertRefused(self.safe_push(), "check change kept apart", lean,
                                 "a pull request of its own")
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertEqual(self.guard(out, "check change kept apart"), "FAIL", out)
        self.assertEqual(len(git(WORK, "worktree", "list").splitlines()), 1)

    def test_check_change_alone_noted_for_the_security_review(self):
        # A change to render.py, with the pages it regenerates and its decisions entry, and
        # nothing else: origin/main's render.py finds the pages stale, which is noted for
        # the security review, in the body and beside the checklist at --merge.
        path = "scripts/render.py"
        changes = {path: self.replaced(path, '"This page keeps three things apart."',
                                       '"This page keeps three things apart, for the test."')}
        changes.update(self.decision(f"`{path}` is changed for the test."))
        sha = self.regenerated_commit("Reword render.py", changes)
        r = self.safe_push("--label", "tooling", "--ready")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "generated pages (origin/main's checks)"), "note", out)
        self.assertEqual(self.guard(out, "generated pages (the commit's checks)"), "ok", out)
        self.assertIsNone(self.guard(out, "check change kept apart"), out)
        self.assertEqual(self.origin_branch(), sha)
        (pr,) = self.gh_state()["prs"]
        self.assertIn("security-review", pr["labels"])
        self.assertIn("generated pages (origin/main's checks)", pr["body"])
        # Review note 11: --merge shows the notes beside the checklist, for the reviews.
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        r = self.safe_push("--merge", "1", "--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "pre-flight notes"), "note", out)
        notes = out[out.index("pre-flight notes"):]
        self.assertIn("generated pages (origin/main's checks)", notes)

    def test_renderer_change_with_content_is_not_kept_apart(self):
        # Pages gone stale under origin/main's render.py show a renderer change, not a
        # check's verdict: render.py may change with what it renders (a restatement's
        # note does), and the commit's own pass still needs the pages current.
        path = "scripts/render.py"
        changes = {path: self.replaced(path, '"This page keeps three things apart."',
                                       '"This page keeps three things apart, for the test."'),
                   "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"}
        changes.update(self.decision(f"`{path}` is changed for the test."))
        sha = self.regenerated_commit("Reword render.py, with a line of reading", changes)
        r = self.safe_push("--label", "tooling")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "generated pages (origin/main's checks)"), "note", out)
        self.assertIn("generated pages (origin/main's checks): stale", out)
        self.assertIsNone(self.guard(out, "render.py (origin/main's checks)"), out)
        self.assertIsNone(self.guard(out, "check change kept apart"), out)
        self.assertEqual(self.origin_branch(), sha)

    def test_renderer_validation_loosened_with_content_is_kept_apart(self):
        # render.py checks docs/program.toml: a stage it did not know, allowed in render.py
        # and used in program.toml in one commit, makes origin/main's render.py fail
        # outright. That is a verdict, not stale pages.
        # The first book's stage line is read from the file, so that the program's own
        # words can change without this test.
        path, program = "scripts/render.py", "docs/program.toml"
        text = self.text(program)
        stage = re.search(r'(?m)^stage = "[^"\n]*"$', text)
        self.assertIsNotNone(stage, f"{program}: no stage line")
        changes = {path: self.replaced(path, 'PROGRAM_STAGES = ("brief",',
                                       'PROGRAM_STAGES = ("anything", "brief",'),
                   program: text[:stage.start()] + 'stage = "anything"' + text[stage.end():]}
        changes.update(self.decision(f"`{path}` is changed for the test."))
        self.regenerated_commit("Loosen render.py's check of program.toml, and use it", changes)
        out = self.assertRefused(self.safe_push("--dry-run"), "check change kept apart",
                                 "docs/program.toml")
        self.assertEqual(self.guard(out, "render.py (origin/main's checks)"), "note", out)
        self.assertEqual(self.guard(out, "check change kept apart"), "FAIL", out)

    def test_check_change_failing_its_own_pass_refused(self):
        # render.py's output changes and the pages are not regenerated: origin/main's
        # render.py finds them current, the commit's own finds them stale, and that refuses.
        path = "scripts/render.py"
        changes = {path: self.replaced(path, '"This page keeps three things apart."',
                                       '"This page keeps three things apart, for the test."')}
        changes.update(self.decision(f"`{path}` is changed for the test."))
        self.commit("Reword render.py, the pages not regenerated", changes)
        out = self.assertRefused(self.safe_push("--dry-run"),
                                 "generated pages (the commit's checks)")
        self.assertEqual(self.guard(out, "generated pages (origin/main's checks)"), "ok", out)
        self.assertEqual(self.guard(out, "generated pages (the commit's checks)"), "FAIL", out)

    def reproof(self) -> dict:
        """III.1 re-proved without one tacit rule (as a re-proof would leave it, Lean
        aside): its Lean file, its record re-stamped, facts.json without the rule; and the
        certificate's expectations moved with it, with a decisions line naming them."""
        lean, record = "Elements/BookIII/Prop01.lean", "review/III/01.toml"
        expect = "tests/certificate_expectations.json"
        new_lean = self.text(lean) + "\n-- A re-proof that no longer needs line_unique.\n"
        stamped = re.sub(r'(?m)^lean = "[^"]*"',
                         f'lean = "{safe_push.heath._sha(new_lean.encode())}"', self.text(record))
        stamped = re.sub(r'(?m)^commit = "[^"]*"', 'commit = "abc1234"', stamped)
        facts = json.loads(self.text("facts.json"))
        removed = 0
        for p in facts["propositions"]:
            if p["ref"] in ("III.1", "III.1 Por."):
                self.assertIn(self.RETAINED_AXIOM, p["axioms"])
                p["axioms"].remove(self.RETAINED_AXIOM)
                removed += 1
        self.assertEqual(removed, 2)
        expectations = json.loads(self.text(expect))
        for ref in ("III.1", "III.1 Por."):
            pin = next(x for x in expectations["expectations"]
                       if (x.get("ref"), x["field"]) == (ref, "axioms") and "count" in x)
            self.assertEqual(pin["count"]["prefix"], "Tacit.")
            pin["count"]["is"] -= 1
            if "equals" in pin:
                pin["equals"].remove(self.RETAINED_AXIOM)
        changes = {lean: new_lean, record: stamped,
                   "facts.json": json.dumps(facts, indent=2, ensure_ascii=False) + "\n",
                   expect: json.dumps(expectations, indent=2, ensure_ascii=False) + "\n"}
        changes.update(self.decision(f"`{expect}`: III.1's re-proof uses one tacit rule fewer."))
        return changes

    def test_pinned_values_move_with_their_content(self):
        # The final review's blocking finding: a re-proof that moves an expected count
        # could land in no order. The expectations are pinned values: they change with
        # the content, origin/main's failure is noted, and the commit's own pass holds.
        expectations = json.loads(self.text(self.EXPECT))["expectations"]
        count = next(x["count"]["is"] for x in expectations
                     if (x.get("ref"), x["field"]) == ("III.1", "axioms") and "count" in x)
        self.regenerated_commit("Re-prove III.1, its expectations with it", self.reproof())
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertIn(f"has {count - 1} names beginning 'Tacit.', not {count}", out)
        self.assertEqual(self.guard(out, "review records (the commit's checks)"), "ok", out)
        self.assertEqual(self.guard(out, "pinned values"), "note", out)
        self.assertIsNone(self.guard(out, "check change kept apart"), out)

    def test_pinned_values_with_check_code_kept_apart(self):
        # The same, with a change to check code as well: kept apart, pinned values or not.
        path = "scripts/check_fidelity.py"
        changes = self.reproof()
        changes[path] = self.text(path) + "\n# A comment for the test.\n"
        changes[DECISIONS] += f"\n- **Another decision for the test.** `{path}` gains a line.\n"
        self.regenerated_commit("Re-prove III.1, and change check_fidelity.py", changes)
        out = self.assertRefused(self.safe_push("--dry-run"), "check change kept apart",
                                 "Elements/BookIII/Prop01.lean")
        self.assertIsNone(self.guard(out, "pinned values"), out)

    EXPECT = "tests/certificate_expectations.json"

    def test_expectation_dropped_with_its_regression_kept_apart(self):
        # This test deliberately injects angle_le_two_right, a locked tacit rule absent from
        # III.1's axiom list both before and after the second axiom retirement (after it,
        # III.1 rests on circle_eq), and drops the corresponding axioms expectations. It
        # verifies that this check change must remain separate from the content change. A
        # retired theorem name such as centre_unique cannot be the injection: the commit's
        # own pass refuses it.
        lean, record = "Elements/BookIII/Prop01.lean", "review/III/01.toml"
        new_lean = self.text(lean) + "\n-- A re-proof that uses angle_le_two_right.\n"
        stamped = re.sub(r'(?m)^lean = "[^"]*"',
                         f'lean = "{safe_push.heath._sha(new_lean.encode())}"', self.text(record))
        stamped = re.sub(r'(?m)^commit = "[^"]*"', 'commit = "abc1234"', stamped)
        facts = json.loads(self.text("facts.json"))
        for p in facts["propositions"]:
            if p["ref"] == "III.1":
                self.assertNotIn("Tacit.angle_le_two_right", p["axioms"])
                p["axioms"] = sorted(p["axioms"] + ["Tacit.angle_le_two_right"])
        data = json.loads(self.text(self.EXPECT))
        count = next(x["count"]["is"] for x in data["expectations"]
                     if (x.get("ref"), x["field"]) == ("III.1", "axioms") and "count" in x)
        data["expectations"] = [x for x in data["expectations"]
                                if (x.get("ref"), x["field"]) != ("III.1", "axioms")]
        changes = {lean: new_lean, record: stamped,
                   "facts.json": json.dumps(facts, indent=2, ensure_ascii=False) + "\n",
                   self.EXPECT: json.dumps(data, indent=2, ensure_ascii=False) + "\n"}
        changes.update(self.decision(f"`{self.EXPECT}`: tidied."))
        self.regenerated_commit("III.1 uses angle_le_two_right, its expectation dropped", changes)
        out = self.assertRefused(self.safe_push("--dry-run"), "check change kept apart",
                                 "drops or loosens an expectation")
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertIn(f"has {count + 1} names beginning 'Tacit.', not {count}", out)
        self.assertEqual(self.guard(out, "review records (the commit's checks)"), "ok", out)
        self.assertEqual(self.guard(out, "check change kept apart"), "FAIL", out)
        self.assertIsNone(self.guard(out, "pinned values"), out)

    def expectations_changed(self, change) -> str:
        """A commit that changes a Lean file, which the checks judge, and the certificate's
        expectations by `change`: given the parsed file, it edits it in place and returns
        None, or returns the file's new text, or False to delete the file."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        data = json.loads(self.text(self.EXPECT))
        result = change(data)
        lean = "Elements/BookIII/Prop01.lean"
        write = {lean: self.text(lean) + "\n-- A line for the test.\n"}
        if result is not False:
            write[self.EXPECT] = result if isinstance(result, str) else \
                json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        return self.commit("A Lean line, and the expectations changed", write,
                           remove=[self.EXPECT] if result is False else ())

    def test_only_expectations_kept_whole_are_pinned_values(self):
        # Each of origin/main's expectations stays, by its ref, field and law, its includes
        # and excludes the same or grown, and only count.is and equals take other values:
        # then the change moves with the content. Anything else is a check change.
        def entry(data, ref, field="axioms"):
            return next(x for x in data["expectations"] if (x.get("ref"), x["field"]) == (ref, field))

        def drop(key, ref="III.1", field="axioms"):
            def change(data):
                del entry(data, ref, field)[key]
            return change

        def moved(data):
            for x in data["expectations"]:
                if "count" in x:
                    x["count"]["is"] -= 1
        weakened = {
            "an expectation removed": lambda d: d["expectations"].remove(entry(d, "III.1")),
            "every expectation removed": lambda d: d.update(expectations=[]),
            "its excludes removed": drop("excludes"),
            "its includes emptied": lambda d: entry(d, "I.5", "inherited").update(includes=[]),
            "its excludes emptied": lambda d: entry(d, "III.1").update(excludes=[]),
            "its count removed": drop("count"),
            "its equals removed": drop("equals", "III.1 Por.", "of"),
            "its count's prefix changed": lambda d: entry(d, "III.1")["count"].update(
                prefix="Tacit.centre"),
            "its ref changed": lambda d: entry(d, "III.1").update(ref="III.2"),
            "the file deleted": lambda d: False,
            "the file unreadable": lambda d: "{ not JSON\n",
        }
        for name, change in weakened.items():
            with self.subTest(name):
                refused, out = self.kept_apart(self.expectations_changed(change),
                                               "python3 scripts/check_fidelity.py")
                self.assertTrue(refused, out)
                self.assertIn("drops or loosens an expectation", out)
                self.assertNotIn("pinned values", out)
        kept = {
            "the counts moved": moved,
            "an equals moved": lambda d: entry(d, "III.1 Por.", "of").update(equals="III.2"),
            "its includes grown": lambda d: entry(d, "I.5", "inherited")["includes"].append(
                self.RETAINED_AXIOM),
            "its excludes grown": lambda d: entry(d, "III.1")["excludes"].append(
                self.RETAINED_AXIOM),
            "a field added": lambda d: entry(d, "III.1", "attached").update(excludes=["III.2"]),
            "an expectation added": lambda d: d["expectations"].append(
                {"ref": "III.2", "field": "axioms", "includes": [self.RETAINED_AXIOM],
                 "why": "A new expectation, for the test."}),
            "a why reworded": lambda d: entry(d, "III.1").update(why="Reworded."),
        }
        for name, change in kept.items():
            with self.subTest(name):
                refused, out = self.kept_apart(self.expectations_changed(change),
                                               "python3 scripts/check_fidelity.py")
                self.assertFalse(refused, out)
                self.assertIn("pinned values", out)

    # The count markers of T1 (#177): Certificate/FIELDS.md gives the lock's count of its
    # words between count markers, which render.py fills and check_fidelity.py checks.
    FIELDS = "Certificate/FIELDS.md"
    WORD_COUNT = re.compile(r"(<!-- count:vocabulary -->)([0-9]+)(<!-- /count -->)")

    def word_added(self) -> dict:
        """A new word in the vocabulary, as a change to the library leaves it, Lean aside:
        facts.json with the word, and the lock written from it by `check_fidelity.py
        --write-lock`."""
        facts = json.loads(self.text("facts.json"))
        self.assertNotIn("PlantedWord", facts["vocabulary"])
        facts["vocabulary"]["PlantedWord"] = "def : Prop := True"
        changes = {"facts.json": json.dumps(facts, indent=2, ensure_ascii=False) + "\n"}
        (WORK / "facts.json").write_text(changes["facts.json"])
        r = subprocess.run([sys.executable, "scripts/check_fidelity.py", "--write-lock"],
                           cwd=WORK, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        changes[self.LOCK] = self.text(self.LOCK)
        self.assertIn('"PlantedWord" = "def : Prop := True"', changes[self.LOCK])
        return changes

    def word_count(self, text: str) -> int:
        (match,) = self.WORD_COUNT.finditer(text)
        return int(match[2])

    def test_count_values_move_with_their_content(self):
        # The content branch of #75 could land in no order: a new word in the lock moves
        # FIELDS.md's count of the words, and origin/main's checks fail on the lock. The
        # count is a pinned value: it changes with the content, origin/main's failure is
        # noted, and the commit's own pass holds the count to the lock.
        changes = self.word_added()
        changes.update(self.decision(f"A word joins `{self.LOCK}`, and `{self.FIELDS}` "
                                     "counts it."))
        sha = self.regenerated_commit("A new word, with its count", changes)
        self.assertEqual(self.word_count(git(WORK, "show", f"{sha}:{self.FIELDS}")),
                         self.word_count(git(WORK, "show", f"{BASE}:{self.FIELDS}")) + 1)
        self.assertNotEqual(safe_push.judged_files(WORK, BASE, sha), [])
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertIn("PlantedWord: a word of the statements", out)
        self.assertEqual(self.guard(out, "review records (the commit's checks)"), "ok", out)
        self.assertEqual(self.guard(out, "pinned values"), "note", out)
        note = out[out.index("pinned values"):]
        for path in (self.LOCK, self.FIELDS):
            self.assertIn(path, note)
        self.assertIsNone(self.guard(out, "check change kept apart"), out)

    def test_count_moved_wrongly_refused_by_its_own_pass(self):
        # The count pinned is the count check_fidelity.py computes: moved to any other
        # value, the commit's own pass refuses it, pinned values or not.
        changes = self.word_added()
        changes.update(self.decision(f"A word joins `{self.LOCK}`, and `{self.FIELDS}` "
                                     "miscounts it."))
        self.regenerated_commit("A new word, with its count", changes)
        moved = self.text(self.FIELDS)
        wrong = self.WORD_COUNT.sub(lambda m: f"{m[1]}{int(m[2]) + 1}{m[3]}", moved)
        self.commit("The count moved too far", {self.FIELDS: wrong})
        out = self.assertRefused(self.safe_push("--dry-run"),
                                 "review records (the commit's checks)")
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertEqual(self.guard(out, "review records (the commit's checks)"), "FAIL", out)
        self.assertIn("count 'vocabulary': stated", out)
        self.assertEqual(self.guard(out, "pinned values"), "note", out)

    def fields_changed(self, change, mode: int | None = None) -> str:
        """A commit from origin/main of a new word in the lock, a line of the foundations,
        which the checks judge, and FIELDS.md with its count of the words moved, then
        changed by `change`, given its text (None deletes the file); `mode`, if given, is
        the file's new mode."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        write = self.word_added()
        text = self.text(self.FIELDS)
        moved = self.WORD_COUNT.sub(lambda m: f"{m[1]}{int(m[2]) + 1}{m[3]}", text)
        self.assertEqual(self.word_count(moved), self.word_count(text) + 1)
        result = change(moved)
        write[self.METRIC] = self.text(self.METRIC) + "\n-- A line for the test.\n"
        if result is not None:
            write[self.FIELDS] = result
        if mode is not None:
            (WORK / self.FIELDS).write_text(result)
            os.chmod(WORK / self.FIELDS, mode)
        return self.commit("A new word, its count and a Lean line", write,
                           remove=[self.FIELDS] if result is None else ())

    def test_only_count_values_moved_are_pinned_values(self):
        # FIELDS.md is a check input: its change is a pinned value while nothing but the
        # values between its count markers moves. Anything else is a check change.
        def renamed(text):
            self.assertEqual(text.count("<!-- count:vocabulary -->"), 1)
            return text.replace("<!-- count:vocabulary -->", "<!-- count:axioms -->")
        weakened = {
            "a line added": lambda t: t + "\nA line for the test.\n",
            "a byte beside the marker changed": lambda t: t.replace(
                "<!-- count:vocabulary -->", " <!-- count:vocabulary -->", 1),
            "the marker renamed": renamed,
            "a marker added": lambda t: t + "\nAnd: <!-- count:axioms -->79<!-- /count -->.\n",
            "the marker removed": lambda t: self.WORD_COUNT.sub(lambda m: m[2], t),
            "the file deleted": lambda t: None,
        }
        beyond = f"it changes {self.FIELDS} beyond the values between count markers"
        for name, change in weakened.items():
            with self.subTest(name):
                refused, out = self.kept_apart(self.fields_changed(change),
                                               "python3 scripts/check_fidelity.py")
                self.assertTrue(refused, out)
                self.assertIn(beyond, out)
                self.assertNotIn("pinned values", out)
        with self.subTest("the file made executable"):
            refused, out = self.kept_apart(self.fields_changed(lambda t: t, mode=0o755),
                                           "python3 scripts/check_fidelity.py")
            self.assertTrue(refused, out)
            self.assertIn(beyond, out)
            self.assertNotIn("pinned values", out)
        with self.subTest("the count moved"):
            refused, out = self.kept_apart(self.fields_changed(lambda t: t),
                                           "python3 scripts/check_fidelity.py")
            self.assertFalse(refused, out)
            self.assertIn("pinned values", out)
            self.assertIn(self.FIELDS, out[out.index("pinned values"):])

    def test_counts_in_check_code_are_never_pinned_values(self):
        # The same count moved, and nothing else, is a pinned value in the Markdown of the
        # check inputs that are not code, and never in scripts/ or in code under tests/.
        line = "The vocabulary: <!-- count:vocabulary -->{}<!-- /count --> words.\n"
        schema = self.text("review/SCHEMA.md")
        pages = {"Certificate/counted.md": "", "tests/counted.md": "",
                 "review/SCHEMA.md": schema, "scripts/counted.md": "",
                 "scripts/counted.py": "# ", "tests/counted.py": "# ",
                 "review/counted.md": ""}
        before = self.commit("Pages with a count", {p: t + line.format(91)
                                                    for p, t in pages.items()})
        after = self.commit("Their counts moved", {p: t + line.format(92)
                                                   for p, t in pages.items()})
        for path in pages:
            with self.subTest(path):
                self.assertEqual(safe_push.pinned(WORK, before, after, path),
                                 safe_push.under(path, ("Certificate/", "tests/counted.md",
                                                        "review/SCHEMA.md")))
        self.assertTrue(all(safe_push.under(p, safe_push.CHECK_INPUTS)
                            and not safe_push.under(p, ("scripts/",))
                            for p in safe_push.COUNTED_PROSE))
        # And the reader is origin/main's: the commit's own, made to read a whole page as
        # a count's value, is not the one read.
        reader = safe_push.COUNT_READER
        loose = self.replaced(reader, "def markers(text, path):\n",
                              "def markers(text, path):\n    return [Marker('vocabulary', "
                              "0, 0, len(text), len(text))]\n\n\ndef _markers(text, path):\n")
        sha = self.commit("A loose reader, and FIELDS.md rewritten", {
            reader: loose, self.FIELDS: "A page for the test.\n"})
        self.assertFalse(safe_push.pinned(WORK, BASE, sha, self.FIELDS))
        # Had origin/main held that reader, the page rewritten would have been one value.
        again = self.commit("FIELDS.md rewritten again", {self.FIELDS: "Another page.\n"})
        self.assertTrue(safe_push.pinned(WORK, sha, again, self.FIELDS))

    def test_counts_between_two_markers_and_pages_added(self):
        # Every byte outside the values stands, between two markers as around them, and
        # in their order; and a page added with a count is a check change.
        page = "Certificate/counted.md"
        line = ("The lock: <!-- count:vocabulary -->{}<!-- /count --> words and "
                "<!-- count:axioms -->{}<!-- /count --> axioms.\n")
        before = self.commit("A page with two counts", {page: line.format(91, 79)})
        self.assertFalse(safe_push.pinned(WORK, BASE, before, page))
        after = self.commit("Both counts moved", {page: line.format(92, 80)})
        self.assertTrue(safe_push.pinned(WORK, before, after, page))
        between = self.commit("A word between them", {
            page: line.format(92, 80).replace(" words and ", " words or ")})
        self.assertFalse(safe_push.pinned(WORK, before, between, page))
        swapped = self.commit("The markers swapped", {page: line.format(91, 79).replace(
            "count:vocabulary", "count:SWAP").replace("count:axioms", "count:vocabulary")
            .replace("count:SWAP", "count:axioms")})
        self.assertFalse(safe_push.pinned(WORK, before, swapped, page))

    def test_counts_unreadable_are_no_pinned_values(self):
        # A page either side cannot read, or a reader of origin/main's that does not load,
        # pins nothing: refused, never a crash.
        page = "Certificate/counted.md"
        line = "The vocabulary: <!-- count:vocabulary -->{}<!-- /count --> words.\n"
        before = self.commit("A page with a count", {page: line.format(91)})
        unreadable = {
            "a marker unclosed": line.format(92).replace("<!-- /count -->", ""),
            "not UTF-8": line.format(92).encode() + b"\xff\n",
        }
        for name, text in unreadable.items():
            with self.subTest(name):
                git(WORK, "checkout", "--quiet", "--force", "--detach", before)
                sha = self.commit(name, {page: text})
                self.assertFalse(safe_push.pinned(WORK, before, sha, page))
        reader = safe_push.COUNT_READER
        for name, write, remove in (
                ("the reader not loading", {reader: "raise ImportError('for the test')\n"}, ()),
                ("the reader missing", {}, (reader,))):
            with self.subTest(name):
                git(WORK, "checkout", "--quiet", "--force", "--detach", before)
                base = self.commit(name, write, remove=remove)
                sha = self.commit("Its count moved", {page: line.format(92)})
                self.assertFalse(safe_push.pinned(WORK, base, sha, page))
        with self.subTest("a symbolic link"):
            git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
            link = WORK / "Certificate" / "linked.md"
            link.symlink_to(line.format(91).strip())
            git(WORK, "add", "--", "Certificate/linked.md")
            first = self.commit("A link with a count")
            link.unlink()
            link.symlink_to(line.format(92).strip())
            git(WORK, "add", "--", "Certificate/linked.md")
            second = self.commit("Its count moved")
            self.assertFalse(safe_push.pinned(WORK, first, second, "Certificate/linked.md"))

    # The model's page (#187): pinned whole for its prose, the model's account of its laws,
    # while its count markers stand, as the other check inputs' do.
    AXIOM_COUNT = re.compile(r"(<!-- count:axioms -->)([0-9]+)(<!-- /count -->)")

    def model_moved(self) -> str:
        """A commit from origin/main of an axiom added with its law (planted_axiom), with
        the pages render.py regenerates from it: MODEL.md gains a line of its account, and
        each of its counts of the axioms moves."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        sha = self.regenerated_commit("Add an axiom, with its law", self.planted_axiom())
        old, new = (git(WORK, "show", f"{rev}:{self.PAGE}") for rev in (BASE, sha))
        self.assertIn("The planted law:", new)
        self.assertEqual([int(m[2]) for m in self.AXIOM_COUNT.finditer(new)],
                         [int(m[2]) + 1 for m in self.AXIOM_COUNT.finditer(old)])
        return sha

    def page_changed(self, moved: str, change, mode: int | None = None) -> str:
        """A commit on `moved` of MODEL.md changed by `change`, given its text (None deletes
        the file); `mode`, if given, is the file's new mode."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", moved)
        result = change(self.text(self.PAGE))
        if mode is not None:
            (WORK / self.PAGE).write_text(result)
            os.chmod(WORK / self.PAGE, mode)
        return self.commit("MODEL.md changed, for the test",
                           {} if result is None else {self.PAGE: result},
                           remove=[self.PAGE] if result is None else ())

    def test_model_page_moves_with_its_markers_standing(self):
        # An axiom added with its law moves the model's account, a line of MODEL.md, and
        # its counts of the axioms; its prose may move further. The same markers stand, by
        # name and in order, so the page is a pinned value and lands with its content.
        moved = self.model_moved()
        reworded = self.page_changed(moved, lambda t: t.replace(
            "Stoicheia's proofs rest on <!-- count:axioms -->",
            "Stoicheia's proofs now rest on <!-- count:axioms -->", 1))
        for name, sha in (("the account and its counts moved", moved),
                          ("a sentence around a marker reworded", reworded)):
            with self.subTest(name):
                self.assertTrue(safe_push.pinned(WORK, BASE, sha, self.PAGE))
                refused, out = self.kept_apart(sha, "python3 scripts/check_fidelity.py")
                self.assertFalse(refused, out)
                self.assertIn("pinned values", out)
                self.assertIn(self.PAGE, out[out.index("pinned values"):])

    def test_model_page_markers_added_removed_or_renamed_kept_apart(self):
        # The same change, with a count marker of MODEL.md added, removed, renamed,
        # reordered or left unclosed, is no pinned value, and keep_apart refuses it when
        # origin/main's checks fail: the commit's own pass checks each value against the
        # marker that holds it. The first count of the axioms renamed to tacit-rules, its
        # value moved to match, would have the page say that the proofs rest on as many
        # axioms as there are tacit rules, and pass that check. Nor is the page deleted,
        # made executable or left unreadable.
        def renamed(text):
            (tacit,) = re.findall(r"<!-- count:tacit-rules -->([0-9]+)<!-- /count -->", text)
            return self.AXIOM_COUNT.sub(
                lambda m: f"<!-- count:tacit-rules -->{tacit}{m[3]}", text, count=1)
        moved = self.model_moved()
        weakened = {
            "a marker added": lambda t: t + (
                "\nThe lock's words: <!-- count:vocabulary -->91<!-- /count -->.\n"),
            "a marker removed": lambda t: self.AXIOM_COUNT.sub(lambda m: m[2], t, count=1),
            "a marker renamed": renamed,
            "the markers reordered": lambda t: t.replace(
                "<!-- count:axioms -->", "<!-- count:SWAP -->", 1).replace(
                "<!-- count:tacit-rules -->", "<!-- count:axioms -->", 1).replace(
                "<!-- count:SWAP -->", "<!-- count:tacit-rules -->", 1),
            "a marker unclosed": lambda t: t.replace("<!-- /count -->", "", 1),
            "the file deleted": lambda t: None,
        }
        marker = f"it adds, removes, renames or reorders a count marker of {self.PAGE}"
        for name, change in weakened.items():
            with self.subTest(name):
                sha = self.page_changed(moved, change)
                self.assertFalse(safe_push.pinned(WORK, BASE, sha, self.PAGE))
                refused, out = self.kept_apart(sha, "python3 scripts/check_fidelity.py")
                self.assertTrue(refused, out)
                self.assertIn(marker, out)
                self.assertNotIn("beyond", out)
                self.assertNotIn("pinned values", out)
        with self.subTest("the file made executable"):
            sha = self.page_changed(moved, lambda t: t, mode=0o755)
            self.assertFalse(safe_push.pinned(WORK, BASE, sha, self.PAGE))
            refused, out = self.kept_apart(sha, "python3 scripts/check_fidelity.py")
            self.assertTrue(refused, out)
            self.assertIn(marker, out)
            self.assertNotIn("pinned values", out)

    # The model's laws (issue #40): an axiom moves with its law, in one pull request.
    LOCK, HASH = "Certificate/axioms.lock", "tests/model/lock.sha256"
    LAWS, PAGE = "tests/model/laws.toml", "tests/model/MODEL.md"
    SEARCH, HYPERBOLIC = "tests/model/search.py", "tests/model/hyperbolic.py"
    RESULTS = "tests/model/results/summary.txt"
    METRIC = "Elements/Foundations/Tacit/Metric.lean"
    MODEL_RUN = "python3 -I tests/model/run.py --fast"
    RUN_MARK = "\n# ======================= run =======================\n"
    RETAINED_LAW_ENTRY = '"Tacit.line_unique" = "line_unique"\n'
    LINE_UNIQUE = ("@axiom('line_unique', dict(A=P, B=P, L=L_, M=L_))\ndef _(c):\n"
                   "    A, B, L, M = c['A'], c['B'], c['L'], c['M']\n"
                   "    if not (A != B and on_line(A, L) and on_line(B, L) and "
                   "on_line(A, M) and on_line(B, M)):\n"
                   "        return None\n    return L == M\n")
    LEN_SELF = {SEARCH: "@axiom('len_self', dict(A=P))\ndef _(c):\n"
                        "    return d2(c['A'], c['A']) == 0\n\n\n",
                HYPERBOLIC: "@axiom('len_self', dict(A=P))\ndef _(c):\n"
                            "    return ch2(c['A'], c['A']) == 1\n\n\n"}
    PLANTED_LAW = {SEARCH: "d2(c['A'], c['A']) == 0", HYPERBOLIC: "ch2(c['A'], c['A']) == 1"}

    def planted_law(self, path: str, fn: str = "_", first: str = "", before: str = "") -> str:
        """`path`, a harness, with the planted law's code added before its run section: a
        function `fn` under `@axiom('planted_law', …)`, its body beginning with `first`, and
        `before` at the top level ahead of it."""
        law = (f"\n{before}@axiom('planted_law', dict(A=P))\ndef {fn}(c):\n{first}"
               f"    return {self.PLANTED_LAW[path]}\n\n")
        return self.replaced(path, self.RUN_MARK, law + self.RUN_MARK)

    def planted_axiom(self) -> dict:
        """An axiom added as the coordinator adds one, Lean aside: its declaration in the
        foundations; facts.json, and the lock written from it by `check_fidelity.py
        --write-lock`; the lock's new hash; its line in the model's laws.toml, and its law's
        code in search.py and hyperbolic.py; a line of MODEL.md and of the results; and a
        decisions line naming the lock and each protected file."""
        name, statement = "Tacit.planted_law", ("∀ (A : Elements.Point), "
                                                "Eq (Elements.len A A) (Elements.len A A)")
        facts = json.loads(self.text("facts.json"))
        facts["axiom_modules"][name] = "Elements.Foundations.Tacit.Metric"
        facts["axiom_types"][name] = statement
        changes = {"facts.json": json.dumps(facts, indent=2, ensure_ascii=False) + "\n"}
        (WORK / "facts.json").write_text(changes["facts.json"])
        r = subprocess.run([sys.executable, "scripts/check_fidelity.py", "--write-lock"],
                           cwd=WORK, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lock = self.text(self.LOCK)
        self.assertIn(f'"{name}" = "{statement}"', lock)
        digest = hashlib.sha256(lock.encode()).hexdigest()
        changes.update({
            self.METRIC: self.text(self.METRIC)
            + "\n/-- A law planted for the test. -/\naxiom planted_law (A : Point) : ‖A A‖ = ‖A A‖\n",
            self.LOCK: lock,
            self.HASH: re.sub(r"(?m)^[0-9a-f]{64}(?=  Certificate/axioms\.lock$)", digest,
                              self.text(self.HASH)),
            self.LAWS: self.replaced(self.LAWS, self.RETAINED_LAW_ENTRY,
                                     self.RETAINED_LAW_ENTRY +
                                     '"Tacit.planted_law" = "planted_law"\n'),
            self.SEARCH: self.planted_law(self.SEARCH),
            self.HYPERBOLIC: self.planted_law(self.HYPERBOLIC),
            self.PAGE: self.text(self.PAGE) + "\nThe planted law: a point is no distance "
                                              "from itself, for the test.\n",
            self.RESULTS: self.text(self.RESULTS) + "planted_law: a line for the test\n"})
        changes.update(self.decision(
            "`Tacit.planted_law` joins the axiom lock, with its law: " + ", ".join(
                f"`{p}`" for p in (self.LOCK, self.HASH, self.LAWS, self.SEARCH,
                                   self.HYPERBOLIC, self.PAGE, self.RESULTS)) + "."))
        return changes

    def test_axiom_lands_with_its_law(self):
        # Issue #40's test: an axiom added moves in one pull request with its entry in the
        # lock, the lock's hash, its law's name in laws.toml, its law's code in the two
        # harnesses that check every law, and the model's account. origin/main's checks
        # fail on it, which is noted; the commit's own pass holds; it lands as content.
        sha = self.regenerated_commit("Add an axiom, with its law", self.planted_axiom())
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "axiom lock"), "ok", out)
        self.assertEqual(self.guard(out, "protected paths"), "ok", out)
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertIn("Tacit.planted_law: an assumption not in Certificate/axioms.lock", out)
        self.assertEqual(self.guard(out, "review records (the commit's checks)"), "ok", out)
        self.assertEqual(self.guard(out, "pinned values"), "note", out)
        note = out[out.index("pinned values"):]
        for path in (self.LOCK, self.HASH, self.LAWS, self.SEARCH, self.HYPERBOLIC, self.PAGE):
            self.assertIn(path, note)
        self.assertIsNone(self.guard(out, "check change kept apart"), out)
        # And the model takes it: its ties to the Lean hold on the commit, and the planted
        # law runs, and holds, in the plane and in the hyperbolic plane.
        self.assertEqual(git(WORK, "rev-parse", "HEAD").strip(), sha)
        r = subprocess.run([sys.executable, "-I", "tests/model/run.py", "--ties"], cwd=WORK,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        n = len(json.loads(git(WORK, "show", f"{BASE}:facts.json"))["axiom_modules"]) + 1
        self.assertIn(f"laws.toml names {n} laws; facts.json declares {n} axioms", r.stdout)
        for path, samples in ((self.SEARCH, 200), (self.HYPERBOLIC, 100)):
            r = subprocess.run([sys.executable, "-I", path, str(samples), "1"], cwd=WORK,
                               env=dict(os.environ, ONLY="planted_law"),
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertRegex(r.stdout, rf"(?m)^planted_law +{samples} +[1-9]\d* +0$")

    def test_law_loosened_beside_an_axiom_kept_apart(self):
        # The same pull request, with line_unique's law in search.py made to pass whatever
        # it meets: a law changed while its axiom stands is a check change, kept apart.
        changes = self.planted_axiom()
        self.assertEqual(changes[self.SEARCH].count(self.LINE_UNIQUE), 1)
        changes[self.SEARCH] = changes[self.SEARCH].replace(
            self.LINE_UNIQUE, self.LINE_UNIQUE.replace("L == M", "True"))
        self.regenerated_commit("Add an axiom, and loosen another's law", changes)
        out = self.assertRefused(self.safe_push("--dry-run"), "check change kept apart",
                                 self.METRIC, "beyond the laws that move with their axioms",
                                 f"the model's laws in {self.SEARCH}")
        self.assertEqual(self.guard(out, "review records (origin/main's checks)"), "note", out)
        self.assertEqual(self.guard(out, "check change kept apart"), "FAIL", out)
        self.assertIsNone(self.guard(out, "pinned values"), out)

    def law_commit(self, change) -> str:
        """A commit from origin/main of what `change` returns, given the planted axiom's
        changes (a path given None is deleted), with a line of the foundations, which the
        checks judge, if it has none."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        planted = self.planted_axiom()
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        write = change(planted)
        write.setdefault(self.METRIC, self.text(self.METRIC) + "\n-- A line for the test.\n")
        return self.commit("An axiom and the model's laws, for the test",
                           {p: v for p, v in write.items() if v is not None},
                           remove=[p for p, v in write.items() if v is None])

    def test_only_laws_moving_with_their_axioms_are_pinned_values(self):
        # A law of the model, its line of laws.toml and its code in search.py and
        # hyperbolic.py, moves only with its axiom's entry in the lock, and its code keeps to
        # itself; the rest of each harness stays as it was. Anything else is a check change.
        def edit(path, old, new):
            def change(planted):
                self.assertEqual(planted[path].count(old), 1, (path, old))
                self.assertNotEqual(old, new)
                return dict(planted, **{path: planted[path].replace(old, new, 1)})
            return change
        loose = self.LINE_UNIQUE.replace("L == M", "True")
        mine = "    pts = [c['A']]\n    pts.append(c['A'])\n"
        len_self = self.LEN_SELF[self.SEARCH]
        len_symm = ("@axiom('len_symm', dict(A=P, B=P))\ndef _(c):\n"
                    "    return d2(c['A'], c['B']) == d2(c['B'], c['A'])\n\n\n")
        weakened = {
            "another law loosened in search.py": edit(self.SEARCH, self.LINE_UNIQUE, loose),
            "another law loosened in hyperbolic.py": edit(self.HYPERBOLIC, self.LINE_UNIQUE,
                                                          loose),
            "the search's box shrunk, outside any law": edit(self.SEARCH, "BOX = 6\n",
                                                             "BOX = 1\n"),
            "a tolerance loosened in model.py": lambda p: dict(p, **{
                "tests/model/model.py": self.replaced("tests/model/model.py", "EPS = 1e-9\n",
                                                      "EPS = 1e-3\n")}),
            "an axiom that stands made to fail in the hyperbolic plane": edit(
                self.LAWS, 'fails = ["Postulate5"]',
                f'fails = ["Postulate5", "{self.RETAINED_AXIOM}"]'),
            "two laws swapped": edit(self.LAWS, '"Tacit.len_self" = "len_self"\n'
                                     '"Tacit.len_symm" = "len_symm"\n',
                                     '"Tacit.len_self" = "len_symm"\n'
                                     '"Tacit.len_symm" = "len_self"\n'),
            "two laws reordered in search.py": edit(self.SEARCH, len_self + len_symm,
                                                      len_symm + len_self),
            "a statement hidden in a comment by a coding cookie": lambda p: dict(p, **{
                self.SEARCH: "# -*- coding: utf-7 -*-\n" + p[self.SEARCH].replace(
                    self.RUN_MARK, "#+AAo-BOX = 1\n" + self.RUN_MARK, 1)}),
            "the law added without its axiom": lambda p: {
                k: v for k, v in p.items() if k not in (self.LOCK, self.HASH, "facts.json")},
            "the new law's code named for a helper": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, fn="on_line")}),
            "the new law with a helper beside it": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, before="def helper():\n"
                                              "    return 0\n\n\n")}),
            "the new law reaching outside itself": lambda p: dict(p, **{
                self.HYPERBOLIC: self.planted_law(self.HYPERBOLIC, first="    SEEDS.clear()\n")}),
            "the new law declaring a global": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, first="    global BOX\n    BOX = 1\n")}),
            "the new law printing a result": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH,
                                              first="    print('len_self 1 1 0')\n")}),
            "the new law printing through help": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(
                    self.SEARCH, first="    help(type('len_self 1 1 0', (), {}))\n")}),
            "the new law ending the run with exit": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, first="    exit(0)\n")}),
            "the new law raising SystemExit": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, first="    raise SystemExit(0)\n")}),
            "the new law reseeding the search": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, first="    c['_rng'].seed(0)\n")}),
            # The reviewer of #40 found that reflection escaped the deny-list; the
            # allow-list refuses it.
            "the new law reaching a frame": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(
                    self.SEARCH, first="    g = (x for x in ())\n"
                                       "    g.gi_frame.f_back.f_globals['BOX']\n")}),
            "the new law looking an attribute up by string": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(
                    self.SEARCH, first="    getattr(c['_rng'], 'seed')(0)\n")}),
            "the new law closing over a global": lambda p: dict(p, **{
                self.HYPERBOLIC: self.planted_law(
                    self.HYPERBOLIC, first="    def h():\n        DEN.clear()\n    h()\n")}),
            # The verifier of #40 found these two: a second name for a shared container.
            "the new law changing a shared container through a second name": lambda p: dict(
                p, **{self.HYPERBOLIC: self.planted_law(
                    self.HYPERBOLIC, first="    d = DEN\n    d[:] = [2]\n")}),
            "the new law changing a shared container through a loop": lambda p: dict(p, **{
                self.HYPERBOLIC: self.planted_law(
                    self.HYPERBOLIC, first="    for d in (DEN,):\n        d.clear()\n")}),
            # And a file the laws are read from deleted, with a law's code changed: refused,
            # not a traceback (tomllib.loads(None) raises AttributeError before 3.14).
            "laws.toml deleted": lambda p: dict(p, **{self.LAWS: None}),
            "the lock deleted": lambda p: dict(p, **{self.LOCK: None}),
        }
        for name, change in weakened.items():
            with self.subTest(name):
                refused, out = self.kept_apart(self.law_commit(change), self.MODEL_RUN)
                self.assertTrue(refused, out)
                self.assertNotIn("pinned values", out)
                if name != "a tolerance loosened in model.py":
                    self.assertIn("beyond the laws that move with their axioms", out)

        def restated(_):
            old = '"Tacit.len_self" = "∀ (A : Elements.Point), Eq (Elements.len A A) 0"'
            new = ('"Tacit.len_self" = "∀ (A B : Elements.Point), Eq A B → '
                   'Eq (Elements.len A B) 0"')
            law = ("@axiom('len_self', dict(A=P, B=P))\ndef _(c):\n    if c['A'] != c['B']:\n"
                   "        return None\n    return d2(c['A'], c['B']) == 0\n\n\n")
            return {self.LOCK: self.replaced(self.LOCK, old, new),
                    self.SEARCH: self.replaced(self.SEARCH, self.LEN_SELF[self.SEARCH], law)}

        def removed(_):
            lock = [line for line in self.text(self.LOCK).splitlines(keepends=True)
                    if not line.startswith('"Tacit.len_self" = ')]
            return {self.LOCK: "".join(lock),
                    self.LAWS: self.replaced(self.LAWS, '"Tacit.len_self" = "len_self"\n', ""),
                    **{p: self.replaced(p, self.LEN_SELF[p], "") for p in self.LEN_SELF}}
        kept = {
            "an axiom added with its law": lambda p: p,
            "and a comment beside it": edit(self.SEARCH, self.RUN_MARK,
                                            "\n# A comment for the test.\n" + self.RUN_MARK),
            "the new law making a container of its own": lambda p: dict(p, **{
                self.SEARCH: self.planted_law(self.SEARCH, first=mine)}),
            "an axiom restated with its law": restated,
            "an axiom removed with its law": removed,
        }
        for name, change in kept.items():
            with self.subTest(name):
                refused, out = self.kept_apart(self.law_commit(change), self.MODEL_RUN)
                self.assertFalse(refused, out)
                self.assertIn("pinned values", out)

    STYLE = ("python3 scripts/check_style.py",
             [sys.executable, "scripts/check_style.py", "--no-lean"])

    def full_checks(self, sha: str, checks: list, negative: list) -> tuple[str | None, str]:
        """safe_push.full_checks on `sha`, as step 4 runs it, in a throwaway worktree, with
        its sequence (origin/main's registry's, as check_sequence reads it) and NEGATIVE cut
        to the steps given (no Lean): its refusal, if any, and its report."""
        rep, out = safe_push.Report(), io.StringIO()
        ctx = safe_push.Context(WORK, sha, BASE, 1, str(ORIGIN), None, {})
        inputs = [(st, p) for st, p in safe_push.changed_files(WORK, BASE, sha)
                  if safe_push.under(p, safe_push.CHECK_INPUTS)]
        refusal = None
        with tempfile.TemporaryDirectory(dir=TMP) as tmp, \
                mock.patch.object(safe_push, "NEGATIVE", negative), \
                contextlib.redirect_stdout(out):
            parent = Path(tmp)
            (parent / "logs").mkdir()
            with safe_push.worktree(WORK, sha, parent, "check") as wt:
                try:
                    safe_push.full_checks(ctx, wt, parent, inputs, rep, parent / "logs",
                                          checks)
                except safe_push.Refusal as e:
                    refusal = str(e)
        return refusal, out.getvalue()

    def test_stage_4_keeps_a_check_change_apart(self):
        # Step 4's own wiring of keep_apart, which the internal flag skips: check_style.py
        # made to pass whatever it finds, with a page of the edition it would refuse.
        path = "scripts/check_style.py"
        base_name = "python3 scripts/check_style.py (origin/main's checks)"
        loosened = {path: self.replaced(path, "    sys.exit(main())", "    sys.exit(0)")}
        loosened.update(self.decision(f"`{path}` passes whatever it finds, for the test."))
        sha = self.commit("Loosen check_style.py, and break one of its rules", dict(loosened, **{
            "mishnah/I/01.md": self.text("mishnah/I/01.md") + "\nA tacit assumption, here.\n"}))
        # Refused after the checks, before the negative tests run.
        ran = TMP / "negative-ran"
        ran.unlink(missing_ok=True)
        marker = ("negative: a marker", [sys.executable, "-c", f"open({str(ran)!r}, 'w')"])
        refusal, out = self.full_checks(sha, [self.STYLE], [marker])
        self.assertEqual(refusal, "a check changed together with what it checks", out)
        self.assertEqual(self.guard(out, base_name), "note", out)
        self.assertEqual(self.guard(out, "check change kept apart"), "FAIL", out)
        self.assertIn("mishnah/I/01.md", out[out.index("check change kept apart"):])
        self.assertFalse(ran.exists(), f"the negative tests ran after the refusal was due:\n{out}")
        # A check failing in the negative tests' pass alone is kept apart there.
        name, cmd = self.STYLE
        refusal, out = self.full_checks(sha, [], [("negative: " + name, cmd)])
        self.assertEqual(refusal, "a check changed together with what it checks", out)
        self.assertEqual(self.guard(out, "negative: " + base_name), "note", out)
        self.assertEqual(self.guard(out, "check change kept apart"), "FAIL", out)
        # The check change alone, with a generated page it would refuse (not judged):
        # noted for the security review, not refused, and the commit's own pass holds.
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        sha = self.commit("Loosen check_style.py, and a page it would refuse", dict(loosened, **{
            "CERTIFICATE.md": self.text("CERTIFICATE.md") + "\nA tacit assumption, here.\n"}))
        refusal, out = self.full_checks(sha, [self.STYLE], [])
        self.assertIsNone(refusal, out)
        self.assertEqual(self.guard(out, base_name), "note", out)
        self.assertEqual(self.step(out, "python3 scripts/check_style.py (the commit's checks)"),
                         "ok", out)
        self.assertIsNone(self.guard(out, "check change kept apart"), out)

    def kept_apart(self, sha: str, *failed: str) -> tuple[bool, str]:
        """keep_apart on `sha`, after these steps failed with origin/main's copies."""
        rep, out = safe_push.Report(), io.StringIO()
        with contextlib.redirect_stdout(out):
            for name in failed:
                rep.add("4", name + safe_push.BASE_PASS, "note", "failed")
            refused = safe_push.keep_apart(WORK, BASE, sha, rep, "4")
        return refused, out.getvalue()

    def test_kept_apart_counts_verdicts_not_freshness(self):
        sha = self.commit("A check, and a line of reading", {
            "scripts/check_links.py": self.text("scripts/check_links.py") + "\n# for the test\n",
            "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"})
        refused, _ = self.kept_apart(sha, "generated pages", "git status --porcelain is empty")
        self.assertFalse(refused)
        # render.py failing outright is a verdict (its check of docs/program.toml, say).
        for verdict in ("python3 scripts/check_fidelity.py", "negative: python3 "
                        "scripts/negative_tests.py", "lake env lean Certificate/Facts.lean",
                        "python3 scripts/render.py", "render.py"):
            with self.subTest(verdict=verdict):
                refused, out = self.kept_apart(sha, verdict)
                self.assertTrue(refused, out)
                self.assertIn("docs/reading.md", out)

    def test_kept_apart_judges_the_edition_not_the_guides_or_stamps(self):
        # The stage 2 pattern: the certificate changes, the pages and a record's stamp
        # follow, and the guides say why; none of that is judged. A record's other lines,
        # a Lean file, and README.md's hand-written part are.
        record = self.text("review/I/01.toml")
        stamped = re.sub(r'(?m)^commit = "[^"]*"', 'commit = "0123456"', record)
        # A `text` stamp added, or rewritten, on a line of its own in [review] is a stamp
        # too (review/SCHEMA.md).
        texted = with_text(re.sub(r'(?m)^text = "[^"]*"\n?', "", self.text("review/I/03.toml")),
                           "sha256:0123456789abcdef")
        changes = {
            "Certificate/Facts.lean": self.text("Certificate/Facts.lean") + "\n-- for the test\n",
            "review/I/01.toml": stamped,
            "review/I/03.toml": texted,
            "book/I/01.md": self.text("book/I/01.md") + "\nA generated line.\n",
            "docs/WORKFLOW.md": self.text("docs/WORKFLOW.md") + "\nA line for the test.\n",
            "AGENTS.md": self.text("AGENTS.md") + "\nA line for the test.\n",
            "docs/briefs/0006-test.md": "A brief for the test.\n"}
        sha = self.commit("The certificate, its pages, a stamp, the guides", changes)
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha), [])
        refused, out = self.kept_apart(sha, "python3 scripts/check_fidelity.py")
        self.assertFalse(refused, out)
        # A stamp taken away is not a stamp: the record is judged.
        unstamped = re.sub(r'(?m)^lean = "[^"]*"\n', "", self.text("review/I/04.toml"))
        self.assertNotEqual(unstamped, self.text("review/I/04.toml"))
        sha = self.commit("And the edition", {
            "review/I/02.toml": self.text("review/I/02.toml") + "\n# A line for the test.\n",
            "review/I/04.toml": unstamped,
            "Elements/BookI/Prop01.lean": self.text("Elements/BookI/Prop01.lean") + "\n-- x\n",
            "README.md": "A hand-written line.\n" + self.text("README.md")})
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha),
                         ["Elements/BookI/Prop01.lean", "README.md", "review/I/02.toml",
                          "review/I/04.toml"])

    def test_a_stamp_line_inside_a_string_is_no_stamp(self):
        # A line shaped as a stamp, added inside a multi-line string, changes the note it
        # is in: the record is judged. The same line added to [review] is a stamp alone.
        path, line = "review/I/03.toml", 'text = "sha256:0123456789abcdef"'
        noted = self.replaced(path, 'scope = "full"\n', 'scope = "full"\n'
                              'note = """\nA note on two lines,\nfor the test."""\n')
        noted = re.sub(r'(?m)^text = "[^"]*"\n?', "", noted)
        first = self.commit("A record with a multi-line note", {path: noted})
        inside = self.commit("A stamp-shaped line inside the note", {
            path: noted.replace("A note on two lines,\n", f"A note on two lines,\n{line}\n", 1)})
        self.assertFalse(safe_push.stamp_only(WORK, first, inside, path))
        git(WORK, "checkout", "--quiet", "--force", "--detach", first)
        stamped = self.commit("A `text` stamp in [review]", {
            path: with_text(noted, "sha256:0123456789abcdef")})
        self.assertTrue(safe_push.stamp_only(WORK, first, stamped, path))

    def test_a_stamp_taken_away_beside_a_stamp_shaped_line_is_judged(self):
        # The [review] `text` stamp taken away, while a line of its shape stays inside a
        # multi-line note: a stamp is gone from its section, and the record is judged.
        path, line = "review/I/03.toml", 'text = "sha256:0123456789abcdef"'
        record = re.sub(r'(?m)^text = "[^"]*"\n?', "", self.text(path))
        self.assertEqual(record.count('scope = "full"\n'), 1)
        noted = record.replace('scope = "full"\n', 'scope = "full"\n'
                               f'note = """\nA note on two lines,\n{line}\n"""\n')
        stamped = with_text(noted, "sha256:3333333333333333")
        first = self.commit("A stamp-shaped line in the note, and a `text` stamp",
                            {path: stamped})
        taken = self.commit("The `text` stamp taken away", {path: noted})
        self.assertFalse(safe_push.stamp_only(WORK, first, taken, path))
        self.assertIn(path, safe_push.judged_files(WORK, first, taken))

    def test_acceptance_and_its_check_change_together_as_a_check_change(self):
        # #249: ACCEPTANCE's table of the limitations allowed, check_acceptance.py's
        # ALLOWED_LIMITS and tests/test_acceptance_limits.py, which ties the two, change in
        # one pull request, each half failing the test alone. Nothing in it is judged, so a
        # failure with origin/main's copies is noted, never kept apart; a page of the
        # edition beside them is judged, and is kept apart.
        failing = "python3 -I tests/test_acceptance_limits.py"
        sha = self.commit("An allowance removed, from the table and the check", {
            "docs/ACCEPTANCE.md": self.text("docs/ACCEPTANCE.md") + "\nA line for the test.\n",
            "scripts/check_acceptance.py": self.text("scripts/check_acceptance.py")
            + "\n# for the test\n",
            "tests/test_acceptance_limits.py": self.text("tests/test_acceptance_limits.py")
            + "\n# for the test\n"})
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha), [])
        refused, out = self.kept_apart(sha, failing)
        self.assertFalse(refused, out)
        sha = self.commit("And a page of the edition", {
            "mishnah/I/01.md": self.text("mishnah/I/01.md") + "\nA line for the test.\n"})
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha), ["mishnah/I/01.md"])
        refused, out = self.kept_apart(sha, failing)
        self.assertTrue(refused, out)
        self.assertIn("mishnah/I/01.md", out)

    def test_harness_runs_from_origin_main(self):
        # The commit empties its own copy of the secret scan and plants a token; run from
        # the commit's checkout, its copy hands over to origin/main's, which refuses it.
        lame = self.replaced("scripts/safe_push.py", "def secret_scan(",
                             "def secret_scan(*a, **k):\n    return None\n\n\ndef _unused(")
        self.commit("Empty the scan, and plant a token", {
            "scripts/safe_push.py": lame, "docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        out = self.assertRefused(self.safe_push(script=WORK / "scripts" / "safe_push.py"),
                                 "running origin/main's in its place", "secret scan")
        self.assertEqual(self.guard(out, "harness"), "ok", out)

    def test_allow_list_entry_added_by_the_push_does_not_count(self):
        self.commit("A flagged line, with its own allow-list entry", {
            "docs/notes.md": f"api_token = \"{TOKEN}\"\n",
            "scripts/safe_push_allow.toml": Secrets.ALLOW})
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/notes.md")

    def test_protected_paths_listed(self):
        for path in ("scripts/safe_push.py", "scripts/hooks/pre-push", ".github/workflows/ci.yml",
                     ".github/pull_request_template.md", "Certificate/axioms.lock",
                     "Certificate/Facts.lean", "tests/certificate_expectations.json",
                     "review/SCHEMA.md", "review/terms.toml", ".gitattributes",
                     ".gitignore", "lakefile.toml", "lakefile.lean", "lean-toolchain",
                     "lake-manifest.json", "scripts/hooks/safe-push", "Audit/Overlaps.lean",
                     "Audit/screen.py", "Audit.lean", "model/lakefile.toml",
                     "model/Model/Audit.lean", "model/Model.lean",
                     "model/lakefile.lean", "model/lean-toolchain", "model/lake-manifest.json",
                     "model/lock.sha256", "checks/01-lake-build.toml", "checks/README.md",
                     "checks/99-a-new-check.toml", "docs/ACCEPTANCE.md"):
            self.assertTrue(safe_push.is_protected(path), path)
        # The registry is a check input too, never judged content (#229), and so is
        # ACCEPTANCE, whose table test_acceptance_limits ties to ALLOWED_LIMITS (#249).
        for path in ("checks/01-lake-build.toml", "docs/ACCEPTANCE.md"):
            self.assertTrue(safe_push.under(path, safe_push.CHECK_INPUTS), path)
            self.assertFalse(safe_push.under(path, safe_push.PROTECTED_JUDGED), path)
        # One home: WORKFLOW.md's "Protected paths" names every one of them, and the
        # template points to it rather than copying the list.
        workflow = (SOURCE / "docs" / "WORKFLOW.md").read_text()
        home = workflow[workflow.index("**Protected paths.**"):]
        home = home[:home.index("\n\n")]
        for path in safe_push.PROTECTED:
            self.assertIn(f"`{path}`", home, path)
        # And step 4 there names the check inputs, as CHECK_INPUTS holds them.
        step4 = workflow[workflow.index("4. *The full checks*"):workflow.index("5. *The push")]
        for path in safe_push.CHECK_INPUTS + safe_push.PINNED + safe_push.MODEL_LAW_CODE:
            self.assertIn(f"`{path}`", step4, path)
        self.assertTrue(all(safe_push.under(p, safe_push.CHECK_INPUTS)
                            for p in safe_push.PINNED + safe_push.MODEL_LAW_CODE))
        template = (SOURCE / ".github" / "pull_request_template.md").read_text()
        self.assertIn('"Protected paths"', template)
        self.assertNotIn("lake-manifest.json", template)
        for path in ("docs/WORKFLOW.md", "review/I/01.toml", "Elements/BookI/Prop01.lean",
                     "heath/I/01.md", "scriptsx/a.py", "book/I/01.md", "Auditx/a.lean",
                     "Audit.leanx", "model/README.md", "model/Model/Hand.lean",
                     "model/Model/Audit.lean.orig", "model/Model/Audit.lean/Hand.lean",
                     "model/Model.lean.orig", "model/Model.lean/Hand.lean",
                     "model/Check/Hand.lean", "model/.gitignore", "docs/reports/overlaps.md",
                     "checksx/a.toml", "docs/checks/a.toml",
                     "docs/ACCEPTANCE.md.orig", "docs/STYLE.md"):
            self.assertFalse(safe_push.is_protected(path), path)
        self.assertTrue(set(safe_push.PROTECTED_JUDGED) <= set(safe_push.PROTECTED))

    REGISTRY_ENTRY = "checks/18-check-links.toml"

    def test_a_registry_entry_removed_without_a_decision_is_refused(self):
        # #229: a check removed from the registry, or its command changed, is a protected
        # change, named file by file; with no decisions entry naming it, guard_protected
        # refuses it. Named, it passes the guard.
        path = self.REGISTRY_ENTRY
        changed = self.replaced(path, '"python3", "scripts/check_links.py"',
                                '"python3", "-c", "pass"').replace(
            'name = "python3 scripts/check_links.py"', 'name = "python3 -c pass"')
        for label, write, remove in (("removed", {}, (path,)),
                                     ("its command changed", {path: changed}, ())):
            with self.subTest(label):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                self.commit(f"A check {label}", write, remove=remove)
                out = self.assertRefused(self.safe_push(), "protected paths",
                                         f"naming them: {path}")
                self.assertEqual(self.guard(out, "protected paths"), "FAIL", out)
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                self.commit(f"A check {label}, named", dict(write, **self.decision(
                    f"The check `{path}` is {label}, for the test.")), remove=remove)
                out = self.safe_push("--dry-run").stdout
                self.assertEqual(self.guard(out, "protected paths"), "ok", out)

    def test_a_registry_entry_removed_with_judged_content_is_kept_apart(self):
        # A check taken out of the registry together with content it would refuse: when a
        # check fails with origin/main's copies, the commit is kept apart, for the registry
        # is a check input, never content the checks judge. The registry that step 4 runs is
        # origin/main's, which still lists the check.
        path = self.REGISTRY_ENTRY
        change = {"docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"}
        change.update(self.decision(f"The check `{path}` is removed, for the test."))
        sha = self.commit("A check removed, and a line of reading", change, remove=(path,))
        self.assertIn("python3 scripts/check_links.py",
                      [name for name, _ in safe_push.check_sequence(WORK, BASE).steps])
        self.assertEqual(safe_push.judged_files(WORK, BASE, sha), ["docs/reading.md"])
        refused, out = self.kept_apart(sha, "python3 scripts/check_links.py")
        self.assertTrue(refused, out)
        kept = out[out.index("check change kept apart"):]
        self.assertIn("docs/reading.md", kept)
        self.assertNotIn(path, kept.split("Land the check change first")[0])
        # The registry's change alone, with the guides, is no change of what they judge.
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        sha = self.commit("A check removed", self.decision(
            f"The check `{path}` is removed, for the test."), remove=(path,))
        refused, out = self.kept_apart(sha, "python3 scripts/check_links.py")
        self.assertFalse(refused, out)


class InterruptedAfterThePush(Edge):
    """(4) An interruption or a failure to follow CI after the push is "pushed; CI not
    followed", exit 3; never "interrupted", exit 1.

    None of these depends on time (#95): each runs through DRIVER on its clock, which never
    reads the wall clock and never waits, twice, once with time standing still and once
    leaping an hour at each reading, past every deadline safe_push keeps, and asks the same
    outcome of both, its reason included, so that neither clock can reach exit 3 by another
    path; and DRIVER runs the harness committed at BASE, so that the run is origin/main's
    harness, never handed over to it out of DRIVER's reach."""

    CLOCKS = ("still", "leap")

    def drive(self, action: str, clock: str, env=None) -> subprocess.CompletedProcess:
        env = env or clean_env()
        env["STOICHEIA_TEST_CLOCK"] = clock
        return subprocess.run([sys.executable, "-c", DRIVER, str(UNDER_TEST), action,
                               str(ORIGIN), BASE, "--_test-skip-checks", *with_branch(())],
                              cwd=WORK, env=env, capture_output=True, text=True)

    def assertOnTheClock(self, out: str, clock: str) -> None:
        """The run was origin/main's harness, under DRIVER, on the clock named: its total
        is 0 s while time stands still, and an hour or more when it leaps."""
        self.assertEqual(self.guard(out, "harness"), "ok", out)
        self.assertNotIn("running origin/main's in its place", out)
        total = re.search(r"^Summary: .* \((\d+) s\)$", out, re.M)
        self.assertIsNotNone(total, out)
        if clock == "still":
            self.assertEqual(int(total.group(1)), 0, out)
        else:
            self.assertGreaterEqual(int(total.group(1)), 3600, out)

    def test_interrupt_while_following_ci(self):
        for clock in self.CLOCKS:
            with self.subTest(clock=clock):
                self.setUp()
                sha = self.good_commit()
                r = self.drive("watch-interrupt", clock)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertIn("Pushed; CI not followed: interrupted (a test interruption)", out)
                self.assertNotIn("Interrupted:", out)
                self.assertEqual(self.origin_branch(), sha)
                self.assertIn("pushed; CI not followed", LOG.read_text().splitlines()[-1])
                self.assertOnTheClock(out, clock)

    def test_failure_while_following_ci(self):
        for clock in self.CLOCKS:
            with self.subTest(clock=clock):
                self.setUp()
                sha = self.good_commit()
                r = self.drive("watch-fail", clock)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertIn("pushed; CI not followed (RuntimeError: gh went away)", out)
                self.assertEqual(self.origin_branch(), sha)
                self.assertOnTheClock(out, clock)

    def test_failure_right_after_the_push(self):
        # The final review: the push lands, and origin stops answering before the branch
        # is seen there. The branch is public from the moment `git push` returns 0.
        flag, hook = TMP / "origin-gone", ORIGIN / "hooks" / "post-receive"
        self.addCleanup(lambda: (hook.unlink(missing_ok=True), flag.unlink(missing_ok=True)))
        bindir = Path(tempfile.mkdtemp(prefix="bin-", dir=TMP))
        (bindir / "git").write_text(
            '#!/bin/sh\nfor a in "$@"; do\n'
            f'    if [ "$a" = ls-remote ] && [ -e "{flag}" ]; then\n'
            '        echo "fatal: unable to access origin: Connection reset" >&2\n'
            '        exit 128\n    fi\ndone\n'
            f'exec "{shutil.which("git")}" "$@"\n')
        (bindir / "git").chmod(0o755)
        for clock in self.CLOCKS:
            with self.subTest(clock=clock):
                self.setUp()
                flag.unlink(missing_ok=True)
                hook.write_text(f'#!/bin/sh\ntouch "{flag}"\n')
                hook.chmod(0o755)
                sha = self.good_commit()
                env = clean_env()
                env["PATH"] = f"{bindir}{os.pathsep}{env['PATH']}"
                r = self.drive("push", clock, env=env)
                hook.unlink()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 3, out)
                self.assertIn("Pushed; CI not followed: `git ls-remote origin refs/heads/"
                              f"{BRANCH}` failed: fatal: unable to access origin", out)
                self.assertNotIn("REFUSED", out)
                self.assertEqual(self.origin_branch(), sha)
                self.assertIn("pushed; CI not followed", LOG.read_text().splitlines()[-1])
                self.assertOnTheClock(out, clock)


class Interpreter(Edge):
    """The pre-push hook and the launcher find a Python 3.11 or later (STOICHEIA_PYTHON, or
    the first of python3.14 ... python3 that is), or refuse; never an older python3."""

    OLD = "exit 1\n"        # a python3 older than 3.11: its version check fails

    def bin_with(self, programs: dict) -> Path:
        """A directory for PATH alone: git and the few tools the hook uses, and the
        programs given (name: a shell script's body)."""
        where = Path(tempfile.mkdtemp(prefix="bin-", dir=TMP))
        for tool in ("git", "grep", "mktemp", "rm"):
            os.symlink(shutil.which(tool), where / tool)
        for name, body in programs.items():
            (where / name).write_text("#!/bin/sh\n" + body)
            (where / name).chmod(0o755)
        return where

    def hook(self, bindir: Path, python: str | None = None) -> subprocess.CompletedProcess:
        sha = self.good_commit()
        env = clean_env()
        env.pop("STOICHEIA_PYTHON")
        env["PATH"] = str(bindir)
        if python:
            env["STOICHEIA_PYTHON"] = python
        return subprocess.run(["/bin/sh", str(HERE / "hooks" / "pre-push"), "origin", str(ORIGIN)],
                              cwd=WORK, env=env, input=f"x {sha} refs/heads/x {'0' * 40}\n",
                              capture_output=True, text=True)

    def test_hook_refuses_without_python_3_11(self):
        r = self.hook(self.bin_with({"python3": self.OLD}))
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("no Python 3.11 or later found", r.stderr)

    def test_hook_finds_a_newer_python(self):
        newer = f'exec "{sys.executable}" "$@"\n'
        for programs, python in (({"python3": self.OLD, "python3.12": newer}, None),
                                 ({"python3": self.OLD}, sys.executable)):
            with self.subTest(programs=sorted(programs), python=python):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                r = self.hook(self.bin_with(programs), python)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 0, out)
                self.assertIn("the secret scan of the push to refs/heads/x", out)

    def test_launcher_refuses_without_python_3_11(self):
        env = clean_env()
        env.pop("STOICHEIA_PYTHON")
        env["PATH"] = str(self.bin_with({"python3": self.OLD}))
        r = subprocess.run(["/bin/sh", str(HERE / "hooks" / "safe-push"), "--dry-run"], cwd=WORK,
                           env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("no Python 3.11 or later found", r.stderr)


class HandOver(Edge):
    """Review notes 2, 3 and 6: origin/main's harness replaces a copy that differs, so an
    interruption after its push is still exit 3; the launcher runs origin/main's copy
    whatever the checkout holds; STOICHEIA_HARNESS is checked; the installed hook and
    launcher are compared with origin/main's."""

    def differing_copy(self, change=None) -> Path:
        """A copy of the harness outside the clone that differs from origin/main's."""
        where = Path(tempfile.mkdtemp(prefix="differing-", dir=TMP))
        text = SAFE_PUSH.read_text()
        text = change(text) if change else text + "\n# A copy that differs.\n"
        (where / "safe_push.py").write_text(text)
        shutil.copy(HERE / "heath.py", where / "heath.py")
        return where / "safe_push.py"

    def interrupted(self, signum: int) -> None:
        sha = self.good_commit()
        pidfile = TMP / f"safe-push-{signum}.pid"
        pidfile.unlink(missing_ok=True)
        env = clean_env()
        env["STOICHEIA_FAKE_GH_KILL"] = f"{pidfile}:{signum}"
        proc = subprocess.Popen(
            [sys.executable, str(self.differing_copy()), "--_test-skip-checks",
             *with_branch(())], cwd=WORK, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL))
        pidfile.write_text(str(proc.pid))
        out, _ = proc.communicate(timeout=300)
        self.assertIn("running origin/main's in its place", out)
        self.assertEqual(proc.returncode, 3, out)
        self.assertIn("Pushed; CI not followed: interrupted", out)
        self.assertIn("pushed; CI not followed", LOG.read_text().splitlines()[-1])
        self.assertEqual(self.origin_branch(), sha)
        self.assertEqual(len(git(WORK, "worktree", "list").splitlines()), 1)

    def test_ctrl_c_after_the_push_of_a_handed_over_run(self):
        self.interrupted(signal.SIGINT)

    def test_sigterm_after_the_push_of_a_handed_over_run(self):
        # A supervisor's timeout signals the process it started, and nothing else.
        self.interrupted(signal.SIGTERM)

    def test_launcher_runs_origin_mains_copy(self):
        # The checkout's copy never hands over, and does not scan; a token is planted. The
        # launcher runs origin/main's copy, which refuses it.
        lame = self.replaced("scripts/safe_push.py", "def harness(repo, base: str, rep: Report)"
                             " -> None:\n", "def harness(repo, base, rep):\n    return None\n\n\n"
                             "def _unused(repo, base: str, rep: Report) -> None:\n")
        lame = lame.replace("def secret_scan(", "def secret_scan(*a, **k):\n    return None\n\n\n"
                            "def _unused_scan(", 1)
        self.commit("A harness that judges itself, and a token", {
            "scripts/safe_push.py": lame, "docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = subprocess.run(["git", "safe-push", "--_test-skip-checks", *with_branch(())],
                           cwd=WORK / "docs", env=clean_env(), capture_output=True, text=True)
        out = self.assertRefused(r, "secret scan")
        self.assertEqual(self.guard(out, "harness"), "ok", out)
        self.assertNotIn("running origin/main's in its place", out)

    def test_launcher_follows_no_foreign_git_dir(self):
        # #359: run from the clone under a GIT_DIR naming another repository, whose
        # origin/main holds a harness of its own, the launcher fetches, copies and runs the
        # clone's origin/main harness, never the other's.
        plain = {name: value for name, value in clean_env().items()
                 if not name.startswith("GIT_")}
        plain.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        tmp = Path(tempfile.mkdtemp(prefix="launcher-359-", dir=TMP))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        marker, foreign = tmp / "the-foreign-harness-ran", tmp / "foreign"
        git(tmp, "init", "-q", str(foreign), env=plain)
        (foreign / "scripts").mkdir()
        (foreign / "scripts" / "safe_push.py").write_text(
            f"HARNESS_PROTOCOL = 1\nopen({str(marker)!r}, 'w').close()\n")
        (foreign / "scripts" / "heath.py").write_text("# The foreign harness's heath.\n")
        git(foreign, "add", "scripts", env=plain)
        git(foreign, "-c", "user.name=Foreign", "-c", "user.email=foreign@example.invalid",
            "commit", "-q", "--no-verify", "-m", "A foreign harness", env=plain)
        git(foreign, "branch", "-M", "main", env=plain)
        git(foreign, "remote", "add", "origin", str(foreign), env=plain)
        git(foreign, "fetch", "-q", "origin", env=plain)
        foreign_blob = git(foreign, "rev-parse", "refs/remotes/origin/main:scripts/safe_push.py",
                           env=plain).strip()
        env = dict(plain, GIT_DIR=str(foreign / ".git"),
                   GIT_INDEX_FILE=str(foreign / ".git" / "index"),
                   STOICHEIA_PUSH_LOG=str(tmp / "pushes.log"))
        r = subprocess.run(["/bin/sh", str(HERE / "hooks" / "safe-push"),
                            "--_test-skip-checks", "--dry-run"], cwd=WORK, env=env,
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        self.assertFalse(marker.exists(), f"the launcher ran the foreign harness:\n{out}")
        # And the clone's harness ran to the end: a dry run of the clone's HEAD.
        self.assertEqual(r.returncode, 0, out)
        own = git(WORK, "rev-parse", "refs/remotes/origin/main:scripts/safe_push.py",
                  env=plain).strip()
        own_heath = git(WORK, "rev-parse", "refs/remotes/origin/main:scripts/heath.py",
                        env=plain).strip()
        copied = sorted(p.name for p in (tmp / "harness").iterdir())
        self.assertEqual(copied, [f"{own}-{own_heath}"], out)
        self.assertNotIn(foreign_blob, " ".join(copied))

    def test_launcher_unsets_every_repository_variable(self):
        tmp = Path(tempfile.mkdtemp(prefix="launcher-env-359-", dir=TMP))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        bindir, recorded = tmp / "bin", tmp / "git-environment.json"
        bindir.mkdir()
        program = ("import json, os, pathlib, sys; "
                   "pathlib.Path(sys.argv[1]).write_text(json.dumps(dict(os.environ))); "
                   "sys.exit(73)")
        shim = bindir / "git"
        shim.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -c "
                        f"{shlex.quote(program)} {shlex.quote(str(recorded))}\n")
        shim.chmod(0o755)
        env = clean_env()
        env.update({name: "/planted" for name in safe_push.REPOSITORY_VARIABLES})
        env["PATH"] = f"{bindir}{os.pathsep}{env['PATH']}"
        r = subprocess.run(["/bin/sh", str(HERE / "hooks" / "safe-push"), "--dry-run"],
                           cwd=WORK, env=env, capture_output=True, text=True)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 73, out)
        self.assertTrue(recorded.is_file(), f"the launcher did not invoke git:\n{out}")
        seen = json.loads(recorded.read_text())
        repository_environment = {name: value for name, value in seen.items()
                                  if name in safe_push.REPOSITORY_VARIABLES}
        self.assertEqual(repository_environment, {"GIT_NO_REPLACE_OBJECTS": "1"})

    def test_launcher_copies_origin_mains_harness_not_its_replacement(self):
        # Issue #256: origin/main's safe_push.py replaced by a copy that never hands over
        # and does not scan. The launcher copies out and runs origin/main's own, which
        # refuses the token.
        lame = self.replaced("scripts/safe_push.py", "def harness(repo, base: str, rep: Report)"
                             " -> None:\n", "def harness(repo, base, rep):\n    return None\n\n\n"
                             "def _unused(repo, base: str, rep: Report) -> None:\n")
        lame = lame.replace("def secret_scan(", "def secret_scan(*a, **k):\n    return None\n\n\n"
                            "def _unused_scan(", 1)
        theirs = git(WORK, "rev-parse", "refs/remotes/origin/main:scripts/safe_push.py").strip()
        env = self.stand_in(theirs, lame)
        self.assertStandsIn("refs/remotes/origin/main", "scripts/safe_push.py", lame, env)
        self.commit("A token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = subprocess.run(["git", "safe-push", "--_test-skip-checks", *with_branch(())],
                           cwd=WORK, env=clean_env(), capture_output=True, text=True)
        out = self.assertRefused(r, "secret scan")
        self.assertEqual(self.guard(out, "harness"), "ok", out)

    def test_hand_over_compares_origin_mains_harness_not_its_replacement(self):
        # origin/main's safe_push.py replaced by the bytes of a copy that does not scan:
        # that copy, run, still finds that it differs from origin/main's, and hands over.
        copy = self.differing_copy(lambda text: text.replace(
            "def secret_scan(", "def secret_scan(*a, **k):\n    return None\n\n\n"
            "def _unused_scan(", 1))
        theirs = git(WORK, "rev-parse", "refs/remotes/origin/main:scripts/safe_push.py").strip()
        env = self.stand_in(theirs, copy.read_text())
        self.assertStandsIn("refs/remotes/origin/main", "scripts/safe_push.py",
                            copy.read_text(), env)
        self.commit("A token", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
        r = subprocess.run([sys.executable, str(copy), "--_test-skip-checks", "--dry-run",
                            *with_branch(())], cwd=WORK, env=clean_env(), capture_output=True,
                           text=True)
        out = self.assertRefused(r, "secret scan")
        self.assertIn("running origin/main's in its place", out)

    def test_install_hooks_installs_the_launcher(self):
        common = Path(git(WORK, "rev-parse", "--path-format=absolute",
                          "--git-common-dir").strip())
        launcher = common / "stoicheia" / "safe-push"
        self.assertEqual(launcher.read_bytes(), (HERE / "hooks" / "safe-push").read_bytes())
        self.assertIn("stoicheia/safe-push", git(WORK, "config", "--get", "alias.safe-push"))

    def test_harness_variable_checked(self):
        self.good_commit()
        env = clean_env()
        env["STOICHEIA_HARNESS"] = "origin/main"
        r = subprocess.run([sys.executable, str(self.differing_copy()), "--_test-skip-checks",
                            "--branch", BRANCH], cwd=WORK, env=env, capture_output=True,
                           text=True)
        self.assertRefused(r, "STOICHEIA_HARNESS says this is origin/main's harness")

    def test_installed_hook_that_differs_is_noted(self):
        hook = hooks_dir() / "pre-push"
        self.swap_hook(hook.read_text() + "\n# STOICHEIA_SAFE_PUSH, and something else\n")
        self.good_commit()
        out = self.safe_push("--dry-run").stdout
        self.assertEqual(self.guard(out, "pre-push hook"), "note", out)
        self.assertIn("differs from origin/main's scripts/hooks/pre-push", out)


class PrivatePaths(Edge):
    """(5) Scratchpad paths, in a file or a message; private paths and machine-made
    identities in a commit's author or committer."""

    def test_scratchpad_paths_refused(self):
        self.commit("Notes with a scratchpad path", {
            "docs/notes.md": f"Read {SCRATCHPAD} first.\n",
            "docs/project.md": f"The project directory is {FOLDED_HOME}-dev-stoicheia.\n"})
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/notes.md", "docs/project.md")

    def test_private_identities_refused(self):
        env = dict(os.environ, GIT_AUTHOR_NAME="someone", GIT_AUTHOR_EMAIL="someone@laptop.local",
                   GIT_COMMITTER_NAME="/" + "Users" + "/someone",
                   GIT_COMMITTER_EMAIL="someone@example.invalid")
        sha = self.commit("A commit by a made-up identity", {
            "docs/reading.md": self.text("docs/reading.md") + "\nA line.\n"}, env=env)
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, f"commit {sha[:12]} author", f"commit {sha[:12]} committer")
        self.assertIn("machine-made identity", out)
        self.assertIn("private path in an identity", out)


class HiddenFiles(Edge):
    """(6) A file marked binary or -diff by .gitattributes, or made binary by a NUL, or
    written in UTF-16, is still scanned."""

    def test_gitattributes_cannot_hide_a_file(self):
        self.commit("Hide two files from the diff", {
            ".gitattributes": "docs/hidden.md binary\ndocs/nodiff.md -diff\n",
            "docs/hidden.md": f"api_token = \"{TOKEN}\"\n",
            "docs/nodiff.md": f"see {SCRATCHPAD}\n"})
        # Installed in the clone as well, as a checkout would have it.
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/hidden.md", "docs/nodiff.md")

    def test_nul_and_utf16_cannot_hide_a_file(self):
        self.commit("Two files that read as binary", {
            "docs/nul.md": b"\0" + f"api_token = \"{TOKEN}\"\n".encode(),
            "docs/wide.md": f"api_token = \"{TOKEN}\"\n".encode("utf-16")})
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/nul.md", "docs/wide.md")

    def test_utf16_after_8_kb_of_prose_or_binary_junk_refused(self):
        # Review note 4: a NUL anywhere makes a file binary, and UTF-16 text is read
        # wherever it stands, not only at the start.
        prose = ("An ordinary line of prose, of the kind a guide is made of.\n" * 160).encode()
        self.assertGreater(len(prose), 8000)
        wide = f"token = {GH_TOKEN}\n".encode("utf-16-le")
        junk = bytes(range(256)) * 4
        self.commit("Two files with UTF-16 text late in them", {
            "docs/early.md": prose, "docs/late.md": prose + wide,
            "docs/junk.bin": junk + f"api_token = \"{TOKEN}\"\n".encode("utf-16-be")})
        out = self.assertRefused(self.safe_push(), "secret scan")
        self.assertFlagged(out, "docs/late.md", "docs/junk.bin")
        self.assertFalse(self.flagged(out, "docs/early.md"), out)
        self.assertNotIn(GH_TOKEN, out)


class AllowList(Edge):
    """(7) An allow-list entry is narrow: one file, one rule, a long enough match, a reason."""

    def test_broad_entries_refused(self):
        narrow = Secrets.ALLOW
        for broad, problem in ((narrow.replace('"docs/notes.md"', '"docs/*"'), "a glob in path"),
                               (narrow.replace('rule = "key, token or secret"\n', ""),
                                "names no rule"),
                               (narrow.replace('match = "api_token"', 'match = "api"'),
                                "match of at least 8"),
                               (narrow.replace('"docs/notes.md"', '"commit 0123456789ab message"'),
                                "cannot be allowed"),
                               (narrow.replace('"docs/notes.md"', '"the pull request\'s body"'),
                                "cannot be allowed")):
            with self.subTest(problem=problem):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                git(ORIGIN, "update-ref", "refs/heads/main", BASE)
                main = self.new_base("A broad entry", {"scripts/safe_push_allow.toml": broad})
                self.commit("A flagged line", {"docs/notes.md": f"api_token = \"{TOKEN}\"\n"})
                r = self.safe_push("--dry-run")
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("broad or incomplete entry", out)
                self.assertIn(problem, out)
                self.assertEqual(self.origin_main(), main)

    def test_an_entry_excuses_its_own_value_alone(self):
        # Review note 5: an entry pins the value it excuses; another token on a line like
        # it, added later, is still refused.
        self.new_base("Allow a fixture", {"scripts/safe_push_allow.toml": Secrets.ALLOW})
        other = base64.b64encode(hashlib.sha256(b"another planted token").digest()).decode()
        self.commit("The allowed line, and another like it", {
            "docs/notes.md": f"api_token = \"{TOKEN}\"\napi_token = \"{other}\"\n"})
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        fail = out[out.index("FAIL  secrets:"):out.index("REFUSED")]
        self.assertIn("docs/notes.md:2: key, token or secret", fail)
        self.assertNotIn("docs/notes.md:1:", fail)
        self.assertIn("A fixture for the test", out)       # line 1, allowed

    def test_a_binary_files_entry_is_as_narrow(self):
        # In a binary file a finding's text is a window around the hit, not the whole
        # file: eight bytes from elsewhere in it excuse nothing, and the report prints
        # no more than the window.
        far = b"FARAWAY-WORDS-" * 20
        blob = far + b"\0" + b"x" * 100 + b"\0\x01\x02" + GH_TOKEN.encode() + b"\0\x03" \
            + b"PADDING!" * 20
        allow = ('[[allow]]\npath = "docs/blob.bin"\nmatch = "FARAWAY-WORDS-"\n'
                 'rule = "GitHub token"\n'
                 f'sha256 = "{hashlib.sha256(b"something else").hexdigest()}"\n'
                 'reason = "A fixture for the test."\n')
        self.new_base("Allow a fixture in a binary file", {"scripts/safe_push_allow.toml": allow})
        self.commit("A binary file holding a token", {"docs/blob.bin": blob})
        r = self.safe_push("--dry-run")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertTrue(self.flagged(out, "docs/blob.bin"), out)
        self.assertNotIn("FARAWAY", out)
        self.assertNotIn(GH_TOKEN, out)

    def test_allow_listed_notes_name_no_flagged_line(self):
        # The final review: an allowed finding's note goes into the public body, and its
        # line may hold a value too short to mask, or a second flagged value. The note
        # names its place, rule and the value's SHA-256 instead, and the body passes.
        bare, key = "/" + "Users" + "/", "AK" + "IA" + "IOSFODNN7EXAMPLE"

        def entry(rule: str, value: str, match: str) -> str:
            return (f'[[allow]]\npath = "docs/notes.md"\nmatch = "{match}"\nrule = "{rule}"\n'
                    f'sha256 = "{hashlib.sha256(value.encode()).hexdigest()}"\n'
                    'reason = "A fixture for the test."\n')
        self.new_base("Allow three fixtures", {"scripts/safe_push_allow.toml": (
            entry("private path", bare, "The scan refuses any path")
            + entry("AWS access key", key, "A fixture line:")
            + entry("private path", FOLDED_HOME, "A fixture line:"))})
        self.commit("Lines holding allowed values", {"docs/notes.md": (
            f"The scan refuses any path under {bare} in a page.\n\n"
            f"A fixture line: {key} beside {FOLDED_HOME} here.\n")})
        r = self.safe_push()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "secrets"), "ok", out)
        body = self.gh_state()["prs"][0]["body"]
        safe_push.check_body(body)
        self.assertEqual(body.count("- allow-listed: docs/notes.md:"), 3, body)
        self.assertIn("(value sha256 ", body)
        for value in (bare, key, FOLDED_HOME):
            self.assertNotIn(value, body)

    def test_the_committed_allow_list_is_narrow(self):
        # The no-mistakes review: the committed allow-list (origin/main's here, BASE) is read
        # by load_allowlist itself, which refuses a broad entry, so the test bites whether
        # or not the list has entries: every entry it holds is read, and an entry planted
        # in it is read when narrow and refused when broad.
        import tomllib
        path = safe_push.ALLOWLIST
        text = (SOURCE / path).read_text()
        self.assertEqual(safe_push.show(WORK, BASE, path), text)
        held = safe_push.load_allowlist(WORK, BASE)
        self.assertEqual(len(held), len(tomllib.loads(text).get("allow", [])))
        narrow = self.commit("A narrow entry", {path: text + "\n" + Secrets.ALLOW})
        digest = hashlib.sha256(TOKEN.encode()).hexdigest()
        self.assertEqual(safe_push.load_allowlist(WORK, narrow)[len(held):], [safe_push.Allow(
            "docs/notes.md", "api_token", "key, token or secret",
            "A fixture for the test, not a real token.", digest)])
        broad = self.commit("A broad entry", {path: text + "\n" + Secrets.ALLOW.replace(
            '"docs/notes.md"', '"docs/*"')})
        with self.assertRaises(safe_push.Refusal) as refused:
            safe_push.load_allowlist(WORK, broad)
        self.assertIn("a glob in path", str(refused.exception))


# Stands in for sandbox-exec where a test wants the main-checks cache in use without
# macOS's sandbox (CI runs these tests on Linux): it writes the command down, drops
# "-p PROFILE", and runs the rest.
FAKE_SANDBOX = """#!/bin/sh
printf '%s\\n' "$*" >> @LOG@
shift 2
exec "$@"
"""


def sandbox_usable() -> str | None:
    """Why macOS's sandbox-exec cannot be used here, or None when it can."""
    if sys.platform != "darwin":
        return "not macOS, so there is no sandbox-exec"
    try:
        r = subprocess.run(["/usr/bin/sandbox-exec", "-p", "(version 1) (allow default)",
                            "/usr/bin/true"], capture_output=True, text=True)
    except OSError as e:
        return f"sandbox-exec cannot be run here ({e})"
    if r.returncode != 0:
        return ("sandbox-exec cannot apply a profile here, as inside another sandbox: "
                + r.stderr.strip())
    return None


@dataclass
class CheckRun:
    refusal: str | None     # full_checks' refusal, if any
    out: str                # what it printed
    rep: safe_push.Report
    ran: list[str]          # the steps run_step was asked to run, in order
    logs: Path              # this run's logs


# The audit events by which Python starts a process (PEP 578), whichever way it is
# reached: subprocess, os.posix_spawn, the os.exec and os.spawn families, os.system,
# os.fork and os.forkpty. While a test watches (watch_processes), each must start the one
# program allowed, or it is refused, and noted. So must each "import", which Python
# raises only for a module not yet loaded, searching the harness's own directory first
# for it: once the sandbox is set, any module but a builtin is refused (N1 of the
# re-review of #224: platform.mac_ver() imported plistlib then).
PROCESS_EVENTS = frozenset({"subprocess.Popen", "os.posix_spawn", "os.exec", "os.spawn",
                            "os.system", "os.fork", "os.forkpty", "os.startfile"})
WATCHING: list[tuple[str, list]] = []       # (the program allowed, the starts refused)


def watch_hook(event: str, args: tuple) -> None:
    if not WATCHING:
        return
    allowed, refused = WATCHING[-1]
    if event == "import":                   # (module, filename, path, meta_path, path_hooks)
        if safe_push.SANDBOX is not None and args[0] not in sys.builtin_module_names:
            refused.append(["import", args[0]])
            raise PermissionError(f"a module imported once the sandbox was set: {args[0]}")
        return
    if event not in PROCESS_EVENTS:
        return
    program, argv = None, [event]
    if event == "subprocess.Popen":         # (executable, args, cwd, env)
        executable, given = args[0], args[1]
        argv = list(given) if isinstance(given, (list, tuple)) else [given]
        program = executable if executable is not None else (argv[0] if argv else None)
    elif event in ("os.posix_spawn", "os.exec"):        # (path, argv, env)
        program, argv = args[0], list(args[1])
    elif event == "os.spawn":               # (mode, path, args, env)
        program, argv = args[1], list(args[2])
    if program is not None and os.fsdecode(program) == allowed:
        return
    refused.append([os.fsdecode(a) if isinstance(a, (str, bytes, os.PathLike)) else repr(a)
                    for a in argv])
    raise PermissionError(f"a process started outside the sandbox: {argv}")


# The same watch in a pre-flight run as its own process, put on its PYTHONPATH as
# sitecustomize.py: once the harness has the sandbox in use (its SANDBOX set), each
# process it starts is noted in the file @LOG@ names, as through the sandbox or not, and
# each module it imports but a builtin is noted and refused.
WATCH_SITECUSTOMIZE = """import os
import sys

EVENTS = @EVENTS@
LOG = @LOG@
SEEN = []


def note(line):
    if line not in SEEN:
        SEEN.append(line)
        with open(LOG, "a") as f:
            f.write(line + "\\n")


def hook(event, args):
    if event not in EVENTS and event != "import":
        return
    main = sys.modules.get("__main__")
    if getattr(main, "SANDBOX", None) is None:
        return
    if event == "import":
        if args[0] not in sys.builtin_module_names:
            note("imported: " + args[0])
            raise PermissionError("a module imported once the sandbox was set: " + args[0])
        return
    program, argv = None, [event]
    if event == "subprocess.Popen":
        argv = list(args[1]) if isinstance(args[1], (list, tuple)) else [args[1]]
        program = args[0] if args[0] is not None else argv[0]
    elif event in ("os.posix_spawn", "os.exec"):
        program, argv = args[0], list(args[1])
    elif event == "os.spawn":
        program, argv = args[1], list(args[2])
    inside = program is not None and os.fsdecode(program) == main.SANDBOX_EXEC
    note("through the sandbox" if inside else "outside: " + " ".join(map(str, argv)))


sys.addaudithook(hook)
"""


# Step 4 watched in a fresh interpreter, so that no module the test process has already
# loaded can hide one imported late: this script, run with -I, imports safe_push, sets it
# up as open_cache leaves it (the stand-in for sandbox-exec, origin/main's harness, the
# stand-in toolchain on the PATH, the steps given), forgets the modules named, imports
# the late ones once the sandbox is set, parses origin/main's allow-list, and runs
# full_checks twice on the commit, a miss and then a hit, with the same watch as
# WATCH_SITECUSTOMIZE's but refusing a process outside the sandbox as well. It writes
# what it saw, the allow-list count, each run's steps and any error to the file named,
# as JSON.
STEP4_WATCH = """import json
import os
import sys

ARGS = json.loads(sys.argv[1])
EVENTS = frozenset(ARGS["events"])
SEEN = []
HARNESS = []


def hook(event, args):
    if not HARNESS or HARNESS[0].SANDBOX is None:
        return
    if event == "import":
        if args[0] not in sys.builtin_module_names:
            SEEN.append("imported: " + args[0])
            raise PermissionError("a module imported once the sandbox was set: " + args[0])
        return
    if event not in EVENTS:
        return
    program, argv = None, [event]
    if event == "subprocess.Popen":
        argv = list(args[1]) if isinstance(args[1], (list, tuple)) else [args[1]]
        program = args[0] if args[0] is not None else argv[0]
    elif event in ("os.posix_spawn", "os.exec"):
        program, argv = args[0], list(args[1])
    elif event == "os.spawn":
        program, argv = args[1], list(args[2])
    if program is not None and os.fsdecode(program) == HARNESS[0].SANDBOX_EXEC:
        return
    SEEN.append("outside: " + " ".join(map(str, argv)))
    raise PermissionError("a process started outside the sandbox: " + " ".join(map(str, argv)))


sys.addaudithook(hook)
sys.path.insert(0, ARGS["here"])
import safe_push  # noqa: E402
from pathlib import Path  # noqa: E402
import tempfile  # noqa: E402

sp = safe_push
# The sequence step 4 runs is given to full_checks, as check_list gives it, and differs
# from the built-in CHECKS, which the cache's key must not read.
SEQUENCE = [(name, cmd) for name, cmd in ARGS["checks"]]
sp.NEGATIVE = [(name, cmd) for name, cmd in ARGS["negative"]]
sp.SANDBOX_EXEC = ARGS["sandbox_exec"]
sp.HARNESS_BLOB = sp.blob_id(Path(sp.__file__).read_bytes())
TOOLS = dict(os.environ, PATH=ARGS["path"])
sp.tool_env = lambda: dict(TOOLS)
ctx = sp.Context(Path(ARGS["work"]), ARGS["sha"], ARGS["base"], 1, ARGS["origin"], None, {})
inputs = [tuple(change) for change in ARGS["inputs"]]
for run in ("miss", "hit"):
    os.makedirs(os.path.join(ARGS["logs"], run))
for name in ARGS["forget"]:
    sys.modules.pop(name, None)
reader = sp.count_markers(ctx.repo, ctx.base)
if ARGS["apart"]:
    sys.modules.pop("dataclasses", None)
runs, allow_count, listed, error = {}, None, None, None
apart = None
HARNESS.append(sp)
sp.CACHE, sp.SANDBOX = Path(ARGS["cache"]), "(version 1) (allow default)"
try:
    for name in ARGS["late"]:
        __import__(name)
    if ARGS["apart"]:
        payload = ("open(" + repr(ARGS["sentinel"]) + ", 'w').write('executed')\\n"
                   "open(" + repr(ARGS["cache_plant"]) + ", 'w').write('written')\\n")
        planted = sp.run(["/bin/sh", "-c", 'printf %s "$1" > "$2"', "sh", payload,
                          os.path.join(ARGS["here"], "dataclasses.py")], ctx.repo)
        if planted.returncode != 0:
            raise RuntimeError("the sandboxed child did not plant dataclasses.py: "
                               + planted.stderr)
        apart_rep = sp.Report()
        apart_rep.add("4", SEQUENCE[0][0] + sp.BASE_PASS, "note", "for the test")
        apart = {"refused": sp.keep_apart(ctx.repo, ctx.base, ctx.sha, apart_rep, "4"),
                 "steps": [[s.name, s.outcome] for s in apart_rep.steps]}
    allow_count = len(sp.load_allowlist(ctx.repo, ctx.base))
    # origin/main's registry, read as step 4's check list reads it, by its own reader.
    read = sp.check_sequence(ctx.repo, ctx.base)
    listed = [[name, cmd] for name, cmd in read.steps]
    for run in ("miss", "hit"):
        rep = sp.Report()
        with tempfile.TemporaryDirectory(dir=ARGS["tmp"]) as tmp:
            with sp.worktree(ctx.repo, ctx.sha, Path(tmp), "check") as wt:
                sp.full_checks(ctx, wt, Path(tmp), inputs, rep,
                               Path(os.path.join(ARGS["logs"], run)), SEQUENCE)
        runs[run] = [[s.name, s.outcome, s.detail] for s in rep.steps]
except BaseException as e:
    error = type(e).__name__ + ": " + str(e)
finally:
    sp.SANDBOX = None
with open(ARGS["out"], "w") as f:
    json.dump({"seen": SEEN, "runs": runs, "allow_count": allow_count, "listed": listed,
               "error": error,
               "reader": reader is not None, "apart": apart,
               "planted": os.path.exists(os.path.join(ARGS["here"], "dataclasses.py")),
               "executed": os.path.exists(ARGS["sentinel"]),
               "cache_written": os.path.exists(ARGS["cache_plant"])}, f)
"""


@contextlib.contextmanager
def watch_processes(allowed: str):
    """Every process started inside the block that is not `allowed` (by its path, as
    run() names the sandbox) is refused, and listed in what this yields. The audit hook,
    once added, stays for the life of the process, and does nothing while none watches."""
    if not getattr(watch_processes, "hooked", False):
        sys.addaudithook(watch_hook)
        watch_processes.hooked = True
    refused: list[list[str]] = []
    WATCHING.append((allowed, refused))
    try:
        yield refused
    finally:
        WATCHING.pop()


class MainChecksCache(Edge):
    """#224: --main-checks-cache keeps origin/main's pass of step 4 by the exact trees it
    ran on, and the harness, toolchain and environment it ran with. A miss runs the pass
    and writes an entry; a hit reports the recorded steps, notes as notes, runs none of
    them, and keep_apart refuses on it as on a miss. Every planted fault in an entry or its
    directory is refused, and the pass recomputed. Without the flag, or without a sandbox,
    or for a change of R0 to R2, nothing is read or written. While the cache is in use, no
    process starts but through the sandbox, and no module is imported but a builtin, in
    the test process and in a fresh one. On macOS, a command run through run() cannot
    write the cache, nor rename a directory above it, but can write elsewhere, and a
    profile that has lost the rules above the cache is caught. No Lean: the toolchain is a
    fixed stand-in, and the steps are stand-ins or Python checks."""

    TOOLCHAIN = {"lean-toolchain": "leanprover/lean4:v4.35.0\n",
                 "lean --version": "Lean (version 4.35.0, a stand-in)",
                 "lake --version": "Lake version 5.0.0 (a stand-in)",
                 "elan which lean": "/opt/a-stand-in/bin/lean"}
    CHECKS = [("check one", ["true"]), ("check two", ["true"])]
    NEGATIVE = [("negative: check three", ["true"])]
    # The stand-in steps that fail with origin/main's copies, and are noted.
    NOTES = {"check two" + safe_push.BASE_PASS, "negative: check three" + safe_push.BASE_PASS}
    # A class whose step 4 runs in full, which the cache serves (open_cache).
    R3 = safe_push.Risk("R3", "for the test")

    def setUp(self):
        super().setUp()
        self.root = Path(os.path.realpath(tempfile.mkdtemp(prefix="main-checks-", dir=TMP)))
        self.dir = self.root / "main-checks"
        self.dir.mkdir()
        self.dir.chmod(0o700)
        self.wrapped = self.root / "sandboxed.log"
        self.fake = self.root / "sandbox-exec"
        self.fake.write_text(FAKE_SANDBOX.replace("@LOG@", shlex.quote(str(self.wrapped))))
        self.fake.chmod(0o755)

    @contextlib.contextmanager
    def active(self, cache: Path | None = None):
        """The cache in use, as open_cache leaves it, with the stand-in for sandbox-exec,
        origin/main's harness running, and the stand-in toolchain."""
        with mock.patch.object(safe_push, "CACHE", cache or self.dir), \
                mock.patch.object(safe_push, "SANDBOX", "(version 1) (allow default)"), \
                mock.patch.object(safe_push, "SANDBOX_EXEC", str(self.fake)), \
                mock.patch.object(safe_push, "HARNESS_BLOB",
                                  safe_push.blob_id(SAFE_PUSH.read_bytes())), \
                mock.patch.object(safe_push, "toolchain",
                                  lambda repo, sha, wt: dict(self.TOOLCHAIN)):
            yield

    def stub(self, stage, name, cmd, cwd, rep, logs, index, fail="FAIL", excludes=()):
        """run_step for the stand-in steps: the NOTES fail, the rest pass; nothing runs."""
        out = f"the output of {name}\n"
        log = logs / f"{index:02d}{safe_push.slug_of(name)}.log"
        log.write_text(out)
        if name not in self.NOTES:
            rep.add(stage, name, "ok", "", 0.25)
            return out
        rep.add(stage, name, fail, f"full output in {log}\n{safe_push.tail(out)}", 0.5)
        if fail == "FAIL":
            raise safe_push.Refusal(f"`{name}` failed on the commit")
        return out

    def inputs(self, sha: str) -> list[tuple[str, str]]:
        return [(st, p) for st, p in safe_push.changed_files(WORK, BASE, sha)
                if safe_push.under(p, safe_push.CHECK_INPUTS)]

    def checks(self, sha: str, checks=None, negative=None, stub=None) -> CheckRun:
        """safe_push.full_checks on `sha` in a throwaway worktree, as step 4 runs it, with
        the sequence it is given (check_list's) and NEGATIVE the stand-ins unless given,
        and run_step watched (and stood in for, when `stub` is given). The built-in CHECKS
        is left as it is, and differs from the sequence, as origin/main's registry may."""
        rep, out, ran = safe_push.Report(), io.StringIO(), []
        ctx = safe_push.Context(WORK, sha, BASE, 1, str(ORIGIN), None, {})
        logs = Path(tempfile.mkdtemp(prefix="logs-", dir=self.root))
        real = safe_push.run_step

        def watched(stage, name, *args, **kwargs):
            ran.append(name)
            return (stub or real)(stage, name, *args, **kwargs)
        refusal = None
        sequence = self.CHECKS if checks is None else checks
        with tempfile.TemporaryDirectory(dir=TMP) as tmp, \
                mock.patch.object(safe_push, "NEGATIVE",
                                  self.NEGATIVE if negative is None else negative), \
                mock.patch.object(safe_push, "run_step", watched), \
                contextlib.redirect_stdout(out):
            parent = Path(tmp)
            with safe_push.worktree(WORK, sha, parent, "check") as wt:
                try:
                    safe_push.full_checks(ctx, wt, parent, self.inputs(sha), rep, logs,
                                          sequence)
                except safe_push.Refusal as e:
                    refusal = str(e)
        return CheckRun(refusal, out.getvalue(), rep, ran, logs)

    def check_change(self, path: str = "scripts/check_links.py") -> str:
        """A commit from BASE that changes one check, and nothing the checks judge."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        return self.commit(f"A comment in {path}", {path: self.text(path) + "\n# for the test\n"})

    def counted_judged_change(self) -> str:
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        fields = self.text("Certificate/FIELDS.md")
        moved, count = re.subn(
            r"(<!-- count:vocabulary -->)([0-9]+)(<!-- /count -->)",
            lambda m: f"{m[1]}{int(m[2]) + 1}{m[3]}", fields)
        self.assertEqual(count, 1)
        return self.commit("A count, a check and judged content", {
            "Certificate/FIELDS.md": moved,
            "scripts/check_links.py": self.text("scripts/check_links.py")
                                      + "\n# for the test\n",
            "Elements/Foundations/Tacit/Metric.lean":
                self.text("Elements/Foundations/Tacit/Metric.lean")
                + "\n-- A line for the test.\n"})

    def entries(self) -> list[Path]:
        return sorted(p for p in self.dir.iterdir() if p.suffix == ".json")

    @staticmethod
    def cache_lines(rep: safe_push.Report) -> list[str]:
        return [s.detail for s in rep.steps if s.name == "main-checks cache"]

    @staticmethod
    def class_of(out: str) -> str | None:
        """The class a pre-flight's step 4 reports (risk_class)."""
        m = re.search(r"^\s+ok\s+class: (R[0-5]), ", out, re.M)
        return m.group(1) if m else None

    @staticmethod
    def outcomes(rep: safe_push.Report) -> list[tuple[str, str]]:
        return [(s.name, s.outcome) for s in rep.steps
                if s.stage == "4" and s.name != "main-checks cache"]

    def base_names(self, steps=None) -> list[str]:
        return [n + safe_push.BASE_PASS for n, _ in (steps or self.CHECKS + self.NEGATIVE)]

    def own_names(self, steps) -> list[str]:
        return [n + " (the commit's checks)" for n, _ in steps]

    @staticmethod
    def put(path: Path, data: bytes, mode: int = 0o600) -> None:
        if path.is_symlink() or path.exists():
            path.unlink()
        path.write_bytes(data)
        path.chmod(mode)

    def test_the_base_tree_is_the_tree_base_copies_lays_down(self):
        # A check changed, one added, one deleted, one made executable, and one made a
        # symbolic link: each kind of change base_copies undoes.
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        (WORK / "scripts/check_links.py").write_text(self.text("scripts/check_links.py")
                                                     + "\n# for the test\n")
        (WORK / "scripts/a_check_for_the_test.py").write_text("print('added')\n")
        (WORK / "tests/a_directory_for_the_test").mkdir()
        (WORK / "tests/a_directory_for_the_test/x.py").write_text("print('added')\n")
        (WORK / "scripts/check_kernel.py").chmod(0o755)
        (WORK / "review/terms.toml").unlink()
        os.symlink("SCHEMA.md", WORK / "review/terms.toml")
        git(WORK, "add", "-A", "--", "scripts", "tests", "review")
        git(WORK, "rm", "-q", "--", "tests/test_screen.py")
        sha = self.commit("Five kinds of change to the check inputs")
        inputs = self.inputs(sha)
        self.assertEqual({s for s, _ in inputs}, {"A", "M", "D", "T"}, inputs)
        tree = safe_push.base_tree(WORK, BASE, sha, inputs)
        self.assertEqual(git(WORK, "status", "--porcelain"), "", "the repository's index moved")
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            parent = Path(tmp)
            env = dict(os.environ, GIT_INDEX_FILE=str(parent / "index"))
            with safe_push.worktree(WORK, sha, parent, "check") as wt:
                with safe_push.base_copies(WORK, BASE, wt, inputs):
                    git(wt, "read-tree", "HEAD", env=env)
                    git(wt, "add", "-A", env=env)
                    laid = git(wt, "write-tree", env=env).strip()
        self.assertEqual(tree, laid)
        self.assertNotEqual(tree, git(WORK, "rev-parse", f"{sha}^{{tree}}").strip())
        for _, path in inputs:
            self.assertEqual(git(WORK, "ls-tree", tree, "--", path),
                             git(WORK, "ls-tree", BASE, "--", path), path)

    def test_the_key_changes_with_each_field(self):
        sha = self.check_change()
        other_check = self.check_change("scripts/check_kernel.py")
        git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
        content_too = self.commit("A check, and a line of reading", {
            "scripts/check_links.py": self.text("scripts/check_links.py") + "\n# for the test\n",
            "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"})
        ctx = safe_push.Context(WORK, sha, BASE, 1, str(ORIGIN), None, {})

        def fields(ctx=ctx, sha=sha, sequence=self.CHECKS) -> dict:
            found, why = safe_push.main_checks_fields(ctx._replace(sha=sha), WORK,
                                                      self.inputs(sha), sequence)
            self.assertIsNotNone(found, why)
            return found

        def key(**kwargs) -> str:
            return safe_push.sha256_of(fields(**kwargs))

        with self.active():
            first = key()
            self.assertEqual(key(), first, "the same trees and run, another key")
            # LANG is keyed by its name, not as a prefix: a variable that merely begins with
            # it is not written into the entry.
            for name in ("UNRELATED_FOR_THE_TEST", "LANGCHAIN_FOR_THE_TEST"):
                with mock.patch.dict(os.environ, {name: "1"}):
                    self.assertEqual(key(), first, f"{name}, which the key does not name, "
                                     "moved it")
            # The harness's own plumbing, which no check reads, parts no runs: a run handed
            # over from a worktree and a run of the launcher share keys.
            self.assertEqual(safe_push.UNKEYED_VARIABLES,
                             {"STOICHEIA_HARNESS", "STOICHEIA_PUSH_LOG", "STOICHEIA_PYTHON"})
            # Nor the terminal's, which begin LC_ and are no locale: a dry run and a push
            # from two terminals share keys.
            self.assertEqual(safe_push.TERMINAL_VARIABLES, {"LC_TERMINAL", "LC_TERMINAL_VERSION"})
            for name in sorted(safe_push.UNKEYED_VARIABLES | safe_push.TERMINAL_VARIABLES):
                with mock.patch.dict(os.environ, {name: "/a/stand-in"}):
                    self.assertEqual(key(), first, f"{name} moved the key")
            # Two commits with one base tree (origin/main's, both changing a check alone)
            # differ in the tree the checks compare it with, so in the key.
            self.assertEqual(fields(sha=other_check)["base_tree"], fields()["base_tree"])
            moved = {
                "origin/main": key(ctx=ctx._replace(base=git(WORK, "rev-parse",
                                                             f"{BASE}^").strip())),
                "the base tree": key(sha=content_too),
                "the commit's tree": key(sha=other_check),
            }
            with mock.patch.object(safe_push, "HARNESS_BLOB", "0" * 40):
                moved["the harness"] = key()
            with mock.patch.object(safe_push, "toolchain", lambda repo, sha, wt: dict(
                    self.TOOLCHAIN, **{"lean --version": "Lean (version 4.36.0)"})):
                moved["the toolchain"] = key()
            for name, value in (("STOICHEIA_FOR_THE_TEST", "1"), ("STOICHEIA_FOR_THE_TEST", "2"),
                                ("LEAN_PATH", "/a/stand-in"), ("LAKE_HOME", "/a/stand-in"),
                                ("PYTHONWARNINGS", "error"), ("PYTHONPATH", "/a/stand-in"),
                                ("LANG", "C.for-the-test"), ("LANGUAGE", "for-the-test"),
                                ("LC_ALL", "C.for-the-test"), ("LC_CTYPE", "C.for-the-test")):
                with mock.patch.dict(os.environ, {name: value}):
                    moved[f"{name}={value}"] = key()
            # The checks step 4 runs, origin/main's registry's, and not the built-in CHECKS:
            # one more check, or the model's job after them, as every real sequence ends.
            moved["one check more"] = key(sequence=self.CHECKS + [("check four", ["true"])])
            moved["the model's job"] = key(sequence=self.CHECKS + safe_push.MODEL_JOB)
            with mock.patch.object(safe_push, "CHECKS", self.CHECKS + [("check four", ["true"])]):
                self.assertEqual(key(), first, "the built-in CHECKS moved the key")
            with mock.patch.object(safe_push, "NEGATIVE", self.NEGATIVE[:0]):
                moved["NEGATIVE"] = key()
            for name, value in moved.items():
                self.assertNotEqual(value, first, name)
            self.assertEqual(len(set(moved.values())), len(moved), moved)
            # No key without origin/main's harness, or without the toolchain.
            with mock.patch.object(safe_push, "HARNESS_BLOB", None):
                self.assertEqual(safe_push.main_checks_fields(ctx, WORK, self.inputs(sha),
                                                              self.CHECKS),
                                 (None, "the harness running is not origin/main's"))
            with mock.patch.object(safe_push, "toolchain", lambda repo, sha, wt: None):
                self.assertIsNone(safe_push.main_checks_fields(ctx, WORK, self.inputs(sha),
                                                               self.CHECKS)[0])

    def test_a_miss_writes_an_entry_and_a_hit_runs_nothing_of_origin_mains_pass(self):
        sha = self.check_change()
        with self.active():
            miss = self.checks(sha, stub=self.stub)
            (path,) = self.entries()
            hit = self.checks(sha, stub=self.stub)
        for r in (miss, hit):
            self.assertIsNone(r.refusal, r.out)
        key = path.stem
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual(key, safe_push.sha256_of(json.loads(path.read_bytes())["key"]))
        (line,) = self.cache_lines(miss.rep)
        self.assertTrue(line.startswith("miss (no entry for this key)"), line)
        (line,) = self.cache_lines(hit.rep)
        self.assertTrue(line.startswith(f"hit: origin/main's checks of these trees reused from "
                                        f"entry {key[:12]}"), line)
        # The miss ran both passes; the hit, the commit's own alone.
        self.assertEqual(miss.ran, self.base_names(self.CHECKS) + self.own_names(self.CHECKS)
                         + self.base_names(self.NEGATIVE) + self.own_names(self.NEGATIVE))
        self.assertEqual(hit.ran, self.own_names(self.CHECKS) + self.own_names(self.NEGATIVE))
        # The same outcomes, in the same order, notes included.
        self.assertEqual(self.outcomes(hit.rep), self.outcomes(miss.rep))
        self.assertEqual([o for n, o in self.outcomes(hit.rep) if n in self.NOTES],
                         ["note", "note"])
        for step in hit.rep.steps:
            if step.name in self.base_names():
                self.assertTrue(step.detail.startswith(
                    f"reused from the cache, entry {key[:12]}, written "), step.detail)
                self.assertIsNone(step.seconds)
        # Each recorded log is written among the hit's logs, and a note points to that
        # copy, not to the log of the run that wrote the entry.
        log = hit.logs / f"12{safe_push.slug_of('check two' + safe_push.BASE_PASS)}.log"
        self.assertEqual(log.read_text(), "the output of check two (origin/main's checks)\n")
        noted = next(s for s in hit.rep.steps if s.name == "check two" + safe_push.BASE_PASS)
        self.assertIn(f"full output in {log}\n", noted.detail)
        self.assertNotIn(str(miss.logs), noted.detail)
        # Every command went through the stand-in for sandbox-exec (run), git with
        # replacement objects off (#256).
        self.assertIn(f"git {' '.join(safe_push.NO_REPLACE_REFS)} -c core.quotePath=false "
                      "worktree add", self.wrapped.read_text())

    def test_the_key_and_the_entry_follow_the_sequence_step_4_runs(self):
        # Step 4 runs origin/main's registry, whose sequence ends in the model's job and so
        # is never the built-in CHECKS: a miss writes that sequence's pass, keyed by it, and
        # the next run on the same trees replays it (the security review of #229 after
        # #392, finding 1).
        sha = self.check_change()
        sequence = self.CHECKS + safe_push.MODEL_JOB
        self.assertNotEqual(sequence, safe_push.CHECKS)
        with self.active():
            miss = self.checks(sha, checks=sequence, stub=self.stub)
            (path,) = self.entries()
            hit = self.checks(sha, checks=sequence, stub=self.stub)
            # The same trees with another sequence are another key: a miss again.
            other = self.checks(sha, stub=self.stub)
        for r in (miss, hit, other):
            self.assertIsNone(r.refusal, r.out)
        entry = json.loads(path.read_bytes())
        self.assertEqual(entry["key"]["checks"], [[n, c] for n, c in sequence])
        self.assertEqual([s["name"] for s in entry["steps"]],
                         self.base_names(sequence + self.NEGATIVE))
        self.assertTrue(self.cache_lines(hit.rep)[0].startswith("hit: "), hit.out)
        self.assertEqual(hit.ran, self.own_names(sequence) + self.own_names(self.NEGATIVE))
        self.assertTrue(self.cache_lines(other.rep)[0].startswith("miss (no entry"),
                        other.out)
        self.assertEqual(len(self.entries()), 2)

    def test_a_valid_written_timestamp_is_reused(self):
        sha = self.check_change()
        with self.active():
            miss = self.checks(sha, stub=self.stub)
            (path,) = self.entries()
            entry = json.loads(path.read_bytes())
            entry["written"] = "2024-02-29 23:59 UTC"
            entry["digest"] = safe_push.sha256_of(
                {k: v for k, v in entry.items() if k != "digest"})
            self.put(path, json.dumps(entry).encode())
            hit = self.checks(sha, stub=self.stub)
        self.assertIsNone(miss.refusal, miss.out)
        self.assertIsNone(hit.refusal, hit.out)
        self.assertEqual(hit.ran, self.own_names(self.CHECKS) + self.own_names(self.NEGATIVE))
        self.assertTrue(self.cache_lines(hit.rep)[0].startswith("hit: "), hit.out)
        reused = [s.detail for s in hit.rep.steps if s.name in self.base_names()]
        self.assertTrue(reused)
        self.assertTrue(all("written 2024-02-29 23:59 UTC" in detail for detail in reused))

    def test_keep_apart_refuses_on_a_hit_as_on_a_miss(self):
        # The fixture of ProtectedPaths.test_stage_4_keeps_a_check_change_apart: origin/main's
        # check_style.py refuses a page of the edition the commit changes, with the check
        # loosened; here it runs in the negative tests' loop, so that origin/main's pass
        # finishes and is kept before keep_apart refuses.
        path = "scripts/check_style.py"
        sha = self.commit("Loosen check_style.py, and break one of its rules", {
            path: self.replaced(path, "    sys.exit(main())", "    sys.exit(0)"),
            "mishnah/I/01.md": self.text("mishnah/I/01.md") + "\nA tacit assumption, here.\n"})
        name, cmd = ProtectedPaths.STYLE
        negative = [("negative: " + name, cmd)]
        with self.active():
            miss = self.checks(sha, checks=[], negative=negative)
            hit = self.checks(sha, checks=[], negative=negative)
        base = "negative: " + name + safe_push.BASE_PASS
        for r in (miss, hit):
            self.assertEqual(r.refusal, "a check changed together with what it checks", r.out)
            self.assertEqual(self.guard(r.out, base), "note", r.out)
            self.assertEqual(self.guard(r.out, "check change kept apart"), "FAIL", r.out)
        self.assertEqual(miss.ran, [base])
        self.assertEqual(hit.ran, [])
        self.assertIn("hit:", self.cache_lines(hit.rep)[0])

        def kept(r: CheckRun) -> str:
            return next(s.detail for s in r.rep.steps if s.name == "check change kept apart")
        self.assertEqual(kept(hit), kept(miss))
        self.assertIn("mishnah/I/01.md", kept(hit))

    def test_nothing_is_written_unless_origin_mains_pass_finished(self):
        # A check change with judged content, kept apart after the checks' loop: the
        # negative tests' loop of origin/main's pass never runs, so nothing is kept.
        sha = self.commit("A check, and a line of the edition", {
            "scripts/check_links.py": self.text("scripts/check_links.py") + "\n# for the test\n",
            "mishnah/I/01.md": self.text("mishnah/I/01.md") + "\nA line for the test.\n"})
        with self.active():
            r = self.checks(sha, stub=self.stub)
        self.assertEqual(r.refusal, "a check changed together with what it checks", r.out)
        self.assertEqual(r.ran, self.base_names(self.CHECKS))
        self.assertEqual(self.entries(), [])

    def test_planted_faults_are_refused_and_the_pass_recomputed(self):
        sha = self.check_change()
        with self.active():
            self.checks(self.check_change("scripts/check_kernel.py"), stub=self.stub)
            (another,) = self.entries()
            self.checks(sha, stub=self.stub)
            (path,) = [p for p in self.entries() if p != another]
        good, theirs, key = path.read_bytes(), another.read_bytes(), path.stem

        def changed(data: bytes, change, digest=True) -> bytes:
            entry = json.loads(data)
            change(entry)
            if digest:
                entry["digest"] = safe_push.sha256_of(
                    {k: v for k, v in entry.items() if k != "digest"})
            return json.dumps(entry).encode()

        def noted_made_ok(entry):
            step = next(s for s in entry["steps"] if s["outcome"] == "note")
            step["outcome"] = "ok"

        refused = "the entry was refused: "
        faults = {
            "a note made ok, the digest left as it was": (
                changed(good, noted_made_ok, digest=False),
                refused + "its digest does not match its contents"),
            "another key's entry, a note made ok and its digest recomputed, under this name": (
                changed(theirs, noted_made_ok), refused + "its key fields are not this run's"),
            "a key field written as true, equal to 1 in Python but not in JSON": (
                changed(good, lambda e: e["key"].update(format=True)),
                refused + "its key fields do not hash to its name"),
            "a wrong harness blob": (
                changed(good, lambda e: e["key"].update(harness_blob="0" * 40)),
                refused + "its key fields are not this run's"),
            "a step missing": (changed(good, lambda e: e["steps"].pop(0)),
                               refused + "its steps are not origin/main's pass"),
            "a step extra": (changed(good, lambda e: e["steps"].append(dict(e["steps"][-1]))),
                             refused + "its steps are not origin/main's pass"),
            "the steps out of order": (changed(good, lambda e: e["steps"].reverse()),
                                       refused + "its steps are not origin/main's pass"),
            "an unknown outcome": (changed(good, lambda e: e["steps"][0].update(outcome="pass")),
                                   refused + "its step check one (origin/main's checks) is not "
                                   "of this format (outcome 'pass')"),
            # Each crashed the run once (math.isfinite overflowed; the log could not be
            # written): S3 of the review of #224.
            "a step's seconds an integer of 400 digits": (
                changed(good, lambda e: e["steps"][0].update(seconds=10 ** 400)),
                refused + "its step check one (origin/main's checks) is not of this format "
                "(its seconds are no time a step could take)"),
            "a lone surrogate in a step's log": (
                changed(good, lambda e: e["steps"][1].update(log="half a pair: \ud800\n")),
                refused + "its step check two (origin/main's checks) is not of this format "
                "(its detail or its log is not text this run can write as UTF-8 and print)"),
            "arbitrary text for the written time": (
                changed(good, lambda e: e.update(written="not a timestamp")),
                refused + "its written time is not of this format"),
            "an embedded newline in the written time": (
                changed(good, lambda e: e.update(written="2026-10-\n21 12:34 UTC")),
                refused + "its written time is not of this format"),
            "a trailing newline in the written time": (
                changed(good, lambda e: e.update(written="2026-10-21 12:34 UTC\n")),
                refused + "its written time is not of this format"),
            "an invalid month in the written time": (
                changed(good, lambda e: e.update(written="2026-13-21 12:34 UTC")),
                refused + "its written time is not of this format"),
            "an invalid day in the written time": (
                changed(good, lambda e: e.update(written="2026-02-30 12:34 UTC")),
                refused + "its written time is not of this format"),
            "an invalid hour in the written time": (
                changed(good, lambda e: e.update(written="2026-10-21 24:34 UTC")),
                refused + "its written time is not of this format"),
            "an invalid minute in the written time": (
                changed(good, lambda e: e.update(written="2026-10-21 12:60 UTC")),
                refused + "its written time is not of this format"),
            "not JSON": (good[:-1], refused + "it is not an entry of this format"),
        }
        large = f"it is larger than {safe_push.ENTRY_BYTES} bytes (16 MiB)"
        fstat = os.fstat

        def understated(fd):
            st = fstat(fd)
            if st.st_size <= safe_push.ENTRY_BYTES:
                return st
            fields = list(st[:10])
            fields[6] = len(good)       # st_size
            return os.stat_result(fields)
        elsewhere = self.root / "elsewhere.json"
        self.put(elsewhere, good)
        cases = [(name, lambda data=data: self.put(path, data), why, contextlib.nullcontext)
                 for name, (data, why) in faults.items()]
        cases += [
            ("the entry a symbolic link", lambda: (path.unlink(), path.symlink_to(elsewhere)),
             "the entry is a symbolic link", contextlib.nullcontext),
            ("the entry of mode 0644", lambda: self.put(path, good, 0o644),
             "the entry has mode 0644, not 0600", contextlib.nullcontext),
            # Any error at all in reading an entry, whatever it holds, is a refusal: here
            # entry_problem, which raises on none of the faults above, made to.
            ("any error in reading the entry", lambda: self.put(path, good),
             refused + "it is not an entry of this format (OverflowError)",
             lambda: mock.patch.object(safe_push, "entry_problem",
                                       side_effect=OverflowError("for the test"))),
            # An entry of a tebibyte, sparse, so taking no disk, is refused by its size and
            # never read: read whole, one hung the run (N2 of the re-review of #224).
            ("an entry of a tebibyte", lambda: (self.put(path, good), os.truncate(path, 2 ** 40)),
             refused + large, contextlib.nullcontext),
            # One that is larger than fstat said, as when it grows meanwhile, is refused by
            # what the read returns.
            ("an entry larger than fstat said",
             lambda: (self.put(path, good), os.truncate(path, safe_push.ENTRY_BYTES + 2)),
             refused + large, lambda: mock.patch.object(safe_push.os, "fstat", understated)),
        ]
        for name, plant, why, during in cases:
            with self.subTest(name), self.active():
                plant()
                with during():
                    r = self.checks(sha, stub=self.stub)
                self.assertIsNone(r.refusal, r.out)
                (line,) = self.cache_lines(r.rep)
                self.assertTrue(line.startswith(f"miss ({why}"), f"{line}\n{why}")
                self.assertEqual(r.ran[:2], self.base_names(self.CHECKS), "not recomputed")
                # Recomputed and written afresh, in place of the bad entry: a hit again.
                self.assertFalse(path.is_symlink())
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                fresh = json.loads(path.read_bytes())
                with mock.patch.object(safe_push, "NEGATIVE", self.NEGATIVE):
                    self.assertIsNone(safe_push.entry_problem(fresh, key, fresh["key"]))
                self.assertEqual([(s["name"], s["outcome"]) for s in fresh["steps"]],
                                 [(s["name"], s["outcome"]) for s in json.loads(good)["steps"]])
        self.assertEqual(elsewhere.read_bytes(), good, "the link's target was written")
        # The entry's harness is checked by itself too, beside the key.
        with self.active(), mock.patch.object(safe_push, "HARNESS_BLOB", "0" * 40):
            entry = json.loads(good)
            self.assertEqual(safe_push.entry_problem(entry, key, entry["key"]),
                             "it was written by another harness")
        # The directory a symbolic link, or of mode 0755: refused, recomputed, nothing written.
        link = self.root / "a-link"
        link.symlink_to(self.dir)
        for name, cache, before, after, why in (
                ("the directory a symbolic link", link, lambda: None, lambda: None,
                 f"{link} is a symbolic link"),
                ("the directory of mode 0755", self.dir, lambda: self.dir.chmod(0o755),
                 lambda: self.dir.chmod(0o700), f"{self.dir} has mode 0755, not 0700")):
            with self.subTest(name), self.active(cache):
                self.put(path, good)
                before()
                try:
                    r = self.checks(sha, stub=self.stub)
                finally:
                    after()
                lines = self.cache_lines(r.rep)
                self.assertTrue(lines[0].startswith(f"miss ({why}"), lines)
                self.assertTrue(lines[1].startswith(f"entry {key[:12]} not written: {why}"), lines)
                self.assertEqual(r.ran[:2], self.base_names(self.CHECKS), "not recomputed")
                self.assertEqual(path.read_bytes(), good)

    def test_without_the_flag_nothing_is_read_or_written(self):
        # In a pre-flight: the directory is not even made.
        self.good_commit()
        root = self.root / "unflagged"
        env = clean_env()
        env["STOICHEIA_PUSH_LOG"] = str(root / "pushes.log")
        r = self.safe_push("--dry-run", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertFalse((root / "main-checks").exists(), out)
        self.assertNotIn("main-checks cache", out)
        # In step 4: origin/main's pass runs, and the cache is neither read nor written.
        sha = self.check_change()
        with mock.patch.object(safe_push, "read_entry", side_effect=AssertionError("read")), \
                mock.patch.object(safe_push, "write_entry", side_effect=AssertionError("written")):
            r = self.checks(sha, stub=self.stub)
        self.assertIsNone(r.refusal, r.out)
        self.assertEqual(r.ran[:2], self.base_names(self.CHECKS))
        self.assertEqual(self.cache_lines(r.rep), [])

    def test_the_flag_in_a_pre_flight(self):
        # For a change of R3, whose step 4 runs in full: the directory is made, mode 0700;
        # with macOS's sandbox the cache is in use, and every command from there on (the
        # guards' check_fidelity.py and render.py among them) runs under it, and no process
        # starts but through it, nor any module is imported but a builtin
        # (WATCH_SITECUSTOMIZE), in a dry run (steps 1 to 3 and 5, step 4 being the
        # internal flag's skip) and in the push that follows it; without the sandbox, the
        # run says why and goes on.
        path = "scripts/check_links.py"
        change = {path: self.text(path) + "\n# A comment for the test.\n"}
        change.update(self.decision(f"A comment in `{path}`, for the test."))
        self.commit("A comment in a check", change)
        root = self.root / "flagged"
        env = clean_env()
        env["STOICHEIA_PUSH_LOG"] = str(root / "pushes.log")
        watch, watched = self.root / "watch", self.root / "watched.log"
        watch.mkdir()
        (watch / "sitecustomize.py").write_text(
            WATCH_SITECUSTOMIZE.replace("@EVENTS@", repr(sorted(PROCESS_EVENTS)))
            .replace("@LOG@", repr(str(watched))))
        env["PYTHONPATH"] = str(watch)
        for args in (("--dry-run", "--main-checks-cache"), ("--main-checks-cache",)):
            with self.subTest(args=args):
                watched.unlink(missing_ok=True)
                r = self.safe_push(*args, env=env)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 0, out)
                self.assertEqual(self.class_of(out), "R3", out)
                seen = watched.read_text().splitlines() if watched.exists() else []
                self.assertEqual([line for line in seen if line != "through the sandbox"],
                                 [], out)
                if sandbox_usable() is None:
                    self.assertEqual(seen, ["through the sandbox"], out)
                cache = root / "main-checks"
                self.assertTrue(cache.is_dir() and not cache.is_symlink(), out)
                self.assertEqual(stat.S_IMODE(cache.stat().st_mode), 0o700)
                self.assertEqual(list(cache.iterdir()), [], "the probe left a file")
                self.assertEqual(self.step(out, "main-checks cache"),
                                 "ok" if sandbox_usable() is None else "note", out)
                self.assertEqual(self.step(out, "review records"), "ok", out)
                self.assertEqual(self.step(out, "generated pages"), "ok", out)
        self.assertEqual(self.origin_branch(), git(WORK, "rev-parse", "HEAD").strip())

    def test_the_flag_for_a_train(self):
        # #383: a train/* branch's train check runs origin/main's check_train.py in the
        # harness's own process after the guards have run the commit's code, so with the
        # flag a train gets no cache and no sandbox; and the check refuses to run if one is
        # set, should a later change call it so.
        root = self.root / "train"
        with mock.patch.object(safe_push, "CACHE", None), \
                mock.patch.object(safe_push, "SANDBOX", None), \
                mock.patch.object(safe_push, "sandbox_problem",
                                  side_effect=AssertionError("a sandbox tried")), \
                mock.patch.dict(os.environ, {"STOICHEIA_PUSH_LOG": str(root / "pushes.log")}), \
                contextlib.redirect_stdout(io.StringIO()):
            rep = safe_push.Report()
            safe_push.open_cache(rep, self.R3, train=True)
            self.assertIsNone(safe_push.CACHE)
            self.assertIsNone(safe_push.SANDBOX)
            self.assertEqual(rep.steps[-1].outcome, "note")
            self.assertIn("train/* branch", rep.steps[-1].detail)
        self.assertFalse((root / "main-checks").exists())
        ctx = safe_push.Context(WORK, BASE, BASE, 1, str(ORIGIN), "train/for-the-test", {})
        with mock.patch.object(safe_push, "SANDBOX", "(version 1)"), \
                mock.patch.object(safe_push, "harness_train",
                                  side_effect=AssertionError("check_train was read")), \
                contextlib.redirect_stdout(io.StringIO()):
            rep = safe_push.Report()
            with self.assertRaises(safe_push.Refusal) as caught:
                safe_push.train_check(ctx, "A body.", rep)
        self.assertIn("cannot run once the main-checks cache's sandbox is set",
                      str(caught.exception))

    def test_the_flag_for_a_change_of_r0_to_r2(self):
        # A change of R0 leaves step 4 to CI: there is no pass to reuse, so the flag makes,
        # reads and writes nothing, and sets no sandbox; the run says so.
        self.good_commit()
        root = self.root / "low"
        env = clean_env()
        env["STOICHEIA_PUSH_LOG"] = str(root / "pushes.log")
        r = self.safe_push("--dry-run", "--main-checks-cache", env=env)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.class_of(out), "R0", out)
        self.assertEqual(self.step(out, "main-checks cache"), "skip", out)
        self.assertIn("main-checks cache: not used this run: the class R0 leaves step 4 to "
                      "CI, and the cache serves only step 4 run in full (R3 to R5)", out)
        self.assertEqual(self.step(out, "full local checks"), "skip", out)
        self.assertFalse((root / "main-checks").exists(), out)
        # Nor is a sandbox set, in open_cache itself.
        with mock.patch.object(safe_push, "CACHE", None), \
                mock.patch.object(safe_push, "SANDBOX", None), \
                mock.patch.object(safe_push, "sandbox_problem",
                                  side_effect=AssertionError("a sandbox tried")), \
                mock.patch.dict(os.environ, {"STOICHEIA_PUSH_LOG": str(root / "pushes.log")}), \
                contextlib.redirect_stdout(io.StringIO()):
            for cls in safe_push.LOW_CLASSES:
                rep = safe_push.Report()
                safe_push.open_cache(rep, safe_push.Risk(cls, "for the test"))
                self.assertIsNone(safe_push.SANDBOX)
                self.assertEqual([(s.stage, s.outcome) for s in rep.steps], [("1", "skip")])
        self.assertFalse((root / "main-checks").exists())

    def test_open_cache_refuses_a_directory_it_may_not_use(self):
        real = self.root / "real"
        real.mkdir(mode=0o700)
        cases = {}
        (self.root / "a").mkdir()
        (self.root / "a" / "main-checks").symlink_to(real)
        cases["a symbolic link"] = (self.root / "a", "is a symbolic link")
        (self.root / "b" / "main-checks").mkdir(parents=True)
        (self.root / "b" / "main-checks").chmod(0o755)
        cases["mode 0755"] = (self.root / "b", "has mode 0755, not 0700")
        (self.root / "c").mkdir()
        (self.root / "c" / "main-checks").write_text("")
        cases["a file"] = (self.root / "c", "is not a directory")
        (self.root / "d-real").mkdir()
        (self.root / "d").symlink_to(self.root / "d-real")
        cases["reached through a link"] = (self.root / "d", "is reached through a symbolic link")
        (self.root / 'e"').mkdir()
        cases["a quotation mark"] = (self.root / 'e"', "holds a quotation mark")
        # Something mounted over the directory: its device is not that of the directory
        # above it. (os.lstat stands in for a mount, which would need the system's help.)
        (self.root / "f" / "main-checks").mkdir(parents=True)
        (self.root / "f" / "main-checks").chmod(0o700)
        cases["mounted over"] = (self.root / "f", f"is on another device than {self.root / 'f'}")
        mounted, lstat = str(self.root / "f" / "main-checks"), os.lstat

        def another_device(path, *args, **kwargs):
            st = lstat(path, *args, **kwargs)
            if os.fspath(path) != mounted:
                return st
            fields = list(st[:10])
            fields[2] = st.st_dev + 1       # st_dev
            return os.stat_result(fields)
        for name, (where, why) in cases.items():
            with self.subTest(name), \
                    mock.patch.dict(os.environ, {"STOICHEIA_PUSH_LOG": str(where / "pushes.log")}), \
                    mock.patch.object(safe_push, "CACHE", None), \
                    mock.patch.object(safe_push, "SANDBOX", None), \
                    mock.patch.object(safe_push.os, "lstat", another_device), \
                    contextlib.redirect_stdout(io.StringIO()):
                rep = safe_push.Report()
                safe_push.open_cache(rep, self.R3)
                self.assertIsNone(safe_push.CACHE)
                self.assertIsNone(safe_push.SANDBOX)
                (step,) = rep.steps
                self.assertEqual((step.stage, step.name, step.outcome),
                                 ("1", "main-checks cache", "note"))
                self.assertIn(why, step.detail)
                self.assertTrue(step.detail.startswith("not used this run: "), step.detail)

    def test_without_a_sandbox_there_is_no_cache(self):
        missing = str(self.root / "no-sandbox-exec")
        here = "/no-sandbox-exec is not there" if sys.platform == "darwin" else "not macOS"
        for name, patch, why in (
                ("sandbox-exec missing", mock.patch.object(safe_push, "SANDBOX_EXEC", missing),
                 here),
                ("not macOS", mock.patch.object(safe_push.sys, "platform", "linux"),
                 "this is not macOS")):
            with self.subTest(name), patch, \
                    mock.patch.dict(os.environ, {"STOICHEIA_PUSH_LOG":
                                                 str(self.root / "probe" / "pushes.log")}), \
                    mock.patch.object(safe_push, "CACHE", None), \
                    mock.patch.object(safe_push, "SANDBOX", None), \
                    contextlib.redirect_stdout(io.StringIO()):
                rep = safe_push.Report()
                safe_push.open_cache(rep, self.R3)
                self.assertIsNone(safe_push.CACHE)
                self.assertIsNone(safe_push.SANDBOX)
                (step,) = rep.steps
                self.assertEqual(step.outcome, "note")
                self.assertIn(why, step.detail)
                self.assertEqual(safe_push.run(["git", "--version"], WORK).args[0], "git")
        # And the pre-flight's step 4 is as without the flag.
        sha = self.check_change()
        r = self.checks(sha, stub=self.stub)
        self.assertIsNone(r.refusal, r.out)
        self.assertEqual(r.ran[:2], self.base_names(self.CHECKS))
        self.assertEqual(self.cache_lines(r.rep), [])
        self.assertEqual(self.entries(), [])

    def test_the_sandbox_keeps_every_command_from_the_cache(self):
        why = sandbox_usable()
        if why:
            self.skipTest(f"macOS's sandbox is needed: {why}")
        log = self.root / "sandboxed" / "pushes.log"
        with mock.patch.dict(os.environ, {"STOICHEIA_PUSH_LOG": str(log)}), \
                mock.patch.object(safe_push, "CACHE", None), \
                mock.patch.object(safe_push, "SANDBOX", None), \
                contextlib.redirect_stdout(io.StringIO()):
            rep = safe_push.Report()
            safe_push.open_cache(rep, self.R3)
            cache = log.parent / "main-checks"
            self.assertEqual(safe_push.CACHE, cache, rep.steps)
            self.assertEqual(rep.steps[-1].outcome, "ok")
            write = ["/bin/sh", "-c", 'echo x > "$1"', "sh"]
            r = safe_push.run([*write, str(cache / "planted.json")], self.root)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.lexists(cache / "planted.json"))
            r = safe_push.run([*write, str(self.root / "elsewhere.txt")], self.root)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((self.root / "elsewhere.txt").read_text(), "x\n")
            # Nor may a command rename a directory above the cache, which would carry the
            # cache out from under the rule, to be written and put back.
            for above in (log.parent, log.parent.parent):
                r = safe_push.run(["/bin/mv", str(above), str(self.root / "moved")], self.root)
                self.assertNotEqual(r.returncode, 0, above)
            self.assertTrue(cache.is_dir())
            self.assertEqual(safe_push.git(WORK, "rev-parse", "HEAD").strip(),
                             git(WORK, "rev-parse", "HEAD").strip())

    def test_a_profile_without_the_rules_above_the_cache_is_caught(self):
        # The trial in open_cache writes harmlessly to the directory above the cache
        # (touch -c): a profile that keeps the directory's own rule and has lost the
        # rules above it, under which a rename could carry the cache away, is no sandbox.
        why = sandbox_usable()
        if why:
            self.skipTest(f"macOS's sandbox is needed: {why}")
        log = self.root / "lost" / "pushes.log"

        def lost(cache: Path) -> str:
            return f'(version 1) (allow default) (deny file-write* (subpath "{cache}"))'
        with mock.patch.dict(os.environ, {"STOICHEIA_PUSH_LOG": str(log)}), \
                mock.patch.object(safe_push, "CACHE", None), \
                mock.patch.object(safe_push, "SANDBOX", None), \
                mock.patch.object(safe_push, "sandbox_profile", lost), \
                contextlib.redirect_stdout(io.StringIO()):
            rep = safe_push.Report()
            safe_push.open_cache(rep, self.R3)
            self.assertIsNone(safe_push.CACHE)
            self.assertIsNone(safe_push.SANDBOX)
        (step,) = rep.steps
        self.assertEqual(step.outcome, "note")
        self.assertIn(f"sandbox-exec did not stop a write to {log.parent}, the directory "
                      "above the cache", step.detail)
        self.assertEqual(list((log.parent / "main-checks").iterdir()), [], "the trial left a file")

    def test_a_trial_write_failing_otherwise_than_by_the_sandbox_passes_nothing(self):
        # The trial's harmless write above the cache must fail with the sandbox's own
        # refusal: a failure for any other reason shows nothing of the rule (E4 of the
        # re-review of #224). sandbox-exec is stood in for by what each command answers.
        answers = {}

        def answered(cmd, cwd, **kwargs):
            said = next((said for program, said in answers.items() if program in cmd), "")
            return subprocess.CompletedProcess(cmd, 1 if said else 0, "", said)
        cache = self.dir
        with mock.patch.object(safe_push, "run", answered), \
                mock.patch.object(safe_push.sys, "platform", "darwin"), \
                mock.patch.object(safe_push, "SANDBOX_EXEC", str(self.fake)):
            answers["/bin/sh"] = f"sh: {cache}/.probe: {safe_push.DENIED}\n"
            answers["/usr/bin/touch"] = f"touch: {cache.parent}: Permission denied\n"
            self.assertEqual(safe_push.sandbox_problem("(a profile)", cache),
                             f"the trial's write to {cache.parent}, the directory above the "
                             "cache, failed otherwise than by the sandbox's refusal (touch: "
                             f"{cache.parent}: Permission denied)")
            answers["/usr/bin/touch"] = f"touch: {cache.parent}: {safe_push.DENIED}\n"
            self.assertIsNone(safe_push.sandbox_problem("(a profile)", cache))

    def test_the_flag_is_the_pre_flights_alone(self):
        r = subprocess.run([sys.executable, str(SAFE_PUSH), "--merge", "1", "--main-checks-cache"],
                           cwd=WORK, env=clean_env(), capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("--merge takes only --dry-run", r.stderr)
        r = subprocess.run([sys.executable, str(SAFE_PUSH), "--help"], cwd=WORK,
                           env=clean_env(), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        text = " ".join(r.stdout.split())
        self.assertIn("--main-checks-cache the pre-flight only", text)
        self.assertIn("Only the runs that land a train pass it (the coordinator ruled): the "
                      "coordinator's dry run of the train and its push", text)
        self.assertIn("The sandbox does not stop a run without the flag", text)

    def test_every_command_starts_in_run(self):
        # The sandbox wraps commands in run() alone, so every command must start there; the
        # hand-over's os.execve, in harness(), comes before open_cache, and so does
        # risk_class, which runs origin/main's risk.py with a time limit (#292).
        tree = ast.parse(SAFE_PUSH.read_text())
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        starters = {("subprocess", n) for n in ("run", "Popen", "call", "check_call",
                                                "check_output", "getoutput",
                                                "getstatusoutput")}
        starters |= {("os", n) for n in ("system", "popen", "fork", "forkpty", "posix_spawn",
                                         "posix_spawnp", "execv", "execve", "execvp",
                                         "execvpe", "execl", "execle", "execlp", "execlpe",
                                         "spawnv", "spawnve", "spawnvp", "spawnvpe")}
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn(node.module, ("subprocess", "os"), ast.unparse(node))
                for alias in node.names:
                    self.assertIsNone(alias.asname if alias.name in ("subprocess", "os")
                                      else None, ast.unparse(node))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and isinstance(node.func.value, ast.Name) \
                    and (node.func.value.id, node.func.attr) in starters:
                where = node
                while where in parents and not isinstance(where, ast.FunctionDef):
                    where = parents[where]
                found.add((getattr(where, "name", "<module>"), node.func.value.id,
                           node.func.attr))
        self.assertEqual(found, {("run", "subprocess", "run"), ("harness", "os", "execve"),
                                 ("risk_class", "subprocess", "run")})
        # In the pre-flight, the class is read before the cache is opened, and the
        # commit's checks (check_commit) run after it.
        preflight = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                         and node.name == "preflight_main")
        line: dict[str, int] = {}
        for node in ast.walk(preflight):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                line[node.func.id] = min(node.lineno, line.get(node.func.id, node.lineno))
        order = ["preconditions", "risk_class", "open_cache", "check_commit"]
        self.assertEqual(sorted(order, key=line.__getitem__), order)


    def test_every_import_is_at_the_top(self):
        # A module imported in a function could be imported once the sandbox is set, and
        # found first in the harness's own directory: so safe_push.py imports nothing
        # but at its top, nor through importlib or __import__, which the audit event of
        # an import does not always see.
        tree = ast.parse(SAFE_PUSH.read_text())
        late = [ast.unparse(node) for top in tree.body
                if not isinstance(top, (ast.Import, ast.ImportFrom))
                for node in ast.walk(top) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(late, [])
        # importlib only in train_check, which never runs with the sandbox set: open_cache
        # sets none for a train/* branch, and train_check refuses if one is set (#383).
        def names(nodes):
            return {node.id for node in nodes if isinstance(node, ast.Name)}
        trains = [node for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef) and node.name == "train_check"]
        self.assertEqual(len(trains), 1)
        inside = {id(node) for node in ast.walk(trains[0])}
        self.assertFalse({"importlib", "__import__"}
                         & names(n for n in ast.walk(tree) if id(n) not in inside))
        self.assertNotIn("__import__", names(ast.walk(trains[0])))
        for name in ("plistlib", "tomllib"):
            self.assertIn(f"\nimport {name}", SAFE_PUSH.read_text())


    def test_the_preflight_activates_the_sandbox_after_classification_and_before_checks(self):
        sha = self.check_change()
        ctx = safe_push.Context(WORK, sha, BASE, 1, str(ORIGIN), None, {})
        events = []

        def classify(*args, **kwargs):
            self.assertIsNone(safe_push.SANDBOX)
            events.append("classification")
            return self.R3

        def preload(*args, **kwargs):
            self.assertEqual(events, ["classification"])
            self.assertIsNone(safe_push.SANDBOX)
            events.append("count reader")

        def activate(rep, risk, train=False):
            self.assertFalse(train)     # the commit is not on a train/* branch
            self.assertEqual(events, ["classification", "count reader"])
            self.assertIsNone(safe_push.SANDBOX)
            events.append("sandbox")
            safe_push.CACHE, safe_push.SANDBOX = self.dir, "(version 1) (allow default)"

        def check(*args, **kwargs):
            self.assertEqual(events, ["classification", "count reader", "sandbox"])
            self.assertIsNotNone(safe_push.SANDBOX)
            events.append("commit checks")
            r = safe_push.run(["/usr/bin/true"], WORK)
            self.assertEqual(r.returncode, 0, r.stderr)
            return safe_push.Preflight([], [])

        args = mock.Mock(dry_run=True, commit=sha, branch=None, test_mode=True, title=None,
                         main_checks_cache=True, body_file=None)
        with mock.patch.object(safe_push, "CACHE", None), \
                mock.patch.object(safe_push, "SANDBOX", None), \
                mock.patch.object(safe_push, "SANDBOX_EXEC", str(self.fake)), \
                mock.patch.object(safe_push, "preconditions", return_value=ctx), \
                mock.patch.object(safe_push, "risk_class", side_effect=classify), \
                mock.patch.object(safe_push, "count_markers", side_effect=preload), \
                mock.patch.object(safe_push, "open_cache", side_effect=activate), \
                mock.patch.object(safe_push, "logs_dir", return_value=self.root / "logs"), \
                mock.patch.object(safe_push, "check_commit", side_effect=check), \
                mock.patch.object(safe_push, "make_record", return_value={}), \
                mock.patch.object(safe_push, "save_record"), \
                mock.patch.object(safe_push, "summary"), \
                contextlib.redirect_stdout(io.StringIO()), \
                watch_processes(str(self.fake)) as refused:
            code = safe_push.preflight_main(WORK, args)
        self.assertEqual(code, 0)
        self.assertEqual(events,
                         ["classification", "count reader", "sandbox", "commit checks"])
        self.assertEqual(refused, [])
        self.assertIn("/usr/bin/true", self.wrapped.read_text())

    def test_no_process_starts_outside_the_sandbox_while_the_cache_is_in_use(self):
        # platform.platform() once ran `uname -p` and `file -b` from the PATH, outside
        # run() and so outside the sandbox (S1 of the review of #224). Here every process
        # started is watched, by Python's own audit events, while the key is computed,
        # the toolchain read (stand-ins for lean, lake and elan, through the real
        # toolchain()), and origin/main's pass missed, kept and hit: only the stand-in
        # for sandbox-exec may start. platform's caches are emptied first, so that it
        # reads afresh what it would read in a run of its own.
        sha = self.check_change()
        tools, said = self.stand_in_tools()
        env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ.get("PATH", ""))
        ctx = safe_push.Context(WORK, sha, BASE, 1, str(ORIGIN), None, {})
        toolchain = safe_push.toolchain
        with self.active(), \
                mock.patch.object(safe_push, "toolchain", toolchain), \
                mock.patch.object(safe_push, "tool_env", lambda: dict(env)), \
                mock.patch.object(platform, "_uname_cache", None), \
                mock.patch.dict(platform._platform_cache, clear=True):
            inputs = self.inputs(sha)
            with watch_processes(str(self.fake)) as refused:
                fields, why = safe_push.main_checks_fields(ctx, WORK, inputs, self.CHECKS)
                miss = self.checks(sha, stub=self.stub)
                hit = self.checks(sha, stub=self.stub)
        self.assertEqual(refused, [], "a process started outside run(), and so outside "
                         "the sandbox, or a module was imported once it was set")
        self.assertIsNotNone(fields, why)
        self.assertEqual(fields["toolchain"]["lean --version"], said["lean"])
        self.assertEqual(fields["toolchain"]["elan which lean"],
                         os.path.realpath(tools / "lean"))
        self.assertEqual(fields["environment"]["platform"][0], platform.system())
        for r in (miss, hit):
            self.assertIsNone(r.refusal, r.out)
        self.assertTrue(self.cache_lines(miss.rep)[0].startswith("miss (no entry"),
                        miss.out)
        self.assertTrue(self.cache_lines(hit.rep)[0].startswith("hit: "), hit.out)
        self.assertEqual(len(self.entries()), 1)
        # And every command those runs started went through the stand-in for sandbox-exec,
        # the toolchain's among them, git with replacement objects off (#256).
        wrapped = self.wrapped.read_text()
        for line in ("lean --version", "lake --version", f"{tools / 'elan'} which lean",
                     f"git {' '.join(safe_push.NO_REPLACE_REFS)} --version"):
            self.assertIn(line, wrapped)

    def stand_in_tools(self) -> tuple[Path, dict]:
        """A directory of stand-ins for lean, lake and elan, and what lean and lake say."""
        tools = self.root / "tools"
        tools.mkdir()
        said = {"lean": "Lean (version 4.35.0, a stand-in)",
                "lake": "Lake version 5.0.0 (a stand-in)"}
        for name, line in said.items():
            (tools / name).write_text(f"#!/bin/sh\necho {shlex.quote(line)}\n")
        (tools / "elan").write_text(f"#!/bin/sh\necho {shlex.quote(str(tools / 'lean'))}\n")
        for name in ("lean", "lake", "elan"):
            (tools / name).chmod(0o755)
        return tools, said

    def step4_watched(self, sha: str, tools: Path, forget=(), late=(), apart=False) -> dict:
        """STEP4_WATCH on `sha`, in a fresh interpreter, the modules `forget` names
        forgotten before the sandbox is set, and those `late` names imported once it is:
        what its watch saw, its runs' steps and any error, and what it printed."""
        name = "-".join((*forget, *late)) or "plain"
        if apart:
            name += "-apart"
        script = self.root / f"step4-watch-{name}.py"
        out = self.root / f"step4-{name}.json"
        harness = self.root / f"harness-{name}"
        harness.mkdir()
        shutil.copy(SAFE_PUSH, harness / "safe_push.py")
        shutil.copy(HERE / "heath.py", harness / "heath.py")
        sentinel = self.root / f"executed-{name}"
        cache_plant = self.dir / f"written-{name}"
        script.write_text(STEP4_WATCH)
        given = {"events": sorted(PROCESS_EVENTS), "here": str(harness), "work": str(WORK),
                 "sha": sha, "base": BASE, "origin": str(ORIGIN), "inputs": self.inputs(sha),
                 "checks": self.CHECKS, "negative": self.NEGATIVE,
                 "sandbox_exec": str(self.fake), "cache": str(self.dir),
                 "path": str(tools) + os.pathsep + os.environ.get("PATH", ""),
                 "logs": tempfile.mkdtemp(prefix="logs-", dir=self.root),
                 "tmp": str(TMP), "forget": list(forget), "late": list(late),
                 "apart": apart, "sentinel": str(sentinel),
                 "cache_plant": str(cache_plant), "out": str(out)}
        r = subprocess.run([sys.executable, "-I", str(script), json.dumps(given)], cwd=WORK,
                           env=clean_env(), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return dict(json.loads(out.read_text()), printed=r.stdout + r.stderr)

    def test_no_process_nor_import_but_the_sandbox_in_a_fresh_interpreter(self):
        # The watch above runs in the test process, whose own imports could hide a module
        # imported late: platform.mac_ver() imported plistlib when the key was first
        # computed, after step 3 had run the commit's code, and Python looks for it first
        # in the harness's own directory, which that code may write (N1 of the re-review
        # of #224). Here the allow-list and step 4 run in a fresh interpreter, the latter
        # missed and then hit: once the sandbox is set, no process starts but through it,
        # and no module is imported but a builtin.
        sha = self.check_change()
        tools, said = self.stand_in_tools()
        seen = self.step4_watched(sha, tools, forget=("tomllib",))
        self.assertEqual((seen["seen"], seen["error"]), ([], None), seen["printed"])
        self.assertEqual(seen["allow_count"], len(safe_push.load_allowlist(WORK, BASE)))
        # origin/main's registry was read there by its own reader, through the sandbox, as
        # step 4's check list reads it, and gave what it gives unsandboxed.
        self.assertEqual(seen["listed"], [[n, c] for n, c in
                                          safe_push.check_sequence(WORK, BASE).steps])
        self.assertTrue(seen["listed"], seen["printed"])
        self.assertIn(f" --rev {BASE} --json {WORK}", self.wrapped.read_text(),
                      "the registry's reader did not run through the sandbox's stand-in")
        cache = {run: [d for name, _, d in steps if name == "main-checks cache"]
                 for run, steps in seen["runs"].items()}
        self.assertTrue(cache["miss"][0].startswith("miss (no entry"), seen["printed"])
        self.assertTrue(cache["hit"][0].startswith("hit: "), seen["printed"])
        self.assertEqual(len(self.entries()), 1)
        self.assertIn(said["lean"], self.entries()[0].read_text())
        self.assertIn("lean --version", self.wrapped.read_text())
        # The watch bites: a module imported once the sandbox is set is refused, and the
        # run stops there; and on macOS, where platform.mac_ver() reads the version file
        # with plistlib, so is plistlib, forgotten before the sandbox is set, as when
        # environment() imported it late. (Elsewhere mac_ver imports nothing.)
        cases = [((), ("colorsys",), "colorsys")]
        if os.path.exists("/System/Library/CoreServices/SystemVersion.plist"):
            cases.append((("plistlib",), (), "plistlib"))
        for forget, late, name in cases:
            with self.subTest(name):
                seen = self.step4_watched(sha, tools, forget=forget, late=late)
                self.assertEqual(seen["seen"], [f"imported: {name}"], seen["printed"])
                self.assertEqual(seen["error"], "PermissionError: a module imported once "
                                 f"the sandbox was set: {name}")

    def test_the_count_reader_is_retained_before_sandboxed_code_can_plant_a_module(self):
        sha = self.counted_judged_change()
        tools, _ = self.stand_in_tools()
        seen = self.step4_watched(sha, tools, forget=("dataclasses",), apart=True)
        self.assertEqual((seen["seen"], seen["error"]), ([], None), seen["printed"])
        self.assertTrue(seen["reader"], seen["printed"])
        self.assertEqual(seen["apart"], {
            "refused": True,
            "steps": [["check one (origin/main's checks)", "note"],
                      ["check change kept apart", "FAIL"]]})
        self.assertTrue(seen["planted"])
        self.assertFalse(seen["executed"])
        self.assertFalse(seen["cache_written"])


class RiskPreflight(Edge):
    """Checks scaled to risk (#292, #301): the pre-flight takes the change's class from
    origin/main's scripts/risk.py, judging the commit's paths against origin/main, never
    from the commit's own copy of the classifier, nor from a label but `release`, which
    only raises it to R5. R0 to R2 keep steps 1 to 3 and leave step 4 to CI, one "skip"
    line saying so; R3 to R5 take the full path, here the internal test flag's skip, since
    step 4 run in full needs Lean (FullChecks). The class is a step line, which reaches
    the pull request's record, and the pre-flight record's "class". Any failure to compute
    it is R5. --merge takes a record that left step 4 to CI only while the class,
    recomputed then, is still R0 to R2; a release merges only on the full pre-flight of its
    head, and with a green run of safe-push-tests there, the head's copy of that workflow
    being origin/main's, each of its three jobs there and passed."""

    SHORT = "left to CI"
    FULL = "internal test flag, local origin"
    GUARDS = ("secrets", "statements", "axiom lock", "protected paths", "heath/",
              "directories", "decision entries", "registry of checks")

    def record(self, sha: str, base: str | None = None) -> dict:
        """The pre-flight's record of `sha` against `base`, BASE unless named."""
        return json.loads((LOG.parent / "preflight" / f"{sha}-{base or BASE}.json").read_text())

    def detail(self, out: str, name: str) -> str:
        """The first line of a step's report after its name: its detail, without its time."""
        m = re.search(r"^\s+(?:ok|FAIL|skip|note)\s+%s: (.*?)(?:  \(\d+\.\d s\))?$"
                      % re.escape(name), out, re.M)
        return m.group(1) if m else ""

    def assertPath(self, r, sha: str, cls: str, path: str, *named: str,
                   base: str | None = None) -> str:
        """The pre-flight of `sha` passed with every guard of steps 1 to 3, classed `cls`
        for the files `named`, and took the `short` path, step 4 left to CI, or the `full`
        one; and its record says so."""
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        for name in self.GUARDS:
            self.assertEqual(self.guard(out, name), "ok", f"{name}:\n{out}")
        for name in ("review records", "generated pages"):
            self.assertRegex(out, r"(?m)^\s+ok\s+%s\b" % re.escape(name))
        self.assertEqual(self.guard(out, "class"), "ok", out)
        line = self.detail(out, "class")
        self.assertTrue(line.startswith(f"{cls}, "), out)
        for name in named:
            self.assertIn(name, line)
        self.assertEqual(self.step(out, "full local checks"), "skip", out)
        skip = self.detail(out, "full local checks")
        record = self.record(sha, base)
        self.assertEqual(record["class"], cls)
        self.assertEqual(record["class_why"], line.removeprefix(f"{cls}, "))
        if path == "short":
            self.assertTrue(skip.startswith(f"class {cls}: {self.SHORT}"), out)
            self.assertNotIn(self.FULL, out)
            self.assertEqual((record["short"], record["full"]), (True, False))
            self.assertEqual([s[:3] for s in record["steps"] if s[0] == "4"],
                             [["4", "class", "ok"], ["4", "full local checks", "skip"]])
        else:
            self.assertEqual(skip, self.FULL, out)
            self.assertFalse(record["short"])
        return out

    def r1_commit(self) -> str:
        """A line in a review record: R1, text and records."""
        return self.commit("A line in a review record", {
            "review/I/01.toml": self.text("review/I/01.toml") + "\n# A line for the test.\n"})

    def lowered(self) -> str:
        """scripts/risk.py made to class every file R0, by a first rule that matches all."""
        return self.replaced(safe_push.RISK, "RULES = [\n", 'RULES = [\n    ("R0", ["*"]),\n')

    def pushed(self, sha: str, *args) -> str:
        """The pre-flight of `sha`, its pull request opened ready, and the body completed
        as the coordinator completes it."""
        r = self.safe_push("--ready", *args)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.set_gh(lambda s: s["prs"][0].update(body=ticked(s["prs"][0]["body"])))
        return sha

    def merge(self) -> subprocess.CompletedProcess:
        return self.safe_push("--merge", "1")

    def test_r1_commit_takes_the_short_path(self):
        sha = self.r1_commit()
        self.assertPath(self.safe_push(), sha, "R1", "short", "review/I/01.toml",
                        "by origin/main's scripts/risk.py")
        # The class reaches the pull request's record: its line, and the steps' table.
        body = self.gh_state()["prs"][0]["body"]
        self.assertIn("Risk class R1: Text and records, by origin/main's scripts/risk.py", body)
        self.assertIn("the full local checks left to CI, for the class R1", body)
        self.assertIn("| 4. class | ok |", body)
        self.assertIn("| 4. full local checks | skip |", body)

    def test_r2_commit_takes_the_short_path(self):
        # A proof file changed, its review record stamped for it, and the pages rendered.
        lean, record = "Elements/BookI/Prop01.lean", "review/I/01.toml"
        new_lean = self.text(lean) + "\n"
        stamped = re.sub(r'(?m)^lean = "[^"]*"',
                         f'lean = "{safe_push.heath._sha(new_lean.encode())}"', self.text(record))
        sha = self.regenerated_commit("A proof file, its record stamped",
                                      {lean: new_lean, record: stamped})
        self.assertPath(self.safe_push("--dry-run"), sha, "R2", "short", lean)

    def test_r3_commit_touching_a_check_takes_the_full_path(self):
        path = "scripts/check_links.py"
        change = {path: self.text(path) + "\n# A comment for the test.\n"}
        change.update(self.decision(f"A comment in `{path}`, for the test."))
        sha = self.commit("A comment in a check", change)
        self.assertPath(self.safe_push("--dry-run"), sha, "R3", "full", path)

    def test_prose_paths_with_a_script_or_a_workflow_are_classed_high(self):
        for path, cls in ((".github/workflows/ci.yml", "R5"), ("scripts/x.py", "R3")):
            with self.subTest(path=path):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                text = (self.text(path) if (WORK / path).exists() else "") + "# For the test.\n"
                change = {"docs/x.md": "A page of prose, for the test.\n", path: text}
                change.update(self.decision(f"`{path}` changes, for the test."))
                sha = self.commit("A page of prose, and a script or a workflow", change)
                self.assertPath(self.safe_push("--dry-run"), sha, cls, "full", path)

    def test_the_commits_own_classifier_does_not_lower_its_class(self):
        change = {safe_push.RISK: self.lowered(),
                  "docs/reading.md": self.text("docs/reading.md") + "\nA line for the test.\n"}
        change.update(self.decision(f"`{safe_push.RISK}` classes every file R0, for the test."))
        sha = self.commit("Every file R0, by the commit's own classifier", change)
        # The commit's own copy would class it R0; origin/main's judges it, R5, for it
        # changes the classifier.
        own = subprocess.run([sys.executable, "-I", str(WORK / safe_push.RISK), "--diff", BASE,
                              sha], cwd=WORK, capture_output=True, text=True)
        self.assertEqual(own.stdout.splitlines()[:1], ["R0 Docs"], own.stdout + own.stderr)
        self.assertPath(self.safe_push("--dry-run"), sha, "R5", "full", safe_push.RISK)

    def test_origin_main_without_the_classifier_is_r5(self):
        main = self.commit("A main without the classifier", remove=(safe_push.RISK,))
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{main}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        sha = self.good_commit()
        out = self.assertPath(self.safe_push("--dry-run"), sha, "R5", "full", base=main)
        self.assertIn(f"has no {safe_push.RISK} to class it", self.detail(out, "class"))

    def main_without(self, message: str, *paths: str, write: dict | None = None) -> str:
        """origin/main moved to a commit of BASE with `paths` removed and `write` written."""
        main = self.commit(message, write, remove=paths)
        git(WORK, "push", "--quiet", "--no-verify", "origin", f"{main}:refs/heads/main")
        git(WORK, "fetch", "--quiet", "origin")
        return main

    def restoring(self, main: str, message: str, *paths: str) -> str:
        """A commit on `main` that brings `paths` back as BASE holds them, each named in a
        decision, with section 8's block rendered from what it brings back."""
        git(WORK, "checkout", "--quiet", "--force", "--detach", main)
        git(WORK, "checkout", BASE, "--", *paths)
        named = " ".join(f"`{p}`" for p in sorted(
            git(WORK, "diff", "--cached", "--name-only", main).split()))
        return self.regenerated_commit(message, self.decision(
            f"These come back, for the test: {named}."))

    def assertRegistryRefused(self, r, main: str, why: str) -> str:
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("REFUSED: origin/main's registry of checks could not be read", out)
        self.assertEqual(self.guard(out, "check list"), "FAIL", out)
        self.assertIn(why, self.detail(out, "check list"))
        self.assertIsNone(self.step(out, "full local checks"), out)
        self.assertEqual(self.origin_main(), main)
        self.assertIsNone(self.origin_branch())
        return out

    def test_the_preflight_runs_origin_mains_registry_never_the_commits(self):
        # #229: a train that removes one check and makes another run nothing changes what
        # its CI runs, never what its pre-flight runs: step 4's sequence is origin/main's
        # registry, read by origin/main's reader. The class is R3, and the train needs the
        # full path.
        removed, emptied = "checks/18-check-links.toml", "checks/07-heath.toml"
        loose = self.replaced(emptied, '["python3", "scripts/heath.py"]',
                              '["python3", "-c", "pass"]').replace(
            'name = "python3 scripts/heath.py"', 'name = "python3 -c pass"')
        git(WORK, "rm", "-q", "--", removed)
        sha = self.regenerated_commit("A check removed, and another that runs nothing", dict(
            {emptied: loose}, **self.decision(f"The check `{removed}` is removed, for the test.\n"
                                              f"The check `{emptied}` runs nothing, for the "
                                              "test.")))
        out = self.assertPath(self.safe_push("--dry-run"), sha, "R3", "full")
        line = self.detail(out, "check list")
        names = [e.name for e in registry.load(WORK, BASE)]
        tree = git(WORK, "rev-parse", f"{BASE}:checks").strip()
        self.assertTrue(line.startswith(f"{len(names) + 1} checks: the {len(names)} of "
                                        f"origin/main's registry, checks/ (tree {tree[:12]})"),
                        line)
        reader = git(WORK, "rev-parse", f"{BASE}:scripts/registry.py").strip()
        self.assertIn(f"scripts/registry.py (blob {reader[:12]})", line)
        self.assertNotIn(git(WORK, "rev-parse", f"{sha}:checks").strip()[:12], line)
        # That sequence is BASE's, the removed check and the other's command with it; the
        # commit's own, were it main, would differ.
        steps = dict(safe_push.check_sequence(WORK, BASE).steps)
        self.assertEqual(list(steps), names + [n for n, _ in safe_push.MODEL_JOB])
        self.assertIn("python3 scripts/check_links.py", steps)
        self.assertEqual(steps["python3 scripts/heath.py"], [safe_push.PY, "scripts/heath.py"])
        own = dict(safe_push.check_sequence(WORK, sha).steps)
        self.assertNotIn("python3 scripts/check_links.py", own)
        self.assertEqual(own["python3 -c pass"], [safe_push.PY, "-c", "pass"])
        # The line is in the record.
        self.assertIn(["4", "check list", "ok"], [s[:3] for s in self.record(sha)["steps"]])

    def test_origin_main_whose_registry_cannot_be_read_refuses(self):
        # An entry origin/main's reader refuses, and a reader that fails: the pre-flight
        # refuses, never runs an empty or partial list, though the commit repairs it (the
        # registry that judges is origin/main's), and its own registry, which step 3 reads,
        # is sound. Its other failures are in Registry. A repair to an entry is R3, to the
        # reader R5.
        entry = "checks/07-heath.toml"
        for label, write, why, cls in (
                ("an unknown field", {entry: lambda: self.text(entry) + 'colour = "red"\n'},
                 f"exited 1: registry.py: {entry}: unknown field 'colour'", "R3"),
                ("a reader that fails",
                 {safe_push.REGISTRY_READER: lambda: "import sys\nsys.exit(4)\n"}, "exited 4",
                 "R5")):
            with self.subTest(label):
                git(ORIGIN, "update-ref", "refs/heads/main", BASE)
                git(WORK, "fetch", "--quiet", "origin")
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                main = self.main_without(f"A main with {label}",
                                         write={p: text() for p, text in write.items()})
                sha = self.restoring(main, f"Repair {label}", *write)
                r = self.safe_push("--dry-run")
                out = self.assertRegistryRefused(r, main, why)
                self.assertEqual(self.guard(out, "registry of checks"), "ok", out)
                self.assertEqual(self.guard(out, "class"), "ok", out)
                self.assertTrue(self.detail(out, "class").startswith(f"{cls}, "), out)
                self.assertNotIn(sha[:12], self.detail(out, "check list"))

    def test_a_reader_that_works_only_beside_its_modules_is_refused_at_step_3(self):
        # A reader that imports a module beside it loads as render.py and CI's
        # run_checks.py load it, from scripts/, and reads the worktree's registry; alone,
        # as a later pre-flight would run it once it is origin/main's, it cannot, and
        # would refuse every train of R3 and above, its own repair among them. Step 3
        # reads the commit's registry with the commit's own reader alone, and refuses it.
        reader, sibling = safe_push.REGISTRY_READER, "scripts/registry_names.py"
        leaning = self.replaced(reader, 'FOLDER = "checks"\n',
                                "from registry_names import FOLDER\n")
        self.commit("A reader that leans on a module beside it", dict(
            {reader: leaning, sibling: 'FOLDER = "checks"\n'}, **self.decision(
                f"`{reader}` takes its folder's name from `{sibling}`, for the test.")))
        loaded = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, 'scripts'); "
             "import registry; print(len(registry.load('.')))"],
            cwd=WORK, capture_output=True, text=True)
        self.assertEqual(loaded.returncode, 0, loaded.stderr)
        self.assertEqual(int(loaded.stdout), len(registry.load(WORK, BASE)))
        out = self.assertRefused(self.safe_push("--dry-run"),
                                 "the invariant guards refused: registry of checks")
        self.assertEqual(self.guard(out, "registry of checks"), "FAIL", out)
        self.assertTrue(self.detail(out, "registry of checks").startswith(
            "the commit's registry of checks could not be read: its scripts/registry.py "
            "exited 1: ModuleNotFoundError: No module named 'registry_names'"), out)
        for name in ("protected paths", "decision entries", "generated pages"):
            self.assertEqual(self.step(out, name), "ok", f"{name}:\n{out}")
        self.assertIsNone(self.step(out, "check list"), out)

    def test_origin_main_without_a_registry_takes_the_built_in_lists(self):
        # The train that brings the registry is judged by the sequence built into the
        # harness, which Units pins, as it was before the registry came. The train brings
        # the reader, so it is R5; its step 3 reads the registry it brings.
        paths = [p for p in HARNESS_FILES if p.startswith("checks/")] + [
            safe_push.REGISTRY_READER]
        main = self.main_without("A main without the registry", *paths)
        self.assertEqual(safe_push.check_sequence(WORK, main).steps,
                         safe_push.CHECKS + safe_push.MODEL_JOB)
        sha = self.restoring(main, "The registry brought", *paths)
        out = self.assertPath(self.safe_push("--dry-run"), sha, "R5", "full", base=main)
        line = self.detail(out, "check list")
        self.assertTrue(line.startswith(
            f"{len(safe_push.CHECKS) + 1} checks: the {len(safe_push.CHECKS)} built into this "
            f"harness, since origin/main {main[:12]} holds no registry yet"), line)

    def test_release_label_is_r5(self):
        sha = self.good_commit()
        out = self.assertPath(self.safe_push("--dry-run", "--label", "release", "--label", "docs"),
                              sha, "R5", "full")
        self.assertIn("the pull request is labelled release", self.detail(out, "class"))
        # The open pull request's label counts as much, read before the checks.
        self.assertPath(self.safe_push(), sha, "R0", "short")
        self.set_gh(lambda s: s["prs"][0]["labels"].append("Release"))
        sha = self.good_commit("A second line, the fix.")
        out = self.assertPath(self.safe_push(), sha, "R5", "full")
        self.assertIn("the pull request is labelled release", self.detail(out, "class"))

    def test_class_fails_closed(self):
        sha = self.good_commit()
        self.assertEqual(safe_push.risk_class(WORK, BASE, sha, set()).cls, "R0")
        for base, head, labels, why in ((BASE, "0" * 40, set(), "could not class it (exit 2"),
                                        ("f" * 40, sha, set(), "git could not read"),
                                        (BASE, sha, None, "labels could not be read")):
            with self.subTest(why=why):
                risk = safe_push.risk_class(WORK, base, head, labels)
                self.assertEqual(risk.cls, "R5", risk)
                self.assertIn(why, risk.why)
        # And a classifier at origin/main that fails, or gives a class below one it gives a
        # file, or outlasts its time, or prints no class, or none of R0 to R5 (the last case
        # is the one the pre-flight below runs).
        for text, why, timeout in (
                ("import sys\nsys.exit(3)\n", "could not class it (exit 3)", 300),
                ("print('R0 Docs')\nprint('  R0 docs/reading.md')\nprint('  R3 scripts/x.py')\n",
                 "gave R0, below the R3 it gave scripts/x.py", 300),
                ("import time\ntime.sleep(60)\nprint('R0 Docs')\n",
                 "could not be run: TimeoutExpired", 1),
                ("print('A class, perhaps.')\n", "printed no class", 300),
                ("print('R6 Beyond')\n", "printed no class", 300)):
            with self.subTest(text=text):
                git(WORK, "checkout", "--quiet", "--force", "--detach", BASE)
                git(ORIGIN, "update-ref", "refs/heads/main", BASE)
                main = self.new_base("A classifier that fails", {safe_push.RISK: text})
                sha = self.good_commit()
                with mock.patch.object(safe_push, "RISK_TIMEOUT", timeout):
                    risk = safe_push.risk_class(WORK, main, sha, set())
                self.assertEqual(risk.cls, "R5", risk)
                self.assertIn(why, risk.why)
        out = self.assertPath(self.safe_push("--dry-run"), sha, "R5", "full", base=main)
        self.assertIn("printed no class", self.detail(out, "class"))

    def test_classifier_and_check_inputs_disagreeing_take_the_full_path(self):
        # origin/main's classifier made to class every file R0: a commit that changes a
        # check is still no change of R0 to R2 by safe_push's own lists, so the full path.
        main = self.new_base("A classifier that classes every file R0",
                             {safe_push.RISK: self.lowered()})
        path = "scripts/check_links.py"
        change = {path: self.text(path) + "\n# A comment for the test.\n"}
        change.update(self.decision(f"A comment in `{path}`, for the test."))
        sha = self.commit("A comment in a check", change)
        out = self.assertPath(self.safe_push("--dry-run"), sha, "R0", "full", base=main)
        self.assertEqual(self.guard(out, "class and check inputs"), "note", out)
        self.assertIn(path, self.detail(out, "class and check inputs"))

    def test_merge_takes_a_short_record_while_the_class_is_low(self):
        sha = self.pushed(self.r1_commit())
        self.assertTrue(self.record(sha)["short"])
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("its class R1 then and R1 now", self.detail(out, "pre-flight"))
        self.assertTrue(self.detail(out, "full local checks").startswith(
            f"class R1: {self.SHORT}"), out)
        self.assertEqual(self.step(out, "safe-push tests"), "skip", out)
        # The only API reads are --merge's preconditions, main's rules and its health: the
        # release gate reads nothing for a pull request not labelled release.
        reads = [c[1] for c in self.gh_state()["calls"] if c[0] == "api"]
        preconditions = ("/rules/branches/main", "labels=main-red",
                         "/actions/workflows/post-merge.yml/runs?")
        self.assertFalse([p for p in reads if not any(k in p for k in preconditions)], reads)
        self.assertEqual(len(self.merges()), 1)

    def test_release_merges_only_on_the_full_preflight_of_its_head(self):
        sha = self.pushed(self.r1_commit())
        self.set_gh(lambda s: s["prs"][0]["labels"].append("release"))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "release record"), "FAIL", out)
        self.assertIn("left the full checks to CI, for the class R1", out)
        self.assertIn("Run the pre-flight again", out)
        self.assertEqual(self.merges(), [])
        # The pre-flight again: the open pull request's label makes it R5, and it takes the
        # full path; then the release merges.
        r = self.safe_push()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.record(sha)["class"], self.record(sha)["short"]), ("R5", False))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertEqual(self.guard(out, "safe-push tests"), "ok", out)
        self.assertEqual(len(self.merges()), 1)

    def test_release_needs_a_green_safe_push_tests_run_at_its_head(self):
        # #301: a run at the head, completed and green, every job passed but `report`.
        sha = self.pushed(self.good_commit(), "--label", "release", "--label", "docs")
        other = dict(GREEN_SUITE, id=502, head_sha="f" * 40)

        def with_job(run_id, name, conclusion):
            return dict(GREEN_SUITE, id=run_id, jobs=[
                dict(j, conclusion=conclusion) if j["name"] == name else j for j in SUITE_JOBS])
        cases = (({"suite_runs": {"*": []}}, "no green run of safe-push-tests.yml at the head"),
                 ({"suite_runs": {"*": [other]}}, "no green run"),
                 ({"suite_runs": {"*": [dict(GREEN_SUITE, id=503, conclusion="failure"),
                                        dict(GREEN_SUITE, id=504, status="in_progress",
                                             conclusion=None)]}}, "no green run"),
                 ({"suite_runs": {"*": [with_job(505, "negative-tests", "failure")]}},
                  "negative-tests failure"),
                 ({"suite_runs": {"*": [with_job(506, "formal-model-kernel", "skipped")]}},
                  "formal-model-kernel skipped"),
                 # A shard that failed or was cancelled holds the release, as any job does.
                 ({"suite_runs": {"*": [with_job(509, "safe-push-shards (3)", "failure")]}},
                  "safe-push-shards (3) failure"),
                 ({"suite_runs": {"*": [with_job(510, "safe-push-shards (8)", "cancelled")]}},
                  "safe-push-shards (8) cancelled"),
                 # A run of a workflow that dropped a job, or that ran one trivial job alone:
                 # each of the workflow's three jobs must be there.
                 ({"suite_runs": {"*": [dict(GREEN_SUITE, id=507, jobs=[
                     j for j in SUITE_JOBS if j["name"] != "negative-tests"])]}},
                  "run 507: negative-tests missing"),
                 ({"suite_runs": {"*": [dict(GREEN_SUITE, id=508, jobs=[
                     {"name": "trivial", "status": "completed", "conclusion": "success"}])]}},
                  "run 508: safe-push-tests missing, negative-tests missing, "
                  "formal-model-kernel missing"),
                 ({"suite_read_fail": True}, "unreadable"))
        for state, why in cases:
            with self.subTest(why=why):
                self.set_gh(lambda s: (s.pop("suite_read_fail", None),
                                       s.update(suite_runs={"*": [GREEN_SUITE]}), s.update(state)))
                r = self.merge()
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertEqual(self.guard(out, "safe-push tests"), "FAIL", out)
                self.assertIn(why, out[out.index("safe-push tests:"):])
                self.assertIn(f"gh workflow run safe-push-tests.yml --ref {BRANCH}"
                              if why != "unreadable" else "unreadable", out)
                self.assertEqual(self.merges(), [])
        self.set_gh(lambda s: (s.pop("suite_read_fail", None),
                               s.update(suite_runs={sha: [other, GREEN_SUITE]})))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("run 501 of safe-push-tests.yml", self.detail(out, "safe-push tests"))
        self.assertEqual(len(self.merges()), 1)

    def test_release_refuses_a_head_that_changes_the_suite_workflow(self):
        # A run at the head runs the head's copy of the workflow, which could drop a job:
        # the head's copy must be origin/main's, whatever GitHub says of the runs.
        path = safe_push.SUITE_PATH
        change = {path: self.text(path) + "# A comment for the test.\n"}
        change.update(self.decision(f"A comment in `{path}`, for the test."))
        sha = self.pushed(self.commit("A comment in the suite's workflow", change),
                          "--label", "release", "--label", "tooling")
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertEqual(self.guard(out, "safe-push tests"), "FAIL", out)
        detail = out[out.index("safe-push tests:"):]
        self.assertIn(f"the head {sha[:12]} changes {path}", detail)
        self.assertIn("land that change first, in a pull request of its own", detail)
        for name in ("release", "label", "CI"):
            self.assertEqual(self.guard(out, name), "ok", f"{name}:\n{out}")
        self.assertFalse([c for c in self.gh_state()["calls"]
                          if c[0] == "api" and "/actions/" in c[-1]])
        self.assertEqual(self.merges(), [])

    def test_release_label_given_after_the_class_was_read_needs_the_full_preflight(self):
        # The label is not on the pull request when --merge first reads it, so the class is
        # R1 and the short record stands in for step 4; the gates' read finds it, and the
        # record made then is still short: refused, by the second look.
        sha = self.pushed(self.r1_commit())
        self.set_gh(lambda s: s.update(late_label={"views": 1, "label": "release"}))
        r = self.merge()
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        self.assertIn("its class R1 then and R1 now", self.detail(out, "pre-flight"))
        self.assertEqual(self.guard(out, "safe-push tests"), "ok", out)
        self.assertEqual(self.guard(out, "release record"), "FAIL", out)
        self.assertIn("left the full checks to CI, for the class R1", out)
        self.assertIn(f"#1 is labelled release, and a release merges only on the full "
                      f"pre-flight of its head, {sha[:12]}", out)
        self.assertIn("release", self.gh_state()["prs"][0]["labels"])
        self.assertEqual(self.merges(), [])


@unittest.skipUnless(os.environ.get("STOICHEIA_SLOW_TESTS") == "1",
                     "the full checks need Lean and take minutes: STOICHEIA_SLOW_TESTS=1")
class FullChecks(Edge):
    """Step 4 for real: the whole sequence once, on a good commit, without the internal
    flag, as a dry run of the pre-flight (the real gh is never called by the tests)."""

    def test_full_sequence_on_a_good_commit(self):
        # R3 by scripts/risk.py, a line in the guide to the checks: an R0 to R2 commit's
        # pre-flight leaves step 4 to CI (docs/decisions/2026-10-22-checks-by-risk.md).
        self.commit("A good commit", {
            "docs/WORKFLOW.md": self.text("docs/WORKFLOW.md") + "\nA line for the test.\n"})
        r = subprocess.run([sys.executable, str(SAFE_PUSH), "--branch", BRANCH, "--dry-run"],
                           cwd=WORK, env=clean_env(), capture_output=True, text=True)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        # origin/main's registry, then the model job's, then the negative tests.
        self.assertEqual(self.step(out, "check list"), "ok", out)
        for name, _ in safe_push.check_sequence(WORK, BASE).steps + safe_push.NEGATIVE:
            self.assertEqual(self.step(out, name), "ok", f"{name}:\n{out}")
        self.assertEqual(self.step(out, "git push"), "skip", out)
        self.assertEqual(self.origin_main(), BASE)
        self.assertEqual(len(git(WORK, "worktree", "list").splitlines()), 1,
                         "a temporary worktree was left behind")


def registry_entry(order, command: list[str], job: str = "check", more: str = "") -> str:
    """A file of the registry of checks, for `command`, named and shown as the command."""
    name = " ".join(command)
    return (f"order = {order}\nname = {json.dumps(name)}\njob = {json.dumps(job)}\n"
            f"command = {json.dumps(command)}\nsection8 = {json.dumps(name)}\n{more}")


def registry_empty(order) -> str:
    """The registry's entry for `git status --porcelain` printing nothing."""
    return (f'order = {order}\nname = "git status --porcelain is empty"\njob = "check"\n'
            'empty = true\nsection8 = "git status --porcelain"\n')


class Registry(unittest.TestCase):
    """The registry of checks (#229), on folders and repositories of the tests' own: each
    rule of its reader, broken, refuses the whole registry with the file named, read from
    the worktree and from Git alike; safe_push reads origin/main's registry with
    origin/main's reader, never the worktree's, refuses whenever it cannot, and holds the
    checks' names itself; step 3 reads the commit's own registry so, with the commit's own
    reader alone; run_checks.py stops at the first check that fails, and fails an `empty`
    check that prints anything; and one file more is one check more for safe_push, section
    8's block and run_checks.py, in the place its order gives it."""

    IDENTITY = ("-c", "user.name=Registry test", "-c",
                "user.email=registry-test@example.invalid", "-c", "commit.gpgsign=false")
    FIRST = registry_entry(10, ["python3", "-c", "print(1)"])
    GOOD = registry_entry(20, ["python3", "-c", "pass"])

    def folder(self, files: dict) -> Path:
        """A root of the test's own under TMP: scripts/registry.py and scripts/run_checks.py
        as this checkout holds them, and checks/ holding `files` (bytes or text; None, a
        folder with a file in it)."""
        root = Path(tempfile.mkdtemp(prefix="registry-", dir=TMP))
        (root / "scripts").mkdir()
        for name in ("registry.py", "run_checks.py"):
            shutil.copy2(HERE / name, root / "scripts" / name)
        (root / "checks").mkdir()
        for name, text in files.items():
            path = root / "checks" / name
            if text is None:
                path.mkdir()
                (path / "inside.toml").write_text(self.GOOD)
            elif isinstance(text, bytes):
                path.write_bytes(text)
            else:
                path.write_text(text)
        (root / ".gitignore").write_text("__pycache__/\n")
        return root

    def committed(self, root: Path, message: str = "A registry for the test") -> Path:
        if not (root / ".git").exists():
            git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, *self.IDENTITY, "commit", "-q", "--allow-empty", "-m", message)
        return root

    def run_checks(self, root: Path, *args: str, github: bool = False):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_ACTIONS"}
        if github:
            env["GITHUB_ACTIONS"] = "true"
        return subprocess.run([sys.executable, str(root / "scripts" / "run_checks.py"),
                               *(args or ("--job", "check"))], cwd=root, env=env,
                              capture_output=True, text=True)

    def test_the_reader_refuses_each_break_naming_the_file(self):
        good, at = self.GOOD, "checks/20-b.toml"
        cases = (
            ("an unknown field", {"20-b.toml": good + 'colour = "red"\n'},
             f"{at}: unknown field 'colour'"),
            ("no section8", {"20-b.toml": good.replace('section8 = "python3 -c pass"\n', "")},
             f"{at}: missing field 'section8'"),
            ("no order", {"20-b.toml": good.replace("order = 20\n", "")},
             f"{at}: missing field 'order'"),
            ("no job", {"20-b.toml": good.replace('job = "check"\n', "")},
             f"{at}: missing field 'job'"),
            ("a name twice", {"20-b.toml": registry_entry(20, ["python3", "-c", "print(1)"])},
             f"{at}: the name 'python3 -c print(1)' is checks/10-a.toml's too"),
            ("an order twice", {"20-b.toml": good.replace("order = 20", "order = 10")},
             f"{at}: the order '10' is checks/10-a.toml's too"),
            ("an order twice, written otherwise",
             {"20-b.toml": good.replace("order = 20", "order = 10.0")},
             f"{at}: the order '10.0' is checks/10-a.toml's too"),
            ("a command that is a string",
             {"20-b.toml": good.replace('["python3", "-c", "pass"]', '"python3 -c pass"')},
             f"{at}: command must be a list of strings"),
            ("a command of numbers", {"20-b.toml": good.replace('["python3", "-c", "pass"]',
                                                                "[1, 2]")},
             f"{at}: command must be a list of strings"),
            ("a command of no words", {"20-b.toml": good.replace('["python3", "-c", "pass"]',
                                                                 "[]")},
             f"{at}: command must be a list of strings"),
            ("a word that is empty", {"20-b.toml": good.replace('"-c", ', '"", ')},
             f"{at}: command must be a list of strings"),
            ("an unknown job", {"20-b.toml": registry_entry(20, ["python3", "-c", "pass"],
                                                            job="model")},
             f"{at}: unknown job 'model'"),
            ("a command and empty", {"20-b.toml": good + "empty = true\n"},
             f"{at}: an entry holds exactly one of command and empty"),
            ("neither", {"20-b.toml": good.replace('command = ["python3", "-c", "pass"]\n', "")},
             f"{at}: an entry holds exactly one of command and empty"),
            ("empty false", {"20-b.toml": registry_empty(20).replace("true", "false")},
             f"{at}: empty is true"),
            ("a name that is not the command",
             {"20-b.toml": good.replace('name = "python3 -c pass"', 'name = "python3 -c x"')},
             f"{at}: name must be 'python3 -c pass'"),
            ("an empty check named otherwise",
             {"20-b.toml": registry_empty(20).replace("git status --porcelain is empty",
                                                      "the worktree is clean")},
             f"{at}: name must be 'git status --porcelain is empty'"),
            ("an order that is text", {"20-b.toml": good.replace("order = 20", 'order = "20"')},
             f"{at}: order must be a number"),
            ("an order that is a truth value",
             {"20-b.toml": good.replace("order = 20", "order = true")},
             f"{at}: order must be a number"),
            ("section8 of two lines",
             {"20-b.toml": good.replace('section8 = "python3 -c pass"', 'section8 = "a\\nb"')},
             f"{at}: section8 must be one line"),
            ("not TOML", {"20-b.toml": "order = \n"}, f"{at}: not TOML"),
            ("not UTF-8", {"20-b.toml": b"order = 20\n\xff\n"}, f"{at}: not UTF-8"),
            ("a name with no number", {"b.toml": good}, "checks/b.toml: expected README.md"),
            ("a name in capitals", {"20-B.toml": good}, "checks/20-B.toml: expected README.md"),
            ("a page of notes", {"notes.md": "Notes.\n"}, "checks/notes.md: expected README.md"),
            ("another suffix", {"20-b.yaml": good}, "checks/20-b.yaml: expected README.md"),
            ("a folder", {"20-b.toml": None}, f"{at}: expected a regular file"),
        )
        for label, files, message in cases:
            with self.subTest(label):
                root = self.folder({"10-a.toml": self.FIRST, **files})
                with self.assertRaises(registry.RegistryError) as raised:
                    registry.load(root)
                self.assertIn(message, str(raised.exception))
                # And from Git, as safe_push reads origin/main's.
                self.committed(root)
                with self.assertRaises(registry.RegistryError) as raised:
                    registry.load(root, "HEAD")
                self.assertIn(message, str(raised.exception))
        # A link, which Git holds as one.
        root = self.folder({"10-a.toml": self.FIRST})
        (root / "checks" / "20-b.toml").symlink_to("10-a.toml")
        for rev in (None, "HEAD"):
            with self.subTest("a link", rev=rev), self.assertRaisesRegex(
                    registry.RegistryError, f"{at}: expected a regular file"):
                registry.load(self.committed(root) if rev else root, rev)
        # No entry, and no folder.
        root = self.folder({"README.md": "The checks.\n"})
        for rev in (None, "HEAD"):
            with self.subTest("no entry", rev=rev), self.assertRaisesRegex(
                    registry.RegistryError, "checks/: no entry"):
                registry.load(self.committed(root) if rev else root, rev)
        shutil.rmtree(root / "checks")
        for rev in (None, "HEAD"):
            with self.subTest("no folder", rev=rev), self.assertRaisesRegex(
                    registry.RegistryError, "checks/: no registry"):
                registry.load(self.committed(root, "No folder") if rev else root, rev)
        # The README and Finder's .DS_Store are passed over; the order decides, not the name.
        root = self.committed(self.folder({
            "README.md": "The checks.\n", ".DS_Store": b"\0junk", "10-a.toml": self.GOOD,
            "20-b.toml": self.FIRST.replace("order = 10", "order = 5")}))
        for rev in (None, "HEAD"):
            with self.subTest("passed over", rev=rev):
                self.assertEqual([(e.path, e.name) for e in registry.load(root, rev)],
                                 [("checks/20-b.toml", "python3 -c print(1)"),
                                  ("checks/10-a.toml", "python3 -c pass")])

    def test_safe_push_reads_origin_mains_registry_and_fails_closed(self):
        root = self.committed(self.folder({"10-a.toml": self.FIRST,
                                           "20-b.toml": registry_empty(20)}))
        checks = safe_push.check_sequence(root, "HEAD")
        self.assertEqual(checks.steps, [("python3 -c print(1)", [safe_push.PY, "-c", "print(1)"]),
                                        ("git status --porcelain is empty", None),
                                        *safe_push.MODEL_JOB])
        tree = git(root, "rev-parse", "HEAD:checks").strip()
        self.assertIn(f"the 2 of origin/main's registry, checks/ (tree {tree[:12]})", checks.why)
        # The reader and the registry are the revision's: the worktree's, broken, are not
        # read, and the revision's, broken, are, though the worktree's are sound.
        good_reader = (root / "scripts" / "registry.py").read_text()
        (root / "scripts" / "registry.py").write_text("import sys\nsys.exit(4)\n")
        (root / "checks" / "10-a.toml").write_text("order = \n")
        self.assertEqual(safe_push.check_sequence(root, "HEAD").steps, checks.steps)
        self.committed(root, "A reader that fails")
        (root / "scripts" / "registry.py").write_text(good_reader)
        (root / "checks" / "10-a.toml").write_text(self.FIRST)
        with self.assertRaisesRegex(safe_push.Refusal, "exited 4"):
            safe_push.check_sequence(root, "HEAD")
        self.committed(root, "A sound reader again")

        def reader(source: str) -> str:
            return f"import json, sys\n{source}\n"
        cases = (
            ("an entry the reader refuses", {"checks/10-a.toml": self.FIRST + "colour = 1\n"},
             (), "exited 1: registry.py: checks/10-a.toml: unknown field 'colour'"),
            ("a reader that prints no list",
             {"scripts/registry.py": reader("print('{}')")}, (), "printed no list of checks"),
            ("a reader that prints nothing", {"scripts/registry.py": reader("")}, (),
             "printed no list of checks"),
            ("a reader that gives no check", {"scripts/registry.py": reader("print('[]')")},
             (), "gives no check"),
            ("a check of another job", {"scripts/registry.py": reader(
                "print(json.dumps([{'name': 'x', 'job': 'model', 'command': ['x'], "
                "'empty': False}]))")}, (), "to the job model, which the pre-flight"),
            ("an entry that is no check", {"scripts/registry.py": reader(
                "print(json.dumps([{'name': 'x', 'job': 'check', 'command': None, "
                "'empty': False}]))")}, (), "printed an entry that is not a check"),
            ("a command of no words", {"scripts/registry.py": reader(
                "print(json.dumps([{'name': 'x', 'job': 'check', 'command': [], "
                "'empty': False}]))")}, (), "printed an entry that is not a check"),
            ("two checks of one name", {"scripts/registry.py": reader(
                "e = {'name': 'x', 'job': 'check', 'command': ['x'], 'empty': False}\n"
                "print(json.dumps([e, e]))")}, (), "two checks of one name"),
            ("no reader", {}, ("scripts/registry.py",),
             "holds checks/ but no regular file scripts/registry.py"),
            ("no folder", {}, ("checks",), "holds scripts/registry.py but no folder checks/"),
            ("a folder that is a file", {"checks": "A file.\n"}, ("checks",),
             "holds scripts/registry.py but no folder checks/"),
        )
        for label, write, remove, why in cases:
            with self.subTest(label):
                git(root, "checkout", "-q", "--force", "HEAD")
                git(root, "clean", "-fdq")
                for path in remove:
                    git(root, "rm", "-rq", "--", path)
                for path, text in write.items():
                    (root / path).write_text(text)
                self.committed(root, label)
                with self.assertRaises(safe_push.Refusal) as raised:
                    safe_push.check_sequence(root, "HEAD")
                self.assertIn("origin/main's registry of checks could not be read", str(raised.exception))
                self.assertIn(why, str(raised.exception))
                git(root, *self.IDENTITY, "revert", "--no-edit", "HEAD")
        # A reader that outlasts its time, and a revision Git does not know.
        (root / "scripts" / "registry.py").write_text("import time\ntime.sleep(30)\n")
        self.committed(root, "A slow reader")
        with mock.patch.object(safe_push, "REGISTRY_TIMEOUT", 1), \
                self.assertRaisesRegex(safe_push.Refusal, "could not be run: TimeoutExpired"):
            safe_push.check_sequence(root, "HEAD")
        with self.assertRaisesRegex(safe_push.Refusal, "git could not list"):
            safe_push.check_sequence(root, "f" * 40)
        # Neither the folder nor the reader: the lists built in, the train that brings them.
        git(root, "rm", "-rq", "--", "checks", "scripts/registry.py")
        self.committed(root, "No registry")
        checks = safe_push.check_sequence(root, "HEAD")
        self.assertEqual(checks.steps, safe_push.CHECKS + safe_push.MODEL_JOB)
        self.assertIn("holds no registry yet", checks.why)
        self.assertTrue(checks.built_in)

    def test_safe_push_holds_the_names_itself(self):
        # FRESHNESS passes over a failure of a step named "generated pages" or "git status
        # --porcelain is empty" when it keeps a check change apart. So check_sequence holds
        # the names itself, never trusting the reader at origin/main, which a train may
        # change: the `empty` entry, and only it, bears that name, and every command's name
        # is its words joined by spaces.
        root = self.committed(self.folder({"10-a.toml": self.FIRST}))
        empty = safe_push.EMPTY_CHECK

        def printing(*entries) -> str:
            listed = [dict(e, job="check") for e in entries]
            return f"import json\nprint(json.dumps({listed!r}))\n"
        cases = (
            ("the empty check named otherwise",
             [{"name": "the worktree is clean", "command": None, "empty": True}],
             f"gives the `empty` check the name 'the worktree is clean', not {empty!r}"),
            ("a command named as the empty check, its words so",
             [{"name": empty, "command": empty.split(), "empty": False}],
             f"gives a command the name {empty!r}, which only the `empty` check may bear"),
            ("a command named as the empty check",
             [{"name": empty, "command": ["true"], "empty": False}],
             f"names a check {empty!r}, not its command's words joined by spaces"),
            ("a command named as stale pages",
             [{"name": "generated pages", "command": ["generated", "pages"], "empty": False}],
             "gives a command the name 'generated pages', which only the `empty` check"),
            ("a command named otherwise than its words",
             [{"name": "lake build", "command": ["true"], "empty": False}],
             "names a check 'lake build', not its command's words joined by spaces"),
        )
        for label, entries, why in cases:
            with self.subTest(label):
                (root / "scripts" / "registry.py").write_text(printing(*entries))
                self.committed(root, label)
                with self.assertRaises(safe_push.Refusal) as raised:
                    safe_push.check_sequence(root, "HEAD")
                self.assertIn("origin/main's registry of checks could not be read",
                              str(raised.exception))
                self.assertIn(why, str(raised.exception))
        # Each named as it should be: a command by its words, the `empty` check by its name.
        (root / "scripts" / "registry.py").write_text(printing(
            {"name": "true --quiet", "command": ["true", "--quiet"], "empty": False},
            {"name": empty, "command": None, "empty": True}))
        self.committed(root, "Names as they should be")
        self.assertEqual(safe_push.check_sequence(root, "HEAD").steps,
                         [("true --quiet", ["true", "--quiet"]), (empty, None),
                          *safe_push.MODEL_JOB])

    def test_step_3_reads_the_commits_registry_as_a_later_preflight_will(self):
        # A reader that imports a module beside it loads as render.py and run_checks.py
        # load it, from scripts/, and reads the worktree. Alone, with -I, from a temporary
        # directory, as the pre-flight runs origin/main's, it cannot: so step 3 runs the
        # commit's own reader so (guard_registry), and refuses it before it can merge and
        # refuse every train after it. Sound, the guard is ok; with neither the folder nor
        # the reader, as before the registry came, it is skipped.
        def guarded(root: Path) -> list:
            rep = safe_push.Report()
            with contextlib.redirect_stdout(io.StringIO()):
                safe_push.guard_registry(root, "HEAD", rep)
            return [(s.stage, s.name, s.outcome, s.detail) for s in rep.steps]
        root = self.committed(self.folder({"10-a.toml": self.FIRST,
                                           "20-b.toml": registry_empty(20)}))
        [(stage, name, outcome, detail)] = guarded(root)
        self.assertEqual((stage, name, outcome), ("3", "registry of checks", "ok"))
        self.assertTrue(detail.startswith("2 checks, as the commit's own scripts/registry.py "
                                          "reads them"), detail)
        reader = root / "scripts" / "registry.py"
        reader.write_text(reader.read_text().replace(
            'FOLDER = "checks"\n', "from registry_names import FOLDER\n", 1))
        (root / "scripts" / "registry_names.py").write_text('FOLDER = "checks"\n')
        self.committed(root, "A reader that leans on a module beside it")
        r = self.run_checks(root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("all 2 checks of the job check passed", r.stdout)
        with self.assertRaises(safe_push.Refusal) as raised:
            safe_push.check_sequence(root, "HEAD", "the commit")
        said = ("the commit's registry of checks could not be read: its scripts/registry.py "
                "exited 1: ModuleNotFoundError: No module named 'registry_names'")
        self.assertEqual(str(raised.exception), said)
        [(stage, name, outcome, detail)] = guarded(root)
        self.assertEqual((stage, name, outcome), ("3", "registry of checks", "FAIL"))
        self.assertTrue(detail.startswith(said + "; so it would refuse the pre-flight of "
                                          "every train once it is origin/main's"), detail)
        # The same registry, which a commit that changes neither the folder nor the reader
        # holds as origin/main's: the fault is main's, and the step says so.
        rep = safe_push.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            safe_push.guard_registry(root, "HEAD", rep, base="HEAD")
        [step] = rep.steps
        self.assertEqual(step.outcome, "FAIL")
        self.assertIn("the commit changes neither checks/ nor scripts/registry.py, so the "
                      "registry it holds is origin/main's", step.detail)
        git(root, "rm", "-rq", "--", "checks", "scripts/registry.py",
            "scripts/registry_names.py")
        self.committed(root, "No registry")
        self.assertEqual(guarded(root), [("3", "registry of checks", "skip",
                                          "the commit holds neither checks/ nor "
                                          "scripts/registry.py")])

    def test_run_checks_stops_at_the_first_check_that_fails(self):
        marker = Path(tempfile.mkdtemp(dir=TMP)) / "the-third-ran"
        third = ["python3", "-c", f"open({str(marker)!r}, 'w')"]
        root = self.committed(self.folder({
            "10-a.toml": registry_entry(10, ["python3", "-c", "print('the first ran')"]),
            "20-b.toml": registry_entry(20, ["python3", "-c", "import sys; sys.exit(3)"]),
            "30-c.toml": registry_entry(30, third)}))
        for github in (False, True):
            with self.subTest(github=github):
                r = self.run_checks(root, github=github)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                first = ("::group::" if github else "==> ") + "1/3 python3 -c print('the first ran')"
                self.assertIn(first, r.stdout)
                self.assertLess(r.stdout.index(first), r.stdout.index("the first ran\n"))
                self.assertIn("2/3 python3 -c import sys; sys.exit(3)", r.stdout)
                self.assertIn("run_checks.py: FAILED: python3 -c import sys; sys.exit(3) "
                              "(checks/20-b.toml): exit 3", r.stderr)
                self.assertIn("the 1 checks after it did not run", r.stderr)
                self.assertNotIn("3/3", r.stdout)
                self.assertFalse(marker.exists(), "a check after the failure ran")
                self.assertEqual("::endgroup::" in r.stdout, github)
                self.assertEqual("::error title=A check failed::" in r.stdout, github)
        # An unknown job, and a registry its reader refuses, run nothing.
        r = self.run_checks(root, "--job", "model")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("no check of the job 'model'", r.stderr)
        (root / "checks" / "40-d.toml").write_text(self.GOOD + "colour = 1\n")
        r = self.run_checks(root)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("checks/40-d.toml: unknown field 'colour'", r.stderr)
        self.assertNotIn("the first ran", r.stdout)

    def test_run_checks_fails_an_empty_check_that_prints(self):
        marker = Path(tempfile.mkdtemp(dir=TMP)) / "the-third-ran"
        root = self.committed(self.folder({
            "10-a.toml": registry_entry(10, ["python3", "-c", "print('a check')"]),
            "20-clean.toml": registry_empty(20),
            "30-c.toml": registry_entry(30, ["python3", "-c", f"open({str(marker)!r}, 'w')"])}))
        r = self.run_checks(root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ok git status --porcelain is empty", r.stdout)
        self.assertIn("all 3 checks of the job check passed", r.stdout)
        self.assertTrue(marker.exists())
        # A new file anywhere in the worktree, or a change to a tracked one, fails it.
        (root / "deep" / "er").mkdir(parents=True)
        (root / "deep" / "er" / "new.txt").write_text("A new file.\n")
        with (root / ".gitignore").open("a") as f:
            f.write("*.bak\n")
        marker.unlink()
        r = self.run_checks(root)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("?? deep/", r.stdout)
        self.assertIn(" M .gitignore", r.stdout)
        self.assertIn("FAILED: git status --porcelain is empty (checks/20-clean.toml): it "
                      "printed what is listed above, and must print nothing", r.stderr)
        self.assertFalse(marker.exists(), "a check after the failure ran")

    def test_one_file_more_is_one_check_more_everywhere(self):
        # Adding a check is adding one file (#229): safe_push's sequence from that
        # revision, section 8's block as render.py writes it, and run_checks.py each gain
        # it, at the place its order gives it, though its name sorts last.
        import render
        files = {"10-a.toml": registry_entry(10, ["python3", "-c", "print('a')"]),
                 "20-b.toml": registry_entry(20, ["python3", "-c", "print('b')"])}
        root = self.committed(self.folder(files))
        before = safe_push.check_sequence(root, "HEAD").steps
        page = ("# A page\n\n<!-- checks -->\n```sh\nan old line\n```\n<!-- /checks -->\n\n"
                "The rest.\n")
        written_before = render.workflow_page(page, registry.load(root))
        (root / "checks" / "90-between.toml").write_text(
            registry_entry(15, ["python3", "-c", "print('between')"]))
        self.committed(root, "One check more")
        names = ["python3 -c print('a')", "python3 -c print('between')", "python3 -c print('b')"]
        after = safe_push.check_sequence(root, "HEAD").steps
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual([n for n, _ in after], names + [n for n, _ in safe_push.MODEL_JOB])
        written = render.workflow_page(page, registry.load(root))
        self.assertEqual(written, "# A page\n\n<!-- checks -->\n```sh\n"
                         "export PATH=$HOME/.elan/bin:$PATH\n" + "\n".join(names)
                         + "\n```\n<!-- /checks -->\n\nThe rest.\n")
        self.assertEqual(len(written.splitlines()), len(written_before.splitlines()) + 1)
        self.assertEqual(render.workflow_page(written, registry.load(root)), written)
        r = self.run_checks(root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        groups = [line for line in r.stdout.splitlines() if line.startswith("==> ")]
        self.assertEqual(groups, [f"==> {i}/3 {name}" for i, name in enumerate(names, 1)])
        self.assertEqual([line for line in r.stdout.splitlines() if line in ("a", "between", "b")],
                         ["a", "between", "b"])
        # A page with no markers, or two pairs, is refused, nothing written.
        for text in ("# A page\n", page + page):
            with self.subTest(text=text), self.assertRaises(SystemExit):
                render.workflow_page(text, registry.load(root))


class HermeticModule(unittest.TestCase):
    """#360: one test of this module, its setUpModule with it, run from a linked worktree
    under a hook's GIT_DIR and GIT_INDEX_FILE naming that worktree's git directory, leaves
    the repository as it was: its HEAD, index and files, and the shared configuration."""

    CHILD = "STOICHEIA_TEST_HERMETIC_CHILD"

    def test_the_module_under_a_hooks_git_dir(self):
        if os.environ.get(self.CHILD):
            self.skipTest("the planted run itself")
        plain = dict(os.environ)  # hermetic already: setUpModule has run
        def g(*args) -> str:
            return subprocess.run(["git", *map(str, args)], env=plain, check=True,
                                  capture_output=True, text=True).stdout
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            main, linked = tmp / "main", tmp / "linked"
            g("init", "-q", main)
            (main / "a.txt").write_text("main\n")
            g("-C", main, "add", "a.txt")
            g("-C", main, "-c", "user.name=Hook-test", "-c", "user.email=hook@example.invalid",
              "commit", "-q", "--no-verify", "-m", "main")
            g("-C", main, "worktree", "add", "-q", "-b", "train", linked)
            git_dir = Path(g("-C", linked, "rev-parse", "--absolute-git-dir").strip())
            watched = {"HEAD": git_dir / "HEAD", "index": git_dir / "index",
                       "config": main / ".git" / "config", "a.txt": linked / "a.txt",
                       "main's a.txt": main / "a.txt"}
            before = {name: path.read_bytes() for name, path in watched.items()}
            heads = (g("-C", main, "rev-parse", "HEAD"), g("-C", linked, "rev-parse", "HEAD"))
            # As a runner under a hook has it: the hook's variables, and the machine's own
            # configuration, which hermetic_git shuts out.
            env = {name: value for name, value in plain.items()
                   if name not in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL")}
            env.update(GIT_DIR=str(git_dir), GIT_INDEX_FILE=str(git_dir / "index"),
                       **{self.CHILD: "1"})
            r = subprocess.run([sys.executable, str(HERE / "test_safe_push.py"),
                                "Units.test_source_statement"], cwd=linked, env=env,
                               capture_output=True, text=True, timeout=900)
            for name, path in watched.items():
                self.assertTrue(path.read_bytes() == before[name], f"{name} changed:\n"
                                + r.stderr[-2000:])
            self.assertNotIn("bare = true", (main / ".git" / "config").read_text())
            self.assertEqual((g("-C", main, "rev-parse", "HEAD"),
                              g("-C", linked, "rev-parse", "HEAD")), heads)
            self.assertEqual(sorted(p.name for p in linked.iterdir()), [".git", "a.txt"])
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])


# The report step needs bash and jq, as GitHub's runners have; there, a missing one fails
# the tests that run the step rather than skipping them.
REPORT_TOOLS = bool(shutil.which("jq") and shutil.which("bash")) \
    or os.environ.get("GITHUB_ACTIONS") == "true"
REPORT_TOOLS_REASON = ("the report step needs bash and jq, as GitHub's runners have (there, "
                       "a missing one fails the test rather than skipping it)")


@unittest.skipUnless(REPORT_TOOLS, REPORT_TOOLS_REASON)
class CadenceReport(unittest.TestCase):
    """The cadence workflow's report step (.github/workflows/safe-push-tests.yml), run as
    GitHub runs it, bash with -e and pipefail, on the shards' logs of a thousand long
    failures, with a stand-in for gh: it opens the issue, listing the first hundred (#300),
    from every shard's log (#233)."""

    def run_report(self, script: str, failures: int):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # Each line longer than the 300 characters the step keeps, so the thousand it
            # keeps (301,000 bytes) are far more than a pipe holds, and a reader that stops
            # early closes it. The failures are dealt among the shards' logs in turn, each
            # log in a folder of its own, as the step's fetch lays them down.
            name = "test_" + "x" * 250
            shards = ci_shard_count(ci_jobs())
            for shard in range(1, shards + 1):
                folder = tmp / "log" / f"test_safe_push-log-{shard}"
                folder.mkdir(parents=True)
                (folder / f"test_safe_push-{shard}.log").write_text("".join(
                    f"FAIL: {name}_{i:04d} (__main__.Merge.{name}_{i:04d})\n"
                    for i in range(shard - 1, failures, shards)) + "Ran 125 tests\n")
            bin_dir = tmp / "bin"
            bin_dir.mkdir()
            gh = bin_dir / "gh"
            gh.write_text('#!/bin/sh\n'
                          'if [ "$1" = api ]; then echo "[[]]"; exit 0; fi\n'
                          'if [ "$1 $2" = "issue create" ]; then\n'
                          '  while [ $# -gt 0 ]; do\n'
                          '    if [ "$1" = --body-file ]; then cp "$2" "$RUNNER_TEMP/created.md"; fi\n'
                          '    shift\n'
                          '  done\n'
                          '  exit 0\n'
                          'fi\n'
                          'exit 1\n')
            gh.chmod(0o755)
            env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                       RUNNER_TEMP=str(tmp), GH_TOKEN="x", GH_REPO="owner/repo",
                       TESTS="failure", NEGATIVE="success", KERNEL="success",
                       RUN_URL="https://example.invalid/run", SHA="0" * 40)
            r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c",
                                script], env=env, capture_output=True, text=True)
            created = tmp / "created.md"
            return r, created.read_text() if created.exists() else None

    def report_script(self) -> str:
        workflow = yaml.safe_load((SOURCE / ".github/workflows/safe-push-tests.yml").read_text())
        step = next(s for s in workflow["jobs"]["report"]["steps"]
                    if s.get("name", "").startswith("Open or update"))
        # GitHub runs `shell: bash` as bash -eo pipefail, which these tests run; without it,
        # bash -e alone, which they would not.
        self.assertEqual(step.get("shell"), "bash")
        return step["run"]

    def test_a_thousand_failures_open_the_issue_with_the_first_hundred(self):
        r, body = self.run_report(self.report_script(), 1000)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNotNone(body, "no issue was opened")
        self.assertIn("(the first 100)", body)
        self.assertEqual(sum(line.startswith("FAIL: ") for line in body.splitlines()), 100)
        self.assertIn("_0099 ", body)       # the first hundred, in order
        self.assertNotIn("_0100 ", body)

    def test_a_few_failures_are_listed_whole(self):
        # Three failures, each in the log of a shard of its own: all three are listed.
        r, body = self.run_report(self.report_script(), 3)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNotNone(body, "no issue was opened")
        self.assertNotIn("(the first 100)", body)
        self.assertEqual(sum(line.startswith("FAIL: ") for line in body.splitlines()), 3)

    def test_a_reader_that_stops_early_would_end_the_step(self):
        # The form #300 replaced: head stops reading, printf meets a closed pipe, and
        # pipefail ends the step before the issue opens. The test above would catch it.
        script = self.report_script()
        self.assertIn("sed -n '1,100p'", script)
        r, body = self.run_report(script.replace("sed -n '1,100p'", "head -n 100"), 1000)
        self.assertTrue(r.returncode != 0 and body is None, (r.returncode, r.stderr))


class OwnGitUnderHook(Edge):
    """safe_push's own commands under a hook (#357): run from a train's linked worktree
    with a hook's GIT_DIR and GIT_INDEX_FILE naming that worktree's git directory, a dry
    run leaves the train's HEAD, its index and the change staged in it as they were."""

    def plain_env(self) -> dict:
        """clean_env() with no variable of git's, so the test's own git is not the hook's,
        and no global or system configuration, so no hook or setting of the machine's runs
        in it (a global core.hooksPath would run on `git worktree add`)."""
        env = {name: value for name, value in clean_env().items()
               if not name.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        return env

    def dry_run_under_hook(self, work_tree: bool) -> None:
        plain = self.plain_env()
        train = TMP / f"hook-train-{self._testMethodName}"
        git(WORK, "worktree", "add", "-q", "--detach", str(train), BASE, env=plain)
        self.addCleanup(git, WORK, "worktree", "prune", env=plain, check=False)
        self.addCleanup(shutil.rmtree, train, ignore_errors=True)
        self.addCleanup(git, WORK, "worktree", "remove", "--force", str(train), env=plain,
                        check=False)
        reading = train / "docs" / "reading.md"
        reading.write_text(reading.read_text() + "\nA line for the test.\n")
        git(train, "add", "docs/reading.md", env=plain)
        git(train, "commit", "-q", "--no-verify", "-m", "A good commit", env=plain)
        reading.write_text(reading.read_text() + "\nA staged line.\n")
        git(train, "add", "docs/reading.md", env=plain)
        status = git(train, "status", "--porcelain", env=plain)
        self.assertEqual(status, "M  docs/reading.md\n")
        git_dir = Path(git(train, "rev-parse", "--absolute-git-dir", env=plain).strip())
        watched = {"the train's HEAD": git_dir / "HEAD",
                   "the train's index": git_dir / "index",
                   "the clone's index": WORK / ".git" / "index",
                   "the shared configuration": WORK / ".git" / "config"}
        before = {name: path.read_bytes() for name, path in watched.items()}
        hook = dict(plain, GIT_DIR=str(git_dir), GIT_INDEX_FILE=str(git_dir / "index"))
        if work_tree:
            hook["GIT_WORK_TREE"] = str(train)
        r = subprocess.run([sys.executable, str(SAFE_PUSH), "--_test-skip-checks",
                            *with_branch(("--dry-run",))], cwd=train, env=hook,
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        for name, path in watched.items():
            self.assertTrue(path.read_bytes() == before[name], f"{name} changed:\n{out}")
        self.assertEqual(git(train, "status", "--porcelain", env=plain), status, out)
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("would push", r.stdout)

    def test_a_hooks_git_dir_and_index_leave_the_train_alone(self):
        # The shape #355's review found: GIT_DIR and GIT_INDEX_FILE alone, naming a linked
        # worktree's git directory; `git worktree add` then checked the commit out into
        # the train's index, and its staged change was lost.
        self.dry_run_under_hook(work_tree=False)

    def test_with_the_hooks_work_tree_too(self):
        self.dry_run_under_hook(work_tree=True)

    def test_every_variable_git_ties_to_a_repository_is_listed(self):
        listed = set(git(SOURCE, "rev-parse", "--local-env-vars",
                         env=self.plain_env()).split())
        self.assertIn("GIT_DIR", listed)
        self.assertEqual(sorted(listed - safe_push.REPOSITORY_VARIABLES), [])

    def test_run_gives_no_command_a_repository_variable(self):
        planted = {name: "/planted" for name in safe_push.REPOSITORY_VARIABLES}
        seen = []
        def record(cmd, **kwargs):
            seen.append((cmd[0], kwargs["env"]))
            return subprocess.CompletedProcess(cmd, 0, "", "")
        with mock.patch.dict(os.environ, planted), \
                mock.patch.object(safe_push.subprocess, "run", record):
            safe_push.run(["git", "status"], WORK)
            safe_push.run(["gh", "pr", "view"], WORK)
            safe_push.run(["git", "status"], WORK, env=dict(os.environ))
            # A check, as run_step starts one: tool_env() keeps GIT_NO_REPLACE_OBJECTS
            # (#355), and run() must not take it away.
            safe_push.run(["sh", "-c", "true"], WORK, env=safe_push.tool_env())
        self.assertEqual([name for name, _ in seen], ["git", "gh", "git", "sh"])
        for name, env in seen:
            left = sorted(set(env) & (safe_push.REPOSITORY_VARIABLES
                                      - {"GIT_NO_REPLACE_OBJECTS"}))
            self.assertEqual(left, [], name)
        self.assertEqual([env.get("GIT_NO_REPLACE_OBJECTS") for _, env in seen],
                         ["1", "/planted", "1", "/planted"])
        # A variable the harness sets on purpose, named in `keep` (base_tree's temporary
        # index), passes; every other is still dropped.
        seen.clear()
        with mock.patch.dict(os.environ, planted), \
                mock.patch.object(safe_push.subprocess, "run", record):
            safe_push.run(["git", "read-tree", "HEAD"], WORK,
                          env=dict(os.environ, GIT_INDEX_FILE="/its/own/index"),
                          keep=("GIT_INDEX_FILE",))
        (_, env), = seen
        self.assertEqual(env["GIT_INDEX_FILE"], "/its/own/index")
        self.assertEqual(sorted(set(env) & safe_push.REPOSITORY_VARIABLES),
                         ["GIT_INDEX_FILE", "GIT_NO_REPLACE_OBJECTS"])
        # And for a program other than git, through own_env.
        seen.clear()
        with mock.patch.dict(os.environ, planted), \
                mock.patch.object(safe_push.subprocess, "run", record):
            safe_push.run(["env"], WORK, env=dict(os.environ, GIT_INDEX_FILE="/its/own/index"),
                          keep=("GIT_INDEX_FILE",))
        (_, env), = seen
        self.assertEqual(env["GIT_INDEX_FILE"], "/its/own/index")
        self.assertEqual(sorted(set(env) & safe_push.REPOSITORY_VARIABLES),
                         ["GIT_INDEX_FILE", "GIT_NO_REPLACE_OBJECTS"])

    def test_only_base_tree_keeps_a_repository_variable(self):
        # `keep` lets a variable that ties git to one repository through: only base_tree
        # may name one, its own temporary GIT_INDEX_FILE, and run() and
        # without_replacements only pass `keep` along (#357, #392).
        tree = ast.parse((SOURCE / "scripts" / "safe_push.py").read_text())
        kept = []

        def visit(node, where):
            # Each call is counted once, under the innermost function that holds it.
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, f"{where}.{child.name}" if where else child.name)
                    continue
                if (isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                        and child.func.id in ("run", "own_env", "without_replacements")):
                    values = [k.value for k in child.keywords if k.arg in ("keep", None)]
                    if child.func.id != "run" and len(child.args) > 1:
                        values.append(child.args[1])
                    kept.extend((where, ast.unparse(value)) for value in values)
                visit(child, where)
        visit(tree, "")
        self.assertEqual(sorted(kept), [("base_tree.index", "('GIT_INDEX_FILE',)"),
                                        ("run", "keep"), ("run", "keep"),
                                        ("without_replacements", "keep")])

    def test_base_tree_uses_only_its_temporary_index(self):
        # base_tree's temporary index, and no caller's or repository's, in each index
        # command; beside the source test above, which holds that no other place names a
        # variable in `keep`.
        path = "docs/reading.md"
        sha = self.commit("A changed base-tree input", {
            path: self.text(path) + "\nA line for the test.\n"})
        expected = git(WORK, "rev-parse", f"{BASE}^{{tree}}").strip()
        repository_index = WORK / ".git" / "index"
        repository_before = repository_index.read_bytes()

        with tempfile.TemporaryDirectory(prefix="caller-index-", dir=TMP) as tmp:
            caller_index = Path(tmp) / "index"
            plain = self.plain_env()
            git(WORK, "read-tree", sha,
                env=dict(plain, GIT_INDEX_FILE=str(caller_index)))
            caller_before = caller_index.read_bytes()
            planted = {name: "/planted" for name in safe_push.REPOSITORY_VARIABLES}
            planted["GIT_INDEX_FILE"] = str(caller_index)
            seen = []
            real_run = subprocess.run

            def record(cmd, **kwargs):
                result = real_run(cmd, **kwargs)
                env = kwargs["env"]
                index = env.get("GIT_INDEX_FILE")
                seen.append((cmd, env, index is not None and Path(index).is_file()))
                return result

            with mock.patch.dict(os.environ, planted), \
                    mock.patch.object(safe_push.subprocess, "run", record):
                tree = safe_push.base_tree(WORK, BASE, sha, [("M", path)])

            self.assertEqual(tree, expected)
            self.assertEqual(caller_index.read_bytes(), caller_before)
            self.assertEqual(repository_index.read_bytes(), repository_before)

        temporary_indexes = []
        for cmd, env, index_exists in seen:
            operation = next(arg for arg in cmd if arg in
                             {"read-tree", "ls-tree", "update-index", "write-tree"})
            left = sorted(set(env) & (safe_push.REPOSITORY_VARIABLES
                                      - {"GIT_INDEX_FILE", "GIT_NO_REPLACE_OBJECTS"}))
            self.assertEqual(left, [], operation)
            self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1", operation)
            if operation == "ls-tree":
                self.assertNotIn("GIT_INDEX_FILE", env)
                continue
            self.assertTrue(index_exists, operation)
            temporary_indexes.append(env["GIT_INDEX_FILE"])
        self.assertEqual(len(set(temporary_indexes)), 1)
        temporary_index = Path(temporary_indexes[0])
        self.assertNotEqual(temporary_index, caller_index)
        self.assertNotEqual(temporary_index, repository_index)
        self.assertFalse(temporary_index.exists())

    MUTATORS = frozenset({"update", "setdefault", "pop", "popitem", "clear", "__setitem__",
                          "__delitem__", "__ior__"})

    def bindings(self, function, name: str) -> list:
        """The values `name` is bound to in `function`: an assignment's, an annotated
        one's or a walrus's value. A binding that holds no single value (an augmented
        assignment, unpacking, a for or with target) counts as None, and so does any
        change to what the name holds: a subscript stored or deleted, or a mutating
        method called on it."""
        values = []
        def stores(target) -> bool:  # the name itself, whether read or stored
            return isinstance(target, ast.Name) and target.id == name
        for node in ast.walk(function):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if stores(target):
                        values.append(node.value)
                    elif isinstance(target, (ast.Tuple, ast.List)) and any(
                            stores(e) for e in ast.walk(target)):
                        values.append(None)
            elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and stores(node.target):
                values.append(node.value)
            elif isinstance(node, ast.AugAssign) and stores(node.target):
                values.append(None)
            elif isinstance(node, (ast.For, ast.AsyncFor)) and any(
                    stores(e) for e in ast.walk(node.target)):
                values.append(None)
            elif isinstance(node, ast.withitem) and node.optional_vars is not None and any(
                    stores(e) for e in ast.walk(node.optional_vars)):
                values.append(None)
            elif (isinstance(node, ast.Subscript) and stores(node.value)
                  and isinstance(node.ctx, (ast.Store, ast.Del))):
                values.append(None)
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                  and stores(node.func.value) and node.func.attr in self.MUTATORS):
                values.append(None)
        return values

    def test_every_launch_is_given_a_built_environment(self):
        # run(), risk.py's launch and the hand-over start the harness's processes: each
        # names an environment built by own_env() or without_replacements(), never the
        # caller's as it is (#357).
        builders = ("own_env", "without_replacements")
        # Each way a process is started, and where its environment goes: a keyword, or
        # the position os's functions take it at. One that takes none (os.system, os.execv
        # and the like) inherits the caller's, and fails here.
        positional = {"os.execve": 2, "os.execvpe": 2, "os.posix_spawn": 2,
                      "os.posix_spawnp": 2, "os.spawnve": 3, "os.spawnvpe": 3,
                      "os.execle": -1, "os.execlpe": -1, "os.spawnle": -1,
                      "os.spawnlpe": -1}
        apis = {*positional, "subprocess.run", "subprocess.Popen", "subprocess.call",
                "subprocess.check_call", "subprocess.check_output",
                "subprocess.getoutput", "subprocess.getstatusoutput", "os.system",
                "os.popen", "os.execv", "os.execvp", "os.execl", "os.execlp", "os.spawnv",
                "os.spawnvp", "os.spawnl", "os.spawnlp", "pty.spawn",
                "asyncio.create_subprocess_exec", "asyncio.create_subprocess_shell"}
        tree = ast.parse((SOURCE / "scripts" / "safe_push.py").read_text())
        launches = []
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(function):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)):
                    continue
                name = f"{node.func.value.id}.{node.func.attr}"
                if name in apis:
                    launches.append((function, name, node))
        # run()'s own, risk.py's and the hand-over's: the CI watch runs through run()
        # since #392.
        self.assertEqual(len(launches), 3, [ast.unparse(n) for _, _, n in launches])
        for function, name, node in launches:
            with self.subTest(launch=ast.unparse(node)[:60]):
                where = f"{name} in {function.name}"
                if name in positional:
                    index = positional[name]
                    fits = len(node.args) > max(index, -index - 1)
                    env = node.args[index] if fits else None
                else:
                    env = next((k.value for k in node.keywords if k.arg == "env"), None)
                self.assertIsNotNone(env, f"{where} names no environment")
                if isinstance(env, ast.Name):
                    # A name (run()'s own env, the hand-over's): every binding of it in the
                    # function binds a call of one of the builders, and nothing changes
                    # what it holds afterwards.
                    values = self.bindings(function, env.id)
                    self.assertTrue(values, f"{where}: {env.id} is never assigned")
                    for value in values:
                        shown = ast.unparse(value) if value is not None else env.id
                        self.assertIsInstance(value, ast.Call, f"{where}: {shown}")
                        self.assertIn(ast.unparse(value.func), builders, f"{where}: {shown}")
                    continue
                self.assertIsInstance(env, ast.Call, ast.unparse(env))
                self.assertIn(ast.unparse(env.func), builders, ast.unparse(env))


class HookEnvironment(unittest.TestCase):
    """The checks' environment under a hook (#355): a program the pre-flight runs as a
    check, given a hook's GIT_DIR and GIT_INDEX_FILE naming a linked worktree's git
    directory, as on 22 October, builds and commits to a repository of its own and leaves
    the enclosing one as it was: its HEAD, index and files, and the shared configuration,
    which git init with that GIT_DIR once turned bare."""

    IDENT = ["-c", "user.name=Hook-test", "-c", "user.email=hook@example.invalid",
             "-c", "commit.gpgsign=false"]

    def setUp(self):
        # The test's own git reads no variable of git's, no global or system configuration
        # and no hook of the machine's: it builds its repositories hermetically.
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for name in ("home", "xdg", "hooks"):
            (tmp / name).mkdir()
        self.env = {name: value for name, value in os.environ.items()
                    if not name.startswith("GIT_")}
        self.env.update(HOME=str(tmp / "home"), XDG_CONFIG_HOME=str(tmp / "xdg"),
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.options = ["-c", f"core.hooksPath={tmp / 'hooks'}",
                        "-c", f"core.excludesFile={os.devnull}"]

    def clean(self) -> dict:
        return dict(self.env)

    def git(self, *args) -> str:
        return subprocess.run(["git", *self.options, *args], env=self.clean(),
                              capture_output=True, text=True, check=True).stdout

    def check_under_hook(self, extra: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            main, linked, inner, logs = (tmp / "main", tmp / "linked", tmp / "inner",
                                         tmp / "logs")
            for folder in (main, inner, logs):
                folder.mkdir()
            self.git("init", "-q", str(main))
            (main / "a.txt").write_text("main\n")
            self.git("-C", str(main), "add", "a.txt")
            self.git("-C", str(main), *self.IDENT, "commit", "-q", "--no-verify", "-m", "main")
            self.git("-C", str(main), "worktree", "add", "-q", "-b", "train", str(linked))
            git_dir = Path(self.git("-C", str(linked), "rev-parse", "--absolute-git-dir")
                           .strip())
            common = main / ".git"
            watched = {"HEAD": git_dir / "HEAD", "index": git_dir / "index",
                       "config": common / "config", "a.txt": linked / "a.txt",
                       "main's a.txt": main / "a.txt"}
            before = {name: path.read_bytes() for name, path in watched.items()}
            heads = (self.git("-C", str(main), "rev-parse", "HEAD"),
                     self.git("-C", str(linked), "rev-parse", "HEAD"))
            git = shlex.join(["git", *self.options])
            # The check writes down the git variables it was started with (#357: run() once
            # took GIT_NO_REPLACE_OBJECTS from it while tool_env() kept it).
            seen = tmp / "seen-variables"
            check = (f"env | grep '^GIT_' | sort > {shlex.quote(str(seen))}; "
                     f"{git} init -q && echo inner > b.txt && {git} add b.txt && "
                     f"{git} {' '.join(self.IDENT)} commit -q --no-verify -m inner")
            hook = {"GIT_DIR": str(git_dir), "GIT_INDEX_FILE": str(git_dir / "index"),
                    "GIT_NO_REPLACE_OBJECTS": "1",
                    **{name: str(linked) if value == "WORKTREE" else value
                       for name, value in extra.items()}}
            with mock.patch.dict(os.environ, {**self.clean(), **hook}, clear=True):
                env = safe_push.tool_env()
                rep = safe_push.Report()
                safe_push.run_step("4", "a check that builds a repository",
                                   ["sh", "-c", check], inner, rep, logs, 1, fail="note")
            # The damage first, so that main's tool_env fails on the incident itself (a
            # failing check is noted, not raised, so these run either way); the messages
            # name git's variables only, never the rest of the environment.
            for name, path in watched.items():
                self.assertEqual(path.read_bytes(), before[name], name)
            self.assertNotIn("bare = true", (common / "config").read_text())
            self.assertEqual((self.git("-C", str(main), "rev-parse", "HEAD"),
                              self.git("-C", str(linked), "rev-parse", "HEAD")), heads)
            self.assertEqual(sorted(p.name for p in linked.iterdir()), [".git", "a.txt"])
            self.assertEqual(rep.steps[-1].outcome, "ok", [s.outcome for s in rep.steps])
            self.assertEqual(self.git("-C", str(inner), "log", "--format=%s"), "inner\n")
            kept = sorted(name for name in env if name.startswith("GIT_"))
            self.assertEqual(kept, ["GIT_NO_REPLACE_OBJECTS"])
            self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
            self.assertEqual(seen.read_text(), "GIT_NO_REPLACE_OBJECTS=1\n")

    def test_a_hooks_git_dir_and_index_reach_no_check(self):
        # The incident's shape: GIT_DIR and GIT_INDEX_FILE alone, naming a linked worktree.
        self.check_under_hook({})

    def test_with_the_hooks_work_tree_too(self):
        self.check_under_hook({"GIT_WORK_TREE": "WORKTREE"})


class Units(unittest.TestCase):
    """The scanner and helpers, with temporary Git only where history is the subject."""

    def test_review_stamp_checks_an_unchanged_commit_in_head_history(self):
        facts = {"propositions": [{"ref": "I.1", "statement": "A test statement."}]}
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            lean = repo / "Elements/BookI/Prop01.lean"
            source = repo / "heath/I/01.md"
            record = repo / "review/I/01.toml"
            for path in (lean, source, record):
                path.parent.mkdir(parents=True, exist_ok=True)
            lean.write_text("theorem Prop1 : True := by trivial\n")
            source.write_text("A test enunciation.\n\nA test proof.\n")
            fingerprint = review_stamp.heath.review_fingerprint(facts, "I.1")
            lean_hash = review_stamp.heath.file_hash(lean)
            text = (f'[statement]\nscope = "full"\nfingerprint = "{fingerprint}"\n\n'
                    '[route]\nkind = "euclid"\n\n[review]\nstage = "exceptions"\n'
                    f'reviewer = "Test reader"\nlean = "{lean_hash}"\n'
                    'text = "sha256:0000000000000000"\n')
            own = review_stamp.heath.text_hash(text)
            record.write_text(text.replace("sha256:0000000000000000", own))
            git(repo, "init", "-q")
            git(repo, "config", "user.name", "review stamp test")
            git(repo, "config", "user.email", "review-stamp-test@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "The files read")
            read_commit = git(repo, "rev-parse", "HEAD").strip()[:12]
            current = record.read_text().replace("[review]\n",
                                                 f'[review]\ncommit = "{read_commit}"\n', 1)
            record.write_text(current)
            git(repo, "add", "review/I/01.toml")
            git(repo, "commit", "-q", "-m", "Record the reading")
            with mock.patch.object(review_stamp, "ROOT", repo), \
                    mock.patch.object(review_stamp.heath, "ROOT", repo), \
                    mock.patch.object(review_stamp.heath, "REVIEW", repo / "review"):
                self.assertEqual(review_stamp.stamp(facts, "I", 1, read_commit, False),
                                 (False, "I.1: current"))
                self.assertEqual(record.read_text(), current)
                git(repo, "checkout", "--quiet", "--orphan", "unrelated")
                git(repo, "add", ".")
                git(repo, "commit", "-q", "-m", "The same files on another history")
                with self.assertRaisesRegex(ValueError, "is not in the history of HEAD"):
                    review_stamp.stamp(facts, "I", 1, read_commit, False)
                self.assertEqual(record.read_text(), current)

    def test_review_stamp_ignores_replacement_objects(self):
        facts = {"propositions": [{"ref": "I.1", "statement": "A test statement."}]}
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            lean = repo / "Elements/BookI/Prop01.lean"
            source = repo / "heath/I/01.md"
            record = repo / "review/I/01.toml"
            for path in (lean, source, record):
                path.parent.mkdir(parents=True, exist_ok=True)
            lean.write_text("theorem Prop1 : True := by trivial\n")
            source.write_text("A test enunciation.\n\nA test proof.\n")
            fingerprint = review_stamp.heath.review_fingerprint(facts, "I.1")
            lean_hash = review_stamp.heath.file_hash(lean)
            old = (f'[statement]\nscope = "full"\nfingerprint = "{fingerprint}"\n\n'
                   '[route]\nkind = "euclid"\nnote = "The old record text."\n\n'
                   '[review]\nstage = "exceptions"\nreviewer = "Test reader"\n'
                   f'lean = "{lean_hash}"\n')
            record.write_text(old)
            git(repo, "init", "-q")
            git(repo, "config", "user.name", "review stamp test")
            git(repo, "config", "user.email", "review-stamp-test@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "The old record text")
            read_full = git(repo, "rev-parse", "HEAD").strip()
            read_commit = read_full[:12]
            current = old.replace("The old record text.", "The changed record text.")
            current = current.replace("[review]\n", f'[review]\ncommit = "{read_commit}"\n', 1)
            record.write_text(current)
            git(repo, "add", "review/I/01.toml")
            git(repo, "commit", "-q", "-m", "Change the record text")
            current_tree = git(repo, "rev-parse", "HEAD^{tree}").strip()
            unrelated = git(repo, "commit-tree", current_tree, "-m", "An unrelated commit").strip()
            replacement = git(repo, "commit-tree", current_tree, "-p", unrelated,
                              "-m", "Replacement contents").strip()
            git(repo, "replace", read_full, replacement)
            self.assertEqual(git(repo, "show", f"{read_full}:review/I/01.toml"), current)
            self.assertEqual(subprocess.run(
                ["git", "merge-base", "--is-ancestor", unrelated, "HEAD"], cwd=repo,
                capture_output=True).returncode, 0)
            # A legacy graft, which --no-replace-objects does not switch off.
            grafted = git(repo, "commit-tree", current_tree, "-m", "A grafted commit").strip()
            head = git(repo, "rev-parse", "HEAD").strip()
            (repo / ".git/info").mkdir(exist_ok=True)
            (repo / ".git/info/grafts").write_text(f"{head} {read_full} {grafted}\n")
            self.assertEqual(subprocess.run(
                ["git", "--no-replace-objects", "merge-base", "--is-ancestor", grafted, "HEAD"],
                cwd=repo, capture_output=True).returncode, 0)
            with mock.patch.object(review_stamp, "ROOT", repo), \
                    mock.patch.object(review_stamp.heath, "ROOT", repo), \
                    mock.patch.object(review_stamp.heath, "REVIEW", repo / "review"):
                self.assertFalse(review_stamp.in_history(unrelated))
                self.assertFalse(review_stamp.in_history(grafted))
                self.assertEqual(review_stamp.migrate_text("I", 1, False),
                                 ("reader", f"I.1: edited since its stamp commit {read_commit}"))
                self.assertEqual(record.read_text(), current)
                with self.assertRaisesRegex(ValueError,
                                            "says something other than it says now"):
                    review_stamp.stamp(facts, "I", 1, read_commit, False)
                self.assertEqual(record.read_text(), current)

    def test_review_stamp_migration_counts_an_unresolved_commit_a_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for name, body in {"Elements/BookI/Prop01.lean": "theorem P : True := trivial\n",
                               "heath/I/01.md": "A test enunciation.\n\nA test proof.\n"}.items():
                (repo / name).parent.mkdir(parents=True, exist_ok=True)
                (repo / name).write_text(body)
            record = repo / "review/I/01.toml"
            record.parent.mkdir(parents=True)
            # Its stamp commit is one this clone never fetched, as in a shallow clone.
            text = ('[statement]\nscope = "full"\nfingerprint = "sha256:0123456789abcdef"\n\n'
                    '[route]\nkind = "euclid"\n\n[review]\nstage = "exceptions"\n'
                    'reviewer = "Test reader"\ncommit = "abcdef1"\n'
                    'lean = "sha256:0123456789abcdef"\n')
            git(repo, "init", "-q")
            git(repo, "config", "user.name", "review stamp test")
            git(repo, "config", "user.email", "review-stamp-test@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            record.write_text(text)
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "A record whose stamp commit is not here")
            cases = {
                "without text": text,
                "matching text": with_text(text, review_stamp.heath.text_hash(text)),
                "stale text": with_text(text, "sha256:0000000000000000"),
            }
            for label, body in cases.items():
                with self.subTest(label=label):
                    record.write_text(body)
                    out = io.StringIO()
                    with mock.patch.object(review_stamp, "ROOT", repo), \
                            mock.patch.object(review_stamp.heath, "ROOT", repo), \
                            mock.patch.object(review_stamp.heath, "REVIEW", repo / "review"), \
                            contextlib.redirect_stdout(out):
                        code = review_stamp.migrate([("I", 1)], dry_run=True)
                    self.assertEqual(code, 1, out.getvalue())
                    self.assertIn(
                        f"✗ I.1: its stamp commit abcdef1 {review_stamp.NO_COMMIT}",
                        out.getvalue())
                    self.assertNotIn("needs a reader, who reads", out.getvalue())
                    self.assertIn("0 need(s) a reader; 1 problem(s)", out.getvalue())
                    self.assertEqual(record.read_text(), body)

    def test_review_stamp_migration_rejects_a_shallow_ancestry_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "source"
            shallow = root / "shallow"
            git(root, "init", "-q", "-b", "main", str(repo))
            git(repo, "config", "user.name", "review stamp test")
            git(repo, "config", "user.email", "review-stamp-test@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            for name, body in {"Elements/BookI/Prop01.lean": "theorem P : True := trivial\n",
                               "heath/I/01.md": "A test enunciation.\n\nA test proof.\n"}.items():
                (repo / name).parent.mkdir(parents=True, exist_ok=True)
                (repo / name).write_text(body)
            record = repo / "review/I/01.toml"
            record.parent.mkdir(parents=True)
            text = ('[statement]\nscope = "full"\n'
                    'fingerprint = "sha256:0123456789abcdef"\n\n'
                    '[route]\nkind = "euclid"\n\n[review]\nstage = "exceptions"\n'
                    'reviewer = "Test reader"\nlean = "sha256:0123456789abcdef"\n')
            record.write_text(text)
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "The base record")
            git(repo, "checkout", "-q", "-b", "feature")
            git(repo, "commit", "-q", "--allow-empty", "-m", "The files read")
            read_full = git(repo, "rev-parse", "HEAD").strip()
            read_commit = read_full[:12]
            stamped = text.replace("[review]\n", f'[review]\ncommit = "{read_commit}"\n', 1)
            record.write_text(stamped)
            git(repo, "add", "review/I/01.toml")
            git(repo, "commit", "-q", "-m", "Record the reading")
            git(repo, "checkout", "-q", "main")
            git(repo, "merge", "-q", "--no-ff", "feature", "-m", "Merge the record")
            for n in range(3):
                git(repo, "commit", "-q", "--allow-empty", "-m", f"Later change {n + 1}")
            git(root, "clone", "-q", "--depth", "2", "--no-single-branch", "--branch", "main",
                repo.as_uri(), str(shallow))
            self.assertEqual(git(shallow, "cat-file", "-t", read_full).strip(), "commit")
            self.assertEqual(git(shallow, "rev-parse", "--is-shallow-repository").strip(),
                             "true")
            before = (shallow / "review/I/01.toml").read_text()
            out = io.StringIO()
            with mock.patch.object(review_stamp, "ROOT", shallow), \
                    mock.patch.object(review_stamp.heath, "ROOT", shallow), \
                    mock.patch.object(review_stamp.heath, "REVIEW", shallow / "review"), \
                    contextlib.redirect_stdout(out):
                self.assertFalse(review_stamp.in_history(read_full))
                code = review_stamp.migrate([("I", 1)], dry_run=False)
            self.assertEqual(code, 1, out.getvalue())
            self.assertIn("incomplete history of this shallow clone", out.getvalue())
            self.assertNotIn("needs a reader, who reads", out.getvalue())
            self.assertIn("0 need(s) a reader; 1 problem(s)", out.getvalue())
            self.assertEqual((shallow / "review/I/01.toml").read_text(), before)
            self.assertNotIn('\ntext = "', before)
            with mock.patch.object(review_stamp, "ROOT", shallow), \
                    mock.patch.object(review_stamp.heath, "ROOT", shallow), \
                    mock.patch.object(review_stamp.heath, "REVIEW", shallow / "review"), \
                    mock.patch.object(review_stamp.heath, "review_fingerprint",
                                      return_value="sha256:0123456789abcdef"):
                with self.assertRaisesRegex(ValueError, "cannot be confirmed in the "
                                            "incomplete history of this shallow clone"):
                    review_stamp.stamp({}, "I", 1, read_commit, False)
                self.assertEqual((shallow / "review/I/01.toml").read_text(), before)
                # A record that already carries a current `text` has nothing to migrate,
                # so the shallow boundary does not make it a problem.
                own = review_stamp.heath.text_hash(before)
                (shallow / "review/I/01.toml").write_text(
                    before.replace("[review]\n", f'[review]\ntext = "{own}"\n', 1))
                self.assertEqual(review_stamp.migrate_text("I", 1, True)[0], "current")

    def test_review_stamp_rejects_an_ambiguous_prefix_even_when_a_ref_shadows_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q", "--object-format=sha1")
            tree = git(repo, "write-tree").strip()
            seen = {}
            collision = None
            for nonce in range(100_000):
                stamp = nonce + 1
                body = (f"tree {tree}\nauthor Test <test@example.invalid> {stamp} +0000\n"
                        f"committer Test <test@example.invalid> {stamp} +0000\n\n"
                        f"Commit {nonce}\n").encode()
                oid = hashlib.sha1(b"commit " + str(len(body)).encode() + b"\0" + body).hexdigest()
                prefix = oid[:7]
                if prefix in seen:
                    collision = (prefix, seen[prefix], (oid, body))
                    break
                seen[prefix] = (oid, body)
            self.assertIsNotNone(collision, "no seven-digit collision in 100,000 commits")
            prefix, first, second = collision
            for expected, body in (first, second):
                written = subprocess.run(
                    ["git", "hash-object", "-t", "commit", "-w", "--stdin"], cwd=repo,
                    input=body, capture_output=True, check=True).stdout.decode().strip()
                self.assertEqual(written, expected)
            with mock.patch.object(review_stamp, "ROOT", repo):
                self.assertEqual(review_stamp.resolve(prefix),
                                 (None, review_stamp.AMBIGUOUS_COMMIT))
            git(repo, "update-ref", "refs/heads/main", second[0])
            git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
            git(repo, "update-ref", f"refs/heads/{prefix}", second[0])
            for name, body in {"Elements/BookI/Prop01.lean": "theorem P : True := trivial\n",
                               "heath/I/01.md": "A test enunciation.\n\nA test proof.\n"}.items():
                (repo / name).parent.mkdir(parents=True, exist_ok=True)
                (repo / name).write_text(body)
            record = repo / "review/I/01.toml"
            record.parent.mkdir(parents=True)
            text = ('[statement]\nscope = "full"\n'
                    'fingerprint = "sha256:0123456789abcdef"\n\n'
                    '[route]\nkind = "euclid"\n\n[review]\nstage = "exceptions"\n'
                    f'reviewer = "Test reader"\ncommit = "{prefix}"\n'
                    'lean = "sha256:0123456789abcdef"\n')
            record.write_text(text)
            out = io.StringIO()
            with mock.patch.object(review_stamp, "ROOT", repo), \
                    mock.patch.object(review_stamp.heath, "ROOT", repo), \
                    mock.patch.object(review_stamp.heath, "REVIEW", repo / "review"), \
                    contextlib.redirect_stdout(out):
                self.assertEqual(review_stamp.resolve(prefix),
                                 (None, review_stamp.AMBIGUOUS_COMMIT))
                code = review_stamp.migrate([("I", 1)], dry_run=True)
            self.assertEqual(code, 1, out.getvalue())
            self.assertIn(f"its stamp commit {prefix} {review_stamp.AMBIGUOUS_COMMIT}",
                          out.getvalue())
            self.assertIn("a reader identifies the intended commit without guessing",
                          out.getvalue())
            self.assertIn("0 need(s) a reader; 1 problem(s)", out.getvalue())
            self.assertEqual(record.read_text(), text)

    def test_describe_distinguishes_review_record_changes(self):
        commit = "1234567890abcdef"
        newer = "fedcba0987654321"
        paths = {
            "review/I/01.toml": (
                f'[review]\ncommit = "{commit}"\nlean = "old"\n',
                f'[review]\ncommit = "{commit}"\nlean = "old"\ntext = "new"\n'),
            "review/I/02.toml": (
                f'[review]\ncommit = "{commit}"\nlean = "old"\ntext = "old"\n',
                f'[review]\ncommit = "{commit}"\nlean = "old"\n'),
            "review/I/03.toml": (
                f'[review]\ncommit = "{commit}"\nlean = "old"\ntext = "old"\n',
                f'[review]\ncommit = "{commit}"\nlean = "new"\ntext = "old"\n'),
            "review/I/04.toml": (
                f'[review]\ncommit = "{commit}"\nlean = "old"\ntext = "old"\n',
                f'[review]\ncommit = "{newer}"\nlean = "new"\ntext = "old"\n'),
            "review/I/05.toml": (
                f'note = "old"\n[review]\ncommit = "{commit}"\nlean = "old"\ntext = "old"\n',
                f'note = "new"\n[review]\ncommit = "{commit}"\nlean = "old"\ntext = "old"\n'),
            "review/I/06.toml": (
                f'note = "old"\n[review]\ncommit = "{commit}"\nlean = "old"\ntext = "old"\n',
                f'note = "new"\n[review]\ncommit = "{commit}"\nlean = "old"\ntext = "new"\n'),
        }
        ctx = safe_push.Context(Path("."), "b" * 40, "a" * 40, 1, "", None, {})

        def changed_files(_repo, _base, _sha, prefix=None):
            return [("M", path) for path in paths] if prefix in (None, "review") else []

        def show(_repo, revision, path):
            return paths[path][0 if revision == ctx.base else 1]

        with mock.patch.object(safe_push, "changed_files", changed_files), \
                mock.patch.object(safe_push, "show", show), \
                mock.patch.object(safe_push, "git", return_value=""):
            records = safe_push.describe(ctx, safe_push.Preflight([], []))["records"]
        self.assertIn("`review/I/01.toml`: its stamps written, its commit kept at "
                      "`1234567890ab`", records)
        self.assertIn("`review/I/02.toml`: a stamp taken away (`text`)", records)
        self.assertNotIn("`review/I/02.toml`: its stamps written", records)
        self.assertIn("`review/I/03.toml`: its stamps written, its commit kept at "
                      "`1234567890ab`", records)
        self.assertIn("`review/I/04.toml`: re-stamped at `fedcba098765`", records)
        self.assertIn("`review/I/05.toml`: touched, not re-stamped", records)
        self.assertIn("`review/I/06.toml`: touched, not re-stamped", records)

    def test_a_crash_once_the_sandbox_is_set_imports_nothing(self):
        # A command's output that is not UTF-8 makes run() raise, and an exception that
        # reaches Python's own handler imports traceback and a dozen more, found first in
        # the harness's own directory, which sandboxed code may write. safe_push.py
        # imports them at its top, so a crash once the sandbox is set imports nothing.
        script = (
            "import sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "import safe_push\n"
            "seen = []\n"
            "def hook(event, args):\n"
            "    if event == 'import' and safe_push.SANDBOX is not None \\\n"
            "            and args[0] not in sys.builtin_module_names:\n"
            "        seen.append(args[0])\n"
            "sys.addaudithook(hook)\n"
            "safe_push.SANDBOX = '(version 1) (allow default)'\n"
            "try:\n"
            "    b'\\xff'.decode('utf-8')\n"
            "except UnicodeDecodeError:\n"
            "    sys.excepthook(*sys.exc_info())\n"
            "safe_push.SANDBOX = None\n"
            "print('SEEN', ','.join(seen))\n")
        r = subprocess.run([sys.executable, "-I", "-c", script, str(HERE)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("UnicodeDecodeError", r.stderr)          # the handler ran
        self.assertIn("SEEN \n", r.stdout, r.stdout + r.stderr)  # and imported nothing

    def test_environment_uses_git_on_the_checks_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            home = tmp / "home"
            effective_bin = home / ".elan" / "bin"
            caller_bin = tmp / "caller-bin"
            effective_bin.mkdir(parents=True)
            caller_bin.mkdir()
            effective_git = effective_bin / "git"
            caller_git = caller_bin / "git"
            effective_git.write_text('#!/bin/sh\n/bin/cat "$0.version"\n')
            caller_git.write_text("#!/bin/sh\necho 'git version caller'\n")
            effective_git.chmod(0o755)
            caller_git.chmod(0o755)
            version = effective_git.with_suffix(".version")
            caller_path = f"{caller_bin}:/usr/bin:/bin"
            caller_source = caller_git.read_bytes()
            with mock.patch.object(safe_push.Path, "home", return_value=home), \
                    mock.patch.dict(os.environ, {"PATH": caller_path}, clear=True):
                version.write_text("git version effective-one\n")
                first = safe_push.environment(SOURCE)
                version.write_text("git version effective-two\n")
                second = safe_push.environment(SOURCE)
                self.assertEqual(os.environ["PATH"], caller_path)
                self.assertEqual(caller_git.read_bytes(), caller_source)
                version.unlink()
                with self.assertRaisesRegex(safe_push.Refusal, "`git --version` failed"):
                    safe_push.environment(SOURCE)
        self.assertEqual(first["PATH"], second["PATH"])
        self.assertEqual(first["git --version"], "git version effective-one")
        self.assertEqual(second["git --version"], "git version effective-two")
        self.assertNotEqual(safe_push.sha256_of(first), safe_push.sha256_of(second))

    def test_only_is_preserved_and_changes_the_main_checks_key(self):
        ctx = safe_push.Context(Path("/repo"), "commit", "main", 1, "/origin", None, {})

        def fake_git(repo, *args, **kwargs):
            if args == ("rev-parse", "commit^{tree}"):
                return "commit-tree\n"
            self.fail(args)

        def fake_run(cmd, cwd, **kwargs):
            self.assertEqual(cmd, ["git", "--version"])
            return subprocess.CompletedProcess(cmd, 0, "git version 2.0\n", "")

        keys = []
        with mock.patch.object(safe_push, "HARNESS_BLOB", "harness-blob"), \
                mock.patch.object(safe_push, "toolchain", return_value={"lean": "4.35"}), \
                mock.patch.object(safe_push, "base_tree", return_value="base-tree"), \
                mock.patch.object(safe_push, "git", side_effect=fake_git), \
                mock.patch.object(safe_push, "run", side_effect=fake_run):
            for only in (None, "between", "parallel"):
                with mock.patch.dict(os.environ, {} if only is None else {"ONLY": only},
                                     clear=True):
                    forwarded = safe_push.tool_env()
                    fields, why = safe_push.main_checks_fields(ctx, Path("/worktree"), [],
                                                               [])
                self.assertEqual(why, "")
                variables = dict(fields["environment"]["variables"])
                if only is None:
                    self.assertNotIn("ONLY", forwarded)
                    self.assertNotIn("ONLY", variables)
                else:
                    self.assertEqual(forwarded["ONLY"], only)
                    self.assertEqual(variables["ONLY"], only)
                keys.append(safe_push.sha256_of(fields))
        self.assertEqual(len(set(keys)), 3)

    def registry_commands(self, entries):
        """The registry's checks, in order, each as section 8 writes its command: the
        `empty` entry as `git status --porcelain`, every other by its name, which is its
        command (the reader holds them so)."""
        checks = []
        for entry in entries:
            if entry.empty:
                self.assertEqual(entry.name, "git status --porcelain is empty")
                self.assertIsNone(entry.command)
                checks.append(FRESHNESS_COMMAND)
            else:
                self.assertEqual(entry.name, " ".join(entry.command))
                checks.append(entry.name)
        return checks

    def assertSequenceAgrees(self, root: Path) -> list:
        """#229: the registry at `root`, checks/, is the one list. It is well formed, of the
        `check` job alone; section 8's first command block in root's docs/WORKFLOW.md is
        what render.py writes from it; root's CI `check` job is its setup and the one step
        that runs it; and root's CI `model` and `negative` jobs run what MODEL_JOB and
        NEGATIVE run. Nothing here reads CHECKS, so the registry grows by a file and its
        render alone. Its entries, in order."""
        entries = registry.load(root)
        self.assertEqual({e.job for e in entries}, {"check"})
        self.assertEqual([e.order for e in entries], sorted(e.order for e in entries))
        for entry in entries:
            self.assertRegex(entry.path, r"^checks/[0-9]+-[a-z0-9-]+\.toml$")
            self.assertEqual(entry.section8.split("#", 1)[0].strip(),
                             FRESHNESS_COMMAND if entry.empty else entry.name)
        workflow = (root / "docs/WORKFLOW.md").read_text()
        regions = registry.MARKERS.findall(workflow)
        self.assertEqual(len(regions), 1, "section 8's block stands between one pair of markers")
        self.assertEqual(regions[0][1], registry.section8_block(entries))
        # The region is section 8's first command block, as before.
        block = workflow.split("## 8. Validation on the integrated revision", 1)[1]
        self.assertLess(block.index("<!-- checks -->"), block.index("```sh\n"))
        block = block.split("```sh\n", 1)[1].split("```", 1)[0]
        documented = [line.split("#", 1)[0].strip() for line in block.splitlines()
                      if line.strip() and not line.startswith("export ")]
        checks = self.registry_commands(entries)
        self.assertEqual(checks, documented)
        ci = (root / ".github/workflows/ci.yml").read_text()
        self.assertEqual(enforced_check_commands(normalized_check_job(ci)), [RUN_CHECKS])
        certificate = checks.index("lake env lean Certificate/Facts.lean")
        self.assertEqual(checks[certificate + 1], "python3 -I tests/test_certificate.py")
        # The pages are rendered, then the whole worktree must be clean: the entry with
        # `empty` comes straight after render.py, and is a check of the whole worktree,
        # with no pathspec, as run_checks.py runs it.
        freshness = checks.index(FRESHNESS_COMMAND)
        self.assertEqual(checks[freshness - 1], RENDER_COMMAND)
        self.assertEqual(entries[freshness].argv(), ["git", "status", "--porcelain"])
        # And CI's `model` and `negative` jobs run what MODEL_JOB and NEGATIVE run, but for
        # the model job's results_check.py, which only CI runs until it joins MODEL_JOB
        # (#378; WORKFLOW, section 8): named here, so that no other step can be CI's alone.
        jobs = yaml.safe_load(ci)["jobs"]
        runs = [line.strip() for step in jobs["model"]["steps"]
                for line in step.get("run", "").splitlines() if line.strip()]
        self.assertEqual(runs, [name for name, _ in safe_push.MODEL_JOB] + CI_ONLY_MODEL)
        runs = [line.strip() for step in jobs["negative"]["steps"][1:]
                for line in step.get("run", "").splitlines() if line.strip()
                and not step.get("uses") and "elan" not in line]
        self.assertEqual(runs, [name.removeprefix("negative: ")
                                for name, _ in safe_push.NEGATIVE])
        return entries

    def test_check_sequence_matches_workflow_and_ci(self):
        self.assertSequenceAgrees(SOURCE)
        # safe_push's own lists, each pinned to a list of the test's own: CHECKS, the
        # `check` job's sequence that stands in while origin/main holds no registry, the
        # sequence every train was judged by before the registry came (never the registry,
        # which grows without it; a follow-up card removes it); MODEL_JOB; and NEGATIVE.
        py = safe_push.PY
        self.assertEqual(safe_push.CHECKS, [
            ("lake build", ["lake", "build"]),
            ("lake build Audit", ["lake", "build", "Audit"]),
            ("lake build Staging", ["lake", "build", "Staging"]),
            ("lake env lean Certificate/Facts.lean",
             ["lake", "env", "lean", "Certificate/Facts.lean"]),
            ("python3 -I tests/test_certificate.py", [py, "-I", "tests/test_certificate.py"]),
            ("python3 scripts/sweep_citations.py --self-test",
             [py, "scripts/sweep_citations.py", "--self-test"]),
            ("python3 scripts/sweep_citations.py", [py, "scripts/sweep_citations.py"]),
            ("python3 scripts/check_kernel.py --self-test",
             [py, "scripts/check_kernel.py", "--self-test"]),
            ("python3 scripts/heath.py", [py, "scripts/heath.py"]),
            ("python3 scripts/check_fidelity.py", [py, "scripts/check_fidelity.py"]),
            ("python3 -I tests/test_check_style.py", [py, "-I", "tests/test_check_style.py"]),
            ("python3 -I tests/test_release_gate.py",
             [py, "-I", "tests/test_release_gate.py"]),
            ("python3 -I tests/test_jev_models.py", [py, "-I", "tests/test_jev_models.py"]),
            ("python3 scripts/audit/jev.py self-test",
             [py, "scripts/audit/jev.py", "self-test"]),
            ("python3 -I tests/test_screen.py", [py, "-I", "tests/test_screen.py"]),
            ("python3 -I tests/test_acceptance_limits.py",
             [py, "-I", "tests/test_acceptance_limits.py"]),
            ("python3 -I tests/test_check_superposition_pins.py",
             [py, "-I", "tests/test_check_superposition_pins.py"]),
            ("python3 -I scripts/check_superposition_pins.py",
             [py, "-I", "scripts/check_superposition_pins.py"]),
            ("python3 scripts/check_style.py", [py, "scripts/check_style.py"]),
            ("python3 scripts/render.py", [py, "scripts/render.py"]),
            ("git status --porcelain is empty", None),
            ("python3 scripts/check_queue.py --tree .",
             [py, "scripts/check_queue.py", "--tree", "."]),
            ("python3 scripts/check_links.py", [py, "scripts/check_links.py"])])
        self.assertEqual(safe_push.MODEL_JOB, [
            ("python3 -I tests/model/run.py --fast",
             [py, "-I", "tests/model/run.py", "--fast"])])
        self.assertEqual(safe_push.NEGATIVE, [
            ("negative: lake build", ["lake", "build"]),
            ("negative: lake env lean Certificate/Facts.lean",
             ["lake", "env", "lean", "Certificate/Facts.lean"]),
            ("negative: python3 scripts/negative_tests.py",
             [py, "scripts/negative_tests.py"])])

    def test_a_check_added_needs_no_change_to_safe_push(self):
        # The review's probe (#229): a copy of the tree with one file more in checks/ and
        # section 8's block rendered from it agrees as this tree does, with safe_push.py
        # as it is: adding a check is the file and its render, and the built-in CHECKS
        # neither holds the check nor needs to.
        import render
        root = Path(tempfile.mkdtemp(prefix="one-check-more-", dir=TMP))
        shutil.copytree(SOURCE / "checks", root / "checks",
                        ignore=shutil.ignore_patterns(".DS_Store"))
        for path in ("docs/WORKFLOW.md", ".github/workflows/ci.yml"):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / path, root / path)
        before = registry.load(root)
        added = ["python3", "-I", "tests/test_one_check_more.py"]
        (root / "checks" / "99-one-check-more.toml").write_text(
            "# An example check, for the test.\n"
            + registry_entry(max(e.order for e in before) + 10, added))
        page = root / "docs/WORKFLOW.md"
        page.write_text(render.workflow_page(page.read_text(), registry.load(root)))
        entries = self.assertSequenceAgrees(root)
        self.assertEqual([e.name for e in entries], [e.name for e in before] + [" ".join(added)])
        self.assertIn(f"\n{' '.join(added)}\n```\n<!-- /checks -->", page.read_text())
        self.assertNotIn(" ".join(added), [name for name, _ in safe_push.CHECKS])

    def test_the_generated_region_is_the_registrys(self):
        # safe_push's guards read section 8's block as generated (GENERATED_REGIONS), the
        # region render.py writes between registry.py's markers, and nothing else.
        workflow = (SOURCE / "docs/WORKFLOW.md").read_text()
        self.assertIn("docs/WORKFLOW.md", safe_push.GENERATED)
        pattern = safe_push.GENERATED_REGIONS["docs/WORKFLOW.md"]
        self.assertEqual([m.group(0) for m in pattern.finditer(workflow)],
                         [m.group(0) for m in registry.MARKERS.finditer(workflow)])
        # A block changed between the markers changes no hand-written part of the page.
        changed = registry.MARKERS.sub(lambda m: m.group(1) + "```sh\nlake build\n```\n"
                                       + m.group(3), workflow)
        self.assertNotEqual(changed, workflow)
        self.assertEqual(pattern.sub("", changed), pattern.sub("", workflow))

    def test_suite_jobs_are_the_workflows_own(self):
        # The release's gate (suite_gate, #301) names the jobs a run of the safe-push-tests
        # workflow must show passed: every job of the workflow but `report`, which needs
        # them all, and the shards (#233), which `safe-push-tests` needs, and which the
        # gate, like any job it does not name, holds to have passed. GitHub names a job with
        # no name and no matrix by its id, as the gate reads it; a workflow that renames or
        # splits one of the jobs SUITE_JOBS names, or adds a job the gate must name, changes
        # SUITE_JOBS too.
        workflow = yaml.safe_load((SOURCE / safe_push.SUITE_PATH).read_text())
        jobs = workflow["jobs"]
        self.assertEqual(set(jobs), {*safe_push.SUITE_JOBS, safe_push.SUITE_REPORT_JOB,
                                     SHARD_JOB})
        for name, job in jobs.items():
            self.assertNotIn("name", job, name)
            self.assertEqual("strategy" in job, name == SHARD_JOB, name)
        self.assertEqual(jobs["safe-push-tests"]["needs"], SHARD_JOB)
        self.assertEqual(jobs[safe_push.SUITE_REPORT_JOB]["needs"], list(safe_push.SUITE_JOBS))
        # The green run of the stand-in for gh: the jobs the gate names, the report, and one
        # job for each shard of the matrix, named as GitHub names them.
        shards = [f"{SHARD_JOB} ({k})" for k in range(1, ci_shard_count(jobs) + 1)]
        self.assertEqual([j["name"] for j in SUITE_JOBS if j["name"] not in shards],
                         [*safe_push.SUITE_JOBS, safe_push.SUITE_REPORT_JOB])
        self.assertEqual([j["name"] for j in SUITE_JOBS if j["name"].startswith(SHARD_JOB)],
                         shards)

    # E2a (#276): a job whose step `lane` reads the change's class does its work only when
    # that step says to run in full, so every step after it carries this condition (#346).
    LANE_CONDITION = "steps.lane.outputs.full == 'true'"

    def ungated_after_lane(self, workflow: dict) -> dict[str, list[str]]:
        """Each job with a step `lane`: the steps that would run for R0 to R2, by name,
        action or position. That is each step before the lane step, which must come
        first, and each step after it whose `if:` is not LANE_CONDITION, alone or as
        ${{ LANE_CONDITION }}."""
        found = {}
        for job_id, job in (workflow.get("jobs") or {}).items():
            steps = job.get("steps") or []
            lane = [i for i, step in enumerate(steps) if step.get("id") == "lane"]
            if not lane:
                continue
            def label(step, i):
                return step.get("name") or step.get("uses") or f"step {i}"
            ungated = [f"{label(step, i)} (before the lane step)"
                       for i, step in enumerate(steps[:lane[0]], 1)]
            for i, step in enumerate(steps[lane[0] + 1:], lane[0] + 2):
                condition = str(step.get("if", "")).strip()
                if condition.startswith("${{") and condition.endswith("}}"):
                    condition = condition[3:-2].strip()
                if condition != self.LANE_CONDITION:
                    ungated.append(label(step, i))
            found[job_id] = ungated
        return found

    def test_every_step_after_the_lane_step_carries_its_condition(self):
        # #339 added steps to CI's negative job without the condition, and every R0 to R2
        # pull request then failed once it had landed. Now this test finds such a step: on
        # any branch in seconds (Units), and on main within six hours, on the cadence that
        # runs this suite. (It fails the pull request that adds the step only once it runs
        # on the pull request's path, #346.) Every workflow is read; CI's negative and
        # formal-model jobs must have the lane step, first.
        workflows = {path.name: yaml.safe_load(path.read_text())
                     for path in sorted((SOURCE / ".github/workflows").glob("*.y*ml"))}
        for name, workflow in workflows.items():
            for job_id, ungated in self.ungated_after_lane(workflow).items():
                self.assertEqual(ungated, [], f"{name}: job {job_id}: the lane step comes "
                                 f"first, and each step after it needs if: "
                                 f"{self.LANE_CONDITION}")
        ci = self.ungated_after_lane(workflows["ci.yml"])
        self.assertTrue({"negative", "formal-model"} <= set(ci), sorted(ci))
        # Planted: the condition taken from one step of each job, or changed, is found.
        for job_id in ("negative", "formal-model"):
            for change in ("removed", "always()", "steps.lane.outputs.full == 'false'"):
                with self.subTest(job=job_id, change=change):
                    planted = copy.deepcopy(workflows["ci.yml"])
                    steps = planted["jobs"][job_id]["steps"]
                    victim = steps[-1]
                    if change == "removed":
                        del victim["if"]
                    else:
                        victim["if"] = change
                    self.assertEqual(self.ungated_after_lane(planted)[job_id],
                                     [victim.get("name") or victim.get("uses")])
        wrapped = copy.deepcopy(workflows["ci.yml"])
        for step in wrapped["jobs"]["negative"]["steps"][1:]:
            step["if"] = "${{ " + self.LANE_CONDITION + " }}"
        self.assertEqual(self.ungated_after_lane(wrapped)["negative"], [])
        # A step put before the lane step runs for every class, as #339's did.
        early = copy.deepcopy(workflows["ci.yml"])
        early["jobs"]["negative"]["steps"].insert(0, {"name": "Too early", "run": "true"})
        self.assertEqual(self.ungated_after_lane(early)["negative"],
                         ["Too early (before the lane step)"])
        # A step with no name is named by its action, and one with neither by its place.
        unnamed = copy.deepcopy(workflows["ci.yml"])
        steps = unnamed["jobs"]["negative"]["steps"]
        steps += [{"uses": "actions/an-action@v1"}, {"run": "true"}]
        self.assertEqual(self.ungated_after_lane(unnamed)["negative"],
                         ["actions/an-action@v1", f"step {len(steps)}"])

    def test_ci_check_job_rejects_skip_and_failure_suppression(self):
        # The run of the registry's checks is the job's one step after its setup (#229):
        # the cases that held each check's step now hold that one.
        source = (SOURCE / ".github/workflows/ci.yml").read_text()
        certificate = RUN_CHECKS
        cases = (
            ("job if", "job", "if", False, "check job has an if condition"),
            ("step if", "step", "if", False, "has an if condition"),
            ("job continue", "job", "continue-on-error", True,
             "check job can continue on error"),
            ("step continue", "step", "continue-on-error", True,
             "can continue on error"),
            ("job dependency", "job", "needs", "acceptance", "has dependencies"),
            ("workflow shell", "workflow", "defaults", {"run": {"shell": "bash {0}"}},
             "default shell override"),
            ("job shell", "job", "defaults", {"run": {"shell": "bash {0}"}},
             "default shell override"),
            ("step shell", "step", "shell", "bash {0}", "has a shell override"),
            ("workflow working directory", "workflow", "defaults",
             {"run": {"working-directory": "bypass"}}, "default working directory"),
            ("job working directory", "job", "defaults",
             {"run": {"working-directory": "bypass"}}, "default working directory"),
            ("step working directory", "step", "working-directory", "bypass",
             "has a working directory"),
            ("wrapped run", "step", "run", f"set +e\n{certificate}\nexit 0",
             "unsupported run body"),
            ("run followed by another command", "step", "run",
             f"{certificate}\n{RENDER_COMMAND}", "unsupported run body"),
            ("failure suppressed on the line", "step", "run", f"{certificate} || true",
             "neither the run of the registry's checks"),
            ("another job's checks", "step", "run", "python3 scripts/run_checks.py --job model",
             "neither the run of the registry's checks"),
            ("one check in its place", "step", "run", "python3 -I tests/test_certificate.py",
             "neither the run of the registry's checks"),
        )
        for label, scope, field, value, message in cases:
            with self.subTest(label=label):
                workflow = yaml.safe_load(source)
                job = workflow["jobs"]["check"]
                target = workflow if scope == "workflow" else job if scope == "job" else next(
                    step for step in job["steps"] if step.get("run") == certificate)
                target[field] = value
                changed = yaml.safe_dump(workflow, sort_keys=False)
                with self.assertRaisesRegex(AssertionError, message):
                    enforced_check_commands(normalized_check_job(changed))
        # The freshness check the render step held is the registry's now: an entry with
        # `empty`, of the whole worktree (test_check_sequence_matches_workflow_and_ci), and
        # no narrower `git status` can stand for it, since such an entry would have a
        # command, and `empty` and `command` exclude each other (Registry).

    def test_ci_check_job_rejects_unmodeled_setup_and_environment(self):
        source = (SOURCE / ".github/workflows/ci.yml").read_text()
        certificate = RUN_CHECKS
        stub = {"name": "Prepare the shell", "run": (
            "printf 'python3() { return 0; }\\n' > \"$RUNNER_TEMP/stub.sh\"\n"
            "echo \"BASH_ENV=$RUNNER_TEMP/stub.sh\" >> \"$GITHUB_ENV\"\n")}
        override = {"BASH_ENV": "stub.sh"}
        unmodeled = "neither the run of the registry's checks nor the modelled setup"

        def step_running(job, command):
            return next(step for step in job["steps"] if step.get("run") == command)

        def step_using(job, action):
            return next(step for step in job["steps"] if step.get("uses") == action)

        def before_certificate(step):
            def insert(workflow, job):
                job["steps"].insert(job["steps"].index(step_running(job, certificate)), step)
            return insert

        def after_the_run(step):
            def insert(workflow, job):
                job["steps"].insert(job["steps"].index(step_running(job, certificate)) + 1,
                                    step)
            return insert

        def reverse_setup_actions(workflow, job):
            job["steps"][:2] = reversed(job["steps"][:2])

        cases = (
            ("BASH_ENV through GITHUB_ENV", before_certificate(stub), unmodeled),
            ("unlisted action", before_certificate({"uses": "example/setup-shell@v1"}),
             unmodeled),
            ("checkout after the run", after_the_run({"uses": "actions/checkout@v5"}),
             "setup after the first check"),
            ("Python setup after the run",
             after_the_run({"uses": "actions/setup-python@v5",
                            "with": {"python-version": "3.12"}}),
             "setup after the first check"),
            ("a check of its own after the run",
             after_the_run({"name": "One more", "run": "python3 scripts/check_links.py"}),
             unmodeled),
            ("a check of its own before the run",
             before_certificate({"name": "One more", "run": RENDER_COMMAND}), unmodeled),
            ("the run twice", after_the_run({"name": "Again", "run": RUN_CHECKS}),
             "exactly once"),
            ("no run", lambda workflow, job: job["steps"].remove(step_running(job, certificate)),
             "exactly once"),
            ("duplicate checkout",
             lambda workflow, job: job["steps"].insert(1, job["steps"][0].copy()),
             "setup sequence differs"),
            ("duplicate Python setup",
             lambda workflow, job: job["steps"].insert(2, job["steps"][1].copy()),
             "setup sequence differs"),
            ("reversed setup actions", reverse_setup_actions, "setup sequence differs"),
            ("missing checkout", lambda workflow, job: job["steps"].pop(0),
             "setup sequence differs"),
            ("missing elan install", lambda workflow, job: job["steps"].pop(2),
             "setup prefix is incomplete"),
            ("checkout of another ref",
             lambda workflow, job: step_using(job, "actions/checkout@v5").update(
                 {"with": {"ref": "other"}}), unmodeled),
            ("checkout of another ref, keeping no token",
             lambda workflow, job: step_using(job, "actions/checkout@v5").update(
                 {"with": {"persist-credentials": False, "ref": "other"}}), unmodeled),
            ("checkout keeping its token",
             lambda workflow, job: step_using(job, "actions/checkout@v5").update(
                 {"with": {"persist-credentials": True}}), unmodeled),
            ("checkout's token setting as a string",
             lambda workflow, job: step_using(job, "actions/checkout@v5").update(
                 {"with": {"persist-credentials": "false"}}), unmodeled),
            ("checkout's token setting as a number",
             lambda workflow, job: step_using(job, "actions/checkout@v5").update(
                 {"with": {"persist-credentials": 0}}), unmodeled),
            ("workflow environment", lambda workflow, job: workflow.update(env=override),
             "check job has an environment override"),
            ("job environment", lambda workflow, job: job.update(env=override),
             "check job has an environment override"),
            ("run step environment",
             lambda workflow, job: step_running(job, certificate).update(env=override),
             "has an environment override"),
            ("setup step environment",
             lambda workflow, job: step_using(job, "actions/setup-python@v5").update(
                 env=override), "has an environment override"),
            ("job container", lambda workflow, job: job.update(container="example/stub"),
             "unmodeled settings"),
        )
        for label, mutate, message in cases:
            with self.subTest(label=label):
                workflow = yaml.safe_load(source)
                mutate(workflow, workflow["jobs"]["check"])
                changed = yaml.safe_dump(workflow, sort_keys=False)
                with self.assertRaisesRegex(AssertionError, message):
                    enforced_check_commands(normalized_check_job(changed))

    def test_ci_check_job_accepts_equivalent_yaml_formatting(self):
        source = (SOURCE / ".github/workflows/ci.yml").read_text()
        expected = normalized_check_job(source)
        equivalent = yaml.safe_dump(yaml.safe_load(source), default_flow_style=True,
                                    sort_keys=True, width=1_000_000)
        self.assertEqual(normalized_check_job(equivalent), expected)
        self.assertEqual(enforced_check_commands(normalized_check_job(equivalent)),
                         enforced_check_commands(expected))

        workflow = yaml.safe_load(source)
        job = workflow["jobs"]["check"]
        step = next(step for step in job["steps"] if step.get("run") == RUN_CHECKS)
        job["continue-on-error"] = False
        step["continue-on-error"] = False
        enforced_check_commands(normalized_check_job(yaml.safe_dump(workflow)))

        workflow = yaml.safe_load(source)
        formal_model = workflow["jobs"]["formal-model"]
        self.assertIn("model", {step.get("working-directory") for step in formal_model["steps"]})
        formal_model["defaults"] = {"run": {"working-directory": "model"}}
        enforced_check_commands(normalized_check_job(yaml.safe_dump(workflow)))

        # A checkout that keeps its token, as before persist-credentials, checks the same.
        workflow = yaml.safe_load(source)
        next(step for step in workflow["jobs"]["check"]["steps"]
             if step.get("uses") == "actions/checkout@v5").pop("with")
        self.assertEqual(enforced_check_commands(normalized_check_job(yaml.safe_dump(workflow))),
                         [RUN_CHECKS])

    def test_every_checkout_keeps_no_token(self):
        # CI's jobs and the post-merge workflow's run with a read-only token; none leaves
        # it in the checkout's git config, where the code checked could read it.
        for name in ("ci.yml", "post-merge.yml"):
            workflow = yaml.safe_load((SOURCE / ".github/workflows" / name).read_text())
            checkouts = [(job, step) for job, spec in workflow["jobs"].items()
                         for step in spec.get("steps", [])
                         if str(step.get("uses", "")).startswith("actions/checkout@")]
            self.assertTrue(checkouts, name)
            for job, step in checkouts:
                with self.subTest(workflow=name, job=job):
                    self.assertIs(step.get("with", {}).get("persist-credentials"), False)

    def flagged(self, line: str) -> list[str]:
        return [f.rule for f in safe_push.scan_text("x", 1, line)]

    def test_secrets_flagged(self):
        hexkey = hashlib.sha256(b"x").hexdigest()
        for line in (f"api_token = \"{TOKEN}\"", f'"client_secret": "{TOKEN}"',
                     f"export GITHUB_TOKEN={hexkey}", KEY_HEADER,
                     "gh" + "p_" + "a1B2" * 9, "sk" + "-" + "proj" + "Ab3dE" * 5,
                     "xo" + "xb-" + "1234-5678-abcdef", "AK" + "IA" + "ABCDEFGH23456789",
                     "Authori" + "zation: Bearer abcdefgh12345678", f"see {PRIVATE_DIR}",
                     "C:" + "\\" + "Users" + "\\someone", "secret" + "s2026/thing",
                     f"cd {SCRATCHPAD}", f"projects/{FOLDED_HOME}/memory",
                     "/tmp/" + "claude" + "-1000/x"):
            self.assertTrue(self.flagged(line), line)

    def test_ordinary_lines_pass(self):
        for line in ('lean = "sha256:061379c1f0411141"', "    key = prop_key(ref)",
                     "the key step is I.5, which Heath does not bracket",
                     "token: docs/reports/crew/voice-02.md",
                     "Authori" + "zation: Bearer ${{ secrets.GITHUB_TOKEN }}",
                     "obtain ⟨L, hA_L, hB_L⟩ := Postulate1 A B (ne_of_between_ends hADB)",
                     "the secret of the construction lies in Postulate 3",
                     "the non-Users-facing part", "a /tmp/build directory"):
            self.assertEqual(self.flagged(line), [], line)
        lean = (SOURCE / "Elements" / "BookIII" / "Prop16.lean").read_text()
        self.assertEqual([f for i, l in enumerate(lean.splitlines())
                          for f in safe_push.scan_text("Prop16.lean", i, l)], [])

    def test_across_lines_encoded_and_linked(self):
        def across(*lines):
            return [f.rule for f in safe_push.scan_block("x", list(enumerate(lines, 1)))]
        self.assertTrue(across("api_token =", f'    "{TOKEN}"'))
        self.assertTrue(across(f'key = "{HEXKEY[:16]}"', f'      "{HEXKEY[16:]}"'))
        self.assertEqual(across(f"api_token = \"{TOKEN}\"", "the next line"),
                         ["key, token or secret"], "flagged once, not again across lines")
        encoded = base64.b64encode(GH_TOKEN.encode()).decode()
        self.assertEqual([f.rule for f in safe_push.scan_text("x", 1, f"v: {encoded}")],
                         ["base64-encoded GitHub token"])
        for target, out in (("../README.md", False), ("sub/file", False), ("/etc/hosts", True),
                            (TILDE_DOWNLOADS, True), ("../../up", True), ("C:\\x", True)):
            self.assertEqual(bool(safe_push.scan_link("docs/link", target)), out, target)

    def test_ordinary_files_pass_read_across_lines(self):
        # Whole files of the repository, every line as if added: nothing is flagged,
        # this harness, its tests, its hook and the template included; and the images,
        # read as binaries.
        for path in ("Elements/BookIII/Prop16.lean", "docs/WORKFLOW.md", "facts.json",
                     "docs/briefs/0002-decisions.md", "review/III/16.toml",
                     "scripts/safe_push.py", "scripts/test_safe_push.py",
                     "scripts/hooks/pre-push", "figures/I/01-idea.svg", "AGENTS.md",
                     "docs/FORMALIZATION.md", "docs/PROGRAM.md",
                     ".github/pull_request_template.md"):
            numbered = list(enumerate((SOURCE / path).read_text().splitlines(), 1))
            self.assertEqual([f.shown() for f in safe_push.scan_block(path, numbered)], [],
                             path)
        for path in sorted((SOURCE / "assets").glob("*.png")):
            self.assertEqual([f.shown() for f in safe_push.scan_binary(path.name,
                                                                        path.read_bytes())],
                             [], path)

    def test_allow_list_pins_the_value(self):
        (f,) = safe_push.scan_text("docs/x.md", 3, f"example_token: {HEXKEY}")
        other = hashlib.sha256(b"another").hexdigest()
        (g,) = safe_push.scan_text("docs/x.md", 4, f"example_token: {other}")

        def entry(match, digest=None):
            return [safe_push.Allow("docs/x.md", match, "key, token or secret", "A fixture.",
                                    digest)]
        self.assertIsNone(safe_push.allowed(f, entry("example_token:")))
        self.assertTrue(safe_push.allowed(f, entry(f"example_token: {HEXKEY}")))
        self.assertIsNone(safe_push.allowed(g, entry(f"example_token: {HEXKEY}")))
        pinned = entry("example_token:", hashlib.sha256(HEXKEY.encode()).hexdigest())
        self.assertTrue(safe_push.allowed(f, pinned))
        self.assertIsNone(safe_push.allowed(g, pinned))
        # A commit message is never allowed, whatever the entry says.
        message = f._replace(path="commit 0123456789ab message")
        self.assertIsNone(safe_push.allowed(message, [safe_push.Allow(
            message.path, f"example_token: {HEXKEY}", "key, token or secret", "x", None)]))

    def test_private_path_flagged_whole(self):
        # Security review (low): an entry pins one private path, not every one on its line.
        other = "/" + "Users" + "/another/notes.txt"
        found = safe_push.scan_text("docs/x.md", 1, f"See ({PRIVATE_DIR}) and \"{other}\".")
        self.assertEqual(sorted(safe_push.flagged_value(f) for f in found),
                         sorted([PRIVATE_DIR, other]))
        first = next(f for f in found if safe_push.flagged_value(f) == PRIVATE_DIR)
        entry = [safe_push.Allow("docs/x.md", "See (", "private path", "A fixture.",
                                 safe_push.value_sha256(first))]
        self.assertEqual([safe_push.allowed(f, entry) is not None for f in found],
                         [safe_push.flagged_value(f) == PRIVATE_DIR for f in found])

    def test_private_path_does_not_hide_a_key_on_the_next_lines(self):
        # Security review of the fixes: a private path, flagged whole, runs on into the
        # next lines when they are read as one; the key across those lines is still found.
        lines = [(1, "/" + "Users" + "/someone/" + "a" * 45), (2, "api_key"), (3, f'= "{TOKEN}"')]
        found = safe_push.scan_block("docs/x.md", lines)
        self.assertTrue([f for f in found if f.rule == "key, token or secret"
                         and TOKEN in safe_push.flagged_value(f)], found)

    def test_private_paths_end_at_colons_and_equals(self):
        a, b = "/" + "Users" + "/someone/a", "/" + "Users" + "/someone/b"
        found = safe_push.scan_text("docs/x.md", 1, f"PATH={a}:{b}")
        self.assertEqual(sorted(safe_push.flagged_value(f) for f in found), [a, b])

    def test_sections(self):
        template = (SOURCE / ".github" / "pull_request_template.md").read_text()
        self.assertEqual(len(safe_push.section_problems(template, template, False)), 4)
        self.assertEqual(len(safe_push.section_problems(template, template, True)), 5)
        # Unfinished work is now judged separately, against the raw text.
        text, problems = safe_push.unfinished_section(template)
        self.assertEqual(problems, [])
        self.assertTrue(safe_push.unfinished_refs(text)[1])
        self.assertEqual(safe_push.section_problems(ticked(template), template, True), [])
        # safe_push's own lines are not the coordinator's words.
        body = template.replace("<!-- safe_push: commits -->", "<!-- safe_push:commits begin "
                                "-->\nCommits:\n\n- `abc1234` A commit\n<!-- safe_push:commits "
                                "end -->")
        self.assertIn('not written: the section "What and why"',
                      safe_push.section_problems(body, template, False))
        self.assertEqual(safe_push.section_problems(ticked(template), None, False), [])
        # A fenced block of filled-in headings at the end does not write the sections.
        fenced = template + "\n```\n" + ticked(template) + "\n```\n"
        self.assertEqual(len(safe_push.section_problems(fenced, template, False)), 4)
        self.assertTrue(safe_push.unfinished_section(fenced)[1])
        # Backticked review names are read; a dash holds a place.
        rows = ticked(template).replace("| /code-review |", "| `/code-review` |")
        self.assertEqual(safe_push.section_problems(rows, template, False), [])
        dash = ticked(template).replace("| /no-mistakes | abc1234 | None. |",
                                        "| /no-mistakes | - | - |")
        self.assertEqual(safe_push.section_problems(dash, template, False),
                         ["not written: the review /no-mistakes, its commit and its findings"])

    def test_binary_findings_carry_a_window(self):
        data = b"A" * 500 + b"\0" + GH_TOKEN.encode() + b"\0" + b"B" * 500
        found = [f for f in safe_push.scan_binary("x.bin", data) if f.rule == "GitHub token"]
        self.assertTrue(found)
        for f in found:
            self.assertLessEqual(len(f.text), len(GH_TOKEN) + 2 * safe_push.WINDOW)
            self.assertEqual(safe_push.flagged_value(f), GH_TOKEN)
            self.assertNotIn(GH_TOKEN, f.shown())

    def test_secret_files(self):
        for path in (".env", "deploy/.env.local", "keys/server.key", "a/b.pem", "id_ed25519"):
            self.assertTrue(safe_push.scan_path(path), path)
        for path in ("docs/env.md", "scripts/check_style.py", "Certificate/axioms.lock"):
            self.assertEqual(safe_push.scan_path(path), [], path)

    def test_names_ref(self):
        names = safe_push.names_ref
        self.assertTrue(names("III.16 keeps its statement", "III.16"))
        self.assertTrue(names("Heath's III. 16", "III.16"))
        self.assertTrue(names("`BookIII.Prop16` changes", "III.16 Por."))
        self.assertFalse(names("III.16 changes", "III.1"))
        self.assertFalse(names("III.1 changes", "I.1"))
        self.assertFalse(names("BookIII.Prop10 changes", "III.1"))

    def test_without_replacements(self):
        # Issue #256: the folder of replacements dropped, and the variable set to "1",
        # whatever the caller set it to; the rest of the environment kept.
        env = safe_push.without_replacements({"GIT_REPLACE_REF_BASE": "refs/stand-ins/",
                                              "GIT_NO_REPLACE_OBJECTS": "0", "HOME": "/home"})
        self.assertEqual(env, {"GIT_NO_REPLACE_OBJECTS": "1", "HOME": "/home"})

    def test_run_pins_replacements_off_for_git_alone(self):
        # run() gives a git command core.useReplaceRefs=false on its command line, right
        # after the program, and an environment without replacements; another program is
        # run as given, in the caller's environment less the variables that tie git to one
        # repository, but GIT_NO_REPLACE_OBJECTS (#357). Nothing is spawned.
        caller = {"GIT_DIR": "/a-hooks-git-dir", "GIT_NO_REPLACE_OBJECTS": "kept-as-given"}
        with mock.patch.dict(os.environ, caller), \
                mock.patch.object(safe_push.subprocess, "run") as spawn:
            safe_push.run(["git", "status"], "/nowhere", env={"HOME": "/home"})
            safe_push.run([sys.executable, "-c", "pass"], "/nowhere")
            expected = {name: value for name, value in os.environ.items()
                        if name not in safe_push.REPOSITORY_VARIABLES
                        or name in safe_push.KEPT_GIT_VARIABLES}
        git_call, other_call = spawn.call_args_list
        self.assertEqual(git_call.args[0], ["git", "-c", "core.useReplaceRefs=false", "status"])
        self.assertEqual(git_call.kwargs["env"],
                         {"HOME": "/home", "GIT_NO_REPLACE_OBJECTS": "1"})
        self.assertEqual(other_call.args[0], [sys.executable, "-c", "pass"])
        self.assertNotIn("GIT_DIR", other_call.kwargs["env"])
        self.assertEqual(other_call.kwargs["env"], expected)
        self.assertEqual(other_call.kwargs["env"]["GIT_NO_REPLACE_OBJECTS"], "kept-as-given")

    def test_source_statement(self):
        src = (SOURCE / "Elements" / "BookIII" / "Prop01.lean").read_text()
        main = safe_push.source_statement(src, 1, None)
        porism = safe_push.source_statement(src, 1, "porism")
        self.assertTrue(main.startswith("{A B : Point} {ABC : Circle}"), main)
        self.assertTrue(porism.startswith("{A B C D G : Point}"), porism)
        self.assertNotIn(":=", main + porism)

    def test_gates_read_what_github_shows(self):
        # The final review: a box or a heading GitHub does not show (in a comment, or in
        # code by CommonMark's rules) counts for neither gate.
        template = (SOURCE / ".github" / "pull_request_template.md").read_text()
        full = ticked(template)

        def both(body):
            return (safe_push.checklist_problems(body, template, True),
                    safe_push.section_problems(body, template, True))
        self.assertEqual(both(full), ([], []))
        head, _, checklist = full.partition("## Checklist\n")
        hidden = {
            "the checklist in a comment": head + "## Checklist\n\n<!--\n" + checklist + "\n-->\n",
            "a comment never closed": head + "## Checklist\n\n<!--\n" + checklist,
            "a fence never closed": "```\n" + full,
            "a fence of four holding three": "````\n```\n" + full + "\n````\n",
            "a tilde fence closed by backticks": "~~~\n" + full + "\n```\n",
            "a fence closed with an info string": "```\n" + full + "\n```text\n",
            "indented code": head + "## Checklist\n\n"
                             + "\n".join("    " + line for line in checklist.splitlines()),
        }
        for name, body in hidden.items():
            with self.subTest(name):
                boxes, written = both(body)
                self.assertTrue(boxes, name)
                if name not in ("the checklist in a comment", "a comment never closed",
                                "indented code"):
                    self.assertTrue(written, name)
        # What GitHub does show still counts: a fence of four holding three, inside "What
        # and why", closed; boxes nested in a list item, indented four.
        shown = full.replace("A change for the test.\n",
                             "A change for the test.\n\n````\n```\nx\n```\n````\n", 1)
        self.assertEqual(both(shown), ([], []))
        nested = full.replace("## Checklist\n\n", "## Checklist\n\n- The boxes:\n\n", 1) \
            .replace("- [x] **Required", "    - [x] **Required")
        self.assertEqual(both(nested)[0], [])

    def test_gates_read_comments_and_code_spans_as_github_does(self):
        # The re-review: "<!--" in a code span or a fenced block is text, as GitHub shows
        # it, and hides nothing. A comment that starts a line still hides the rest when it
        # is never closed; one opened mid-line and closed within its paragraph is dropped,
        # and one never closed there is text.
        template = (SOURCE / ".github" / "pull_request_template.md").read_text()
        full = ticked(template)

        def swap(old, new):
            self.assertEqual(full.count(old), 1, old)
            return full.replace(old, new)

        def both(body):
            return (safe_push.checklist_problems(body, template, True),
                    safe_push.section_problems(body, template, True))
        why, ok = "A change for the test.\n", '"Nothing". -->\n'
        cell = "| /no-mistakes | abc1234 | None. |"
        shown = {
            "an opener and a closer in a cell's code spans": swap(
                cell, "| /no-mistakes | abc1234 | `<!--` then `-->` |"),
            "an escaped comment in a cell": swap(
                cell, "| /no-mistakes | abc1234 | \\<!-- shown as it is --> |"),
            "a code span in Needs the owner's OK": swap(
                ok, ok + "\nThis only changes how `<!--` is read.\n"),
            "an opener mid-line in Needs the owner's OK": swap(
                ok, ok + "\nThis only changes how <!-- is read.\n"),
            "a code span in the /code-review cell": swap(
                "| /code-review | abc1234 | None. |",
                "| /code-review | abc1234 | fixed: an unclosed `<!--` in code hid the rest |"),
            "a fenced block before the checklist": swap(
                "## Checklist\n", "```html\n<!-- an opener\n```\n\n## Checklist\n"),
            "an opener and a closer in two code spans": swap(
                why, "A change: `<!--` opens a comment, and `-->` closes it.\n"),
            "a code span of two backticks": swap(why, "A change to `` `<!--` `` spans.\n"),
            "an opener mid-line, never closed": swap(why, "A change: strips each <!-- note.\n"),
            "an escaped opener": swap(why, "A change to \\<!-- notes.\n"),
        }
        for name, body in shown.items():
            with self.subTest(name):
                self.assertEqual(both(body), ([], []))
        hidden = swap("## Checklist\n", "<!-- a note never closed\n\n## Checklist\n")
        self.assertEqual(len(both(hidden)[0]), 10, both(hidden))
        commented = swap(cell, "| /no-mistakes | abc1234 | <!-- x --> |")
        self.assertEqual(both(commented), ([], ["not written: the review /no-mistakes, its "
                                                "commit and its findings"]))
        across = swap(why, "A change <!-- begun here\nand ended here --> for the test.\n")
        self.assertEqual(safe_push.sections(across)["What and why"], "A change  for the test.")
        escaped = swap(why, "A change to \\<!-- these notes --> for the test.\n")
        self.assertIn("<!-- these notes -->", safe_push.sections(escaped)["What and why"])

    def test_a_box_counts_only_where_github_shows_one(self):
        # The no-mistakes review: a box counts only as a task-list item GitHub shows, a list
        # item indented three spaces at most at the top level, or nested in a list item by
        # its content column; never a paragraph's line, code or raw HTML.
        template = (SOURCE / ".github" / "pull_request_template.md").read_text()
        head, _, checklist = ticked(template).partition("## Checklist\n")
        boxes = [line for line in checklist.splitlines() if line.startswith("- [x]")]
        self.assertEqual(len(safe_push.boxes(ticked(template))), 10)

        def problems(lines, indent=""):
            body = head + "## Checklist\n\n" + lines + "\n".join(indent + b for b in boxes)
            return safe_push.checklist_problems(body + "\n", template, True)
        hidden = {
            "four spaces under a paragraph's line": ("See below.\n", "    "),
            "four past a list item's content": ("- The boxes:\n\n", "      "),
            "in a fence nested in a list item": ("- The boxes:\n\n    ```\n", "    "),
            "in a <pre> block": ("<pre>\n", ""),
            "in an HTML block": ("<details>\n", ""),
        }
        for name, (lines, indent) in hidden.items():
            with self.subTest(name):
                self.assertEqual(len(problems(lines, indent)), 10)
        shown = {
            "three spaces under a paragraph's line": ("See below.\n", "   "),
            "nested by its item's content column": ("1. The boxes:\n\n", "   "),
            "after a fence its list item ends": ("- A note:\n\n  ```\n  code\n", ""),
            "after an HTML block a blank line ends": ("<details>\n<summary>Boxes</summary>\n\n",
                                                      ""),
        }
        for name, (lines, indent) in shown.items():
            with self.subTest(name):
                self.assertEqual(problems(lines, indent), [])

    def test_markers_count_only_on_lines_of_their_own(self):
        # The re-review: safe_push writes its markers on lines of their own; one quoted in
        # the coordinator's words (in a code span) is not one. Refreshing the parts, placing
        # the summary and reading the body for the gates keep every word and section.
        template = (SOURCE / ".github" / "pull_request_template.md").read_text()
        names = ("commits", "statements", "records", "protected", "generated")

        def part(name, text):
            return f"<!-- safe_push:{name} begin -->\n{text}\n<!-- safe_push:{name} end -->"

        def block(text):
            return part("preflight", text).replace("preflight begin", "preflight begin "
                                                   "sha=a base=b", 1)

        def place(text, after, words):
            self.assertEqual(text.count(after), 1, after)
            return text.replace(after, f"{after}\n{words}\n", 1)
        why = ("Moves the records: safe_push writes them after "
               "`<!-- safe_push:records begin -->`, and its summary after "
               "`<!-- safe_push:preflight begin -->` (the template's "
               "`<!-- safe_push: preflight -->`).\n\nMore of the coordinator's reasoning.")
        approval = "I.1: the decisions entry of 18 October."
        words = place(place(template, "code it checks. -->\n", why),
                      'or "None". -->\n', approval)
        # A body file with the quotes: the summary goes to the template's place for it.
        filled = safe_push.put_block(words, block("OLD-summary"))
        self.assertIn(why, filled)
        self.assertGreater(filled.index("\n<!-- safe_push:preflight begin sha=a base=b -->\n"),
                           filled.index("## Checks run on the exact commit"))
        for name in names:
            filled = filled.replace(f"<!-- safe_push: {name} -->", part(name, f"OLD-{name}"))
        for body in (filled, filled.replace("\n", "\r\n")):
            with self.subTest(crlf="\r" in body):
                new = safe_push.put_block(
                    safe_push.refreshed(body, {n: part(n, f"NEW-{n}") for n in names}),
                    block("NEW-summary"))
                for text in (why, approval):
                    self.assertIn(text.replace("\n", "\r\n") if "\r" in body else text, new)
                self.assertEqual(re.findall(r"(?m)^## [^\r\n]*", new),
                                 re.findall(r"(?m)^## [^\r\n]*", body))
                for name in names + ("summary",):
                    self.assertIn(f"NEW-{name}", new)
                    self.assertNotIn(f"OLD-{name}", new)
                shown = safe_push.sections(body)
                self.assertIn("More of the coordinator's reasoning.", shown["What and why"])
                self.assertNotIn("OLD-", shown["What and why"])
                self.assertEqual(shown["Statements changed"], approval)

    def test_preflight_block_writes_the_home_directory_as_tilde(self):
        # A step-4 note names its log, under the home directory: the public body has ~.
        log = f"{Path.home()}/.cache/stoicheia/logs/x/18-git-status-is-empty.log"
        record = {"steps": [], "full": True,
                  "notes": [["git status --porcelain is empty (origin/main's checks)",
                             f"full output in {log}"]]}
        block = safe_push.preflight_block("a" * 40, "b" * 40, record)
        self.assertNotIn(str(Path.home()), block)
        self.assertIn("full output in ~/.cache/stoicheia/logs/x/", block)
        safe_push.check_body(block)

    def test_preflight_block_keeps_harness_distinct_and_reads_older_markers(self):
        sha, base, harness = (c * 40 for c in "abc")
        block = safe_push.preflight_block(sha, base, {"full": True, "harness_sha": harness})
        match = safe_push.BLOCK.fullmatch(block)
        self.assertIsNotNone(match)
        self.assertEqual(match.groups(), (sha, base, harness))
        self.assertIn("Verdict: PASS.", block)
        older = block.replace(f" harness={harness}", "")
        match = safe_push.BLOCK.fullmatch(older)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(3) or match.group(2), base)
        for previous in (block, older):
            self.assertEqual(safe_push.put_block(previous, block), block)

    def test_merge_train_input_refuses_unreadable_body(self):
        ctx = safe_push.Context(Path("."), "a" * 40, "b" * 40, 1, "", None, {},
                                branch="train/docs-1")
        for view in ({}, {"body": None}, {"body": []}, {"body": False}):
            with self.subTest(view=view):
                with self.assertRaisesRegex(safe_push.Refusal, "current pull request body"):
                    safe_push.merge_train_input(ctx, view)
        self.assertEqual(safe_push.merge_train_input(ctx, {"body": ""}), "")
        self.assertEqual(safe_push.merge_train_input(ctx, {"body": "Current body."}),
                         "Current body.")
        self.assertIsNone(safe_push.merge_train_input(ctx._replace(branch="docs/test"), {}))

    def test_main_red_fix_is_read_as_github_shows_the_body(self):
        read = safe_push.main_red_fix
        self.assertIsNone(read(""))
        self.assertIsNone(read("## What and why\n\nA change.\n"))
        self.assertEqual(read("A fix.\n\nFixes main-red: #12\n"), {12})
        self.assertEqual(read("Fixes main-red: #12, #15.\r\n"), {12, 15})
        # In a comment or in code, GitHub does not show it: no declaration.
        self.assertIsNone(read("<!-- Fixes main-red: #12 -->\n"))
        self.assertIsNone(read("```\nFixes main-red: #12\n```\n"))
        for body in ("Fixes main-red: 12\n", "Fixes main-red: #12 and #15\n",
                     "Fixes main-red: #12, #12\n", "Fixes main-red: #0\n",
                     "Fixes main-red: #12\n\nFixes main-red: #15\n", "Fixes main-red #12\n"):
            with self.subTest(body=body):
                with self.assertRaisesRegex(safe_push.Refusal, "unreadable main-red fix"):
                    read(body)

    def test_a_red_main_admits_only_the_fix_of_every_open_issue(self):
        def verdict(red, failed, body):
            rep = safe_push.Report()
            safe_push.red_or_fix(rep, red, failed, "detail", body)
            return [(s.name, s.outcome) for s in rep.steps]

        self.assertEqual(verdict([], None, ""), [("main health", "ok")])
        self.assertEqual(verdict([], None, "Fixes main-red: #12\n"), [("main health", "ok")])
        self.assertEqual(verdict([12], "post-merge run 1 failed", "Fixes main-red: #12\n"),
                         [("main health", "note")])
        self.assertEqual(verdict([12, 15], None, "Fixes main-red: #15, #12\n"),
                         [("main health", "note")])
        failed = "post-merge run 1 at abc concluded failure"
        cases = (([12], None, "", "Only its fix lands"),
                 ([12], failed, "A change.\n", "Only its fix lands"),
                 ([12, 15], None, "Fixes main-red: #12\n", "not every open main-red issue"),
                 ([12], None, "Fixes main-red: #12, #15\n", "not every open main-red issue"),
                 ([12], None, "Fixes main-red: #13\n", "not every open main-red issue"),
                 ([], failed, "Fixes main-red: #12\n", "no open main-red issue names it"))
        for red, failed_run, body, message in cases:
            with self.subTest(red=red, failed=failed_run, body=body):
                with self.assertRaisesRegex(safe_push.Refusal, message) as caught:
                    verdict(red, failed_run, body)
                self.assertIn("main is red", str(caught.exception))

    def test_block_current_holds_the_queue_judge_s_harness_rule(self):
        # Main's first-parent chain, newest first: a harness may be the block's base or a
        # later commit of the chain, never an older one, and never off the chain. The
        # head holds the block's base and what is older, not main's later commits.
        tip, later, base, older = "d" * 40, "c" * 40, "b" * 40, "a" * 40
        sha = "e" * 40
        ctx = safe_push.Context(Path("."), sha, base, 1, "", None, {}, branch="docs-1",
                                queue=True, harness_sha=tip)
        record = {"harness_sha": tip}

        def block(harness, train_row=False, at=base):
            return safe_push.BLOCK.search(
                f"<!-- safe_push:preflight begin sha={sha} base={at} harness={harness} -->\n"
                "Verdict: PASS.\n\n| Step | Outcome | Seconds |\n|---|---|---|\n"
                + ("| 3. train | ok | 0.4 |\n" if train_row else "")
                + "<!-- safe_push:preflight end -->")

        def history(*first_parents):
            """git as block_current asks it: main's first-parent chain, or what the head
            holds."""
            def answer(repo, *args, **kwargs):
                held = (sha, base, older)
                return "\n".join(first_parents if "--first-parent" in args else held)
            return answer

        chain = (tip, later, base, older)
        with mock.patch.object(safe_push, "git", side_effect=history(*chain)):
            self.assertTrue(safe_push.block_current(ctx, block(tip), record))
            self.assertTrue(safe_push.block_current(ctx, block(later), record))
            self.assertTrue(safe_push.block_current(ctx, block(base), record))
            self.assertFalse(safe_push.block_current(ctx, block(older), record))
            self.assertFalse(safe_push.block_current(ctx, block("f" * 40), record))
            self.assertFalse(safe_push.block_current(ctx, block(later[:12]), record))
            self.assertFalse(safe_push.block_current(ctx._replace(queue=False),
                                                     block(later), record))
            self.assertFalse(safe_push.block_current(ctx._replace(sha="f" * 40),
                                                     block(tip), record))
            train = ctx._replace(branch="train/docs-1")
            self.assertFalse(safe_push.block_current(train, block(tip), record))
            self.assertTrue(safe_push.block_current(train, block(tip, train_row=True), record))
            # As b7aac65f: an old main commit as both base and harness, for a head built on
            # newer main. The judge refuses it, so it is not current, even were this run
            # to compare against that old commit.
            self.assertFalse(safe_push.block_current(ctx, block(older, at=older), record))
            self.assertFalse(safe_push.block_current(ctx._replace(base=older),
                                                     block(older, at=older), record))
            # And the reverse: the block the judge accepts is current, whatever base the
            # context names (block_current reads main's chain itself), even one off it.
            self.assertTrue(safe_push.block_current(ctx._replace(base="9" * 40),
                                                    block(base), record))
            self.assertTrue(safe_push.block_current(ctx._replace(base="9" * 40),
                                                    block(tip), record))
        with mock.patch.object(safe_push, "git", side_effect=history(tip, later)):
            self.assertFalse(safe_push.block_current(ctx, block(later), record))
        self.assertFalse(safe_push.block_current(ctx, None, record))

    def test_github_api_reads_refuse_unreadable_answers(self):
        ctx = safe_push.Context(Path("."), "a" * 40, "b" * 40, 1, "", "test/stoicheia", {},
                                gh=("gh",))

        def answer(code, stdout, stderr=""):
            return mock.patch.object(safe_push, "run", return_value=subprocess.CompletedProcess(
                [], code, stdout, stderr))

        with answer(0, "not JSON"), self.assertRaisesRegex(
                safe_push.Refusal, "did not give a readable JSON answer"):
            safe_push.api_json(ctx, "repos/test/stoicheia/x")
        with answer(0, json.dumps({"errors": [{"message": "no"}]})), self.assertRaisesRegex(
                safe_push.Refusal, "reported errors"):
            safe_push.api_json(ctx, "graphql")
        missing = json.dumps({"message": "Not Found", "status": "404"})
        with answer(1, missing, "gh: Not Found (HTTP 404)"):
            self.assertIsNone(safe_push.api_json(ctx, "repos/x", missing=True))
            with self.assertRaisesRegex(safe_push.Refusal, "could not read GitHub's repos/x"):
                safe_push.api_json(ctx, "repos/x")
        with answer(1, "", "gh: Server Error (HTTP 500)"), self.assertRaisesRegex(
                safe_push.Refusal, "could not read GitHub's repos/x"):
            safe_push.api_json(ctx, "repos/x", missing=True)
        with mock.patch.object(safe_push, "run", side_effect=OSError("no gh")), \
                self.assertRaisesRegex(safe_push.Refusal, "could not read GitHub's repos/x"):
            safe_push.api_json(ctx, "repos/x")
        for pages in (None, {}, [], [{}], [[], None]):
            with self.subTest(pages=pages):
                with self.assertRaisesRegex(safe_push.Refusal, "expected pages of entries"):
                    safe_push.api_pages(pages, "entries")
        self.assertEqual(safe_push.api_pages([[1], [], [2]], "entries"), [1, 2])

    def test_queue_reads_refuse_unreadable_answers(self):
        head = "a" * 40
        ctx = safe_push.Context(Path("."), head, "b" * 40, 1, "", "test/stoicheia", {},
                                branch="docs-1", gh=("gh",), queue=True)
        good = {"id": "PR_1", "state": "OPEN", "headRefOid": head, "headRefName": "docs-1",
                "baseRefName": "main", "mergeCommit": None, "mergeQueueEntry": None}

        def graphql(view):
            return mock.patch.object(safe_push, "api_json", return_value={
                "data": {"repository": {"pullRequest": view}}})

        with graphql(good):
            self.assertEqual(safe_push.queue_view(ctx, 1), good)
        for change in ({"headRefOid": "c" * 40}, {"headRefName": "other"},
                       {"baseRefName": "next"}, {"state": "DRAFT"}, {"id": ""},
                       {"mergeQueueEntry": {"id": ""}},
                       {"mergeQueueEntry": {"id": "MQ_1", "headCommit": {"oid": "short"}}}):
            with self.subTest(change=change):
                with graphql(dict(good, **change)), self.assertRaisesRegex(
                        safe_push.Refusal, "unreadable queue (state|group head)"):
                    safe_push.queue_view(ctx, 1)
        with graphql({k: v for k, v in good.items() if k != "mergeQueueEntry"}), \
                self.assertRaisesRegex(safe_push.Refusal, "unreadable queue state"):
            safe_push.queue_view(ctx, 1)
        ack = {"id": "MQ_1", "headCommit": None, "pullRequest": {"id": "PR_1", "headRefOid": head}}

        def acknowledged(entry):
            return mock.patch.object(safe_push, "api_json", return_value={
                "data": {"enqueuePullRequest": {"mergeQueueEntry": entry}}})

        with acknowledged(ack):
            self.assertEqual(safe_push.enqueue(ctx, good), ack)
        for entry in (None, dict(ack, id=""), dict(ack, pullRequest={"id": "PR_2",
                                                                     "headRefOid": head}),
                      dict(ack, pullRequest={"id": "PR_1", "headRefOid": "c" * 40})):
            with self.subTest(entry=entry):
                with acknowledged(entry), self.assertRaisesRegex(
                        safe_push.Refusal, "unreadable enqueue acknowledgement"):
                    safe_push.enqueue(ctx, good)
        self.assertIsNone(safe_push.queue_group({"headCommit": None}))
        self.assertEqual(safe_push.queue_group({"headCommit": {"oid": head}}), head)
        for commit in ({"oid": 7}, {"oid": "short"}, "a" * 40, {}):
            with self.subTest(commit=commit):
                with self.assertRaisesRegex(safe_push.Refusal, "unreadable queue group head"):
                    safe_push.queue_group({"headCommit": commit})

    def test_queue_base_is_the_newest_main_commit_the_head_contains(self):
        # Main's first-parent chain, newest first, and what the head holds: the base is the
        # newest commit of the chain held, the judge's base for the block, never the head's
        # merge base with main when that lies off the chain (a member merged on its own,
        # "9" * 40 here, which the head holds and main has as a second parent).
        tip, older, oldest, member, head = "d" * 40, "c" * 40, "b" * 40, "9" * 40, "a" * 40
        ctx = safe_push.Context(Path("."), head, tip, 1, "", None, {})

        def history(chain, held):
            def answer(repo, *args, **kwargs):
                return "\n".join(chain if "--first-parent" in args else held) + "\n"
            return answer

        chain = (tip, older, oldest)
        for held, base in (((head, member, older, oldest), older),
                           ((head, tip, older, oldest), tip),
                           ((head, member, oldest), oldest)):
            with self.subTest(held=held):
                with mock.patch.object(safe_push, "git", side_effect=history(chain, held)):
                    self.assertEqual(safe_push.queue_base(ctx, head), base)
        for chain, held in ((chain, (head, member)), ((), (head, older)),
                            (("short",), ("short",))):
            with self.subTest(chain=chain, held=held):
                with mock.patch.object(safe_push, "git", side_effect=history(chain, held)), \
                        self.assertRaisesRegex(safe_push.Refusal, "contains no commit of "
                                               "origin/main's first-parent chain"):
                    safe_push.queue_base(ctx, head)

    def test_queue_main_refuses_a_closed_request_and_reports_an_unknown_end(self):
        head = "a" * 40
        ctx = safe_push.Context(Path("."), head, "b" * 40, 1, "", "test/stoicheia", {},
                                branch="docs-1", gh=("gh",), queue=True)
        view = {"id": "PR_1", "state": "OPEN", "headRefOid": head, "mergeQueueEntry": None}
        entry = {"id": "MQ_1", "headCommit": None}

        def follow(*views):
            output = io.StringIO()
            with mock.patch.object(safe_push, "fetch_base", return_value="b" * 40), \
                    mock.patch.object(safe_push, "main_health"), \
                    mock.patch.object(safe_push, "queue_view", side_effect=list(views)), \
                    mock.patch.object(safe_push, "enqueue", return_value=entry) as enqueue, \
                    mock.patch.object(safe_push, "summary"), \
                    contextlib.redirect_stdout(output):
                code = safe_push.queue_main(ctx, 1, safe_push.Report(), False, True, "")
            return code, output.getvalue(), enqueue

        code, out, enqueue = follow(dict(view, state="CLOSED"))
        self.assertEqual(code, 1, out)
        self.assertIn("#1 is no longer open", out)
        enqueue.assert_not_called()
        code, out, enqueue = follow(view, dict(view, state="CLOSED"))
        self.assertEqual(code, 3, out)
        self.assertIn("#1 is CLOSED; no queue verdict is known", out)
        enqueue.assert_called_once()

    def test_own_pull_requests(self):
        # Ours: the head a branch of the base repository itself (isCrossRepository false),
        # of the branch's name, whatever owner GitHub names; never a fork's of that name.
        ctx = safe_push.Context(Path("."), "a" * 40, "b" * 40, 1, "", "test/stoicheia", {},
                                "test-pr")

        def pr(number, cross, login, branch="test-pr"):
            p = {"number": number, "headRefName": branch,
                 "headRepositoryOwner": {"login": login}}
            return p if cross is None else dict(p, isCrossRepository=cross)
        prs = [pr(1, False, "test"), pr(2, False, "new-owner"), pr(3, True, "stranger"),
               pr(4, True, "test"), pr(5, None, "test"), pr(6, False, "test", "other")]
        self.assertEqual([p["number"] for p in safe_push.own_prs(ctx, prs)], [1, 2])

    def test_mentions_count_nothing_the_guards_refused_before(self):
        # The guards' patterns before a mention had to start the text or follow whitespace
        # or one of ( < [ ` " ' * (main at 756bdbae): the files guard's, and the directories
        # guard's, which took no prefix. Over every form below, the rule now counts none of
        # the forms those refused, but a directory's own additions, each starting where a
        # mention may: anchored at the root, by a relative link that resolves, or ending a
        # sentence when the mention holds a slash, so that a directory at the root named
        # bare, as "the figures.", names nothing. It counts every form those counted that
        # starts so, and none other.
        before = {"file": r"(?<![\w/.-])(?P<prefix>/|(?:\.\.?/)*)%s(?!\.?[\w/-])",
                  "directory": r"(?<![\w/.-])(?P<prefix>)%s/?(?![\w./-])"}
        paths = (("file", "scripts/check_style.py"), ("directory", "mishnah/test"),
                 ("directory", "figures"))
        # What stands before the path: a head, then a prefix. No head ends in / or ., so
        # that the prefix, read whole, is the one given.
        leads = ["", *"!#$%&()*+,-:;<=>?@[\\]^_`{|}~\"'aZ0 \t\u00a0\u201c\u2018\u00ab\u00e9"]
        heads = [outer + lead for outer in ("", "x", "_", "*", "(") for lead in leads]
        prefixes = ("", "/", ".", "../../", "./../../", "../", "~/", "C:/", "@/", "x/",
                    "https://example.com/~/")
        tails = ("", ".", "/", "/.", "..", "./", "_", "'s", ")", "`", "*", ",", "-old", ".md",
                 "/x")
        sources = (DECISIONS, "docs/decisions/2026-10-21-test.md")

        def counts(pattern, path, text, source):
            hunk = safe_push.Hunk(source, [], [safe_push.Added(source, 1, text)])
            return safe_push.names_path([hunk], path, pattern)

        newly, lost, elsewhere = [], [], []
        for kind, path in paths:
            now = safe_push.mention(path, kind == "directory")
            then = re.compile(before[kind] % re.escape(path))
            for source, head, prefix, tail in itertools.product(sources, heads, prefixes, tails):
                text = head + prefix + path + tail
                counted, was = counts(now, path, text, source), counts(then, path, text, source)
                # Where a mention may start: a prefix of its own (none, the root's /, or
                # the ./ and ../ steps of a link), after the start, a space or an opening mark.
                starts = prefix in ("", "/", "../../", "./../../", "../") and (
                    not head or head[-1].isspace() or head[-1] in "(<[`\"'*")
                added = kind == "directory" and starts and (
                    prefix in ("/", "../../", "./../../") or tail == "/."
                    or (tail == "." and "/" in prefix + path))
                if counted and not was and not added:
                    newly.append((kind, source, text))
                if was and starts and not counted:
                    lost.append((kind, source, text))
                if counted and not starts:
                    elsewhere.append((kind, source, text))
        self.assertEqual(newly, [])
        self.assertEqual(lost, [])
        self.assertEqual(elsewhere, [])
        # The forms the security re-review found, refused now, and a few the guards counted
        # before that start otherwise, refused too.
        for kind, path, text in (
                ("directory", "mishnah/test", "~/mishnah/test/"),
                ("directory", "mishnah/test", "C:/mishnah/test/"),
                ("directory", "mishnah/test", "@/mishnah/test/"),
                ("directory", "mishnah/test", "https://example.com/~/mishnah/test/"),
                ("directory", "mishnah/test", "x+mishnah/test/"),
                ("file", "scripts/check_style.py", "x+scripts/check_style.py"),
                ("file", "scripts/check_style.py", "~/scripts/check_style.py"),
                ("file", "scripts/check_style.py", "x:scripts/check_style.py"),
                ("directory", "figures", "Nothing changes in the figures.")):
            with self.subTest(text=text):
                pattern = safe_push.mention(path, kind == "directory")
                self.assertFalse(counts(pattern, path, text, sources[1]))

    def test_revert_advice_and_slug(self):
        ctx = safe_push.Context(Path("."), "a" * 40, "b" * 40, 3, "", None, {})
        # The record is restored from origin/main: each of the folder and the page that it
        # holds, for git restore stops at a path its source lacks.
        with mock.patch.object(safe_push, "git_ok", return_value=True):
            advice = safe_push.revert_advice(ctx)
        self.assertIn(f"git revert --no-commit -m 1 {'a' * 40}", advice)
        self.assertIn("git restore --source=origin/main --staged --worktree -- docs/decisions/ "
                      f"{DECISIONS}\n", advice)
        page = mock.patch.object(safe_push, "git_ok",
                                 side_effect=lambda repo, *args: args[-1].endswith(DECISIONS))
        with page:
            self.assertIn(f"git restore --source=origin/main --staged --worktree -- {DECISIONS}\n",
                          safe_push.revert_advice(ctx))
        with mock.patch.object(safe_push, "git_ok", return_value=False):
            self.assertNotIn("git restore", safe_push.revert_advice(ctx))
        self.assertIn(f"docs/decisions/{datetime.date.today().isoformat()}-revert-{'a' * 12}.md",
                      advice)
        self.assertIn(f"git safe-push --branch revert-{'a' * 12} --label <kind>", advice)
        self.assertIn("--label tooling", safe_push.revert_advice(ctx, "tooling"))
        self.assertEqual(safe_push.github_slug("https://github.com/jackChallis/stoicheia.git"),
                         "jackChallis/stoicheia")
        self.assertEqual(safe_push.github_slug("git@github.com:jackChallis/stoicheia.git"),
                         "jackChallis/stoicheia")
        self.assertFalse(safe_push.is_local("https://github.com/jackChallis/stoicheia.git"))

    def test_identities(self):
        flagged = safe_push.scan_identity
        self.assertTrue(flagged("a", "Some One <someone@Some-MacBook.local>"))
        self.assertTrue(flagged("a", "someone <someone@(none)>"))
        self.assertTrue(flagged("a", "/" + "Users" + "/someone <a@example.org>"))
        self.assertEqual(flagged("a", "Stoicheia Team <team@example.org>"), [])
        self.assertEqual(flagged("a", "GitHub <noreply@github.com>"), [])

    def test_checklist(self):
        template = ("- [ ] **Required:** One.\n- [ ] **Required if protected:** Two.\n"
                    "- [ ] Optional.\n")
        problems = safe_push.checklist_problems
        self.assertEqual(problems(template.replace("[ ] **Required:**", "[x] **Required:**"),
                                  template, False), [])
        self.assertEqual(problems(template, template, False), ["unticked: Required: One."])
        self.assertEqual(len(problems(template, template, True)), 2)
        self.assertEqual(problems("- [x] **Required:** One.\n", template, True),
                         ["missing from the body: Required if protected: Two."])
        self.assertTrue(problems("No checklist at all.", None, False))

    def test_judge_checks(self):
        judge = safe_push.judge_checks
        self.assertEqual(judge(PASSING)[0], "success")
        self.assertEqual(judge(PASSING[:2])[0], "missing")
        self.assertEqual(judge(PASSING + [{"name": "check", "bucket": "fail"}])[0], "failure")
        self.assertEqual(judge(PASSING + [{"name": "other", "bucket": "pending"}])[0], "pending")
        # A check outside REQUIRED_CHECKS, as safe-push-tests is, holds a merge while it
        # fails, and a skipped run of it holds nothing back (#157).
        unrequired = {"name": "safe-push-tests", "workflow": "Safe-push tests"}
        self.assertEqual(judge(PASSING + [dict(unrequired, bucket="fail", state="FAILURE")])[0],
                         "failure")
        self.assertEqual(judge(PASSING + [dict(unrequired, bucket="skipping",
                                               state="SKIPPED")])[0], "success")
        # The two checks the ruleset gained on 20 October (#142) hold a merge as the first
        # three do. `acceptance` runs only on a pull request, and a push's run skips it, so
        # a skipped run beside the pull request's passing one is a pass, and a skipped run
        # alone is not.
        for name in ("formal-model", "acceptance"):
            with self.subTest(name=name):
                own = next(c for c in PASSING if c["name"] == name)
                others = [c for c in PASSING if c is not own]
                failed = dict(own, bucket="fail", state="FAILURE")
                skipped = dict(own, bucket="skipping", state="SKIPPED")
                verdict, detail = judge(others)
                self.assertEqual(verdict, "missing")
                self.assertIn(f"no passing run of {name} ", detail)
                verdict, detail = judge(others + [failed])
                self.assertEqual(verdict, "failure")
                self.assertIn(f"failing: {name} ", detail)
                self.assertEqual(judge(PASSING + [failed])[0], "failure")
                self.assertEqual(judge(others + [skipped])[0], "missing")
                self.assertEqual(judge(PASSING + [skipped])[0], "success")

    @staticmethod
    def law(body: str, path: str = "tests/model/hyperbolic.py",
            head: str = "@axiom('x', dict(A=P))\ndef _(c):\n") -> bool:
        """Does a law of `path`, under `head`, with `body` and then `return True`, keep to
        the allow-list (self_contained)?"""
        lines = "".join(f"    {line}\n" for line in body.split("\n"))
        fn = ast.parse(f"{head}{lines}    return True\n")
        return safe_push.self_contained(fn.body[0], path)

    def test_a_harness_is_read_as_python_reads_it(self):
        base = b"X = 1\n"
        cookie = b"# -*- coding: utf-7 -*-\nX = 1\n#+AAo-X = 2\n"
        self.assertNotEqual(safe_push.law_code(base)[0], safe_push.law_code(cookie)[0])
        self.assertEqual(safe_push.law_code(cookie.decode("utf-8"))[0],
                         safe_push.law_code(base)[0])

    def test_every_law_keeps_to_the_allow_list(self):
        # Issue #40, and its reviewer's finding, with thanks: a law's code is read against
        # an allow-list collected from the laws themselves. Every law of the two harnesses
        # keeps to it; and each entry is one some law needs, so that the list is no wider
        # than the laws: without the entry, a law is refused. (An axiom removed with the
        # one law that used an entry leaves the entry harmless, and this test then asks
        # for it to go, in a check change of its own.)
        laws = {}
        for path in safe_push.MODEL_LAW_CODE:
            _, laws[path] = safe_push.law_code((SOURCE / path).read_text())
            for name, fn in laws[path].items():
                self.assertTrue(safe_push.self_contained(fn, path), f"{path}: {name}")

        def refused_somewhere(paths) -> bool:
            return any(not safe_push.self_contained(fn, path)
                       for path in paths for fn in laws[path].values())
        for path, roles in safe_push.LAW_GLOBALS.items():
            for role, names in roles.items():
                for name in names:
                    narrower = {p: dict(r) for p, r in safe_push.LAW_GLOBALS.items()}
                    narrower[path][role] = names - {name}
                    with self.subTest(path=path, role=role, entry=name), \
                            mock.patch.object(safe_push, "LAW_GLOBALS", narrower):
                        self.assertTrue(refused_somewhere([path]))
        for const in ("LAW_BUILTINS", "LAW_MODULES", "LAW_MATH", "LAW_ATTRIBUTES",
                      "LAW_MUTATORS", "LAW_KINDS"):
            names = getattr(safe_push, const)
            for name in names:
                with self.subTest(list=const, entry=name), \
                        mock.patch.object(safe_push, const, names - {name}):
                    self.assertTrue(refused_somewhere(safe_push.MODEL_LAW_CODE))

    def test_a_law_reaches_nothing_off_the_allow_list(self):
        # Issue #40, and its reviewer's finding, with thanks: the check was a deny-list,
        # which reflection escaped; under the allow-list, each route the reviewer named is
        # refused, and so is every name, attribute and piece of syntax the laws do not use.
        refused = {
            # The reviewer's routes: a frame chain, the random module's os, a namespace by
            # vars or __dict__, a lookup by string, a closure over a global, a default
            # argument bound to a shared container.
            "a generator's frame": "g = (x for x in ())\n"
                                   "g.gi_frame.f_back.f_globals['DEN'].clear()",
            "a frame, from sys": "sys._getframe(1).f_globals['SEEDS'].clear()",
            "a traceback's frame": "try:\n    1 / 0\nexcept ZeroDivisionError as e:\n"
                                   "    e.__traceback__.tb_frame.f_globals['DEN'].clear()",
            "random's os": "random._os.system('true')",
            # Two the deny-list let through: the decimal context every law of the
            # hyperbolic plane computes in, coarsened; and a result forged by print.
            "random's os, coarsening the decimals": "m = random._os.sys.modules['decimal']\n"
                                                    "m.setcontext(m.Context(prec=2))",
            "random's os, printing": "random._os.sys.modules['builtins'].print('len_self 1 1 0')",
            "the random numbers' module": "c['_rng'].__class__",
            "vars": "vars()['DEN'].clear()",
            "vars of a module": "vars(math)['pi']",
            "a __dict__": "math.__dict__['pi']",
            "globals": "globals()['DEN'].clear()",
            "the builtins by string": "__builtins__['exec']('DEN.clear()')",
            "getattr with a string": "getattr(c['_rng'], 'seed')(0)",
            "__getattribute__ with a string": "c['_rng'].__getattribute__('seed')(0)",
            "a format string's attribute": "'{0.__class__}'.format(c)",
            "a closure over a global": "def h():\n    return DEN\nh().clear()",
            "a closure changing a global": "def h():\n    DEN.clear()\nh()",
            "a default argument bound to a shared container": "def h(d=DEN):\n    d.append(1)\nh()",
            "a default argument bound to its own list": "ws = []\ndef h(d=ws):\n"
                                                        "    d.append(1)\nh()",
            # A global under a name a comprehension or an inner function binds: Python
            # resolves it outside them to the global, and so does the check.
            "print, bound only in a comprehension": "[print for print in ()]\n"
                                                    "print('len_self 1 1 0')",
            "exit, bound only in a function": "def h():\n    exit = 0\nexit(0)",
            "a table, bound only in a function": "def h():\n    SEEDS = {}\nSEEDS[1] = 2",
            # The syntax the laws do not use.
            "an import": "import os",
            "global": "global BOX\nBOX = 1",
            "nonlocal": "def h():\n    nonlocal c\n    c = 1",
            "a walrus": "(y := 1)",
            "a lambda": "f = lambda: 0",
            "yield": "yield 1",
            "try": "try:\n    pass\nexcept Exception:\n    pass",
            "with": "with c['_rng'] as d:\n    pass",
            "raise": "raise SystemExit(0)",
            "assert": "assert c",
            "del": "ws = [1]\ndel ws[0]",
            "a class": "class K:\n    pass",
            "an f-string": "s = f'{c}'",
            "a starred name": "a, *b = [1, 2]",
            "an annotated name": "x: list = []",
            "a generator returned": "return (x for x in ())",
            "a generator kept": "g = (x for x in ())",
            "a decorated function": "@feq\ndef h():\n    pass",
            "a function with a starred parameter": "def h(*x):\n    pass",
            "keywords unpacked": "feq(**{'a': 1, 'b': 1})",
            "a dict unpacked": "d = {**c}",
            "a dunder name": "__x = 1",
            # The names and attributes the laws do not use, or not so.
            "a builtin not on the list": "sorted([1])",
            "type": "type(c)",
            "dict, called": "d = dict(a=1)",
            "a helper as a value": "f = on_line",
            "a builtin as a value": "m = map(float, [1])",
            "a value called": "SEEDS()",
            "a table, itself": "s = SEEDS",
            "a table, stored into": "SEEDS[1] = 2",
            "a table's method": "SEEDS.setdefault(1, 2)",
            "an attribute of math not on the list": "math.floor(1)",
            "math's attribute on another": "x = 4\nx.sqrt()",
            "an attribute not on the list": "s = set()\ns.add(1)",
            "the random numbers reseeded": "c['_rng'].seed(0)",
            "the random numbers' state": "c['_rng'].setstate(c['_rng'].getstate())",
            "an attribute stored": "ws = []\nws.x = 1",
        }
        for name, body in refused.items():
            with self.subTest(refused=name):
                self.assertFalse(self.law(body), body)
        # A name of one harness is refused in the other.
        self.assertFalse(self.law("make_circle(c['A'], c['B'])", "tests/model/search.py"))
        self.assertFalse(self.law("x = SEEDS[c['al']]", "tests/model/search.py"))
        self.assertFalse(self.law("x = RA"))
        # The law's own signature and decorator: positional parameters only, and the
        # decorator's kinds and generator as the laws write them.
        for head in ("def _(c, d=DEN):", "def _(c, *a):", "def _(c: print('x')):",
                     "def _(c) -> print('x'):", "def _(c, /):"):
            with self.subTest(signature=head):
                self.assertFalse(self.law("pass", head=f"@axiom('x', dict(A=P))\n{head}\n"))
        for decorator, path in (("@axiom('x', dict(A=print('hi')))", None),
                                ("@axiom('x', {'A': P})", None),
                                ("@axiom('x', dict(A=P), print)", None),
                                ("@axiom('x', dict(A=P), gs_cm(print))", None),
                                ("@axiom('x', dict(A=P), gen=gs_p4)", None),
                                ("@axiom('x', dict(A=P), gs_p4)", "tests/model/search.py")):
            with self.subTest(decorator=decorator):
                self.assertFalse(self.law("pass", path or "tests/model/hyperbolic.py",
                                          f"{decorator}\ndef _(c):\n"))
        accepted = {
            "a closure over its own names": "A = c['A']\ndef iso(X):\n    x = X[0] - A[0]\n"
                                            "    return x\ny = iso(c['A'])",
            "its own list, changed in a function": "ws = []\ndef h():\n    ws.append(1)\nh()",
            "a table read": "x = SEEDS[c['al']]",
            "math's pi": "x = math.pi",
            "the random numbers drawn": "x = c['_rng'].randint(0, 3) + c['_rng'].random()",
            "a generator unpacked": "a, b = (c[k] for k in 'AB')",
            "a generator as an argument": "x = all(on_line(w, c['L']) for w in [c['A']])",
            "a loop with break and continue": "j = 0\nwhile j < 3:\n    j += 1\n"
                                              "    if j == 2:\n        break\n    continue",
            "comprehensions of its own": "x = [w for w in range(3)]\ny = {w: w for w in x}",
        }
        for name, body in accepted.items():
            with self.subTest(accepted=name):
                self.assertTrue(self.law(body), body)
        for decorator in ("@axiom('x', dict())", "@axiom('x', dict(A=P, L=L_, al=C_), gs_p4)",
                          "@axiom('x', dict(A=P), gs_cm('side'))",
                          "@axiom('x', dict(A=P), gs_convex())"):
            with self.subTest(decorator=decorator):
                self.assertTrue(self.law("pass", head=f"{decorator}\ndef _(c):\n"))

    def test_a_law_changes_only_containers_it_made(self):
        # Issue #40, and its verifier's finding, with thanks: a law's code may change a
        # container only through a name it bound to a container made in its own body. A
        # second name for a shared one, an element of its own, its argument, or a shuffle
        # of what it did not make, is refused. Under the allow-list most of these name a
        # global or an attribute it does not hold, and are refused for that as well.
        refused = {
            "a second name": "d = DEN\nd[:] = [2]",
            "a loop's name": "for d in (DEN,):\n    d.clear()",
            "a comprehension's name": "[d.clear() for d in (DEN,)]",
            "a name bound by with": "with c['_rng'] as d:\n    d.clear()",
            "a second name, added to": "d = DEN\nd += [2]",
            "a second name, by a method": "d = DEN\nd.append(1)",
            "a second name, merged into": "d = SEEDS\nd |= {1: 2}",
            "a second name, deleted from": "d = SEEDS\ndel d[1]",
            "one of two names unpacked": "a, b = [], DEN\nb.clear()",
            "a starred name": "a, *b = [], DEN\nb.clear()",
            "a name bound twice": "ws = []\nfor ws in (DEN,):\n    pass\nws.clear()",
            "a name bound to a choice": "d = DEN or []\nd.clear()",
            "a copy made by a method": "ws = DEN.copy()\nws.clear()",
            "a constructor rebound": "list = lambda: DEN\nws = list()\nws.clear()",
            "an element of its own": "x = [DEN]\nx[0].clear()",
            "an element of its own, by a slice": "x = [DEN]\nx[0][:] = []",
            "an element of its own, added to": "x = [DEN]\nx[0] += [1]",
            "an element of a tuple": "d = (DEN,)\nd[0].clear()",
            "its argument": "c['A'] = 1",
            "a second name for its argument": "d = c\nd['x'] = 1",
            "its argument, merged into": "c |= {}",
            "an element of its argument, appended to": "c['A'].append(1)",
            "a second name for its argument, appended to": "d = c\nd.append(1)",
            "a table's entry, added to": "d = SEEDS[c['al']]\nd += [1]",
            "an element of its own, appended to": "x = [[]]\nx[0].append(1)",
            "an element of its own list, added to": "x = [[]]\nx[0] += [1]",
            "a helper's argument": "def h(x):\n    x.clear()\nh(DEN)",
            "a method kept for later": "m = DEN.clear\nm()",
            "a shuffle": "c['_rng'].shuffle(DEN)",
            "a dunder method": "class K:\n    def __radd__(self, o):\n        return 0",
            "the shared name itself": "DEN[:] = [2]",
            "the shared name, by a method": "SEEDS.clear()",
            "another module, reached": "sys.modules['decimal'].setcontext(None)",
            "a shell": "os.system('true')",
        }
        for name, body in refused.items():
            with self.subTest(refused=name):
                self.assertFalse(self.law(body), body)
        accepted = {
            "a list of its own": "ws = []\nws.append(1)",
            "unpacked, with a number halved": "ws, t = [], Fr(1, 2)\nt /= 2\nws.append(t)",
            "a counter": "j = 1\nj += 1",
            "a set made by a call": "s = set()\ns = s | {1}",
            "a list stored into": "ws = [0]\nws[0] = 1",
            "one list under two names": "a = b = []\na.append(1)\nb.append(2)",
            "a list added to": "ws = []\nws += [1]",
            "a comprehension appended to": "xs = [y for y in range(3)]\nxs.append(3)",
        }
        for name, body in accepted.items():
            with self.subTest(accepted=name):
                self.assertTrue(self.law(body), body)

    def test_the_laws_files_absent_read_as_none(self):
        # The verifier of #40 found it: a file absent (show gives None) reads as None, not a
        # traceback; tomllib.loads(None) raises AttributeError before Python 3.14.
        self.assertIsNone(safe_push.locked_axioms(None))
        self.assertIsNone(safe_push.model_laws(None))
        self.assertIsNone(safe_push.law_code(None))
        self.assertIsNone(safe_push.locked_axioms("not = [toml"))
        self.assertIsNone(safe_push.model_laws('[laws]\n"Tacit.len_self" = "len_self"\n'))
        laws = (SOURCE / safe_push.MODEL_LAWS).read_text()
        self.assertEqual(safe_push.model_laws(laws)["Postulate5"], ("Postulate5", True))

    def test_an_expectation_is_kept_by_its_ref_field_and_law(self):
        # #150's review: a `law`, or a `ref`, says what an expectation reads, so one added,
        # dropped or changed retargets it, and the expectation is not kept, even where the
        # retargeted one would still pass.
        def file(*expectations):
            return json.dumps({"expectations": list(expectations)})

        def without(x, key):
            return {k: v for k, v in x.items() if k != key}

        law = {"ref": "I.8", "field": "cited_laws", "law": "prop7",
               "includes": ["Postulate1"], "why": "I.7's law is proved with constructions."}
        listed = {"ref": "I.8", "field": "cited_laws", "includes": ["prop7"],
                  "why": "I.8 cites I.7's law."}
        top = {"field": "construction_rules", "includes": ["Postulate1"],
               "excludes": ["Postulate4"], "why": "Postulate 1 constructs."}
        old = file(law, listed, top)
        retargeted = {
            "its law dropped": file(without(law, "law"), listed, top),
            "its law changed": file(dict(law, law="lenSymm"), listed, top),
            "a law added": file(law, dict(listed, law="prop7"), top),
            "its ref dropped": file(law, without(listed, "ref"), top),
            "a ref added": file(law, listed, dict(top, ref="I.4")),
            "its ref changed": file(dict(law, ref="I.4"), listed, top),
            "its field changed": file(law, listed, dict(top, field="axiom_modules")),
        }
        for name, new in retargeted.items():
            with self.subTest(name):
                self.assertFalse(safe_push.kept_expectations(old, new))
        kept = {
            "unchanged": old,
            "reordered": file(top, listed, law),
            "a why reworded": file(dict(law, why="Reworded."), listed, top),
            "its includes grown": file(dict(law, includes=["Postulate1", "Postulate3"]),
                                       listed, top),
            "an expectation added": file(law, listed, top, dict(law, law="lenSymm",
                                                                 includes=[], equals=[])),
        }
        for name, new in kept.items():
            with self.subTest(name):
                self.assertTrue(safe_push.kept_expectations(old, new))

    def test_a_harness_cut_short_fails_the_run(self):
        # Issue #40, and the no-mistakes review's finding, with thanks: a harness that ends
        # early with status 0, by SystemExit(0) among others, fails run.py's judge.
        r = subprocess.run([sys.executable, "-I", "-c", JUDGE_RUNS, str(SOURCE / "tests/model")],
                           cwd=SOURCE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        whole, cut = json.loads(r.stdout)
        self.assertEqual(whole, [])
        self.assertEqual(cut, ["structured stopped before its last line"])


# The shards (#233). On the cadence the suite took 72 to 78 minutes in one job, and more on
# a slow runner, so the cadence workflow runs it as `--shard K/N` for each K from 1 to N,
# side by side, and its safe-push-tests job passes only when every shard succeeded and the
# shards' lists of the tests they ran prove that each test ran once and passed. Each test
# runs in exactly one shard: the tests are listed by unittest's own loader, so a new one is
# never missed, and dealt out by the seconds each took on a GitHub runner, kept beside this
# file; a test missing there weighs their median. The proof is built from what the shards
# ran, not from the dealing.
TIMES = HERE / "test_safe_push_times.json"
CADENCE = SOURCE / safe_push.SUITE_PATH
SHARD_JOB, GATHER_JOB = "safe-push-shards", "safe-push-tests"
USAGE = ("usage: test_safe_push.py --shard K/N [--ran FILE], with 1 <= K <= N; "
         "--cover DIR; or --times-from-log LOG..., each alone")
# The outcomes, as unittest's log words them, of a test that passed or was skipped.
PASSED = ("ok", "skipped", "expected failure")


@dataclass(frozen=True)
class ShardPlan:
    shard_of: dict[str, int]     # each test, as Class.test_name, and its shard, from 1
    loads: tuple[float, ...]     # each shard's expected seconds, the module's setup included
    unmeasured: tuple[str, ...]  # the tests the times do not name, which weigh the median
    median: float


def loaded_tests() -> list[unittest.TestCase]:
    """This suite's tests, as unittest's own loader lists them, in the order it runs them."""
    def flat(suite):
        for test in suite:
            yield from flat(test) if isinstance(test, unittest.TestSuite) else (test,)
    return list(flat(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])))


def time_key(test: unittest.TestCase) -> str:
    """A test's name in the times file: Class.test_name."""
    return ".".join(test.id().split(".")[-2:])


def load_times(path: Path = TIMES) -> tuple[float, dict[str, float]]:
    """The module's setup, which every shard pays once, and each test's seconds."""
    data = json.loads(path.read_text())
    return float(data["setUpModule"]), {str(k): float(v) for k, v in data["tests"].items()}


def shard_plan(keys: list[str], count: int, times: dict[str, float], setup: float) -> ShardPlan:
    """Deal the tests to `count` shards, longest first: each test, heaviest first and then
    by name, goes to the shard with the least time so far, then the fewest tests, then the
    lowest number. A test the times do not name weighs their median. Every test lands in
    exactly one shard, and in the same one whatever order the keys and times come in."""
    if len(set(keys)) != len(keys):
        raise ValueError("two tests share a name")
    median = statistics.median(times.values()) if times else 0.0
    weight = {key: times.get(key, median) for key in keys}
    loads, sizes, shard_of = [setup] * count, [0] * count, {}
    for key in sorted(keys, key=lambda key: (-weight[key], key)):
        index = min(range(count), key=lambda i: (loads[i], sizes[i], i))
        shard_of[key] = index + 1
        loads[index] += weight[key]
        sizes[index] += 1
    return ShardPlan(shard_of, tuple(loads), tuple(sorted(set(keys) - set(times))), median)


def shard_report(plan: ShardPlan, shard: int) -> list[str]:
    """What a shard says before it runs: the tests with no measured time, and its share."""
    lines = [f"No measured time for {key} in scripts/{TIMES.name}: it weighs their median, "
             f"{plan.median:g} s." for key in plan.unmeasured]
    mine = sum(1 for index in plan.shard_of.values() if index == shard)
    lines.append(f"Shard {shard} of {len(plan.loads)}: {mine} of {len(plan.shard_of)} tests, "
                 f"about {plan.loads[shard - 1]:.0f} s by the times measured on a GitHub "
                 f"runner, the module's setup included.")
    return lines


def script_command(argv: list[str]) -> tuple | None:
    """What the command line asks of this script beyond unittest's own arguments, each form
    standing alone: ("shard", K, N, FILE or None) for `--shard K/N [--ran FILE]`, ("cover",
    DIR) for `--cover DIR` and ("times", [LOG, ...]) for `--times-from-log LOG...`; None
    when it names none of them. Any other use of them exits with status 2."""
    if not any(arg.startswith(("--shard", "--ran", "--cover", "--times-from-log"))
               for arg in argv):
        return None

    def plain(arg: str) -> bool:
        return arg != "" and not arg.startswith("-")

    if argv[0] == "--shard" and len(argv) in (2, 4):
        match = re.fullmatch(r"([1-9][0-9]*)/([1-9][0-9]*)", argv[1])
        if (match and int(match[1]) <= int(match[2])
                and (len(argv) == 2 or (argv[2] == "--ran" and plain(argv[3])))):
            return "shard", int(match[1]), int(match[2]), Path(argv[3]) if argv[2:] else None
    elif argv[0] == "--cover" and len(argv) == 2 and plain(argv[1]):
        return "cover", Path(argv[1])
    elif argv[0] == "--times-from-log" and len(argv) > 1 and all(map(plain, argv[1:])):
        return "times", [Path(arg) for arg in argv[1:]]
    print(USAGE, file=sys.stderr)
    sys.exit(2)


class RanResult(unittest.TextTestResult):
    """unittest's verbose result, which also keeps each test it ran, as Class.test_name,
    with its outcome in the word its log gives: ok, skipped, expected failure, FAIL, ERROR
    or unexpected success. A subtest's failure is its test's; a failing fixture of a module
    or a class is no test, and the tests it kept from running are not listed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ran: list[list[str]] = []

    def startTest(self, test):
        super().startTest(test)
        self.ran.append([time_key(test), "unfinished"])

    def outcome(self, test, word: str) -> None:
        test = getattr(test, "test_case", test)  # a subtest's test
        if (isinstance(test, unittest.TestCase) and self.ran
                and self.ran[-1][0] == time_key(test) and self.ran[-1][1] not in ("FAIL", "ERROR")):
            self.ran[-1][1] = word

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcome(test, "ok")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcome(test, "FAIL")

    def addError(self, test, err):
        super().addError(test, err)
        self.outcome(test, "ERROR")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcome(test, "skipped")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.outcome(test, "expected failure")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.outcome(test, "unexpected success")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.outcome(test, "FAIL" if issubclass(err[0], test.failureException) else "ERROR")


class RanRunner(unittest.TextTestRunner):
    """unittest's verbose runner, keeping the RanResult of its run."""
    resultclass = RanResult

    def __init__(self, **kwargs):
        super().__init__(verbosity=2, **kwargs)
        self.result: RanResult | None = None

    def _makeResult(self):
        self.result = super()._makeResult()
        return self.result


def run_shard(shard: int, count: int, ran: Path | None = None) -> None:
    """Run exactly the tests dealt to shard `shard` of `count`, in unittest's order, and
    exit with unittest's verdict. When `ran` is given, write to it the tests the shard ran,
    each with its outcome: a shard that stops before its end writes nothing there."""
    tests = loaded_tests()
    setup, times = load_times()
    plan = shard_plan([time_key(test) for test in tests], count, times, setup)
    for line in shard_report(plan, shard):
        print(line, file=sys.stderr)
    names = [time_key(test) for test in tests if plan.shard_of[time_key(test)] == shard]
    if not names:
        sys.exit(f"Shard {shard} of {count} has no tests: {len(tests)} tests fill at most "
                 f"{len(tests)} shards.")
    runner = RanRunner(warnings=None if sys.warnoptions else "default")
    unittest.main(argv=sys.argv[:1], defaultTest=names, testRunner=runner, exit=False)
    if ran is not None:
        ran.parent.mkdir(parents=True, exist_ok=True)
        ran.write_text(json.dumps({"shard": shard, "count": count,
                                   "ran": runner.result.ran if runner.result else []},
                                  indent=1) + "\n")
    sys.exit(0 if runner.result is not None and runner.result.wasSuccessful() else 1)


def ci_jobs() -> dict:
    """The jobs of the cadence workflow, which runs the shards and the proof."""
    return yaml.safe_load(CADENCE.read_text())["jobs"]


def ci_shard_count(jobs: dict) -> int:
    """N, from the matrix of the cadence workflow's shard job, whose one dimension holds 1
    to N in turn, each once, N > 1: `strategy.job-total`, which each shard is given as N,
    is then N too."""
    matrix = jobs[SHARD_JOB]["strategy"]["matrix"]
    shards = matrix.get("shard") if isinstance(matrix, dict) else None
    if (not isinstance(matrix, dict) or list(matrix) != ["shard"] or not isinstance(shards, list)
            or len(shards) < 2 or any(type(shard) is not int for shard in shards)
            or shards != list(range(1, len(shards) + 1))):
        raise ValueError(f"The matrix of {SHARD_JOB} is {matrix!r}: it should have one "
                         "dimension, shard, holding 1 to N in turn, N > 1, and nothing else.")
    return len(shards)


def read_ran(path: Path) -> tuple[int, int, list[tuple[str, str]]] | None:
    """(K, N, [(test, outcome), ...]) from the list `--shard K/N --ran FILE` wrote; None
    when the file is not such a list."""
    try:
        data = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    if not (isinstance(data, dict) and set(data) == {"shard", "count", "ran"}
            and type(data["shard"]) is int and type(data["count"]) is int
            and isinstance(data["ran"], list)
            and all(isinstance(entry, list) and len(entry) == 2
                    and all(isinstance(part, str) for part in entry) for entry in data["ran"])):
        return None
    return data["shard"], data["count"], [(key, outcome) for key, outcome in data["ran"]]


def cover(directory: Path, count: int, discovered: list[str]) -> list[str]:
    """What keeps the lists in `directory`, which the `count` shards wrote of the tests they
    ran, from proving that each test of `discovered` ran once, in one shard, and passed or
    was skipped: each fault named, or nothing when they prove it. A shard that stopped
    before its end wrote no list, and its tests are then named as run in no shard."""
    problems, lists = [], {}
    files = sorted(path for path in directory.rglob("*") if path.is_file()) \
        if directory.is_dir() else []
    for path in files:
        read = read_ran(path)
        if read is None:
            problems.append(f"{path} is not a shard's list of the tests it ran.")
            continue
        shard, total, ran = read
        if total != count or not 1 <= shard <= count:
            problems.append(f"{path} is the list of shard {shard} of {total}, but CI's matrix "
                            f"has {count} shards.")
        elif shard in lists:
            problems.append(f"Shard {shard} left two lists, {lists[shard][0]} and {path}.")
        else:
            lists[shard] = (path, ran)
    problems += [f"Shard {shard} of {count} left no list of the tests it ran: it stopped "
                 "before its end, or its list was not kept."
                 for shard in range(1, count + 1) if shard not in lists]
    runs: dict[str, list[tuple[int, str]]] = {}
    for shard in sorted(lists):
        for key, outcome in lists[shard][1]:
            runs.setdefault(key, []).append((shard, outcome))
    problems += [f"{key} ran in no shard." for key in discovered if key not in runs]
    listed = set(discovered)
    for key, seen in runs.items():
        if len(seen) > 1:
            problems.append(f"{key} ran {len(seen)} times: by shard "
                            + " and shard ".join(str(shard) for shard, _ in seen) + ".")
        if key not in listed:
            problems.append(f"{key} ran in shard {seen[0][0]}, but unittest's loader does not "
                            "list it here.")
        problems += [f"{key} did not pass in shard {shard}: {outcome}."
                     for shard, outcome in seen if outcome not in PASSED]
    return problems


def cover_command(directory: Path) -> int:
    """`--cover DIR`: the proof over the shards' lists in DIR, against this checkout's tests
    as unittest's loader lists them and the N of the cadence workflow's matrix."""
    try:
        count = ci_shard_count(ci_jobs())
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    discovered = [time_key(test) for test in loaded_tests()]
    problems = cover(directory, count, discovered)
    if problems:
        print(f"The shards' lists in {directory} do not prove that each of the "
              f"{len(discovered)} tests ran once and passed:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    words = [outcome for path in directory.rglob("*") if path.is_file()
             for _, outcome in read_ran(path)[2]]
    print(f"Each of the {len(discovered)} tests unittest's loader lists here ran once, in one "
          f"of the {count} shards: "
          + ", ".join(f"{words.count(word)} {word}" for word in sorted(set(words))) + ".")
    return 0


# A line of a CI log as `gh run view RUN --log` gives it, the job and the step before it, or
# as a job's log gives it, without them: the time GitHub stamped on it, then the line.
LOG_LINE = re.compile(r"(?:(?P<job>[^\t]*)\t[^\t]*\t)?\ufeff?(?P<stamp>\d{4}-\d\d-\d\dT"
                      r"\d\d:\d\d:\d\d)(?P<fraction>\.\d+)?Z ?(?P<text>.*)")
# A test's line at verbosity 2, `test_x (__main__.Class.test_x) ... ok`.
TEST_LINE = re.compile(r"(?P<method>test\w*) \((?:\w+\.)*?(?P<cls>\w+)\.(?P=method)\)")
RUN_STEP = "##[group]Run python3 scripts/test_safe_push.py"
TIMES_ABOUT = (
    "Seconds each test of scripts/test_safe_push.py took on a GitHub runner, to a tenth of "
    "a second, written by `python3 scripts/test_safe_push.py --times-from-log` from the "
    "times GitHub stamped on the lines of {source} on {date} ({shards} shards, {tests} "
    "tests). Each shard's log is at verbosity 2, and a test's line is written when the "
    "test ends, so a test's time runs from the line before its own to the last line of its "
    "output. setUpModule is the module's setup, the clone of the repository, which every "
    "shard pays once: the median of the shards' setups, each from the shard's report to "
    "the line setUpModule prints when its clone is ready. `--shard K/N` deals the tests "
    "out by these times; a test missing here weighs their median.")


def stamp_seconds(stamp: str, fraction: str | None) -> float:
    moment = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S")
    return moment.replace(tzinfo=datetime.timezone.utc).timestamp() + float(fraction or 0)


def script_runs(lines: list[tuple[float, str]]):
    """The lines of each step of one job's log that runs this script, after its first."""
    run = None
    for stamp, text in lines:
        if text.startswith("##[group]Run ") or text == "Post job cleanup.":
            if run is not None:
                yield run
            run = [] if text.startswith(RUN_STEP) else None
        elif run is not None:
            run.append((stamp, text))
    if run is not None:
        yield run


def shard_times(lines: list[tuple[float, str]]) -> tuple[float, list[tuple[str, float]]]:
    """The setup's seconds and each test's, in the order they ran, from one run of this
    script in a CI log, each line with the time GitHub stamped on it. ValueError when the
    run does not show them: a run cut short, a count that differs from unittest's, or no
    line from setUpModule."""
    starts = [index for index, (_, text) in enumerate(lines) if TEST_LINE.match(text)]
    rule = next((index for index in range(starts[0], len(lines))
                 if re.fullmatch(r"[-=]{70}", lines[index][1])), None)
    ran = next((match for _, text in lines[starts[0]:]
                if (match := re.fullmatch(r"Ran (\d+) tests? in [\d.]+s", text))), None)
    if rule is None or ran is None:
        raise ValueError("the run stops before unittest's summary, so its last test's time "
                         "is unknown.")
    starts = [index for index in starts if index < rule]
    if int(ran[1]) != len(starts):
        raise ValueError(f"unittest ran {ran[1]} tests, but {len(starts)} lines name one.")
    marks = [index for index in range(1, starts[0]) if lines[index][1] == SETUP_DONE]
    if len(marks) != 1:
        raise ValueError(f"not exactly one line '{SETUP_DONE}' before the first test, so "
                         "the setup's time is unknown.")
    setup = lines[marks[0]][0] - lines[marks[0] - 1][0]
    times, before = [], lines[starts[0] - 1][0]
    for start, end in zip(starts, starts[1:] + [rule]):
        block = lines[start:end]
        while len(block) > 1 and not block[-1][1].strip():
            block.pop()  # the blank line unittest writes before its summary
        match = TEST_LINE.match(lines[start][1])
        times.append((f"{match['cls']}.{match['method']}", round(block[-1][0] - before, 1)))
        before = block[-1][0]
    return setup, times


def times_from_logs(logs: dict[str, str], discovered: list[str]) -> dict:
    """The times file, from CI logs by name: each run of this script there with its tests'
    lines, in any job (one job's log, or a whole run's from `gh run view RUN --log`).
    ValueError, naming each fault, unless they give each test of `discovered` once."""
    jobs: dict[tuple[str, str], list[tuple[float, str]]] = {}
    for name, log in logs.items():
        for raw in log.split("\n"):
            line = LOG_LINE.fullmatch(raw.rstrip("\r"))
            if line:
                jobs.setdefault((name, line["job"] or ""), []).append(
                    (stamp_seconds(line["stamp"], line["fraction"]), line["text"]))
    problems, setups, seconds, where, firsts = [], [], {}, {}, []
    for (name, job), lines in jobs.items():
        label = f"{name}, {job}" if job else name
        for run in script_runs(lines):
            if not any(TEST_LINE.match(text) for _, text in run):
                continue  # a step that runs no test, such as the proof
            try:
                setup, times = shard_times(run)
            except ValueError as error:
                problems.append(f"{label}: {error}")
                continue
            setups.append(setup)
            firsts.append(run[0][0])
            for key, value in times:
                if key in seconds:
                    problems.append(f"{key} ran in {where[key]} and again in {label}.")
                seconds[key], where[key] = value, label
    if not setups and not problems:
        problems.append("These logs hold no run of scripts/test_safe_push.py with its tests' "
                        "lines.")
    if not problems:
        problems += [f"{key} has no line in these logs." for key in discovered
                     if key not in seconds]
        problems += [f"{key} ran in {where[key]}, but unittest's loader does not list it here."
                     for key in sorted(set(seconds) - set(discovered))]
    if problems:
        raise ValueError("\n".join(problems))
    pulls = sorted({number for log in logs.values()
                    for number in re.findall(r"refs/remotes/pull/(\d+)/merge", log)})
    first = datetime.datetime.fromtimestamp(min(firsts), datetime.timezone.utc)
    return {"about": TIMES_ABOUT.format(
                source=(f"the CI run of pull request #{pulls[0]}" if len(pulls) == 1
                        else "the CI logs " + ", ".join(logs)),
                date=f"{first.day} {first:%B %Y}", shards=len(setups), tests=len(seconds)),
            "setUpModule": round(statistics.median(setups), 1),
            "tests": dict(sorted(seconds.items()))}


def write_times(data: dict, path: Path = TIMES) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def times_command(logs: list[Path]) -> int:
    """`--times-from-log LOG...`: the times file, written from the shards' CI logs, against
    this checkout's tests as unittest's loader lists them."""
    try:
        data = times_from_logs({str(path): path.read_text(encoding="utf-8", errors="replace")
                                for path in logs},
                               [time_key(test) for test in loaded_tests()])
    except (OSError, ValueError) as error:
        print(f"No times written to scripts/{TIMES.name}:\n{error}", file=sys.stderr)
        return 1
    write_times(data)
    print(f"Wrote scripts/{TIMES.name}: {len(data['tests'])} tests, setUpModule "
          f"{data['setUpModule']} s.")
    return 0


def stand_in_main(*, defaultTest: list[str], testRunner: RanRunner,
                  failing: frozenset[str] = frozenset(), **_) -> None:
    """unittest.main as the Shards tests stub it: each test named, in turn, is a stand-in
    that passes at once, or fails at once if it is among `failing`, run by the runner
    given."""
    class StandIn(unittest.TestCase):
        __module__ = "shard_stand_in"  # no module of that name, so no setUpModule runs

        def __init__(self, key: str):
            super().__init__()
            self.key = key

        def runTest(self):
            if self.key in failing:
                self.fail("planted")

        def id(self):
            return f"{self.__module__}.{self.key}"

        def __str__(self):
            return f"{self.key} (a stand-in, which passes or fails at once)"

    testRunner.run(unittest.TestSuite([StandIn(name) for name in defaultTest]))


# A token of a GitHub expression, in the forms the cadence workflow's conditions use.
EXPRESSION_TOKEN = re.compile(r"\s*(?:(?P<op>&&|\|\||==|!=|!|\(|\))|'(?P<string>[^']*)'"
                              r"|(?P<call>[a-z]+)\(\)|(?P<name>[A-Za-z_][\w.-]*))")


def step_runs(condition: str | None, context: dict[str, str], failed: bool,
              cancelled: bool = False) -> bool:
    """Whether GitHub runs a step whose `if` is `condition`, a step before it having failed
    or not, and the run cancelled or not; or a job, `failed` then saying that a job it
    needs did not succeed. It reads the forms the cadence workflow uses: a status function
    (always(), success(), failure() or cancelled()), or a context's value compared, by ==
    or !=, with a quoted string, ignoring case as GitHub does; joined by &&, || and !, in
    parentheses or not. A condition with no status function holds only when, besides, no
    step before it failed and the run is not cancelled. Any other form, and a context the
    model is not given, is a ValueError."""
    text = (condition or "").strip()
    if text.startswith("${{") and text.endswith("}}"):
        text = text[3:-2].strip()
    tokens, at = [], 0
    while at < len(text):
        match = EXPRESSION_TOKEN.match(text, at)
        if not match:
            raise ValueError(f"a condition this model does not read: {condition!r}")
        tokens.append(next((kind, value) for kind, value in match.groupdict().items()
                           if value is not None))
        at = match.end()
    status = {"always": True, "success": not failed and not cancelled, "failure": failed,
              "cancelled": cancelled}

    def refused():
        return ValueError(f"a condition this model does not read: {condition!r}")

    def either(i: int) -> tuple[bool, int]:
        held, i = both(i)
        while tokens[i:i + 1] == [("op", "||")]:
            right, i = both(i + 1)
            held = held or right
        return held, i

    def both(i: int) -> tuple[bool, int]:
        held, i = negation(i)
        while tokens[i:i + 1] == [("op", "&&")]:
            right, i = negation(i + 1)
            held = held and right
        return held, i

    def negation(i: int) -> tuple[bool, int]:
        if tokens[i:i + 1] == [("op", "!")]:
            held, i = negation(i + 1)
            return not held, i
        return term(i)

    def term(i: int) -> tuple[bool, int]:
        kind, value = tokens[i] if i < len(tokens) else (None, None)
        if (kind, value) == ("op", "("):
            held, i = either(i + 1)
            if tokens[i:i + 1] == [("op", ")")]:
                return held, i + 1
        elif kind == "call" and value in status:
            return status[value], i + 1
        elif (kind == "name" and tokens[i + 1:i + 2] in ([("op", "==")], [("op", "!=")])
              and tokens[i + 2:i + 3] and tokens[i + 2][0] == "string"):
            if value not in context:
                raise ValueError(f"a context this model is not given: {value!r}")
            same = context[value].casefold() == tokens[i + 2][1].casefold()
            return same == (tokens[i + 1][1] == "=="), i + 3
        raise refused()

    held = True
    if tokens:
        held, end = either(0)
        if end != len(tokens):
            raise refused()
    if not any(kind == "call" for kind, _ in tokens):
        held = held and not failed and not cancelled
    return held


def resolved(value, context: dict[str, str]):
    """`value` with each ${{ name }} in it read from `context`, as GitHub reads an env, a
    `with` or a script before the step runs; a value that is not a string, as it is. A
    name the context does not give is a ValueError."""
    if not isinstance(value, str):
        return value

    def read(match) -> str:
        if match[1] not in context:
            raise ValueError(f"a context this model is not given: {match[1]!r}")
        return context[match[1]]
    return re.sub(r"\$\{\{ ([\w.-]+) \}\}", read, value)


def run_steps(steps: list[dict], context: dict[str, str], passes) -> tuple[list[str], str]:
    """A job's steps as GitHub runs them: each step whose condition holds, by step_runs,
    passes, fails or is cancelled as `passes(step, read)` says (True, False or
    "cancelled"), `read` holding its env, its `with` and its script with each ${{ }} read
    from `context`. A step that fails fails the job, unless it may continue on error, and
    a step cancelled cancels it; the steps after it see that, and each step's outcome. The
    steps that ran, each by its id, else its action, else its name, and the job's result:
    success, failure or cancelled. A step with a key this model does not read, or a shell
    but bash, is a ValueError."""
    context, failed, cancelled, ran = dict(context), False, False, []
    for step in steps:
        if set(step) - {"name", "id", "if", "uses", "with", "run", "env", "shell",
                        "continue-on-error"} or step.get("shell", "bash") != "bash":
            raise ValueError(f"a step this model does not read: {step!r}")
        outcome = "skipped"
        if step_runs(step.get("if"), context, failed, cancelled):
            ran.append(step.get("id") or step.get("uses") or step["name"])
            read = {"env": {name: resolved(text, context)
                            for name, text in step.get("env", {}).items()},
                    "with": {name: resolved(text, context)
                             for name, text in step.get("with", {}).items()},
                    "run": resolved(step.get("run"), context)}
            verdict = passes(step, read)
            outcome = ("cancelled" if verdict == "cancelled"
                       else "success" if verdict is True else "failure")
            cancelled = cancelled or outcome == "cancelled"
            failed = failed or (outcome == "failure" and step.get("continue-on-error") is not True)
        if "id" in step:
            context[f"steps.{step['id']}.outcome"] = outcome
    return ran, "cancelled" if cancelled else "failure" if failed else "success"


def run_workflow(jobs: dict, context: dict[str, str], runner,
                 given: dict[str, str]) -> dict[str, str]:
    """A workflow's jobs as GitHub runs them, each after the jobs it needs, which come
    before it: a job in `given` ends as it says; another is skipped when its `if` does not
    hold, by step_runs over the results of the jobs it needs (`failed` saying that one did
    not succeed), and otherwise runs its steps by run_steps, once for each value of its
    matrix's one dimension when it has one, each run with that value as matrix.<name>, the
    count as strategy.job-total, and `runner.temp(job, value)` as its runner.temp, while
    `runner.passes(job, value, step, read)` says how each step ends. A matrix's result,
    which the jobs that need it read, is failure when a run failed, else cancelled when one
    was cancelled, else success. Each job's result, by id."""
    results: dict[str, str] = {}
    for job_id, job in jobs.items():
        needs = job.get("needs", [])
        needs = [needs] if isinstance(needs, str) else list(needs)
        if any(need not in results for need in needs):
            raise ValueError(f"{job_id} needs a job that does not come before it")
        if job_id in given:
            results[job_id] = given[job_id]
            continue
        here = dict(context, **{f"needs.{need}.result": results[need] for need in needs})
        if not step_runs(job.get("if"), here, any(results[need] != "success" for need in needs)):
            results[job_id] = "skipped"
            continue
        matrix = job.get("strategy", {}).get("matrix")
        [(dimension, values)] = matrix.items() if matrix else [(None, [None])]
        ends = []
        for value in values:
            run = dict(here, **{"runner.temp": str(runner.temp(job_id, value))})
            if dimension is not None:
                run.update({f"matrix.{dimension}": str(value),
                            "strategy.job-total": str(len(values))})
            ends.append(run_steps(job["steps"], run, lambda step, read, value=value:
                                  runner.passes(job_id, value, step, read))[1])
        results[job_id] = ("failure" if "failure" in ends
                           else "cancelled" if "cancelled" in ends else "success")
    return results


def conclusion(results: dict[str, str]) -> str:
    """A run's conclusion from its jobs' results: failure when a job failed, else
    cancelled when one was cancelled, else success, a skipped job counting for neither."""
    ends = set(results.values())
    return "failure" if "failure" in ends else "cancelled" if "cancelled" in ends else "success"


REPORT_TITLE = "safe-push-tests: the cadence run on main is red"
# A stand-in for gh in the report's step: the issues read gives one open issue labelled
# blocks-release, of the report's title, when OPEN_ISSUE names its number, and none
# otherwise; `issue create` and `issue comment` keep their body. Each call is kept.
REPORT_GH = r'''#!/bin/sh
printf '%s\n' "$*" >> "$GH_CALLS"
if [ "$1" = api ]; then
  if [ -n "$OPEN_ISSUE" ]; then
    printf '[[{"number": %s, "title": "%s"}]]\n' "$OPEN_ISSUE" "$REPORT_TITLE"
  else
    echo '[[]]'
  fi
  exit 0
fi
if [ "$1" = issue ] && { [ "$2" = create ] || [ "$2" = comment ]; }; then
  while [ $# -gt 0 ]; do
    if [ "$1" = --body-file ]; then cp "$2" "$GH_BODY"; fi
    shift
  done
  exit 0
fi
exit 1
'''


class CadenceRun:
    """Runs of the cadence workflow, as run_workflow drives them, with stand-ins for what
    GitHub and the jobs do. A shard runs run_shard by the command its step gives, each
    test a stand-in that passes at once, or fails if among `failing`, and tee's log holds
    what it said; a shard among `cancelled` is cancelled as its tests start. The proof is
    cover_command, by the command its step gives. The verdict's and the report's scripts
    run under bash, as GitHub runs them, the report's with a stand-in for gh. Artifacts are
    kept by name in a folder that every attempt of the run shares, the case in which a
    rerun could see an earlier attempt's lists (whether GitHub's fetch does is not
    tried, and nothing relies on it), and fetched by pattern, each into a folder of its own; an artifact among `lost` is
    kept and then lost. negative-tests and formal-model-kernel, which need Lean, end as
    `given` says, success unless it says otherwise."""

    def __init__(self, root: Path):
        self.root, self.attempt = root, 0
        self.artifacts = root / "artifacts"
        self.artifacts.mkdir()

    def run(self, *, failing=frozenset(), cancelled=frozenset(), lost=frozenset(),
            open_issue: int | None = None, given: dict[str, str] | None = None) -> dict[str, str]:
        """One attempt of the run, on main, every job of the workflow: each job's result."""
        self.attempt += 1
        self.failing, self.cancelled, self.lost = failing, cancelled, lost
        self.open_issue = open_issue
        self.said: dict[str, str] = {}
        self.calls: list[str] = []
        self.body: str | None = None
        context = {"github.ref": "refs/heads/main", "github.token": "x",
                   "github.repository": "owner/repo", "github.server_url": "https://github.invalid",
                   "github.run_id": "1", "github.sha": "0" * 40}
        return run_workflow(ci_jobs(), context, self, {
            "negative-tests": "success", "formal-model-kernel": "success", **(given or {})})

    def temp(self, job: str, value) -> Path:
        path = self.root / f"attempt-{self.attempt}" / f"{job}-{value}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def passes(self, job: str, value, step: dict, read: dict):
        uses, script, temp = step.get("uses", ""), read["run"] or "", self.temp(job, value)
        if uses.startswith(("actions/checkout@", "actions/setup-python@")) \
                or script == "python3 -m pip install -r scripts/requirements-test_safe_push.txt":
            return True
        if uses.startswith("actions/upload-artifact@"):
            return self.upload(read["with"])
        if uses.startswith("actions/download-artifact@"):
            return self.download(read["with"])
        if "scripts/test_safe_push.py --shard" in script:
            return self.shard(value, script, temp)
        if "scripts/test_safe_push.py --cover" in script:
            return self.cover(script, temp)
        if step.get("id") == "verdict":
            return self.bash("verdict", ["-e"], script, read["env"], temp)
        if job == safe_push.SUITE_REPORT_JOB and step.get("shell") == "bash":
            return self.report(script, read["env"], temp)
        raise AssertionError(f"a step of {job} this stand-in does not run: {step!r}")

    def command(self, line: str, temp: Path) -> tuple:
        argv = shlex.split(line.replace("$RUNNER_TEMP", str(temp)))
        if argv[:2] != ["python3", "scripts/test_safe_push.py"]:
            raise AssertionError(f"not a run of this script: {line!r}")
        return script_command(argv[2:])

    def shard(self, value, script: str, temp: Path):
        if value in self.cancelled:
            return "cancelled"
        lines = [line for line in script.splitlines() if line.strip()]
        if len(lines) != 2 or lines[0] != "set -o pipefail" or lines[1].count(" 2>&1 | tee ") != 1:
            raise AssertionError(f"a shard's script this stand-in does not run: {script!r}")
        line, tee = lines[1].split(" 2>&1 | tee ")
        kind, shard, count, ran = self.command(line, temp)
        said, code = io.StringIO(), None
        with mock.patch.object(unittest, "main", side_effect=lambda **kwargs: stand_in_main(
                failing=self.failing, **kwargs)), contextlib.redirect_stderr(said):
            try:
                run_shard(shard, count, ran)
            except SystemExit as stopped:
                code = stopped.code
        [log] = shlex.split(tee.replace("$RUNNER_TEMP", str(temp)))
        Path(log).write_text(said.getvalue())
        return kind == "shard" and code == 0

    def cover(self, script: str, temp: Path) -> bool:
        kind, directory = self.command(script.strip(), temp)
        said = io.StringIO()
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cover_command(directory)
        self.said["cover"] = said.getvalue()
        return kind == "cover" and code == 0

    def upload(self, given: dict) -> bool:
        name, source = given["name"], Path(given["path"])
        if not source.is_file():
            return given.get("if-no-files-found", "warn") != "error"
        kept = self.artifacts / name
        if kept.exists() and given.get("overwrite") is not True:
            return False
        shutil.rmtree(kept, ignore_errors=True)
        if name not in self.lost:
            kept.mkdir()
            shutil.copy(source, kept / source.name)
        return True

    def download(self, given: dict) -> bool:
        for kept in sorted(self.artifacts.iterdir()):
            if fnmatch.fnmatchcase(kept.name, given["pattern"]):
                shutil.copytree(kept, Path(given["path"]) / kept.name)
        return True

    def bash(self, name: str, flags: list[str], script: str, env: dict, temp: Path,
             path: str = "") -> bool:
        r = subprocess.run(["bash", "--noprofile", "--norc", *flags, "-c", script],
                           capture_output=True, text=True,
                           env={"PATH": path + os.environ["PATH"], "RUNNER_TEMP": str(temp), **env})
        self.said[name] = r.stdout + r.stderr
        return r.returncode == 0

    def report(self, script: str, env: dict, temp: Path) -> bool:
        tools = temp / "bin"
        tools.mkdir()
        (tools / "gh").write_text(REPORT_GH)
        (tools / "gh").chmod(0o755)
        calls, body = temp / "gh-calls", temp / "gh-body.md"
        passed = self.bash("report", ["-eo", "pipefail"], script, dict(
            env, GH_CALLS=str(calls), GH_BODY=str(body), OPEN_ISSUE=str(self.open_issue or ""),
            REPORT_TITLE=REPORT_TITLE), temp, path=f"{tools}{os.pathsep}")
        self.calls = calls.read_text().splitlines() if calls.exists() else []
        self.body = body.read_text() if body.exists() else None
        return passed


class Shards(unittest.TestCase):
    """The cadence workflow's shards of this suite and the job that gathers them (#233),
    without git or network: the shards of its matrix hold every test once, a test the
    times do not name among them; each shard lists the tests it ran, and the proof over
    those lists names each test not run once and each list missing; the times are read
    from a CI log; safe-push-tests passes only when every shard succeeded and the proof
    holds; and a run in which a shard's test fails, a shard's list is missing, or a shard
    is cancelled or skipped is red, and reported."""

    def jobs(self) -> dict:
        return ci_jobs()

    def ci_shard_count(self) -> int:
        return ci_shard_count(self.jobs())

    def run_every_shard(self, count: int, directory: Path,
                        failing: frozenset[str] = frozenset()) -> tuple[list[list[str]], list[str]]:
        """`--shard K/count --ran directory/ran-K.json` for each K, unittest.main stubbed so
        that each test named is a stand-in that passes at once, or fails if it is among
        `failing`, its shard then exiting 1: the names each shard handed unittest, and what
        each said before it ran."""
        dealt, said = [], []
        for shard in range(1, count + 1):
            err = io.StringIO()
            with mock.patch.object(unittest, "main", side_effect=lambda **kwargs: stand_in_main(
                    failing=failing, **kwargs)) as main, \
                    contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as stopped:
                run_shard(shard, count, directory / f"ran-{shard}.json")
            names = main.call_args.kwargs["defaultTest"]
            self.assertEqual(stopped.exception.code, 1 if failing & set(names) else 0,
                             err.getvalue())
            self.assertIs(main.call_args.kwargs["exit"], False)
            dealt.append(names)
            said.append(err.getvalue())
        return dealt, said

    def gather(self, shards: str,
               failing: frozenset[str] = frozenset()) -> tuple[list[str], str, str]:
        """safe-push-tests as GitHub runs it after shards that ended `shards`: each step by
        run_steps, those in `failing` failing, the others passing, and the verdict's script
        run by bash, as GitHub runs a step's script on Linux, stopping at the first failure.
        The steps that ran, the job's result, and what the verdict said."""
        said = []

        def passes(step: dict, read: dict) -> bool:
            if step.get("id") != "verdict":
                return (step.get("id") or step.get("uses")) not in failing
            r = subprocess.run(["bash", "-e", "-c", read["run"]], capture_output=True,
                               text=True, env={"PATH": os.environ["PATH"], **read["env"]})
            said.append(r.stdout + r.stderr)
            return r.returncode == 0

        ran, result = run_steps(self.jobs()[GATHER_JOB]["steps"], {
            f"needs.{SHARD_JOB}.result": shards, "runner.temp": "RUNNER_TEMP"}, passes)
        return ran, result, "".join(said)

    def shard_context(self, shard: int) -> dict[str, str]:
        return {"matrix.shard": str(shard), "strategy.job-total": str(self.ci_shard_count()),
                "runner.temp": "RUNNER_TEMP"}

    def test_ci_shards_hold_every_test_once(self):
        # What `--shard K/N --ran FILE` hands unittest.main, for each K of the N in CI's
        # matrix, and lists as run: each test of the loader's list once, in the loader's
        # order. The proof over those lists, all of them complete, passes.
        count = self.ci_shard_count()
        keys = [time_key(test) for test in loaded_tests()]
        self.assertIn("Shards.test_ci_shards_hold_every_test_once", keys)
        with tempfile.TemporaryDirectory() as tmp:
            dealt, _ = self.run_every_shard(count, Path(tmp))
            for shard, names in enumerate(dealt, 1):
                self.assertTrue(names, f"shard {shard} runs no test")
                self.assertEqual(names, [key for key in keys if key in set(names)])
                self.assertEqual(json.loads((Path(tmp) / f"ran-{shard}.json").read_text()),
                                 {"shard": shard, "count": count,
                                  "ran": [[name, "ok"] for name in names]})
            self.assertEqual(cover(Path(tmp), count, keys), [])
        self.assertEqual(sorted(key for names in dealt for key in names), sorted(keys))
        setup, times = load_times()
        plan = shard_plan(keys, count, times, setup)
        for shard, names in enumerate(dealt, 1):
            self.assertAlmostEqual(plan.loads[shard - 1], setup + sum(
                times.get(key, plan.median) for key in names))

    def test_a_test_missing_from_the_times_runs_in_one_shard(self):
        # The new test runs: a test a later train adds, or renames, which the times file
        # does not name, is dealt to one shard, which hands it to unittest, lists it as run
        # and names it in its log; and the proof, whose loader lists it too, passes.
        class Planted(unittest.TestCase):
            def test_added_by_a_later_train(self):
                pass

        planted = "Planted.test_added_by_a_later_train"
        count = self.ci_shard_count()
        self.assertNotIn(planted, load_times()[1])
        with mock.patch.object(sys.modules[__name__], "Planted", Planted, create=True), \
                tempfile.TemporaryDirectory() as tmp:
            keys = [time_key(test) for test in loaded_tests()]
            self.assertIn(planted, keys)
            dealt, said = self.run_every_shard(count, Path(tmp))
            [shard] = [shard for shard, names in enumerate(dealt, 1) if planted in names]
            self.assertIn([planted, "ok"], json.loads(
                (Path(tmp) / f"ran-{shard}.json").read_text())["ran"])
            for text in said:
                self.assertIn(f"No measured time for {planted} ", text)
            self.assertEqual(cover(Path(tmp), count, keys), [])
        self.assertNotIn(planted, [time_key(test) for test in loaded_tests()])

    def test_a_failing_shard_keeps_its_list_and_the_proof_names_the_test(self):
        # A shard one of whose tests fails exits 1, having written its list with that
        # test's outcome; the proof over every list, the others complete, names it.
        count = self.ci_shard_count()
        keys = [time_key(test) for test in loaded_tests()]
        failed = "Shards.test_a_failing_shard_keeps_its_list_and_the_proof_names_the_test"
        with tempfile.TemporaryDirectory() as tmp:
            dealt, _ = self.run_every_shard(count, Path(tmp), frozenset({failed}))
            [shard] = [shard for shard, names in enumerate(dealt, 1) if failed in names]
            self.assertIn([failed, "FAIL"], json.loads(
                (Path(tmp) / f"ran-{shard}.json").read_text())["ran"])
            self.assertEqual(cover(Path(tmp), count, keys),
                             [f"{failed} did not pass in shard {shard}: FAIL."])

    def test_the_proof_names_each_test_not_run_once_and_each_list_missing(self):
        # Each list complete, then one fault planted in a copy of them: the dropped one, a
        # test the loader lists that no shard ran; a test two shards ran, or one ran twice;
        # a test the loader does not list; one that failed; a shard's list missing, as a
        # shard that stopped before its end leaves it; and a list too many or not a list.
        count = self.ci_shard_count()
        keys = [time_key(test) for test in loaded_tests()]

        def left_no_list(shard: int) -> str:
            return (f"Shard {shard} of {count} left no list of the tests it ran: it stopped "
                    "before its end, or its list was not kept.")

        with tempfile.TemporaryDirectory() as tmp:
            whole = Path(tmp) / "whole"
            dealt, _ = self.run_every_shard(count, whole)
            self.assertEqual(cover(whole, count, keys), [])

            def planted(case: str, change) -> tuple[Path, list[str]]:
                directory = Path(tmp) / case
                shutil.copytree(whole, directory)
                change(directory)
                return directory, cover(directory, count, keys)

            def edit(shard: int, change):
                def apply(directory: Path):
                    path = directory / f"ran-{shard}.json"
                    data = json.loads(path.read_text())
                    change(data["ran"])
                    path.write_text(json.dumps(data))
                return apply

            first, second = dealt[0][0], dealt[1][0]
            self.assertEqual(planted("dropped", edit(2, lambda ran: ran.pop(0)))[1],
                             [f"{second} ran in no shard."])
            self.assertEqual(
                planted("in two shards", edit(3, lambda ran: ran.append([first, "ok"])))[1],
                [f"{first} ran 2 times: by shard 1 and shard 3."])
            self.assertEqual(
                planted("twice in one", edit(1, lambda ran: ran.append([first, "ok"])))[1],
                [f"{first} ran 2 times: by shard 1 and shard 1."])
            self.assertEqual(planted("unknown", edit(count, lambda ran: ran.append(
                ["Renamed.test_old_name", "ok"])))[1],
                [f"Renamed.test_old_name ran in shard {count}, but unittest's loader does "
                 "not list it here."])
            for word in ("FAIL", "ERROR", "unexpected success", "unfinished"):
                self.assertEqual(
                    planted(f"failed {word}",
                            edit(2, lambda ran, word=word: ran[0].__setitem__(1, word)))[1],
                    [f"{second} did not pass in shard 2: {word}."])
            self.assertEqual(
                planted("a list missing", lambda directory: (directory / "ran-4.json").unlink())[1],
                [left_no_list(4)] + [f"{key} ran in no shard." for key in keys
                                     if key in dealt[3]])

            def beyond(directory: Path):
                (directory / "ran-extra.json").write_text(json.dumps(
                    {"shard": count + 1, "count": count + 1, "ran": []}))
            directory, problems = planted("beyond the matrix", beyond)
            self.assertEqual(problems, [f"{directory / 'ran-extra.json'} is the list of shard "
                                        f"{count + 1} of {count + 1}, but CI's matrix has "
                                        f"{count} shards."])
            directory, problems = planted(
                "not a list", lambda directory: (directory / "stray.txt").write_text("ok\n"))
            self.assertEqual(problems, [f"{directory / 'stray.txt'} is not a shard's list of "
                                        "the tests it ran."])

            def again(directory: Path):
                (directory / "again").mkdir()
                shutil.copy(directory / "ran-1.json", directory / "again")
            directory, problems = planted("two lists for one shard", again)
            self.assertEqual(problems, [f"Shard 1 left two lists, {directory / 'again/ran-1.json'}"
                                        f" and {directory / 'ran-1.json'}."])
            nothing = [left_no_list(shard) for shard in range(1, count + 1)] + [
                f"{key} ran in no shard." for key in keys]
            (Path(tmp) / "empty").mkdir()
            self.assertEqual(cover(Path(tmp) / "empty", count, keys), nothing)
            self.assertEqual(cover(Path(tmp) / "absent", count, keys), nothing)

    def test_the_list_of_what_ran_gives_each_tests_outcome(self):
        # The list a shard writes, from what unittest ran: each test with its outcome, a
        # failing subtest failing its test; a class whose fixture failed ran no test.
        class Outcomes(unittest.TestCase):
            def test_a_pass(self):
                pass

            def test_b_failure(self):
                self.fail("planted")

            def test_c_error(self):
                raise RuntimeError("planted")

            @unittest.skip("planted")
            def test_d_skip(self):
                pass

            @unittest.expectedFailure
            def test_e_expected_failure(self):
                self.fail("planted")

            @unittest.expectedFailure
            def test_f_unexpected_success(self):
                pass

            def test_g_a_subtest_fails(self):
                for number in (1, 2, 3):
                    with self.subTest(number=number):
                        if number == 3:
                            self.skipTest("planted")
                        self.assertEqual(number, 1)

            def test_h_subtests_pass(self):
                with self.subTest(number=1):
                    pass

        class Unready(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise RuntimeError("planted")

            def test_never_runs(self):
                pass

        for case in (Outcomes, Unready):
            case.__module__ = "shard_stand_in"  # no module of that name, so no setUpModule
        runner = RanRunner(stream=io.StringIO())
        runner.run(unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case)
                                      for case in (Outcomes, Unready)))
        self.assertEqual(runner.result.ran, [
            ["Outcomes.test_a_pass", "ok"], ["Outcomes.test_b_failure", "FAIL"],
            ["Outcomes.test_c_error", "ERROR"], ["Outcomes.test_d_skip", "skipped"],
            ["Outcomes.test_e_expected_failure", "expected failure"],
            ["Outcomes.test_f_unexpected_success", "unexpected success"],
            ["Outcomes.test_g_a_subtest_fails", "FAIL"], ["Outcomes.test_h_subtests_pass", "ok"]])
        self.assertFalse(runner.result.wasSuccessful())
        self.assertEqual(len(runner.result.errors), 2, "test_c_error, and Unready's fixture")

    def test_the_count_of_shards_is_read_from_the_matrix(self):
        def jobs(matrix) -> dict:
            return {SHARD_JOB: {"strategy": {"matrix": matrix}}}

        self.assertEqual(ci_shard_count(jobs({"shard": [1, 2, 3]})), 3)
        for matrix in ({"shard": [1]}, {"shard": [2, 3]}, {"shard": [1, 3]},
                       {"shard": [1, 1, 2]}, {"shard": [True, 2]}, {"shard": [1, 2.0]},
                       {"shard": [1, 2], "include": [{"shard": 3}]},
                       {"shard": [1, 2], "os": ["ubuntu-latest"]}, {"shard": "1, 2"},
                       "${{ fromJSON('[1, 2]') }}"):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                ci_shard_count(jobs(matrix))

    def test_a_test_with_no_measured_time_is_still_dealt(self):
        setup, times = load_times()
        keys = [time_key(test) for test in loaded_tests()]
        dropped = sorted(set(keys) & set(times))[0]
        fewer = {key: value for key, value in times.items() if key != dropped}
        plan = shard_plan(keys + ["Later.test_added"], 7, fewer, setup)
        self.assertEqual(plan.unmeasured, tuple(sorted(
            set(keys) - set(times) | {dropped, "Later.test_added"})))
        self.assertEqual(plan.median, statistics.median(fewer.values()))
        self.assertEqual(sorted(plan.shard_of), sorted(keys + ["Later.test_added"]))
        for key in plan.unmeasured:
            self.assertIn(plan.shard_of[key], range(1, 8))
            for shard in range(1, 8):
                self.assertIn(f"No measured time for {key} ", "\n".join(shard_report(plan, shard)))
        self.assertEqual(shard_plan(["A.test_one"], 2, {}, 0.0).shard_of, {"A.test_one": 1})

    def test_the_dealing_is_deterministic(self):
        setup, times = load_times()
        keys = [time_key(test) for test in loaded_tests()]
        count = self.ci_shard_count()
        plan = shard_plan(keys, count, times, setup)
        self.assertEqual(shard_plan(list(reversed(keys)), count,
                                    dict(reversed(list(times.items()))), setup), plan)
        # Ties go by name, then to the shard with the least time, the fewest tests, and the
        # lowest number: tests that weigh nothing are spread, not heaped on the first shard.
        tied = shard_plan(["C.test", "A.test", "B.test", "D.test"], 2,
                          {"A.test": 1.0, "B.test": 1.0, "C.test": 0.0, "D.test": 0.0}, 0.0)
        self.assertEqual(tied.shard_of, {"A.test": 1, "B.test": 2, "C.test": 1, "D.test": 2})

    def test_the_command_line(self):
        self.assertIsNone(script_command([]))
        self.assertIsNone(script_command(["Units"]))
        self.assertIsNone(script_command(["Units.test_sections", "Shards"]))
        self.assertEqual(script_command(["--shard", "3/7"]), ("shard", 3, 7, None))
        self.assertEqual(script_command(["--shard", "3/7", "--ran", "ran-3.json"]),
                         ("shard", 3, 7, Path("ran-3.json")))
        self.assertEqual(script_command(["--cover", "lists"]), ("cover", Path("lists")))
        self.assertEqual(script_command(["--times-from-log", "a.log", "b.log"]),
                         ("times", [Path("a.log"), Path("b.log")]))
        for argv in (["--shard"], ["--shard", "0/7"], ["--shard", "8/7"], ["--shard", "3"],
                     ["--shard", "3/7", "Units"], ["Units", "--shard", "3/7"],
                     ["--shard=3/7"], ["--shard", "-1/7"], ["--shard", "3/7", "--ran"],
                     ["--shard", "3/7", "--ran", "--cover"], ["--shard", "3/7", "--ran", ""],
                     ["--shard", "3/7", "--ran", "a", "b"], ["--shard", "3/7", "--cover", "a"],
                     ["--ran", "ran-3.json"], ["--ran", "ran-3.json", "--shard", "3/7"],
                     ["--cover"], ["--cover", "a", "b"], ["--cover", "--shard"],
                     ["Units", "--cover", "lists"], ["--cover=lists"], ["--times-from-log"],
                     ["--times-from-log", "a.log", "--cover", "lists"],
                     ["--times-from-log", ""]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit) as stopped:
                    script_command(argv)
                self.assertEqual(stopped.exception.code, 2)

    def test_the_times_from_a_ci_log(self):
        # A few lines in the form of a CI log as `gh run view RUN --log` gives it: two
        # shards, each with setUpModule's line, and a test whose output takes two lines;
        # the step of the proof, which runs no test, and another job's tests, which are
        # not this script's. A job's own log, without the job and step, reads the same.
        def job(name: str, lines: list[str]) -> list[str]:
            return [f"{name}\tUNKNOWN STEP\t{line}" for line in lines]

        rule = "-" * 70
        one = job("safe-push-shards (1)", [
            "﻿2026-10-21T20:39:17.6326931Z Current runner version: '2.338.0'",
            "2026-10-21T20:39:18.1000000Z [command]/usr/bin/git checkout --progress --force "
            "refs/remotes/pull/239/merge",
            "2026-10-21T20:39:22.2694272Z ##[group]Run python3 scripts/test_safe_push.py "
            '--shard 1/7 --ran "$RUNNER_TEMP/ran-1.json"',
            "2026-10-21T20:39:22.2743253Z shell: /usr/bin/bash -e {0}",
            "2026-10-21T20:39:22.2745639Z ##[endgroup]",
            "2026-10-21T20:39:23.0000000Z Shard 1 of 7: 2 of 4 tests, about 22 s by the times "
            "measured on a GitHub runner, the module's setup included.",
            f"2026-10-21T20:39:28.5000000Z {SETUP_DONE}",
            "2026-10-21T20:39:39.0860550Z test_good_commit_dry_run_then_push_from_a_dirty_tree "
            "(__main__.Accepts.test_good_commit_dry_run_then_push_from_a_dirty_tree) ... ok",
            "2026-10-21T20:39:39.2395058Z test_nothing_to_push "
            "(__main__.Accepts.test_nothing_to_push) ... ok",
            "2026-10-21T20:39:39.6935317Z ",
            f"2026-10-21T20:39:39.6935985Z {rule}",
            "2026-10-21T20:39:39.6936467Z Ran 2 tests in 16.420s",
            "2026-10-21T20:39:39.6936649Z ",
            "2026-10-21T20:39:39.6936747Z OK",
            "2026-10-21T20:39:39.7276141Z Post job cleanup."])
        two = job("safe-push-shards (2)", [
            "2026-10-21T20:39:24.0000000Z ##[group]Run python3 scripts/test_safe_push.py "
            '--shard 2/7 --ran "$RUNNER_TEMP/ran-2.json"',
            "2026-10-21T20:39:24.0100000Z ##[endgroup]",
            "2026-10-21T20:39:25.0000000Z Shard 2 of 7: 2 of 4 tests, about 205 s by the "
            "times measured on a GitHub runner, the module's setup included.",
            f"2026-10-21T20:39:31.1000000Z {SETUP_DONE}",
            "2026-10-21T20:39:33.0000000Z test_a_bare_top_level_directory_ends_no_sentence "
            "(__main__.DecisionEntries.test_a_bare_top_level_directory_ends_no_sentence) ... "
            "a line the test wrote",
            "2026-10-21T20:39:36.6000000Z ok",
            "2026-10-21T20:42:47.9927230Z test_full_sequence_on_a_good_commit "
            "(__main__.FullChecks.test_full_sequence_on_a_good_commit) ... skipped 'the full "
            "checks need Lean and take minutes: STOICHEIA_SLOW_TESTS=1'",
            "2026-10-21T20:42:48.3000000Z ",
            f"2026-10-21T20:42:48.3000100Z {rule}",
            "2026-10-21T20:42:48.3000200Z Ran 2 tests in 197.000s",
            "2026-10-21T20:42:48.3000300Z ",
            "2026-10-21T20:42:48.3000400Z OK (skipped=1)",
            "2026-10-21T20:42:48.4000000Z ##[group]Run actions/upload-artifact@v5"])
        others = job("safe-push-tests", [
            "2026-10-21T20:43:30.0000000Z ##[group]Run python3 scripts/test_safe_push.py "
            '--cover "$RUNNER_TEMP/safe-push-ran"',
            "2026-10-21T20:43:30.0100000Z ##[endgroup]",
            "2026-10-21T20:43:31.0000000Z Each of the 4 tests unittest's loader lists here "
            "ran once, in one of the 7 shards: 3 ok, 1 skipped."]) + job("acceptance", [
            "2026-10-21T20:40:00.0000000Z ##[group]Run python3 -I tests/test_check_acceptance.py",
            "2026-10-21T20:40:01.0000000Z test_compare (__main__.Compare.test_compare) ... ok"])
        keys = ["Accepts.test_good_commit_dry_run_then_push_from_a_dirty_tree",
                "Accepts.test_nothing_to_push",
                "DecisionEntries.test_a_bare_top_level_directory_ends_no_sentence",
                "FullChecks.test_full_sequence_on_a_good_commit"]

        def times(lines: list[str], discovered: list[str] = keys) -> dict:
            return times_from_logs({"run.log": "\n".join(lines) + "\n"}, discovered)

        data = times(two + others + one)
        self.assertEqual(data["tests"], {keys[0]: 10.6, keys[1]: 0.2, keys[2]: 5.5,
                                         keys[3]: 191.4})
        self.assertEqual(data["setUpModule"], 5.8)
        self.assertIn("the CI run of pull request #239 on 21 October 2026 (2 shards, 4 tests)",
                      data["about"])
        with tempfile.TemporaryDirectory() as tmp:
            write_times(data, Path(tmp) / "times.json")
            self.assertEqual(load_times(Path(tmp) / "times.json"), (5.8, data["tests"]))
        alone = times_from_logs({"job.txt": "\n".join(line.split("\t", 2)[2] for line in one)},
                                keys[:2])
        self.assertEqual((alone["setUpModule"], alone["tests"]),
                         (5.5, {keys[0]: 10.6, keys[1]: 0.2}))

        def refused(lines: list[str], discovered: list[str] = keys) -> str:
            with self.assertRaises(ValueError) as caught:
                times(lines, discovered)
            return str(caught.exception)

        label = "run.log, safe-push-shards"
        self.assertEqual(refused([line.replace("Ran 2 tests", "Ran 3 tests") for line in one]
                                 + two),
                         f"{label} (1): unittest ran 3 tests, but 2 lines name one.")
        self.assertEqual(refused(one + [line for line in two if SETUP_DONE not in line]),
                         f"{label} (2): not exactly one line '{SETUP_DONE}' before the first "
                         "test, so the setup's time is unknown.")
        self.assertEqual(refused(one[:9] + two), f"{label} (1): the run stops before "
                         "unittest's summary, so its last test's time is unknown.")
        self.assertEqual(refused(one + two + [line.replace("(1)", "(3)") for line in one]),
                         f"{keys[0]} ran in {label} (1) and again in {label} (3).\n"
                         f"{keys[1]} ran in {label} (1) and again in {label} (3).")
        self.assertEqual(refused(one + two, keys + ["Later.test_added"]),
                         "Later.test_added has no line in these logs.")
        self.assertEqual(refused(one + two, keys[1:]), f"{keys[0]} ran in {label} (1), but "
                         "unittest's loader does not list it here.")
        self.assertEqual(refused(others), "These logs hold no run of scripts/test_safe_push.py "
                         "with its tests' lines.")

    def test_every_shard_runs_its_part_of_the_suite(self):
        jobs = self.jobs()
        job = jobs[SHARD_JOB]
        self.ci_shard_count()
        self.assertEqual(list(jobs)[0], SHARD_JOB)
        self.assertFalse({"name", "needs", "if", "continue-on-error"} & set(job))
        self.assertEqual(job["strategy"]["fail-fast"], False)
        self.assertEqual(job["permissions"], {"contents": "read"})
        self.assertEqual(job["timeout-minutes"], 60)
        # Each shard runs the commit the workflow runs, with the whole history; runs its
        # part, pipefail keeping the tests' status through tee, which keeps its output in a
        # log of its own; lists the tests it ran; and keeps the list and the log under names
        # of their own, for 35 days, beyond the 30 in which GitHub lets a run's failed jobs
        # be run again, which reruns no shard that passed: a shard that stops before its
        # end lists nothing, and keeps no list.
        self.assertEqual([{key: value for key, value in step.items() if key != "name"}
                          for step in job["steps"]], [
            {"uses": "actions/checkout@v5",
             "with": {"fetch-depth": 0, "persist-credentials": False}},
            {"uses": "actions/setup-python@v5", "with": {"python-version": "3.12"}},
            {"run": "python3 -m pip install -r scripts/requirements-test_safe_push.txt"},
            {"run": "set -o pipefail\n"
                    "python3 scripts/test_safe_push.py "
                    "--shard ${{ matrix.shard }}/${{ strategy.job-total }} "
                    '--ran "$RUNNER_TEMP/ran-${{ matrix.shard }}.json" 2>&1 '
                    '| tee "$RUNNER_TEMP/test_safe_push-${{ matrix.shard }}.log"\n'},
            {"if": "always()", "uses": "actions/upload-artifact@v5",
             "with": {"name": "safe-push-ran-${{ matrix.shard }}",
                      "path": "${{ runner.temp }}/ran-${{ matrix.shard }}.json",
                      "if-no-files-found": "error", "retention-days": 35, "overwrite": True}},
            {"if": "always()", "uses": "actions/upload-artifact@v5",
             "with": {"name": "test_safe_push-log-${{ matrix.shard }}",
                      "path": "${{ runner.temp }}/test_safe_push-${{ matrix.shard }}.log",
                      "if-no-files-found": "ignore", "retention-days": 35, "overwrite": True}}])
        # A shard whose tests fail, having written its list, still keeps it and its log,
        # and fails.
        tests = job["steps"][3]
        for failing in (None, tests):
            with self.subTest(tests_fail=failing is not None):
                ran, result = run_steps(job["steps"], self.shard_context(1),
                                        lambda step, read: step is not failing)
                self.assertEqual(ran[-2:], ["actions/upload-artifact@v5"] * 2)
                self.assertEqual(len(ran), len(job["steps"]))
                self.assertEqual(result, "success" if failing is None else "failure")
        ran, result = run_steps(job["steps"], self.shard_context(1),
                                lambda step, read: step is not job["steps"][0])
        self.assertEqual(ran, ["actions/checkout@v5"] + ["actions/upload-artifact@v5"] * 2)
        self.assertEqual(result, "failure")

    def test_safe_push_tests_proves_from_what_the_shards_ran(self):
        # Whatever the shards' result, before the verdict on it: the commit the shards ran,
        # checked out as they checked it out, every shard's list fetched, and the proof run
        # over them once the parser is in, whether or not the fetch failed. Each shard's
        # list, and each shard's log, which the report fetches, has a name its fetch's
        # pattern matches, and no other artifact's name matches that pattern.
        jobs = self.jobs()
        steps = jobs[GATHER_JOB]["steps"]
        self.assertEqual(steps[0]["with"], jobs[SHARD_JOB]["steps"][0]["with"])
        self.assertEqual([{key: value for key, value in step.items() if key != "name"}
                          for step in steps[:-1]], [
            {"uses": "actions/checkout@v5",
             "with": {"fetch-depth": 0, "persist-credentials": False}},
            {"uses": "actions/setup-python@v5", "with": {"python-version": "3.12"}},
            {"id": "install",
             "run": "python3 -m pip install -r scripts/requirements-test_safe_push.txt"},
            {"id": "fetch", "uses": "actions/download-artifact@v5",
             "with": {"pattern": "safe-push-ran-*", "path": "${{ runner.temp }}/safe-push-ran"}},
            {"id": "cover", "if": "always() && steps.install.outcome == 'success'",
             "run": 'python3 scripts/test_safe_push.py --cover "$RUNNER_TEMP/safe-push-ran"'}])
        self.assertEqual(steps[-1]["id"], "verdict")
        report = jobs[safe_push.SUITE_REPORT_JOB]["steps"][0]
        self.assertEqual(report["uses"], "actions/download-artifact@v5")
        count = self.ci_shard_count()
        names = {str(step["with"]["name"]).replace("${{ matrix.shard }}", str(shard))
                 for job in jobs.values() for step in job.get("steps", [])
                 if "upload-artifact" in step.get("uses", "") for shard in range(1, count + 1)}
        for pattern, own in ((steps[3]["with"]["pattern"], "safe-push-ran-{}"),
                             (report["with"]["pattern"], "test_safe_push-log-{}")):
            with self.subTest(pattern=pattern):
                self.assertEqual(sorted(name for name in names
                                        if fnmatch.fnmatchcase(name, pattern)),
                                 sorted(own.format(shard) for shard in range(1, count + 1)))

    def test_safe_push_tests_passes_only_when_every_shard_passed(self):
        job = self.jobs()[GATHER_JOB]
        self.assertNotIn("name", job, "the job is named by its id: safe-push-tests")
        self.assertEqual(job["needs"], SHARD_JOB)
        self.assertEqual(job["if"], "always()")
        self.assertEqual(job["permissions"], {"contents": "read"})
        self.assertNotIn("continue-on-error", job)
        step = job["steps"][-1]
        self.assertEqual(step["id"], "verdict")
        self.assertEqual(step["if"], "always()")
        self.assertFalse({"shell", "continue-on-error", "uses"} & set(step))
        self.assertEqual(step["env"], {"SHARDS": f"${{{{ needs.{SHARD_JOB}.result }}}}",
                                       "COVER": "${{ steps.cover.outcome }}"})
        self.assertNotIn("${{", step["run"])
        every = ["actions/checkout@v5", "actions/setup-python@v5", "install", "fetch", "cover",
                 "verdict"]

        ran, result, said = self.gather("success")
        self.assertEqual((ran, result), (every, "success"), said)
        self.assertIn("Every shard of scripts/test_safe_push.py succeeded.", said)
        self.assertIn("The shards' lists prove that every test ran once", said)
        # Whatever the shards' result, the proof runs, naming what failed or did not run,
        # and then the verdict fails the job: every result but success is red, by name.
        for shards in ("failure", "cancelled", "skipped", "", "neutral"):
            with self.subTest(shards=shards):
                ran, result, said = self.gather(shards)
                self.assertEqual((ran, result), (every, "failure"), said)
                self.assertIn(shards if shards in ("failure", "cancelled", "skipped")
                              else f"'{shards}'", said)
        # A fetch that fails, a list missing, fails the job, and the proof still runs; a
        # proof that fails, or never runs, fails the job, though every shard succeeded.
        for failing, proved in (("fetch", True), ("cover", True),
                                ("actions/checkout@v5", False), ("install", False)):
            with self.subTest(failing=failing):
                ran, result, said = self.gather("success", frozenset({failing}))
                self.assertEqual(result, "failure")
                self.assertIs("cover" in ran, proved)
                self.assertEqual(ran[-1], "verdict")
                self.assertIn("Every shard of scripts/test_safe_push.py succeeded.", said)
                if failing != "fetch":
                    self.assertIn("The proof that every test ran once, in one shard, and "
                                  f"passed ended '{'failure' if proved else 'skipped'}'", said)

    def test_the_conditions_are_read_as_github_reads_them(self):
        # The model of a condition, on the forms the cadence workflow writes: the report's
        # job runs on main whenever one of the three jobs it needs did not succeed, and
        # never on another branch; and on the operators themselves.
        report = self.jobs()[safe_push.SUITE_REPORT_JOB]["if"]

        def reports(ref: str, tests: str, negative="success", kernel="success") -> bool:
            results = {"safe-push-tests": tests, "negative-tests": negative,
                       "formal-model-kernel": kernel}
            return step_runs(report, {"github.ref": ref, **{
                f"needs.{job}.result": result for job, result in results.items()}},
                "success" != tests or "success" != negative or "success" != kernel)

        self.assertFalse(reports("refs/heads/main", "success"))
        for result in ("failure", "cancelled", "skipped"):
            with self.subTest(result=result):
                self.assertTrue(reports("refs/heads/main", result))
                self.assertTrue(reports("refs/heads/main", "success", negative=result))
                self.assertTrue(reports("refs/heads/main", "success", kernel=result))
                self.assertFalse(reports("refs/heads/train/x", result))
        self.assertTrue(step_runs("!cancelled() && (a == 'x' || a == 'y')", {"a": "Y"}, True))
        self.assertFalse(step_runs("!cancelled()", {}, False, cancelled=True))
        self.assertTrue(step_runs("a != 'x' || !(a == 'x')", {"a": "z"}, False))
        self.assertFalse(step_runs("a == 'x'", {"a": "x"}, True), "no status function")
        self.assertFalse(step_runs("!always()", {}, False))
        self.assertFalse(step_runs("success()", {}, False, cancelled=True))
        self.assertTrue(step_runs("cancelled()", {}, False, cancelled=True))
        self.assertTrue(step_runs("${{ failure() }}", {}, True))
        self.assertTrue(step_runs(None, {}, False))
        self.assertFalse(step_runs("", {}, True))
        for condition in ("contains(github.ref, 'main')", 'github.ref == "main"', "github.ref",
                          "always() &&", "(always()", "success() always()", "started()",
                          "fromJSON('true')", "needs.other.result == 'success'"):
            with self.subTest(condition=condition), self.assertRaises(ValueError):
                step_runs(condition, {"github.ref": "refs/heads/main"}, False)

    # The planted reds: whole runs of the cadence workflow, its jobs and steps read from it,
    # by CadenceRun. Each test fails when the guard it names is taken away.

    @unittest.skipUnless(REPORT_TOOLS, REPORT_TOOLS_REASON)
    def test_a_failing_test_in_one_shard_turns_the_run_red_and_reports_it(self):
        # (a) One test fails, as a deliberate failure would, in the shard the dealing gives
        # it: that shard fails, and with it the matrix; the proof names the test; the
        # verdict job, safe-push-tests, ends red, and the run with it; and the report job
        # runs, reads the test from that shard's log, and opens the issue labelled
        # blocks-release, or comments on the one already open. The guards: the verdict job
        # runs whatever the shards did, and the report's condition reads its result.
        failed = "Shards.test_a_failing_test_in_one_shard_turns_the_run_red_and_reports_it"
        count = self.ci_shard_count()
        setup, times = load_times()
        shard = shard_plan([time_key(test) for test in loaded_tests()], count, times,
                           setup).shard_of[failed]
        for open_issue in (None, 7):
            with self.subTest(open_issue=open_issue), tempfile.TemporaryDirectory() as tmp:
                run = CadenceRun(Path(tmp))
                results = run.run(failing=frozenset({failed}), open_issue=open_issue)
                self.assertEqual(results, {SHARD_JOB: "failure", GATHER_JOB: "failure",
                                           "negative-tests": "success",
                                           "formal-model-kernel": "success",
                                           "report": "success"}, run.said)
                self.assertEqual(conclusion(results), "failure")
                self.assertIn(f"{failed} did not pass in shard {shard}: FAIL.", run.said["cover"])
                self.assertIn("The shards ended in failure", run.said["verdict"])
                self.assertIsNotNone(run.body, run.said.get("report"))
                self.assertIn("- `safe-push-tests` (`scripts/test_safe_push.py`, its shards and "
                              "the proof that every test ran once and passed): failure", run.body)
                self.assertNotIn("negative-tests", run.body)
                self.assertIn(f"FAIL: {failed} (a stand-in", run.body)
                calls = "\n".join(run.calls)
                if open_issue is None:
                    self.assertIn(f"issue create --title {REPORT_TITLE} --label blocks-release "
                                  "--body-file ", calls)
                else:
                    self.assertIn(f"issue comment {open_issue} --body-file ", calls)
                    self.assertNotIn("issue create", calls)

    @unittest.skipUnless(REPORT_TOOLS, REPORT_TOOLS_REASON)
    def test_a_missing_list_fails_the_proof_and_turns_the_run_red(self):
        # (b) Every shard succeeds, but one shard's list is lost once kept, so the fetch
        # finds the others alone: the proof fails, naming that shard, the verdict is red
        # though the matrix succeeded, and the run is red and reported, though no test
        # failed. The guard: the proof's demand for a list from every shard of the matrix.
        count = self.ci_shard_count()
        lost = count // 2
        with tempfile.TemporaryDirectory() as tmp:
            run = CadenceRun(Path(tmp))
            results = run.run(lost=frozenset({f"safe-push-ran-{lost}"}))
            self.assertEqual(results, {SHARD_JOB: "success", GATHER_JOB: "failure",
                                       "negative-tests": "success",
                                       "formal-model-kernel": "success",
                                       "report": "success"}, run.said)
            self.assertEqual(conclusion(results), "failure")
            self.assertIn(f"Shard {lost} of {count} left no list of the tests it ran",
                          run.said["cover"])
            self.assertIn("Every shard of scripts/test_safe_push.py succeeded.",
                          run.said["verdict"])
            self.assertIn("The proof that every test ran once, in one shard, and passed "
                          "ended 'failure'", run.said["verdict"])
            self.assertIsNotNone(run.body, run.said.get("report"))
            self.assertIn("No failing test is named in the shards' logs", run.body)

    @unittest.skipUnless(REPORT_TOOLS, REPORT_TOOLS_REASON)
    def test_a_cancelled_or_skipped_shard_turns_the_verdict_red(self):
        # (c) A first attempt, every shard green, keeps every list, and the run is green,
        # with no report. Then the jobs run again (GitHub's "re-run all jobs"), and the last
        # shard is cancelled as its tests start, keeping no list of its own; or the shards
        # are skipped. The first attempt's lists still prove that every test ran once and
        # passed, so the proof passes; the verdict is red all the same, and the run is red
        # and reported. The guard: the verdict's own judgement of the matrix's result.
        count = self.ci_shard_count()
        with tempfile.TemporaryDirectory() as tmp:
            run = CadenceRun(Path(tmp))
            results = run.run()
            self.assertEqual(results, {SHARD_JOB: "success", GATHER_JOB: "success",
                                       "negative-tests": "success",
                                       "formal-model-kernel": "success",
                                       "report": "skipped"}, run.said)
            self.assertEqual(conclusion(results), "success")
            for shards, how, said in (
                    ("cancelled", {"cancelled": frozenset({count})}, "The shards ended cancelled"),
                    ("skipped", {"given": {SHARD_JOB: "skipped"}}, "The shards were skipped")):
                with self.subTest(shards=shards):
                    results = run.run(**how)
                    self.assertEqual(results[SHARD_JOB], shards)
                    self.assertEqual((results[GATHER_JOB], results["report"]),
                                     ("failure", "success"), run.said)
                    self.assertEqual(conclusion(results), "failure")
                    self.assertIn(f"tests unittest's loader lists here ran once, in one of the "
                                  f"{count} shards", run.said["cover"])
                    self.assertIn(said, run.said["verdict"])
                    self.assertIsNotNone(run.body, run.said.get("report"))
                    self.assertIn(f"`scripts/test_safe_push.py`, its shards and the proof that "
                                  "every test ran once and passed): failure", run.body)

if __name__ == "__main__":
    command = script_command(sys.argv[1:])
    if command is None:
        unittest.main(verbosity=2)
    elif command[0] == "shard":
        run_shard(*command[1:])
    elif command[0] == "cover":
        sys.exit(cover_command(command[1]))
    else:
        sys.exit(times_command(command[1]))
