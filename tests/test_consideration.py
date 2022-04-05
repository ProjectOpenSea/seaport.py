#!/usr/bin/python3

import pytest


def test_sanity(consideration, accounts):
    assert consideration.address is not None
    assert consideration.name() == "Consideration"
