import json
import os
import sys
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "virajsanghavi007")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day, .ContributionCalendar-day"):
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        count_attr = cell.get("data-count")
        if level is None:
            level = 0
        if count_attr is not None:
            count = int(count_attr)
        else:
            tt_id = cell.get("id")
            count = 0
            if tt_id:
                tt = soup.select_one(f"tool-tip[for={tt_id}]")
                if tt and tt.text.strip()[0].isdigit():
                    count = int(tt.text.strip().split()[0])
        days.append({"date": d, "count": count, "level": int(level)})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = sum(d["count"] for d in days)

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            if d["date"] == days[-1]["date"]:
                continue
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"])

    monthly = {}
    for d in days:
        month_key = d["date"][:7]
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    days = fetch_days()
    if not days:
        print("no contribution days parsed, aborting without overwrite", file=sys.stderr)
        sys.exit(1)

    payload = {"days": days, "stats": derive_stats(days)}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"wrote {len(days)} days -> {OUT_PATH}")


if __name__ == "__main__":
    main()
