# 🔑 Creating Google Gemini API Key - Step by Step

## Current Dialog: "No Cloud Projects Available"

### ✅ Solution: Create a New Project

When you see "No Cloud Projects Available" in the dropdown:

1. **Click the dropdown** where it says "No Cloud Projects Available"
2. Look for option: **"Create API key in new project"**
3. Click that option
4. Google will automatically:
   - Create a new Cloud project for you
   - Generate an API key
   - Associate the key with that project

### Alternative: Create Project First

If you don't see "Create API key in new project", do this:

1. **Cancel this dialog** (click Cancel)
2. **Visit:** https://console.cloud.google.com/projectcreate
3. **Create a new project:**
   - Project name: `PR Review Agent` (or anything you want)
   - Organization: (leave default)
   - Click **"Create"**
4. **Go back to AI Studio:** https://aistudio.google.com/app/apikey
5. **Click "Create API key"** again
6. Now your new project will appear in the dropdown
7. Select your project
8. Click **"Create key"**

### 📋 What to Fill In

```
┌─────────────────────────────────────────────────┐
│ Create a new key                                │
├─────────────────────────────────────────────────┤
│ Name your key (optional):                       │
│ ┌─────────────────────────────────────────────┐ │
│ │ PR Review Agent                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Choose an imported project:                     │
│ ┌─────────────────────────────────────────────┐ │
│ │ [Create API key in new project] ← Choose!   │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│           [Cancel]    [Create key]              │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Quick Answer for Your Case

**In the "Choose an imported project" dropdown:**
- Click it
- Select **"Create API key in new project"**
- Or if you see a project name, select it

Then click **"Create key"** button (it will become blue/enabled)

---

## ✅ After Creating the Key

1. **Copy the key immediately** (starts with `AIzaSy...`)
2. **Save it** somewhere safe (you can't see it again)
3. **Update these files:**

### File 1: `workers/.dev.vars`
```bash
GEMINI_API_KEY=AIzaSy_YOUR_KEY_HERE
```

### File 2: Update Cloudflare Worker
```powershell
cd C:\Users\versu\OneDrive\Desktop\PR@REVIEW\pr_review_agent\workers
echo "AIzaSy_YOUR_KEY_HERE" | npx wrangler secret put GEMINI_API_KEY
```

---

## 🚫 Troubleshooting

### "No Cloud Projects Available" won't go away
**Solution:** Create project manually first:
1. Visit: https://console.cloud.google.com/projectcreate
2. Create project: "PR Review Agent"
3. Return to AI Studio and try again

### "Create key" button is disabled/grayed out
**Solution:** You must either:
- Select "Create API key in new project" from dropdown, OR
- Create a project first and then select it

### Can't find the dropdown option
**Solution:** Click directly on "No Cloud Projects Available" text - it's a dropdown

---

## 📸 Visual Guide

```
Current screen:
┌──────────────────────────────────────────┐
│ Choose an imported project               │
│ ┌──────────────────────────────────────┐ │
│ │ No Cloud Projects Available      [▼] │ │  ← CLICK HERE
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘

After clicking:
┌──────────────────────────────────────────┐
│ Choose an imported project               │
│ ┌──────────────────────────────────────┐ │
│ │ ☑ Create API key in new project     │ │  ← SELECT THIS
│ │ ──────────────────────────────────── │ │
│ │ Or: Your existing projects show here │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

---

## ⏱️ What Happens Next

1. **Click "Create key"** (after selecting project option)
2. **Wait 2-5 seconds** - Google creates the key
3. **Key appears** in a dialog/text box
4. **COPY IT IMMEDIATELY** - You can't see it again!
5. **Use it** in your `workers/.dev.vars` file

---

## 💡 Pro Tip

If this is your first time using Google AI Studio:
- Just select "Create API key in new project"
- Google handles everything automatically
- No need to manually create a Cloud project

---

**TL;DR:** Click the "No Cloud Projects Available" dropdown → Select "Create API key in new project" → Click "Create key" → Copy the key! 🔑
