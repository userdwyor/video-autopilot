"""Stage 1 — pick a fresh, viral-leaning idea for the channel's niche."""
from __future__ import annotations
import requests
import re
from .config import load_prompt
from .knowledge import strategy_notes
from .llm import complete
from .utils import extract_json, log, recent_topics


def get_trends(cfg: dict) -> list[str]:
    """Optional trend seeds. Default: none (LLM uses niche knowledge).

    Hook a real trends source here (Google Trends via pytrends, a niche RSS feed,
    YouTube search autocomplete, etc.) and return a list of keyword strings.
    The analytics feedback loop can also inject winning past topics here.
    """
    return cfg["channel"].get("trend_seeds", [])


def generate_idea(cfg: dict) -> dict:
    ch = cfg["channel"]
    notes = strategy_notes(ch["key"])
    
    # --- TAMBAHAN: RISET TREN VIRAL DARI GOOGLE NEWS ---
    print("🕵️‍♀️ Dewi lagi riset tren viral di Google News...")
    viral_news = []
    try:
        # Ambil berita terpopuler di Indonesia
        r = requests.get("https://news.google.com/rss?hl=id&gl=ID&ceid=ID:id", timeout=10)
        # Ekstrak judul berita
        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', r.text)
        viral_news = titles[1:6] # Ambil 5 berita teratas
        print(f"✅ Tren hari ini: {viral_news}")
    except Exception as e:
        print(f"⚠️ Gagal narik tren: {e}")

    # Ambil trend_seeds dari config (kalau ada)
    manual_trends = get_trends(cfg)
    
    # Gabungkan berita viral + trend manual dari config
    all_trends = viral_news + manual_trends
    
    # Masukin ke Prompt
    prompt = load_prompt("ideation").format(
        niche=ch["niche"],
        name=ch["name"],
        audience=ch["audience"],
        angle=ch["angle"],
        trends="\n".join(f"- {t}" for t in all_trends) or "(none - use your niche expertise)",
        recent_topics="\n".join(f"- {t}" for t in recent_topics(ch["key"])) or "(none)",
        creator_notes=notes or "(none provided)",
        n=6,
    )
    data = extract_json(complete(prompt, cfg, max_tokens=1200))
    ideas = data.get("ideas", [])
    if not ideas:
        raise RuntimeError("Ideation returned no ideas.")
    best = ideas[0]  # already ranked best-first by the prompt
    log(f"idea: \"{best['title']}\" (save-worthiness {best.get('save_worthiness', '?')}/5)", "ok")
    return best
