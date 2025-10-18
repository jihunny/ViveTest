# Survival Analysis Tool (Kaplan–Meier + Weibull + B10)

This repository provides a small Python CLI that reads an Excel file and performs:
- Kaplan–Meier survival estimation with confidence bands
- Parametric Weibull fit with B10 life computation
- Log–log survival plots to assess Weibull suitability

Outputs are saved as PNG plots and CSV summaries in `outputs/`.

## Quick Start (Windows PowerShell with uv)

1) Generate a sample dataset (Excel):
```
uv run --with pandas --with numpy --with openpyxl python make_sample_data.py
```
This writes `sample_data.xlsx` with columns: `time`, `event` (1=failure, 0=censored), `group`.

2) Dry‑run to inspect your Excel (optional):
```
uv run --with openpyxl --with pandas python main.py .\sample_data.xlsx --dry-run
uv run --with openpyxl --with pandas python main.py .\sample_data.xlsx --list-sheets
```

3) Run the analysis (KM + Weibull + B10 + log–log):
```
uv run --with pandas --with numpy --with matplotlib --with lifelines --with openpyxl \
  python main.py .\sample_data.xlsx time event --group-col group --out-dir outputs
```

## Using Your Own Excel
- Required columns: a numeric time column and an event indicator (1=failure, 0=censored).
- Optional: a `group` column for subgroup curves.
- If needed, specify a sheet name: `--sheet Sheet1`.

## Outputs
- Plots: `km_plot.png`, `km_loglog_plot.png`, `weibull_plot.png`, `weibull_loglog_plot.png`
- Summaries: `km_summary.csv` (KM medians), `weibull_summary.csv` (λ, ρ, B10)

## B10 Life (What it Means)
By definition, B10 is the time by which 10% have failed (90% survive). For a Weibull model with
survival `S(t)=exp(-(t/λ)^ρ)`, `B10 = λ * (-ln(0.9))^(1/ρ)`. The Weibull plot annotates this point.

## Troubleshooting
- PowerShell script activation errors: run `Set-ExecutionPolicy -Scope Process Bypass` first.
- If plots don’t show lines on log–log, ensure `time > 0` and `0 < S(t) < 1` for some range.
