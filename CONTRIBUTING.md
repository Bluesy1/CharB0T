<!--
SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>

SPDX-License-Identifier: MIT
-->
# Welcome to Charbot's contributing guide <!-- omit in toc -->

Thank you for investing your time in contributing to our project! Any contribution you make will be reflected in the bot in due time :sparkles:. 

Read our [Code of Conduct](./CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

In this guide you will get an overview of the contribution workflow from opening an issue, creating a PR, reviewing, and merging the PR.

Use the table of contents icon on the top left corner of this document to get to a specific section of this guide quickly.

## New contributor guide

To get an overview of the project, read the [README](README.md). Here are some resources to help you get started with open source contributions:

- [Finding ways to contribute to open source on GitHub](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github)
- [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git)
- [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Collaborating with pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests)


## Getting started

### Issues

We welcome issues that report bugs, request new features, or mention issues and concerns. 
**If you find security issues, contact me privately via discord, not publicly.**

### Submitting Code

We welcome people submitting their own code, as long as the code is a welcome change, either via an 
[issue](https://github.com/Bluesy1/CharB0T/issues) on Github, or by communicating on discord with us!

Once you know the code is a welcome change, clone the repository and make the changes.
After you make sure the changes, please make sure that the code passes static type analysis via pyright[^1], and that the code style passes black[^1].
The configuration for both of these can be found in the [pyproject.toml](./pyproject.toml) file if you need to do manual configuration.

We also use other code analysis tools like flake8[^1] for python source analysis. We use pytest for python and a combination of the built in tests and `yare` for parametrized tests in rust.
We target 80% project and diff coverage in this project. If you add new code, please add approprate unittests for the code as needed.

Finally, if you are adding new files, make sure they contain copyright and lisence information, as well as explicit encoding for utf-8 files

[^1]: #type: ignore, #pyright: ignore, and other ignore comments for various parts of the CI are allowed with valid explanation. 

