# Run3_BSM_Htautau_Scripts

本仓库用于 Run3 BSM H→ττ 分析的辅助脚本和绘图工具。  
内容按文件夹进行组织，每个文件夹对应一个功能模块。

---

## 📂 pre-fit_band_plot

该文件夹主要用于 **预拟合图 (pre-fit plots)** 的绘制，支持等宽 error band 的展示。

### 文件说明

- **`plot_config_prefit_equal_band.py`**  
  - 用途：配置绘制 **等宽 error band** 的脚本。  
  - 功能：
    - 可选择绘制 **总系统误差** error band  
    - 或仅绘制 **统计误差** error band  

- **`run.sh`**  
  - 用途：执行绘图任务的脚本。  
  - 功能：
    - 调用 `plot_config_prefit_equal_band.py`  
    - 可绘制 **PNN 输入变量 (PNN input var)** 图  
    - 可绘制 **PNN score** 图  

---

（更多文件夹说明待补充）
