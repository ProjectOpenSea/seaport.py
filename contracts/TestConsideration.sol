// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import "consideration/contracts/Consideration.sol";

contract TestConsideration is Consideration {
    constructor(
        address legacyProxyRegistry,
        address legacyTokenTransferProxy,
        address requiredProxyImplementation
    ) Consideration(legacyProxyRegistry, legacyTokenTransferProxy, requiredProxyImplementation) {}
}
