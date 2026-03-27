# Code Style & Standards

## Formatting and Linting

- **Formatter**: Black + isort (line length: 200 chars)
- **Linter**: Pylint with custom rules in `pyproject.toml`
- **Type Checking**: mypy enabled with `check_untyped_defs=true`
- **Naming**: Follow PEP 8, public API = no leading underscore
- **Disabled Pylint Checks**: Missing docstrings, fixme, too-few-public-methods, too-many-ancestors, cyclic-import, etc. (see `pyproject.toml`)
- **Descriptive variable names over clever abbreviations**

## FastAPI Best Practices

- Use dependency injection for database sessions, authentication, and shared services
- Leverage Pydantic models for request/response validation
- Implement proper exception handling with custom exception types
- Include comprehensive OpenAPI documentation


