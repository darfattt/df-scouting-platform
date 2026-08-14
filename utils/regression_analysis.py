"""
Regression Analysis utilities for football player statistics.

Performs OLS and Poisson regression to analyze which player statistics
most influence goal scoring (Goals per 90).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler
import warnings
from styles.design_system import (
    CANVAS, SOFT_CLOUD, INK, MUTE, SUCCESS, INFO, apply_nike_style,
)

warnings.filterwarnings("ignore")


# Default variables for regression analysis
DEFAULT_DEPENDENT_VAR = "Goals per 90"

DEFAULT_INDEPENDENT_VARS = [
    "Shots per 90",
    "Progressive passes per 90",
    "Touches in box per 90",
    "Received passes per 90",
    "xG per 90",
    "Dribbles per 90",
    "Offensive duels per 90",
    "Passes to penalty area per 90",
    "Accelerations per 90",
    "Progressive runs per 90",
]


def prepare_regression_data(
    df: pd.DataFrame,
    dependent_var: str = DEFAULT_DEPENDENT_VAR,
    independent_vars: List[str] = None,
    min_minutes: int = 500,
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Prepare data for regression analysis.

    Args:
        df: Player dataframe
        dependent_var: Target variable (default: Goals per 90)
        independent_vars: List of predictor variables
        min_minutes: Minimum minutes played to include

    Returns:
        Tuple of (X DataFrame, y Series, list of valid independent vars)
    """
    if independent_vars is None:
        independent_vars = DEFAULT_INDEPENDENT_VARS

    # Filter by minimum minutes
    df_filtered = df[df["Minutes played"] >= min_minutes].copy()

    # Select only rows with valid dependent variable
    df_filtered = df_filtered[df_filtered[dependent_var].notna()]

    # Check which independent variables are available
    available_vars = []
    for var in independent_vars:
        if var in df_filtered.columns:
            available_vars.append(var)

    if len(available_vars) == 0:
        raise ValueError("No independent variables found in dataset")

    # Create feature matrix and target
    X = df_filtered[available_vars].copy()
    y = df_filtered[dependent_var].copy()

    # Handle missing values in X
    X = X.fillna(X.median())

    # Remove any rows with missing target values
    valid_idx = y.notna()
    X = X[valid_idx]
    y = y[valid_idx]

    return X, y, available_vars


def calculate_vif(X: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Variance Inflation Factor for multicollinearity check.

    Args:
        X: Feature matrix with constant term

    Returns:
        DataFrame with VIF values for each feature
    """
    # Add constant for VIF calculation
    X_with_const = sm.add_constant(X)

    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [
        variance_inflation_factor(X_with_const.values, i + 1)
        for i in range(len(X.columns))
    ]

    # Interpretation
    vif_data["Interpretation"] = vif_data["VIF"].apply(
        lambda x: "High multicollinearity"
        if x > 10
        else "Moderate multicollinearity"
        if x > 5
        else "Low multicollinearity"
    )

    return vif_data.sort_values("VIF", ascending=False)


def fit_ols_model(X: pd.DataFrame, y: pd.Series, add_constant: bool = True):
    """
    Fit Ordinary Least Squares (OLS) regression model.

    Args:
        X: Feature matrix
        y: Target variable
        add_constant: Whether to add intercept term

    Returns:
        Fitted OLS model results
    """
    if add_constant:
        X = sm.add_constant(X)

    model = sm.OLS(y, X)
    results = model.fit()

    return results


def fit_poisson_model(X: pd.DataFrame, y: pd.Series, add_constant: bool = True):
    """
    Fit Poisson regression model for count data.

    Args:
        X: Feature matrix
        y: Target variable (goals, count data)
        add_constant: Whether to add intercept term

    Returns:
        Fitted Poisson model results
    """
    # Ensure non-negative values for Poisson
    y_poisson = y.copy()
    y_poisson = np.maximum(y_poisson, 0)

    if add_constant:
        X = sm.add_constant(X)

    model = sm.Poisson(y_poisson, X)
    results = model.fit(disp=0)

    return results


def generate_interpretation(results, model_name: str = "OLS"):
    """
    Generate automated interpretation of regression results.

    Args:
        results: Fitted model results
        model_name: Name of the model

    Returns:
        List of interpretation strings
    """
    interpretations = []

    # Model fit
    if hasattr(results, "rsquared"):
        interpretations.append(
            f"**Model Fit:** R-squared = {results.rsquared:.3f} "
            f"({results.rsquared * 100:.1f}% of variance explained)"
        )
        if hasattr(results, "rsquared_adj"):
            interpretations.append(
                f"**Adjusted R-squared:** {results.rsquared_adj:.3f}"
            )

    if hasattr(results, "llf"):
        interpretations.append(f"**Log-Likelihood:** {results.llf:.2f}")

    if hasattr(results, "aic"):
        interpretations.append(f"**AIC:** {results.aic:.2f}")

    if hasattr(results, "bic"):
        interpretations.append(f"**BIC:** {results.bic:.2f}")

    interpretations.append("---")
    interpretations.append("**Variable Interpretations:**")

    # Coefficient interpretations
    params = results.params
    pvalues = results.pvalues

    for var in params.index:
        if var == "const":
            continue

        coef = params[var]
        pval = pvalues[var]

        if pval < 0.001:
            significance = "highly significant (p < 0.001)"
        elif pval < 0.01:
            significance = "very significant (p < 0.01)"
        elif pval < 0.05:
            significance = "significant (p < 0.05)"
        elif pval < 0.10:
            significance = "marginally significant (p < 0.10)"
        else:
            significance = "not significant (p >= 0.10)"

        if coef > 0:
            direction = "increase"
        else:
            direction = "decrease"

        if pval < 0.05:
            interp = (
                f"- **{var}**: An increase of 1 unit is associated with an "
                f"{direction} of {abs(coef):.4f} in goals per 90 "
                f"({significance})"
            )
        else:
            interp = (
                f"- **{var}**: No statistically significant relationship detected "
                f"({significance})"
            )

        interpretations.append(interp)

    return interpretations


def create_correlation_heatmap(
    X: pd.DataFrame, figsize: Tuple[int, int] = (12, 10)
) -> plt.Figure:
    """
    Create correlation heatmap for independent variables.

    Args:
        X: Feature matrix
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    apply_nike_style(fig, ax)

    # Calculate correlation matrix
    corr_matrix = X.corr()

    # Create heatmap
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="RdBu_r",
        center=0,
        square=True,
        fmt=".2f",
        cbar_kws={"shrink": 0.8},
        ax=ax,
        annot_kws={"size": 8},
    )

    plt.title(
        "Correlation Matrix - Independent Variables",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    return fig


def create_scatter_plots(
    X: pd.DataFrame, y: pd.Series, n_cols: int = 3, figsize: Tuple[int, int] = None
) -> plt.Figure:
    """
    Create scatter plots of each independent variable vs dependent variable.

    Args:
        X: Feature matrix
        y: Target variable
        n_cols: Number of columns in subplot grid
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    n_vars = len(X.columns)
    n_rows = (n_vars + n_cols - 1) // n_cols

    if figsize is None:
        figsize = (n_cols * 4, n_rows * 3.5)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    apply_nike_style(fig, axes=list(axes.flatten() if hasattr(axes, 'flatten') else [axes]))

    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()

    for idx, var in enumerate(X.columns):
        ax = axes[idx]

        # Scatter plot
        ax.scatter(X[var], y, alpha=0.5, color=INFO, edgecolors="white", s=50)

        # Add trend line
        z = np.polyfit(X[var], y, 1)
        p = np.poly1d(z)
        ax.plot(X[var], p(X[var]), "r--", alpha=0.8, linewidth=2)

        # Formatting
        ax.set_xlabel(var, fontsize=10)
        ax.set_ylabel("Goals per 90", fontsize=10)
        ax.set_title(f"{var} vs Goals", fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Calculate correlation
        corr = X[var].corr(y)
        ax.text(
            0.05,
            0.95,
            f"r = {corr:.3f}",
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    # Hide unused subplots
    for idx in range(n_vars, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    return fig


def create_coefficient_plot(results, figsize: Tuple[int, int] = (10, 6)):
    """
    Create coefficient plot with confidence intervals.

    Args:
        results: Fitted model results
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    apply_nike_style(fig, ax)

    params = results.params
    conf_int = results.conf_int()

    # Remove constant
    if "const" in params.index:
        params = params.drop("const")
        conf_int = conf_int.drop("const")

    # Sort by coefficient value
    sorted_idx = params.abs().sort_values(ascending=True).index
    params = params[sorted_idx]
    conf_int = conf_int.loc[sorted_idx]

    # Calculate error bars
    errors = [params - conf_int.iloc[:, 0], conf_int.iloc[:, 1] - params]

    # Colors based on significance
    pvalues = results.pvalues
    if "const" in pvalues.index:
        pvalues = pvalues.drop("const")

    colors = [SUCCESS if pvalues[var] < 0.05 else MUTE for var in params.index]

    # Create horizontal bar plot
    y_pos = np.arange(len(params))
    ax.barh(
        y_pos,
        params,
        xerr=errors,
        capsize=5,
        color=colors,
        alpha=0.7,
        edgecolor="black",
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        [var[:30] + "..." if len(var) > 30 else var for var in params.index], fontsize=9
    )
    ax.axvline(x=0, color="black", linestyle="-", linewidth=0.8)
    ax.set_xlabel("Coefficient Value", fontsize=11)
    ax.set_title(
        "Regression Coefficients with 95% Confidence Intervals",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.grid(True, axis="x", alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#007d48", alpha=0.7, label="Significant (p < 0.05)"),
        Patch(facecolor=MUTE, alpha=0.7, label="Not significant"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    plt.tight_layout()
    return fig


def create_residual_plots(
    results,
    X: pd.DataFrame,
    y: pd.Series,
    figsize: Tuple[int, int] = (14, 5),
):
    """
    Create residual analysis plots.

    Args:
        results: Fitted model results
        X: Feature matrix
        y: Target variable
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    apply_nike_style(fig, axes=list(axes))

    fitted_values = results.fittedvalues
    residuals = results.resid

    # Plot 1: Residuals vs Fitted
    ax1 = axes[0]
    ax1.scatter(
        fitted_values, residuals, alpha=0.5, color=INFO, edgecolors="white"
    )
    ax1.axhline(y=0, color="red", linestyle="--", alpha=0.8)
    ax1.set_xlabel("Fitted Values", fontsize=10)
    ax1.set_ylabel("Residuals", fontsize=10)
    ax1.set_title("Residuals vs Fitted", fontsize=11, fontweight="bold")
    ax1.grid(True, alpha=0.3)

    # Plot 2: Q-Q Plot
    ax2 = axes[1]
    sm.qqplot(residuals, line="45", ax=ax2)
    ax2.set_title("Q-Q Plot (Normality)", fontsize=11, fontweight="bold")
    ax2.grid(True, alpha=0.3)

    # Plot 3: Residuals Distribution
    ax3 = axes[2]
    ax3.hist(residuals, bins=20, color=INFO, alpha=0.7, edgecolor="white")
    ax3.axvline(x=0, color="red", linestyle="--", alpha=0.8)
    ax3.set_xlabel("Residuals", fontsize=10)
    ax3.set_ylabel("Frequency", fontsize=10)
    ax3.set_title("Distribution of Residuals", fontsize=11, fontweight="bold")
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def compare_models(
    ols_results,
    poisson_results,
):
    """
    Compare OLS and Poisson regression models.

    Args:
        ols_results: OLS model results
        poisson_results: Poisson model results

    Returns:
        DataFrame with model comparison metrics
    """
    comparison = {
        "Metric": ["Log-Likelihood", "AIC", "BIC"],
        "OLS": [
            ols_results.llf if hasattr(ols_results, "llf") else np.nan,
            ols_results.aic if hasattr(ols_results, "aic") else np.nan,
            ols_results.bic if hasattr(ols_results, "bic") else np.nan,
        ],
        "Poisson": [
            poisson_results.llf,
            poisson_results.aic,
            poisson_results.bic,
        ],
    }

    return pd.DataFrame(comparison)


def get_available_variables(df: pd.DataFrame) -> List[str]:
    """
    Get list of available numeric variables for regression.

    Args:
        df: Player dataframe

    Returns:
        List of variable names
    """
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Filter for relevant stats (per 90, percentages, counts)
    relevant_vars = []
    for col in numeric_cols:
        if any(
            keyword in col.lower()
            for keyword in [
                "per 90",
                "%",
                "goals",
                "shots",
                "passes",
                "duels",
                "touches",
                "dribbles",
                "crosses",
                "assists",
                "xg",
                "xa",
                "interceptions",
                "tackles",
                "accelerations",
                "progressive",
            ]
        ):
            relevant_vars.append(col)

    return sorted(relevant_vars)
