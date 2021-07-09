//
// Created by erolsson on 18/11/2020.
//

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include "utilities.h"

std::vector<double> time_points;
std::vector<double> carbon_potential;
std::vector<double> parameters;

extern "C" void uexternaldb_(const int* lop, const int* lrestart, const double* time, const double* dtime,
                             const int* kstep, const int* kinc) {
    if (*lop == 0) {
        // Beginning of analysis
        std::string run_directory = get_fortran_string(getoutdir_);
        std::string job_name = get_fortran_string(getjobname_);
        std::string prefix = "Toolbox_Carbon_";
        std::string simulation_name(job_name.begin()+prefix.size(), job_name.end());
        std::string data_file_name = prefix + simulation_name + ".car";
        std::ifstream data_file(run_directory + "/" +  data_file_name);
        std::string data_line;
        std::string data_type = "";
        while (getline(data_file, data_line)) {
            if (data_line[0] == '*' && data_line[1] != '*') {
                std::transform(data_line.begin(), data_line.end(), data_line.begin(), ::tolower);
                data_type = data_line;
            }
            else if (data_type == "*carbon_potential") {
                std::vector<std::string> line_data;
                std::stringstream line(data_line);
                std::string val;
                while (getline(line, val, ',')) {
                    line_data.push_back(val);
                }
                time_points.push_back(stod(line_data[0]));
                carbon_potential.push_back(stod(line_data[1]));
            }
            else if (data_type == "*carbon_transfer_parameters"){
                std::stringstream line(data_line);
                std::string val;
                while (getline(line, val, ',')) {
                    parameters.push_back(stod(val));
                }
            }
        }
    }
}

extern "C" void dflux_(double* flux, const double& sol, const int& kstep, const int& kink, const double* time,
                       const int& noel, const int& npt, const double* coords, const int& jltyp,
                       const double& temp, const double& press, const char* sname) {
    double t = time[1];
    auto it = std::lower_bound(time_points.begin(), time_points.end(), t);
    unsigned time_point = it - time_points.begin();
    double c_pot;
    if (time_point == 0) {
        c_pot = carbon_potential[0];
    }
    else {
        double dc = carbon_potential[time_point] - carbon_potential[time_point - 1];
        double dt = time_points[time_point] - time_points[time_point - 1];
        c_pot = carbon_potential[time_point - 1] + dc/dt*(t - time_points[time_point - 1]);
    }
    double a = parameters[0] + parameters[1]*temp;
    double b = parameters[2] + parameters[3]*temp;

    double beta = a + b*sol;

    flux[0] = (c_pot - sol)*beta;
    flux[1] = -beta + (c_pot - sol)*b;
}
