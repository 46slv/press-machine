# Press Machine 2.2 利用メモ

## まず色空間
Inputはこのnodeへ実際に入る色空間/transferに合わせる。前段CST等があるならカメラのファイル名だけで決めない。Output Sameは入力の符号化へ戻す指定で、Rec709表示変換ではない。

## 調整の順序
1. Pre SaturationでCompへ入れる彩度を調整。Threshold/Amount/KneeでSat Compを決め、Makeup Saturationでその後の彩度を補う。Pre/Makeupは100中立。
2. Comp Skin Protectは上の三工程全体の変化を、元入力から求めた肌maskで一回弱める。Compを二回実行するつまみではない。100でも全画面や全ての肌を無条件にidentityへ戻す機能ではない。
3. HueのAngle/Pattern/Strengthで色方向を作り、Bias/Split/Pivot/Widthで輝度に応じた作用を調整。Strength0でもBias/Splitの作用は残る。現在の式を変更・最終採用する操作ではない。
4. DensityはそのHue後の実色から沈み/持ち上がりを作る。通常の有効領域では正値で沈み、負値で持ち上がる。グローバルな露出/contrastつまみではない。
5. Look Skin ProtectはHueとDensityを合わせた変化を保護する。『Densityだけの肌保護』ではない。Density BypassはDensityだけを止め、HueやそのLook Skin保護を止めるスイッチではない。
6. FinalのShadow/Highlight Desatで最後の暗部/明部の色残りを調整。Input/Outputの色空間指定とは別の工程。

## Graphの読み方
GraphをONにし、viewerをOpenFXオーバーレイにする。Graphは書出し画像へ焼き込まない。auto1.5は小viewerで縮小上限があり、400x308未満は非表示。
- Hue色見本はPatternの方向キーで、画像中の実測色ではない。数や大きさはPattern/Strengthで変わる。
- Hue曲線は無彩色基準を現行Hue単独に通した輝度別の出力色方向/強さ。Pre/Comp/Makeupや写真の平均色を測ったものではない。縦軸は生成色度半径/Y、線色は色方向キー。下の帯はY=.18へ正規化した表示色で、実画素RGBそのものではない。表示用色域clipもある。
- Sat Comp曲線はBASE COMP BEFORE MAKEUP。Pre/Makeup/Skinを合成した全工程の曲線と取り違えない。
- Density曲線も固定色probeの参照応答。保護後Hueから保護後Lookへの差分で、全工程の効果や写真のhistogram・肌領域の測定値ではない。

## 保存と旧版
表示名は2.2だが、既存trial作品互換のため内部bundle名とIDにv3が残る。同ID版は並列installしない。v2やV21作品を自動変換しない。旧版へ戻す前は作品を別名保存/DRP保全し、旧bundleをhashごと保管する。Makeupを使った作品を古い版で上書き保存しない。

## 確認済みと未完
限定Host表示/保存/画素、短尺4K、現行DCTL、Density連携の証拠はあるが、全素材/profile/全range、長時間/リアルタイム/alphaの全面保証ではない。設定例の強さや見た目を推奨preset・採用判断にしない。
