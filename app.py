import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st

# 1) Page setup
st.set_page_config(
    page_title="Shortest Path Finder (Graph Theory)",
    page_layout="wide",
)

st.title("🗺️ Shortest Path Finder using Graph Theory")
st.write(
    "แอปพลิเคชันจำลองการหาเส้นทางที่สั้นที่สุดในกราฟ (Shortest Path) "
    "โดยใช้อัลกอริทึม Dijkstra ผ่านไลบรารี NetworkX และแสดงผลแบบ Interactive ด้วย Streamlit"
)

# 2) INPUT (Sidebar)
with st.sidebar:
  st.header("⚙️ ตั้งค่ากราฟและจุดเริ่มต้น/ปลายทาง")

  graph_type = st.selectbox(
      "เลือกรูปแบบกราฟตัวอย่าง",
      [
          "Custom Graph (5 โหนด)",
          "Grid Graph (ตารางตารางเมือง)",
          "Random Graph (สุ่ม)",
      ],
  )

  if graph_type == "Custom Graph (5 โหนด)":
    st.info(
        "กราฟตัวอย่าง 5 โหนด (A, B, C, D, E) พร้อมน้ำหนักเส้นเชื่อม (Weight)"
    )
    start_node = st.selectbox(
        "จุดเริ่มต้น (Source)", ["A", "B", "C", "D", "E"], index=0
    )
    end_node = st.selectbox(
        "จุดปลายทาง (Target)", ["A", "B", "C", "D", "E"], index=4
    )

  elif graph_type == "Grid Graph (ตารางตารางเมือง)":
    rows = st.slider("จำนวนแถว (Rows)", 2, 6, 3)
    cols = st.slider("จำนวนคอลัมน์ (Cols)", 2, 6, 3)
    start_node = 0
    end_node = (rows * cols) - 1
    st.info(f"จุดเริ่มต้น: {start_node}, จุดปลายทาง: {end_node}")

  else:  # Random Graph
    num_nodes = st.slider("จำนวนโหนด (Nodes)", 4, 15, 8)
    seed_val = st.number_input(
        "Random Seed (เพื่อให้กราฟคงที่)", value=42, step=1
    )
    start_node = 0
    end_node = num_nodes - 1

  show_weights = st.checkbox("แสดงน้ำหนักของเส้นเชื่อม (Weights)", value=True)

# 3) CALCULATION (สร้างกราฟและคำนวณเส้นทางที่สั้นที่สุด)
@st.cache_data
def create_graph(g_type, **kwargs):
  G = nx.Graph()
  if g_type == "Custom Graph (5 Nodes)":
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
  elif g_type == "Grid Graph (ตารางตารางเมือง)":
    r = kwargs.get("rows", 3)
    c = kwargs.get("cols", 3)
    G = nx.grid_2d_graph(r, c)
    np.random.seed(42)
    for u, v in G.edges():
      G[u][v]["weight"] = np.random.randint(1, 10)
  else:
    n = kwargs.get("num_nodes", 8)
    s = kwargs.get("seed_val", 42)
    G = nx.erdos_renyi_graph(n, 0.4, seed=s)
    if not nx.is_connected(G):
      G = nx.connected_caveman_graph(2, n // 2)
    np.random.seed(s)
    for u, v in G.edges():
      G[u][v]["weight"] = np.random.randint(1, 15)
  return G

if graph_type == "Custom Graph (5 โหนด)":
  G = create_graph("Custom Graph (5 Nodes)")
elif graph_type == "Grid Graph (ตารางตารางเมือง)":
  G = create_graph("Grid Graph (ตารางตารางเมือง)", rows=rows, cols=cols)
else:
  G = create_graph("Random Graph", num_nodes=num_nodes, seed_val=seed_val)

nodes_list = list(G.nodes())
if start_node not in nodes_list or end_node not in nodes_list:
  st.warning("จุดเริ่มต้นหรือจุดปลายทางไม่ถูกต้อง กรุณาเลือกใหม่")
  st.stop()

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

# 4) OUTPUT (แสดงผลลัพธ์)
col1, col2 = st.columns(2)
with col1:
  if path_found:
    st.metric(
        label="ระยะทางรวมที่สั้นที่สุด (Total Distance)",
        value=f"{shortest_distance}",
    )
  else:
    st.error("ไม่พบเส้นทางเชื่อมต่อระหว่างจุดเริ่มต้นและปลายทาง")

with col2:
  if path_found:
    path_str = " ➔ ".join([str(n) for n in shortest_path])
    st.metric(label="ลำดับเส้นทาง (Shortest Path)", value=path_str)

st.markdown("---")

st.subheader("📊 แผนภาพแสดงโครงสร้างกราฟและเส้นทางที่สั้นที่สุด")
fig, ax = plt.subplots(figsize=(8, 6))

if graph_type == "Grid Graph (ตารางตารางเมือง)":
  pos = {node: (node[1], -node[0]) for node in G.nodes()}
else:
  pos = nx.spring_layout(G, seed=42)

path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
all_edges = G.edges()

nx.draw_networkx_nodes(
    G, pos, node_color="#aec7e8", node_size=700, ax=ax
)
if path_found:
  nx.draw_networkx_nodes(
      G, pos, nodelist=shortest_path, node_color="#ff7f0e", node_size=800, ax=ax
  )

nx.draw_networkx_edges(
    G, pos, edgelist=all_edges, width=2, edge_color="gray", ax=ax
)
if path_found:
  nx.draw_networkx_edges(
      G, pos, edgelist=path_edges, width=4, edge_color="r", ax=ax
  )

nx.draw_networkx_labels(
    G, pos, font_size=12, font_family="sans-serif", ax=ax
)

if show_weights:
  edge_weights = nx.get_edge_attributes(G, "weight")
  nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_weights, ax=ax)

ax.axis("off")
st.pyplot(fig)
plt.close(fig)

with st.expander("📁 ดูข้อมูลรายละเอียดเส้นเชื่อมทั้งหมดในกราฟ (Edges Table)"):
  edge_data = []
  for u, v, d in G.edges(data=True):
    edge_data.append({"From": u, "To": v, "Weight": d.get("weight", 1)})
  df_edges = pd.DataFrame(edge_data)
  st.dataframe(df_edges, hide_index=True)

  csv_bytes = df_edges.to_csv(index=False).encode("utf-8")
  st.download_button(
      "📥 ดาวน์โหลดข้อมูลกราฟ (CSV)",
      csv_bytes,
      file_name="graph_edges.csv",
      mime="text/csv",
  )
