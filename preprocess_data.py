import pandas as pd
import os
import logging
from get_data import DEPT_CODE_TO_REGION
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DepartmentRegionMapper:
    def __init__(self):

        pass

    def map_departments_to_regions(self, df, dept_col='code_departement'):
        """
        Maps department codes in the DataFrame to their corresponding regions.

        Parameters:
            df (pd.DataFrame): The DataFrame containing department codes.
            dept_col (str): The column name for department codes.

        Returns:
            pd.DataFrame: The DataFrame with an additional 'region' column.
        """
        if dept_col not in df.columns:
            logging.error(f"Department column '{dept_col}' not found in DataFrame.")
            raise KeyError(f"Department column '{dept_col}' not found in DataFrame.")

        # Perform the mapping
        df['region'] = df[dept_col].map(DEPT_CODE_TO_REGION)

        # Log any unmapped departments
        missing_regions = df['region'].isnull().sum()
        if missing_regions > 0:
            logging.warning(f"{missing_regions} records have missing region information.")

        return df


class DataPreprocessor:
    """
    Handles data preprocessing tasks such as calculating price per square meter and grouping data.
    """

    def __init__(self, dataframe):
        self.df = dataframe

    def calculate_price_per_m2(self):
        """
        Calculate the price per square meter for each transaction.
        """
        logging.info("Calculating 'price_per_m2'...")
        self.df['price_per_m2'] = self.df['valeur_fonciere'] / self.df['surface_reelle_bati']

        # Remove rows with missing or zero values in price, surface, or location
        initial_count = len(self.df)
        self.df = self.df[
            (self.df['price_per_m2'].notnull()) &
            (self.df['price_per_m2'] > 0) &
            (self.df['surface_reelle_bati'].notnull()) &
            (self.df['surface_reelle_bati'] > 0)
        ]
        removed = initial_count - len(self.df)
        logging.info(f"Removed {removed} invalid records based on 'price_per_m2' and 'surface_reelle_bati'.")

    def group_by_level(self, levels, column_names):
        """
        Group data by the specified levels and calculate the average price per square meter.

        Parameters:
            levels (list of str): The column names to group by (e.g., ['commune', 'type_local']).
            column_names (list of str): The names to assign to the grouping columns in the output DataFrame.

        Returns:
            pd.DataFrame: A DataFrame with the grouping columns and the average price per square meter.
        """
        if not isinstance(levels, list):
            levels = [levels]
        if not isinstance(column_names, list):
            column_names = [column_names]

        if len(levels) != len(column_names):
            logging.error("The number of levels and column_names must match.")
            raise ValueError("The number of levels and column_names must match.")

        for level in levels:
            if level not in self.df.columns:
                logging.error(f"Grouping level '{level}' does not exist in the DataFrame.")
                raise KeyError(f"Grouping level '{level}' does not exist in the DataFrame.")

        logging.info(f"Grouping data by {levels}...")
        df_grouped = self.df.groupby(levels)['price_per_m2'].mean().reset_index()
        df_grouped.columns = column_names + ['average_price_per_m2']
        logging.info(f"Grouped data by {levels} successfully.")
        return df_grouped


class DataHandler:
    """
    Handles data loading and saving operations.
    """

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def load_data(self, filename):
        """
        Load data from a pickle file.

        Parameters:
            filename (str): The name of the pickle file to load.

        Returns:
            pd.DataFrame: The loaded DataFrame.
        """
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            logging.error(f"Data file '{filepath}' does not exist.")
            raise FileNotFoundError(f"Data file '{filepath}' does not exist.")
        logging.info(f"Loading data from '{filepath}'...")
        df = pd.read_pickle(filepath)
        logging.info(f"Loaded data with {len(df)} records.")
        return df

    def save_data(self, df, filename):
        """
        Save a DataFrame to a pickle file.

        Parameters:
            df (pd.DataFrame): The DataFrame to save.
            filename (str): The name of the pickle file to save to.
        """
        filepath = os.path.join(self.data_dir, filename)
        logging.info(f"Saving data to '{filepath}'...")
        df.to_pickle(filepath)
        logging.info(f"Data saved to '{filepath}' successfully.")


def main():
    # Initialize DataHandler
    data_handler = DataHandler(data_dir='data')

    # Load the main data
    try:
        data = data_handler.load_data('full.pkl')

    except FileNotFoundError as e:
        logging.error(e)
        return

    # Initialize DepartmentRegionMapper and map regions
    mapper = DepartmentRegionMapper()
    data = mapper.map_departments_to_regions(data, dept_col='code_departement')

    # Initialize DataPreprocessor and preprocess data
    preprocessor = DataPreprocessor(data)
    preprocessor.calculate_price_per_m2()

    # Group by 'commune' and 'type_local'
    try:
        df_by_commune = preprocessor.group_by_level(
            levels=['code_commune', 'type_local'],
            column_names=['commune', 'type_local']
        )
        df_by_departement = preprocessor.group_by_level(
            levels=['code_departement', 'type_local'],
            column_names=['departement', 'type_local']
        )
        df_by_region = preprocessor.group_by_level(
            levels=['region', 'type_local'],
            column_names=['region', 'type_local']
        )
    except KeyError as e:
        logging.error(f"Grouping failed: {e}")
        return
    except ValueError as e:
        logging.error(f"Grouping parameters error: {e}")
        return

    # Save the grouped DataFrames
    try:
        data_handler.save_data(df_by_commune, 'prix_m2_par_commune.pkl')
        data_handler.save_data(df_by_departement, 'prix_m2_par_departement.pkl')
        data_handler.save_data(df_by_region, 'prix_m2_par_region.pkl')
    except Exception as e:
        logging.error(f"Failed to save grouped DataFrames: {e}")
        return

    # Optionally, save the updated main DataFrame with the 'region' column
    try:
        data_handler.save_data(data, 'full_with_region.pkl')
    except Exception as e:
        logging.error(f"Failed to save updated main DataFrame: {e}")
        return

    # Print the updated columns
    logging.info("Updated DataFrame Columns:")
    print(data.columns)

    # Optional: Display sample data for verification
    print("\nSample of 'type_local' in main DataFrame:")
    print(data['type_local'].head(50))

    print("\nSample of Grouped DataFrame by Region and Type Local:")
    print(df_by_departement.head(100).to_string())

    region_filter = data['region'] == 'Île-de-France'
    type_local_filter = data['type_local'] == 'Local industriel. commercial ou assimilé'

    # Apply the filters
    filtered_df = df_by_region[region_filter & type_local_filter]
    # Sort the filtered DataFrame by 'price_per_m2' in descending order
    sorted_filtered_df = filtered_df.sort_values(by='price_per_m2', ascending=False)

    print(sorted_filtered_df.head(100).to_string())


if __name__ == '__main__':
    main()