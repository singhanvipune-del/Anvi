from ai.autocorrect_hybrid import autocorrect_name


def fix_names(df, columns):
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(autocorrect_name)
    return df