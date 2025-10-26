import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io

# --- 设置绘图环境 ---
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

# --- 新增：定义理想气体常数 ---
R = 8.314  # 理想气体常数, J/(mol·K)

# --- 1. 定义曲线函数 ---


def solvus_line_alpha(T):
    """
    α / (α + δ') 相界线 (您提供的第一个公式)
    """
    term1 = 0.1809
    term2 = 6.413e-4 * T
    term3 = -1.861e-6 * T**2
    term4 = 1.4684e-9 * T**3
    return term1 + term2 + term3 + term4


# --- 新增：根据图片公式定义的函数 ---
def solvus_line_ae(T):
    """
    (α + δ') / δ' 相界线 (根据图片公式 X_ae = 0.60086 exp{-8,669.55/RT})
    """
    # 注意：公式中的 -8,669.55 在代码中要写成 -8669.55
    return 0.60086 * np.exp(-8669.55 / (R * T))

# --- 新增：Table 1 中另外两组理论曲线（Hallstedt & Kim；Khachaturyan et al.） ---
# Hallstedt & Kim (绿色)：
#   δ′ 溶解度（Xαe）: Xαe = 0.68885 * exp(-8876.23 / (R*T))
#   α 溶解度（Xδ′e）: Xδ′e = 0.1869 + 6.01049e-4*T - 1.7699e-6*T**2 + 1.37689e-9*T**3

def solvus_line_ae_hallstedt(T):
    return 0.68885 * np.exp(-8876.23 / (R * T))


def solvus_line_alpha_hallstedt(T):
    return 0.1869 + 6.01049e-4 * T - 1.7699e-6 * T**2 + 1.37689e-9 * T**3

# Khachaturyan 等（红色）：
#   δ′ 溶解度（Xαe）: Xαe = 0.70189 * exp(-9062.89 / (R*T))
#   α 溶解度（Xδ′e）: Xδ′e = 0.1749 + 6.81639e-4*T - 1.9539e-6*T**2 + 1.55999e-9*T**3

def solvus_line_ae_khachaturyan(T):
    return 0.70189 * np.exp(-9062.89 / (R * T))


def solvus_line_alpha_khachaturyan(T):
    return 0.1749 + 6.81639e-4 * T - 1.9539e-6 * T**2 + 1.55999e-9 * T**3


# --- 2. 加载您的原始数据 ---
# --- 加载实验数据（若文件不存在则跳过散点绘制） ---
try:
    df = pd.read_csv("data.csv")
    print(df.info)
except Exception as e:
    print("加载 data.csv 失败，跳过散点绘制:", e)
    df = pd.DataFrame(columns=["author", "X(Li)", "Temperature"])  # 空数据占位

# --- 新增：加载 Al_Li_data_with_at_percent2.csv 数据（可选） ---
try:
    df_additional = pd.read_csv("Al_Li_data_with_at_percent2.csv")
    print("Additional data info:")
    print(df_additional.info)
    df_additional.columns = df_additional.columns.str.strip()  # 去掉列名前后空格
except Exception as e:
    print("加载 Al_Li_data_with_at_percent2.csv 失败（可忽略）:", e)
    df_additional = None

# --- 新增：从论文 Appendix Table 6/7 内嵌实验数据（原子分数Li, 温度K） ---
table6_points = {
    "Williams & Edington": [(0.078, 505), (0.107, 594), (0.129, 615)],
    "Ceresara et al.": [(0.0506, 293), (0.0564, 398), (0.0593, 423), (0.0602, 423), (0.0665, 473)],
    "Cocco et al.": [(0.0502, 293), (0.0556, 398), (0.0584, 423), (0.0663, 473)],
    "Jensrud & Ryum": [(0.10960, 596)],
    "Nozato & Nakai": [(0.05845, 510), (0.06285, 505), (0.07336, 522), (0.07697, 530), (0.08701, 545), (0.09730, 579)],
    "Livet and Bloch": [(0.04421, 423), (0.05509, 453)],
    "Baumann & Williams": [(0.079, 528)],
    "Fujikawa et al.": [(0.0237, 473)],
    "Liu & Williams": [(0.088, 563)],
    "Shaiu et al.": [(0.070, 468), (0.120, 578)],
    "Jo": [(0.0460, 493), (0.0493, 513)],
    "Abis et al.": [(0.070, 463)],
    "Del Río et al.": [(0.099, 550)],
    "Noble & Bray": [
        (0.0254, 343), (0.0380, 373), (0.0432, 373), (0.0475, 403), (0.0530, 403),
        (0.0498, 423), (0.0520, 423), (0.0532, 423), (0.0550, 443), (0.0600, 473),
        (0.0690, 493), (0.0763, 519), (0.0983, 578), (0.1200, 632), (0.1200, 643), (0.1314, 665)
    ],
    "Mergia et al.": [(0.0483, 363), (0.0464, 393), (0.0512, 423), (0.0597, 458), (0.0720, 483)],
    "Tsao et al.": [(0.0489, 423), (0.0543, 433), (0.0456, 443)],
    "Khushaim et al.": [(0.059, 444.4), (0.062, 460.5), (0.065, 468.0), (0.070, 480.6), (0.072, 490.3), (0.076, 501.6)],
}

table7_points = {
    "Tamura et al.": [(0.2279, 473)],
    "Cocco et al.": [(0.2461, 293.0), (0.2375, 398.0), (0.2326, 423.0), (0.2197, 473.0)],
    "Livet and Bloch": [(0.2514, 423.0), (0.2272, 453.0)],
    "Sung et al.": [(0.2174, 573)],
    "Liu & Williams": [(0.2537, 428), (0.2271, 498), (0.2360, 428), (0.2180, 498), (0.2050, 563)],
    "Khushaim et al.": [(0.2170, 444.4), (0.2100, 460.5), (0.2050, 468), (0.2000, 480.6), (0.1990, 490.3), (0.1950, 501.6)],
}
# 将 Table 6/7 转为 DataFrame 并并入 df
rows_t6 = [{"author": a, "X(Li)": x, "Temperature": t} for a, pts in table6_points.items() for (x, t) in pts]
rows_t7 = [{"author": a, "X(Li)": x, "Temperature": t} for a, pts in table7_points.items() for (x, t) in pts]
df_table6 = pd.DataFrame(rows_t6)
df_table7 = pd.DataFrame(rows_t7)
df = pd.concat([df, df_table6, df_table7], ignore_index=True)
# --- 3. 准备绘图数据 ---
T_values = np.linspace(280, 700, 500)  # 调整温度起始点以匹配右侧曲线

# This Investigation（作者本研究）
x_black_left = solvus_line_alpha(T_values)        # Xδ′e（多项式）
x_black_right = solvus_line_ae(T_values)          # Xαe（指数）

# Hallstedt & Kim（绿色）
x_hallstedt_left = solvus_line_alpha_hallstedt(T_values)
x_hallstedt_right = solvus_line_ae_hallstedt(T_values)

# Khachaturyan 等（红色）
x_khacha_left = solvus_line_alpha_khachaturyan(T_values)
x_khacha_right = solvus_line_ae_khachaturyan(T_values)

# --- 4. 开始绘图 ---
fig, ax = plt.subplots(figsize=(10, 12))

# --- 绘制计算曲线 ---
# 绘制左侧曲线
ax.plot(
    x_black_left, T_values, color="black", linewidth=2.5, label="This Investigation"
)
# --- 新增：绘制右侧曲线 ---
# 绘制右侧曲线，不加label，这样两条线会共用一个图例项
ax.plot(x_black_right, T_values, color="black", linewidth=2.5)

# --- 新增：Table 1 两组曲线 ---
# Hallstedt & Kim（绿色，虚线）
ax.plot(x_hallstedt_left, T_values, color="green", linewidth=2, linestyle="--", label="Hallstedt & Kim")
ax.plot(x_hallstedt_right, T_values, color="green", linewidth=2, linestyle="--")

# Khachaturyan 等（红色，虚线）
ax.plot(x_khacha_left, T_values, color="red", linewidth=2, linestyle="--", label="Khachaturyan et al.")
ax.plot(x_khacha_right, T_values, color="red", linewidth=2, linestyle="--")


# --- 绘制所有实验数据点 ---
# 创建一个样式字典，为每个作者指定标记样式
author_styles = {
    "Tamura et al.": {"marker": "o", "s": 80, "facecolor": "darkgoldenrod"},
    "Williams & Edington": {"marker": "o", "s": 80, "facecolor": "red"},
    "Ceresara et al.": {"marker": "s", "s": 70, "facecolor": "deepskyblue"},
    "Cocco et al.": {"marker": "s", "s": 70, "facecolor": "green"},
    "Nozato & Nakai": {
        "marker": "v",
        "s": 70,
        "facecolor": "purple",
        "edgecolor": "purple",
    },
    "Jensrud & Ryum": {"marker": "D", "s": 60, "facecolor": "silver"},
    "Livet and Bloch": {"marker": "s", "s": 70, "facecolor": "red"},
    "Baumann & Williams": {
        "marker": "v",
        "s": 80,
        "facecolor": "green",
        "edgecolor": "green",
    },
    "Fujikawa et al.": {"marker": "D", "s": 60, "facecolor": "pink"},
    "Sung et al.": {"marker": "D", "s": 60, "facecolor": "black"},
    "Liu & Williams": {"marker": "<", "s": 80, "facecolor": "limegreen"},
    "Shaiu et al.": {"marker": "^", "s": 80, "facecolor": "darkgreen"},
    "Jo": {"marker": "o", "s": 80, "facecolor": "cyan"},
    "Abis et al.": {"marker": "p", "s": 80, "facecolor": "black"},
    "Del Río et al.": {"marker": "<", "s": 80, "facecolor": "mediumspringgreen"},
    "Noble & Bray": {"marker": "o", "s": 80, "facecolor": "blue"},
    "Mergia et al.": {"marker": "D", "s": 60, "facecolor": "red"},
    "Tsao et al.": {"marker": "^", "s": 80, "facecolor": "orange"},
    "Khushaim et al.": {"marker": ">", "s": 80, "facecolor": "olive"},
}

# 循环绘制每个作者的数据点
for author, style in author_styles.items():
    author_data = df[df["author"] == author]
    if not author_data.empty:
        ax.scatter(author_data["X(Li)"], author_data["Temperature"], **style)


# --- 5. 设置图表样式和注释 ---
ax.set_xlim(0, 0.4)  # 扩大x轴范围以适应新数据点
ax.set_ylim(280, 700)
ax.set_xlabel("$X_{Li}$", fontsize=16)
ax.set_ylabel("T (K)", fontsize=16)

# 添加相区文本注释 (已修正LaTeX语法)
ax.text(0.05, 650, r"$\alpha$", fontsize=22)
ax.text(0.15, 450, r"$\alpha + \delta^{\prime}$", fontsize=22)
ax.text(0.22, 650, r"$\delta^{\prime}$", fontsize=22)

# --- 6. 创建图例 ---
from matplotlib.lines import Line2D

curve_handles, curve_labels = ax.get_legend_handles_labels()
scatter_handles = [
    Line2D(
        [0],
        [0],
        marker=style["marker"],
        color="w",  # 标记内部颜色设为白色，仅显示边框
        markerfacecolor=style["facecolor"],
        markersize=8,
        label=f"{author}",
    )
    for author, style in author_styles.items()
]

fig.legend(
    handles=curve_handles + scatter_handles,
    loc="lower center",
    bbox_to_anchor=(0.5, 0),
    ncol=4,
    fontsize=9,
)
plt.tight_layout(rect=[0, 0.15, 1, 1])

# --- 新增：导出三组六条曲线数据到 Excel ---
export_df = pd.DataFrame({
    "T(K)": T_values,
    "Xδ′e_ThisInvestigation": x_black_left,
    "Xαe_ThisInvestigation": x_black_right,
    "Xδ′e_HallstedtKim": x_hallstedt_left,
    "Xαe_HallstedtKim": x_hallstedt_right,
    "Xδ′e_Khachaturyan": x_khacha_left,
    "Xαe_Khachaturyan": x_khacha_right,
})
export_path = "Al_Li_phase_boundaries_curves.xlsx"
# 使用 openpyxl 写出多工作表：曲线 + Table6/7 实验数据
try:
    with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Curves")
        df_table6.to_excel(writer, index=False, sheet_name="Table6_Exp_Xαe")
        df_table7.to_excel(writer, index=False, sheet_name="Table7_Exp_Xδ′e")
    print(f"已导出曲线与实验数据到 Excel: {export_path}")
except Exception as e:
    print("导出 Excel 失败:", e)

# --- 新增：保存一张包含所有曲线的 PNG ---
fig_path = "phase_boundaries.png"
try:
    fig.savefig(fig_path, dpi=300)
    print(f"已保存 PNG 图: {fig_path}")
except Exception as e:
    print("保存 PNG 失败:", e)

plt.show()
