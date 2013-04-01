#!/bin/bash
#echo "Bash version ${BASH_VERSION}..."

for p in 4 #16 64  
do
    #echo $i
    #mkdir "$HOME/working_dir/parallel_implementations/pcompact/iteration_$p"
    mkdir "$HOME/github/parallel_implementations/pcompact/iteration_$p"
    cd iteration_$p
    #python $HOME/working_dir/parallel_implementations/pcompact/mp_code.py $HOME/working_dir/parallel_implementations/pcompact/16x16.dbf $p 
    python $HOME/github/parallel_implementations/pcompact/mp_code.py $HOME/github/parallel_implementations/pcompact/16x16.dbf $p
    cd ../
done
