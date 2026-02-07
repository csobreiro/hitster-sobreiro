import streamlit as st
import pandas as pd
import yt_dlp
import musicbrainzngs as mb
import time
import random
import os
import glob

# --- 1. CONFIGURAÇÃO DA PÁGINA (FORÇAR TEMA ESCURO) ---
st.set_page_config(
    page_title="Hitster by SOBREIRO", 
    page_icon="🔥", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. DESIGN NEON E FUNDO (COM OVERRIDE DE BRANCO) ---
LINK_IMAGEM = "https://images.unsplash.com/photo-1514525253361-bee8718a74a2?q=80&w=1920&auto=format&fit=crop"

st.markdown(f"""
    <style>
    /* Forçar o fundo em todas as camadas possíveis */
    .stApp, .stAppViewMain, .main, .block-container {{
        background-image: url("{LINK_IMAGEM}") !important;
        background-attachment: fixed !important;
        background-size: cover !important;
        background-position: center !important;
        background-color: #000000 !important; /* Caso a imagem falhe, fica preto */
    }}

    /* Container central (Cartão de Jogo) - Mais opaco para garantir leitura */
    .main .block-container {{
        background-color: rgba(0, 0, 0, 0.85) !important;
        padding: 1.5rem !important;
        border-radius: 20px !important;
        margin-top: 20px !important;
        border: 2px solid #ff00ff !important;
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.5) !important;
        max-width: 95% !important;
    }}

    /* Títulos e Textos com brilho */
    h1 {{
        color: #00ffff !important;
        text-shadow: 0 0 15px #00ffff !important;
        text-align: center !important;
    }}
    
    label, p, span, div {{
        color: #ffffff !important;
    }}

    /* Estilo das Abas */
    button[data-baseweb="tab"] {{
        background-color: transparent !important;
        color: #888 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #ff00ff !important;
        color: white !important;
    }}

    /* Esconder o cabeçalho padrão do Streamlit que é branco */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# Identificação
mb.set_useragent("HitsterSobreiroApp", "3.0", "teu@email.com")

# --- 3. FONTES ---
URL_FOGOFRIO = "https://www.youtube.com/playlist?list=PLrMihvbkFsqCvEtiTvKoY78wzNa1udsfs"
OUTRAS_FONTES = [
    "https://www.youtube.com/playlist?list=PLjg3drSMULZHbK0N6BGTCev1xdYX4gT9f",
    "https://www.youtube.com/playlist?list=PL0VFGkqlYy0BE5oxJiYwcj0b3t3F9prGz",
    "https://www.youtube.com/playlist?list=PLw-VjHDlEOgtZJSEFcEhn3L1Fp3qzh_Gz",
    "https://www.youtube.com/playlist?list=PL_bKAgO9uCN0RNEZg2d85TUVPohzw9bxy"
]

# --- 4. FUNÇÕES ---
def buscar_ano(titulo):
    busca = titulo.split('(')[0].split('[')[0].replace('Official Video', '').strip()
    try:
        time.sleep(0.3) 
        res = mb.search_releases(query=busca, limit=1)
        if res['release-list']:
            data = res['release-list'][0].get('date', '')
            if data: return data.split('-')[0]
    except: pass
    return "???" 

def criar_novo_excel(nome_ficheiro):
    progresso = st.progress(0)
    status = st.empty()
    ydl_opts = {'quiet': True, 'extract_flat': True}
    status.write(f"🚀 SOBREIRO a fabricar baralho...")
    musicas_final = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(URL_FOGOFRIO, download=False)
            for m in info['entries']:
                if m:
                    ano = buscar_ano(m['title'])
                    musicas_final.append({"Link": f"https://www.youtube.com/watch?v={m['id']}", "Titulo": m['title'], "Ano": ano, "Origem": "Fogofrio"})
        except: pass
        for url in OUTRAS_FONTES:
            if len(musicas_final) >= 500: break
            try:
                info = ydl.extract_info(url, download=False)
                for m in info['entries']:
                    if m and len(musicas_final) < 500:
                        ano = buscar_ano(m['title'])
                        if ano != "???":
                            musicas_final.append({"Link": f"https://www.youtube.com/watch?v={m['id']}", "Titulo": m['title'], "Ano": ano, "Origem": "Geral"})
                            progresso.progress(len(musicas_final) / 500)
            except: continue
    random.shuffle(musicas_final)
    df = pd.DataFrame(musicas_final)
    df.insert(0, 'N_Carta', range(1, len(df) + 1))
    df.to_excel(f"{nome_ficheiro}.xlsx", index=False)
    status.success(f"✨ Pronto!")

# --- 5. INTERFACE ---
st.title("🔥 Hitster by SOBREIRO")
tab1, tab2 = st.tabs(["▶️ JOGAR", "⚙️ CRIAR"])

with tab2:
    nome_input = st.text_input("Nome do baralho:")
    if st.button("🚀 Gerar Excel"):
        if nome_input:
            criar_novo_excel(nome_input)
            st.cache_data.clear()

with tab1:
    ficheiros = glob.glob("*.xlsx")
    if ficheiros:
        escolha = st.selectbox("Baralho:", ficheiros)
        @st.cache_data
        def carregar_dados(nome): return pd.read_excel(nome)
        df_jogo = carregar_dados(escolha)
        
        num = st.number_input(f"Nº da carta:", min_value=1, max_value=len(df_jogo), step=1, value=None)

        if num:
            musica = df_jogo[df_jogo['N_Carta'] == num].iloc[0]
            video_id = musica['Link'].split("v=")[-1].split("&")[0]
            
            st.markdown(f"### 🔊 Carta #{num}")
            st.components.v1.html(f"""
                <div style="position: relative; width: 100%; height: 160px; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid #00ffff;">
                    <iframe src="https://www.youtube-nocookie.com/embed/{video_id}?autoplay=0&rel=0&controls=1&playsinline=1" width="100%" height="160" frameborder="0" allow="autoplay; encrypted-media"></iframe>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 60px; background: #000; z-index: 9999; display: flex; align-items: center; justify-content: center; color: #00ffff; font-family: sans-serif; font-size: 11px; letter-spacing: 2px; pointer-events: none;">
                        🔒 SOBREIRO PLAYER
                    </div>
                </div>
            """, height=180)
            
            if st.button("Revelar Resposta 🔍"):
                st.markdown(f"<h2 style='color: #ff00ff; text-align: center;'>{musica['Titulo']}</h2>", unsafe_allow_html=True)
                st.metric("Ano", musica['Ano'])
    else:
        st.warning("Cria um baralho primeiro.")
