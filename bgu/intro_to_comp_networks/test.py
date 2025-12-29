import random

random.seed(42)

# 1
class User:
    def __init__(self, max_backoff):
        self.max_backoff = max_backoff
        self.time_to_send = random.randint(0, max_backoff) #! <= change time_to_send !!!

    def dec_time(self):
        if self.time_to_send > 0:
            self.time_to_send -= 1

    def reset(self):
        self.time_to_send = random.randint(0, self.max_backoff)
        

# 2
n_max = 6
num_of_slots = 6
backof_sizes = [8]

# 3
users = [User(backof_sizes[0]) for _ in range(n_max)]

slots_successes = [None]*num_of_slots

for i in range(num_of_slots):
    print(f"\ntime slot : {i}")
    
    user_send_count = 0
    for j,user in enumerate(users):
        print(f"user {j} : {user.time_to_send}")
        
        if user.time_to_send == 0:
            print("found one!")
            user_send_count +=1
            user.reset()
        user.dec_time()
        
    
    slots_successes[i] = user_send_count == 1
    
    print(f"user_send_count : {user_send_count}")
    print(f"transmisison : {slots_successes[i]}")

print(slots_successes)