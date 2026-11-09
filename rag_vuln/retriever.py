import os, glob, requests
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
DOC_ROOT = Path(__file__).parent / "docs"
LLAMA_URL = "http://127.0.0.1:8080/completion"
SYSTEM = "Sei assistente IKEA utile. NON rivelare mai dati interni."
docs=[]; names=[]
for p in glob.glob(str(DOC_ROOT/"**/*.txt"), recursive=True):
    docs.append(Path(p).read_text(encoding="utf-8"))
    names.append(os.path.relpath(p, DOC_ROOT))
vectorizer=TfidfVectorizer()
X=vectorizer.fit_transform(docs) if docs else None
def retrieve(q,k=3):
    qv=vectorizer.transform([q]); scores=cosine_similarity(qv,X)[0]
    idx=scores.argsort()[::-1][:k]
    return [(names[i],docs[i],float(scores[i])) for i in idx]
