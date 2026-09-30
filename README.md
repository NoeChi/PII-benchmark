# deid-benchmark

中文(台灣醫療情境)去識別化 / PII 遮蔽的基準測試。對**任何**去識別化 HTTP API 跑同一份固定考卷,算出漏遮、誤遮與延遲,並可與上一次的結果比較有沒有退步。

所有測試資料皆為虛構(假名、假病歷號、正確檢核碼的假身分證…),可以安全放進 git、交給別人跑。

原本是 hermes-stack(GX10 `~/Taro/Projects/hermes-stack/deid-benchmark`)拿來比較自家 deid-web 與院內 privacy_guard v2 的工具,這份改成通用版:受測系統改由設定檔描述,不再寫死兩套。

## 快速開始

需要 Python 3.11+ 與 [uv](https://docs.astral.sh/uv/)。

```bash
# 1. 描述你的 API
cp systems.example.toml systems.toml      # 編輯 url / body / output
cp .env.example .env                       # 需要 token 就放這裡,systems.toml 用 ${VAR} 引用

# 2. 先送一句範例確認接得上
uv run python -m deid_bench check

# 3. 跑全部
./run.sh
```

不想寫設定檔,也可以臨時指定一套:

```bash
uv run python -m deid_bench check --url http://127.0.0.1:8000/deid
./run.sh --url http://127.0.0.1:8000/deid --name my-api \
  --body '{"text": "{text}", "lang": "zh-TW"}' --output data.masked \
  --header "Authorization: Bearer $TOKEN" --label-pattern '\[([A-Z_]+)\]'
```

## 設定受測系統(`systems.toml`)

每個 `[systems.<名稱>]` 是一套系統,可以同時放好幾套互相比較。名稱會出現在報告,也用來與基準對應。

```toml
[systems.my-api]
type = "http"
url = "http://127.0.0.1:8000/deid"
body = { text = "{text}" }          # request body 範本;值是 "{text}" 的地方換成測資
output = "masked"                   # 回應 JSON 裡遮蔽結果的路徑,巢狀用點:"data.result.0.text"
headers = { Authorization = "Bearer ${MY_API_TOKEN}" }
label_pattern = '\[([A-Z_]+)\]'     # 建議填,見下
```

| 欄位 | 預設 | 說明 |
|---|---|---|
| `type` | `http` | `http`(通用)或 `deid-web`(hermes-stack 專用,見下) |
| `url` | 必填 | API 位址 |
| `method` | `POST` | |
| `body` | `{ text = "{text}" }` | body 範本,可巢狀 |
| `format` | `json` | `json`、`form`(x-www-form-urlencoded)、`raw`(body 是純字串) |
| `output` | `masked` | 從回應取結果的路徑 |
| `response_type` | `json` | 回應本身就是純文字時設 `text`,並把 `output` 設成 `""` |
| `status_field` / `ok_values` | 無 / `["success","ok",true]` | 回應裡的成功旗標;不符合就記為錯誤(仍計分) |
| `headers` | 無 | 字串中的 `${VAR}` 會換成環境變數 |
| `label_pattern` | 無 | 遮蔽標籤的 regex |
| `timeout` / `concurrency` | 600 / `CONCURRENCY`(4) | 秒 / 同時在途請求數 |
| `verify_tls` | `true` | 自簽憑證可設 `false` |

`--systems a,b` 只跑設定檔裡的其中幾套;`--config` 換設定檔。

### `label_pattern`

用來辨識輸出中的遮蔽標籤,影響兩件事:

1. **誘餌題(adversarial)的誤遮**:這些文字完全沒有個資,輸出只要比對到任何標籤就算誤遮。**沒填時改成「輸出與原文不同就算誤遮」**,所以 API 若會順手改動空白或標點,誤遮會被高估,建議填。
2. **人名部分殘留**:判斷 `[NAME]彤` 這類「標籤旁邊還留一個字」。沒填時用寬鬆的預設樣式(`[...]`、`<TAG>`、`***`、`█`)。

有 capture group 時,第一個非空 group 當作型別名稱,報告末尾會統計各型別的用量。

### `type = "deid-web"`

hermes-stack 的 deid-web 除了遮蔽,還能用 `/api/restore` 取回代號與原文的對照,所以能多量四項:代號型別對不對、同一原文是否對到多個代號、遮蔽範圍有沒有吃到相鄰字、還原後是否等於原文。一般 API 沒有這些功能,報告裡就不會出現這幾欄。

在 GX10 上跑時,用 `scripts/run-with-deid-web.sh` 起一個隔離的實例(port 8199、獨立 DB),避免把幾百筆測試寫進正式環境(8100)的 conversion log。

## 指令

```bash
./run.sh                                  # = uv run python -m deid_bench run(先讀 .env)
./run.sh --label after-fix                # 檔名加標籤
./run.sh --long-sizes 4000,32000,128000   # 長文字數;0 = 不跑長文
./run.sh --suites names_zh,ids            # 只跑部分套件

uv run python -m deid_bench list                   # 套件與 case 數
uv run python -m deid_bench dump names_zh          # 看測資
uv run python -m deid_bench check                  # 每套系統送一句範例
uv run python -m deid_bench report results/X.json  # 重新產生報告
uv run python -m deid_bench compare results/new.json results/old.json
uv run python -m deid_bench baseline results/X.json   # 設為 baseline/latest.json
```

## 產物

- `results/<時間>.json`:每個 case × 系統的完整評分與輸出
- `results/<時間>.md`:報告(套件總覽、各系統的漏遮/誤遮清單、所有系統都漏的共同盲區、觀察項、長文)
- `results/<時間>-vs-baseline.md`:與 `baseline/latest.json` 的退步/進步清單(有設基準時)
- `results/<時間>-synthetic_<n>-<系統>.txt`:長文的完整遮蔽輸出

基準比較依**系統名稱**對應,只比兩邊都有的系統。`run` 與 `compare` 在有退步(或基準有、這次沒跑到的 case)時回傳 exit code 1,可以接 CI。只跑部分套件時,沒跑到的 case 也會被算成退步。

`reference/` 放了 2026-09-14 在 GX10 跑的一份完整結果(deid-web 對 privacy_guard v2,系統名分別是 `mine` 與 `v2`),可以當作參考分數。

## 計分

`deid_bench/model.py` 的 `Case`:

| 欄位 | 意思 |
|---|---|
| `mask` | 必須被遮的值 → 期望型別(P_NAME/PID/NID/HID/PHONE/EMAIL/ADDR/OTHER) |
| `keep` | 必須保留的值;消失就是誤遮 |
| `observe` | 政策未定(例如「陳醫師」、宏觀地名、生日),只在報告列出各系統有沒有遮,不計分 |
| `known_gap` | 已知極限(base64、URL 編碼),獨立列出 |
| `no_mask` | 整段不該有任何遮蔽(adversarial 套件) |

- **recall**:mask 值不再出現於輸出
- **partial**:人名整體不在,但頭兩字或尾兩字仍在(例如 `郭曉彤` → `[tok]彤`)
- **keep**:keep 值仍在輸出
- **type / inconsistent / extended / roundtrip**:只有 `deid-web` 類型量得到

計分只看「值是否還出現在輸出」,和 API 用什麼方式遮(標籤、星號、代換成假名)無關。但**代換成假名**的系統若剛好換成測資裡另一個值,會被誤算;值若同時出現在別處(例如兩列共用同一個病歷號)也會互相影響。

請求失敗的 case 不進 recall/keep 分母,另列在「請求失敗」;失敗會自動重試一次。每個套件用固定亂數種子,只跑部分套件或換順序都不會改變測資內容。

## 套件

| 套件 | 內容 |
|---|---|
| names_zh | 常見/二字/複姓/罕用字/日式人名、稱謂相鄰、重複、密集 |
| names_foreign | 英文名、羅馬拼音、中英混排 |
| ids | 身分證、病歷號(有/無關鍵字、表格)、健保卡號、員編/床號/檢驗值(不該遮) |
| contacts | 手機/市話/國際碼/分機、email 各種寫法 |
| addresses | 完整/部分地址、機構名(不該遮) |
| formats | 30+ 種文字格式 × 6 個假名 |
| structures | 名冊、班表、CSV/JSON/Markdown 混合個資、鍵值紀錄 |
| scenarios | 入院、出院、交班、電話紀錄、會診、社工、雙語、用藥、檢驗、轉診、事件通報 |
| adversarial | 沒有個資的誘餌文字:醫院名、職稱、人名命名疾病、藥名、地名、三字詞 |
| encoding | 全形、空格、零寬字元、換行切斷、簡體、HTML entity、RTL |
| longtext | 合成長文(預設 4000 與 32000 字;可加 128000) |

新增 case:在對應的 `deid_bench/suites/*.py` 加 `Case(...)`,id 要唯一;用 `dump` 檢查測資、`list` 確認數量。

## 給別人用之前

- 跑一次就會把整份考卷送到對方的 API。若要用來比較廠商,考慮保留一部分 case 不公開,避免對方針對考卷調校。
- `reference/` 的結果裡有院內 privacy_guard v2 的網址;要給院外的人時先拿掉。
