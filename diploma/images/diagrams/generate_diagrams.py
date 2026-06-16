#!/usr/bin/env python3
"""Generate diploma/presentation diagrams for TLAS/BLAS/BVH topic."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np

OUT = Path(__file__).resolve().parent
DPI = 200

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.unicode_minus": False,
})


def save(fig, name: str):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  {name}.png / .pdf")


def box(ax, xy, w, h, text, fc="#E8F0FE", ec="#1A73E8", fontsize=9, weight="normal"):
    x, y = xy
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.4, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, weight=weight, wrap=True)
    return (x, y, w, h)


def arrow(ax, p1, p2, color="#444444"):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.2, color=color, connectionstyle="arc3,rad=0.0",
    ))


def diagram_tlas_blas():
    """Scene architecture: testGI → BVH → TLAS → BLAS."""
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Архитектура ray tracing в testGI: сцена, BVH, TLAS и BLAS", fontsize=13, weight="bold", pad=12)

    # Top: application layer
    box(ax, (0.4, 5.7), 10.2, 0.9, "testGI: 16 инстансов дома (4×4), RTSM, фиксированная камера", fc="#FFF8E1", ec="#F9A825", fontsize=10)

    # BVH subsystem
    box(ax, (0.4, 4.5), 10.2, 1.0,
        "Подсистема bvh:: (Context «GI»)\n"
        "add_mesh / add_instance  →  bvh::build  →  TLAS + BLAS на GPU",
        fc="#E3F2FD", ec="#1565C0", fontsize=9)

    arrow(ax, (5.5, 5.7), (5.5, 5.5))

    # TLAS
    tlas = box(ax, (1.0, 2.8), 9.0, 1.4,
               "TLAS (Top-Level Acceleration Structure)\n"
               "Дерево инстансов: каждый лист — ссылка на BLAS + transform (mat43f)\n"
               "16 домов × K кластеров = 16·K инстансов в TLAS",
               fc="#F3E5F5", ec="#7B1FA2", fontsize=9, weight="bold")

    arrow(ax, (5.5, 4.5), (5.5, 4.2))

    # BLAS row
    colors = ["#FFEBEE", "#E8F5E9", "#E0F7FA", "#FFF3E0"]
    labels = [
        "BLAS #1\n(K треуг.\nкластер 0)",
        "BLAS #2\n(кластер 1)",
        "…",
        "BLAS #K\n(кластер K−1)",
    ]
    xs = [0.6, 3.0, 5.4, 7.8]
    for i, (x, lab, c) in enumerate(zip(xs, labels, colors)):
        ec = ["#C62828", "#2E7D32", "#888888", "#EF6C00"][i]
        box(ax, (x, 0.5), 2.0, 1.8, lab, fc=c, ec=ec, fontsize=8)

    for x in xs[:2] + xs[3:]:
        arrow(ax, (x + 1.0, 2.8), (x + 1.0, 2.3))

    arrow(ax, (6.4, 2.8), (6.4, 2.3), color="#888888")

    # Side: one model
    box(ax, (0.4, 0.5), 0.0, 0.0, "", fc="none", ec="none")  # noop
    ax.text(10.2, 1.4,
            "Один дом = K BLAS\n(после MERGE-ALL)\n\nBaseline: ~10 BLAS\n(по RElem-ам)",
            ha="right", va="center", fontsize=8.5,
            bbox=dict(boxstyle="round", facecolor="#FAFAFA", edgecolor="#999999"))

    # Ray trace
    box(ax, (0.4, 0.05), 4.5, 0.35, "rtsm::do_trace — лучи обходят TLAS, затем попадают в BLAS", fc="#ECEFF1", ec="#546E7A", fontsize=8)
    save(fig, "01_scene_tlas_blas")


def diagram_baseline_vs_optimized():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    ax.set_title("Baseline vs MERGE-ALL: перекрытие AABB в TLAS", fontsize=13, weight="bold", pad=10)

    def draw_house_panel(ox, title, mode, time_ms, speedup):
        ax.text(ox + 2.5, 5.1, title, ha="center", fontsize=11, weight="bold")
        ax.text(ox + 2.5, 4.75, mode, ha="center", fontsize=8.5, color="#555555")

        # House outline
        house = Rectangle((ox + 0.8, 1.2), 3.4, 2.2, fill=False, edgecolor="#333333", linewidth=1.5)
        ax.add_patch(house)
        roof_x = [ox + 0.8, ox + 2.5, ox + 4.2]
        roof_y = [3.4, 4.3, 3.4]
        ax.fill(roof_x, roof_y, fill=False, edgecolor="#333333", linewidth=1.5)

        if "Baseline" in title:
            # overlapping big AABBs
            rng = np.random.default_rng(42)
            for i in range(8):
                cx = ox + 0.5 + rng.uniform(0, 3.5)
                cy = 1.0 + rng.uniform(0, 2.5)
                r = mpatches.FancyBboxPatch(
                    (cx - 1.5, cy - 1.0), 3.0, 2.5,
                    boxstyle="round,pad=0.01,rounding_size=0.05",
                    linewidth=1.2, edgecolor=plt.cm.tab10(i % 10), facecolor=plt.cm.tab10(i % 10), alpha=0.25,
                )
                ax.add_patch(r)
            ax.text(ox + 2.5, 0.55, "Каждый RElem → BLAS\nAABB ≈ весь дом\n→ сильные перекрытия", ha="center", fontsize=8)
        else:
            # spatial clusters
            clusters = [
                (ox + 0.9, 1.3, 1.0, 1.0, "#E53935"),
                (ox + 2.0, 1.3, 1.1, 1.0, "#43A047"),
                (ox + 3.2, 1.3, 0.9, 1.0, "#1E88E5"),
                (ox + 0.9, 2.4, 1.5, 0.9, "#FB8C00"),
                (ox + 2.5, 2.4, 1.6, 0.9, "#8E24AA"),
                (ox + 1.2, 3.5, 2.6, 0.5, "#00897B"),
            ]
            for x, y, w, h, c in clusters:
                ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor=c, alpha=0.55, linewidth=1))
            ax.text(ox + 2.5, 0.55, "Morton + split на K кластеров\n→ малые локальные BLAS\n→ мало перекрытий в TLAS", ha="center", fontsize=8)

        ax.text(ox + 2.5, 0.05, f"rtsm::do_trace ≈ {time_ms} мс  ({speedup})", ha="center", fontsize=9, weight="bold", color="#1565C0")

    draw_house_panel(0.3, "Baseline (K=0)", "bad_house: случайный split", "9,15", "×1")
    draw_house_panel(6.2, "MERGE-ALL (K=64)", "bad_house + оптимизация", "1,07", "×8,6")

    ax.annotate("", xy=(6.0, 2.5), xytext=(5.5, 2.5),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=2))
    save(fig, "02_baseline_vs_optimized")


def diagram_pipeline():
    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.set_title("Пайплайн метода MERGE-ALL (testgi_dynrend_bvh_pre)", fontsize=13, weight="bold", pad=10)

    steps = [
        ("1. Сбор\nRElem-ов\nLOD0", "#FFF3E0", "#EF6C00"),
        ("2. Morton-\nсортировка\nцентроидов", "#E8F5E9", "#2E7D32"),
        ("3. Split\nна K\nкластеров", "#E3F2FD", "#1565C0"),
        ("4. VB/IB\nна кластер", "#F3E5F5", "#7B1FA2"),
        ("5. bvh::\nadd_mesh", "#FFEBEE", "#C62828"),
        ("6. bvh::\nadd_instance\n×16 домов", "#E0F7FA", "#00838F"),
    ]
    w, h = 1.55, 1.5
    y = 1.2
    for i, (txt, fc, ec) in enumerate(steps):
        x = 0.35 + i * 1.95
        box(ax, (x, y), w, h, txt, fc=fc, ec=ec, fontsize=8.5)
        if i < len(steps) - 1:
            arrow(ax, (x + w + 0.02, y + h / 2), (x + 1.95 - 0.02, y + h / 2))

    box(ax, (0.35, 0.15), 11.3, 0.75,
        "Управление: settings.blk → bvhMergeAllRelems = K_req  |  "
        "K_eff = max(K_req, ⌈N/21845⌉)  |  per-RElem путь пропускается",
        fc="#FAFAFA", ec="#757575", fontsize=8.5)
    save(fig, "03_merge_all_pipeline")


def diagram_testgi_scene():
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_xlim(-20, 70)
    ax.set_ylim(-5, 55)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Тестовая сцена testGI: 4×4 инстанса, шаг 15 м", fontsize=13, weight="bold", pad=10)

    for row in range(4):
        for col in range(4):
            x, y = col * 15, row * 15
            ax.add_patch(Rectangle((x - 1.5, y - 1), 3, 2.5, facecolor="#BCAAA4", edgecolor="#5D4037", linewidth=0.8))
            ax.add_patch(plt.Polygon([[x - 1.5, y + 1.5], [x, y + 3], [x + 1.5, y + 1.5]], closed=True, facecolor="#8D6E63", edgecolor="#5D4037", linewidth=0.8))

    # Camera
    cam_x, cam_y = -16, 16
    ax.plot(cam_x, cam_y, "o", color="#1565C0", markersize=10)
    ax.annotate("Камера\n(fixed)", (cam_x, cam_y), xytext=(cam_x - 8, cam_y + 12),
                fontsize=9, color="#1565C0",
                arrowprops=dict(arrowstyle="-|>", color="#1565C0"))

    # Sun
    ax.annotate("", xy=(25, 45), xytext=(5, 50),
                arrowprops=dict(arrowstyle="-|>", color="#F9A825", lw=2))
    ax.text(2, 51, "Солнце\n(RTSM)", fontsize=9, color="#F57F17")

    ax.text(22.5, -3, "origin (0,0)", ha="center", fontsize=8, color="#666666")
    save(fig, "04_testgi_scene_layout")


def diagram_k_sweep():
    K = [0, 64, 96, 128, 192, 256]
    bad = [9.15, 1.07, 1.13, 1.22, 1.23, 1.30]
    real = [2.75, 1.01, 1.06, 1.06, 1.11, 1.18]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(K, bad, "o-", color="#C62828", linewidth=2, markersize=7, label="bad_house (случайный split)")
    ax.plot(K, real, "s-", color="#1565C0", linewidth=2, markersize=7, label="bad_house_new_mesh (материальный split)")

    ax.axvspan(64, 128, alpha=0.12, color="#43A047", label="Плато K_req ≈ 64…128")
    ax.set_xlabel("K_req (bvhMergeAllRelems)", fontsize=11)
    ax.set_ylabel("rtsm::do_trace, мс", fontsize=11)
    ax.set_title("Зависимость времени трассировки от K_req", fontsize=13, weight="bold")
    ax.set_xticks(K)
    ax.grid(True, alpha=0.35, linestyle="--")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, 10)
    save(fig, "05_k_sweep_chart")


def diagram_dagor_stack():
    """Layer cake: DX12 → d3d → bvh → rtsm."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Стек ПО: от GPU до rtsm::do_trace", fontsize=13, weight="bold", pad=10)

    layers = [
        ("DirectX 12 Raytracing\n(TLAS/BLAS API)", "#ECEFF1", "#546E7A", 4.8),
        ("Dagor d3d:: + drv3d_DX12\nсоздание / удаление AS", "#E3F2FD", "#1565C0", 3.8),
        ("gameLibs/bvh\nContext, add_mesh, build", "#F3E5F5", "#7B1FA2", 2.8),
        ("testGI hook\nMERGE-ALL preprocessing", "#FFF8E1", "#F9A825", 1.8),
        ("rtsm::do_trace\n(измеряемая метрика)", "#FFEBEE", "#C62828", 0.6),
    ]
    for text, fc, ec, y in layers:
        box(ax, (1.0, y), 6.0, 0.85, text, fc=fc, ec=ec, fontsize=9)
        if y > 0.6:
            arrow(ax, (4.0, y), (4.0, y - 0.05))

    save(fig, "06_software_stack")


def main():
    print(f"Output: {OUT}")
    diagram_tlas_blas()
    diagram_baseline_vs_optimized()
    diagram_pipeline()
    diagram_testgi_scene()
    diagram_k_sweep()
    diagram_dagor_stack()
    print("Done.")


if __name__ == "__main__":
    main()
