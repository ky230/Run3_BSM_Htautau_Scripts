import gzip
from correctionlib.schemav2 import CorrectionSet,Correction,Category,CategoryItem
from itertools import chain
import correctionlib.schemav2 as schema
# from JSONTools import *
import pandas as pd
import numpy as np
import os
#############################################################
import json
import sys

# -----------------------------
# Function 1: extract SFs from TH2F ROOT files
from ROOT import TFile
import correctionlib.schemav2 as schema



# TH2F * 3
 
def getSFs(fn="filename", sfhists=["btag_eff_light","btag_eff_cjet","btag_eff_bjet"]):
    """
    读取三个 TH2F (pt, eta) histogram，并返回 {flavor: MultiBinning}
    flavor: 0 -> light, 4 -> c, 5 -> b
    """
    from ROOT import TFile
    import correctionlib.schemav2 as schema

    flavor_map = {"btag_eff_light": 0, "btag_eff_cjet": 4, "btag_eff_bjet": 5}
    
    tf = TFile(fn[0])
    hists = {flavor_map[name]: tf.Get(name) for name in sfhists}
    
    if any(h is None for h in hists.values()):
        raise RuntimeError(f"One of the histograms {sfhists} not found in {fn[0]}")

    # 获取 bin edges
    x_edges = [hists[0].GetXaxis().GetBinLowEdge(i+1) for i in range(hists[0].GetNbinsX())] + [hists[0].GetXaxis().GetBinUpEdge(hists[0].GetNbinsX())]
    y_edges = [hists[0].GetYaxis().GetBinLowEdge(i+1) for i in range(hists[0].GetNbinsY())] + [hists[0].GetYaxis().GetBinUpEdge(hists[0].GetNbinsY())]

    # flavor → MultiBinning
    out = {}
    for flav, h in hists.items():
        values = []
        for ix in range(1, h.GetNbinsX()+1):
            for iy in range(1, h.GetNbinsY()+1):
                values.append(h.GetBinContent(ix, iy))

        mb = schema.MultiBinning.parse_obj({
            "inputs": ["pt", "eta"],
            "nodetype": "multibinning",
            "edges": [x_edges, y_edges],
            "content": values,
            "flow": "error"
        })
        out[flav] = mb

    tf.Close()
    return out


def SFyearwise(files=[], names=[], valtypes=["btagging-eff"]):
    """
    生成 JSON: ValType -> Channel -> Flavor -> MultiBinning
    """
    output = schema.Category.parse_obj({
        "nodetype": "category",
        "input": "ValType",
        "content": [
            schema.CategoryItem.parse_obj({
                "key": val,
                "value": schema.Category.parse_obj({
                    "nodetype": "category",
                    "input": "Channel",
                    "content": [
                        schema.CategoryItem.parse_obj({
                            "key": name,
                            "value": schema.Category.parse_obj({
                                "nodetype": "category",
                                "input": "flavor",
                                "content": [
                                    schema.CategoryItem.parse_obj({
                                        "key": flav,
                                        "value": mb
                                    }) 
                                    for flav, mb in getSFs(fn=files[name]).items()
                                ]
                            })
                        })
                        for name in names
                    ]
                })
            })
            for val in valtypes
        ]
    })
    return output




def load_config(config_file):
    with open(config_file) as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <config_file> <Iteration>")
        sys.exit(1)
        
    config_file = sys.argv[1]
    Iteration = sys.argv[2]
    data = load_config(config_file)

    years = data['years']
      
    #############################################################
    
    for name in years:
        fullpath="JSONs/"+Iteration+"/"+name
        if not os.path.exists(fullpath):
            os.makedirs(fullpath)
            print(f"Folder '{fullpath}' created.")
        else:
            print(f"Folder '{fullpath}' already exists.")

    #Names that you want for errors for files above (same order please)
    nameJSON=data['nameJSON'] # Name of final JSON
    sfhist=data['sfhist']


    namesSFs=data['Channels']  #channel
    
    years=data['years']
    folders=data['folders']
    files=[data[myfile] for myfile in data['files']]

    for year,folder,filelist in zip(years,folders,files):
        corrs=[]
        print(f'Storing SFs for {year} in  {folder}')
        print(f'-----------------------')
        print(folder)

        corr = Correction.parse_obj(
            {
                "version": 2,
                "name": "Btagging effciency[pt,eta,flavor]",
                "description": f"These are the electron ID & Reco Scale Factors (nominal, up or down) for {year} dataset. They are available for the cut-based and MVA IDs. They are dependent on the transverse momenta and pseudorapidity of the electron.",
                "inputs": [
                    {"name": "year","type": "string", "description": "year/scenario: example, 2017, 2022FG etc"},
                    {"name": "ValType","type": "string", "description": "btagging-eff"},
                    {"name": "Channel","type": "string", "description": "em/et/mt/tt"},
                    {"name": "pt", "type": "real", "description": "Jet pt"},
                    {"name": "eta", "type": "real", "description": "Jet eta"},
                    {"name": "flavor", "type": "int", "description": "Jet flavor (0: light, 4: c, 5: b)"}
                    
                    

                ],
                "output": {"name": "weight", "type": "real", "description": "value of scale factor (nominal, up or down)"},
                "data": schema.Category.parse_obj({
                    "nodetype": "category",
                    "input": "year",
                    "content": [
                        schema.CategoryItem.parse_obj({"key":year,
                                                        "value": SFyearwise(files=filelist,names=namesSFs)})]
                })
            })
        
        corrs.append(corr)
            
        #Save JSON
        cset = CorrectionSet(schema_version=2, corrections=corrs,description=f"These are the electron ID & Reco Scale Factors (nominal, up or down) for {year} dataset. They are available for the cut-based and MVA IDs. They are dependent on the transverse momenta and pseudorapidity of the electron. Please keep in the mind that if your analysis is sensitive to high pT electrons (>500 GeV), we recommend you to use HEEP ID. In any case, you have even some electrons above 500 GeV, be careful while applying these SFs.")
    
        fullpath="JSONs/"+Iteration+"/"+year
        with open(f"{fullpath}/{nameJSON}", "w") as fout:
            fout.write(json.dumps(cset.dict(exclude_unset=True), indent=4))