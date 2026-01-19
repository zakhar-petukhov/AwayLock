#!/bin/bash

# Start AwayLock service

PLIST_PATH="$HOME/Library/LaunchAgents/com.awaylock.plist"

if [ ! -f "$PLIST_PATH" ]; then
    echo "❌ AwayLock not installed. Run ./install.sh first"
    exit 1
fi

if launchctl list 2>/dev/null | grep -q "com.awaylock"; then
    echo "⚠️  AwayLock is already running"
else
    launchctl load "$PLIST_PATH"
    echo "✅ AwayLock started"
fi

echo ""
echo "📋 Logs: tail -f ~/.awaylock.log"
