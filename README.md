# consideration.py

A library to help interfacing with the Consideration smart contract.

## Installation

1. Install [pyenv](https://github.com/pyenv/pyenv)

2. Install poetry

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

3. Set the poetry venv to be in the current project directory (useful for VSCode):

```
poetry config virtualenvs.in-project true
```

4. Run `poetry install`

5. (Optional) If running VSCode, set the interpreter to be `.venv/bin/python`

## Testing

### Prerequisites

1. Install yarn `npm i -g yarn`

Using a node package manager such as `nvm` is highly recommended!

2. Run `yarn`

### Running tests

To run the tests:

```
poetry run brownie test --network
```
