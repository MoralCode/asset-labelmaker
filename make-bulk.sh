#!/bin/bash

#Parallel runs in N-process batches
# https://unix.stackexchange.com/a/216475/

#batch size
N=5
(
for id in {00001..00050}; do 
   ((i=i%N)); ((i++==0)) && wait
   	ASSETID="E$id" make default &
done
wait
echo "Done."
exit 0
)
