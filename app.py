import streamlit as st
import requests
import random

st.set_page_config(page_title="Tumblr Feed Casuale", layout="wide")
st.title("🎲 Tumblr Feed Casuale")

# ==== CONFIGURAZIONE - CAMBIA QUESTO! ====
blog_identifier = "pillolediuomo.tumblr.com"  # <-- METTI IL TUO BLOG QUI!
# ========================================

API_KEY = "fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"

# ==== TEST DIAGNOSTICO ====
st.subheader("🔍 Diagnostica")

# Test 1: Info blog
test_url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/info"
test_params = {'api_key': API_KEY}

try:
    response = requests.get(test_url, params=test_params)
    data = response.json()
    
    st.write(f"**URL testato:** `{test_url}`")
    st.write(f"**Status code HTTP:** {response.status_code}")
    st.write(f"**Meta risposta:** {data.get('meta', {})}")
    
    if data.get('meta', {}).get('status') == 200:
        blog_info = data.get('response', {}).get('blog', {})
        st.success(f"✅ Blog trovato! Nome: {blog_info.get('name')}")
        st.write(f"**Post totali:** {blog_info.get('total_posts', 0)}")
        st.write(f"**Visibilità:** {'Pubblico' if blog_info.get('is_adult', False)==False else 'Adulti'}")
    else:
        st.error(f"❌ Errore: {data.get('meta', {}).get('msg')}")
        if data.get('errors'):
            st.json(data.get('errors'))
            
except Exception as e:
    st.error(f"❌ Errore di connessione: {e}")

st.divider()

# ==== RECUPERO POST (solo se il test è ok) ====
@st.cache_data(ttl=3600)
def get_all_posts():
    all_posts = []
    offset = 0
    limit = 20
    
    progress_bar = st.progress(0)
    
    # Prima chiamata per sapere quanti post totali
    url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/posts"
    params = {'api_key': API_KEY, 'limit': 1, 'npf': True}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        total_posts = data.get('response', {}).get('total_posts', 0)
        
        if total_posts == 0:
            st.warning("Il blog ha 0 post pubblici.")
            return []
            
        st.write(f"📊 **Trovati {total_posts} post totali**")
        
        while offset < min(total_posts, 1000):
            params = {'api_key': API_KEY, 'limit': limit, 'offset': offset, 'npf': True}
            response = requests.get(url, params=params)
            data = response.json()
            
            posts = data.get('response', {}).get('posts', [])
            if not posts:
                break
                
            all_posts.extend(posts)
            offset += limit
            progress_bar.progress(min(offset / total_posts, 1.0))
            
    except Exception as e:
        st.error(f"Errore nel recupero: {e}")
        
    progress_bar.empty()
    return all_posts

# Bottone per refresh
if st.button("🔀 Mostra post in ordine casuale"):
    st.cache_data.clear()
    st.rerun()

with st.spinner("Caricamento post..."):
    posts = get_all_posts()

if posts:
    shuffled = random.sample(posts, len(posts))
    st.caption(f"🎲 Mostrati {len(shuffled)} post in ordine casuale")
    
    for post in shuffled:
        with st.container():
            # Mostra contenuto semplificato per test
            st.markdown(f"**ID:** {post.get('id')}")
            st.markdown(f"**Data:** {post.get('date')}")
            st.markdown(f"**URL:** [link]({post.get('post_url')})")
            
            # Mostra un estratto
            if 'summary' in post and post['summary']:
                st.markdown(f"**Riassunto:** {post['summary'][:200]}")
            elif 'content' in post:
                for block in post.get('content', []):
                    if block.get('type') == 'text':
                        st.markdown(block.get('text', '')[:200])
                        break
            
            st.divider()
else:
    st.warning("Nessun post trovato. Controlla i risultati della diagnostica sopra.")
