# Al–Li 相界曲线导出器（Al–Li Solvus Curves Exporter）

> 基于 Alan J. Ardell (2023 JPED) 的相界复现与导出

本项目在作者拟合曲线的基础上，将论文 Table 1 中另外两组理论曲线（Hallstedt & Kim；Khachaturyan 等）加入同一张图，并将三组六条曲线的计算数据导出为 Excel 文件。

<img width="1503" height="1508" alt="image" src="https://github.com/user-attachments/assets/ba8c95dc-d094-4326-ab81-5ecc9cb45ff1" />


## 文件结构
- `The Equilibrium α (Al-Li Solid Solution) and Metastable δ′ (Al3Li) Phase Boundaries in Aluminum–Lithium Alloys.pdf`：作者论文 PDF。
- `gg copy.py`：主绘图与数据导出脚本（三组曲线）。
- `extract_table1.py`：尝试从 PDF 自动提取 Table 1 表格与公式的脚本（辅助）。
- `dump_pdf_text.py`：将 PDF 的可读文本抽取到 `pdf_full_text.txt`（辅助定位 Table 1）。
- `Al_Li_phase_boundaries_curves.xlsx`：导出的曲线数据（三组、六条，按温度列出）。
- `phase_boundaries.png`：包含全部曲线的 PNG 预览图。
- `pdf_full_text.txt`：PDF 文本抽取结果，便于检索 Table 1 内容。
- `table1_coeffs.json`：自动解析到的公式系数（若能解析会写入）。

## 环境与依赖
建议使用 Python 3.10+。安装依赖：

```
pip install numpy matplotlib pandas openpyxl pdfplumber
```

说明：
- `numpy`、`matplotlib`、`pandas`：数值计算与绘图、导出。
- `openpyxl`：写 Excel。
- `pdfplumber`：抽取 PDF 表格与文本（仅辅助）。

## 快速开始：绘图与导出（三组六条曲线）
在项目目录下运行：

```
python "gg copy.py"
```

输出：
- `Al_Li_phase_boundaries_curves.xlsx`：包含三组曲线（作者本研究、Hallstedt & Kim、Khachaturyan 等）在 `280–700 K`（500个点）的计算值：
  - `T(K)`
  - `Xδ′e_ThisInvestigation`, `Xαe_ThisInvestigation`
  - `Xδ′e_HallstedtKim`, `Xαe_HallstedtKim`
  - `Xδ′e_Khachaturyan`, `Xαe_Khachaturyan`
- `phase_boundaries.png`：绘制的整张图（黑色为作者本研究；绿色/红色虚线为 Table 1 两组）。

散点数据：
- 若同目录存在 `data.csv` 与/或 `Al_Li_data_with_at_percent2.csv`，脚本会绘制对应作者的数据点；若不存在，脚本会跳过散点绘制，仅生成曲线与导出文件。

## 公式来源与实现
理想气体常数：`R = 8.314 J/(mol·K)`。

作者本研究（黑色，已在论文中给出）：
- δ′ 相（`Xδ′e(T)`，多项式，妥协取平均理论曲线）：
  - `Xδ′e = 0.1809 + 6.413e-4*T − 1.861e-6*T^2 + 1.4684e-9*T^3`
- α 相（`Xαe(T)`，指数，Arrhenius）：
  - `Xαe = 0.60086 * exp(−8669.55 / (R*T))`

Table 1（两组理论曲线）：
- Hallstedt & Kim：
  - `Xαe = 0.68885 * exp(−8876.23 / (R*T))`
  - `Xδ′e = 0.1869 + 6.01049e-4*T − 1.7699e-6*T^2 + 1.37689e-9*T^3`
- Khachaturyan 等：
  - `Xαe = 0.70189 * exp(−9062.89 / (R*T))`
  - `Xδ′e = 0.1749 + 6.81639e-4*T − 1.9539e-6*T^2 + 1.55999e-9*T^3`

在 `gg copy.py` 中，这些函数已经实现：
- `solvus_line_alpha(T)`, `solvus_line_ae(T)`（作者本研究）
- `solvus_line_alpha_hallstedt(T)`, `solvus_line_ae_hallstedt(T)`
- `solvus_line_alpha_khachaturyan(T)`, `solvus_line_ae_khachaturyan(T)`
并统一采样 `T_values = linspace(280, 700, 500)` 进行计算与绘制。

## 辅助：PDF 表格与文本抽取
- 抽取全文文本以定位 Table 1：
  ```
  python dump_pdf_text.py
  ```
  输出 `pdf_full_text.txt`，可搜索 `Table 1` 或公式片段以校核。
- 自动提取表格与解析公式（能力受 PDF 版式与嵌入字体影响）：
  ```
  python extract_table1.py
  ```
  若成功：输出 `table1_raw.xlsx` / `table1_raw.csv`（原始表格）、`table1_coeffs.json`（解析到的公式与系数）。本项目已在 `gg copy.py` 中手动实现 Table 1 公式，即使自动解析不到也不影响主流程。

## 常见问题与说明
- `data.csv` / `Al_Li_data_with_at_percent2.csv` 不存在：脚本会提示并跳过散点绘制，但曲线与导出仍会生成。
- 字体中文显示：脚本设置了 `SimHei`，确保中文标签正常显示；若没有该字体，可改为系统可用字体。
- 温度范围或采样数量：在 `gg copy.py` 修改 `T_values` 即可，例如：
  ```python
  T_values = np.linspace(300, 650, 400)
  ```
- 线型与颜色：在绘制部分调整 `color` 与 `linestyle`。目前作者本研究为黑色实线，两组理论曲线为绿色/红色虚线。
- 单位一致性：所有公式均以原文定义，温度 `T` 单位为 K，浓度以原文的原子分数（例如 `Xαe = 0.088` 等）。

## 参考
- Ardell, A. J. (2023). The Equilibrium α (Al-Li Solid Solution) and Metastable δ′ (Al3Li) Phase Boundaries in Aluminum–Lithium Alloys. J. Phase Equilib. Diffus., 44:255–268.
- Hallstedt & Kim（热力学评估模型）与 Khachaturyan 等（BMG 模型）的相界表达式，见论文 Table 1。
