from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_sample(n_per_group: int = 100, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    def one_group(label: str, shape: float, scale: float) -> pd.DataFrame:
        # Weibull-distributed failure times
        failure = scale * rng.weibull(shape, size=n_per_group)
        # Exponential censoring times (some observations are censored)
        censor = rng.exponential(scale=1.6 * scale, size=n_per_group)
        time = np.minimum(failure, censor)
        event = (failure <= censor).astype(int)
        return pd.DataFrame({"time": time, "event": event, "group": label})

    a = one_group("A", shape=1.5, scale=1000.0)
    b = one_group("B", shape=2.0, scale=800.0)
    df = pd.concat([a, b], ignore_index=True)
    # Shuffle rows
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    # Round times for readability
    df["time"] = df["time"].round(2)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sample survival dataset and save as Excel")
    parser.add_argument("--out", type=Path, default=Path("sample_data.xlsx"), help="Output Excel path")
    parser.add_argument("--n", type=int, default=100, help="Samples per group")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    args = parser.parse_args()

    df = generate_sample(n_per_group=args.n, seed=args.seed)
    df.to_excel(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")
    print("Columns: time (float), event (0/1), group (str)")


if __name__ == "__main__":
    main()

