#!/bin/bash

# ===========================================
# AwayLock Uninstaller
# ===========================================

PLIST_NAME="com.awaylock.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "==========================================="
echo "🗑  AwayLock — Uninstall"
echo "==========================================="
echo ""

# Stop agent
if launchctl list 2>/dev/null | grep -q "com.awaylock"; then
    echo "⏹  Stopping agent..."
    launchctl unload "$PLIST_PATH" 2>/dev/null
    echo "✅ Agent stopped"
else
    echo "ℹ️  Agent was not running"
fi

# Remove plist
if [ -f "$PLIST_PATH" ]; then
    rm "$PLIST_PATH"
    echo "✅ Plist removed"
else
    echo "ℹ️  Plist not found"
fi

echo ""
echo "==========================================="
echo "✅ AwayLock uninstalled"
echo "==========================================="
echo ""
echo "Files NOT removed (in case you want to reinstall):"
echo "   - Scripts: $(pwd)/*.py"
echo "   - Config:  $(pwd)/config.json"
echo "   - Logs:    ~/.awaylock.log"
echo ""
echo "For complete removal:"
echo "   rm -rf $(pwd)"
echo "   rm ~/.awaylock.log ~/.awaylock.error.log"
