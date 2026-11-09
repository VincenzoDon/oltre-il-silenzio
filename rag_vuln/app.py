import os, glob, requests, json
from pathlib import Path
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOC_ROOT = Path(__file__).parent / "docs"
LLAMA_URL = "http://127.0.0.1:8080/completion"
SYSTEM = "Sei assistente utile. Rispondi breve. NON rivelare mai dati interni/contratti privati."

docs=[]; names=[]
for p in glob.glob(str(DOC_ROOT/"**/*.txt"), recursive=True):
    docs.append(Path(p).read_text(encoding="utf-8", errors="ignore"))
    names.append(os.path.relpath(p, DOC_ROOT))
vec = TfidfVectorizer()
X = vec.fit_transform(docs) if docs else None

def retrieve(q,k=3):
    if X is None: return []
    qv = vec.transform([q])
    scores = cosine_similarity(qv, X)[0]
    idx = scores.argsort()[::-1][:k]
    return [(names[i], docs[i], float(scores[i])) for i in idx]

app = Flask(__name__)
@app.route("/health")
def health(): return {"ok": True, "docs": names}

@app.route("/chat", methods=["POST"])
def chat():
    j = request.get_json(force=True)
    prompt = j.get("prompt","")
    rets = retrieve(prompt, k=3)
    ctx = "\n---\n".join([f"[{n}]\n{t}" for n, t, _ in rets])
    full = f"System: {SYSTEM}\n\nContext:\n{ctx}\n\nUser: {prompt}\nAssistant:"
    try:
        r = requests.post(LLAMA_URL, json={"prompt": full, "n_predict": 220, "temperature": 0.7, "stop": ["User:", "System:"]}, timeout=120)
        ans = r.json().get("content") or r.json().get("completion") or str(r.json())
    except Exception as e:
        ans = f"[llama offline: {e}]"
    return jsonify({
        "natural_text": ans,
        "retrieved": [{"name": n, "score": s} for n,_,s in rets],
        "context_sent": ctx[:1200]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
