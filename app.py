import streamlit as st
import pandas as pd
import yt_dlp
import musicbrainzngs as mb
import time
import random
import os
import glob

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Hitster by SOBREIRO", page_icon="🔥")
mb.set_useragent("HitsterSobreiroApp", "3.0", "teu@email.com")

URL_FOGOFRIO = "https://www.youtube.com/playlist?list=PLrMihvbkFsqCvEtiTvKoY78wzNa1udsfs"
OUTRAS_FONTES = [
    "https://www.youtube.com/playlist?list=PLjg3drSMULZHbK0N6BGTCev1xdYX4gT9f",
    "https://www.youtube.com/playlist?list=PL0VFGkqlYy0BE5oxJiYwcj0b3t3F9prGz",
    "https://www.youtube.com/playlist?list=PLw-VjHDlEOgtZJSEFcEhn3L1Fp3qzh_Gz",
    "https://www.youtube.com/playlist?list=PL_bKAgO9uCN0RNEZg2d85TUVPohzw9bxy"
]

# --- FUNÇÕES ---

def obter_url_audio_direto(youtube_url):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=False)
            return info['url']
        except: return None

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

    # Mistura tudo
    random.shuffle(musicas_final)
    
    # CRIA O DATAFRAME E ADICIONA A COLUNA DE NUMERAÇÃO NO EXCEL
    df = pd.DataFrame(musicas_final)
    df.insert(0, 'N_Carta', range(1, len(df) + 1)) # Cria a coluna na posição 0
    
    df.to_excel(f"{nome_ficheiro}.xlsx", index=False)
    status.success(f"✨ Baralho '{nome_ficheiro}.xlsx' criado com numeração de 1 a {len(df)}!")

# --- INTERFACE ---
st.title("🔥 Hitster by SOBREIRO")

tab1, tab2 = st.tabs(["▶️ Jogar", "⚙️ Criar Baralhos"])

with tab2:
    st.header("Fábrica de Baralhos SOBREIRO")
    nome_input = st.text_input("Nome do novo baralho:")
    if st.button("🚀 Gerar Ficheiro Excel"):
        if nome_input:
            criar_novo_excel(nome_input)
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
            # Procura a música que tem o número correspondente na coluna 'N_Carta'
            musica = df_jogo[df_jogo['N_Carta'] == num].iloc[0]
            st.markdown(f"### 🔊 A tocar Carta #{num}")
            
            url_direta = obter_url_audio_direto(musica['Link'])
            if url_direta:
                st.audio(url_direta)
            
            if st.button("Revelar Resposta 🔍"):
                st.success(f"🎵 **{musica['Titulo']}**")
                st.metric("Ano", musica['Ano'])
                if musica['Origem'] == "Fogofrio":
                    st.caption("🔥 Curadoria SOBREIRO: Esta música veio da tua playlist principal!")
    else:
        st.warning("Nenhum baralho encontrado. Vai a 'Criar Baralhos'.")