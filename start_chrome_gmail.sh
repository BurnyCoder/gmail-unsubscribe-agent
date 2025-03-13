#!/bin/bash

# Close any existing Chrome instances with the debug profile
pkill -f "chrome.*--remote-debugging-port=9222" || true

# Try different Chrome binary names that might exist on the system
if command -v google-chrome &> /dev/null; then
    CHROME_BIN="google-chrome"
elif command -v google-chrome-stable &> /dev/null; then
    CHROME_BIN="google-chrome-stable"
elif command -v chromium-browser &> /dev/null; then
    CHROME_BIN="chromium-browser"
elif command -v chromium &> /dev/null; then
    CHROME_BIN="chromium"
else
    echo "Error: Chrome or Chromium browser not found"
    exit 1
fi

echo "Starting $CHROME_BIN with remote debugging..."
"$CHROME_BIN" --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug-profile https://gmail.com 