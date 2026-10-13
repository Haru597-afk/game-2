import networkx as nx
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Shortest Path Click Game", layout="centered")

st.title("🗺️ เกมคลิกเลือกเส้นทางที่สั้นที่สุด (Shortest Path Click Game)")
st.write(
    "กติกา: ระบบจะสุ่มกราฟ จุดเริ่มต้น และจุดปลายทางให้ ให้คุณใช้เมาส์คลิกที่โหนดบนแผนภาพเพื่อเดินทีละก้าว จากนั้นกดปุ่มยืนยันด้านล่างเพื่อตรวจคะแนน!"
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
  if st.button("🔄 สุ่มแผนที่ใหม่"):
    generate_new_game()
    st.rerun()

if st.session_state.game_started:
  G = st.session_state.G
  start_node = st.session_state.start_node
  end_node = st.session_state.end_node

  st.info(
      f"🎯 จุดเริ่มต้น (Start): โหนด {start_node} ➔ จุดปลายทาง (Finish): โหนด"
      f" {end_node}"
  )

  # คำนวณเส้นทางที่สั้นที่สุดด้วย Dijkstra
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

  # 3. วาดโหนดแบบแยก Trace (ปุ่มวงกลมคลิกได้ง่ายและแม่นยำ)
  node_x = []
  node_y = []
  node_text = []
  node_colors = []

  nodes_list = list(G.nodes())
  for node in nodes_list:
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

  # Trace สำหรับปุ่มวงกลมโหนด (รองรับการคลิก)
  node_trace = go.Scatter(
      x=node_x,
      y=node_y,
      mode="markers",
      hoverinfo="text",
      text=node_text,
      marker=dict(
          showscale=False,
          color=node_colors,
          size=40,
          line=dict(width=2, color="black"),
      ),
  )

  # Trace สำหรับตัวหนังสือชื่อโหนด (แยกต่างหากเพื่อไม่ให้บังการคลิก)
  text_trace = go.Scatter(
      x=node_x,
      y=node_y,
      mode="text",
      text=node_text,
      textposition="middle center",
      textfont=dict(color="black", size=12, family="sans-serif"),
      hoverinfo="none",
  )

  fig = go.Figure(
      data=[edge_trace, weight_trace, node_trace, text_trace],
      layout=go.Layout(
          showlegend=False,
          hovermode="closest",
          margin=dict(b=20, l=20, r=20, t=20),
          xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
          yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
      ),
  )

  # คำนวณระยะทางเริ่มต้น
  current_user_path = st.session_state.user_path
  total_user_dist = 0
  for i in range(len(current_user_path) - 1):
    u = current_user_path[i]
    v = current_user_path[i + 1]
    total_user_dist += G[u][v]["weight"]

  # แสดงกราฟและดักจับการคลิกเมาส์
  st.write("👇 **คลิกที่โหนดบนแผนภาพเพื่อเดินทีละก้าว:**")
  selected_point = plotly_events(
      fig, click_event=True, hover_event=False, override_height=450
  )

  # จัดการคลิกโหนดผ่าน pointIndex ของ node_trace (ซึ่งอยู่ใน index ที่ 2)
  if selected_point:
    if selected_point[0].get("curveNumber") == 2:
      clicked_idx = selected_point[0].get("pointIndex")
      if clicked_idx is not None and clicked_idx < len(nodes_list):
        clicked_node = nodes_list[clicked_idx]
        last_node = st.session_state.user_path[-1]

        if clicked_node == last_node and len(st.session_state.user_path) > 1:
          st.session_state.user_path.pop()
          st.rerun()
        elif G.has_edge(last_node, clicked_node):
          st.session_state.user_path.append(clicked_node)
          st.rerun()

  st.markdown("---")
  path_display = " ➔ ".join([str(n) for n in current_user_path])
  st.write(f"🚶‍♂️ **เส้นทางที่คุณเดินปัจจุบัน:** {path_display}")
  st.write(f"ระยะทางรวมที่คุณเดินตอนนี้: **{total_user_dist} หน่วย**")

  # ปุ่มยืนยันคำตอบในตอนท้าย
  if st.button("🏁 ยืนยันคำตอบ (Confirm Path)"):
    if len(current_user_path) <= 1:
      st.warning("⚠️ กรุณาคลิกเลือกเส้นทางเดินอย่างน้อย 1 ก้าว")
    elif current_user_path[-1] != end_node:
      st.warning(
          f"⚠️ ยังเดินไม่ถึงจุดปลายทาง! (ปัจจุบันอยู่ที่โหนด {current_user_path[-1]}"
          f" แต่เป้าหมายคือโหนด {end_node})"
      )
    else:
      if total_user_dist == optimal_dist:
        st.balloons()
        st.success("🎉 ยินดีด้วย! คุณหาเส้นทางที่สั้นที่สุดได้ถูกต้องและยอดเยี่ยมมาก!")
      else:
        optimal_str = " ➔ ".join([str(n) for n in optimal_path])
        st.info(
            f"🏁 ผลลัพธ์: ระยะทางรวมของคุณคือ {total_user_dist} หน่วย"
            f" (เส้นทางที่สั้นที่สุดจริง ๆ คือ {optimal_dist} หน่วย: {optimal_str})"
        )
