import streamlit as st
import pandas as pd
import yt_dlp
import musicbrainzngs as mb
import time
import random
import os
import glob

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Hitster by SOBREIRO", page_icon="🔥", layout="centered")

# --- ADICIONAR IMAGEM DE FUNDO ---
# Substitui o link abaixo pelo link da imagem que pretendes usar
LINK_FUNDO = "https://images.unsplash.com/photo-1514525253361-bee8718a74a2?q=80&w=1920&auto=format&fit=crop"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{LINK_FUNDO}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}
    /* Tornar os textos mais legíveis sobre a imagem */
    .stApp h1, .stApp h3, .stApp p, .stApp label {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
    }}
    /* Fundo ligeiramente escuro para os controlos */
    .stSelectbox, .stNumberInput {{
        background-color: rgba(0,0,0,0.5);
        border-radius: 10px;
        padding: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Identificação para a base de dados de música
mb.set_useragent("HitsterSobreiroApp", "3.0", "carlos.mateus.sobreiro@email.com")

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
    
    status.write(f"🚀 SOBREIRO está a preparar o baralho: {nome_ficheiro}...")
    musicas_final = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # 1. Playlist Fogofrio
        try:
            info = ydl.extract_info(URL_FOGOFRIO, download=False)
            for m in info['entries']:
                if m:
                    ano = buscar_ano(m['title'])
                    musicas_final.append({
                        "Link": f"https://www.youtube.com/watch?v={m['id']}", 
                        "Titulo": m['title'], 
                        "Ano": ano, 
                        "Origem": "Fogofrio"
                    })
        except: pass

        # 2. Outras fontes
        fontes_baralhadas = OUTRAS_FONTES.copy()
        random.shuffle(fontes_baralhadas)
        
        for url in fontes_baralhadas:
            if len(musicas_final) >= 500: break
            try:
                info = ydl.extract_info(url, download=False)
                random.shuffle(info['entries'])
                for m in info['entries']:
                    if m and len(musicas_final) < 500:
                        ano = buscar_ano(m['title'])
                        if ano != "???":
                            musicas_final.append({
                                "Link": f"https://www.youtube.com/watch?v={m['id']}", 
                                "Titulo": m['title'], 
                                "Ano": ano, 
                                "Origem": "Geral"
                            })
                            progresso.progress(len(musicas_final) / 500)
            except: continue

    random.shuffle(musicas_final)
    df = pd.DataFrame(musicas_final)
    df.insert(0, 'N_Carta', range(1, len(df) + 1))
    df.to_excel(f"{nome_ficheiro}.xlsx", index=False)
    status.success(f"✨ Baralho '{nome_ficheiro}.xlsx' pronto!")

# --- INTERFACE ---
st.title("🔥 Hitster by SOBREIRO")

tab1, tab2 = st.tabs(["▶️ Jogar", "⚙️ Criar Baralhos"])

with tab2:
    st.header("Fábrica de Baralhos SOBREIRO")
    nome_input = st.text_input("Nome do novo baralho (ex: Mix_Sobreiro):")
    if st.button("🚀 Gerar e Guardar Excel"):
        if nome_input:
            criar_novo_excel(nome_input)
            st.cache_data.clear()
        else:
            st.error("Escreve um nome para o ficheiro!")

with tab1:
    ficheiros = glob.glob("*.xlsx")
    
    if ficheiros:
        escolha = st.selectbox("Escolhe o teu baralho:", ficheiros)
        
        @st.cache_data
        def carregar_dados(nome):
            return pd.read_excel(nome)

        df_jogo = carregar_dados(escolha)
        
        st.divider()
        num = st.number_input(f"Nº da carta (1 a {len(df_jogo)}):", min_value=1, max_value=len(df_jogo), step=1, value=None)

        if num:
            musica = df_jogo[df_jogo['N_Carta'] == num].iloc[0]
            video_id = musica['Link'].split("v=")[-1].split("&")[0]
            
            st.markdown(f"### 🔊 A carregar Carta #{num}")

            # PLAYER ANTI-APP: Usa youtube-nocookie e parâmetros para forçar o browser
            st.components.v1.html(f"""
                <div style="position: relative; width: 100%; height: 160px; background: #000; border-radius: 12px; overflow: hidden; -webkit-mask-image: -webkit-radial-gradient(white, black);">
                    <iframe 
                        src="https://www.youtube-nocookie.com/embed/{video_id}?autoplay=0&rel=0&controls=1&playsinline=1&enablejsapi=1&origin={st.get_option('browser.serverAddress')}" 
                        width="100%" 
                        height="160" 
                        frameborder="0" 
                        allow="autoplay; encrypted-media" 
                        allowfullscreen
                        style="pointer-events: auto;">
                    </iframe>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 60px; background: #000; z-index: 9999; display: flex; align-items: center; justify-content: center; color: #555; font-family: sans-serif; font-size: 11px; letter-spacing: 1px; pointer-events: none; border-bottom: 1px solid #222;">
                        🔒 SOBREIRO PLAYER • TÍTULO OCULTO
                    </div>
                </div>
            """, height=180)
            
            st.caption("Clica no Play no centro. Se o telemóvel pedir para abrir em ecrã inteiro, recusa para não veres o título.")

            if st.button("Revelar Resposta 🔍"):
                st.success(f"🎵 **{musica['Titulo']}**")
                st.metric("Ano Original", musica['Ano'])
                if musica['Origem'] == "Fogofrio":
                    st.write("🔥 *Curadoria SOBREIRO*")
    else:
        st.warning("⚠️ Nenhum baralho encontrado. Vai a 'Criar Baralhos'.")
