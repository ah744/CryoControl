#!/bin/bash

./CryoControlSim.py ../Algorithms/Ising/2M/ising_model.n100.flat2M. &&
./CryoControlSim.py ../Algorithms/Ising/100K/ising_model.n100.flat100k. &&
./CryoControlSim.py ../Algorithms/Ising/10K/ising_model.n100.flat010k. && 
./CryoControlSim.py ../Algorithms/Ising/1K/ising_model.n100.flat001k. && 
./CryoControlSim.py ../Algorithms/Ising/0K/ising_model.n100.flat000k. 
