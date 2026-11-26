# SatComp #19 — Resolve 実機診断の最終判定

**診断完了。元の8操作子付きResolveFXは不合格、採用不可。固定プロファイルの直接Color DCTLは、検証したHDR変換の回避策であって置換製品ではない。** ベースは [Draft #19](https://github.com/46slv/press-machine/pull/19) `769a014c22c5d857fd771a659672171340a753b1`。Resolve Studio `21.1.0.14`、Windows/CUDA、DaVinci YRGB、合成素材、640×360/24p、Full、RGB float ZIP EXR。EXRは保存された32ビット値を二つの経路で照合した。ユーザー素材での評価ではない。

| 診断 | 実機結果・判定 |
|---|---|
| SC-01：LogC4の極端HDR | 元経路でRゼロ `229,376/230,400`。代表点 `8.088068 → 0`。保存・再オープンおよびRGBA/texture ABIを換えた試験でも失敗。固定直接Colorでは参照許容内。 |
| SC-02：LogC3／DIの極端入力 | 同じ入力・カーブ比較。両ResolveFXでRゼロ `229,376/230,400`、固定直接は両方ゼロ欠落なし・許容内。代表点はLogC3 `10.006374`、DI `9.807870` を直接経路で保持。実測直適用を `z`、OFFを `x` とした条件付き `f32(x + f32(z - x))` が各RGB全画素でResolveFXに数値一致。 |
| SC-08：DI +8〜+12段 | ResolveFXでR/Gそれぞれ `88/640` 閾値超過、固定直接で `0/640`。最大スケール誤差 `2.53294e-5` 対 `1.97964e-7`。この素材では欠落なし、A不変。固定直接の無変更再オープンも一致。 |
| SC-09：定数専用ネイティブOFX | 別IDのCUDA専用フィルターは原画を読まず `(8.125,8.125,0.375,1)` を返す。直接Colorは全 `230,400` 画素で定数そのもの。組み込みResolveFXと別IDネイティブOFXの出力は全RGBAビット一致し、R/Gは各 `54,000` 画素が0、各 `7,200` 画素が16。BとAは全画素で期待値。試験したネイティブOFXに差し替えるだけでは直らない。本件にLog式や組み込みDCTLの変換本体は不要。GPU/ホストの具体的な演算やすべてのOFXには断定不可。`A=0` はこのストレス試験から除外。 |
| SC-03/04：アルファ・合成済み輪郭 | フレーム1、20/20捕捉・採点。straight、premult、Linear合成済み、誤Log合成済みの旧新がRGB/Aビット一致。6通りの候補再オープンも一致。合成済み輪郭のR差 `0.702000` 対 `0.187388` は効果OFFの時点から存在。候補有効でも `0.384417` 対 `0.125384`。 |
| SC-10：微小アルファの経路比較 | DWG Linear→AP1/DIの同じ本体で、固定直接とResolveFXはAが入力とビット一致、両経路のRGB最大差 `3.73e-9`。テスト行の `A=1.528e-9〜9.226e-8` の11点では、両経路とも通常のstraight変換後A乗算と異なる。次のサンプル `A=1.353e-7` 以上では通常モデルに整合。特定したのはサンプル間の境界のみで、正確な閾値や処理段は不明。A=0は別集計：straightは隠れRGBを保持、premultはRGBゼロ。 |
| SC-11：Resolve内・実際の二層合成 | V1不透明背景＋V2ぼけ輪郭、Normal、効果なし。straight/premultともLinear参照RGBとの差は最大 `1.19e-7`、誤Log合成は棄却。一方、両方同じ `13,320/230,400` 画素で理想のA=1から1 ULP下。**RGBの合成順は合格、完全不透明のAビット一致は不合格。** SatCompなしで生じるため候補固有ではない。内部の発生段・実素材の可視差は未確認。 |

通常ぼけ境界2フレームの旧新・OFF/バイパス・再オープン一致は先行完了済みで、今回再実行していない。AP1同色域およびAP1→DWGの所定クロマ試験、既存別ビルドによるDensity単独対照は検証済みの条件に限る。Densityの全体受入や版をまたぐ保証ではない。

## 数値の再計測（実機操作なし）

同梱の作業ディレクトリで Python 3 と FFmpeg を使用。出力先は未作成の別名を指定する。実機では別途、同一版・CUDA、共有 `live-resolve` 排他、使い捨てプロジェクト、追加専用の試験名を使用する。ドライバーはこのWindows環境の証跡用で、他の環境へそのまま配置・実行しない。

```sh
python -B build_sc02_direct_extreme.py --check
python -B build_sc10_profile.py --check
python -B build_sc11_plate.py --check
python -B measure_sc02.py replay-sc02.json
python -B measure_sc34.py replay-sc34
python -B measure_sc34_tiny_alpha.py replay-tiny-alpha
python -B measure_sc09.py replay-sc09.json
python -B measure_sc10.py replay-sc10.json
python -B measure_sc11.py replay-sc11.json
```

- [極端カーブ](evidence/sc02-final.json)／[DI近域の別包](DI-ROUTE-R2-REPORT.md)
- [20件と再オープン](evidence/sc34-final/metrics.json)／[小Aの詳表](evidence/sc34-tiny-alpha/metrics.json)
- [別ID定数](evidence/sc09-final.json)／[微小Aの直接対比](evidence/sc10-final.json)／[二層の結果](evidence/sc11-final-v2.json)
- [Astra独立レビュー](evidence/pi/sc-final-astra-review.md)／[モデル経路レシート](evidence/pi/sc-final-astra-route.json)：SC09/10/11の範囲を限定した原因帰属をADOPT。二層Aの不一致は別のホスト対照で、元8項目のHDR修正を合格にする証拠ではない。
- ネイティブOFXの単体試験とResolve実機は別。前者はRTX 3070 Ti／GTX 1650のCUDAデバイス書込みとガード領域を測定。後者は固有IDで登録、1ノードへの適用を読戻し、同一フレームをレンダー。バックグラウンドdragでは適用されず、対象ウィンドウ限定のforeground drag後にだけ適用・測定。実機結果は単体PASSから推定していない。

## 残る作業と条件

現行ホスト・固定条件での原因切り分けは終了した。元経路の修正は未完了。次は **Hermes Code** が、現用Resolveやライブラリを変えない隔離済みの対応版、または元の8項目を維持して出力を保持できる具体的な修正を確保できた時に、先に8.125の定数対照、次にLogC4／LogC3／DIの固定素材を再試験する。定数で同じ欠落を示す経路は通常回帰に進めない。実素材での見え方は、使用範囲の明確な素材がある場合に別途評価する。固定直接方式の製品採用は今回の範囲外。

SC11終了後、専用OFFへ戻し、同じスクラッチプロジェクトで91件完了・アイドル・共有枠 `FREE` を確認。所有試験DCTLと別ID OFXは回収済み。既存案件・既存エフェクトの上書き、製品更新、push・公開・外部問い合わせは行っていない。
