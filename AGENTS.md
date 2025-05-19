# AGENTS.md – Guidelines for the MCP Data Assistant Agent

> **Read this entire file before performing any action.** Failing to follow these rules may invalidate the task.

---

## 1. Environment initialization

Dependencies are automatically installed via the agent interface during the configuration phase.
The wheelhouse directory contains all required packages for offline installation.

* Required environment variables:
  - `PYTHONPATH`: Set to `.`
  - `PROJECT_ROOT`: Set to `/workspace/mcp-data-assistant`
  
* Optional secrets:
  - `OPENAI_API_KEY`: Required only if using OpenAI models (not needed for Ollama)

---

## 2. Quality gates (run in this order)

```bash
pytest -q --cov=tools --cov=agent --cov-report=term-missing --cov-fail-under=85  # tests and coverage ≥ 85%
ruff check .                                                                      # code formatting and linting
ruff format --check .                                                             # code formatting check
mypy tools/ agent/ tests/ --python-version 3.12                                   # strict typing
bandit -r tools/ agent/ -ll -x /tests/                                            # security scan
```

All commands must return exit code 0. Fix any failing gate **before committing**.

---

## 3. GitHub workflow compatibility

This project follows GitHub Actions CI/CD standards:

* All PRs must pass automated checks
* CI pipeline runs the quality gates listed above
* Commits must follow conventional commit format
* Branch protection requires PR reviews before merging to `main`

---

## 4. Project structure

| Directory  | Purpose                                               |
| ---------- | ----------------------------------------------------- |
| `agent/`   | LLM assistant logic and session management            |
| `tools/`   | Core MCP tools (SQL, CSV, PDF)                        |
| `tests/`   | Unit and integration tests                            |
| `static/`  | Static assets including MCP schema                    |
| `data/`    | Sample datasets for testing                           |
| `reports/` | Generated PDF reports                                 |

---

## 5. Coding standards

| Topic      | Mandatory rules                                                                      |
| ---------- | ------------------------------------------------------------------------------------- |
| Format     | Use **ruff format** (line length 120) and **ruff check**.                            |
| Typing     | Provide complete hints. `mypy --strict` must succeed without unjustified ignores.     |
| Tests      | Every bug fix or feature requires unit tests. Minimum 85% coverage required.         |
| Logs       | Use the `logging` module, never `print`.                                             |
| Security   | Avoid `eval`, plain secrets and unclean temp files. Follow OWASP guidelines.         |
| Imports    | Use absolute imports for project modules.                                            |
| Docstrings | Google style docstrings for all public functions/classes.                            |

---

## 6. MCP-specific guidelines

* Maintain MCP schema in `static/schema.json` for all tool changes
* Follow Model Context Protocol standards for tool implementation
* Ensure tools are stateless and idempotent
* Implement proper error handling with meaningful MCP error responses

---

## 7. Commit convention

```
<type>(<scope>): <short summary>

<body if needed – 72 chars/line>

BREAKING CHANGE: <explanation>
```

*Allowed types*: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `chore`, `ci`.
*Scope* should point to a module (e.g. `agent`, `tools`, `sql`, `csv`, `pdf`).
Make commits atomic: one change, one green test.

---

## 8. Pull request rules

1. Create a branch named `feat/<issue-id>-slug` or `fix/<issue-id>-slug`.
2. Open a PR to `main` and include:
   * **What**: short summary
   * **Why**: business need or bug
   * **How**: technical approach (include diagrams if useful)
   * **Test Plan**: commands and test cases covered
   * **MCP Impact**: schema changes or tool behavior changes
3. Ensure all quality gates pass **before** requesting review.
4. Update `CHANGELOG.md` when needed; add a new `## [Unreleased]` section.
5. Link the PR to the related issue.

---

## 9. Standard workflow

1. **Analyze** the issue or description.
2. **Plan** your work (files, steps) and post the plan as a comment in the issue.
3. **Check** existing tests for context and patterns.
4. **Implement** in small units (functions < 30 lines).
5. Run all quality gates locally (section 2).
6. Commit following the convention (section 7).
7. Push the branch, open the PR and ensure CI is green.
8. Request review once all checks pass.

---

## 10. Tool development checklist

When developing MCP tools:

- [ ] Tool inherits from appropriate base class
- [ ] Implements required MCP protocol methods
- [ ] Returns properly formatted JSON responses
- [ ] Handles edge cases gracefully
- [ ] Includes comprehensive test coverage
- [ ] Updates schema.json if adding new tool
- [ ] Add tool documentation to README.md

---

## 11. Assistant development

When working on the Assistant module:

- [ ] Maintain conversation history properly
- [ ] Handle model switching (OpenAI/Ollama) gracefully
- [ ] Implement proper error recovery
- [ ] Test with both model backends
- [ ] Ensure session cleanup
- [ ] Handle API key absence for Ollama mode

---

## 12. Quick troubleshooting

| Failure                      | Immediate action                                           |
| --------------------------- | ---------------------------------------------------------- |
| ImportError                 | Check if package is in requirements.txt and wheelhouse/    |
| Coverage < 85%              | Add missing tests or justify the drop in the PR.           |
| mypy errors                 | Add type hints or refactor the code.                       |
| Tool execution fails        | Check schema.json alignment with implementation.           |
| Assistant connection errors | Verify OPENAI_API_KEY or Ollama service status.            |
| CI pipeline fails           | Check GitHub Actions logs and fix locally first.           |

---

## 13. Testing guidelines

* Write tests first (TDD approach encouraged)
* Use pytest fixtures for common setup
* Mock external services (OpenAI, Ollama)
* Test both success and failure paths
* Use parameterized tests for multiple scenarios
* Ensure tests are deterministic

---

## 14. Environment considerations

* The project supports Python 3.12+
* SQLite and PostgreSQL database support
* Gradio 5.29+ for UI
* ReportLab for PDF generation
* Ollama integration for local models
* All dependencies pre-downloaded in wheelhouse/

---

**Remember:** *Clean, tested, documented code; no shortcuts. MCP tools must be reliable and stateless. Always ensure GitHub workflow compliance.*