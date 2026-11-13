# PressMachine Fusion API Toolkit

既存の **compiled PressMachine v2.0** を、DaVinci Resolve の標準 Fusion API から読み取り、パラメーターを一つずつ変更する Python ツールです。新しいプラグイン、GUI、常駐サーバーは追加しません。

対象は Fusion コンポジション内の次の RegID です。

`ofx.com._46slv.PressMachine.v2.skinaxis`

**Color ページに置かれた既存 OFX ノードを、この方法で直接読み書きすることはできません。** Color ページ用の汎用 OFX 操作 API を提供するものではありません。

## できることと制限

- 現在のプロジェクト、タイムライン、再生ヘッド上の動画クリップに関連付いた既存コンポジションと、対象ツールを列挙します。
- 固定スキーマにある 25 個の処理パラメーターを読み取ります。
- 明示した一つのパラメーターに、最大一回だけ `SetInput` を呼びます。変更前の全 25 値と、変更後の対象値・残り 24 値を確認します。
- コンポジションやツールの作成、接続変更、ページ移動、プロジェクト／タイムライン切り替え、画像取得、レンダー、保存、リセット、自動復旧、自動再試行は行いません。
- Source 画像、Fusion 共通コントロール、Fdb、未知の ID は書き込み対象外です。画像データや共通コントロールの値も読みません。
- 同じ Resolve を別の人・スクリプト・AI が同時に操作しないでください。標準 API に原子的な比較・更新トランザクションはありません。二重の直前確認で危険を減らしますが、競合を完全には防げません。

## 動作条件

1. DaVinci Resolve と対応する Python 実行環境、公式の `DaVinciResolveScript` モジュールが必要です。この配布物は Python 3.12 でオフライン検証しました。
2. compiled PressMachine v2.0 が既にインストールされ、対象の **Fusion** コンポジション内に置かれている必要があります。
3. Resolve で対象のプロジェクト、タイムライン、クリップを開き、プレビューが落ち着くのを待ちます。プロジェクトのレンダーは停止していること、対象コンポジションがロックされていないことが必要です。
4. 作業前に、必要な変更の保存・バックアップを本人の通常の手順で行ってください。このツール自体は保存しません。

外部スクリプトからの接続可否は Resolve の版・実行環境・既存設定に依存します。CLI は通常の公式インストール位置だけを確認し、インストール、設定変更、権限変更、サーバー起動はしません。接続できない場合はそこで止まります。既に取得済みの Resolve ハンドルを利用する方法は後述します。

公式モジュールの検索位置:

- Windows: `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules\DaVinciResolveScript.py`
- macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/DaVinciResolveScript.py`
- Linux: `/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py`

## 最短の使い方: Pre を 50 → 60 にする

以下は PowerShell 用です。配布フォルダーを任意の場所に展開し、その中で実行してください。`python` の代わりに、公式 SDK と互換性のある Python の実行ファイルを指定しても構いません。`pip install` は不要です。

### 1. 既存の対象を列挙する

```powershell
python .\pressmachine_fusion.py list --out .\targets-01.json
```

出力の `context` でプロジェクト・タイムライン・クリップの名前と ID、再生ヘッド位置を確認します。`targets` の中から、変更したい対象の次の値を控えます。

- `association_name`: クリップ側が持つコンポジションの関連付け名
- `tool_name`: そのコンポジション内の正確なツール名
- `tool_id`: 今のセッションで観測したツール ID
- `frame`: 読み書きするコンポジションの現在フレーム

**`comp_display_name` は説明用です。選択に使わないでください。** Fusion の `COMPS_Name` とクリップ側の関連付け名は、特にローカライズ環境では一致しないことがあります。

`targets` が空なら、このクリップ内に対応する既存 Fusion ツールが見つかっていません。Color ページの同名ノードを代わりに操作したり、新しいコンポジションを自動作成したりはしません。

### 2. 全 25 値を読み、変更前のスナップショットを保存する

次の名前と ID は例です。必ず **自分の `list` 結果** に置き換えます。

```powershell
python .\pressmachine_fusion.py inspect --targets .\targets-01.json --comp "Composition 1" --tool "PressMachinev201" --tool-id 7 --out .\before-01.json
```

`state.values.pm_pre` が本当に `50` で、意図した対象かを確認します。期待値を合わせるために JSON を編集してはいけません。値が違う場合は、変更の意図を確認し直してください。

### 3. 同じ対象・フレームのまま、一回だけ変更する

スナップショット取得から **300 秒以内** に実行します。途中で再生ヘッドや対象を変えた場合は、最初から読み直します。

```powershell
python .\pressmachine_fusion.py set --snapshot .\before-01.json --param pm_pre --expect 50 --value 60 --journal .\set-pre-01.jsonl
```

正常に読戻しを確認すると、`outcome` は `success_numeric_only` になります。確認する項目:

- `set_input_attempted: true`
- `numeric_readback_verified: true`、`readback: 60`
- `other_parameters_unchanged: true`
- `undo_closed: true`、`journal_complete: true`
- `changes` に `pm_pre` だけがある

`SetInput` や Undo 関数が `None` を返すこと自体は失敗ではありません。新しい値の読戻しと残り 24 値の比較で判定します。`SetInput` に伴って通常の Fusion プレビューが動き始めても、変更後の読み取りは許可します。プロジェクトのレンダー、ロック、対象の変化は別途検出します。

この結果は **数値の読戻し確認** です。画の正しさや色の正確さ、保存後の復元を保証しません。このコマンドは画像を取得せず、レンダーも保存も行いません。

## その他のパラメーター

正確な ID・型・範囲・選択肢は `schema/press_machine_v2.json` を参照してください。スキーマの内容と SHA-256 を固定しており、変更されたスキーマは拒否します。

- `double`: 範囲内の有限な数値。文字列、NaN、Infinity、bool は不可です。`step` は UI の刻みであり、このツールは値を自動丸めしません。
- `choice`: **0 始まりの整数インデックス**。ラベル文字列や `1.0`、小数は不可です。例えば `pm_hue_points_index` のインデックス `4` は、表示上の「6」です。
- `bool`: 整数 `0` / `1`、または JSON の `false` / `true`。`1.0` は不可です。
- 読み取りでは、Host の Number 型が返す整数相当の浮動小数も受け入れます。
- 範囲内でも、Host 側の実際の許容範囲が狭ければ拒否します。

API は各 ID に対応していますが、**既存の実機で書き込みと画の変化を確認できているのは Pre だけ**です。他の ID まで実機検証済みとは扱わないでください。

## Fusion に入ってくる色を合わせる

`pmi_ig`（Input Primaries）と `pmi_it`（Input Transfer）は、**PressMachine の Source に実際に届く画像の色域・伝達特性** に合わせます。プロジェクトの表示設定、ビューアーの見え方、タイムラインの色空間名だけから決めないでください。MediaIn、前段ノード、Resolve のカラーマネージメントが関係します。このツールはそれらを判定も変更もしません。

入力のスキーマ既定値は DWG D65 / DaVinci Intermediate ですが、現在の Fusion 入力がその状態だという証拠にはなりません。既知の入力素材と前段の変換を確認してから使います。出力の `Same as Input` は、指定した入力設定に従う選択肢です。ビューアー用の変換を逆算する機能ではありません。

今回の数値 API 検証は色校正ではありません。Pre の画の差分が確認できても、入力・出力の色設定が正しいという結論にはなりません。

## 止まったとき

| outcome / 終了コード | 意味 | 次にすること |
| --- | --- | --- |
| `success_numeric_only` / 0 | 対象値の読戻しと、残り 24 値の不変を確認 | 必要に応じて本人が画と保存を確認 |
| `blocked` / 2 | 既知の前提条件で停止。`SetInput` は呼んでいない | 理由を確認し、状態を整えて新しいファイル名で読み直す |
| `partial` / 3 | 読戻しはできたが、要求値・他の値・返り値などに不一致がある | 手を止め、Host と記録を確認。自動で戻さない |
| `uncertain` / 4 | 変更・Undo・対象・記録の完全性を確定できない | **再実行しない**。Host と記録を確認してから判断 |

よくある停止理由:

- 別のプロジェクト／タイムライン／クリップ、名前の変更、再生ヘッド移動、コンポジションのフレーム変更。
- 取得から 300 秒超過、将来日時、不足した値、手編集された JSON、重複キー、非有限数。
- 対象値だけでなく、別のパラメーターや状態が取得後に変わった。
- 対象が無効、接続済み、式やキーフレーム付き、または状態を確認できない。
- 25 個のうち欠けた／重複した入力、異なる RegID、異なるツール ID。
- プロジェクトのレンダー、書き込み前のコンポジションのレンダー、ロック。
- 同じ出力ファイル名が既に存在する。

`inspect` / `list` / ジャーナルは既存ファイルを上書きしません。書き込みを開始するスナップショットには `before-01.json.claim` のような使用済み印を排他的に作ります。印があるスナップショットは別名のジャーナルでも再利用できません。解除のために印を消すのではなく、実際の状態を確認して **新しいスナップショット** を取得してください。

ジャーナルは各段階で flush / fsync します。`before_set_input` まであって最終結果がない場合、その直後に変更された可能性があります。プロセス停止・通信例外・ディスク障害のあとに同じ命令を繰り返さないでください。記録と画面を確認するための情報を残し、自動ロールバックは行いません。

## 既存の Resolve ハンドルを使う

既に Resolve のスクリプティング環境があり、`resolve` を取得済みなら、新しい SDK 接続を作らず同じハンドルを渡せます。モジュールの import 自体には接続や Host 操作の副作用はありません。

配布フォルダーを Python の import 対象にしたうえで、まず読み取りだけを行います。

```python
import pressmachine_fusion as pm

listing = pm.list_targets(resolve)
print(listing)
# 次の3値は、上の結果を確認して置き換える。
selection = pm.select_target(listing, "Composition 1", "PressMachinev201", 7)
snapshot = pm.inspect_target(resolve, selection)
pm.save_snapshot(snapshot, "before-02.json")
```

本人が対象と値を確認し、同じ操作担当が、別の人・AI と重複しない状態で必要なときだけ実行します。

```python
result = pm.set_once(resolve, "before-02.json", "pm_pre", 50, 60, "set-pre-02.jsonl")
print(result)
```

JSON から Python コードやモジュールを指定する仕組みはありません。関数は `Blocked`、ファイル衝突などの例外、または明示的な `outcome` を返します。例外を捕まえて自動再試行するループには入れないでください。

## 検証範囲とファイル

- `pressmachine_fusion.py`: import 可能な本体と CLI
- `schema/press_machine_v2.json`: production v2 の固定スキーマの完全コピー
- `test_pressmachine_fusion.py`: 合成 SDK オブジェクトを使うオフライン試験
- `validate_offline.py`: コンパイル、モック試験、相対パス付きハッシュ記録の生成
- `OFFLINE_VALIDATION.json`: この配布物のオフライン検証結果。実機試験を主張しない記録
- `HOST_VERIFICATION.json`: この配布物の、範囲を限定した実機確認結果。実環境の名前・ID・素材パスを除いた要約

```powershell
python .\validate_offline.py --out .\offline-check-02.json
```

**この配布物の実機確認:** 2026-11-08、既に接続済みの Resolve ハンドルと既存の Fusion 検証対象を使い、対象列挙・選択・全 25 値の読み取り・スナップショット保存・Pre の **50 → 60 の一回変更** を確認しました。結果は `success_numeric_only`、読戻し `60`、他の 24 値は不変、Undo 終了確認済みです。`SetInput` の返り値は `None` でした。製品のソースとバイナリーは変更していません。

この実機確認では、CLI による新規接続、画像取得・レンダー、プロジェクト保存は行っていません。**この配布物単体による画像応答、外部 CLI 接続、保存・再起動後の復元、色校正、Color ページ直接操作、Fdb は未検証** です。既存ハンドルで成功したことと、利用者の環境で外部 CLI が接続できることは別です。

既存の別検証では、production v2 の Fusion 経路で全 25 処理 ID を読めること、Pre の **100 → 50** の一回変更と数値の読戻し、同一フレームの出力画像の変化を確認しています。これは **経路の成立を示す先行検証** であり、この配布物の画像応答試験の代用にはしません。

RegID の一致だけでは、ロード中のバイナリーの版やハッシュまで識別できません。想定した production v2 のインストールを使用してください。製品ソース、コア、バイナリーはこの配布物では変更しません。

生成したスナップショットやジャーナルには、その環境のプロジェクト・タイムライン・クリップの名前と ID が入ります。手元の作業記録として扱い、確認せず公開・共有しないでください。配布物に実環境のキャプチャや個人の素材パスは含めていません。
