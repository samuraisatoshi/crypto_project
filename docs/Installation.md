# Installation Guide

This guide provides step-by-step instructions for setting up the ML Trade project.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Git
- pip (Python package installer)
- TA-Lib dependencies

### Operating System Specific Setup

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-pip

# Install TA-Lib dependencies
sudo apt-get install -y ta-lib
```

#### macOS
```bash
# Using Homebrew
brew install ta-lib
```

#### Windows
1. Download TA-Lib from [here](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip)
2. Unzip and copy files to C:\ta-lib
3. Add C:\ta-lib\bin to PATH environment variable

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/projeto_ml_trade.git
cd projeto_ml_trade
```

2. Create and activate virtual environment:
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy example file
cp attribs.env.example attribs.env

# Edit with your values
nano attribs.env
```

Required environment variables:
- `BINANCE_API_KEY`: Your Binance API key
- `BINANCE_API_SECRET`: Your Binance API secret
- `DATA_DIR`: Directory for storing datasets
- `STORAGE_TYPE`: Local or cloud storage type

## Verification

1. Run tests:
```bash
pytest
```

2. Start the application:
```bash
streamlit run app_streamlit.py
```

3. Access the web interface:
```
http://localhost:8501
```

## Common Issues

### TA-Lib Installation

If you encounter issues installing TA-Lib:

#### Linux
```bash
# Alternative installation method
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

#### Windows
1. Use pre-built wheels:
```bash
pip install --index-url https://pypi.org/simple/ TA-Lib
```

2. Or download and install the appropriate wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)

### Other Common Issues

1. Memory Errors:
   - Increase system swap space
   - Use smaller datasets for testing
   - Enable data chunking

2. Performance Issues:
   - Use Parquet file format
   - Enable Streamlit caching
   - Optimize data loading

3. Data Storage:
   - Ensure sufficient disk space
   - Set correct permissions
   - Configure storage paths

## Updating

To update the project:

1. Pull latest changes:
```bash
git pull origin main
```

2. Update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

3. Run database migrations (if any):
```bash
python setup_env.py
```

## Development Setup

For development work:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Configure IDE:
- Use Python 3.8+
- Enable type checking
- Set up linting (flake8)
- Configure autoformatting (black)

## Cloud Storage Setup (Optional)

If using cloud storage:

1. Install cloud provider SDK
2. Configure credentials
3. Update storage settings in attribs.env

## Next Steps

After installation:
1. Review the ProjectExplanation.md for project overview
2. Check DataSetExplain.md for data format details
3. Start with downloading some test data
4. Try running a basic backtest

## Support

If you encounter any issues:
1. Check the logs in logs/
2. Review common issues above
3. Search existing GitHub issues
4. Create a new issue if needed
