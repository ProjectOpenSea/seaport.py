#!/usr/bin/python3

from time import sleep

import pytest
from brownie.network.account import Accounts, _PrivateKeyAccount
from web3 import Web3

from seaport.seaport import Seaport
from seaport.types import ContractOverrides, SeaportConfig


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def seaport_contract(
    TestSeaport,
    TestConduitController,
    accounts: Accounts,
):
    conduit_controller = TestConduitController.deploy({"from": accounts[0]})

    consideration = TestSeaport.deploy(
        conduit_controller.address,
        {"from": accounts[0]},
    )

    return consideration


@pytest.fixture(scope="module")
def seaport(
    seaport_contract,
):
    return Seaport(
        provider=Web3.HTTPProvider("http://127.0.0.1:8545"),
        config=SeaportConfig(
            overrides=ContractOverrides(
                contract_address=seaport_contract.address,
            )
        ),
    )


@pytest.fixture(scope="module")
def erc20(TestERC20, accounts: Accounts):
    return TestERC20.deploy({"from": accounts[0]})


@pytest.fixture(scope="module")
def erc721(TestERC721, accounts: Accounts):
    return TestERC721.deploy({"from": accounts[0]})


@pytest.fixture(scope="module")
def erc1155(TestERC1155, accounts: Accounts):
    return TestERC1155.deploy({"from": accounts[0]})


@pytest.fixture(scope="module")
def second_erc721(TestERC721, accounts: Accounts):
    return TestERC721.deploy({"from": accounts[0]})


@pytest.fixture(scope="module")
def second_erc1155(TestERC1155, accounts: Accounts):
    return TestERC1155.deploy({"from": accounts[0]})


@pytest.fixture(scope="module")
def offerer(accounts: Accounts) -> _PrivateKeyAccount:
    return accounts[0]


@pytest.fixture(scope="module")
def zone(accounts: Accounts) -> _PrivateKeyAccount:
    return accounts[1]


@pytest.fixture(scope="module")
def fulfiller(accounts: Accounts) -> _PrivateKeyAccount:
    return accounts[2]


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    # Prevents Web3 connection error when tx hasn't finished when tests are done executing
    # https://github.com/smartcontractkit/full-blockchain-solidity-course-py/issues/173#issuecomment-974789232
    sleep(1)
