# 🔧 Quick Fix Guide

## ✅ Issue Fixed!

The error "Failed to fetch PR" has been improved with better error messages. The app will now tell you exactly what went wrong.

---

## 🧪 Test With These Working PRs

### Option 1: Facebook React (Very Active)
- **Owner:** `facebook`
- **Repo:** `react`
- **PR Number:** Try a recent one from https://github.com/facebook/react/pulls
- Example: `31727`, `31726`, etc.

### Option 2: Microsoft VS Code
- **Owner:** `microsoft`  
- **Repo:** `vscode`
- **PR Number:** Try from https://github.com/microsoft/vscode/pulls
- Example: `232890`, `232889`, etc.

### Option 3: Your Own Repos
- Use any **public** GitHub repository
- Must be a **merged** or **open** PR
- Private repos won't work without a GitHub token

---

## 🐛 Common Issues & Fixes

### "Failed to fetch PR (404)"
**Cause:** PR doesn't exist or repo is private

**Fix:**
- Check the PR number is correct
- Make sure the repository is **public**
- Try the example PRs above

### "Failed to fetch PR (403)"
**Cause:** GitHub API rate limit (60 requests/hour without auth)

**Fix:**
- Wait an hour, or
- Add a GitHub token to the backend (see below)

### "Review API failed"
**Cause:** Backend API or Gemini issue

**Fix:**
- Check backend: https://pr-review-worker.kenshifan3000.workers.dev/api/status
- Should return `{"ok": true}`
- If not, check Gemini API key is configured

---

## 🎯 How to Test Right Now

1. **Visit:** https://pr-review.pages.dev
2. **Click:** "New Review"
3. **Enter:**
   ```
   Owner: facebook
   Repo: react
   PR Number: 31727
   ```
4. **Click:** "Start Review"
5. **Wait:** 5-10 seconds for AI analysis
6. **See:** Score, grade, and suggestions!

---

## 🔑 Optional: Add GitHub Token (For More Requests)

If you hit GitHub rate limits, add a token:

1. **Generate token:** https://github.com/settings/tokens
2. **Scopes needed:** `public_repo` (read public repositories)
3. **Add to Workers:**
   ```bash
   cd workers
   echo "YOUR_GITHUB_TOKEN" | npx wrangler secret put GITHUB_TOKEN
   ```

Then update the frontend code to send the token in requests.

---

## 🌐 Your Live URLs

**Frontend:** https://pr-review.pages.dev  
**Backend API:** https://pr-review-worker.kenshifan3000.workers.dev  
**Status Check:** https://pr-review-worker.kenshifan3000.workers.dev/api/status

---

## ✅ What's Working

- ✅ Backend API (Cloudflare Workers)
- ✅ Frontend (Cloudflare Pages)  
- ✅ Gemini AI integration
- ✅ GitHub API calls
- ✅ Better error messages

**Try it now with a valid PR!** 🚀
