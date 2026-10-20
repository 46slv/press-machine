# Development Worklog

## 2026-06-21

### 要求

Press Machine を Density を含む複合ツールから、彩度圧縮専用 DCTL として再建する。

初期要求:

- RGB から Y を計算
- `RGB - Y` を色差成分とする
- 色差ベクトル長を彩度量とする
- Threshold、Ratio、Knee による soft-knee compression
- 圧縮後色差を Y に戻して RGB を再構成
- UI は Amount、Threshold、Ratio、Knee、Mix
- `Mix = 0` と `Amount = 0` は無効
- NaN、除算ゼロ、極端値への安全処理

### 実施内容

- 新規 `Press Machine` プロジェクトフォルダを作成。
- 製品要件、アルゴリズム、UI、グラフ、設計判断、未決事項、移行メモを分離して文書化。
- Amount と Mix の重複問題を記録。
- Amount を effective ratio の制御、Mix を最終 wet/dry とする案を提示。
- 標準的な ratio 式と audio compressor 型 soft-knee を推奨案として記録。
- 絶対色差長が scene-linear で露出依存になる問題を記録。
- working domain と luma weights を実装前の最重要決定事項とした。

### 次の作業

1. working domain を決める。
2. luma weights を決める。
3. saturation metric を決める。
4. Amount の役割を確定する。
5. UI 範囲とデフォルトを決める。
6. 数学関数の CPU リファレンスとテストを作る。
7. DCTL v0.1 を実装する。

## 2026-06-22

### 決定事項

- 明るさではなく彩度を基準に圧縮する。
- 同じ彩度なら、明るさが違っても同程度に圧縮する方向を目標とする。
- ほぼ黒い領域の微小色差やカラーノイズには反応しにくくする。
- 暗部保護はユーザー向け機能ではなく内部安定化処理とする。
- 効果量スライダーは `Amount` 一つにし、`Mix` を削除する。
- 複数の入力色空間へ DCTL 内部で対応する。

### 次に決めること

- 初期対応する入力色空間。
- 彩度を測る共通空間。
- 知覚寄り彩度指標の具体式。
- 黒付近の滑らかな反応抑制。

### 製品定義の確定

ユーザー確認により、以下を中核定義として採用:

> 見た目の彩度が高すぎる部分を見つけ、信号として正確かつ予測可能に圧縮する。

- Detector は体感的な彩度へ寄せる。
- 実際の減衰は機械的かつ再現可能にする。
- Density は別機能として扱い、Press Machine には含めない。
- 製品版には detector mode の切り替えを設けず、検証で選んだ単一方式を採用する。

### 色相中立性

- 色相による知覚補正は行わない。
- 同じ検出彩度なら、色相に関係なく同じ比率で圧縮する。
- 色差ベクトルの方向を維持し、意図的な色相回転を起こさない。
- ベクトルスコープ上で同じ半径の色が等しい割合で中心へ移動することを目標とする。
- DaVinci Resolve の通常のベクトルスコープを正式な評価基準とする。
- Threshold を soft-knee の中心として定義する。
- Knee は遷移帯の全幅とする。
- Ratio は一般的なコンプレッサー比として定義する。
- `Infinity:1` は色差ベクトル長を Threshold に制限する彩度リミッターとする。
- Limiter は RGB チャンネルクリップではなく、Knee に応じて hard/soft に動作する。
- Limiter は独立 checkbox ではなく Ratio スライダーの最大位置で選択する。
- DCTL UI の制約上、最大値表示を `Infinity` に置き換えられない可能性があるため、ラベルとグラフで補足する。
- Ratio の初期範囲を `1.0-20.0` とし、最大値 `20.0` を Limiter として扱う。
- Ratio の UI ラベルを `Ratio (Max = Limit)` とする。
- 初期版から DWG/Intermediate、Rec.709 Gamma 2.4、ACEScct、Linear、LogC3/AWG3、LogC4/AWG4 に対応する。
- 色空間変換では transfer function と primaries の両方を扱う。
- `Linear` の primaries は追加ヒアリング事項とする。
- ARRI 入力は `LogC3/AWG3`、`LogC4/AWG4` のペアとして扱う。Log カーブだけを色空間として扱わない。
- 曖昧な `Linear` 入力を廃止し、`ACEScg / AP1 Linear` として定義する。
- ACES2065-1/AP0 ではなく、演算用途に適した ACEScg/AP1 を採用する。
- Rec.709 Gamma 2.4 と Rec.709 Scene を別モードとして初期対応する。
- ARRI LogC3/AWG3 は EI 800 固定とし、EI 選択 UI を設けない。
- ARRIRAW の現像と EI メタデータ処理は Press Machine の責務外とする。
- 彩度 Detector は Resolve ベクトルスコープ中心からの距離を基準とする。
- 明るさによる彩度補正はせず、明るさは黒付近の反応停止だけに使用する。
- 色差平面上で放射状に圧縮し、色相角を維持する。
- `Black Protect` checkbox を追加し、初期値を ON とする。
- Black Protect OFF では暗部も通常どおり圧縮対象にする。
- 初期版では保護範囲を内部固定値とし、調整スライダーは設けない。
- Black Protect はほぼ黒の微小色差だけを対象とする最小限の範囲にする。
- 暗い有彩色、夜景、ネオンは通常の圧縮対象として残す。
- Amount は入力彩度と完全圧縮後彩度の線形補間とする。
- Amount の 50% は実際の彩度減少量の 50% とする。
- Amount UI は `0-100` 表示とし、内部で `Amount / 100` に変換する。
- Threshold UI はベクトルスコープ基準の `0-100` とする。
- 入力彩度は100でクランプせず、100を超える信号もRatioに従って処理する。
