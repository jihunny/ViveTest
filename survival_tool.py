"""
Survival analysis utilities for Kaplan-Meier and Weibull analysis.

Expected input: an Excel file with at least two columns:
- time column: non-negative duration until event or censoring (e.g., hours)
- event column: 1 if event/failure occurred, 0 if censored
Optional grouping column to analyze subgroups.

Outputs: plots saved to files and CSV summaries for reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, WeibullFitter


@dataclass
class KMResult:
    group: str
    median_time: Optional[float]


@dataclass
class WeibullResult:
    group: str
    lambda_: float
    rho_: float
    b10_time: float


def load_excel(path: Path, sheet: Optional[str] = None) -> pd.DataFrame:
    # If sheet is None, read the first sheet (0) instead of all sheets
    sheet_arg = 0 if sheet is None else sheet
    df = pd.read_excel(path, sheet_name=sheet_arg, engine="openpyxl")
    return df


def list_excel_sheets(path: Path) -> List[str]:
    x = pd.ExcelFile(path, engine="openpyxl")
    return list(x.sheet_names)


def _ensure_event_binary(series: pd.Series) -> pd.Series:
    # Accept 1/0, True/False, "1"/"0", or any truthy mapping
    if series.dtype == bool:
        return series.astype(int)
    try:
        return series.astype(int)
    except Exception:
        return series.astype(bool).astype(int)


def kaplan_meier_analysis(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: Optional[str] = None,
    out_path: Path = Path("outputs/km_plot.png"),
    x_label: str = "Time",
    title_prefix: str | None = None,
) -> List[KMResult]:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    times = df[time_col].astype(float)
    events = _ensure_event_binary(df[event_col])

    plt.figure(figsize=(7, 5))
    kmf = KaplanMeierFitter()
    results: List[KMResult] = []
    loglog_series: List[Tuple[str, np.ndarray, np.ndarray]] = []

    if group_col and group_col in df.columns:
        for group, gdf in df.groupby(group_col):
            t = gdf[time_col].astype(float)
            e = _ensure_event_binary(gdf[event_col])
            kmf.fit(t, e, label=str(group))
            kmf.plot_survival_function(ci_show=True)
            median_time = kmf.median_survival_time_
            results.append(KMResult(group=str(group), median_time=median_time))

            # Capture series for log-log plot
            surv_df = kmf.survival_function_
            tt = surv_df.index.to_numpy(dtype=float)
            ss = surv_df.iloc[:, 0].to_numpy(dtype=float)
            loglog_series.append((str(group), tt, ss))
    else:
        kmf.fit(times, events, label="All")
        kmf.plot_survival_function(ci_show=True)
        results.append(KMResult(group="All", median_time=kmf.median_survival_time_))

        surv_df = kmf.survival_function_
        tt = surv_df.index.to_numpy(dtype=float)
        ss = surv_df.iloc[:, 0].to_numpy(dtype=float)
        loglog_series.append(("All", tt, ss))

    title = "Kaplan-Meier Survival Estimate"
    if title_prefix:
        title = f"{title_prefix} - {title}"
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel("Survival probability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    # Save summary CSV
    km_summary = pd.DataFrame([r.__dict__ for r in results])
    km_summary.to_csv(out_path.with_name("km_summary.csv"), index=False)

    # Log-log KM plot: y = ln(-ln(S(t))) vs x = ln(t)
    plt.figure(figsize=(7, 5))
    for label, tt, ss in loglog_series:
        # Keep valid domain: t>0 and 0<S<1
        mask = (tt > 0) & (ss > 0) & (ss < 1)
        if not np.any(mask):
            continue
        x = np.log(tt[mask])
        y = np.log(-np.log(ss[mask]))
        plt.plot(x, y, label=label)
    if loglog_series:
        plt.legend()
    title = "KM Log-Log Survival Plot"
    if title_prefix:
        title = f"{title_prefix} - {title}"
    plt.title(title)
    plt.xlabel("ln(time)")
    plt.ylabel("ln(-ln(S(t)))")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path.with_name("km_loglog_plot.png"), dpi=150)
    plt.close()

    return results


def _b_time_from_weibull(lambda_: float, rho_: float, failure_fraction: float = 0.1) -> float:
    # For Weibull S(t) = exp(-(t/lambda)^rho), F(t)=1-S(t).
    # B10 => F=0.10 => t = lambda * (-ln(1-0.10))**(1/rho)
    if not (0.0 < failure_fraction < 1.0):
        raise ValueError("failure_fraction must be in (0,1)")
    return float(lambda_ * (-np.log(1.0 - failure_fraction)) ** (1.0 / rho_))


def weibull_analysis(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: Optional[str] = None,
    out_path: Path = Path("outputs/weibull_plot.png"),
    annotate_b10: bool = True,
    x_label: str = "Time",
    title_prefix: str | None = None,
) -> List[WeibullResult]:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: List[WeibullResult] = []
    plt.figure(figsize=(7, 5))

    if group_col and group_col in df.columns:
        groups = list(df.groupby(group_col))
    else:
        groups = [("All", df)]

    # For log-log plot, accumulate analytic Weibull survival curves
    loglog_series: List[Tuple[str, np.ndarray, np.ndarray]] = []

    for label, gdf in groups:
        wf = WeibullFitter()
        t = gdf[time_col].astype(float)
        e = _ensure_event_binary(gdf[event_col])
        wf.fit(t, e, label=str(label))
        wf.plot_survival_function()
        lambda_ = float(wf.lambda_)  # scale
        rho_ = float(wf.rho_)  # shape
        b10 = _b_time_from_weibull(lambda_, rho_, 0.10)
        results.append(WeibullResult(group=str(label), lambda_=lambda_, rho_=rho_, b10_time=b10))

        if annotate_b10:
            plt.scatter([b10], [0.9], marker="o")
            plt.text(b10, 0.9, f"  B10={b10:.3g}", va="center")

        # Build analytic survival on a positive time grid for log-log plot
        tpos = t[t > 0]
        if len(tpos) > 0:
            tmin = float(np.nanmax([np.min(tpos), 1e-9]))
            tmax = float(np.max(t))
            if tmax > tmin:
                grid = np.geomspace(tmin, tmax, 100)
                s = wf.survival_function_at_times(grid).to_numpy()
                loglog_series.append((str(label), grid, s))

    title = "Weibull Parametric Survival Fit"
    if title_prefix:
        title = f"{title_prefix} - {title}"
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel("Survival probability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    # Save summary CSV
    wb_summary = pd.DataFrame([r.__dict__ for r in results])
    wb_summary.to_csv(out_path.with_name("weibull_summary.csv"), index=False)

    # Weibull log-log plot (should be ~linear for good fits)
    plt.figure(figsize=(7, 5))
    for label, tt, ss in loglog_series:
        mask = (tt > 0) & (ss > 0) & (ss < 1)
        if not np.any(mask):
            continue
        x = np.log(tt[mask])
        y = np.log(-np.log(ss[mask]))
        plt.plot(x, y, label=label)
    if loglog_series:
        plt.legend()
    title = "Weibull Log-Log Survival Plot"
    if title_prefix:
        title = f"{title_prefix} - {title}"
    plt.title(title)
    plt.xlabel("ln(time)")
    plt.ylabel("ln(-ln(S(t)))")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path.with_name("weibull_loglog_plot.png"), dpi=150)
    plt.close()

    # Weibull probability plot (label y-axis in unreliability F(t) %)
    # Using the same transformed y = ln(-ln(S)) values but labeling in F = 1-S space
    plt.figure(figsize=(7, 5))
    for label, tt, ss in loglog_series:
        mask = (tt > 0) & (ss > 0) & (ss < 1)
        if not np.any(mask):
            continue
        x = np.log(tt[mask])
        y = np.log(-np.log(ss[mask]))
        plt.plot(x, y, label=label)
    if loglog_series:
        plt.legend()
    # Build Weibull probability y-ticks: common unreliability percentages
    unreliab = np.array([0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9])
    S_ticks = 1.0 - unreliab
    y_ticks = np.log(-np.log(S_ticks))
    y_labels = [f"{int(u*100)}%" for u in unreliab]
    plt.yticks(y_ticks, y_labels)
    title = "Weibull Probability Plot"
    if title_prefix:
        title = f"{title_prefix} - {title}"
    plt.title(title)
    plt.xlabel("ln(time)")
    plt.ylabel("Unreliability F(t)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path.with_name("weibull_probability_plot.png"), dpi=150)
    plt.close()

    return results


def analyze_excel(
    excel_path: Path,
    time_col: str,
    event_col: str,
    group_col: Optional[str] = None,
    out_dir: Path = Path("outputs"),
    sheet: Optional[str] = None,
    time_unit: Optional[str] = None,
    title_prefix: Optional[str] = None,
) -> Tuple[List[KMResult], List[WeibullResult]]:
    df = load_excel(excel_path, sheet)
    # Basic validation
    missing = [c for c in [time_col, event_col] if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}. Found: {list(df.columns)}")
    out_dir.mkdir(parents=True, exist_ok=True)

    x_label = "Time" if not time_unit else f"Time ({time_unit})"
    km_results = kaplan_meier_analysis(
        df,
        time_col=time_col,
        event_col=event_col,
        group_col=group_col,
        out_path=out_dir / "km_plot.png",
        x_label=x_label,
        title_prefix=title_prefix,
    )
    wb_results = weibull_analysis(
        df,
        time_col=time_col,
        event_col=event_col,
        group_col=group_col,
        out_path=out_dir / "weibull_plot.png",
        annotate_b10=True,
        x_label=x_label,
        title_prefix=title_prefix,
    )

    return km_results, wb_results
