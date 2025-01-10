# 语音助手Demo_v1

> [Whisper Docker](https://hub.docker.com/r/onerahmet/openai-whisper-asr-webservice/tags)
> [Whisper](https://github.com/openai/whisper)

### 通过构建成docker镜像进行使用

```bash
# gpu
docker pull onerahmet/openai-whisper-asr-webservice:v1.7.0-gpu
# cpu
docker pull onerahmet/openai-whisper-asr-webservice:v1.7.0
```
### 启动命令
```bash
docker run -d \
--gpus all \
-p 9000:9000 \
-e ASR_MODEL=base \
-e ASR_ENGINE=openai_whisper \
-v /models:/root/.cache/whisper \
onerahmet/openai-whisper-asr-webservice:latest-gpu
```
> 第一次访问会下载模型，所以需要稍等一会