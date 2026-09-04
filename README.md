# FOMO Family Auto-Follow Bot

[English](README.md) | [Bahasa Indonesia](README.id.md)

A Python script to automate following accounts on [fomo.family](https://fomo.family), with features for scraping followers from multiple targets, skipping already-followed accounts, delaying between requests, and reporting followers/following stats before & after running.

> ⚠️ **Disclaimer:** This script interacts with fomo.family's internal API using your personal account token/cookie. Using automation like this may violate the platform's Terms of Service and could result in rate-limiting or account suspension. Use at your own risk, ideally with reasonable volume (not mass-following thousands of accounts at once). **DYOR (Do Your Own Research)** — you are fully responsible for how you use this script; the author takes no responsibility for any consequences.

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

## Getting the Code

Clone this repository:

```bash
git clone https://github.com/heluvaa/FOMO-Family-Auto-Follow-Bot.git
cd FOMO-Family-Auto-Follow-Bot
```

Don't have Git installed? Download it here: [git-scm.com/downloads](https://git-scm.com/downloads)

Alternatively, click the green **Code** button on the [repo page](https://github.com/heluvaa/FOMO-Family-Auto-Follow-Bot) → **Download ZIP**, then extract it.

## File Structure

```
.
├── main.py   # Main script
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
python3 main.py
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

## Platform-Specific Setup

### 📱 Android (Termux)

1. Install [Termux](https://termux.dev/) from F-Droid (recommended) or the Play Store.
2. Open Termux and update packages:
   ```bash
   pkg update && pkg upgrade -y
   ```
3. Install Python and Git:
   ```bash
   pkg install python git -y
   ```
4. Clone the repo (or transfer the files manually into Termux's home folder):
   ```bash
   git clone https://github.com/heluvaa/FOMO-Family-Auto-Follow-Bot.git
   cd FOMO-Family-Auto-Follow-Bot
   ```
5. Install the dependency:
   ```bash
   pip install curl_cffi
   ```
6. Create your `config.json` (copy from `config.example.json` and fill in your values):
   ```bash
   cp config.example.json config.json
   nano config.json
   ```
   (Edit the file, then press `Ctrl + O`, `Enter`, `Ctrl + X` to save and exit nano)
7. Run the bot:
   ```bash
   python main.py
   ```

> Tip: Termux may close background processes when the app isn't in focus. Enable "Acquire wakelock" in the Termux notification, or disable battery optimization for Termux in your phone's app settings, to prevent the script from being killed mid-run.

### 🪟 Windows

1. Download and install [Python](https://www.python.org/downloads/) (check **"Add Python to PATH"** during installation).
2. Download and install [Git for Windows](https://git-scm.com/downloads) (optional, only needed if cloning via command line).
3. Open **Command Prompt** or **PowerShell**.
4. Clone the repository:
   ```powershell
   git clone https://github.com/heluvaa/FOMO-Family-Auto-Follow-Bot.git
   cd FOMO-Family-Auto-Follow-Bot
   ```
   (Or skip Git entirely: click the green **Code** button on the [repo page](https://github.com/heluvaa/FOMO-Family-Auto-Follow-Bot) → **Download ZIP** → extract it → open Command Prompt in that folder)
5. Install the dependency:
   ```powershell
   pip install curl_cffi
   ```
6. Create your `config.json` by copying `config.example.json` and filling in your values (you can edit it with Notepad).
7. Run the bot:
   ```powershell
   python main.py
   ```

> If `python` isn't recognized, try `py` instead (`py main.py`), or reinstall Python with "Add to PATH" checked.

### 🖥️ VPS / Linux Server

1. Connect via SSH to your VPS.
2. Install Python and pip if not already available:
   ```bash
   sudo apt update && sudo apt install python3 python3-pip git -y
   ```
3. Clone the repo:
   ```bash
   git clone https://github.com/heluvaa/FOMO-Family-Auto-Follow-Bot.git
   cd FOMO-Family-Auto-Follow-Bot
   ```
4. Install the dependency:
   ```bash
   pip3 install curl_cffi
   ```
5. Create your `config.json`:
   ```bash
   cp config.example.json config.json
   nano config.json
   ```
6. Run the bot directly:
   ```bash
   python3 main.py
   ```
7. To keep it running after you disconnect SSH (optional), use `screen` or `tmux`:
   ```bash
   sudo apt install screen -y
   screen -S autofollow
   python3 main.py
   # Press Ctrl+A then D to detach; reattach later with: screen -r autofollow
   ```

## Troubleshooting

- **`[ERROR] File 'config.json' tidak ditemukan`** → make sure `config.json` is in the same folder where you run the script.
- **401 / 403 status on requests** → your token/cookie has expired; log in again and grab a fresh token.
- **`Tidak ada target baru untuk difollow`** → all followers from the scraped targets are already followed by you.

## Support / Donate

If this project helps you, consider supporting its development. Any amount is greatly appreciated 🙏

- **Bitcoin:** `13YVRErt7gqG2vVqPSg6ZbXibc4EhuqYZn`
- **EVM Address:** `0x13972547B1c875fC46700364B5A985F39Ce4E46b`
- **Solana:** `GNJGHfr1VygCKmLRxTmrgNXEQm77G1wzyCDjHqFkdHM9`
- **TRX:** `TPW9tZ1Q44nDrCrkuwR2XaGiPohvx41KEC`
- **Sociabuzz:** https://sociabuzz.com/xzvxco/tribe
- **FOMO Family:** [@kobo_kanaeru](https://fomo.family)

Thank you, whatever you can give truly means a lot!

## License

Use and modify freely for personal purposes. Not affiliated with fomo.family.
