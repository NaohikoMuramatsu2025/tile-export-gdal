import configparser
import subprocess
import pyperclip  # ← クリップボード読み取り用

# ========== STEP 1: user_input.ini 読み込み ==========
config = configparser.ConfigParser()
config.read('user_input.ini', encoding='utf-8-sig')

# INIから読み込んだ中心点（元の値を保持）
lat_ini = float(config['CENTER']['lat'])
lon_ini = float(config['CENTER']['lon'])

scale = int(config['OUTPUT']['scale'])
paper_width_mm = int(config['OUTPUT']['paper_width_mm'])
paper_height_mm = int(config['OUTPUT']['paper_height_mm'])
output_file = config['OUTPUT']['file_name']

zoom_level = config['GDAL'].getint('zoom_level', 18)

# ========== MAP番号の読み取り ==========
map_number = int(config['MAP'].get('map_type', '1'))

# ========== MAP番号に応じたURL切り替え ==========
if map_number == 1:
    server_url = "https://cyberjapandata.gsi.go.jp/xyz/std/${z}/${x}/${y}.png"
elif map_number == 2:
    server_url = "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/${z}/${x}/${y}.jpg"
elif map_number == 3:
    server_url = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${z}/${y}/${x}"
elif map_number == 4:
    server_url = "https://tile.openstreetmap.org/${z}/${x}/${y}.png"
else:
    raise ValueError("サポートされていないMAP番号です")

# ========== STEP 1.5: クリップボードから座標取得（あれば） ==========
def get_coords_from_clipboard():
    try:
        text = pyperclip.paste()
        if ',' in text:
            lat_str, lon_str = map(str.strip, text.strip().split(','))
            return float(lat_str), float(lon_str)
    except Exception as e:
        print(f"⚠️ クリップボードの解析失敗: {e}")
    return None

coords = get_coords_from_clipboard()
if coords:
    lat_center, lon_center = coords
    print(f"📋 クリップボード座標を使用: lat={lat_center}, lon={lon_center}")
else:
    lat_center, lon_center = lat_ini, lon_ini
    print(f"🗂 INIファイル座標を使用: lat={lat_center}, lon={lon_center}")

# ========== STEP 2: 範囲（m） ==========
half_width_m = (paper_width_mm / 1000) * scale / 2
half_height_m = (paper_height_mm / 1000) * scale / 2

# ========== STEP 3: gdaltransform による中心変換 ==========
def to_mercator(lon, lat):
    result = subprocess.run(
        ['gdaltransform', '-s_srs', 'EPSG:4326', '-t_srs', 'EPSG:3857'],
        input=f"{lon} {lat}\n", text=True, capture_output=True
    )
    x, y, *_ = result.stdout.strip().split()
    return float(x), float(y)

x_center, y_center = to_mercator(lon_center, lat_center)

x_min = x_center - half_width_m
x_max = x_center + half_width_m
y_min = y_center - half_height_m
y_max = y_center + half_height_m

# ========== STEP 4: VRTファイル作成 ==========
vrt_content = f'''<GDAL_WMS>
    <Service name="TMS">
       <ServerUrl>{server_url}</ServerUrl>
    </Service>
    <DataWindow>
        <UpperLeftX>-20037508.34</UpperLeftX>
        <UpperLeftY>20037508.34</UpperLeftY>
        <LowerRightX>20037508.34</LowerRightX>
        <LowerRightY>-20037508.34</LowerRightY>
        <TileLevel>{zoom_level}</TileLevel>
        <YOrigin>top</YOrigin>
    </DataWindow>
    <Projection>EPSG:3857</Projection>
    <BlockSizeX>256</BlockSizeX>
    <BlockSizeY>256</BlockSizeY>
    <BandsCount>3</BandsCount>
    <DataType>Byte</DataType>
    <ZeroBlockHttpCodes>404</ZeroBlockHttpCodes>
</GDAL_WMS>
'''
with open('map_source.vrt', 'w') as f:
    f.write(vrt_content)
print("✅ VRTファイルを生成しました")

# ========== STEP 5: GeoTIFF 生成（TFWなし） ==========
print("🟡 GeoTIFFを生成中（TFWなし）...")
subprocess.run([
    'gdal_translate',
    '-projwin', str(x_min), str(y_max), str(x_max), str(y_min),
    '-a_srs', 'EPSG:3857',
    '-of', 'GTiff',
    'map_source.vrt',
    output_file
])
print(f"✅ GeoTIFF出力完了: {output_file}（.tfwは生成されません）")

# ========== 完了 ==========
print("🎉 完了：GeoTIFFファイルが正常に生成されました")
