# hamilbus
Applying graph theory to a public transport network.

## Development Setup

### Installing Development Dependencies

Install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

### Development Tools

This project uses the following tools for code quality and testing:

#### Formatting with Black

Format your code to ensure consistent style:

```bash
black src/ tests/
```

#### Linting with Ruff

Check for code issues and style violations:

```bash
ruff check src/ tests/
```

Fix auto-fixable issues:

```bash
ruff check --fix src/ tests/
```

#### Testing with Pytest

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

#### Running All Checks

To run all development checks (format, lint, and test):

```bash
black src/ tests/ && ruff check --fix src/ tests/ && pytest
black src/ tests/ ; ruff check --fix src/ tests/ ; pytest
```
