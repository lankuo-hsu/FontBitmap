"""===============================================
配合ESP32程式：btMagicWS2812_20250218.ino
不限字數，可中英數字
操作：手機藍牙傳送字串，如"中華民國萬歲 Good Luck"
=================================================="""
#取得漢字的字型點陣資料
import socket       #UDP通訊
from PIL import Image, ImageDraw, ImageFont
#from fontTools.ttLib import TTFont
import os,time

UDP_IP = "0.0.0.0"  # 本地監聽 IP
UDP_PORT = 12345     # ESP32 發送請求的埠號
ESP_IP = "192.168.0.10"  # ESP32 固定 IP
ESP_PORT = 12346  # ESP32 接收數據的埠號

# 設定字型
#FONT_PATH = r"C:\Windows\Fonts\msjh.ttc"  # 微軟正黑體
FONT_PATH = r"C:\Windows\Fonts\mingliu.ttc"   #細明體


print(f"模型文件是否存在: {os.path.exists(FONT_PATH)}")

FONT_SIZE = 16  # 點陣大小
fs=16;
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# 建立副程式回傳點陣，繪出中文
def Get_bitmap_from_ttf(font_path, char, size):
    # 用 getbbox() 取得字元的邊界 (左, 上, 右, 下)
    bbox = font.getbbox(char)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # 建立一個白底影像
    image = Image.new("1", (width, height), 0)
    draw = ImageDraw.Draw(image)
    
    # 繪製字元
    draw.text((-bbox[0], -bbox[1]), char, font=font, fill=1)
    
    # 轉換成 16x16 點陣
    image = image.resize((fs, fs), Image.Resampling.NEAREST)
    
    # 轉換成二維陣列
    bitmap = [[image.getpixel((x, y)) for x in range(fs)] for y in range(fs)]
    
    return bitmap

# UDP 伺服器設置
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening on UDP {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    #text = data.decode("utf-8")[-8:].strip() # 取最後 8 個字元清理空格
    text = data.decode("utf-8")     
    
    if not text:
        print("Empty or invalid text received.")
        continue

    print(f"Received text: {text}")
    # 為每個字元生成點陣並傳輸
    for char in text:
        bitmap = Get_bitmap_from_ttf(FONT_PATH, char, FONT_SIZE) # 生成點陣
        # 印出點陣字
        for row in bitmap:
            print(' '.join(['#' if pixel else '.' for pixel in row]))
            
        flat_bitmap = [pixel for row in bitmap for pixel in row]  # 展平成 1D 陣列
        response = "".join(map(str, flat_bitmap))  # 將點陣轉為字符串
        sock.sendto(response.encode(), addr)  # 傳輸給 ESP32
        


        