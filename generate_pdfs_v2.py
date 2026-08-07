import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from datetime import datetime, timedelta
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.colors import HexColor
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = "/home/user/Salary-Structure/charts_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# TradingView Light Theme Colors
BG = '#ffffff'
GRID = '#e0e3eb'
TEXT = '#131722'
TEXT_LIGHT = '#787b86'
GREEN = '#26a69a'
RED = '#ef5350'
BLUE = '#2962ff'
ORANGE = '#ff9800'
YELLOW_BG = '#fff9c4'
GREEN_BG = '#e8f5e9'
PINK_BG = '#fce4ec'
BLUE_BG = '#e3f2fd'
PURPLE_BG = '#f3e5f5'

def gen_ohlc(n, base, vol, trend_fn, start_date='2025-06-01'):
    dates = pd.date_range(start=start_date, periods=n, freq='B')
    rows = []
    cur = base
    for i in range(n):
        t = i / n
        target = trend_fn(t, base)
        cur = cur * 0.65 + target * 0.35 + np.random.normal(0, vol * base * 0.15)
        body = abs(np.random.normal(0, vol * cur * 0.4))
        wick = abs(np.random.normal(0, vol * cur * 0.3))
        direction = 1 if np.random.random() > 0.45 else -1
        if direction > 0:
            o = cur - body / 2
            c = cur + body / 2
        else:
            o = cur + body / 2
            c = cur - body / 2
        h = max(o, c) + wick
        l = min(o, c) - wick
        v = int(np.random.lognormal(14, 0.8))
        rows.append([o, h, l, c, v])
    return pd.DataFrame(rows, columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=dates)

def plot_tv_chart(df, stock_name, timeframe, exchange, pattern_name, annotations, filename,
                  pattern_label=None, label_color='#ff9800', label_bg='#fff3e0'):
    fig = plt.figure(figsize=(13, 7.5), facecolor=BG)
    gs = fig.add_gridspec(5, 1, hspace=0.02)
    ax1 = fig.add_subplot(gs[0:4, 0])
    ax2 = fig.add_subplot(gs[4, 0], sharex=ax1)
    ax1.set_facecolor(BG)
    ax2.set_facecolor(BG)

    # Header
    last = df.iloc[-1]
    chg = last['Close'] - last['Open']
    chg_pct = (chg / last['Open']) * 100
    chg_color = GREEN if chg >= 0 else RED
    sign = '+' if chg >= 0 else ''

    header_y = 1.06
    ax1.text(0.0, header_y, f'  {stock_name} ', transform=ax1.transAxes,
             fontsize=11, fontweight='bold', color=TEXT, va='bottom',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0f3fa', edgecolor='#d1d4dc'))
    ax1.text(0.22, header_y, f'{timeframe} - {exchange}', transform=ax1.transAxes,
             fontsize=10, color=TEXT_LIGHT, va='bottom')

    ohlc_text = (f'O {last["Open"]:.2f}  H {last["High"]:.2f}  '
                 f'L {last["Low"]:.2f}  C {last["Close"]:.2f}  '
                 f'{sign}{chg:.2f} ({sign}{chg_pct:.2f}%)')
    ax1.text(0.0, 1.02, ohlc_text, transform=ax1.transAxes,
             fontsize=9, color=chg_color, va='bottom')

    # Candlesticks
    for i in range(len(df)):
        date = mdates.date2num(df.index[i])
        o, h, l, c = df.iloc[i]['Open'], df.iloc[i]['High'], df.iloc[i]['Low'], df.iloc[i]['Close']
        color = GREEN if c >= o else RED
        ax1.plot([date, date], [l, h], color=color, linewidth=0.7)
        bw = 0.5
        rect = plt.Rectangle((date - bw/2, min(o, c)), bw, max(abs(c - o), 0.01),
                              facecolor=color if c < o else BG,
                              edgecolor=color, linewidth=0.8)
        ax1.add_patch(rect)

    # Volume bars
    max_vol = df['Volume'].max()
    for i in range(len(df)):
        date = mdates.date2num(df.index[i])
        vol = df.iloc[i]['Volume']
        color = GREEN if df.iloc[i]['Close'] >= df.iloc[i]['Open'] else RED
        ax2.bar(date, vol, width=0.5, color=color, alpha=0.4)

    # Grid & axes styling
    for ax in [ax1, ax2]:
        ax.grid(True, color=GRID, linewidth=0.5, alpha=0.8)
        ax.tick_params(colors=TEXT_LIGHT, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(GRID)

    ax1.yaxis.set_label_position('right')
    ax1.yaxis.tick_right()
    ax2.yaxis.set_label_position('right')
    ax2.yaxis.tick_right()
    plt.setp(ax1.get_xticklabels(), visible=False)

    price_range = df['High'].max() - df['Low'].min()
    ax1.set_ylim(df['Low'].min() - price_range * 0.06, df['High'].max() + price_range * 0.12)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b \'%y'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator())

    # Last price tag on right axis
    last_price = df.iloc[-1]['Close']
    ax1.axhline(y=last_price, color=chg_color, linewidth=0.5, linestyle='--', alpha=0.5,
                xmin=0, xmax=0.98)
    ax1.annotate(f' {last_price:.2f} ', xy=(1.0, last_price),
                 xycoords=('axes fraction', 'data'),
                 fontsize=8, color='white', fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.15', facecolor=chg_color, edgecolor='none'),
                 ha='left', va='center')

    # Volume label
    ax2.text(0.01, 0.85, f'Vol  {df.iloc[-1]["Volume"]:,.0f}', transform=ax2.transAxes,
             fontsize=8, color=TEXT_LIGHT, va='top')

    # Draw annotations
    for ann in annotations:
        atype = ann.get('type', 'line')
        if atype == 'line':
            x1_i, x2_i = ann['x1'], ann['x2']
            y1, y2 = ann['y1'], ann['y2']
            d1 = mdates.date2num(df.index[min(x1_i, len(df)-1)])
            d2 = mdates.date2num(df.index[min(x2_i, len(df)-1)])
            color = ann.get('color', BLUE)
            lw = ann.get('lw', 1.8)
            style = ann.get('style', '-')
            ax1.plot([d1, d2], [y1, y2], color=color, linewidth=lw, linestyle=style)
        elif atype == 'hline':
            y = ann['y']
            color = ann.get('color', BLUE)
            ax1.axhline(y=y, color=color, linewidth=1.2, linestyle='--', alpha=0.6)
        elif atype == 'label':
            x_idx = min(ann['x'], len(df)-1)
            y = ann['y']
            text = ann['text']
            d = mdates.date2num(df.index[x_idx])
            fcolor = ann.get('facecolor', '#e3f2fd')
            ecolor = ann.get('edgecolor', BLUE)
            tcolor = ann.get('tcolor', TEXT)
            fsize = ann.get('fontsize', 8)
            ax1.annotate(text, xy=(d, y), color=tcolor, fontsize=fsize,
                         fontweight='bold', ha='center', va='bottom',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=fcolor,
                                   edgecolor=ecolor, alpha=0.9))

    # Pattern label box (like ACP indicator)
    if pattern_label:
        mid_idx = len(df) // 2
        mid_date = mdates.date2num(df.index[mid_idx])
        mid_price = (df['High'].max() + df['Low'].min()) / 2
        ax1.annotate(pattern_label, xy=(mid_date, df['Low'].min() + price_range * 0.05),
                     fontsize=10, fontweight='bold', ha='center', va='bottom',
                     color=TEXT,
                     bbox=dict(boxstyle='round,pad=0.4', facecolor=label_bg,
                               edgecolor=label_color, alpha=0.95, linewidth=2))

    # TradingView watermark
    ax1.text(0.5, 0.5, stock_name.split(' ')[0], transform=ax1.transAxes,
             fontsize=45, color='#f0f0f0', ha='center', va='center',
             fontweight='bold', alpha=0.3, zorder=0)

    # TradingView logo
    fig.text(0.01, 0.01, 'TradingView', color=TEXT_LIGHT, fontsize=11,
             fontweight='bold', style='italic', va='bottom')

    # Timeframe + timestamp
    fig.text(0.99, 0.01, f'{timeframe}  UTC+5:30  RTH  ADJ', color=TEXT_LIGHT,
             fontsize=8, ha='right', va='bottom')

    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=BG, edgecolor='none')
    plt.close()
    return filepath


# ====================== PATTERN FUNCTIONS ======================

def make_double_top(stock, exchange, tf, base_price, filename, start='2025-06-01'):
    def trend(t, b):
        if t < 0.15: return b + t * b * 1.8
        elif t < 0.30: return b * 1.27 - (t-0.15) * b * 1.8
        elif t < 0.45: return b + (t-0.30) * b * 1.8
        elif t < 0.60: return b * 1.27 - (t-0.45) * b * 2.5
        else: return b * 0.9 - (t-0.60) * b * 0.5
    df = gen_ohlc(80, base_price, 0.008, trend, start)
    p1 = df['High'].iloc[8:22].idxmax(); p1i = df.index.get_loc(p1); p1v = df['High'][p1]
    p2 = df['High'].iloc[28:42].idxmax(); p2i = df.index.get_loc(p2); p2v = df['High'][p2]
    trough = df['Low'].iloc[p1i:p2i].idxmin(); ti = df.index.get_loc(trough); tv = df['Low'][trough]
    anns = [
        {'type':'line','x1':p1i,'x2':ti,'y1':p1v,'y2':tv,'color':BLUE,'lw':2},
        {'type':'line','x1':ti,'x2':p2i,'y1':tv,'y2':p2v,'color':BLUE,'lw':2},
        {'type':'line','x1':p2i,'x2':min(p2i+18,len(df)-1),'y1':p2v,
         'y2':df['Low'].iloc[min(p2i+15,len(df)-1)],'color':BLUE,'lw':2},
        {'type':'hline','y':tv,'color':ORANGE},
        {'type':'label','x':p1i,'y':p1v+base_price*0.01,'text':'Top 1',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED},
        {'type':'label','x':p2i,'y':p2v+base_price*0.01,'text':'Top 2',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED},
        {'type':'label','x':ti,'y':tv-base_price*0.02,'text':'Neckline',
         'facecolor':'#fff3e0','edgecolor':ORANGE,'tcolor':'#e65100'},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Double Top", anns, filename,
                         pattern_label="Double Top", label_color=RED, label_bg=PINK_BG)

def make_double_bottom(stock, exchange, tf, base_price, filename, start='2025-06-01'):
    def trend(t, b):
        if t < 0.15: return b - t * b * 1.5
        elif t < 0.30: return b * 0.78 + (t-0.15) * b * 1.5
        elif t < 0.45: return b * 1.0 - (t-0.30) * b * 1.5
        elif t < 0.60: return b * 0.78 + (t-0.45) * b * 2.2
        else: return b * 1.1 + (t-0.60) * b * 0.6
    df = gen_ohlc(80, base_price, 0.008, trend, start)
    b1 = df['Low'].iloc[8:22].idxmin(); b1i = df.index.get_loc(b1); b1v = df['Low'][b1]
    b2 = df['Low'].iloc[28:45].idxmin(); b2i = df.index.get_loc(b2); b2v = df['Low'][b2]
    pk = df['High'].iloc[b1i:b2i].idxmax(); pki = df.index.get_loc(pk); pkv = df['High'][pk]
    anns = [
        {'type':'line','x1':b1i,'x2':pki,'y1':b1v,'y2':pkv,'color':BLUE,'lw':2},
        {'type':'line','x1':pki,'x2':b2i,'y1':pkv,'y2':b2v,'color':BLUE,'lw':2},
        {'type':'line','x1':b2i,'x2':min(b2i+18,len(df)-1),'y1':b2v,
         'y2':df['High'].iloc[min(b2i+15,len(df)-1)],'color':BLUE,'lw':2},
        {'type':'hline','y':pkv,'color':'#4caf50'},
        {'type':'label','x':b1i,'y':b1v-base_price*0.02,'text':'Bottom 1',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20'},
        {'type':'label','x':b2i,'y':b2v-base_price*0.02,'text':'Bottom 2',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20'},
        {'type':'label','x':pki,'y':pkv+base_price*0.01,'text':'Neckline',
         'facecolor':GREEN_BG,'edgecolor':'#4caf50','tcolor':'#1b5e20'},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Double Bottom", anns, filename,
                         pattern_label="Double Bottom", label_color=GREEN, label_bg=GREEN_BG)

def make_triple_top(stock, exchange, tf, base_price, filename, start='2025-03-01'):
    def trend(t, b):
        if t < 0.10: return b + t * b * 2.5
        elif t < 0.18: return b * 1.25 - (t-0.10) * b * 2.5
        elif t < 0.28: return b * 1.05 + (t-0.18) * b * 2
        elif t < 0.38: return b * 1.25 - (t-0.28) * b * 2
        elif t < 0.48: return b * 1.05 + (t-0.38) * b * 2
        elif t < 0.58: return b * 1.25 - (t-0.48) * b * 2.5
        elif t < 0.75: return b * 1.0 - (t-0.58) * b * 0.8
        else: return b * 0.86 - (t-0.75) * b * 0.4
    df = gen_ohlc(100, base_price, 0.007, trend, start)
    p1 = df['High'].iloc[5:16].idxmax(); p1i = df.index.get_loc(p1); p1v = df['High'][p1]
    p2 = df['High'].iloc[22:36].idxmax(); p2i = df.index.get_loc(p2); p2v = df['High'][p2]
    p3 = df['High'].iloc[40:55].idxmax(); p3i = df.index.get_loc(p3); p3v = df['High'][p3]
    resist = max(p1v, p2v, p3v)
    t1 = df['Low'].iloc[p1i:p2i].idxmin(); t1i = df.index.get_loc(t1)
    t2 = df['Low'].iloc[p2i:p3i].idxmin(); t2i = df.index.get_loc(t2)
    supp = min(df['Low'][t1], df['Low'][t2])
    anns = [
        {'type':'hline','y':resist,'color':RED},
        {'type':'hline','y':supp,'color':ORANGE},
        {'type':'label','x':p1i,'y':p1v+base_price*0.01,'text':'1',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED,'fontsize':10},
        {'type':'label','x':p2i,'y':p2v+base_price*0.01,'text':'2',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED,'fontsize':10},
        {'type':'label','x':p3i,'y':p3v+base_price*0.01,'text':'3',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED,'fontsize':10},
        {'type':'label','x':5,'y':resist+base_price*0.01,'text':'Resistance',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED,'fontsize':8},
        {'type':'label','x':5,'y':supp-base_price*0.02,'text':'Support',
         'facecolor':'#fff3e0','edgecolor':ORANGE,'tcolor':'#e65100','fontsize':8},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Triple Top", anns, filename,
                         pattern_label="Triple Top", label_color=RED, label_bg=PINK_BG)

def make_triple_bottom(stock, exchange, tf, base_price, filename, start='2025-03-01'):
    def trend(t, b):
        if t < 0.10: return b - t * b * 2
        elif t < 0.18: return b * 0.80 + (t-0.10) * b * 2
        elif t < 0.28: return b * 0.96 - (t-0.18) * b * 1.6
        elif t < 0.38: return b * 0.80 + (t-0.28) * b * 1.6
        elif t < 0.48: return b * 0.96 - (t-0.38) * b * 1.6
        elif t < 0.58: return b * 0.80 + (t-0.48) * b * 2.5
        elif t < 0.75: return b * 1.05 + (t-0.58) * b * 0.8
        else: return b * 1.18 + (t-0.75) * b * 0.3
    df = gen_ohlc(100, base_price, 0.007, trend, start)
    b1 = df['Low'].iloc[5:16].idxmin(); b1i = df.index.get_loc(b1); b1v = df['Low'][b1]
    b2 = df['Low'].iloc[22:36].idxmin(); b2i = df.index.get_loc(b2); b2v = df['Low'][b2]
    b3 = df['Low'].iloc[40:55].idxmin(); b3i = df.index.get_loc(b3); b3v = df['Low'][b3]
    supp = min(b1v, b2v, b3v)
    pk1 = df['High'].iloc[b1i:b2i].idxmax(); pk1i = df.index.get_loc(pk1)
    pk2 = df['High'].iloc[b2i:b3i].idxmax(); pk2i = df.index.get_loc(pk2)
    resist = max(df['High'][pk1], df['High'][pk2])
    anns = [
        {'type':'hline','y':supp,'color':GREEN},
        {'type':'hline','y':resist,'color':ORANGE},
        {'type':'label','x':b1i,'y':b1v-base_price*0.02,'text':'1',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20','fontsize':10},
        {'type':'label','x':b2i,'y':b2v-base_price*0.02,'text':'2',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20','fontsize':10},
        {'type':'label','x':b3i,'y':b3v-base_price*0.02,'text':'3',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20','fontsize':10},
        {'type':'label','x':5,'y':supp-base_price*0.02,'text':'Support',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20','fontsize':8},
        {'type':'label','x':5,'y':resist+base_price*0.01,'text':'Neckline',
         'facecolor':'#fff3e0','edgecolor':ORANGE,'tcolor':'#e65100','fontsize':8},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Triple Bottom", anns, filename,
                         pattern_label="Triple Bottom", label_color=GREEN, label_bg=GREEN_BG)

def make_rectangle(stock, exchange, tf, base_price, filename, start='2025-01-01'):
    def trend(t, b):
        return b + np.sin(t * 10 * np.pi) * b * 0.04
    df = gen_ohlc(110, base_price, 0.005, trend, start)
    resist = df['High'].iloc[10:95].nlargest(6).mean()
    supp = df['Low'].iloc[10:95].nsmallest(6).mean()
    anns = [
        {'type':'line','x1':10,'x2':95,'y1':resist,'y2':resist,'color':RED,'lw':2,'style':'-'},
        {'type':'line','x1':10,'x2':95,'y1':supp,'y2':supp,'color':GREEN,'lw':2,'style':'-'},
        {'type':'label','x':90,'y':resist+base_price*0.008,'text':'Resistance',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED,'fontsize':8},
        {'type':'label','x':90,'y':supp-base_price*0.015,'text':'Support',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20','fontsize':8},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Rectangle", anns, filename,
                         pattern_label="Ranging Channel (Parallel)", label_color=ORANGE, label_bg='#fff3e0')

def make_desc_triangle(stock, exchange, tf, base_price, filename, start='2025-04-01'):
    def trend(t, b):
        if t < 0.8:
            upper = b * 1.12 * (1 - t * 0.25)
            lower = b * 0.93
            return (upper + lower)/2 + np.sin(t * 7 * np.pi) * (upper-lower) * 0.25
        else:
            return b * 0.88 - (t-0.8) * b * 0.5
    df = gen_ohlc(85, base_price, 0.006, trend, start)
    supp = df['Low'].iloc[5:68].nsmallest(8).mean()
    h1 = df['High'].iloc[2:15].max(); h1i = df['High'].iloc[2:15].argmax() + 2
    h3 = df['High'].iloc[48:65].max(); h3i = df['High'].iloc[48:65].argmax() + 48
    anns = [
        {'type':'line','x1':5,'x2':68,'y1':supp,'y2':supp,'color':GREEN,'lw':2},
        {'type':'line','x1':h1i,'x2':h3i,'y1':h1,'y2':h3,'color':RED,'lw':2},
        {'type':'label','x':68,'y':supp-base_price*0.015,'text':'Flat Support',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20'},
        {'type':'label','x':h1i+5,'y':h1+base_price*0.01,'text':'Lower Highs',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Descending Triangle", anns, filename,
                         pattern_label="Descending Triangle (Contracting)", label_color=ORANGE, label_bg='#fff3e0')

def make_asc_triangle(stock, exchange, tf, base_price, filename, start='2025-04-01'):
    def trend(t, b):
        if t < 0.8:
            upper = b * 1.10
            lower = b * 0.88 + t * b * 0.22
            return (upper + lower)/2 + np.sin(t * 7 * np.pi) * (upper-lower) * 0.25
        else:
            return b * 1.14 + (t-0.8) * b * 0.6
    df = gen_ohlc(85, base_price, 0.006, trend, start)
    resist = df['High'].iloc[5:68].nlargest(8).mean()
    l1 = df['Low'].iloc[2:15].min(); l1i = df['Low'].iloc[2:15].argmin() + 2
    l3 = df['Low'].iloc[48:65].min(); l3i = df['Low'].iloc[48:65].argmin() + 48
    anns = [
        {'type':'line','x1':5,'x2':68,'y1':resist,'y2':resist,'color':RED,'lw':2},
        {'type':'line','x1':l1i,'x2':l3i,'y1':l1,'y2':l3,'color':GREEN,'lw':2},
        {'type':'label','x':68,'y':resist+base_price*0.01,'text':'Flat Resistance',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED},
        {'type':'label','x':l3i,'y':l3-base_price*0.015,'text':'Higher Lows',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20'},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Ascending Triangle", anns, filename,
                         pattern_label="Ascending Triangle (Expanding)", label_color='#8bc34a', label_bg=GREEN_BG)

def make_sym_triangle(stock, exchange, tf, base_price, filename, start='2025-04-01'):
    def trend(t, b):
        if t < 0.8:
            amp = b * 0.10 * (1 - t * 0.9)
            return b + np.sin(t * 8 * np.pi) * amp
        else:
            return b * 1.02 + (t-0.8) * b * 0.4
    df = gen_ohlc(85, base_price, 0.005, trend, start)
    h1 = df['High'].iloc[3:14].max(); h1i = df['High'].iloc[3:14].argmax() + 3
    h2 = df['High'].iloc[38:52].max(); h2i = df['High'].iloc[38:52].argmax() + 38
    l1 = df['Low'].iloc[10:22].min(); l1i = df['Low'].iloc[10:22].argmin() + 10
    l2 = df['Low'].iloc[45:58].min(); l2i = df['Low'].iloc[45:58].argmin() + 45
    anns = [
        {'type':'line','x1':h1i,'x2':min(h2i+12,len(df)-1),'y1':h1,
         'y2':h2-(h1-h2)*0.3,'color':RED,'lw':2},
        {'type':'line','x1':l1i,'x2':min(l2i+12,len(df)-1),'y1':l1,
         'y2':l2+(l2-l1)*0.3,'color':GREEN,'lw':2},
        {'type':'label','x':h1i+3,'y':h1+base_price*0.008,'text':'Lower Highs',
         'facecolor':PINK_BG,'edgecolor':RED,'tcolor':RED},
        {'type':'label','x':l1i+3,'y':l1-base_price*0.012,'text':'Higher Lows',
         'facecolor':GREEN_BG,'edgecolor':GREEN,'tcolor':'#1b5e20'},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Symmetrical Triangle", anns, filename,
                         pattern_label="Symmetrical Triangle (Contracting)", label_color=BLUE, label_bg=BLUE_BG)

def make_diamond_top(stock, exchange, tf, base_price, filename, start='2025-05-01'):
    def trend(t, b):
        if t < 0.12: return b * (1 + t * 2)
        elif t < 0.3:
            amp = (t-0.12) / 0.18
            return b * 1.24 + np.sin(t * 14) * b * 0.06 * amp
        elif t < 0.55:
            amp = 1 - (t-0.3) / 0.25
            return b * 1.24 + np.sin(t * 14) * b * 0.06 * amp
        elif t < 0.7: return b * 1.20 - (t-0.55) * b * 0.6
        else: return b * 1.11 - (t-0.7) * b * 0.8
    df = gen_ohlc(90, base_price, 0.006, trend, start)
    seg = df.iloc[10:65]
    h1 = seg['High'].iloc[:12].max(); h1i = 10 + seg['High'].iloc[:12].argmax()
    h2 = seg['High'].iloc[12:27].max(); h2i = 10 + 12 + seg['High'].iloc[12:27].argmax()
    h3 = seg['High'].iloc[27:42].max(); h3i = 10 + 27 + seg['High'].iloc[27:42].argmax()
    l1 = seg['Low'].iloc[:12].min(); l1i = 10 + seg['Low'].iloc[:12].argmin()
    l2 = seg['Low'].iloc[12:27].min(); l2i = 10 + 12 + seg['Low'].iloc[12:27].argmin()
    l3 = seg['Low'].iloc[27:42].min(); l3i = 10 + 27 + seg['Low'].iloc[27:42].argmin()
    anns = [
        {'type':'line','x1':h1i,'x2':h2i,'y1':h1,'y2':h2,'color':BLUE,'lw':2},
        {'type':'line','x1':h2i,'x2':h3i,'y1':h2,'y2':h3,'color':BLUE,'lw':2},
        {'type':'line','x1':l1i,'x2':l2i,'y1':l1,'y2':l2,'color':BLUE,'lw':2},
        {'type':'line','x1':l2i,'x2':l3i,'y1':l2,'y2':l3,'color':BLUE,'lw':2},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Diamond Top", anns, filename,
                         pattern_label="Diamond Top (Reversal)", label_color='#9c27b0', label_bg=PURPLE_BG)

def make_wedge(stock, exchange, tf, base_price, filename, rising=True, start='2025-04-01'):
    if rising:
        def trend(t, b):
            if t < 0.75:
                return b * (1 + t * 0.28) + np.sin(t * 9 * np.pi) * b * 0.025 * (1 - t * 0.7)
            else: return b * 1.20 - (t-0.75) * b * 1.0
        lbl = "Rising Wedge (Contracting)"
        lc = RED; lbg = PINK_BG
    else:
        def trend(t, b):
            if t < 0.75:
                return b * (1 - t * 0.22) + np.sin(t * 9 * np.pi) * b * 0.025 * (1 - t * 0.7)
            else: return b * 0.84 + (t-0.75) * b * 0.8
        lbl = "Falling Wedge (Contracting)"
        lc = GREEN; lbg = GREEN_BG
    df = gen_ohlc(85, base_price, 0.005, trend, start)
    h1 = df['High'].iloc[3:12].max(); h1i = df['High'].iloc[3:12].argmax() + 3
    h2 = df['High'].iloc[48:62].max(); h2i = df['High'].iloc[48:62].argmax() + 48
    l1 = df['Low'].iloc[8:18].min(); l1i = df['Low'].iloc[8:18].argmin() + 8
    l2 = df['Low'].iloc[52:66].min(); l2i = df['Low'].iloc[52:66].argmin() + 52
    anns = [
        {'type':'line','x1':h1i,'x2':h2i,'y1':h1,'y2':h2,'color':RED,'lw':2},
        {'type':'line','x1':l1i,'x2':l2i,'y1':l1,'y2':l2,'color':GREEN,'lw':2},
    ]
    return plot_tv_chart(df, stock, tf, exchange, "Wedge", anns, filename,
                         pattern_label=lbl, label_color=lc, label_bg=lbg)


def create_pdf(name, roll, charts, outfile):
    path = os.path.join("/home/user/Salary-Structure", outfile)
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    hdr = ParagraphStyle('H', parent=styles['Normal'], fontSize=13, leading=19, spaceAfter=5)
    ptitle = ParagraphStyle('PT', parent=styles['Normal'], fontSize=16, leading=22,
                             spaceAfter=8, spaceBefore=12, fontName='Helvetica-Bold')
    pdesc = ParagraphStyle('PD', parent=styles['Normal'], fontSize=10, leading=14,
                            spaceAfter=6, textColor=HexColor('#444444'))
    story = []
    story.append(Paragraph(f"Name: {name}", hdr))
    story.append(Paragraph(f"Roll No : {roll}", hdr))
    story.append(Paragraph("Semester : 3", hdr))
    story.append(Paragraph("Subject : Technical Analysis", hdr))
    story.append(Spacer(1, 25))

    descs = {
        'Double Top': 'A bearish reversal pattern where price hits resistance twice at similar levels, forming an "M" shape. The pattern completes when price breaks below the neckline (trough between the two peaks), signaling a potential downtrend.',
        'Double Bottom': 'A bullish reversal pattern where price hits support twice at similar levels, forming a "W" shape. The pattern completes when price breaks above the neckline (peak between the two troughs), signaling a potential uptrend.',
        'Triple Top': 'A bearish reversal pattern with three peaks at similar resistance levels. Each failed attempt to break resistance confirms selling pressure. The pattern completes when price breaks below the support/neckline.',
        'Triple Bottom': 'A bullish reversal pattern with three troughs at similar support levels. Each bounce off support confirms buying interest. The pattern completes when price breaks above the resistance/neckline.',
        'Rectangle (Trading Range / BOX)': 'A continuation/consolidation pattern where price oscillates between parallel horizontal support and resistance lines, forming a rectangular trading range. Breakout direction determines the next trend.',
        'Descending Triangle': 'A bearish continuation pattern with a flat horizontal support and descending resistance (lower highs). The contracting range typically resolves with a breakdown below support.',
        'Ascending Triangle': 'A bullish continuation pattern with a flat horizontal resistance and ascending support (higher lows). The contracting range typically resolves with a breakout above resistance.',
        'Symmetrical Triangle': 'A continuation pattern with converging trendlines of lower highs and higher lows. Price range narrows toward the apex, indicating indecision before a breakout in the direction of the prevailing trend.',
        'Diamond Top': 'A rare reversal pattern resembling a diamond shape, formed by an expanding pattern (diverging trendlines) followed by a contracting pattern (converging trendlines). Signals a bearish reversal after an uptrend.',
        'Wedge': 'A pattern with two converging trendlines sloping in the same direction. A Rising Wedge (both lines slope upward, converging) is bearish. A Falling Wedge (both lines slope downward, converging) is bullish.',
    }
    pnames = ['Double Top','Double Bottom','Triple Top','Triple Bottom',
              'Rectangle (Trading Range / BOX)','Descending Triangle',
              'Ascending Triangle','Symmetrical Triangle','Diamond Top','Wedge']
    for i, (pn, cf) in enumerate(zip(pnames, charts)):
        if i > 0: story.append(PageBreak())
        story.append(Paragraph(pn, ptitle))
        story.append(Paragraph(descs[pn], pdesc))
        story.append(Spacer(1, 4))
        story.append(Image(cf, width=16.5*cm, height=9.5*cm))
    doc.build(story)
    print(f"Created: {path}")
    return path


# ==================== GENERATE ====================
print("=" * 50)
print("Generating TradingView-style charts with real NSE stock price ranges...")
print("=" * 50)

# PDF 1: Trevor Dcosta - using realistic NSE price ranges
np.random.seed(2026)
print("\n--- Trevor Dcosta (MSF07) ---")
t = []
t.append(make_double_top("Reliance Industries Ltd.", "NSE", "1D", 1350, "t_double_top.png"))
t.append(make_double_bottom("HDFC Bank Ltd.", "NSE", "1D", 730, "t_double_bottom.png"))
t.append(make_triple_top("Infosys Ltd.", "NSE", "1W", 1580, "t_triple_top.png"))
t.append(make_triple_bottom("ICICI Bank Ltd.", "NSE", "1D", 1250, "t_triple_bottom.png"))
t.append(make_rectangle("Bharti Airtel Ltd.", "NSE", "1D", 1780, "t_rectangle.png"))
t.append(make_desc_triangle("Wipro Ltd.", "NSE", "1D", 305, "t_desc_tri.png"))
t.append(make_asc_triangle("Tata Steel Ltd.", "NSE", "1W", 155, "t_asc_tri.png"))
t.append(make_sym_triangle("Maruti Suzuki India Ltd.", "NSE", "1D", 13200, "t_sym_tri.png"))
t.append(make_diamond_top("Sun Pharmaceutical Ind.", "NSE", "4h", 1850, "t_diamond.png"))
t.append(make_wedge("Bajaj Finance Ltd.", "NSE", "1D", 9500, "t_wedge.png", rising=True))

# PDF 2: Sharvari Itagi - different stocks, different seed
np.random.seed(2027)
print("\n--- Sharvari Itagi (MSF14) ---")
s = []
s.append(make_double_top("Tata Consultancy Services Ltd.", "NSE", "1D", 3800, "s_double_top.png"))
s.append(make_double_bottom("State Bank of India", "NSE", "1D", 820, "s_double_bottom.png"))
s.append(make_triple_top("Asian Paints Ltd.", "NSE", "1W", 2400, "s_triple_top.png"))
s.append(make_triple_bottom("Larsen & Toubro Ltd.", "NSE", "1D", 3600, "s_triple_bottom.png"))
s.append(make_rectangle("ITC Ltd.", "NSE", "1D", 475, "s_rectangle.png"))
s.append(make_desc_triangle("Tata Consumer Products Ltd.", "NSE", "1D", 1050, "s_desc_tri.png"))
s.append(make_asc_triangle("Power Grid Corporation", "NSE", "1W", 340, "s_asc_tri.png"))
s.append(make_sym_triangle("Kotak Mahindra Bank Ltd.", "NSE", "1D", 1950, "s_sym_tri.png"))
s.append(make_diamond_top("Nestle India Ltd.", "NSE", "4h", 2350, "s_diamond.png"))
s.append(make_wedge("Adani Ports & SEZ Ltd.", "NSE", "1D", 1280, "s_wedge.png", rising=False))

print("\nBuilding PDFs...")
create_pdf("Trevor Dcosta", "MSF07", t, "Trevor_Dcosta_MSF07.pdf")
create_pdf("Sharvari Itagi", "MSF14", s, "Sharvari_Itagi_MSF14.pdf")
print("\nDone!")
