# Makefile
BIN = ./bin/

all : $(BIN)/linker $(BIN)/cachesim $(BIN)/moduleextraction

$(BIN)/linker : Linker.cpp
	g++ -std=c++11 Linker.cpp -o $(BIN)/linker 
$(BIN)/cachesim : CacheSim.cpp
	g++ -std=c++11 CacheSim.cpp -o $(BIN)/cachesim
$(BIN)/moduleextraction : ModuleExtraction.cpp
	g++ -std=c++11 ModuleExtraction.cpp -o $(BIN)/moduleextraction 
