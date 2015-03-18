# Contributing to Combine

Want to hack on Combine? Awesome! Here are instructions to get you started. They are not perfect. Please let us know if anything feels wrong or incomplete.

## Reporting Security Issues

The Combine maintainers take security very seriously. If you discover a security issue, please bring it to their attention right away!

_TODO: this needs review and planning_

Please send your report privately to [security@something.com](mailto:security@something.com), please **DO NOT** file a public issue.

Security reports are greatly appreciated and we will publicly thank you for it. We currently do not offer a paid security bounty program, but are not ruling it out in the future.

## Design and Cleanup Proposals

When considering a design proposal, we are looking for:

* A description of the problem this design proposal solves
* A pull request, not an issue, that modifies the documentation describing the feature you are proposing, adding new documentation if necessary.
  * Please prefix your issue with `Proposal:` in the title
* Please review [the existing proposals](https://github.com/mlsecproject/combine/pulls?q=is%3Aopen+is%3Apr+label%3AProposal) before reporting a new one. You can always pair with someone if you both have the same idea.

When considering a cleanup task, we are looking for:

* A description of the refactors made
  * Please note any logic changes if necessary
* A pull request with the code
  * Please prefix the title of your PR with `Cleanup:` so we can quickly address it.
  * Your pull request must remain up to date with `dev`, so rebase as
    necessary.

## Reporting Issues

A great way to contribute to the project is to send a detailed report when you encounter an issue. We always appreciate a well-written, thorough bug report and will thank you for it!

When reporting [issues](https://github.com/mlsecproject/combine/issues) on GitHub, please include your host OS (Ubuntu 12.04, Fedora 19, etc) and version of Python (from `python -V`).

Please also include the steps required to reproduce the problem if possible and applicable.  This information will help us review and fix your issue faster.

### Template

```
Description of problem:


`Combine version`:


`Combine info`:


`python -V`:


How reproducible:


Steps to Reproduce:
1.
2.
3.


Actual Results:


Expected Results:


Additional info:



```

## Contribution guidelines

### Pull requests are always welcome

We are always thrilled to receive pull requests. We do our best to process them as quickly as possible. You're not sure if that typo is worth a pull request? Do it! We will appreciate it.

If your pull request is not accepted on the first try, don't be discouraged! If there's a problem with the implementation, we will provide feedback on what to improve.

We try very hard to keep Combine lean and focused. We don't want it to do everything for everybody. This means that we might decide against incorporating a new feature. However, we might help you find a way to implement that feature *on top of* Combine. For example, this might take the form of an add-on tool outside of the main repository that integrates with Combine.

### Create issues...

Any significant improvement should be documented as [a GitHub issue](https://github.com/mlsecproject/combine/issues) before anybody starts working on it.

### ...but check for existing issues first!

Please take a moment to check that an issue doesn't already exist documenting your bug report or improvement proposal. If it does, it never hurts to add a quick ":+1:" or "I have this problem too". This will help prioritize the most common problems and requests.

### Branches

We follow a simplified version of the popular [git flow](http://nvie.com/posts/a-successful-git-branching-model/).

* `master` MUST always be production-deployable. `dev` may not be ready for production but should pass all existing tests. (At the time of this writing, a test suite is under development.)
* The only branches that will be merged directly into master are `dev` (for a release) or hotfixes for significant bugs that need immediate attention. Hotfixes will merge into `master` and `dev`
* All other development forks off from the `dev` branch and merges back into it.

### Conventions

Fork the repository and make changes on your fork in a feature branch:

* Start from the `dev` branch.
* If it's a bug fix branch, name it iXXXX-something where XXXX is the number of the issue.
* If it's a feature branch, create an enhancement issue to announce your intentions and name it iXXXX-something where XXXX is the number of the issue.

Update the documentation when creating or modifying features. Review your documentation changes for clarity, concision, and correctness.

Write clean code. Universally formatted code promotes ease of writing, reading, and maintenance. Always run `pep8 file.py` on each changed file before committing your changes. Most editors have plug-ins that do this automatically. And yes, four spaces instead of tabs. We'll generally forgive long lines - but please be reasonable!

Pull requests descriptions should be as clear as possible and include a reference to all the issues that they address.

Commit messages should start with a short summary (max. 50 chars) written in the imperative, followed by an optional, more detailed explanatory text which is separated from the summary by an empty line.

Others will review your code review and may add comments to your pull request. Discuss, then make the suggested modifications and push additional commits to your feature branch. Be sure to post a comment after pushing. The new commits will show up in the pull request automatically, but the reviewers will not be notified unless you comment. If you collaborate with others and they want to add commits, they should issue a PR to your fork and you can merge it into your branch.

Pull requests must be cleanly rebased on top of the `dev` branch without multiple branches mixed into the PR.

**Git tip**: If your PR no longer merges cleanly, use `rebase dev` in your feature branch to update your pull request rather than `merge dev`.

Messages for commits that fix or close an issue should include a reference like `Closes #XXXX` or `Fixes #XXXX`, which will automatically close the issue when merged.

### Merge approval

Combine maintainers use :+1: or :shipit: in comments on the code review to indicate acceptance. Once it's approved, the maintainers will handle merging.

### Accept the CLA

_TODO: insert instructions about CLA from Alex_

## Community Guidelines

We want to keep the Combine community awesome, growing, and collaborative. We need your help to keep it that way. These general guidelines for the community will assist with this:

* Be nice: Be courteous, respectful and polite to fellow community members: no regional, racial, gender, orientation, or other abuse will be tolerated. We like nice people way better than mean ones!

* Encourage diversity and participation: Make everyone in our community feel welcome, regardless of their background, skill level, or the extent of their contributions. Do everything possible to encourage participation in our community.

* Keep it legal: Basically, don't get us in trouble. Share only content that you own, do not share private or sensitive information, and don't break the law.

* Stay on topic: Make sure that you are posting to the correct repository and avoid off-topic discussions. Remember that updating an issue or responding to an email could potentially send notifications to a large number of people. Please consider this before you update. Also remember that nobody likes spam.

## References:
We based these on the excellent [Docker contribution guidelines](https://github.com/docker/docker/blob/master/CONTRIBUTING.md).
