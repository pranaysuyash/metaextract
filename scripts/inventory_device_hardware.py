#!/usr/bin/env python3
"""Device and Hardware metadata field inventory.

This script generates an inventory of device and hardware fingerprinting
fields used in digital forensics and security analysis:

- Device identifiers (serial numbers, IMEI, MAC addresses)
- Hardware signatures (CPU, motherboard, TPM)
- Firmware versions (BIOS, UEFI, device firmware)
- Peripheral devices (printers, scanners, cameras)
- Mobile device metadata
- IoT device fields
"""

import json
from pathlib import Path
from typing import Dict, List


# Device identifier fields
DEVICE_IDENTIFIERS = [
    # Serial numbers
    "SerialNumber", "Serial_No", "Serial_Number", "SerialID",
    "DeviceSerial", "AssetTag", "ServiceTag", "ProductID",
    "VendorID", "ProductName", "VendorName", "Manufacturer",
    "ModelNumber", "ModelName", "Revision", "Version",

    # IMEI/MEID
    "IMEI", "IMEI1", "IMEI2", "MEID", "ESN", "DeviceID",
    "SIM_ID", "SIM_Serial", "ICCID", "IMSI", "MSISDN",

    # MAC addresses
    "MAC_Address", "MAC", "MAC_Addr", "Hardware_Address",
    "Ethernet_Address", "WiFi_MAC", "Bluetooth_MAC", "Ethernet_MAC",
    "MAC_Address_Primary", "MAC_Address_Secondary",

    # UUIDs/GUIDs
    "UUID", "GUID", "DeviceUUID", "SystemUUID", "MachineGUID",
    "InstallationID", "ComputerName", "HostName", "DomainName",
    "NetBIOS_Name", "SID", "MachineSID", "ObjectGUID",
]

# Hardware signature fields
HARDWARE_SIGNATURES = [
    # CPU
    "CPU_ID", "CPU_Info", "CPU_Architecture", "CPU_Family",
    "CPU_Model", "CPU_Stepping", "CPU_Cores", "CPU_Threads",
    "CPU_Speed", "CPU_Bits", "CPU_Vendor", "CPU_Brand",
    "CPU_Features", "CPU_Flags", "CPU_microcode", "CPU_Platform",
    "CPU_Signature", "CPU_BSP", "CPU_APIC", "CPU_TSC",

    # Motherboard
    "Motherboard_Manufacturer", "Motherboard_Model", "Motherboard_Rev",
    "Motherboard_SN", "Bios_Board", "System_Board", "Baseboard",
    "Baseboard_Manufacturer", "Baseboard_Model", "Baseboard_SN",

    # Chipset
    "Chipset", "Northbridge", "Southbridge", "PCI_Bridge",
    "ISA_Bridge", "SATA_Controller", "USB_Controller",

    # Memory
    "RAM_Size", "RAM_Slots", "RAM_Type", "RAM_Speed",
    "RAM_Vendor", "RAM_Part", "RAM_Serial", "Memory_Size",
    "Memory_Channels", "Memory_Timing", "Memory_Voltage",

    # Storage
    "Disk_Model", "Disk_Vendor", "Disk_Serial", "Disk_Firmware",
    "Disk_Size", "Disk_Interface", "Disk_Protocol", "SSD_Model",
    "NVMe_Model", "NVMe_Serial", "NVMe_Firmware",

    # TPM
    "TPM_Version", "TPM_Manufacturer", "TPM_Firmware",
    "TPM_Spec_Version", "TPM_Pcr_Banks", "TPM_Family",
    "TPM_Manufacturer_ID", "TPM_Revision", "TPM_Device_ID",

    # GPU
    "GPU_Model", "GPU_Vendor", "GPU_RAM", "GPU_BIOS",
    "GPU_Serial", "GPU_Version", "GPU_Bus", "GPU_PCIe",
    "CUDA_Version", "OpenCL_Version", "Vulkan_Version",

    # BIOS/UEFI
    "BIOS_Vendor", "BIOS_Version", "BIOS_Date", "BIOS_Revision",
    "BIOS_ID", "BIOS_Firmware", "UEFI_Vendor", "UEFI_Version",
    "UEFI_Date", "SecureBoot", "SecureBoot_Status", "Boot_Mode",
    "Boot_Order", "Boot_Priority", "Legacy_Boot", "EFI_System_Partition",
]

# Firmware version fields
FIRMWARE_VERSIONS = [
    # BIOS/UEFI
    "BIOS_Version", "BIOS_Date", "BIOS_Revision", "BIOS_Firmware",
    "BIOS_Vendor", "BIOS_ID", "BIOS_Rom_Size", "BIOS_Language",
    "BIOS_Characteristic", "BIOS_Features", "BIOS_Supported",

    # UEFI
    "UEFI_Vendor", "UEFI_Version", "UEFI_Date", "UEFI_Revision",
    "UEFI_Build", "UEFI_SecureBoot", "UEFI_PE_Cert", "UEFI_Cert",

    # Device firmware
    "Firmware_Version", "Firmware_Date", "Firmware_Revision",
    "Firmware_Build", "Firmware_Patch", "Firmware_Author",
    "Firmware_Signature", "Firmware_Hash", "Firmware_Checksum",

    # Network firmware
    "NIC_Firmware", "WiFi_Firmware", "Bluetooth_Firmware",
    "Modem_Firmware", "Baseband_Firmware", "RF_Firmware",

    # Peripheral firmware
    "Printer_Firmware", "Scanner_Firmware", "Camera_Firmware",
    "Keyboard_Firmware", "Mouse_Firmware", "Touchpad_Firmware",
    "Display_Firmware", "Monitor_Firmware", "Projector_Firmware",

    # Storage firmware
    "SSD_Firmware", "HDD_Firmware", "NVMe_Firmware", "USB_Firmware",
    "RAID_Controller_Firmware", "SAS_Controller_Firmware",

    # Mobile firmware
    "Baseband_Version", "Modem_Version", "Radio_Version",
    "Bootloader_Version", "HLOS_Version", "Firmware_Version",
    "EFS_Version", "RPM_Version", "SBL_Version", "ABOOT_Version",
    "TrustZone_Version", "TZ_Version", "Hypervisor_Version",
]

# Peripheral device fields
PERIPHERAL_DEVICES = [
    # Printers
    "Printer_Name", "Printer_Model", "Printer_Serial", "Printer_IP",
    "Printer_MAC", "Printer_Status", "Printer_Counter", "Printer_Pages",
    "Printer_Toner", "Printer_Config", "Printer_Jobs", "Printer_Queue",

    # Scanners
    "Scanner_Name", "Scanner_Model", "Scanner_Serial", "Scanner_Res",
    "Scanner_Bit_Depth", "Scanner_Optical_Res", "Scanner_Feeder",
    "Scanner_Duplex", "Scanner_Speed", "Scanner_Interface",

    # Cameras
    "Camera_Name", "Camera_Model", "Camera_Serial", "Camera_Res",
    "Camera_MegaPixels", "Camera_Sensor", "Camera_Lens", "Camera_Flash",
    "Camera_Zoom", "Camera_ISO", "Camera_Firmware", "Camera_Mode",

    # Monitors
    "Monitor_Name", "Monitor_Model", "Monitor_Serial", "Monitor_Size",
    "Monitor_Res", "Monitor_Bit_Depth", "Monitor_Refresh", "Monitor_Type",
    "Monitor_Backlight", "Monitor_Panel", "Monitor_EDID",

    # Keyboards
    "Keyboard_Name", "Keyboard_Model", "Keyboard_Type", "Keyboard_Layout",
    "Keyboard_Backlight", "Keyboard_Firmware", "Keyboard_Macro",

    # Mice
    "Mouse_Name", "Mouse_Model", "Mouse_Type", "Mouse_Sensor",
    "Mouse_DPI", "Mouse_Buttons", "Mouse_Polling", "Mouse_Firmware",

    # Storage devices
    "USB_Device", "USB_Vendor", "USB_Product", "USB_Serial",
    "USB_Version", "USB_Speed", "USB_Power", "USB_Hub",
    "Thunderbolt_Device", "FireWire_Device", "eSATA_Device",

    # Audio
    "Audio_Device", "Audio_Codec", "Audio_Sample_Rate", "Audio_Bits",
    "Audio_Channels", "Audio_Firmware", "Microphone", "Speaker",

    # Network devices
    "Network_Adapter", "NIC_Name", "NIC_Model", "NIC_Speed",
    "NIC_Port", "NIC_Connection", "NIC_Virtual", "NIC_Bond",
]

# Mobile device fields
MOBILE_DEVICE = [
    # iOS
    "iOS_Version", "iPad_Version", "iPhone_Name", "iPhone_Model",
    "iPhone_Generation", "iPhone_Chip", "iPhone_Architecture",
    "Apple_TV_Version", "iPod_Version", "Watch_Version",
    "Watch_Model", "Watch_Generation", "Watch_Size", "Watch_Band",
    "iOS_Build", "iOS_Revision", "iOS_Beta", "iOS_Update",

    # Android
    "Android_Version", "Android_Security_Patch", "Android_Patch_Level",
    "Android_Build", "Android_Build_Number", "Baseband_Version",
    "Kernel_Version", "Linux_Version", "System_Version",
    "MIUI_Version", "ColorOS_Version", "OxygenOS_Version",
    "OneUI_Version", "EMUI_Version", "Flyme_Version",

    # Device info
    "Device_Name", "Device_Model", "Device_Brand", "Device_Product",
    "Device_Manufacturer", "Device_Hardware", "Device_Board",
    "Device_Platform", "Device_SOC", "Device_Chipset",
    "Device_CPU_ABI", "Device_Cores", "Device_Supported_ABIs",

    # Display
    "Display_Resolution", "Display_Density", "Display_Size",
    "Display_PPI", "Display_HDR", "Display_Brightness",
    "Display_Refresh_Rate", "Display_Protection", "Display_Type",

    # Battery
    "Battery_Capacity", "Battery_Type", "Battery_Health",
    "Battery_Temperature", "Battery_Voltage", "Battery_Cycle",
    "Battery_Charging", "Fast_Charging", "Wireless_Charging",

    # Sensors
    "Accelerometer", "Gyroscope", "Magnetometer", "Proximity",
    "Light_Sensor", "Barometer", "Heart_Rate", "Fingerprint",
    "Face_Unlock", "Iris_Scanner", "GPS", "GLONASS",
    "Beidou", "Galileo", "NFC", "Bluetooth", "WiFi", "Cellular",
]

# IoT device fields
IOT_DEVICES = [
    # Smart home
    "Smart_TV", "Smart_TV_Model", "Smart_TV_OS", "Smart_TV_Apps",
    "Smart_Speaker", "Voice_Assistant", "Smart_Lock", "Smart_Thermostat",
    "Smart_Camera", "Smart_Doorbell", "Smart_Plug", "Smart_Bulb",
    "Smart_Switch", "Smart_Sensor", "Smart_Appliance", "Smart_Meter",

    # Wearables
    "Smart_Watch", "Fitness_Tracker", "Heart_Rate_Monitor", "Sleep_Tracker",
    "GPS_Tracker", "Pedometer", "VR_Headset", "AR_Glasses",

    # Industrial IoT
    "PLC", "SCADA", "Industrial_Sensor", "Industrial_Camera",
    "Robotics", "CNC_Machine", "3D_Printer", "Drone", "UGV", "UAV",

    # Medical IoT
    "Pacemaker", "Insulin_Pump", "Hearing_Aid", "Medical_Monitor",
    "Health_Tracker", "Blood_Glucose_Monitor", "Pulse_Oximeter",

    # Automotive
    "ECU", "ECU_Version", "TCU", "Telematic_Unit", "Infotainment",
    "GPS_Navigation", "Dash_Camera", "OBD2", "CAN_Bus", "VIN",
]

# Generate complete inventory
def generate_inventory(output_dir: Path) -> None:
    """Generate device and hardware metadata field inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "generated_at": "",
        "source": "Hardware Specifications and Device Fingerprinting Standards",
        "categories": {},
    }

    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Device identifiers
    inventory["categories"]["Device_Identifiers"] = {
        "description": "Device identifier fields (serial, IMEI, MAC, UUID)",
        "fields": sorted(DEVICE_IDENTIFIERS),
        "count": len(DEVICE_IDENTIFIERS),
    }

    # Hardware signatures
    inventory["categories"]["Hardware_Signatures"] = {
        "description": "Hardware fingerprinting fields (CPU, motherboard, TPM)",
        "fields": sorted(HARDWARE_SIGNATURES),
        "count": len(HARDWARE_SIGNATURES),
    }

    # Firmware versions
    inventory["categories"]["Firmware_Versions"] = {
        "description": "Firmware version fields (BIOS, UEFI, device)",
        "fields": sorted(FIRMWARE_VERSIONS),
        "count": len(FIRMWARE_VERSIONS),
    }

    # Peripheral devices
    inventory["categories"]["Peripheral_Devices"] = {
        "description": "Peripheral device fields (printers, scanners, cameras)",
        "fields": sorted(PERIPHERAL_DEVICES),
        "count": len(PERIPHERAL_DEVICES),
    }

    # Mobile device
    inventory["categories"]["Mobile_Device"] = {
        "description": "Mobile device fields (iOS, Android)",
        "fields": sorted(MOBILE_DEVICE),
        "count": len(MOBILE_DEVICE),
    }

    # IoT devices
    inventory["categories"]["IoT_Devices"] = {
        "description": "IoT device fields (smart home, wearables, industrial)",
        "fields": sorted(IOT_DEVICES),
        "count": len(IOT_DEVICES),
    }

    # Calculate totals
    all_fields = (
        DEVICE_IDENTIFIERS + HARDWARE_SIGNATURES + FIRMWARE_VERSIONS +
        PERIPHERAL_DEVICES + MOBILE_DEVICE + IOT_DEVICES
    )
    unique_fields = len(set(all_fields))

    inventory["totals"] = {
        "total_fields": len(all_fields),
        "unique_fields": unique_fields,
        "categories": len(inventory["categories"]),
    }

    # Write JSON
    output_path = output_dir / "device_hardware_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print("DEVICE AND HARDWARE INVENTORY SUMMARY")
    print("=" * 60)
    print()
    print(f"Total fields: {len(all_fields):,}")
    print(f"Unique fields: {unique_fields:,}")
    print(f"Categories: {len(inventory['categories'])}")
    print()

    for cat_name, cat_data in inventory["categories"].items():
        print(f"  {cat_name}: {cat_data['count']:,} fields")

    print()
    print("=" * 60)
    print("TOTAL DEVICE/HARDWARE FIELDS: {:,}".format(len(all_fields)))
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate device and hardware metadata field inventory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/device_hardware_inventory"),
        help="Output directory (default: dist/device_hardware_inventory)",
    )
    args = parser.parse_args()

    generate_inventory(args.out_dir)


if __name__ == "__main__":
    main()
