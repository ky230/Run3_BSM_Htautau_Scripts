import sys
import ROOT

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 simple_plot.py <root_file> <tree_name> <branch_name>")
        sys.exit(1)

    root_file = sys.argv[1]
    tree_name = sys.argv[2]
    branch_name = sys.argv[3]

    f = ROOT.TFile.Open(root_file)
    if not f or f.IsZombie():
        print(f"Error opening file {root_file}")
        sys.exit(1)

    tree = f.Get(tree_name)
    if not tree:
        print(f"Tree {tree_name} not found in file")
        sys.exit(1)

    # 创建直方图
    hist = ROOT.TH1F("hist", f"{branch_name};{branch_name};Entries", 100, 0, 0)  
    # 注意：这里 binning 会自动根据 Fill 调整，如果 branch 没有范围信息，可以先扫描一下 min/max 再设置
    
    tree.Draw(f"{branch_name} >> hist")

    canvas = ROOT.TCanvas("canvas", "canvas", 800, 600)
    hist.Draw()
    canvas.SaveAs(f"PNGs/{branch_name}.png")

    f.Close()
    print(f"Saved histogram to {branch_name}.png")

if __name__ == "__main__":
    main()
