# Design Decisions

設計判断は、決定日、理由、影響を含めて記録します。

## D-001: 彩度圧縮専用ツールとして再建する

- Status: Decided
- Date: 2026-06-21

旧版の Density、Luma Power、Makeup、Gamut Limit などをコアから外し、一定以上の彩度を自然に圧縮する責務へ限定します。

## D-002: RGB-Y の色差ベクトルを使用する

- Status: Decided
- Date: 2026-06-21

```text
Y = dot(RGB, weights)
chroma = RGB - Y
sat = length(chroma)
```

圧縮後は chroma の方向を維持したまま長さだけを変更し、元の Y に戻します。

## D-003: Threshold、Ratio、Knee を持つ

- Status: Decided
- Date: 2026-06-21

Threshold 超過分に ratio compression を適用し、Knee 内では連続的に遷移させます。

## D-004: 効果量スライダーは Amount のみとする

- Status: Decided
- Date: 2026-06-22

純粋な彩度圧縮では Amount と Mix の結果が重複しやすいため、最終 UI では効果量スライダーを一つにします。

- `Amount = 0`: 入力をそのまま返す。
- `Amount = 1`: Threshold、Ratio、Knee で定義された圧縮を完全適用する。
- Amount の途中値は、実際の彩度減少量が線形に増える定義を優先する。

`Mix` は削除します。

## D-005: 旧版の log ratio mapping を廃止する

- Status: Proposed
- Date: 2026-06-21

`1 + log(Ratio)` では UI の Ratio が一般的な圧縮比を表しません。新版では `T + (x - T) / R` という標準的な ratio の意味を推奨します。

## D-006: 初期版ではガマットクランプを行わない

- Status: Proposed
- Date: 2026-06-21

彩度圧縮は chroma を neutral point へ縮小する処理です。出力 RGB の一律クランプは広色域値や HDR 値を損なう可能性があるため、初期版では除外します。

## D-007: グラフは診断表示として設計する

- Status: Proposed
- Date: 2026-06-21

入力彩度対出力彩度、恒等線、Threshold、Knee を表示します。処理とグラフは同じ helper 関数を使います。

## D-008: 明るさではなく彩度を圧縮判断に使う

- Status: Decided
- Date: 2026-06-22

明るいという理由だけで圧縮量を増やしません。同じ彩度として判定される色は、明るさが異なっても同程度に圧縮されることを目標にします。

この要件を満たすため、絶対的な RGB 色差量ではなく、明るさに対して相対化された彩度指標を検討します。具体的な数式は未決です。

## D-009: 黒付近では検出を抑制する

- Status: Decided
- Date: 2026-06-22

ほぼ黒い領域の微小な RGB 差やカラーノイズへ過敏に反応しないよう、内部的な black protection を設けます。

これはデノイズや暗部彩度調整ではなく、彩度検出を安定させるための固定処理とします。初期案ではユーザー向けスライダーを設けません。

## D-010: 複数の入力色空間へ内部対応する

- Status: Decided
- Date: 2026-06-22

Press Machine は入力色空間を選択できる設計とし、内部の共通処理空間へ変換してから彩度圧縮を行います。

対応する色空間、共通処理空間、変換精度は今後決定します。

## D-011: 知覚寄りの検出と機械的な圧縮を組み合わせる

- Status: Decided
- Date: 2026-06-22

Press Machine の中核を次のように定義します。

> 見た目の彩度が高すぎる部分を見つけ、信号として正確かつ予測可能に圧縮する。

Detector は体感的な彩度へ寄せます。一方、検出後の処理は色差ベクトルの方向と輝度を維持し、Threshold、Ratio、Knee、Amount から再現可能な結果を生成します。

## D-012: 製品版に検出モード切り替えを設けない

- Status: Decided
- Date: 2026-06-22

Signal、Relative、Perceptual などのモード切り替えは、Threshold の意味と操作感を複雑にします。開発中の比較実験には複数方式を使用できますが、製品版は検証で選んだ単一方式を採用します。

## D-013: 色相による圧縮量の補正を行わない

- Status: Decided
- Date: 2026-06-22

赤、緑、青、マゼンタなど、色相ごとに Threshold や圧縮量を変えません。同じ検出彩度を持つ色は、色相に関係なく同じ比率で圧縮します。

目標は、ベクトルスコープ上で同じ距離にある色が、同じ設定によって等しい割合で中心方向へ移動することです。

ここでいう「知覚寄り」は、人間が特定の色相を強く感じることへの補正ではなく、主に明るさの違いによって彩度判定が変わりすぎないことを指します。

## D-014: Resolve ベクトルスコープを色相中立性の評価基準とする

- Status: Decided
- Date: 2026-06-22

通常の DaVinci Resolve ベクトルスコープ上で、同じ半径にある異なる色相が、同じ設定によって同じ割合だけ中心へ移動することを目標とします。

評価時にはスコープ設定、入力色空間、表示変換、信号レベルを固定します。

## D-015: Threshold を soft-knee の中心とする

- Status: Decided
- Date: 2026-06-22

Threshold は圧縮が完全に始まる境界ではなく、soft-knee 遷移範囲の中心を表します。

Knee は遷移範囲の全幅とします。

```text
knee_start = Threshold - Knee / 2
knee_end   = Threshold + Knee / 2
```

- `knee_start` 以下は無変換。
- Knee 内では圧縮率が滑らかに増加。
- `knee_end` 以上では指定 Ratio のカーブへ完全移行。

UI 数値、処理式、グラフ表示でこの定義を統一します。

## D-016: Ratio は一般的なコンプレッサー比とする

- Status: Decided
- Date: 2026-06-22

Knee 上端より高い領域では、Threshold 超過量を Ratio で除算します。

```text
compressed = Threshold + (input - Threshold) / Ratio
```

- `1:1`: 無変換
- `2:1`: Threshold 超過量を 1/2 にする
- `4:1`: Threshold 超過量を 1/4 にする
- `10:1`: 強い圧縮
- `Infinity:1`: 彩度リミッター

## D-017: Infinity Ratio は彩度リミッターとして動作する

- Status: Decided
- Date: 2026-06-22

`Infinity:1` では、Knee 上端以降の出力彩度を Threshold に固定します。Knee が 0 の場合は Threshold で hard limit し、Knee が 0 より大きい場合は上限へ滑らかに接続する soft limiter とします。

これは RGB チャンネルを個別にクリップする処理ではありません。色差ベクトルの長さだけを制限し、色相方向と輝度は維持します。

## D-018: Limiter は Ratio スライダーの最大位置で選択する

- Status: Decided
- Date: 2026-06-22

独立した Limiter checkbox は設けず、Ratio スライダーの最大位置を `Infinity:1` として内部処理します。

DCTL の標準数値スライダーでは、最大位置の数値表示だけを `Infinity` に置き換えられない可能性が高いため、UI ラベル、グラフ、ドキュメントで最大位置が Limiter であることを明示します。

初期仕様では Ratio の範囲を `1.0-20.0` とし、最大値 `20.0` を内部的に `Infinity:1` として扱います。

UI ラベルは `Ratio (Max = Limit)` とします。最大位置直前から Limiter への操作感は、DCTL 試作後に Resolve 上で確認します。

## D-019: 初期版から主要6系統の入力色空間へ対応する

- Status: Decided
- Date: 2026-06-22

初期版の Input Color Space は以下を対象とします。

- DaVinci Wide Gamut / Intermediate
- Rec.709 Gamma 2.4
- Rec.709 Scene
- ACEScct / AP1
- ACEScg / AP1 Linear
- ARRI LogC3 / ARRI Wide Gamut 3
- ARRI LogC4 / ARRI Wide Gamut 4

各入力は、対応する transfer function と primaries を使って内部共通空間へ変換します。単に Log カーブだけを外し、異なる RGB 色域の数値を同一視する実装にはしません。

Linear 入力は `ACEScg / AP1 Linear` として定義します。

ARRI モードでは LogC3 または LogC4 のカーブだけを指定するのではなく、必ず対応する AWG3 または AWG4 と組み合わせます。

- LogC3: transfer function
- AWG3: RGB primaries / gamut
- LogC4: transfer function
- AWG4: RGB primaries / gamut

内部変換では、Log カーブを Linear 化した後も AWG の色域情報を保持し、共通処理空間へ行列変換します。

## D-020: Linear 入力は ACEScg / AP1 Linear とする

- Status: Decided
- Date: 2026-06-23

曖昧な `Linear` モードは設けず、`ACEScg / AP1 Linear` と明記します。

ACES には主に次の Linear encoding があります。

- `ACES2065-1`: AP0 Linear。交換・保存を主目的とする
- `ACEScg`: AP1 Linear。画像演算、CG、コンポジット向け

Press Machine では演算用途に適した ACEScg を採用します。ACEScct も AP1 primaries を使用するため、ACEScct 入力から ACEScg への変換では primaries 変換は不要で、transfer function の解除だけを行います。

## D-021: Rec.709 Gamma 2.4 と Rec.709 Scene の両方へ対応する

- Status: Decided
- Date: 2026-06-23

Input Color Space では以下を別モードとして用意します。

- Rec.709 / Gamma 2.4
- Rec.709 / Scene

両者は同じ Rec.709 primaries を使用しますが、信号の伝達特性と scene/display referred の扱いが異なります。内部変換関数を分離し、同じものとして扱いません。

## D-022: LogC3 は EI 800 固定とする

- Status: Decided
- Date: 2026-06-23

Press Machine の `ARRI LogC3 / AWG3` モードは EI 800 の scene-linear exposure factor 用 LogC3 curve として実装します。EI 選択 UI は設けません。

理由:

- DaVinci Resolve の一般的な CST では `ARRI LogC3` が単一 Gamma 項目として扱われ、EI 選択を要求しない。
- ARRI は異なる EI の素材へ単一変換を使用する場合、EI 800 用変換を推奨している。
- EI UI を追加すると、Press Machine の本来の彩度圧縮操作から外れる。

ARRIRAW の現像や EI メタデータ処理は Press Machine の責務外です。Press Machine は、すでに `LogC3/AWG3` として渡された RGB 信号を処理します。

## D-023: 彩度検出は Resolve ベクトルスコープ基準とする

- Status: Decided
- Date: 2026-06-23

通常の信号領域では、DaVinci Resolve のベクトルスコープ中心からの距離に対応する色差半径を彩度検出値とします。

- 明るさによる彩度の重み付けは行わない。
- 同じスコープ半径には、色相や明るさに関係なく同じ gain reduction を返す。
- 明るさは黒付近の誤反応を抑制するためだけに使用する。
- 圧縮後はスコープ中心へ向かって色差半径を縮小し、色相角を維持する。

ここでいう「知覚寄り」は色相別の知覚補正ではなく、ユーザーがResolveのスコープで確認できる実用的な彩度尺度を意味します。

## D-024: Black Protect を ON/OFF 可能にする

- Status: Decided
- Date: 2026-06-23

UI に `Black Protect` checkbox を追加します。

- ON: 黒付近では彩度圧縮の検出結果を滑らかに弱める。
- OFF: 黒付近を含め、通常領域と同じ彩度基準で処理する。
- Default: ON

初期版では保護範囲と遷移幅を内部固定値とし、専用の強度または範囲スライダーは設けません。実画像テストで固定値では不足すると判明した場合のみ、追加 UI を再検討します。

## D-025: Black Protect は最小限の範囲とする

- Status: Decided
- Date: 2026-06-23

Black Protect は、完全な黒および黒に近い領域の微小色差・カラーノイズだけを対象とします。

- 暗い服、暗い有彩色、夜景、ネオンなどは通常の圧縮対象とする。
- 深いシャドウ全体を保護しない。
- 保護の解除は滑らかに行い、輝度境界を見せない。

具体的な内部閾値は、共通処理空間とテスト信号を確定した後に決めます。

## D-026: Amount は彩度減少量に対して線形とする

- Status: Decided
- Date: 2026-06-23

Amount は未処理の入力彩度と完全圧縮後の彩度を線形補間します。

```text
final_saturation =
    input_saturation
    + Amount * (compressed_saturation - input_saturation)
```

- `Amount = 0`: 完全バイパス
- `Amount = 0.5`: 完全適用時の彩度減少量の半分
- `Amount = 1`: 完全適用

Amount にカーブ補正、指数変換、対数変換を加えません。UI 値と実際の gain reduction を直線的に対応させます。

## D-027: Amount UI は 0-100 表示とする

- Status: Decided
- Date: 2026-06-23

Amount の UI 範囲は `0-100` とし、百分率として操作します。内部では次のように `0.0-1.0` へ変換します。

```text
amount_normalized = Amount / 100
```

表示単位と内部単位は異なりますが、変換は単純な比例であり、操作感と実際の gain reduction は線形です。

## D-028: Threshold UI は 0-100 とする

- Status: Decided
- Date: 2026-06-23

Threshold は Resolve ベクトルスコープの基準半径を `0-100` として表示します。

- `0`: スコープ中心
- `100`: 基準外周
- UI と内部正規化の対応は線形

100を超える入力彩度はクランプしません。Thresholdを100より高く設定できないだけで、入力彩度100超もRatioに従って処理します。

例として Threshold 100、入力彩度160の場合:

- `1:1`: 160
- `2:1`: 130
- `4:1`: 115
- `Infinity:1`: 100
