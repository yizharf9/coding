import random
import matplotlib.pyplot as plt

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
        

# 3 + # 2
def run_slotted_aloha(n = 4,num_of_slots = 1000,backof_sizes = 8,print_flag = False):
    users = [User(backof_sizes) for _ in range(n)]

    slots_successes = [None]*num_of_slots

    for i in range(num_of_slots):
        if print_flag : print(f"\ntime slot : {i}")
        
        user_send_count = 0
        for j,user in enumerate(users):
            if print_flag : print(f"user {j} : {user.time_to_send}")
            
            if user.time_to_send == 0:
                user_send_count +=1
                user.reset()
                if print_flag : print(f"found one!, new time {user.time_to_send}")
            else : 
                user.dec_time()
            
        
        slots_successes[i] = user_send_count == 1
        
        if print_flag : print(f"user_send_count : {user_send_count}")
        if print_flag : print(f"transmisison : {slots_successes[i]}")
    return sum(slots_successes)/num_of_slots , n

n_max = 65
backoff_sizes = [2**(i+3) for i in range(5)]
num_of_slots = 50_000
for backoff in backoff_sizes:
    stats = []
    for i in range(n_max):
        total_successes = run_slotted_aloha(backof_sizes=backoff,n=i,num_of_slots=num_of_slots)
        # print(total_successes)
        stats.append(total_successes)
    print(f"finished running with : {}")
    # print(stats)
    x = [item[1] for item in stats]
    y = [item[0] for item in stats]

    plt.plot(x,y,label = f"max_backoff={backoff}")
    plt.xlabel("num of users [N]")
    plt.ylabel(f"success rate [%]")
    
    plt.legend()

plt.title(f"success rate as a function of num of users \nnum_of_slots : {num_of_slots}")
plt.show()
    
