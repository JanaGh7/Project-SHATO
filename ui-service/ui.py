import gradio as gr
import requests
import base64
import tempfile

# --- Service Endpoints ---
STT_URL = "http://stt-service:8000/transcribe"
ORCH_URL = "http://orchestrator-service:8000/process"

def b64_to_wav(audio_b64):
    if not audio_b64:
        return None
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

# Step 2: Orchestration using STT or text input
def run_orch(input_text):
    if not input_text:
        return "", "", "", None

    try:
        orch_resp = requests.post(ORCH_URL, json={"input_text": input_text})
        data = orch_resp.json()

        status_code = data.get("status_code", orch_resp.status_code)
        status_message = data.get("status_message", "")
        audio_b64 = data.get("audio_base64")

        # Logic for verbal response based on status code
        if status_code in [200, 360]:
            verbal_response = data.get("verbal_response", "")
            audio_out = b64_to_wav(audio_b64) if audio_b64 else None
        elif status_code == 400:
            verbal_response = "the llm didn't work properly, please try again"
            audio_out = b64_to_wav(audio_b64) if audio_b64 else None
        elif status_code == 500:
            status_message = "One of the main services didn't work properly. Please try again later."
            verbal_response = ""
            audio_out = None
        else:
            verbal_response = "[Unexpected error: check orchestrator]"
            audio_out = None

        return str(status_code), status_message, verbal_response, audio_out

    except Exception as e:
        return "FAILED", "[EXCEPTION] " + str(e), "", None

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## Robot Voice/Text Control Interface")

    # Tab 1: Voice Command
    with gr.Tab("Voice Command"):
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record Command")
        stt_output = gr.Textbox(label="Recognized Speech")
        status_code_out = gr.Textbox(label="Status Code")
        status_msg_out = gr.Textbox(label="Status Message")
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
            outputs=[status_code_out, status_msg_out, llm_response, audio_out]
        )

    # Tab 2: Text Command
    with gr.Tab("Text Command"):
        text_input = gr.Textbox(label="Enter Command Text")
        status_code_out2 = gr.Textbox(label="Status Code")
        status_msg_out2 = gr.Textbox(label="Status Message")
        llm_response2 = gr.Textbox(label="Robot Response", lines=3)
        audio_out2 = gr.Audio(label="Robot Speech", type="filepath")

        text_input.submit(
            fn=run_orch,
            inputs=text_input,
            outputs=[status_code_out2, status_msg_out2, llm_response2, audio_out2]
        )

demo.launch(server_name="0.0.0.0", server_port=7860)
