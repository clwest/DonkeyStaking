import pytest
from brownie import Contract, ZERO_ADDRESS
from brownie.test import given, strategy
from hypothesis import settings


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