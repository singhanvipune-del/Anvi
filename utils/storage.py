import pandas as pd

def save_file(df: pd.DataFrame, output_path: str):
    """Save cleaned dataframe as CSV or Excel."""
    if output_path.endswith(".csv"):
        df.to_csv(output_path, index=False)
    elif output_path.endswith(".xlsx"):
        df.to_excel(output_path, index=False)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")