# GitHub 實戰新手完全指南 (SOP)

這份文件記錄了將本地專案發布到 GitHub、日常維護更新，以及跨多台電腦（Windows / Mac）同步的完整標準作業程序。日後任何新專案只要依序操作即可。

---

## 目錄
1. [前期環境準備 (每台電腦只需做一次)](#一前期環境準備-每台電腦只需做一次)
2. [建立新專案並推送到 GitHub (全新專案流程)](#二建立新專案並推送到-github-全新專案流程)
3. [日常開發更新流程 (平常修改程式時)](#三日常開發更新流程-平常修改程式時)
4. [多電腦同步工作流程 (Windows ⬌ Mac / 筆電 ⬌ 桌機)](#四多電腦同步工作流程-windows--mac--筆電--桌機)
5. [常見錯誤與防坑技巧](#五常見錯誤與防坑技巧)

---

## 一、前期環境準備 (每台電腦只需做一次)

### 1. 安裝 Git 工具
- **Windows**：開啟 PowerShell / CMD 執行：
  ```cmd
  winget install --id Git.Git -e --source winget
  ```
  *(或至 [git-scm.com](https://git-scm.com/) 下載安裝檔)*
- **Mac**：開啟 Terminal 執行：
  ```bash
  xcode-select --install
  ```

### 2. 設定作者身分資訊
安裝完成後，開啟終端機設定你的名字與 Email（這會記錄在每次存檔紀錄中）：
```bash
git config --global user.name "你的英文名字或暱稱"
git config --global user.email "你的GitHub信箱@gmail.com"
```

---

## 二、建立新專案並推送到 GitHub (全新專案流程)

### 步驟 1：建立乾淨的專案目錄
- **隱私防護**：不要把一整顆硬碟或混雜公司機密資料的總目錄直接做成 Git。建立一個**專屬的專案資料夾**（例如 `D:\work\my_project`），只把該專案需要的程式碼放進去。

建議每個開源專案必備以下檔案：
- **`專案程式碼`**（如 `.py`、`.js` 等）
- **`requirements.txt`**：環境依賴套件（如 `pip freeze > requirements.txt`）
- **`.gitignore`**：設定不要上傳到雲端的暫存檔或密碼檔（如 `*.pyc`, `build/`, `dist/`, `.env`）
- **`README.md`**：專案使用說明
- **`LICENSE`**：開源條款（推薦最通用的 MIT License）

---

### 步驟 2：在 GitHub 網站上建立空儲存庫
1. 開啟 [https://github.com/new](https://github.com/new)。
2. **Repository name**：輸入專案英文名稱（例如 `ics2gcal`）。
3. **Description**：簡短說明這專案的功能（有助於搜尋與分享預覽）。
4. **Public / Private**：公開選 Public；私人專案選 Private。
5. **重要**：下方的 **「Add a README file」請不要勾選**（因為我們本地端已經有了）。
6. 點擊綠色的 **「Create repository」**。
7. 建立成功後，複製網頁上的 HTTPS 網址：
   `https://github.com/你的帳號/專案名稱.git`

---

### 步驟 3：在本地終端機初始化並首次推送 (Push)

打開終端機，依序執行以下指令：

```cmd
# 1. 切換到專案資料夾
cd D:\work\專案名稱

# 2. 初始化 Git 本地倉庫
git init

# 3. 將所有檔案加入暫存區
git add .

# 4. 建立第一個存檔點 (Commit)
git commit -m "Initial commit: 首次專案建立"

# 5. 將預設分支命名為 main
git branch -M main

# 6. 綁定 GitHub 雲端倉庫 (請將網址替換為你剛剛複製的實際網址)
git remote add origin https://github.com/你的帳號/專案名稱.git

# 7. 推送上傳至 GitHub
git push -u origin main
```
> 第一次執行 `git push` 時，系統會彈出瀏覽器視窗要求授權 GitHub 登入，只要點擊確認授權即可。

---

## 三、日常開發更新流程 (平常修改程式時)

日後程式有新增功能、修復 Bug 時，只要記住**黃金三步驟**：

```cmd
# 1. 切換至專案目錄
cd D:\work\專案名稱

# 2. 查看目前改動了哪些檔案 (選填，確認用)
git status

# 3. 將改動加入存檔準備區
git add .

# 4. 建立存檔點並寫下更新說明
git commit -m "修復時間時區問題並調整介面文字"

# 5. 推送上傳到 GitHub
git push
```

---

## 四、多電腦同步工作流程 (Windows ⬌ Mac / 筆電 ⬌ 桌機)

當你在兩台不同的電腦之間切換工作時：

### 1. 新電腦第一次使用該專案 (下載)
新電腦只要執行 `clone`，不需要重複 `git init`：
```bash
git clone https://github.com/你的帳號/專案名稱.git
cd 專案名稱
pip install -r requirements.txt
```

---

### 2. 日常切換電腦的標準節奏（兩步循環）

```text
☀️ 開工前 (電腦 A 或 B)
  └──> 執行 git pull (拉取最新進度)
        └──> 開始撰寫 / 修改程式碼
              └──> 🌙 收工 / 換電腦前
                    └──> 執行 git add . ➔ git commit -m "..." ➔ git push
                          └──> 換到另一台電腦重複此循環
```

#### ☀️ 開工前第一步（拉取最新進度）：
```bash
git pull
```
*確保另一台電腦推上來的進度已經同步到眼前這台電腦。*

#### 🌙 收工 / 換電腦前第二步（推上雲端）：
```bash
git add .
git commit -m "更新今日工作進度"
git push
```

---

## 五、常見錯誤與防坑技巧

### 1. `系統找不到指定的檔案`
- **原因**：指令中帶有 `<>` 角括號（例如直接複製了 `<你的帳號>`）。在 Windows CMD 中 `<` 是特殊符號。
- **解法**：去掉角括號，換成真實帳號名稱：`https://github.com/DarrentChen/ics2gcal.git`。

### 2. `fatal: remote origin already exists`
- **原因**：先前已經設定過遠端網址。
- **解法**：先移除舊的再重新加：
  ```bash
  git remote remove origin
  git remote add origin https://github.com/你的帳號/專案名稱.git
  ```

### 3. `Updates were rejected because the remote contains work...`
- **原因**：你在另一台電腦有推過新程式碼，但眼前這台電腦還沒 `git pull` 就直接修改並 `git push`。
- **解法**：先執行 `git pull` 把雲端最新版合併進來，若有衝突解決後再 `git push`。

### 4. 敏感資料千萬不要 Commit
- 帳號密碼、API Key、個人私人信箱、公司的客戶資料（如 `.ics` 測試檔）**一律加入 `.gitignore`**，不要推上公開的 GitHub！

