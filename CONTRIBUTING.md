# Contributing

This project aims to make contributing as straightforward as possible. This
document outlines what you should expect, how to go about contributing, and 
a few tips.

## Quick Start

First, finish reading this document.

For relatively simple ways to contribute, take a look at issues labeled:

* [good first issue](https://github.com/d0c-s4vage/pfp/labels/good%20first%20issue)
* [needs-triage](https://github.com/d0c-s4vage/pfp/labels/needs-triage)
* [documentation](https://github.com/d0c-s4vage/pfp/labels/documentation)

For those who want or feel able to immediately start contributing code,
take a look at issues labeled:

* [concrete-issue](https://github.com/d0c-s4vage/pfp/labels/concrete-issue)

## Expectations

Contributors should feel free to ping the maintainers for feedback on proposed changes,
implementation ideas, code architecture, and all things related to changing the
code base. The maintainers pledge to be as available as possible to promote
discussion and help contributors determine how and where to implement the
changes they desire.

Contributors should also expect feedback on completed changes. Code quality,
documentation, and non-breaking changes are of high importance.

## Code Style

Althought PEP8/black formatting guides are not enforced (yet) on this project,
they are very highly recommended.

Above all, code must:

* Be Legible
* Be Easy to follow
* Have docstrings for all "public"/interface functions
* Use descriptive function and variable names
* Not use "trivia" programming

## Testing

Pfp currently uses the built-in `unittest` module for testing. The script
at `bin/run_tests` will run all tests for pfp.

Rules of thumb for testing:

* All code changes must result in passing tests on Travis-CI
* All new features must have new tests that test the new feature
* All fixed bugs should have accompanying test that ensure the bug is not
  reintroduced

## Versioning

This project uses [semantic versioning](https://semver.org/), aka SemVer. All
version numbers of pfp must be in the `X.Y.Z` format, where:

| Part | Name          | Description                                                         |
|------|---------------|---------------------------------------------------------------------|
| `X`  | Major Version | Incremented with changes that break backwards-compatability         |
| `Y`  | Minor version | Incremented with new features that maintain backwards compatability |
| `Z`  | Patch version | Incremented with bugfixes                                           |

Pfp's philosophy around version numbers is that they are not special and
can be incremented as often as work is done. I.e., there is no need to queue
up work for months to form a large "release". As long as tests are passing
and documentation is up-to-date with a change that was made, the version number
can be incremented.

### Mechanics of Releasing New Versions

New versions of pfp are released by:

* Merging all desired changes to the master branch
* Updating the CHANGELOG with release notes for the new version
* Tagging the current state of the master branch `git tag -a vX.Y.Z`. This will
  open your `$EDITOR` - paste in the contents of the `vX.Y.Z` CHANGELOG section
  as the tag's annotated text.
* Push master: `git push origin master`
* Push the tags: `git push origin --tags`
* Update the `vX.Y.Z` release text in GitHub under the
  [releases tab](https://github.com/d0c-s4vage/pfp/releases) with the
  `vX.Y.Z` section text from the CHANGELOG

Done! Travis-CI takes care of pushing the new package version to PyPi.

## Branching

Pfp uses a modified git-flow (modified for the addition of `bugfix`
branches). The main concepts of git-flow are:

* Two main branches exist: `master` and `develop`
* New features are branched off of develop and are named `feature/XX-short_description`,
  where `XX` is the issue number that is being coded towards
* Bug fixes that are found in production are hotfixes, are branched off of the
  master branch, and are named `hotfix/XX-short_description`.
* Bug fixes that are found in develop branch are bugfixes, are branched off of
  the develop branch, and are named `bugfix/XX-short_description`.

## Triaging Reported Bugs

Triaging reported bugs can be a major help in contributing to pfp. User-
reported bugs usually require valdation of:

* The bug itself
* Platform
* Python version
* pfp version

Often the user-created issue is not detailed enough to directly code towards,
and additional investigation must be done to determine the actual bug, with full
error stack trace and inputs that trigger the bug.

For example, suppose a user submits a bug titled *Pfp fails with this
010 template* and provides the template that pfp fails on. Below are the steps that
should usually be taken in triaging this bug:

* Validate that pfp fails utilizing the template 
* Determine if the error was due to pfp, or a user error. Usually it's
  pfp's fault if an exception is raised
* Determine the actual error(s). This is needed to create a new issue clear enough
  to code towards. E.g., "pfp has issues handling parameterized, typedef'd
  structs (a made up problem in pfp)
* Create new concrete issues with the `concrete-issue` label for all concrete
  problems found, referencing the original, user-created issue in the new
  issues' descriptions.
* Comment on the user-created issue, thanking the user for reporting the bug and
  detailing what needs to happen to fix the problem they experienced.

An example of this can be seen with [#78](https://github.com/d0c-s4vage/pfp/issues/78)

### Triaging Gotchas

Pfp is composed of two main projects:

* pfp (this project)
* py010parser - https://github.com/d0c-s4vage/py010parser

py010parser is responsible for parsing the 010 template source into an AST
(abstract syntax tree), which is then consumed and used by pfp.

Occassionally a ticket will have to be moved between projects, especially since
users of pfp generally aren't aware of the underline structure and simply
report issues directly to pfp (this project).

## Fixing bugs

Once all concrete bugs are completed associated with a user-reported issue,
close the user-reported issue, commenting on it to notify the user that their
issue has been resolved.

An example of this can be seen with [#78](https://github.com/d0c-s4vage/pfp/issues/78)
