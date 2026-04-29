# Aramex Parcel Tracking

A Home Assistant custom integration for tracking Aramex (Australia) parcels.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

## Features

- Track one or more Aramex parcels simultaneously
- Sensors for service type, pickup location, delivery location, ETA, and scan history
- Most recent scan exposed as sensor state; full scan history available as attributes
- Polls every 15 minutes automatically

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant instance
2. Go to **Integrations**
3. Click the three-dot menu → **Custom repositories**
4. Add `https://github.com/sh00t2kill/ha-aramex-parcel-tracking` with category **Integration**
5. Search for **Aramex** and click **Download**
6. Restart Home Assistant

### Manual

1. Copy the `custom_components/aramex/` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** and search for **Aramex**
3. Enter your parcel label number (e.g. `MP0085494934`)
4. Click **Submit**

Repeat for each parcel you want to track.

## Sensors

Each configured label number creates the following sensors:

| Sensor | State | Attributes |
|---|---|---|
| `sensor.aramex_{label}_service` | Delivery service description | — |
| `sensor.aramex_{label}_pickup` | Pickup city | `franchise_code` |
| `sensor.aramex_{label}_delivery` | Delivery city | `franchise_code` |
| `sensor.aramex_{label}_eta` | Estimated delivery date | `transit_days`, `is_delayed`, `delay_message` |
| `sensor.aramex_{label}_scans` | Most recent scan description | `last_scan_date`, `scans` (full history) |

## Example Automation

```yaml
automation:
  - alias: "Notify when parcel is out for delivery"
    trigger:
      - platform: state
        entity_id: sensor.aramex_mp0085494934_scans
        to: "On board with courier for delivery"
    action:
      - service: notify.mobile_app
        data:
          message: "Your Aramex parcel is out for delivery today!"
```
