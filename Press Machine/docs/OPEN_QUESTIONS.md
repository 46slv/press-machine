# Open Questions

実装開始前に、優先度順で決定します。

## Q-001: 対応する入力色空間

初期版から以下へ対応することは決定済みです。

- DaVinci Wide Gamut / Intermediate
- Rec.709 Gamma 2.4
- Rec.709 Scene
- ACEScct / AP1
- ARRI LogC3 / ARRI Wide Gamut 3
- ARRI LogC4 / ARRI Wide Gamut 4
- ACEScg / AP1 Linear

未決事項:

- Rec.709 Scene の正確な変換定義を Resolve の挙動と照合する

ARRI の Log transfer function と Wide Gamut primaries を必ずペアで扱うことは決定済みです。
Linear 入力を ACEScg / AP1 Linear とすることも決定済みです。
Rec.709 Gamma 2.4 と Rec.709 Scene の両方へ対応することも決定済みです。
LogC3 を EI 800 固定とすることも決定済みです。

## Q-002: 共通処理空間と輝度計算

入力をどの共通空間へ変換し、そこで明るさと彩度を測るかを決めます。

- XYZ または xyY 系
- LMS 系
- AP1 Linear
- DWG Linear
- 入力色域の Linear RGB

複数色域で同じ感触を目指すなら、特定 RGB 色域の距離を直接使うより、共通の知覚寄り空間で検出する案が有力です。

## Q-003: Scope-based Detector の正確な定義

Resolve ベクトルスコープ基準を採用することは決定済みです。

実装検証で確定する項目:

- ベクトルスコープ相当の色差行列
- 色差を計算する信号のガンマ状態
- full/video range の扱い
- Input Color Space 間で Threshold を共通化する正規化
- Resolve のスコープ表示との許容誤差

## Q-003A: ベクトルスコープの検証条件

基準には DaVinci Resolve の通常のベクトルスコープを使用することが決定済みです。

実装検証前に、以下の条件を固定します。

- Resolve のカラーマネジメント設定
- Press Machine を置くノード位置
- スコープの color space
- 表示変換の前後どちらを測定するか
- テストチャートの信号レベル

## Q-005: Soft-knee の数式

Threshold を Knee の中心、Knee を全幅とすることは決定済みです。

数式の推奨:

audio compressor 型の二次 soft-knee。

代替:

- smoothstep による補間
- cubic Hermite
- sigmoid

評価基準:

- 単調性
- C1 連続性
- Ratio の意味が保たれること
- GPU コスト

## Q-004: Black protection の形

`Black Protect` checkbox を追加し、初期値を ON とすることは決定済みです。

候補:

- 彩度検出の分母へ滑らかな floor を入れる
- 明るさに応じて detector をフェードする
- 両方を組み合わせる

未決事項:

- 保護を開始・終了する内部輝度
- fade に smoothstep を使うか
- 異なる入力色空間で同じ見え方にするための輝度正規化

初期版では保護範囲を固定し、範囲スライダーは設けません。
保護範囲を最小限にすることは決定済みです。

## Q-005: Soft-knee の数式

推奨:

audio compressor 型の二次 soft-knee。

代替:

- smoothstep による補間
- cubic Hermite
- sigmoid

評価基準:

- 単調性
- C1 連続性
- Ratio の意味が保たれること
- GPU コスト

## Q-006: Threshold と Knee の UI 範囲

Threshold を `0-100` とすることは決定済みです。

未決事項:

- Threshold の初期値
- Knee の最大値と初期値
- Resolve ベクトルスコープの基準外周を内部数値へ対応させる正規化係数

## Q-006A: Infinity Ratio の UI

以下は決定済みです。

- Ratio の数値範囲は `1.0-20.0`
- 最大値 `20.0` を内部的に `Infinity:1` として扱う
- UI ラベルは `Ratio (Max = Limit)`

最大位置直前から Limiter へ移る際の操作感のみ、Resolve 上の試作で確認します。

## Q-007: グラフを製品 UI に含めるか

- `Show Graph` checkbox を追加する
- 開発版だけに含める
- グラフなしでリリースする

推奨:

開発中は必須。製品版では checkbox で任意表示。

## Q-008: グラフの軸レンジ

- 固定 0-1
- 固定 0-2
- working domain ごとの固定値
- 自動レンジ

推奨:

working domain ごとの固定値。

## Q-009: 負 RGB と HDR 値

初期推奨はクランプせず保持です。Resolve 上での実画像検証が必要です。

## Q-010: バイパスの厳密性

`Amount = 0`、`Ratio = 1` では、演算後の近似値ではなく入力を直接返す設計を推奨します。
