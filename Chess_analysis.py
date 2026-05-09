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
                        "PGN": g["pgn"], "Color": "White" if es_blanco else "Black", "Resultado": mi_lado['result'],
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
    st.markdown("## Hub")
    modo = st.radio("Sections", ["📈 Dashboard", "📂PGN Visor", "📅Chess.com History", "🧪 Playground"])
    st.divider()

    # SELECTOR UNIVERSAL DE COLOR (Perspectiva)
    st.write("**Side / Filtro:**")
    color_global = st.radio("Play with:", ["White", "Black"], horizontal=True)
    orientacion = chess.WHITE if color_global == "White" else chess.BLACK

    st.divider()
    user_input = st.text_input("Username", placeholder="MagnusCarlsen")
    hoy = datetime.date.today()
    rango = st.date_input("Period", value=(hoy - datetime.timedelta(days=30), hoy))


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
                st.caption("ADVANTAGE: Black | White")
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

if modo == "📈 Dashboard":
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
                                   color_discrete_sequence=['#bbbbbb' if color_global == "White" else '#404040'])
            st.plotly_chart(fig_res, use_container_width=True)
    else:
        st.info("No data found.")

elif modo == "📂PGN Visor":
    pgn_ejemplo = """1. e4 c5 2. Nc3 Nc6 3. Nf3 g6 4. h4 $6 h6 $2 5. h5 g5 $1 6. d4 $1 cxd4 7. Nxd4 d6 8.
Be3 Nf6 9. f3 Bg7 10. Qd2 O-O 11. O-O-O Nxd4 12. Bxd4 Be6 13. Nd5 Bxd5 $6 14.
exd5 Qc7 15. Kb1 Rac8 16. c3 $2 Qa5 $1 17. Qe1 $2 Rfe8 $6 18. Bxf6 $2 Bxf6 19. Bd3 $4 Kf8
$9 20. Qe4 $4 Rxc3 $3 21. Rc1 Rxc1+ 22. Rxc1 Qb6 $1 23. Qe2 Qd4 24. Be4 a6 25. g4 b5 $1
26. Rc6 a5 $2 27. Qxb5 a4 $2 28. a3 Kg7 29. Ka2 Ra8 30. Rc4 Qf2 31. Rb4 Rc8 32. Qxa4
Rc1 33. Qb3 $2 Qe1 34. Qd3 Ra1+ $1 35. Kb3 Rd1 $2 36. Qc2 $9 Rd2 $1 37. Qc4 Rxb2+ $2 38.
Ka4 Rd2 $1 39. Rb8 $4 Rxd5 $9 40. Bxd5 Qe3 41. Rb3 $6 Qa7+ 42. Kb4 e6 43. Bc6 $6 d5
44. Qb5 $2 Be7+ $9 45. Kc3 Bf6+ $2 46. Kc2 Qf2+ 47. Kc1 $6 Qe1+ 48. Kc2 Qf2+ 49. Kd1 $1
Qg1+ 50. Kd2 Qf2+ $2 51. Qe2 Qd4+ 52. Qd3 Qc5 53. Kd1 $4 Qxc6 54. Rb1 Qd6 55. Rc1
Qh2 56. Rc2 Qh1+ 57. Kd2 Qh2+ 58. Kd1 Qf4 59. Ke2 Qd6 60. Kd1 e5 $2 61. Rd2 e4 $6
62. fxe4 Qb6 $9 63. Qxd5 $9 Qg1+ 64. Ke2 $2 Qe3+ $4 65. Kxe3 Be5 $2 66. Kf3 Bf4 67. Rd4
Kf8 $6 68. Qf5 Ke7 69. Rd7+ Ke8 70. Qxf7# 1-0"""

    # Cambiamos 'placeholder' por 'value' para que el texto sea editable y real
    txt = st.text_area("Paste PGN:", value=pgn_ejemplo, height=250)

    if txt:
        if st.session_state.get('l_pgn') != txt:
            st.session_state.ptr = 0
            st.session_state.l_pgn = txt
        visor_partida(txt)

elif modo == "📅Chess.com History":
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