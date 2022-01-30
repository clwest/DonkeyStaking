// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DonkeyToken is ERC20 {
    constructor() public ERC20("Donkey Token", "DONK") {
        _mint(msg.sender, 1e21);
    }
}
