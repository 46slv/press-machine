# Algorithm Design

## 1. 推奨する初期アルゴリズム

初期版では、標準的な audio compressor に近い ratio の定義を採用します。旧版の `1 + log(Ratio)` マッピングは使いません。

hard-knee の基本式は次です。

```text
x = sat_in
T = Threshold
R = effective_ratio

x <= T: y = x
x >  T: y = T + (x - T) / R
```

`R = 1` は恒等変換です。`R` が大きいほど Threshold より上の傾きが小さくなります。

`R = Infinity` の場合:

```text
x <= T: y = x
x >  T: y = T
```

これは色差ベクトル長に対する saturation limiter です。RGB チャンネルを個別にクリップする処理ではありません。

## 2. Amount の推奨定義

`Amount` は入力彩度と完全圧縮後彩度の間を線形補間します。

```text
sat_final = sat_input + Amount * (sat_compressed - sat_input)
```

- `Amount = 0`: 完全バイパス
- `Amount = 0.5`: gain reduction の半分
- `Amount = 1`: Ratio を完全適用

指数、対数、smoothstep などによる Amount 自体の再マッピングは行いません。

## 3. Soft Knee

推奨案は、audio compressor で一般的な二次補間です。

Knee の全幅を `K` とした場合:

```text
lower = T - K / 2
upper = T + K / 2
```

```text
x < lower:
    y = x

x > upper:
    y = T + (x - T) / R

otherwise:
    d = x - lower
    y = x + (1 / R - 1) * d^2 / (2K)
```

この式は hard-knee の上下の式へ滑らかにつながり、一次微分も連続します。

`K <= epsilon` の場合は hard-knee に切り替えます。

`R = Infinity` では `1 / R = 0` として扱えます。

```text
x < lower:
    y = x

x > upper:
    y = T

otherwise:
    d = x - lower
    y = x - d^2 / (2K)
```

これにより Knee 下端の傾き 1 から、Knee 上端の傾き 0 へ滑らかに移行します。

## 4. RGB の分解と再構成

```text
Y = dot(rgb, luma_weights)
neutral = (Y, Y, Y)
chroma = rgb - neutral
sat_in = sqrt(max(dot(chroma, chroma), 0))
```

圧縮後:

```text
scale = sat_out / max(sat_in, epsilon)
chroma_out = chroma * scale
wet_rgb = neutral + chroma_out
```

`sat_in <= epsilon` の場合は `wet_rgb = rgb` とします。

## 5. Saturation Metric の重要な論点

### A. 絶対色差長

```text
sat = length(rgb - Y)
```

ユーザーの元要件に忠実で、実装が単純です。一方、scene-linear では露出が上がると同じ chromaticity でも sat が増えます。そのため、明るい色ほど強く圧縮されます。

### B. Y 正規化色差長

```text
sat = length(rgb - Y) / max(abs(Y), epsilon)
```

露出に対して比較的安定しますが、暗部と Y が 0 に近い領域で不安定になりやすく、追加の toe 制御が必要です。また、元要件の「色差ベクトルの長さ」から意味が変わります。

### C. ハイブリッド正規化

```text
sat = length(rgb - Y) / max(abs(Y), floor)
```

暗部の暴走を抑えながら露出依存を減らせますが、`floor` という新しい固定値または UI が必要になります。

### 初期推奨

まず A を正しく実装して基準版とします。ただし、評価時には同じ色を複数露出で比較し、露出依存が実用上問題になるか確認します。問題が明確なら C を次の候補とします。

## 5.1 色相中立性

Detector は色相ごとの知覚感度補正を行いません。

望ましい検出量は、色相角ではなく無彩色軸からの距離だけで決まります。同じ検出半径にある色には同じ圧縮係数を返します。

```text
gain = compressed_saturation / input_saturation
chroma_out = chroma * gain
```

全色差成分へ同じ `gain` を掛けるため、処理空間内では色差ベクトルの方向が維持されます。

ただし、入力色空間ごとの変換やベクトルスコープの色差定義が異なる場合、内部尺度での等方性とスコープ上の完全な等距離変化が一致しない可能性があります。正式な評価では、使用する Resolve ベクトルスコープの表示条件を固定して検証します。

## 5.2 Scope-based Detector

彩度検出は、Resolve ベクトルスコープに対応する二次元色差平面で行います。

概念式:

```text
chroma_a = first opponent color axis
chroma_b = second opponent color axis
scope_radius = sqrt(chroma_a^2 + chroma_b^2)
```

Detector は `scope_radius` だけを Threshold、Ratio、Knee と比較します。色相角 `atan2(chroma_b, chroma_a)` は使用しません。

圧縮後:

```text
gain = compressed_radius / input_radius
chroma_a_out = chroma_a * gain
chroma_b_out = chroma_b * gain
```

これにより、Detector の色差平面では中心方向への放射状圧縮になります。

Resolve ベクトルスコープと完全に一致させるための色差行列、信号レンジ、ガンマ適用位置は実測検証で確定します。

## 6. Working Domain

RGB-Y の演算結果は、入力の符号化と色域に強く依存します。

候補:

- DCTL に scene-linear RGB が入力されることを前提とする。
- DWG/Intermediate など特定の Log working space を前提とする。
- Input Color Space UI を追加し、内部で Linear 変換する。
- Resolve の node color space 管理に任せ、Press Machine 自体は変換を持たない。

初期推奨は「変換を持たず、使用者がノード前後で作業空間を管理する」です。専用 DCTL の責務を彩度圧縮に限定でき、色空間変換コードによる誤差と保守コストを避けられます。ただし、正式にサポートする working domain は実装前に決定が必要です。

## 7. Luma Weights

色域に合わない luma weights を使うと `Y` と chroma 方向が変わります。

候補:

- Rec.709 weights 固定
- DaVinci Wide Gamut weights 固定
- AP1 weights 固定
- working space に応じて選択

Input Color Space UI を持たない場合、初期版は使用前提の working space に対応する一組へ固定するのが妥当です。

## 8. 安全処理

```text
epsilon = 1e-6
sat_sq = max(dot(chroma, chroma), 0)
sat_in = sqrt(sat_sq)
```

- `Amount <= 0`、`Mix <= 0`、`Ratio <= 1` は入力を直接返す。
- `sat_in <= epsilon` は入力を直接返す。
- `Threshold` は 0 以上に制限する。
- `Ratio` は 1 以上に制限する。
- `Knee` は 0 以上に制限する。
- `sat_out` は `[0, sat_in]` に制限し、誤差による彩度増加を防ぐ。
- RGB 自体は原則として 0-1 にクランプしない。

## 9. ガマット処理

初期版ではガマットクランプを行いません。

元の chroma 方向を縮小するだけなら、`0 <= scale <= 1` の範囲では RGB は neutral point `Y` に近づきます。通常は入力より極端な RGB を作りにくい処理です。入力が有効であれば、追加のハードクランプはむしろハイライトや広色域値を壊す可能性があります。
