#!/bin/bash
#echo "Bash version ${BASH_VERSION}..."

for i in 125 250 500 750 1000  
do
    #echo $i
    mkdir "$HOME/working_dir/parallel_implementations/pcompact/iteration_$i"
    cd iteration_$i
    python $HOME/working_dir/parallel_implementations/pcompact/mp_code.py $HOME/working_dir/parallel_implementations/pcompact/16x16.dbf $i
    cd ../
done
