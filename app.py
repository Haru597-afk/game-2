import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Hardcore Shortest Path Game", layout="centered")

st.title("🔥 เกมคลิกหาเส้นทางที่สั้นที่สุด (ระดับฮาร์ดคอร์)")
st.write(
    "ยินดีต้อนรับสู่โหมดความยากสูงสุด! ระบบจะสร้างกราฟขนาดใหญ่ โครงสร้างซับซ้อน และค่าน้ำหนักที่หลากหลายสะใจ เลือกรูปแบบและความยากด้านล่างแล้วมาท้าทายกันเลย!"
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
    else:
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
        f"จุดเริ่มต้น (Start): โหนด {start_node} | จุดปลายทาง (Finish): โหนด {end_node} (ทั้งหมด {len(G.nodes())} โหนด)"
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
        line=dict(width=1.5, color="#888"),
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
        weight_text.append(str(d["weight"]))

    weight_trace = go.Scatter(
        x=weight_x,
        y=weight_y,
        mode="text",
        text=weight_text,
        textfont=dict(color="red", size=12, family="sans-serif"),
        hoverinfo="none",
    )

    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))
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
        text=node_text,
        textposition="top center",
        hoverinfo="text",
        marker=dict(
            showscale=False,
            color=node_colors,
            size=28,
            line=dict(width=2, color="black"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, weight_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    st.write(
        "👇 **คลิกที่โหนดเพื่อเดินทีละก้าว (ระวังเลือกเส้นทางผิดนะ!):**"
    )
    selected_point = plotly_events(
        fig, click_event=True, hover_event=False, override_height=520
    )

    if selected_point:
        if selected_point[0].get("curveNumber") == 2:
            clicked_idx = selected_point[0]["pointIndex"]
            clicked_node = list(G.nodes())[clicked_idx]
            last_node = st.session_state.user_path[-1]

            if clicked_node == last_node:
                st.warning(f"คุณอยู่ที่โหนด {clicked_node} แล้ว")
            elif G.has_edge(last_node, clicked_node):
                st.session_state.user_path.append(clicked_node)
                st.session_state.submitted = False
                st.rerun()
            else:
                st.error(
                    f"❌ ไม่มีเส้นทางเชื่อมตรงจากโหนด {last_node} ไปยัง {clicked_node}"
                )

    current_user_path = st.session_state.user_path
    total_user_dist = 0

    for i in range(len(current_user_path) - 1):
        u = current_user_path[i]
        v = current_user_path[i + 1]
        total_user_dist += G[u][v]["weight"]

    st.markdown("---")
    path_display = " ➔ ".join(str(n) for n in current_user_path)
    st.write(f"🚶‍♂️ **เส้นทางที่คุณเดินปัจจุบัน:** {path_display}")
    st.write(f"ระยะทางรวมที่คุณเดินตอนนี้: **{total_user_dist} หน่วย**")

    if current_user_path[-1] == end_node:
        st.success(
            "🎯 เดินทางถึงเป้าหมายแล้ว! กดปุ่มด้านล่างเพื่อตรวจคำตอบระดับเซียน"
        )
        if not st.session_state.submitted:
            if st.button("🏁 ยืนยันคำตอบขั้นเด็ดขาด"):
                st.session_state.submitted = True
                st.rerun()
        else:
            if total_user_dist == optimal_dist:
                st.balloons()
                st.success(
                    "🏆 สุดยอดมาก! คุณหาเส้นทางที่สั้นที่สุดในกราฟสุดโหดนี้ได้อย่างแม่นยำ!"
                )
            else:
                st.error(
                    f"❌ ยังไม่ใช่เส้นทางที่สั้นที่สุด! (ระยะทางรวม: {total_user_dist} หน่วย) ลองพยายามหาเส้นทางอื่นที่สั้นกว่านี้ดูอีกครั้ง"
                )
                if st.button("🔄 เริ่มเดินใหม่เพื่อหาเส้นทางที่สั้นกว่า"):
                    st.session_state.user_path = [
                        st.session_state.start_node
                    ]
                    st.session_state.submitted = False
                    st.rerun()
    else:
        st.info("💡 วางแผนเส้นทางอย่างรอบคอบแล้วเดินต่อไปให้ถึงเป้าหมาย")
