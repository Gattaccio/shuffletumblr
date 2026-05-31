import streamlit as st
import requests
import random

st.set_page_config(page_title="Tumblr Feed Casuale", layout="wide")
st.title("🎲 Il mio Tumblr in ordine casuale")

# CAMBIA QUESTO con il nome del tuo blog (es. "mio-blog.tumblr.com")
blog_identifier = "il-tuo-blog.tumblr.com"

# API key pubblica di Tumblr (funziona per tutti i blog pubblici)
# Questa è la chiave demo ufficiale di Tumblr
API_KEY = "fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"

@st.cache_data(ttl=3600)
def get_all_posts():
    all_posts = []
    offset = 0
    limit = 20
    
    progress_bar = st.progress(0)
    
    while True:
        # URL CORRETTO con api_key
        url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/posts"
        params = {
            'api_key': API_KEY,      # ← fondamentale!
            'limit': limit,
            'offset': offset,
            'npf': True              # formato moderno
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # Debug: mostra se c'è errore
            if data.get('meta', {}).get('status') != 200:
                st.error(f"Errore API: {data.get('meta', {}).get('msg', 'Sconosciuto')}")
                break
            
            posts = data['response']['posts']
            if not posts:
                break
                
            all_posts.extend(posts)
            offset += limit
            
            # Aggiorna progress bar
            total = data['response'].get('total_posts', 0)
            if total > 0:
                progress_bar.progress(min(offset / total, 1.0))
            
            # Limite di sicurezza
            if offset >= 1000 or offset >= total:
                break
                
        except Exception as e:
            st.error(f"Errore: {e}")
            break
    
    progress_bar.empty()
    return all_posts

# Bottone per nuovo ordine
if st.button("🔀 Nuovo ordine casuale"):
    st.cache_data.clear()
    st.rerun()

# Carica e mostra i post
with st.spinner("Caricamento post..."):
    posts = get_all_posts()

if posts:
    shuffled_posts = random.sample(posts, len(posts))
    st.caption(f"📊 {len(shuffled_posts)} post totali")
    
    for post in shuffled_posts:
        with st.container():
            post_type = post.get('type', 'text')
            st.markdown(f"**📝 Tipo:** {post_type}")
            
            # Gestione contenuto per NPF (formato moderno)
            if 'content' in post:  # NPF format
                for block in post.get('content', []):
                    if block.get('type') == 'text':
                        st.markdown(block.get('text', '')[:500])
                    elif block.get('type') == 'image':
                        for media in block.get('media', []):
                            if 'url' in media:
                                st.image(media['url'], use_container_width=True)
            else:  # Legacy format
                if post_type == 'text' and 'body' in post:
                    st.markdown(post['body'][:500])
                elif post_type == 'photo' and 'photos' in post:
                    for photo in post['photos'][:1]:
                        st.image(photo['original_size']['url'], use_container_width=True)
                elif 'summary' in post:
                    st.markdown(post['summary'][:300])
            
            post_url = post.get('post_url')
            if post_url:
                st.markdown(f"[🔗 Vedi su Tumblr]({post_url})")
            
            st.divider()
else:
    st.warning("Nessun post trovato. Verifica che il blog esista e sia pubblico.")
