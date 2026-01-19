"""AwayLock monitor - proximity detection and screen locking."""

from __future__ import annotations

import asyncio
import subprocess
from typing import TYPE_CHECKING

from bleak import BleakScanner

from config import Config, log

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice


class AwayLock:
    """Main proximity monitoring and screen locking logic."""

    def __init__(self, config: Config):
        self.config = config
        self.away_counter = 0
        self._running = True

    def stop(self) -> None:
        """Signal the monitor to stop."""
        self._running = False

    @staticmethod
    def lock_screen() -> None:
        """Turn off display (triggers lock)."""
        subprocess.run(["pmset", "displaysleepnow"], check=False)

    def is_target_device(self, device: BLEDevice) -> bool:
        """Check if this is our target device."""
        if self.config.device_address:
            return device.address.lower() == self.config.device_address.lower()
        if device.name and self.config.device_name:
            return self.config.device_name.lower() in device.name.lower()
        return False

    async def scan_all_devices(self) -> None:
        """Display all nearby BLE devices."""
        log.info("Scanning all Bluetooth devices (10 sec)...")
        print("-" * 60)

        devices = await BleakScanner.discover(timeout=10, return_adv=True)
        sorted_devices = sorted(
            devices.values(),
            key=lambda x: x[1].rssi,
            reverse=True
        )

        if not sorted_devices:
            print("No devices found!")
            print("-" * 60)
            return

        print(f"Found {len(sorted_devices)} devices (sorted by signal strength):\n")

        for i, (device, adv_data) in enumerate(sorted_devices, 1):
            name = device.name or "(unnamed)"
            rssi = adv_data.rssi
            addr = device.address
            print(f"{i:3}. {name}")
            print(f"     RSSI: {rssi} dBm | UUID: {addr}")

        print()
        print("-" * 60)
        print("To use a device, copy its UUID and run:")
        print('   python main.py --address "UUID" --save')
        print("-" * 60)

    async def find_device(self) -> tuple[bool, int | None, str | None]:
        """Find device via full scan. Returns (found, rssi, name)."""
        devices = await BleakScanner.discover(
            timeout=self.config.scan_duration,
            return_adv=True
        )
        for device, adv_data in devices.values():
            if self.is_target_device(device):
                return True, adv_data.rssi, device.name
        return False, None, None

    async def monitor(self) -> None:
        """Main monitoring loop."""
        cfg = self.config
        identifier = cfg.device_address or cfg.device_name
        search_by = "UUID" if cfg.device_address else "name"

        print("\n" + "=" * 60)
        print("AWAYLOCK STARTED")
        print("=" * 60)
        print(f"   Search by:   {search_by}")
        print(f"   Device:      {identifier}")
        print(f"   RSSI threshold: {cfg.rssi_threshold} dBm")
        print(f"   Scan duration:  {cfg.scan_duration} sec")
        print(f"   Lock trigger:   {cfg.away_count_threshold} consecutive checks")
        print("=" * 60)
        print("   Press Ctrl+C to stop\n", flush=True)

        while self._running:
            try:
                found, rssi, name = await self.find_device()
                display_name = name or str(identifier)[:20]

                if found and rssi is not None:
                    if rssi >= cfg.rssi_threshold:
                        self.away_counter = 0
                        log.info(f"Nearby: {display_name} (RSSI: {rssi})")
                    else:
                        self.away_counter += 1
                        log.info(
                            f"Far: {display_name} (RSSI: {rssi}) — "
                            f"{self.away_counter}/{cfg.away_count_threshold}"
                        )
                else:
                    self.away_counter += 1
                    log.info(
                        f"Device not found — "
                        f"{self.away_counter}/{cfg.away_count_threshold}"
                    )

                if self.away_counter >= cfg.away_count_threshold:
                    log.info("LOCKING SCREEN!")
                    self.lock_screen()
                    self.away_counter = 0
                    await asyncio.sleep(10)  # Cooldown after lock

                await asyncio.sleep(cfg.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Error: {e}")
                await asyncio.sleep(cfg.check_interval)

    async def calibrate(self) -> None:
        """Calibration mode — shows RSSI in real-time."""
        cfg = self.config
        identifier = cfg.device_address or cfg.device_name
        search_by = "UUID" if cfg.device_address else "name"

        print("\n" + "=" * 60)
        print("CALIBRATION MODE")
        print("=" * 60)
        print(f"   Search by:  {search_by}")
        print(f"   Device:     {identifier}")
        print("   Walk 5 meters away and note the RSSI value")
        print("   Press Ctrl+C to exit")
        print("=" * 60 + "\n", flush=True)

        while self._running:
            try:
                devices = await BleakScanner.discover(timeout=5, return_adv=True)

                found = False
                for device, adv_data in devices.values():
                    if self.is_target_device(device):
                        rssi = adv_data.rssi
                        name = device.name or "Device"
                        bar_len = max(0, min(30, rssi + 100))
                        bar = "█" * bar_len + "░" * (30 - bar_len)
                        print(f"{name}: RSSI {rssi:4d} dBm [{bar}]", flush=True)
                        found = True
                        break

                if not found:
                    print("Scanning... (device not found in this cycle)", flush=True)

            except asyncio.CancelledError:
                break
