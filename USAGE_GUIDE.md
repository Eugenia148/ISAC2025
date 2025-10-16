# Centralized API Configuration Usage Guide

This guide explains how to use the centralized API configuration system for your ISAC 2025 project.

## 🚀 Quick Start

### 1. Set Up Your Credentials

Copy the example environment file and add your credentials:

```bash
cp env.example .env
```

Edit `.env` and add your StatsBomb credentials:

```env
SB_USERNAME=your_username
SB_PASSWORD=your_password
```

### 2. Import and Use

In any Python file or notebook, simply import the configuration:

```python
from src.config import get_statsbomb_client, is_premium_access

# Get authenticated client
sb = get_statsbomb_client()

# Check if you have premium access
if is_premium_access():
    print("✅ Premium access available")
else:
    print("ℹ️  Using open data access only")

# Use the client normally
competitions = sb.competitions()
matches = sb.matches(competition_id=73, season_id=317)
```

## 📁 What Was Created

### `src/config.py`
- **Centralized credential management**
- **Automatic authentication** when imported
- **Support for multiple credential naming conventions**
- **Status checking functions**

### `env.example`
- **Template for environment variables**
- **Documentation of supported credential formats**

### Updated Files
- **`src/get_data.py`** - Now uses centralized config
- **`src/pull_data.ipynb`** - Updated to use new system
- **`src/striker_role.ipynb`** - Updated to use new system

## 🔧 Supported Credential Formats

The system automatically detects credentials using these environment variable names:

1. **`SB_USERNAME`** / **`SB_PASSWORD`** (recommended)
2. **`STATSBOMB_USER`** / **`STATSBOMB_PASS`**
3. **`STATSBOMB_USERNAME`** / **`STATSBOMB_PASSWORD`**

## 📊 Benefits

### Before (Multiple Files)
```python
# In every file, you had to:
import os
from dotenv import load_dotenv
from statsbombpy import sb

load_dotenv()
username = os.getenv('SB_USERNAME')
password = os.getenv('SB_PASSWORD')
# Manual credential handling...
```

### After (Centralized)
```python
# Just one line:
from src.config import get_statsbomb_client
sb = get_statsbomb_client()
```

## 🛠️ Advanced Usage

### Check Authentication Status
```python
from src.config import is_premium_access

if is_premium_access():
    # Access premium data
    player_stats = sb.player_season_stats(competition_id=73, season_id=317)
else:
    # Use open data only
    print("Limited to open data access")
```

### Handle Authentication Errors
```python
from src.config import statsbomb_config

status = statsbomb_config.get_connection_status()
if "failed" in status:
    print(f"Authentication issue: {status}")
```

## 🔒 Security Notes

- **Never commit your `.env` file** (it's in `.gitignore`)
- **Use the `env.example` template** to document required variables
- **Credentials are loaded once** and cached for the session
- **Automatic fallback** to open data if credentials are missing

## 📝 Example Scripts

See `src/example_usage.py` for a complete example of how to use the centralized configuration.

## 🆘 Troubleshooting

### "No credentials found"
- Make sure you have a `.env` file in your project root
- Check that your credentials use one of the supported variable names
- Verify the credentials are correct

### "Authentication failed"
- Double-check your username and password
- Ensure your StatsBomb account has API access
- Try logging into the StatsBomb website to verify credentials

### Import errors
- Make sure you're importing from the correct path: `from src.config import ...`
- Ensure you're running from the project root directory
