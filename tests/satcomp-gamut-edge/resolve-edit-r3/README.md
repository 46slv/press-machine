# SatComp #19 — Resolve 21.2 Windows Edit独立OFXの限定受入

最終報告（2026-11-26、会話記録 `33889`）を、保存済み実機監査・評価ZIP・試験した固定OFXに照合して保全する。Draft #19の入力は `769a014c22c5d857fd771a659672171340a753b1`。この差分は隔離レビュー用の記録のみで、実装・配布物・既存の判定は変更しない。**Windows版 Resolve Studio `21.2.0.6`／CUDA設定／EditクリップOFX／固定合成素材で限定合格。製品OFXはCPUレンダー**。制作導入、公開、他環境は対象外。

[21.1.0.14の元Color組み込みResolveFX記録](../resolve-final/SATCOMP-RESOLVE-FINAL.md)は不合格のまま。21.2.0.6でも同じ組み込み経路の定数対照は不合格。以下のEdit定数・製品9ケースをColorの修正とはみなさない。

## 証跡の対応

| 対象 | SHA-256 |
|---|---|
| [実機監査（ZIP内 `evidence/edit-matrix-audit.json` とバイト一致）](evidence/edit-matrix-audit.json) | `b031f9adc02acfbb53c943845d1134adca7bec8b4244603aebe1c46bcf7afa77` |
| `SatComp-HDR-Native-Win64-Edit-evaluation-r3.zip`（別保管、48メンバー） | `89ee3031f32e71185453f084eae313c3c9d7127c64af7f3ec9090a7d5a2d4dcc` |
| ZIP内 `SatCompHDR.ofx.bundle/Contents/Win64/SatCompHDR.ofx`（`org.satcomp.hdr.native.r1`） | `ce23c769e5e8944a44db43f3cb41e56f1b3f2cf5ab304042012002df2d678858` |

[要約と元レシートのハッシュ](evidence/run-summary.json)は定数診断、既定値、8操作子、負例、保存再出力、別工程の回収を対応付ける。元レシート・実機出力・配布物は別保管で、このリポジトリに含めない。実機監査にはEXRファイルとデコードRGBAそれぞれのSHA-256を記録（後者は行順のlittle-endian float32をR/G/B/A平面順に連結）。ハッシュ照合だけを再レンダーや画素採点とはみなさない。

ローカル照合は `Get-FileHash -Algorithm SHA256` で上の3点を比較し、展開したZIPの `SHA256SUMS.txt` で素材と補助JSONも確認する。監査JSONの元バイト列（CRLF）はこのディレクトリのGit属性で保持している。

## 再現条件と採点

同じ版・CUDA設定を使用する別の検証環境で、共有Resolve排他枠とアイドル状態を確認し、専用プロジェクトだけで実施する。既存プラグインを上書きしない。公式アプリ内スクリプトと標準Computer Useで適用・Inspector・個別レンダージョブを照合した（外部公式MCPは接続不成立）。DaVinci YRGB（自動色管理なし）、640×360／24 fps／Full、正方画素、個別クリップ、`RGB float (ZIP)` EXR、`ExportAlpha=true`／`AlphaMode=1`（Straight）、音声なし。試験素材は評価ZIPの `source/reference-pack/manifest.json` に照合し、ケースごとに指定フレームの同じバイト列を連番2枚として別の試験binへ取り込み、24 fpsと指定の入力Alpha Modeを読み戻す。各クリップで同じ1フレームだけを書き出す。

1. **定数対照を先に実施。** `run-summary.json` の固定入力と診断バイナリを使い、同一条件のEdit OFF、CUDA診断ON、CPU診断ONを別ジョブで出力。OFFは全RGBAが入力とビット一致、ONは各230,400画素が `(8.125, 8.125, 0.375, 1)` とビット一致すること。診断OFXと製品を取り違えない。
2. **固定製品の適用と設定。** Editの対象クリップに `SatComp HDR (Native Preview)` を有効化し、既定値でRGBAが恒等になることと、8操作子の非既定値の読戻しを別々に確認。次表は毎ケース既定値から開始し、記載項目だけを変える。既定値は `Comp Bypass=Off`、入力 `DWG D65 / DaVinci Intermediate`、出力色域・伝達は両方 `Same as Input`、`Threshold=25`、`Amount %=0`、`Knee %=20`。

| ケース | 素材（`source/reference-pack/`） | 既定値からの変更 |
|---|---|---|
| `logc4` | `range4.000000.exr` | 入力 `Relative Linear` → 出力 `LogC4 Scene`、`Comp Bypass=On` |
| `logc3` | `range3.000000.exr` | 入力 `Relative Linear` → 出力 `LogC3 EI800 Exposure`、`Comp Bypass=On` |
| `di` | `range3.000000.exr` | 入力 `Relative Linear` → 出力 `DaVinci Intermediate`、`Comp Bypass=On` |
| `ap1` | `chroma.000000.exr` | 入力 `ACES AP1 CAT02 / LogC4 Scene` → 出力 `DWG D65 / Relative Linear`、`Comp Bypass=On` |
| `blur0` / `blur1` | `normal.000000.exr` / `normal.000001.exr` | 入力 `Relative Linear`、`Amount %=100` |
| `blurpass` | `normal.000000.exr` | 入力 `Relative Linear`、`Amount %=100`、`Comp Bypass=On` |
| `straight` / `premult` | `straight.000000.exr` / `premult.000000.exr` | 入力 `Relative Linear` → 出力 `DaVinci Intermediate`、`Amount %=100`、入力Alpha ModeをそれぞれStraight／Premultiplied |

3. **実際の出力を比較。** ジョブごとに開始とは別の `Complete`／100% とfloat32 RGBA出力を照合する。4変換は有限RGB、`abs(error)/max(1, abs(reference)) ≤ 1e-5`、意図しないゼロ化なし、Aビット一致。3つのHDRランプは中心行の隣接ステップ誤差も `≤ 2e-5`。LogC4／LogC3／AP1の参照は同梱EXR、DIは固定参照式から算出。ぼけ2フレームは暖色中心差 `≥ 1e-3`、無彩色差 `≤ 2e-6`、輪郭の最大隣接ステップは入力最大値の4倍以下。バイパスは元RGBAにビット一致。両AlphaケースのAは全画素一致、通常部分AのRGBは独立CPU参照と一致（詳細は監査JSON）。微小Aは別集計で、Strict Straight RGBは不合格。
4. **保存・再オープンと回収。** `blur0`（`Amount %=100`）で保存を確認してから専用PFを閉じて開き直し、対象クリップ・OFX有効状態・8設定を読み戻す。同一ジョブを再描画し、前後別々に `Complete`／100% を取得してRGBAのビット一致を確認する。matrix-r2本体の再出力は未成立。成功した別ラン（persistence-r4）の初回RGBAがmatrix-r2の `blur0` とも一致している。回収は試験所有分だけ。既存ジョブ・状態・タイムライン・設定を元の台帳と照合し、元OFF／アイドル、試験追加ファイルの不在、枠の `RELEASED` → `FREE` を独立に確認する。

### 保存済み捕捉の再採点（Resolve起動・操作なし）

元の検証作業ルート（監査スクリプト、合成素材と生レシートが保存されている別保管先）で以下を実行する。評価ZIP単体には実機出力・生レシート・監査ドライバーはない。標準出力のJSONをこのディレクトリの監査JSONと**パース後**に照合する。ZIP内の元監査はパース前のバイトも照合できる。

```sh
python -B satcomp-edit-endpoint/matrix_audit.py evidence/satcomp-edit-product-matrix-r2 --cleanup evidence/satcomp-edit-product-matrix-r2-unload --persistence evidence/satcomp-edit-product-persistence-r4
```

## 合格に含まない事項

- 旧Color（21.1.0.14）および21.2.0.6の元組み込み経路の定数対照は不合格。直接Colorの定数合格、Fusionのパススルー、Edit合格はそれぞれ別。Fusionの定数レンダーは未成立。
- 両Alpha出力はAビット一致だが、微小Aの厳格Straight RGBは不合格。A=0の隠れRGB保持は保証外。対象サンプルの差であり、正確な境界や処理段は未同定。
- 巨大な負入力を含む能動診断は、表現可能域の変換は成立したが、元の絶対ステップ基準は不合格。製品9ケースの限定合格では上書きしない。
- 外部公式MCPは未復旧。制作素材、他の版・OS・GPU／ホスト・色管理、性能、制作導入・リリースは未受入。
