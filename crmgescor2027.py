from datetime import date, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN GENERAL Y ESTILO UI / UX
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CarteraPulse CRM | Corredores de Seguros",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
            max-width: 1320px;
        }
        .hero-box {
            background: linear-gradient(120deg, #0f172a 0%, #1e3a8a 60%, #0284c7 100%);
            color: #ffffff;
            padding: 1.4rem 1.7rem;
            border-radius: 16px;
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 25px -10px rgba(15, 23, 42, 0.35);
        }
        .hero-box h1 {
            margin: 0;
            font-size: 1.65rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .hero-box p {
            margin: 0.35rem 0 0 0;
            color: #dbeafe;
            font-size: 0.95rem;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1rem 1.15rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        .kpi-label {
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748b;
            margin-bottom: 0.25rem;
        }
        .kpi-value {
            font-size: 1.55rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.2;
        }
        .kpi-sub {
            font-size: 0.8rem;
            margin-top: 0.3rem;
            color: #059669;
            font-weight: 500;
        }
        .kpi-sub-warn {
            font-size: 0.8rem;
            margin-top: 0.3rem;
            color: #d97706;
            font-weight: 600;
        }
        div[data-testid="stMetric"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 0.8rem 1rem;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 2. DATOS INICIALES DE EJEMPLO (PARA DEMO INSTANTÁNEA)
# ---------------------------------------------------------------------------
@st.cache_data
def generar_cartera_inicial() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    hoy = date.today()

    clientes = [
        ("Grupo Logístico Sur", "Empresa", "Auto Flota", "Seguros del Plata", 14800, 0.16, 0.38, "Vigente", 18),
        ("María Fernanda Sosa", "Persona", "Hogar Integral", "Mapfre", 1450, 0.20, 0.12, "Vigente", 12),
        ("Clínica del Parque", "Empresa", "Salud / Médico", "Sancor Seguros", 9600, 0.14, 0.54, "Por Renovar", 45),
        ("Carlos Alberto Méndez", "Persona", "Vida Individual", "Zurich", 2100, 0.22, 0.05, "Vigente", 75),
        ("Constructora Andina", "Empresa", "Responsabilidad Civil", "Chubb", 11200, 0.15, 0.29, "Vigente", 24),
        ("Lucía Gómez Retail", "Comercio", "Comercio / PyME", "Allianz", 3400, 0.18, 0.41, "Por Renovar", 60),
        ("Martín Ezequiel Ruiz", "Persona", "Automotor", "Seguros del Plata", 1820, 0.17, 0.65, "Siniestro Abierto", 15),
        ("Agropecuaria El Ceibo", "Empresa", "Agro / Maquinaria", "Sancor Seguros", 16500, 0.15, 0.22, "Vigente", 90),
        ("Estudio Jurídico Soler", "Empresa", "Comercio / PyME", "Mapfre", 2750, 0.18, 0.10, "Vigente", 110),
        ("Valeria Castro", "Persona", "Hogar Integral", "Zurich", 1290, 0.20, 0.00, "Vigente", 8),
        ("Transportes del Este", "Empresa", "Auto Flota", "Allianz", 12900, 0.16, 0.48, "Por Renovar", 21),
        ("Diego Nicolás Silva", "Persona", "Automotor", "Chubb", 2350, 0.17, 0.19, "Vigente", 52),
    ]

    filas = []
    for idx, (cliente, tipo_cli, ramo, aseguradora, prima, com_pct, sin_pct, estado, dias_vence) in enumerate(
        clientes, start=1001
    ):
        inicio = hoy - timedelta(days=int(rng.integers(30, 330)))
        vencimiento = hoy + timedelta(days=dias_vence)
        comision = round(prima * com_pct, 2)
        siniestros_usd = round(prima * sin_pct, 2)
        filas.append(
            {
                "Poliza": f"POL-{idx}",
                "Cliente": cliente,
                "Tipo_Cliente": tipo_cli,
                "Ramo": ramo,
                "Aseguradora": aseguradora,
                "Prima_Anual_USD": float(prima),
                "Comision_Pct": round(com_pct * 100, 1),
                "Comision_USD": comision,
                "Siniestros_USD": siniestros_usd,
                "Siniestralidad_Pct": round(sin_pct * 100, 1),
                "Estado": estado,
                "Fecha_Emision": inicio,
                "Fecha_Vencimiento": vencimiento,
                "Dias_Para_Vencer": (vencimiento - hoy).days,
            }
        )
    return pd.DataFrame(filas)


if "df_cartera" not in st.session_state:
    st.session_state.df_cartera = generar_cartera_inicial()


# ---------------------------------------------------------------------------
# 3. ENCABEZADO Y BARRA LATERAL DE FILTROS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-box">
        <h1>🛡️ CarteraPulse CRM — Inteligencia para Corredores de Seguros</h1>
        <p>Gestioná tu cartera, detectá renovaciones a tiempo, compará ramos/aseguradoras y visualizá tendencias en segundos.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

df_full = st.session_state.df_cartera.copy()
df_full["Fecha_Emision"] = pd.to_datetime(df_full["Fecha_Emision"])
df_full["Fecha_Vencimiento"] = pd.to_datetime(df_full["Fecha_Vencimiento"])
hoy_ts = pd.Timestamp(date.today())
df_full["Dias_Para_Vencer"] = (df_full["Fecha_Vencimiento"] - hoy_ts).dt.days

with st.sidebar:
    st.markdown("### 🎛️ Filtros de Cartera")
    ramos_sel = st.multiselect(
        "Ramos",
        options=sorted(df_full["Ramo"].unique()),
        default=sorted(df_full["Ramo"].unique()),
    )
    aseg_sel = st.multiselect(
        "Aseguradoras",
        options=sorted(df_full["Aseguradora"].unique()),
        default=sorted(df_full["Aseguradora"].unique()),
    )
    estados_sel = st.multiselect(
        "Estado de Póliza",
        options=sorted(df_full["Estado"].unique()),
        default=sorted(df_full["Estado"].unique()),
    )
    buscar_cli = st.text_input("🔍 Buscar cliente o póliza", placeholder="Ej. Clínica, POL-1003...")

    st.divider()
    st.markdown("### 📥 Importar tu propio CSV")
    archivo_subido = st.file_uploader("Subí un CSV con tus pólizas", type=["csv"])
    if archivo_subido is not None:
        try:
            df_sub = pd.read_csv(archivo_subido)
            st.session_state.df_cartera = df_sub
            st.success("¡Cartera cargada! Actualizá o revisá las pestañas.")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo leer el CSV: {e}")

    if st.button("🔄 Restaurar datos demo", use_container_width=True):
        st.session_state.df_cartera = generar_cartera_inicial()
        st.rerun()

# Aplicar filtros
mask = (
    df_full["Ramo"].isin(ramos_sel if ramos_sel else df_full["Ramo"].unique())
    & df_full["Aseguradora"].isin(aseg_sel if aseg_sel else df_full["Aseguradora"].unique())
    & df_full["Estado"].isin(estados_sel if estados_sel else df_full["Estado"].unique())
)
if buscar_cli.strip():
    q = buscar_cli.strip().lower()
    mask = mask & (
        df_full["Cliente"].str.lower().str.contains(q, na=False)
        | df_full["Poliza"].str.lower().str.contains(q, na=False)
    )

df = df_full[mask].copy()

# ---------------------------------------------------------------------------
# 4. KPIs PRINCIPALES (SIEMPRE VISIBLES)
# ---------------------------------------------------------------------------
prima_total = df["Prima_Anual_USD"].sum() if not df.empty else 0.0
comision_total = df["Comision_USD"].sum() if not df.empty else 0.0
polizas_activas = len(df)
por_vencer_30 = len(df[(df["Dias_Para_Vencer"] >= 0) & (df["Dias_Para_Vencer"] <= 30)]) if not df.empty else 0
siniestralidad_prom = (
    (df["Siniestros_USD"].sum() / prima_total * 100) if prima_total > 0 else 0.0
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Prima Anual Gestionada</div>
            <div class="kpi-value">${prima_total:,.0f}</div>
            <div class="kpi-sub">Cartera filtrada · {polizas_activas} pólizas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Comisión Estimada</div>
            <div class="kpi-value">${comision_total:,.0f}</div>
            <div class="kpi-sub">Ingreso proyectado por cartera</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    clase_vence = "kpi-sub-warn" if por_vencer_30 > 0 else "kpi-sub"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Vencen en ≤ 30 días</div>
            <div class="kpi-value">{por_vencer_30}</div>
            <div class="{clase_vence}">Prioridad de contacto y renovación</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Siniestralidad Global</div>
            <div class="kpi-value">{siniestralidad_prom:.1f}%</div>
            <div class="kpi-sub">Siniestros vs. Prima anual</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

if df.empty:
    st.warning("No hay pólizas que coincidan con los filtros actuales. Ajustá los filtros en la barra lateral.")
    st.stop()

# ---------------------------------------------------------------------------
# 5. PESTAÑAS PRINCIPALES (TENDENCIAS, CARTERA, COMPARADOR, NUEVA PÓLIZA)
# ---------------------------------------------------------------------------
tab_tend, tab_cart, tab_comp, tab_nueva = st.tabs(
    ["📈 Tendencias de Cartera", "📁 Cartera Completa", "⚖️ Comparador", "➕ Agregar Póliza"]
)

# --- TAB 1: TENDENCIAS ---
with tab_tend:
    col_left, col_right = st.columns([1.35, 1])

    with col_left:
        st.subheader("Evolución mensual de emisiones y comisiones")
        df_mes = (
            df.assign(Mes=df["Fecha_Emision"].dt.to_period("M").dt.to_timestamp())
            .groupby("Mes", as_index=False)[["Prima_Anual_USD", "Comision_USD"]]
            .sum()
            .sort_values("Mes")
        )
        fig_mes = go.Figure()
        fig_mes.add_trace(
            go.Bar(
                x=df_mes["Mes"],
                y=df_mes["Prima_Anual_USD"],
                name="Prima Anual (USD)",
                marker_color="#2563eb",
            )
        )
        fig_mes.add_trace(
            go.Scatter(
                x=df_mes["Mes"],
                y=df_mes["Comision_USD"],
                name="Comisión (USD)",
                mode="lines+markers",
                line=dict(color="#10b981", width=3),
            )
        )
        fig_mes.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=25, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_mes, use_container_width=True)

    with col_right:
        st.subheader("Distribución de prima por ramo")
        df_ramo = df.groupby("Ramo", as_index=False)["Prima_Anual_USD"].sum().sort_values(
            "Prima_Anual_USD", ascending=False
        )
        fig_ramo = px.pie(
            df_ramo,
            values="Prima_Anual_USD",
            names="Ramo",
            hole=0.48,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_ramo.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=25, b=10),
        )
        st.plotly_chart(fig_ramo, use_container_width=True)

    st.subheader("🚨 Radar de renovaciones próximas (ordenadas por urgencia)")
    df_radar = df.sort_values("Dias_Para_Vencer")[
        ["Poliza", "Cliente", "Ramo", "Aseguradora", "Prima_Anual_USD", "Comision_USD", "Estado", "Dias_Para_Vencer"]
    ].head(8)
    st.dataframe(
        df_radar,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prima_Anual_USD": st.column_config.NumberColumn("Prima (USD)", format="$%.0f"),
            "Comision_USD": st.column_config.NumberColumn("Comisión (USD)", format="$%.0f"),
            "Dias_Para_Vencer": st.column_config.NumberColumn("Días p/ vencer", format="%d días"),
        },
    )

# --- TAB 2: CARTERA COMPLETA ---
with tab_cart:
    st.subheader("Gestión detallada de pólizas y clientes")
    st.caption("Podés ordenar por cualquier columna haciendo clic en su encabezado o descargar tu cartera filtrada.")

    df_show = df.copy()
    df_show["Fecha_Emision"] = df_show["Fecha_Emision"].dt.strftime("%Y-%m-%d")
    df_show["Fecha_Vencimiento"] = df_show["Fecha_Vencimiento"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prima_Anual_USD": st.column_config.NumberColumn("Prima Anual", format="$%.2f"),
            "Comision_Pct": st.column_config.NumberColumn("Comisión %", format="%.1f%%"),
            "Comision_USD": st.column_config.NumberColumn("Comisión USD", format="$%.2f"),
            "Siniestros_USD": st.column_config.NumberColumn("Siniestros USD", format="$%.2f"),
            "Siniestralidad_Pct": st.column_config.NumberColumn("Siniestralidad %", format="%.1f%%"),
        },
    )

    csv_bytes = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar cartera filtrada (CSV)",
        data=csv_bytes,
        file_name="cartera_seguros_filtrada.csv",
        mime="text/csv",
    )

# --- TAB 3: COMPARADOR ---
with tab_comp:
    st.subheader("Comparador inteligente de cartera")
    modo_comp = st.radio(
        "¿Qué querés comparar?",
        options=["Dos Ramos", "Dos Aseguradoras"],
        horizontal=True,
    )

    if modo_comp == "Dos Ramos":
        col_dim = "Ramo"
        opciones = sorted(df_full["Ramo"].unique())
    else:
        col_dim = "Aseguradora"
        opciones = sorted(df_full["Aseguradora"].unique())

    if len(opciones) >= 2:
        col_a, col_b = st.columns(2)
        with col_a:
            item_a = st.selectbox("Opción A", opciones, index=0)
        with col_b:
            item_b = st.selectbox("Opción B", opciones, index=1 if len(opciones) > 1 else 0)

        def resumir_segmento(nombre: str) -> dict:
            sub = df_full[df_full[col_dim] == nombre]
            prima = sub["Prima_Anual_USD"].sum()
            com = sub["Comision_USD"].sum()
            sin = sub["Siniestros_USD"].sum()
            n_pol = len(sub)
            ticket = prima / n_pol if n_pol > 0 else 0.0
            sini_pct = (sin / prima * 100) if prima > 0 else 0.0
            return {
                "Segmento": nombre,
                "Pólizas": n_pol,
                "Prima Total (USD)": round(prima, 2),
                "Comisión Total (USD)": round(com, 2),
                "Ticket Promedio (USD)": round(ticket, 2),
                "Siniestralidad (%)": round(sini_pct, 1),
            }

        res_a = resumir_segmento(item_a)
        res_b = resumir_segmento(item_b)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                f"Prima: {item_a}",
                f"${res_a['Prima Total (USD)']:,.0f}",
                delta=f"{res_a['Prima Total (USD)'] - res_b['Prima Total (USD)']:+,.0f} vs {item_b}",
            )
        with m2:
            st.metric(
                f"Comisión: {item_a}",
                f"${res_a['Comisión Total (USD)']:,.0f}",
                delta=f"{res_a['Comisión Total (USD)'] - res_b['Comisión Total (USD)']:+,.0f} vs {item_b}",
            )
        with m3:
            st.metric(
                f"Siniestralidad: {item_a}",
                f"{res_a['Siniestralidad (%)']:.1f}%",
                delta=f"{res_a['Siniestralidad (%)'] - res_b['Siniestralidad (%)']:+.1f} pts vs {item_b}",
                delta_color="inverse",
            )

        st.dataframe(pd.DataFrame([res_a, res_b]), use_container_width=True, hide_index=True)
    else:
        st.info("Necesitás al menos 2 categorías distintas para comparar.")

# --- TAB 4: AGREGAR NUEVA PÓLIZA ---
with tab_nueva:
    st.subheader("Registrar nueva póliza en tu cartera")
    with st.form("form_nueva_poliza", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            cliente_n = st.text_input("Nombre del Cliente *", placeholder="Ej. Distribuidora Norte")
            tipo_cli_n = st.selectbox("Tipo de Cliente", ["Persona", "Empresa", "Comercio"])
            ramo_n = st.selectbox(
                "Ramo",
                ["Automotor", "Auto Flota", "Hogar Integral", "Vida Individual", "Salud / Médico", "Comercio / PyME", "Responsabilidad Civil", "Agro / Maquinaria"],
            )
        with f2:
            aseg_n = st.text_input("Aseguradora *", placeholder="Ej. Seguros del Plata")
            prima_n = st.number_input("Prima Anual (USD) *", min_value=50.0, value=2500.0, step=50.0)
            com_pct_n = st.slider("Comisión (%)", min_value=1.0, max_value=40.0, value=18.0, step=0.5)
        with f3:
            sini_n = st.number_input("Siniestros Acumulados (USD)", min_value=0.0, value=0.0, step=50.0)
            estado_n = st.selectbox("Estado", ["Vigente", "Por Renovar", "Siniestro Abierto"])
            dias_v_n = st.number_input("Días hasta vencimiento", min_value=1, max_value=730, value=180)

        enviado = st.form_submit_button("💾 Guardar Póliza en Cartera", type="primary")
        if enviado:
            if not cliente_n.strip() or not aseg_n.strip():
                st.error("Completá al menos el nombre del cliente y la aseguradora.")
            else:
                hoy_d = date.today()
                com_usd_n = round(prima_n * (com_pct_n / 100.0), 2)
                sini_pct_n = round((sini_n / prima_n) * 100.0, 1) if prima_n > 0 else 0.0
                nuevo_id = f"POL-{1000 + len(st.session_state.df_cartera) + 1}"

                nueva_fila = {
                    "Poliza": nuevo_id,
                    "Cliente": cliente_n.strip(),
                    "Tipo_Cliente": tipo_cli_n,
                    "Ramo": ramo_n,
                    "Aseguradora": aseg_n.strip(),
                    "Prima_Anual_USD": float(prima_n),
                    "Comision_Pct": float(com_pct_n),
                    "Comision_USD": com_usd_n,
                    "Siniestros_USD": float(sini_n),
                    "Siniestralidad_Pct": sini_pct_n,
                    "Estado": estado_n,
                    "Fecha_Emision": pd.Timestamp(hoy_d),
                    "Fecha_Vencimiento": pd.Timestamp(hoy_d + timedelta(days=int(dias_v_n))),
                    "Dias_Para_Vencer": int(dias_v_n),
                }
                st.session_state.df_cartera = pd.concat(
                    [st.session_state.df_cartera, pd.DataFrame([nueva_fila])],
                    ignore_index=True,
                )
                st.success(f"¡Póliza **{nuevo_id}** registrada para **{cliente_n}**!")
