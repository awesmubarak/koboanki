# Contributing to Koboanki

This short guide explains the conventions this project follow so that everything
runs smoothly.

---

## 1. Local development

1. Install the **`uv`** package manager (https://github.com/astral-sh/uv).
2. Create or update the local virtual-environment:

   ```bash
   uv sync --dev
   ```

3. Run the checks that CI will execute:

   ```bash
   uv ruff check .            # style & linting
   uv mypy .                  # static types (strict)
   uv pytest -q               # unit tests
   ```

   CI uses the exact same commands, so you should see the same results
   locally.

## 2. Commit messages

We loosely follow the [Conventional Commits](https://www.conventionalcommits.org)
spec. A few examples:

* `feat: add export to HTML`
* `fix: handle empty annotation database`
* `docs: add example config for Kobo Libra`
* `refactor(gui): migrate to f-strings`
* `chore: update dev dependencies`

The prefix makes changelog generation and release notes much easier, but the
rule is *not* enforced by any hooks - don't worry if you forget.

## 3. Changelog

`CHANGELOG.md` is maintained manually by @awesmubarak. If your change is
user-visible, add a short bullet point in the PR description under
`## Changelog - Unreleased` and it will be copied across.
