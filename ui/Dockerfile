FROM python:3.11
WORKDIR /ui

# install gradio
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "ui.py"]
