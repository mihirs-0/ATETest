import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional

class WaferSimulator:
    def __init__(self, 
                 num_wafers: int = 100,
                 num_dies_per_wafer: int = 100,
                 num_test_bins: int = 10,
                 yield_target: float = 0.95,
                 variation: float = 0.05):
        """
        Initialize the wafer simulator.
        
        Args:
            num_wafers: Number of wafers to simulate
            num_dies_per_wafer: Number of dies per wafer
            num_test_bins: Number of test bins/categories
            yield_target: Target yield percentage
            variation: Allowed variation in yield
        """
        self.num_wafers = num_wafers
        self.num_dies_per_wafer = num_dies_per_wafer
        self.num_test_bins = num_test_bins
        self.yield_target = yield_target
        self.variation = variation
        
    def generate_test_data(self) -> pd.DataFrame:
        """Generate simulated wafer test data."""
        data = []
        current_time = datetime.now()
        
        for wafer_id in range(1, self.num_wafers + 1):
            # Generate random yield for this wafer
            wafer_yield = np.random.normal(self.yield_target, self.variation)
            wafer_yield = max(0, min(1, wafer_yield))  # Clamp between 0 and 1
            
            # Calculate number of passing dies
            num_passing = int(self.num_dies_per_wafer * wafer_yield)
            
            # Generate die data
            for die_id in range(1, self.num_dies_per_wafer + 1):
                is_passing = die_id <= num_passing
                
                # Generate test bin results
                test_results = {}
                for bin_id in range(1, self.num_test_bins + 1):
                    if is_passing:
                        # Passing dies have high probability of passing all tests
                        test_results[f'bin_{bin_id}'] = np.random.choice(
                            [True, False], 
                            p=[0.95, 0.05]
                        )
                    else:
                        # Failing dies have random test results
                        test_results[f'bin_{bin_id}'] = np.random.choice(
                            [True, False], 
                            p=[0.3, 0.7]
                        )
                
                # Add test parameters
                test_params = {
                    'voltage': np.random.normal(1.0, 0.1),
                    'current': np.random.normal(0.5, 0.05),
                    'temperature': np.random.normal(25, 2)
                }
                
                # Create data entry
                entry = {
                    'timestamp': current_time,
                    'wafer_id': f'WF{wafer_id:04d}',
                    'die_id': f'D{die_id:03d}',
                    'is_passing': is_passing,
                    **test_results,
                    **test_params
                }
                
                data.append(entry)
                
            # Increment time for next wafer
            current_time += timedelta(minutes=random.randint(5, 15))
            
        return pd.DataFrame(data)
    
    def save_to_csv(self, filename: str = 'wafer_test_data.csv'):
        """Save generated test data to CSV file."""
        df = self.generate_test_data()
        df.to_csv(filename, index=False)
        return df 