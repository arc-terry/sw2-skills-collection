---
name: schematic-reasoner
description: >
  針對 schematic PDF、GPIO table、BOM、datasheet 做可追溯的電路分析。
  可建立 signal alias / canonical net、跨頁與跨 PDF 跟線、解析 IC 型號與規格、
  必要時用 web_fetch / agent-browser 補 public spec，並把分析結果收斂成結構化 table、
  VERIFIED / INCOMPLETE / EXCLUDED facts 與主動提問清單。
---

# Schematic Reasoner

## 這個 skill 的本質

這不是「DTS skill」。

這是一個 **讀 PDF、找線、辨識器件、理解電氣語義、把電路事實整理成可重用資料結構** 的 skill。

它的輸出可以拿去做 DTS、spec、table、review note、bring-up checklist，
但 skill 本身應該停留在 **電路分析層**。

## 主要能力

這個 skill 必須能做：

1. **讀 PDF / OCR fallback**
   - 讀 schematic、block diagram、datasheet、BOM
   - 文字層不乾淨時，允許 OCR fallback

2. **找線 / 跟線**
   - 從 signal name 找到 tag / net
   - 跨頁追蹤
   - 跨 PDF 追蹤（mainboard ↔ daughter board ↔ module）
   - 穿過 connector / header / cable pin continuation

3. **Signal alias / canonical net normalization**
   - 例如 `SDA` 經過電阻後變 `SDA_0`
   - 本質上仍可能是同一條信號，只是局部命名不同
   - skill 必須建立 `canonical_signal` 與 `aliases`

4. **IC 型號解析**
   - 用 refdes / marking / BOM / datasheet / package information 推 part number
   - 若本機沒有 datasheet 或 spec，可用 `web_fetch` / `agent-browser` 補 public spec
   - 若用了 web spec，必須回頭核對 schematic/BOM 的 package、pin count、package code、可見 pinout 是否相符

5. **電氣語義判讀**
   - pull-up / pull-down
   - open-drain / push-pull
   - active-high / active-low
   - external inversion / transistor stage
   - lane swap / pair swap / polarity swap
   - reset / power-enable / interrupt / wake / LED drive / button sense

6. **行為理解**
   - button：按下時是拉高還是拉低、是否有外部 pull-up/down、是否經過 debounce/RC
   - LED：source/sink、是否 active-low、是否經過 shift register / expander / transistor
   - high-speed / differential path：是否有 lane swap、pair swap、polarity inversion，以及它是已證成事實還是僅候選

7. **表格化輸出**
   - 將線路與元件分析轉成可重用 table / schema
   - 不是只輸出自然語言

8. **主動提問**
   - 遇到歧義時，能明確指出缺什麼證據、問什麼問題

## 核心原則

1. **Evidence first**
   - 每個結論都必須能回指到 PDF / BOM / datasheet / public spec。

2. **Canonical before semantic**
   - 先證明「這是不是同一條線」，再證明「這條線代表什麼功能」。

3. **Separate identity from meaning**
   - `GPIO_26 = RBR_FB` 成立，不等於 `GPIO_26 = wakeup-trigger-pin-gpio`。

4. **Public spec is allowed, answer key is not**
   - 可用 public datasheet / public reference manual 補 device identity / capability。
   - 但 web 補到的型號必須再和 schematic/BOM 的封裝與 pinout 對回來，不能只因 family 看起來像就定案。
   - 不可用 board answer key 直接補硬體結論。

5. **Status must be explicit**
   - `VERIFIED` / `INCOMPLETE` / `EXCLUDED` 必須分清楚。

## 標準工作流

### Step 1. 盤點證據

先列：

- schematic PDFs
- block diagram
- GPIO table / pin mux table
- BOM / DNP table
- datasheet / product brief
- public web datasheet / spec（若本地沒有）

### Step 2. 建立索引

每張 PDF 都要有：

- page index
- tag/net index
- refdes index
- connector pinout index
- component-to-page index

### Step 3. 建立 canonical signal graph

對每條線，建立：

- `canonical_signal`
- `aliases`
- `path_segments`
- `bridges`

常見 bridge 類型：

- off-page marker
- connector pin continuation
- 0R resistor
- series resistor
- level shifter channel
- net rename（如 `SDA -> SDA_0`）

### Step 4. 做保守 tracing

跟線時要能辨識：

- 直連
- 被動元件穿透
- DNP 斷線
- 多路分支
- differential pair
- lane / pair correspondence
- connector mapping

trace 斷掉時，標 `INCOMPLETE`，不要補猜。

### Step 5. 解 device identity

優先順序：

1. 本地 BOM / PDF 明確 part number
2. package marking
3. 本地 datasheet
4. `web_fetch` / `agent-browser` 查 public datasheet / product page

若使用 web 工具，必須記錄：

- URL
- 使用到的欄位
- 它補的是 device identity 還是 electrical behavior
- package / pin count / package code / pinout 與 schematic/BOM 的比對結果

### Step 6. 判讀 electrical semantics

skill 必須能從線路關係判定：

- pull-up / pull-down 是否存在
- signal idle level
- external active-high / active-low
- 是否有反相級
- 是否存在 lane swap / pair swap / polarity swap
- 是否由 expander / shift register / transistor 驅動
- button / LED 的實際讀法

### Step 7. 轉成結構化 table

至少要能輸出兩類表：

#### Signal table

- `canonical_signal`
- `aliases`
- `source_ref`
- `sink_ref`
- `path_segments`
- `swap_status`
- `swap_detail`
- `electrical_traits`
- `population_state`
- `status`
- `provenance`

#### Device table

- `refdes`
- `part_number`
- `normalized_compatible`
- `bus`
- `address`
- `pins_used`
- `status`
- `provenance`

### Step 8. 主動提問

只有在以下情況問：

- connector 對接有多個可能
- 同一顆 IC 有多個候選型號
- 文字層 / OCR 不足以定 pinout
- active polarity 無法由外部電路定案
- public spec 與 schematic evidence 互相衝突

問題要明確指出：

- 缺什麼證據
- 現在有哪些候選解
- 問這題會影響哪個結論

## 輸出格式

預設輸出四段：

1. `VERIFIED facts`
2. `INCOMPLETE facts`
3. `EXCLUDED claims`
4. `Questions for user`

每個 fact 至少包含：

- `what`
- `status`
- `why`
- `where proved`
- `confidence`

若題目是單一主題盤點（例如 `UART count/usage`、`SoC power rails`、`LED topology`），
可在上述四段之外，再輸出一份 **topic report**，建議骨架為：

1. `Title / Scope`
2. `Primary evidence sources`
3. `Summary`
4. `Per-instance or per-rail breakdown`
5. `Open questions / unresolved points`

其中 `Per-instance or per-rail breakdown` 應盡量包含：

- instance / rail 名稱
- mapping 或 endpoint
- population state
- active level / electrical traits（若適用）
- evidence line（來自哪份 PDF / XLSX / page / row）

此外，skill 可以使用兩種中介格式幫助分析收斂：

### Hardware Intent Table

適合在「先把電路意圖整理乾淨，再決定下游輸出」時使用。

建議欄位：

- `object_type`
- `instance`
- `signal_or_pin`
- `function`
- `active_level`
- `connection_target`
- `population_state`
- `evidence`

### Clarification Request

適合在證據不足、但已經能明確描述缺口時使用。

至少包含：

- `question`
- `missing_evidence`
- `current_candidates`
- `downstream_impact`

## Tool policy

- **local evidence first**
- **public web lookup second**
- `web_fetch` / `agent-browser` 只拿來補：
  - IC 型號
  - datasheet
  - product brief
  - standard pinout / electrical spec
- 不可拿 web 上的 board DTS / forum post 當硬體真相

## 反模式

- 只因 signal 名稱很像，就當成同一條線
- 只因過一顆電阻就當成一定是不同信號
- 只因 public ref 有 property，就當成硬體已證成
- 把 IC compatible 補齊，卻順便把 board wiring 一起猜掉
- trace 中斷時默默 fallback 成成功

## 參考

- `references/analysis-playbook.md`
