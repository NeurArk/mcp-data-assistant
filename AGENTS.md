# AGENTS.md – Guidelines for the MCP Data Assistant Project

> **Read this entire file before performing any action.** This guide helps you navigate the codebase, run tests, and adhere to project standards.

---

## 1. Codebase Navigation

This project implements Model Context Protocol (MCP) tools for data analysis. Key areas:

| Directory  | Purpose                                    | Key Files                                   |
| ---------- | ------------------------------------------ | ------------------------------------------- |
| `agent/`   | LLM assistant logic and session management | `assistant.py`, `session_manager.py`        |
| `tools/`   | Core MCP tools (SQL, CSV, PDF)             | `sql_tool.py`, `csv_tool.py`, `pdf_tool.py` |
| `tests/`   | Unit and integration tests                 | Test files mirror source structure          |
| `static/`  | Static assets including MCP schema         | `schema.json` (MCP tool definitions)        |
| `data/`    | Sample datasets for testing                | `sales.db`, `people.csv`                    |
| `reports/` | Generated PDF reports output directory     | Empty initially, populated during runtime   |

Key entry points:

- `app.py`: Main Gradio application
- `scripts/demo_cli.py`: Command-line interface

---

## 2. Development Environment Setup

### Environment Variables

```bash
export PYTHONPATH="."
export PROJECT_ROOT=$(pwd)
```

### Dependencies

All required packages are in `requirements.txt`. The `wheelhouse/` directory contains pre-downloaded packages for offline installation:

```bash
pip install -r requirements.txt --find-links wheelhouse/
```

### Optional Secrets

- `OPENAI_API_KEY`: Required only if using OpenAI models (not needed for Ollama)

---

## 3. Testing and Quality Assurance

Run these commands for testing and code quality:

```bash
# Run tests
pytest -v

# Code formatting and linting
ruff check .

# Code formatting check
ruff format --check .

# Type checking (Python 3.12)
mypy tools/ agent/ tests/ --python-version 3.12

# Security scan (exclude tests)
bandit -r tools/ agent/ -ll -x /tests/
```

### Testing Best Practices

- Write tests first (TDD approach encouraged)
- Use pytest fixtures for common setup
- Mock external services (OpenAI, Ollama)
- Test both success and failure paths
- Use parameterized tests for multiple scenarios
- Ensure tests are deterministic

---

## 4. Standard Development Workflow

1. **Analyze** the issue or requirement
2. **Plan** your approach (files to modify, tests to write)
3. **Check** existing code patterns and tests
4. **Implement** in small, testable units
5. **Run** all tests and quality checks
6. **Commit** following the convention below
7. **Push** and ensure CI passes

---

## 5. Commit Convention

```
<type>(<scope>): <short summary>

<body if needed – 72 chars/line>

BREAKING CHANGE: <explanation>
```

Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `chore`, `ci`
Scope: module name (e.g., `agent`, `tools`, `sql`, `csv`, `pdf`)

Example:

```
feat(sql): add support for PostgreSQL connections

- Implement PostgreSQL connection handler
- Add tests for connection types
- Update schema.json with new parameters
```

---

## 6. Tool Development Guidelines

When developing MCP tools:

- [ ] Tool inherits from appropriate base class
- [ ] Implements required MCP protocol methods
- [ ] Returns properly formatted JSON responses
- [ ] Handles edge cases gracefully
- [ ] Includes comprehensive tests
- [ ] Updates `static/schema.json` if adding new tool
- [ ] Adds tool documentation to README.md

MCP tools must be:

- Stateless and idempotent
- Properly error-handled with meaningful error responses
- Well-documented with examples

---

## 7. Assistant Module Guidelines

When working on the Assistant module:

- [ ] Maintain conversation history properly
- [ ] Handle model switching (OpenAI/Ollama) gracefully
- [ ] Implement proper error recovery
- [ ] Test with both model backends
- [ ] Ensure session cleanup
- [ ] Handle API key absence for Ollama mode

---

## 8. Quick Troubleshooting

| Issue                       | Solution                                         |
| --------------------------- | ------------------------------------------------ |
| ImportError                 | Check requirements.txt and wheelhouse/ directory |
| mypy errors                 | Add type hints or refactor the code              |
| Tool execution fails        | Check schema.json alignment with implementation  |
| Assistant connection errors | Verify OPENAI_API_KEY or Ollama service status   |
| CI pipeline fails           | Check GitHub Actions logs and fix locally first  |

---

## 9. Important Technical Details

### Database Support

- SQLite (default) and PostgreSQL support
- Connection strings handled via SQL tool

### UI Framework

- Gradio 5.29+ for web interface
- Session-based state management

### PDF Generation

- ReportLab for PDF creation
- Matplotlib for charts/visualizations

### Model Support

- OpenAI API integration
- Ollama for local models
- Dynamic model switching

---

## 10. CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- All PRs must pass automated checks
- Quality gates run automatically
- Branch protection requires PR reviews
- Commits must follow conventional format

---

**Remember:** Write clean, tested, documented code. MCP tools must be reliable and stateless. Prioritize code readability and maintainability.