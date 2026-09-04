import os
import json
import time
import random
import datetime
from curl_cffi import requests

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
BOLD = '\033[1m'
RESET = '\033[0m'

CONFIG_PATH = "config.json"


# ------------------------- KONFIGURASI -------------------------

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"{RED}[ERROR] File '{CONFIG_PATH}' tidak ditemukan. "
              f"Buat file itu dulu (lihat config.json contoh).{RESET}")
        raise SystemExit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = ["auth_token", "cookie", "my_user_id", "my_user_handle", "targets_to_scrape"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        print(f"{RED}[ERROR] Field wajib kosong/hilang di config.json: {missing}{RESET}")
        raise SystemExit(1)

    cfg.setdefault("limit_per_target", 50)
    cfg.setdefault("delay_min_seconds", 0.8)
    cfg.setdefault("delay_max_seconds", 2.0)
    return cfg


def build_headers(cfg):
    auth = cfg["auth_token"].strip()
    return {
        "accept": "*/*",
        "accept-language": "id-ID",
        "authorization": auth if auth.startswith("Bearer") else f"Bearer {auth}",
        "cookie": cfg["cookie"].strip(),
        "origin": "https://fomo.family",
        "referer": "https://fomo.family/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "x-supported-chains": "1,56,143,4663,8453,1399811149",
        "content-type": "application/json",
    }


# ------------------------- HELPER PARSING -------------------------

def extract_user_list(json_data):
    """Cari list user (followers/following) di dalam struktur JSON yang bisa nested."""
    if isinstance(json_data, dict):
        for value in json_data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict) and "displayName" in value[0]:
                return value
            if isinstance(value, dict):
                found = extract_user_list(value)
                if found:
                    return found
    return []


def extract_number_field(json_data, keywords):
    """Cari angka pertama di JSON yang key-nya mengandung salah satu keyword (mis. 'follower')."""
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            key_lower = key.lower()
            is_number = isinstance(value, (int, float)) and not isinstance(value, bool)
            if is_number and any(k in key_lower for k in keywords):
                return value
            if isinstance(value, (dict, list)):
                found = extract_number_field(value, keywords)
                if found is not None:
                    return found
    elif isinstance(json_data, list):
        for item in json_data:
            found = extract_number_field(item, keywords)
            if found is not None:
                return found
    return None


def extract_text_field(json_data, keywords):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            key_lower = key.lower()
            if isinstance(value, str) and any(k in key_lower for k in keywords):
                return value
            if isinstance(value, (dict, list)):
                found = extract_text_field(value, keywords)
                if found:
                    return found
    elif isinstance(json_data, list):
        for item in json_data:
            found = extract_text_field(item, keywords)
            if found:
                return found
    return None


# ------------------------- API CALLS -------------------------

def get_my_profile(headers, my_user_handle):
    """Ambil data profil sendiri (lewat userHandle): username, followers, dan following saat ini."""
    url = f"https://prod-api.fomo.family/v2/users/userHandle/{my_user_handle}"
    try:
        response = requests.get(url, headers=headers, impersonate="chrome120")
        if response.status_code == 200:
            data = response.json()
            username = extract_text_field(data, ["userhandle", "handle", "username", "displayname"]) or my_user_handle
            follower_count = extract_number_field(data, ["follower"])
            following_count = extract_number_field(data, ["following"])
            return username, follower_count, following_count
        else:
            print(f"{RED}[ERROR] Gagal ambil profil sendiri. Status: {response.status_code}{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR] Kesalahan saat ambil profil sendiri: {e}{RESET}")
    return my_user_handle, None, None


def get_my_following_ids(headers, my_user_id):
    """Ambil daftar ID user yang SUDAH saya follow, untuk keperluan skip."""
    url = f"https://prod-api.fomo.family/v2/users/{my_user_id}/following"
    following_ids = set()
    try:
        response = requests.get(url, headers=headers, impersonate="chrome120")
        if response.status_code == 200:
            data = response.json()
            users = extract_user_list(data)
            for u in users:
                if u.get("id"):
                    following_ids.add(u["id"])
        else:
            print(f"{YELLOW}[WARN] Tidak bisa ambil daftar following (Status: {response.status_code}). "
                  f"Skip-duplikat mungkin tidak akurat.{RESET}")
    except Exception as e:
        print(f"{YELLOW}[WARN] Gagal ambil daftar following: {e}{RESET}")
    return following_ids


def get_followers(headers, target_id):
    url = f"https://prod-api.fomo.family/v2/users/{target_id}/followers"
    try:
        response = requests.get(url, headers=headers, impersonate="chrome120")
        if response.status_code == 200:
            data = response.json()
            followers_list = extract_user_list(data)
            results = []
            for user in followers_list:
                if user.get("id"):
                    results.append({
                        "id": user.get("id"),
                        "name": user.get("displayName", "Unknown"),
                        "handle": user.get("userHandle", "Unknown"),
                    })
            return results
        else:
            print(f"{RED}[ERROR] Gagal tarik followers dari {target_id}. Status: {response.status_code}{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR] Kesalahan sistem saat scrape {target_id}: {e}{RESET}")
    return []


def follow_user(target, headers, my_user_id, current_idx, total_targets):
    url = "https://prod-api.fomo.family/follows"
    payload = {"user_id": my_user_id, "following_id": target["id"]}

    time_str = datetime.datetime.now().strftime("[%H:%M:%S]")

    try:
        response = requests.post(url, headers=headers, json=payload, impersonate="chrome120")
        if response.status_code in (200, 201):
            print(f"{GREEN}{time_str} {MAGENTA}[{current_idx}/{total_targets}]{GREEN} "
                  f"SUCCESS - Follow: {BOLD}{target['name']}{RESET}{GREEN} @{target['handle']}{RESET}")
            return True
        else:
            print(f"{RED}{time_str} {MAGENTA}[{current_idx}/{total_targets}]{RED} "
                  f"FAILED - Follow: {BOLD}{target['name']}{RESET}{RED} @{target['handle']} | Status: {response.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}{time_str} {MAGENTA}[{current_idx}/{total_targets}]{RED} "
              f"ERROR - Follow: {BOLD}{target['name']}{RESET}{RED} @{target['handle']} | Sistem: {e}{RESET}")
        return False


# ------------------------- MAIN -------------------------

def main():
    print(f"{BOLD}{MAGENTA}=== BOT AUTO-FOLLOW FOMO FAMILY (v2) ==={RESET}\n")

    cfg = load_config()
    headers = build_headers(cfg)
    my_user_id = cfg["my_user_id"]
    limit_per_target = cfg["limit_per_target"]
    delay_min = cfg["delay_min_seconds"]
    delay_max = cfg["delay_max_seconds"]

    my_user_handle = cfg["my_user_handle"]

    # --- Statistik akun SEBELUM ---
    print(f"{CYAN}Mengambil data akun sebelum bot dijalankan...{RESET}")
    username, followers_before, following_before = get_my_profile(headers, my_user_handle)
    print(f"{BLUE}Username     :{RESET} {BOLD}@{username}{RESET}")
    print(f"{BLUE}Followers    :{RESET} {followers_before if followers_before is not None else 'Tidak diketahui'}")
    print(f"{BLUE}Following    :{RESET} {following_before if following_before is not None else 'Tidak diketahui'}\n")

    # --- Ambil daftar following untuk skip duplikat ---
    print(f"{CYAN}Mengambil daftar user yang sudah kamu follow (untuk skip)...{RESET}")
    already_following = get_my_following_ids(headers, my_user_id)
    print(f"{BLUE}Sudah follow {BOLD}{len(already_following)}{RESET}{BLUE} akun sebelumnya.{RESET}\n")

    # --- Scrape multi-target ---
    all_targets = {}
    for target_id in cfg["targets_to_scrape"]:
        print(f"{CYAN}Scraping followers dari target: {target_id} ...{RESET}")
        followers = get_followers(headers, target_id)
        new_count = 0
        for user in followers:
            if user["id"] == my_user_id:
                continue  # jangan follow diri sendiri
            if user["id"] in already_following:
                continue  # skip yang sudah difollow
            if user["id"] not in all_targets:
                all_targets[user["id"]] = user
                new_count += 1
        print(f"  {MAGENTA}->{RESET} {len(followers)} followers ditemukan, {BOLD}{new_count}{RESET} baru (belum difollow & belum di antrian).")

    candidates = list(all_targets.values())[:limit_per_target]
    total_targets = len(candidates)

    if total_targets == 0:
        print(f"\n{YELLOW}Tidak ada target baru untuk difollow (semua sudah difollow atau kosong).{RESET}")
        return

    print(f"\n{BOLD}Total target unik yang akan difollow: {len(candidates)}{RESET}")
    print(f"{MAGENTA}{'-' * 65}{RESET}")

    success_count = 0
    for idx, target in enumerate(candidates, start=1):
        ok = follow_user(target, headers, my_user_id, idx, total_targets)
        if ok:
            success_count += 1
        if idx < total_targets:
            time.sleep(random.uniform(delay_min, delay_max))

    print(f"{MAGENTA}{'-' * 65}{RESET}")
    print(f"{BOLD}{GREEN}Proses selesai. Berhasil follow {success_count}/{total_targets}.{RESET}\n")

    # --- Statistik akun SESUDAH ---
    print(f"{CYAN}Mengambil data akun setelah bot dijalankan...{RESET}")
    _, followers_after, following_after = get_my_profile(headers, my_user_handle)
    print(f"{BLUE}Username     :{RESET} {BOLD}@{username}{RESET}")
    print(f"{BLUE}Followers sebelum :{RESET} {followers_before if followers_before is not None else '-'}")
    print(f"{BLUE}Followers sesudah :{RESET} {followers_after if followers_after is not None else '-'}")
    if followers_before is not None and followers_after is not None:
        selisih_followers = followers_after - followers_before
        warna = GREEN if selisih_followers >= 0 else RED
        print(f"{BLUE}Selisih followers :{RESET} {warna}{'+' if selisih_followers >= 0 else ''}{selisih_followers}{RESET}")
    print()
    print(f"{BLUE}Following sebelum :{RESET} {following_before if following_before is not None else '-'}")
    print(f"{BLUE}Following sesudah :{RESET} {following_after if following_after is not None else '-'}")
    if following_before is not None and following_after is not None:
        selisih_following = following_after - following_before
        warna = GREEN if selisih_following >= 0 else RED
        print(f"{BLUE}Selisih following :{RESET} {warna}{'+' if selisih_following >= 0 else ''}{selisih_following}{RESET}")


if __name__ == "__main__":
    main()
