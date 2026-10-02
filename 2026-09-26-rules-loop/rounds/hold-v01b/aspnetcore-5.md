<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了對封閉泛型元件（closed generic components）的測試，涵蓋 EndpointHtmlRenderer 與 ServerComponentDeserializer。整體測試結構良好，但存在一個測試中的型別不一致（ClientMode 測試使用 GenericComponent<string> 而非 GenericComponent<int>），可能導致測試失敗或誤導。此外，ServerComponentDeserializerTest.cs 的命名空間與類別宣告格式不符合 repo 規範（R02、R18），且新增的 GenericTestComponent<T> 類別未標記為 sealed（R14）。建議修正這些問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837` | ClientMode 測試使用錯誤的泛型型別參數 | 0.90 |
| 🔸 | Minor | `src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10` | [R02] 命名空間宣告未使用 file-scoped 語法 | 0.80 |
| 🔸 | Minor | `src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:12` | [R18] 類別宣告的開頭大括號未換行 | 0.80 |
| 🔸 | Minor | `src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:590` | [R14] 內部測試類別未標記為 sealed | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837</code> ClientMode 測試使用錯誤的泛型型別參數</summary>

在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，參數使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為實際元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。

建議將斷言中的 `GenericComponent<string>` 改為 `GenericComponent<int>`，以符合實際使用的型別。

**判斷依據**：diff 中新增的測試方法 `CanPrerender_ClosedGenericComponent_ClientMode` 內，prerender 使用 `typeof(GenericComponent<int>)`，但後續斷言使用 `typeof(GenericComponent<string>)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10</code> [R02] 命名空間宣告未使用 file-scoped 語法</summary>

此檔案將原本的 file-scoped namespace 改為 block-scoped namespace，違反 repo 規範 R02（Use File-Scoped Namespace Declarations）。

建議改回 file-scoped namespace 宣告，例如：
```csharp
namespace Microsoft.AspNetCore.Components.Server.Circuits;
```

**判斷依據**：diff 中將原本的 `namespace Microsoft.AspNetCore.Components.Server.Circuits;` 改為 `namespace Microsoft.AspNetCore.Components.Server.Circuits` 並加上大括號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:12</code> [R18] 類別宣告的開頭大括號未換行</summary>

類別 `ServerComponentDeserializerTest` 的開頭大括號與類別宣告在同一行，違反 repo 規範 R18（Opening Braces Must Be on New Line (Allman Style)）。

建議將大括號移至下一行：
```csharp
public class ServerComponentDeserializerTest
{
```

**判斷依據**：diff 中新增的類別宣告行 `public class ServerComponentDeserializerTest` 後緊接著 `{`，未換行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:590</code> [R14] 內部測試類別未標記為 sealed</summary>

新增的 `GenericTestComponent<T>` 類別是內部實作類別，且未預期被繼承，但未標記為 `sealed`，違反 repo 規範 R14（Sealed Keyword Required for Internal Implementation Classes）。

建議加上 `sealed` 修飾詞：
```csharp
private sealed class GenericTestComponent<T> : IComponent
```

**判斷依據**：diff 中新增的類別宣告 `private class GenericTestComponent<T> : IComponent` 缺少 `sealed`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6956 (cache hit 6912) ｜ completion tokens 1107 ｜ PR #5</sub>