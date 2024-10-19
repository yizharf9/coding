excercice_path = "../rust/advent_of_code2015/src/excercice.txt"
sample_path = "../rust/advent_of_code2015/src/sample.txt"

def get_routes(locations:list[str],current_route:list[str]=[],routes:list[list[str]]=[]):
    # print(f"{current_route}\n")
    
    if len(locations) == 0:        
        routes.append(current_route)
        
    for i in range(len(locations)):
        possible_locations = locations[:i]+locations[i+1:]
        next_route = current_route + [locations[i]]
        get_routes(possible_locations,next_route,routes) 

def get_total_distance(route:list[str],roads:list[(str,str,int)]):
    total_distance = 0
    for i in range(len(route)-1):
        source = route[i]
        destination = route[i+1]
        total_distance += roads[source][destination]
    return total_distance

roads:dict[dict[int]] = {}
locations = set()

with open(excercice_path) as f:
    f = f.readlines()
    for line in f:
        terms = line.split()
        source = terms[0]
        destination = terms[2]
        distance = int(terms[4])
        
        if roads.get(source,0) == 0 :
            roads.update({source:{}})
            if roads[source].get(destination,0) == 0:
                roads[source].update({destination:0})
            
        if  roads.get(destination,0) == 0:
            roads.update({destination:{}})
            if roads[source].get(destination,0) == 0:
                roads[destination].update({source:0})
        
        roads[source].update({destination:distance})
        roads[destination].update({source:distance})
        roads.update()
        locations.add(terms[0])
        locations.add(terms[2])

all_locations = [loc for loc in locations]
for key,val in roads.items():
    print(key,val)

result = []
get_routes(all_locations,[],result)
# for route in result:
#     print(route)
#     print(get_total_distance(route,roads))

shortest_road = min(
    result,
    key= lambda route : get_total_distance(route,roads)
)
longest_road = max(
    result,
    key= lambda route : get_total_distance(route,roads)
)
print(f"\nthe shortest road is {shortest_road} \nwith length {get_total_distance(shortest_road,roads)}")
print(f"\nthe longest road is {longest_road} \nwith length {get_total_distance(longest_road,roads)}")
