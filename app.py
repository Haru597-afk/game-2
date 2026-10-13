import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import streamlit as st

st.set_page_config(page_title="Shortest Path Game", layout="centered")

st.title("🗺️ เกมเลือกเส้นทางที่สั้นที่สุด (Shortest Path Game)")
st.write(
    "กติกา: ระบบจะสุ่มกราฟ จุดเริ่มต้น และจุดปลายทางให้ "
    "ให้คุณเลือกเส้นทางเดินจากรายการด้านล่างรวดเดียวให้ครบถ้วน แล้วกดปุ่มยืนยันเพื่อตรวจคะแนน!"
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
      f"🎯 จุดเริ่มต้น (Start): โหนด **{start_node}**  ➔  จุดปลายทาง (Finish): โหนด"
      f" **{end_node}**"
  )

  # คำนวณเส้นทางที่สั้นที่สุดด้วย Dijkstra (เก็บไว้ตรวจตอนกดคอนเฟิร์ม)
  optimal_path = nx.shortest_path(
      G, source=start_node, target=end_node, weight="weight"
  )
  optimal_dist = nx.shortest_path_length(
      G, source=start_node, target=end_node, weight="weight"
  )

  # ให้ผู้เล่นเลือกเส้นทางแบบรวดเดียวจบด้วย multiselect (ไม่มีการรีเฟรชหน้าจอระหว่างเลือก)
  all_nodes = list(G.nodes())
  user_selected_path = st.multiselect(
      "👇 เลือกโหนดลำดับเส้นทางที่คุณต้องการเดิน (เริ่มต้นจาก Start ไปจนถึง Finish):",
      all_nodes,
      default=[start_node],
  )

  # คำนวณระยะทางและตรวจสอบเส้นทางแบบเรียลไทม์ (ไม่แสดงคำเตือนน่ารำคาญ)
  total_user_dist = 0
  is_valid_structure = True

  if len(user_selected_path) > 1:
    for i in range(len(user_selected_path) - 1):
      u = user_selected_path[i]
      v = user_selected_path[i + 1]
      if G.has_edge(u, v):
        total_user_dist += G[u][v]["weight"]
      else:
        is_valid_structure = False

  # แสดงผลรูปกราฟด้วย Matplotlib (พร้อมตัวเลขบอกระยะทางชัดเจน)
  fig, ax = plt.subplots(figsize=(8, 5))
  pos = nx.spring_layout(G, seed=42)

  # วาดเส้นเชื่อมทั้งหมด
  nx.draw_networkx_edges(
      G, pos, edgelist=G.edges(), width=2, edge_color="gray", ax=ax
  )

  # ไฮไลต์เส้นทางที่ผู้เล่นเลือกด้วยสีฟ้า
  if len(user_selected_path) > 1:
    user_edges = list(zip(user_selected_path[:-1], user_selected_path[1:]))
    nx.draw_networkx_edges(
        G, pos, edgelist=user_edges, width=4, edge_color="blue", ax=ax
    )

  # วาดโหนด (Start สีเขียว, Finish สีส้ม)
  nx.draw_networkx_nodes(
      G, pos, node_color="lightblue", node_size=700, ax=ax
  )
  nx.draw_networkx_nodes(
      G, pos, nodelist=[start_node], node_color="lightgreen", node_size=800, ax=ax
  )
  nx.draw_networkx_nodes(
      G, pos, nodelist=[end_node], node_color="orange", node_size=800, ax=ax
  )
  nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", ax=ax)

  # แสดงน้ำหนัก (Weight) บนเส้นเชื่อม
  edge_weights = nx.get_edge_attributes(G, "weight")
  nx.draw_networkx_edge_labels(
      G, pos, edge_labels=edge_weights, font_color="red", font_size=12, ax=ax
  )

  ax.axis("off")
  st.pyplot(fig)
  plt.close(fig)

  st.markdown("---")
  path_display = " ➔ ".join(str(n) for n in user_selected_path)
  st.write(f"🚶‍♂️ **เส้นทางที่คุณเลือก:** {path_display}")
  st.write(f"ระยะทางรวมที่คุณเดิน: **{total_user_dist} หน่วย**")

  # ปุ่มยืนยันคำตอบในตอนท้าย
  if st.button("🏁 ยืนยันคำตอบเพื่อตรวจคะแนน (Confirm)"):
    if len(user_selected_path) <= 1:
      st.warning("⚠️ กรุณาเลือกเส้นทางเดินอย่างน้อย 1 ก้าว")
    elif user_selected_path[0] != start_node or user_selected_path[-1] != end_node:
      st.error(
          f"❌ เส้นทางไม่ถูกต้อง: ต้องเริ่มต้นที่โหนด {start_node} และสิ้นสุดที่โหนด"
          f" {end_node}"
      )
    elif not is_valid_structure:
      st.error("❌ เส้นทางไม่ถูกต้อง: มีบางช่วงที่ไม่มีเส้นเชื่อมถึงกันโดยตรง!")
    else:
      if total_user_dist == optimal_dist:
        st.balloons()
        st.success(
            "🎉 ยินดีด้วย! คุณเลือกเส้นทางที่สั้นที่สุดได้อย่างยอดเยี่ยมที่สุด!"
        )
      else:
        optimal_str = " ➔ ".join(str(n) for n in optimal_path)
        st.info(
            f"🏁 ระยะทางรวมของคุณคือ {total_user_dist} หน่วย (เส้นทางที่สั้นที่สุดที่แท้จริงคือ"
            f" {optimal_dist} หน่วย ได้แก่: {optimal_str})"
        )
