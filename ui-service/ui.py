import gradio as gr
import requests
import base64
import tempfile

# --- Service Endpoints ---
STT_URL = "http://stt-service:8000/transcribe"
ORCH_URL = "http://orchestrator-service:8000/process"   # FastAPI orchestrator

def b64_to_wav(audio_b64):
    """Convert base64 audio to a temporary WAV file and return its path"""
    audio_bytes = base64.b64decode(audio_b64)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.write(audio_bytes)
    temp_file.close()
    return temp_file.name

def process_audio(audio_file):
    with open(audio_file, "rb") as f:
        stt_resp = requests.post(STT_URL, files={"file": f})
    stt_text = stt_resp.json().get("text", "[ERROR: STT failed]")
    
    status, response, audio_out = _process_pipeline(stt_text)
    return stt_text, status, response, audio_out

def process_text(input_text):
    status, response, audio_out = _process_pipeline(input_text)
    return status, response, audio_out

def _process_pipeline(input_text):
    try:
        orch_resp = requests.post(ORCH_URL, json={"input_text": input_text})
        data = orch_resp.json()
        
        if orch_resp.status_code == 200:
            # success path
            status = "SUCCESS"
            response = data.get("verbal_response", "")
            audio_b64 = data.get("audio_base64")
            audio_out = b64_to_wav(audio_b64) if audio_b64 else None
            return status, response, audio_out
        else:
            # failed validation
            status = "FAILED"
            detail = data.get("detail", "Unknown error")
            return status, detail, None

    except Exception as e:
        return "FAILED", f"[EXCEPTION] {str(e)}", None

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## 🎙️ Robot Voice/Text Control Interface")
    
    with gr.Tab("🎤 Voice Command"):
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record Command")
        stt_output = gr.Textbox(label="Recognized Speech")
        status_out = gr.Textbox(label="Execution Status")
        llm_response = gr.Textbox(label="Robot Response" , lines= 3)
        audio_out = gr.Audio(label="Robot Speech", type="filepath")
        
        audio_input.change(
            fn=process_audio,
            inputs=audio_input,
            outputs=[stt_output, status_out, llm_response, audio_out]
        )
    
    with gr.Tab("⌨️ Text Command"):
        text_input = gr.Textbox(label="Enter Command Text")
        status_out2 = gr.Textbox(label="Execution Status")
        llm_response2 = gr.Textbox(label="Robot Response",  lines= 3)
        audio_out2 = gr.Audio(label="Robot Speech", type="filepath")
        
        text_input.submit(
            fn=process_text,
            inputs=text_input,
            outputs=[status_out2, llm_response2, audio_out2]
        )
    
    gr.Markdown("## TEST UI VERSION 3")

demo.launch(server_name="0.0.0.0", server_port=7860)
