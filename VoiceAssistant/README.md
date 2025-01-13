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
> 模型列表:'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'

### 启动可视化界面
```bash
docker run -itd --name voiceassistant 
-v /zkzd/voiceassistant:/workspace 
-e ASR_MODEL=http://127.0.0.1:9000
--restart always
DockerImage:tag
```
其中DockerImage:tag为voiceassistant的镜像名称和tag,默认为ASR_MODEL 为前面启动whisper容器地址