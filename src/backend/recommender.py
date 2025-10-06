import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAPERS_CSV = os.path.join(BASE_DIR, "datasets", "papers.csv")
LINKS_CSV  = os.path.join(BASE_DIR, "datasets", "paper_to_datasets.csv")

# ---------- Load data (exact columns) ----------
papers = pd.read_csv(PAPERS_CSV, dtype={"pmcid": str, "pmid": str, "title": str, "paper_url": str})
links  = pd.read_csv(LINKS_CSV,  dtype={"paper_pmcid": str, "dataset_type": str, "dataset_id": str, "dataset_url": str})

# Basic cleaning / normalization
papers = papers.dropna(subset=["pmcid", "title", "paper_url"]).copy()
papers["pmcid"] = papers["pmcid"].str.strip().str.upper()

links = links.dropna(subset=["paper_pmcid", "dataset_id"]).copy()
links["paper_pmcid"] = links["paper_pmcid"].str.strip().str.upper()
links["dataset_id"]  = links["dataset_id"].str.strip().str.upper()
links["dataset_type"] = links["dataset_type"].fillna("").str.strip().str.upper()

# Remove exact duplicate link rows if any
links = links.drop_duplicates(subset=["paper_pmcid","dataset_id","dataset_url"])

# ---------- Map papers → datasets ----------
def _group_row(r):
    return {
        "dataset_id":  r["dataset_id"],
        "dataset_type": r.get("dataset_type", None),
        "dataset_url": r.get("dataset_url", None)
    }

paper_to_datasets = (
    links.groupby("paper_pmcid")
         .apply(lambda g: [_group_row(r) for _, r in g.iterrows()], include_groups=False)
         .to_dict()
)

# ---------- TF-IDF over titles ----------
papers["__text__"] = papers["title"].fillna("")
_vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
_X = _vectorizer.fit_transform(papers["__text__"])

_pmcids = papers["pmcid"].tolist()
_idx = {_pmcids[i]: i for i in range(len(_pmcids))}

# ---------- API-like functions ----------
def search_papers(query: str, k: int = 10):
    if not query or not str(query).strip():
        return []
    sims = cosine_similarity(_vectorizer.transform([query]), _X).ravel()
    order = sims.argsort()[::-1][:k]
    return [{
        "pmcid": _pmcids[i],
        "title": papers.iloc[i]["title"],
        "paper_url": papers.iloc[i]["paper_url"],
        "score": float(sims[i])
    } for i in order]

def similar_papers(pmcid: str, k: int = 10):
    pmcid = str(pmcid).strip().upper()
    i = _idx.get(pmcid)
    if i is None:
        return []
    sims = cosine_similarity(_X[i], _X).ravel()
    sims[i] = -1
    order = sims.argsort()[::-1][:k]
    return [{
        "pmcid": _pmcids[j],
        "title": papers.iloc[j]["title"],
        "paper_url": papers.iloc[j]["paper_url"],
        "score": float(sims[j])
    } for j in order]

def paper_detail(pmcid: str, k_similar: int = 10):
    pmcid = str(pmcid).strip().upper()
    row = papers.loc[papers["pmcid"] == pmcid]
    if row.empty:
        return {"error": "paper not found", "pmcid": pmcid}
    return {
        "pmcid": pmcid,
        "title": row.iloc[0]["title"],
        "paper_url": row.iloc[0]["paper_url"],
        "datasets": paper_to_datasets.get(pmcid, []),
        "similar": similar_papers(pmcid, k=k_similar)
    }
