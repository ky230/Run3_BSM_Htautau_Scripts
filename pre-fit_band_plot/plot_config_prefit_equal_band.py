#!/usr/bin/env python
# coding: utf-8
import os
import sys
import ROOT
import math
from array import array
from collections import defaultdict
from glob import glob

# ------------------------
# User Custom Configuration
# ------------------------

masses = [60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 
        120, 125, 130, 135, 140, 160, 180, 200, 250]



default_plot_vars = {
    #Mass: 5
    'mt_tot': ('mt_tot', ';m_{T}^{tot} [GeV];NEvents'),
    'm_vis': ('m_vis', '; m^{vis}[GeV];NEvents'),
    'mt_1': ('mt_1', ';m_{T}^{l_{1}}[GeV];NEvents'),
    'mt_2': ('mt_2', ';m_{T}^{l_{2}}[GeV];NEvents'),
    'Met': ('met', ';met[GeV];NEvents'),
     
    #Momentum: 3/4 缺 pt_vis
    'pt_1': ('pt_1', ';p_{T}^{l_{1}} ;NEvents'),
    'pt_2': ('pt_2', ';p_{T}^{l_{2}} ;NEvents'),
    'pt_tt': ('pt_tt', ';p_{T}^{#tau#tau} ;NEvents'),
    'pt_vis': ('pt_vis', ';p_#text{vis}^{#tau#tau} ;NEvents'),
    

    #Angle: 6
    'dphi_12': ('dphi_12', ';#Delta#phi(l_{1},l_{2});NEvents'),
    'deta_12': ('deta_12', ';#Delta#eta(l_{1},l_{2});NEvents'),
    'dphi_H1' : ('dphi_H1', ';#Delta#phi(#scale[0.8]{ditau},l_{1});NEvents'),
    'dphi_H2' : ('dphi_H2', ';#Delta#phi(#scale[0.8]{ditau},l_{2});NEvents'),
    'deltaR_ditaupair': ('deltaR_ditaupair', ';#DeltaR ;NEvents'),
    'metphi': ('metphi', ';#Delta#phi_{#scale[0.8]{MET}};NEvents'),

    #Advanced: 8/10 缺 Njets m_T^{\text{dileptonMET}
    'm_fastmtt': ('m_fastmtt', '; m^{#tau#tau};NEvents'),
    'pt_fastmtt': ('pt_fastmtt', ';p_{T}^{#tau#tau} ;NEvents'),
    'eta_fastmtt': ('eta_fastmtt', ';eta_{#tau#tau};NEvents'),
    'nbtag': ('nbtag', ';Nbtag;NEvents'),
    'kT': ('kT', ';kT;NEvents'),
    'antikT': ('antikT', ';antikT;NEvents'),
    'pt1_LT_to_ptH': ('pt1_LT_to_ptH', ';p_{T}^{l_{1}} / p_{T}^{#tau#tau};NEvents'),
    'pt2_LT_to_ptH': ('pt2_LT_to_ptH', ';p_{T}^{l_{2}} / p_{T}^{#tau#tau};NEvents'),

    'antikT': ('antikT', ';antikT;NEvents'),
    # 'Njets': ('Njets', ';kT;NEvents'),
    # 'mTdileptonMET' : ('mTdileptonMET',';m_{T}^{#scale[0.8]{dileptonMET}};NEvents')

    # 'pzetamissvis':('pzetamissvis', ';#D#zeta;NEvents'),
    

}

PNN_plot_vars =  {}

for m in masses:
    PNN_plot_vars[f'PNN_{m}'] = (f'PNN_{m}', f'; PNN_{m};NEvents')

######  default config


default_samples = {
    'Data': ['Data', ['data_obs'], 1],
    'Signal_bbH_1000': ['bbH-1000', ['bbH_signal_1000'], 1],
    'Signal_ggH_1000': ['ggH-1000', ['ggH_signal_1000'], 1],
    'Top': ['Top', ['ttbar'], 1],
    "DY-Jets-tt": ['DY-Jets-#tau#tau', ["Zto2L_tt"], 1],
    "DY-Jets-ll": ['DY-Jets-ll', ["Zto2L_ll"], 1],
    "other": ['Other', ["other"], 1],
    "fakes": ['Fakes', ["fakes"], 1],
    "diboson": ['Diboson', ["diboson"], 1],
}

default_stacking_order = ['other','diboson','fakes','DY-Jets-tt' ,'DY-Jets-ll' , 'Top',  ]

default_sample_colors = {
    'fakes': 901,
    'DY-Jets-ll': 814,
    'DY-Jets-tt': 865,
    "Top": 401,
    'diboson': 838,
    'other': 920,
    "200*bbH-100": 416,
    "200*ggH-100": 632,
    "bbH-1000": 416,
    "ggH-1000": 632,
}

default_regions = ["btag","nob"]


####### PNN-specific configurations

pnn_samples = {
    'Data': ['Data', ['data_obs'], 1],
    'Top': ['Top', ['ttbar'], 1],
    "DY-Jets-tt": ['DY-Jets-#tau#tau', ["Zto2L_tt"], 1],
    "DY-Jets-ll": ['DY-Jets-ll', ["Zto2L_ll"], 1],
    "other": ['Other', ["other"], 1],
    "fakes": ['Fakes', ["fakes"], 1],
    "diboson": ['Diboson', ["diboson"], 1],
}
for m in masses:
    pnn_samples[f'Signal_bbH_{m}'] = [f'200*bbH-{m}', [f'bbH_signal_{m}'], 200]
    pnn_samples[f'Signal_ggH_{m}'] = [f'200*ggH-{m}', [f'ggH_signal_{m}'], 200]



pnn_stacking_order = [ 'Top','other' , 'diboson','fakes','DY-Jets-tt' ,'DY-Jets-ll' ,  ]

pnn_sample_colors = {
    'fakes': 901,
    'DY-Jets-ll': 814,
    'DY-Jets-tt': 865,
    "Top": 401,
    'diboson': 838,
    'other': 920,
    # f"200*bbH-{mass}": 416,
    # f"200*ggH-{mass}": 632,
}
for m in masses:
    pnn_sample_colors[f'200*bbH-{m}'] = 416
    pnn_sample_colors[f'200*ggH-{m}'] = 632

pnn_regions = ["btag","nob1","nob2","nob3","nob4"]

# Initialize with default values
plot_vars=default_plot_vars
samples = default_samples
stacking_order = default_stacking_order
sample_colors = default_sample_colors
regions = default_regions


# ------------------------
# Core Functions
# ------------------------
def get_hist(f, region, hist_name):
    if not f.GetDirectory(region):
        print(f"[WARNING] Region '{region}' not found in file.")
        return None
    hist = f.Get(f"{region}/{hist_name}")
    if not hist:
        print(f"[WARNING] Histogram '{hist_name}' not found in region '{region}'")
        return None
    return hist.Clone()

#new function 
def rebin_hist_to_same_bins(original_hist):
    """
    将输入的直方图转换为0到1范围内的等宽binning,保持与原直方图相同的bin数量
    并按顺序将原始数据填入新直方图
    
    参数:
        original_hist: 输入的ROOT.TH1直方图对象
        
    返回:
        新的ROOT.TH1直方图对象,具有0到1的等宽binning和相同的bin数量
    """
    # 获取原始直方图的bin数量
    original_num_bins = original_hist.GetNbinsX()
    
    # 创建新的直方图,范围从0到1,保持与原直方图相同的bin数量
    new_hist = ROOT.TH1F(
        f"rebinned_{original_hist.GetName()}",
        f"Rebinned {original_hist.GetTitle()};x;Entries",
        original_num_bins,  # 与原始直方图相同的bin数量
        0.0,                # x最小值
        1.0                 # x最大值
    )
    
    # 按顺序遍历原始直方图的每个bin,并填入新直方图的对应bin
    for bin_idx in range(1, original_num_bins + 1):  # ROOT的bin索引从1开始
        # 获取原始bin的内容和误差
        bin_content = original_hist.GetBinContent(bin_idx)
        bin_error = original_hist.GetBinError(bin_idx)
        
        # 直接将内容填充到新直方图的对应序号bin中
        new_hist.SetBinContent(bin_idx, bin_content)
        new_hist.SetBinError(bin_idx, bin_error)
    
    # 处理overflow和underflow bins（如果需要）
    new_hist.SetBinContent(0, original_hist.GetBinContent(0))
    new_hist.SetBinError(0, original_hist.GetBinError(0))
    new_hist.SetBinContent(original_num_bins + 1, original_hist.GetBinContent(original_num_bins + 1))
    new_hist.SetBinError(original_num_bins + 1, original_hist.GetBinError(original_num_bins + 1))
    
    return new_hist

def get_syst_histos(f, region, process, n_bins, PNN = False):
    
    syst_blacklist = [
        "fitUnc", 
        "jesUncTotal"
        # "btagUncbc_correlated_",     
        # "btagUncbc_uncorrelated_",
        # "btagUnclight_correlated_",
        # "btagUnclight_uncorrelated_"
    ]
    
    syst_up = defaultdict(lambda: [0]*n_bins)
    syst_down = defaultdict(lambda: [0]*n_bins)
    keys = [k.GetName() for k in f.Get(region).GetListOfKeys()]
    print(f"\n[DEBUG] Getting systematics for process: {process} in region: {region}")
    
    processed_systs = set()
    syst_pairs_count = 0
    syst_missing_pairs = []
    valid_syst_pairs = []
    skipped_blacklist = []

    for k in sorted(keys): 
        if not k.startswith(process + "__"):
            continue
            
        syst_name = k.replace(process + "__", "")
        

        base = syst_name[:-2] if syst_name.endswith("Up") else syst_name[:-4]
        if base in syst_blacklist:
            if base not in skipped_blacklist:
                print(f"[INFO] Skipping blacklisted systematic: {base}")
                skipped_blacklist.append(base)
            continue
            

        is_up = syst_name.endswith("Up")
        is_down = syst_name.endswith("Down")
        
        if not (is_up or is_down):
            print(f"[WARNING] {k} has no Up/Down suffix")
            continue
            
        base = syst_name[:-2] if is_up else syst_name[:-4]  

        if base in processed_systs:
            continue
            

        counterpart = f"{process}__{base}Down" if is_up else f"{process}__{base}Up"
        

        if counterpart not in keys:
            print(f"[WARNING] {k} missing counterpart -> {counterpart}")
            syst_missing_pairs.append(base)
            continue
            

        h_up = f.Get(f"{region}/{process}__{base}Up")
        h_down = f.Get(f"{region}/{process}__{base}Down")
        nominal = get_hist(f, region, process)

        if PNN:
            h_up = rebin_hist_to_same_bins(h_up)
            h_down = rebin_hist_to_same_bins(h_down)
            nominal = rebin_hist_to_same_bins(nominal)       
        if not h_up or not h_down or not nominal:
            print(f"[WARNING] Missing histograms for pair: {base}Up/Down")
            continue
            

        processed_systs.add(base)
        syst_pairs_count += 1
        valid_syst_pairs.append(base)
        

        for i in range(1, n_bins+1):
            delta_up = abs(h_up.GetBinContent(i) - nominal.GetBinContent(i))
            delta_down = abs(h_down.GetBinContent(i) - nominal.GetBinContent(i))
            delta = max(delta_up, delta_down)
            syst_up[base][i-1] = delta**2
            syst_down[base][i-1] = delta**2
    

    print("\n[SYST REPORT]")
    print(f"Total keys scanned: {len(keys)}")
    print(f"Valid systematics pairs: {syst_pairs_count}")
    print(f"Skipped blacklisted systematics: {len(skipped_blacklist)}")
    
    if skipped_blacklist:
        print("\nBlacklisted systematics skipped:")
        for i, syst in enumerate(sorted(skipped_blacklist), 1):
            print(f"  {i:3d}. {syst}")
    
    print("\nList of valid systematics:")
    for i, syst in enumerate(sorted(valid_syst_pairs), 1):
        print(f"  {i:3d}. {syst}")
    
    if syst_missing_pairs:
        print(f"\nMissing counterparts ({len(syst_missing_pairs)}):")
        for i, syst in enumerate(sorted(syst_missing_pairs), 1):
            print(f"  {i:3d}. {syst}")
    else:
        print("\nAll systematics have complete Up/Down pairs")
    
    print(f"\n[INFO] Process: {process} -> Valid pairs: {syst_pairs_count}")
    print(f"[INFO] Missing counterparts: {len(syst_missing_pairs)}")
    print(f"[INFO] Blacklisted systematics skipped: {len(skipped_blacklist)}")

    # ---- 新增：打印前五大的系统误差来源 ----
    def top_systematics(syst_dict, n=5):
        totals = {k: sum(v) for k, v in syst_dict.items()}  # 每个系统的总 Δ²
        sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_totals[:n]

    top_up = top_systematics(syst_up)
    top_down = top_systematics(syst_down)

    print("\n[TOP SYSTEMATIC UNCERTAINTIES]")

    print("Top 5 syst_up contributors:")
    for i, (name, val) in enumerate(top_up, 1):
        print(f"  {i:2d}. {name:<30} total Δ² = {val:.6f}")
        print(f"      {name} = {syst_up[name]}")

    print("Top 5 syst_down contributors:")
    for i, (name, val) in enumerate(top_down, 1):
        print(f"  {i:2d}. {name:<30} total Δ² = {val:.6f}")
        print(f"      {name} = {syst_down[name]}")


    
    return syst_up, syst_down

def total_uncertainty(f, region, background_processes, n_bins, statonly=False, PNN=False):
    tot_up = [0.]*n_bins
    tot_down = [0.]*n_bins
    print(f"[INFO] Total background processes to compute uncertainty: {len(background_processes)}")

    for proc in background_processes:
        h_nom = get_hist(f, region, proc)
        if PNN:
            h_nom = rebin_hist_to_same_bins(h_nom)
        if not h_nom:
            print(f"[WARNING] Cannot get nominal hist for {proc}")
            continue
        if proc != "fakes":
           stat2 = [max(h_nom.GetBinError(i+1)**2, 0.0) for i in range(n_bins)]
        else :
           stat2 = [0 for i in range(n_bins)]
           print("fakes")
           #stat2 = [max(h_nom.GetBinError(i+1)**2, 0.0) for i in range(n_bins)]
        print("\n")

        print(f"This is {proc} in {region}: ")
        print("stat^2:",stat2)
        syst_up2, syst_down2 = get_syst_histos(f, region, proc, n_bins, PNN) #这一步是得到某个过程,所有的系统误差

        syst_factor = 0 if statonly else 1  # Multiply syst terms by this factor
        print(f"[DEBUG] proc={proc}, statonly={statonly}, syst_factor={syst_factor}")

        for i in range(n_bins):
            syst_up_sum = sum([v[i] for v in syst_up2.values()])
            syst_down_sum = sum([v[i] for v in syst_down2.values()])
            
            print(f"n_bins {i}")
            

            # 开始累积总误差, 做法是把这一个process 的系统误差 和 统计误差 加到 tot_up
            tot_up[i] += (syst_up_sum *  syst_factor + stat2[i])
            tot_down[i] += (syst_down_sum *  syst_factor + stat2[i])


            print(f"stat2[i] : {stat2[i]} ,   syst_up2[i]: {syst_up_sum } ,  tot_up2[i]: {tot_up[i] } ")
            print(f"stat2[i] : {stat2[i]} ,   syst_down2[i]: {syst_down_sum } ,  tot_down2[i]: {tot_down[i] } ")
        
        
        print("\n")     
        print("tot_up2:",tot_up)
        print("tot_down2:",tot_down)
        print("\n")
    return [math.sqrt(u) for u in tot_up], [math.sqrt(d) for d in tot_down]

def draw_plot(file_path, output_dir, region, var_key='m_fastmtt', log_scale=False,statonly=False, xy_log_scale=False,PNN=False, blind=False):
    var, title = plot_vars[var_key]
    print(f"\n[INFO] Processing file: {file_path}")
    print(f"[INFO] Region: {region}")
    print(f"[INFO] Scale: {'xy_Log' if xy_log_scale else 'Log' if log_scale else 'Lin'}")  # 完整的三元表达式 
    
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        print(f"[ERROR] Failed to open ROOT file: {file_path}")
        return

    data_hist = get_hist(f, region, samples['Data'][1][0])
    if PNN:
        data_hist = rebin_hist_to_same_bins(data_hist)
    
    if not data_hist:
        print(f"[ERROR] Data histogram missing: {region}/{samples['Data'][1][0]}")
        return

    nbins = data_hist.GetNbinsX()
    xmin = data_hist.GetBinLowEdge(1)
    xmax = data_hist.GetBinLowEdge(nbins + 1)
    if xy_log_scale:
        data_hist.GetXaxis().SetRangeUser(50, 5000)

    c = ROOT.TCanvas(f"c_{region}_{'xylog' if xy_log_scale else 'log' if log_scale else 'lin'}","", 900, 900)
    pad1 = ROOT.TPad(f"pad1","{region}",0,0.25,1,1)
    pad2 = ROOT.TPad("pad2","",0,0,1,0.25)
    pad1.SetBottomMargin(0.02)
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.35)
    pad1.Draw()
    pad2.Draw()
    check = array('d', [data_hist.GetBinLowEdge(i+1) for i in range(nbins)] + [xmax])
    print(check, "hi")
    stack = ROOT.THStack()
    total_mc = data_hist.Clone()
    for i in range(1, nbins+1):
        total_mc.SetBinContent(i, 0)
        total_mc.SetBinError(i, 0)
    total_mc.SetName("total_mc")
    total_mc.SetTitle("")
    print("data_hist first bin, ", data_hist.GetBinContent(0), data_hist.GetBinContent(1) )
    #total_mc = ROOT.TH1F("total_mc", "", nbins, array('d', [data_hist.GetBinLowEdge(i+1) for i in range(nbins)] + [xmax]))
    bkg_histos = []


    for sname in stacking_order:
        print(f"[INFO] Processing stack: {sname}")
        h_total = total_mc.Clone(f"bkg_{sname}")
        h_total.Reset()
        for sample in samples[sname][1]:
            h = get_hist(f, region, sample)
            if PNN:
                h = rebin_hist_to_same_bins(h)
            if not h:
                print(f"[WARNING] Missing histogram: {region}/{sample}")
                continue
            print(f"   [OK] Loaded hist: {region}/{sample}")
            h.Scale(samples[sname][2])
            h_total.Add(h)
        h_total.SetFillColor(sample_colors[sname])
        stack.Add(h_total)
        bkg_histos.append(h_total)
        total_mc.Add(h_total)
    print("Background processes being processed:", [samples[x][1][0] for x in stacking_order])
    up_errs, down_errs = total_uncertainty(f, region, [samples[x][1][0] for x in stacking_order], nbins, statonly=statonly, PNN=PNN)

    print("\n")
    print(f"[INFO] Finishing processes of all Background of {var_key}_{'xy_Log' if xy_log_scale else 'Log' if log_scale else 'Lin'}.png in {region}  region ")
    print("up_errs:",up_errs)
    print("down_errs:",down_errs)

    band = total_mc.Clone("err_band")
    for i in range(1, nbins+1):
        max_err = max(up_errs[i-1], down_errs[i-1])  # 取上/下误差中的最大值
        print(f"bin {i} of {var} in {region} :")
        print("max_err:",max_err)
        print("bin content:",band.GetBinContent(i))
        if band.GetBinContent(i) != 0:
         print(f"err_band:{max_err/band.GetBinContent(i)}")
        band.SetBinError(i, 1 * max_err)
    band.SetFillColor(922)
    band.SetFillStyle(3001)

    print("\n[DEBUG] Background process yields:")
    for i, sname in enumerate(stacking_order):
        h = bkg_histos[i]
        print(f"  {sname:10s}: integral = {h.Integral():.4f}, max_bin = {h.GetMaximum():.4f}")


    ##### draw pad1 : stack plots
    pad1.cd()
    if log_scale:
      pad1.SetLogy()
    if xy_log_scale:  
      pad1.SetLogx()
      pad1.SetLogy()

######## draw 

    stack.Draw("hist")
    set_top_plot_general_style(stack,log_scale,xy_log_scale)
    band.Draw("e2 same")
    total_mc.Draw("same hist")


    # 将 data_hist 转换为 TGraph（without error）
    n_bins = data_hist.GetNbinsX()
    g_data = ROOT.TGraph()
    point_index = 0  

    for i in range(n_bins):
        x = data_hist.GetBinCenter(i + 1)
        y = data_hist.GetBinContent(i + 1)

        if y == 0:
            continue  # 跳过内容为 0 的点
        if blind:
                if "mt_tot" in var_key:
                    skip = 7
                else:
                    skip = 5
                if i >= skip:
                    continue
        g_data.SetPoint(point_index, x, y)
        point_index += 1



    g_data.SetMarkerStyle(20)
    g_data.SetMarkerSize(1.7)
    g_data.SetMarkerColor(ROOT.kBlack)
    g_data.SetLineWidth(0)


    g_data.Draw("P same")


    # Adjust Y-axis range
    current_max = stack.GetMaximum()



    if xy_log_scale:
            min_non_zero = min([h.GetMinimum(0) for h in [data_hist, total_mc] if h.GetMinimum(0) > 0])
            stack.SetMinimum(min_non_zero * 0.01)
            stack.SetMaximum(current_max * 100)
            stack.GetXaxis().SetLabelSize(0)
    elif log_scale:

        min_non_zero = min([h.GetMinimum(0) for h in [data_hist, total_mc] if h.GetMinimum(0) > 0])
        stack.SetMinimum(min_non_zero * 0.01)
        stack.SetMaximum(current_max * 100)
        stack.GetXaxis().SetLabelSize(0)
    else:
        stack.GetYaxis().SetNoExponent(False)         
        stack.GetYaxis().SetMoreLogLabels(False)
        ROOT.TGaxis.SetMaxDigits(3)                 
        current_max = stack.GetMaximum()
        stack.SetMaximum(current_max * 1.74)



    if PNN:
        signal_hists = []
        for m in masses:
            for s in [f'Signal_bbH_{m}', f'Signal_ggH_{m}']:
                print(f"[INFO] Loading signal: {s}")
                sig_hist = get_hist(f, region, samples[s][1][0])
                print(samples[s][1][0], "check signal")
                print(sig_hist)
                if sig_hist:
                    sig_hist = rebin_hist_to_same_bins(sig_hist)
                else:
                    continue
                if sig_hist:
                    print(f"   [OK] Loaded Signal: {samples[s][1][0]}")
                    sig_hist.Scale(samples[s][2])
                    sig_hist.SetLineColor(sample_colors[samples[s][0]])
                    sig_hist.SetLineWidth(2)
                    sig_hist.SetLineStyle(1)
                    sig_hist.SetFillStyle(0)
                    sig_hist.Draw("hist same")
                    signal_hists.append(sig_hist)

    if blind and not PNN:  ## basically plotting for mt_tot
        print("hi, i am here")
        signal_hists = []
        for m in [1000]:
            for s in [f'Signal_bbH_{m}', f'Signal_ggH_{m}']:
                print(f"[INFO] Loading signal: {s}")
                sig_hist = get_hist(f, region, samples[s][1][0])
                print(samples[s][1][0], "check signal")
                print(sig_hist)
                if sig_hist:
                    print(f"   [OK] Loaded Signal: {samples[s][1][0]}")
                    sig_hist.Scale(samples[s][2])
                    sig_hist.SetLineColor(sample_colors[samples[s][0]])
                    sig_hist.SetLineWidth(2)
                    sig_hist.SetLineStyle(1)
                    sig_hist.SetFillStyle(0)
                    sig_hist.Draw(" same hist ")
                    signal_hists.append(sig_hist)
                    for i in range(nbins):
                        print(sig_hist.GetBinContent(i))
                    print("i have drawn signal")


    ###### adjust
    stack.GetXaxis().SetTitle(title.split(";")[1])
    stack.GetYaxis().SetTitle(title.split(";")[2])
    title_text = ROOT.TLatex()
    title_text.SetNDC(True)  
    title_text.SetTextFont(42)  
    title_text.SetTextSize(0.045)
    title_text.SetTextAlign(22)  
    

    title_text.DrawLatex(0.49, 0.96, f"{region}")

    # 原 legend 坐标
    x1, y1 = 0.7, 0.6
    x2, y2 = 0.83, 0.83

    # 计算中心和新宽高
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    scale = 1.5
    w = (x2 - x1) * scale
    h = (y2 - y1) * scale

    # 新坐标
    x1_new = cx - w / 2.0
    x2_new = cx + w / 2.0
    y1_new = cy - h / 2.0
    y2_new = cy + h / 2.0

    # 放大后的 legend
    legend = ROOT.TLegend(x1_new, y1_new, x2_new, y2_new)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    legend.AddEntry(g_data, "Data", "p")

    band_for_legend = band.Clone("band_for_legend")
    band_for_legend.SetLineColor(922)
    band_for_legend.SetFillColor(922)
    band_for_legend.SetFillStyle(3001)
    if  not statonly :
     legend.AddEntry(band_for_legend, "Bkg. Total. Unc", "f")
    else:
     legend.AddEntry(band_for_legend, "Bkg. Stat. Unc", "f")   

    for s in stacking_order[::-1]:
        legend.AddEntry(bkg_histos[stacking_order.index(s)], samples[s][0], "f")
    if PNN:        
        for sig_hist in signal_hists:
            for s_key, s_val in samples.items():
                if s_val[1][0] in sig_hist.GetName():
                    legend.AddEntry(sig_hist, s_val[0], "l")
                    break
    legend.Draw()

    if blind and not PNN:        
        for sig_hist in signal_hists:
            for s_key, s_val in samples.items():
                if s_val[1][0] in sig_hist.GetName():
                    legend.AddEntry(sig_hist, s_val[0], "l")
                    break
    legend.Draw()


    #### draw pad2
    pad2.Clear()


    pad2.cd()
    if xy_log_scale:  
      pad2.SetLogx()
 
##### TGraph method



    n_bins = data_hist.GetNbinsX()


    x_vals, y_vals = [], []
    x_errs, y_errs_low, y_errs_high = [], [], []

    for i in range(1, n_bins + 1):
        data_val = data_hist.GetBinContent(i)
        mc_val = total_mc.GetBinContent(i)

        print(f"data error bar bin{i-1} in {region} region:")

        if blind:
            if "mt_tot" in var_key:
                skip = 8
            else:
                skip = 6
            if i >= skip:
                continue


        if mc_val <= 0:
            continue  
        if data_val <= 0:
            continue  


        x = data_hist.GetBinCenter(i)
        ex = 0
        ratio_val = (data_val - mc_val) / mc_val
        err = 1. / math.sqrt(data_val)  
        print("y_err:",err)

        x_vals.append(x)
        y_vals.append(ratio_val)
        x_errs.append(ex*0)
        y_errs_low.append(err)
        y_errs_high.append(err)

    # 转为 array
    g_ratio = ROOT.TGraphAsymmErrors(
        len(x_vals),
        array('d', x_vals),
        array('d', y_vals),
        array('d', x_errs), array('d', x_errs),
        array('d', y_errs_low), array('d', y_errs_high)
    )

    # 样式设置
    g_ratio.GetXaxis().SetTitle(title.split(";")[1])

    if xy_log_scale:
      g_ratio.GetXaxis().SetLimits(data_hist.GetBinLowEdge(2), data_hist.GetXaxis().GetXmax())   ## only for 
    else:
      g_ratio.GetXaxis().SetLimits(data_hist.GetXaxis().GetXmin(), data_hist.GetXaxis().GetXmax())  
   
    set_bottom_plot_general_style(g_ratio)
    ROOT.gStyle.SetEndErrorSize(0)
    g_ratio.Draw("AP")  




    # 画 y=±0.2 两条虚线
    line_plus = ROOT.TLine(g_ratio.GetXaxis().GetXmin(), 0.2, g_ratio.GetXaxis().GetXmax(), 0.2)
    line_minus = ROOT.TLine(g_ratio.GetXaxis().GetXmin(), -0.2, g_ratio.GetXaxis().GetXmax(), -0.2)
    for line in (line_plus, line_minus):
        line.SetLineColor(ROOT.kGray+2)
        line.SetLineStyle(2)
        line.SetLineWidth(1)
        line.Draw("same")


    err_band_ratio = band.Clone("band_ratio")
    for i in range(1, err_band_ratio.GetNbinsX()+1):
        print(f"bin {i}:")
        if total_mc.GetBinContent(i) > 0:
            err_band_ratio.SetBinContent(i, 0)
            err_band_ratio.SetBinError(i, band.GetBinError(i)/total_mc.GetBinContent(i))
            print("band.GetBinError(i):",band.GetBinError(i))
            print("total_mc.GetBinContent(i):",total_mc.GetBinContent(i))
            print("err_band_ratio.SetBinError:",err_band_ratio.GetBinError(i))
        else:
            err_band_ratio.SetBinContent(i, 0)
            err_band_ratio.SetBinError(i, 0)
            print("band.GetBinError(i):",band.GetBinError(i))
            print("total_mc.GetBinContent(i):",total_mc.GetBinContent(i))
            print("err_band_ratio.SetBinError:",err_band_ratio.GetBinError(i))

    set_bottom_plot_pull_style(err_band_ratio)


    err_band_ratio.Draw("e2 same")

    outdir = os.path.join(output_dir, region)
    os.makedirs(outdir, exist_ok=True)
    suffix = ""
    if xy_log_scale:
        suffix = "_xylog"
    elif log_scale:
        suffix = "_log"
    else:
        suffix = "_lin"
    
    out_pdf = os.path.join(outdir, f"{var}{suffix}.pdf")
    out_png = os.path.join(outdir, f"{var}{suffix}.png")
    c.SaveAs(out_pdf)
    c.SaveAs(out_png)
    print(f"[INFO] Saved plot: {out_pdf}")
    f.Close()

# ------------------------
# Utilities
# ------------------------
def set_top_plot_general_style(obj, log_scale=False, xy_log_scale=False):
    ROOT.gStyle.SetHistMinimumZero(True)
    ROOT.gStyle.SetPadTickY(1)
    if log_scale:
        # obj.GetYaxis().SetLabelSize(0.02)
        obj.GetYaxis().CenterTitle(True)
        obj.GetYaxis().SetNdivisions(505)
        obj.GetYaxis().SetTitleOffset(1.1)

        obj.GetXaxis().SetLabelSize(0)
        obj.GetXaxis().SetTitleSize(0)
        obj.GetYaxis().SetTitleSize(0.05)
        obj.GetYaxis().SetTitleOffset(1.01)
        obj.GetYaxis().CenterTitle(True)
        obj.GetYaxis().SetLabelSize(0.05)
    elif xy_log_scale:
        # 双对数坐标的特殊样式
        obj.GetYaxis().CenterTitle(True)
        obj.GetYaxis().SetLabelSize(0.05)
        obj.GetYaxis().SetNdivisions(505)
        obj.GetYaxis().SetTitleOffset(1.1)
        obj.GetYaxis().SetTitleSize(0.05)
        
        obj.GetXaxis().SetLabelSize(0.05)  
        obj.GetXaxis().SetTitleSize(0.05)


    else:
        obj.GetYaxis().SetLabelSize(0.2)
        obj.GetYaxis().SetNdivisions(505)
        obj.GetYaxis().SetTitleOffset(1.1)
        obj.GetYaxis().SetNoExponent(False)
        obj.GetYaxis().SetMoreLogLabels(True) 
        obj.GetXaxis().SetLabelSize(0)
        obj.GetXaxis().SetTitleSize(0)
        obj.GetYaxis().SetTitleSize(0.05)
        obj.GetYaxis().SetTitleOffset(1.02)
        obj.GetYaxis().CenterTitle(True)
        obj.GetYaxis().SetLabelSize(0.05)

def set_bottom_plot_general_style(obj):
    obj.GetYaxis().CenterTitle(True)
    obj.GetYaxis().SetTitleSize(0.13)
    obj.GetYaxis().SetTitleOffset(0.36)
    obj.GetYaxis().SetLabelSize(0.14)
    obj.GetYaxis().SetNdivisions(505)

    obj.GetXaxis().SetTitleSize(0.14)

    
    obj.GetXaxis().SetLabelSize(0.14)

    obj.GetXaxis().SetTitleOffset(1.02)
    obj.GetXaxis().SetLabelOffset(0.01)
    obj.GetXaxis().SetNdivisions(510)
    obj.GetXaxis().SetTickLength(obj.GetXaxis().GetTickLength() * 3.0)
    obj.GetXaxis().SetTitleFont(42)
    obj.GetXaxis().SetLabelFont(42)
    obj.GetYaxis().SetTitleFont(42)
    obj.GetYaxis().SetLabelFont(42)
    obj.SetTitle('')
    
    obj.SetLineColor(1)
    obj.SetLineWidth(1)
    obj.SetMarkerStyle(20)
    obj.SetMarkerSize(1.2)
    obj.SetMinimum(-0.3)
    obj.SetMaximum(0.3)
    obj.SetTitle("")
    obj.GetYaxis().SetTitle("#frac{Data-MC}{MC}")
    obj.SetStats(0)  


 


 

def set_bottom_plot_pull_style(obj):
    obj.SetFillColor(922)

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    # 首先处理可选参数
    statonly = False
    xy_log = False
    pnn_mode = False
    blind = False
    
    if "--statonly" in sys.argv:
        statonly = True
        sys.argv.remove("--statonly")  # 移除标志
    if "--PNN" in sys.argv:
        pnn_mode = True
        sys.argv.remove("--PNN")
        plot_vars=PNN_plot_vars
        samples = pnn_samples
        stacking_order = pnn_stacking_order
        sample_colors = pnn_sample_colors
        regions = pnn_regions
    if "--xy_log" in sys.argv:  
        xy_log = True
        sys.argv.remove("--xy_log")
    if "--blind" in sys.argv:  
        blind = True
        sys.argv.remove("--blind")      
        

    
    # 然后检查必需参数
    if len(sys.argv) != 3:
            print("Usage: python plot_config_prefit.py <file_dir> <output_dir> [--statonly] [--PNN]")
            sys.exit(1)

    file_dir = sys.argv[1]
    output_dir = sys.argv[2]
    ROOT.gROOT.SetBatch(True)

    for var in plot_vars:
        root_files = glob(f"{file_dir}/*{var}*.root")
        if not root_files:
            print(f"[WARNING] No ROOT files found for variable '{var}' in: {file_dir}")
            continue
        for fpath in root_files:
            for region in regions:
                # Draw linear scale plot
                draw_plot(fpath, output_dir, region, var, log_scale=False, statonly=statonly,xy_log_scale=xy_log,PNN=pnn_mode,blind=blind)
                # Draw log scale plot
                draw_plot(fpath, output_dir, region, var, log_scale=True, statonly=statonly,xy_log_scale=xy_log,PNN=pnn_mode,blind=blind)
