from setuptools import setup, find_packages

setup(
    name="atetest",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "dash>=2.11.0",
        "dash-bootstrap-components>=1.4.0",
        "python-dotenv>=1.0.0",
        "scikit-learn>=1.2.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0"
    ],
    python_requires=">=3.8",
) 