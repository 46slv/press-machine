# Migration Notes

## 1. 旧版の位置付け

旧版は `press machime` フォルダに保存されています。新版の設計資料や実装とは分離し、参照用として残します。

## 2. 引き継ぐもの

- RGB から luma と chroma を分離する基本構造
- chroma ベクトル長を彩度量として扱う考え方
- chroma 方向を維持した再構成
- `sat_in` 極小時のゼロ除算ガード
- Mac/Metal を意識した DCTL 記述
- 圧縮カーブのグラフ表示という考え方
- グラフと処理の軸スケールを一致させる教訓
- chroma 分離前に luma をクランプしないという教訓

## 3. 廃止するもの

- `Pre_Saturation`
- `Dynamic_Density`
- `Makeup`
- `Luma_Density_Power`
- `Luma_Density`
- `Sat_Density`
- `Density_Comp`
- `Density_SatBoost`
- `Gamut_Limit`
- `Threshold^3` の暗黙マッピング
- `1 + log(Ratio)` の独自 ratio mapping

## 4. 再設計するもの

- `Amount` の意味
- soft-knee の数式
- Threshold と Knee の範囲
- working domain
- luma weights
- グラフの軸レンジ
- 色空間変換を DCTL 内に持つかどうか

## 5. 互換性

新版は旧版プリセットとのパラメータ互換を目標にしません。

名称は同じ Press Machine を継続しますが、アルゴリズムと UI は新規設計として扱います。

