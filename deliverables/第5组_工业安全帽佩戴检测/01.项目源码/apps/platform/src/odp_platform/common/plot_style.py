"""matplotlib 学术绘图风格（可选）。"""

def apply_academic_style() -> None:
    """应用学术发表级 matplotlib 绘图风格。"""
    try:
        import matplotlib.pyplot as plt
        plt.style.use("seaborn-v0_8-whitegrid")
        plt.rcParams.update({
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        })
    except ImportError:
        pass
