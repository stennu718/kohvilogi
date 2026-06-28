# Screenshots

This directory contains screenshots for the README.

## What to Capture

Please take screenshots of the following screens at **1280x800** resolution (or similar 16:10):

| File | Screen | Description |
|------|--------|-------------|
| `screenshot-dashboard.png` | Main page | Dashboard showing recent entries, quick stats, and add form |
| `screenshot-map.png` | World map page | Interactive map with coffee regions highlighted |
| `screenshot-stats.png` | Statistics page | Charts/monthly breakdown and consumption analytics |
| `screenshot-passport.png` | Coffee passport | Country passport view showing visited countries |

## How to Capture

1. Start the application: `uvicorn app.main:app --reload`
2. Navigate to `http://localhost:8000`
3. Log a few sample entries to make screenshots look realistic
4. Use your browser's DevTools (F12 → Device Toolbar) to set viewport to 1280x800
5. Save screenshots as PNG files in this directory

## Notes

- Use light theme for consistency
- Use a sample dataset with ~10-20 entries across different countries for a populated look
- Ensure no personal/real data is visible in screenshots
