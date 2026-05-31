import streamlit as st
import requests
import random

st.set_page_config(page_title="Tumblr Feed Casuale", layout="wide")
st.title("🎲 Il mio Tumblr in ordine casuale")

# ==== CONFIGURAZIONE - CAMBIA QUESTO! ====
blog_identifier = "pillolediuomo.tumblr.com"  # <-- METTI IL TUO BLOG QUI!
# ========================================

API_KEY = "fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"

@st.cache_data(ttl=3600)
def get_all_posts():
    all_posts = []
    offset = 0
    limit = 20
    
    url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/posts"
    
    try:
        params = {
            'api_key': API_KEY,
            'limit': limit,
            'offset': offset
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'response' not in data:
            st.error(f"Risposta API inaspettata: {data.get('meta', {}).get('msg', 'Errore sconosciuto')}")
            return []
        
        posts_data = data['response']
        
        if isinstance(posts_data, list):
            all_posts = posts_data
        elif isinstance(posts_data, dict):
            if 'posts' in posts_data:
                all_posts = posts_data['posts']
            else:
                st.warning(f"Struttura dati ricevuta: {list(posts_data.keys())}")
                return []
        
        if not all_posts:
            return []
        
        total_posts = data.get('response', {}).get('total_posts', len(all_posts))
        
        while len(all_posts) < min(total_posts, 1000) and offset + limit < min(total_posts, 1000):
            offset += limit
            params['offset'] = offset
            response = requests.get(url, params=params)
            data = response.json()
            
            more_posts = data.get('response', {})
            if isinstance(more_posts, dict) and 'posts' in more_posts:
                new_posts = more_posts['posts']
            elif isinstance(more_posts, list):
                new_posts = more_posts
            else:
                break
                
            if not new_posts:
                break
            all_posts.extend(new_posts)
            
    except Exception as e:
        st.error(f"Errore nel recupero: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    return all_posts

if st.button("🔀 Mostra post in ordine casuale"):
    st.cache_data.clear()

with st.spinner("Caricamento post..."):
    posts = get_all_posts()

if posts:
    shuffled = random.sample(posts, len(posts))
    st.caption(f"🎲 Trovati {len(posts)} post. Mostrati in ordine casuale.")
    
    for i, post in enumerate(shuffled[:50]):
        with st.container():
            st.markdown(f"**Post #{i+1}**")
            
            if 'summary' in post and post['summary']:
                st.markdown(f"📝 {post['summary'][:300]}")
            elif 'body' in post:
                st.markdown(f"📝 {post['body'][:300]}")
            elif 'title' in post and post['title']:
                st.markdown(f"📌 **{post['title']}**")
            
            post_url = post.get('post_url')
            if post_url:
                st.markdown(f"[🔗 Vedi il post originale]({post_url})")
            
            if 'date' in post:
                st.caption(f"📅 {post['date']}")
            
            if 'tags' in post and post['tags']:
                tags_str = ", ".join(post['tags'][:5])
                st.caption(f"🏷️ {tags_str}")
            
            st.divider()
else:
    st.warning("Nessun post trovato. Verifica il nome del blog.")
