# AGENTS.md - Guidelines for Codex Agent

**Read this entire file before acting. Failing to follow these rules invalidates the task.**

## 1. Mandatory setup

1. Execute `./setup.sh` when the container starts.
   - The script installs dependencies from `wheelhouse/` entirely offline.
   - Stop the task if installation fails.
2. Do not add new online dependencies. The container has no internet access.

## 2. Quality gates (run in this order)

```bash
pytest -q --cov=src --cov-fail-under=90
black --check .
isort --check-only .
flake8 .
mypy src/ tests/
bandit -r src -ll
```

All commands must exit with code 0. Fix issues before committing.

## 3. Coding standards

| Topic | Mandatory rules |
| ----- | ----------------|
| Format | Use **Black** (120 char line length) and **isort** for imports. |
| Typing | Provide complete type hints. `mypy --strict` should pass without unnecessary ignores. |
| Tests | Every bug fix or feature requires unit tests. |
| Logs | Use the `logging` module, never `print`. |
| Security | Avoid `eval`, plaintext secrets and uncleaned temp files. |

## 4. Conventional commits

```
<type>(<scope>): <short summary>

<body if needed, wrapped at 72 characters>

BREAKING CHANGE: <explanation>
```

Allowed types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `chore`, `ci`.
Scope is the folder or module (e.g. `auth`, `api`, `db`). Keep commits atomic.

## 5. Pull request process

1. Create a branch named `feat/<issue-id>-slug` or `fix/<issue-id>-slug`.
2. Open a PR to `main` with the template:
   - **What**: concise summary.
   - **Why**: business need or bug description.
   - **How**: technical approach (include diagrams if useful).
   - **Test Plan**: commands and cases covered.
3. Ensure `make check` passes before requesting review.
4. Update `CHANGELOG.md` if needed under `## [Unreleased]`.

## 6. Standard workflow for every task

1. Analyse the issue or description.
2. Plan changes and outline them in a PR comment.
3. Implement small units (<30 lines per function).
4. Run all quality gates locally.
5. Commit following conventional commits.
6. Push the branch, open the PR, verify CI is green.

## 7. Quick troubleshooting

| Failure | Action |
| ------- | ------ |
| `ImportError` | Add the missing wheel to `wheelhouse/`, rerun `setup.sh`. |
| Coverage <90% | Add missing tests or justify drop in the PR. |
| `mypy` error | Add type hints or refactor code. |

**Remember:** *Clean, tested, documented code; no shortcuts.*
