#!/usr/bin/env python3
import sys
import ROOT
import numpy as np

if len(sys.argv) != 5:
    print("Usage: python example_TH3F.py <root_file> <pT> <eta> <flavor>")
    sys.exit(1)

root_file = sys.argv[1]
pT_val = float(sys.argv[2])
eta_val = float(sys.argv[3])
flav_val = int(sys.argv[4])

# 打开 ROOT 文件
f = ROOT.TFile.Open(root_file)
if not f or f.IsZombie():
    print(f"Cannot open file {root_file}")
    sys.exit(1)

# 获取 TH3F
hist = f.Get("btag_eff")
if not hist:
    print("TH3F 'btag_eff' not found in file")
    sys.exit(1)

# 获取 binning
pt_bins = [hist.GetXaxis().GetBinLowEdge(i+1) for i in range(hist.GetNbinsX())] + [hist.GetXaxis().GetBinUpEdge(hist.GetNbinsX())]
eta_bins = [hist.GetYaxis().GetBinLowEdge(i+1) for i in range(hist.GetNbinsY())] + [hist.GetYaxis().GetBinUpEdge(hist.GetNbinsY())]
flav_bins = [int(hist.GetZaxis().GetBinCenter(i+1)) for i in range(hist.GetNbinsZ())]

# 找到对应 bin
pt_bin = hist.GetXaxis().FindBin(pT_val)
eta_bin = hist.GetYaxis().FindBin(eta_val)
flav_bin = hist.GetZaxis().FindBin(flav_val)

# 获取内容
value = hist.GetBinContent(pt_bin, eta_bin, flav_bin)
print(f"b-tag efficiency at pT={pT_val}, eta={eta_val}, flavor={flav_val} -> {value:.4f}")

f.Close()
