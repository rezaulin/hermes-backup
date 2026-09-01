# Windows Mobile USB Driver Sources

Verified 2026-08-23 via GitHub API (stars/licenses/push dates) and HTTP status checks on vendor URLs. Re-verify before shipping — repos go stale and vendor URLs move.

## ADB / Fastboot (all Android brands)
| Source | Stars | License | Last push | Notes |
|---|---|---|---|---|
| koush/UniversalAdbDriver | 2317 | Apache-2.0 (LICENSE file in repo) | 2021-07 | Ships signed usb_driver/ + installer; adb.clockworkmod.com live. **Best bundle candidate.** |
| fawazahmed0/Latest-adb-fastboot-installer-for-windows | 833 | Unlicense | 2023-09 | Batch installer that always pulls latest official Google driver — good pattern reference for dynamic download. |
| Google USB Driver (official) | — | — | — | developer.android.com/studio/run/win-usb (200 OK). Signed by Google; canonical source. |

## Qualcomm EDL 9008 (QDLoader 9008 / QHSUSB_BULK)
| Source | Stars | License | Last push | Notes |
|---|---|---|---|---|
| bkerler/edl | 2542 | GPL-3.0 | 2026-08 | Most credible EDL source. `Drivers/Windows/` contains `zadig-2.8.exe`, `libusb-1.0.26-binaries.7z`, `Install_Windows.bat`; also `install_edl_win10_win11.ps1`. |
| hybacmb/O1R-Driverlnstaller-Tools | 2 | none | 2026-02 | OPPO/OnePlus/Realme one-click 9008 driver tool — too small/unlicensed to trust as source. |

Key fact: EDL mode is best handled by **Zadig installing WinUSB/libusb** on the 9008 device, not by any OEM INF. That makes libusb/Zadig (LGPL/GPL, redistributable) the legal and practical path — no Qualcomm OEM driver needed.

## MediaTek preloader / BROM / VCOM
| Source | Stars | License | Last push | Notes |
|---|---|---|---|---|
| bkerler/mtkclient | 1068 | GPL-3.0 | 2026-08 | README-WINDOWS.md recipe: stock Windows COM driver + **UsbDk** (daynix/UsbDk, github releases), test with `UsbDkController -n` looking for VID 0x0E8D PID 0x0003. |

Avoid: random "MTK VCOM driver" repacks — mostly self-signed/unsigned with no license.

## Apple (iPhone/iPad)
| Source | Stars | License | Last push | Notes |
|---|---|---|---|---|
| NelloKudo/Apple-Mobile-Drivers-Installer | 488 | GPL-3.0 | 2025-04 | PowerShell script pulling Apple drivers from **Microsoft Update Catalog** + AppleMobileDeviceSupport64.msi from iTunes. The legal pattern — Apple binaries are never redistributed. |
| libimobiledevice/* + doronz88/pymobiledevice3 (2655*, GPL-3.0) | — | — | 2026 | Protocol libraries for talking to iOS without iTunes; complements the driver story. |

Known catalog .cab URLs (from NelloKudo README, may rotate):
- Apple USB: `https://catalog.s.download.windowsupdate.com/d/msdownload/update/driver/drvs/2020/11/01d96dfd-2f6f-46f7-8bc3-fd82088996d2_a31ff7000e504855b3fa124bf27b3fe5bc4d0893.cab`
- Apple tether (netaapl): `https://catalog.s.download.windowsupdate.com/c/msdownload/update/driver/drvs/2017/11/netaapl_7503681835e08ce761c52858949731761e1fa5a1.cab`

## Samsung Download mode
Official: `https://developer.samsung.com/mobile/android-usb-driver.html` (200 OK). GitHub mirrors exist (e.g. T11x-TWRP/samsung_usb_driver_windows) but link to official instead.

## Huawei
HiSuite: `https://consumer.huawei.com/en/support/hisuite/` (200 OK) — bundles its own drivers.

## Generic driver-installer infrastructure
| Source | Stars | License | Notes |
|---|---|---|---|
| pbatard/libwdi | 2321 | GPL-3.0 | Windows driver installer library for USB devices — embed instead of shelling out to Zadig if you need programmatic control. |
| daynix/UsbDk | — | open source | github.com/daynix/UsbDk/releases — the MTK path. |

## Verified URL status (2026-08-23)
200: dl.google.com/android/repository/platform-tools-latest-windows.zip • adb.clockworkmod.com • zadig.akeo.ie • libusb.info • developer.android.com/studio/run/win-usb • developer.android.com/studio/run/oem-usb • developer.samsung.com/mobile/android-usb-driver.html • support.apple.com/en-us/HT210384 • consumer.huawei.com/en/support/hisuite/ • github.com/daynix/UsbDk/releases • catalog.update.microsoft.com search page
403: usbdrivers.net • 000: xiaomi.com (geo-blocked from this host)

## Negative findings (GitHub search noise)
No credible standalone Samsung/Xiaomi/Oppo/Vivo/Realme driver pack repos surfaced — searches returned unrelated noise. Conclusion: for those brands, ADB/Fastboot via UniversalAdbDriver + Zadig/UsbDk for EDL/VCOM covers repair needs without any vendor-specific driver. Don't bundle vendor repacks.

## Research workflow that worked
1. `curl -s "https://api.github.com/search/repositories?q=<terms>&sort=stars&order=desc&per_page=N" -o file.json` — **never pipe into python3 directly** (security scanner blocks `curl | interpreter`; save to file, parse separately).
2. Parse with a small standalone script: print full_name, stars, license SPDX, pushed_at, description.
3. For shortlist: fetch `/contents/` to confirm actual driver files exist; fetch raw READMEs via raw.githubusercontent.com.
4. Verify vendor URLs with `curl -o /dev/null -w "%{http_code}" -L`.
