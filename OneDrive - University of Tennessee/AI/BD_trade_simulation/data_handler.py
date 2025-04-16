"""
Data handler for loading and preprocessing trade data.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime


class TradeDataHandler:
    """Handle trade data loading and preprocessing"""
    
    def __init__(self, data_path=None):
        """
        Initialize the data handler
        
        Args:
            data_path (str): Path to the trade data file
        """
        self.data_path = data_path
        self.data = None
        
    def load_data(self, sample_size=None):
        """
        Load the trade data from CSV file
        
        Args:
            sample_size (int, optional): Number of rows to sample for faster processing
            
        Returns:
            pandas.DataFrame: Loaded trade data
        """
        print(f"Loading trade data from {self.data_path}...")
        
        # For large CSV files, we can use chunking or sampling
        if sample_size:
            self.data = pd.read_csv(self.data_path, nrows=sample_size)
        else:
            # Use chunking for very large files
            chunks = []
            chunk_size = 100000  # Adjust based on available memory
            
            for chunk in pd.read_csv(self.data_path, chunksize=chunk_size):
                chunks.append(chunk)
                
            self.data = pd.concat(chunks, ignore_index=True)
            
        print(f"Loaded data with {len(self.data)} rows and {len(self.data.columns)} columns.")
        return self.data
    
    def get_summary_statistics(self):
        """
        Generate summary statistics for the trade data
        
        Returns:
            dict: Dictionary of summary statistics
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        # Get basic summary statistics
        stats = {
            'row_count': len(self.data),
            'column_count': len(self.data.columns),
            'columns': list(self.data.columns),
            'numeric_columns': {},
            'categorical_columns': {},
            'missing_values': self.data.isnull().sum().to_dict(),
        }
        
        # Get statistics for numeric columns
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            stats['numeric_columns'][col] = {
                'mean': self.data[col].mean(),
                'median': self.data[col].median(),
                'std': self.data[col].std(),
                'min': self.data[col].min(),
                'max': self.data[col].max(),
            }
            
        # Get statistics for categorical columns
        cat_cols = self.data.select_dtypes(exclude=['number']).columns
        for col in cat_cols:
            stats['categorical_columns'][col] = {
                'unique_values': self.data[col].nunique(),
                'top_values': self.data[col].value_counts().head(5).to_dict(),
            }
            
        return stats
    
    def preprocess_data(self):
        """
        Preprocess the trade data for analysis
        
        Returns:
            pandas.DataFrame: Preprocessed trade data
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        # Make a copy to avoid modifying the original data
        processed_data = self.data.copy()
        
        # Handle missing values based on context
        for col in processed_data.columns:
            # Handle numeric columns
            if processed_data[col].dtype in ['int64', 'float64']:
                # Fill missing values with median
                processed_data[col] = processed_data[col].fillna(processed_data[col].median())
            else:
                # Fill missing categorical values with mode
                processed_data[col] = processed_data[col].fillna(processed_data[col].mode()[0] if not processed_data[col].mode().empty else "Unknown")
        
        # Convert date columns to datetime if any
        date_columns = [col for col in processed_data.columns if 'date' in col.lower() or 'year' in col.lower()]
        for col in date_columns:
            try:
                processed_data[col] = pd.to_datetime(processed_data[col])
            except:
                print(f"Could not convert {col} to datetime.")
        
        return processed_data
    
    def split_export_import_data(self):
        """
        Split the data into export and import datasets
        
        Returns:
            tuple: (export_data, import_data)
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # This implementation assumes there's a 'trade_type' or similar column
        # Adjust according to the actual data structure
        if 'trade_type' in self.data.columns:
            export_data = self.data[self.data['trade_type'] == 'export']
            import_data = self.data[self.data['trade_type'] == 'import']
            return export_data, import_data
        else:
            print("Could not identify trade type column. Returning original data.")
            return self.data, self.data
    
    def get_data_by_year(self, year):
        """
        Filter data for a specific year
        
        Args:
            year (int): Year to filter
            
        Returns:
            pandas.DataFrame: Filtered data
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # This implementation assumes there's a 'year' or 'date' column
        # Adjust according to the actual data structure
        if 'year' in self.data.columns:
            return self.data[self.data['year'] == year]
        elif 'date' in self.data.columns:
            return self.data[pd.DatetimeIndex(self.data['date']).year == year]
        else:
            print("Could not identify year column.")
            return self.data
    
    def get_data_by_sector(self, sector):
        """
        Filter data for a specific sector
        
        Args:
            sector (str): Sector name
            
        Returns:
            pandas.DataFrame: Filtered data
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # This implementation assumes there's a 'sector' column
        # Adjust according to the actual data structure
        if 'sector' in self.data.columns:
            return self.data[self.data['sector'] == sector]
        else:
            print("Could not identify sector column.")
            return self.data
    
    def save_processed_data(self, output_path):
        """
        Save processed data to a new file
        
        Args:
            output_path (str): Path to save the processed data
            
        Returns:
            str: Path to the saved file
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        self.data.to_csv(output_path, index=False)
        print(f"Saved processed data to {output_path}")
        return output_path


if __name__ == "__main__":
    # Example usage
    data_handler = TradeDataHandler("../bd_trade_data.csv")
    # Load only a sample for testing
    data = data_handler.load_data(sample_size=1000)
    stats = data_handler.get_summary_statistics()
    
    print("\nData Summary:")
    print(f"Number of rows: {stats['row_count']}")
    print(f"Number of columns: {stats['column_count']}")
    print(f"Columns: {', '.join(stats['columns'])}")
    
    processed_data = data_handler.preprocess_data()
    data_handler.save_processed_data("../data/processed_trade_data.csv")
