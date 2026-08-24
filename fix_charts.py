"""Fix 3 charts: Double Top, Ascending Triangle, Wedge — better pattern shapes."""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "trevor_charts")

TV_DARK = {
    'bg': '#131722',
    'candle_up': '#26a69a',
    'candle_down': '#ef5350',
    'grid': '#1e222d',
    'text': '#d1d4dc',
    'axis': '#363a45',
}


def plot_candlestick(ax, opens, highs, lows, closes):
    width = 0.6
    for i in range(len(opens)):
        if closes[i] >= opens[i]:
            color = TV_DARK['candle_up']
            body_low, body_high = opens[i], closes[i]
        else:
            color = TV_DARK['candle_down']
            body_low, body_high = closes[i], opens[i]
        ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=0.8)
        ax.bar(i, body_high - body_low, bottom=body_low, width=width,
               color=color, edgecolor=color, linewidth=0.5)


def setup_axes(fig, ax, ticker, timeframe, n):
    ax.set_facecolor(TV_DARK['bg'])
    fig.patch.set_facecolor(TV_DARK['bg'])
    ax.tick_params(colors=TV_DARK['text'], labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_color(TV_DARK['axis'])
    ax.spines['left'].set_color(TV_DARK['axis'])
    ax.spines['bottom'].set_color(TV_DARK['axis'])
    ax.grid(True, alpha=0.15, color=TV_DARK['grid'])
    ax.set_xlim(-2, n + 2)
    ax.set_title(f"{ticker}  ·  NSE  ·  {timeframe}", color=TV_DARK['text'],
                fontsize=11, loc='left', pad=10, fontfamily='monospace')
    ax.text(0.99, 0.02, "TradingView", transform=ax.transAxes, fontsize=9,
            color='#555555', ha='right', va='bottom', fontfamily='sans-serif')
    ax.set_ylabel('Price (INR)', color=TV_DARK['text'], fontsize=10)


def draw_line(ax, x1, y1, x2, y2, color='#2196F3', style='--', lw=2, label=None):
    ax.plot([x1, x2], [y1, y2], color=color, linestyle=style, linewidth=lw, alpha=0.85)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, label, color=color, fontsize=9, ha='center', va='bottom',
                fontweight='bold', bbox=dict(boxstyle='round,pad=0.3',
                facecolor=TV_DARK['bg'], edgecolor=color, alpha=0.8))


def draw_circle(ax, x, y, r, color, label=None, pos='top'):
    circle = plt.Circle((x, y), r, fill=False, edgecolor=color, linewidth=2.5)
    ax.add_patch(circle)
    if label:
        offset = r + 2 if pos == 'top' else -(r + 2)
        va = 'bottom' if pos == 'top' else 'top'
        ax.text(x, y + offset, label, color=color, fontsize=9, ha='center',
                va=va, fontweight='bold')


def make_ohlcv_from_path(price_path, volatility=0.015):
    """Generate OHLCV from a defined price path (close prices)."""
    n = len(price_path)
    opens, highs, lows, closes = [], [], [], []
    for i in range(n):
        c = price_path[i]
        o = price_path[i - 1] if i > 0 else c * (1 + np.random.normal(0, 0.003))
        wick = abs(np.random.normal(0, volatility * 0.4 * c))
        h = max(o, c) + wick
        l = min(o, c) - abs(np.random.normal(0, volatility * 0.4 * c))
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
    return opens, highs, lows, closes


def fix_double_top():
    """Axis Bank Monthly - clean double top with two clear peaks."""
    np.random.seed(42)
    n = 100

    # Define price path: rise -> peak1 -> dip -> peak2 (same level) -> decline
    path = []
    for i in range(n):
        if i < 10:
            p = 850 + i * 8  # uptrend
        elif i < 20:
            p = 930 + (i - 10) * 7  # continue up
        elif i < 30:
            p = 1000 + (i - 20) * 3  # approach peak 1
        elif i == 30:
            p = 1035  # peak 1
        elif i < 40:
            p = 1035 - (i - 30) * 6  # pullback
        elif i < 45:
            p = 975 - (i - 40) * 3  # neckline area ~960
        elif i < 55:
            p = 960 + (i - 45) * 7  # rise to peak 2
        elif i == 55:
            p = 1030  # peak 2
        elif i < 65:
            p = 1030 - (i - 55) * 5  # pullback from peak 2
        elif i < 72:
            p = 980 - (i - 65) * 4  # approach neckline
        elif i < 80:
            p = 952 - (i - 72) * 5  # break neckline
        else:
            p = 912 - (i - 80) * 6  # decline
        path.append(p + np.random.normal(0, 4))

    o, h, l, c = make_ohlcv_from_path(path, 0.008)

    fig, ax = plt.subplots(figsize=(14, 7))
    plot_candlestick(ax, o, h, l, c)
    setup_axes(fig, ax, "AXISBANK", "Monthly", n)

    draw_circle(ax, 30, max(h[28:33]), 3.5, '#FF5252', 'Top 1')
    draw_circle(ax, 55, max(h[53:58]), 3.5, '#FF5252', 'Top 2')

    resistance_y = (max(h[28:33]) + max(h[53:58])) / 2
    draw_line(ax, 20, resistance_y, 65, resistance_y, '#FF9800', ':', 1.5, 'Resistance')

    neckline_y = min(l[40:50])
    draw_line(ax, 15, neckline_y, 80, neckline_y, '#2196F3', '--', 2, 'Neckline')

    ax.annotate('Breakdown', xy=(75, neckline_y - 15), fontsize=10, color='#FF5252',
                fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#FF5252', lw=2),
                xytext=(82, neckline_y + 15))

    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "chart_01_double_top.png"), dpi=150,
                bbox_inches='tight', facecolor=TV_DARK['bg'])
    plt.close()
    print("Fixed: Double Top (Axis Bank)")


def fix_ascending_triangle():
    """BPCL Daily - flat resistance with rising lows."""
    np.random.seed(600)
    n = 120

    resistance = 478
    path = []
    for i in range(n):
        if i < 10:
            p = 350 + i * 8  # initial rise
        elif i < 15:
            p = 430 + (i - 10) * 6
        elif i < 20:
            p = 460 + (i - 15) * 3  # approach resistance
        elif i == 20:
            p = 475  # touch resistance
        elif i < 30:
            p = 475 - (i - 20) * 5  # pullback to ~425
        elif i < 35:
            p = 425 + (i - 30) * 0.5  # low 1 ~427
        elif i < 45:
            p = 427 + (i - 35) * 5  # rise back
        elif i == 45:
            p = 477  # touch resistance again
        elif i < 55:
            p = 477 - (i - 45) * 4  # pullback to ~437
        elif i < 60:
            p = 437 + (i - 55) * 1  # low 2 ~442 (higher low)
        elif i < 70:
            p = 442 + (i - 60) * 3.5  # rise
        elif i == 70:
            p = 476  # touch resistance
        elif i < 78:
            p = 476 - (i - 70) * 3  # pullback to ~452
        elif i < 82:
            p = 452 + (i - 78) * 1  # low 3 ~456 (higher low)
        elif i < 90:
            p = 456 + (i - 82) * 3  # rise to resistance
        elif i == 90:
            p = 478  # touch resistance
        elif i < 95:
            p = 478 - (i - 90) * 2  # small pullback ~468
        elif i < 100:
            p = 468 + (i - 95) * 3  # breakout attempt
        elif i < 105:
            p = 483 + (i - 100) * 4  # breakout!
        else:
            p = 503 + (i - 105) * 5  # post-breakout rally
        path.append(p + np.random.normal(0, 3))

    o, h, l, c = make_ohlcv_from_path(path, 0.006)

    # Cap highs during pattern formation to not exceed resistance much
    for i in range(15, 95):
        h[i] = min(h[i], resistance + 4)

    fig, ax = plt.subplots(figsize=(14, 7))
    plot_candlestick(ax, o, h, l, c)
    setup_axes(fig, ax, "BPCL", "Daily", n)

    draw_line(ax, 15, resistance, 95, resistance, '#FF5252', '-', 2.5,
              'Flat Upper Trend Line')

    # Rising lower trendline: connecting the higher lows
    low1_x, low1_y = 32, min(l[28:36])
    low3_x, low3_y = 80, min(l[76:84])
    draw_line(ax, low1_x, low1_y, low3_x, low3_y, '#4CAF50', '-', 2.5,
              'Rising Lower Trend Line')

    mid_x = 55
    mid_y = (resistance + (low1_y + low3_y) / 2) / 2
    ax.text(mid_x, mid_y, 'Ascending Triangle\nPattern Formation',
            color='#2196F3', fontsize=11, ha='center', va='center',
            fontweight='bold', alpha=0.5)

    ax.annotate('Breakout', xy=(102, resistance + 15), fontsize=10,
                color='#4CAF50', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=2),
                xytext=(108, resistance + 40))

    # Price labels
    ax.text(2, resistance + 3, f'{resistance:.2f}', color='#FF5252',
            fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FF5252',
                     edgecolor='#FF5252', alpha=0.15))
    ax.text(2, min(l[0:5]) - 2, f'{min(l[0:5]):.2f}', color='#4CAF50',
            fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#4CAF50',
                     edgecolor='#4CAF50', alpha=0.15))

    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "chart_07_ascending_triangle.png"), dpi=150,
                bbox_inches='tight', facecolor=TV_DARK['bg'])
    plt.close()
    print("Fixed: Ascending Triangle (BPCL)")


def fix_wedge():
    """Tata Motors 4 Hour - rising wedge with both trendlines sloping up, converging."""
    np.random.seed(900)
    n = 110

    path = []
    for i in range(n):
        if i < 8:
            p = 650 + i * 10  # initial rise
        elif i < 15:
            p = 730 + (i - 8) * 5
        elif i < 80:
            # Rising wedge: oscillate between rising support and resistance
            # Both lines slope up but converge
            progress = (i - 15) / 65
            upper = 765 + progress * 80  # upper: 765 -> 845
            lower = 700 + progress * 110  # lower: 700 -> 810 (steeper)
            cycle = (i - 15) % 16
            if cycle < 8:
                # Rise toward upper
                frac = cycle / 8
                p = lower + (upper - lower) * (0.3 + 0.7 * frac)
            else:
                # Fall toward lower
                frac = (cycle - 8) / 8
                p = upper - (upper - lower) * (0.3 + 0.7 * frac)
        elif i < 85:
            p = 830 - (i - 80) * 4  # start of breakdown
        elif i < 95:
            p = 810 - (i - 85) * 8  # breakdown
        else:
            p = 730 - (i - 95) * 7  # sharp decline
        path.append(p + np.random.normal(0, 4))

    o, h, l, c = make_ohlcv_from_path(path, 0.008)

    fig, ax = plt.subplots(figsize=(14, 7))
    plot_candlestick(ax, o, h, l, c)
    setup_axes(fig, ax, "TATAMOTORS", "4 Hour", n)

    # Upper trendline (slower rise)
    draw_line(ax, 15, 770, 80, 848, '#FF5252', '-', 2.5, 'Upper Trendline')
    # Lower trendline (steeper rise, converging)
    draw_line(ax, 15, 700, 80, 812, '#4CAF50', '-', 2.5, 'Lower Trendline')

    ax.text(48, 770, 'Rising Wedge\n(Bearish)', color='#FF9800',
            fontsize=12, ha='center', va='center', fontweight='bold', alpha=0.6)

    ax.annotate('Breakdown', xy=(88, 770), fontsize=10, color='#FF5252',
                fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#FF5252', lw=2),
                xytext=(95, 800))

    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "chart_10_wedge.png"), dpi=150,
                bbox_inches='tight', facecolor=TV_DARK['bg'])
    plt.close()
    print("Fixed: Wedge (Tata Motors)")


if __name__ == "__main__":
    fix_double_top()
    fix_ascending_triangle()
    fix_wedge()
    print("All 3 charts fixed!")
