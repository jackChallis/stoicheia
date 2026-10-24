- **The safe_push tests run on the cadence as eight shards side by side (#233).** Since
  the owner's cadence plan of 22 October, no pull request runs
  `scripts/test_safe_push.py`: the workflow `.github/workflows/safe-push-tests.yml` runs
  it on main every six hours and on demand, and until now did so in one job,
  `safe-push-tests`. In that job the suite took 72 to 78 minutes, and 137 on a slow
  runner; on as slow a runner it reached the job's limit, then 150 minutes, and was
  cancelled, and the limit went to 300 while the suite waited for its shards. This train
  shards it, and does no more, as
  the coordinator's rulings of 23 October 11:30 Pacific set it out, with
  the coordinator's request of 23 October 08:15 Pacific; the coordinator posted the scope
  ruling and the design on #233.

  The dealing. `python3 scripts/test_safe_push.py --shard K/N` lists the suite's tests with
  unittest's own loader, so that a new test is never missed, and weighs each by the
  seconds it took on a GitHub runner, kept in the new `scripts/test_safe_push_times.json`:
  288 tests, read from the timestamps of the log of #239's run on 21 October, with an
  estimate of the module's setup, the clone of the repository that every shard pays once.
  It deals them out longest first, each to the shard with the least time so far, then the
  fewest tests, then the lowest number, ties between tests going by name, so that every
  test lands in exactly one shard, the same one on every machine, and shard K runs exactly
  its own, in unittest's order. A test the file does not name weighs their median, 2.7
  seconds, and every shard's log names it: today 133 of the 421 tests the loader lists. The
  times stay as they were measured, and the file's note says only how. With `--ran FILE`
  a shard writes, after its run, each test it ran with its outcome; `--cover DIR` proves
  from such lists that each test the loader lists ran once, in one shard, and passed,
  failing, naming each, on a test no shard ran, a test run twice, a shard of the matrix
  that left no list (as one that stops before its end leaves none), a test the loader
  does not list, and a test that did not pass; and `--times-from-log LOG` writes the times
  file from a CI log in which each shard's step opens with this script's command, the
  setup measured up to a line `setUpModule` now prints when its clone is ready (the
  cadence's shard step opens with `set -o pipefail`, which that reader does not take for
  this script's step). Without `--shard` the whole suite runs, as before.

  The workflow. Its one job for the suite becomes two. `safe-push-shards` is a matrix of
  eight, `shard: [1, 2, 3, 4, 5, 6, 7, 8]`, the one place the workflow writes N, each
  shard given N as `strategy.job-total`; none stops the others when it fails, each may
  take 60 minutes,
  checks out the whole history, keeps no token, and installs Python 3.12 and the pinned
  YAML parser; each runs its part under `set -o pipefail`, its output kept by `tee` in a
  log of its own, and keeps its list and its log as artifacts for 35 days, a shard run
  again replacing both. Whether a later attempt of the run can fetch a list an earlier
  attempt kept is GitHub's to say, and nothing relies on it: by the coordinator's ruling
  of 24 October 04:40, a run re-run with "re-run all jobs" is judged afresh, and one
  re-run with "re-run failed jobs", whose proof may not see the other shards' earlier
  lists, then stays red, for the proof never passes on lists it cannot see.
  `safe-push-tests`, the name the release's gate and the report read, now needs the
  shards and runs whatever they did: it checks out the commit they ran, fetches every
  list, and runs the coverage proof whatever the shards' result. It is
  green only when GitHub's result for the matrix is success, which it is only when every
  shard succeeded, and the proof passed; a shard that failed, was cancelled, stopped at
  its limit or was skipped, or a list missing, makes it red, never skipped, and the run's
  conclusion red with it. Both judgements stay, and the job's comment says why: the proof
  fails on a shard of the matrix with no list and on any test that did not pass, while
  the matrix's result catches a shard cancelled in a rerun of all the jobs, should its
  list from the earlier attempt still be seen. The `report` job needs the same three jobs
  as before, keeps its title, its leave to write issues, which no other job has, and its
  running no code of the repository, still names the red jobs, and now reads the failing
  tests from every shard's log, fetched by pattern. `scripts/safe_push.py` is unchanged:
  its release gate already holds every job of the run but `report` to have passed, the
  shards among them, beside the three jobs it names.

  The card's second part, running only the test classes that a change touches, is left
  out: it would choose tests for a pull request, and no pull request has run the suite
  since the owner's cadence plan of 22 October.

  The tests. A new class, `Shards`, without git or network, checks that for the N of the
  cadence workflow's matrix the names that `--shard K/N --ran FILE` hands unittest, and
  the lists it writes, hold every test of the loader's list once, in its order, and pass
  the proof; that a test the times file does not name is dealt, run and listed; that the
  proof, given the lists with one fault planted, names it; that a list gives each test's
  outcome; that the times read from a few lines of a CI log are those its timestamps
  give; that the dealing is the same whatever order its inputs come in; that each form of
  the command line stands alone; and that the shard job and the verdict job are as above,
  their steps run as GitHub runs them under a model of its conditions, which reads `&&`,
  `||`, `!` and parentheses, and the verdict's script run under bash for every
  result of the matrix. A model of a whole run, `CadenceRun`, runs the workflow's own jobs
  and steps, with stand-ins for the shards' tests, the artifacts and `gh`, and the
  verdict's and the report's scripts under bash. On it stand three planted reds: a test
  failing in one shard makes the verdict and the run red, and the report opens the issue
  labelled `blocks-release`, or comments on the one open, naming that test; a shard's list
  lost once kept makes the proof fail, naming the shard, and the run red, though every
  shard succeeded; and a shard cancelled in a rerun, or the shards skipped, makes the
  verdict red, even where the model lets the first attempt's lists be seen and pass the
  proof. Each of the three
  was seen to fail with its guard taken out in a scratch copy: the report's condition on
  the verdict's result, the verdict job's `always()`, the proof's demand for a list from
  every shard, and the verdict's reading of the matrix's result. `CadenceReport` now deals
  its failures among the shards' logs, each in a folder of its own as the fetch lays them
  down, and `Units` holds the shard job to the workflow beside the jobs the release's gate
  names. No check or test is weakened.

  [WORKFLOW](../WORKFLOW.md), section 8, gives the account of the cadence workflow and
  its shards, and how to run one; section 10 counts the shards among the jobs a release's
  run must pass.

  This entry approves the change to `.github/workflows/safe-push-tests.yml`, where the
  suite's job becomes the matrix of eight shards and the verdict under the old name, and
  the report reads the shards' logs.

  This entry approves the change to `scripts/test_safe_push.py`: the dealing, the lists
  and the proof, the times reader, the class `Shards` with its model of a run and its
  three planted reds, and the report's tests on the shards' logs.

  This entry approves the new file `scripts/test_safe_push_times.json`, the measured
  seconds by which the shards are dealt.
