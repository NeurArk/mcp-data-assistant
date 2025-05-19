# AGENTS.md – Guidelines for the Codex Agent

> **Read this entire file before performing any action.** Failing to follow these rules may invalidate the task.

---

## 1. Mandatory initialization

1. **Run** `./setup.sh` as soon as the environment starts.
   * The script installs all dependencies **offline** from the `wheelhouse/` directory.
   * Stop the task if installation fails.
2. Do **not** add new online dependencies. The container operates without internet access.

---

## 2. Quality gates (run in this order)

```bash
pytest -q --cov=src --cov-fail-under=90   # tests and coverage ≥ 90%
black --check .                           # code formatting
isort --check-only .                      # import order
flake8 .                                  # lint
mypy src/ tests/                          # strict typing
bandit -r src -ll                         # security scan
```

All commands must return exit code 0. Fix any failing gate **before committing**.

---

## 3. Coding standards

| Topic   | Mandatory rules                                                                  |
| ------- | ------------------------------------------------------------------------------- |
| Format  | Use **Black** (max line length 120) and **isort**.                              |
| Typing  | Provide complete hints. `mypy --strict` must succeed without unjustified ignores. |
| Tests   | Every bug fix or feature requires unit tests.                                    |
| Logs    | Use the `logging` module, never `print`.                                         |
| Security| Avoid `eval`, plain secrets and unclean temp files.                              |

---

## 4. Commit convention

```
<type>(<scope>): <short summary>

<body if needed – 72 chars/line>

BREAKING CHANGE: <explanation>
```

*Allowed types*: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `chore`, `ci`.
*Scope* should point to a folder or module (e.g. `auth`, `api`, `db`).
Make commits atomic: one change, one green test.

---

## 5. Pull request rules

1. Create a branch named `feat/<issue-id>-slug` or `fix/<issue-id>-slug`.
2. Open a PR to `main` and fill the template:
   * **What**: short summary
   * **Why**: business need or bug
   * **How**: technical approach (diagram if useful)
   * **Test Plan**: commands and cases covered
3. Ensure `make check` passes **before** assigning a reviewer.
4. Update `CHANGELOG.md` when needed; add a new `## [Unreleased]` section.

---

## 6. Standard workflow

1. **Analyze** the issue or description.
2. **Plan** your work (files, steps) and post the plan in the PR comments.
3. **Implement** in small units (<30 lines per function).
4. Run all Quality gates locally (section 2).
5. Commit following the convention (section 4).
6. Push the branch, open the PR and confirm CI is green.

---

## 7. Quick troubleshooting

| Failure            | Immediate action                                                  |
| ------------------ | ---------------------------------------------------------------- |
| ImportError        | Add the missing wheel to `wheelhouse/`, rerun `setup.sh`.        |
| Coverage < 90%     | Add missing tests or justify the drop in the PR.                 |
| mypy errors        | Add hints or refactor the code.                                   |

---

**Remember:** *Clean, tested, documented code; no shortcuts.*

