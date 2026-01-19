#!/bin/bash

# Stop AwayLock service

PLIST_PATH="$HOME/Library/LaunchAgents/com.awaylock.plist"

if launchctl list 2>/dev/null | grep -q "com.awaylock"; then
    launchctl unload "$PLIST_PATH"
    echo "✅ AwayLock stopped"
else
    echo "ℹ️  AwayLock is not running"
fi
