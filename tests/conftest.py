import pytest
from web3 import Web3
from scripts.helpful_scripts import get_account
from brownie_tokens import MintableForkToken
from brownie import MockERC20, Contract, network
from test_helpers.utils import *


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass

@pytest.fixture
def amount_staked():
    return Web3.toWei(1, "ether")

@pytest.fixture
def random_erc20():
    account = get_account()
    erc20 = MockERC20.deploy({"from": account})
    return erc20

# Deploy and Mint DonkeyToken
@pytest.fixture(scope="module")
def donkeyToken(Token, accounts):
    return DonkeyToken.deploy("Donkey Token", "DONK", 18, 1e21,  accounts[0])

 # Referance Account A
@pytest.fixture(scope="module")
def alice():
    account = get_account()
    return accounts[0]
    # Referance Account B
@pytest.fixture(scope="module")
def bob(accounts):
    return accounts[1]

# Pulls contracts if they exist otherwise makes API call to etherscan
def load_contract(addr):
    try:
        cont = Contract(addr)
    except ValueError:
        cont = Contract.from_explorer(addr)
    return cont


# Gets the curve registry contract
@pytest.fixture(scope="module")
def registry():
    return load_contract("0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5")

# calls the tripool from registry
@pytest.fixture(scope="module")
def tripool(registry):
    return load_contract(registry.pool_list(0))


@pytest.fixture(scope="module")
def tripool_lp_token(registry, tripool):
    return load_contract(registry.get_lp_token(tripool))


# Mints tokens and deposits them into the first contract of the pool
@pytest.fixture(scope="module")
def tripool_funded(registry, alice, tripool):
    dai_addr = registry.get_coins(tripool)[0]
    dai = MintableForkToken(dai_addr)
    amount = 1e21
    dai.approve(tripool, amount, {"from": alice})
    dai._mint_for_testing(alice, amount)

    amounts = [amount, 0, 0]
    tripool.add_liquidity(amounts, 0, {"from": alice})
    return tripool

@pytest.fixture(scope="module")
def tripool_rewards(alice, tripool_funded):
    return stake_into_rewards(tripool_funded, alice)