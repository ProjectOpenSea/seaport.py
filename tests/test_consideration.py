#!/usr/bin/python3

import pytest


def test_sanity(consideration, accounts):
    assert consideration.address is not None
    assert consideration.name() == "Consideration"


def test_erc20(erc_20, accounts):
    erc_20.mint(accounts[0], 1e19)
    print(erc_20.balanceOf(accounts[0]))
    assert erc_20.balanceOf(accounts[0]) == 0
