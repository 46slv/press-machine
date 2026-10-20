# Changelog

## Unreleased

### Added

- 彩度圧縮専用ツールとしての新規要件定義。
- アルゴリズム、UI、グラフ、設計判断、未決事項の開発文書。
- 旧版からの移行方針。

### Changed

- Press Machine の責務を彩度圧縮に限定。
- 効果量 UI を `Amount` 一つに整理し、`Mix` を要件から削除。
- 明るさではなく相対的な彩度を圧縮判断に使う方針へ変更。
- 複数入力色空間を内部変換で扱う方針へ変更。

### Removed

- 新版のコア仕様から Density、Makeup、Luma processing、Gamut Limit を除外。
- `Mix` パラメータを削除。
