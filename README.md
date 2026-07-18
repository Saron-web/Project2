# Nutritional Insights Dashboard

A dynamic frontend dashboard for visualizing nutritional data with interactive charts, connected to Azure Functions.

## Features

- **Interactive Charts**: Bar, scatter, pie, and heatmap visualizations
- **Real-time Data**: Dynamic chart updates with data from Azure Functions
- **Filtering**: Filter by diet type and search functionality
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Performance Metrics**: Displays execution time from backend

## Architecture

```
Frontend (HTML/JS) 
    ↓ (fetch())
Azure Functions Endpoint
    ↓
Azure Blob Storage
    ↓ (CSV data)
Backend Processing
    ↓
JSON Response
    ↓
Charts & Visualization
```

## API Integration

The dashboard connects to:
```
https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights
```

### Query Parameters
- `dietType` (optional): Filter by diet type (vegan, keto, mediterranean, dash, paleo)
- `search` (optional): Search by diet name

### Expected Response
```json
{
  "barData": {
    "labels": ["Protein", "Carbs", "Fat"],
    "values": [25.5, 50.2, 18.3]
  },
  "scatterData": {
    "points": [
      {"x": 25.5, "y": 50.2},
      ...
    ]
  },
  "pieData": {
    "labels": ["Vegan", "Keto", ...],
    "values": [100, 150, ...]
  },
  "heatmapData": [[1, 0.5, 0.2], ...],
  "executionTime": "1.23ms"
}
```

## Local Development

### Prerequisites
- Python 3.x (for local server)
- Modern web browser

### Running Locally

1. Clone the repository:
```bash
git clone <repo-url>
cd Project2
```

2. Start a local HTTP server:
```bash
python -m http.server 8000 --directory fronted
```

3. Open browser to `http://localhost:8000`

## Deployment to Azure Static Web Apps

### Option 1: Using Azure Portal

1. Create an Azure Static Web Apps resource in Azure Portal
2. Connect your GitHub repository
3. Configure build settings:
   - **App location**: `/fronted`
   - **API location**: (leave empty)
   - **Output location**: (leave empty)
4. Deploy

### Option 2: Using GitHub Actions

The repository includes an automated deployment workflow (`.github/workflows/azure-static-web-apps-deploy.yml`).

1. Create Azure Static Web Apps resource
2. In Azure Portal, copy the deployment token
3. Add secret to GitHub: `Settings → Secrets → Actions → New repository secret`
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: (paste the token)
4. Push to main branch - deployment automatically starts

### Option 3: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name myResourceGroup --location "East US"

# Create Static Web App
az staticwebapp create \
  --name nutritional-insights \
  --resource-group myResourceGroup \
  --location "East US" \
  --repo-url <github-repo-url> \
  --repo-token <github-token>
```

## Testing End-to-End Flow

### Verification Checklist
- [ ] Frontend loads without errors (check browser console)
- [ ] "Get Nutritional Insights" button fetches data
- [ ] Bar chart displays macronutrient data
- [ ] Scatter plot shows protein vs carbs relationship
- [ ] Pie chart displays diet type distribution
- [ ] Heatmap shows nutrient correlations
- [ ] Filter by diet type updates charts
- [ ] Search functionality works with debounce
- [ ] Execution time displays in metadata
- [ ] All charts render responsively on mobile

### Manual Testing Steps

1. Open dashboard in browser
2. Check Developer Console (F12) for any errors
3. Click "Get Nutritional Insights" button
4. Verify all charts populate with data
5. Select different diet types from dropdown
6. Type in search box to filter results
7. Verify metadata shows execution time

## Troubleshooting

### Charts Not Appearing
- Check browser console for errors (F12)
- Verify Azure Function endpoint is accessible
- Check CORS headers in Azure Function response

### Data Not Loading
- Verify Azure Function URL is correct
- Check network tab in DevTools for failed requests
- Ensure Azure Function has data in blob storage

### Slow Performance
- Monitor Azure Function logs
- Check backend processing time
- Verify network connectivity

## File Structure

```
Project2/
├── fronted/
│   ├── index.html       # Main HTML with chart containers
│   ├── script.js        # Chart rendering and API integration
├── staticwebapp.config.json    # Azure Static Web Apps configuration
├── package.json         # Project metadata
├── .github/
│   └── workflows/
│       └── azure-static-web-apps-deploy.yml  # CI/CD pipeline
└── README.md           # This file
```

## Performance Optimization

- Charts are rendered using Chart.js with responsive options
- Search uses 400ms debounce to avoid excessive API calls
- Old chart instances are destroyed before creating new ones
- Lazy loading of data on user interaction

## Browser Compatibility

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- IE11: ⚠️ May need polyfills

## Person 3 - Deployment Deliverables

| Item | Status | Details |
|------|--------|---------|
| Frontend Integration | ✅ Complete | fetch() connects to Azure Function |
| Dynamic Charts | ✅ Complete | Bar, Scatter, Pie, Heatmap charts |
| JSON Data Handling | ✅ Complete | Proper error handling and data formatting |
| Azure Deployment Config | ✅ Complete | staticwebapp.config.json and GitHub Actions |
| Live Dashboard URL | ✅ Deployed | https://gentle-bush-041c4050f.7.azurestaticapps.net |
| E2E Testing | ✅ Verified | Dashboard loads, API calls succeed, charts render correctly |

## Contact & Support

For questions about the deployment or technical issues, refer to the Azure Static Web Apps documentation or Azure Functions documentation.

---

**Last Updated**: 2026-07-18
**Deployed To**: https://gentle-bush-041c4050f.7.azurestaticapps.net
