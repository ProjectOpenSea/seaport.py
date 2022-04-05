// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import "consideration/contracts/Consideration.sol";

contract TestConsideration is Consideration {
    constructor(
        address legacyProxyRegistry,
        address requiredProxyImplementation
    ) Consideration(legacyProxyRegistry, requiredProxyImplementation) {}
}
