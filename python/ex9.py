excercice_path = "../rust/advent_of_code2015/src/excercice.txt"
sample_path = "../rust/advent_of_code2015/src/sample.txt"

roads = {}
locations = set()
with open(excercice_path) as f:
    f = f.readlines()
    for line in f:
        terms = line.split()
        # (terms[0],terms[2]),terms[4])
        
        
        roads.update()
        locations.add(terms[0])
        locations.add(terms[2])

all_locations = [loc for loc in locations]

print(all_locations)

# def get_routes(locations:list[str],current_route:list[str]=[],routes:list[list[str]]=[]):
#     print(f"{current_route}\n")
#     if len(locations) == 0:        
#         return []
    
#     for i in range(len(locations)):
#         possible_locations = locations[:i]+locations[i+1:]
#         next_route = current_route + [locations[i]]
        
#         possible_routes = get_routes(possible_locations,next_route,routes)
#         if len(possible_routes) == 0:
#             routes.append(possible_routes + next_route)
#         else:
#             for route in possible_routes:
#                 route = current_route + route
#                 routes.append(route)
                
#     return routes

global _routes
_routes = []

def get_routes(locations:list[str],current_route:list[str]=[]):
    # print(f"{current_route}\n")
    if len(locations) == 0:        
        return _routes.append(current_route)
    
    for i in range(len(locations)):
        possible_locations = locations[:i]+locations[i+1:]
        next_route = current_route + [locations[i]]
        get_routes(possible_locations,next_route)



get_routes(all_locations)
for route in _routes:
    print(route)
    
def get_total_distance(route:list[str],roads:list[(str,str,int)]):
    total_distance = 0
    for i in range(len(route)-1):
        pass