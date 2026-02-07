import streamlit as st
import pandas as pd
import yt_dlp
import musicbrainzngs as mb
import time
import random
import os
import glob
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Hitster by SOBREIRO", 
    page_icon="🔥", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. FUNÇÃO PARA CARREGAR O FUNDO LOCAL (ANTI-BRANCO) ---
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read())
        st.markdown(
            f"""
            <style>
            /* Define a imagem de fundo na camada base */
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string.decode()}");
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
            }}

            /* FORÇAR TRANSPARÊNCIA: Isto remove as camadas brancas do Streamlit */
            .stAppViewMain, .main, .block-container, [data-testid="stHeader"], [data-testid="stToolbar"] {{
                background-color: rgba(0,0,0,0) !important;
            }}

            /* Criar um cartão escuro para os controlos serem legíveis */
            div[data-testid="stVerticalBlock"] > div:has(div.stFrame), .stTabs {{
                background: rgba(0,0,0,0.7) !important;
                padding: 20px !important;
                border-radius: 20px !important;
                border: 1px solid #333 !important;
            }}

            /* Forçar cor das letras e títulos */
            h1, h2, h3, p, label, .stMarkdown, span, div[data-testid="stMetricValue"] {{
                color: white !important;
                text-shadow: 2px 2px 4px #000000 !important;
            }}

            /* Ajuste dos inputs para não ficarem brancos */
            input, .stSelectbox div {{
                background-color: rgba(0,0,0,0.6) !important;
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"⚠️ Erro: O ficheiro '{image_file}' não foi encontrado no GitHub!")

# Aplicar o fundo
add_bg_from_local('Fundo.png')

# Identificação para MusicBrainz
mb.set_useragent("HitsterSobreiroApp", "3.0", "carlos.mateus.sobreiro@email.com")

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
                            musicas_final.append({"Link": f"https://www.youtube.com/watch?v={m['id']}", "Titulo": m['title'], "Ano": ano, "Origem": "Geral"})
                            progresso.progress(len(musicas_final) / 500)
            except: continue
    random.shuffle(musicas_final)
    df = pd.DataFrame(musicas_final)
    df.insert(0, 'N_Carta', range(1, len(df) + 1))
    df.to_excel(f"{nome_ficheiro}.xlsx", index=False)
    status.success(f"✨ Baralho '{nome_ficheiro}.xlsx' pronto!")

# --- 5. INTERFACE ---
st.title("🔥 Hitster by SOBREIRO")
tab1, tab2 = st.tabs(["▶️ JOGAR", "⚙️ CRIAR BARALHOS"])

with tab2:
    st.header("Fábrica de Baralhos")
    nome_input = st.text_input("Nome do novo baralho:")
    if st.button("🚀 Gerar Excel"):
        if nome_input:
            criar_novo_excel(nome_input)
            st.cache_data.clear()
        else:
            st.error("Escreve um nome!")

with tab1:
    ficheiros = glob.glob("*.xlsx")
    if ficheiros:
        escolha = st.selectbox("Escolhe o teu baralho:", ficheiros)
        @st.cache_data
        def carregar_dados(nome): return pd.read_excel(nome)
        df_jogo = carregar_dados(escolha)
        
        st.divider()
        num = st.number_input(f"Nº da carta:", min_value=1, max_value=len(df_jogo), step=1, value=None)

        if num:
            musica = df_jogo[df_jogo['N_Carta'] == num].iloc[0]
            video_id = musica['Link'].split("v=")[-1].split("&")[0]
            
            st.markdown(f"### 🔊 Carta #{num}")
            st.components.v1.html(f"""
                <div style="position: relative; width: 100%; height: 160px; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid #333;">
                    <iframe src="https://www.youtube-nocookie.com/embed/{video_id}?autoplay=0&rel=0&controls=1&playsinline=1" width="100%" height="160" frameborder="0" allow="autoplay; encrypted-media"></iframe>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 60px; background: #000; z-index: 9999; display: flex; align-items: center; justify-content: center; color: #555; font-family: sans-serif; font-size: 11px; pointer-events: none;">
                        🔒 SOBREIRO PLAYER • TÍTULO OCULTO
                    </div>
                </div>
            """, height=180)
            
            if st.button("Revelar Resposta 🔍"):
                st.success(f"🎵 **{musica['Titulo']}**")
                st.metric("Ano", musica['Ano'])
                if musica['Origem'] == "Fogofrio":
                    st.write("🔥 *Curadoria SOBREIRO*")
    else:
        st.warning("⚠️ Cria um baralho primeiro na aba lateral.")

