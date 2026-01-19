#!/bin/bash

# ===========================================
# AwayLock Installer for macOS
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.awaylock.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==========================================="
echo "🔒 AwayLock — Installation"
echo "==========================================="
echo ""

# Check/create venv
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install --upgrade pip
    pip install bleak
    echo -e "${GREEN}✅ venv created${NC}"
else
    echo -e "${GREEN}✅ venv already exists${NC}"
fi

PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
SCRIPT_PATH="$SCRIPT_DIR/main.py"

# Check script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ main.py not found${NC}"
    exit 1
fi

# Check config
CONFIG_FILE="$SCRIPT_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}⚠️  Config not found!${NC}"
    echo "   First run:"
    echo "   $PYTHON_PATH $SCRIPT_PATH --scan"
    echo "   $PYTHON_PATH $SCRIPT_PATH --address \"YOUR-UUID\" --save"
    exit 1
fi

echo -e "${GREEN}✅ Config found: $CONFIG_FILE${NC}"

# Create LaunchAgents directory if needed
mkdir -p "$LAUNCH_AGENTS_DIR"

# Stop old agent if running
if launchctl list 2>/dev/null | grep -q "com.awaylock"; then
    echo "🔄 Stopping existing agent..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

# Create plist
echo "📝 Creating LaunchAgent..."

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.awaylock</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_PATH</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$HOME/.awaylock.log</string>
    
    <key>StandardErrorPath</key>
    <string>$HOME/.awaylock.error.log</string>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

echo -e "${GREEN}✅ Plist created: $PLIST_PATH${NC}"

# Load agent
echo "🚀 Starting agent..."
launchctl load "$PLIST_PATH"

# Check status
sleep 2
if launchctl list 2>/dev/null | grep -q "com.awaylock"; then
    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}✅ AwayLock installed and running!${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo "📋 Useful commands:"
    echo ""
    echo "   Status:    launchctl list | grep awaylock"
    echo "   Logs:      tail -f ~/.awaylock.log"
    echo "   Errors:    tail -f ~/.awaylock.error.log"
    echo "   Stop:      launchctl unload $PLIST_PATH"
    echo "   Start:     launchctl load $PLIST_PATH"
    echo "   Uninstall: ./uninstall.sh"
    echo ""
else
    echo -e "${RED}❌ Failed to start. Check logs:${NC}"
    echo "   cat ~/.awaylock.error.log"
fi
