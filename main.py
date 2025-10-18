import argparse
from pathlib import Path

from survival_tool import analyze_excel, load_excel, list_excel_sheets


def main():
    parser = argparse.ArgumentParser(
        description="Kaplan-Meier and Weibull survival analysis from Excel. Computes B10 life and saves plots/summaries.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("excel", type=Path, help="Path to Excel file (.xlsx)")
    parser.add_argument("time_col", type=str, nargs="?", help="Name of the time-to-event column")
    parser.add_argument("event_col", type=str, nargs="?", help="Name of the event indicator column (1=failure, 0=censored)")
    parser.add_argument("--group-col", type=str, default=None, help="Optional grouping column for subgroup analyses")
    parser.add_argument("--sheet", type=str, default=None, help="Excel sheet name (if not first)")
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"), help="Directory for plots and CSV summaries")
    parser.add_argument("--dry-run", action="store_true", help="Only inspect the Excel file: list columns, dtypes, head, and optional group counts")
    parser.add_argument("--list-sheets", action="store_true", help="List available sheet names and exit")

    args = parser.parse_args()

    if args.list_sheets:
        sheets = list_excel_sheets(args.excel)
        print("Sheets:")
        for s in sheets:
            print(f"  - {s}")
        return

    if args.dry_run:
        df = load_excel(args.excel, args.sheet)
        print("Columns:")
        for c in df.columns:
            print(f"  - {c}: {df[c].dtype}")
        print("\nHead:")
        print(df.head(5).to_string(index=False))
        if args.group_col and args.group_col in df.columns:
            print("\nGroup counts:")
            print(df[args.group_col].value_counts(dropna=False))
        if args.time_col:
            print(f"\nTime column provided: {args.time_col} -> exists: {args.time_col in df.columns}")
        if args.event_col:
            print(f"Event column provided: {args.event_col} -> exists: {args.event_col in df.columns}")
        return

    if not args.time_col or not args.event_col:
        raise SystemExit("time_col and event_col are required unless using --dry-run/--list-sheets")

    km_results, wb_results = analyze_excel(
        excel_path=args.excel,
        time_col=args.time_col,
        event_col=args.event_col,
        group_col=args.group_col,
        out_dir=args.out_dir,
        sheet=args.sheet,
    )

    print("Kaplan-Meier results:")
    for r in km_results:
        print(f"  group={r.group:>10s} median_time={r.median_time}")

    print("\nWeibull results (includes B10 life):")
    for r in wb_results:
        print(f"  group={r.group:>10s} lambda={r.lambda_:.4g} rho={r.rho_:.4g} B10={r.b10_time:.4g}")

    print(f"\nSaved: {args.out_dir / 'km_plot.png'}, {args.out_dir / 'weibull_plot.png'}")
    print(f"Saved: {args.out_dir / 'km_summary.csv'}, {args.out_dir / 'weibull_summary.csv'}")


if __name__ == "__main__":
    main()
