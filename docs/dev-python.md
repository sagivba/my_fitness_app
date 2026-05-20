# Python development guide

## Assumptions

This repository is optimized for development with:

- WSL
- VS Code
- Python 3.12+
- unittest
- optional Docker Compose

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment variables

Copy the example file:

```bash
cp .env.example .env
```

The important value is:

```text
PYTHONPATH=src
```

## Run tests

```bash
scripts/test.sh quick
```

Full output:

```bash
scripts/test.sh full
```

Direct unittest command:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Run app locally

```bash
PYTHONPATH=src flask --app my_fitness_app.app:create_app run --debug
```

## VS Code

Open the repository from WSL, not from a Windows path.

Recommended:

```bash
code .
```
