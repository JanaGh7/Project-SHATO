import gradio as gr
import requests
import base64
import tempfile

# --- Service Endpoints ---
STT_URL = "http://stt-service:8000/transcribe"
ORCH_URL = "http://orchestrator-service:8000/process"

def b64_to_wav(audio_b64):
    audio_bytes = base64.b64decode(audio_b64)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.write(audio_bytes)
    temp_file.close()
    return temp_file.name

# Step 1: Call STT
def run_stt(audio_file):
    if not audio_file:
        return "[No audio recorded]", None

    try:
        with open(audio_file, "rb") as f:
            stt_resp = requests.post(STT_URL, files={"file": f})
        stt_text = stt_resp.json().get("transcription", "[ERROR: STT failed]")
    except Exception as e:
        stt_text = f"[STT ERROR] {e}"

    return stt_text, stt_text  # second value is passed to next step

# Step 2: Orchestration using STT output
def run_orch(stt_text):
    if not stt_text:
        return "", "", None

    try:
        orch_resp = requests.post(ORCH_URL, json={"input_text": stt_text})
        data = orch_resp.json()
        if orch_resp.status_code == 200:
            status = "SUCCESS"
            response = data.get("verbal_response", "")
            audio_b64 = data.get("audio_base64")
            audio_out = b64_to_wav(audio_b64) if audio_b64 else None
            return status, response, audio_out
        else:
            status = "FAILED"
            detail = data.get("detail", "")
            return status, detail, None
    except Exception as e:
        return "FAILED", f"[EXCEPTION] {str(e)}", None

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## Robot Voice/Text Control Interface")

    with gr.Tab("Voice Command"):
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record Command")
        stt_output = gr.Textbox(label="Recognized Speech")
        status_out = gr.Textbox(label="Execution Status")
        llm_response = gr.Textbox(label="Robot Response", lines=3)
        audio_out = gr.Audio(label="Robot Speech", type="filepath")

        # Step 1: STT
        audio_input.change(
            fn=run_stt,
            inputs=audio_input,
            outputs=[stt_output, stt_output]  # pass stt text to next step
        )

        # Step 2: Orchestration
        stt_output.change(
            fn=run_orch,
            inputs=stt_output,
            outputs=[status_out, llm_response, audio_out]
        )

    with gr.Tab("Text Command"):
        text_input = gr.Textbox(label="Enter Command Text")
        status_out2 = gr.Textbox(label="Execution Status")
        llm_response2 = gr.Textbox(label="Robot Response", lines=3)
        audio_out2 = gr.Audio(label="Robot Speech", type="filepath")

        text_input.submit(
            fn=run_orch,
            inputs=text_input,
            outputs=[status_out2, llm_response2, audio_out2]
        )

demo.launch(server_name="0.0.0.0", server_port=7860)
