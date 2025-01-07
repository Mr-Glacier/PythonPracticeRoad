from flask import Flask
from flask import request
from flask_cors import CORS
from text2vec import SentenceModel
import os

model_path = os.getenv("MODEL_NAME", "text2vec-base-chinese")
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')
# "shibing624/text2vec-base-chinese"
base_path = '/zkzd/models/'
t2v_model = SentenceModel(base_path + model_path)


def to_embeddings_text2vec(item):
    sentence_embeddings = t2v_model.encode(item)
    return sentence_embeddings.tolist()


def to_embeddings_text2vec_list(items):
    sentence_embeddings = t2v_model.encode(items)
    ret_list = []
    for s in sentence_embeddings:
        ret_list.append(s.tolist())
    return ret_list


@app.route('/')
def hello_world():
    return "text2vec,ok"


@app.route('/text2vec', methods=['GET'])
def text2vec():
    return to_embeddings_text2vec(request.args.get('q'))


@app.route('/text2vec', methods=['POST'])
def text2vecs():
    data = request.json["qs"]
    return to_embeddings_text2vec_list(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3100)
