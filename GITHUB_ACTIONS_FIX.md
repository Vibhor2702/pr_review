# GitHub Actions Job 50920448307 - Troubleshooting Guide

## 🔍 **Most Likely Issues & Solutions**

### **1. Missing GEMINI_API_KEY Secret (Most Common)**

**Problem:** The workflow needs a Google Gemini API key to function.

**Solution:**
1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GEMINI_API_KEY`
5. Value: Your actual Google Gemini API key from [Google AI Studio](https://makersuite.google.com/)

### **2. Python Version Compatibility**

**Problem:** The workflow was using Python 3.10, but the project may need 3.11+

**Solution:** ✅ **Fixed** - Updated workflow to use Python 3.11

### **3. Module Import Issues**

**Problem:** The `src.main` module couldn't be imported properly

**Solution:** ✅ **Fixed** - Added `pip install -e .` to install the package in development mode

### **4. Missing Artifacts Directory**

**Problem:** The workflow tries to upload artifacts but the directory doesn't exist

**Solution:** ✅ **Fixed** - Added `mkdir -p artifacts` before running the review

## 📋 **Quick Fixes Applied**

1. **Enhanced error checking** for missing secrets
2. **Updated Python version** to 3.11
3. **Added troubleshooting script** to debug environment issues
4. **Improved error handling** in the PR review step
5. **Updated GitHub Actions versions** (upload-artifact@v4, github-script@v7)
6. **Added debugging output** to see what's happening

## 🚀 **How to Apply the Fixes**

The workflow file has been updated with all necessary fixes. To apply them:

1. **Commit the changes:**
   ```bash
   git add .github/workflows/pr_review.yml scripts/troubleshoot.sh
   git commit -m "Fix GitHub Actions workflow - Job 50920448307"
   git push origin main
   ```

2. **Add the required secret:**
   - Go to your repository on GitHub
   - Settings → Secrets and variables → Actions
   - Add `GEMINI_API_KEY` with your actual API key

3. **Test the workflow:**
   - Create a new PR or push to an existing PR
   - Check the Actions tab for the workflow run

## 🔧 **Manual Debugging**

If the issue persists, you can run the troubleshooting script locally:

```bash
chmod +x scripts/troubleshoot.sh
./scripts/troubleshoot.sh
```

Or test the main functionality directly:

```bash
# Test import
python -c "import src.main; print('Success')"

# Test with demo data
python -m src.main review --provider github --owner microsoft --repo vscode --pr 123 --verbose
```

## 📊 **Workflow Changes Summary**

- ✅ Added secret validation
- ✅ Updated Python version (3.10 → 3.11)  
- ✅ Added package installation (`pip install -e .`)
- ✅ Enhanced error handling
- ✅ Added debugging steps
- ✅ Updated action versions
- ✅ Created troubleshooting script

## 🎯 **Next Steps**

1. **Immediate:** Add the `GEMINI_API_KEY` secret to your repository
2. **Push:** Commit and push the updated workflow file
3. **Test:** Create a test PR to verify the workflow works
4. **Monitor:** Check the Actions tab for successful runs

## 📞 **Still Having Issues?**

If the workflow still fails after these changes:

1. Check the **Actions** tab in your GitHub repository
2. Look at the **detailed logs** of each step
3. The troubleshooting script will provide environment details
4. Ensure your Gemini API key is valid and has sufficient quota

The most common cause of failure is missing the `GEMINI_API_KEY` secret. Make sure to add it to your repository secrets!