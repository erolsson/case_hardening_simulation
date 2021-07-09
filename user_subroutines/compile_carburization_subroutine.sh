#!/bin/bash
g++ -c -O3 -std=c++17 -fPIC  -o carbon_flux_subroutine.o carbon_flux_subroutine.cpp
g++ -c -O3 -std=c++17 -fPIC  -o utilities.o utilities.cpp
gfortran -c -fPIC getpartinfo.f
ld -r carbon_flux_subroutine.o getpartinfo.o utilities.o /usr/lib/gcc/x86_64-linux-gnu/9/libstdc++.a -o carburization_subroutine.o
