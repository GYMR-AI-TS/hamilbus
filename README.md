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

## Usage

hamilbus is run from the command line with one of three subcommands depending on where you want to enter the pipeline.

### Configuration

hamilbus looks for a `config.toml` file in the current directory. Copy the example config and edit it to match your setup:

```bash
cp config.toml.example config.toml
```

Any setting in the config file can be overridden by passing the corresponding CLI flag. CLI flags always win over config file values.

---

### `hamilbus run` — Full pipeline

Runs everything from raw GTFS data to a solution. Exemples :

```bash
hamilbus run
hamilbus run --gtfs-folder ./data/naolib
hamilbus run --solver or_tools nearest_neighbor --save-solution
hamilbus run --solver or_tools --save-matrix --save-solution ./results/my_solution.json --serve
```

| Flag | Description |
|---|---|
| `--gtfs-folder` | Path to the folder containing GTFS files |
| `--graph` | Path to a pre-built graph file, skips graph construction |
| `--ignored-lines` | Line IDs to exclude, e.g. `--ignored-lines L80 L81` |
| `--distance-method` | Distance calculation method (default: `geodesic`) |
| `--solver` | One or more solvers to run, e.g. `--solver or_tools nearest_neighbor` |
| `--result-type` | `cycle` (default) or `path` |
| `--start` | Starting stop ID(s) for path solving, e.g. `--start 23` or `--start 21 42` or `--start all` |
| `--complete-graph` | Use complete graph, skip path reconstruction |
| `--save-matrix` | Save the distance matrix. Omit a path to use `output_dir` |
| `--save-solution` | Save the solution. Omit a path to use `output_dir` |
| `--serve` | Launch the visualisation server after solving |

---

### `hamilbus solve` — Solver only

Runs one or more solvers on a pre-computed distance matrix. No graph or matrix computation. 
Optionally launch the server to visualize the solutions. Exemples :

```bash
hamilbus solve --matrix ./results/matrix.npy
hamilbus solve --matrix ./results/matrix.npy --solver or_tools nearest_neighbor
hamilbus solve --matrix ./results/matrix.npy --result-type path --start all --save-solution
```

| Flag | Description |
|---|---|
| `--matrix` | Path to a saved distance matrix file |
| `--solver` | One or more solvers to run |
| `--result-type` | `cycle` (default) or `path` |
| `--start` | Starting stop ID(s) for path solving |
| `--complete-graph` | Use complete graph, skip path reconstruction |
| `--save-solution` | Save the solution. Omit a path to use `output_dir` |
| `--serve` | Launch the visualisation server after solving |

---

### `hamilbus serve` — Visualisation server

Launches the server to visualise the network and optionally overlay saved solutions. No computation apart from optionally creating the graph. Exemples :

```bash
hamilbus serve
hamilbus serve --graph ./results/graph.pkl
hamilbus serve --graph ./results/graph.pkl --solution ./results/solution.json
hamilbus serve --gtfs-folder ./data/naolib --solution ./results/sol1.json ./results/sol2.json
```

| Flag | Description |
|---|---|
| `--gtfs-folder` | Path to GTFS files, used to build the graph if no `--graph` is provided |
| `--graph` | Path to a pre-built graph file |
| `--solution` | One or more solution files to overlay on the network |

### Development Tools

This project uses the following tools for code quality and testing:

#### Formatting with Ruff

Format your code to ensure consistent style:

```bash
ruff format src/
ruff format tests/ --line-length 130

```

#### Linting with Ruff

Check for code issues and style violations:

```bash
ruff check .
```

Fix auto-fixable issues:

```bash
ruff check --fix .
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

To run all development checks (format, lint, test, and import smoke test), matching CI:

```bash
ruff format --check src/ && ruff format --check tests/ --line-length 130 && ruff check . && pytest && python -c "import hamilbus; print('Import successful')"
ruff format --check src/ ; ruff format --check tests/ --line-length 130 ; ruff check . ; pytest ; python -c "import hamilbus; print('Import successful')"
```
