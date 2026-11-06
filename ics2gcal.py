from datetime import datetime, timedelta, timezone
import json
import os
import subprocess
import sys
import urllib.parse
import webbrowser
from icalendar import Calendar


def parse_ics_to_google_url(ics_path, account=None):
    with open(ics_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    # 尋找檔案中的第一個 VEVENT (活動)
    events = [comp for comp in cal.walk() if comp.name == "VEVENT"]
    if not events:
        print("檔案中找不到有效的活動內容。")
        return None

    if len(events) > 1:
        print(f"提示：檔案中包含 {len(events)} 個活動，目前僅處理第 1 個活動。")

    event = events[0]

    # 擷取活動欄位內容
    summary = str(event.get("summary", ""))
    description = str(event.get("description", ""))
    location = str(event.get("location", ""))

    # 擷取發起人 (ORGANIZER) 與 參與者 (ATTENDEE)
    organizer_prop = event.get("organizer")
    attendees_prop = event.get("attendee")

    extra_details = []
    attendee_emails = []

    def format_person(person_prop):
        cn = person_prop.params.get("CN", "").strip("'\"") if hasattr(person_prop, "params") else ""
        raw_val = str(person_prop)
        email = raw_val.replace("mailto:", "").replace("MAILTO:", "").strip()
        if cn and cn != email:
            return f"{cn} <{email}>", email
        return email, email

    if organizer_prop:
        org_display, org_email = format_person(organizer_prop)
        extra_details.append(f"【發起人】: {org_display}")

    if attendees_prop:
        if not isinstance(attendees_prop, list):
            attendees_prop = [attendees_prop]
        
        att_displays = []
        for att in attendees_prop:
            att_display, att_email = format_person(att)
            att_displays.append(f"- {att_display}")
            if att_email:
                attendee_emails.append(att_email)
        
        if att_displays:
            extra_details.append("【參與人員】:\n" + "\n".join(att_displays))

    # 擷取其他常見重要欄位 (線上會議連結、狀態、重複規則、優先級、分類等)
    other_fields = []
    
    # 會議/活動連結
    url_val = event.get("url")
    if not url_val:
        # 檢查常見微軟 Teams 會議連結標籤
        url_val = event.get("x-microsoft-skypeteamsmeetingurl")
    if url_val:
        other_fields.append(f"• 會議連結 (URL): {url_val}")

    # 活動狀態 (CONFIRMED / TENTATIVE / CANCELLED)
    status_val = event.get("status")
    if status_val:
        status_map = {"CONFIRMED": "已確認 (CONFIRMED)", "TENTATIVE": "暫定 (TENTATIVE)", "CANCELLED": "已取消 (CANCELLED)"}
        other_fields.append(f"• 活動狀態: {status_map.get(str(status_val).upper(), str(status_val))}")

    # 重複規則 (RRULE)
    rrule_val = event.get("rrule")
    if rrule_val:
        other_fields.append(f"• 重複規則: {rrule_val.to_ical().decode('utf-8', errors='ignore') if hasattr(rrule_val, 'to_ical') else str(rrule_val)}")

    # 分類 / 標籤 (CATEGORIES)
    categories_val = event.get("categories")
    if categories_val:
        cat_text = ", ".join(str(c) for c in categories_val.cats) if hasattr(categories_val, "cats") else str(categories_val)
        other_fields.append(f"• 分類標籤: {cat_text}")

    # 優先程度 (PRIORITY: 1=高, 5=中, 9=低)
    priority_val = event.get("priority")
    if priority_val:
        other_fields.append(f"• 優先等級: {priority_val}")

    # 機密程度 (CLASS: PUBLIC / PRIVATE / CONFIDENTIAL)
    class_val = event.get("class")
    if class_val:
        other_fields.append(f"• 機密等級: {class_val}")

    # 忙碌狀態 (TRANSP: OPAQUE=忙碌, TRANSPARENT=空閒)
    transp_val = event.get("transp")
    if transp_val:
        other_fields.append(f"• 日曆狀態: {'忙碌' if str(transp_val).upper() == 'OPAQUE' else '空閒'}")

    # 附件連結 (ATTACH)
    attach_val = event.get("attach")
    if attach_val:
        if not isinstance(attach_val, list):
            attach_val = [attach_val]
        attach_links = [str(a) for a in attach_val]
        other_fields.append("• 附件連結:\n  " + "\n  ".join(attach_links))

    if other_fields:
        extra_details.append("【其他活動資訊】:\n" + "\n".join(other_fields))

    # 將所有解析到的資訊整合到內文
    full_description_parts = []
    if extra_details:
        full_description_parts.append("\n\n".join(extra_details))
    if description.strip():
        full_description_parts.append("【活動說明】:\n" + description.strip())
    
    full_description = "\n\n----------------------------------------\n\n".join(full_description_parts)

    dtstart_prop = event.get("dtstart")
    if not dtstart_prop:
        print("活動缺少開始時間 (DTSTART)。")
        return None
    dtstart = dtstart_prop.dt

    dtend_prop = event.get("dtend")
    duration_prop = event.get("duration")
    if dtend_prop:
        dtend = dtend_prop.dt
    elif duration_prop:
        dtend = dtstart + duration_prop.dt
    else:
        # 若無結束時間與持續時間，全天活動預設加 1 天，一般活動則與開始時間相同
        dtend = (
            dtstart
            if isinstance(dtstart, datetime)
            else dtstart + timedelta(days=1)
        )

    # 格式化時間為 Google Calendar URL 所需格式 (YYYYMMDDTHHMMSSZ 或 YYYYMMDDTHHMMSS)
    def format_time(dt):
        if isinstance(dt, datetime):
            # 若帶有時區，轉為 UTC 時間格式並加上 Z
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
                return dt.strftime("%Y%m%dT%H%M%SZ")
            # 若無時區資訊 (Floating time)，不加 Z 以使用使用者當地日曆時區
            return dt.strftime("%Y%m%dT%H%M%S")
        else:
            # 若為全天活動 (date 物件)
            return dt.strftime("%Y%m%d")

    start_str = format_time(dtstart)
    end_str = format_time(dtend)
    dates_str = f"{start_str}/{end_str}"

    # 組裝 Google 日曆網址參數
    params = {
        "action": "TEMPLATE",
        "text": summary,
        "dates": dates_str,
        "details": full_description,
        "location": location,
    }

    # 若有抓到參與者 Email，透過 add 參數自動填入邀請對象欄位
    if attendee_emails:
        params["add"] = ",".join(attendee_emails)

    # 若有指定帳號 (Email 或 authuser 索引)，帶入 authuser 參數
    if account:
        params["authuser"] = account

    base_url = "https://calendar.google.com/calendar/render"
    google_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return google_url


def find_chrome_profile_directory(account):
    """根據使用者輸入的 Email、使用者名稱或 Profile 資料夾名稱找出 Chrome Profile Directory"""
    if not account:
        return None

    # 如果直接傳入 Profile 1、Default 等目錄名
    local_state_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State")
    if os.path.exists(local_state_path):
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            info_cache = data.get("profile", {}).get("info_cache", {})
            
            # 1. 優先精準比對目錄名稱 (如 'Profile 1', 'Default')
            if account in info_cache:
                return account

            # 2. 比對 Email (user_name) 或 Profile 顯示名稱 (name)
            for folder, info in info_cache.items():
                user_name = info.get("user_name", "")
                name = info.get("name", "")
                if account.lower() == user_name.lower() or account.lower() == name.lower():
                    return folder

            # 3. 模糊比對 Email 前綴
            for folder, info in info_cache.items():
                user_name = info.get("user_name", "")
                if account.lower() in user_name.lower():
                    return folder
        except Exception:
            pass

    return None


def open_in_chrome(url, account=None):
    # 嘗試呼叫 Chrome 開啟；若找不到路徑則使用預設瀏覽器開啟
    chrome_path = None

    # 常見 Chrome 安裝路徑檢查 (Windows / macOS)
    possible_paths = [
        # Windows 64-bit / 32-bit
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        # macOS
        r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            chrome_path = path
            break

    profile_dir = find_chrome_profile_directory(account) if account else None

    if chrome_path:
        # 如果指定了 Chrome 帳號/設定檔，使用命令列參數精準啟動對應 Profile
        if profile_dir:
            cmd = [chrome_path, f"--profile-directory={profile_dir}", url]
            subprocess.Popen(cmd)
        else:
            # 指定使用 Chrome 開啟網址
            webbrowser.register(
                "chrome", None, webbrowser.BackgroundBrowser(chrome_path)
            )
            webbrowser.get("chrome").open(url)
    else:
        print("未偵測到預設路徑的 Chrome，改用系統預設瀏覽器開啟...")
        webbrowser.open(url)


def print_usage():
    usage_text = """ics2gcal - iCalendar (.ics) 轉 Google 日曆小工具

【使用說明】
將 .ics 檔案解析並自動以 Google Chrome 開啟新增至 Google 日曆。

【指令格式】
ics2gcal.exe [ics檔案路徑] [Google帳號/Profile]

【參數說明】
1. ics檔案路徑: 必填，.ics 活動檔案路徑
2. Google帳號/Profile: 選填，可填入：
   • Google 信箱：如 darrent.chen@gmail.com
   • Chrome 設定檔名稱：如 "Darrent.Chen"
   • 若未提供，則使用最近開啟的 Chrome 視窗

【使用範例】
1. 使用預設帳號開啟：
   ics2gcal.exe "D:\\work\\invite.ics"

2. 指定特定 Google 帳號開啟：
   ics2gcal.exe "D:\\work\\invite.ics" "darrent.chen@gmail.com"
   ics2gcal.exe "D:\\work\\invite.ics" "tentel@tentel.com.tw"

【檔案關聯建議】
在 .ics 檔案按右鍵 >「開啟檔案」>「選擇其他應用程式」，
勾選「永遠以此應用程式開啟」，並指向 ics2gcal.exe，
日後只要雙擊任何 .ics 檔案即會自動於 Google 日曆開啟！"""
    clean_text = usage_text.strip()
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, clean_text, "ics2gcal 使用說明", 0x40 | 0x0)
    except Exception:
        print(clean_text)


if __name__ == "__main__":
    file_path = None
    account = None

    # 解析命令列參數:
    # 支援格式:
    #   python ics2gcal.py "file.ics"
    #   python ics2gcal.py "file.ics" "darrent.chen@gmail.com"
    #   python ics2gcal.py "file.ics" --account="darrent.chen@gmail.com"
    args = sys.argv[1:]
    for arg in args:
        if arg.startswith("--account="):
            account = arg.split("=", 1)[1].strip("'\"")
        elif os.path.isfile(arg) and not file_path:
            file_path = arg
        elif not account and not os.path.isfile(arg):
            account = arg.strip("'\"")

    # 如果沒有提供 .ics 檔案，顯示使用說明並結束
    if not file_path:
        print_usage()
        sys.exit(0)

    print(f"正在讀取檔案：{file_path}")
    if account:
        print(f"指定開啟帳號：{account}")
    google_calendar_url = parse_ics_to_google_url(file_path, account=account)

    if google_calendar_url:
        print("解析成功，準備以 Chrome 開啟 Google 日曆...")
        open_in_chrome(google_calendar_url, account=account)