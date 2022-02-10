# @version 0.3.1

from vyper.interfaces import ERC20

interface Curve2Pool:
    def add_liquidity(amounts: uint256[2], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[2]): nonpayable

interface Curve3Pool:
    def add_liquidity(amounts: uint256[3], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[3]): nonpayable

interface Curve4Pool:
    def add_liquidity(amounts: uint256[4], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[4]): nonpayable

interface Curve2PoolUnderlying:
    def add_liquidity(amountsUnderlying: uint256[2], min_mint_amount: uint256, use_underlying: bool): nonpayable
    def remove_liquidity(_amountsUnderlying: uint256, min_amounts: uint256[2]): nonpayable

interface Curve3PoolUnderlying:
    def add_liquidity(amountsUnderlying: uint256[3], min_mint_amount: uint256, use_underlying: bool): nonpayable
    def remove_liquidity(_amountsUnderlying: uint256, min_amounts: uint256[3]): nonpayable

interface Curve4PoolUnderlying:
    def add_liquidity(amountsUnderlying: uint256[4], min_mint_amount: uint256, use_underlying: bool): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[4]): nonpayable

interface Gauge:
    def deposit(_value: uint256): nonpayable
    def withdraw(amount: uint256): nonpayable
    def balanceOf(arg0: address) -> uint256: view

interface Registry:
    def get_n_coins(_pool: address) -> uint256[2]: view
    def get_coins(_pool: address) -> address[8]: view
    def get_underlying_coins(_pool: address) -> address[8]: view
    def get_gauges(_pool: address) -> (address[10], int128[10]): view
    def is_meta(_pool: address) -> bool: view
    def get_pool_from_lp_token(arg0: address) -> address: view
    def get_lp_token(arg0: address) -> address: view

interface AddressProvider:
    def get_registry() -> address: nonpayable


address_provider: public(AddressProvider)
registry: public(Registry)
owner: public(address)

# Internal Functions 

@internal 
def _load_coins(pool_addr: address, use_underlying: bool) -> address[8]:
    if use_underlying == True:
        return self.registry.get_underlying_coins(pool_addr)
    else:
        return self.registry.get_coins(pool_addr)

@internal
def _get_coin_index(coin_addr: address, pool_addr: address, use_underlying: bool) -> int256[2]:
    """
    @notice Determine the index of a coin in a pool
    @param coin_addr Address of the ERC20 token
    @param pool_addr Address of the Curve pool
    """

    coins: address[8] = self._load_coins(pool_addr, use_underlying)
    ret_index: int256 = -1
    ret_number: int256 = -1

    for i in range(8):
        if coin_addr == coins[i]:
            ret_index = i
        if ret_number == -1 and coins[i] == ZERO_ADDRESS:
            ret_number = i
    return [ret_index, ret_number]

@internal
def _add_liquidity(
        coin_addr: address, 
        pool_addr: address, 
        use_underlying: bool):
    """
    @ notice Approve and Deposit ERC20 into a Curve pool
    @parma coin_addr Address of ERC20 Token
    @param pool_addr Address of Curve Pool
    """

    coin_bal: uint256 = ERC20(coin_addr).balanceOf(self)
    assert coin_bal > 0, "Coin balance must be greater than 0"

    ERC20(coin_addr).approve(pool_addr, coin_bal)
    coin_index: int256[2] = self._get_coin_index(coin_addr, pool_addr, use_underlying)
    assert coin_index[0] >= 0, "Coins not found"

    if coin_index[1] == 2:
        liq_arr: uint256[2] = [0, 0]
        liq_arr[coin_index[0]] = coin_bal
        if use_underlying:
            Curve2PoolUnderlying(pool_addr).add_liquidity(liq_arr, 0, True)
        else:
            Curve2Pool(pool_addr).add_liquidity(liq_arr, 0)

    elif coin_index[1] == 3:
        liq_arr: uint256[3] = [0, 0, 0]
        liq_arr[coin_index[0]] = coin_bal
        if use_underlying:
            Curve3PoolUnderlying(pool_addr).add_liquidity(liq_arr, 0, True)
        else:
            Curve3Pool(pool_addr).add_liquidity(liq_arr, 0)

    elif coin_index[1] == 4:
        liq_arr: uint256[4] = [0, 0, 0, 0]
        liq_arr[coin_index[0]] = coin_bal
        if use_underlying:
            Curve4PoolUnderlying(pool_addr).add_liquidity(liq_arr, 0, True)
        else:
            Curve4Pool(pool_addr).add_liquidity(liq_arr, 0)
    
    else:
        assert False, "Pool not supported"


# CONSTRUCTORS

@external
def __init__(address_provider: address):
    """
    @notice Initialize the Address Provider
    @param address_provider Address of the Curve Address Provider
    """

    self.address_provider = AddressProvider(address_provider)
    self.registry = Registry(self.address_provider.get_registry())
    self.owner = msg.sender


@external
def donk(coin_addr: address, pool_addr: address):
        """
        @notice Donk into a Curve Pool, then stake in Rewards Gauge
        @param coin_addr Address of ERC20 Token
        @param pool_addr Address of Curve Pool
        """
        if coin_addr in self.registry.get_coins(pool_addr):
            self._add_liquidity(coin_addr, pool_addr, False)

        elif self.registry.is_meta(pool_addr):
            metapool_lp: address = self.registry.get_coins(pool_addr)[1]
            metapool: address = self.registry.get_pool_from_lp_token(metapool_lp)
            self._add_liquidity(coin_addr, metapool, False)
            self._add_liquidity(metapool_lp, pool_addr, False)
        elif coin_addr in self.registry.get_underlying_coins(pool_addr):
            self._add_liquidity(coin_addr, pool_addr, True)
        else:
            assert False

        lp_addr: address = self.registry.get_lp_token(pool_addr)
        lp_bal: uint256 = ERC20(lp_addr).balanceOf(self)
        assert lp_bal > 0, "Error with deposit"

        rewards_addr: address = self.registry.get_gauges(pool_addr)[0][0]
        ERC20(lp_addr).approve(rewards_addr, lp_bal)
        Gauge(rewards_addr).deposit(lp_bal)

@external
def undonk_balanced(pool_addr: address):
    """
    @notice Withdraw liquidity from Curve Rewards Gauge and Unstake
    @param pool_addr Pool Address to Drain
    """

    lp_addr: address = self.registry.get_lp_token(pool_addr)
    rewards_addr: address = self.registry.get_gauges(pool_addr)[0][0]

    Gauge(rewards_addr).withdraw(Gauge(rewards_addr).balanceOf(self))
    coins: uint256 = self.registry.get_n_coins(pool_addr)[1]
    if coins == 2:
        Curve2Pool(pool_addr).remove_liquidity(
            ERC20(lp_addr).balanceOf(self),
            [0, 0]
        )
    elif coins == 3:
        Curve3Pool(pool_addr).remove_liquidity(
            ERC20(lp_addr).balanceOf(self),
            [0, 0, 0]
        )
    elif coins == 4:
        Curve4Pool(pool_addr).remove_liquidity(
            ERC20(lp_addr).balanceOf(self),
            [0, 0, 0, 0]
        )

@external
def claim_erc20(coin_addr: address):
    """
    @notice Drain all ERC20 tokens to your address
    @param coin_addr Address of ERC20 Token
    """
    assert self.owner == msg.sender, "Only Owner"
    ERC20(coin_addr).transfer(msg.sender, ERC20(coin_addr).balanceOf(self))

@external
def set_registry():
    """
    @notice Set the Registry Address
    """
    self.registry = Registry(self.address_provider.get_registry())

