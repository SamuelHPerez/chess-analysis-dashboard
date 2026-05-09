import streamlit as st
import pandas as pd
import chess.pgn
import chess.svg
import plotly.express as px
import requests
from io import StringIO
import datetime

# --- CONFIGURACIÓN ESTÉTICA (DARK CHESS THEME) ---
st.set_page_config(page_title="Chess Intelligence", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    .stMetric { background-color: #161616; padding: 20px; border-radius: 8px; border: 1px solid #262626; }
    .stButton > button { background-color: #262626; color: white; border: 1px solid #404040; }
    .stButton > button:hover { border-color: #d4af37; color: #d4af37; }
    </style>
""", unsafe_allow_html=True)


# --- MOTOR Y LÓGICA ---
@st.cache_data(ttl=3600, show_spinner=False)
def consultar_motor(fen):
    try:
        url = f"https://lichess.org/api/cloud-eval?fen={fen}"
        res = requests.get(url, timeout=1.0).json()
        if "pvs" in res:
            move = res["pvs"][0]["moves"].split()[0]
            score = res["pvs"][0].get("cp", 0) / 100.0
            return move, score
    except:
        pass
    return None, None


@st.cache_data(show_spinner="Calculando métricas...")
def cargar_historial_completo(user, inicio, fin):
    headers = {"User-Agent": "SamuelChessApp/1.0"}
    rows = []
    try:
        url_base = f"https://api.chess.com/pub/player/{user}/games/archives"
        archivos = requests.get(url_base, headers=headers).json().get("archives", [])
        for arc in reversed(archivos[-2:]):
            partidas = requests.get(arc, headers=headers).json().get("games", [])
            for g in partidas:
                dt = datetime.date.fromtimestamp(g["end_time"])
                if inicio <= dt <= fin:
                    w, b = g["white"], g["black"]
                    es_blanco = w['username'].lower() == user.lower()
                    mi_lado = w if es_blanco else b
                    rival_lado = b if es_blanco else w
                    rows.append({
                        "Fecha": dt, "Dia_Semana": dt.strftime('%A'), "Label": f"{w['username']} vs {b['username']}",
                        "PGN": g["pgn"], "Color": "Blanco" if es_blanco else "Negro", "Resultado": mi_lado['result'],
                        "Win_Val": 1 if mi_lado['result'] == 'win' else (
                            0.5 if mi_lado['result'] in ['draw', 'repetition', 'stalemate'] else 0),
                        "Mi_Elo": mi_lado['rating'], "Rival_Elo": rival_lado['rating']
                    })
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()


# --- ESTADO DE SESIÓN ---
if 'ptr' not in st.session_state: st.session_state.ptr = 0
if 'playground_board' not in st.session_state: st.session_state.playground_board = chess.Board()

# --- SIDEBAR: SELECTOR UNIVERSAL ---
with st.sidebar:
    st.markdown("## ♟️ Samuel's Hub")
    modo = st.radio("Secciones", ["📈 Dashboard Pro", "📂 Visor PGN", "📅 Chess.com", "🧪 Playground"])
    st.divider()

    # SELECTOR UNIVERSAL DE COLOR (Perspectiva)
    st.write("**Perspectiva / Filtro:**")
    color_global = st.radio("Juego con:", ["Blanco", "Negro"], horizontal=True)
    orientacion = chess.WHITE if color_global == "Blanco" else chess.BLACK

    st.divider()
    user_input = st.text_input("Username")
    hoy = datetime.date.today()
    rango = st.date_input("Periodo", value=(hoy - datetime.timedelta(days=30), hoy))


# --- FUNCION VISOR ACTUALIZADA ---
def visor_partida(pgn_string, orientacion_manual=None):
    # Usamos la orientación global si no se especifica una manual
    lado_tablero = orientacion_manual if orientacion_manual is not None else orientacion

    juego = chess.pgn.read_game(StringIO(pgn_string))
    if not juego: return
    movs = []
    b_aux = juego.board()
    for m in juego.mainline_moves():
        movs.append({"obj": m, "san": b_aux.san(m)})
        b_aux.push(m)

    col_t, col_i = st.columns([1.2, 1])
    b_render = juego.board()
    for m in movs[:st.session_state.ptr]: b_render.push(m["obj"])

    with col_t:
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("⏪"): st.session_state.ptr = 0
        if c2.button("⬅️"): st.session_state.ptr = max(0, st.session_state.ptr - 1)
        if c3.button("➡️"): st.session_state.ptr = min(len(movs), st.session_state.ptr + 1)
        if c4.button("⏩"): st.session_state.ptr = len(movs)

        last = movs[st.session_state.ptr - 1]["obj"] if st.session_state.ptr > 0 else None
        svg = chess.svg.board(
            board=b_render,
            size=500,
            lastmove=last,
            orientation=lado_tablero
        )
        st.image(svg, use_container_width=True)

    with col_i:
        # 1. Aquí se abre el contenedor (la marca dorada que ves)
        st.markdown('<div class="eval-card">', unsafe_allow_html=True)

        m_m, m_e = consultar_motor(b_render.fen())

        if m_m:
            # 1. Lógica de cálculo
            score_clamped = max(-5, min(5, m_e))
            score_normalized = (score_clamped + 5) / 10

            # 2. Renderizado limpio
            with st.container():
                st.caption("VENTAJA: NEGRO | BLANCO")
                st.progress(score_normalized)

                col_metrics1, col_metrics2 = st.columns(2)
                with col_metrics1:
                    st.metric("Engine Eval", f"{m_e:+.2f}")
                with col_metrics2:
                    st.markdown(f"**Best Move**")
                    st.markdown(
                        f"<h2 style='color:#d4af37; margin-top:-15px;'>{b_render.san(chess.Move.from_uci(m_m))}</h2>",
                        unsafe_allow_html=True)

        # 3. Cerramos el contenedor
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.container(height=350):
            for i in range(0, len(movs), 2):
                cn, cw, cb = st.columns([0.3, 1, 1])
                cn.write(f"{int(i / 2) + 1}.")
                if cw.button(movs[i]["san"], key=f"v_w_{i}"): st.session_state.ptr = i + 1
                if i + 1 < len(movs):
                    if cb.button(movs[i + 1]["san"], key=f"v_b_{i}"): st.session_state.ptr = i + 2


# --- MODOS ---

if modo == "📈 Dashboard Pro":
    st.header(f"Performance Analysis: {user_input}")
    df_raw = cargar_historial_completo(user_input, rango[0], rango[1])

    if not df_raw.empty:
        # FILTRO DINÁMICO basado en el Selector Universal
        df = df_raw[df_raw['Color'] == color_global]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Win Rate ({color_global})", f"{(df['Win_Val'].mean() * 100):.1f}%")
        c2.metric("Games Played", len(df))
        c3.metric("Elo Average", int(df['Mi_Elo'].mean()))
        c4.metric("Color Strength", "High" if df['Win_Val'].mean() > 0.5 else "Neutral")

        st.divider()
        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(px.line(df, x="Fecha", y="Mi_Elo", title=f"Rating Progression as {color_global}",
                                    template="plotly_dark", color_discrete_sequence=['#ffffff']),
                            use_container_width=True)

            dias_ord = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            df_d = df.groupby('Dia_Semana')['Win_Val'].mean().reindex(dias_ord).reset_index()
            st.plotly_chart(px.bar(df_d, x='Dia_Semana', y='Win_Val', title=f"Efficiency per Day ({color_global})",
                                   template="plotly_dark", color_discrete_sequence=['#404040']),
                            use_container_width=True)
        with col_r:
            fig_res = px.histogram(df, x="Resultado", title=f"Outcomes as {color_global}",
                                   template="plotly_dark",
                                   color_discrete_sequence=['#bbbbbb' if color_global == "Blanco" else '#404040'])
            st.plotly_chart(fig_res, use_container_width=True)
    else:
        st.info("No data found.")

elif modo == "📂 Visor PGN":
    txt = st.text_area("Paste PGN:", height=150)
    if txt:
        if st.session_state.get('l_pgn') != txt: st.session_state.ptr = 0; st.session_state.l_pgn = txt
        visor_partida(txt)

elif modo == "📅 Chess.com":
    df_h = cargar_historial_completo(user_input, rango[0], rango[1])
    if not df_h.empty:
        # Filtramos el historial para que coincida con el selector
        df_filtered = df_h[df_h['Color'] == color_global]
        if not df_filtered.empty:
            idx = st.selectbox("Select Match:", df_filtered.index,
                               format_func=lambda x: f"{df_filtered.loc[x, 'Fecha']} | {df_filtered.loc[x, 'Label']}")
            if st.session_state.get('c_g') != idx: st.session_state.ptr = 0; st.session_state.c_g = idx
            visor_partida(df_filtered.loc[idx, 'PGN'])
        else:
            st.warning(f"No hay partidas registradas con piezas {color_global.lower()} en este rango.")

elif modo == "🧪 Playground":
    st.subheader("Tactical Sandbox")
    cp, cc = st.columns([1.2, 1])
    with cc:
        with st.form("p_form", clear_on_submit=True):
            m = st.text_input("Enter Move (SAN):")
            if st.form_submit_button("Execute"):
                try:
                    st.session_state.playground_board.push_san(m); st.rerun()
                except:
                    st.error("Illegal")
        if st.button("↩️ Undo") and st.session_state.playground_board.move_stack:
            st.session_state.playground_board.pop();
            st.rerun()
        m_m, m_e = consultar_motor(st.session_state.playground_board.fen())
        if m_m: st.markdown(f"### Eval: `{m_e:+.2f}`")
    with cp:
        st.image(chess.svg.board(st.session_state.playground_board, size=500, orientation=orientacion),
                 use_container_width=True)