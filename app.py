import streamlit as st
import requests
import random
import time

st.set_page_config(page_title="Tumblr Shuffle", layout="wide")
st.title("🎲 Tumblr Feed in Ordine Casuale")

# ==================================================
# ⚠️ CAMBIA QUESTA VARIABILE CON IL NOME DEL TUO BLOG ⚠️
# Esempio: "il-tuo-blog.tumblr.com" (LASCIA .tumblr.com alla fine)
BLOG_IDENTIFIER = "pillolediuomo.tumblr.com"  # <-- METTI IL TUO BLOG QUI!
# ==================================================

API_KEY = "fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"

@st.cache_data(ttl=3600)
def fetch_and_shuffle_posts():
    """Recupera tutti i post pubblici del blog e li restituisce in ordine casuale."""
    all_posts = []
    offset = 0
    limit = 20
    max_retries = 5

    progress_bar = st.progress(0, text="Recupero post dal blog...")

    while True:
        url = f"https://api.tumblr.com/v2/blog/{BLOG_IDENTIFIER}/posts"
        params = {
            'api_key': API_KEY,
            'limit': limit,
            'offset': offset
        }

        retries = 0
        success = False
        response = None

        while not success and retries < max_retries:
            try:
                response = requests.get(url, params=params)
                
                if response.status_code == 429:
                    wait_time = 2 ** retries
                    st.warning(f"Limite API raggiunto. Attesa di {wait_time} secondi...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    success = True
                    break
            except Exception as e:
                st.warning(f"Errore di connessione: {e}. Riprovo...")
                time.sleep(2)
                retries += 1

        if not success or response is None:
            st.error(f"Impossibile recuperare i post dopo {max_retries} tentativi.")
            break

        if response.status_code != 200:
            st.error(f"Errore HTTP: {response.status_code}")
            break

        try:
            data = response.json()
        except Exception as e:
            st.error(f"Errore nel parsing JSON: {e}")
            break

        if data.get('meta', {}).get('status') != 200:
            st.error(f"Errore API: {data.get('meta', {}).get('msg')}")
            break

        if 'response' not in data or 'posts' not in data['response']:
            st.error("Struttura risposta API inaspettata.")
            break

        posts_in_this_batch = data['response']['posts']
        
        if not posts_in_this_batch:
            break

        all_posts.extend(posts_in_this_batch)

        total_posts_on_blog = data['response'].get('total_posts', 0)
        if total_posts_on_blog > 0:
            progress_bar.progress(min(offset / total_posts_on_blog, 1.0))
        
        if len(posts_in_this_batch) < limit:
            break
            
        offset += limit
        
        if offset >= 1000:
            st.warning("Hai più di 1000 post. L'API ne mostra al massimo 1000.")
            break

        time.sleep(0.5)

    progress_bar.empty()

    if not all_posts:
        return []
    
    random.shuffle(all_posts)
    return all_posts

# --- Interfaccia Streamlit ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"**Blog:** `{BLOG_IDENTIFIER}`")
with col2:
    if st.button("🎲 Mescola e Mostra", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

with st.spinner("Caricamento e mescolamento dei post in corso..."):
    shuffled_posts = fetch_and_shuffle_posts()

if shuffled_posts:
    st.success(f"✅ Trovati e mescolati {len(shuffled_posts)} post!")
    
    for i, post in enumerate(shuffled_posts):
        with st.container():
            # Mostra il contenuto principale
            if 'summary' in post and post['summary']:
                st.markdown(f"**{post['summary'][:300]}**")
            elif 'body' in post:
                st.markdown(post['body'][:500], unsafe_allow_html=True)
            elif 'title' in post and post['title']:
                st.markdown(f"## {post['title']}")
                
            # Mostra foto se presenti
            if 'photos' in post and post['photos']:
                photo_url = post['photos'][0]['original_size']['url']
                st.image(photo_url, use_container_width=True)
            
            # Mostra link e data
            col_date, col_link = st.columns([2, 1])
            with col_date:
                st.caption(f"📅 {post.get('date', 'Data sconosciuta')}")
            with col_link:
                st.caption(f"🔗 [Apri post originale]({post.get('post_url', '#')})")
            
            # Mostra i tag
            if 'tags' in post and post['tags']:
                tags_html = " ".join([f'<code style="background-color:#f0f2f6; padding:2px 6px; border-radius:10px;">#{tag}</code>' for tag in post['tags'][:5]])
                st.markdown(f"🏷️ {tags_html}", unsafe_allow_html=True)
            
            st.divider()
            
            # Mostra solo i primi 50 post per performance
            if i >= 49:
                st.info(f"📄 Mostrati i primi 50 post su {len(shuffled_posts)}. Ricarica la pagina per vedere altri post in ordine casuale.")
                break
else:
    st.warning(f"""
    ### ⚠️ Nessun post pubblico trovato per `{BLOG_IDENTIFIER}`
    
    **Possibili cause:**
    1. **Blog privato/nascosto** - L'API non può leggere blog con l'impostazione "Nascondi blog dai risultati di ricerca" attivata
    2. **Blog vuoto** - Nessun post pubblicato
    3. **Nome errato** - Verifica che sia esattamente `nomedeltuoblog.tumblr.com`
    
    **Per verificare, apri questo link nel browser:**
