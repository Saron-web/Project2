# 🚀 Quick Deployment Reference

## One-Command Summary
This project is **100% ready for deployment** to Azure Static Web Apps. No additional code changes needed.

---

## ⚡ 5-Minute Deployment

### Step 1: Create Azure Resource (2 min)
```
1. Go to: portal.azure.com
2. Search: "Static Web Apps"
3. Click: Create
4. Fill:
   - Resource Group: Create new (e.g., "nutritional-insights")
   - Name: "nutritional-insights-dashboard"
   - Plan: Free
   - Region: (your region)
5. Click: Next
```

### Step 2: Connect GitHub (2 min)
```
1. Click: "Sign in with GitHub"
2. Select: your account
3. Select: your repo
4. Select: branch "main"
5. Click: Next
```

### Step 3: Configure Build (1 min)
```
Build Presets: Custom
App location: /fronted
API location: (leave blank)
Output location: (leave blank)
Click: Review + Create
```

---

## 🔑 Get Deployment Token

After Azure creates the resource:

```
1. Go to: Static Web App → Settings → API tokens
2. Copy: Deployment token
3. Go to: GitHub → Repo → Settings → Secrets
4. Click: New repository secret
5. Name: AZURE_STATIC_WEB_APPS_API_TOKEN
6. Value: (paste token)
7. Save
```

---

## 📤 Deploy

```bash
# This automatically deploys via GitHub Actions:
git push origin main

# Check status at:
# GitHub → Actions → "Azure Static Web Apps CI/CD"
```

---

## ✅ Get Live URL

After deployment completes (2-5 min):

```
Azure Portal → Your Static Web App → Overview → URL
Example: https://xyz-abc-123.azurestaticapps.net/
```

---

## 🧪 Test Live Dashboard

1. Open live URL in browser
2. Open DevTools Console (F12)
3. Click "Get Nutritional Insights"
4. Verify charts appear

---

## 📋 Quick Checklist

- [ ] Git repo created
- [ ] Azure account ready
- [ ] Azure Static Web Apps resource created
- [ ] GitHub repo connected
- [ ] Build settings: app location = /fronted
- [ ] GitHub secret added
- [ ] `git push origin main` executed
- [ ] Deployment completed (check Actions)
- [ ] Live URL obtained
- [ ] Dashboard tested

---

## 🔗 Important Links

| Item | URL |
|------|-----|
| Azure Portal | https://portal.azure.com |
| GitHub | https://github.com |
| This Repo | (your repo URL) |
| Azure Docs | https://learn.microsoft.com/en-us/azure/static-web-apps/ |
| Chart.js Docs | https://www.chartjs.org/docs/ |

---

## 🎯 Expected Result

After deployment:
- ✅ Public dashboard accessible
- ✅ Charts auto-load with data
- ✅ Filters work dynamically
- ✅ No console errors
- ✅ API calls successful
- ✅ Charts render correctly

---

## ⚠️ Troubleshooting

### Deployment Failed?
```
1. Check GitHub Actions log
2. Verify app location = /fronted
3. Ensure branch is main
```

### Charts Not Showing?
```
1. Open DevTools (F12)
2. Check for errors
3. Verify Azure Function is accessible
4. Try API_TEST.html
```

### API Returns Error?
```
1. Check Azure Function status
2. Verify data is in blob storage
3. Check CORS is enabled
```

---

## 📞 Need Help?

See full documentation:
- `README.md` - Feature documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment steps
- `API_TEST.html` - Interactive API testing

---

## 🎉 Success!

Your dashboard will be live at:
```
https://[your-app-name].azurestaticapps.net/
```

Share this URL with stakeholders!

---

**Ready to Deploy?** → Start with Step 1 above ⬆️
