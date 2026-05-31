import streamlit as st
import requests
import random

st.set_page_config(page_title="Tumblr Shuffle", layout="wide")
st.title("🎲 Tumblr Feed in Ordine Casuale")

# ==================================================
# ⚠️ CAMBIA QUESTA VARIABILE CON IL NOME DEL TUO BLOG ⚠️
# Esempio: "il-tuo-blog.tumblr.com" (LASCIA .tumblr.com alla fine)
BLOG_IDENTIFIER = "pillolediuomo.tumblr.com"
# ==================================================

API_KEY = "fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"

@st.cache_data(ttl=3600)
def fetch_and_shuffle_posts():
    """Recupera tutti i post pubblici del blog e li restituisce in ordine casuale."""
    all_posts = []
    offset = 0
    limit = 20 # Tumblr permette massimo 20 post per chiamata API [citation:1]

    # Crea una barra di progresso per feedback visivo durante il caricamento
    progress_bar = st.progress(0, text="Recupero post dal blog...")

    while True:
        # Costruzione URL chiamata API
        # Nota: Non usiamo 'npf' per mantenere la risposta semplice e stabile [citation:1]
        url = f"https://api.tumblr.com/v2/blog/{BLOG_IDENTIFIER}/posts"
        params = {
            'api_key': API_KEY,
            'limit': limit,
            'offset': offset
        }

        response = requests.get(url, params=params)
        
        # Controllo fondamentale: la richiesta è andata a buon fine?
        if response.status_code != 200:
            st.error(f"Errore di connessione all'API: {response.status_code}")
            break

        data = response.json()
        
        # Verifichiamo che la risposta API sia valida [citation:2]
        if data.get('meta', {}).get('status') != 200:
            st.error(f"Errore API: {data.get('meta', {}).get('msg')}")
            break

        # Estraiamo i post dalla risposta. La struttura è fissa: response -> posts [citation:6]
        posts_in_this_batch = data['response']['posts']
        
        if not posts_in_this_batch:
            # Se non ci sono più post, usciamo dal loop
            break

        # Aggiungiamo i post alla nostra lista completa
        all_posts.extend(posts_in_this_batch)
        
        # Aggiorniamo la progress bar
        total_posts_on_blog = data['response'].get('total_posts', 0)
        if total_posts_on_blog > 0:
            progress_bar.progress(min(offset / total_posts_on_blog, 1.0))
        
        # Se abbiamo recuperato meno post del limite, significa che siamo all'ultima pagina
        if len(posts_in_this_batch) < limit:
            break
            
        # Prepariamo l'offset per la pagina successiva [citation:3]
        offset += limit
        
        # Limite di sicurezza per non fare migliaia di chiamate
        if offset >= 1000:
            st.warning("Hai più di 1000 post. L'API ne mostra al massimo 1000.")
            break

    progress_bar.empty()

    if not all_posts:
        return []
    
    # Mescoliamo TUTTI i post recuperati
    random.shuffle(all_posts)
    return all_posts

# --- Interfaccia Streamlit ---
if st.button("🎲 Mescola e Mostra"):
    # Questo forza la cache a ricaricare i dati al prossimo click
    st.cache_data.clear()

with st.spinner("Caricamento e mescolamento dei post in corso... Attendere."):
    shuffled_posts = fetch_and_shuffle_posts()

if shuffled_posts:
    st.success(f"Trovati e mescolati {len(shuffled_posts)} post!")
    
    # Mostriamo i post, 10 per volta per non appesantire la pagina
    for i, post in enumerate(shuffled_posts):
        with st.container():
            # Mostra il contenuto principale
            if 'summary' in post and post['summary']:
                st.markdown(f"**{post['summary'][:300]}**")
            elif 'body' in post:
                # Per i post di tipo 'text', 'body' contiene l'HTML. Lo mostriamo direttamente.
                st.markdown(post['body'][:500], unsafe_allow_html=True)
            elif 'title' in post and post['title']:
                st.markdown(f"## {post['title']}")
                
            # Mostra foto se presenti (semplificato)
            if 'photos' in post and post['photos']:
                photo_url = post['photos'][0]['original_size']['url']
                st.image(photo_url, use_container_width=True)
            
            # Link e dettagli
            st.caption(f"📅 {post.get('date', 'Data sconosciuta')} | 🔗 [Apri post originale]({post.get('post_url', '#')})")
            
            # Mostra i tag
            if 'tags' in post and post['tags']:
                tags_html = " ".join([f'<code style="background-color:#f0f2f6; padding:2px 6px; border-radius:10px;">#{tag}</code>' for tag in post['tags'][:5]])
                st.markdown(f"🏷️ {tags_html}", unsafe_allow_html=True)
            st.divider()
else:
    st.warning(f"""
    ### Nessun post pubblico trovato per `{BLOG_IDENTIFIER}`.
    
    **Ragioni possibili:**
    1.  **Blog Privato/Nascosto:** L'API non può leggere blog con l'impostazione "Nascondi [blog] dai risultati di ricerca?" attivata. [citation:9]
    2.  **Blog Vuoto:** Il blog non contiene ancora post pubblicati.
    3.  **Nome errato:** Assicurati che il nome sia esattamente come nel tuo URL (es. `miosuperblog.tumblr.com`).
    
    **Per verificare, apri questo link nel browser:**
    `https://api.tumblr.com/v2/blog/{BLOG_IDENTIFIER}/info?api_key={API_KEY}`
    """)
