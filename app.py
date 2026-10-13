import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import streamlit as st

st.set_page_config(page_title="Shortest Path Game", layout="centered")

st.title("🗺️ เกมทายเส้นทางที่สั้นที่สุด (Shortest Path Game)")
st.write(
    "กติกา: ระบบจะสุ่มกราฟและจุดเริ่มต้น-จุดปลายทางให้ "
    "ให้คุณเลือกเส้นทางเดินเองทีละโหนด แล้วมาดูกันว่าระยะทางรวมที่คุณเดินเป็นเท่าไหร่"
    " และเทียบกับเส้นทางที่สั้นที่สุดของ Dijkstra!"
)

# ใช้ st.session_state เพื่อเก็บบันทึกสถานะเกมและป้องกันกราฟสุ่มใหม่เองเวลากดเลือก[cite: 5]
if "game_started" not in st.session_state:
  st.session_state.game_started = False


def generate_new_game():
  n = 6
  seed = np.random.randint(1, 1000)
  G = nx.erdos_renyi_graph(n, 0.5, seed=seed)
  while not nx.is_connected(G):
    seed = np.random.randint(1, 1000)
    G = nx.erdos_renyi_graph(n, 0.5, seed=seed)

  np.random.seed(seed)
  for u, v in G.edges():
    G[u][v]["weight"] = int(np.random.randint(1, 20))

  nodes = list(G.nodes())
  st.session_state.G = G
  st.session_state.start_node = nodes[0]
  st.session_state.end_node = nodes[-1]
  st.session_state.game_started = True


# ปุ่มเริ่มเกมหรือสุ่มแผนที่ใหม่
if not st.session_state.game_started:
  if st.button("🎮 เริ่มเกมใหม่ / สุ่มแผนที่"):
    generate_new_game()
    st.rerun()
else:
  G = st.session_state.G
  start_node = st.session_state.start_node
  end_node = st.session_state.end_node

  if st.button("🔄 สุ่มแผนที่ใหม่"):
    generate_new_game()
    st.rerun()

  st.info(
      f"จุดเริ่มต้น (Start): **โหนด {start_node}**  |  จุดปลายทาง (Finish): **โหนด"
      f" {end_node}**"
  )

  # คำนวณคำตอบที่สั้นที่สุดด้วย Dijkstra รอไว้เทียบ
  optimal_path = nx.shortest_path(
      G, source=start_node, target=end_node, weight="weight"
  )
  optimal_dist = nx.shortest_path_length(
      G, source=start_node, target=end_node, weight="weight"
  )

  # ให้ผู้เล่นเลือกเส้นทางโดยระบุลำดับโหนดที่ต้องการเดินผ่าน
  all_nodes = list(G.nodes())
  user_selected_path = st.multiselect(
      "เลือกโหนดตามลำดับเส้นทางที่คุณจะเดิน (ตั้งแต่ Start ไปจนถึง Finish):",
      all_nodes,
      default=[start_node],
  )

  valid_path = True
  total_user_dist = 0

  if len(user_selected_path) > 1:
    if (
        user_selected_path[0] != start_node
        or user_selected_path[-1] != end_node
    ):
      st.warning(
          f"⚠️ เส้นทางต้องเริ่มต้นที่โหนด {start_node} และสิ้นสุดที่โหนด"
          f" {end_node}"
      )
      valid_path = False
    else:
      for i in range(len(user_selected_path) - 1):
        u = user_selected_path[i]
        v = user_selected_path[i + 1]
        if G.has_edge(u, v):
          total_user_dist += G[u][v]["weight"]
        else:
          st.error(f"❌ ไม่มีเส้นทางเชื่อมระหว่างโหนด {u} และ {v} (เดินผิดกฎ!)")
          valid_path = False
          break

  # แสดงผลกราฟ
  fig, ax = plt.subplots(figsize=(8, 5))
  pos = nx.spring_layout(G, seed=42)

  # วาดเส้นเชื่อมทั้งหมด
  nx.draw_networkx_edges(
      G, pos, edgelist=G.edges(), width=2, edge_color="gray", ax=ax
  )

  # ไฮไลต์เส้นทางที่ผู้เล่นเลือกด้วยสีฟ้า
  if valid_path and len(user_selected_path) > 1:
    user_edges = list(zip(user_selected_path[:-1], user_selected_path[1:]))
    nx.draw_networkx_edges(
        G, pos, edgelist=user_edges, width=4, edge_color="blue", ax=ax
    )

  # วาดโหนด (Start สีเขียว, Finish สีส้ม, ปกติสีฟ้า)
  nx.draw_networkx_nodes(
      G, pos, node_color="lightblue", node_size=700, ax=ax
  )
  nx.draw_networkx_nodes(
      G, pos, nodelist=[start_node], node_color="lightgreen", node_size=800, ax=ax
  )
  nx.draw_networkx_nodes(
      G, pos, nodelist=[end_node], node_color="orange", node_size=800, ax=ax
  )
  nx.draw_networkx_labels(G, pos, font_size=12, ax=ax)

  edge_weights = nx.get_edge_attributes(G, "weight")
  nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_weights, ax=ax)

  ax.axis("off")
  st.pyplot(fig)
  plt.close(fig)

  # แสดงผลคะแนนและผลลัพธ์
  if valid_path and len(user_selected_path) > 1:
    st.success(
        f"🚶‍♂️ ระยะทางที่คุณ
