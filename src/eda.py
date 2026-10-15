"""Exploratory figures for the README. python -m src.eda"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import FIGURES, TARGET
from src.data import build_clean


def main():
    df = build_clean()
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(6, 4))
    df[TARGET].value_counts(normalize=True).rename({0: "No default", 1: "Default"}).plot(
        kind="bar", ax=ax)
    ax.set_title(f"Overall default rate: {df[TARGET].mean():.1%}")
    ax.set_ylabel("Share of clients")
    fig.tight_layout(); fig.savefig(FIGURES / "01_default_rate.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(data=df, x="age_group", y=TARGET, ax=ax, errorbar=None)
    ax.set_ylabel("Default rate"); ax.set_title("Default rate by age group")
    fig.tight_layout(); fig.savefig(FIGURES / "02_default_by_age.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x=TARGET, y="utilization", ax=ax)
    ax.set_xticklabels(["No default", "Default"])
    ax.set_title("Credit utilisation vs. default outcome")
    fig.tight_layout(); fig.savefig(FIGURES / "03_utilization_vs_default.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df, x="months_delinquent", y=TARGET, ax=ax, errorbar=None)
    ax.set_ylabel("Default rate"); ax.set_xlabel("Months delinquent (last 6)")
    ax.set_title("Default rate rises sharply with delinquency history")
    fig.tight_layout(); fig.savefig(FIGURES / "04_default_by_delinquency.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(data=df, x="education", y=TARGET, ax=ax, errorbar=None,
               order=df.groupby("education")[TARGET].mean().sort_values(ascending=False).index)
    ax.set_ylabel("Default rate"); ax.set_title("Default rate by education level")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout(); fig.savefig(FIGURES / "05_default_by_education.png", dpi=150); plt.close(fig)

    num_cols = ["credit_limit", "age", "utilization", "months_delinquent",
               "worst_delinquency", "payment_ratio", TARGET]
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm",
               center=0, ax=ax)
    ax.set_title("Correlation matrix")
    fig.tight_layout(); fig.savefig(FIGURES / "06_correlation.png", dpi=150); plt.close(fig)

    print(f"6 figures -> {FIGURES}")


if __name__ == "__main__":
    main()
