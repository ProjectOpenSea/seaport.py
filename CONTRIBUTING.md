# Contributing

## Installation

1. Install [pyenv](https://github.com/pyenv/pyenv)

2. Setup Pyenv

```
pyenv install 3.9.12
pyenv virtualenv 3.9.12 seaport
pyenv activate seaport
```

3. Install Poetry

```
pip install poetry==1.1.13
```

4. Run `poetry install`

5. (Optional) If running VSCode, set the interpreter to be the `seaport` virtualenv.

## Testing

### Prerequisites

1. Install yarn `npm i -g yarn`

Using a node package manager such as `nvm` is highly recommended.

2. Run `yarn`

This is needed to run Hardhat as our RPC provider.

### Running tests

To run the tests:

```
poetry run brownie test --network hardhat
```

Running a single test:

```
poetry run brownie test --network hardhat -k test_basic_fulfill
```
