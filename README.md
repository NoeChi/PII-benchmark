# deid-benchmark

中文(台灣醫療情境)去識別化 / PII 遮蔽的基準測試。對**任何**去識別化 HTTP API 跑同一份固定考卷,算出漏遮、誤遮與延遲,並可與上一次的結果比較有沒有退步。

所有測試資料皆為虛構(假名、假病歷號、正確檢核碼的假身分證…),可以安全放進 git、交給別人跑。

原本是 hermes-stack(GX10 `~/Taro/Projects/hermes-stack/deid-benchmark`)拿來比較自家 deid-web 與院內 privacy_guard v2 的工具,這份改成通用版:受測系統改由設定檔描述,不再寫死兩套。

## 快速開始

需要 Python 3.11+ 與 [uv](https://docs.astral.sh/uv/)。

**第一次使用(每台電腦只做一次)**:建立設定檔,再把裡面的 `url` / `body` / `output` 改成你的 API。
⚠️ 已經有 `systems.toml` 就別再 `cp`,會把改好的設定蓋掉。

```bash
cp systems.example.toml systems.toml      # 然後編輯 systems.toml(範例檔裡的網址是假的,一定要改)
cp .env.example .env                       # 選用:API 需要 token 才要,systems.toml 用 ${VAR} 引用
```

**測試**:下面兩個指令都會打 `systems.toml` 裡寫的**所有**系統,差別只在送多少。

1. **確認連線(剛寫好或改過 `systems.toml` 時才需要)**:每套只送 1 句範例,印出輸入與輸出,看到 `✓ 接得上` 就代表設定沒問題。

   ```bash
   uv run python -m deid_bench check
   ```

2. **正式跑考卷**:每套送整份考卷(約 240 題),產生報告。設定沒改的話,之後每次都只要跑這個。

   ```bash
   ./run.sh
   ```

### 不寫設定檔,用參數臨時指定一套

加了 `--url` 就**不讀** `systems.toml`,改打你指定的網址。

以下的網址、欄位名、token 都是**範例值**,要換成你的 API 實際的樣子,照抄會連不到:

```bash
# 最少只要給 --url;API 收 {"text": "..."}、回 {"masked": "..."} 時其他都用預設就好
uv run python -m deid_bench check --url https://deid.example.com/api/mask

# 格式不同時,用參數描述
export API_TOKEN=你的token
./run.sh --url https://deid.example.com/api/mask --name my-api \
  --body '{"text": "{text}", "lang": "zh-TW"}' \
  --output data.masked \
  --header "Authorization: Bearer $API_TOKEN" \
  --label-pattern '\[([A-Z_]+)\]'
```

| 參數 | 要改成什麼 | 沒給時 |
|---|---|---|
| `--url` | 你的 API 位址(必填) | — |
| `--name` | 隨便取,報告與基準比較用的系統名稱 | `api` |
| `--body` | 你的 API 收的 JSON;要放測資的地方寫 `"{text}"`,其餘照你的 API 填 | `{"text": "{text}"}` |
| `--output` | 回應 JSON 中遮蔽結果的位置;`{"data": {"masked": "..."}}` 就寫 `data.masked` | `masked` |
| `--header` | 需要認證才加;可重複給多個 | 不加 |
| `--label-pattern` | 你的 API 遮蔽標籤的樣子,見下方「label_pattern」 | 不設 |

不確定回應長什麼樣?先用 `curl` 打一次看回傳的 JSON,再決定 `--output`。

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

**一句話:告訴測試工具「你的 API 把個資遮掉後,會換成什麼樣子」。** 填了算得比較準;不填也能跑。

每個 API 遮個資的寫法不一樣,例如輸入 `病人王小明`:

| API 輸出 | 標籤長相 | `label_pattern` 可以這樣寫 |
|---|---|---|
| `病人[NAME]` | `[大寫字]` | `'\[([A-Z_]+)\]'` |
| `病人[PII:PERSON]` | `[PII:大寫字]` | `'\[PII:([A-Z_]+)\]'` |
| `病人<PERSON>` | `<大寫字>` | `'<([A-Z_]+)>'` |
| `病人***` | 星號 | `'\*{2,}'` |

好幾種寫法混用時用 `|` 串起來,例如 `'\[PII:([A-Z_]+)\]|<([A-Z_]+)>'`。在 toml 裡記得用**單引號**包起來,反斜線才不會被吃掉。

**為什麼需要知道標籤長相?用在兩個地方:**

1. **抓「不該遮卻遮了」**。考卷裡有一組誘餌題(adversarial),內容完全沒有個資,只是故意放了容易誤判的字,例如:

   ```
   病人罹患川崎病,轉介至台中榮民總醫院,由護理師衛教。
   ```

   正確答案是一個字都不遮。
   - **有填**:輸出只要出現標籤(例如把「川崎」當人名遮成 `罹患[NAME]病`),就算誤遮。
   - **沒填**:工具不知道標籤長怎樣,只能比「輸出跟原文一不一樣」。有些 API 會順手改掉空白或標點,明明沒遮也會被判誤遮,分數會偏低。

2. **抓「只遮一半」**。例如 `郭曉彤` 被輸出成 `[NAME]彤`,最後一個字還留著,仍可能認出是誰。工具要知道 `[NAME]` 是標籤,才看得出「標籤旁邊還黏著一個字」。沒填時會拿常見的長相去猜(`[...]`、`<TAG>`、`***`、`█`)。

**括號 `( )` 的作用**:regex 裡括號括起來的部分會被當成**標籤種類**。例如 `\[PII:([A-Z_]+)\]` 碰到 `[PII:PERSON]` 會抓出 `PERSON`,報告最後會統計各種類的數量(`PERSON 120, PHONE 45…`),看得出你的 API 最常把什麼當個資。沒有括號時,就用整個標籤當名稱。

**怎麼確認寫對了**:跑 `uv run python -m deid_bench check`,輸出裡有「標籤:{...}」那行就對了;寫錯會提醒「label_pattern 沒有比對到任何標籤」。

### `type = "deid-web"`

> 只跟 hermes-stack 的 deid-web(GX10 上的去個資網頁服務)有關。測其他 API 的人可以跳過這一節,一律用 `type = "http"`。

**一句話:deid-web 遮完還能還原,所以能多檢查四件事。**

一般的去識別化 API 是**單向**的,遮掉就拿不回原文:

```
輸入:病人王小明來看診
輸出:病人[PII:PERSON]來看診
```

deid-web 是**雙向**的:用帶編號的代號遮蔽,再透過 `/api/restore` 換回原文。

```
輸出:病人[P_NAME_a1b2c3]來看診
還原:[P_NAME_a1b2c3] → 王小明
```

因為知道「哪個代號對應哪段原文」,所以能多檢查:

| 檢查項目 | 出錯的例子 | 為什麼是問題 |
|---|---|---|
| 代號型別對不對 | 身分證 `A123456789` 被標成 `[PHONE_…]` | 有遮到,但種類判錯 |
| 同一個人是否對到同一個代號 | 文中兩次「王小明」,一次 `[P_NAME_a1…]`、一次 `[P_NAME_b2…]` | 讀的人會以為是兩個不同的人 |
| 有沒有多遮到旁邊的字 | `護理師王小明` → `護理[P_NAME_…]` | 連「師」也一起吃掉 |
| 還原後是否跟原文一模一樣 | 遮完再還原,少了一個字 | 還原功能有 bug |

一般 API 沒有還原功能,這四項量不到,報告裡就不會出現這幾欄。

**在 GX10 上測 deid-web:用 `scripts/run-with-deid-web.sh`,不要直接打正式服務。**

GX10 的 `:8100` 是正式服務,每處理一筆都會寫進紀錄(conversion log)。直接拿考卷打它,幾百筆假資料會混進正式紀錄。這支腳本會:

1. 另外起一個**測試用**的 deid-web(port `8199`、獨立資料庫)
2. 拿考卷打這個測試實例
3. 跑完自動關掉

`systems.toml` 要有這一段,才會測到它:

```toml
[systems.deid-web]
type = "deid-web"
url = "http://127.0.0.1:8199"
```

```bash
WEB_DIR=~/Taro/Projects/hermes-stack/deid-web scripts/run-with-deid-web.sh
```

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
