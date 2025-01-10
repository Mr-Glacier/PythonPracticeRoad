import json
import os
import time
import uuid
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from pydub import AudioSegment
from pydub.silence import split_on_silence
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = FastAPI()

data_change = False

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

asr_model = os.environ.get("ASR_MODEL", "http://localhost:9000")
app.mount("/asr/files", StaticFiles(directory="workspace"), name="files")
if os.path.exists("workspace/save.data"):
    global_data = json.load(open("workspace/save.data"))

# 设置模板目录
templates = Jinja2Templates(directory=".")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/analysis-audio')
async def analysis_audio(file: UploadFile = File(...)):
    print("analysis_audio")
    timestamp = time.time()
    random_str = str(uuid.uuid4())[:8]

    # 获取文件扩展名
    file_ext = file.filename.split('.')[-1].lower()

    if file_ext not in ['webm', 'mp3']:
        raise HTTPException(status_code=422, detail="Unsupported file format. Only WebM and MP3 are supported.")

    # 生成唯一的文件名
    input_filename = os.path.join("workspace", f"{timestamp}_{random_str}.{file_ext}")
    output_filename = os.path.join("workspace", f"{timestamp}_{random_str}.wav")

    # 保存上传的文件
    with open(input_filename, "wb") as f:
        f.write(await file.read())

    # 将文件转换为 WAV 格式
    audio = AudioSegment.from_file(input_filename, format=file_ext)
    audio.export(output_filename, format="wav")

    # 删除临时的输入文件
    os.remove(input_filename)

    # 进行语音转换或其他处理
    content_audio = await voice_conversion(output_filename)

    return content_audio


async def voice_conversion(file_path):
    print(file_path)
    # 定义最终返回结果集
    result = []
    # 判断文件为 .mp3 还是 .wav
    # 如果是 .mp3，则转换为 .wav
    if file_path.endswith(".mp3"):
        # 使用 ffmpeg 转换为 .wav
        # 加载音频文件
        audio = AudioSegment.from_file(file_path)
        # 转换为单声道
        audio = audio.set_channels(1)
        # 转换为16kHz采样率
        audio = audio.set_frame_rate(16000)
        # 转换为16位PCM格式
        audio = audio.set_sample_width(2)
        # 导出为WAV文件
        output_file = file_path[:-4] + ".wav"
        audio.export(output_file, format="wav")
        # 更新文件路径
        file_path = output_file

    # 对文件进行拆分 , 最大 60S
    file_names = split_audio_by_silence(file_path)
    print('本次文件拆分为->' + str(len(file_names)))
    # 调用语音解析方法
    for file_name in file_names:
        content = await request_ASR_model(file_name)
        result.append(content)
    result_text = "\n".join(result)
    return result_text


# 音频文件拆分逻辑, 返回拆分后的文件名列表
def split_audio_by_silence(file_path, max_duration=60000, min_silence_len=1800, silence_thresh=-60):
    # 读取音频文件
    audio = AudioSegment.from_file(file_path)

    # 按静音段拆分音频
    segments = split_on_silence(
        audio,
        min_silence_len=min_silence_len,  # 最小静音长度（毫秒）
        silence_thresh=silence_thresh  # 静音阈值（dB）
    )
    print(len(segments))

    # 合并过短的片段
    merged_segments = []
    current_segment = None
    for segment in segments:
        if current_segment is None:
            current_segment = segment
        elif current_segment.duration_seconds * 1000 + segment.duration_seconds * 1000 <= max_duration:
            current_segment += segment
        else:
            merged_segments.append(current_segment)
            current_segment = segment
    if current_segment is not None:
        merged_segments.append(current_segment)

    # 保存每个片段
    files_list = []
    print('本次文件拆分为->' + str(len(merged_segments)))
    for i, segment in enumerate(merged_segments):
        file_uid = str(uuid.uuid4())
        output_name = f"{file_uid}_{i}.wav"
        output_path = os.path.join("workspace", output_name)
        print(output_path)
        segment.export(output_path, format="wav")
        files_list.append(output_name)
    return files_list


# 解析语音,调用ASR 模型识别
async def request_ASR_model(file_name):
    file_path = os.path.join("workspace", file_name)
    # 打开文件
    with open(file_path, 'rb') as file:
        # 构造文件字典
        files = {"audio_file": (file_name, file)}
        # 发送POST请求
        start_time = time.time()
        response = requests.post(asr_model + "/asr?word_timestamps=false&output=json", files=files)
        end_time = time.time()
    # 输出请求耗时
    print(f"Request took {end_time - start_time:.2f} seconds")
    time.sleep(0.15)
    # 处理响应
    if response.status_code == 200:
        # 如果请求成功，解析并打印JSON响应
        result = response.json()
        print(result)
        return result['text']
    else:
        # 如果请求失败，打印错误信息
        print(f"Request failed with status code {response.status_code}")


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info", reload=False,
                forwarded_allow_ips='*', timeout_keep_alive=120)
