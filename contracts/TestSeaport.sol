// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import "seaport/contracts/Seaport.sol";

contract TestSeaport is Seaport {
    constructor(address conduitController) Seaport(conduitController) {}
}
