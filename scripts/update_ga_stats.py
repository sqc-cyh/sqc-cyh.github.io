#!/usr/bin/env python3
"""Generate the public GA4 page-view summary used by the static homepage."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2 import service_account


def page_views(client: BetaAnalyticsDataClient, property_name: str, start_date: str) -> int:
    response = client.run_report(
        RunReportRequest(
            property=property_name,
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
            metrics=[Metric(name="screenPageViews")],
        )
    )
    if not response.rows:
        return 0
    return int(response.rows[0].metric_values[0].value)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: update_ga_stats.py OUTPUT_PATH")

    raw_credentials = os.environ.get("GA4_SERVICE_ACCOUNT_JSON")
    property_id = os.environ.get("GA4_PROPERTY_ID")
    if not raw_credentials or not property_id:
        raise SystemExit("GA4_SERVICE_ACCOUNT_JSON and GA4_PROPERTY_ID are required")

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(raw_credentials),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=credentials)
    property_name = f"properties/{property_id}"
    stats = {
        "today": page_views(client, property_name, "today"),
        "total": page_views(client, property_name, "2000-01-01"),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }

    output_path = Path(sys.argv[1])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stats, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
