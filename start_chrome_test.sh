#!/bin/bash

# Close any existing Chrome instances
pkill -f chrome

# Start Chrome with remote debugging on port 9222
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug-profile