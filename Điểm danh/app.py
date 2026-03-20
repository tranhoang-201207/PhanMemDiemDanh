from flask import Flask, request, render_template, jsonify
from google import genai
from PIL import Image
import re
from datetime import datetime
import requests

app = Flask(__name__)

# --- CẤU HÌNH API GEMINI ---
client = genai.Client(api_key="AIzaSyD2thItqgXpq9yohNTafoZAsKgBMSketzE")

@app.route('/')
def trang_chu():
    return render_template('index.html')

@app.route('/quet', methods=['POST'])
def quet_the():
    if 'anh_the' not in request.files:
        return jsonify({'success': False, 'message': 'Không nhận được ảnh.'})
        
    file_anh = request.files['anh_the']
    
    try:
        img = Image.open(file_anh)
        cau_lenh = "Đây là ảnh chụp thẻ sinh viên. Hãy tìm và trả về cho tôi DUY NHẤT một chuỗi số là Mã số sinh viên (thường có từ 8 đến 10 chữ số). Không cần giải thích."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[cau_lenh, img]
        )
        
        ket_qua_tu_ai = response.text.strip()
        print(f"=> AI nhận diện: {ket_qua_tu_ai}")
        
        danh_sach_mssv = re.findall(r'\d{8,10}', ket_qua_tu_ai)
        
        if len(danh_sach_mssv) > 0:
            mssv = danh_sach_mssv[0]
            thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            URL_GOOGLE_SHEETS = "https://script.google.com/macros/s/AKfycbycEsvk1fHl19k5zH1E0X121VbHls1V9I25vQvFjWfA8m0B28p-JmC01t0j0F7XF2Pz/exec"
            
            payload = {
                "mssv": mssv,
                "thoi_gian": thoi_gian
            }
            
            requests.post(URL_GOOGLE_SHEETS, json=payload)
                
            return jsonify({'success': True, 'message': f'Lưu thành công MSSV: {mssv}'})
        else:
            return jsonify({'success': False, 'message': f'AI không thấy MSSV. Đọc ra: {ket_qua_tu_ai}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {e}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
