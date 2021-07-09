//
// Created by erolsson on 18/11/2020.
//

#ifndef CASE_HARDENING_TOOLBOX_UTILITIES_H
#define CASE_HARDENING_TOOLBOX_UTILITIES_H

#include <string>

std::string get_fortran_string(void (*fortran_func)(char*, int&, int));
extern "C" void getoutdir_(char* outdir, int&, int);
extern "C" void getjobname_(char* outdir, int&, int);
extern "C" void getpartinfoc_(char* name, int& name_len, const int& num, const int& jtype, int& user_num, int& error);
extern "C" void getelemnumberuser_(const int& num, int& user_num);

#endif //CASE_HARDENING_TOOLBOX_UTILITIES_H
