# Frontend Debugging Instructions

## Debug Logging Added

I've added comprehensive console logging to track the data flow:

### 1. execute.tsx - Query Execution Page
Logs the full API response:
```javascript
console.log('[QueryExecute] Received query result:', {
  columns, rowCount, executionTimeMs, sql,
  hasExportCsvUrl, hasExportJsonUrl,
  exportCsvUrl, exportJsonUrl, exportExpiresAt,
  fullData
});
```

### 2. ResultTable.tsx - Result Table Component
Logs:
- When component renders
- When useEffect triggers
- Export URL detection
- showExportPrompt state changes

### 3. ExportDialog.tsx - Export Dialog Component
Logs when component is called/renders with all props

---

## How to Debug

### Step 1: Open Browser Developer Console
1. Open your browser (Chrome/Edge/Firefox)
2. Go to http://localhost:5176
3. Press F12 to open Developer Tools
4. Click on "Console" tab

### Step 2: Execute a Query
1. Navigate to your database (e.g., "AldataBase")
2. Execute a simple query like: `SELECT 1 as id`
3. Watch the console output

### Step 3: Check Console Output

**Expected output sequence:**
1. `[QueryExecute] Received query result:` - Should show `hasExportCsvUrl: true`
2. `[ResultTable] Render called:` - Should show `hasExportCsvUrl: true`
3. `[ResultTable] useEffect triggered:` - Should show `shouldShow: true`
4. `[ResultTable] Export URLs detected, showing dialog:` - Confirmation
5. `[ResultTable] showExportPrompt state changed: true` - State update
6. `[ExportDialog] Render called:` - Dialog is rendering

### Step 4: Look for Issues

**If you don't see export URLs:**
- Check `[QueryExecute] Received query result:`
- If `hasExportCsvUrl: false`, the backend is not returning export URLs
- Check the Network tab to see the actual API response

**If export URLs are present but dialog doesn't show:**
- Check if `[ResultTable] Export URLs detected, showing dialog:` appears
- Check if `showExportPrompt state changed: true` appears
- Check for any React errors in console

---

## Quick Test Commands

### Test Backend API Directly:
```bash
curl -X POST "http://localhost:8000/api/v1/dbs/AldataBase/query" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT 1 as id"}'
```

Expected response should include:
- `exportCsvUrl`
- `exportJsonUrl`
- `exportExpiresAt`

### Check Servers Running:
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5176
```

---

## Common Issues

### Issue 1: Frontend not receiving export URLs
**Symptom:** `[QueryExecute]` shows `hasExportCsvUrl: false`
**Cause:** Backend not returning URLs
**Fix:** Restart backend server

### Issue 2: Dialog not showing despite URLs present
**Symptom:** URLs in response but no dialog
**Cause:** State management or React rendering issue
**Fix:** Check console errors

### Issue 3: Component renders but dialog not visible
**Symptom:** `[ExportDialog] Render called:` with `visible: true` but nothing shows
**Cause:** CSS or z-index issue
**Fix:** Check Ant Design Modal styles

---

## Next Steps

After checking the console:
1. Share the console output with me
2. I'll identify the exact issue
3. Apply the fix

The debugging logs will tell us exactly where the data flow breaks.
