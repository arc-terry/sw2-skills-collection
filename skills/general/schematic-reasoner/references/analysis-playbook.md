# Analysis Playbook

這份 playbook 把 BGW720 實戰裡收斂出來、但又不只侷限於 DTS 的電路分析規則整理起來。

## 1. PDF 能力不是「看得到字」就夠

skill 至少要能處理：

- 有文字層 PDF
- OCR fallback
- 同一張圖上 connector / tag / refdes 分散在不同區塊
- 多張 PDF 間的跨板延續

所以 skill 的第一步不應只是抽全文，而是抽：

- page index
- tag index
- refdes index
- connector pinout index

## 2. `canonical_signal` 必須是一級資料結構

例如：

- `SDA`
- `R123`
- `SDA_0`

如果 `SDA` 經過 series resistor 變成 `SDA_0`，
那這比較像是同一條 bus segment 的 rename，而不是全新功能信號。

建議 skill 內部至少保存：

- `canonical_signal`
- `aliases`
- `bridge_type`
- `bridge_reason`

常見 bridge：

- `offpage`
- `connector`
- `series_resistor`
- `zero_ohm`
- `level_shifter`
- `net_rename`

## 3. Cross-PDF tracing 要先靠 connector pin continuity

多板設計中，真正穩定的延續證據通常不是名字，而是：

- connector name
- pin number
- pin function

就算 mainboard 叫 `J5`、daughter 叫 `J1`，
只要 pin 對 pin 的映射被證成，tracing 就應該繼續。

## 4. IC 型號解析要分層

建議解析優先級：

1. schematic/BOM 明確 part number
2. silkscreen / package marking
3. 本地 datasheet
4. public web spec / datasheet

而且要明確分開：

- **device identity**：這顆是不是 `TCA9555` / `PCA9555` family
- **board wiring**：它接在哪條 bus、哪個 pin 真的有用

前者可用 web/public datasheet 補，後者仍必須回 schematic。

另外，若是從 public web datasheet / product page 補 identity，
至少還要回頭核對：

- package / package code
- pin count
- visible pin functions / pinout
- BOM 或絲印是否支持這個封裝候選

若這些對不上，就只能停在候選，不應標成 `VERIFIED`。

## 5. 電氣語義要從外圍電路推，不是只看命名

skill 應能讀出：

- pull-up / pull-down
- idle level
- active-high / active-low
- open-drain
- inversion stage
- current sink / current source
- lane swap / pair swap / polarity swap

### Button

至少應判讀：

- 按下時是拉高還是拉低
- default idle level
- 外部 pull-up/down 是否存在
- 是否有 RC / debounce

### LED

至少應判讀：

- LED 是 source drive 還是 sink drive
- active-high / active-low
- 是否經過 transistor / expander / shift register
- `line-name` / board behavior 是否需要另外問人

### Swap / high-speed path behavior

至少應判讀：

- 差分對或 lane 的預期對應是什麼
- 實際 tracing 到的對應是什麼
- 是 `lane swap`、`pair swap` 還是 `polarity swap`
- swap 發生在 SoC、connector、middle device 還是終端附近
- 這是已證成 wiring fact，還是目前只到候選

## 6. 共線 / 共名 / 共功能是三個不同層次

要分清楚：

- **共線**：真的是同一條電氣連線
- **共名**：名稱長得像
- **共功能**：最後都屬於 I2C/Reset/LED 類功能

skill 不能因為其中一個成立，就自動把另外兩個都當成立。

## 7. 遇到歧義時要主動問，但問題要帶 context

好的問題：

- 哪個 connector 對接不明？
- 哪兩個 IC 型號候選衝突？
- 哪個 polarity 無法定案？
- 這個問題會影響哪個 downstream 結論？

壞的問題：

- 「這個是不是對的？」
- 「你看一下這個」

## 8. 結果要能轉成 table，不只轉成文字

建議最少輸出：

### Signal table

| 欄位 | 說明 |
|---|---|
| `canonical_signal` | 最終歸一名稱 |
| `aliases` | 中途出現過的 net/tag 名稱 |
| `path_segments` | 經過哪些元件 / connector / page |
| `bridge_types` | continuity 的證據種類 |
| `swap_status` / `swap_detail` | 是否有 swap、是哪一種 swap、在哪裡發生 |
| `electrical_traits` | pull-up / active-low / open-drain 等 |
| `source_refs` / `sink_refs` | 線路兩端或主要端點 |
| `status` | VERIFIED / INCOMPLETE / EXCLUDED |
| `provenance` | pdf / page / refdes / method / confidence |

### Device table

| 欄位 | 說明 |
|---|---|
| `refdes` | 元件編號 |
| `part_number` | 型號 |
| `normalized_family` | 正規化 family / compatible |
| `bus` | I2C/SPI/PCIE/UART/... |
| `address_or_cs` | address / chip-select / lane |
| `pins_used` | 真正被用到的腳位 |
| `population_state` | populated / DNP / unknown |
| `status` | VERIFIED / INCOMPLETE / EXCLUDED |
| `provenance` | 證據來源 |

## 9. 交付報告也要有固定骨架

從這次參考的 `.mhtml` 內容來看，有兩種形式值得吸收：

### A. 中介分析格式

適合用來把「還沒收斂成最終答案」的硬體事實先整理好：

- `Hardware Intent Table`
- `Clarification Request`

`Hardware Intent Table` 的價值在於先把：

- object / instance
- signal / pin
- function
- active level
- connection target
- population state
- evidence

這些欄位整理成半結構化資料，再交給下游 DTS / spec / review。

`Clarification Request` 的價值在於：

- 明確指出缺什麼
- 目前有哪些候選
- 問這題會影響哪個結論

而不是只丟一句模糊的「請再確認」。

### B. 主題式交付報告

像 `uart_report.txt` 這類輸出，適合當成 skill 的 **topic report** 模板。

建議骨架：

1. `Title / Scope`
2. `Primary evidence sources`
3. `Summary`
4. `Per-instance / per-rail / per-device breakdown`
5. `Open questions`

其中每個 breakdown 最好都包含：

- instance 名稱
- mapping / endpoint
- population state
- 需要時的 electrical traits
- inline evidence

這種格式很適合：

- UART count and usage
- power rail ownership / enable path
- LED / button topology
- bus inventory

## 10. 不要把 AI 對話 UI 雜訊一起學進來

要吸收的是「資料結構與報告骨架」，
不是：

- model 比較
- 工具名稱炫技
- 對話平台 UI 文案
- 與硬體事實無關的 meta 討論

skill 應保留 evidence、mapping、question template，
但排除對話產品本身的包裝層。

## 11. BGW720 這次最重要的實戰教訓

- `wan_sfp:i2c-bus` 要靠 cage-level page-local context，不可順手猜
- `USB1` 不能因 controller-side signal 存在就視為板上有 port
- `wakeup-trigger-pin-gpio` 必須單獨證成；reference conflict 時回 raw evidence
- `USB_POWER` 與 `POWER_CONTROL` 不能混
- `RF_DISABLE_L` / `PEWAKE` 是 board control line，不是 power node
- `gpio@27` 的 device identity 與 `gpiocext_wlan` 的 alias naming 要分開看
- `swap` 不能只當成 trace 附註；它本身就是 board behavior，需要被明確建模、輸出、並在證據不足時保留為候選而非定論

## 12. 一句話總結

這個 skill 的目標不是「幫某個下游格式湊答案」，
而是把 **PDF → signal graph → device identity → electrical meaning → structured table**
這條鏈做對。 
