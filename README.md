# FOMO Family Auto-Follow Bot

[English](README.md) | [Bahasa Indonesia](README.id.md)

A Python script to automate following accounts on [fomo.family](https://fomo.family), with features for scraping followers from multiple targets, skipping already-followed accounts, delaying between requests, and reporting followers/following stats before & after running.

> ⚠️ **Disclaimer:** This script interacts with fomo.family's internal API using your personal account token/cookie. Using automation like this may violate the platform's Terms of Service and could result in rate-limiting or account suspension. Use at your own risk, ideally with reasonable volume (not mass-following thousands of accounts at once).

## Features

- ✅ Scrape followers from multiple targets at once (`targets_to_scrape` can hold many IDs)
- ✅ Automatically skip accounts you already follow
- ✅ Skip duplicates across targets (a follower won't be followed twice)
- ✅ Randomized delay between follows (configurable, default 0.8–2.0 seconds)
- ✅ Load token & cookie from a config file instead of manual input each run
- ✅ Followers & following report (before vs. after)
- ✅ Colored terminal output for easier reading

## Requirements

- Python 3.8+
- `curl_cffi` library

Install the dependency:

```bash
pip install curl_cffi
```

## File Structure

```
.
├── bot_autofollow.py   # Main script
├── config.json          # Configuration (token, cookie, targets, etc.)
└── README.md
```

## Configuration (`config.json`)

Create a `config.json` file in the same folder as the script, formatted like this:

```json
{
  "auth_token": "Bearer xxxxxxxxxxxxxxxx",
  "cookie": "your_full_cookie_string",
  "my_user_id": "your-account-uuid",
  "my_user_handle": "your_username",
  "targets_to_scrape": [
    "target-id-1",
    "target-id-2"
  ],
  "limit_per_target": 50,
  "delay_min_seconds": 0.8,
  "delay_max_seconds": 2.0
}
```

### How to get each value

| Field | How to obtain it |
|---|---|
| `auth_token` | Open fomo.family in your browser → log in → open DevTools (F12) → **Network** tab → find any request to `prod-api.fomo.family` → look at the `authorization` header → copy its value (including `Bearer `) |
| `cookie` | In the same request, copy the value of the `cookie` header |
| `my_user_id` | Found in your profile API response, under the `id` field |
| `my_user_handle` | Your fomo.family username (the one shown in your profile URL) |
| `targets_to_scrape` | User IDs (not usernames) of the accounts whose followers you want to scrape. Can be obtained from the leaderboard or user profile API response |

⚠️ **Do not commit `config.json` to GitHub** — this file contains your personal token/cookie. Add it to `.gitignore`:

```
config.json
```

Use `config.example.json` (with no real values) as a template if you plan to share the repo publicly.

## How to Run

```bash
python3 bot_autofollow.py
```

What happens step by step:

1. The script reads `config.json` and validates required fields.
2. It fetches and displays your account stats (followers & following) **before** the run.
3. It fetches the list of accounts you already follow (used for skipping).
4. It scrapes followers from every ID in `targets_to_scrape`, merges them into a unique list, and removes anyone already followed or duplicated.
5. It follows each candidate one by one with a randomized delay in between, printing success/failure status for each account.
6. It fetches your account stats again **after** the run and shows the difference.

## Additional Configuration

| Field | Default | Description |
|---|---|---|
| `limit_per_target` | 50 | Total cap on unique accounts to follow in one run (not per target) |
| `delay_min_seconds` | 0.8 | Minimum delay between follows (seconds) |
| `delay_max_seconds` | 2.0 | Maximum delay between follows (seconds) |

## Troubleshooting

- **`[ERROR] File 'config.json' tidak ditemukan`** → make sure `config.json` is in the same folder where you run the script.
- **401 / 403 status on requests** → your token/cookie has expired; log in again and grab a fresh token.
- **`Tidak ada target baru untuk difollow`** → all followers from the scraped targets are already followed by you.

## License

Use and modify freely for personal purposes. Not affiliated with fomo.family.
