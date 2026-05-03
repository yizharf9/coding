.data
    ones_array: .word 1,1,1,1,1,1,1,1,1,1,1,1,1

    prefix_array : .space 52

.text
.global main

main :
    # specified addresses for the loops building the program
    # 1. the address of the ones_array in t0
    la t0, ones_array
    # 2. the address of the prefix_array in t1
    la t1, prefix_array

    # specified address for the loop counter in t2
    li t2, 13

    # specified address for the output of the program in t3
    li t3, 0


# A loop for summing
prefix_loop :
    # stop condition
    beq t2, zero, sum_prep

    # load the i-th number in the array at each iteration
    lw t4, 0(t0)

    # add the i-th number in the ones_array to the current running sum
    add t3, t3, t4

    # advance the array pointer pointing at the 
    # 1. current ones_array element 
    addi t0, t0, 4
    # 2. current prefix_array element 
    addi t1, t1, 4

    # subtract one iteration from the loop counter
    addi t2, t2, -1

    # jump back to the beggining of the loop for re-evaluation of the loop condition
    j prefix_loop

# before summing an array we need to run this function
sum_prep :
    # loads starting address of the array
    la t1, prefix_array
    # loads the total number of iterations
    li t2, 13
    # initializes the sum of the array to 0
    li t5, 0

# iterating through all calculated values in prefix array one last time 
# to calculate the desired output
sum_loop :
    # after this loop the, exit the program
    beq t2, zero, end_prog

    # load the current element of prefix_array that was previously calculated
    lw t4, 0(t1)

    # t5 accumalates all values in the array
    add t5, t5, t4

    # 2. advance pointer of current prefix_array element 
    addi t1, t1, 4

    # subtract one iteration from the loop counter
    addi t2, t2, -1
    
    # jump back to the beggining of the loop for re-evaluation of the loop condition    
    j sum_loop

end_prog : 
    # load final result from the output register of the summing loop 
    # to a0 - designated register for the printing function
    mv a0, t5 

    # loads the print function in designated register for execution
    li a7, 1 
    # execution of command inside register a7 accordingly
    ecall 

    # loads the exit-program function in designated register for execution
    li a7, 10
    # execution of command inside register a7 accordingly, as of before...
    ecall

    # END OF PROGRAM

