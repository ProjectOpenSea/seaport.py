#!/usr/bin/python3

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def legacy_proxy_registry(WyvernProxyRegistry, accounts):
    legacy_proxy_registry_contract = WyvernProxyRegistry.deploy({"from": accounts[0]})
    legacy_proxy_registry_contract.delegateProxyImplementation()

    return legacy_proxy_registry_contract


@pytest.fixture(scope="module")
def consideration(TestConsideration, legacy_proxy_registry, accounts):
    legacy_proxy_implementation = legacy_proxy_registry.delegateProxyImplementation()

    return TestConsideration.deploy(
        legacy_proxy_registry.address,
        legacy_proxy_implementation,
        {"from": accounts[0]},
    )
