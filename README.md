# 🔌 TCP2API

> A lightweight bridge that exposes TCP device data as an HTTP API.

---

## 📌 Context

Many industrial and embedded devices don't speak REST — they communicate over raw TCP 
with proprietary protocols. This project solves that by acting as a translation layer:
it connects to the device, sends a trigger command, parses the response, and delivers 
the data through a clean HTTP endpoint.

Two variants are available: one returning only numeric readings, and one that also 
captures a webcam image and returns it as base64 in the same payload.

---

## 🔄 How it works

1. API receives an HTTP request
2. Opens a TCP socket to the remote device
3. Sends a trigger command framed with `STX` (`\x02`) and `ETX` (`\x03`) control bytes
4. Reads the raw response in blocks with timeout protection
5. Filters and parses useful messages, discarding auxiliary responses like `OK`
6. Returns structured JSON

In the webcam variant, a camera frame is also captured, encoded as PNG in base64, 
and included in the same response.

---

## 🔌 Endpoints

### Root variant — numeric data only

```
GET /numeros
```
```json
{ "numeros": ["..."] }
```

### Webcam variant — numeric data + image

```
GET /
```
```json
{
  "numeros": ["..."],
  "imagem": "base64..."
}
```

---

## 🛠️ Tech Stack

| | |
|---|---|
| API | Python, Flask |
| Communication | TCP sockets (`socket`) |
| Image capture | OpenCV |
| Encoding | Base64 |

---

## 💡 Technical highlights

- **Protocol framing** with `STX`/`ETX` control bytes for reliable message delimiting
- **Defensive socket reading** with timeout to avoid indefinite blocking
- **Response filtering** — only useful messages are forwarded, noise is discarded
- **Dual variant design** — minimal version and extended version with webcam capture
- Bridge pattern between legacy TCP protocol and modern HTTP consumption

---

## 🚀 Running locally

**Requirements:** Python 3, pip, access to a compatible TCP device

### Root variant

```bash
pip install flask
python main.py
```

### Webcam variant

```bash
pip install -r python/requirements.txt
python python/main.py
```

> App runs on `0.0.0.0:5000` by default.
> Update the device IP and port in the code to match your environment.

---

## 📁 Structure

```text
main.py                 → Minimal API, numeric TCP data only
python/main.py          → Extended API, TCP data + webcam image in base64
python/requirements.txt → Dependencies for the webcam variant
python/primeiro.bat     → Windows setup and run script
```
