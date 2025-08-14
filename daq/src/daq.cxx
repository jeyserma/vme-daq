// **********************************************************************
// *   DAQ for the GIF
// *   Y.Benhammou, Alexis Fagot
// *   14/1/2015
// *********************************************************************

#include "../include/DataReader.h"
#include "../include/utils.h"
#include "../include/MsgSvc.h"
#include <limits>
#include <fstream>

using namespace std;

int main(int argc ,char *argv[]) {
    string ini_path;
    int run_id;

    if(argc == 3) {
        ini_path = argv[1];
        run_id = atoi(argv[2]);
    } else {
        SendDAQError();
        exit(EXIT_FAILURE);
    }

    MSG_INFO("DAQ Program 2025");
    MSG_INFO("INI FILE " + ini_path);
    MSG_INFO("RUN NUMBER " + std::to_string(run_id));

    DataReader *DR = new DataReader();
    DR->SetRunId(run_id);

    /* Initialisation of the setup */
    MSG_INFO("[DAQ] Initialisation of the TDCs. Please wait, this may take a few minutes...");
    DR->Init(ini_path);
    MSG_INFO("[DAQ] Initialisation done, start acquisition");


    DR->Update();
    DR->Run();


    MSG_INFO("[DAQ] Run finished.");

}

