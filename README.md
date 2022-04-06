# consideration.py

A library to help interfacing with the Consideration smart contract.

## Installation

1. Install [pyenv](https://github.com/pyenv/pyenv)

2. Install poetry

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

3. Run `poetry install`

4. Activate your virtual environment

```
source $(poetry env info --path)/bin/activate
```

## Testing

### Prerequisites

Install ganache-cli `npm i -g ganache-cli`

Using a node package manager such as `nvm` is highly recommended!

### Running tests

To run the tests:

```bash
poetry run brownie test
```
