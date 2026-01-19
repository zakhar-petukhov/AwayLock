#!/usr/bin/env python3
"""
AwayLock for macOS
Locks the screen when a Bluetooth device moves away from Mac
"""

import argparse
import asyncio
import signal

from config import Config
from monitor import AwayLock


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Lock Mac when a Bluetooth device moves away",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --scan                              Find all devices
  %(prog)s --address "ABC-123-DEF"             Monitor by UUID
  %(prog)s --address "ABC-123-DEF" --save      Save UUID to config
  %(prog)s --address "ABC-123-DEF" --calibrate Calibration mode
  %(prog)s --threshold -65                     Set RSSI threshold
        """
    )

    parser.add_argument("--scan", action="store_true",
                        help="Scan for all BLE devices")
    parser.add_argument("--address", "-a", type=str,
                        help="Device UUID/MAC address (recommended)")
    parser.add_argument("--name", "-n", type=str,
                        help="Device name (fallback)")
    parser.add_argument("--threshold", "-t", type=int,
                        help="RSSI threshold (default: -70)")
    parser.add_argument("--interval", "-i", type=int,
                        help="Seconds between checks")
    parser.add_argument("--scan-time", type=int,
                        help="Scan duration in seconds (default: 6)")
    parser.add_argument("--calibrate", "-c", action="store_true",
                        help="Calibration mode (shows RSSI)")
    parser.add_argument("--save", "-s", action="store_true",
                        help="Save settings to config file")

    return parser.parse_args()


async def main() -> None:
    """Main entry point."""
    args = parse_args()
    config = Config.load()

    # Apply command line arguments
    config.update(
        device_address=args.address,
        device_name=args.name,
        rssi_threshold=args.threshold,
        check_interval=args.interval,
        scan_duration=args.scan_time,
    )

    if args.save:
        config.save()

    monitor = AwayLock(config)

    # Set up graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, monitor.stop)

    if args.scan:
        await monitor.scan_all_devices()
    elif args.calibrate:
        if not config.device_address and not config.device_name:
            print("Specify --address or --name for calibration")
            print("Run --scan first to find the device UUID")
            return
        await monitor.calibrate()
    else:
        if not config.device_address and not config.device_name:
            print("Specify --address or --name")
            print("Run --scan first to find the device UUID")
            return
        await monitor.monitor()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nStopped")
