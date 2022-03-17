from brownie import DonkeyToken, DonkeyStaking, Stake, network, config
from scripts.helpers.helpful_scripts import get_account, get_contract, KEPT_BALANCE
from web3 import Web3

# from brownie import *
# from brownie_tokens import *

# def main():
#     t = MintableForkToken('dai')
#     pool = Contract("3pool")
#     t._mint_for_testing(accounts[0], 10000 * 10 ** t.decimals())
    
#     s = Stake.deploy(Contract('address_provider'), {'from': accounts[0]})
#     t.transfer(s, t.balanceOf(accounts[0]), {'from': accounts[0]})
    
#     print(s.show_balance(t).return_value)





def deploy_donkey_staking_and_donkey_token():
    account = get_account()
    donkey_token = DonkeyToken.deploy({"from": account})
    donkey_staking = DonkeyStaking.deploy(
        donkey_token.address, 
        {"from": account}, 
        publish_source = config["networks"][network.show_active()].get("verify", False),
        )
    tx = donkey_token.transfer(donkey_staking.address, donkey_token.totalSupply() - KEPT_BALANCE, {"from": account})
    tx.wait(1)
    # donkey_token, weth_token, fau_token=dai
    weth_token = get_contract("weth_token") 
    fau_token = get_contract("fau_token")
    dict_of_all_tokens = {
        donkey_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }

    add_allowed_tokens(donkey_staking, dict_of_all_tokens, account)
    return donkey_staking, donkey_token

def add_allowed_tokens(donkey_staking, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = donkey_staking.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = donkey_staking.setPriceFeedContract(token.address, dict_of_allowed_tokens[token], {"from": account})
        set_tx.wait(1)
    return donkey_staking


def main():
    deploy_donkey_staking_and_donkey_token()