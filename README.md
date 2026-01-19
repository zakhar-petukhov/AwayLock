# AwayLock

Automatically lock your Mac when you walk away. Uses Bluetooth to detect when your phone, watch, or any other BLE device moves out of range.

## Requirements

- macOS
- Python 3.10+
- A Bluetooth device (iPhone, Apple Watch, AirPods, Fitbit, etc.)

## Quick Start

### 1. Clone and setup

```bash
git clone https://github.com/yourusername/AwayLock.git
cd AwayLock

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Find your device

Make sure Bluetooth is enabled on your Mac and your device is nearby.

```bash
python main.py --scan
```

You'll see a list of all nearby Bluetooth devices:

```
Found 12 devices (sorted by signal strength):

  1. iPhone
     RSSI: -45 dBm | UUID: ABC12345-1234-5678-9ABC-DEF012345678
  2. Apple Watch
     RSSI: -52 dBm | UUID: DEF67890-1234-5678-9ABC-DEF012345678
  3. AirPods Pro
     RSSI: -60 dBm | UUID: 123ABCDE-1234-5678-9ABC-DEF012345678
...
```

Copy the **UUID** of the device you want to use.

### 3. Save your device

```bash
python main.py --address "YOUR-UUID-HERE" --save
```

### 4. Test it

Run manually to make sure it works:

```bash
python main.py
```

You should see:
```
AWAYLOCK STARTED
   Search by:   UUID
   Device:      YOUR-UUID-HERE
   RSSI threshold: -70 dBm
   ...

[12:30:15] Nearby: iPhone (RSSI: -47)
[12:30:21] Nearby: iPhone (RSSI: -45)
```

Walk away from your Mac — it should lock when you're about 5 meters away.

Press `Ctrl+C` to stop.

### 5. Install as a background service (optional)

To run AwayLock automatically when you log in:

```bash
./install.sh
```

Done! AwayLock will now start automatically and run in the background.

## Commands

| Command | Description |
|---------|-------------|
| `python main.py --scan` | Find all nearby Bluetooth devices |
| `python main.py --address "UUID" --save` | Save device UUID to config |
| `python main.py` | Start monitoring |
| `python main.py --calibrate` | Show real-time signal strength |
| `python main.py --threshold -65` | Set custom RSSI threshold |
| `./install.sh` | Install as background service |
| `./uninstall.sh` | Remove background service |
| `./start.sh` | Start the service |
| `./stop.sh` | Stop the service |

## Configuration

Settings are stored in `config.json`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `device_address` | — | UUID of your Bluetooth device |
| `device_name` | — | Device name (fallback if no UUID) |
| `rssi_threshold` | -70 | Signal strength threshold in dBm |
| `away_count_threshold` | 3 | Consecutive weak signals before lock |
| `scan_duration` | 6 | Bluetooth scan duration in seconds |
| `check_interval` | 3 | Time between checks in seconds |

## Adjusting Sensitivity

**Locks too early?** Lower the threshold (e.g., `-80`):
```bash
python main.py --threshold -80 --save
```

**Doesn't lock when you walk away?** Raise the threshold (e.g., `-60`):
```bash
python main.py --threshold -60 --save
```

**Find the perfect value** using calibration mode:
```bash
python main.py --calibrate
```
Walk to the distance where you want it to lock and note the RSSI value shown.

### What is RSSI?

RSSI (Received Signal Strength Indicator) measures how strong the Bluetooth signal is:

```
RSSI (dBm)     Approximate Distance
─────────────────────────────────────
-40 to -50     Less than 1 meter
-50 to -60     1-2 meters
-60 to -70     2-4 meters
-70 to -80     4-7 meters
-80 to -90     More than 7 meters
```

The more negative the number, the weaker the signal (farther away).

## Viewing Logs

```bash
# Watch logs in real-time
tail -f ~/.awaylock.log

# Check for errors
cat ~/.awaylock.error.log
```

## Troubleshooting

### "No devices found"

- Make sure Bluetooth is enabled on your Mac
- Wake up your device (unlock your phone, tap your watch screen)
- Try scanning again — some devices don't advertise constantly

### Device not detected reliably

- Use UUID instead of device name (`--address` is more reliable than `--name`)
- Some devices go to sleep to save battery — try a device that stays active
- Reduce `scan_duration` in config if scans take too long

### Service not starting

Check the logs:
```bash
cat ~/.awaylock.error.log
```

Make sure the config file exists:
```bash
cat config.json
```

### Screen doesn't lock

- Make sure "Require password after sleep" is enabled in System Preferences → Security & Privacy
- Try running manually first: `python main.py`

## How It Works

1. AwayLock scans for Bluetooth devices every few seconds
2. When it finds your device, it checks the signal strength (RSSI)
3. If the signal is weak for several consecutive checks, it assumes you've walked away
4. It locks the screen using `pmset displaysleepnow`

## Files

```
AwayLock/
├── main.py           # Entry point
├── config.py         # Configuration management
├── monitor.py        # Bluetooth scanning and locking logic
├── config.json       # Your settings
├── install.sh        # Install as background service
├── uninstall.sh      # Remove background service
├── start.sh          # Start service
├── stop.sh           # Stop service
└── requirements.txt  # Python dependencies

~/.awaylock.log       # Application logs
~/.awaylock.error.log # Error logs
```

## License

MIT
