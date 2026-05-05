"""
data_loader.py - Dynamic CSV loading from data folder
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path


class DataLoader:
    """
    Loads CSV files from the data folder dynamically.
    
    Attributes
    ----------
    data_dir : Path
        Path to the data folder
    datasets : dict
        Dictionary mapping dataset names to (x_data, y_data) tuples
    available_names : list
        List of available dataset names
    """
    
    def __init__(self, data_dir='./data'):
        """
        Initialize DataLoader.
        
        Parameters
        ----------
        data_dir : str, optional
            Path to data folder (default: './data')
        """
        self.data_dir = Path(data_dir)
        self.datasets = {}
        self.available_names = []
        self._load_all_datasets()
    
    def _load_all_datasets(self):
        """Scan and load all CSV files from data directory."""
        if not self.data_dir.exists():
            print(f"Warning: Data directory {self.data_dir} not found.")
            return
        
        csv_files = list(self.data_dir.glob('*.csv'))
        for csv_file in csv_files:
            try:
                name = csv_file.stem  # filename without extension
                x, y = self._load_csv(csv_file)
                if x is not None and y is not None:
                    self.datasets[name] = (x, y)
                    self.available_names.append(name)
                    print(f"✓ Loaded dataset: {name}")
            except Exception as e:
                print(f"✗ Failed to load {csv_file.name}: {e}")
    
    def _load_csv(self, filepath):
        """
        Load a CSV file and extract two columns.
        
        Parameters
        ----------
        filepath : Path
            Path to CSV file
        
        Returns
        -------
        tuple or (None, None)
            (x_array, y_array) or (None, None) on error
        """
        try:
            df = pd.read_csv(filepath)
            
            if df.shape[1] < 2:
                raise ValueError(f"CSV must have at least 2 columns, got {df.shape[1]}")
            
            # Extract first two columns
            x = df.iloc[:, 0].values.astype(float)
            y = df.iloc[:, 1].values.astype(float)
            
            # Validate data
            if len(x) < 2:
                raise ValueError("Need at least 2 data points")
            
            if not np.all(np.diff(x) > 0):
                # Sort by x if not already sorted
                idx = np.argsort(x)
                x = x[idx]
                y = y[idx]
            
            return x, y
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None, None
    
    def get_dataset(self, name):
        """
        Retrieve a dataset by name.
        
        Parameters
        ----------
        name : str
            Dataset name (filename without .csv)
        
        Returns
        -------
        tuple
            (x_array, y_array) or (None, None) if not found
        """
        return self.datasets.get(name, (None, None))
    
    def get_available_datasets(self):
        """Return list of available dataset names."""
        return self.available_names.copy()
    
    def reload(self):
        """Reload all datasets (useful for dynamic file updates)."""
        self.datasets.clear()
        self.available_names.clear()
        self._load_all_datasets()
