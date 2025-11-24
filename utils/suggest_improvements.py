def advanced_improvements(df):
    improvements = []
    if df.shape[1] > 20:
        improvements.append("Dataset very wide: consider dimensionality reduction.")
    if df.shape[0] > 500000:
        improvements.append("Large dataset: consider chunk processing for performance.")
    return improvements