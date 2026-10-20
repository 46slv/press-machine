# Press Machine

DaVinci Resolve 用の彩度コンプレッサー DCTL を開発するためのプロジェクトです。

Press Machine は、一定以上の彩度だけを滑らかに圧縮し、低彩度域、色相、輝度感をできる限り維持することを目的とします。旧版に含まれていた Density、Makeup、Gamut Limit などのルック生成機能は、新版のコア仕様には含めません。

製品の中核となる定義:

> 見た目の彩度が高すぎる部分を見つけ、信号として正確かつ予測可能に圧縮する。

## 現在の段階

要件定義およびアルゴリズム設計中です。DCTL の実装はまだ開始していません。

## ドキュメント

- [`docs/PRODUCT_REQUIREMENTS.md`](docs/PRODUCT_REQUIREMENTS.md): 製品目的、要件、非目標、受け入れ条件
- [`docs/ALGORITHM.md`](docs/ALGORITHM.md): 数学モデルと安全処理
- [`docs/UI_AND_GRAPH.md`](docs/UI_AND_GRAPH.md): UI パラメータとグラフ表示案
- [`docs/DECISIONS.md`](docs/DECISIONS.md): 決定済み事項と設計判断
- [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md): 今後一緒に決める項目
- [`docs/MIGRATION_NOTES.md`](docs/MIGRATION_NOTES.md): 旧版から引き継ぐ点、廃止する点
- [`dev/WORKLOG.md`](dev/WORKLOG.md): 開発メモと作業履歴
- [`CHANGELOG.md`](CHANGELOG.md): バージョン単位の変更履歴

## 基本方針

1. 彩度圧縮だけに責務を限定する。
2. `Mix = 0` と `Amount = 0` は厳密に元画像を返す。
3. Threshold 未満は原則として変化させない。
4. 色差ベクトルの方向を維持し、色相回転を避ける。
5. luma は再構成時まで変更しない。
6. NaN、Inf、ゼロ除算を防ぐ。
7. 処理とグラフで同じ圧縮関数を使用する。
8. 圧縮対象の検出は体感的な彩度へ寄せ、実際の減衰は機械的かつ再現可能にする。
