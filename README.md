# Nutritional Insights Dashboard (Phase 2)

Live frontend: https://gentle-bush-041c4050f.7.azurestaticapps.net/
Backend function (example): https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights
Repo: https://github.com/Saron-web/Project2.git

Quick test (local):
  python -m http.server 8000 --directory fronted
  open http://localhost:8000 and click "Get Nutritional Insights"

Sample request:
  GET /api/get_nutritional_insights?dietType=keto

Sample (trimmed) response:
{
  "barData": {"labels": ["Protein","Carbs","Fat"], "values": [25.5,50.2,18.3]},
  "scatterData": {"points": [{"x":25.5,"y":50.2}]},
  "pieData": {"labels":["Vegan","Keto"],"values":[100,150]},
  "executionTime": "1.23ms"
}

Required Function App settings (set in Azure Portal):
  - AZURE_STORAGE_CONNECTION_STRING
  - AZURE_STORAGE_CONTAINER_NAME
  - AZURE_STORAGE_BLOB_NAME (if used)

CORS: Confirm the static app origin is allowed in the Function App Allowed Origins.

Submission blurb (paste into form):
The frontend is deployed at https://gentle-bush-041c4050f.7.azurestaticapps.net and calls the Azure Function at https://rishabh-diet-function-2026-crh8cfbxfhhybmf4.mexicocentral-01.azurewebsites.net/api/get_nutritional_insights. Repo: https://github.com/Saron-web/Project2.git. See this README for quick test steps. Screenshots can be provided on request.

Last updated: 2026-07-18
