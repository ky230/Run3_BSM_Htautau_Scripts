import numpy as np
import correctionlib
import argparse

# === 参数解析 ===
parser = argparse.ArgumentParser(description="Evaluate btagging efficiency scale factors from JSON")
parser.add_argument("json_path", help="Path to btagging efficiency JSON file")
parser.add_argument("year", help="Data-taking year (e.g. 2022EE, 2023, etc.)")
parser.add_argument("channel", help="Analysis channel (e.g. mt, et, tt, em)")
args = parser.parse_args()

json_path = args.json_path
year = args.year
Channel = args.channel

ValType = "btagging-eff"

# === 加载 correctionlib JSON ===
btvjson = correctionlib.CorrectionSet.from_file(json_path)
corr = btvjson["Btagging effciency[pt,eta,flavor]"]

# === 生成 200 个随机 jet 特征 ===
jet_pt    = np.random.uniform(25.0, 180.0, 20)
jet_eta   = np.random.uniform(-2.5, 2.5, 20)
jet_flav  = np.random.choice([0, 4, 5], 20)

# === 计算 SF ===
sf_all = corr.evaluate(year, ValType, Channel,
                       jet_pt,
                       jet_eta,
                       jet_flav)

# === 输出结果 ===
print(f"{'index':>5} | {'pt':>8} | {'eta':>8} | {'flavor':>6} | {'SF':>6}")
print("-"*45)
for i in range(len(jet_pt)):
    print(f"{i:5d} | {jet_pt[i]:8.2f} | {jet_eta[i]:8.2f} | {jet_flav[i]:6.1f} | {sf_all[i]:6.3f}")

