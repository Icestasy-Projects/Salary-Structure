import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.patches import FancyArrowPatch
from datetime import datetime, timedelta
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.colors import HexColor
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = "/home/user/Salary-Structure/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TV_GREEN = '#26a69a'
TV_RED = '#ef5350'
TV_BG = '#131722'
TV_GRID = '#2a2e39'
TV_TEXT = '#d1d4dc'
TV_LINE = '#2962ff'
TV_ANNOTATION = '#f7c548'
LABEL_COLOR = '#ffffff'

def generate_ohlc(n_days, base_price, volatility, trend_func):
    dates = pd.date_range(start='2026-01-05', periods=n_days, freq='B')
    prices = []
    current = base_price
    for i in range(n_days):
        t = i / n_days
        target = trend_func(t, base_price)
        current = current * 0.7 + target * 0.3
        noise = np.random.normal(0, volatility * current)
        current += noise
        o = current + np.random.normal(0, volatility * current * 0.3)
        c = current + np.random.normal(0, volatility * current * 0.3)
        h = max(o, c) + abs(np.random.normal(0, volatility * current * 0.5))
        l = min(o, c) - abs(np.random.normal(0, volatility * current * 0.5))
        vol = int(np.random.uniform(500000, 5000000))
        prices.append([o, h, l, c, vol])
    df = pd.DataFrame(prices, columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=dates)
    return df

def plot_candlestick(df, title, stock_name, exchange, timeframe, annotations=None, filename='chart.png'):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={'height_ratios': [4, 1]},
                                     facecolor=TV_BG)
    ax1.set_facecolor(TV_BG)
    ax2.set_facecolor(TV_BG)

    for i in range(len(df)):
        date = mdates.date2num(df.index[i])
        o, h, l, c = df.iloc[i]['Open'], df.iloc[i]['High'], df.iloc[i]['Low'], df.iloc[i]['Close']
        color = TV_GREEN if c >= o else TV_RED
        ax1.plot([date, date], [l, h], color=color, linewidth=0.8)
        body_bottom = min(o, c)
        body_height = abs(c - o)
        rect = plt.Rectangle((date - 0.3, body_bottom), 0.6, body_height,
                              facecolor=color, edgecolor=color, linewidth=0.5)
        ax1.add_patch(rect)

    ax1.set_xlim(mdates.date2num(df.index[0]) - 2, mdates.date2num(df.index[-1]) + 2)
    price_range = df['High'].max() - df['Low'].min()
    ax1.set_ylim(df['Low'].min() - price_range * 0.05, df['High'].max() + price_range * 0.1)

    ax1.grid(True, color=TV_GRID, alpha=0.5, linewidth=0.5)
    ax2.grid(True, color=TV_GRID, alpha=0.5, linewidth=0.5)

    ax1.tick_params(colors=TV_TEXT, labelsize=8)
    ax2.tick_params(colors=TV_TEXT, labelsize=8)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_color(TV_GRID)
    ax1.spines['left'].set_color(TV_GRID)
    ax1.spines['bottom'].set_color(TV_GRID)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_color(TV_GRID)
    ax2.spines['left'].set_color(TV_GRID)
    ax2.spines['bottom'].set_color(TV_GRID)

    header = f"{stock_name} - {timeframe} - {exchange}"
    ax1.text(0.01, 1.02, header, transform=ax1.transAxes, color=TV_TEXT,
             fontsize=10, fontweight='bold', va='bottom')

    last_c = df.iloc[-1]['Close']
    last_o = df.iloc[-1]['Open']
    price_color = TV_GREEN if last_c >= last_o else TV_RED
    ax1.text(0.01, 0.96, f"O {last_o:.2f}  H {df.iloc[-1]['High']:.2f}  L {df.iloc[-1]['Low']:.2f}  C {last_c:.2f}",
             transform=ax1.transAxes, color=price_color, fontsize=8, va='top')

    for i in range(len(df)):
        date = mdates.date2num(df.index[i])
        vol = df.iloc[i]['Volume']
        color = TV_GREEN if df.iloc[i]['Close'] >= df.iloc[i]['Open'] else TV_RED
        ax2.bar(date, vol, width=0.6, color=color, alpha=0.6)

    ax2.set_ylabel('Volume', color=TV_TEXT, fontsize=8)
    ax2.yaxis.label.set_color(TV_TEXT)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)

    fig.text(0.01, 0.01, 'TradingView', color='#787b86', fontsize=10, fontweight='bold',
             style='italic', va='bottom')

    if annotations:
        for ann in annotations:
            ann_type = ann.get('type', 'line')
            if ann_type == 'line':
                x1_idx, x2_idx = ann['x1'], ann['x2']
                y1, y2 = ann['y1'], ann['y2']
                d1 = mdates.date2num(df.index[min(x1_idx, len(df)-1)])
                d2 = mdates.date2num(df.index[min(x2_idx, len(df)-1)])
                style = ann.get('style', '-')
                lw = ann.get('lw', 1.5)
                color = ann.get('color', TV_LINE)
                ax1.plot([d1, d2], [y1, y2], color=color, linewidth=lw, linestyle=style)
            elif ann_type == 'hline':
                y = ann['y']
                color = ann.get('color', TV_LINE)
                style = ann.get('style', '--')
                ax1.axhline(y=y, color=color, linewidth=1.2, linestyle=style, alpha=0.7)
            elif ann_type == 'label':
                x_idx = ann['x']
                y = ann['y']
                text = ann['text']
                d = mdates.date2num(df.index[min(x_idx, len(df)-1)])
                color = ann.get('color', LABEL_COLOR)
                fontsize = ann.get('fontsize', 9)
                ax1.annotate(text, xy=(d, y), color=color, fontsize=fontsize,
                             fontweight='bold', ha='center', va='bottom',
                             bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e222d',
                                       edgecolor=TV_LINE, alpha=0.9))
            elif ann_type == 'arrow':
                x_idx = ann['x']
                y1, y2 = ann['y1'], ann['y2']
                d = mdates.date2num(df.index[min(x_idx, len(df)-1)])
                color = ann.get('color', TV_ANNOTATION)
                ax1.annotate('', xy=(d, y2), xytext=(d, y1),
                             arrowprops=dict(arrowstyle='->', color=color, lw=2))
            elif ann_type == 'circle':
                x_idx = ann['x']
                y = ann['y']
                d = mdates.date2num(df.index[min(x_idx, len(df)-1)])
                r = ann.get('r', 3)
                color = ann.get('color', TV_LINE)
                circle = plt.Circle((d, y), r, fill=False, color=color, linewidth=1.5)
                ax1.add_patch(circle)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=TV_BG, edgecolor='none')
    plt.close()
    return filepath


# ============ PATTERN GENERATORS ============

def make_double_top(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.15:
            return base * (1 + t * 2)
        elif t < 0.3:
            return base * 1.3 - (t - 0.15) * base * 1.5
        elif t < 0.45:
            return base * 1.05 + (t - 0.3) * base * 1.8
        elif t < 0.6:
            return base * 1.32 - (t - 0.45) * base * 2
        elif t < 0.75:
            return base * 1.0 - (t - 0.6) * base * 0.5
        else:
            return base * 0.92 - (t - 0.75) * base * 0.3
    df = generate_ohlc(80, 500, 0.008, trend)
    peak1_idx = df['High'].iloc[10:25].idxmax()
    peak2_idx = df['High'].iloc[30:45].idxmax()
    p1_i = df.index.get_loc(peak1_idx)
    p2_i = df.index.get_loc(peak2_idx)
    p1_val = df['High'].iloc[p1_i]
    p2_val = df['High'].iloc[p2_i]
    trough_idx = df['Low'].iloc[p1_i:p2_i].idxmin()
    t_i = df.index.get_loc(trough_idx)
    t_val = df['Low'].iloc[t_i]
    annotations = [
        {'type': 'line', 'x1': p1_i, 'x2': t_i, 'y1': p1_val, 'y2': t_val, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': t_i, 'x2': p2_i, 'y1': t_val, 'y2': p2_val, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': p2_i, 'x2': min(p2_i + 20, len(df)-1), 'y1': p2_val,
         'y2': df['Low'].iloc[min(p2_i+15, len(df)-1)], 'color': TV_LINE, 'lw': 2},
        {'type': 'hline', 'y': t_val, 'color': '#ff9800', 'style': '--'},
        {'type': 'label', 'x': p1_i, 'y': p1_val + 5, 'text': 'Top 1', 'color': '#ff5252'},
        {'type': 'label', 'x': p2_i, 'y': p2_val + 5, 'text': 'Top 2', 'color': '#ff5252'},
        {'type': 'label', 'x': t_i, 'y': t_val - 8, 'text': 'Neckline', 'color': '#ff9800'},
    ]
    return plot_candlestick(df, "Double Top", stock_name, exchange, timeframe, annotations, filename)

def make_double_bottom(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.15:
            return base * (1 - t * 1.5)
        elif t < 0.3:
            return base * 0.78 + (t - 0.15) * base * 1.5
        elif t < 0.45:
            return base * 1.0 - (t - 0.3) * base * 1.5
        elif t < 0.6:
            return base * 0.78 + (t - 0.45) * base * 2
        else:
            return base * 1.08 + (t - 0.6) * base * 0.8
    df = generate_ohlc(80, 450, 0.008, trend)
    bot1_idx = df['Low'].iloc[10:25].idxmin()
    bot2_idx = df['Low'].iloc[30:50].idxmin()
    b1_i = df.index.get_loc(bot1_idx)
    b2_i = df.index.get_loc(bot2_idx)
    b1_val = df['Low'].iloc[b1_i]
    b2_val = df['Low'].iloc[b2_i]
    peak_idx = df['High'].iloc[b1_i:b2_i].idxmax()
    pk_i = df.index.get_loc(peak_idx)
    pk_val = df['High'].iloc[pk_i]
    annotations = [
        {'type': 'line', 'x1': b1_i, 'x2': pk_i, 'y1': b1_val, 'y2': pk_val, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': pk_i, 'x2': b2_i, 'y1': pk_val, 'y2': b2_val, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': b2_i, 'x2': min(b2_i + 20, len(df)-1), 'y1': b2_val,
         'y2': df['High'].iloc[min(b2_i+15, len(df)-1)], 'color': TV_LINE, 'lw': 2},
        {'type': 'hline', 'y': pk_val, 'color': '#4caf50', 'style': '--'},
        {'type': 'label', 'x': b1_i, 'y': b1_val - 8, 'text': 'Bottom 1', 'color': '#4caf50'},
        {'type': 'label', 'x': b2_i, 'y': b2_val - 8, 'text': 'Bottom 2', 'color': '#4caf50'},
        {'type': 'label', 'x': pk_i, 'y': pk_val + 5, 'text': 'Neckline', 'color': '#4caf50'},
    ]
    return plot_candlestick(df, "Double Bottom", stock_name, exchange, timeframe, annotations, filename)

def make_triple_top(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.1:
            return base * (1 + t * 2.5)
        elif t < 0.2:
            return base * 1.25 - (t - 0.1) * base * 2
        elif t < 0.3:
            return base * 1.05 + (t - 0.2) * base * 2
        elif t < 0.4:
            return base * 1.25 - (t - 0.3) * base * 2
        elif t < 0.5:
            return base * 1.05 + (t - 0.4) * base * 2
        elif t < 0.6:
            return base * 1.25 - (t - 0.5) * base * 2
        elif t < 0.75:
            return base * 1.05 - (t - 0.6) * base * 1
        else:
            return base * 0.9 - (t - 0.75) * base * 0.5
    df = generate_ohlc(90, 600, 0.007, trend)
    p1_i = df['High'].iloc[5:18].idxmax()
    p2_i = df['High'].iloc[22:36].idxmax()
    p3_i = df['High'].iloc[40:54].idxmax()
    p1 = df.index.get_loc(p1_i)
    p2 = df.index.get_loc(p2_i)
    p3 = df.index.get_loc(p3_i)
    p1v = df['High'].iloc[p1]
    p2v = df['High'].iloc[p2]
    p3v = df['High'].iloc[p3]
    resistance = max(p1v, p2v, p3v)
    t1_i = df['Low'].iloc[p1:p2].idxmin()
    t2_i = df['Low'].iloc[p2:p3].idxmin()
    t1 = df.index.get_loc(t1_i)
    t2 = df.index.get_loc(t2_i)
    support = min(df['Low'].iloc[t1], df['Low'].iloc[t2])
    annotations = [
        {'type': 'hline', 'y': resistance, 'color': '#ff5252', 'style': '--'},
        {'type': 'hline', 'y': support, 'color': '#ff9800', 'style': '--'},
        {'type': 'label', 'x': p1, 'y': p1v + 5, 'text': 'Top 1', 'color': '#ff5252'},
        {'type': 'label', 'x': p2, 'y': p2v + 5, 'text': 'Top 2', 'color': '#ff5252'},
        {'type': 'label', 'x': p3, 'y': p3v + 5, 'text': 'Top 3', 'color': '#ff5252'},
        {'type': 'label', 'x': 3, 'y': resistance + 5, 'text': 'Resistance', 'color': '#ff5252', 'fontsize': 8},
        {'type': 'label', 'x': 3, 'y': support - 8, 'text': 'Support / Neckline', 'color': '#ff9800', 'fontsize': 8},
    ]
    return plot_candlestick(df, "Triple Top", stock_name, exchange, timeframe, annotations, filename)

def make_triple_bottom(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.1:
            return base * (1 - t * 2)
        elif t < 0.2:
            return base * 0.8 + (t - 0.1) * base * 1.5
        elif t < 0.3:
            return base * 0.95 - (t - 0.2) * base * 1.5
        elif t < 0.4:
            return base * 0.8 + (t - 0.3) * base * 1.5
        elif t < 0.5:
            return base * 0.95 - (t - 0.4) * base * 1.5
        elif t < 0.6:
            return base * 0.8 + (t - 0.5) * base * 2
        elif t < 0.75:
            return base * 1.0 + (t - 0.6) * base * 1
        else:
            return base * 1.15 + (t - 0.75) * base * 0.5
    df = generate_ohlc(90, 350, 0.007, trend)
    b1_i = df['Low'].iloc[5:18].idxmin()
    b2_i = df['Low'].iloc[22:36].idxmin()
    b3_i = df['Low'].iloc[40:54].idxmin()
    b1 = df.index.get_loc(b1_i)
    b2 = df.index.get_loc(b2_i)
    b3 = df.index.get_loc(b3_i)
    b1v = df['Low'].iloc[b1]
    b2v = df['Low'].iloc[b2]
    b3v = df['Low'].iloc[b3]
    support = min(b1v, b2v, b3v)
    pk1_i = df['High'].iloc[b1:b2].idxmax()
    pk2_i = df['High'].iloc[b2:b3].idxmax()
    pk1 = df.index.get_loc(pk1_i)
    pk2 = df.index.get_loc(pk2_i)
    resistance = max(df['High'].iloc[pk1], df['High'].iloc[pk2])
    annotations = [
        {'type': 'hline', 'y': support, 'color': '#4caf50', 'style': '--'},
        {'type': 'hline', 'y': resistance, 'color': '#ff9800', 'style': '--'},
        {'type': 'label', 'x': b1, 'y': b1v - 5, 'text': 'Bottom 1', 'color': '#4caf50'},
        {'type': 'label', 'x': b2, 'y': b2v - 5, 'text': 'Bottom 2', 'color': '#4caf50'},
        {'type': 'label', 'x': b3, 'y': b3v - 5, 'text': 'Bottom 3', 'color': '#4caf50'},
        {'type': 'label', 'x': 3, 'y': support - 5, 'text': 'Support', 'color': '#4caf50', 'fontsize': 8},
        {'type': 'label', 'x': 3, 'y': resistance + 3, 'text': 'Neckline / Resistance', 'color': '#ff9800', 'fontsize': 8},
    ]
    return plot_candlestick(df, "Triple Bottom", stock_name, exchange, timeframe, annotations, filename)

def make_rectangle(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        cycle = np.sin(t * 8 * np.pi) * base * 0.06
        return base + cycle
    df = generate_ohlc(100, 800, 0.006, trend)
    mid_start = 10
    mid_end = 85
    resistance = df['High'].iloc[mid_start:mid_end].nlargest(5).mean()
    support = df['Low'].iloc[mid_start:mid_end].nsmallest(5).mean()
    annotations = [
        {'type': 'line', 'x1': mid_start, 'x2': mid_end, 'y1': resistance, 'y2': resistance,
         'color': '#ff5252', 'lw': 2, 'style': '-'},
        {'type': 'line', 'x1': mid_start, 'x2': mid_end, 'y1': support, 'y2': support,
         'color': '#4caf50', 'lw': 2, 'style': '-'},
        {'type': 'label', 'x': mid_end - 5, 'y': resistance + 5, 'text': 'Resistance', 'color': '#ff5252'},
        {'type': 'label', 'x': mid_end - 5, 'y': support - 8, 'text': 'Support', 'color': '#4caf50'},
        {'type': 'label', 'x': (mid_start + mid_end) // 2, 'y': (resistance + support) / 2,
         'text': 'Trading Range / BOX', 'color': '#ffffff', 'fontsize': 10},
    ]
    return plot_candlestick(df, "Rectangle (Trading Range)", stock_name, exchange, timeframe, annotations, filename)

def make_descending_triangle(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.8:
            upper = base * 1.15 * (1 - t * 0.3)
            lower = base * 0.92
            mid = (upper + lower) / 2
            cycle = np.sin(t * 6 * np.pi) * (upper - lower) * 0.3
            return mid + cycle
        else:
            return base * 0.88 - (t - 0.8) * base * 0.4
    df = generate_ohlc(85, 950, 0.006, trend)
    support_level = df['Low'].iloc[5:70].nsmallest(8).mean()
    h1 = df['High'].iloc[3:15].max()
    h2 = df['High'].iloc[25:40].max()
    h3 = df['High'].iloc[50:65].max()
    h1_i = df['High'].iloc[3:15].idxmax()
    h3_i = df['High'].iloc[50:65].idxmax()
    h1_loc = df.index.get_loc(h1_i)
    h3_loc = df.index.get_loc(h3_i)
    annotations = [
        {'type': 'line', 'x1': 5, 'x2': 70, 'y1': support_level, 'y2': support_level,
         'color': '#4caf50', 'lw': 2},
        {'type': 'line', 'x1': h1_loc, 'x2': h3_loc, 'y1': h1, 'y2': h3,
         'color': '#ff5252', 'lw': 2},
        {'type': 'label', 'x': 70, 'y': support_level - 10, 'text': 'Support (Flat)', 'color': '#4caf50'},
        {'type': 'label', 'x': h1_loc, 'y': h1 + 8, 'text': 'Lower Highs', 'color': '#ff5252'},
        {'type': 'label', 'x': min(75, len(df)-1), 'y': support_level - 25, 'text': 'Breakdown',
         'color': '#ff9800', 'fontsize': 9},
    ]
    return plot_candlestick(df, "Descending Triangle", stock_name, exchange, timeframe, annotations, filename)

def make_ascending_triangle(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.8:
            upper = base * 1.12
            lower = base * 0.88 + t * base * 0.25
            mid = (upper + lower) / 2
            cycle = np.sin(t * 6 * np.pi) * (upper - lower) * 0.3
            return mid + cycle
        else:
            return base * 1.15 + (t - 0.8) * base * 0.5
    df = generate_ohlc(85, 280, 0.006, trend)
    resistance_level = df['High'].iloc[5:70].nlargest(8).mean()
    l1_i = df['Low'].iloc[3:15].idxmin()
    l3_i = df['Low'].iloc[50:65].idxmin()
    l1_loc = df.index.get_loc(l1_i)
    l3_loc = df.index.get_loc(l3_i)
    l1 = df['Low'].iloc[l1_loc]
    l3 = df['Low'].iloc[l3_loc]
    annotations = [
        {'type': 'line', 'x1': 5, 'x2': 70, 'y1': resistance_level, 'y2': resistance_level,
         'color': '#ff5252', 'lw': 2},
        {'type': 'line', 'x1': l1_loc, 'x2': l3_loc, 'y1': l1, 'y2': l3,
         'color': '#4caf50', 'lw': 2},
        {'type': 'label', 'x': 70, 'y': resistance_level + 3, 'text': 'Resistance (Flat)', 'color': '#ff5252'},
        {'type': 'label', 'x': l3_loc, 'y': l3 - 4, 'text': 'Higher Lows', 'color': '#4caf50'},
        {'type': 'label', 'x': min(78, len(df)-1), 'y': resistance_level + 8, 'text': 'Breakout',
         'color': '#ff9800', 'fontsize': 9},
    ]
    return plot_candlestick(df, "Ascending Triangle", stock_name, exchange, timeframe, annotations, filename)

def make_symmetrical_triangle(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.8:
            amplitude = base * 0.12 * (1 - t * 0.9)
            cycle = np.sin(t * 7 * np.pi) * amplitude
            return base + cycle
        else:
            return base * 1.02 + (t - 0.8) * base * 0.5
    df = generate_ohlc(85, 1200, 0.005, trend)
    h1_i = df['High'].iloc[3:15].idxmax()
    h2_i = df['High'].iloc[40:55].idxmax()
    l1_i = df['Low'].iloc[10:25].idxmin()
    l2_i = df['Low'].iloc[45:60].idxmin()
    h1_loc = df.index.get_loc(h1_i)
    h2_loc = df.index.get_loc(h2_i)
    l1_loc = df.index.get_loc(l1_i)
    l2_loc = df.index.get_loc(l2_i)
    annotations = [
        {'type': 'line', 'x1': h1_loc, 'x2': min(h2_loc + 15, len(df)-1),
         'y1': df['High'].iloc[h1_loc],
         'y2': df['High'].iloc[h2_loc] - (df['High'].iloc[h1_loc] - df['High'].iloc[h2_loc]) * 0.3,
         'color': '#ff5252', 'lw': 2},
        {'type': 'line', 'x1': l1_loc, 'x2': min(l2_loc + 15, len(df)-1),
         'y1': df['Low'].iloc[l1_loc],
         'y2': df['Low'].iloc[l2_loc] + (df['Low'].iloc[l2_loc] - df['Low'].iloc[l1_loc]) * 0.3,
         'color': '#4caf50', 'lw': 2},
        {'type': 'label', 'x': h1_loc, 'y': df['High'].iloc[h1_loc] + 10, 'text': 'Lower Highs', 'color': '#ff5252'},
        {'type': 'label', 'x': l1_loc, 'y': df['Low'].iloc[l1_loc] - 12, 'text': 'Higher Lows', 'color': '#4caf50'},
        {'type': 'label', 'x': min(70, len(df)-1), 'y': df['Close'].iloc[min(70, len(df)-1)] + 15,
         'text': 'Apex / Convergence', 'color': '#ffffff', 'fontsize': 9},
    ]
    return plot_candlestick(df, "Symmetrical Triangle", stock_name, exchange, timeframe, annotations, filename)

def make_diamond_top(stock_name, exchange, timeframe, filename):
    def trend(t, base):
        if t < 0.1:
            return base * (1 + t * 2)
        elif t < 0.25:
            amplitude = (t - 0.1) / 0.15
            return base * 1.2 + np.sin(t * 12) * base * 0.08 * amplitude
        elif t < 0.5:
            amplitude = 1 - (t - 0.25) / 0.25
            return base * 1.2 + np.sin(t * 12) * base * 0.08 * amplitude
        elif t < 0.6:
            return base * 1.2 - (t - 0.5) * base * 0.5
        else:
            return base * 1.15 - (t - 0.6) * base * 0.8
    df = generate_ohlc(90, 1300, 0.006, trend)
    region = df.iloc[10:70]
    h1 = region['High'].iloc[:15].max()
    h2 = region['High'].iloc[15:30].max()
    h3 = region['High'].iloc[30:45].max()
    l1 = region['Low'].iloc[:15].min()
    l2 = region['Low'].iloc[15:30].min()
    l3 = region['Low'].iloc[30:45].min()
    h1_loc = 10 + region['High'].iloc[:15].argmax()
    h2_loc = 10 + 15 + region['High'].iloc[15:30].argmax()
    h3_loc = 10 + 30 + region['High'].iloc[30:45].argmax()
    l1_loc = 10 + region['Low'].iloc[:15].argmin()
    l2_loc = 10 + 15 + region['Low'].iloc[15:30].argmin()
    l3_loc = 10 + 30 + region['Low'].iloc[30:45].argmin()
    annotations = [
        {'type': 'line', 'x1': h1_loc, 'x2': h2_loc, 'y1': h1, 'y2': h2, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': h2_loc, 'x2': h3_loc, 'y1': h2, 'y2': h3, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': l1_loc, 'x2': l2_loc, 'y1': l1, 'y2': l2, 'color': TV_LINE, 'lw': 2},
        {'type': 'line', 'x1': l2_loc, 'x2': l3_loc, 'y1': l2, 'y2': l3, 'color': TV_LINE, 'lw': 2},
        {'type': 'label', 'x': h2_loc, 'y': h2 + 10, 'text': 'Diamond Formation', 'color': '#ffffff', 'fontsize': 10},
        {'type': 'label', 'x': min(75, len(df)-1), 'y': df['Low'].iloc[min(75, len(df)-1)] - 10,
         'text': 'Breakdown', 'color': '#ff9800'},
    ]
    return plot_candlestick(df, "Diamond Top", stock_name, exchange, timeframe, annotations, filename)

def make_wedge(stock_name, exchange, timeframe, filename, rising=True):
    if rising:
        def trend(t, base):
            if t < 0.75:
                upper_slope = base * 0.3
                return base * (1 + t * 0.3) + np.sin(t * 8 * np.pi) * base * 0.03 * (1 - t * 0.8)
            else:
                return base * 1.22 - (t - 0.75) * base * 1.2
    else:
        def trend(t, base):
            if t < 0.75:
                return base * (1 - t * 0.25) + np.sin(t * 8 * np.pi) * base * 0.03 * (1 - t * 0.8)
            else:
                return base * 0.82 + (t - 0.75) * base * 1.0
    df = generate_ohlc(85, 700, 0.005, trend)
    if rising:
        h1_loc = 5
        h2_loc = 55
        l1_loc = 12
        l2_loc = 58
        h1 = df['High'].iloc[3:12].max()
        h2 = df['High'].iloc[45:65].max()
        l1 = df['Low'].iloc[8:20].min()
        l2 = df['Low'].iloc[50:65].min()
        wedge_label = 'Rising Wedge'
        breakdown_label = 'Bearish Breakdown'
        bd_color = '#ff5252'
    else:
        h1_loc = 5
        h2_loc = 55
        l1_loc = 12
        l2_loc = 58
        h1 = df['High'].iloc[3:12].max()
        h2 = df['High'].iloc[45:65].max()
        l1 = df['Low'].iloc[8:20].min()
        l2 = df['Low'].iloc[50:65].min()
        wedge_label = 'Falling Wedge'
        breakdown_label = 'Bullish Breakout'
        bd_color = '#4caf50'
    annotations = [
        {'type': 'line', 'x1': h1_loc, 'x2': h2_loc, 'y1': h1, 'y2': h2, 'color': '#ff5252', 'lw': 2},
        {'type': 'line', 'x1': l1_loc, 'x2': l2_loc, 'y1': l1, 'y2': l2, 'color': '#4caf50', 'lw': 2},
        {'type': 'label', 'x': 30, 'y': (h1 + h2) / 2 + 5, 'text': wedge_label, 'color': '#ffffff', 'fontsize': 10},
        {'type': 'label', 'x': min(72, len(df)-1),
         'y': df['Close'].iloc[min(72, len(df)-1)] + (8 if not rising else -8),
         'text': breakdown_label, 'color': bd_color, 'fontsize': 9},
    ]
    return plot_candlestick(df, wedge_label, stock_name, exchange, timeframe, annotations, filename)


def create_pdf(student_name, roll_no, chart_files, output_filename):
    filepath = os.path.join("/home/user/Salary-Structure", output_filename)
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('CustomTitle', parent=styles['Normal'],
                                  fontSize=14, leading=20, alignment=TA_LEFT,
                                  spaceAfter=6)
    info_style = ParagraphStyle('Info', parent=styles['Normal'],
                                 fontSize=12, leading=18, alignment=TA_LEFT,
                                 spaceAfter=4)
    pattern_title = ParagraphStyle('PatternTitle', parent=styles['Normal'],
                                    fontSize=16, leading=22, alignment=TA_LEFT,
                                    spaceAfter=10, spaceBefore=15,
                                    fontName='Helvetica-Bold')
    pattern_desc = ParagraphStyle('PatternDesc', parent=styles['Normal'],
                                   fontSize=10, leading=14, alignment=TA_LEFT,
                                   spaceAfter=8, textColor=HexColor('#444444'))

    story = []

    story.append(Paragraph(f"Name: {student_name}", title_style))
    story.append(Paragraph(f"Roll No : {roll_no}", info_style))
    story.append(Paragraph("Semester : 3", info_style))
    story.append(Paragraph("Subject : Technical Analysis", info_style))
    story.append(Spacer(1, 30))

    pattern_descriptions = {
        'Double Top': 'A bearish reversal pattern formed after an uptrend where price reaches a resistance level twice, creating two peaks at approximately the same level, followed by a decline below the neckline (support).',
        'Double Bottom': 'A bullish reversal pattern formed after a downtrend where price reaches a support level twice, creating two troughs at approximately the same level, followed by a breakout above the neckline (resistance).',
        'Triple Top': 'A bearish reversal pattern where price tests a resistance level three times without breaking through, forming three peaks at similar levels before declining below the support/neckline.',
        'Triple Bottom': 'A bullish reversal pattern where price tests a support level three times without breaking through, forming three troughs at similar levels before breaking above the resistance/neckline.',
        'Rectangle (Trading Range / BOX)': 'A continuation pattern where price oscillates between horizontal support and resistance levels, forming a rectangular trading range or box pattern.',
        'Descending Triangle': 'A bearish continuation pattern characterized by a flat horizontal support level and a series of lower highs forming a descending trendline. Typically breaks down below support.',
        'Ascending Triangle': 'A bullish continuation pattern characterized by a flat horizontal resistance level and a series of higher lows forming an ascending trendline. Typically breaks out above resistance.',
        'Symmetrical Triangle': 'A continuation pattern formed by converging trendlines of lower highs and higher lows. The decreasing range indicates indecision before a breakout in either direction.',
        'Diamond Top': 'A rare bearish reversal pattern that resembles a diamond shape, formed by a broadening pattern followed by a symmetrical triangle. It signals a potential trend reversal from bullish to bearish.',
        'Wedge': 'A pattern where converging trendlines slope in the same direction. A Rising Wedge (bearish) has both lines sloping up with convergence, while a Falling Wedge (bullish) has both sloping down.',
    }

    pattern_names = [
        'Double Top', 'Double Bottom', 'Triple Top', 'Triple Bottom',
        'Rectangle (Trading Range / BOX)', 'Descending Triangle',
        'Ascending Triangle', 'Symmetrical Triangle', 'Diamond Top', 'Wedge'
    ]

    for i, (pname, cfile) in enumerate(zip(pattern_names, chart_files)):
        if i > 0:
            story.append(PageBreak())

        story.append(Paragraph(pname, pattern_title))
        story.append(Paragraph(pattern_descriptions[pname], pattern_desc))
        story.append(Spacer(1, 5))

        img = Image(cfile, width=16*cm, height=9.3*cm)
        story.append(img)
        story.append(Spacer(1, 10))

    doc.build(story)
    print(f"Created: {filepath}")
    return filepath


# ============ GENERATE ALL CHARTS ============

print("Generating charts for Trevor Dcosta (MSF07)...")
np.random.seed(42)

trevor_charts = []
trevor_charts.append(make_double_top("Reliance Industries Ltd.", "NSE", "1D", "trevor_double_top.png"))
trevor_charts.append(make_double_bottom("HDFC Bank Ltd.", "NSE", "1D", "trevor_double_bottom.png"))
trevor_charts.append(make_triple_top("Infosys Ltd.", "NSE", "1D", "trevor_triple_top.png"))
trevor_charts.append(make_triple_bottom("ICICI Bank Ltd.", "NSE", "1D", "trevor_triple_bottom.png"))
trevor_charts.append(make_rectangle("Bharti Airtel Ltd.", "NSE", "1D", "trevor_rectangle.png"))
trevor_charts.append(make_descending_triangle("Wipro Ltd.", "NSE", "1D", "trevor_desc_tri.png"))
trevor_charts.append(make_ascending_triangle("Tata Steel Ltd.", "NSE", "1D", "trevor_asc_tri.png"))
trevor_charts.append(make_symmetrical_triangle("Maruti Suzuki India Ltd.", "NSE", "1D", "trevor_sym_tri.png"))
trevor_charts.append(make_diamond_top("Sun Pharmaceutical Ind. Ltd.", "NSE", "4h", "trevor_diamond.png"))
trevor_charts.append(make_wedge("Bajaj Finance Ltd.", "NSE", "1D", "trevor_wedge.png", rising=True))

print("Generating charts for Sharvari Itagi (MSF14)...")
np.random.seed(123)

sharvari_charts = []
sharvari_charts.append(make_double_top("Tata Consultancy Services Ltd.", "NSE", "1D", "sharvari_double_top.png"))
sharvari_charts.append(make_double_bottom("State Bank of India", "NSE", "1D", "sharvari_double_bottom.png"))
sharvari_charts.append(make_triple_top("Asian Paints Ltd.", "NSE", "1D", "sharvari_triple_top.png"))
sharvari_charts.append(make_triple_bottom("Larsen & Toubro Ltd.", "NSE", "1D", "sharvari_triple_bottom.png"))
sharvari_charts.append(make_rectangle("ITC Ltd.", "NSE", "1D", "sharvari_rectangle.png"))
sharvari_charts.append(make_descending_triangle("Tata Consumer Products Ltd.", "NSE", "1D", "sharvari_desc_tri.png"))
sharvari_charts.append(make_ascending_triangle("Power Grid Corporation", "NSE", "1D", "sharvari_asc_tri.png"))
sharvari_charts.append(make_symmetrical_triangle("Kotak Mahindra Bank Ltd.", "NSE", "1D", "sharvari_sym_tri.png"))
sharvari_charts.append(make_diamond_top("Nestle India Ltd.", "NSE", "4h", "sharvari_diamond.png"))
sharvari_charts.append(make_wedge("Adani Ports & SEZ Ltd.", "NSE", "1D", "sharvari_wedge.png", rising=False))

print("\nCreating PDFs...")
create_pdf("Trevor Dcosta", "MSF07", trevor_charts, "Trevor_Dcosta_MSF07.pdf")
create_pdf("Sharvari Itagi", "MSF14", sharvari_charts, "Sharvari_Itagi_MSF14.pdf")

print("\nDone! Both PDFs created successfully.")
