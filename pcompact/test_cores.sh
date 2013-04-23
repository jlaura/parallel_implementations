#!/bin/bash
#echo "Bash version ${BASH_VERSION}..."

for p in 4 #16 64
do 
    for c in 10 8 6 4 2
        do
	echo $p $c
	python mp_code.py 16x16.dbf $p $c  
done
done

#for p in 9 #36 81
#do
    #for c in 10 8 6 4 2
        #do
	#echo $p
	#python mp_code.py 18x18.dbf $p $c
#done
#done

#for p in 49
#do
	#echo $p
	#python mp_code.py 14x14.dbf $p 12
#done

#for p in 25 100
#do
	#echo $p
	#python mp_code.py 20x20.dbf $p 12
#done

