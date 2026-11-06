# ics2gcal

> **iCalendar (`.ics`) 轉 Google 日曆小工具**  
> 一鍵解析會議邀請或活動檔案 (`.ics`)，自動於 Google Chrome 開啟並填入 Google 日曆，支援多 Google 帳號與 Windows 檔案關聯！

---

## ✨ 功能特色

- ⚡ **一鍵開啟**：雙擊任何 `.ics` 檔案，自動啟動 Chrome 並填妥 Google 日曆新增活動頁面。
- 👥 **完整資訊解析**：
  - 活動標題、開始與結束時間（支援跨時區轉換及全天活動）
  - 地點與線上會議連結（Teams、Zoom、Webex 等）
  - 自動整理**【發起人】**與**【參與人員】**名單至活動內文，並自動帶入 Google 日曆邀請對象
  - 完整保留活動狀態、重複規則 (RRULE)、分類、機密等級與原信件詳細內容
- 🔄 **多 Google 帳號支援**：
  - 支援傳入參數指定 Google 帳號 / Chrome Profile，多身分切換不打架。
  - 若未指定，自動使用最近開啟的 Chrome 視窗。
- 🖥️ **Windows 原生支援**：
  - 提供已編譯的 `.exe` 獨立執行檔，無黑底主控台閃爍，不需要安裝 Python 即可直接使用。
  - 支援 Windows 右鍵「以此外掛開啟」設定永遠關聯。

---

## 🚀 快速開始

### 方法一：直接下載已編譯的 `.exe`（推薦）

1. 至本專案的 [Releases](../../releases) 下載最新的 `ics2gcal.exe`。
2. 將 `ics2gcal.exe` 放置於常用目錄（如 `C:\Program Files\ics2gcal\`）。
3. **設定預設開啟程式**：
   - 在任何一個 `.ics` 檔案上按**滑鼠右鍵** ➜ **「開啟檔案」** ➜ **「選擇其他應用程式」**。
   - 勾選 **「永遠以此應用程式開啟 .ics 檔案」**。
   - 點選 **「瀏覽此電腦上的應用程式」**，選取 `ics2gcal.exe`。
4. 之後只要雙擊任何 `.ics` 會議通知，就會自動在 Google 日曆打開！

---

### 方法二：使用 Python 執行原始碼

#### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

#### 2. 指令格式與範例

```bash
# 基本用法：使用預設帳號開啟
python ics2gcal.py "meeting.ics"

# 指定 Google 帳號開啟
python ics2gcal.py "meeting.ics" "your_email@gmail.com"
```

---

## 🛠️ 自行打包為 `.exe`

若要自行打包為單一執行檔：

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=calendar.ico --name=ics2gcal ics2gcal.py
```

打包完成後的執行檔會產生於 `dist/ics2gcal.exe`。

---

## 📄 授權條款

本專案採用 [MIT License](LICENSE) 授權。

