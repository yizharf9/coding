# # Day 8 - Part 1 and Part 2
# import sys, re
# str = ''
# eval = ''
# reverseCount = 0
# with open('../rust/advent_of_code2015/src/excercice.txt') as f:
#     for line in f:
#         line = line.rstrip()
#         str += line
#         eval += line[1:-1] # strip quotes
#         reverseCount += line.count('\\') + line.count('"') + len(line) + 2 # add 2 for surrounding quotes each string has
# # Lets get rid of a few things
# eval = re.sub(r'\\x..|\\.', '*', eval)
# # solution
# print ('Part 1 answer is {0} - {1} = {2}'.format(len(str), len(eval), len(str)-len(eval)))
# print ('Part 2 answer is {0} - {1} = {2}'.format(reverseCount, len(str), reverseCount - len(str)))
import numpy as np

tot = 0
for i in range(1,36):
    tot += np.cos((2*np.pi*i)/17)

    
print(4*tot)

    