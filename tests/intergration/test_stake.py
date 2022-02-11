import pytest
from brownie import Contract, ZERO_ADDRESS
from brownie.test import given, strategy
from hypothesis import settings


def test_stake_contract_ether(stake, ether, alice, registry):
    pool_id = 13
    pool = Contract(registry.pool_list(pool_id))
    _coins = registry.get_coins(pool)
    _underlying = registry.get_underlying_coins(pool)
    coin_list = _coins + _underlying
    
    stake.donk(ether, pool, {"from": alice, 'value': alice.balance()})
    assert stake.balance() == 0
    assert alice.balance() == 0

@pytest.mark.skip()
@given(pool_id=strategy("uint", min_value=0, max_value=41, exclude=[3, 4, 9, 16, 17, 21, 39]))
def test_stake_contract_dai(stake, dai, alice, registry, pool_id):
    pool = Contract(registry.pool_list(pool_id))
    _coins = registry.get_coins(pool)
    _underlying = registry.get_underlying_coins(pool)
    coin_list = _coins + _underlying
    
    if dai.address not in coin_list:
        return
    
    dai.transfer(stake, dai.balanceOf(alice), {"from": alice})
    stake.donk(dai, pool, {"from": alice})
    assert dai.balanceOf(stake) == 0
    
@settings(max_examples=100)
@given(pool_id=strategy("uint", min_value=0, max_value=66, exclude=[53]))
def test_stake_factory_dai(stake, dai, alice, registry, pool_id):
    factory = Contract(stake.factory())
    pool = Contract(factory.pool_list(pool_id))
    
    # Is the target coin in the pool
    if factory.is_meta(pool):
        coin_list = factory.get_underlying_coins(pool)
    else:
        coin_list = factory.get_coins(pool)
        
    # If DAI is nto in hte list return
    if dai.address not in coin_list:
        return
    
    # if factory pool is to low return 
    if pool.totalSupply() ==0:
        return
    
    if is_pool_low(factory, pool, dai.balanceOf(alice)):
        return
    
    dai.transer(stake, dai.balanceOf(alice), {"from": alice})
    stake.donk(dai, pool, {"from": alice})
    assert dai.balanceOf(stake) == 0

# Calculate if the pool value is to low
def is_pool_low(factory, pool, val):
    total_bal = 0
    
    # Grabbing number of coins
    coin_count = factory.get_n_coins(pool)
    if coin_count == 0:
        coin_count = retrieve_coin_count(pool)
        
    # Add the coin balanceOf
    for c in range(coin_count):
        _decimals = Contract(pool.coins(c)).decimals()
        total_bal += pool.balances(c) / 10 ** _decimals
    
    # Skip if test balance is to low
    if val > total_bal:
        return True
    else:
        return False
    
# Manually fectch coin count if fails directly
def retrieve_coin_count(pool):
    coin_count = 0
    for i in range(8):
        try:
            if pool.coins(i) != ZERO_ADDRESS:
                coin_count += 1
        except:
            pass
    return coin_count