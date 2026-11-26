# Press Machine 2.2.1で狙う、青灰の影とクリーム色の日向

**結論：青灰の低中間調と淡い暖色の明部を作る土台には使える。最も暗い黒を無彩色寄りに戻す処理も単体でできる。黒の深さ、ハイライトの肩、同じ明るさの肌・標識と背景の分離、カット間のマッチはResolve側に分ける。** 参照映像との一致やResolveでのこのレシピの実機A/Bは未検証。以下の数値はプリセットではない。

## 参照で見えたもの

[Ryo Ichikawa「Hello FX5 Setup.」0:50–1:05](https://youtu.be/LacjCmbb3X0?t=50) の配信区間を取得・デコードし、約0.5秒刻みのコマとショットの代表コマを観察。[先行の静止画観察](https://github.com/46slv/press-machine/blob/8afc47b6bf2a76e30fdb09a8acbc24f6d008297e/tests/satcomp-gamut-edge/look-reference-ryo-ichikawa.md) は過去に見た2枚の記述を参照し、元添付2枚の個別画素とは照合していない。時刻は本編の概算サンプル位置で、正確なカット境界ではない。

| 本編の観測コマ | シャドー／中間調／ハイライトと暖色 |
| --- | --- |
| 0:50–0:51.5 | 顔の寄り。帽子と髭の最暗部は黒に近い。肌はベージュ〜桃色、襟は赤茶。背景のぼけには青とクリーム色。 |
| 0:52–0:54 | 湾曲壁の低中間調は青灰〜スレート、路面の影は濃い青灰。入口の奥は黒に近い。壁上部に淡いクリーム色、上着にはくすんだベージュが残る。 |
| 0:54.5–0:56.5 | 標識のある街角。手前の壁と路面は青灰、木や建物の奥は黒に近い。奥の外壁は黄みのクリーム色で、小さな赤が残る。 |
| 0:57–0:59 | 青い空と白っぽい雲、ほぼ黒い電柱・電線。空の青は日陰の青とは別。ここにクリーム色の明部を無理に作らない。 |
| 0:59.5–1:04 | ビル街。ガラスの青〜シアンと黒に近い手前。前半は明るいクリーム色の外壁と小さな赤い尾灯、後半はクリーム色の面積が目立たない。後半の変化が別カットかは未確定。 |
| 1:04.5付近 | 屋内の機材。冷たい灰色と黒い奥、控えめな肌色と小さな赤橙が見える。屋外の設定をそのまま当てる根拠はない。 |

目標に一番近いのは街角と、奥に明るい外壁が見える街路。先行メモの青灰の壁・濃い青灰の路面・ベージュの保持と整合する。**最暗部までティールにしない。黄緑は明部全般の共通色ではない。** 配信抜粋のデコードは1280×720、H.264、24000/1001 fps、BT.709の色域・伝達・マトリクス、TVレンジタグ。これは配信側の信号で、元の撮影プロファイル、光源、白バランス、露出、LUT、処理順の証拠ではない。カットをまたぐ連続再生での見え方、フリッカー、カメラ原素材との比較は未確認。参照画像・動画は掲載しない。

## Resolveでの開始手順

1. **Normalize／ショットバランス。** まず正しい入力を割り当てる。RCMでタイムラインがDaVinci Wide Gamut / DaVinci Intermediateなら、Pressの入力は `DWG D65` / `DaVinci Intermediate`、出力は2項目とも `Same as Input`。表示変換はRCM側の一度だけ。非管理のYRGBでCSTを使うなら、素材プロファイル → DWG/Intermediate → 調整・Press → 目標ディスプレイ、の順でプロファイルと表示変換を明示。すでにRec.709/Gamma 2.4へ仕上がった信号に使うなら `Rec.709 D65` / `Gamma 2.4`、出力Same、追加の表示変換なし。素材の `Rec.709 OETF` と表示用 `Gamma 2.4` を同一視しない。Sony Logが実際の入力なら、素材に合う設定を確認してCST/RCMで正規化する。動画のタイトルから素材のプロファイルを決めない。
2. **露出・白バランス・黒の位置をPressの前で合わせる。** PrimariesまたはHDR Wheelsで顔・壁・日向の明るさの関係を作り、暗い壁の階調を残す。前段の露出を変えると、同じSplit値でも色が切り替わる位置が動く。明るい空や白い雲は暖色化を強制しない。黒点／トーやハイライトの肩はHDR Wheels／Custom Curvesと出力変換の担当。色を抜くことと暗くすることを別々に見る。
3. **Hueだけで影／日向の色方向を作る。** `Hue Strength=0`、`Hue Bias=0`、`Luma Pivot EV=0`、`Luma Width=1`。ランプで `Hue Angle=55`、`Luma Split=+20` を診断起点にして、下側が青方向・上側が黄方向になるか確認。合わなければ角度を回し、`−20`で向きが入れ替わることを確認。ショットではSplitを0から上げ、まずパッチの試験値より弱い量も比較する。Pivotで境目、Widthを上げて境目付近を緩める。影と日向が既に希望の色ならSplitは不要。Patternは必要時だけ少量足す。明部が黄緑へ行きすぎる、または青とクリームが同軸で決まらなければ、Splitを弱めて下記の別ノードへ。
4. **彩度と濃さは分ける。** `Pre Saturation=100`、`Makeup Saturation=100`、`Amount %=0`、`Density=0`から始める。強すぎる青・赤だけなら `Threshold=80`、`Knee %=20` のまま `Amount %=10` を単独A/B。これは色相別の調整ではなく、同じ特性の暖色にも効く。まずMakeupは100のまま。色の付いた壁にだけさらに重さが必要なら `Density Chroma=0`、`Saturation Response=2` で `Density` 正側を少しずつ足して 0 と比較。診断の `±50` は符号確認用で、推奨値ではない。肌があるカットは `Look Skin Protect` を上げて個別確認（CPU診断は70）。Pre/Comp/Makeupで肌が変わる場合だけ `Comp Skin Protect` も調整する。
5. **最暗部の色を整理し、必要な領域だけ別ノードへ。** `Highlight Desat Threshold=1` のまま（OFF）、`Shadow Desat Threshold` を0から上げ、青灰の壁より下だけ色を抜く。診断はThreshold `.16`、Knee `.09`。これらはDI(Y)の座標でIREではない。Kneeを極端に狭めず、黒い入口と青灰の壁を分けて確認。肌・ベージュ・赤い小物も同じ明るさなら影側の着色やFinal Desatに巻き込まれる。背景と同じ輝度の被写体はHSL Qualifier＋ソフトなPower Window（必要時トラッキング）でOFX適用を制限するか、限定した未処理枝を戻す。全体を暖め直すのではなく、必要なら `Hue vs Hue` / `Hue vs Sat` やHDR Wheelsの明るさ別ゾーンで、空・ガラス・外壁・小物を分ける。RGBパレードとベクトルスコープを見ながら、カットごとに強さと対象を決める。

**順番の要点：** 入力正規化・ショットバランス → Press（Hueを先に試すが、内部の演算順は固定） → 局所補正・出力の最終確認。被写体をOFXから外すマットまたは分岐はPressと同じ信号域で組む。S字や肩で見え方を作る処理を、SplitやFinalで代用しない。

## 何をどこで行うか

| OFX単体 | Resolve標準ノード／色管理 | OFXにない機能・限界 |
| --- | --- | --- |
| 輝度別の寒暖軸、任意のPattern、彩度の上側の抑制、着色した領域の濃さ、最暗部と最明部の低彩度化、肌色近傍での部分保護。 | 素材入力・WB・露出・黒点と肩、ショットマッチ、狙った色相の独立調整、Qualifier/Windowで被写体を分離して保護、出力のトーン／色域マッピング。 | Splitの両端は同じ軸の反対向きで、影と光を任意の独立2色に設定できない。肌保護は被写体の識別ではない。ピクセル単位の処理で位置、面積、時系列を使ったマッチや照明／光学拡散の再現はしない。PQ/HLG、legal/full変換、トーンマップ、自動色域クリップはない。 |

### 操作子と処理順（v2.2.1ソース）

内部はリニアDWG D65。入出力の色域と伝達は独立。色域はDWG、ARRI Wide Gamut 3 / 4、ACES AP1 CAT02、Rec.709、Rec.2020、P3 D65。伝達はDaVinci Intermediate、LogC3 EI800 Exposure、LogC4 Scene、ACEScct Reversible、Relative Linear、Gamma 2.4 / 2.2、sRGB、Rec.709 OETF。それぞれの出力には既定 `Same as Input` がある。実際に変換する場合はOFX後のプロファイルを記録し、EXRに残るカメラ注記だけで判断しない。

| グループ | ラベル：範囲／既定 |
| --- | --- |
| Sat Comp | `Pre Saturation` / `Makeup Saturation`：0–200／100中立。`Threshold`：0–100／80、`Amount %`：0–100／0、`Knee %`：0–100／20。`Comp Skin Protect`：0–100／0。 |
| Hue | `Hue Angle`：0–360°／0（肌色基準、HSV角ではない）。`Hue Pattern`：Mono / Analogous / Complementary（既定）/ Split Complementary / Triadic / Tetradic。`Hue Strength`：0–100／0。`Hue Bias`：−100–100／0。`Luma Split`：−300–300／0。 |
| Luma Curve TEST | `Luma Pivot EV`：−6–6／0。`Luma Width`：0.25–4／1。 |
| Density | `Density`：−300–300／0。`Density Chroma`：−100–100／0。`Saturation Response`：1–4／2。`Shadow Protect` / `Highlight Protect` / `Look Skin Protect`：0–100／0。`Shadow Range` / `Highlight Range`：0–100／50。`Density Bypass`：OFF/ON／OFF。 |
| Final Desaturation | すべて0–1。`Shadow Desat Threshold`：0（OFF）。`Highlight Desat Threshold`：1（OFF）。両 `Desat Knee`：0.18。 |

- 正規化された元入力で `Y_ref` と肌マスクを求める。**Pre → Comp → Makeup** の変化を `Comp Skin Protect`、**Pattern → Bias/Split → Density** の変化を `Look Skin Protect` でそれぞれ部分的に戻す。その後でFinal Desaturationと出力符号化。`Threshold`は彩度モデルのUI値でスコープ上の%ではない（圧縮が有効なときUI 80→内部25）。Amount 0またはThreshold 100はCompだけOFF、Makeupは逆圧縮ではない。
- `Hue Strength=0` はPatternだけOFF。`Hue Bias=0` なら `Luma Split>0` はPivotの上をAngle、下をAngleの反対へ寄せ、負側は逆。Biasは全体の駆動に足され、色の反転位置を動かしうる。Pivotは元入力のリニアXYZ `Y=0.18×2^EV`、Widthは付近の応答を変える。どちらも明るさを変える操作ではない。`Split Complementary`は色相アンカーの配置で、輝度分割とは別。複数アンカーは境界に近い既存色を弱めることがあり、Bias/SplitやMonoはグレーにも色を作れる。
- `Density`はHue後の彩度に応じ、通常域で正が暗化、負が明化。`Density Chroma`と `Shadow/Highlight Protect/Range` はDensity段だけに作用し、`Density Bypass`で止まるのもその段だけ。`Look Skin Protect`は名前がDensity欄でもHueにも効く。FinalはLook後の `DI(Y)` で色差を減らす。黒の深さを下げず、肌保護もFinalまでは届かない。有効なShadowはThreshold以上を保持し、Kneeの区間を経て下端 `max(0, T−K)` 以下で無彩色化。有効なHighlightはThreshold以下を保持し、Kneeの区間を経て上端 `min(1, T+K)` 以上で無彩色化。Knee 0では影はT未満、明部はT超で無彩色化。両マスクの保持率は乗算。`Graph`は別の既定OFFのHUDフラグで、実画素のスコープでも書き出しオーバーレイでもない。

根拠（固定コミット）: [30処理操作子](https://github.com/46slv/press-machine/blob/9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4/parameters/press_machine_v3_curve.json) · [色管理の入口](https://github.com/46slv/press-machine/blob/9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4/core/press_machine/PixelPipeline.dctlh#L1-L11) · [Hue・処理順](https://github.com/46slv/press-machine/blob/9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4/core/press_machine/VNextHue.dctlh#L76-L146) · [Pivot/Width](https://github.com/46slv/press-machine/blob/9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4/core/press_machine/HueLumaCurve.dctlh#L5-L28) · [Comp/Density/Final](https://github.com/46slv/press-machine/blob/9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4/core/press_machine/PixelMath.dctlh#L1423-L1477) · [HUDと別のGraph操作子](https://github.com/46slv/press-machine/blob/9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4/adapters/ofx/generate_descriptors.py#L25-L40)。

## 試した範囲と実機比較の手順

**対象：** [公開 Windows x64 OFX v2.2.1](https://github.com/46slv/press-machine/releases/tag/ofx/v2.2.1)、ビルド元 `9e235de0a3f2fb1f87e4122ad8f354e7c6f598f4`。表示 `Press Machine 2.2`、互換ID `com.46slv.PressMachine.v3.curve.dev`／OFX版3.1。ZIP・同梱OFX・バインディングのSHA256を[版の記録](PressMachine-2.2.1-Release.md#exact-artifact)と照合し、バインディングの18入力も固定元（生成ヘッダーを含む）の正規化改行SHA256と一致。署名検証ではない。評価時のmain `53939b2897d171aafc82003d1a817a68082d47c8` と固定元の間で追跡された `parameters/`、`core/`、`adapters/ofx/src/` の差分なし。

**今回のCPU A/B：** Windows x64 MSVC Releaseで固定ソースの `PressMachineParity` をビルドし、`NativeV3.cpp` の `pm_eval30` を呼んだ。DWG D65 / Relative Linear、出力Same、float32 RGBA、A=1、表示変換なし。11無彩色＋8色付きの合成パッチ、11設定。データは[小型JSON](PressMachine-2.2.1-Ryo-Look-CPU.json)（RGB/Yは丸めた値）。公開`.ofx`のロード・Resolve・CUDA・実写はこの比較に含まない。

- 入出力同一プロファイルの既定値は全パッチで元RGBと一致。Split単独の最大絶対ΔYは `8.69e−8`。グレーで `+20` はY=`.04`を青側、Y=`.72`を黄側へ（DWG RGBでB−Rの符号比較）。`−20`で反転。Pivot `+1` ではY=`.36`のグレーが元と一致した。これは表示後の色相や知覚上の一致を示さない。
- Shadow Desat `.16/.09` は着色されたY=`.003`を無彩色に戻し、Y=`.04`の青方向を維持。暗い暖色は `Look Skin Protect=70` で変化が弱くなったが、その後のFinal Desatで無彩色になった。同じ保護設定は試した明暗の暖色パッチのSplit差分を弱めたが、元の色に完全には戻さなかった。
- 青灰・クリーム・明るい暖色ではDensity `+50`のYが低下、`−50`は上昇。例えば青灰のYは `.04000` → `.03629` / `.04409`。Density Bypassで全パッチがSplit単独と一致。`Amount %=10`で高彩度の青と暖色のいずれもDWGのRGB最大−最小値が下がった（知覚彩度ではない）。別に固定元のCurve診断14,535チェック、Makeup 165ケース、Neutral Hue 27,864サンプルのCPUテストが通った。

**実機は未実施：** 既設OFXには公開バイナリとは別のSHAで、同じバンドル名と同じプラグインIDを持つものがあった。[公式の版別手順](PressMachine-2.2.1-Release.md#install-and-rollback)は同IDの並列インストールを禁じている。既設版の上書き、移動による無効化・入れ替えは行わなかった。隔離プロジェクトだけではホスト全体のOFX衝突は隔離できない。版の記録にある別の素材での既報Resolve実測（4K 206フレーム、AWG4/LogC4 → Rec.709/Gamma 2.4、Density 0/100と保存再読込）は本ルックの検証ではない。

### CPU診断を追試する

Windows x64のMSVC/CMakeとResolveのOpenFX SDKが入った環境で、上記固定コミットの別コピーを使う。以下は `adapters/ofx/` で実行した生成・ビルド・既存テストの手順（Visual Studio 2019の場合）。既存ファイルを上書きしない隔離コピーで実行する。`PressMachineParity` はCPU診断ライブラリであり、配布OFXを作るターゲットではない。

```powershell
python -B regenerate.py
python -B generate_descriptors.py
cmake -S . -B build-look-ryo -G "Visual Studio 16 2019" -A x64
cmake --build build-look-ryo --config Release --target PressMachineParity PressMachineMakeupTests PressMachineNeutralHueTests
New-Item -ItemType Directory -Path build
Copy-Item build-look-ryo/Release/PressMachineParity.dll build/VNextNative.dll
python -B tests/verify_luma_curve.py
./build-look-ryo/Release/PressMachineMakeupTests.exe
./build-look-ryo/Release/PressMachineNeutralHueTests.exe
```

同じディレクトリから、下の最小例で青灰側のグレーを比較できる。全パッチの入力は次節の表、設定差分はJSONの `parameter_cases`（記載のない創作操作子はスキーマ既定）、出力列は `R,G,B,Y`。`pm_eval30` の第3引数0は不透明な試験入力をStraightとして処理する指定。

```python
import ctypes as C
import json
from pathlib import Path

schema = json.loads(Path('../../parameters/press_machine_v3_curve.json').read_text())
api = C.CDLL(str(Path('build-look-ryo/Release/PressMachineParity.dll').resolve()))
api.pm_eval30.argtypes = [C.POINTER(C.c_float), C.POINTER(C.c_double), C.c_int, C.POINTER(C.c_float)]
api.pm_eval30.restype = None
api.pm_vnext_y.argtypes = [C.POINTER(C.c_double)]
api.pm_vnext_y.restype = C.c_double

for split in (0, 20, -20):
    overrides = {'pmi_it': 4, 'pm_hue_angle': 55, 'pm_luma_split': split}
    p = (C.c_double * 30)(*(overrides.get(x['id'], x['default']) for x in schema))
    src, dst = (C.c_float * 4)(.04, .04, .04, 1), (C.c_float * 4)()
    api.pm_eval30(src, p, 0, dst)
    y = api.pm_vnext_y((C.c_double * 3)(*dst[:3]))
    print(split, [round(v, 9) for v in (*dst[:3], y)])
```

### 次のA/B：別の競合しないResolve環境で

1. 公開ZIP・バイナリSHAを照合して同IDがない環境に入れ、実際のロード版、Resolve版、バックエンド、色管理を記録する。制作PFではなく新規の検証プロジェクトを使用。元素材はここで生成できるチャートと、権利の明らかな未グレードの短い実写（青い陰、明るい無彩色〜クリーム、肌または暖色小物、動き）に分ける。参照のYouTube映像を入力にして焼き付け済みのグレードを成功扱いしない。
2. CPUとの数値比較は、実写向けのRCM設定を引き継がず、**非管理のDaVinci YRGB**で行う。チャートは不透明floatのDWG Linear EXR、Full。OFX直前まで色変換や既存LUTを入れず、`DWG D65` / `Relative Linear` → `Same as Input` をOFXに指定する。計測出力は入力と同じDWG Linearのfloat EXR。表示用CSTは観察時だけ有効にする。灰色のY=`0/.003/.01/.02/.04/.08/.18/.36/.72/1.44/2.88`。色パッチの元DWG RGBと合わせるYは下表。`RGB × 目標Y / (0.27411851R+0.87363190G−0.14775041B)` で各色のYをそろえる。肌色風のパッチは顔を表す試験ではない。必要なら同じ色を大小2箇所に置く。

   | パッチ | 元DWG RGB | Y |
   | --- | --- | --- |
   | 青灰 | (.85, 1, 1.25) | .04 |
   | クリーム | (1.15, 1.04, .80) | .72 |
   | 黄緑 | (1.02, 1.12, .72) | .72 |
   | 暖色3段 | (1.55, .88, .65) | .003 / .04 / .36 |
   | 高彩度青 | (.20, .90, 1.9) | .08 |
   | 高彩度暖色 | (2.1, .65, .25) | .18 |

3. 同一入力・同一表示変換で **A＝バイパスと中立、B＝Pressだけ、C＝Press＋Resolve標準補正** を比較する。Bでは上のCPU数値を用いて1項目ずつON/OFF。パッチ中央の線形RGB/Yは**表示変換なしのfloat出力**で比較し、見た目とスコープは**固定のSDR表示変換あり**で確認する。`Graph`は測定に使わない。RGBの範囲外、レベルの取り違え、変換重複をチェックする。
4. 実写では暗い入口と壁の濃淡、白雲とクリーム色の分離、複数輝度にまたがる肌・ベージュ・赤を個別比較。A/B/Cの同フレームとカットまたぎ再生を見て、好み・副作用・合否を別記。使用版、ノード順、調整値、色空間、レンダー設定、比較コマ・領域を保存する。実写でこの結果が確認されるまでプリセット扱いしない。
