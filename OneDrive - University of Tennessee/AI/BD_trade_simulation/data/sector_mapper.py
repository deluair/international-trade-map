"""
Maps HS92 product codes to economic sectors for the structural transformation model.
"""
import pandas as pd
import os


class SectorMapper:
    """Maps HS product codes to economic sectors and processes trade data."""
    
    def __init__(self, data_dir=None):
        """
        Initialize the sector mapper.
        
        Args:
            data_dir (str): Directory containing data files
        """
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.data_dir = data_dir
        self.hs_to_sector = {}
        self.country_codes = {}
        self.hs_codes = {}
        
        # Load reference data
        self._load_reference_data()
        # Create HS to sector mapping
        self._create_sector_mapping()
    
    def _load_reference_data(self):
        """Load country and product code reference data."""
        # Load country codes
        country_file = os.path.join(self.data_dir, 'country_codes_V202501.csv')
        if os.path.exists(country_file):
            country_df = pd.read_csv(country_file)
            self.country_codes = dict(zip(country_df['country_code'], country_df['country_name']))
            print(f"Loaded {len(self.country_codes)} country codes")
        else:
            print(f"Warning: Country code file not found at {country_file}")
        
        # Load HS product codes
        product_file = os.path.join(self.data_dir, 'product_codes_HS92_V202501.csv')
        if os.path.exists(product_file):
            product_df = pd.read_csv(product_file)
            self.hs_codes = dict(zip(product_df['code'], product_df['description']))
            print(f"Loaded {len(self.hs_codes)} product codes")
        else:
            print(f"Warning: Product code file not found at {product_file}")
    
    def _create_sector_mapping(self):
        """
        Create mapping from HS codes to economic sectors.
        
        This uses HS92 classification to map products to the sectors used in the
        structural transformation model.
        """
        # RMG (Ready-Made Garments)
        rmg_chapters = [61, 62]  # Apparel chapters
        
        # Leather
        leather_codes = [41, 42, 43, 64]  # Leather, leather articles, footwear
        
        # Jute
        jute_codes = [53, 5303, 5307, 5310]  # Jute and jute products
        
        # Frozen food
        frozen_food_codes = [3, 16]  # Fish and fish preparations
        
        # Pharma
        pharma_codes = [30]  # Pharmaceutical products
        
        # IT services (limited trade data representation)
        it_codes = [8471, 8473, 85]  # Computers and parts, electrical machinery
        
        # Light engineering
        engineering_codes = [73, 76, 84, 87]  # Metal products, machinery
        
        # Agro processing
        agro_codes = [7, 8, 9, 10, 11, 12, 15, 17, 18, 19, 20, 21, 22, 23, 24]
        
        # Home textiles
        home_textile_codes = [63]  # Other made-up textile articles
        
        # Shipbuilding
        shipbuilding_codes = [89]  # Ships, boats
        
        # For each HS code, assign a sector
        for hs_code in self.hs_codes:
            # Convert to string for safer comparison
            hs_str = str(hs_code)
            chapter = int(hs_str[:2]) if len(hs_str) >= 2 else 0
            
            # Assign sector based on HS code/chapter
            if chapter in rmg_chapters:
                self.hs_to_sector[hs_code] = 'rmg'
            elif chapter in leather_codes:
                self.hs_to_sector[hs_code] = 'leather'
            elif chapter in jute_codes or hs_str.startswith('5303') or hs_str.startswith('5307') or hs_str.startswith('5310'):
                self.hs_to_sector[hs_code] = 'jute'
            elif chapter in frozen_food_codes:
                self.hs_to_sector[hs_code] = 'frozen_food'
            elif chapter in pharma_codes:
                self.hs_to_sector[hs_code] = 'pharma'
            elif chapter in it_codes or hs_str.startswith('8471') or hs_str.startswith('8473'):
                self.hs_to_sector[hs_code] = 'it_services'
            elif chapter in engineering_codes:
                self.hs_to_sector[hs_code] = 'light_engineering'
            elif chapter in agro_codes:
                self.hs_to_sector[hs_code] = 'agro_processing'
            elif chapter in home_textile_codes:
                self.hs_to_sector[hs_code] = 'home_textiles'
            elif chapter in shipbuilding_codes:
                self.hs_to_sector[hs_code] = 'shipbuilding'
            else:
                # Other sectors not explicitly modeled
                self.hs_to_sector[hs_code] = 'other'
        
        print(f"Mapped {len(self.hs_to_sector)} product codes to sectors")
    
    def process_trade_data(self, year=None, bangladesh_code=50):
        """
        Process trade data for a specific year.
        
        Args:
            year (int, optional): Year to filter data
            bangladesh_code (int): Country code for Bangladesh in the dataset
            
        Returns:
            tuple: (export_data, import_data) as pandas DataFrames
        """
        # Load trade data
        trade_file = os.path.join(self.data_dir, 'bd_trade_data.csv')
        if not os.path.exists(trade_file):
            raise FileNotFoundError(f"Trade data file not found at {trade_file}")
        
        print(f"Loading trade data from {trade_file}...")
        # Using chunks for memory efficiency
        chunks = []
        for chunk in pd.read_csv(trade_file, chunksize=100000):
            # Filter for the specified year if provided
            if year is not None:
                chunk = chunk[chunk['t'] == year]
            
            # Only keep chunks with data after year filter
            if not chunk.empty:
                chunks.append(chunk)
        
        if not chunks:
            raise ValueError(f"No trade data found for year {year}")
        
        # Combine chunks
        trade_data = pd.concat(chunks, ignore_index=True)
        print(f"Loaded {len(trade_data)} trade records")
        
        # Add sector column based on product code
        trade_data['sector'] = trade_data['k'].apply(
            lambda x: self.hs_to_sector.get(x, 'other') if x in self.hs_to_sector 
            else self.hs_to_sector.get(int(str(x)[:2] + '0000') if len(str(x)) >= 2 else 0, 'other')
        )
        
        # Convert values from thousands to billions (for consistency with the model)
        trade_data['value_billions'] = trade_data['v'] / 1_000_000
        
        # Split into exports and imports (i=Bangladesh for exports, j=Bangladesh for imports)
        export_data = trade_data[trade_data['i'] == bangladesh_code].copy()
        import_data = trade_data[trade_data['j'] == bangladesh_code].copy()
        
        # Aggregate by sector
        export_by_sector = export_data.groupby('sector')['value_billions'].sum().reset_index()
        import_by_sector = import_data.groupby('sector')['value_billions'].sum().reset_index()
        
        # Rename to match model expectations
        export_by_sector.rename(columns={'value_billions': 'export_value'}, inplace=True)
        import_by_sector.rename(columns={'value_billions': 'import_value'}, inplace=True)
        
        return export_by_sector, import_by_sector
    
    def get_sector_totals(self, year=None):
        """
        Get total export value by sector for a specific year.
        
        Args:
            year (int, optional): Year to filter data
            
        Returns:
            dict: Sector export totals in billion USD
        """
        export_data, _ = self.process_trade_data(year)
        
        # Convert to dictionary format
        sector_totals = dict(zip(export_data['sector'], export_data['export_value']))
        
        # Ensure all model sectors are represented
        all_sectors = ['rmg', 'leather', 'jute', 'frozen_food', 'pharma', 
                      'it_services', 'light_engineering', 'agro_processing',
                      'home_textiles', 'shipbuilding']
        
        # Add missing sectors with zero values
        for sector in all_sectors:
            if sector not in sector_totals:
                sector_totals[sector] = 0.0
        
        return sector_totals


if __name__ == "__main__":
    # Example usage
    mapper = SectorMapper()
    export_data, import_data = mapper.process_trade_data(year=2023)
    
    print("\nExport totals by sector (billion USD):")
    for sector, value in export_data.sort_values('export_value', ascending=False).itertuples(index=False):
        print(f"{sector}: ${value:.3f} billion")
    
    print("\nImport totals by sector (billion USD):")
    for sector, value in import_data.sort_values('import_value', ascending=False).itertuples(index=False):
        print(f"{sector}: ${value:.3f} billion")
