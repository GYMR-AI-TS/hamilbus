# hamilbus
Applying graph theory to a public transport network.

## Data

This project uses public transit data following the [GTFS standard](https://gtfs.org/documentation/schedule/reference/), and specifically files :
- stops.txt : the list of stops
- routes.txt : the list of lines
- shapes.txt : the list of coordinates representing the "shapes" of lines
We use Nantes (France) as an example : data can be found [here](https://data.nantesmetropole.fr/explore/dataset/244400404_transports_commun_naolib_nantes_metropole_gtfs/information/)

## Development Setup

### Installing Development Dependencies

Install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

## How to run

```bash
cd hamilbus
python -m hamilbus.main
```

Then open http://127.0.0.1:3000

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
