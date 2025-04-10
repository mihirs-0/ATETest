import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

from src.data_generation.wafer_simulator import WaferSimulator
from src.analysis.metrics import ATEMetrics
from src.alerts.alert_system import AlertSystem
from src.dashboard.app import app

def load_config():
    """Load configuration from environment variables."""
    load_dotenv()
    
    email_config = {
        'sender': os.getenv('EMAIL_SENDER'),
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'username': os.getenv('EMAIL_USERNAME'),
        'password': os.getenv('EMAIL_PASSWORD')
    }
    
    slack_config = {
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
        'default_channel': os.getenv('SLACK_CHANNEL', '#alerts')
    }
    
    return email_config, slack_config

def main():
    # Load configuration
    email_config, slack_config = load_config()
    
    # Initialize components
    simulator = WaferSimulator()
    alert_system = AlertSystem(email_config, slack_config)
    
    # Generate test data
    print("Generating test data...")
    df = simulator.generate_test_data()
    
    # Initialize metrics calculator
    metrics = ATEMetrics(df)
    
    # Calculate metrics
    print("Calculating metrics...")
    yield_df = metrics.calculate_yield()
    test_coverage = metrics.calculate_test_coverage()
    cost_per_unit, cost_breakdown = metrics.calculate_cost_per_unit()
    
    # Check for yield drops
    print("Checking for yield drops...")
    alerts = metrics.detect_yield_drops()
    
    # Send alerts if needed
    if not alerts.empty:
        print("Sending alerts...")
        for _, alert in alerts.iterrows():
            alert_system.send_alert(
                alert_data=alert.to_dict(),
                recipients=['admin@example.com'],
                slack_channel='#yield-alerts'
            )
    
    # Print summary
    print("\nSummary:")
    print(f"Total Wafers: {len(yield_df)}")
    print(f"Average Yield: {yield_df['yield'].mean():.2%}")
    print(f"Cost per Good Die: ${cost_per_unit:.2f}")
    
    # Start dashboard
    print("\nStarting dashboard...")
    print("Access the dashboard at: http://localhost:8050")
    app.run(debug=True, host='0.0.0.0', port=8050)

if __name__ == '__main__':
    main() 