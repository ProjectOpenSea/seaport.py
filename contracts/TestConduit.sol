// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import "seaport/contracts/conduit/Conduit.sol";

contract TestConduit is Conduit {
    constructor() Conduit() {}
}
