import gradio as gr
import requests

# --- Service Endpoints (host-accessible) ---
STT_URL = "#"
LLM_URL = ""
ORCH_URL =  ""

def process_audio(audio_file):
    """Pipeline for audio input → STT → LLM → Orchestrator"""
    with open(audio_file, "rb") as f:
        stt_resp = requests.post(STT_URL, files={"file": f})
    stt_text = stt_resp.json().get("text", "[ERROR: STT failed]")
    
    llm_resp = requests.post(LLM_URL, json={"input_text": stt_text})
    llm_data = llm_resp.json()
    command = llm_data.get("command", {})
    response = llm_data.get("verbal_response", "[ERROR: LLM failed]")
    
    orch_resp = requests.post(ORCH_URL, json={"command": command})
    orch_data = orch_resp.json()
    
    return stt_text, response, orch_data

def process_text(input_text):
    """Pipeline for direct text → LLM → Orchestrator"""
    llm_resp = requests.post(LLM_URL, json={"input_text": input_text})
    llm_data = llm_resp.json()
    command = llm_data.get("command", {})
    response = llm_data.get("verbal_response", "[ERROR: LLM failed]")
    
    orch_resp = requests.post(ORCH_URL, json={"command": command})
    orch_data = orch_resp.json()
    
    return response, orch_data

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## 🎙️ Robot Voice/Text Control Interface")
    
    with gr.Tab("🎤 Voice Command"):
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record Command")
        stt_output = gr.Textbox(label="Recognized Speech")
        llm_response = gr.Textbox(label="Robot Response")
        orch_status = gr.Textbox(label="Execution Status")
        
        audio_input.change(
            fn=process_audio,
            inputs=audio_input,
            outputs=[stt_output, llm_response, orch_status]
        )
    
    with gr.Tab("⌨️ Text Command (LLM Test)"):
        text_input = gr.Textbox(label="Enter Command Text")
        llm_response2 = gr.Textbox(label="Robot Response")
        orch_status2 = gr.Textbox(label="Execution Status")
        
        text_input.submit(
            fn=process_text,
            inputs=text_input,
            outputs=[llm_response2, orch_status2]
        )

demo.launch(server_name="0.0.0.0", server_port=7860)