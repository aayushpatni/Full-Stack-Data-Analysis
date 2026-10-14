# ─── Data Analysis Engine ───────────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import time
from scipy import stats

from config import PALETTE
from utils import b64_fig, styled_fig


def analyse(df, filename):
    """
    Run a full exploratory data analysis on the given DataFrame.

    Returns a dict with:
      - summary     : high-level dataset statistics
      - stats       : per-column descriptive statistics
      - charts      : list of { title, img (base64), type }
      - insights    : list of human-readable insight strings
      - analysis_time, num_cols, cat_cols
    """
    t0 = time.time()
    charts = []
    insights = []

    df = df.copy()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = []

    # Try parsing date columns
    for c in cat_cols[:]:
        try:
            parsed = pd.to_datetime(df[c], format='mixed')
            df[c] = parsed
            date_cols.append(c)
            cat_cols.remove(c)
        except:
            pass

    # ── Summary stats ───────────────────────────────────────────────────────
    summary = {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'numeric_cols': len(num_cols),
        'categorical_cols': len(cat_cols),
        'missing_pct': round(df.isnull().mean().mean() * 100, 2),
        'duplicates': int(df.duplicated().sum()),
        'memory_kb': round(df.memory_usage(deep=True).sum() / 1024, 1),
        'filename': filename
    }

    # ── Numeric stats table ─────────────────────────────────────────────────
    stats_data = {}
    if num_cols:
        desc = df[num_cols].describe().round(3)
        stats_data = desc.to_dict()

    # ── 1. Missing value heatmap ────────────────────────────────────────────
    if df.isnull().any().any():
        fig, ax = styled_fig(10, 4)
        miss = df.isnull().astype(int)
        if miss.shape[1] > 20:
            miss = miss.iloc[:, :20]
        sns.heatmap(miss, ax=ax, cmap='RdPu', cbar=False,
                    yticklabels=False, linewidths=0.3)
        ax.set_title('Missing Values Map', fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Columns')
        charts.append({'title': 'Missing Values Heatmap', 'img': b64_fig(fig), 'type': 'heatmap'})
        missing_cols = df.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0]
        if not missing_cols.empty:
            insights.append(f"⚠️ {len(missing_cols)} column(s) have missing values. Highest: '{missing_cols.idxmax()}' ({missing_cols.max()} nulls).")

    # ── 2. Numeric distributions ────────────────────────────────────────────
    if num_cols:
        cols_to_plot = num_cols[:6]
        ncols = min(3, len(cols_to_plot))
        nrows = (len(cols_to_plot) + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
        fig.patch.set_facecolor('#0F0F1A')
        axes = np.array(axes).flatten() if hasattr(axes, '__len__') else [axes]
        for i, col in enumerate(cols_to_plot):
            ax = axes[i]
            ax.set_facecolor('#161628')
            data = df[col].dropna()
            ax.hist(data, bins=30, color=PALETTE[i % len(PALETTE)], alpha=0.85, edgecolor='none')
            ax.axvline(data.mean(), color='#FFD700', linewidth=1.5, linestyle='--', label=f'μ={data.mean():.2f}')
            ax.set_title(col[:20], color='#EEE', fontsize=10, fontweight='bold')
            ax.tick_params(colors='#AAA', labelsize=8)
            ax.grid(True, color='#222', linewidth=0.4)
            for spine in ax.spines.values():
                spine.set_edgecolor('#333')
            ax.legend(fontsize=7, facecolor='#0F0F1A', labelcolor='#EEE')
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        fig.suptitle('Numeric Distributions', color='#EEE', fontsize=14, fontweight='bold', y=1.01)
        plt.tight_layout()
        charts.append({'title': 'Numeric Distributions', 'img': b64_fig(fig), 'type': 'histogram'})

        # Insights from distributions
        for col in num_cols:
            d = df[col].dropna()
            if len(d) > 10:
                sk = d.skew()
                if abs(sk) > 1:
                    direction = 'right' if sk > 0 else 'left'
                    insights.append(f"📊 '{col}' is {direction}-skewed (skewness={sk:.2f}), suggesting outliers or non-normal distribution.")

    # ── 3. Correlation heatmap ───────────────────────────────────────────────
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig, ax = styled_fig(max(8, len(num_cols)), max(6, len(num_cols) - 1))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        cmap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr, mask=mask, ax=ax, cmap=cmap, vmax=1, vmin=-1,
                    center=0, annot=len(num_cols) <= 12,
                    fmt='.2f', annot_kws={'size': 8},
                    linewidths=0.5, linecolor='#222',
                    cbar_kws={'shrink': 0.8})
        ax.set_title('Correlation Matrix', fontsize=13, fontweight='bold', pad=10)
        plt.tight_layout()
        charts.append({'title': 'Correlation Heatmap', 'img': b64_fig(fig), 'type': 'heatmap'})

        # Strong correlations
        corr_pairs = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                val = corr.iloc[i, j]
                if abs(val) > 0.7:
                    corr_pairs.append((corr.columns[i], corr.columns[j], val))
        if corr_pairs:
            pair = max(corr_pairs, key=lambda x: abs(x[2]))
            insights.append(f"🔗 Strong correlation ({pair[2]:.2f}) between '{pair[0]}' and '{pair[1]}'.")

    # ── 4. Categorical bar charts ────────────────────────────────────────────
    for col in cat_cols[:3]:
        vc = df[col].value_counts().head(12)
        if len(vc) < 2:
            continue
        fig, ax = styled_fig(10, 4)
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(vc))]
        bars = ax.barh(vc.index.astype(str), vc.values, color=colors, edgecolor='none', height=0.65)
        for bar, val in zip(bars, vc.values):
            ax.text(bar.get_width() + max(vc.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f'{val:,}', va='center', ha='left', color='#CCC', fontsize=8)
        ax.set_title(f'Distribution: {col}', fontsize=13, fontweight='bold')
        ax.set_xlabel('Count')
        ax.invert_yaxis()
        plt.tight_layout()
        charts.append({'title': f'Category: {col}', 'img': b64_fig(fig), 'type': 'bar'})
        top = vc.index[0]
        insights.append(f"🏆 Most common value in '{col}': '{top}' ({vc.iloc[0]:,} occurrences, {vc.iloc[0]/len(df)*100:.1f}%).")

    # ── 5. Pie chart for top categorical column ──────────────────────────────
    if cat_cols:
        col = cat_cols[0]
        vc = df[col].value_counts().head(8)
        if len(vc) >= 2:
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#0F0F1A')
            ax.set_facecolor('#0F0F1A')
            wedge_colors = PALETTE[:len(vc)]
            wedges, texts, autotexts = ax.pie(
                vc.values, labels=None,
                colors=wedge_colors, autopct='%1.1f%%',
                startangle=140, pctdistance=0.82,
                wedgeprops={'edgecolor': '#0F0F1A', 'linewidth': 2},
            )
            for at in autotexts:
                at.set_color('#EEE')
                at.set_fontsize(9)
            legend_labels = [f"{k} ({v:,})" for k, v in zip(vc.index.astype(str), vc.values)]
            ax.legend(wedges, legend_labels, loc='lower center',
                      bbox_to_anchor=(0.5, -0.12), ncol=3,
                      fontsize=8, facecolor='#161628', labelcolor='#CCC',
                      edgecolor='#333')
            ax.set_title(f'Pie Chart: {col}', color='#EEE', fontsize=13, fontweight='bold')
            plt.tight_layout()
            charts.append({'title': f'Pie: {col}', 'img': b64_fig(fig), 'type': 'pie'})

    # ── 6. Box plots for outlier detection ───────────────────────────────────
    if num_cols:
        cols_to_box = num_cols[:5]
        fig, axes = plt.subplots(1, len(cols_to_box), figsize=(4 * len(cols_to_box), 5))
        fig.patch.set_facecolor('#0F0F1A')
        if len(cols_to_box) == 1:
            axes = [axes]
        for i, (col, ax) in enumerate(zip(cols_to_box, axes)):
            data = df[col].dropna()
            bp = ax.boxplot(data, patch_artist=True, notch=False,
                            boxprops=dict(facecolor=PALETTE[i % len(PALETTE)], alpha=0.8),
                            medianprops=dict(color='#FFD700', linewidth=2),
                            whiskerprops=dict(color='#888'),
                            capprops=dict(color='#888'),
                            flierprops=dict(marker='o', color='#FF6584', markersize=3, alpha=0.5))
            ax.set_facecolor('#161628')
            ax.set_title(col[:15], color='#EEE', fontsize=9, fontweight='bold')
            ax.tick_params(colors='#AAA', labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor('#333')
            ax.grid(True, color='#222', linewidth=0.4, axis='y')

            # Count outliers
            Q1, Q3 = data.quantile(0.25), data.quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((data < Q1 - 1.5 * IQR) | (data > Q3 + 1.5 * IQR)).sum()
            if outliers > 0:
                insights.append(f"🚨 '{col}' has {outliers} outlier(s) ({outliers/len(data)*100:.1f}% of data).")

        fig.suptitle('Outlier Detection (Box Plots)', color='#EEE', fontsize=13, fontweight='bold')
        plt.tight_layout()
        charts.append({'title': 'Box Plots — Outlier Detection', 'img': b64_fig(fig), 'type': 'boxplot'})

    # ── 7. Time series if date cols found ───────────────────────────────────
    if date_cols and num_cols:
        dcol = date_cols[0]
        ncol = num_cols[0]
        ts = df[[dcol, ncol]].dropna().sort_values(dcol)
        if len(ts) > 3:
            fig, ax = styled_fig(12, 5)
            ax.plot(ts[dcol], ts[ncol], color='#6C63FF', linewidth=2, alpha=0.9)
            ax.fill_between(ts[dcol], ts[ncol], alpha=0.15, color='#6C63FF')
            ax.set_title(f'Time Series: {ncol} over {dcol}', fontsize=13, fontweight='bold')
            ax.set_xlabel(dcol)
            ax.set_ylabel(ncol)
            plt.xticks(rotation=30)
            plt.tight_layout()
            charts.append({'title': f'Time Series: {ncol}', 'img': b64_fig(fig), 'type': 'timeseries'})
            insights.append(f"📅 Time-series data detected. '{ncol}' spans {ts[dcol].min().date()} to {ts[dcol].max().date()}.")

    # ── 8. Scatter plot (top 2 numeric) ─────────────────────────────────────
    if len(num_cols) >= 2:
        x_col, y_col = num_cols[0], num_cols[1]
        sample = df[[x_col, y_col]].dropna().head(2000)
        fig, ax = styled_fig(9, 5)
        sc = ax.scatter(sample[x_col], sample[y_col], c=PALETTE[0],
                        alpha=0.5, s=20, edgecolors='none')
        # Regression line
        if len(sample) > 5:
            m, b, r, p, _ = stats.linregress(sample[x_col], sample[y_col])
            xline = np.linspace(sample[x_col].min(), sample[x_col].max(), 100)
            ax.plot(xline, m * xline + b, color='#FFD700', linewidth=2,
                    label=f'R²={r**2:.3f}')
            ax.legend(fontsize=9, facecolor='#0F0F1A', labelcolor='#EEE')
            if abs(r) > 0.6:
                insights.append(f"📈 Linear regression of '{y_col}' on '{x_col}' shows R²={r**2:.3f} — a {('strong' if abs(r)>0.8 else 'moderate')} fit.")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'Scatter: {x_col} vs {y_col}', fontsize=13, fontweight='bold')
        plt.tight_layout()
        charts.append({'title': f'Scatter: {x_col} vs {y_col}', 'img': b64_fig(fig), 'type': 'scatter'})

    elapsed = round(time.time() - t0, 2)

    if not insights:
        insights.append("✅ Dataset looks clean with no major issues detected.")
    insights.insert(0, f"🕒 Full analysis completed in {elapsed}s across {len(charts)} chart(s).")

    return {
        'success': True,
        'summary': summary,
        'stats': stats_data,
        'charts': charts,
        'insights': insights,
        'analysis_time': elapsed,
        'num_cols': num_cols,
        'cat_cols': cat_cols
    }
