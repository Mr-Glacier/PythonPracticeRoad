# Text2Vec 文本向量化
> source:  https://github.com/shibing624/text2vec

### 通过构建成docker镜像进行使用
```bash
docker run -itd \
  --name text2vec \
  -p 13100:3100 \
  -v /zkzd/ai/server/text2vec_models:/zkzd/models \
  -e MODEL_NAME=text2vec-base-chinese \
  registry.cn-beijing.aliyuncs.com/zedata/text2vec:2025
```