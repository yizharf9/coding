excercice_path = "../rust/advent_of_code2015/src/excercice.txt"
sample_path = "../rust/advent_of_code2015/src/sample.txt"

roads = []
locations = set()
with open(sample_path) as f:
    f = f.readlines()
    for line in f:
        terms = line.split()
        roads.append(((terms[0],terms[2]),terms[4]))
        locations.add(terms[0])
        locations.add(terms[2])

all_locations = [loc for loc in locations]

print(all_locations)

def get_routes(locations:list[str],current_route:list[str]=[],routes:list[list[str]]=[]):
    print(f"{current_route}\n")
    if len(locations) == 0:        
        return []
    
    for i in range(len(locations)):
        possible_locations = locations[:i]+locations[i+1:]
        next_route = current_route + [locations[i]]
        
        possible_routes = get_routes(possible_locations,next_route,routes)
        
        for route in possible_routes:
            route = current_route + route
            routes.append(route)
        
    return routes

get_routes(all_locations)