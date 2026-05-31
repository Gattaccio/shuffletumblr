import streamlit as st
import requests
import random

st.set_page_config(page_title="Tumblr Feed Casuale", layout="wide")
st.title("🎲 Il mio Tumblr in ordine casuale")

blog_identifier = "pillolediuomo.tumblr.com"  # CAMBIA QUESTO!

@st.cache_data(ttl=3600)  # Cache per 1 ora per non chiamare l'API troppo spesso
def get_all_posts():
    all_posts = []
    offset = 0
    limit = 20
    
    progress_bar = st.progress(0)
    
    while True:
        url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/posts"
        params = {'limit': limit, 'offset': offset, 'npf': True}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'response' not in data or 'posts' not in data['response']:
                break
                
            posts = data['response']['posts']
            if not posts:
                break
                
            all_posts.extend(posts)
            offset += limit
            progress_bar.progress(min(offset / 1000, 1.0))
            
        except Exception as e:
            st.error(f"Errore: {e}")
            break
    
    progress_bar.empty()
    return all_posts

# Bottone per nuovo ordine casuale
if st.button("🔀 Nuovo ordine casuale"):
    st.cache_data.clear()

# Recupera e mescola i post
with st.spinner("Caricamento post..."):
    posts = get_all_posts()
    
if posts:
    shuffled_posts = random.sample(posts, len(posts))  # Mescolamento
    
    st.caption(f"📊 {len(shuffled_posts)} post totali")
    
    for post in shuffled_posts:
        with st.container():
            # Tipo di post
            post_type = post.get('type', 'text')
            st.markdown(f"**📝 Tipo:** {post_type}")
            
            # Contenuto in base al tipo
            if post_type == 'text' and 'body' in post:
                st.markdown(post['body'][:500])
            elif post_type == 'photo' and 'photos' in post:
                for photo in post['photos'][:1]:
                    st.image(photo['original_size']['url'], use_container_width=True)
            elif 'summary' in post:
                st.markdown(post['summary'][:300])
            
            # Link al post originale
            post_url = post.get('post_url')
            if post_url:
                st.markdown(f"[🔗 Vedi su Tumblr]({post_url})")
            
            st.divider()
else:
    st.warning("Nessun post trovato sul blog.")
