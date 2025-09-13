import pandas as pd
import os

def load_levels(file_path):
    """
    Load and process hydrology data from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Processed DataFrame with relevant columns.
    """
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Drop unnecessary columns
    df.drop(columns=['completeness', 'quality', 'qcode'], inplace=True, errors='ignore')

    # Replace all values in 'measure' column with 'level'
    if 'measure' in df.columns:
        df['measure'] = 'level'

    # Extract station name from filename
    filename = os.path.basename(file_path)
    station_name = filename.split('-level-15min-Qualified.csv')[0]

    # Add 'station' column
    df['station'] = station_name

    return df
