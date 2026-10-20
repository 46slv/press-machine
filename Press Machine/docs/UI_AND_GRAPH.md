# UI and Graph Design

## 1. 推奨 UI

| Parameter | 推奨範囲 | Default | 意味 |
| --- | ---: | ---: | --- |
| `Amount` | 0-100 | 100 | 彩度減少量の適用率 |
| `Threshold` | 0-100 | 未決 | soft-knee 中心となるスコープ彩度 |
| `Ratio` | 1-20 | 4.0 | Threshold 超過分の圧縮比。最大位置は Limit |
| `Knee` | 0-1 または Threshold と同単位 | 未決 | soft-knee の全幅 |
| `Input_Color_Space` | combo | 未決 | 入力信号の色空間 |
| `Black_Protect` | checkbox | ON | 黒付近の彩度検出を抑制 |

診断表示を採用する場合:

| Parameter | Type | Default | 意味 |
| --- | --- | --- | --- |
| `Show_Graph` | checkbox | OFF | 圧縮カーブを画像上へ表示 |

## 1.1 Black Protect

Black Protect は彩度を下げる処理ではなく、黒付近でコンプレッサーの検出量を弱める機能です。

- ON: 固定された黒レベル範囲で効果量を 0 から 1 へ滑らかにフェードする。
- OFF: フェード係数を常に 1 とする。

初期版では範囲スライダーを設けません。

固定範囲は最小限とし、ほぼ黒の微小色差だけを除外します。

## 2. Amount

効果量スライダーは Amount のみにします。

Amount は完全圧縮結果と未処理の彩度量を線形補間する案を第一候補とします。

```text
final_saturation = input_saturation
                 + Amount * (compressed_saturation - input_saturation)
```

この定義では Amount を 0 から 1 へ動かしたとき、実際に減少する彩度量が直線的に増えます。`Amount = 0` では入力を直接返します。

この仕様は決定済みです。Amount のスライダー自体に感度カーブを追加しません。

UI は百分率として `0-100` を表示し、内部では `Amount / 100` を使用します。

## 3. Threshold の表示単位

Threshold は Resolve ベクトルスコープの基準半径を `0-100` として表示します。スライダーには指数、対数、三乗などの感度マッピングを加えません。

入力彩度自体は100でクランプしません。100を超える広色域信号も、ThresholdとRatioに基づいて処理します。

## 4. Knee の定義

Threshold は soft-knee の中心として定義します。Knee は「半幅」ではなく「全幅」です。

```text
Knee lower = Threshold - Knee / 2
Knee upper = Threshold + Knee / 2
```

この定義は audio compressor の一般的な説明と合わせやすく、グラフ上にも帯として表示できます。

- Knee 下端までは無変換。
- Threshold では遷移の中央。
- Knee 上端以降は指定 Ratio の傾き。

## 4.1 Limiter 表示

`Infinity:1` は彩度リミッターです。

- Knee が 0: Threshold で折れる hard limiter
- Knee が 0 より大きい: Threshold 上限へ滑らかに接続する soft limiter

グラフでは、Knee 上端以降が水平になります。

DCTL UI では Ratio スライダーの最大値 `20.0` を Limiter と解釈します。

標準の数値スライダーでは最大位置だけを文字列 `Infinity` と表示できない可能性が高いため、次の方法で意味を明示します。

- UI ラベルを `Ratio (Max = Limit)` とする
- グラフ上では最大位置で水平な limiter curve を表示
- README と操作説明に最大位置の意味を記載

スライダーが最大値として表示する数値は、内部的には Ratio として使わず `inverse_ratio = 0` とします。

## 5. グラフの目的

グラフはルックを作る装飾ではなく、以下を確認する診断表示とします。

- Threshold の位置
- Knee の範囲
- Ratio と Amount が作る傾き
- 入力彩度に対する出力彩度
- identity line との差

## 6. 推奨グラフ仕様

- X 軸: input saturation
- Y 軸: output saturation
- identity line: 灰色
- compression curve: 明るい緑またはシアン
- Threshold: 細い縦線
- Knee: 半透明相当の暗い帯、または上下境界線
- 背景: 半透明のニュートラルグレー
- 配置: 左下
- サイズ: 画面短辺を基準に約 25-30%
- `Amount` を反映した最終的な彩度カーブを表示する

## 7. 軸レンジ

固定 `[0, 1]` または `[0, 2]` は作業空間によって不足または過大になります。

候補:

1. 固定レンジ
   実装が簡単で比較しやすい。

2. Threshold 基準レンジ
   `x_max = max(base_range, Threshold + 2 * Knee)` など。UI 操作で軸が動き、比較しにくくなる。

3. 作業空間ごとの固定レンジ
   working domain を固定する場合に最も実用的。

初期推奨は 3 です。working domain 決定後、テストパッチの sat 分布から固定レンジを決めます。

## 8. 実装上の必須条件

- 圧縮関数を `compress_saturation()` のような helper にまとめる。
- メイン処理とグラフ描画の両方から同じ helper を呼ぶ。
- identity line と curve は同じ軸正規化を使う。
- 線幅はピクセル解像度に対して安定するよう正規化する。
- グラフ OFF 時の追加計算を最小限にする。

## 9. 検討中の追加表示

- 現在の Threshold 数値
- Knee 境界
- 代表入力点の gain reduction
- false-color による圧縮量表示

初期版では文字描画と false-color は含めず、カーブ、恒等線、Threshold、Knee のみを推奨します。
