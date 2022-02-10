from brownie import *

def main():
    # Pull Address Provider to retrieve Dynamically

    address_provider = "0x0000000022d53366457f9d5e68ec105046fc4383"
    ap = set_alias(address_provider, "address_provider")
    minter_address = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"
    minter = set_alias(minter_address, "minter_address")
    


    # Set up Provider contracts with aliases
    
    # minter = set_alias(m.token(), "minter")
    registry = set_alias(ap.get_registry(), "registry")
    pool_info = set_alias(ap.get_address(1), "pool_info")
    exchange = set_alias(ap.get_address(2), "registry_exchange")
    factory = set_alias(ap.get_address(3), "factory")
    distributor = set_alias(ap.get_address(4), "distributor")

    controller = set_alias(registry.gauge_controller(), "gauge_controller")

    # CRV + veCRV
    crv = set_alias(controller.token(), "crv")
    vecrv = set_alias(controller.voting_escrow(), "vecrv")

    # Set up Pool contracts with aliases pool, lp and rewards
    for index in range(registry.pool_count()):
        # Set the aliases
        pool_addr =registry.pool_list(index)
        name = registry.get_pool_name(pool_addr)
        pool = set_alias(pool_addr, name)

        # Set the LP Token
        lp = set_alias(registry.get_lp_token(pool), f"{name}_lp")

        # Set the Rewards Token
        rewards_addr = registry.get_gauges(pool)[0][0]
        rewards_alias = f"{name}_rewards"
        pool_rewards = set_alias(rewards_addr, rewards_alias)

    
    # Setting tokens to be minted globally with brownie token minter
    # Tripool
    tri = Contract("3pool")
    dai = set_alias(tri.coins(0), "dai")
    usdc = set_alias(tri.coins(1), "usdc")
    tether = set_alias(tri.coins(2), "tether")

    # Convex pools 

    cvx = set_alias("0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b", "cvx")
    cvx = set_alias("0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7", "cvxcrv")
    booster = set_alias("0xF403C135812408BFbE8713b5A23a04b3D48AAE31", "cvx_booster")
    staker = set_alias("0xCF50b810E57Ac33B91dCF525C6ddd9881B139332", "cvx_staker")

def load_contract(addr):
    try:
        c = Contract(addr)
    except:
        c = Contract.from_explorer(addr)
    return c

def set_alias(addr, name):
    if addr == ZERO_ADDRESS:
        return
    print(f"Setting alias for {name} as {addr}")
    c = load_contract(addr)

    try:
        c.set_alias(name)
    except Exception as e:
        print(e)
        old = load_contract(name)
        print(f"Unsetting alias for {name} as {old.address}")
        old.set_alias(None)
        c.set_alias(name)
    return c
