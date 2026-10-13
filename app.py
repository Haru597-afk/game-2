import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Shortest Path Click Game", layout="centered")

st.title("🗺️ เกมคลิกเลือกเส้นทางที่สั้นที่สุด (Shortest Path Click Game)")
st.write(
    "กติกา: เลือกรูปแบบกราฟและกดเริ่มเกม จากนั้นคลิกที่โหนดเพื่อเดินไปยังเป้าหมาย "
    "โดยระบบจะไม่เฉลยระหว่างทาง ให้กดปุ่มยืนยันในตอนท้ายเพื่อตรวจคำตอบ!"
)

# 1) ตั้งค่าสถานะเกมด้วย st.session_state
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# เพิ่มตัวเลือกรูปแบบกราฟใน Sidebar หรือส่วนหัว
graph_type = st.selectbox(
    "เลือกรูปแบบกราฟ (Graph Topology)",
    [
        "สุ่มทั่วไป (Erdos-Renyi)",
        "กราฟตาราง (Grid Graph)",
        "กราฟวงแหวน (Cycle & Chords)",
        "กราฟต้นไม้ (Balanced Tree)",
        "กราฟสมบูรณ์ (Complete Graph)",
    ],
)


def generate_new_game(g_type):
    seed = np.random.randint(1, 1000)
    np.random.seed(seed)

    if g_type == "กราฟตาราง (Grid Graph)":
        # สร้าง Grid 2x3 หรือ 3x3 (ใช้ m=2, n=3 ให้มี 6 โหนด)
        G = nx.grid_2d_graph(2, 3)
        # เปลี่ยนชื่อโหนดจาก tuple (x,y) เป็นตัวเลข 0 ถึง 5 เพื่อให้ใช้ง่าย
        mapping = {node: i for i, node in enumerate(G.nodes())}
        G = nx.relabel_nodes(G, mapping)
    elif g_type == "กราฟวงแหวน (Cycle & Chords)":
        n = 6
        G = nx.cycle_graph(n)
        # เพิ่มเส้นเชื่อมทแยงมุมเพิ่มความท้าทาย
        if seed % 2 == 0:
            G.add_edge(0, 3)
            G.add_edge(1, 4)
        else:
            G.add_edge(0, 4)
            G.add_edge(1, 3)
    elif g_type == "กราฟต้นไม้ (Balanced Tree)":
        # r=2, h=2 ให้ได้ 7 โหนด (หรือปรับตามต้องการ)
        G = nx.balanced_tree(2, 2)
    elif g_type == "กราฟสมบูรณ์ (Complete Graph)":
        n = 5
        G = nx.complete_graph(n)
    else:  # สุ่มทั่วไป (Erdos-Renyi)
        n = 6
        G = nx.erdos_renyi_graph(n, 0.45, seed=seed)
        while not nx.is_connected(G):
            seed = np.random.randint(1, 1000)
            G = nx.erdos_renyi_graph(n, 0.45, seed=seed)

    # สุ่มค่าน้ำหนัก (Weight) ให้กับทุกเส้นเชื่อม
    for u, v in G.edges():
        G[u][v]["weight"] = int(np.random.randint(1, 20))

    nodes = list(G.nodes())
    st.session_state.G = G
    st.session_state.start_node = nodes[0]
    st.session_state.end_node = nodes[-1]
    st.session_state.user_path = [nodes[0]]
    st.session_state.submitted = False
    st.session_state.game_started = True


# ปุ่มเริ่มเกมหรือสุ่มแผนที่ใหม่
col_b1, col_b2 = st.columns(2)
with col_b1:
    if (
        st.button("🎮 เริ่มเกมใหม่ / สุ่มแผนที่")
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
        f"จุดเริ่มต้น (Start): โหนด {start_node}  |  จุดปลายทาง (Finish): โหนด {end_node}"
    )

    # คำนวณคำตอบที่สั้นที่สุดด้วย Dijkstra
    optimal_path = nx.shortest_path(
        G, source=start_node, target=end_node, weight="weight"
    )
    optimal_dist = nx.shortest_path_length(
        G, source=start_node, target=end_node, weight="weight"
    )

    # กำหนด Layout ตามรูปแบบกราฟเพื่อให้แสดงผลสวยงามขึ้น
    if "Grid Graph" in graph_type:
        pos = nx.spring_layout(G, seed=42)
    elif "Balanced Tree" in graph_type:
        pos = nx.spring_layout(G, seed=42)
    else:
        pos = nx.spring_layout(G, seed=42)

    # 1. วาดเส้นเชื่อม (Edges)
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
        line=dict(width=2, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # 2. เพิ่มตัวเลขแสดงระยะทาง (Weight) ไว้ตรงกลางเส้นเชื่อม
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
        textfont=dict(color="red", size=14, family="sans-serif"),
        hoverinfo="none",
    )

    # 3. วาดโหนด (Nodes)
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
            size=35,
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

    # แสดงกราฟและดักจับการคลิกเมาส์
    st.write("👇 **คลิกที่โหนดบนแผนภาพเพื่อเดินทีละก้าว:**")
    selected_point = plotly_events(
        fig, click_event=True, hover_event=False, override_height=450
    )

    # ถ้ามีการคลิกที่โหนด
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

    # คำนวณระยะทางที่ผู้เล่นเดินสะสม
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

    # หากเดินถึงโหนดปลายทางแล้ว ให้แสดงปุ่มคอนเฟิร์ม
    if current_user_path[-1] == end_node:
        st.success(
            "🎯 คุณเดินมาถึงจุดปลายทางแล้ว! กดปุ่มด้านล่างเพื่อยืนยันและตรวจคำตอบ"
        )
        if not st.session_state.submitted:
            if st.button("🏁 ยืนยันคำตอบ (Confirm Path)"):
                st.session_state.submitted = True
                st.rerun()
        else:
            if total_user_dist == optimal_dist:
                st.balloons()
                st.success(
                    "🎉 ยินดีด้วย! คุณหาเส้นทางที่สั้นที่สุดได้ถูกต้องและยอดเยี่ยมมาก!"
                )
            else:
                optimal_str = " ➔ ".join(str(n) for n in optimal_path)
                st.info(
                    f"🏁 ผลลัพธ์: ระยะทางรวมของคุณคือ {total_user_dist} หน่วย"
                    f" (เส้นทางที่สั้นที่สุดจริง ๆ คือ {optimal_dist} หน่วย: {optimal_str})"
                )
    else:
        st.info("💡 เดินทางต่อไปให้ถึงโหนดปลายทาง (Finish) เพื่อทำการยืนยันคำตอบ")
