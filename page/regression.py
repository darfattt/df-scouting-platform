import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

def render_regression_analysis_page(df_filtered):
    """
    Render Regression Analysis page to study relationships between metrics
    """
    st.header("Regression Analysis")

    if len(df_filtered) == 0:
        st.warning("⚠️ No players match the selected filters.")
        return

    numeric_cols = df_filtered.select_dtypes(include=["number"]).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox("Predictor (X):", numeric_cols, index=numeric_cols.index("Age") if "Age" in numeric_cols else 0)
    with col2:
        y_col = st.selectbox("Target (Y):", numeric_cols, index=numeric_cols.index("Market value") if "Market value" in numeric_cols else 1)

    df_reg = df_filtered[[x_col, y_col]].dropna()
    if len(df_reg) < 10:
        st.error("Not enough data for regression.")
        return

    X = df_reg[[x_col]].values
    y = df_reg[y_col].values
    
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    
    st.metric("R-Squared", f"{r2:.3f}")
    
    fig, ax = plt.subplots()
    sns.regplot(x=x_col, y=y_col, data=df_reg, ax=ax, scatter_kws={'alpha':0.5})
    st.pyplot(fig)
    plt.close(fig)
