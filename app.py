import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st

# 1) Page setup
st.set_page_config(page_title="Shortest Path Challenge Game", page_layout="wide")

st.title("🎮 Shortest Path Challenge Game (ทฤษฎีกราฟ)")
st.write(
    "ยินดีต้อนรับสู่เกมหาเส้นทางที่สั้นที่สุด! "
    "เลือกจุดเริ่มต้นและจุดปลายทางในเมือง แล้วดูว่าอัลกอริทึม Dijkstra "
    "จะคำนวณหาเส้นทางที่สั้นที่สุดให้คุณอย่างไร"
)

# 2) INPUT (Sidebar Setup)
with st.sidebar:
  st.header("⚙️ ตั้งค่าเกมและกราฟ")

  graph_type = st.selectbox(
      "เลือกแผนที่/ประเภทกราฟ",
      [
          "🗺️ แผนที่เมืองจำลอง (Custom 5 Nodes)",
          "🏙️ แผนที่ตารางเมือง (Grid Graph)",
          "🎲 แผนที่สุ่ม (Random Network)",
      ],
  )

  if graph_type == "🗺️ แผนที่เมืองจำลอง (Custom 5 Nodes)":
    st.info("เมืองจำลอง 5 โหนด (A, B, C, D, E) พร้อมระยะทางระหว่างเมือง")
    start_node = st.selectbox(
        "จุดเริ่มต้น (Start)", ["A", "B", "C", "D", "E"], index=0
    )
    end_node = st.selectbox(
        "จุดปลายทาง (Target)", ["A", "B", "C", "D", "E"], index=4
    )

  elif graph_type == "🏙️ แผนที่ตารางเมือง (Grid Graph)":
    rows = st.slider("จำนวนแถว (Rows)", 2, 5, 3)
    cols = st.slider("จำนวนคอลัมน์ (Cols)", 2, 5, 3)
    start_node = (0, 0)
    end_node = (rows - 1, cols - 1)
    st.info(f"จุดเริ่มต้น: {start_node} ➔ จุดปลายทาง: {end_node}")

  else:  # Random Network
    num_nodes = st.slider("จำนวนโหนด/เมือง (Nodes)", 5, 12, 7)
    seed_val = st.number_input(
        "Seed สุ่มแผนที่ (เปลี่ยนเพื่อเปลี่ยนผังเมือง)", value=42, step=1
    )
    start_node = 0
    end_node = num_nodes - 1
    st.info(f"จุดเริ่มต้น: {start_node} ➔ จุดปลายทาง: {end_node}")

  show_weights = st.checkbox(
      "แสดงระยะทาง/น้ำหนักของเส้นเชื่อม (Weights)", value=True
  )


# 3) CALCULATION (สร้างกราฟและคำนวณ Dijkstra Shortest Path)
@st.cache_data
def build_game_graph(g_type, **kwargs):
  G = nx.Graph()
  if g_type == "Custom":
    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
    ]
    for u, v, w in edges:
      G.add_edge(u, v, weight=w)
  elif g_type == "Grid":
    r = kwargs.get("rows", 3)
    c = kwargs.get("cols", 3)
    G = nx.grid_2d_graph(r, c)
    np.random.seed(10)
    for u, v in G.edges():
      G[u][v]["weight"] = int(np.random.randint(1, 10))
  else:
    n = kwargs.get("num_nodes", 7)
    s = kwargs.get("seed_val", 42)
    G = nx.erdos_renyi_graph(n, 0.45, seed=s)
    if not nx.is_connected(G):
      components = list(nx.connected_components(G))
      for i in range(len(components) - 1):
        u = list(components[i])[0]
        v = list(components[i + 1])[0]
        G.add_edge(u, v)
    np.random.seed(s)
    for u, v in G.edges():
      G[u][v]["weight"] = int(np.random.randint(1, 15))
  return G


# โหลดข้อมูลกราฟ
if graph_type == "🗺️ แผนที่เมืองจำลอง (Custom 5 Nodes)":
  G = build_game_graph("Custom")
elif graph_type == "🏙️ แผนที่ตารางเมือง (Grid Graph)":
  G = build_game_graph("Grid", rows=rows, cols=cols)
else:
  G = build_game_graph("Random", num_nodes=num_nodes, seed_val=seed_val)

# คำนวณ Dijkstra
try:
  shortest_path = nx.shortest_path(
      G, source=start_node, target=end_node, weight="weight"
  )
  shortest_distance = nx.shortest_path_length(
      G, source=start_node, target=end_node, weight="weight"
  )
  path_found = True
except nx.NetworkXNoPath:
  path_found = False
  shortest_path = []
  shortest_distance = float("inf")

# 4) OUTPUT (ส่วนแสดงผลและกระดานเกม)
if start_node == end_node:
  st.warning("⚠️ จุดเริ่มต้นและจุดปลายทางเป็นจุดเดียวกัน กรุณาเลือกจุดใหม่")
else:
  col_m1, col_m2 = st.columns(2)
  with col_m1:
    if path_found:
      st.metric(
          label="🏆 ระยะทางรวมที่สั้นที่สุด (Shortest Distance)",
          value=f"{shortest_distance} หน่วย",
      )
    else:
      st.error("❌ ไม่พบเส้นทางที่สามารถเชื่อมถึงกันได้")

  with col_m2:
    if path_found:
      path_str = " ➔ ".join([str(n) for n in shortest_path])
      st.metric(label="🚩 เส้นทางที่เลือก (Dijkstra Path)", value=path_str)

st.markdown("---")

# วาดกราฟและเส้นทางไฮไลต์
st.subheader("🗺️ แผนที่กราฟแสดงเส้นทางที่ดีที่สุด")
fig, ax = plt.subplots(figsize=(9, 6))

if graph_type == "🏙️ แผนที่ตารางเมือง (Grid Graph)":
  pos = {node: (node[1], -node[0]) for node in G.nodes()}
else:
  pos = nx.spring_layout(G, seed=42)

all_edges = G.edges()
path_edges = (
    list(zip(shortest_path[:-1], shortest_path[1:])) if path_found else []
)

# วาดโหนดทั้งหมด
nx.draw_networkx_nodes(
    G, pos, node_color="#a1c4fd", node_size=700, ax=ax
)

# ไฮไลต์จุดเริ่มต้นและจุดจบ
if path_found:
  nx.draw_networkx_nodes(
      G, pos, nodelist=[start_node], node_color="#2ecc71", node_size=900, ax=ax
  )
  nx.draw_networkx_nodes(
      G, pos, nodelist=[end_node], node_color="#e74c3c", node_size=900, ax=ax
  )
  mid_nodes = [n for n in shortest_path if n not in (start_node, end_node)]
  if mid_nodes:
    nx.draw_networkx_nodes(
        G, pos, nodelist=mid_nodes, node_color="#f39c12", node_size=800, ax=ax
    )

# วาดเส้นเชื่อม
nx.draw_networkx_edges(
    G, pos, edgelist=all_edges, width=2, edge_color="#bdc3c7", ax=ax
)
if path_found:
  nx.draw_networkx_edges(
      G, pos, edgelist=path_edges, width=4, edge_color="#e74c3c", ax=ax
  )

# แสดงป้ายชื่อโหนด
nx.draw_networkx_labels(
    G, pos, font_size=11, font_weight="bold", ax=ax
)

# แสดงระยะทาง/น้ำหนักเส้นเชื่อม
if show_weights:
  edge_weights = nx.get_edge_attributes(G, "weight")
  nx.draw_networkx_edge_labels(
      G, pos, edge_labels=edge_weights, font_color="#2c3e50", ax=ax
  )

ax.axis("off")
st.pyplot(fig)
plt.close(fig)

# 5) ตารางข้อมูลเส้นเชื่อมทั้งหมด (Data Table)
with st.expander("📊 ดูข้อมูลระยะทางทั้งหมดระหว่างโหนด (Edge List)"):
  edge_list = []
  for u, v, d in G.edges(data=True):
    edge_list.append({"From": u, "To": v, "Distance (Weight)": d.get("weight", 1)})
  df_edges = pd.DataFrame(edge_list)
  st.dataframe(df_edges, use_container_width=True)

  csv_bytes = df_edges.to_csv(index=False).encode("utf-8")
  st.download_button(
      "📥 ดาวน์โหลดข้อมูลกราฟ (CSV)",
      csv_bytes,
      file_name="shortest_path_graph.csv",
      mime="text/csv",
  )
