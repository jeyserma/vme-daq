
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


xMin, xMax = 0, 1000

hist_all = ROOT.TH1D("all", "All hits", 1000, 0, 10000)
hist_mp = ROOT.TH1D("mp", "Hit multiplicity", 5, 0, 5)
hist_dt12 = ROOT.TH1D("hist_dt12", "#DeltaT(hit2,hit1)", xMax-xMin, xMin, xMax)
hist_dt_2 = ROOT.TH1D("hist_dt_2", "#DeltaT 2 hits", xMax-xMin, xMin, xMax)
hist_dt_3 = ROOT.TH1D("hist_dt_3", "#DeltaT 3 hits", xMax-xMin, xMin, xMax)
hist_dt_4 = ROOT.TH1D("hist_dt_4", "#DeltaT 4 hits", xMax-xMin, xMin, xMax)

hist_all.SetLineColor(ROOT.kRed)

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
    hist_dt_2.GetXaxis().SetTitle("#DeltaT (ns)")
    hist_dt_2.Draw()
    c.SaveAs(f"output/hist_dt_2_runid{scanid}.png")
    c.Clear()

    hist_dt_3.GetXaxis().SetTitle("#DeltaT (ns)")
    hist_dt_3.Draw()
    c.SaveAs(f"output/hist_dt_3_runid{scanid}.png")
    c.Clear()


    hist_dt_4.GetXaxis().SetTitle("#DeltaT (ns)")
    hist_dt_4.Draw()
    c.SaveAs(f"output/hist_dt_4_runid{scanid}.png")
    c.Clear()

    hist_all.GetXaxis().SetTitle("Hit timestamp (ns)")
    hist_all.Draw()
    c.SaveAs(f"output/hist_all_runid{scanid}.png")
    c.Clear()

    hist_dt12.GetXaxis().SetTitle("#DeltaT (ns)")
    hist_dt12.Draw()
    c.SaveAs(f"output/hist_dt12_runid{scanid}.png")
    c.Clear()

    hist_mp.GetXaxis().SetTitle("Hit multiplicity")
    hist_mp.Draw()
    c.SaveAs(f"output/hist_mp_runid{scanid}.png")
    c.Clear()



