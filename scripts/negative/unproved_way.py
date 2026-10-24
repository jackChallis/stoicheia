"""Without a build, on III.5's review record: a further combination in its [overlap]'s
`ways` that `Audit/Overlaps.lean` does not prove III.5 from, the rules of
`Audit.III_5_crossing` without Definition I.15, each an axiom in facts.json, is
refused by `check_fidelity.py`, naming the record, the combination and the theorems
the file proves III.5 by; the record's other combinations are not named. The record is
restored after. The combination, UNPROVED_WAY, and with_way, which writes it into the
record, are in scripts/negative_tests.py, where tests/test_negative_tests.py reads them.
"""

import negative_tests as nt

BUILDS = False


def plant() -> None:
    """III.5's [overlap] given a further combination that Audit/Overlaps.lean does not
    prove it from (UNPROVED_WAY): check_fidelity refuses it, naming the record, the
    combination and what the file proves, while the record's other combinations pass and
    no rule is missing from facts.json."""
    record = nt.heath.review_path("III", 5)
    rel = record.relative_to(nt.ROOT).as_posix()
    saved = record.read_text()
    planted, k = nt.with_way(saved, nt.UNPROVED_WAY)
    record.write_text(planted)
    try:
        nt.expect_failure("a combination Audit/Overlaps.lean does not prove, in III.5's "
                          "[overlap]", nt.fidelity(),
                          f"{rel}: [overlap] `ways` {k} names [{', '.join(nt.UNPROVED_WAY)}] as "
                          "containing III.5", "(`Audit.III_5_crossing`)",
                          unwanted=("is not one of the axioms in facts.json",
                                    "[overlap] `rule` and `also` names"))
    finally:
        record.write_text(saved)
