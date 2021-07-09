//
// Created by erolsson on 18/12/2019.
//

#include <cstdlib>
#include <fstream>
#include <iostream>
#include <mutex>
#include <sstream>
#include <vector>

#include "utilities.h"

std::string get_material_name(const char* cmname) {
    std::string material_name(cmname);
    unsigned i = 0;
    while (isalnum(material_name[i])) {
        ++i;
    }
    return std::string(material_name.begin(), material_name.begin() + i);
}

void assign_material_parameters_from_line(const std::string& data_line, double& param1, double& param2) {

    std::stringstream line(data_line);
    std::string val;
    unsigned i = 0;
    while (getline(line, val, ',')) {
        if (i == 1) {
            param1 = stod(val);
        }
        else if (i ==2) {
            param2 = stod(val);
        }
        ++i;
    }
}


enum Phases { Austenite=0, Ferrite=1, Pearlite=2, UBainite=3, LBainite=4, QMartnsite=5, TMartensite=6};

class Phase {
public:
    Phase(double a1, double a2, double a3, double a4, double a5) :
        a1_{ a1 }, a2_{ a2 }, a3_{ a3 }, a4_{ a4*100 }, a5_{ a5*100 }  {    }

    [[nodiscard]] double expansion(double T, double C) const {
        return a1_*T + a2_*T*T + a3_*T*T*T + a4_*C*T + a5_*C*T*T;
    }

    [[nodiscard]] double dedT(double T, double C) const {
        return a1_ + 2*a2_*T + 3*a3_*T*T + a4_*C + 2*a5_*C*T;
    }

private:
    double a1_;
    double a2_;
    double a3_;
    double a4_;
    double a5_;
};

std::vector<Phase> phases {};

std::mutex set_parameters_mutex;
std::vector<double> read_values_from_string(const std::string& data_line, std::size_t values_to_read) {
    std::stringstream line(data_line);
    std::string val;
    std::vector<double> values;
    unsigned i = 0;

    while (getline(line, val, ',')) {
        if (i < values_to_read) {
            values.push_back(stod(val));
        }
        ++i;
    }
    return values;
}

void assign_expansion_parameters(const std::string& material_name) {
    {
        std::lock_guard<std::mutex> lock(set_parameters_mutex);
        if (phases.empty()){
            std::string dante_path(std::getenv("DANTE_PATH"));
            unsigned dante_version = 4;
            unsigned start_line = 68;
            std::string mech_file_name;
            if (dante_path.find("DANTEDB4") != std::string::npos) {
                mech_file_name = dante_path + "/UDB/" + material_name + "/" + material_name + ".MEC";
            }
            else {
                mech_file_name = dante_path + "/USR/" + material_name + "/" + material_name + ".MEC";
                std::cout << mech_file_name << "\n";
                dante_version = 3;
                start_line = 100;
            }
            std::ifstream mech_file(mech_file_name);
            std::string data_line;
            std::vector<std::string> data_lines;
            while (getline(mech_file, data_line)) {
                data_lines.push_back(data_line);
            }
            for (unsigned phase_idx = 0; phase_idx != 7; ++phase_idx) {
                data_line = data_lines[phase_idx*3 + start_line];
                std::string val;

                if (dante_version == 3) {
                    if (phase_idx == 0) {
                        auto values = read_values_from_string(data_line, 3);
                        phases.emplace_back(values[2], 0., 0., 0., 0.);
                    }
                    else if (phase_idx < 5) {
                        auto values = read_values_from_string(data_line, 6);
                        phases.emplace_back(values[2], values[4], 0., values[3], values[5]);
                    }
                    else {
                        auto values = read_values_from_string(data_line, 8);
                        phases.emplace_back(values[3], values[5], values[7], values[4], values[6]);
                    }
                }
                else  {
                    auto values = read_values_from_string(data_line, 2);
                    phases.emplace_back(values[0], values[1], 0., 0., 0.);
                }

            }
        }
    }
}


class State {
    double* data_;
public:
    explicit State(double* data) : data_(data) {}
    double& austenite() { return data_[0];  }
    double& carbon() { return data_[1]; }
    double& ferrite() { return data_[2];  }
    double& lbainite() { return data_[4];  }
    double& pearlite() { return data_[5];  }
    double& q_martensite() { return data_[6];  }
    double& t_martensite() { return data_[7];  }
    double& ubainite() { return data_[8];  }
};



extern "C" void uexpan_(double* expan, double* expandt, const double* temp, const double* time, const double* dtime,
                        const double* predef, const double* dpred, double* statev, const char* cmnae,
                        const int* nstatv, const int* noel) {
    std::cout << "Starting expan_\n";
    if (phases.empty()) {
        std::string material_name = get_material_name(cmnae);
        assign_expansion_parameters(material_name);
    }
    std::cout << "Phases set\n";
    auto state = State(statev);
    double dT = temp[1];
    double C = state.carbon();

    *expan = phases[Phases::Austenite].expansion(dT, C)*state.austenite()
            + phases[Phases::Ferrite].expansion(dT, C)*state.ferrite()
            + phases[Phases::LBainite].expansion(dT, C)*state.lbainite()
            + phases[Phases::Pearlite].expansion(dT, C)*state.pearlite()
            + phases[Phases::QMartnsite].expansion(dT, C)*state.q_martensite()
            + phases[Phases::TMartensite].expansion(dT, C)*state.t_martensite()
            + phases[Phases::UBainite].expansion(dT, C)*state.ubainite();

    *expandt = phases[Phases::Austenite].dedT(dT, C)*state.austenite()
               + phases[Phases::Ferrite].dedT(dT, C)*state.ferrite()
               + phases[Phases::LBainite].dedT(dT, C)*state.lbainite()
               + phases[Phases::Pearlite].dedT(dT, C)*state.pearlite()
               + phases[Phases::QMartnsite].dedT(dT, C)*state.q_martensite()
               + phases[Phases::TMartensite].dedT(dT, C)*state.t_martensite()
               + phases[Phases::UBainite].dedT(dT, C)*state.ubainite();
}