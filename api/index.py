import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image

app = Flask(__name__, template_folder='templates', static_folder='static')

# Gemini API Yapılandırması
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# GAME MAKER AI Kişiliği ve Sistem Talimatı
SYSTEM_PROMPT = (
    "Senin adın GAME MAKER AI. Üst düzey bir oyun geliştirme asistanısın. "
    "Unity, Unreal Engine, Godot, Three.js ve GameMaker gibi motorlarda uzmansın. "
    "Kullanıcının oyun projelerini hatırlarsın, teknik hataları çözer ve optimizasyon önerirsin. "
    "Yanıtların profesyonel, çözüm odaklı ve Türkçe olmalıdır."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form.get('message', '')
        history_raw = request.form.get('history', '[]')
        history = json.loads(history_raw) # Geçmişi liste formatına çevir
        image_file = request.files.get('image')

        # Sohbet oturumunu hafıza ile başlat
        chat_session = model.start_chat(history=history)
        
        content = []
        if image_file:
            img = Image.open(image_file.stream)
            content.append(img)
        
        if user_message:
            content.append(user_message)

        # Yanıt al
        response = chat_session.send_message(content)
        
        # Güncellenmiş geçmişi oluştur
        updated_history = []
        for msg in chat_session.history:
            updated_history.append({
                "role": msg.role,
                "parts": [p.text if hasattr(p, 'text') else "[Görsel Veri]" for p in msg.parts]
            })

        return jsonify({
            'response': response.text,
            'history': updated_history
        })

    except Exception as e:
        return jsonify({'response': f'Sistem Hatası: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)