from brownie import ZERO_ADDRESS, Contract

class CurveRouter:
    
    # Registries to use for finding routes
    # The contracts are aliased through brownie
    
    registries = [
        Contract('crypto_registry'),
        Contract('registry'),
        Contract('factory')
    ]
    
    # How many hops
    max_hop = 3
    
    # Special Routing
    tripool = Contract("3pool")
    tripool_lp = Contract("3pool_lp")
    weth = Contract("weth_address")
    eth = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    
    
    def __init__(self, source_coin, max_hops=3):
            
        self.source_coin = source_coin
        self.max_hops = max_hops
        self.open_ends = self.load_v2_coins()
        self.routes = self.find_crypto_paths()
    
    def load_v2_coins(self):
        
        crypto_registry = self.registries[0]
        ret_arr = []
        for _i in range(crypto_registry.coin_count()):
            ret_arr.append(crypto_registry.get_coin(_i))
        return ret_arr
    
    def find_crypto_paths(self):
        
        i = 0
        open_ends = self.open_ends
        found_routes = [self.source_coin]
        route_map = {}
        
        for i in range(self.max_hops):
            i += 1
            open_ends, found_routes, route_map = self.recurse(
                open_ends, found_routes, route_map, 
            )
            print(
                f"Hop {i} found {len(found_routes)} endpoints, {len(open_ends)} remaining"
            )
            
            if i > self.max_hops:
                print("Terminating ", i)
                break
        self.open_ends = open_ends
        return route_map
    
    def fetch_route(self, addr1, addr2):
        
        
        for registry in self.registries:
            _route = registry.find_pool_for_coins(addr1, addr2)
            if _route != ZERO_ADDRESS:
                return _route
        
        if self.can_route_3pool(addr1, addr2):
            return self.tripool.address
        
        if self.can_route_weth(addr1, addr2):
            return self.weth.address
        
        return ZERO_ADDRESS
    
    def can_route_3pool(self, addr1, addr2):
        
        if addr1 == self.tripool_lp:
            other_token = addr2
        elif addr2 == self.tripool_lp:
            other_token = addr1
        else:
            return False
        
        for _i in range(2):
            if self.tripool.coins(_i) == other_token:
                return True
        return False
    
    def can_route_weth(self, addr1, addr2):
        if addr1 == self.weth and addr2 == self.eth:
            return True
        elif addr2 == self.weth and addr1 == self.eth:
            return True
        return False
    
    def recurse(self, missing_endpoints, starting_points, routes):
        
        next_starting_points = []
        
        for starting_point in starting_points:
            
            missing_endpoints, _found, local_routes = self.find_routes(
                missing_endpoints, starting_point
            )
            
            # Update the master routing dictionary
            for _end, _path in local_routes.items():
                if starting_point in routes:
                    routes[_end] = routes[starting_point] + [(_path, _end)]
                else:
                    routes[_end] = [(_path, _end)]
            next_starting_points += _found
            
        return missing_endpoints, next_starting_points, routes
    
    def find_routes(self, missing_endpoints, starting_point):
        
        
        # Initalize returns
        local_missing_endpoints = []
        local_found_endpoints = []
        local_routes = {}
        
        # loop missing endpoints
        
        for missing_v2_token in missing_endpoints:
            if starting_point == missing_v2_token:
                continue
            
            # Does a route exist between the two addresses?
            fetched_route = self.fetch_route(starting_point, missing_v2_token)
            
            # Update found endpoints and routeing info if located
            if fetched_route != ZERO_ADDRESS:
                local_found_endpoints.append(missing_v2_token)
                local_routes[missing_v2_token] = fetched_route
                
            # Endpoint is still missing
            else:
                local_missing_endpoints.append(missing_v2_token)
        
        return local_missing_endpoints, local_found_endpoints, local_routes
    
    
    # Display Functions to make it readable by humans
    
    def nameOf(self, pool):
        
        """
        Get the name of Curve pool across several registries
        : parm pool: Address of pool to lookup
        :return: Human readable symbol
        """
        # Factory pools don't hae a registry name lookup
        try:
            return Contract(pool).symbol()
        except:
            pass
        
        # other registries have name functions
        
        for registry in self.registries:
            _name = registry.get_pool_name(pool)
            if _name != "":
                return _name
        
        return pool
    
    def summarize(self):
        
        for coin, route in self.routes.items():
            print(f"\n Found Route to {Contract(coin).symbol()} ")
            for path in route:
                print(
                    f"Hop to {Contract(path[1]).symbol()} using {self.nameOf(path[0])} ({path[0]}) "
                )
        if self.open_ends != []:
            print(f"\n No path in {self.max_hops} hops found for:")
            for path in self.open_ends:
                print("NOPE", Contract(path).symbol())
                
                
        