import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="Backend Estação de Atendimento - Detecção Facial & Triagem")

# ------------------------------------------------------------------------------
# 1. MODELO DE DADOS ENVIADOS NA ETAPA 3
# ------------------------------------------------------------------------------
class DadosTriagem(BaseModel):
    nome: str
    idade: int
    queixa: str
    temperatura: float
    spo2: int
    frequencia_cardiaca: int
    frequencia_respiratoria: int
    dor: int


# ------------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DO MEDIAPIPE FACE LANDMARKER
# ------------------------------------------------------------------------------
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Inicializa a câmera local (webcam)
camera = cv2.VideoCapture(0)


# ------------------------------------------------------------------------------
# 3. FUNÇÕES AUXILIARES E PROCESSAMENTO DE VÍDEO
# ------------------------------------------------------------------------------
def extrair_roi_testa(landmarks, w, h):
    """
    Calcula a ROI da testa e olhos com expansão em pixels (padding).
    """
    indices_olhos = [10, 67, 297, 109, 338, 133, 362]
    indices_utilizar = indices_olhos
    
    pts = []
    for idx in indices_utilizar:
        lm = landmarks[idx]
        pts.append((int(lm.x * w), int(lm.y * h)))
    
    pts = np.array(pts)
    x, y, bw, bh = cv2.boundingRect(pts)
    
    # --- Fatores de Expansão ---
    padding_x = int(bw * 0.1)        # Expande 10% na largura
    padding_y_topo = int(bh * 0.1)   # Expande 10% para cima
    padding_y_baixo = int(bh * 0.1)  # Expande 10% para baixo

    # Aplica os limites garantindo que não saia da borda da imagem (0 a w, 0 a h)
    x_min = max(0, x - padding_x)
    x_max = min(w, x + bw + padding_x)
    y_min = max(0, y - padding_y_topo)
    y_max = min(h, y + bh + padding_y_baixo)
    
    return x_min, y_min, x_max, y_max

def gerar_frames_webcam():
    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Converte para formato Image do MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Processa a imagem com o detector
        detection_result = detector.detect(mp_image)

        if detection_result.face_landmarks:
            face_landmarks = detection_result.face_landmarks[0]
            
            x1, y1, x2, y2 = extrair_roi_testa(face_landmarks, w, h)
            
            # Desenha a ROI da medição
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame, 
                "ROI Medicao (Testa/Olhos)", 
                (x1, max(20, y1 - 8)), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (0, 255, 0), 
                2
            )
        else:
            cv2.putText(
                frame, 
                "Aguardando paciente...", 
                (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, 
                (0, 0, 255), 
                2
            )

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# ------------------------------------------------------------------------------
# 4. ROTAS DA API FASTAPI
# ------------------------------------------------------------------------------
@app.get("/video_feed")
def video_feed():
    """Rota para streaming contínuo da webcam em tempo real."""
    return StreamingResponse(
        gerar_frames_webcam(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/triagem/classificar")
def classificar_atendimento(dados: DadosTriagem):
    """
    Rota que recebe todos os dados consolidados das 3 etapas do front-end.
    Aplica regra ESI preliminar para simulação.
    """
    # Exemplo de regra determinística ESI preliminar
    nivel_esi = 4
    if dados.spo2 < 90 or dados.frequencia_cardiaca > 140:
        nivel_esi = 1
    elif dados.spo2 < 94 or dados.temperatura >= 38.5 or dados.dor >= 7:
        nivel_esi = 2
    elif dados.temperatura >= 37.8 or dados.dor >= 4:
        nivel_esi = 3

    descricao_esi = {
        1: "Nível 1 - Emergência (Risco Imediato)",
        2: "Nível 2 - Muito Urgente",
        3: "Nível 3 - Urgente",
        4: "Nível 4 - Pouco Urgente",
        5: "Nível 5 - Não Urgente"
    }

    return {
        "paciente": dados.nome,
        "idade": dados.idade,
        "nivel_esi": nivel_esi,
        "classificacao": descricao_esi[nivel_esi],
        "sinais_recebidos": dados
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "camera_active": camera.isOpened()}