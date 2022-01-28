from brownie import network, exceptions
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS, 
    get_account, 
    get_contract, 
    INITIAL_PRICE_FEED_VALUE, 
    DECIMALS, 
    KEPT_BALANCE,
)
from scripts.deploy import deploy_donkey_staking_and_donkey_token
import pytest




def test_set_price_feed_contract():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    donkey_staking, donkey_token = deploy_donkey_staking_and_donkey_token()
    # Act
    price_feed_address = get_contract("eth_usd_price_feed")
    donkey_staking.setPriceFeedContract(donkey_token.address, price_feed_address, {"from": account})
    # Assert
    assert donkey_staking.tokenPriceFeedMapping(donkey_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        donkey_staking.setPriceFeedContract(donkey_token.address, price_feed_address, {"from": non_owner})


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    donkey_staking, donkey_token = deploy_donkey_staking_and_donkey_token()
    # Act
    donkey_token.approve(donkey_staking.address, amount_staked, {"from": account})
    donkey_staking.stakeTokens(amount_staked, donkey_token.address, {"from": account})
    # Assert
    assert (
        donkey_staking.stakingBalance(donkey_token.address, account.address) == amount_staked
    )
    assert donkey_staking.uniqueTokensStaked(account.address) == 1
    assert donkey_staking.stakers(0) == account.address
    return donkey_staking, donkey_token


def test_issue_tokens(amount_staked):    
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    donkey_staking, donkey_token = test_stake_tokens(amount_staked)
    starting_balance = donkey_token.balanceOf(account.address)
    # Act
    donkey_staking.issueTokens({"from": account})
    # Assert
    assert (
        donkey_token.balanceOf(account.address) == starting_balance + INITIAL_PRICE_FEED_VALUE
    )

def test_get_token_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    donkey_staking, donkey_token = deploy_donkey_staking_and_donkey_token()
    # Act and Assert
    assert donkey_staking.getTokenValue(donkey_token.address) == (
        INITIAL_PRICE_FEED_VALUE,
        DECIMALS
    )
    
    
def test_get_user_total_value(amount_staked, random_erc20):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    donkey_staking, donkey_token = test_stake_tokens(amount_staked)
    # Act
    donkey_staking.addAllowedTokens(random_erc20.address, {"from": account})
    donkey_staking.setPriceFeedContract(
        random_erc20.address, get_contract("eth_usd_price_feed"), {"from": account}
        )
    random_erc20_amount_staked = amount_staked * 2
    random_erc20.approve(
        donkey_staking.address, random_erc20_amount_staked, {"from": account}
        )
    donkey_staking.stakeTokens(
        random_erc20_amount_staked, random_erc20.address, {"from": account}
        )
    # Assert
    total_value = donkey_staking.getUserTotalValue(account.address)
    assert total_value == INITIAL_PRICE_FEED_VALUE * 3


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    donkey_staking, donkey_token = test_stake_tokens(amount_staked)
    # Act
    donkey_staking.unstakeTokens(donkey_token.address, {"from": account})
    # Assert
    assert donkey_token.balanceOf(account.address) == KEPT_BALANCE
    assert donkey_staking.stakingBalance(donkey_token.address, account.address) == 0
    assert donkey_staking.uniqueTokensStaked(account.address) == 0


def test_add_allowed_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    donkey_staking, donkey_token = deploy_donkey_staking_and_donkey_token()
    # Act
    donkey_staking.addAllowedTokens(donkey_token.address, {"from": account})
    # Assert
    assert donkey_staking.allowedTokens(0) == donkey_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        donkey_staking.addAllowedTokens(donkey_token.address, {"from": non_owner})