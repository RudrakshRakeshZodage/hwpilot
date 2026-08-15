"""Generate high-resolution dark-themed sequence diagram image for HwPilot README & PyPI."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, ax = plt.subplots(figsize=(16, 9.5), dpi=200)
fig.patch.set_facecolor("#0B0F19")
ax.set_facecolor("#0B0F19")
ax.set_xlim(0, 1600)
ax.set_ylim(0, 950)
ax.axis("off")

# Participants configuration
actors = [
    {"name": "User (CLI)", "x": 130, "color": "#38BDF8"},
    {"name": "Hardware Detector", "x": 390, "color": "#818CF8"},
    {"name": "Compatibility Engine", "x": 670, "color": "#C084FC"},
    {"name": "Environment Manager", "x": 950, "color": "#F472B6"},
    {"name": "PyTorch Index CDN", "x": 1220, "color": "#FB923C"},
    {"name": "GPU Tensor Verifier", "x": 1470, "color": "#4ADE80"},
]

top_y = 860
bottom_y = 70

# Draw Top and Bottom Actor Boxes and Lifelines
for act in actors:
    x = act["x"]
    col = act["color"]
    
    # Lifeline (vertical dashed line)
    ax.plot([x, x], [bottom_y + 35, top_y - 25], color="#273142", linestyle="--", linewidth=1.5, zorder=1)
    
    # Top Box
    box_w, box_h = 190, 48
    rect_top = patches.FancyBboxPatch(
        (x - box_w/2, top_y - box_h/2), box_w, box_h,
        boxstyle="round,pad=0.2,rounding_size=8",
        facecolor="#161F30", edgecolor=col, linewidth=1.5, zorder=3
    )
    ax.add_patch(rect_top)
    ax.text(x, top_y, act["name"], color="#FFFFFF", fontsize=10.5, fontweight="bold", ha="center", va="center", zorder=4)

    # Bottom Box
    rect_bot = patches.FancyBboxPatch(
        (x - box_w/2, bottom_y - box_h/2), box_w, box_h,
        boxstyle="round,pad=0.2,rounding_size=8",
        facecolor="#161F30", edgecolor="#374151", linewidth=1.2, zorder=3
    )
    ax.add_patch(rect_bot)
    ax.text(x, bottom_y, act["name"], color="#9CA3AF", fontsize=9.5, fontweight="bold", ha="center", va="center", zorder=4)

# Steps Configuration
steps = [
    {"num": 1, "from": 130, "to": 390, "y": 780, "text": "Execute: hwpilot setup -y", "dashed": False, "color": "#38BDF8"},
    {"num": 2, "from": 390, "to": 390, "y": 715, "text": "Probe CPU, GPU (nvidia-smi), OS & Python", "self": True, "color": "#818CF8"},
    {"num": 3, "from": 390, "to": 670, "y": 645, "text": "Hardware Specs (RTX 4060, Driver 610.74, Py 3.13)", "dashed": True, "color": "#818CF8"},
    {"num": 4, "from": 670, "to": 670, "y": 580, "text": "Match Driver vs CUDA Matrix (defaults.json)", "self": True, "color": "#C084FC"},
    {"num": 5, "from": 670, "to": 130, "y": 510, "text": "Display Resolved Plan (PyTorch 2.6.0 + CUDA 12.4)", "dashed": True, "color": "#C084FC"},
    {"num": 6, "from": 130, "to": 950, "y": 440, "text": "Create Isolated Virtual Environment (./hwpilot-env)", "dashed": False, "color": "#F472B6"},
    {"num": 7, "from": 950, "to": 1220, "y": 370, "text": "Request & Stream CUDA 12.4 Wheels (~2.53 GB)", "dashed": False, "color": "#FB923C"},
    {"num": 8, "from": 1220, "to": 950, "y": 300, "text": "Extract & Unpack PyTorch DLLs into ./hwpilot-env", "dashed": True, "color": "#FB923C"},
    {"num": 9, "from": 950, "to": 1470, "y": 230, "text": "Execute GPU Tensor Matrix Multiplication (torch.mm)", "dashed": False, "color": "#4ADE80"},
    {"num": 10, "from": 1470, "to": 130, "y": 160, "text": "Verification PASSED: GPU Accelerated • manifest.json Saved", "dashed": True, "color": "#4ADE80"},
]

# Draw Arrows & Step Labels
for s in steps:
    y = s["y"]
    col = s["color"]
    num_str = str(s["num"])
    
    if s.get("self"):
        # Self loop
        x = s["from"]
        loop_w, loop_h = 75, 26
        ax.annotate(
            "", xy=(x, y - loop_h), xytext=(x, y),
            arrowprops=dict(arrowstyle="->", color=col, lw=1.8, connectionstyle="angle,angleA=0,angleB=90,rad=10")
        )
        # Step Number Badge
        circle = patches.Circle((x + 18, y - loop_h/2), 12, facecolor="#1E293B", edgecolor=col, linewidth=1.2, zorder=5)
        ax.add_patch(circle)
        ax.text(x + 18, y - loop_h/2, num_str, color="#FFFFFF", fontsize=8.5, fontweight="bold", ha="center", va="center", zorder=6)
        
        # Text
        ax.text(x + 40, y - loop_h/2, s["text"], color="#E2E8F0", fontsize=9.5, va="center", ha="left", zorder=6)
    else:
        x_from = s["from"]
        x_to = s["to"]
        style = "--" if s.get("dashed") else "-"
        
        # Arrow
        ax.annotate(
            "", xy=(x_to, y), xytext=(x_from, y),
            arrowprops=dict(
                arrowstyle="-|>",
                color=col,
                lw=1.8,
                linestyle=style,
                mutation_scale=14
            ),
            zorder=3
        )
        
        # Midpoint for Badge & Label
        x_mid = (x_from + x_to) / 2
        
        # Badge
        badge_x = x_mid - 15 if x_from < x_to else x_mid + 15
        circle = patches.Circle((badge_x, y + 14), 11, facecolor="#1E293B", edgecolor=col, linewidth=1.2, zorder=5)
        ax.add_patch(circle)
        ax.text(badge_x, y + 14, num_str, color="#FFFFFF", fontsize=8, fontweight="bold", ha="center", va="center", zorder=6)
        
        # Text Box / Label
        offset_x = badge_x + 16 if x_from < x_to else badge_x - 16
        ha_align = "left" if x_from < x_to else "right"
        ax.text(offset_x, y + 14, s["text"], color="#E2E8F0", fontsize=9.2, fontweight="500", va="center", ha=ha_align, zorder=6)

plt.tight_layout()
plt.savefig("architecture.png", dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
print("Saved architecture.png successfully!")
