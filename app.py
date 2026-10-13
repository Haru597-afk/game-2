import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hardcore Shortest Path Game", layout="centered")

st.title("🔥 เกมคลิกหาเส้นทางที่สั้นที่สุด (ระดับฮาร์ดคอร์)")
st.write(
    "ยินดีต้อนรับสู่โหมดความยากสูงสุด! ระบบจะสุ่มจำนวนโหนดและโครงสร้างกราฟให้โดยอัตโนมัติ (สูงสุดไม่เกิน 10 โหนด) พร้อมค่าน้ำหนักที่ชัดเจนบนพื้นหลังสีขาว"
)

if "game_started" not in st.session_state:
    st.session_state.game_started = False

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


def generate_new_game(g_type):
    seed = np.random.randint(1, 10000)
    np.random.seed(seed)
    n = int(np.random.randint(5, 11))

    if g_type == "Small-World (Watts-Strogatz)":
        k = min(3, n - 1)
        G = nx.watts_strogatz_graph(n, k=k, p=0.35, seed=seed)
    elif g_type == "Scale-Free (Barabasi-Albert)":
        m = min(2, max(1, n - 2))
        G = nx.barabasi_albert_graph(n, m=m, seed=seed)
    elif g_type == "Large Grid Graph":
        side = int(np.sqrt(n))
        r, c = side, max(2, n // side)
        G = nx.grid_2d_graph(r, c)
    elif g_type == "Random Geometric Graph":
        G = nx.random_geometric_graph(n, radius=0.55, seed=seed)
        while not nx.is_connected(G):
            seed = np.random.randint(1, 10000)
            G = nx.random_geometric_graph(n, radius=0.55, seed=seed)
    else:
        p = max(0.3, 4.0 / n)
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
        st.button("🎮 เริ่มเกมใหม่ / สุ่มแผนที่และจำนวนโหนด")
        or not st.session_state.game_started
    ):
        generate_new_game(graph_type)
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
        f"จุดเริ่มต้น (Start): โหนด {start_node} | จุดปลายทาง (Finish): โหนด {end_node} (เกมนี้มีทั้งหมด {len(G.nodes())} โหนด)"
    )

    optimal_dist = nx.shortest_path_length(
        G, source=start_node, target=end_node, weight="weight"
    )
    pos = nx.spring_layout(G, seed=42)

    edge_x = []
    edge_y = []
    for u, v, d in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2.5, color="#555"),
        hoverinfo="none",
        mode="lines",
    )

    weight_x = []
    weight_y = []
    weight_text = []
    for u, v, d in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        weight_x.append((x0 + x1) / 2)
        weight_y.append((y0 + y1) / 2)
        weight_text.append(f"<b>[{d['weight']}]</b>")

    weight_trace = go.Scatter(
        x=weight_x,
        y=weight_y,
        mode="text",
        text=weight_text,
        textfont=dict(color="red", size=16),
        hoverinfo="none",
    )

    node_x = []
    node_y = []
    node_colors = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        if node == start_node:
            node_colors.append("lightgreen")
        elif node == end_node:
            node_colors.append("orange")
        elif node in st.session_state.user_path:
            node_colors.append("skyblue")
        else:
            node_colors.append("white")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[str(n) for n in G.nodes()],
        textposition="top center",
        hoverinfo="text",
        marker=dict(
            showscale=False,
            color=node_colors,
            size=36,
            line=dict(width=3, color="black"),
        ),
        textfont=dict(size=14, color="black"),
    )

    fig = go.Figure(
        data=[edge_trace, weight_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="แผนผังเครือข่ายเส้นทางพร้อมค่าน้ำหนัก",
                font=dict(size=16),
            ),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=500,
        ),
    )

    st.plotly_chart(fig)

    with st.expander("📋 ตารางแสดงค่าน้ำหนักของทุกเส้นเชื่อมในกราฟนี้"):
        edge_data = [
            {
                "เส้นเชื่อมระหว่างโหนด": f"{u} ⟷ {v}",
                "ค่าน้ำหนัก (Weight)": G[u][v]["weight"],
            }
            for u, v in G.edges()
        ]
        st.table(edge_
