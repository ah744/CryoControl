#!/bin/bash
loc=~/Scaffold_Master_October4/scripts/
names=('binary_welded_tree.n100s100' 'boolean_formula.x2y2' 'ground_state_estimation.m10' 'ising_model.n100' 'qft.n05' 'sha1.n1024' 'shors.n4' 'shors.n512' 'square_root.n10')
items=(10 100 500 1000 10000 100000 1000000)
for key in "${names[@]}"
do
	mkdir -p $key
	cd $key
	cp /home/aholmes/Scaffold_Master_October4/scripts/full-parallel-$key/*lpfs .
	cd ../
done
