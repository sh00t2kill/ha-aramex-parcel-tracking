import requests
import json
from datetime import datetime

LABEL_NUMBER = ""

URL = "https://www.aramex.com.au/umbraco/api/TrackingApi/GetTrackingData"

PARAMS = {
    "LabelNo": LABEL_NUMBER,
    "dataFormat": "json",
}

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "referer": f"https://www.aramex.com.au/tools/track?l={LABEL_NUMBER}",
    "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_tracking(label_number: str = LABEL_NUMBER) -> dict:
    params = {**PARAMS, "LabelNo": label_number}
    headers = {**HEADERS, "referer": f"https://www.aramex.com.au/tools/track?l={label_number}"}
    response = requests.get(URL, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


def print_tracking(data: dict) -> None:
    result = data.get("result", {})

    print(f"Label:        {result.get('LabelNumber')}")
    print(f"From:         {result.get('PickupFranchise')} ({result.get('PickupFranchiseCode')})")
    print(f"To:           {result.get('DeliveryFranchise')} ({result.get('DeliveryFranchiseCode')})")
    print(f"ETA:          {result.get('DeliveryETADate')}")

    service = result.get("DeliveryServiceType", {})
    print(f"Service:      {service.get('Description')}")

    hubs = result.get("TransitHubs", {}).get("Hubs", [])
    if hubs:
        print("\nTransit hubs:")
        for hub in hubs:
            print(f"  [{hub.get('status'):10}]  {hub.get('transitName')} ({hub.get('transitRf')})  — {hub.get('type')}")

    scans = result.get("Scans", [])
    if scans:
        print("\nScan history:")
        for scan in scans:
            print(f"  {scan.get('Date')}  {scan.get('Name')} ({scan.get('Franchise')})  — {scan.get('Description')}")

    delay = result.get("ServiceDelay", {})
    if delay.get("IsDelayed"):
        print(f"\nDelay notice: {delay.get('Message')}")

    print(f"\nGenerated in: {data.get('generated_in')}")


if __name__ == "__main__":
    import sys

    label = sys.argv[1] if len(sys.argv) > 1 else LABEL_NUMBER
    data = fetch_tracking(label)
    print_tracking(data)
