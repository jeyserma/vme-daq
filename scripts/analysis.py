
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

outputDir = "/var/www/html/webdcs"
xMin, xMax = 0, 4000
binWidth = 100 # in ns
nBins = int((xMax-xMin)/binWidth)

hist_all = ROOT.TH1D("all", "All hits;Hit time (ns);Events / 100 ns", 100, 0, 10000)
hist_mp = ROOT.TH1D("mp", "Hit multiplicity;Number of hits;Events", 10, 0, 10)
hist_dt12 = ROOT.TH1D("hist_dt12", f"Time difference (MP>=2);#DeltaT(hit2, hit1);Events / {binWidth} ns", nBins, xMin, xMax)
hist_dt_2 = ROOT.TH1D("hist_dt_2", f"Time difference (MP==2);#DeltaT(hit2, hit1);Events / {binWidth} ns", nBins, xMin, xMax)
hist_dt_3 = ROOT.TH1D("hist_dt_3", f"Time difference (MP==3);#DeltaT(hit3, hit1);Events / {binWidth} ns", nBins, xMin, xMax)
hist_dt_4 = ROOT.TH1D("hist_dt_4", f"Time difference (MP==4);#DeltaT(hit4, hit1);Events / {binWidth} ns", nBins, xMin, xMax)

#hist_all.SetLineColor(ROOT.kRed)

if __name__ == "__main__":

    scanid = args.id

    fIn = ROOT.TFile(f"output_run_{scanid}.root")
    tree = fIn.Get("RAWData")
    tree.Print()
    for iev in range(tree.GetEntries()):
        tree.GetEntry(iev)
        number_of_hits = tree.number_of_hits

        print(f"Processing event {iev}, number of hits {number_of_hits}")

        TDC_channel = tree.TDC_channel
        TDC_TimeStamp = tree.TDC_TimeStamp

        for i in TDC_TimeStamp:
            hist_all.Fill(i)

        nhits = len(TDC_TimeStamp)
        hist_mp.Fill(nhits)
        if nhits <= 1:
            continue
        firstHit = min(TDC_TimeStamp)
        hits_dt = [i-firstHit for i in TDC_TimeStamp]
        del(hits_dt[0])
        if nhits == 2:
            for i in hits_dt:
                hist_dt_2.Fill(i)
                print(i)

        if nhits == 3:
            for i in hits_dt:
                hist_dt_3.Fill(i)
                print(i)
        if nhits == 4:
            for i in hits_dt:
                hist_dt_4.Fill(i)
                print(i)

        if nhits > 1:
            hist_dt12.Fill(hits_dt[0])

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



