# 🚨 IMMEDIATE ACTION REQUIRED

## ⚠️ Your API Key Was Exposed on GitHub

GitGuardian detected your Gemini API key in the public repository.

---

## ✅ What I've Already Done

1. ✅ **Removed the exposed key from documentation**
   - `HOW_IT_WORKS.md` now uses placeholders
   - No real keys in any committed files

2. ✅ **Pushed security fix to GitHub**
   - Sanitized all documentation
   - Created incident report

---

## 🔴 WHAT YOU MUST DO NOW (5 minutes)

### Step 1: Delete/Revoke Old Key (1 minute)

I opened Google AI Studio for you. Follow these steps:

1. Find the key ending in: `...phT8Hig`
2. Click the **🗑️ Delete** button next to it
3. Confirm deletion

**Why:** Anyone who saw it on GitHub can use it until you delete it.

---

### Step 2: Create New Key (1 minute)

Still on https://aistudio.google.com/app/apikey:

1. Click **"Create API Key"**
2. Select your Google Cloud project (or "Create new project")
3. Click **"Create"**
4. **Copy the new key** (starts with `AIzaSy...`)

---

### Step 3: Update Local Development (1 minute)

Open this file in VS Code:
```
workers/.dev.vars
```

Replace the old key with your NEW key:
```bash
GEMINI_API_KEY=YOUR_NEW_KEY_HERE
```

Save the file.

---

### Step 4: Update Production Worker (2 minutes)

Run this in PowerShell (replace YOUR_NEW_KEY with your actual new key):

```powershell
cd C:\Users\versu\OneDrive\Desktop\PR@REVIEW\pr_review_agent\workers
echo "YOUR_NEW_KEY_HERE" | npx wrangler secret put GEMINI_API_KEY
```

This updates the production Cloudflare Worker with the new key.

---

### Step 5: Test Everything Works (1 minute)

**Test Local:**
```powershell
cd workers
npm run dev
# Visit http://localhost:8787/api/status
```

**Test Production:**
```powershell
curl https://pr-review-worker.kenshifan3000.workers.dev/api/status
```

If both return `"ok": true`, you're all set! ✅

---

## 🎯 Summary

- ⏱️ **Time Required:** 5 minutes
- 🔴 **Priority:** CRITICAL - Do this now
- ✅ **Documentation:** Already fixed (pushed to GitHub)
- 🔄 **Old Key:** Must be revoked (Step 1)
- 🆕 **New Key:** Generate and update (Steps 2-4)
- 🧪 **Testing:** Verify everything works (Step 5)

---

## 📋 Quick Checklist

Copy this and check off as you complete:

```
[ ] Revoked old key on Google AI Studio
[ ] Generated new key
[ ] Updated workers/.dev.vars
[ ] Updated Cloudflare Worker secret
[ ] Tested local dev server works
[ ] Tested production API works
```

---

## ❓ Need Help?

If anything doesn't work:
1. Check `SECURITY_INCIDENT.md` for detailed troubleshooting
2. Make sure you copied the NEW key correctly (no spaces)
3. Make sure you're in the `workers/` directory for commands

---

**🚀 Once complete, your app will be secure and fully functional!**
