import os
import sys
import ROOT
import math
from array import array
from collections import defaultdict
from glob import glob

# masses = [60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 
#          120, 125, 130, 135, 140, 160, 180, 200, 250]

masses = [200]

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


    # 'pzetamissvis':('pzetamissvis', ';#D#zeta;NEvents'),
    
    #f'PNN_{mass}': (f'PNN_{mass}', f'; PNN_{mass};NEvents'),
    #'PNN_100': ('PNN_100', '; PNN_100;NEvents'),
    #'PNN_200': ('PNN_200', '; PNN_200;NEvents'),

}


PNN_plot_vars =  {}

for m in masses:
    PNN_plot_vars[f'PNN_{m}'] = (f'PNN_{m}', f'; PNN_{m};NEvents')

######  default config


default_samples = {
    'Data': ['Data', ['data_obs'], 1],


    'bbH-100': ['bbH-100', ['bbH_signal_100'], 1],
    'ggH-100': ['ggH-100', ['ggH_signal_100'], 1],
    'bbH-200': ['bbH-200', ['bbH_signal_200'], 1],
    'ggH-200': ['ggH-200', ['ggH_signal_200'], 1],


    'Top': ['Top', ['ttbar'], 1],
    "DY-Jets-tt": ['DY-Jets-#tau#tau', ["Zto2L_tt"], 1],
    "DY-Jets-ll": ['DY-Jets-ll', ["Zto2L_ll"], 1],
    "other": ['Other', ["other"], 1],
    "fakes": ['Fakes', ["fakes"], 1],
    "diboson": ['Diboson', ["diboson"], 1],
}


default_stacking_order = ['other','diboson','DY-Jets-tt' ,'DY-Jets-ll' , 'Top',  ]

PNN_stacking_order = ['bbH-200']


default_sample_colors = {
    'fakes': 901,
    'DY-Jets-ll': 814,
    'DY-Jets-tt': 865,
    "Top": 401,
    'diboson': 838,
    'other': 920,
    "bbH-100": 814,
    "ggH-100": 865,
    "bbH-200": 814,
    "ggH-200": 865,
}

default_regions = ["btag","nob"]
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



def draw_plot(file_path, output_dir, region, var_key='m_fastmtt', log_scale=False, PNN=False ):
    var, title = plot_vars[var_key]
    print(f"\n[INFO] Processing file: {file_path}")
    print(f"[INFO] Region: {region}")
    print(f"[INFO] Scale: {'Log' if log_scale else 'Lin'}")

    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        print(f"[ERROR] Failed to open ROOT file: {file_path}")
        return

    # ========== 基础设置 ==========
    first_sample = None
    for s in stacking_order:
        if s.lower() != "fakes":
            first_sample = samples[s][1][0]
            break
    if first_sample is None:
        print("[ERROR] No valid sample found in stacking_order")
        return

    test_hist = get_hist(f, region, first_sample)
    nbins = test_hist.GetNbinsX()
    xmin = test_hist.GetBinLowEdge(1)
    xmax = test_hist.GetBinLowEdge(nbins + 1)

    c = ROOT.TCanvas(f"c_{region}_{'log' if log_scale else 'lin'}", "", 900, 900)
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.25, 1, 1)
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.25)
    pad1.SetBottomMargin(0.02)
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.35)
    pad1.Draw()
    pad2.Draw()

    # ========== JES 定义 ==========
    jes_variations = {
        'nominal':       {'linestyle': 1, 'color': ROOT.kBlack,   'linewidth': 2},
        'jesUncBBEC1Up': {'linestyle': 2, 'color': ROOT.kRed+1,   'linewidth': 4},
        'jesUncBBEC1Down': {'linestyle': 2, 'color': ROOT.kBlue+1, 'linewidth': 4},
    }


    all_totals = {}
    stacks = {}

    for jes_var in jes_variations.keys():
        stack_var = ROOT.THStack(f"stack__{jes_var}", "")
        total_var = test_hist.Clone(f"total__{jes_var}")
        total_var.Reset()

        for sname in stacking_order:
            if sname.lower() == "fakes":
                continue

            h_total = test_hist.Clone(f"bkg__{sname}__{jes_var}")
            h_total.Reset()
            for sample in samples[sname][1]:
                if jes_var == 'nominal':
                    h = get_hist(f, region, sample)
                else:
                    h = get_hist(f, region, f"{sample}__{jes_var}")
                if not h:
                    continue
                h.Scale(samples[sname][2])
                h_total.Add(h)

            color = sample_colors[sname]
            h_total.SetLineColor(color)
            h_total.SetLineWidth(1)
            h_total.SetFillColor(color if jes_var == 'nominal' else 0)
            h_total.SetFillStyle(1001 if jes_var == 'nominal' else 0)
            stack_var.Add(h_total)
            total_var.Add(h_total)

        stacks[jes_var] = stack_var
        all_totals[jes_var] = total_var

    # ========== pad1: nominal堆叠 + Up/Down线 ==========
    pad1.cd()
    pad1.SetLogy(log_scale)
    # 如果变量名是 mt_tot，则开启 x 轴 log
    if var_key == "mt_tot":
        pad1.SetLogx(True)
        pad1.SetLogy(True)
        pad2.SetLogx(True)
        pad1.SetLogy(True)
    else:
        pad1.SetLogx(False)
        pad2.SetLogx(False)

    stacks['nominal'].Draw("hist")
    set_top_plot_general_style(stacks['nominal'].GetHistogram(), log_scale=log_scale)
    stacks['nominal'].GetYaxis().SetTitle(title.split(';')[2])
    

    # ========== 调整 Y 轴范围 ==========
    current_max = stacks['nominal'].GetMaximum()

    if log_scale:
        # log y 模式
        min_non_zero = min(
            h.GetMinimum(0) for h in all_totals.values() if h.GetMinimum(0) > 0
        )
        stacks['nominal'].SetMinimum(min_non_zero * 0.01)
        stacks['nominal'].SetMaximum(current_max * 100)
        stacks['nominal'].GetXaxis().SetLabelSize(0)
    else:
        # 线性 y 模式
        stacks['nominal'].GetYaxis().SetNoExponent(False)
        stacks['nominal'].GetYaxis().SetMoreLogLabels(False)
        ROOT.TGaxis.SetMaxDigits(3)
        stacks['nominal'].SetMaximum(current_max * 1.74)


    for jes_var in ['jesUncBBEC1Up', 'jesUncBBEC1Down']:
        all_totals[jes_var].SetLineColor(jes_variations[jes_var]['color'])
        all_totals[jes_var].SetLineStyle(jes_variations[jes_var]['linestyle'])
        all_totals[jes_var].SetLineWidth(jes_variations[jes_var]['linewidth'])
        all_totals[jes_var].Draw("hist same")

    legend = ROOT.TLegend(0.62, 0.65, 1.02, 0.9)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    # nominal stack legend
    for i, sname in enumerate(stacking_order):
        if sname.lower() == "fakes":
            continue
        h_for_legend = stacks['nominal'].GetHists().At(i)
        legend.AddEntry(h_for_legend, samples[sname][0], "f")
    legend.AddEntry(all_totals['jesUncBBEC1Up'], "jesUncBBEC1Up", "l")
    legend.AddEntry(all_totals['jesUncBBEC1Down'], "jesUncBBEC1Down", "l")
    legend.Draw()

    # ========== pad2: ratio ==========
    pad2.cd()
    frame = all_totals['nominal'].Clone("frame")
    frame.Reset()
    set_bottom_plot_general_style(frame)
    frame.Draw()

    line = ROOT.TLine(xmin, 1, xmax, 1)
    line.SetLineColor(ROOT.kBlack)
    line.Draw("same")

    ratios = {}
    for jes_var in ['jesUncBBEC1Up', 'jesUncBBEC1Down']:
        r = all_totals[jes_var].Clone(f"ratio__{jes_var}")
        r.Divide(all_totals['nominal'])
        r.SetLineColor(jes_variations[jes_var]['color'])
        r.SetLineStyle(jes_variations[jes_var]['linestyle'])
        r.SetLineWidth(jes_variations[jes_var]['linewidth'])
        r.Draw("hist same")
        ratios[jes_var] = r

    # ratio legend
    leg2 = ROOT.TLegend(0.10, 0.75, 0.30, 0.93)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0)
    leg2.AddEntry(ratios['jesUncBBEC1Up'], "jesUncBBEC1Up", "l")
    leg2.AddEntry(ratios['jesUncBBEC1Down'], "jesUncBBEC1Down", "l")
    leg2.Draw()

    frame.GetXaxis().SetTitle(title.split(';')[1])
    frame.GetXaxis().SetTitleSize(0.15)
    frame.GetXaxis().SetTitleOffset(1.0)



    region_dir = os.path.join(output_dir, region)
    os.makedirs(region_dir, exist_ok=True)


    scale_tag = "log" if log_scale else "lin"
    outname = os.path.join(region_dir, f"{sname}_{var_key}_{scale_tag}.png")

    c.SaveAs(outname)
    print(f"[SAVED] {outname}")





# ------------------------
# Utilities
# ------------------------
def set_top_plot_general_style(obj, log_scale=False):
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
    obj.SetMinimum(0.75)
    obj.SetMaximum(1.25)
    obj.SetTitle("")
    obj.GetYaxis().SetTitle("#frac{Up/Down}{Nominal}")
    obj.SetStats(0)  


 


 

def set_bottom_plot_pull_style(obj):
    obj.SetFillColor(922)

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
  
    pnn_mode = False
    if "--PNN" in sys.argv:
        pnn_mode = True
        sys.argv.remove("--PNN")
        plot_vars=PNN_plot_vars
        stacking_order = PNN_stacking_order
        regions = pnn_regions
    
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
                draw_plot(fpath, output_dir, region, var, log_scale=False , PNN=pnn_mode )
                # Draw log scale plot
                # draw_plot(fpath, output_dir, region, var, log_scale=True, PNN=pnn_mode)
