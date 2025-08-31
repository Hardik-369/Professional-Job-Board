# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### ❌ Error: "Client.init() got an unexpected keyword argument 'proxies'"

**Problem**: This error occurs when there's a version compatibility issue with the OpenAI library or when the client initialization receives unexpected parameters.

**Solutions Applied**:

1. **Enhanced Error Handling**: The ranking agent now gracefully handles OpenAI client initialization errors
2. **Fallback Mechanisms**: If OpenAI client fails, the app continues with basic ranking
3. **Version Compatibility**: Updated requirements.txt to use compatible OpenAI versions
4. **Multiple Initialization Methods**: Added fallback initialization approaches

**What was fixed**:
- ✅ Added try/catch blocks around OpenAI client initialization
- ✅ Implemented graceful degradation when API client fails
- ✅ Added compatibility layer for different OpenAI library versions
- ✅ Enhanced logging to identify and handle specific errors

### 🛠️ General Troubleshooting Steps

#### 1. Dependency Issues
```bash
# Reinstall dependencies with specific versions
pip uninstall openai
pip install openai>=1.3.0,<2.0.0

# Or reinstall all dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 2. API Key Issues
- Check that your API keys are correctly set in `.env` file
- Verify API keys are valid and have proper permissions
- The app works without API keys (basic mode)

#### 3. Network/Firewall Issues
- Check internet connection
- Verify no corporate firewall blocking API calls
- Try running with debug logging enabled

#### 4. Environment Issues
```bash
# Check Python version (requires 3.8+)
python --version

# Check if all packages are installed
pip list | grep -E "(streamlit|openai|firecrawl)"
```

### 🔍 Debug Mode

To enable debug logging, add this to your `.env` file:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

### 📊 System Status Check

The application includes a built-in health check:
1. Click "Health Check" button in the footer
2. Review system component status
3. Check API configuration status

### 🆘 If Problems Persist

1. **Check logs**: Look for error messages in the console
2. **Try basic mode**: The app works without API keys
3. **Update dependencies**: Run `pip install -r requirements.txt --upgrade`
4. **Restart application**: Close and restart Streamlit

### 📝 Error Reporting

If you encounter new errors:
1. Note the exact error message
2. Check which component is failing (Crawler, Search, Ranking, UI)
3. Verify your environment configuration
4. Try running the test script: `python test_fix.py`

## ✅ Verification

The application now includes:
- **Graceful error handling** - continues working even when components fail
- **Fallback mechanisms** - basic functionality when APIs unavailable
- **Better logging** - clear error messages and status updates
- **Compatibility fixes** - works with different library versions

Your job board should now work reliably! 🎯