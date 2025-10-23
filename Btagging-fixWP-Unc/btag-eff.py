#!/usr/bin/env python3
import sys
import ROOT
import numpy as np
from tqdm import tqdm

ROOT.EnableImplicitMT()  # 启用多线程

# -------------------
# 配置 binning
pt_bins = np.array([20, 30,40,50, 70,90, 100,120, 140, 160, 180, 200], dtype=float)
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


def check_channel_cut(channel, event):
    # 返回 (leading pt, 对应 eta)，若列表为空则返回 0
    def leading_pt_eta(pt_list, eta_list):
        if len(pt_list) == 0:
            return 0., 0.
        idx = np.argmax(pt_list)
        return pt_list[idx], eta_list[idx]

    # ---- et channel ----
    if channel == "et":
        lead_e_pt, lead_e_eta = leading_pt_eta(event["Electron_pt"], event["Electron_eta"])
        lead_tau_pt, lead_tau_eta = leading_pt_eta(event["Tau_pt"], event["Tau_eta"])
        return (event["nElectron"] >= 1 and event["nTau"] >= 1 and
                lead_e_pt > 25 and lead_tau_pt > 25 and
                abs(lead_e_eta) < 2.1 and abs(lead_tau_eta) < 2.3)

    # ---- mt channel ----
    elif channel == "mt":
        lead_mu_pt, lead_mu_eta = leading_pt_eta(event["Muon_pt"], event["Muon_eta"])
        lead_tau_pt, lead_tau_eta = leading_pt_eta(event["Tau_pt"], event["Tau_eta"])
        return (event["nMuon"] >= 1 and event["nTau"] >= 1 and
                lead_mu_pt > 23 and lead_tau_pt > 30 and
                abs(lead_mu_eta) < 2.1 and abs(lead_tau_eta) < 2.3)

    # ---- tt channel ----
    elif channel == "tt":
        lead_tau_pt, lead_tau_eta = leading_pt_eta(event["Tau_pt"], event["Tau_eta"])
        return (event["nTau"] >= 2 and lead_tau_pt > 35 and abs(lead_tau_eta) < 2.3)

    # ---- em channel ----
    elif channel == "em":
        lead_mu_pt, lead_mu_eta = leading_pt_eta(event["Muon_pt"], event["Muon_eta"])
        lead_e_pt, lead_e_eta = leading_pt_eta(event["Electron_pt"], event["Electron_eta"])
        return (event["nMuon"] >= 1 and event["nElectron"] >= 1 and
                lead_mu_pt > 15 and lead_e_pt > 15 and
                abs(lead_mu_eta) < 2.4 and abs(lead_e_eta) < 2.4)
    elif channel == "None":
        return True


# -------------------
def process_files(files, era="2022preEE", channel="et"):
    btag_threshold = get_btag_threshold(era)
    print(f"=== Processing era: {era} ===")
    print(f"Using btag_threshold = {btag_threshold}")
    print(f"Channel: {channel}")
    

    arrays_list = []
    # 用进度条显示读取文件进度
    for f in tqdm(files, desc="Reading ROOT files"):
        df = ROOT.RDataFrame("Events", f)
        df = df.Define("Jet_hadronFlavour_int", "std::vector<int>(Jet_hadronFlavour.begin(), Jet_hadronFlavour.end())")
        # 基础列：Jet 信息总是需要的
        columns = ["Jet_pt", "Jet_eta", "Jet_hadronFlavour_int", "Jet_btagPNetB"]

        # 按 channel 增加所需列         # 如果 channel 不在列表里，则只读前四个 Jet 列
        if channel == "et":
            columns += ["nElectron", "Electron_pt", "Electron_eta",
                        "nTau", "Tau_pt", "Tau_eta"]
        elif channel == "mt":
            columns += ["nMuon", "Muon_pt", "Muon_eta",
                        "nTau", "Tau_pt", "Tau_eta"]
        elif channel == "tt":
            columns += ["nTau", "Tau_pt", "Tau_eta"]
        elif channel == "em":
            columns += ["nMuon", "Muon_pt", "Muon_eta",
                        "nElectron", "Electron_pt", "Electron_eta"]

        arr = df.AsNumpy(columns=columns)
        arrays_list.append(arr)

    # 合并多个文件的 numpy arrays
    arrays = {}
    for key in arrays_list[0].keys():
        arrays[key] = np.concatenate([arr[key] for arr in arrays_list])

    print("Unique hadronFlavour_int values:", np.unique(np.concatenate(arrays["Jet_hadronFlavour_int"])))
    n_events = len(arrays["Jet_pt"])
    print(f"Total events = {n_events}")

    # 初始化统计数组
    n_pt = len(pt_bins) - 1
    n_eta = len(eta_bins) - 1
    n_flav = len(flav_bins)
    total = np.zeros((n_pt, n_eta, n_flav), dtype=int)
    btagged = np.zeros((n_pt, n_eta, n_flav), dtype=int)

    # tqdm 进度条
    for i in tqdm(range(n_events), desc="Processing events"):
        event = {key: arrays[key][i] for key in arrays}
        channel_cut = check_channel_cut(channel, event)
        pts, etas, flavs, btags = event["Jet_pt"], event["Jet_eta"], event["Jet_hadronFlavour_int"], event["Jet_btagPNetB"]

        for pt, eta, flav, btag in zip(pts, etas, flavs, btags):
            bjets_cut = (pt > 20 and abs(eta) < 2.5)
            if not (bjets_cut and channel_cut):
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

    # 计算效率
    with np.errstate(divide='ignore', invalid='ignore'):
        eff = np.true_divide(btagged, total)
        eff[total==0] = 0.0

    # ---- 创建 TH3F ----
    hist3D = ROOT.TH3F("btag_eff", "b-tagging efficiency",
                       n_pt, pt_bins,
                       n_eta, eta_bins,
                       len(flav_bins_edges)-1, flav_bins_edges)
    for i in range(n_pt):
        for j in range(n_eta):
            for k, flav in enumerate(flav_bins):
                hist3D.SetBinContent(i+1, j+1, k+1, eff[i,j,k])
    hist3D.SetOption("COLZ")
    hist3D.SetStats(0)

    # ---- TH2F per flavor ----
    hist2D_dict = {}
    flavor_names = {0:"light", 4:"cjet", 5:"bjet"}
    for k, flav in enumerate(flav_bins):
        name = f"btag_eff_{flavor_names[flav]}"
        hist2D = ROOT.TH2F(name, f"b-tagging efficiency ({flavor_names[flav]})",
                           n_pt, pt_bins, n_eta, eta_bins)
        for i in range(n_pt):
            for j in range(n_eta):
                hist2D.SetBinContent(i+1, j+1, eff[i,j,k])
        ROOT.gStyle.SetPaintTextFormat("f")
        hist2D.SetOption("COLZ")
        hist2D.SetStats(0)
        hist2D_dict[flav] = hist2D

    return hist3D, hist2D_dict, total, btagged


# -------------------
def save_efficiency_histograms(hist3D, hist2D_dict, era, channel, out_dir="ROOT_btagging_eff"):
    import os
    os.makedirs(out_dir, exist_ok=True)  # 确保输出目录存在
    out_fname = f"{out_dir}/btag_eff_dxc_{era}_{channel}.root"
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
    # print("tot_all",tot_all)
    # print("pass_all",pass_all)
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
