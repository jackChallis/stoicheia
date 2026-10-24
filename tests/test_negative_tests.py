#!/usr/bin/env python3
"""Restoration regressions for scripts/negative_tests.py, without Lean, and without Git
outside temporary repositories.

    python3 -I tests/test_negative_tests.py

The negative suite runs these first. Temporary files stand in for Lake outputs;
simulated builds delete, replace and create them before failing or being interrupted.
A temporary repository stands in for the pre-flight's pass with origin/main's checks,
whose work tree lacks the files a commit adds under the check inputs while Git's index
still lists them. The plants are reached as the suite reaches them, through its loader
of scripts/negative/, and the loader is tested on temporary folders of small plants; one
test runs the suite as a script, in a temporary copy, to see that its plants share the
running module and that no bytecode runs in place of the runner or a plant. Small Lean
texts, never built, stand in for Audit/Overlaps.lean, for check_fidelity's reading of the
combinations it proves, which the plant of an unproved combination relies on. The comment
reader the scripts share is fed the texts on which a reader could read a Lean comment
otherwise than Lean does, each with Lean's own reading.
"""

import importlib.util
import io
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import negative_tests as negative  # noqa: E402


def plant(name):
    """The plant() of scripts/negative/<name>.py, as the loader gives it."""
    plants, faults = negative.load_plants(REPO / "scripts" / "negative")
    assert not faults, faults
    return next(p for p in plants if p.name == name).plant


def stand_in(root, **kwargs):
    """One stand-in plant, its function a Mock given `kwargs`, as load_plants returns it."""
    function = Mock(**kwargs)
    return ([negative.Plant("heath_word", root / "scripts/negative/heath_word.py",
                            "A stand-in.", False, function)], []), function


class RestorationTests(unittest.TestCase):
    def setUp(self):
        tmp = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(tmp)
        self.build = self.root / ".lake/build"
        self.planted = self.root / "Elements/Foundations/Tacit/Planted.lean"
        self.planted.parent.mkdir(parents=True)
        self.enterContext(patch.multiple(negative, ROOT=self.root, PLANTED=self.planted,
                                        failures=[]))
        self.output = self.enterContext(redirect_stdout(io.StringIO()))

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def files(self):
        return {p.relative_to(self.build): p.read_bytes()
                for p in self.build.rglob("*") if p.is_file()}

    def outputs(self, module):
        for kind, suffixes in (
                ("lib/lean", ("olean", "ilean", "trace", "olean.hash", "ilean.hash",
                              "olean.private")),
                ("ir", ("c", "c.hash", "setup.json")),
                ("native", ("c.o", "c.o.hash"))):
            for suffix in suffixes:
                self.write(self.build / kind / f"{module}.{suffix}",
                           b"olean\x00original " + suffix.encode())

    def damage_outputs(self):
        for path in self.build.rglob("*"):
            if path.is_file():
                if path.suffix in (".olean", ".ilean", ".c"):
                    path.unlink()
                else:
                    path.write_bytes(b"incomplete")
        self.write(self.build / "ir/New/Dependent.c", b"new output")

    def failed_rebuild(self, interrupt):
        self.damage_outputs()
        if interrupt:
            raise KeyboardInterrupt("restoration build interrupted")
        return subprocess.CompletedProcess([], 1, "", "restoration build failed")

    def test_snapshot_removes_outputs_when_build_tree_was_absent(self):
        saved = negative.BuildOutputs()
        self.outputs("Elements/BookI/Prop01")
        saved.restore()
        self.assertEqual(self.files(), {})

    def test_temporary_module_snapshot_keeps_neighbours(self):
        self.outputs("Elements/Foundations/Tacit/Planted")
        saved = self.files()
        snapshot = negative.BuildOutputs("**/Elements/Foundations/Tacit/Planted.*")
        self.damage_outputs()
        self.outputs("Elements/Foundations/Tacit/PlantedMore")
        self.outputs("Other/Planted")
        neighbours = {p: data for p, data in self.files().items() if p not in saved}
        snapshot.restore()
        self.assertEqual(self.files(), saved | neighbours)

    def test_successful_rebuild_keeps_new_outputs_and_replays(self):
        self.outputs("Elements/BookI/Prop01")
        path = self.build / "lib/lean/Elements/BookI/Prop01.olean"
        calls = []
        def run(*cmd):
            calls.append(cmd)
            if len(calls) == 1:
                self.assertTrue(path.read_bytes().startswith(b"broken"))
                return subprocess.CompletedProcess(cmd, 1, "", "failed to read file "
                    "Elements/BookI/Prop01.olean: invalid header")
            if cmd == ("lake", "build"):
                self.assertFalse(path.exists(), "restoration must force the rebuild")
                self.write(path, b"olean rebuilt")
            else:
                self.assertEqual(cmd, calls[0], "the restored environment must be replayed")
                self.assertEqual(path.read_bytes(), b"olean rebuilt")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        with patch.object(negative, "run", side_effect=run), \
                patch.object(negative.check_kernel, "toolchain_bin",
                             return_value=Path("toolchain")):
            plant("corrupt_olean")()
        self.assertEqual(len(calls), 3)
        self.assertEqual(path.read_bytes(), b"olean rebuilt")
        self.assertEqual(negative.failures, [])

    def test_corrupt_olean_restores_all_outputs(self):
        for interrupt in (False, True):
            with self.subTest(interrupt=interrupt):
                self.outputs("Elements/BookI/Prop01")
                self.outputs("Elements/BookI/Prop02")
                saved = self.files()
                def run(*cmd):
                    if cmd == ("lake", "build"):
                        return self.failed_rebuild(interrupt)
                    return subprocess.CompletedProcess(cmd, 1, "", "failed to read file "
                        "Elements/BookI/Prop01.olean: invalid header")
                with patch.object(negative, "run", side_effect=run) as commands, \
                        patch.object(negative.check_kernel, "toolchain_bin",
                                     return_value=Path("toolchain")):
                    if interrupt:
                        with self.assertRaises(KeyboardInterrupt):
                            plant("corrupt_olean")()
                    else:
                        plant("corrupt_olean")()
                        self.assertIn("the restored Elements build: exit 1", negative.failures)
                self.assertEqual(commands.call_count, 2)
                self.assertEqual(self.files(), saved)

    def ill_typed_commands(self, replay, rebuild):
        """Stand-ins for the ill-typed plant's commands: the compile must read a copy of I.1
        outside the tree, with the plant, and write I.1's `.olean`; `replay` answers
        leanchecker and `rebuild` the restoration build."""
        source = self.root / "Elements/BookI/Prop01.lean"
        self.write(source, b"import Elements.Figure.Basics\n")
        path = self.build / "lib/lean/Elements/BookI/Prop01.olean"
        def run(*cmd):
            if cmd[:3] == ("lake", "env", "lean"):
                copy = Path(cmd[-1])
                self.assertFalse(copy.is_relative_to(self.root), "the copy must be outside")
                self.assertEqual(copy, Path(cmd[cmd.index("-R") + 1])
                                 / "Elements/BookI/Prop01.lean")
                self.assertEqual(cmd[cmd.index("-o") + 1], str(path))
                self.assertEqual(copy.read_text(), "import Lean.Elab.Command\n"
                                 + source.read_text() + negative.ILL_TYPED_LEAN)
                self.write(path, b"olean planted")
                return subprocess.CompletedProcess(cmd, 0, "", "")
            if cmd == ("lake", "build"):
                return rebuild(cmd)
            self.assertEqual(cmd, ("lake", "env", "toolchain/leanchecker", "--fresh", "Elements"))
            return replay(cmd)
        return path, run

    def test_ill_typed_proof_rejected_then_rebuilt_and_replayed(self):
        name = negative.ILL_TYPED
        for message, caught in (
                (f"while replaying declaration '{name}':\n(kernel) declaration type "
                 f"mismatch, '{name}' has type\n  True\n", True),
                ("failed to read file Elements/BookI/Prop01.olean: invalid header", False)):
            with self.subTest(caught=caught):
                negative.failures.clear()
                self.outputs("Elements/BookI/Prop01")
                replays = []
                def replay(cmd):
                    replays.append(path.read_bytes())
                    return subprocess.CompletedProcess(cmd, 1 if len(replays) == 1 else 0,
                                                       "", message)
                def rebuild(cmd):
                    self.assertFalse(path.exists(), "restoration must force the rebuild")
                    self.write(path, b"olean rebuilt")
                    return subprocess.CompletedProcess(cmd, 0, "", "")
                path, run = self.ill_typed_commands(replay, rebuild)
                with patch.object(negative, "run", side_effect=run) as commands, \
                        patch.object(negative.check_kernel, "toolchain_bin",
                                     return_value=Path("toolchain")):
                    plant("ill_typed_proof")()
                self.assertEqual(commands.call_count, 4)
                self.assertEqual(replays, [b"olean planted", b"olean rebuilt"])
                if caught:
                    self.assertEqual(negative.failures, [])
                else:
                    self.assertEqual(len(negative.failures), 1)
                    self.assertIn("not caught", negative.failures[0])

    def test_ill_typed_proof_restores_all_outputs(self):
        for interrupt in (False, True):
            with self.subTest(interrupt=interrupt):
                negative.failures.clear()
                self.outputs("Elements/BookI/Prop01")
                self.outputs("Elements/BookI/Prop02")
                saved = self.files()
                path, run = self.ill_typed_commands(
                    lambda cmd: subprocess.CompletedProcess(
                        cmd, 1, "", f"while replaying declaration '{negative.ILL_TYPED}'"),
                    lambda cmd: self.failed_rebuild(interrupt))
                with patch.object(negative, "run", side_effect=run) as commands, \
                        patch.object(negative.check_kernel, "toolchain_bin",
                                     return_value=Path("toolchain")):
                    if interrupt:
                        with self.assertRaises(KeyboardInterrupt):
                            plant("ill_typed_proof")()
                    else:
                        plant("ill_typed_proof")()
                        self.assertIn("the Elements build restored after the ill-typed "
                                      "proof: exit 1", negative.failures)
                self.assertEqual(commands.call_count, 3)
                self.assertEqual(self.files(), saved)

    def test_missing_files_restored_byte_for_byte(self):
        rels = ("figures/I/01.svg", "figures/I/01-idea.svg", "mishnah/I/01.md")
        originals = {rel: f"<{rel}>\r\nno newline at the end".encode() for rel in rels}
        for outcome in ("caught", "not caught", "interrupted"):
            with self.subTest(outcome=outcome):
                negative.failures.clear()
                for rel, data in originals.items():
                    self.write(self.root / rel, data)
                def fidelity(*args):
                    missing = [rel for rel in rels if not (self.root / rel).exists()]
                    self.assertEqual(len(missing), 1)
                    if outcome == "interrupted":
                        raise KeyboardInterrupt("fidelity check interrupted")
                    if outcome == "not caught":
                        return subprocess.CompletedProcess([], 0, "", "")
                    return subprocess.CompletedProcess(
                        [], 1, f"✗ I.1: {missing[0]} is missing\n", "")
                with patch.object(negative, "fidelity", side_effect=fidelity) as checks:
                    if outcome == "interrupted":
                        with self.assertRaises(KeyboardInterrupt):
                            plant("missing_files")()
                    else:
                        plant("missing_files")()
                self.assertEqual(checks.call_count, 1 if outcome == "interrupted" else 3)
                for rel, data in originals.items():
                    self.assertEqual((self.root / rel).read_bytes(), data)
                if outcome == "caught":
                    self.assertEqual(negative.failures, [])
                elif outcome == "not caught":
                    self.assertEqual(len(negative.failures), 3)

    def test_audit_restores_all_outputs(self):
        source = self.root / "Audit/Overlaps.lean"
        for multiline, interrupt in ((False, False), (False, True),
                                     (True, False), (True, True)):
            with self.subTest(multiline=multiline, interrupt=interrupt):
                dropped = ("Elements.Tacit.outside_of_between" if multiline
                           else "Elements.Tacit.inside_of_between")
                axioms = (f"propext,\n Classical.choice,\n Quot.sound,\n {dropped}"
                          if multiline else dropped)
                original = f"'Audit.III_2' depends on axioms: [{axioms}]".encode()
                self.write(source, original)
                self.outputs("Audit/Overlaps")
                self.outputs("Audit")
                saved = self.files()
                def run(*cmd):
                    self.assertEqual(cmd, ("lake", "build", "Audit"))
                    if source.read_bytes() == original:
                        return self.failed_rebuild(interrupt)
                    self.damage_outputs()
                    return subprocess.CompletedProcess(cmd, 1, "", "Audit/Overlaps.lean: "
                        "Docstring on `#guard_msgs` does not match generated message "
                        f"Audit.III_2 {dropped}")
                with patch.object(negative, "run", side_effect=run) as commands:
                    if interrupt:
                        with self.assertRaises(KeyboardInterrupt):
                            plant("changed_audit_pin")()
                    else:
                        plant("changed_audit_pin")()
                        self.assertIn("the restored audit build: exit 1", negative.failures)
                self.assertEqual(commands.call_count, 2)
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(self.files(), saved)

    def test_audit_drops_one_project_axiom_and_keeps_other_pins(self):
        source = self.root / "Audit/Overlaps.lean"
        for axioms in (
                "Elements.Tacit.inside_of_between",
                "propext, Classical.choice, Quot.sound, Elements.Tacit.outside_of_between",
                "propext,\n Classical.choice,\n Elements.Postulate1,\n Quot.sound,\n "
                "Elements.Tacit.outside_of_between"):
            with self.subTest(axioms=axioms):
                names = [a.strip() for a in axioms.split(",")]
                dropped = next(a for a in names if a.startswith("Elements."))
                remaining = names.copy()
                remaining.remove(dropped)
                prefix = "/-- info: 'Audit.I_2' depends on axioms: [Elements.Postulate1] -/\n"
                suffix = "\n-/\n#guard_msgs in\n#print axioms Audit.III_2\n"
                original = (prefix + "/--\ninfo: 'Audit.III_2' depends on axioms: ["
                            + axioms + "]" + suffix).encode()
                self.write(source, original)
                calls = []
                def run(*cmd):
                    calls.append(cmd)
                    self.assertEqual(cmd, ("lake", "build", "Audit"))
                    if len(calls) == 2:
                        self.assertEqual(source.read_bytes(), original)
                        return subprocess.CompletedProcess(cmd, 0, "", "")
                    changed = source.read_text()
                    self.assertTrue(changed.startswith(prefix))
                    self.assertTrue(changed.endswith(suffix))
                    pin = re.search(r"'Audit\.III_2' depends on axioms: \[([^\]]*)\]", changed)
                    self.assertEqual([a.strip() for a in pin[1].split(",") if a.strip()],
                                     remaining)
                    return subprocess.CompletedProcess(cmd, 1, "", "Audit/Overlaps.lean: "
                        "Docstring on `#guard_msgs` does not match generated message "
                        f"Audit.III_2 {dropped}")
                with patch.object(negative, "run", side_effect=run):
                    plant("changed_audit_pin")()
                self.assertEqual(len(calls), 2)
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(negative.failures, [])

    def test_planted_outputs_cleaned_after_restoration(self):
        originals = {}
        for rel in ("Elements/BookI/Prop15.lean", "Elements/BookI/Prop16.lean", "facts.json"):
            originals[rel] = (REPO / rel).read_bytes()
            self.write(self.root / rel, originals[rel])
        for preexisting, outcome in ((False, "success"), (True, "success"),
                                     (False, "failed"), (True, "failed"),
                                     (False, "interrupted"), (True, "interrupted")):
            with self.subTest(preexisting=preexisting, outcome=outcome):
                for path in self.build.rglob("*"):
                    if path.is_file():
                        path.unlink()
                if preexisting:
                    self.outputs("Elements/Foundations/Tacit/Planted")
                saved = self.files()
                def run(*cmd):
                    self.assertEqual(cmd, ("lake", "build"))
                    self.outputs("Elements/Foundations/Tacit/Planted")
                    self.write(self.build / "ir/Elements/Foundations/Tacit/Planted.new",
                               b"new output")
                    if not self.planted.exists():
                        if outcome == "success":
                            return subprocess.CompletedProcess(cmd, 0, "", "")
                        return self.failed_rebuild(outcome == "interrupted")
                    return subprocess.CompletedProcess(cmd, 1, "", "planted build failed")
                with patch.object(negative, "run", side_effect=run) as commands:
                    if outcome == "interrupted":
                        with self.assertRaises(KeyboardInterrupt):
                            plant("planted_assumptions")()
                    else:
                        plant("planted_assumptions")()
                self.assertEqual(commands.call_count, 2)
                self.assertFalse(self.planted.exists())
                for rel, data in originals.items():
                    self.assertEqual((self.root / rel).read_bytes(), data)
                self.assertEqual(self.files(), saved)

    def test_law_plants_restore_sources_and_outputs(self):
        # The plant in two clean laws' proofs (#150), at each of its stages: whether the
        # planted build, the probe that prints the pins, the audit build or the certificate
        # run fails or is interrupted, or the run goes through to check_fidelity.py, and
        # whatever the restoration build does, the law proofs, the audit pins and
        # facts.json come back, and so do the outputs when the restoration build fails.
        rels = ("Elements/Figure/Superposition.lean", "Audit/Superposition.lean", "facts.json")
        originals = {rel: (REPO / rel).read_bytes() for rel in rels}
        names = [m[2] for m in negative.AUDIT_PIN.finditer(originals[rels[1]].decode())]
        self.assertTrue(names)
        steps = ("baseline", "planted", "probe", "audit", "certificate", "fidelity")
        caught = ("✗ I.4: its construction_rules for the cited law lenSymm is ['Postulate1'], "
                  "not []\n✗ I.8: its construction_rules for the cited law lenSymm is "
                  "['Postulate1'], not []\n✗ I.4: its construction_rules for the cited law "
                  "angleSymm is ['Tacit.circles_meet'], not []\n")
        cases = [(stage, outcome, restoring)
                 for stage in ("planted", "probe", "audit", "certificate")
                 for outcome in ("failed", "interrupted")
                 for restoring in ("success", "failed", "interrupted")]
        cases += [(None, "completed", restoring)
                  for restoring in ("success", "failed", "interrupted")]
        for stage, outcome, restoring in cases:
            with self.subTest(stage=stage, outcome=outcome, restoring=restoring):
                for rel, data in originals.items():
                    self.write(self.root / rel, data)
                for path in self.build.rglob("*"):
                    if path.is_file():
                        path.unlink()
                self.outputs("Elements/Figure/Superposition")
                saved = self.files()
                calls = []

                def ends(step, cmd, ok):
                    """The step's result: its failure or interruption at `stage`."""
                    if step != stage:
                        return ok
                    self.damage_outputs()
                    if outcome == "interrupted":
                        raise KeyboardInterrupt(f"{step} interrupted")
                    return subprocess.CompletedProcess(cmd, 1, "", f"{step} failed")

                def run(*cmd):
                    calls.append(cmd)
                    step = steps[len(calls) - 1] if len(calls) <= len(steps) else None
                    done = subprocess.CompletedProcess(cmd, 0, "", "")
                    if cmd == ("lake", "build", "Elements", "Audit"):
                        # The restoration build, with every source back.
                        for rel, data in originals.items():
                            self.assertEqual((self.root / rel).read_bytes(), data)
                        if restoring == "success":
                            return done
                        return self.failed_rebuild(restoring == "interrupted")
                    if step in ("baseline", "fidelity"):
                        self.assertEqual(cmd, (sys.executable, "scripts/check_fidelity.py"))
                        if step == "baseline":
                            # The unplanted tree's problems, read before anything is planted.
                            for rel, data in originals.items():
                                self.assertEqual((self.root / rel).read_bytes(), data)
                            return subprocess.CompletedProcess(cmd, 0, "✓ fidelity\n", "")
                        return subprocess.CompletedProcess(cmd, 1, caught, "")
                    if step == "planted":
                        self.assertEqual(cmd, ("lake", "build"))
                        laws = (self.root / rels[0]).read_text()
                        self.assertIn("have _planted := @Postulate1", laws)
                        self.assertIn("have _planted := @Tacit.circles_meet", laws)
                        return ends(step, cmd, done)
                    if step == "probe":
                        self.assertEqual(cmd[:3], ("lake", "env", "lean"))
                        probe = Path(cmd[3])
                        self.assertEqual(probe.name, "Pins.lean")
                        self.assertNotEqual(probe.parent, self.root)
                        printed = [line.split(" ", 2)[2]
                                   for line in probe.read_text().splitlines()
                                   if line.startswith("#print axioms ")]
                        self.assertEqual(printed, names)
                        out = "".join(f"{probe}:{i}:0: info: '{n}' depends on axioms: "
                                      f"[propext, Elements.Postulate1]\n"
                                      for i, n in enumerate(names, 2))
                        return ends(step, cmd, subprocess.CompletedProcess(cmd, 0, out, ""))
                    if step == "audit":
                        self.assertEqual(cmd, ("lake", "build", "Audit"))
                        audit = (self.root / rels[1]).read_text()
                        self.assertEqual(audit.count("[propext, Elements.Postulate1]"),
                                         len(names))
                        return ends(step, cmd, done)
                    self.assertEqual(step, "certificate")
                    self.assertEqual(cmd, ("lake", "env", "lean", "Certificate/Facts.lean"))
                    (self.root / "facts.json").write_text("{}\n")
                    return ends(step, cmd, done)

                interrupted = "interrupted" in (outcome, restoring)
                with patch.object(negative, "run", side_effect=run):
                    if interrupted:
                        with self.assertRaises(KeyboardInterrupt):
                            plant("construction_in_clean_laws")()
                    else:
                        plant("construction_in_clean_laws")()
                reached = len(steps) if stage is None else steps.index(stage) + 1
                self.assertEqual(len(calls), reached + 1)
                self.assertEqual(calls[-1], ("lake", "build", "Elements", "Audit"))
                for rel, data in originals.items():
                    self.assertEqual((self.root / rel).read_bytes(), data)
                if restoring != "success":
                    self.assertEqual(self.files(), saved)
                if stage is None and restoring == "success":
                    self.assertEqual(negative.failures, [])
                negative.failures.clear()

    @staticmethod
    def axiom_pin(name, axioms="[propext]"):
        return (f"/--\ninfo: '{name}' depends on axioms: {axioms}\n-/\n"
                f"#guard_msgs in\n#print axioms {name}\n")

    STATEMENT_PIN = ("/--\ninfo: Elements.law : ∀ c ∈ cites, c.Holds primitives\n-/\n"
                     "#guard_msgs in\n#check Elements.law\n")

    def test_audit_pins_never_run_across_a_statement_pin(self):
        # #150's review: a statement pin (`#guard_msgs in` over `#check`) before an axiom
        # pin must be neither read into its message nor rewritten.
        rel = "Audit/Pins.lean"
        text = ("import Elements\n\n" + self.STATEMENT_PIN + "\n" + self.axiom_pin("Elements.a")
                + "\n" + self.STATEMENT_PIN + "\n" + self.axiom_pin("Elements.b"))
        self.write(self.root / rel, text.encode())
        found = list(negative.AUDIT_PIN.finditer(text))
        self.assertEqual([m[2] for m in found], ["Elements.a", "Elements.b"])
        for m in found:
            self.assertNotIn("#check", m[0])

        def run(*cmd):
            self.assertEqual(cmd[:3], ("lake", "env", "lean"))
            return subprocess.CompletedProcess(cmd, 0, "".join(
                f"{cmd[3]}:{i}:0: info: '{n}' depends on axioms: [propext, Elements.P]\n"
                for i, n in enumerate(("Elements.a", "Elements.b"), 2)), "")
        with patch.object(negative, "run", side_effect=run):
            changed = negative.rewritten_pins(rel)
        self.assertEqual(negative.failures, [])
        self.assertEqual(changed, text.replace("[propext]", "[propext, Elements.P]"))
        self.assertEqual(changed.count(self.STATEMENT_PIN), 2)

    def test_every_print_axioms_must_be_read_as_a_pin(self):
        # A `#print axioms` the pattern does not read as a pin fails the plant, before Lean
        # is run, rather than being left as it was.
        rel = "Audit/Pins.lean"
        self.write(self.root / rel, ("import Elements\n\n" + self.axiom_pin("Elements.a")
                                     + "\n#print axioms Elements.b\n").encode())
        with patch.object(negative, "run", side_effect=AssertionError("Lean was run")):
            self.assertIsNone(negative.rewritten_pins(rel))
        self.assertEqual(negative.failures, [
            f"printing the pins of {rel}: 2 `#print axioms` commands, but 1 pins read; "
            "update this test"])
        negative.failures.clear()
        text = ("import Elements\n\n" + self.axiom_pin("Elements.a")
                + "\n" + self.axiom_pin("Elements.b"))
        self.write(self.root / rel, text.encode())

        def run(*cmd):
            self.assertEqual(cmd[:3], ("lake", "env", "lean"))
            self.assertEqual(Path(cmd[3]).read_text().splitlines(), [
                "import Elements", "#print axioms Elements.a", "#print axioms Elements.b"])
            return subprocess.CompletedProcess(cmd, 0, "".join(
                f"{cmd[3]}:{i}:0: info: '{name}' depends on axioms: [propext, Elements.P]\n"
                for i, name in enumerate(("Elements.a", "Elements.b"), 2)), "")

        with patch.object(negative, "run", side_effect=run):
            changed = negative.rewritten_pins(rel)
        self.assertEqual(negative.failures, [])
        self.assertEqual(changed, text.replace("[propext]", "[propext, Elements.P]"))

    def test_certificate_plant_restores_source_on_interruption(self):
        source = self.root / "Certificate/Facts.lean"
        original = (REPO / "Certificate/Facts.lean").read_bytes()
        self.write(source, original)
        def interrupted(*cmd):
            self.assertEqual(cmd, (sys.executable, "-I", "tests/test_certificate.py"))
            self.assertIn(b"Derives.len_congr", source.read_bytes())
            self.assertNotIn(b"used.contains coincidenceStep", source.read_bytes())
            raise KeyboardInterrupt("certificate test interrupted")
        with patch.object(negative, "run", side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                plant("certificate_constructor_counting")()
        self.assertEqual(source.read_bytes(), original)

    def test_certificate_plant_restores_source_when_mutation_fails(self):
        source = self.root / "Certificate/Facts.lean"
        original = (REPO / "Certificate/Facts.lean").read_bytes().replace(b"\n", b"\r\n")
        for error in (KeyboardInterrupt("mutation interrupted"), OSError("partial write")):
            with self.subTest(error=type(error).__name__):
                self.write(source, original)
                def damaged_write(path, text, *args, **kwargs):
                    self.assertEqual(path, source)
                    self.assertIn("Derives.len_congr", text)
                    path.write_bytes(text[:100].encode())
                    raise error
                with patch.object(Path, "write_text", damaged_write), \
                        patch.object(negative, "run") as commands:
                    with self.assertRaises(type(error)) as raised:
                        plant("certificate_constructor_counting")()
                self.assertIs(raised.exception, error)
                commands.assert_not_called()
                self.assertEqual(source.read_bytes(), original)

    def test_cited_law_plant_restores_source_and_outputs(self):
        source = self.root / negative.SYNTAX
        original = (REPO / negative.SYNTAX).read_bytes()
        for interrupt in (False, True):
            with self.subTest(interrupt=interrupt):
                negative.failures.clear()
                self.write(source, original)
                self.outputs("Elements/Foundations/Superposition/Syntax")
                self.outputs("Elements/BookI/Prop08")
                saved = self.files()
                def run(*cmd):
                    self.assertEqual(cmd, ("lake", "build", "Elements.BookI.Prop08"))
                    if source.read_bytes() == original:
                        return self.failed_rebuild(interrupt)
                    self.assertIn(b"  | planted\n", source.read_bytes())
                    self.damage_outputs()
                    return subprocess.CompletedProcess(cmd, 1, "", f"error: {negative.HOLDS_ALL}"
                                                       ":84:2: Missing cases:\nCited.planted\n")
                with patch.object(negative, "run", side_effect=run) as commands:
                    if interrupt:
                        with self.assertRaises(KeyboardInterrupt):
                            plant("cited_law_unproved")()
                    else:
                        plant("cited_law_unproved")()
                        self.assertEqual(negative.failures, ["the restored I.8 build: exit 1"])
                self.assertEqual(commands.call_count, 2)
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(self.files(), saved)

    def test_cited_law_refused_elsewhere_is_not_holds_all(self):
        source = self.root / negative.SYNTAX
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes((REPO / negative.SYNTAX).read_bytes())
        def run(*cmd):
            return subprocess.CompletedProcess(cmd, 1, "", (
                "error: Elements/Figure/Superposition.lean:109:2: Missing cases:\n"
                f"error: {negative.HOLDS_ALL}:84:2: Missing cases:\nCited.planted\n"))
        with patch.object(negative, "run", side_effect=run):
            plant("cited_law_unproved")()
        self.assertTrue(any("also refused outside" in f and "Elements/Figure/Superposition.lean"
                            in f for f in negative.failures), negative.failures)

    def test_figure_guard_runs_differ_in_the_guard_alone(self):
        original = (REPO / negative.RESTRICTION).read_text()
        control = negative.plant_figure_guard(original, negative.OVER_THE_FIGURE)
        plant = negative.plant_figure_guard(original, negative.OVER_ALL_POINTS)
        self.assertEqual(control.replace(negative.OVER_THE_FIGURE, "GUARD"),
                         plant.replace(negative.OVER_ALL_POINTS, "GUARD"))
        for text in (control, plant):
            proof = text[text.index(negative.RESTRICT):]
            self.assertIn("hh hX hΓ", proof)
            self.assertIn(negative.THROUGH_THE_EMBEDDING, proof)
            self.assertTrue(text.endswith(f"#print axioms {negative.RESTRICT_NAME}\n"))
            # Rule.iff_figure and its docstring are left out, and nothing else.
            self.assertNotIn(negative.IFF_FIGURE, text)
            self.assertNotIn("for laws that hold.**", text)
            self.assertNotIn("\n\n\n", text)
            self.assertIn("def Rule.Figure", text)
            self.assertIn("structure Interpretation.Embedding", text)
        start = original.index("/-- **The rule is its part about the figure")
        iff = original[start:original.index("\n\n", original.index(negative.IFF_FIGURE))]
        edited = ["      ¬ I.OnLine (v.pt h) (v.line l) → (∀ ℓ ∈ Γ, ℓ.Holds v) → φ.Holds v",
                  "  intro n m Γ a b c d g h l φ dφ v hT hd hg hdg hh hΓ"]
        removed = [line for line in original.splitlines() if line not in plant.splitlines()]
        self.assertEqual(sorted(removed), sorted(iff.splitlines() + edited))

    def test_figure_guard_needs_the_control_to_compile_and_the_plant_to_fail(self):
        source = self.root / negative.RESTRICTION
        original = (REPO / negative.RESTRICTION).read_bytes()
        proved = (f"'{negative.RESTRICT_NAME}' depends on axioms: "
                  "[propext, Classical.choice, Quot.sound]\n")
        sorried = (f"'{negative.RESTRICT_NAME}' depends on axioms: "
                   "[propext, sorryAx, Classical.choice, Quot.sound]\n")
        # (label, the control's errors and axioms, the plant's, the failure expected); a
        # run exits 1 when it has an error, or when a fourth item says so.
        cases = (
            ("caught", ([], proved), (["restrict"], sorried), None),
            ("the control refused inside the theorem", (["restrict"], sorried),
             (["restrict"], sorried), "the control"),
            ("the control refused elsewhere", (["other"], proved), (["restrict"], sorried),
             "the control"),
            ("the control failing with no error read", ([], proved, 1),
             (["restrict"], sorried), "the control"),
            ("the control resting on sorry", ([], sorried), (["restrict"], sorried),
             "the control"),
            ("the control's axioms not printed", ([], ""), (["restrict"], sorried),
             "the control"),
            ("the plant refused outside the theorem", ([], proved), (["other"], proved),
             "not caught by Rule.Figure.restrict alone"),
            ("the plant refused inside and outside", ([], proved),
             (["restrict", "other"], sorried), "not caught by Rule.Figure.restrict alone"),
            ("the plant compiled", ([], proved), ([], proved),
             "not caught by Rule.Figure.restrict alone"),
            ("the plant refused but proved", ([], proved), (["restrict"], proved),
             "not caught by Rule.Figure.restrict alone"),
        )
        for label, control, planted, expected in cases:
            with self.subTest(label):
                negative.failures.clear()
                self.write(source, original)
                calls = []
                def run(*cmd):
                    self.assertEqual(cmd, ("lake", "env", "lean", negative.RESTRICTION))
                    text = source.read_text()
                    is_control = negative.OVER_THE_FIGURE in text
                    self.assertNotEqual(is_control, negative.OVER_ALL_POINTS in text)
                    self.assertNotIn(negative.IFF_FIGURE, text)
                    calls.append(is_control)
                    line = {"restrict": negative.declaration_lines(text, negative.RESTRICT)[2],
                            "other": 1}
                    errors, axioms, *code = control if is_control else planted
                    return subprocess.CompletedProcess(
                        cmd, code[0] if code else int(bool(errors)), axioms, "".join(
                            f"{negative.RESTRICTION}:{line[e]}:5: error: Type mismatch\n"
                            for e in errors))
                with patch.object(negative, "run", side_effect=run):
                    plant("figure_guard_over_all_points")()
                self.assertEqual(source.read_bytes(), original)
                if expected is None:
                    self.assertEqual(negative.failures, [])
                    self.assertEqual(calls, [True, False])
                else:
                    self.assertEqual(len(negative.failures), 1, negative.failures)
                    self.assertIn(expected, negative.failures[0])
                    if expected == "the control":
                        self.assertEqual(calls, [True])

    def test_figure_guard_restores_the_source_when_interrupted(self):
        source = self.root / negative.RESTRICTION
        original = (REPO / negative.RESTRICTION).read_bytes()
        self.write(source, original)
        with patch.object(negative, "run", side_effect=KeyboardInterrupt), \
                self.assertRaises(KeyboardInterrupt):
            plant("figure_guard_over_all_points")()
        self.assertEqual(source.read_bytes(), original)

    def test_failed_regressions_stop_before_any_plant(self):
        loaded, first = stand_in(self.root)

        def run(*cmd):
            if cmd[:2] == ("git", "status"):
                return subprocess.CompletedProcess(cmd, 0, "", "")
            return subprocess.CompletedProcess(cmd, 1, "", "regression failed")
        with patch.object(negative, "run", side_effect=run) as commands, \
                patch.object(negative, "load_plants", return_value=loaded) as load:
            self.assertEqual(negative.main(), 1)
        # The bracket's entry status comes before the regressions, and its closing one after.
        self.assertEqual([call.args for call in commands.call_args_list],
                         [("git", "status", "--porcelain"),
                          (sys.executable, "-I", "tests/test_negative_tests.py"),
                          ("git", "status", "--porcelain")])
        first.assert_not_called()
        load.assert_not_called()

    def test_counts_only_invokes_no_lake_or_lean_build(self):
        commands = []

        def run(*cmd):
            commands.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")

        # The real plants are loaded, from the repository, and the count plant's run is
        # stood in for.
        with patch.object(negative, "run", side_effect=run), \
                patch.object(negative, "ROOT", REPO), \
                patch.object(negative, "run_plant") as counts:
            self.assertEqual(negative.main(("--counts-only",)), 0)
        self.assertEqual(commands, [
            (sys.executable, "-I", "tests/test_negative_tests.py"),
            (sys.executable, "-I", "tests/test_generated_counts.py"),
            (sys.executable, "-I", "tests/test_decision_entries.py"),
            (sys.executable, "-I", "tests/test_risk.py"),
            (sys.executable, "-I", "tests/test_axiom_lock.py"),
        ])
        self.assertFalse(any(part in {"lake", "lean"}
                             for command in commands for part in command))
        counts.assert_called_once()
        self.assertEqual(counts.call_args.args[0].name, "count_markers")

    def test_final_status_checked_without_replacing_original_exception(self):
        for final in ("unchanged", "changed", "failed", "raised"):
            with self.subTest(final=final):
                negative.failures.clear()
                status_calls = []
                original = KeyboardInterrupt("plant interrupted")
                output = io.StringIO()
                def run(*cmd):
                    if cmd[:2] != ("git", "status"):
                        return subprocess.CompletedProcess(cmd, 0, "", "")
                    status_calls.append(cmd)
                    if len(status_calls) == 2:
                        if final == "raised":
                            raise OSError("final status unavailable")
                        if final == "failed":
                            return subprocess.CompletedProcess(cmd, 1, "", "status failed")
                        if final == "changed":
                            return subprocess.CompletedProcess(cmd, 0, " M unexpected\n", "")
                    return subprocess.CompletedProcess(cmd, 0, " M entry\n", "")
                loaded, _ = stand_in(self.root, side_effect=original)
                with redirect_stdout(output), \
                        patch.object(negative, "run", side_effect=run), \
                        patch.object(negative, "load_plants", return_value=loaded):
                    with self.assertRaises(KeyboardInterrupt) as raised:
                        negative.main()
                self.assertIs(raised.exception, original)
                self.assertEqual(len(status_calls), 2)
                if final == "changed":
                    self.assertIn("the working tree did not return to its entry Git status",
                                  negative.failures)
                    self.assertIn(
                        "✗ the working tree did not return to its entry Git status:\n",
                        output.getvalue())
                    self.assertIn(" M unexpected\n", output.getvalue())
                elif final == "failed":
                    self.assertIn("final Git status: exit 1", negative.failures)
                    self.assertIn("✗ final Git status: exit 1\n", output.getvalue())
                    self.assertIn("status failed\n", output.getvalue())
                elif final == "raised":
                    self.assertIn(
                        "Final Git status also failed: OSError: final status unavailable\n",
                        output.getvalue())
                else:
                    self.assertIn(
                        "✓ working tree restored to its entry Git status\n",
                        output.getvalue())


class CircleRuleTests(unittest.TestCase):
    inside = "Tacit.inside_of_between"
    outside = "Tacit.outside_of_between"

    def setUp(self):
        tmp = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(tmp)
        self.lock = self.root / "Certificate/axioms.lock"
        self.lock.parent.mkdir()
        self.errors = []
        self.enterContext(patch.multiple(negative, ROOT=self.root, failures=[]))
        self.enterContext(patch.object(negative.check_fidelity, "errors", self.errors))
        self.enterContext(redirect_stdout(io.StringIO()))

    def fixture(self, locked, proved=None):
        types = {name: "fixture statement" for name in locked}
        self.lock.write_text(negative.check_fidelity.render_lock(types, {}))
        facts = {"axiom_types": types, "axiom_modules": {}, "vocabulary": {}}
        if proved is not None:
            facts["proved_rules"] = proved
        return facts

    def test_locked_rules_need_no_proved_rules_key(self):
        facts = self.fixture((self.inside, self.outside))
        self.assertEqual(negative.check_fidelity.check_lock(facts, self.lock), 2)
        self.assertEqual(self.errors, [])

    def test_either_proved_rule_needs_the_other_as_a_locked_axiom(self):
        for proved, locked in ((self.inside, self.outside), (self.outside, self.inside)):
            for dependencies in ([], ["Postulate1"], [proved], [locked], ["Postulate1", locked]):
                with self.subTest(proved=proved, dependencies=dependencies):
                    self.errors.clear()
                    facts = self.fixture((locked,), {proved: dependencies})
                    self.assertEqual(negative.check_fidelity.check_lock(facts, self.lock), 1)
                    if locked in dependencies:
                        self.assertEqual(self.errors, [])
                    else:
                        self.assertEqual(len(self.errors), 1)
                        self.assertIn(proved, self.errors[0])
                        self.assertIn("proved without another forbidden circle rule",
                                      self.errors[0])

    def test_missing_or_renamed_rule_is_refused_without_proof(self):
        for proved in (None, {}, {"Tacit.renamed": [self.outside]}):
            with self.subTest(proved=proved):
                self.errors.clear()
                facts = self.fixture((self.outside,), proved)
                negative.check_fidelity.check_lock(facts, self.lock)
                self.assertEqual(len(self.errors), 1)
                self.assertIn(f"{self.inside} (Circle 2): not an axiom", self.errors[0])
                self.assertIn("renamed", self.errors[0])

    def test_unlocked_dependency_and_circular_proofs_are_refused(self):
        facts = self.fixture((), {self.inside: [self.outside], self.outside: [self.inside]})
        negative.check_fidelity.check_lock(facts, self.lock)
        self.assertEqual(len(self.errors), 2)
        for rule, error in zip(negative.check_fidelity.FORBIDDEN_CIRCLE_RULES, self.errors):
            self.assertIn(rule, error)
            self.assertIn("proved without another forbidden circle rule", error)

    def test_circle_plant_checks_both_cases_and_restores_either_lock(self):
        for retired in (False, True):
            with self.subTest(retired=retired):
                facts = self.fixture((self.outside,) if retired else (self.inside, self.outside))
                (self.root / "facts.json").write_text(json.dumps(facts))
                saved = self.lock.read_bytes()
                saved_facts = (self.root / "facts.json").read_bytes()
                self.errors[:] = ["a previous finding"]
                with patch.object(negative.check_fidelity, "check_lock",
                                  wraps=negative.check_fidelity.check_lock) as check:
                    plant("circle_proved")()
                self.assertEqual(check.call_count, 2)
                calls = [call.args[0] for call in check.call_args_list]
                self.assertEqual(calls[0]["proved_rules"][self.inside], [])
                self.assertEqual(calls[1]["proved_rules"][self.inside], [self.outside])
                self.assertEqual(negative.failures, [])
                self.assertEqual(self.errors, ["a previous finding"])
                self.assertEqual(self.lock.read_bytes(), saved)
                self.assertEqual((self.root / "facts.json").read_bytes(), saved_facts)

    def test_circle_plant_restores_on_failure_or_interrupt(self):
        for retired in (False, True):
            for exception in (RuntimeError, KeyboardInterrupt):
                with self.subTest(retired=retired, exception=exception):
                    facts = self.fixture((self.outside,) if retired
                                         else (self.inside, self.outside))
                    (self.root / "facts.json").write_text(json.dumps(facts))
                    saved = self.lock.read_bytes()
                    self.errors[:] = ["a previous finding"]
                    with patch.object(negative.check_fidelity, "check_lock",
                                      side_effect=exception("interrupted")):
                        with self.assertRaises(exception):
                            plant("circle_proved")()
                    self.assertEqual(self.lock.read_bytes(), saved)
                    self.assertEqual(self.errors, ["a previous finding"])
                    self.assertEqual(json.loads((self.root / "facts.json").read_text()), facts)


class AbsentTrackedFileTests(unittest.TestCase):
    """A commit adds a check and its test (and a note beside them), and the pre-flight's
    pass with origin/main's checks (scripts/safe_push.py, step 4, base_copies) unlinks
    each from the work tree while Git's index still lists it. Every listing of tracked
    files names them and goes on with what is present; one absent outside the check
    inputs is a failure, and an error reading one, as in a directory of mode 000, is
    raised. Git runs only in a temporary repository, without user config."""

    present = {"scripts/check.py": "# the check\n", "tests/test_check.py": "# its test\n",
               "docs/notes.md": "Words: <!-- count:vocabulary -->3<!-- /count -->.\n"}
    added = ("scripts/new_check.py", "tests/test_new_check.py", "tests/new_check.md",
             "tests/a\x1b[2K\rforged\nline.py")

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.enterContext(patch.dict(os.environ, {**env, "GIT_CONFIG_GLOBAL": os.devnull,
                                                  "GIT_CONFIG_NOSYSTEM": "1"}, clear=True))
        self.enterContext(patch.multiple(negative, ROOT=self.root, failures=[]))
        self.output = self.enterContext(redirect_stdout(io.StringIO()))
        files = {**self.present, **{rel: f"# added: {rel}\n" for rel in self.added}}
        for rel, text in files.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text)
        self.git("init", "-q")
        self.git("add", "--", *files)
        self.git("-c", "user.name=test", "-c", "user.email=test@example.invalid",
                 "commit", "-q", "--no-verify", "-m", "add a check and its test")
        for rel in self.added:
            (self.root / rel).unlink()       # as base_copies takes out a file the commit adds
        self.assertEqual(self.git_names(), sorted(files))

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True,
                              check=True).stdout

    def git_names(self):
        result = subprocess.run(["git", "ls-files", "-z"], cwd=self.root,
                                capture_output=True, check=True)
        return [name.decode() for name in result.stdout.split(b"\0") if name]

    def note(self, rel):
        return ("note: tracked but absent from the work tree (under the check inputs, as a "
                "file the commit adds is in the pre-flight's pass with origin/main's "
                f"checks): {rel!r}\n")

    def assert_named(self, failures=()):
        for rel in self.added:
            self.assertIn(self.note(rel), self.output.getvalue())
        self.assertEqual(negative.failures, list(failures))

    def test_count_copy_names_absent_files_and_copies_the_rest(self):
        with negative.count_source_copy() as (copy, env):
            copied = {p.relative_to(copy).as_posix() for p in copy.rglob("*") if p.is_file()}
            self.assertEqual(copied, set(self.present))
            for rel in self.present:
                self.assertEqual((copy / rel).read_bytes(), (self.root / rel).read_bytes())
            self.assertEqual((env["GIT_DIR"], env["GIT_WORK_TREE"]),
                             (str(self.root / ".git"), str(copy)))
        self.assert_named()

    def test_marker_copy_names_absent_files(self):
        _, listing = negative.tracked_names()
        copy = Path(self.enterContext(tempfile.TemporaryDirectory()))
        negative.copy_marker_files(copy, listing)
        copied = {p.relative_to(copy).as_posix() for p in copy.rglob("*") if p.is_file()}
        self.assertEqual(copied, set(self.present))
        self.assert_named()

    def test_generated_outputs_pass_over_absent_markdown(self):
        self.assertEqual(negative.generated_files(), {self.root / "docs/notes.md"})
        self.assertIn(self.note("tests/new_check.md"), self.output.getvalue())
        self.assertEqual(negative.failures, [])

    def test_absent_file_outside_the_check_inputs_fails(self):
        (self.root / "docs/notes.md").unlink()
        message = ("tracked but absent from the work tree, outside the check inputs: "
                   "'docs/notes.md'")
        with negative.count_source_copy() as (copy, _):
            copied = {p.relative_to(copy).as_posix() for p in copy.rglob("*") if p.is_file()}
            self.assertEqual(copied, {"scripts/check.py", "tests/test_check.py"})
        _, listing = negative.tracked_names()
        negative.copy_marker_files(Path(self.enterContext(tempfile.TemporaryDirectory())),
                                   listing)
        self.assertEqual(self.output.getvalue().count(f"✗ {message}\n"), 2)
        self.assert_named([message])

    def test_an_unreadable_directory_is_not_absent(self):
        docs = self.root / "docs"
        docs.chmod(0)
        self.addCleanup(docs.chmod, 0o755)
        _, listing = negative.tracked_names()
        with self.assertRaises(PermissionError), negative.count_source_copy():
            pass
        with self.assertRaises(PermissionError):
            negative.copy_marker_files(Path(self.enterContext(tempfile.TemporaryDirectory())),
                                       listing)
        self.assertEqual(self.output.getvalue(), "")
        self.assertEqual(negative.failures, [])


class BookZeroImportTests(unittest.TestCase):
    """check_fidelity's rule 3 on a small tree, without Lean (#200): Book Zero's imports
    read as Lean 4.35 reads them, through comments, strings and «…» names, and through
    the edition's own files."""

    rel = "Elements/Figure/Planted.lean"
    tree = {"Elements/BookI/Prop01.lean": "theorem planted : True := trivial\n",
            "Elements/Companions.lean": "import Elements.BookI.Prop01\n",
            "Elements/Foundations/Words.lean": "import Init.Prelude\n",
            "Elements/Figure/Lines.lean": "import Elements.Foundations.Words\n"}

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        for rel, text in self.tree.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text)

    def findings(self, text, rel=None):
        (self.root / (rel or self.rel)).write_text(text, encoding="utf-8")
        return [line for line in negative.rules_in(self.root).stdout.split("\n") if line]

    def refused(self, line):
        return f"{self.rel}:{line}: Book Zero must not import a proposition"

    def test_each_spelling_of_the_negative_plants_is_refused_on_its_line(self):
        for what, text, *extra in negative.BOOK_ZERO_SPELLINGS:
            with self.subTest(what=what):
                found = self.findings(text)
                line = text.count("\n", 0, text.rindex("import")) + 1
                self.assertEqual(len(found), 1, found)
                self.assertTrue(found[0].startswith(self.refused(line)), found)
                for words in extra:
                    self.assertIn(words, found[0])

    def test_text_that_only_holds_an_import_is_not_refused(self):
        _, text = negative.BOOK_ZERO_TEXT
        self.assertEqual(self.findings(text), [])
        for text in ('def s := "\\" import Elements.BookI.Prop01"\n',
                     "def s := r#\"import Elements.BookI.Prop01\"#\n",
                     "def «import Elements.BookI.Prop01 » := 1\n",
                     "-- import Elements.BookI.Prop01\nimport Elements.Figure.Lines\n",
                     "/- /- -/ import Elements.BookI.Prop01 -/\n",
                     "theorem planted_import_ok : True := trivial\n",
                     "example := Lean.Parser.Module.import\n"):
            with self.subTest(text=text):
                self.assertEqual(self.findings(text), [])

    def test_a_comment_or_string_hides_no_import(self):
        for text, line in (("/- \" -/ import Elements.BookI.Prop01\n", 1),
                           ('def s := "/-"\nimport Elements.BookI.Prop01\n', 2),
                           ("-- a remark\n/-! A doc -/\nimport Elements.BookI.Prop01\n", 3),
                           ("import Elements.Figure.Lines -- a remark\n"
                            "import Elements.BookI.Prop01\n", 2),
                           # Lean reads these braces as text, but both readings end
                           # in one place, so read_lean keeps them as code (rule 4),
                           # failing closed.
                           ('def s := "{ import Elements.BookI.Prop01 }"\n', 1)):
            with self.subTest(text=text):
                self.assertEqual(self.findings(text), [self.refused(line)])

    def test_plain_imports_and_lean_s_own_pass(self):
        text = ("module\n\nprelude\npublic import Elements.Figure.Lines\n"
                "meta import  «Elements».«Foundations».Words\nimport all Init.Data.List.Basic\n")
        self.assertEqual(self.findings(text), [])

    def test_a_name_the_scan_cannot_read_is_refused(self):
        for text in ("import «Elements».«Book I».Prop01\n", "import «Elements.BookI».Prop01\n",
                     "import Elements.«».Prop01\n", "import Elements.Figure.Lines.\n",
                     "import Elements.«Figure»import Elements.BookI.Prop01\n", "import\n"):
            with self.subTest(text=text):
                found = self.findings(text)
                self.assertTrue(found and found[0].startswith(self.refused(1)), found)
                self.assertIn("cannot read this import for certain", found[0])

    def test_an_import_through_the_edition_s_files_is_refused(self):
        # Cycle.lean and Planted.lean import each other; Planted.lean brings in the rest.
        foundations = self.root / "Elements/Foundations"
        (foundations / "Cycle.lean").write_text("import Elements.Foundations.Planted\n")
        for planted, importer, brought in (
                ("import Elements.Companions\n", "Elements/Companions.lean",
                 "`Elements.BookI.Prop01`"),
                ("import «Elements/BookI».Prop01\n", "Elements/Foundations/Planted.lean",
                 "a module the scan cannot read for certain")):
            with self.subTest(planted=planted):
                (foundations / "Planted.lean").write_text(
                    "import Elements.Foundations.Cycle\n" + planted)
                self.assertEqual(self.findings("import Elements.Foundations.Cycle\n"),
                                 [f"{self.refused(1)}, and `Elements.Foundations.Cycle` brings "
                                  f"one in: {importer} imports {brought}"])

    def test_a_symlinked_module_directory_is_refused_without_reading_its_target(self):
        target = self.root / "Outside"
        target.mkdir()
        (target / "Bridge.lean").write_bytes(b"\xff")
        (self.root / "Elements/Alias").symlink_to(target, target_is_directory=True)
        self.assertEqual(self.findings("import Elements.Alias.Bridge\n"), [
            "Elements/Alias: a symbolic link, which the source scan does not follow; "
            "use a regular file or directory (docs/FORMALIZATION.md, section 7)",
            f"{self.refused(1)}, and `Elements.Alias.Bridge` reaches Elements/Alias, "
            "a symbolic link which the import scan does not follow",
        ])

    def test_a_root_module_symlink_is_refused_without_reading_its_target(self):
        target = self.root / "Outside.lean"
        target.write_bytes(b"\xff")
        (self.root / "Bridge.lean").symlink_to(target)
        self.assertEqual(self.findings("import Bridge\n"), [
            f"{self.refused(1)}, and `Bridge` reaches Bridge.lean, a symbolic link which "
            "the import scan does not follow",
        ])

    def test_a_transitive_symlinked_directory_outside_source_trees_is_refused(self):
        target = self.root / "Outside"
        target.mkdir()
        (target / "Hidden.lean").write_bytes(b"\xff")
        (self.root / "Support").symlink_to(target, target_is_directory=True)
        (self.root / "Bridge.lean").write_text("import Support.Hidden\n")
        self.assertEqual(self.findings("import Bridge\n"), [
            f"{self.refused(1)}, and `Bridge` reaches Support, a symbolic link which "
            "the import scan does not follow",
        ])

    def test_a_lone_carriage_return_in_a_followed_file_hides_no_import(self):
        # Bridge.lean, a root module the scan does not read for rule 4, read from its bytes
        # as Lean reads it: its `--` comment ends at the line feed, not at the lone `\r`, so
        # the quote after the `\r` opens no string, and the import on the next line is read.
        (self.root / "Bridge.lean").write_bytes(
            b'-- a remark\r"\nimport Elements.BookI.Prop01\n-- "\n')
        self.assertEqual(self.findings("import Bridge\n"), [
            f"{self.refused(1)}, and `Bridge` brings one in: Bridge.lean imports "
            "`Elements.BookI.Prop01`",
        ])

    def test_a_cycle_ends_and_files_outside_book_zero_may_import_propositions(self):
        (self.root / "Elements/Foundations/Words.lean").write_text(
            "import Elements.Figure.Lines\n")
        self.assertEqual(self.findings("import Elements.Figure.Lines\n"), [])
        self.assertEqual(self.findings("import Elements.BookI.Prop01\n",
                                       "Elements/BookI/Prop02.lean"), [])


class OverlapWayTests(unittest.TestCase):
    """check_fidelity's hold of an [overlap]'s combinations to Audit/Overlaps.lean, without
    Lean (#293): what `overlap_proofs` reads from the file's text, which combinations
    `check_overlap_ways` refuses, and the record that the plant `unproved_way` writes."""

    SECTION = "/-! ## Rules that state a proposition, give it at once, or supply its step -/"

    @staticmethod
    def pin(name, *axioms):
        return (f"/--\ninfo: '{name}' depends on axioms: [{', '.join(axioms)}]\n-/\n"
                f"#guard_msgs in\n#print axioms {name}\n")

    def setUp(self):
        self.errors = []
        self.enterContext(patch.object(negative.check_fidelity, "errors", self.errors))
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def proofs(self, text):
        path = self.root / f"Overlaps{len(list(self.root.iterdir()))}.lean"
        path.write_text(text, encoding="utf-8")
        return negative.check_fidelity.overlap_proofs(path)

    def audit(self, body, head="", pins=()):
        """A file in the audit's shape: `head`, then `body` in the section, in the namespace
        Audit, then each pin, as (name, axiom, …)."""
        return (f"{head}namespace Audit\n\n{self.SECTION}\n\n{body}\n"
                "/-! ## Hypotheses our measure leaves idle -/\n\nend Audit\n\n"
                + "".join(self.pin(*p) for p in pins))

    def test_the_audit_file_proves_main_s_combinations(self):
        """Main's file, in its own order (III.5 by crossing before radius, as III.5's note
        has them), and nothing of `Audit.I_7`, which proves no overlap."""
        proofs, problem = negative.check_fidelity.overlap_proofs(
            negative.check_fidelity.AUDIT_OVERLAPS)
        self.assertEqual(problem, "")
        found = {ref: [(name, sorted(axioms)) for name, axioms in found]
                 for ref, found in proofs.items()}
        self.assertEqual(found, {
            "III.2": [("Audit.III_2", ["Tacit.outside_of_between"]),
                      ("Audit.III_2_outside", ["Tacit.outside_of_between"])],
            "III.5": [("Audit.III_5", ["Tacit.circle_eq", "Tacit.inside_not_on"]),
                      ("Audit.III_5_crossing",
                       ["Definition15", "Tacit.len_lt_of_inside", "Tacit.lt_irrefl"]),
                      ("Audit.III_5_radius",
                       ["Definition15", "Tacit.inside_not_on", "Tacit.on_circle_of_len_eq"])],
            "III.6": [("Audit.III_6",
                       ["Tacit.centre_inside", "Tacit.circle_eq", "Tacit.inside_not_on"])]})
        self.assertIn("Audit.I_7", negative.check_fidelity.AUDIT_NOT_OVERLAPS)
        for ref in ("III.2", "III.5", "III.6"):
            n = int(ref.split(".")[1])
            negative.check_fidelity.check_overlap_ways(ref, ref, negative.heath.load_review(
                "III", n)["overlap"])
        self.assertEqual(self.errors, [])

    def test_only_a_pinned_theorem_of_the_first_section_of_the_proposition_s_type(self):
        rule = "Elements.Tacit.circle_eq"
        text = ("namespace Audit\n" + self.SECTION + "\n"
                "/-- theorem fake : type_of% @Elements.BookIII.Prop7 := x -/\n"
                "theorem kept : type_of% @Elements.BookIII.Prop5 := x\n"
                "theorem nameless : type_of% @Elements.BookIII.Prop5 := x\n"
                "theorem misnamed : type_of% @Elements.BookIII.Prop5 := x\n"
                "theorem twice : type_of% @Elements.BookIII.Prop5 := x\n"
                "theorem companion : type_of% @Elements.BookIII.Prop24.equalCircles := x\n"
                "theorem fake2 : True := x\n"
                "end Audit\nnamespace Other\n"
                "theorem elsewhere : type_of% @Elements.BookIII.Prop6 := x\nend Other\n"
                "namespace Audit\n/-! ## Hypotheses our measure leaves idle -/\n"
                "theorem later : type_of% @Elements.BookIII.Prop26 := x\nend Audit\n"
                + self.pin("Audit.kept", "propext", "Classical.choice", rule, "sorryAx",
                           "Quot.sound")
                + self.pin("Audit.fake", rule) + self.pin("Audit.companion", rule)
                + self.pin("Audit.later", rule) + self.pin("Audit.elsewhere", rule)
                + "/--\ninfo: 'Audit.other' depends on axioms: [" + rule + "]\n-/\n"
                "#guard_msgs in\n#print axioms Audit.misnamed\n"
                + "/--\ninfo: 'Audit.twice' depends on axioms: [" + rule + "]\n---\n"
                "info: 'Audit.twice' depends on axioms: [" + rule + "]\n-/\n"
                "#guard_msgs in\n#print axioms Audit.twice\n"
                + "-- " + self.pin("Audit.nameless", rule).replace("\n", " "))
        proofs, problem = self.proofs(text)
        self.assertEqual(problem, "")
        self.assertEqual(proofs, {"III.5": [("Audit.kept", frozenset(
            {"Tacit.circle_eq", "_root_.sorryAx"}))]})

    def test_a_file_without_its_first_section_is_named(self):
        for text, why in (("theorem t : type_of% @Elements.BookIII.Prop5 := x\n", "no"),
                          (self.SECTION + "\n" + self.SECTION + "\n", "more than one")):
            with self.subTest(why=why):
                proofs, problem = self.proofs(text)
                self.assertEqual(proofs, {})
                self.assertIn(f"has {why} section headed \"## Rules that state", problem)
        proofs, problem = negative.check_fidelity.overlap_proofs(self.root / "Missing.lean")
        self.assertEqual((proofs, problem[-10:]), ({}, "is missing"))
        # A link is not followed, though it points to a file the scan would accept, and is
        # named as written.
        target = self.root / "Target.lean"
        target.write_text(self.audit("theorem X : type_of% @Elements.BookIII.Prop5 :=\n  x\n",
                                     pins=[("Audit.X", "Elements.Tacit.a")]), encoding="utf-8")
        (self.root / "Link.lean").symlink_to(target)
        self.assertEqual(negative.check_fidelity.overlap_proofs(self.root / "Link.lean"),
                         ({}, f"{self.root}/Link.lean is a symbolic link, which the scan does "
                              "not follow"))
        self.assertEqual(negative.check_fidelity.overlap_proofs(target)[1], "")

    def test_a_heading_in_a_string_is_no_heading(self):
        """A string's text that reads as the section's heading, plain or raw, is no heading:
        alone, the file has no such section; beside the heading, it is not a second."""
        prop = "theorem X : type_of% @Elements.BookIII.Prop5 :=\n  x\n"
        for literal in (f'"{self.SECTION}"', f'r#"{self.SECTION}"#'):
            with self.subTest(literal=literal):
                proofs, problem = self.proofs(f"namespace Audit\ndef s := {literal}\n{prop}"
                                              "end Audit\n"
                                              + self.pin("Audit.X", "Elements.Tacit.a"))
                self.assertEqual(proofs, {})
                self.assertIn("has no section headed", problem)
                self.assertEqual(self.proofs(self.audit(f"def s := {literal}\n{prop}",
                                                        pins=[("Audit.X", "Elements.Tacit.a")])),
                                 ({"III.5": [("Audit.X", frozenset({"Tacit.a"}))]}, ""))

    def test_what_could_make_a_type_mean_another_refuses_the_file(self):
        """Files that Lean builds with their pins (the outside reviewer's probes: an
        instance-implicit `variable`, an `include`, a theorem that shadows a proposition, a
        namespace `Elements.BookIII` within Audit, an `export`; and a dotted constructor, a
        structure's, an instance with a priority, a «…» name, a theorem in a syntax
        quotation whose name another declaration has, and an import outside `Elements`;
        the second outside review's: a «…» name under `_root_` holding dots, a «…» name
        holding a dot beside a `where` auxiliary of that name, and a local notation that
        reads `type_of% … :=` otherwise): each could make the scan take a theorem for a
        proof of a proposition it does not prove, so each refuses the whole file, naming
        its line."""
        uses = "  have := @Elements.Tacit.inside_not_on\n"
        prop = "theorem T : type_of% @Elements.BookIII.Prop5 :=\n" + uses + "  x\n"
        for head, body, at, said in [
                ("", "class Bad : Prop where\n  bad : False\n\nvariable [Bad]\n\n"
                     "theorem III_5_inst : type_of% @Elements.BookIII.Prop5 :=\n" + uses
                     + "  (Bad.bad).elim\n", "variable [Bad]",
                 "has `variable` before the section's end"),
                ("", "include hX\n\ntheorem III_5_incl : type_of% @Elements.BookIII.Prop5 :=\n"
                     + uses + "  hX\n", "include hX", "has `include` before the section's end"),
                ("", "theorem Elements.BookIII.Prop6 : True := trivial\n\n"
                     "theorem III_6_shadow : type_of% @Elements.BookIII.Prop6 :=\n" + uses
                     + "  trivial\n", "theorem Elements",
                 "declares `Elements.BookIII.Prop6`, a name with a part `Elements`"),
                ("", "namespace Elements.BookIII\ntheorem Prop8 : True := trivial\n"
                     "end Elements.BookIII\n\ntheorem III_8_nested : type_of% "
                     "@Elements.BookIII.Prop8 :=\n" + uses + "  trivial\n",
                 "namespace Elements",
                 "opens the namespace `Elements.BookIII`, a name with a part `Elements`"),
                ("namespace Fake\ntheorem Prop7 : True := trivial\nend Fake\n\n",
                 "export Fake (Prop7)\n\ntheorem III_7_alias : type_of% "
                 "@Elements.BookIII.Prop7 :=\n" + uses + "  trivial\n", "export Fake",
                 "has `export` before the section's end"),
                ("", "inductive T : Prop\n  | Elements.BookIII.Prop5 : T\n\nnamespace T\n"
                     + prop + "end T\n", "| Elements",
                 "declares the constructor `Elements.BookIII.Prop5`"),
                ("", "structure S : Prop where\n  Elements.BookIII.Prop5 ::\n  x : True\n",
                 "Elements.BookIII.Prop5 ::",
                 "declares the constructor `Elements.BookIII.Prop5`"),
                ("", "class C : Prop where\n  x : True\n\n"
                     "instance (priority := 10) Elements.BookIII.Prop5 : C := ⟨trivial⟩\n\n"
                     + prop, "instance (priority",
                 "declares `Elements.BookIII.Prop5`, a name with a part `Elements`"),
                ("", "theorem «Elements».BookIII.Prop6 : True := trivial\n",
                 "theorem «Elements»", "declares `«Elements».BookIII.Prop6`"),
                ("", "def q : Lean.MacroM Lean.Syntax :=\n  `(command| theorem Z : type_of% "
                     "@Elements.BookIII.Prop5 := rfl)\n\ntheorem Z : True :=\n" + uses
                     + "  trivial\n", "theorem Z : type_of%",
                 "declares `Audit.Z`, and another declaration of the file has that name too"),
                ("import Elements\nimport Audit.Shadow\n\n", prop, "import Audit.Shadow",
                 "imports `Audit.Shadow`, outside `Elements`"),
                ("", "theorem _root_.«Elements.Tacit.inside_of_between» : type_of% "
                     "@Elements.BookIII.Prop6 :=\n  @Elements.BookIII.Prop6\n",
                 "theorem _root_", "declares `_root_.«Elements.Tacit.inside_of_between»`, a "
                 "name with a part in «…» that holds a dot"),
                ("", "theorem «III_5_y.x» : type_of% @Elements.BookIII.Prop5 := "
                     "@Elements.BookIII.Prop5\n\ndef III_5_y : Nat := 0\nwhere x : True :=\n"
                     "  have := @Elements.Tacit.len_lt_of_inside\n"
                     "  have := @Elements.Tacit.lt_irrefl\n  trivial\n",
                 "theorem «III_5_y.x»", "declares `«III_5_y.x»`, a name with a part in «…» "
                 "that holds a dot, which the scan cannot tell from a longer name"),
                ("", "section\nlocal notation:max \"type_of%\" _a:max \" := \" b:max => b\n\n"
                     "theorem III_5_n : type_of% @Elements.BookIII.Prop5 := True := by\n"
                     "  have := @Elements.Tacit.len_lt_of_inside\n"
                     "  have := @Elements.Tacit.lt_irrefl\n  trivial\nend\n",
                 "local notation", "has `notation` before the section's end")]:
            with self.subTest(said=said):
                text = self.audit(body, head, [(name, "Elements.Tacit.inside_not_on") for name
                                               in ("Audit.III_5_inst", "Audit.III_5_incl",
                                                   "Audit.III_6_shadow", "Audit.III_8_nested",
                                                   "Audit.III_7_alias", "Audit.T.T", "Audit.T",
                                                   "Audit.Z", "Elements.Tacit.inside_of_between",
                                                   "Audit.III_5_y.x", "Audit.III_5_n")])
                proofs, problem = self.proofs(text)
                line = text[:text.index(at)].count("\n") + 1
                self.assertEqual(proofs, {})
                self.assertIn(f".lean:{line} {said}", problem)
        # What follows the section cannot change what its theorems prove.
        self.assertEqual(self.proofs(self.audit(prop, pins=[("Audit.T", "Elements.Tacit.a")])
                                     + "variable (n : Nat)\nexport Fake (Prop7)\n"),
                         ({"III.5": [("Audit.T", frozenset({"Tacit.a"}))]}, ""))

    def test_the_namespaces_are_read_as_lean_reads_them(self):
        """Each theorem by the full name Lean gives it, so that the pin read is its own:
        with a dotted namespace that `end` closes a part at a time, a namespace opened in
        the middle of a line, or named on the next line, a `noncomputable section`, a
        `mutual` block and a dotted section, each closed by `end`, and `_root_`. In the first
        two, a scan that missed the namespace would take another theorem's pin."""
        prop = "theorem X : type_of% @Elements.BookIII.Prop5 :=\n  x\n"
        a, b = "Elements.Tacit.a", "Elements.Tacit.b"
        for head, body, pins, name in [
                ("theorem X : True := trivial\n\n", "namespace A.B\nend B\nend A\n" + prop,
                 [("X", b), ("Audit.X", a)], "Audit.X"),
                ("", "theorem X : True := trivial\ntheorem W : True := trivial namespace Foo\n"
                     + prop + "end Foo\n", [("Audit.X", b), ("Audit.Foo.X", a)], "Audit.Foo.X"),
                ("", "namespace\n  Foo\n" + prop + "end\n  Foo\n", [("Audit.Foo.X", a)],
                 "Audit.Foo.X"),
                ("", "noncomputable section\ntheorem Y : True := trivial\nend\n\nmutual\n"
                     "theorem Z : True := trivial\nend\n\nsection S.T\nend T\nend S\n" + prop,
                 [("Audit.X", a)], "Audit.X"),
                ("", prop.replace("theorem X", "theorem _root_.X"), [("X", a)], "X")]:
            with self.subTest(body=body):
                self.assertEqual(self.proofs(self.audit(body, head, pins)),
                                 ({"III.5": [(name, frozenset({"Tacit.a"}))]}, ""))

    def test_a_theorem_that_proves_no_overlap_is_left_out(self):
        """`Audit.I_7`, a circular derivation through I.7's own corollary, is no overlap of
        I.7, though its type is I.7's and its axioms are pinned."""
        text = self.audit("theorem I_7 : type_of% @Elements.BookI.Prop7 :=\n  x\n\n"
                          "theorem III_5 : type_of% @Elements.BookIII.Prop5 :=\n  x\n",
                          pins=[("Audit.I_7", "Elements.Tacit.a"),
                                ("Audit.III_5", "Elements.Tacit.a")])
        self.assertEqual(self.proofs(text),
                         ({"III.5": [("Audit.III_5", frozenset({"Tacit.a"}))]}, ""))

    def test_each_combination_must_be_proved_exactly(self):
        overlap = {"rule": "Tacit.circle_eq", "also": ["Tacit.inside_not_on"], "kind": "gives",
                   "ways": [["Definition15", "Tacit.len_lt_of_inside"],
                            ["Definition15", "Tacit.len_lt_of_inside", "Tacit.lt_irrefl",
                             "Tacit.circle_eq"],
                            ["Definition15", "Tacit.inside_not_on", "Tacit.on_circle_of_len_eq"]]}
        negative.check_fidelity.check_overlap_ways("III.5", "review/III/05.toml", overlap)
        self.assertEqual([e.split(" names ")[0] for e in self.errors],
                         ["review/III/05.toml: [overlap] `ways` 1",
                          "review/III/05.toml: [overlap] `ways` 2"])
        self.assertIn("The file proves III.5 from [Tacit.circle_eq, Tacit.inside_not_on] "
                      "(`Audit.III_5`), from [Definition15, Tacit.len_lt_of_inside, "
                      "Tacit.lt_irrefl] (`Audit.III_5_crossing`) and from [Definition15, "
                      "Tacit.inside_not_on, Tacit.on_circle_of_len_eq] (`Audit.III_5_radius`).",
                      self.errors[0])
        self.errors.clear()
        negative.check_fidelity.check_overlap_ways(
            "III.7", "review/III/07.toml", {"rule": "Tacit.circle_eq", "kind": "states"})
        self.assertEqual(len(self.errors), 1)
        self.assertIn("The file has no theorem there of type "
                      "`type_of% @Elements.BookIII.Prop7` with its axioms pinned", self.errors[0])

    def test_the_initial_combination_names_each_rule_once(self):
        base = negative.heath.load_review("III", 5)
        further = [["Definition15", "Tacit.len_lt_of_inside", "Tacit.lt_irrefl"]]
        for duplicate, also in (
                ("Tacit.circle_eq", ["Tacit.circle_eq"]),
                ("Tacit.inside_not_on", ["Tacit.inside_not_on", "Tacit.inside_not_on"])):
            for ways in (None, further):
                with self.subTest(duplicate=duplicate, ways=ways is not None):
                    overlap = {"rule": "Tacit.circle_eq", "also": also, "kind": "gives"}
                    if ways is not None:
                        overlap["ways"] = ways
                    with self.assertRaises(negative.heath.ReviewError) as caught:
                        negative.heath.validate_review(base | {"overlap": overlap}, "III", 5,
                                                       require_stamp=False,
                                                       where="the test record")
                    self.assertIn(
                        f"[overlap]: `rule` and `also` lists {duplicate!r} twice",
                        caught.exception.problems)

        for ways in (None, further):
            with self.subTest(valid=True, ways=ways is not None):
                overlap = {"rule": "Tacit.circle_eq", "also": ["Tacit.inside_not_on"],
                           "kind": "gives"}
                if ways is not None:
                    overlap["ways"] = ways
                checked = negative.heath.validate_review(base | {"overlap": overlap}, "III", 5,
                                                          require_stamp=False,
                                                          where="the test record")
                self.assertEqual(checked["overlap"], overlap)

    def test_the_plant_adds_one_way_and_keeps_the_rest_of_the_record(self):
        import tomllib
        text = negative.heath.review_path("III", 5).read_text()
        before = tomllib.loads(text)
        planted, k = negative.with_way(text, negative.UNPROVED_WAY)
        after = tomllib.loads(planted)
        self.assertEqual(k, len(before["overlap"].get("ways", [])) + 1)
        self.assertEqual(after["overlap"].pop("ways")[-1], negative.UNPROVED_WAY)
        before["overlap"].pop("ways", None)
        self.assertEqual(after, before)
        # A record that has `ways` already, written across lines, gains the plant's at the end.
        twice, k2 = negative.with_way(planted, ["Tacit.circle_eq", "Tacit.centre_inside"])
        self.assertEqual((k2, tomllib.loads(twice)["overlap"]["ways"][-2:]),
                         (k + 1, [negative.UNPROVED_WAY,
                                  ["Tacit.circle_eq", "Tacit.centre_inside"]]))
        record = negative.heath.validate_review(after | {"overlap": tomllib.loads(planted)[
            "overlap"]}, "III", 5, require_stamp=False, where="the planted record")
        negative.check_fidelity.check_overlap_ways("III.5", "the planted record",
                                                   record["overlap"])
        self.assertEqual(len(self.errors), 1, self.errors)
        self.assertTrue(self.errors[0].startswith(
            f"the planted record: [overlap] `ways` {k} names "
            "[Tacit.len_lt_of_inside, Tacit.lt_irrefl] as containing III.5"), self.errors[0])


class CommentReaderTests(unittest.TestCase):
    """The one reader of Lean comments that the scripts share, check_fidelity's
    `comment_end`, read through `lean_comments` and `read_lean`, without Lean (#206): the
    texts on which a reader that began a block's body at its third character, or read no
    strings or character literals, could read otherwise than Lean 4.35. Each expected
    reading is Lean's: each text was elaborated in Lean 4.35 as written, alone in a scratch
    file outside the tree, where the names after its comments were defined, those within
    them unknown, and each of UNCLOSED refused as an unterminated comment. Then
    the three readers that call it, check_fidelity's `_blank_remarks`, check_style's
    `lean_note_spans` and the Jev generator's `comment_end`, each read them so too."""

    # (a text, the comments Lean reads in it, in order, the names it defines and those it
    # does not, which stand within a comment)
    CASES = (
        ("/-/- -/ def after_slash_dash : Nat := 1\n", ["/-/- -/"], ["after_slash_dash"], []),
        ("/-/ x -/ def after_slash : Nat := 2\n", ["/-/ x -/"], ["after_slash"], []),
        ("/-/-/ def after_slash_dash_slash : Nat := 3\n", ["/-/-/"],
         ["after_slash_dash_slash"], []),
        ("/--/ def hidden_in_doc : Nat := 0 -/ def after_doc_slash : Nat := 4\n",
         ["/--/ def hidden_in_doc : Nat := 0 -/"], ["after_doc_slash"], ["hidden_in_doc"]),
        ("/-!/ x -/ def after_module_doc_slash : Nat := 5\n", ["/-!/ x -/"],
         ["after_module_doc_slash"], []),
        ("/- /- -/ def hidden_in_nested : Nat := 0 -/ def after_nested : Nat := 6\n",
         ["/- /- -/ def hidden_in_nested : Nat := 0 -/"], ["after_nested"],
         ["hidden_in_nested"]),
        ('def opener_in_string : String := "/-" def after_string : Nat := 7\n', [],
         ["opener_in_string", "after_string"], []),
        ('def closer_after_quote : Nat := 8 /- "-/ def after_quote : Nat := 9 -- "\n',
         ['/- "-/', '-- "'], ["closer_after_quote", "after_quote"], []),
        ("def dash_char : Char := '-'/- a remark -/ def after_dash_char : Nat := 10\n",
         ["/- a remark -/"], ["dash_char", "after_dash_char"], []),
        ("def slash_char : Char := '/'-- a remark\ndef after_slash_char : Nat := 11\n",
         ["-- a remark"], ["slash_char", "after_slash_char"], []),
        ("def quote_char : Char := '\"' /- \"-/ def after_quote_char : Nat := 12 -- \"\n",
         ['/- "-/', '-- "'], ["quote_char", "after_quote_char"], []),
        ("/- -- -/ def after_dashes_in_block : Nat := 13\n", ["/- -- -/"],
         ["after_dashes_in_block"], []),
        ("-- /-\ndef after_opener_in_line : Nat := 14\n", ["-- /-"],
         ["after_opener_in_line"], []),
        ('def in_hole : String := s!"{(1 : Nat) /- c -/}" def after_hole : Nat := 15\n',
         ["/- c -/"], ["in_hole", "after_hole"], []),
    )
    # Likewise, each with its last comment not closed, which runs to the end.
    UNCLOSED = (
        ("def before_unclosed : Nat := 1\n/- unclosed /- -/\ndef hidden_unclosed : Nat := 0\n",
         ["/- unclosed /- -/\ndef hidden_unclosed : Nat := 0\n"], ["before_unclosed"],
         ["hidden_unclosed"]),
        ("def before_bare : Nat := 1\n/-", ["/-"], ["before_bare"], []),
    )

    @classmethod
    def setUpClass(cls):
        import check_style
        cls.check_style = check_style
        spec = importlib.util.spec_from_file_location(
            "jev_questions_comment_reader", REPO / "scripts/audit/jev_questions.py")
        cls.questions = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.questions
        cls.addClassCleanup(sys.modules.pop, spec.name, None)
        spec.loader.exec_module(cls.questions)

    def spans(self, text, comments):
        """Each of `comments`, read from `text` in order, as its offsets in it."""
        found, at = [], 0
        for comment in comments:
            at = text.index(comment, at)
            found.append((at, at + len(comment)))
            at += len(comment)
        return found

    def cases(self):
        """Each case, with its comments' offsets and whether its last comment is closed."""
        for (text, comments, defined, hidden), closed in (
                [(case, True) for case in self.CASES]
                + [(case, False) for case in self.UNCLOSED]):
            yield text, self.spans(text, comments), defined, hidden, closed

    def test_each_comment_ends_where_lean_ends_it(self):
        for text, spans, _, _, closed in self.cases():
            with self.subTest(text=text):
                self.assertEqual(negative.check_fidelity.lean_comments(text), spans)
                for start, end in spans[:None if closed else -1]:
                    self.assertEqual(negative.check_fidelity.comment_end(text, start), end)
                if not closed:
                    self.assertEqual(spans[-1][1], len(text))
                    self.assertIsNone(negative.check_fidelity.comment_end(text, spans[-1][0]))

    def test_read_lean_shows_the_names_lean_defines_and_no_other(self):
        for text, _, defined, hidden, _ in self.cases():
            with self.subTest(text=text):
                words = set(re.findall(r"\w+", negative.check_fidelity.read_lean(text)[0]))
                self.assertLessEqual(set(defined), words)
                self.assertFalse(set(hidden) & words)

    def test_plain_string_braces_create_no_speculative_comment(self):
        comment = "/- not_a_comment -/"
        text = f'def s : String := "{{ {comment} }}"\n'
        expected = text.replace(comment, " " * len(comment))
        strings = []
        self.assertEqual(negative.check_fidelity.lean_comments(text), [])
        self.assertEqual(negative.check_fidelity._blank_remarks(text), text)
        self.assertEqual(self.check_style.lean_note_spans(text), [])
        self.assertEqual(negative.check_fidelity.read_lean(text, strings), (expected, []))
        self.assertEqual(strings, [(text.index('"'), f"{{ {comment} }}")])

    def test_the_readers_that_call_it_read_each_case_so(self):
        for text, spans, _, _, closed in self.cases():
            blocks = [(i, j) for i, j in spans if text.startswith("/-", i)]
            remarks = list(text)
            for i, j in blocks:
                remarks[i:j] = ["\n" if ch == "\n" else " " for ch in text[i:j]]
            ended = spans if closed else spans[:-1]
            notes = [(i + (3 if text.startswith(("/--", "/-!"), i) else 2), j - 2)
                     for i, j in blocks if (i, j) in ended]
            with self.subTest(text=text):
                self.assertEqual(negative.check_fidelity._blank_remarks(text), "".join(remarks))
                self.assertEqual(self.check_style.lean_note_spans(text), notes)
                for i, j in ended:
                    self.assertEqual(self.questions.comment_end(text, i), j)
                if not closed:
                    with self.assertRaisesRegex(self.questions.Refusal, "unterminated"):
                        self.questions.comment_end(text, spans[-1][0])

    def test_the_jev_generator_runs_check_fidelity_s_own_reader(self):
        source = b'''raise AssertionError("unrelated top-level code ran")

def comment_end(src, i):
    return ("controlled reader", src, i)
'''
        checked = (REPO / "scripts/check_fidelity.py").resolve()
        with patch.object(self.questions, "read_no_follow", return_value=source) as read:
            reader = self.questions.shared_function(*self.questions.READER)
        read.assert_called_once_with(checked)
        self.assertEqual(reader("prefix /- comment -/ suffix", 7),
                         ("controlled reader", "prefix /- comment -/ suffix", 7))

    def test_the_jev_generator_prepares_its_reader_before_running_helpers(self):
        invalid = (
            ("missing", None, r"check_fidelity\.py: helper module is missing"),
            ("absent", b"def another_function():\n    pass\n",
             r"defines no single function comment_end"),
            ("duplicate", b"def comment_end(src, i):\n    pass\n\n"
                          b"def comment_end(src, i):\n    pass\n",
             r"defines no single function comment_end"),
        )
        helper_names = {name for name, _ in self.questions.HELPERS}
        for label, reader, message in invalid:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                audit = root / "scripts/audit"
                audit.mkdir(parents=True)
                generator = audit / "jev_questions.py"
                generator.write_bytes((REPO / "scripts/audit/jev_questions.py").read_bytes())
                (root / "scripts/heath.py").write_text(
                    'raise AssertionError("heath helper ran")\n', encoding="utf-8")
                (audit / "jev.py").write_text(
                    'raise AssertionError("Jev helper ran")\n', encoding="utf-8")
                if reader is not None:
                    (root / "scripts/check_fidelity.py").write_bytes(reader)
                name = f"jev_questions_invalid_reader_{label}"
                spec = importlib.util.spec_from_file_location(name, generator)
                module = importlib.util.module_from_spec(spec)
                with patch.dict(sys.modules) as modules:
                    for dependency in helper_names:
                        modules.pop(dependency, None)
                    modules[name] = module
                    with self.assertRaisesRegex(ValueError, message):
                        spec.loader.exec_module(module)
                    self.assertFalse(helper_names & modules.keys())

    def test_the_jev_generator_delegates_to_check_fidelity_s_reader(self):
        source = "prefix /- comment -/ suffix"
        offset = source.index("/-")
        sentinel = object()
        with patch.object(self.questions, "shared_comment_end", return_value=sentinel) as shared:
            self.assertIs(self.questions.comment_end(source, offset), sentinel)
        shared.assert_called_once_with(source, offset)

        with patch.object(self.questions, "shared_comment_end", return_value=None) as shared:
            with self.assertRaisesRegex(self.questions.Refusal,
                                        r"^unterminated Lean comment$"):
                self.questions.comment_end(source, offset)
        shared.assert_called_once_with(source, offset)


PLANT = '''{doc}
import subprocess

import negative_tests as nt

{builds}


{plant}
'''
DOC = '"""A plant the loader\'s tests write."""'


def plant_source(name, *, doc=DOC, builds="BUILDS = False", body='nt.refused("{name}: caught")',
                 function=None, before=""):
    """A plant's file: it leaves planted-<name> in ROOT, so a test sees that it ran, and then
    does `body`; `before`, if given, is module-level code ahead of plant()."""
    if function is None:
        function = ("def plant() -> None:\n"
                    f'    (nt.ROOT / "planted-{name}").touch()\n'
                    f"    {body.format(name=name)}")
    if before:
        function = f"{before}\n\n\n{function}"
    return PLANT.format(doc=doc, builds=builds, plant=function)


def unchecked_bytecode(source, cfile):
    """Compile `source` to `cfile` as bytecode that Python's import never compares with the
    source beside it (an unchecked hash), the bytecode a plant's or the runner's could be."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "stand_in.py"
        path.write_text(source)
        Path(cfile).parent.mkdir(parents=True, exist_ok=True)
        py_compile.compile(str(path), cfile=str(cfile), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)


class LoaderTests(unittest.TestCase):
    """The loader of scripts/negative/, and main() around it, on temporary folders of small
    plants, without Lean or Git: `run` is a stand-in that passes, so the regressions, the
    Git bracket and the final check are calls it records."""

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.folder = self.root / "scripts/negative"
        self.folder.mkdir(parents=True)
        self.enterContext(patch.multiple(negative, ROOT=self.root, failures=[]))
        self.calls = []
        self.fidelity = 0

        def run(*cmd):
            self.calls.append(cmd)
            code = self.fidelity if cmd[1:] == ("scripts/check_fidelity.py",) else 0
            return subprocess.CompletedProcess(cmd, code, "", "")
        self.enterContext(patch.object(negative, "run", side_effect=run))
        self.output = self.enterContext(redirect_stdout(io.StringIO()))

    def write(self, name, text):
        (self.folder / name).write_text(text)

    def reset(self):
        for path in (self.root / "scripts", self.folder):
            if path.is_symlink():
                path.unlink()
        if (self.root / "elsewhere").exists():
            shutil.rmtree(self.root / "elsewhere")
        if self.folder.is_dir():
            shutil.rmtree(self.folder)
        else:
            self.folder.unlink(missing_ok=True)
        self.folder.mkdir(parents=True)
        for path in self.root.glob("planted-*"):
            path.unlink()
        negative.failures.clear()
        self.calls.clear()
        self.output.truncate(0)
        self.output.seek(0)

    def planted(self):
        return sorted(p.name.removeprefix("planted-") for p in self.root.glob("planted-*"))

    def git_status(self):
        return [cmd for cmd in self.calls if cmd[:2] == ("git", "status")]

    def assert_refused_before_planting(self, *faults):
        """main() fails on `faults`, each the start of a failure, with nothing planted and no
        closing check of the unplanted tree; the entry Git status, taken before loading, is
        compared once more at the end."""
        self.assertEqual(negative.main(), 1)
        self.assertEqual(len(negative.failures), len(faults), negative.failures)
        for fault, failure in zip(faults, negative.failures):
            self.assertTrue(failure.startswith(fault), f"{failure!r} for {fault!r}")
            self.assertIn(f"✗ {failure}\n", self.output.getvalue())
        self.assertIn("loading the plants (scripts/negative/):\n  ✗ " + negative.failures[0],
                      self.output.getvalue())
        self.assertEqual(self.planted(), [])
        self.assertEqual(len(self.git_status()), 2)
        self.assertNotIn((sys.executable, "scripts/check_fidelity.py"), self.calls)

    def test_the_stable_order(self):
        for name, builds in (("zeta", False), ("alpha", True), ("beta", False),
                             ("gamma", True), ("a1_b", False)):
            self.write(f"{name}.py", plant_source(name, builds=f"BUILDS = {builds}"))
        plants, faults = negative.load_plants()
        self.assertEqual(faults, [])
        order = [("a1_b", False), ("beta", False), ("zeta", False), ("alpha", True),
                 ("gamma", True)]
        self.assertEqual([(p.name, p.builds) for p in plants], order)
        self.assertEqual(plants[0].path, self.folder / "a1_b.py")
        self.assertEqual(plants[0].description, "A plant the loader's tests write.")
        again, faults = negative.load_plants(self.folder)
        self.assertEqual([p[:4] for p in again], [p[:4] for p in plants])
        self.assertEqual(faults, [])
        self.assertEqual(negative.main(), 0)
        output = self.output.getvalue()
        headings = [output.index(f"\n{name} (scripts/negative/{name}.py)\n") for name, _ in order]
        self.assertEqual(headings, sorted(headings))
        for name, _ in order:
            self.assertRegex(output, rf"\n  {name}: \d+\.\d\ds \(including restoration\)\n")
        self.assertEqual(self.planted(), sorted(name for name, _ in order))
        self.assertEqual(len(self.git_status()), 2)

    def test_each_fault_fails_main_with_nothing_planted(self):
        def file(text=""):
            return lambda path: path.write_text(text)

        def link(target):
            return lambda path: path.symlink_to(target)

        def directory(path):
            path.mkdir()

        name = "not a plant's file name, which is [a-z][a-z0-9_]*.py"
        unloaded = "does not load: "
        cases = [
            ("Capital.py", file(plant_source("Capital")), name),
            ("1st.py", file(plant_source("1st")), name),
            ("with-dash.py", file(plant_source("dash")), name),
            ("_private.py", file(plant_source("private")), name),
            ("notes.txt", file("notes"), name),
            ("good.py.orig", file(plant_source("orig")), name),
            ("README", file("A folder of plants."), name),
            ("__pycache__", file(), name),
            (".good.py.swp", file("an editor's swap file"), name),
            (".DS_Store", directory, "a directory, not a plant's file"),
            (".DS_Store", link(self.folder / "good.py"), "a symbolic link, which is not read"),
            ("linked.py", link(self.folder / "good.py"), "a symbolic link, which is not read"),
            ("dangling.py", link(self.root / "missing.py"), "a symbolic link, which is not read"),
            ("cached", link(self.root), "a symbolic link, which is not read"),
            ("nested", directory, "a directory, not a plant's file"),
            ("nested.py", directory, "a directory, not a plant's file"),
            ("broken.py", file(plant_source("broken", function="def plant(:\n    pass")),
             unloaded + "SyntaxError: "),
            ("raises.py", file(DOC + '\nraise RuntimeError("raised on import")\n'),
             unloaded + "RuntimeError: raised on import"),
            ("exits.py", file(DOC + "\nimport sys\nsys.exit(3)\n"), unloaded + "SystemExit: 3"),
            ("imports.py", file(DOC + "\nimport no_such_module_for_a_plant\n"),
             unloaded + "ModuleNotFoundError: "),
            ("undescribed.py", file(plant_source("undescribed", doc="")), "no description"),
            ("blank.py", file(plant_source("blank", doc='"""  \n  """')), "no description"),
            ("unbuilt.py", file(plant_source("unbuilt", builds="")), "no BUILDS"),
            ("one.py", file(plant_source("one", builds="BUILDS = 1")),
             "BUILDS is 1, not True or False"),
            ("words.py", file(plant_source("words", builds='BUILDS = "False"')),
             "BUILDS is 'False', not True or False"),
            ("nothing.py", file(plant_source("nothing", builds="BUILDS = None")),
             "BUILDS is None, not True or False"),
            ("plantless.py", file(plant_source("plantless", function="")), "no plant()"),
            ("uncallable.py", file(plant_source("uncallable", function='plant = "plant"')),
             "plant is str, not a function"),
            ("argued.py", file(plant_source("argued", function="def plant(where):\n    pass")),
             "plant() must take no arguments"),
            ("keyword.py",
             file(plant_source("keyword", function="def plant(*, where):\n    pass")),
             "plant() must take no arguments"),
        ]
        for entry, make, reason in cases:
            with self.subTest(entry=entry, reason=reason):
                self.reset()
                self.write("good.py", plant_source("good"))
                make(self.folder / entry)
                self.assert_refused_before_planting(f"scripts/negative/{entry}: {reason}")
        with self.subTest(entry="several faults in one file"):
            self.reset()
            self.write("bare.py", plant_source("bare", doc="", builds="", function=""))
            self.assert_refused_before_planting(
                "scripts/negative/bare.py: no description", "scripts/negative/bare.py: no BUILDS",
                "scripts/negative/bare.py: no plant()")

    def test_a_missing_or_empty_folder_fails_main(self):
        cases = [("missing", lambda: self.folder.rmdir(),
                  "scripts/negative: the plants' folder cannot be listed (FileNotFoundError"),
                 ("a file", lambda: (self.folder.rmdir(), self.folder.write_text("")),
                  "scripts/negative: the plants' folder cannot be listed (NotADirectoryError"),
                 ("empty", lambda: None, "scripts/negative: no plants"),
                 ("only __pycache__", lambda: (self.folder / "__pycache__").mkdir(),
                  "scripts/negative: no plants"),
                 ("only .DS_Store", lambda: (self.folder / ".DS_Store").write_bytes(b"\0"),
                  "scripts/negative: no plants")]
        linked = ("scripts/negative: the plants' folder is, or passes through, a symbolic "
                  "link")

        def a_linked_folder():
            elsewhere = self.root / "elsewhere"
            elsewhere.mkdir()
            (elsewhere / "good.py").write_text(plant_source("good"))
            self.folder.rmdir()
            self.folder.symlink_to(elsewhere, target_is_directory=True)

        def a_linked_scripts_folder():
            scripts = self.root / "scripts"
            elsewhere = self.root / "elsewhere"
            scripts.rename(elsewhere)
            (elsewhere / "negative/good.py").write_text(plant_source("good"))
            scripts.symlink_to(elsewhere, target_is_directory=True)

        cases += [("a link", a_linked_folder, linked),
                  ("in a linked scripts/", a_linked_scripts_folder, linked)]
        for what, make, fault in cases:
            with self.subTest(folder=what):
                self.reset()
                make()
                self.assert_refused_before_planting(fault)
        with self.subTest(folder="an entry that resolves outside it"):
            # As if the entry became a link after it was looked at: the loader still reads
            # only a file directly in the folder.
            self.reset()
            (self.root / "elsewhere").mkdir()
            (self.root / "elsewhere/outside.py").write_text(plant_source("outside"))
            (self.folder / "outside.py").symlink_to(self.root / "elsewhere/outside.py")
            with patch.object(Path, "is_symlink", lambda path: False):
                self.assert_refused_before_planting(
                    f"scripts/negative/outside.py: resolves to {self.root}/elsewhere/outside.py, "
                    "which is not directly in the plants' folder")
        self.reset()

    def test_pycache_and_ds_store_are_passed_over(self):
        self.write("good.py", plant_source("good"))
        (self.folder / "__pycache__").mkdir()
        (self.folder / "__pycache__/stale.cpython-312.pyc").write_bytes(b"not a plant")
        (self.folder / ".DS_Store").write_bytes(b"\0\0\0\1Bud1")
        plants, faults = negative.load_plants()
        self.assertEqual(([p.name for p in plants], faults), (["good"], []))
        self.assertIn("note: scripts/negative/.DS_Store passed over: Finder's settings for "
                      "the folder, which Git ignores, not a plant\n", self.output.getvalue())

    def test_a_plant_is_compiled_from_its_text_never_from_bytecode(self):
        """Bytecode beside a plant, which Python's import would run without comparing it
        with the source, is not read: the plant is the file's text."""
        self.write("good.py", plant_source("good"))
        unchecked_bytecode(plant_source("good", doc='"""From bytecode."""',
                                        builds="BUILDS = True"),
                           importlib.util.cache_from_source(str(self.folder / "good.py")))
        plants, faults = negative.load_plants()
        self.assertEqual(faults, [])
        self.assertEqual([(p.name, p.description, p.builds) for p in plants],
                         [("good", "A plant the loader's tests write.", False)])

    def test_a_plant_that_exits_fails_and_the_run_goes_on(self):
        self.write("a_exits.py", plant_source("a_exits", before="import sys",
                                              body='nt.refused("{name}: caught"); sys.exit(0)'))
        self.write("b_later.py", plant_source("b_later"))
        self.assertEqual(negative.main(), 1)
        message = "a_exits: plant() exited (0) instead of returning"
        self.assertEqual(negative.failures, [message])
        self.assertIn(f"a_exits (scripts/negative/a_exits.py):\n  ✗ {message}\n",
                      self.output.getvalue())
        self.assertEqual(self.planted(), ["a_exits", "b_later"])
        self.assertIn((sys.executable, "scripts/check_fidelity.py"), self.calls)
        self.assertEqual(len(self.git_status()), 2)

    def test_a_run_that_stops_short_of_its_plants_fails(self):
        """A plant that empties the runner's list of chosen plants stops the loop early;
        the run counts the plants it ran against those chosen."""
        self.write("a_clears.py", plant_source("a_clears", before="import sys", body=(
            'nt.refused("{name}: caught"); sys._getframe(2).f_locals["chosen"].clear()')))
        self.write("b_never.py", plant_source("b_never"))
        self.assertEqual(negative.main(), 1)
        self.assertEqual(negative.failures, ["only 1 of the 2 plants chosen were run"])
        self.assertEqual(self.planted(), ["a_clears"])

    def test_a_file_that_changes_a_shared_name_fails_by_name(self):
        """A plant's file may not rebind or delete a name of the runner, nor of the modules
        it shares, nor add one to the runner, as it loads or as its plant() runs; the name is
        put back, so the plants after it are judged by the runner's own helpers."""
        expect_failure = negative.expect_failure
        check_lock = negative.check_fidelity.check_lock
        # Each name is put back by these too, should the guard fail, so no later test meets
        # a changed one.
        for module, name in ((negative, "expect_failure"), (negative, "PLANT_FILE"),
                             (negative.check_fidelity, "check_lock"), (negative.heath, "ROOT")):
            self.enterContext(patch.object(module, name, getattr(module, name)))
        self.addCleanup(lambda: vars(negative).pop("planted_name", None))
        fake = "lambda *args, **kwargs: nt.refused('faked')"
        later = plant_source("b_later", body=(
            'nt.expect_failure("a check that passes", subprocess.CompletedProcess('
            '[], 0, "", ""))'))
        put_back = ("(put back); a plant leaves the names it shares with the runner as it "
                    "finds them")
        with self.subTest(when="as it loads"):
            self.reset()
            self.write("good.py", plant_source("good"))
            self.write("rebinds.py", plant_source("rebinds", before=f"nt.expect_failure = {fake}"))
            self.assert_refused_before_planting(
                "scripts/negative/rebinds.py: rebinds negative_tests.expect_failure as it loads "
                + put_back)
            self.assertIs(negative.expect_failure, expect_failure)
        for change, reason in (
                (f"nt.expect_failure = {fake}", "rebinds negative_tests.expect_failure"),
                ("nt.check_fidelity.check_lock = lambda *args: 0",
                 "rebinds check_fidelity.check_lock"),
                ("nt.failures = []", "rebinds negative_tests.failures"),
                ("nt.planted_name = 1", "adds negative_tests.planted_name"),
                ("del nt.PLANT_FILE", "deletes negative_tests.PLANT_FILE"),
                ("del nt.heath.ROOT", "deletes heath.ROOT")):
            with self.subTest(when="as it runs", change=change):
                self.reset()
                failures = negative.failures
                self.write("a_changes.py", plant_source("a_changes", body=change))
                self.write("b_later.py", later)
                self.assertEqual(negative.main(), 1)
                message = (f"a_changes: scripts/negative/a_changes.py {reason} as it runs "
                           f"{put_back}")
                self.assertIs(negative.failures, failures)
                self.assertEqual(negative.failures,
                                 [message, "a check that passes: not caught"])
                self.assertIn(f"a_changes (scripts/negative/a_changes.py):\n  ✗ {message}\n",
                              self.output.getvalue())
                self.assertEqual(self.planted(), ["a_changes", "b_later"])
                self.assertIs(negative.expect_failure, expect_failure)
                self.assertIs(negative.check_fidelity.check_lock, check_lock)
                self.assertFalse(hasattr(negative, "planted_name"))
                self.assertTrue(hasattr(negative, "PLANT_FILE"))
                self.assertEqual(negative.heath.ROOT, REPO)
        with self.subTest(when="a name added to a shared module"):
            self.reset()
            self.addCleanup(lambda: vars(negative.check_fidelity).pop("planted_name", None))
            self.write("adds.py", plant_source("adds", body=(
                'nt.check_fidelity.planted_name = 1; nt.refused("{name}: caught")')))
            self.assertEqual(negative.main(), 0)
            self.assertEqual(negative.failures, [])

    def test_a_name_changed_by_the_closing_check_fails(self):
        """The names are looked at once more after the closing check of the unplanted tree,
        so a change made after the last plant's guard, as by a hook that a file left as it
        loaded, fails the run, and the name is put back."""
        check_lock = negative.check_fidelity.check_lock
        self.enterContext(patch.object(negative.check_fidelity, "check_lock", check_lock))

        def run(*cmd):
            self.calls.append(cmd)
            if cmd[1:] == ("scripts/check_fidelity.py",):
                negative.check_fidelity.check_lock = lambda *args: 0
            return subprocess.CompletedProcess(cmd, 0, "", "")
        self.write("good.py", plant_source("good"))
        with patch.object(negative, "run", side_effect=run):
            self.assertEqual(negative.main(), 1)
        message = ("rebinds check_fidelity.check_lock after the closing check (put back); a "
                   "plant leaves the names it shares with the runner as it finds them")
        self.assertEqual(negative.failures, [message])
        self.assertIn(f"outside any plant:\n  ✗ {message}\n", self.output.getvalue())
        self.assertIs(negative.check_fidelity.check_lock, check_lock)

    def test_a_plant_that_changes_earlier_failures_or_refusals_fails(self):
        """The failures and refusals recorded before a plant only grow: a plant() that
        clears the failures, or pops a refusal, fails by its name, and the earlier entries
        are put back, so the closing list still holds the earlier failure."""
        earlier = ('nt.refused("{name}: caught"); nt.expect_failure("a check that passes", '
                   'subprocess.CompletedProcess([], 0, "", ""))')
        message = "b_changes: changed the failures or refusals recorded before it"
        for change in ("nt.failures.clear()", "nt.refusals.pop()"):
            with self.subTest(change=change):
                self.reset()
                refusals = len(negative.refusals)
                self.write("a_earlier.py", plant_source("a_earlier", body=earlier))
                self.write("b_changes.py", plant_source("b_changes", body=(
                    change + '; nt.refused("{name}: caught")')))
                self.write("c_later.py", plant_source("c_later"))
                self.assertEqual(negative.main(), 1)
                self.assertEqual(negative.failures, ["a check that passes: not caught", message])
                self.assertEqual(negative.refusals[refusals], "a_earlier: caught")
                self.assertTrue(self.output.getvalue().endswith(
                    "2 negative-test failure(s):\n"
                    "a_earlier (scripts/negative/a_earlier.py):\n"
                    "  ✗ a check that passes: not caught\n"
                    f"b_changes (scripts/negative/b_changes.py):\n  ✗ {message}\n"))
                self.assertEqual(self.planted(), ["a_earlier", "b_changes", "c_later"])

    def test_a_warning_recorded_against_the_runner_is_passed_over(self):
        """Python's warnings machinery adds `__warningregistry__` to the module a warning is
        attributed to, ignored warnings too, so the guard passes over that one name
        (UNGUARDED): a plant whose helper raises a warning is not refused for it."""
        vars(negative).pop("__warningregistry__", None)
        self.addCleanup(lambda: vars(negative).pop("__warningregistry__", None))
        self.write("warns.py", plant_source("warns", before="import warnings", body=(
            'warnings.warn_explicit("probe", UserWarning, "negative_tests.py", 1, '
            'registry=vars(nt).setdefault("__warningregistry__", {{}})); '
            'nt.refused("{name}: caught")')))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(negative.main(), 0)
        self.assertEqual(negative.failures, [])
        self.assertIn("__warningregistry__", vars(negative))

    def test_the_entry_git_status_comes_first_of_all(self):
        """The restoration regressions load the real plants' folder, so the entry Git status
        is taken before them, as main()'s first command."""
        self.write("good.py", plant_source("good"))
        self.assertEqual(negative.main(), 0)
        self.assertEqual(self.calls[0], ("git", "status", "--porcelain"))
        self.assertEqual(self.calls[1], (sys.executable, "-I", "tests/test_negative_tests.py"))

    def test_a_file_written_as_a_plant_loads_shows(self):
        """The entry Git status is taken before the plants' files are read, so a file that
        one writes as it loads is a change the closing comparison sees."""
        def run(*cmd):
            self.calls.append(cmd)
            written = sorted(p.name for p in self.root.glob("written-*"))
            status = cmd[:2] == ("git", "status")
            out = "".join(f"?? {name}\n" for name in written) if status else ""
            return subprocess.CompletedProcess(cmd, 0, out, "")
        self.write("writes.py", plant_source("writes", before=(
            '(nt.ROOT / "written-as-it-loads").touch()')))
        with patch.object(negative, "run", side_effect=run):
            self.assertEqual(negative.main(), 1)
        self.assertEqual(negative.failures,
                         ["the working tree did not return to its entry Git status"])
        self.assertIn("?? written-as-it-loads\n", self.output.getvalue())

    def test_a_plant_that_refuses_nothing_fails_by_name(self):
        self.write("quiet.py", plant_source("quiet", body='print("✓ a control, not a refusal")'))
        self.write("loud.py", plant_source("loud"))
        self.assertEqual(negative.main(), 1)
        message = "quiet: nothing refused what scripts/negative/quiet.py planted"
        self.assertEqual(negative.failures, [message])
        self.assertIn(f"✗ {message}\n", self.output.getvalue())
        self.assertIn(f"quiet (scripts/negative/quiet.py):\n  ✗ {message}\n",
                      self.output.getvalue())
        self.assertEqual(self.planted(), ["loud", "quiet"])
        self.assertEqual(len(self.git_status()), 2)

    def test_a_plant_whose_check_passes_fails(self):
        self.write("passes.py", plant_source("passes", body=(
            'nt.expect_failure("a check that passes", subprocess.CompletedProcess('
            '[], 0, "", ""), "refused")')))
        self.assertEqual(negative.main(), 1)
        message = "a check that passes: not caught (missing 'refused')"
        self.assertEqual(negative.failures, [message])
        self.assertIn(f"passes (scripts/negative/passes.py):\n  ✗ {message}\n",
                      self.output.getvalue())

    def test_a_plant_that_records_a_refusal_passes(self):
        self.write("caught.py", plant_source("caught", body=(
            'nt.expect_failure("a check that fails", subprocess.CompletedProcess('
            '[], 1, "refused here", ""), "refused")')))
        self.write("judged.py", plant_source("judged", body='nt.refused("judged by hand")'))
        refusals = len(negative.refusals)
        self.assertEqual(negative.main(), 0)
        self.assertEqual(negative.failures, [])
        self.assertEqual(negative.refusals[refusals:], ["a check that fails: caught",
                                                        "judged by hand"])
        for line in ("✓ a check that fails: caught\n", "✓ judged by hand\n",
                     "✓ the unplanted tree passes check_fidelity.py\n"):
            self.assertIn(line, self.output.getvalue())
        self.assertTrue(self.output.getvalue().endswith(
            "2 of 2 plants run\n✓ every planted change was caught\n"))

    def test_failures_outside_a_plant_have_a_heading_of_their_own(self):
        self.write("passes.py", plant_source("passes", body=(
            'nt.expect_failure("a check that passes", subprocess.CompletedProcess('
            '[], 0, "", ""))')))
        self.fidelity = 1
        self.assertEqual(negative.main(), 1)
        self.assertEqual(negative.failures, ["a check that passes: not caught",
                                             "the unplanted tree failed check_fidelity.py"])
        self.assertTrue(self.output.getvalue().endswith(
            "2 negative-test failure(s):\n"
            "passes (scripts/negative/passes.py):\n  ✗ a check that passes: not caught\n"
            "outside any plant:\n  ✗ the unplanted tree failed check_fidelity.py\n"))

    def test_plant_option(self):
        for name in ("one", "two", "three"):
            self.write(f"{name}.py", plant_source(name))
        self.assertEqual(negative.main(["--plant", "two", "--plant", "one"]), 0)
        self.assertEqual(self.planted(), ["one", "two"])
        self.assertEqual(len(self.git_status()), 2)
        self.assertEqual(self.calls[-2], (sys.executable, "scripts/check_fidelity.py"))
        output = self.output.getvalue()
        self.assertLess(output.index("\none (scripts/negative/one.py)\n"),
                        output.index("\ntwo (scripts/negative/two.py)\n"))
        self.assertTrue(output.endswith("✓ every change planted by 2 of the 3 plants was "
                                        "caught; the others were not run (--plant)\n"))
        self.assertNotIn("every planted change was caught", output)
        with self.subTest(names="all three"):
            self.reset()
            for name in ("one", "two", "three"):
                self.write(f"{name}.py", plant_source(name))
            self.assertEqual(negative.main(["--plant", "one", "--plant", "two",
                                            "--plant", "three"]), 0)
            self.assertTrue(self.output.getvalue().endswith(
                "3 of 3 plants run\n✓ every planted change was caught\n"))
        for known, unknown in ((["one", "nine"], "'nine'"), (["ten", "nine"], "'ten', 'nine'")):
            with self.subTest(names=known):
                for path in self.root.glob("planted-*"):
                    path.unlink()
                self.calls.clear()
                errors = io.StringIO()
                with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
                    negative.main([arg for name in known for arg in ("--plant", name)])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn(f"no plant {unknown} in scripts/negative/; the plants are one, "
                              "three, two", errors.getvalue())
                self.assertEqual(self.planted(), [])
                # The entry status is taken before loading, and compared again on the exit.
                self.assertEqual(len(self.git_status()), 2)
                self.assertNotIn((sys.executable, "scripts/check_fidelity.py"), self.calls)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            negative.main(["--plant", "one", "--counts-only"])
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(self.planted(), [])

    def test_counts_only_runs_count_markers_alone_without_git(self):
        self.write("count_markers.py", plant_source("count_markers"))
        self.write("other.py", plant_source("other"))
        self.assertEqual(negative.main(["--counts-only"]), 0)
        self.assertEqual(self.planted(), ["count_markers"])
        self.assertEqual(self.git_status(), [])
        self.assertTrue(self.output.getvalue().endswith(
            "✓ count plants passed; other plants were not run (--counts-only)\n"))

    def test_the_real_plants_load(self):
        folder = REPO / "scripts" / "negative"
        plants, faults = negative.load_plants(folder)
        self.assertEqual(faults, [])
        names = [p.name for p in plants]
        self.assertEqual(len(names), len(set(names)))
        passed_over = {"__pycache__", ".DS_Store"}
        self.assertEqual(sorted(names), sorted(path.stem for path in folder.iterdir()
                                               if path.name not in passed_over))
        self.assertEqual(plants, sorted(plants, key=lambda p: (p.builds, p.name)))
        for p in plants:
            self.assertEqual(p.path, folder / f"{p.name}.py")
            self.assertTrue(p.description)


PROBE = '''"""A probe: is this plant's nt the module whose run_plant is running it?"""
import sys

import negative_tests as nt

BUILDS = False


def plant() -> None:
    frame = sys._getframe(1)
    while frame.f_code.co_name != "run_plant":
        frame = frame.f_back
    print(f"shared: {frame.f_globals is vars(nt)}; running: {nt is sys.modules['__main__']}")
    nt.refused("the probe: caught")
'''


class ScriptTests(unittest.TestCase):
    """The suite run as a script, as CI runs it, in a temporary copy of scripts/ whose
    regressions are empty stand-ins and whose one plant is a probe, named count_markers so
    that --counts-only runs it without Git or Lean."""

    def test_the_plants_share_the_running_module_and_no_bytecode_runs(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / "scripts/negative").mkdir(parents=True)
        for path in (REPO / "scripts").glob("*.py"):
            shutil.copyfile(path, root / "scripts" / path.name)
        (root / "tests").mkdir()
        for _, rel in negative.REGRESSIONS:
            (root / rel).write_text("")
        probe = root / "scripts/negative/count_markers.py"
        probe.write_text(PROBE)
        # Bytecode that Python's import would run in place of the runner's source, were the
        # file imported a second time, or of the plant's, were it imported at all.
        stand_in = 'print("{}: a stand-in from bytecode")\nraise SystemExit(0)\n'
        unchecked_bytecode(stand_in.format("runner"), importlib.util.cache_from_source(
            str(root / "scripts/negative_tests.py")))
        unchecked_bytecode(stand_in.format("plant"),
                           importlib.util.cache_from_source(str(probe)))
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        result = subprocess.run([sys.executable, "scripts/negative_tests.py", "--counts-only"],
                                cwd=root, env=env, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn("a stand-in from bytecode", output)
        self.assertIn("shared: True; running: True\n✓ the probe: caught\n", result.stdout)
        self.assertTrue(result.stdout.endswith(
            "✓ count plants passed; other plants were not run (--counts-only)\n"), output)


if __name__ == "__main__":
    unittest.main()
