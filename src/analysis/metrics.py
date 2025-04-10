import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta

class ATEMetrics:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the metrics calculator with test data.
        
        Args:
            df: DataFrame containing wafer test data
        """
        self.df = df
        self.bin_columns = [col for col in df.columns if col.startswith('bin_')]
        
    def calculate_yield(self, group_by: str = 'wafer_id') -> pd.DataFrame:
        """
        Calculate yield metrics.
        
        Args:
            group_by: Column to group by (e.g., 'wafer_id', 'timestamp')
            
        Returns:
            DataFrame with yield metrics
        """
        yield_df = self.df.groupby(group_by).agg({
            'is_passing': ['count', 'sum']
        }).reset_index()
        
        yield_df.columns = [group_by, 'total_dies', 'passing_dies']
        yield_df['yield'] = yield_df['passing_dies'] / yield_df['total_dies']
        
        return yield_df
    
    def calculate_test_coverage(self) -> Dict[str, float]:
        """
        Calculate test coverage for each bin.
        
        Returns:
            Dictionary with coverage percentages for each test bin
        """
        coverage = {}
        for bin_col in self.bin_columns:
            total_tests = len(self.df)
            passed_tests = self.df[bin_col].sum()
            coverage[bin_col] = passed_tests / total_tests
            
        return coverage
    
    def calculate_cost_per_unit(self, 
                              wafer_cost: float = 1000.0,
                              test_cost_per_die: float = 0.5) -> Tuple[float, pd.DataFrame]:
        """
        Calculate cost metrics.
        
        Args:
            wafer_cost: Cost per wafer
            test_cost_per_die: Cost to test each die
            
        Returns:
            Tuple of (average_cost_per_good_die, cost_breakdown_df)
        """
        # Calculate total cost
        total_wafers = self.df['wafer_id'].nunique()
        total_dies = len(self.df)
        total_passing = self.df['is_passing'].sum()
        
        total_cost = (total_wafers * wafer_cost) + (total_dies * test_cost_per_die)
        cost_per_good_die = total_cost / total_passing if total_passing > 0 else float('inf')
        
        # Create cost breakdown
        cost_breakdown = pd.DataFrame({
            'metric': ['Total Wafers', 'Total Dies', 'Passing Dies', 'Total Cost', 'Cost per Good Die'],
            'value': [total_wafers, total_dies, total_passing, total_cost, cost_per_good_die]
        })
        
        return cost_per_good_die, cost_breakdown
    
    def analyze_correlations(self) -> pd.DataFrame:
        """
        Analyze correlations between test bins and parameters.
        
        Returns:
            DataFrame with correlation matrix
        """
        # Combine bin results and test parameters
        analysis_cols = self.bin_columns + ['voltage', 'current', 'temperature']
        return self.df[analysis_cols].corr()
    
    def detect_yield_drops(self, 
                          threshold: float = 0.95,
                          window_size: int = 5) -> pd.DataFrame:
        """
        Detect significant yield drops.
        
        Args:
            threshold: Minimum acceptable yield
            window_size: Number of wafers to consider in rolling window
            
        Returns:
            DataFrame with yield drop alerts
        """
        yield_df = self.calculate_yield()
        yield_df['rolling_yield'] = yield_df['yield'].rolling(window=window_size).mean()
        
        alerts = yield_df[yield_df['rolling_yield'] < threshold].copy()
        alerts['alert_type'] = 'Yield Drop'
        alerts['severity'] = np.where(
            alerts['rolling_yield'] < threshold * 0.9,
            'Critical',
            'Warning'
        )
        
        return alerts[['wafer_id', 'rolling_yield', 'alert_type', 'severity']] 