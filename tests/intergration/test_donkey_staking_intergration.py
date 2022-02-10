from brownie import network
from scripts.helpers.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
from scripts.deploy import  deploy_donkey_staking_and_donkey_token 
import pytest

def test_stake_and_issue_correct_amounts(amount_staked):
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for intergration testing!")
    donkey_staking, donkey_token = deploy_donkey_staking_and_donkey_token()
    account = get_account()
    donkey_token.approve(donkey_staking.address, amount_staked, ({"from": account}))
    donkey_staking.stakeTokens(amount_staked, donkey_token.address, ({"from": account}))
    starting_balance = donkey_token.balanceOf(account.address)
    price_feed_contract = get_contract("dai_usd_price_feed")
    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    # stake 1 token should = $2,000
    # staker should be issued 2000 tokens
    amount_token_to_issue = (
        price / 10**price_feed_contract.decimals()
    ) * amount_staked
    # Act 
    issue_tx = donkey_staking.issueTokens({"from": account})
    issue_tx.wait(1)
    # assert
    assert (
        donkey_token.balanceOf(account.address) == amount_token_to_issue + starting_balance
    )