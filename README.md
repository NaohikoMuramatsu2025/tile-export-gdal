# タイルエクスポート GDAL

📍 **GDALを使って地図タイルを指定領域でGeoTIFF出力するツール**

## 🧰 使用ライブラリ・ツール
- Python 3.x
- GDAL（gdal_translate, gdaltransform）
- `pyperclip`

## 📝 使用方法
1. `user_input.ini` を開いて中心座標や出力条件を設定
2. 緯度経度をクリップボードにコピーすればそれが優先されます（例: `34.7,137.7`）
3. 実行：
4. GeoTIFFが出力されます（用紙サイズ指定・ズームレベル指定対応）

## 🗺️ 対応マップ
- 国土地理院 標準地図 / 航空写真
- Esri 衛星画像
- OpenStreetMap

## 📁 構成ファイル
- `main.py`：出力スクリプト本体
- `user_input.ini`：設定ファイル（中心座標、地図種別など）

## 🗣️ 作者
[G空間の世界 gkukan.jp](https://gkukan.jp)
