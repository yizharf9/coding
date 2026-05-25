.data
    ones_array: .word 1,1,1,1,1,1,1,1,1,1,1,1,1
#    ones_array: .word 1,2,3,4,5,6,7,8,9,10,11,12,13


    prefix_array : .space 52
    
    output : .space 4

.text
.global main


main :
	la t1,ones_array

	la t2,prefix_array
	
	#counter register
	li t3,13
	
	#a[n] register
	li t4,0

	# accumalater register
	li t5,0
	
	#li t3,13
	
set_prefix :

	lw t4,0(t1)
	
	beqz t3,set_ehad_mi_yodea
		
	add t5,t5,t4
	
	sw t5, 0(t2)
	
	addi t1,t1,4
	addi t2,t2,4	
	
	addi t3,t3,-1
	
	j set_prefix
	
set_ehad_mi_yodea :

	la t2,prefix_array
	
	li t3,13
	li t4,0
	li t5,0	
	
	j ehad_mi_yodea
	
ehad_mi_yodea :
	beqz t3,end_prog
	
	lw t4,0(t2)
	
	add t5,t5,t4
	
	addi t2,t2,4
	addi t3,t3,-1
	
	j ehad_mi_yodea 

end_prog :
	la t6,output
	

	sw t5,0(t6)
	
	
