"""A frontend layer for producing zip files for the gradescope autograder.

The main work of this module is to generate the gradescope autograder zip file. The
specification for this file is here:
<https://gradescope-autograders.readthedocs.io/en/latest/specs/>. Specifically, we are
given two entrypoints:

 * setup.sh, a Bash script.
 * run_autograder, any executable file.

Both will be executed from a directory `/autograder` created by the autograder's Docker
harness.

We may also add arbitrary files to the zip. These will be available at
`/autograder/source`.

Docker will provide the student submission in the `/autograder/submission` directory.

Our current high-level approach is as follows:

 * Install python and aga in the `setup.sh` file.
 * Pickle the `Problem` at `/autograder/source/problem.pckl`.
 * Provide a `run_autograder` python file which unpickles the `Problem`, uses the
 `loader` module to load the student submission, and runs them against each other.

Some implementation details:

We use tempfile from the Python standard library to generate a temporary directory in
which we build the contents of the zip archive. The `run_autograder` and `setup.sh`
files in `resources/` are copied directly to this tempdir.

We use `dill` for pickling, instead of the standard library's `pickle`, because pickle
behaves weirdly with decorated functions, and `functools.update_wrapper` was
insufficient to fix this.
"""

from .into_zip import InvalidProblem, into_gradescope_zip

__all__ = ("into_gradescope_zip", "InvalidProblem")
