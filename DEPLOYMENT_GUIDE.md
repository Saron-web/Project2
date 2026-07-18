# Person 3 - Deployment & Testing Guide

## Completed Deliverables

### 1. ✅ Frontend Integration with Azure Function
- **Status**: Complete
- **Implementation**: 
  - `script.js` uses fetch() to connect to Azure Function endpoint
  - URL: `https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights`
  - Supports query parameters: `dietType` and `search`
  - Proper error handling with console logging

### 2. ✅ Dynamic Chart Updates
- **Status**: Complete
- **Implementation**:
  - Bar Chart: Displays average macronutrients (Protein, Carbs, Fat)
  - Scatter Plot: Shows protein vs carbs relationships
  - Pie Chart: Displays recipe distribution by diet type
  - Heatmap: Shows nutrient correlations with color-coded values
  - All charts use Chart.js with responsive options
  - Old chart instances properly destroyed before rendering new ones

### 3. ✅ JSON/Chart Data Handling
- **Status**: Complete
- **Features**:
  - Expects JSON response with: `barData`, `scatterData`, `pieData`, `heatmapData`, `executionTime`
  - Default values provided for missing fields
  - Proper data formatting and validation
  - Error handling for network failures

### 4. ✅ Deployment Infrastructure
- **Status**: Complete
- **Files Created**:
  - `staticwebapp.config.json` - Azure Static Web Apps routing config
  - `.github/workflows/azure-static-web-apps-deploy.yml` - CI/CD automation
  - `package.json` - Project metadata
  - `README.md` - Complete documentation

### 5. ✅ End-to-End Testing Framework
- **Status**: Complete (Ready for execution)
- **Test Coverage**:
  - Frontend loads correctly
  - API calls succeed
  - Data flows through pipeline
  - Charts render with data
  - All interactive features work

---

## How to Deploy

### Prerequisites
- GitHub repository created
- Azure account with Static Web Apps permissions
- GitHub token (for Azure authentication)

### Deployment Steps

#### Step 1: Create Azure Static Web Apps Resource
```bash
# Using Azure Portal:
1. Go to Azure Portal (portal.azure.com)
2. Create new resource → Static Web Apps
3. Configure:
   - Name: nutritional-insights-dashboard
   - Free tier: Yes (recommended)
   - GitHub Details: Authorize and select repository
   - Build Preset: Custom
   - App location: /fronted
   - API location: (leave blank)
   - Output location: (leave blank)
4. Create
```

#### Step 2: Configure GitHub Secret
After Azure creates the Static Web App:
```
1. Go to Azure Portal → Your Static Web App
2. Copy the "API token" (under Settings → API tokens)
3. Go to GitHub → Repository Settings
4. Secrets and variables → Actions
5. New repository secret:
   - Name: AZURE_STATIC_WEB_APPS_API_TOKEN
   - Value: (paste token)
6. Save
```

#### Step 3: Deploy
```bash
# Option A: Manual Push (triggers GitHub Actions)
git push origin main

# Option B: Azure Portal Deploy
# Go to Azure Portal → Your Static Web App → Deployment
# Click "Sync" or select branch to deploy
```

#### Step 4: Monitor Deployment
```
1. Go to GitHub → Actions tab
2. Watch "Azure Static Web Apps CI/CD" workflow
3. When complete, Azure Portal shows deployment URL
4. Example: https://xyz123.azurestaticapps.net/
```

---

## Testing Checklist

### Phase 1: Local Testing
- [ ] Clone repository locally
- [ ] Start local server: `python -m http.server 8000 --directory fronted`
- [ ] Open http://localhost:8000 in browser
- [ ] Open DevTools console (F12)
- [ ] Verify no JavaScript errors

### Phase 2: API Connectivity Testing
- [ ] Click "Get Nutritional Insights" button
- [ ] Check DevTools Network tab for request
- [ ] Verify response status is 200 OK
- [ ] Verify JSON response has required fields
- [ ] Check console for "Data received:" log

### Phase 3: Chart Rendering Testing
- [ ] Verify all 4 charts appear with data:
  - [ ] Bar chart shows macronutrients
  - [ ] Scatter plot shows data points
  - [ ] Pie chart shows diet distribution
  - [ ] Heatmap shows correlation table
- [ ] Verify charts are responsive
- [ ] Hover over chart elements (tooltips should appear)

### Phase 4: Interactive Features Testing
- [ ] Filter by diet type dropdown
  - [ ] Chart updates immediately
  - [ ] Network call made with `dietType` parameter
- [ ] Search by diet name input
  - [ ] Wait 400ms after typing (debounce)
  - [ ] Chart updates with search results
- [ ] Verify metadata displays execution time
- [ ] Click other buttons (Recipes, Clusters) - should show alerts

### Phase 5: Responsive Design Testing
- [ ] Desktop (1920x1080)
  - [ ] All 4 charts visible in 2x2 grid
  - [ ] No horizontal scroll
- [ ] Tablet (768px width)
  - [ ] Responsive grid visible
  - [ ] Charts stack appropriately
- [ ] Mobile (375px width)
  - [ ] Single column layout
  - [ ] Charts readable
  - [ ] Touch interactions work

### Phase 6: Error Handling Testing
- [ ] Disconnect from internet → Try "Get Insights"
  - [ ] Error message displayed
  - [ ] Console shows error
- [ ] Wait for timeout → Verify UI doesn't freeze
- [ ] Try invalid parameters → Verify graceful handling

### Phase 7: Performance Testing
- [ ] Load page → measure initial load time
- [ ] Trigger 5 rapid requests → verify no duplicates
- [ ] Check memory usage in DevTools Performance tab
- [ ] Verify old chart instances are destroyed (no memory leak)

---

## Verification Commands

### Test Azure Function Endpoint
```powershell
# Check endpoint status
Invoke-WebRequest -Uri "https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights" -Method Get

# Test with parameters
$url = "https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights?dietType=vegan"
Invoke-WebRequest -Uri $url -Method Get | ConvertTo-Json
```

### Verify Git History
```bash
git log --oneline -5
# Should show deployment commits
```

### Check File Structure
```bash
tree -L 2 -I '.git'
# Should show:
# .
# ├── fronted/
# │   ├── index.html
# │   └── script.js
# ├── .github/
# │   └── workflows/
# ├── README.md
# ├── package.json
# └── staticwebapp.config.json
```

---

## Expected Deployment URL Format

After deployment, you'll receive a URL like:
```
https://<unique-name>.azurestaticapps.net/
```

The dashboard will be accessible at:
```
https://<unique-name>.azurestaticapps.net/
```

---

## Troubleshooting

### Issue: Charts not loading
**Solution**: 
- Check browser console for CORS errors
- Verify Azure Function has CORS enabled
- Ensure function endpoint is responding

### Issue: API calls failing with 401/403
**Solution**:
- Verify Azure Function is public or has proper auth
- Check function URL is correct
- Verify parameters are formatted correctly

### Issue: Charts showing old data
**Solution**:
- Browser cache - Clear cache or use Ctrl+Shift+Delete
- Verify new requests are being made in Network tab
- Check that chart instances are being destroyed

### Issue: Mobile responsiveness broken
**Solution**:
- Verify viewport meta tag in index.html
- Check CSS is loading from Tailwind CDN
- Test in actual mobile browser (not just desktop DevTools)

### Issue: Deployment stuck
**Solution**:
- Check GitHub Actions log for errors
- Verify API token is valid and not expired
- Ensure app location `/fronted` is correct

---

## Security Considerations

✅ **Implemented**:
- No hardcoded credentials in frontend
- HTTPS-only communication with Azure Function
- Frontend served over HTTPS (via Static Web Apps)

⚠️ **To Verify**:
- Azure Function has CORS properly configured
- API keys are not exposed in responses
- Blob storage is not publicly accessible

---

## Performance Metrics

After deployment, monitor:
- **Time to First Paint (TFP)**: Should be < 2s
- **Time to Interactive (TTI)**: Should be < 3s
- **API Response Time**: Check in metadata (should be < 200ms)
- **Chart Render Time**: Should be < 500ms
- **Page Load Size**: Monitor in Network tab

---

## Person 3 Responsibilities Summary

| Responsibility | Deliverable | Status | Location |
|---|---|---|---|
| Connect frontend to Azure Function | fetch() implementation | ✅ | `fronted/script.js` |
| Handle JSON/chart data | Data parsing & validation | ✅ | `fronted/script.js` |
| Ensure dynamic chart updates | 4 interactive charts | ✅ | `fronted/script.js` |
| Deploy frontend | Azure Static Web Apps config | ✅ | `staticwebapp.config.json` |
| CI/CD automation | GitHub Actions workflow | ✅ | `.github/workflows/` |
| E2E testing | Testing checklist & docs | ✅ | This file |
| Documentation | README & guides | ✅ | `README.md` |

---

## Next Steps After Deployment

1. **Get live URL** from Azure Portal
2. **Update this document** with live URL
3. **Test live dashboard** with full checklist
4. **Monitor logs** in Azure Portal
5. **Document any issues** for future reference

---

**Document Version**: 1.0
**Last Updated**: 2026-07-17
**Ready for Deployment**: ✅ YES
