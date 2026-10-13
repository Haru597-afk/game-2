import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Shortest Path Click Game", layout="centered")

st.title("🗺️ เกมคลิกเลือกเส้นทางที่สั้นที่สุด (Shortest Path Click Game)")
st.write(
    "กติกา: ระบบจะสุ่มกราฟ จุดเริ่มต้น และจุดปลายทางให้ "
    "ให้คุณใช้เมาส์คลิกที่โหนดบนรูปแผนภาพเพื่อเดินตามเส้นทาง แล้วระบบจะรวมระยะทางให้ทันที!"
)

# 1) ตั้งค่าสถานะเกมด้วย st.session_state
if "game_started" not in st.session_state:
  st.session_state.game_started = False


def generate_new_game():
  n = 6
  seed = np.random.randint(1, 1000)
  G = nx.erdos_renyi_graph(n, 0.45, seed=seed)
  while not nx.is_connected(G):
    seed = np.random.randint(1, 1000)
    G = nx.erdos_renyi_graph(n, 0.45, seed=seed)

  np.random.seed(seed)
  for u, v in G.edges():
    G[u][v]["weight"] = int(np.random.randint(1, 20))

  nodes = list(G.nodes())
  st.session_state.G = G
  st.session_state.start_node = nodes[0]
  st.session_state.end_node = nodes[-1]
  st.session_state.user_path = [nodes[0]]
  st.session_state.game_started = True


# ปุ่มเริ่มเกมหรือสุ่มแผนที่ใหม่
col_b1, col_b2 = st.columns(2)
with col_b1:
  if st.button("🎮 เริ่มเกมใหม่ / สุ่มแผนที่") or not st.session_state.game_started:
    generate_new_game()
    st.rerun()
with col_b2:
  if st.button("🔄 รีเซ็ตเส้นทางที่เดิน"):
    st.session_state.user_path = [st.session_state.start_node]
    st.rerun()

if st.session_state.game_started:
  G = st.session_state.G
  start_node = st.session_state.start_node
  end_node = st.session_state.end_node

  st.info(
      f"จุดเริ่มต้น (Start): โหนด **{start_node}**  |  จุดปลายทาง (Finish): โหนด"
      f" **{end_node}**"
  )

  # คำนวณคำตอบที่สั้นที่สุดด้วย Dijkstra รอไว้เทียบ
  optimal_path = nx.shortest_path(
      G, source=start_node, target=end_node, weight="weight"
  )
  optimal_dist = nx.shortest_path_length(
      G, source=start_node, target=end_node, weight="weight"
  )

  # สร้าง Layout สำหรับพล็อตด้วย Plotly
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
  st.write("
