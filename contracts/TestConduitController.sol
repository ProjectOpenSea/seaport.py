// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import "seaport/contracts/conduit/ConduitController.sol";

contract TestConduitController is ConduitController {
    constructor() ConduitController() {}
}
