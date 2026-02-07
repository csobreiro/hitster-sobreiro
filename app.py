import streamlit as st
import pandas as pd
import yt_dlp
import musicbrainzngs as mb
import time
import random
import os
import glob
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Hitster by SOBREIRO", page_icon="🔥", layout="centered")

# --- FUNÇÃO PARA O FUNDO LOCAL ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Tenta aplicar o fundo.png
try:
    if os.path.exists('fundo.png'):
        bin_str = get_base64('fundo.png')
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
            }}
            h1, h3, p, label, .stMarkdown {{
                color: white !important;
                text-shadow: 2px 2px 8px #000000 !important;
            }}
            .stSelectbox, .stNumberInput {{
                background-color: rgba(0,0,0,0.4);
                border-radius: 10px;
                padding: 5px;
            }}
            </style>
            """, unsafe_allow_html=True)
except Exception:
    pass

# Identificação para a base de dados de música
mb.set_useragent("HitsterSobreiroApp", "3.0", "teu@email.com")

# --- FONTES ---
URL_FOGOFRIO = "https://www.youtube.com/playlist?list=PLrMihvbkFsqCvEtiTvKoY78wzNa1udsfs"
OUTRAS_FONTES = [
    "https://www.youtube.com/playlist?list=PLjg3drSMULZHbK0N6BGTCev1xdYX4gT9f",
    "https://www.youtube.com/playlist?list=PL0VFGkqlYy0BE5oxJiYwcj0b3t3F9prGz",
    "https://www.youtube.com/playlist?list=PLw-VjHDlEOgtZJSEFcEhn3L1Fp3qzh_Gz",
    "https://www.youtube.com/playlist?list=PL_bKAgO9uCN0RNEZg2d85TUVPohzw9bxy"
]

# --- FUNÇÕES ---
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
    status.write(f"🚀 SOBREIRO a preparar baralho...")
    musicas_final = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(URL_FOGOFRIO, download=False)
            for m in info['entries']:
                if m:
                    ano = buscar_ano(m['title'])
                    musicas_final.append({"Link": f"https://www.youtube.com/watch?v={m['id']}", "Titulo": m['title'], "Ano": ano, "Origem": "Fogofrio"})
        except: pass
        fontes_baralhadas = OUTRAS_FONTES.copy()
        random.shuffle(fontes_baralhadas)
        for url in fontes_baralhadas:
            if len(musicas_final) >= 500: break
            try:
                info = ydl.extract_info(url, download=False)
                for m in info['entries']:
                    if m and len(musicas_final) < 500:
                        ano = buscar_ano(m['title'])
                        if ano != "???":
                            musicas_final
