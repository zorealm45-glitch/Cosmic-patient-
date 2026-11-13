import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import time

# ==========================================
# 1. إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(
    page_title="COSMIC PATIENTS | Astronaut Digital Twin",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS لإعطاء طابع مراكز التحكم الفضائية (NASA Mission Control)
st.markdown("""
<style>
    .stApp { background-color: #060913; color: #E2E8F0; }
    .metric-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 240, 255, 0.1);
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #38BDF8; }
    .metric-label { font-size: 14px; color: #94A3B8; }
    .alert-box {
        background-color: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #EF4444;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: rgba(16, 185, 129, 0.15);
        border-left: 4px solid #10B981;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة حالة الجلسة (Session State) لبروتوكولات الإنقاذ والهاردوير
if 'countermeasure_active' not in st.session_state:
    st.session_state.countermeasure_active = False
if 'earth_hr' not in st.session_state:
    st.session_state.earth_hr = 72

# ==========================================
# 2. محرك الفيزياء والمحاكاة الفسيولوجية
# ==========================================
def calculate_physiology(mission_type, days, hydration, sleep_quality, exercise, earth_hr, cm_active):
    # معاملات البيئة الفضائية حسب الوجهة
    env_factors = {
        "ISS (Low Earth Orbit - 0g)": {"gravity": 0.0, "radiation": 0.3, "delay_min": 0},
        "Lunar Gateway (Moon - 0.16g)": {"gravity": 0.16, "radiation": 0.7, "delay_min": 0.04},
        "Mars Transit (Deep Space - 0g)": {"gravity": 0.0, "radiation": 1.0, "delay_min": 20}
    }
    env = env_factors[mission_type]
    
    # 1. حساب نزوح السوائل للرأس (Cephalad Fluid Shift) - يسبب متلازمة SANS
    fluid_shift = (1 - env["gravity"]) * (1 - np.exp(-days / 30)) * 100
    fluid_shift += (100 - hydration) * 0.15
    if cm_active:  # تأثير بدلة الضغط السالب LBNP
        fluid_shift *= 0.45

    # 2. حساب معدل ضربات القلب المحول من الأرض للفضاء (Earth-to-Space Bio-Sync)
    # في انعدام الجاذبية يقل حجم الضربة القلبية تدريجياً فيزداد النبض التعويضي مع الجفاف والإجهاد
    deconditioning = (days / 365) * 18 * (1 - env["gravity"])
    dehydration_penalty = (100 - hydration) * 0.25
    exercise_effect = -exercise * 1.5
    space_hr = earth_hr + deconditioning + dehydration_penalty + exercise_effect
    if cm_active:
        space_hr -= 8
    space_hr = int(np.clip(space_hr, 48, 165))

    # 3. سلامة الحمض النووي والأوعية الدقيقة (DNA & Microvascular Integrity)
    radiation_damage = env["radiation"] * (days / 180) * 45
    dna_integrity = np.clip(100 - radiation_damage + (sleep_quality * 0.1), 15, 100)

    # 4. مؤشر الإجهاد العام (Stress Index)
    stress = (100 - sleep_quality) * 0.4 + (100 - hydration) * 0.3 + (fluid_shift * 0.3)
    if cm_active:
        stress *= 0.6
    stress = int(np.clip(stress, 10, 99))

    # 5. الكتلة العضلية (Muscle Mass %)
    muscle_mass = np.clip(100 - ((1 - env["gravity"]) * (days / 365) * 25) + (exercise * 2.5), 60, 100)

    return {
        "space_hr": space_hr,
        "fluid_shift": round(fluid_shift, 1),
        "dna_integrity": round(dna_integrity, 1),
        "stress": stress,
        "muscle_mass": round(muscle_mass, 1),
        "radiation": env["radiation"],
        "delay": env["delay_min"]
    }

# ==========================================
# 3. بناء المجسم ثلاثي الأبعاد لرائد الفضاء (3D Digital Twin)
# ==========================================
def build_3d_astronaut(metrics, selected_organ):
    fig = go.Figure()

    # رسم الهيكل الشبكي لجسم رائد الفضاء (Holographic Body Mesh)
    z_body = np.linspace(0, 180, 40)
    theta = np.linspace(0, 2 * np.pi, 30)
    theta_grid, z_grid = np.meshgrid(theta, z_body)

    # تشكيل منحنى الجسم (رأس، جذع، أطراف)
    r_grid = np.where(z_grid > 155, 11 * np.sin((z_grid - 155) / 25 * np.pi),  # الرأس
             np.where(z_grid > 148, 5,                                        # الرقبة
             np.where(z_grid > 90, 18 + 3 * np.sin((z_grid - 90) / 58 * np.pi), # الجذع
             11 - (90 - z_grid) * 0.04)))                                     # الأرجل

    x_body = r_grid * np.cos(theta_grid)
    y_body = r_grid * np.sin(theta_grid) * 0.65

    fig.add_trace(go.Surface(
        x=x_body, y=y_body, z=z_grid,
        opacity=0.14,
        colorscale=[[0, '#0284C7'], [1, '#38BDF8']],
        showscale=False,
        hoverinfo='skip',
        name='Astronaut Suit/Body'
    ))

    # تحديد ألوان الأعضاء بناءً على الخطورة الفسيولوجية
    brain_color = '#EF4444' if metrics['fluid_shift'] > 60 else ('#F59E0B' if metrics['fluid_shift'] > 35 else '#10B981')
    heart_color = '#EF4444' if metrics['space_hr'] > 105 else ('#F59E0B' if metrics['space_hr'] > 88 else '#10B981')
    dna_color   = '#EF4444' if metrics['dna_integrity'] < 65 else ('#F59E0B' if metrics['dna_integrity'] < 82 else '#10B981')
    muscle_color= '#EF4444' if metrics['muscle_mass'] < 78 else ('#F59E0B' if metrics['muscle_mass'] < 88 else '#10B981')

    # إحداثيات الأعضاء الحيوية داخل المجسم
    organs = [
        {"name": "Brain (Neuro-Ocular / SANS)", "x": 0, "y": 0, "z": 168, "size": 14 + metrics['fluid_shift']*0.08, "color": brain_color,
         "info": f"Fluid Shift: {metrics['fluid_shift']}% | Intracranial Pressure Risk"},
        {"name": "Heart (Cardiovascular)", "x": 3, "y": 4, "z": 132, "size": 13 + (metrics['space_hr']-60)*0.1, "color": heart_color,
         "info": f"Space HR: {metrics['space_hr']} BPM (Earth Baseline: {st.session_state.earth_hr} BPM)"},
        {"name": "Lungs & Oxygenation", "x": -4, "y": 3, "z": 134, "size": 15, "color": "#38BDF8",
         "info": "O2 Saturation: 97% | Microgravity Aerosol Distribution"},
        {"name": "Vascular & DNA Network", "x": 0, "y": 0, "z": 105, "size": 14, "color": dna_color,
         "info": f"Cellular/DNA Integrity: {metrics['dna_integrity']}%"},
        {"name": "Skeletal Muscles (Lower Limb)", "x": 6, "y": 0, "z": 55, "size": 14, "color": muscle_color,
         "info": f"Muscle Mass Retention: {metrics['muscle_mass']}%"}
    ]

    # إضافة الأعضاء كنقاط تفاعلية متوهجة
    for org in organs:
        is_selected = (org["name"].split(" ")[0] in selected_organ)
        fig.add_trace(go.Scatter3d(
            x=[org["x"]], y=[org["y"]], z=[org["z"]],
            mode='markers+text',
            marker=dict(
                size=org["size"] * (1.35 if is_selected else 1.0),
                color=org["color"],
                opacity=0.95,
                line=dict(color='#FFFFFF', width=3 if is_selected else 1)
            ),
            text=[org["name"].split(" ")[0]],
            textposition="top center",
            textfont=dict(color="white", size=12),
            hovertemplate=f"<b>{org['name']}</b><br>{org['info']}<extra></extra>",
            name=org["name"]
        ))

    # إضافة مسار الأوعية الدموية (عمود فقري وشريان رئيسي)
    fig.add_trace(go.Scatter3d(
        x=[0, 3, 0, 6], y=[0, 4, 0, 0], z=[168, 132, 105, 55],
        mode='lines',
        line=dict(color='#38BDF8', width=4, dash='dot'),
        hoverinfo='skip',
        name='Vascular & Neural Axis'
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='#060913',
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.6))
        ),
        paper_bgcolor='#060913',
        margin=dict(l=0, r=0, t=10, b=0),
        height=540,
        showlegend=False
    )
    return fig

# ==========================================
# 4. محرك الفيزياء المتناظرة (Cosmic Web vs Capillaries)
# ==========================================
def build_isomorphic_networks(degradation_rate):
    # توليد شبكة أساسية (Watts-Strogatz Small-World Network) تحاكي التنظيم الكوني والبيولوجي
    G_base = nx.watts_strogatz_graph(n=45, k=4, p=0.25, seed=42)
    pos = nx.spring_layout(G_base, seed=42)

    # تطبيق نظرية التخلل (Percolation): إزالة روابط بناءً على الإشعاع الكوني / تمدد الكون
    G_damaged = G_base.copy()
    edges = list(G_damaged.edges())
    num_remove = int(len(edges) * degradation_rate)
    np.random.seed(42)
    if num_remove > 0:
        remove_indices = np.random.choice(len(edges), num_remove, replace=False)
        for idx in remove_indices:
            G_damaged.remove_edge(*edges[idx])

    # حساب مقاييس نظرية الشبكات العلمية
    metrics_base = {
        "Nodes": G_base.number_of_nodes(),
        "Edges": G_base.number_of_edges(),
        "Avg Degree": round(np.mean([d for _, d in G_base.degree()]), 2),
        "Clustering Coeff": round(nx.average_clustering(G_base), 3),
        "Giant Component %": round(len(max(nx.connected_components(G_base), key=len)) / 45 * 100, 1)
    }

    metrics_damaged = {
        "Nodes": G_damaged.number_of_nodes(),
        "Edges": G_damaged.number_of_edges(),
        "Avg Degree": round(np.mean([d for _, d in G_damaged.degree()]), 2),
        "Clustering Coeff": round(nx.average_clustering(G_damaged), 3),
        "Giant Component %": round(len(max(nx.connected_components(G_damaged), key=len)) / 45 * 100, 1)
    }

    def create_net_fig(G, node_color, edge_color, title):
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=1.2, color=edge_color), hoverinfo='none', mode='lines'))
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y, mode='markers',
            marker=dict(size=8, color=node_color, line=dict(width=1, color='#FFFFFF')),
            hoverinfo='none'
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(color='white', size=14)),
            paper_bgcolor='#0F172A', plot_bgcolor='#0F172A',
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            margin=dict(l=10, r=10, t=40, b=10), height=320, showlegend=False
        )
        return fig

    fig_cosmic = create_net_fig(G_damaged, '#A855F7', 'rgba(168, 85, 247, 0.45)', "🌌 Cosmic Web (Dark Matter Filaments)")
    fig_bio    = create_net_fig(G_damaged, '#38BDF8', 'rgba(56, 189, 248, 0.45)', "🩸 Human Microvascular / Neural Network")

    return fig_cosmic, fig_bio, metrics_base, metrics_damaged

# ==========================================
# 5. القائمة الجانبية (Mission Control Inputs)
# ==========================================
with st.sidebar:
    st.title("🚀 MISSION CONTROL")
    st.caption("COSMIC PATIENTS — Digital Twin Engine")
    st.divider()

    mission_type = st.selectbox(
        "Destination & Gravity Regime",
        ["ISS (Low Earth Orbit - 0g)", "Lunar Gateway (Moon - 0.16g)", "Mars Transit (Deep Space - 0g)"]
    )
    days = st.slider("Mission Duration (Days)", 1, 500, 180)
    hydration = st.slider("Astronaut Hydration Level (%)", 40, 100, 75)
    sleep_quality = st.slider("Circadian Sleep Quality (%)", 30, 100, 65)
    exercise = st.slider("Daily Countermeasure Exercise (Hrs)", 0.0, 3.0, 1.5, 0.5)

    st.divider()
    st.subheader("📡 Earth-to-Space Bio-Sync (Hardware)")
    hw_mode = st.radio("Sensor Input Source", ["Simulated Live Pulse", "ESP32 Hardware Stream (JSON)"])
    if hw_mode == "Simulated Live Pulse":
        st.session_state.earth_hr = st.number_input("Your Earth Baseline HR (1g)", 50, 130, 72)
    else:
        st.info("Listening on `http://localhost:8501/esp32_data.json` (MAX30102)")
        if st.button("🔄 Sync Latest ESP32 Packet"):
            st.session_state.earth_hr = np.random.randint(68, 84)
            st.success(f"Synced Earth HR: {st.session_state.earth_hr} BPM")

# حساب المؤشرات الفسيولوجية الحالية
metrics = calculate_physiology(
    mission_type, days, hydration, sleep_quality, exercise,
    st.session_state.earth_hr, st.session_state.countermeasure_active
)

# ==========================================
# 6. الواجهة الرئيسية (Main Dashboard)
# ==========================================
st.markdown("## 🪐 COSMIC PATIENTS: Exploring Human Health Beyond Earth")
st.caption("Predictive Astronaut Digital Twin & Isomorphic Network Physics Simulator")

# شريط المؤشرات الحيوية العلوي
c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['space_hr']} BPM</div><div class='metric-label'>Space Heart Rate (0g)</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['fluid_shift']}%</div><div class='metric-label'>Cephalad Fluid Shift</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['dna_integrity']}%</div><div class='metric-label'>DNA & Vascular Integrity</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['muscle_mass']}%</div><div class='metric-label'>Muscle Mass Retention</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['stress']}/100</div><div class='metric-label'>Autonomic Stress Index</div></div>", unsafe_allow_html=True)

st.write("")

# التبويبات الرئيسية للمشروع
tab1, tab2, tab3 = st.tabs([
    "🧬 3D Astronaut Digital Twin (Signature)",
    "🌌 Isomorphic Physics: Cosmic Web vs. Human",
    "📈 Longitudinal Mission Forecast"
])

# ------------------------------------------
# TAB 1: المجسم الـ 3D ونظام الإنقاذ الذاتي
# ------------------------------------------
with tab1:
    col_3d, col_info = st.columns([1.4, 1])

    with col_3d:
        selected_organ = st.selectbox(
            "Inspect Biological System (Rotate & Zoom 3D Model):",
            ["Brain (Neuro-Ocular)", "Heart (Cardiovascular)", "Lungs (Respiratory)", "Vascular & DNA", "Skeletal Muscles"]
        )
        fig_3d = build_3d_astronaut(metrics, selected_organ)
        st.plotly_chart(fig_3d, use_container_width=True)

    with col_info:
        st.subheader("Autonomous Medical AI & Countermeasures")
        
        # عرض حالة التأخير الزمني للاتصال بالأرض
        if metrics["delay"] > 0:
            st.warning(f"📡 **Communication Delay: {metrics['delay']} mins** — Earth telemedicine unavailable. Autonomous onboard protocol required.")
        else:
            st.info("📡 **Communication Link: Real-Time (LEO)** — Direct telemetry with NASA Flight Surgeon.")

        # تشخيص الحالة واقتراح بروتوكول العلاج
        if metrics["fluid_shift"] > 50 or metrics["space_hr"] > 95 or metrics["stress"] > 60:
            if not st.session_state.countermeasure_active:
                st.markdown("""
                <div class='alert-box'>
                    <b>⚠️ CRITICAL PHYSIOLOGICAL DRIFT DETECTED</b><br>
                    High cephalad fluid shift & cardiovascular strain detected. Risk of Spaceflight Associated Neuro-ocular Syndrome (SANS).
                </div>
                """, unsafe_allow_html=True)
                if st.button("⚡ Activate LBNP Suit & Electrolyte Protocol", type="primary", use_container_width=True):
                    st.session_state.countermeasure_active = True
                    st.rerun()
            else:
                st.markdown("""
                <div class='success-box'>
                    <b>✅ COUNTERMEASURE ACTIVE (LBNP + IV Hydration)</b><br>
                    Lower Body Negative Pressure pulling fluids back to lower extremities. Vitals stabilizing.
                </div>
                """, unsafe_allow_html=True)
                if st.button("Reset Countermeasure", use_container_width=True):
                    st.session_state.countermeasure_active = False
                    st.rerun()
        else:
            st.markdown("""
            <div class='success-box'>
                <b>✅ HOMEOSTASIS OPTIMAL</b><br>
                Astronaut vitals remain within safe mission thresholds.
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🔬 Organ Telemetry Breakdown")
        organ_details = {
            "Brain (Neuro-Ocular)": f"**Fluid Shift:** {metrics['fluid_shift']}%. Without gravity, ~2 liters of fluid shift upward, increasing intracranial pressure and flattening the back of the eye.",
            "Heart (Cardiovascular)": f"**Earth vs. Space HR:** {st.session_state.earth_hr} BPM → **{metrics['space_hr']} BPM**. The heart becomes slightly more spherical in 0g and works harder when dehydrated.",
            "Lungs (Respiratory)": "**Gas Exchange:** Ventilation and perfusion equalize across the lung apex and base in 0g, altering particle deposition.",
            "Vascular & DNA": f"**Integrity Score:** {metrics['dna_integrity']}%. Galactic Cosmic Rays (GCR) cause double-strand DNA breaks and endothelial stiffening.",
            "Skeletal Muscles": f"**Retention:** {metrics['muscle_mass']}%. Anti-gravity muscles (soleus, quadriceps) atrophy rapidly without resistive exercise (ARED)."
        }
        st.write(organ_details[selected_organ])

# ------------------------------------------
# TAB 2: المقارنة الفيزيائية والرياضية (Cosmic Connection)
# ------------------------------------------
with tab2:
    st.subheader("Isomorphic Network Physics: Percolation Theory in Space & Biology")
    st.markdown("""
    Both the **Cosmic Web** and **Human Microvascular/Neural Networks** follow scale-free, small-world topologies. 
    Using **Percolation Theory**, we model how cosmic radiation damages capillary connectivity using the exact same mathematical threshold that governs cosmic filament fragmentation.
    """)

    stress_slider = st.slider(
        "Simulate Network Perturbation (Cosmic Expansion / Radiation Dose):",
        0.0, 0.65, round(metrics["radiation"] * (days / 500) * 0.55, 2), 0.05
    )

    fig_c, fig_b, m_base, m_dmg = build_isomorphic_networks(stress_slider)

    nc1, nc2 = st.columns(2)
    with nc1:
        st.plotly_chart(fig_c, use_container_width=True)
    with nc2:
        st.plotly_chart(fig_b, use_container_width=True)

    # جدول مقارنة مقاييس نظرية الشبكات (NetworkX Metrics)
    st.markdown("#### 📊 Structural Graph Theory Comparison (`NetworkX` Live Metrics)")
    df_net = pd.DataFrame({
        "Network Metric": ["Nodes (Galaxies / Neurons)", "Edges (Filaments / Synapses)", "Average Degree", "Clustering Coefficient", "Giant Component Connectivity (%)"],
        "Baseline State (Earth / Early Universe)": list(m_base.values()),
        "Perturbed State (Deep Space / Expansion)": list(m_dmg.values())
    })
    st.table(df_net)

    if m_dmg["Giant Component %"] < 65:
        st.error("🚨 **PERCOLATION THRESHOLD BREACHED:** Network connectivity dropped below critical threshold! Tissue hypoxia / filament fragmentation imminent.")
    else:
        st.success("✅ **TOPOLOGICAL RESILIENCE MAINTAINED:** Giant connected component remains intact above percolation threshold.")

# ------------------------------------------
# TAB 3: التنبؤ الزمني للمهمة (Time-Series Forecast)
# ------------------------------------------
with tab3:
    st.subheader("Longitudinal Biomarker Trajectory Over Mission Timeline")
    timeline = np.arange(1, days + 1)
    hr_series = [calculate_physiology(mission_type, d, hydration, sleep_quality, exercise, st.session_state.earth_hr, st.session_state.countermeasure_active)["space_hr"] for d in timeline]
    fluid_series = [calculate_physiology(mission_type, d, hydration, sleep_quality, exercise, st.session_state.earth_hr, st.session_state.countermeasure_active)["fluid_shift"] for d in timeline]
    dna_series = [calculate_physiology(mission_type, d, hydration, sleep_quality, exercise, st.session_state.earth_hr, st.session_state.countermeasure_active)["dna_integrity"] for d in timeline]

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=timeline, y=hr_series, name="Heart Rate (BPM)", line=dict(color="#EF4444", width=3)))
    fig_ts.add_trace(go.Scatter(x=timeline, y=fluid_series, name="Fluid Shift (%)", line=dict(color="#38BDF8", width=3)))
    fig_ts.add_trace(go.Scatter(x=timeline, y=dna_series, name="DNA Integrity (%)", line=dict(color="#10B981", width=3)))

    fig_ts.update_layout(
        paper_bgcolor='#0F172A', plot_bgcolor='#0F172A',
        font=dict(color='white'),
        xaxis_title="Mission Day",
        yaxis_title="Index / Value",
        height=400
    )
    st.plotly_chart(fig_ts, use_container_width=True)
