import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Hardcore Shortest Path Game", layout="centered")

st.title("🔥 เกมคลิกหาเส้นทางที่สั้นที่สุด (ระดับฮาร์ดคอร์)")
st.write(
    "ยินดีต้อนรับสู่โหมดความยากสูงสุด! ระบบจะสร้างกราฟขนาดใหญ่ โครงสร้างซับซ้อน "
    "และค่าน้ำหนักที่หลากหลายสะใจ เลือกรูปแบบและความยากด้านล่างแล้วมาท้าทายกันเลย!"
)

if "game_started" not in st.session_state:
    st.session_state.game_started = False

col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    graph_type = st.selectbox(
        "โครงสร้างกราฟขั้นสูง (Topology)",
        [
            "Small-World (Watts-Strogatz)",
            "Scale-Free (Barabasi-Albert)",
            "Large Grid Graph",
            "Random Geometric Graph",
            "Complex Erdos-Renyi",
        ],
    )
with col_opt2:
    num_nodes = st.slider(
        "จำนวนโหนดในกราฟ (ความยาก)", min_value=10, max_value=25, value=16, step=1
    )


def generate_new_game(g_type, n):
    seed = np.random.randint(1, 10000)
    np.random.seed(seed)

    if g_type == "Small-World (Watts-Strogatz)":
        k = min(4, n - 1)
        G = nx.watts_strogatz_graph(n, k=k, p=0.35, seed=seed)
    elif g_type == "Scale-Free (Barabasi-Albert)":
        m = min(3, max(1, n - 2))
        G = nx.barabasi_albert_graph(n, m=m, seed=seed)
    elif g_type == "Large Grid Graph":
        side = int(np.sqrt(n))
        r, c = side, max(2, n // side)
        G = nx.grid_2d_graph(r, c)
    elif g_type == "Random Geometric Graph":
        G = nx.random_geometric_graph(n, radius=0.45, seed=seed)
        while not nx.is_connected(G):
            seed = np.random.randint(1, 10000)
            G = nx.random_geometric_graph(n, radius=0.45, seed=seed)
    else:  # Complex Erdos-Renyi
        p = max(0.25, 4.0 / n)
        G = nx.erdos_renyi_graph(n, p, seed=seed)
        while not nx.is_connected(G):
            seed = np.random.randint(1, 10000)
            G = nx.erdos_renyi_graph(n, p, seed=seed)

    mapping = {node: i for i, node in enumerate(sorted(G.nodes(), key=str))}
    G = nx.relabel_nodes(G, mapping)

    np.random.seed(seed)
    for u, v in G.edges():
        G[u][v]["weight"] = int(np.random.randint(5, 99))

    nodes = list(G.nodes())
    st.session_state.G = G
    st.session_state.start_node = nodes[0]
    st.session_state.end_node = nodes[-1]
    st.session_state.user_path = [nodes[0]]
    st.session_state.submitted = False
    st.session_state.game_started = True


col_b1, col_b2 = st.columns(2)
with col_b1:
    if (
        st.button("🎮 เริ่มเกมใหม่ / สุ่มแผนที่ฮาร์ดคอร์")
        or not st.session_state.game_started
    ):
        generate_new_game(graph_type, num_nodes)
        st.rerun()
with col_b2:
    if st.button("🔄 รีเซ็ตเส้นทางที่เดิน"):
        st.session_state.user_path = [st.session_state.start_node]
        st.session_state.submitted = False
        st.rerun()

if st.session_state.game_started:
    G = st.session_state.G
    start_node = st.session_state.start_node
    end_node = st.session_state.end_node

    st.info(
        f"จุดเริ่มต้น (Start): โหนด {start_node}
