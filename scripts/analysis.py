
import sys
import os
import glob
import argparse

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetOptTitle(0)

parser = argparse.ArgumentParser()
parser.add_argument("--id", type=int, default="-1", help="Run ID")
args = parser.parse_args()

outputDir = "output" # /var/www/html/webdcs
xMin, xMax = 0, 4000
binWidth = 100 # in ns
nBins = int((xMax-xMin)/binWidth)

hist_all = ROOT.TH1D("all", "All hits;Hit time (ns);Events / 100 ns", 100, 0, 10000)
hist_mp = ROOT.TH1D("mp", "Hit multiplicity;Number of hits;Events", 20, 0, 20)
hist_dt12 = ROOT.TH1D("hist_dt12", f"Time difference (MP>=2);#DeltaT(hit2, hit1);Events / {binWidth} ns", nBins, xMin, xMax)
hist_dt_2 = ROOT.TH1D("hist_dt_2", f"Time difference (MP==2);#DeltaT(hit2, hit1);Events / {binWidth} ns", nBins, xMin, xMax)
hist_dt_3 = ROOT.TH1D("hist_dt_3", f"Time difference (MP==3);#DeltaT(hit3, hit1);Events / {binWidth} ns", nBins, xMin, xMax)
hist_dt_4 = ROOT.TH1D("hist_dt_4", f"Time difference (MP==4);#DeltaT(hit4, hit1);Events / {binWidth} ns", nBins, xMin, xMax)

#hist_all.SetLineColor(ROOT.kRed)

def get_timestamps(ch_targets, channels, timestamps):
    ret = []
    for i,ch in enumerate(channels):
        if ch in ch_targets:
            ret.append(timestamps[i])
    return ret



if __name__ == "__main__":

    scanid = args.id
    outputDir = f"/home/submit/jaeyserm/public_html/vme_daq/run{scanid}/" # /var/www/html/webdcs

    channels_select = [3016]
    triggers_select = [3018]
    veto_channels = list(range(3020,3040))

    fIn = ROOT.TFile(f"output_run_{scanid}.root") # open file
    tree = fIn.Get("RAWData") # get the tree
    tree.Print()
    for iev in range(tree.GetEntries()): # loop over all events(triggers) in the tree
        tree.GetEntry(iev) # get the event
        number_of_hits = tree.number_of_hits # number of hits

        print(f"Processing event {iev}, number of hits {number_of_hits}")

        TDC_channel = tree.TDC_channel # vector of TDC channels fired
        # the address of the TDC is 33330000
        # therefore, hits are stored from channel 3000 to 3127 (in total 128 available channels)
        TDC_TimeStamp = tree.TDC_TimeStamp # timestamps of these channels fired (units in ns)


        # trigger requirement
        timstamp_sel_trg = get_timestamps(triggers_select, TDC_channel, TDC_TimeStamp)
        #timstamp_sel_trg = [t for t in timstamp_sel_trg if t > 1500]
        if len(timstamp_sel_trg) == 0:
            print("ERROR NO TRIGGERS")
            continue

        ## Veto selected channels
        veto = False
        for veto_ch in veto_channels:
            if veto_ch in TDC_channel:
                veto = True
                break

        if veto:
            print("Veto on selected channel")
            continue



        timstamp_sel = get_timestamps(channels_select, TDC_channel, TDC_TimeStamp)
        timstamp_sel_veto = [t for t in timstamp_sel if t < 1500]
        if len(timstamp_sel_veto) > 0:
            print("Veto extra trigger below 1500 ns")
            continue

        for i in timstamp_sel:
            hist_all.Fill(i) # fill all timestamps

        nhits = len(timstamp_sel)
        hist_mp.Fill(nhits)
        if nhits <= 1:
            continue


        # compute all hits time minus first hit (= trigger hit)
        firstHit = min(timstamp_sel)
        hits_dt = [i-firstHit for i in timstamp_sel]
        del(hits_dt[0])
        if nhits == 2:
            for i in hits_dt:
                hist_dt_2.Fill(i)
                #print(i)

        if nhits == 3:
            for i in hits_dt:
                hist_dt_3.Fill(i)
                #print(i)
        if nhits == 4:
            for i in hits_dt:
                hist_dt_4.Fill(i)
                #print(i)

        if nhits > 1:
            hist_dt12.Fill(hits_dt[0])
            print(hits_dt[0])

    fIn.Close()


    c = ROOT.TCanvas("c", "c", 1000, 750)
    hist_dt_2.Draw()
    c.SaveAs(f"{outputDir}/hist_dt_2_runid{scanid}.png")
    c.Clear()

    hist_dt_3.Draw()
    c.SaveAs(f"{outputDir}/hist_dt_3_runid{scanid}.png")
    c.Clear()


    hist_dt_4.Draw()
    c.SaveAs(f"{outputDir}/hist_dt_4_runid{scanid}.png")
    c.Clear()

    hist_all.Draw()
    c.SaveAs(f"{outputDir}/hist_all_runid{scanid}.png")
    c.Clear()

    hist_dt12.Draw()
    c.SaveAs(f"{outputDir}/hist_dt12_runid{scanid}.png")
    c.Clear()

    hist_mp.Draw()
    c.SaveAs(f"{outputDir}/hist_mp_runid{scanid}.png")
    c.Clear()


