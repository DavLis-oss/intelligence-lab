import google.generativeai as genai
import feedparser
import time
import os
import requests

# --- CONFIGURATION ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 1. LA LISTE DES SOURCES "TECH-ELITE"
SOURCES = [
    "https://news.google.com/rss/search?q=SearchGPT+OR+Perplexity+AI+OR+LLM+Indexing+OR+Search+Generative+Experience&hl=en-US&gl=US&ceid=US:en",
    "https://openai.com/news/rss.xml",
    "https://ai.meta.com/blog/rss/",
    "https://www.anthropic.com/index.xml",
    "https://blog.google/technology/ai/rss/",
    "https://techcrunch.com/category/artificial-intelligence/feed/"
]

# --- FONCTIONS UTILES ---

def is_already_processed(link):
    if not os.path.exists("processed_links.txt"): 
        return False
    with open("processed_links.txt", "r") as f:
        return link in f.read()

def save_to_github(title, content, source_url):
    # Création du dossier _drafts s'il n'existe pas
    if not os.path.exists("_drafts"):
        os.makedirs("_drafts")
    
    filename = f"_drafts/{title.replace(' ', '_')[:50]}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: \"{title}\"\nsource: {source_url}\n---\n\n{content}")
    
    with open("processed_links.txt", "a") as f:
        f.write(f"{source_url}\n")

def send_to_telegram(title, preview_text, github_url):
    message = f"🚨 *NEW DRAFT READY*\n\n"
    message += f"*Title:* {title}\n\n"
    message += f"*Preview:* {preview_text[:200]}...\n\n"
    message += f"🔗 [Review & Publish on GitHub]({github_url})"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

def should_i_publish(title, summary):
    prompt = f"As an AI Visibility Expert, judge if this news is relevant for 'AI Audit Scan Intelligence'. We focus ONLY on AI Search, LLM Indexing, SearchGPT, Perplexity, or Algorithm updates. News: {title}. Answer ONLY 'YES' or 'NO'."
    try:
        response = model.generate_content(prompt)
        return "YES" in response.text.upper()
    except:
        return False

# --- FONCTION PRINCIPALE ---

def fetch_and_write():
    for url in SOURCES:
        print(f"Checking source: {url}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:2]:
            if not is_already_processed(entry.link) and should_i_publish(entry.title, entry.summary):
                print(f"Processing relevant news: {entry.title}")

                # LE PROMPT "HUMAN-ONLY"
                prompt = f"""
                Write a sharp, conversational tech column for 'AiAuditScan Intelligence'.
                Topic: {entry.title}. Summary: {entry.summary}.

                CRITICAL INSTRUCTION: WRITE LIKE A SENIOR TECH JOURNALIST. NO ROBOTIC FILLER.

                🚫 THE "DEAD GIVEAWAY" BLACKLIST (DO NOT USE):
                - VERBS: Delve, Utilize, Leverage, Harness, Foster, Elevate, Revolutionize, Transform, Unleash, Paving the way, Navigate.
                - ADJECTIVES: Comprehensive, Holistic, Nuanced, Pivotal, Inextricably, Transformative, Vibrant, Robust, Cutting-edge, Seamless, Dynamic.
                - NOUNS/ANALOGIES: Tapestry, Realm, Interplay, Kaleidoscope, Symphony, Metamorphosis, Game-changer, Paradigm shift, Testament.

                🚫 BANNED PHRASES & TRANSITIONS:
                - No "In today’s fast-paced world" or "digital landscape".
                - No "It’s important to note", "At the end of the day", "Crucial to understand".
                - No "Furthermore", "Moreover", "Additionally", "In conclusion", "To sum up".
                - No "Let's dive in" or "Deep dive".
                - No "As a testament to" or "It goes without saying".

                🚫 NO DASHES: Do not use em dashes (--) or dashes (-) for structure. Use commas or full stops.

                💡 SIMPLIFICATION RULES:
                - Use "Use" instead of "Utilize".
                - Use "Try" instead of "Endeavor".
                - Use "Help" instead of "Facilitate".
                - Use "Start" instead of "Commence".
                - Use Active Voice only. Cut all unnecessary adjectives.

                STRUCTURE:
                1. THE HOOK: What's the news? (Direct, bold, no fluff).
                2. THE IMPACT: Why does this change AI visibility or AEO? 
                3. THE AIAUDITSCAN TAKE: "Our scans show..." (Insert AI Audit Scan naturally).
                4. ACTION: One clear move for a CMO or CTO to make today.

                LANGUAGE: English.
                """
                
                try:
                    response = model.generate_content(prompt)
                    article_text = response.text
                    
                    # Sauvegarde locale (GitHub Action s'occupera du push)
                    save_to_github(entry.title, article_text, entry.link)
                    
                    # Lien direct vers l'édition GitHub (remplace TON_USER et TON_REPO)
                    github_edit_url = f"https://github.com/TON_USER/TON_REPO/edit/main/_drafts/{entry.title.replace(' ', '_')[:50]}.md"
                    
                    # Notification mobile
                    send_to_telegram(entry.title, article_text, github_edit_url)
                    
                    print(f"✅ News sent to Telegram: {entry.title}")
                    time.sleep(10) 
                    
                except Exception as e:
                    print(f"Error processing {entry.title}: {e}")

if __name__ == "__main__":
    fetch_and_write()
