#!/bin/bash
g++ -c -O3 -std=c++17 -fPIC -I "${EIGENPATH}" -o initial_values.o initial_values.cpp
g++ -c -O3 -std=c++17 -fPIC -I "${EIGENPATH}" -o heat_expansion.o heat_expansion.cpp
g++ -c -O3 -std=c++17 -fPIC -I "${EIGENPATH}" -o utilities.o utilities.cpp
gfortran -c -fPIC getpartinfo.f
ld -r initial_values.o heat_expansion.o getpartinfo.o utilities.o /usr/lib/gcc/x86_64-linux-gnu/9/libstdc++.a -o cooling_subroutine.o
