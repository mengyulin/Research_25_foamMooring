#!/bin/bash
#
# How-to use:
# Assuming a fixed number of outer iterations per time step!
# $ ./extractMulti.sh log.interFoam

file=$1

# Count the outer corrector
NCOM=$(cat $file | grep "Centre of mass" | wc -l)
NTIME=$(cat $file | grep "^Time = " | wc -l)
NOUTER=$((NCOM / NTIME))
echo "nOuterCorrector = $NCOM / $NTIME = $NOUTER"

# Load the data on separate files
grep -e "^Time = " $file | cut -d " " -f 3 > logs/times
grep "Centre of mass" $file | cut -d ":" -f 2 | tr -d "()" > logs/cM
grep "Linear velocity" $file | cut -d ":" -f 2 | tr -d "()" > logs/lV
grep "Angular velocity" $file | cut -d ":" -f 2 | tr -d "()" > logs/aV
grep "Orientation" $file  | cut -d ":" -f 2 | tr -d "()" > logs/orientation

# Split the files with data repeated each outer corrector
for ((i = 1 ; i <= $NOUTER ; i++)); do
    cat logs/cM | awk "(NR-$i) % $NOUTER == 0" > logs/cM.$i
    cat logs/lV | awk "(NR-$i) % $NOUTER == 0" > logs/lV.$i
    cat logs/aV | awk "(NR-$i) % $NOUTER == 0" > logs/aV.$i
    cat logs/orientation | awk "(NR-$i) % $NOUTER == 0" > logs/orientation.$i
done

paste logs/times logs/cM.* > logs/t_vs_CoM
paste logs/times logs/lV.* > logs/t_vs_linearV
paste logs/times logs/aV.* > logs/t_vs_angularV
paste logs/times logs/orientation.* > logs/t_vs_orientation

rm logs/times logs/cM* logs/lV* logs/orientation* logs/aV*
