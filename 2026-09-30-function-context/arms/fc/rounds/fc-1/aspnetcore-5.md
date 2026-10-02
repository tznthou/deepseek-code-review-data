<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了封閉泛型元件在 prerender 與 server component deserialization 的測試涵蓋。整體測試結構與既有測試一致，主要風險在於測試斷言的正確性與型別處理。最需要注意的是 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，preamble marker 的型別名稱斷言使用了 `GenericComponent<string>` 而非實際渲染的 `GenericComponent<int>`，可能導致測試失敗或誤判。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837` | ClientMode 測試中 preamble marker 的型別名稱斷言錯誤 | 0.90 |
| 🔸 | Minor | `src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124` | 參數值轉換使用 Convert.ToInt64 可能隱藏型別問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837</code> ClientMode 測試中 preamble marker 的型別名稱斷言錯誤</summary>

在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，實際渲染的元件型別是 `GenericComponent<int>`，但斷言卻使用了 `typeof(GenericComponent<string>).Assembly.GetName().Name` 和 `typeof(GenericComponent<string>).FullName`。這會導致測試失敗，因為 `GenericComponent<string>` 的 full name 與 `GenericComponent<int>` 不同。建議改為 `typeof(GenericComponent<int>)`。

**判斷依據**：diff 中新增的測試方法 `CanPrerender_ClosedGenericComponent_ClientMode` 內，渲染使用 `typeof(GenericComponent<int>)`，但斷言使用 `typeof(GenericComponent<string>)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124</code> 參數值轉換使用 Convert.ToInt64 可能隱藏型別問題</summary>

在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 來驗證參數值。如果實際反序列化的值是 `JsonElement` 或其他型別，`Convert.ToInt64` 可能成功轉換，但無法驗證型別是否正確。建議直接斷言型別為 `JsonElement` 並取得其值，或使用 `Assert.IsType<long>` 等更精確的斷言。

**判斷依據**：diff 中新增的測試方法 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 內，使用了 `Convert.ToInt64` 進行轉換。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5546 (cache hit 1536) ｜ completion tokens 678 ｜ PR #5</sub>