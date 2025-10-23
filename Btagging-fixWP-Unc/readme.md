# CMS Corrections and Fixes: FixedWP b-tagging Scale Factors and Uncertainties 

## Overview
working path: ` /afs/cern.ch/user/l/leyan/public/Btagging-fixWP-Unc` 

Documentation for fixed working point (fixedWP) b-tagging scale factors (SF) and associated uncertainties in CMS analyses.

https://docs.google.com/document/d/1AFzKqSpXs5Z3F8CvdSFRcJJd59fl_Zc26IijGXeJQos/edit?tab=t.0


fixedWP btagging SF and uncertainties
https://btv-wiki.docs.cern.ch/PerformanceCalibration/fixedWPSFRecommendations/ 

Method 1a) Event reweighting using scale factors and MC b-tagging efficiencies

该方法的目标是：仅通过改变选中模拟事件(即通过event selection的模拟事件)的 weight，to predict correct event yield in data。

在这种方法下，事件不会从一个 Nbtag 数量的区间迁移到另一个区间。也就是说，事件的 Nbtag 不会因为权重调整而发生变化。每个模拟事件原本有多少个 b-tag，在加权后依然保持相同的数量。

scale factors, SF 作为乘法因子作用到事件权重上 𝑤  SF 来应用，其计算时会考虑所有在分析中使用 b-tag 信息的喷注(参见引言中的说明) 具体公式参考: https://btv-wiki.docs.cern.ch/PerformanceCalibration/fixedWPSFRecommendations/#scale-factor-recommendations-for-event-reweighting

$\omega_{SF} = \prod_{i \in \text{tagged jets}} \frac{SF_i[p_T, \eta, \text{flav}] \cdot \epsilon_i[p_T, \eta, \text{flav}] }{\epsilon_i[p_T, \eta, \text{flav}]} \cdot \prod_{j \in \text{untagged jets}} \frac{1 - SF_j[p_T, \eta, \text{flav}] \cdot \epsilon_j[p_T, \eta, \text{flav}]}{1 - \epsilon_j[p_T, \eta, \text{flav}]}$`  

$\epsilon[p_T, \eta, \text{flav}] = \frac{N_\text{b-tagged jets}[p_T, \eta, \text{flav}]}{N_\text{total jets}[p_T, \eta, \text{flav}]}$





---

## 程序与脚本说明

| 程序名               | 功能描述                                                                 |
|----------------------|--------------------------------------------------------------------------|
| `check.py`           | 存储所有分支(branch)名称的参考文件                                      |
| `simple_plot.py`     | 快速绘图工具，可以检查skim sample tree 中的branch                                     |
| `btag-eff.py`        | **备用主程序**：输入3种ttbar文件 → 输出1个TH3F eff root + 3个TH2F eff root（按light/c/b味区分） |
| `btag-eff_dxc.py`    | **多线程优化版(现在使用的)**：已集成era和channel筛选条件，提高运行效率               |
| `example_TH3F.py`    | TH3F输出检查工具，用于验证主程序的输出结果                              |
| `run.sh`             | 批量交condor作业的脚本，支持按era和channel自动运行任务                            |
| `quick_plot`         | 专门绘制light/c/b jet eff 曲线的工具                                    |

---


## Folders :


| 文件夹名               | 功能描述                                                                 |
|----------------------|--------------------------------------------------------------------------|
| `PNGs`   | 存储simple_plot.py绘制的图, 检查 skim sample 里某些变量                                 |
| `ROOT_btagging_eff`           |  存储 btag-eff_dxc.py 的 output   --- `eff_ROOT`:  所有era,所有channel的 eff root示例文件  --- `JSON`: ROOT 转 correctionlib  示例文件,格式严格按照 BTV btagging.json                               |
| `Skimmed_sample`     | 分era 存储 btag-eff_dxc.py 的 input, btagging eff 是通过skimmed sample计算, 选取 TTbar 过程, 按照 eos 对应路径 1/3 统计量 链接自: /eos/cms/store/group/phys_higgs/HLepRare/skim_2025_v1, 里面各个文件夹有快速下载的脚本`download.sh`                                     |
| `CMSSW_15_0_13_patch1/src`    |  root 转 json 工作路径,这里没有上传到git, 自行选择一个最新版本即可                            |





---




## Workflow :

### 1.计算 $\epsilon(p_T, \eta, \text{flav})$

- 计算出 eff.root 文件, 分era 和 channel, 使用`btag-eff_dxc.py` 和 交作业脚本 `run.sh`, 脚本中需要按照VHmm 更改 $channel , 

  具体修改的地方: `L24 def get_btag_threshold(era) `如果VHmm 用多个wp 需要去查对应的threshold 参考 https://btv-wiki.docs.cern.ch/ScaleFactors/Run3Summer22/#ak4-b-tagging , `L32 def check_channel_cut_expr(channel, delta_r_min=0.5)` 按照VHmm的各channel cut去修改cut.     `L241 out_dir="/eos/home-l/leyan/Htautau/Btagging-fixWP-Unc/ROOT_btagging_eff"` 输出路径改一下 

  多个wp的话就需要按照如下公式, 另外code逻辑需要改, 因为有超过1个eff需要计算

  $w_{SF} =
  \prod_{i \in \text{tagged at T WP}}
  \frac{ SF^T_i[p_T, \eta, \text{flav}] \cdot \epsilon^T_i[p_T, \eta, \text{flav}] }{ \epsilon^T_i[p_T, \eta, \text{flav}] }
  \cdot
  \prod_{j \in \text{tagged at L WP but not T WP}}
  \frac{ SF^L_j[p_T, \eta, \text{flav}] \cdot \epsilon^L_j[p_T, \eta, \text{flav}] - SF^T_j[p_T, \eta, \text{flav}] \cdot \epsilon^T_j[p_T, \eta, \text{flav}] }{ \epsilon^L_j[p_T, \eta, \text{flav}] - \epsilon^T_j[p_T, \eta, \text{flav}] }
  \cdot
  \prod_{k \in \text{not tagged at L WP}}
  \frac{ 1 - SF^L_k[p_T, \eta, \text{flav}] \cdot \epsilon^L_k[p_T, \eta, \text{flav}] }{ 1 - \epsilon^L_k[p_T, \eta, \text{flav}] }$





- skim sample较大, 一般可能消耗 1~2 天计算得到root文件, 根据channel cut的不同决定

- 示例文件: /eos/home-l/leyan/Htautau/Btagging-fixWP-Unc/ROOT_btagging_eff/btag_eff_dxc_202*_
*_with_DeltaR.root   里面包含一个 $3D[p_T, \eta, \text{flav}]$ TH3F 和  3个 分flavor, light b c 的 $2D[p_T, \eta]$ TH2F

- 算好之后用 会有 era $\times$ channel 个数量的 root file , 命名在`btag-eff_dxc.py` L241和L244

- `/eos/home-l/leyan/Htautau/Btagging-fixWP-Unc/example_TH3F.py`   随便输入一组 $[p_T, \eta, \text{flav}]$ 看看 btagging_eff的值是否正确

- 再用`quick_plot.py` 对所有root文件绘图, 看看算出来eff值是否正常, 可参考Htautau画的: https://hig-25006.web.cern.ch/Btagging-effciency/


### 2. 将eff.root文件 转为 correctionlib json文件
在`/eos/home-l/leyan/Htautau/Btagging-fixWP-Unc/CMSSW_15_0_13_patch1/src` 中进行, 需要CMSSW环境, 版本随便, 可参考我的,  运行需要cmsenv, 没有上传到git, 自行选择版本
#### 程序与脚本说明

| 文件名               | 功能描述                                                            |
|----------------------|--------------------------------------------------------------------------|
| `CreateElectron_ID+Reco_2D.py`   |   root 转 json 主程序, 用法: `python3 CreateElectron_ID+Reco_2D.py  Btagging_eff_Config.json  <文件夹名> `  需要cmsenv                                |
| `Btagging_eff_Config.json`           | 集成主程序的input的 config文件, 需要修改                              |
| `btvExample.py`     | 快速检查 json文件是否有效,  程序内输入20组随机的 $[p_T, \eta, \text{flav}]$ 检查eff是否可读, 与 第一步`example_TH3F.py` cross check   需要cmsenv                                |                    |
