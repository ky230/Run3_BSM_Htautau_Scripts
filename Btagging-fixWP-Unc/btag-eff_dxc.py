#!/usr/bin/env python3
import sys
import ROOT
import numpy as np
from tqdm import tqdm
import threading
import time

# ROOT.EnableImplicitMT()  # 启用多线程

# -------------------
# 配置 binning
pt_bins = np.array(
    [20, 30, 50, 70, 100, 140, 200, 300, 600, 1000], dtype=float
)
eta_bins = np.array([-2.5, 2.5], dtype=float)
flav_bins = [0, 4, 5]  # light, c, b

# flavor bin 边界 (Z 轴)
flav_bins_edges = np.array([-0.5, 0.5, 4.5, 5.5], dtype=float)  # 对应 [0], [4], [5]


# -------------------
def get_btag_threshold(era):
    thresholds = {
        "2022preEE": 0.245,
        "2022postEE": 0.2605,
        "2023preBPix": 0.1917,
        "2023postBPix": 0.1919
    }
    return thresholds.get(era, 0.245)
def check_channel_cut_expr(channel, delta_r_min=0.5):
    """返回 RDataFrame 可用的 channel cut 表达式（使用 leading lepton + 基础 Jet cut + ΔR 防重叠）"""
    jet_cut = "ROOT::VecOps::All(Jet_pt>20) && ROOT::VecOps::All(abs(Jet_eta)<2.5)"

    if channel == "et":
        # leading Electron vs leading Tau
        return (
            f"nElectron>=1 && nTau>=1 && "
            "ROOT::VecOps::Max(Electron_pt)>25 && ROOT::VecOps::Max(Tau_pt)>25 && "
            "abs(Electron_eta[ROOT::VecOps::ArgMax(Electron_pt)])<2.1 && "
            "abs(Tau_eta[ROOT::VecOps::ArgMax(Tau_pt)])<2.3 && "
            f"ROOT::VecOps::DeltaR(Electron_eta[ROOT::VecOps::ArgMax(Electron_pt)], "
            f"Electron_phi[ROOT::VecOps::ArgMax(Electron_pt)], "
            f"Tau_eta[ROOT::VecOps::ArgMax(Tau_pt)], "
            f"Tau_phi[ROOT::VecOps::ArgMax(Tau_pt)]) > {delta_r_min} && "
            f"{jet_cut}"
        )
    elif channel == "mt":
        # leading Muon vs leading Tau
        return (
            f"nMuon>=1 && nTau>=1 && "
            "ROOT::VecOps::Max(Muon_pt)>23 && ROOT::VecOps::Max(Tau_pt)>30 && "
            "abs(Muon_eta[ROOT::VecOps::ArgMax(Muon_pt)])<2.1 && "
            "abs(Tau_eta[ROOT::VecOps::ArgMax(Tau_pt)])<2.3 && "
            f"ROOT::VecOps::DeltaR(Muon_eta[ROOT::VecOps::ArgMax(Muon_pt)], "
            f"Muon_phi[ROOT::VecOps::ArgMax(Muon_pt)], "
            f"Tau_eta[ROOT::VecOps::ArgMax(Tau_pt)], "
            f"Tau_phi[ROOT::VecOps::ArgMax(Tau_pt)]) > {delta_r_min} && "
            f"{jet_cut}"
        )
    elif channel == "tt":
        return (
            f"nTau>=2 && ROOT::VecOps::Argsort(Tau_pt, std::greater<float>()).size()>1 && "
            "Tau_pt[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[0]]>35 && "
            "Tau_pt[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[1]]>35 && "
            "abs(Tau_eta[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[0]])<2.3 && "
            "abs(Tau_eta[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[1]])<2.3 && "
            f"ROOT::VecOps::DeltaR("
            "Tau_eta[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[0]], Tau_phi[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[0]], "
            "Tau_eta[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[1]], Tau_phi[ROOT::VecOps::Argsort(Tau_pt, std::greater<float>())[1]]"
            f") > {delta_r_min} && "
            f"{jet_cut}"
        )

    elif channel == "em":
        # leading Muon vs leading Electron
        return (
            f"nMuon>=1 && nElectron>=1 && "
            "ROOT::VecOps::Max(Muon_pt)>15 && ROOT::VecOps::Max(Electron_pt)>15 && "
            "abs(Muon_eta[ROOT::VecOps::ArgMax(Muon_pt)])<2.4 && "
            "abs(Electron_eta[ROOT::VecOps::ArgMax(Electron_pt)])<2.4 && "
            f"ROOT::VecOps::DeltaR(Muon_eta[ROOT::VecOps::ArgMax(Muon_pt)], "
            f"Muon_phi[ROOT::VecOps::ArgMax(Muon_pt)], "
            f"Electron_eta[ROOT::VecOps::ArgMax(Electron_pt)], "
            f"Electron_phi[ROOT::VecOps::ArgMax(Electron_pt)]) > {delta_r_min} && "
            f"{jet_cut}"
        )
    elif channel == "None":
        return f"1 && {jet_cut}"  # always true but加jet cut
    else:
        raise ValueError(f"Unknown channel: {channel}")






# -------------------
def process_files(files, era="2022preEE", channel="et"):
    import tqdm


    btag_threshold = get_btag_threshold(era)
    print(f"=== Processing era: {era} ===")
    print(f"Using btag_threshold = {btag_threshold}")
    print(f"Channel: {channel}")

    # ---- 创建 RDataFrame（直接传入多个文件） ----
    print("Reading ROOT files...")
    df = ROOT.RDataFrame("Events", files)
    df = df.Define("Jet_hadronFlavour_int", "std::vector<int>(Jet_hadronFlavour.begin(), Jet_hadronFlavour.end())")

    # ---- channel + jet cut ----
    df = df.Filter(check_channel_cut_expr(channel))

    # ---- 初始化 TH3F ----
    n_pt = len(pt_bins) - 1
    n_eta = len(eta_bins) - 1
    n_flav = len(flav_bins)

    hist3D = ROOT.TH3F("btag_eff", "b-tagging efficiency",
                       n_pt, pt_bins,
                       n_eta, eta_bins,
                       len(flav_bins_edges)-1, flav_bins_edges)

    hist2D_dict = {}
    flavor_names = {0:"light", 4:"cjet", 5:"bjet"}
    for k, flav in enumerate(flav_bins):
        name = f"btag_eff_{flavor_names[flav]}"
        hist2D_dict[flav] = ROOT.TH2F(name, f"b-tagging efficiency ({flavor_names[flav]})",
                                      n_pt, pt_bins, n_eta, eta_bins)

    # ---- 初始化计数数组 ----
    total = np.zeros((n_pt, n_eta, n_flav), dtype=int)
    btagged = np.zeros((n_pt, n_eta, n_flav), dtype=int)

    # ---- 分块读取 AsNumpy 并累加 total/btagged ----
    print("Processing events in chunks...")
    total_events_after_filter = 0
    chunk_size = 20000
    start = 0
    pbar = tqdm.tqdm(desc="Chunks", unit="events", mininterval=5)

    while True:
        df_chunk = df.Range(start, start + chunk_size)
        it_chunk = df_chunk.AsNumpy(columns=["Jet_pt", "Jet_eta", "Jet_hadronFlavour_int", "Jet_btagPNetB"])
        n_chunk_events = len(it_chunk["Jet_pt"])
        if n_chunk_events == 0:
            break

        for pts, etas, flavs, btags in zip(it_chunk["Jet_pt"], it_chunk["Jet_eta"],
                                        it_chunk["Jet_hadronFlavour_int"],
                                        it_chunk["Jet_btagPNetB"]):
            for pt, eta, flav, btag in zip(pts, etas, flavs, btags):
                if pt <= 20 or abs(eta) >= 2.5:
                    continue
                if flav not in flav_bins:
                    continue
                pt_idx = np.searchsorted(pt_bins, pt, side="right") - 1
                pt_idx = min(pt_idx, n_pt-1)
                eta_idx = 0
                flav_idx = flav_bins.index(flav)
                total[pt_idx, eta_idx, flav_idx] += 1
                if btag > btag_threshold:
                    btagged[pt_idx, eta_idx, flav_idx] += 1

        total_events_after_filter += n_chunk_events
        start += chunk_size
        pbar.update(n_chunk_events)

    pbar.close()
    print(f"Total events after Filter = {total_events_after_filter}")
    print("Finished processing events.")


    # ---- 计算效率并填充 TH3F/TH2F ----
    with np.errstate(divide='ignore', invalid='ignore'):
        eff = np.true_divide(btagged, total)
        eff[total==0] = 0.0

    for i in range(n_pt):
        for j in range(n_eta):
            for k, flav in enumerate(flav_bins):
                hist3D.SetBinContent(i+1, j+1, k+1, eff[i,j,k])
                hist2D_dict[flav].SetBinContent(i+1, j+1, eff[i,j,k])
                ROOT.gStyle.SetPaintTextFormat("f")
                hist2D_dict[flav].SetOption("COLZ")
                hist2D_dict[flav].SetStats(0)
                hist3D.SetOption("COLZ")
                hist3D.SetStats(0)

    return hist3D, hist2D_dict, total, btagged







# -------------------
def save_efficiency_histograms(hist3D, hist2D_dict, era, channel, out_dir="/eos/home-l/leyan/Htautau/Btagging-fixWP-Unc/ROOT_btagging_eff"):
    import os
    os.makedirs(out_dir, exist_ok=True)  # 确保输出目录存在
    out_fname = f"{out_dir}/btag_eff_dxc_{era}_{channel}_with_DeltaR.root"
    f_out = ROOT.TFile(out_fname, "RECREATE")
    hist3D.Write()
    for h2 in hist2D_dict.values():
        h2.Write()
    f_out.Close()
    print(f"\nSaved TH3F and TH2F per flavor to {out_fname}")

# -------------------
def main():
    if len(sys.argv) < 4:
        print("Usage: python b-eff-rdf.py <root_file1> [<root_file2> ...] <era> <channel>")
        sys.exit(1)

    files = sys.argv[1:-2]
    era = sys.argv[-2]
    channel = sys.argv[-1]

    hist3D, hist2D_dict, total, btagged = process_files(files, era, channel)
    save_efficiency_histograms(hist3D, hist2D_dict, era, channel)

    # ---- 原打印逻辑 ----
    n_pt = len(pt_bins)-1
    for i in range(n_pt):
        for k, flav in enumerate(flav_bins):
            n_tot = total[i,0,k]
            n_btag = btagged[i,0,k]
            eff = n_btag / n_tot if n_tot > 0 else 0.0
            print(f"pT bin [{pt_bins[i]:.0f},{pt_bins[i+1]:.0f}], flav={flav} : "
                  f"N_total={n_tot}, N_btagged={n_btag}, eff={eff:.3f}")

    tot_all = total.sum()
    pass_all = btagged.sum()
    print("tot_all",tot_all)
    print("pass_all",pass_all)
    overall_rate = pass_all / tot_all if tot_all > 0 else 0.0

    eff_by_flav = {}
    weight_by_flav = {}
    for k, flav in enumerate(flav_bins):
        tot_f = total[:, 0, k].sum()

        pass_f = btagged[:, 0, k].sum()
        print("flav:",flav)
        print("tot_f:",tot_f)
        print("pass_f:",pass_f)
        eff_f = pass_f / tot_f if tot_f > 0 else 0.0
        w_f = tot_f / tot_all if tot_all > 0 else 0.0
        eff_by_flav[flav] = eff_f
        weight_by_flav[flav] = w_f

    sum_eff = sum(eff_by_flav.values())
    weighted_avg = sum(eff_by_flav[f]*weight_by_flav[f] for f in flav_bins)

    print("\n=== Global checks ===")
    print(f"Overall tagged fraction (all jets): {overall_rate:.6f} = sum(N_pass)/sum(N_total)")
    for flav in flav_bins:
        print(f"flav={flav}: eff={eff_by_flav[flav]:.6f}, weight={weight_by_flav[flav]:.6f}")
    print(f"Sum of per-flavor efficiencies (should NOT be 1): {sum_eff:.6f}")
    print(f"Weighted average of efficiencies (should equal overall): {weighted_avg:.6f}")
# -------------------
if __name__ == "__main__":
    main()
