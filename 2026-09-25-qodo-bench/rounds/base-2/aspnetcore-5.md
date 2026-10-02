<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了對封閉泛型元件（closed generic components）的測試涵蓋範圍，包含 EndpointHtmlRenderer 與 ServerComponentDeserializer 的測試，並新增一個測試用的泛型元件。整體而言，測試結構合理，但存在一些型別不一致與斷言可能不正確的問題，可能導致測試失敗或誤判。最需要優先修正的是 ClientMode 測試中使用了錯誤的泛型型別（GenericComponent<string> 而非 GenericComponent<int>），以及 ServerComponentDeserializerTest 中參數值型別轉換的脆弱性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837` | ClientMode 測試中使用了錯誤的泛型型別 | 0.90 |
| ⚠️ | Major | `src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124` | 參數值型別轉換脆弱，可能因文化特性失敗 | 0.80 |
| 🔸 | Minor | `src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837` | ClientMode 測試中未驗證 Descriptor 內容 | 0.70 |
| 🔸 | Minor | `src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124` | 使用 Convert.ToInt64 可能隱藏型別資訊 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837</code> ClientMode 測試中使用了錯誤的泛型型別</summary>

在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，元件是以 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同（例如 `GenericComponent`1[[System.Int32]]` vs `GenericComponent`1[[System.String]]`）。建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

**判斷依據**：diff 中新增的測試方法 `CanPrerender_ClosedGenericComponent_ClientMode` 內，prerender 使用 `typeof(GenericComponent<int>)`，但斷言使用 `typeof(GenericComponent<string>)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124</code> 參數值型別轉換脆弱，可能因文化特性失敗</summary>

在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 long。然而，`parameters["Value"]` 的實際型別取決於反序列化過程，可能是 `JsonElement` 或其他型別。如果該值不是可直接轉換為 long 的型別（例如是 `JsonElement`），`Convert.ToInt64` 可能拋出例外或產生非預期結果。建議先確認參數值的實際型別，或使用更強健的轉換方式（例如 `Assert.IsType<JsonElement>(parameters["Value"])` 後再取得數值）。

**判斷依據**：diff 中新增的測試方法 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 內，直接使用 `Convert.ToInt64` 轉換參數值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837</code> ClientMode 測試中未驗證 Descriptor 內容</summary>

在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，僅驗證了 preamble marker 的 Assembly 與 TypeName，但未驗證 descriptor 的內容（例如參數定義與值）。這可能導致測試涵蓋不足，無法確保序列化與反序列化的正確性。建議參考其他測試（如 ServerMode 測試）增加對 descriptor 的驗證。

**判斷依據**：diff 中新增的測試方法 `CanPrerender_ClosedGenericComponent_ClientMode` 內，僅有 preamble marker 的型別與名稱斷言，未對 descriptor 進行驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124</code> 使用 Convert.ToInt64 可能隱藏型別資訊</summary>

在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64` 將參數值轉換為 long，但未驗證參數值的原始型別。這可能導致測試無法偵測到反序列化過程中型別資訊的遺失或錯誤。建議先斷言參數值的型別（例如 `Assert.IsType<JsonElement>(parameters["Value"])`），再進行數值比較。

**判斷依據**：diff 中新增的測試方法 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 內，直接使用 `Convert.ToInt64` 轉換參數值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4771 (cache hit 4736) ｜ completion tokens 1280 ｜ PR #5</sub>