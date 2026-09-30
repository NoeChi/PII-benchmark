# 去識別化基準報告 2026-09-14T19:37:05

- 系統:mine, v2;case 數 240;耗時 54.0 秒
- 版本:deid-web `62b5cc5-dirty`, hermes-gateway `7cdf883-dirty`, presidio-service `8062f39-dirty`
- 自家服務回報:audit_model `qwen3.6-35b`,presidio `6e47f91+healthz`,web `62b5cc5-dirty`

計分:recall = 該遮的值不再出現於輸出;keep = 該保留的值仍在輸出;partial = 人名頭兩字或尾兩字殘留;type = 自家代號型別與期望不符;known gap 另計。

## 各套件總覽

| 套件 | cases | mine recall | mine keep | mine partial | mine p50 ms | v2 recall | v2 keep | v2 partial | v2 p50 ms | mine type錯 |
|---|---|---|---|---|---|---|---|---|---|---|
| names_zh | 44 | 56/56 (100%) | 15/15 (100%) | 0 | 382 | 32/56 (57%) | 15/15 (100%) | 10 | 71 | 0 |
| names_foreign | 16 | 16/16 (100%) | 2/4 (50%) | 0 | 199 | 13/16 (81%) | 3/4 (75%) | 0 | 71 | 0 |
| ids | 28 | 24/25 (96%) | 18/19 (95%) | 0 | 192 | 15/25 (60%) | 17/19 (89%) | 0 | 72 | 1 |
| contacts | 28 | 20/20 (100%) | 4/6 (67%) | 0 | 165 | 19/20 (95%) | 6/6 (100%) | 0 | 68 | 0 |
| addresses | 25 | 15/15 (100%) | 12/15 (80%) | 0 | 194 | 13/14 (93%) | 11/15 (73%) | 0 | 68 | 0 |
| formats | 35 | 198/198 (100%) | 26/27 (96%) | 0 | 212 | 132/198 (67%) | 27/27 (100%) | 99 | 73 | 0 |
| structures | 11 | 161/161 (100%) | 35/36 (97%) | 0 | 2390 | 124/161 (77%) | 35/36 (97%) | 9 | 100 | 1 |
| scenarios | 12 | 66/66 (100%) | 55/60 (92%) | 0 | 146 | 53/66 (80%) | 58/60 (97%) | 14 | 82 | 0 |
| adversarial | 18 | — | 63/77 (82%) | 0 | 1 | — | 69/77 (90%) | 0 | 70 | 0 |
| encoding | 20 | 19/20 (95%) | 2/2 (100%) | 0 | 118 | 11/20 (55%) | 2/2 (100%) | 0 | 73 | 0 |
| longtext | 3 | 8219/8219 (100%) | 15/15 (100%) | 0 | 7842 | 6166/8219 (75%) | 15/15 (100%) | 497 | 706 | 0 |
| **合計** | 240 | **8794/8796 (100%)** | **247/276 (89%)** | 0 | | **6578/8795 (75%)** | **258/276 (93%)** | 629 | | 2 |

## 請求失敗 / 附帶錯誤(失敗的 case 不進 recall 分母):1 / 0

- 失敗 `v2` addresses/english_address: 26ms {"status":"fail","value":"","message":"Unable to map deterministic redaction value"}

## 自家系統需要看的地方（mine）

### 漏遮(整個值殘留):2
- encoding/zero_width_in_nid: `A1234​56789`  → 輸出:`身分證 A1234​56789`
- ids/mrn_repeated_bare: `10234567`  → 輸出:`Admission ID: [PID_0c4514],訂單號 10234567`

### 部分殘留(人名頭尾兩字):0
(無)

### 誤遮(該保留卻消失):29
- addresses/city_only: `高雄市`  → 輸出:`病人從[ADDR_61f60c]北上就醫。`
- addresses/landmark: `中山路`  → 輸出:`掛號櫃台在一樓大廳,靠近[ADDR_0bf99c]側門。`
- addresses/road_only: `中山路`  → 輸出:`沿著[ADDR_0bf99c]往北就會看到醫院。`
- adversarial/eponymous_diseases: `馬凡氏症候群`  → 輸出:`鑑別診斷包含川崎病、阿茲海默症、帕金森氏症、庫欣氏症候群、[P_NAME_8a5e76]氏症候群、杜興氏肌肉失養症。`
- adversarial/eponymous_diseases: `[任何遮蔽] P_NAME×1`  → 輸出:`鑑別診斷包含川崎病、阿茲海默症、帕金森氏症、庫欣氏症候群、[P_NAME_8a5e76]氏症候群、杜興氏肌肉失養症。`
- adversarial/name_like_common_words: `高雄`  → 輸出:`[P_NAME_383144]變法、[P_NAME_1f5587]、[P_NAME_c3a99a]為歷史人物;[ADDR_46ce5f]、[ADDR_49be9d]為縣市。`
- adversarial/name_like_common_words: `屏東`  → 輸出:`[P_NAME_383144]變法、[P_NAME_1f5587]、[P_NAME_c3a99a]為歷史人物;[ADDR_46ce5f]、[ADDR_49be9d]為縣市。`
- adversarial/place_like_words: `中正紀念堂`  → 輸出:`[ADDR_cadf52]、[ADDR_cb16d0]、台中市政府、[ADDR_3cc2b7]、[ADDR_1e17e4]。`
- adversarial/place_like_words: `大同電鍋`  → 輸出:`[ADDR_cadf52]、[ADDR_cb16d0]、台中市政府、[ADDR_3cc2b7]、[ADDR_1e17e4]。`
- adversarial/place_like_words: `中山高速公路`  → 輸出:`[ADDR_cadf52]、[ADDR_cb16d0]、台中市政府、[ADDR_3cc2b7]、[ADDR_1e17e4]。`
- adversarial/place_like_words: `民生社區`  → 輸出:`[ADDR_cadf52]、[ADDR_cb16d0]、台中市政府、[ADDR_3cc2b7]、[ADDR_1e17e4]。`
- adversarial/place_like_words: `[任何遮蔽] ADDR×4`  → 輸出:`[ADDR_cadf52]、[ADDR_cb16d0]、台中市政府、[ADDR_3cc2b7]、[ADDR_1e17e4]。`
- adversarial/surname_chars_in_words: `吳郭魚`  → 輸出:`陳舊性骨折、林口長庚、黃疸、張力性氣胸、[P_NAME_c6c3c8]、[P_NAME_c97f83]。`
- adversarial/three_char_terms: `王不留行`  → 輸出:`[P_NAME_d91665]留行、[P_NAME_9f9b88]、[P_NAME_32f595]中藥材;李子、蘋果為水果。`
- adversarial/three_char_terms: `白頭翁`  → 輸出:`[P_NAME_d91665]留行、[P_NAME_9f9b88]、[P_NAME_32f595]中藥材;李子、蘋果為水果。`
- adversarial/three_char_terms: `何首烏`  → 輸出:`[P_NAME_d91665]留行、[P_NAME_9f9b88]、[P_NAME_32f595]中藥材;李子、蘋果為水果。`
- adversarial/three_char_terms: `[任何遮蔽] P_NAME×3`  → 輸出:`[P_NAME_d91665]留行、[P_NAME_9f9b88]、[P_NAME_32f595]中藥材;李子、蘋果為水果。`
- contacts/tollfree: `0800-123-456`  → 輸出:`客服專線 [PHONE_36c561],[ADDR_866cef] [PHONE_1b17f9]。`
- contacts/tollfree: `0800-030-598`  → 輸出:`客服專線 [PHONE_36c561],[ADDR_866cef] [PHONE_1b17f9]。`
- formats/csv_multi_row: `科主任`  → 輸出:`西醫師,重症部,重內1,[P_NAME_382392],2355,[P_NAME_eafd05]主任⏎西醫師,重症部,重內1,[P_NAME_917add],5730,主治醫師⏎西…`
- ids/nhi_drug_code: `BC23456100`  → 輸出:`健保碼 [HID_9769cf],批號 A1234567`
- names_foreign/famous_not_patient: `Framingham`  → 輸出:`依據 [ADDR_211497] 與 [ADDR_1a5dd1] [ADDR_c443b0] 評估。`
- names_foreign/famous_not_patient: `Glasgow`  → 輸出:`依據 [ADDR_211497] 與 [ADDR_1a5dd1] [ADDR_c443b0] 評估。`
- scenarios/incident_report: `護理長`  → 輸出:`異常事件通報⏎事件:病人跌倒⏎時間:2026-09-13 22:40⏎地點:12A 病房走廊⏎當事人:[P_NAME_85e2c2](病歷號 [PID_0c4514])⏎發現者:護…`
- scenarios/lab_report: `檢驗師`  → 輸出:`檢驗報告⏎姓名 [P_NAME_917add] 病歷號 [PID_0c4514] 採檢 2026-09-13 08:15⏎項目 | 結果 | 參考值⏎WBC | 11.2 | 4-…`
- scenarios/phone_log: `檢驗科`  → 輸出:`電話紀錄⏎09:10 家屬[P_NAME_b69e45]來電([PHONE_b6c687])詢問手術時間,已告知 14:00。⏎10:25 回撥 [PHONE_97faba] [A…`
- scenarios/referral_letter: `中山醫學大學附設醫院`  → 輸出:`轉診[P_NAME_cd0bfa]⏎[P_NAME_d4fb7b]:⏎茲有病人[P_NAME_b69e45](身分證 [NID_3dee11],病歷號 [PID_e2860e]),…`
- scenarios/social_work: `中山區公所`  → 輸出:`社工訪視紀錄⏎個案:[P_NAME_ccf3e1](身分證 [NID_29a874])獨居,主要照顧者為女[P_NAME_d75032](電話 [PHONE_b6c687],ema…`
- structures/csv_full_pii_6: `12B-01`  → 輸出:`姓名,病歷號,身分證,電話,地址,床號,診斷⏎[P_NAME_2102eb],[PID_4a1a46],[NID_4b8dfc],[PHONE_880e92],[ADDR_70ef…`

### 型別錯誤(值 → 實際/期望):2
- ids/hid_bare: `000012345678 → OTHER_IDENTIFYING/HID`  → 輸出:`卡號 [OTHER_IDENTIFYING_f06f24] 已註銷`
- structures/json_patients_5: `000069576018 → NID/HID`  → 輸出:`[{"name":"[P_NAME_9ac50e]","mrn":"[PID_db20d9]","nid":"[NID_0890fc]","phone":"[PHONE_d9f16…`

### 遮蔽範圍吃到相鄰字(值 → 實際被遮整段):189
- contacts/landline_with_ext: `04-23592525 → 04-23592525 ext 2610`  → 輸出:`聯絡電話 [PHONE_4258cf],請於上班時間來電。`
- formats/fullwidth_space_separated: `刁沄妘 → 刁沄妘　龎芫綺`  → 輸出:`[P_NAME_377ea2]　[P_NAME_6446a4]　[P_NAME_b69e45]　[P_NAME_85e2c2]　[P_NAME_ccf3e1]`
- formats/fullwidth_space_separated: `龎芫綺 → 刁沄妘　龎芫綺`  → 輸出:`[P_NAME_377ea2]　[P_NAME_6446a4]　[P_NAME_b69e45]　[P_NAME_85e2c2]　[P_NAME_ccf3e1]`
- formats/log_line: `刁沄妘 → =刁沄妘`  → 輸出:`2026-09-14 10:00:01 INFO user[P_NAME_ec5198] action=login⏎2026-09-14 10:00:05 INFO user=[P…`
- formats/log_line: `林晏伃 → =林晏伃`  → 輸出:`2026-09-14 10:00:01 INFO user[P_NAME_ec5198] action=login⏎2026-09-14 10:00:05 INFO user=[P…`
- formats/natural_enumeration: `刁沄妘 → 為刁沄妘`  → 輸出:`本科現有六位主治醫師,分別[P_NAME_a2545d]、[P_NAME_917add]、[P_NAME_6446a4]、[P_NAME_b69e45]、[P_NAME_85e2c…`
- formats/sql_insert: `刁沄妘 → 刁沄妘'`  → 輸出:`INSERT INTO staff (name, emp_id) VALUES ('[P_NAME_e8651a], 2355), ('[P_NAME_b3b675], 5730)…`
- formats/sql_insert: `龎芫綺 → 龎芫綺'`  → 輸出:`INSERT INTO staff (name, emp_id) VALUES ('[P_NAME_e8651a], 2355), ('[P_NAME_b3b675], 5730)…`
- formats/sql_insert: `郭曉彤 → 郭曉彤'`  → 輸出:`INSERT INTO staff (name, emp_id) VALUES ('[P_NAME_e8651a], 2355), ('[P_NAME_b3b675], 5730)…`
- formats/sql_insert: `林晏伃 → 林晏伃'`  → 輸出:`INSERT INTO staff (name, emp_id) VALUES ('[P_NAME_e8651a], 2355), ('[P_NAME_b3b675], 5730)…`
- formats/star_separated: `刁沄妘 → 刁沄妘★龎芫綺★`  → 輸出:`[P_NAME_9a3094][P_NAME_6446a4]★[P_NAME_ede76e][P_NAME_4d658b][P_NAME_ccf3e1]`
- formats/star_separated: `龎芫綺 → 刁沄妘★龎芫綺★`  → 輸出:`[P_NAME_9a3094][P_NAME_6446a4]★[P_NAME_ede76e][P_NAME_4d658b][P_NAME_ccf3e1]`
- formats/star_separated: `曾智杰 → 曾智杰★`  → 輸出:`[P_NAME_9a3094][P_NAME_6446a4]★[P_NAME_ede76e][P_NAME_4d658b][P_NAME_ccf3e1]`
- formats/star_separated: `林晏伃 → 林晏伃★`  → 輸出:`[P_NAME_9a3094][P_NAME_6446a4]★[P_NAME_ede76e][P_NAME_4d658b][P_NAME_ccf3e1]`
- names_foreign/english_David: `David Chen → Patient David Chen`  → 輸出:`[P_NAME_a48f40] was admitted for observation.`
- names_foreign/english_Sarah: `Sarah Lee → Patient Sarah Lee`  → 輸出:`[P_NAME_90057a] was admitted for observation.`
- names_foreign/mixed_zh_en: `Sarah Lee → Dr. Sarah Lee`  → 輸出:`病人 [P_NAME_f7c1d6]([P_NAME_602088])由 [P_NAME_8de280] 收治。`
- names_zh/adjacent_no_delim: `刁沄妘 → 刁沄妘龎芫綺郭曉彤`  → 輸出:`與會:[P_NAME_290c03]`
- names_zh/adjacent_no_delim: `龎芫綺 → 刁沄妘龎芫綺郭曉彤`  → 輸出:`與會:[P_NAME_290c03]`
- names_zh/adjacent_no_delim: `郭曉彤 → 刁沄妘龎芫綺郭曉彤`  → 輸出:`與會:[P_NAME_290c03]`
- names_zh/japanese_田中美咲: `田中美咲 → 患田中美咲`  → 輸出:`外籍病[P_NAME_d71a1e]需要日文翻譯協助。`
- names_zh/name_with_english_alias: `郭曉彤 → 郭曉彤 (Tina Kuo`  → 輸出:`[P_NAME_dd3ce5]) 為本次個管師。`
- names_zh/name_with_english_alias: `Tina Kuo → 郭曉彤 (Tina Kuo`  → 輸出:`[P_NAME_dd3ce5]) 為本次個管師。`
- names_zh/rare_洪熒里: `洪熒里 → 師洪熒里`  → 輸出:`護理[P_NAME_1e72ce]負責 12A 病房今日晚班。`
- names_zh/rare_諶芷妘: `諶芷妘 → 師諶芷妘`  → 輸出:`護理[P_NAME_d47e0e]負責 12A 病房今日晚班。`
- names_zh/rare_邵翊喆: `邵翊喆 → 師邵翊喆`  → 輸出:`護理[P_NAME_66ae84]負責 12A 病房今日晚班。`
- names_zh/rare_鄔紜瑄: `鄔紜瑄 → 師鄔紜瑄`  → 輸出:`護理[P_NAME_c1c48e]負責 12A 病房今日晚班。`
- names_zh/rare_闕昀蓁: `闕昀蓁 → 師闕昀蓁`  → 輸出:`護理[P_NAME_e8ab1c]負責 12A 病房今日晚班。`
- names_zh/rare_麴沛芸: `麴沛芸 → 師麴沛芸`  → 輸出:`護理[P_NAME_9e69fa]負責 12A 病房今日晚班。`
- names_zh/rare_龔玥彤: `龔玥彤 → 師龔玥彤`  → 輸出:`護理[P_NAME_789d54]負責 12A 病房今日晚班。`
- names_zh/repeated_3x: `刁沄妘 → 刁沄妘入院`  → 輸出:`[P_NAME_3906db]。[P_NAME_b9f740]屬已通知。明日[P_NAME_382392]安排手術。`
- names_zh/repeated_3x: `刁沄妘 → 刁沄妘家`  → 輸出:`[P_NAME_3906db]。[P_NAME_b9f740]屬已通知。明日[P_NAME_382392]安排手術。`
- names_zh/title_after: `王小明 → 請王小明`  → 輸出:`[P_NAME_5d98d2]醫師回電。`
- names_zh/two_char_張偉: `張偉 → 張偉於`  → 輸出:`病患[P_NAME_f79ed5]急診留觀,家屬陪同。`
- names_zh/two_char_李娜: `李娜 → 李娜於`  → 輸出:`病患[P_NAME_ca9a24]急診留觀,家屬陪同。`
- names_zh/two_char_林芳: `林芳 → 林芳於`  → 輸出:`病患[P_NAME_bb5370]急診留觀,家屬陪同。`
- names_zh/two_char_王明: `王明 → 王明於`  → 輸出:`病患[P_NAME_e9bbe9]急診留觀,家屬陪同。`
- scenarios/incident_report: `龎芫綺 → 長龎芫綺`  → 輸出:`異常事件通報⏎事件:病人跌倒⏎時間:2026-09-13 22:40⏎地點:12A 病房走廊⏎當事人:[P_NAME_85e2c2](病歷號 [PID_0c4514])⏎發現者:護…`
- scenarios/lab_report: `王小明 → 師王小明`  → 輸出:`檢驗報告⏎姓名 [P_NAME_917add] 病歷號 [PID_0c4514] 採檢 2026-09-13 08:15⏎項目 | 結果 | 參考值⏎WBC | 11.2 | 4-…`
- scenarios/nursing_handover: `龎芫綺 → 師龎芫綺`  → 輸出:`病房交班 12A⏎03 床 [P_NAME_85e2c2]:術後第二天,血壓 128/82,血糖 142,已拔引流管,預計 9/16 出院。⏎04 床 [P_NAME_ccf3e1…`
- scenarios/phone_log: `龎小芸 → 兒龎小芸`  → 輸出:`電話紀錄⏎09:10 家屬[P_NAME_b69e45]來電([PHONE_b6c687])詢問手術時間,已告知 14:00。⏎10:25 回撥 [PHONE_97faba] [A…`
- scenarios/social_work: `龎芫綺 → 兒龎芫綺`  → 輸出:`社工訪視紀錄⏎個案:[P_NAME_ccf3e1](身分證 [NID_29a874])獨居,主要照顧者為女[P_NAME_d75032](電話 [PHONE_b6c687],ema…`
- longtext/synthetic_128000: 117 個,例如 `['侯婷紜 → 侯婷紜(病', '顏妍柏 → 顏妍柏(病', '連睿涵 → 連睿涵(病', '蘇彤翔 → 蘇彤翔(病', '曾和妍 → 曾和妍(病', '范雅冠 → 范雅冠(病']`
- longtext/synthetic_32000: 27 個,例如 `['趙欣欣 → 趙欣欣(病', '紀雅冠 → 紀雅冠(病', '鍾宇舒 → 鍾宇舒(病', '康婷婕 → 康婷婕(病', '阮彤翰 → 阮彤翰(病', '魏芬冠 → 魏芬冠(病']`
- longtext/synthetic_4000: 3 個,例如 `['傅芬軒 → 傅芬軒(病', '孫語睿 → 孫語睿(病', '紀淑宇 → 紀淑宇(病']`

### 同一原文對到多個代號:1
- names_zh/repeated_3x: `刁沄妘`  → 輸出:`[P_NAME_3906db]。[P_NAME_b9f740]屬已通知。明日[P_NAME_382392]安排手術。`

### 還原後不等於原文:3
- formats/python_repr_list: `roundtrip`  → 輸出:`["[P_NAME_382392]","[P_NAME_917add]","[P_NAME_6446a4]","[P_NAME_b69e45]","[P_NAME_85e2c2]"…`
- formats/python_repr_nested: `roundtrip`  → 輸出:`{"rows":[{"name":"[P_NAME_382392]"},{"name":"[P_NAME_917add]"},{"name":"[P_NAME_6446a4]"},…`
- structures/json_patients_5: `roundtrip`  → 輸出:`[{"name":"[P_NAME_9ac50e]","mrn":"[PID_db20d9]","nid":"[NID_0890fc]","phone":"[PHONE_d9f16…`


## 院內 v2 的弱點（v2）

### 漏遮(整個值殘留):2217
(短 case 只列前 60 筆,共 164)
- addresses/address_in_csv: `刁沄妘`  → 輸出:`姓名,地址⏎[PII:PERSON],[PII:LOC]⏎刁沄妘,[PII:LOC]`
- contacts/mobile_intl_zero: `+886 (0)912-345-678`  → 輸出:`手機 +886 (0)912-345-678`
- encoding/fullwidth_nid: `Ａ１２３４５６７８９`  → 輸出:`身分證 Ａ１２３４５６７８９`
- encoding/fullwidth_phone: `０９１２３４５６７８`  → 輸出:`電話 ０９１２３４５６７８`
- encoding/nid_lowercase: `a123456789`  → 輸出:`身分證 a123456789`
- encoding/nid_with_dash: `A12-345-6789`  → 輸出:`身分證 A12-345-6789`
- encoding/simplified_chinese: `王晓彤`  → 輸出:`病人王晓彤,联系电话 [PII:PHONE],住址[PII:LOC]西屯区台湾大道四段1650号`
- encoding/spaced_nid: `A 1 2 3 4 5 6 7 8 9`  → 輸出:`身分證 A 1 2 3 4 5 6 7 8 9`
- encoding/spaced_phone: `0 9 1 2 3 4 5 6 7 8`  → 輸出:`電話 0 9 1 2 3 4 5 6 7 8`
- encoding/zero_width_in_name: `王​小​明`  → 輸出:`病人王​小​明今日入院`
- encoding/zero_width_in_nid: `A1234​56789`  → 輸出:`身分證 A1234​56789`
- formats/ascii_box_table: `刁沄妘`  → 輸出:`┌────────┬────────┐⏎│ 刁沄妘 │ 2355   │⏎│ 龎芫綺 │ 5730   │⏎│ [PII:PERSON]彤 │ 8075   │⏎│ [PII:PE…`
- formats/ascii_box_table: `龎芫綺`  → 輸出:`┌────────┬────────┐⏎│ 刁沄妘 │ 2355   │⏎│ 龎芫綺 │ 5730   │⏎│ [PII:PERSON]彤 │ 8075   │⏎│ [PII:PE…`
- formats/chat_log: `刁沄妘`  → 輸出:`[10:00] 刁沄妘: 早安⏎[10:01] 龎芫綺: 早⏎[10:02] [PII:PERSON]彤: morning⏎[10:03] [PII:PERSON]杰: 都到了嗎⏎…`
- formats/chat_log: `龎芫綺`  → 輸出:`[10:00] 刁沄妘: 早安⏎[10:01] 龎芫綺: 早⏎[10:02] [PII:PERSON]彤: morning⏎[10:03] [PII:PERSON]杰: 都到了嗎⏎…`
- formats/csv_multi_row: `刁沄妘`  → 輸出:`西醫師,重症部,重內1,刁沄妘,2355,科主任⏎西醫師,重症部,重內1,龎芫綺,5730,主治醫師⏎西醫師,重症部,重內1,[PII:PERSON]彤,8075,主治醫師⏎西醫師…`
- formats/csv_multi_row: `龎芫綺`  → 輸出:`西醫師,重症部,重內1,刁沄妘,2355,科主任⏎西醫師,重症部,重內1,龎芫綺,5730,主治醫師⏎西醫師,重症部,重內1,[PII:PERSON]彤,8075,主治醫師⏎西醫師…`
- formats/email_header: `刁沄妘`  → 輸出:`From: 刁沄妘 <[PII:EMAIL]>⏎To: 龎芫綺 <[PII:EMAIL]>⏎Cc: [PII:PERSON]彤, [PII:PERSON]杰, [PII:PERSO…`
- formats/email_header: `龎芫綺`  → 輸出:`From: 刁沄妘 <[PII:EMAIL]>⏎To: 龎芫綺 <[PII:EMAIL]>⏎Cc: [PII:PERSON]彤, [PII:PERSON]杰, [PII:PERSO…`
- formats/fullwidth_space_separated: `刁沄妘`  → 輸出:`刁沄妘　龎芫綺　[PII:PERSON]彤　[PII:PERSON]杰　[PII:PERSON]伃　[PII:PERSON]`
- formats/fullwidth_space_separated: `龎芫綺`  → 輸出:`刁沄妘　龎芫綺　[PII:PERSON]彤　[PII:PERSON]杰　[PII:PERSON]伃　[PII:PERSON]`
- formats/html_spans: `刁沄妘`  → 輸出:`<span>刁沄妘</span><span>龎芫綺</span><span>[PII:PERSON]彤</span><span>[PII:PERSON]杰</span><span>…`
- formats/html_spans: `龎芫綺`  → 輸出:`<span>刁沄妘</span><span>龎芫綺</span><span>[PII:PERSON]彤</span><span>[PII:PERSON]杰</span><span>…`
- formats/html_table: `刁沄妘`  → 輸出:`<table><tr><th>姓名</th><th>科別</th></tr><tr><td>刁沄妘</td><td>重內1</td></tr><tr><td>龎芫綺</td><td…`
- formats/html_table: `龎芫綺`  → 輸出:`<table><tr><th>姓名</th><th>科別</th></tr><tr><td>刁沄妘</td><td>重內1</td></tr><tr><td>龎芫綺</td><td…`
- formats/ini_toml: `刁沄妘`  → 輸出:`[doc1]⏎name = 刁沄妘⏎id = 2355⏎[doc2]⏎name = 龎芫綺⏎id = 5730⏎[doc3]⏎name = [PII:PERSON]彤⏎id = 8…`
- formats/ini_toml: `龎芫綺`  → 輸出:`[doc1]⏎name = 刁沄妘⏎id = 2355⏎[doc2]⏎name = 龎芫綺⏎id = 5730⏎[doc3]⏎name = [PII:PERSON]彤⏎id = 8…`
- formats/json_array: `刁沄妘`  → 輸出:`["刁沄妘","龎芫綺","[PII:PERSON]彤","[PII:PERSON]杰","[PII:PERSON]伃","[PII:PERSON]"]`
- formats/json_array: `龎芫綺`  → 輸出:`["刁沄妘","龎芫綺","[PII:PERSON]彤","[PII:PERSON]杰","[PII:PERSON]伃","[PII:PERSON]"]`
- formats/json_dict: `刁沄妘`  → 輸出:`{"a":"刁沄妘","b":"龎芫綺","c":"[PII:PERSON]彤","d":"[PII:PERSON]杰","e":"[PII:PERSON]伃","f":"[PII…`
- formats/json_dict: `龎芫綺`  → 輸出:`{"a":"刁沄妘","b":"龎芫綺","c":"[PII:PERSON]彤","d":"[PII:PERSON]杰","e":"[PII:PERSON]伃","f":"[PII…`
- formats/json_in_json_string: `刁沄妘`  → 輸出:`{"output":"{\"names\":[\"刁沄妘\",\"龎芫綺\",\"[PII:PERSON]彤\",\"[PII:PERSON]杰\",\"[PII:PERSON]伃…`
- formats/json_in_json_string: `龎芫綺`  → 輸出:`{"output":"{\"names\":[\"刁沄妘\",\"龎芫綺\",\"[PII:PERSON]彤\",\"[PII:PERSON]杰\",\"[PII:PERSON]伃…`
- formats/json_nested: `刁沄妘`  → 輸出:`{"rows":[{"name":"刁沄妘","id":1},{"name":"龎芫綺","id":2},{"name":"[PII:PERSON]彤","id":3},{"nam…`
- formats/json_nested: `龎芫綺`  → 輸出:`{"rows":[{"name":"刁沄妘","id":1},{"name":"龎芫綺","id":2},{"name":"[PII:PERSON]彤","id":3},{"nam…`
- formats/log_line: `刁沄妘`  → 輸出:`2026-09-14 10:00:01 INFO user=刁沄妘 action=login⏎2026-09-14 10:00:05 INFO user=龎芫綺 action=vi…`
- formats/log_line: `龎芫綺`  → 輸出:`2026-09-14 10:00:01 INFO user=刁沄妘 action=login⏎2026-09-14 10:00:05 INFO user=龎芫綺 action=vi…`
- formats/markdown_bold_names: `刁沄妘`  → 輸出:`**刁沄妘** 重內1, **龎芫綺** 重內1, **[PII:PERSON]彤** 重內1, **[PII:PERSON]杰** 重內1, **[PII:PERSON]伃** …`
- formats/markdown_bold_names: `龎芫綺`  → 輸出:`**刁沄妘** 重內1, **龎芫綺** 重內1, **[PII:PERSON]彤** 重內1, **[PII:PERSON]杰** 重內1, **[PII:PERSON]伃** …`
- formats/markdown_bullet: `刁沄妘`  → 輸出:`醫師名單:⏎- 刁沄妘(重內1, 2355)⏎- 龎芫綺(重內1, 5730)⏎- [PII:PERSON]彤(重內1, 8075)⏎- [PII:PERSON]杰(重內1, 83…`
- formats/markdown_bullet: `龎芫綺`  → 輸出:`醫師名單:⏎- 刁沄妘(重內1, 2355)⏎- 龎芫綺(重內1, 5730)⏎- [PII:PERSON]彤(重內1, 8075)⏎- [PII:PERSON]杰(重內1, 83…`
- formats/markdown_numbered: `刁沄妘`  → 輸出:`1. 刁沄妘⏎2. 龎芫綺⏎3. [PII:PERSON]彤⏎4. [PII:PERSON]杰⏎5. [PII:PERSON]伃⏎6. [PII:PERSON]`
- formats/markdown_numbered: `龎芫綺`  → 輸出:`1. 刁沄妘⏎2. 龎芫綺⏎3. [PII:PERSON]彤⏎4. [PII:PERSON]杰⏎5. [PII:PERSON]伃⏎6. [PII:PERSON]`
- formats/markdown_table: `刁沄妘`  → 輸出:`| 職類 | 科別 | 姓名 | 員編 | 職稱 |⏎|-----|-----|------|-----|------|⏎| 西醫師 | 重內1 | 刁沄妘 | 2355 | 科主…`
- formats/markdown_table: `龎芫綺`  → 輸出:`| 職類 | 科別 | 姓名 | 員編 | 職稱 |⏎|-----|-----|------|-----|------|⏎| 西醫師 | 重內1 | 刁沄妘 | 2355 | 科主…`
- formats/multi_space_aligned: `刁沄妘`  → 輸出:`西醫師   重症部   重內1   刁沄妘    2355  科主任⏎西醫師   重症部   重內1   龎芫綺    5730  主治醫師⏎西醫師   重症部   重內1   […`
- formats/multi_space_aligned: `龎芫綺`  → 輸出:`西醫師   重症部   重內1   刁沄妘    2355  科主任⏎西醫師   重症部   重內1   龎芫綺    5730  主治醫師⏎西醫師   重症部   重內1   […`
- formats/natural_enumeration: `刁沄妘`  → 輸出:`本科現有六位主治醫師,分別為刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃及[PII:PERSON]。`
- formats/natural_enumeration: `龎芫綺`  → 輸出:`本科現有六位主治醫師,分別為刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃及[PII:PERSON]。`
- formats/natural_with_dunhao: `刁沄妘`  → 輸出:`醫師有:刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃、[PII:PERSON]等六位。`
- formats/natural_with_dunhao: `龎芫綺`  → 輸出:`醫師有:刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃、[PII:PERSON]等六位。`
- formats/pipe_table_clean: `刁沄妘`  → 輸出:`西醫師|重症部|重內1|刁沄妘|2355|科主任⏎西醫師|重症部|重內1|龎芫綺|5730|主治醫師⏎西醫師|重症部|重內1|[PII:PERSON]彤|8075|主治醫師⏎西醫師…`
- formats/pipe_table_clean: `龎芫綺`  → 輸出:`西醫師|重症部|重內1|刁沄妘|2355|科主任⏎西醫師|重症部|重內1|龎芫綺|5730|主治醫師⏎西醫師|重症部|重內1|[PII:PERSON]彤|8075|主治醫師⏎西醫師…`
- formats/pipe_table_with_row_numbers_and_dates: `刁沄妘`  → 輸出:`2 西醫師 | 重症部 | 重內1 | 刁沄妘 | 2355 | 科主任 | 115/01/01 | 117/12/31⏎3 西醫師 | 重症部 | 重內1 | 龎芫綺 | 573…`
- formats/pipe_table_with_row_numbers_and_dates: `龎芫綺`  → 輸出:`2 西醫師 | 重症部 | 重內1 | 刁沄妘 | 2355 | 科主任 | 115/01/01 | 117/12/31⏎3 西醫師 | 重症部 | 重內1 | 龎芫綺 | 573…`
- formats/python_repr_list: `刁沄妘`  → 輸出:`['刁沄妘', '龎芫綺', '[PII:PERSON]彤', '[PII:PERSON]杰', '[PII:PERSON]伃', '[PII:PERSON]']`
- formats/python_repr_list: `龎芫綺`  → 輸出:`['刁沄妘', '龎芫綺', '[PII:PERSON]彤', '[PII:PERSON]杰', '[PII:PERSON]伃', '[PII:PERSON]']`
- formats/python_repr_nested: `刁沄妘`  → 輸出:`{'rows': [{'name': '刁沄妘'}, {'name': '龎芫綺'}, {'name': '[PII:PERSON]彤'}, {'name': '[PII:PERS…`
- formats/python_repr_nested: `龎芫綺`  → 輸出:`{'rows': [{'name': '刁沄妘'}, {'name': '龎芫綺'}, {'name': '[PII:PERSON]彤'}, {'name': '[PII:PERS…`
- formats/semicolon_separated: `刁沄妘`  → 輸出:`西醫師;重症部;重內1;刁沄妘;2355;科主任⏎西醫師;重症部;重內1;龎芫綺;5730;主治醫師⏎西醫師;重症部;重內1;[PII:PERSON]彤;8075;主治醫師⏎西醫師…`
- longtext/synthetic_128000: 1639 個,例如 `['000073795067', '000019108445', '51541742', '51917463', '方妘智', '61620951']`
- longtext/synthetic_32000: 372 個,例如 `['000003455757', '李宥宇', '79493103', '32785312', '59926583', '10310235']`
- longtext/synthetic_4000: 42 個,例如 `['汪承彤', '000096098543', '000084838956', '藍紜雯', '19361510', '24867974']`

### 部分殘留(人名頭尾兩字):629
(短 case 只列前 60 筆,共 132)
- formats/ascii_box_table: `郭曉彤`  → 輸出:`┌────────┬────────┐⏎│ 刁沄妘 │ 2355   │⏎│ 龎芫綺 │ 5730   │⏎│ [PII:PERSON]彤 │ 8075   │⏎│ [PII:PE…`
- formats/ascii_box_table: `曾智杰`  → 輸出:`┌────────┬────────┐⏎│ 刁沄妘 │ 2355   │⏎│ 龎芫綺 │ 5730   │⏎│ [PII:PERSON]彤 │ 8075   │⏎│ [PII:PE…`
- formats/ascii_box_table: `林晏伃`  → 輸出:`┌────────┬────────┐⏎│ 刁沄妘 │ 2355   │⏎│ 龎芫綺 │ 5730   │⏎│ [PII:PERSON]彤 │ 8075   │⏎│ [PII:PE…`
- formats/chat_log: `郭曉彤`  → 輸出:`[10:00] 刁沄妘: 早安⏎[10:01] 龎芫綺: 早⏎[10:02] [PII:PERSON]彤: morning⏎[10:03] [PII:PERSON]杰: 都到了嗎⏎…`
- formats/chat_log: `曾智杰`  → 輸出:`[10:00] 刁沄妘: 早安⏎[10:01] 龎芫綺: 早⏎[10:02] [PII:PERSON]彤: morning⏎[10:03] [PII:PERSON]杰: 都到了嗎⏎…`
- formats/chat_log: `林晏伃`  → 輸出:`[10:00] 刁沄妘: 早安⏎[10:01] 龎芫綺: 早⏎[10:02] [PII:PERSON]彤: morning⏎[10:03] [PII:PERSON]杰: 都到了嗎⏎…`
- formats/csv_multi_row: `郭曉彤`  → 輸出:`西醫師,重症部,重內1,刁沄妘,2355,科主任⏎西醫師,重症部,重內1,龎芫綺,5730,主治醫師⏎西醫師,重症部,重內1,[PII:PERSON]彤,8075,主治醫師⏎西醫師…`
- formats/csv_multi_row: `曾智杰`  → 輸出:`西醫師,重症部,重內1,刁沄妘,2355,科主任⏎西醫師,重症部,重內1,龎芫綺,5730,主治醫師⏎西醫師,重症部,重內1,[PII:PERSON]彤,8075,主治醫師⏎西醫師…`
- formats/csv_multi_row: `林晏伃`  → 輸出:`西醫師,重症部,重內1,刁沄妘,2355,科主任⏎西醫師,重症部,重內1,龎芫綺,5730,主治醫師⏎西醫師,重症部,重內1,[PII:PERSON]彤,8075,主治醫師⏎西醫師…`
- formats/email_header: `郭曉彤`  → 輸出:`From: 刁沄妘 <[PII:EMAIL]>⏎To: 龎芫綺 <[PII:EMAIL]>⏎Cc: [PII:PERSON]彤, [PII:PERSON]杰, [PII:PERSO…`
- formats/email_header: `曾智杰`  → 輸出:`From: 刁沄妘 <[PII:EMAIL]>⏎To: 龎芫綺 <[PII:EMAIL]>⏎Cc: [PII:PERSON]彤, [PII:PERSON]杰, [PII:PERSO…`
- formats/email_header: `林晏伃`  → 輸出:`From: 刁沄妘 <[PII:EMAIL]>⏎To: 龎芫綺 <[PII:EMAIL]>⏎Cc: [PII:PERSON]彤, [PII:PERSON]杰, [PII:PERSO…`
- formats/fullwidth_space_separated: `郭曉彤`  → 輸出:`刁沄妘　龎芫綺　[PII:PERSON]彤　[PII:PERSON]杰　[PII:PERSON]伃　[PII:PERSON]`
- formats/fullwidth_space_separated: `曾智杰`  → 輸出:`刁沄妘　龎芫綺　[PII:PERSON]彤　[PII:PERSON]杰　[PII:PERSON]伃　[PII:PERSON]`
- formats/fullwidth_space_separated: `林晏伃`  → 輸出:`刁沄妘　龎芫綺　[PII:PERSON]彤　[PII:PERSON]杰　[PII:PERSON]伃　[PII:PERSON]`
- formats/html_spans: `郭曉彤`  → 輸出:`<span>刁沄妘</span><span>龎芫綺</span><span>[PII:PERSON]彤</span><span>[PII:PERSON]杰</span><span>…`
- formats/html_spans: `曾智杰`  → 輸出:`<span>刁沄妘</span><span>龎芫綺</span><span>[PII:PERSON]彤</span><span>[PII:PERSON]杰</span><span>…`
- formats/html_spans: `林晏伃`  → 輸出:`<span>刁沄妘</span><span>龎芫綺</span><span>[PII:PERSON]彤</span><span>[PII:PERSON]杰</span><span>…`
- formats/html_table: `郭曉彤`  → 輸出:`<table><tr><th>姓名</th><th>科別</th></tr><tr><td>刁沄妘</td><td>重內1</td></tr><tr><td>龎芫綺</td><td…`
- formats/html_table: `曾智杰`  → 輸出:`<table><tr><th>姓名</th><th>科別</th></tr><tr><td>刁沄妘</td><td>重內1</td></tr><tr><td>龎芫綺</td><td…`
- formats/html_table: `林晏伃`  → 輸出:`<table><tr><th>姓名</th><th>科別</th></tr><tr><td>刁沄妘</td><td>重內1</td></tr><tr><td>龎芫綺</td><td…`
- formats/ini_toml: `郭曉彤`  → 輸出:`[doc1]⏎name = 刁沄妘⏎id = 2355⏎[doc2]⏎name = 龎芫綺⏎id = 5730⏎[doc3]⏎name = [PII:PERSON]彤⏎id = 8…`
- formats/ini_toml: `曾智杰`  → 輸出:`[doc1]⏎name = 刁沄妘⏎id = 2355⏎[doc2]⏎name = 龎芫綺⏎id = 5730⏎[doc3]⏎name = [PII:PERSON]彤⏎id = 8…`
- formats/ini_toml: `林晏伃`  → 輸出:`[doc1]⏎name = 刁沄妘⏎id = 2355⏎[doc2]⏎name = 龎芫綺⏎id = 5730⏎[doc3]⏎name = [PII:PERSON]彤⏎id = 8…`
- formats/json_array: `郭曉彤`  → 輸出:`["刁沄妘","龎芫綺","[PII:PERSON]彤","[PII:PERSON]杰","[PII:PERSON]伃","[PII:PERSON]"]`
- formats/json_array: `曾智杰`  → 輸出:`["刁沄妘","龎芫綺","[PII:PERSON]彤","[PII:PERSON]杰","[PII:PERSON]伃","[PII:PERSON]"]`
- formats/json_array: `林晏伃`  → 輸出:`["刁沄妘","龎芫綺","[PII:PERSON]彤","[PII:PERSON]杰","[PII:PERSON]伃","[PII:PERSON]"]`
- formats/json_dict: `郭曉彤`  → 輸出:`{"a":"刁沄妘","b":"龎芫綺","c":"[PII:PERSON]彤","d":"[PII:PERSON]杰","e":"[PII:PERSON]伃","f":"[PII…`
- formats/json_dict: `曾智杰`  → 輸出:`{"a":"刁沄妘","b":"龎芫綺","c":"[PII:PERSON]彤","d":"[PII:PERSON]杰","e":"[PII:PERSON]伃","f":"[PII…`
- formats/json_dict: `林晏伃`  → 輸出:`{"a":"刁沄妘","b":"龎芫綺","c":"[PII:PERSON]彤","d":"[PII:PERSON]杰","e":"[PII:PERSON]伃","f":"[PII…`
- formats/json_in_json_string: `郭曉彤`  → 輸出:`{"output":"{\"names\":[\"刁沄妘\",\"龎芫綺\",\"[PII:PERSON]彤\",\"[PII:PERSON]杰\",\"[PII:PERSON]伃…`
- formats/json_in_json_string: `曾智杰`  → 輸出:`{"output":"{\"names\":[\"刁沄妘\",\"龎芫綺\",\"[PII:PERSON]彤\",\"[PII:PERSON]杰\",\"[PII:PERSON]伃…`
- formats/json_in_json_string: `林晏伃`  → 輸出:`{"output":"{\"names\":[\"刁沄妘\",\"龎芫綺\",\"[PII:PERSON]彤\",\"[PII:PERSON]杰\",\"[PII:PERSON]伃…`
- formats/json_nested: `郭曉彤`  → 輸出:`{"rows":[{"name":"刁沄妘","id":1},{"name":"龎芫綺","id":2},{"name":"[PII:PERSON]彤","id":3},{"nam…`
- formats/json_nested: `曾智杰`  → 輸出:`{"rows":[{"name":"刁沄妘","id":1},{"name":"龎芫綺","id":2},{"name":"[PII:PERSON]彤","id":3},{"nam…`
- formats/json_nested: `林晏伃`  → 輸出:`{"rows":[{"name":"刁沄妘","id":1},{"name":"龎芫綺","id":2},{"name":"[PII:PERSON]彤","id":3},{"nam…`
- formats/log_line: `郭曉彤`  → 輸出:`2026-09-14 10:00:01 INFO user=刁沄妘 action=login⏎2026-09-14 10:00:05 INFO user=龎芫綺 action=vi…`
- formats/log_line: `曾智杰`  → 輸出:`2026-09-14 10:00:01 INFO user=刁沄妘 action=login⏎2026-09-14 10:00:05 INFO user=龎芫綺 action=vi…`
- formats/log_line: `林晏伃`  → 輸出:`2026-09-14 10:00:01 INFO user=刁沄妘 action=login⏎2026-09-14 10:00:05 INFO user=龎芫綺 action=vi…`
- formats/markdown_bold_names: `郭曉彤`  → 輸出:`**刁沄妘** 重內1, **龎芫綺** 重內1, **[PII:PERSON]彤** 重內1, **[PII:PERSON]杰** 重內1, **[PII:PERSON]伃** …`
- formats/markdown_bold_names: `曾智杰`  → 輸出:`**刁沄妘** 重內1, **龎芫綺** 重內1, **[PII:PERSON]彤** 重內1, **[PII:PERSON]杰** 重內1, **[PII:PERSON]伃** …`
- formats/markdown_bold_names: `林晏伃`  → 輸出:`**刁沄妘** 重內1, **龎芫綺** 重內1, **[PII:PERSON]彤** 重內1, **[PII:PERSON]杰** 重內1, **[PII:PERSON]伃** …`
- formats/markdown_bullet: `郭曉彤`  → 輸出:`醫師名單:⏎- 刁沄妘(重內1, 2355)⏎- 龎芫綺(重內1, 5730)⏎- [PII:PERSON]彤(重內1, 8075)⏎- [PII:PERSON]杰(重內1, 83…`
- formats/markdown_bullet: `曾智杰`  → 輸出:`醫師名單:⏎- 刁沄妘(重內1, 2355)⏎- 龎芫綺(重內1, 5730)⏎- [PII:PERSON]彤(重內1, 8075)⏎- [PII:PERSON]杰(重內1, 83…`
- formats/markdown_bullet: `林晏伃`  → 輸出:`醫師名單:⏎- 刁沄妘(重內1, 2355)⏎- 龎芫綺(重內1, 5730)⏎- [PII:PERSON]彤(重內1, 8075)⏎- [PII:PERSON]杰(重內1, 83…`
- formats/markdown_numbered: `郭曉彤`  → 輸出:`1. 刁沄妘⏎2. 龎芫綺⏎3. [PII:PERSON]彤⏎4. [PII:PERSON]杰⏎5. [PII:PERSON]伃⏎6. [PII:PERSON]`
- formats/markdown_numbered: `曾智杰`  → 輸出:`1. 刁沄妘⏎2. 龎芫綺⏎3. [PII:PERSON]彤⏎4. [PII:PERSON]杰⏎5. [PII:PERSON]伃⏎6. [PII:PERSON]`
- formats/markdown_numbered: `林晏伃`  → 輸出:`1. 刁沄妘⏎2. 龎芫綺⏎3. [PII:PERSON]彤⏎4. [PII:PERSON]杰⏎5. [PII:PERSON]伃⏎6. [PII:PERSON]`
- formats/markdown_table: `郭曉彤`  → 輸出:`| 職類 | 科別 | 姓名 | 員編 | 職稱 |⏎|-----|-----|------|-----|------|⏎| 西醫師 | 重內1 | 刁沄妘 | 2355 | 科主…`
- formats/markdown_table: `曾智杰`  → 輸出:`| 職類 | 科別 | 姓名 | 員編 | 職稱 |⏎|-----|-----|------|-----|------|⏎| 西醫師 | 重內1 | 刁沄妘 | 2355 | 科主…`
- formats/markdown_table: `林晏伃`  → 輸出:`| 職類 | 科別 | 姓名 | 員編 | 職稱 |⏎|-----|-----|------|-----|------|⏎| 西醫師 | 重內1 | 刁沄妘 | 2355 | 科主…`
- formats/multi_space_aligned: `郭曉彤`  → 輸出:`西醫師   重症部   重內1   刁沄妘    2355  科主任⏎西醫師   重症部   重內1   龎芫綺    5730  主治醫師⏎西醫師   重症部   重內1   […`
- formats/multi_space_aligned: `曾智杰`  → 輸出:`西醫師   重症部   重內1   刁沄妘    2355  科主任⏎西醫師   重症部   重內1   龎芫綺    5730  主治醫師⏎西醫師   重症部   重內1   […`
- formats/multi_space_aligned: `林晏伃`  → 輸出:`西醫師   重症部   重內1   刁沄妘    2355  科主任⏎西醫師   重症部   重內1   龎芫綺    5730  主治醫師⏎西醫師   重症部   重內1   […`
- formats/natural_enumeration: `郭曉彤`  → 輸出:`本科現有六位主治醫師,分別為刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃及[PII:PERSON]。`
- formats/natural_enumeration: `曾智杰`  → 輸出:`本科現有六位主治醫師,分別為刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃及[PII:PERSON]。`
- formats/natural_enumeration: `林晏伃`  → 輸出:`本科現有六位主治醫師,分別為刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃及[PII:PERSON]。`
- formats/natural_with_dunhao: `郭曉彤`  → 輸出:`醫師有:刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃、[PII:PERSON]等六位。`
- formats/natural_with_dunhao: `曾智杰`  → 輸出:`醫師有:刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃、[PII:PERSON]等六位。`
- formats/natural_with_dunhao: `林晏伃`  → 輸出:`醫師有:刁沄妘、龎芫綺、[PII:PERSON]彤、[PII:PERSON]杰、[PII:PERSON]伃、[PII:PERSON]等六位。`
- longtext/synthetic_128000: 384 個,例如 `['盧翰彤', '馬智嫚', '侯晴紜', '戴淑伃', '古怡彤', '阮庭辰']`
- longtext/synthetic_32000: 102 個,例如 `['簡宏妍', '范麗妍', '田佳杰', '蔡庭冠', '紀雅冠', '蘇羽彤']`
- longtext/synthetic_4000: 11 個,例如 `['曹妤冠', '徐翰承', '丁品妍', '曹宜冠', '曹柏芫', '鄭瑋芫']`

### 誤遮(該保留卻消失):18
- addresses/city_only: `高雄市`  → 輸出:`病人從[PII:LOC]北上就醫。`
- addresses/institution_中山區公所: `中山區公所`  → 輸出:`病人自[PII:LOC]公所轉診至本院。`
- addresses/landmark: `中山路`  → 輸出:`掛號櫃台在一樓大廳,靠近[PII:LOC]側門。`
- addresses/road_only: `中山路`  → 輸出:`沿著[PII:LOC]往北就會看到醫院。`
- adversarial/eponymous_diseases: `馬凡氏症候群`  → 輸出:`鑑別診斷包含川崎病、阿茲海默症、帕金森氏症、庫欣氏症候群、[PII:PERSON]氏症候群、杜興氏肌肉失養症。`
- adversarial/eponymous_diseases: `[任何遮蔽] PERSON×1`  → 輸出:`鑑別診斷包含川崎病、阿茲海默症、帕金森氏症、庫欣氏症候群、[PII:PERSON]氏症候群、杜興氏肌肉失養症。`
- adversarial/hospital_names: `中山區公所`  → 輸出:`台中榮民總醫院、中山醫學大學附設醫院、臺大醫院、中國醫藥大學附設醫院、[PII:LOC]公所、台中市政府衛生局、彰化基督教醫院皆為本區合作醫院。`
- adversarial/hospital_names: `[任何遮蔽] LOC×1`  → 輸出:`台中榮民總醫院、中山醫學大學附設醫院、臺大醫院、中國醫藥大學附設醫院、[PII:LOC]公所、台中市政府衛生局、彰化基督教醫院皆為本區合作醫院。`
- adversarial/place_like_words: `中正紀念堂`  → 輸出:`中正[PII:PERSON]、大同電鍋、台中市政府、中山[PII:LOC]、民生社區。`
- adversarial/place_like_words: `中山高速公路`  → 輸出:`中正[PII:PERSON]、大同電鍋、台中市政府、中山[PII:LOC]、民生社區。`
- adversarial/place_like_words: `[任何遮蔽] PERSON×1, LOC×1`  → 輸出:`中正[PII:PERSON]、大同電鍋、台中市政府、中山[PII:LOC]、民生社區。`
- adversarial/surname_chars_in_words: `張力性氣胸`  → 輸出:`陳舊性骨折、林口長庚、黃疸、[PII:PERSON]性氣胸、吳郭魚、劉海。`
- ids/bed_number: `12A-03`  → 輸出:`床號 [PII:LOC],房號 305。`
- ids/nhi_drug_code: `BC23456100`  → 輸出:`健保碼 [PII:ID],批號 A1234567`
- names_foreign/english_in_table: `Ward`  → 輸出:`| Name | [PII:PERSON] |⏎|---|---|⏎| [PII:PERSON] | 12A |⏎| [PII:PERSON] | 12B |`
- scenarios/admission_note: `Murphy's sign`  → 輸出:`入院病歷⏎病人:刁沄妘  性別:女  年齡:67⏎病歷號:[PII:ID]  身分證:[PII:ID]  健保卡號:000012345678⏎聯絡人:[PII:PERSON]杰(兒…`
- scenarios/social_work: `中山區公所`  → 輸出:`社工訪視紀錄⏎個案:[PII:PERSON](身分證 [PII:ID])獨居,主要照顧者為女兒龎芫綺(電話 [PII:PHONE],email [PII:EMAIL])。⏎戶籍地址…`
- structures/key_value_record: `5A-12`  → 輸出:`姓名:[PII:PERSON]紜⏎病歷號:[PII:ID]⏎身分證:[PII:ID]⏎性別:女⏎出生:1975-03-02⏎電話:[PII:PHONE]⏎地址:[PII:LOC]⏎…`


## 兩套都漏(共同盲區):2

- encoding/zero_width_in_nid: `A1234​56789`
- ids/mrn_repeated_bare: `10234567`

## 觀察項(政策未定,不計分):值 → 各系統有沒有遮

| case | 值 | mine | v2 | 備註 |
|---|---|---|---|---|
| addresses/district_only | `台中市西屯區` | 遮 | 遮 | 宏觀地名,報告說我方偏保守 |
| addresses/fullwidth_digits | `台中市西屯區台灣大道四段１６５０號` | 遮 | 遮 |  |
| addresses/no_number | `台中市西屯區台灣大道四段` | 遮 | 遮 |  |
| addresses/with_postal | `40705` | 遮 | 遮 |  |
| adversarial/long_numbers_not_id | `88001234567` | 留 | 留 |  |
| adversarial/name_like_common_words | `王安石` | 遮 | 遮 | 歷史人物是否算個資由政策決定 |
| adversarial/name_like_common_words | `張飛` | 遮 | 遮 | 歷史人物是否算個資由政策決定 |
| adversarial/name_like_common_words | `關羽` | 遮 | 遮 | 歷史人物是否算個資由政策決定 |
| adversarial/surname_chars_in_words | `林口長庚` | 留 | 留 | 姓氏字開頭的醫學/一般名詞 |
| contacts/email_generic_dept | `service@hospital.org.tw` | 遮 | 遮 | 單位信箱是否該遮 |
| contacts/email_malformed | `mei.lin@example` | 遮 | 留 |  |
| contacts/email_obfuscated | `mei.lin (at) example (dot) com` | 遮 | 留 |  |
| contacts/hospital_switchboard | `04-23592525` | 遮 | 遮 | 醫院總機是否該遮為政策問題 |
| contacts/landline_fenji | `2610` | 遮 | 遮 | 分機是否一併遮為政策問題 |
| contacts/landline_with_ext | `2610` | 遮 | 遮 | 分機是否一併遮為政策問題 |
| contacts/line_id | `meilin_0912` | 遮 | 留 |  |
| contacts/url_with_name | `wang-xiao-ming` | 遮 | 留 |  |
| encoding/markdown_escaped | `王\_小明` | 遮 | 留 |  |
| encoding/markdown_escaped | `0912\-345\-678` | 遮 | 留 |  |
| encoding/name_partially_redacted | `王○明` | 遮 | 留 | 已手動部分遮蔽的名字 |
| encoding/name_partially_redacted | `陳O華` | 遮 | 留 | 已手動部分遮蔽的名字 |
| encoding/name_spaced | `王 小 明` | 遮 | 留 |  |
| encoding/name_with_middle_dot | `王·小明` | 遮 | 留 |  |
| encoding/rtl_mark | `王小明` | 遮 | 遮 | RTL override 字元包住 |
| formats/base64_payload | `eyJuYW1lcyI6IFsi5YiB5rKE5aaYIiwgIum+juiK…` | 遮 | 留 | base64,兩套皆抓不到 |
| formats/percent_encoded | `%E5%88%81%E6%B2%84%E5%A6%98` | 遮 | 留 | URL 百分比編碼 |
| formats/percent_encoded | `%E9%BE%8E%E8%8A%AB%E7%B6%BA` | 遮 | 留 | URL 百分比編碼 |
| ids/dates | `1980/05/12` | 留 | 留 | 生日是否遮為政策問題 |
| ids/mrn_bare_prose | `10234567` | 遮 | 留 | 裸號碼無關鍵字,報告已知我方刻意不抓 |
| ids/mrn_long_12 | `123456789012` | 遮 | 遮 | 超出常見長度 |
| ids/nhi_drug_code | `A1234567` | 留 | 留 | 批號長得像身分證但少一碼 |
| ids/nid_invalid_checksum | `K276594273` | 遮 | 遮 | 檢核碼錯誤 |
| ids/order_number | `88` | 留 | 留 |  |
| ids/phone_like_not_phone | `0987654321` | 遮 | 遮 | 像手機的數字但不是 |
| names_foreign/allcaps_passport_style | `1980-05-12` | 遮 | 留 |  |
| names_foreign/initials | `J. Chen` | 遮 | 遮 |  |
| names_foreign/initials | `M. Wang` | 遮 | 遮 |  |
| names_foreign/romanized_lowercase | `lin mei-ling` | 遮 | 留 | 全小寫拼音 |
| names_zh/nickname | `小明` | 遮 | 留 |  |
| names_zh/nickname | `小華` | 遮 | 留 |  |
| names_zh/surname_honorific_only | `王先生` | 遮 | 留 |  |
| names_zh/surname_title_only | `陳醫師` | 遮 | 留 | 只有姓+職稱,政策未定 |
| names_zh/surname_title_only | `林護理師` | 遮 | 留 | 只有姓+職稱,政策未定 |
| scenarios/admission_note | `67` | 留 | 留 |  |
| scenarios/discharge_summary | `2610` | 留 | 遮 |  |
| structures/key_value_record | `1975-03-02` | 留 | 留 |  |

## 已知極限(不計分)

- `mine` formats/base64_payload: base64,兩套皆抓不到;觀察 {'eyJuYW1lcyI6IFsi5YiB5rKE5aaYIiwgIum+juiKq+e2uiJdfQ==': True}
- `v2` formats/base64_payload: base64,兩套皆抓不到;觀察 {'eyJuYW1lcyI6IFsi5YiB5rKE5aaYIiwgIum+juiKq+e2uiJdfQ==': False}
- `mine` formats/percent_encoded: URL 百分比編碼;觀察 {'%E5%88%81%E6%B2%84%E5%A6%98': True, '%E9%BE%8E%E8%8A%AB%E7%B6%BA': True}
- `v2` formats/percent_encoded: URL 百分比編碼;觀察 {'%E5%88%81%E6%B2%84%E5%A6%98': False, '%E9%BE%8E%E8%8A%AB%E7%B6%BA': False}

## 超長文

| case | 系統 | 個資值 | 漏遮 | 誤遮 | 秒 |
|---|---|---|---|---|---|
| longtext/synthetic_128000 | mine | 6420 | 0 | 0 | 25.6 |
| longtext/synthetic_128000 | v2 | 6420 | 1639 | 0 | 3.5 |
| longtext/synthetic_32000 | mine | 1602 | 0 | 0 | 7.8 |
| longtext/synthetic_32000 | v2 | 1602 | 372 | 0 | 0.7 |
| longtext/synthetic_4000 | mine | 197 | 0 | 0 | 3.4 |
| longtext/synthetic_4000 | v2 | 197 | 42 | 0 | 0.3 |

漏遮依型別(依 case 期望型別統計):
- v2 longtext/synthetic_128000: 前 15 個 `['000073795067', '000019108445', '51541742', '51917463', '方妘智', '61620951', '45125394', '94942698', '38718890', '柯伃宏', '84695303', '郭承婕', '97184297', '83736455', '88422958']`
- v2 longtext/synthetic_32000: 前 15 個 `['000003455757', '李宥宇', '79493103', '32785312', '59926583', '10310235', '25841433', '馬宥伃', '75968889', '塗翰涵', '000019086734', '蔣妘涵', '65458234', '32757106', '22506128']`
- v2 longtext/synthetic_4000: 前 15 個 `['汪承彤', '000096098543', '000084838956', '藍紜雯', '19361510', '24867974', '55075980', '68187197', '邱承芬', '91037987', '74812322', '徐承彤', '羅冠怡', '000040236926', '78691884']`

## 各系統標籤用量

- mine: P_NAME 3232, PHONE 1775, PID 1610, ADDR 1498, NID 867, EMAIL 312, OTHER_IDENTIFYING 260, HID 178, REL 142
- v2: PERSON 2459, PHONE 1767, ID 1190, LOC 905, EMAIL 309
