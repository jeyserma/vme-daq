// ****************************************************************************************************
// *   DataReader
// *   Alexis Fagot
// *   23/01/2015
// ****************************************************************************************************

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <ctime>
#include <unistd.h>
#include <chrono>

#include "TH1I.h"
#include "TH1D.h"

#include "../include/DataReader.h"
#include "../include/MsgSvc.h"
#include "../include/utils.h"

using namespace std;

// ****************************************************************************************************

DataReader::DataReader(){
    //Initialisation of the RAWData vectors
    TDCData.EventList = new vector<int>;
    TDCData.NHitsList = new vector<int>;
    TDCData.QFlagList = new vector<int>;
    TDCData.ChannelList = new vector< vector<int> >;
    TDCData.TimeStampList = new vector< vector<float> >;
    TDCData.TriggerTimeStampList = new vector<int64_t>;

    //Cleaning all the vectors
    TDCData.EventList->clear();
    TDCData.NHitsList->clear();
    TDCData.QFlagList->clear();
    TDCData.ChannelList->clear();
    TDCData.TimeStampList->clear();
    TDCData.TriggerTimeStampList->clear();

    StopFlag = false;
}

// ****************************************************************************************************

DataReader::~DataReader(){

}

// ****************************************************************************************************

void DataReader::SetIniFile(string inifilename){
    iniFile = new IniFile(inifilename);
    iniFile->Read();
}

// ****************************************************************************************************

void DataReader::SetMaxTriggers(){
    MaxTriggers = iniFile->intType("General","MaxTriggers",MAXTRIGGERS_V1190A);
}

void DataReader::SetRunId(int id){
    run_id = id;
}

// ****************************************************************************************************

Data32 DataReader::GetMaxTriggers(){
    return MaxTriggers;
}

// ****************************************************************************************************

void DataReader::SetVME(){
    VME = new v1718(iniFile);
}

// ****************************************************************************************************

void DataReader::SetTDC(){
    nTDCs = iniFile->intType("General","Tdcs",MINNTDC);
    TDCs = new v1190a(VME->GetHandle(),iniFile,nTDCs);

    /*********** initialize the TDC 1190a ***************************/
    TDCs->Set(iniFile,nTDCs);
}

// ****************************************************************************************************

int DataReader::GetQFlag(Uint it){
    int flag = TDCData.QFlagList->at(it);
    int nDigits = nTDCs;

    int tmpflag = flag;
    while(nDigits != 0){
        int tdcflag = tmpflag/(int)pow(10,nDigits-1);

        if(tdcflag == CORRUPTED) flag = flag + 2*(int)pow(10,nDigits-1);

        tmpflag = tmpflag%(int)pow(10,nDigits-1);
        nDigits--;
    }

    return flag;
}

// ****************************************************************************************************

void DataReader::Init(string inifilename){
    SetIniFile(inifilename);
    SetMaxTriggers();
    SetVME();
    SetTDC();
}

// ****************************************************************************************************

void DataReader::Update(){
    iniFile->Read();
    SetMaxTriggers();
}

// ****************************************************************************************************

void DataReader::FlushBuffer(){
    VME->SendBUSY(ON);
    TDCs->Clear(nTDCs);
    VME->SendBUSY(OFF);
}

// ****************************************************************************************************

string DataReader::GetFileName(){
    string outputfName = "output_run_" + std::to_string(run_id) + ".root";
    return outputfName;
}

// ****************************************************************************************************

void DataReader::WriteRunRegistry(string filename){
    /*
    //Open the run registry file and wirte the new file name
    ofstream runregistry(__registrypath.c_str(),ios::app);

    string filepath = filename.substr(0,filename.find_last_of("/")+1);
    string name = filename.substr(filename.find_last_of("/")+1);

    runregistry << GetTimeStamp() << '\t' << name << '\t' << filepath << '\n';
    runregistry.close();

    //Save the last run name in the "last" file (useful to start
    //offline analysis from DCS)
    ofstream last(__lastfilepath.c_str(),ios::out);
    last << name.substr(0,name.find_last_of("."));
    last.close();
    */
}

// ****************************************************************************************************

void DataReader::Run(){
    //Get the output file name and create the ROOT file
    Uint TriggerCount = 0;
    Uint LastEventCount = 0;
    string outputFileName = GetFileName();
    long long startstamp = GetTimeStamp();

    TFile *outputFile = new TFile(outputFileName.c_str(), "recreate");

    //Create the data tree where the data will be saved
    //For each entry will be saved the event tag, the number of hits recorded
    //in the TDCs, the list of fired TDC channels and the time stamps of the
    //hits.
    TTree *RAWDataTree = new TTree("RAWData","RAWData");

    int           EventCount = -9;          //Event tag
    int           nHits = -8;               //Number of fired TDC channels in event
    int           qflag = -7;               //Event quality flag (0 = CORRUPTED | 1 = GOOD)
    int64_t       trigger_timestamp = -1;   //Trigger timestamp (in ms since UNIX EPOCH)
    vector<int>   TDCCh;                    //List of fired TDC channels in event
    vector<float> TDCTS;                    //list of fired TDC channels time stamps

    TDCCh.clear();
    TDCTS.clear();

    //Set the branches that will contain the previously defined variables
    RAWDataTree->Branch("EventNumber",          &EventCount, "EventNumber/I");
    RAWDataTree->Branch("number_of_hits",       &nHits,      "number_of_hits/I");
    RAWDataTree->Branch("Quality_flag",         &qflag,      "Quality_flag/I");
    RAWDataTree->Branch("TDC_channel",          &TDCCh);
    RAWDataTree->Branch("TDC_TimeStamp",        &TDCTS);
    RAWDataTree->Branch("trigger_timestamp",    &trigger_timestamp, "trigger_timestamp/L");

    //Cleaning all the vectors that will contain the data
    TDCData.EventList->clear();
    TDCData.NHitsList->clear();
    TDCData.QFlagList->clear();
    TDCData.ChannelList->clear();
    TDCData.TimeStampList->clear();
    TDCData.TriggerTimeStampList->clear();

    //Clear all the buffers that can have started to be filled
    //by incoming triggers and start data taking. If non efficiency
    //tun type, turn ON trigger pulse.
    FlushBuffer();

    VME->RDMTriggerPulse(ON);

    MSG_INFO("[DAQ] Run started");
    MSG_INFO("[DAQ] Triggers collected: 0");

    //Every once in a while read the run file to check for a KILL command
    //Create a check kill clock
    //Uint CKill_Clk = 0;
    //Uint CKill_Clk_Cycle = (Uint)CHECKKILLPERIOD/(CHECKIRQPERIOD*1e-6);
    //bool KillReceived = false;

    //Read the output buffer until the min number of trigger is achieved
    //while(TriggerCount < GetMaxTriggers() && !KillReceived){
    bool stopAcq = false;
    while(TriggerCount < GetMaxTriggers() && !stopAcq){
        //Check the TDC buffers for data every 100ms
        //If there is data, an interupt request is present
        usleep(CHECKIRQPERIOD);

        if(VME->CheckIRQ()){
            //Stop data acquisition with BUSY as VETO (the rising time of
            //the signal is of the order of 1ms)
            VME->SendBUSY(ON);
            usleep(1000);
            

            //Read the data
            TriggerCount = TDCs->Read(&TDCData,nTDCs);
            //std::cout << ms << " TriggerCount=" << TriggerCount << " TriggerTimeStampListSize=" << TDCData.TriggerTimeStampList->size() << " TDCData.EventList.size=" << TDCData.EventList->size() << std::endl;

            MSG_INFO("[DAQ] Triggers collected: "+std::to_string(TriggerCount));

            // get the trigger time in ms
            auto now = std::chrono::system_clock::now();
            auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
            
            for(int k=0; k<(TriggerCount-LastEventCount); k++) {
                TDCData.TriggerTimeStampList->push_back(ms);
            }

            LastEventCount = TriggerCount; // update lastEventCount

            //Resume data taking - Release VETO signal
            VME->SendBUSY(OFF);
        }

        stopAcq = CheckKILL();
        //Increment the kill clock
        //CKill_Clk++;

        //check inside the run file for a KILL command
        
        //if(CKill_Clk == CKill_Clk_Cycle){
        //    KillReceived = CheckKILL();
        //    CKill_Clk = 0;
        //}
    }


    //Write the data from the RAWData structure to the TTree and
    //change the QFlag digits that are equal to 0, to 2 for later
    //offline analysis.
    for(Uint i=0; i<TDCData.EventList->size(); i++){
        EventCount  = TDCData.EventList->at(i);
        nHits       = TDCData.NHitsList->at(i);
        qflag       = GetQFlag(i);
        TDCCh       = TDCData.ChannelList->at(i);
        TDCTS       = TDCData.TimeStampList->at(i);
        trigger_timestamp = TDCData.TriggerTimeStampList->at(i);
        RAWDataTree->Fill();
    }

    VME->RDMTriggerPulse(OFF);

    RAWDataTree->Print();
    RAWDataTree->Write();

    delete RAWDataTree;

    //******************************************************************************


    //Needed variable to go through the configuration file
    string group;
    string Parameter;
    string RPClabel;
    int value = 0;


    //Now fill the configuration parameters
    IniFileData inidata = iniFile->GetFileData();

    for(IniFileDataIter Iter = inidata.begin(); Iter!= inidata.end(); Iter++){
        size_t separator_pos = Iter->first.find_first_of('.');
        if (separator_pos == string::npos)
            continue;

        group = Iter->first.substr(0, separator_pos);
    }

    outputFile->Close();

    delete outputFile;

}
