#!/usr/bin/python3

from brownie.network.account import Accounts
import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def legacy_proxy_registry(WyvernProxyRegistry, accounts: Accounts):
    legacy_proxy_registry_contract = WyvernProxyRegistry.deploy({"from": accounts[0]})
    legacy_proxy_registry_contract.delegateProxyImplementation()

    return legacy_proxy_registry_contract


@pytest.fixture(scope="module")
def consideration(TestConsideration, legacy_proxy_registry, accounts: Accounts):
    legacy_proxy_implementation = legacy_proxy_registry.delegateProxyImplementation()

    return TestConsideration.deploy(
        legacy_proxy_registry.address,
        legacy_proxy_implementation,
        {"from": accounts[0]},
    )


@pytest.fixture(scope="module")
def erc_20(DummyERC20, accounts: Accounts):
    return DummyERC20.deploy({"from": accounts[0]})


def erc_721(DummyERC721, accounts: Accounts):
    return DummyERC721.deploy({"from": accounts[0]})


def erc_1155(DummyERC1155, accounts: Accounts):
    return DummyERC1155.deploy({"from": accounts[0]})
