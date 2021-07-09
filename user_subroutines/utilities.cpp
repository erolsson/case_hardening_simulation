//
// Created by erolsson on 18/11/2020.
//

#include <string>

std::string get_fortran_string(void (*fortran_func)(char*, int&, int)){
    char out_char[256];
    int out_len = 0;
    fortran_func(out_char, out_len, 256);
    return std::string(out_char, out_char+out_len);
}