from datetime import date, timedelta
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN GENERAL, RUTAS LOCALES Y ESTILO UI/UX
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CarteraCorredor UY | CRM Local Estilo FileMaker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_DB_LOCAL = BASE_DIR / "cartera_corredor_uy.json"
TC_UYU_USD = 42.0

DEPARTAMENTOS_UY = [
    "Montevideo",
    "Canelones",
    "Maldonado",
    "Paysandú",
    "Salto",
    "Colonia",
    "Rivera",
    "Tacuarembó",
    "Cerro Largo",
    "Soriano",
    "Rocha",
    "San José",
    "Artigas",
    "Durazno",
    "Florida",
    "Lavalleja",
    "Treinta y Tres",
    "Flores",
    "Río Negro",
]

ZONAS_CIRCULACION = [
    "Urbana - Capital (Montevideo)",
    "Metropolitana (MVD - Canelones - Costa)",
    "Interior Urbano / Departamental",
    "Ruta Nacional / Mercosur",
    "Rural / Agroindustrial",
]

COMPANIAS_UY = [
    "BSE",
    "Sura",
    "Mapfre Uruguay",
    "Porto Seguro",
    "HDI Seguros",
    "Berkley",
]

COBERTURAS_CATALOGO = [
    "Todo Riesgo con Deducible",
    "Terceros Completo + Robo + Cristales",
    "Responsabilidad Civil (SOA / RC)",
    "Hogar Integral / Combinado Familiar",
    "Comercio / PyME / Todo Riesgo Operativo",
    "Agro / Maquinaria / Silobolsa",
    "Vida Colectivo / Personal",
]

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.35rem;
            padding-bottom: 2.5rem;
            max-width: 1400px;
        }
        .hero-box {
            background: linear-gradient(120deg, #090d16 0%, #172554 55%, #0284c7 100%);
            color: #ffffff;
            padding: 1.35rem 1.7rem;
            border-radius: 16px;
            margin-bottom: 1.1rem;
            box-shadow: 0 10px 25px -12px rgba(9, 13, 22, 0.45);
        }
        .hero-box h1 {
            margin: 0;
            font-size: 1.58rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .hero-box p {
            margin: 0.3rem 0 0 0;
            color: #e0f2fe;
            font-size: 0.93rem;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 0.95rem 1.1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        .kpi-label {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748b;
            margin-bottom: 0.2rem;
        }
        .kpi-value {
            font-size: 1.48rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.2;
        }
        .kpi-sub {
            font-size: 0.78rem;
            margin-top: 0.25rem;
            color: #059669;
            font-weight: 600;
        }
        .kpi-sub-warn {
            font-size: 0.78rem;
            margin-top: 0.25rem;
            color: #d97706;
            font-weight: 700;
        }
        .fm-card {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #0284c7;
            border-radius: 10px;
            padding: 0.85rem 1.05rem;
            margin-bottom: 0.9rem;
            color: #1e293b;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 2. GENERADOR DE 50 CLIENTES / PÓLIZAS DE URUGUAY + PERSISTENCIA EN DISCO
# ---------------------------------------------------------------------------
def generar_50_polizas_uruguay() -> pd.DataFrame:
    rng = np.random.default_rng(2026)
    hoy = date.today()

    nombres_pila = [
        "Martín", "Camila", "Sebastián", "Valentina", "Lucas", "Sofía", "Matías",
        "Lucía", "Diego", "Florencia", "Nicolás", "Agustina", "Federico", "Romina",
        "Joaquín", "Micaela", "Gonzalo", "Paula", "Rodrigo", "Carolina", "Facundo",
        "Jimena", "Andrés", "Natalia", "Bruno", "Mariana", "Ignacio", "Carla",
        "Esteban", "Belén", "Mauricio", "Eugenia", "Gastón", "Vanesa", "Pablo",
        "Cecilia", "Alejandro", "Sabrina", "Leonardo", "Patricia", "Gabriel", "Verónica",
        "Ramiro", "Lorena", "Matteo", "Alicia", "Hernán", "Solange", "Álvaro", "Inés",
    ]
    apellidos = [
        "Rodríguez", "Fernández", "Pérez", "González", "López", "Martínez", "Silva",
        "Acosta", "Sosa", "Núñez", "Pereira", "Morales", "Castro", "Bentancur",
        "Silvera", "Olivera", "Alvez", "Suárez", "Méndez", "Barrios", "Pintos",
        "Giménez", "Duarte", "Ferreira", "Villar", "Correa", "Delgado", "Lemos",
        "Machado", "Cabrera", "Ríos", "Vázquez", "Herrera", "Techera", "Larrosa",
    ]
    empresas_uy = [
        "Logística Litoral SRL",
        "Agropecuaria Queguay SA",
        "Distribuidora Esteña",
        "Clínica Salud del Plata",
        "Constructora Costa Azul",
        "Taller Mecánico Central",
        "Supermercado del Barrio",
        "Transportes Río Uruguay",
        "Estudio Contable Sur",
        "Ferretería Paysandú",
    ]
    cuotas_opciones = [1, 3, 6, 10, 12]
    filas = []

    for i in range(50):
        es_empresa = (i % 6 == 0) and ((i // 6) < len(empresas_uy))
        if es_empresa:
            cliente = empresas_uy[i // 6]
            tipo_cli = "Empresa"
        else:
            cliente = f"{nombres_pila[i]} {apellidos[(i * 3) % len(apellidos)]}"
            tipo_cli = "Persona"

        depto = DEPARTAMENTOS_UY[i % len(DEPARTAMENTOS_UY)]
        if depto == "Montevideo":
            zona = "Urbana - Capital (Montevideo)"
        elif depto in ["Canelones", "Maldonado", "San José"]:
            zona = "Metropolitana (MVD - Canelones - Costa)"
        elif es_empresa and i % 2 == 0:
            zona = "Ruta Nacional / Mercosur"
        elif depto in ["Paysandú", "Salto", "Soriano", "Río Negro", "Durazno", "Cerro Largo", "Tacuarembó"] and i % 3 == 0:
            zona = "Rural / Agroindustrial"
        else:
            zona = "Interior Urbano / Departamental"

        compania = COMPANIAS_UY[(i * 2) % len(COMPANIAS_UY)]
        cobertura = COBERTURAS_CATALOGO[(i * 3) % len(COBERTURAS_CATALOGO)]

        moneda = "USD" if i % 3 != 0 else "UYU"
        premio = float(rng.integers(450, 4600)) if moneda == "USD" else float(rng.integers(15000, 160000))
        cuotas = int(cuotas_opciones[i % len(cuotas_opciones)])
        valor_cuota = round(premio / cuotas, 2)

        com_pct = float(rng.choice([12.0, 15.0, 18.0, 20.0, 22.0]))
        comision_monto = round(premio * (com_pct / 100.0), 2)

        sin_pct = float(rng.choice([0.0, 0.0, 8.0, 15.0, 28.0, 45.0, 62.0]))
        siniestros_monto = round(premio * (sin_pct / 100.0), 2)

        dias_atras = int(rng.integers(15, 340))
        vig_desde = hoy - timedelta(days=dias_atras)
        vig_hasta = vig_desde + timedelta(days=365)
        dias_restantes = (vig_hasta - hoy).days

        if dias_restantes <= 0:
            estado = "Vencida"
        elif dias_restantes <= 30:
            estado = "Por Renovar"
        elif sin_pct >= 50:
            estado = "Siniestro en Curso"
        else:
            estado = "Vigente"

        filas.append(
            {
                "Poliza": f"UY-{202600 + i + 1}",
                "Cliente": cliente,
                "Tipo_Cliente": tipo_cli,
                "Departamento": depto,
                "Zona_Circulacion": zona,
                "Compania": compania,
                "Cobertura": cobertura,
                "Moneda": moneda,
                "Premio_Cotizado": premio,
                "Cuotas": cuotas,
                "Valor_Cuota": valor_cuota,
                "Comision_Pct": com_pct,
                "Comision_Monto": comision_monto,
                "Siniestros_Monto": siniestros_monto,
                "Siniestralidad_Pct": round(sin_pct, 1),
                "Estado": estado,
                "Vigencia_Desde": vig_desde.isoformat(),
                "Vigencia_Hasta": vig_hasta.isoformat(),
                "Dias_Restantes": int(dias_restantes),
            }
        )

    return pd.DataFrame(filas)


def guardar_db_local(df_in: pd.DataFrame) -> None:
    df_save = df_in.copy()
    for col_f in ["Vigencia_Desde", "Vigencia_Hasta"]:
        if col_f in df_save.columns:
            df_save[col_f] = pd.to_datetime(df_save[col_f], errors="coerce").dt.strftime("%Y-%m-%d")
    ARCHIVO_DB_LOCAL.write_text(
        json.dumps(df_save.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def cargar_db_local() -> pd.DataFrame:
    if ARCHIVO_DB_LOCAL.exists():
        try:
            raw = json.loads(ARCHIVO_DB_LOCAL.read_text(encoding="utf-8"))
            if isinstance(raw, list) and len(raw) > 0:
                return pd.DataFrame(raw)
        except Exception:
            pass
    df_init = generar_50_polizas_uruguay()
    guardar_db_local(df_init)
    return df_init


if "df_cartera" not in st.session_state:
    st.session_state.df_cartera = cargar_db_local()


# ---------------------------------------------------------------------------
# 3. ENCABEZADO Y PANEL LATERAL (FILTROS + RESPALDO LOCAL)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-box">
        <h1>🛡️ CarteraCorredor UY — Tu CRM Local Estilo FileMaker</h1>
        <p>Modo Corredor · 50 clientes de Uruguay precargados · Guardado automático en archivo local (<code>cartera_corredor_uy.json</code>) + Respaldos.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

df_base = st.session_state.df_cartera.copy()
df_base["Vigencia_Desde"] = pd.to_datetime(df_base["Vigencia_Desde"], errors="coerce")
df_base["Vigencia_Hasta"] = pd.to_datetime(df_base["Vigencia_Hasta"], errors="coerce")
hoy_ts = pd.Timestamp(date.today())
df_base["Dias_Restantes"] = (df_base["Vigencia_Hasta"] - hoy_ts).dt.days
df_base["Cuotas"] = pd.to_numeric(df_base["Cuotas"], errors="coerce").fillna(1).clip(lower=1).astype(int)
df_base["Premio_Cotizado"] = pd.to_numeric(df_base["Premio_Cotizado"], errors="coerce").fillna(0.0)
df_base["Comision_Pct"] = pd.to_numeric(df_base["Comision_Pct"], errors="coerce").fillna(0.0)
df_base["Valor_Cuota"] = (df_base["Premio_Cotizado"] / df_base["Cuotas"]).round(2)
df_base["Comision_Monto"] = (df_base["Premio_Cotizado"] * (df_base["Comision_Pct"] / 100.0)).round(2)

with st.sidebar:
    st.markdown("### 🎛️ Filtros de Cartera")
    moneda_vista = st.radio("Moneda de tablero", ["USD", "UYU"], horizontal=True)

    deptos_sel = st.multiselect(
        "Departamento",
        options=sorted(df_base["Departamento"].dropna().unique()),
        default=sorted(df_base["Departamento"].dropna().unique()),
    )
    zonas_sel = st.multiselect(
        "Zona de circulación",
        options=sorted(df_base["Zona_Circulacion"].dropna().unique()),
        default=sorted(df_base["Zona_Circulacion"].dropna().unique()),
    )
    cias_sel = st.multiselect(
        "Compañía aseguradora",
        options=sorted(df_base["Compania"].dropna().unique()),
        default=sorted(df_base["Compania"].dropna().unique()),
    )
    cobs_sel = st.multiselect(
        "Cobertura",
        options=sorted(df_base["Cobertura"].dropna().unique()),
        default=sorted(df_base["Cobertura"].dropna().unique()),
    )
    buscar = st.text_input("🔎 Buscar cliente, póliza o depto", placeholder="Ej. Paysandú, BSE, UY-202601...")

    st.divider()
    st.markdown("### 💾 Guardado y Copias de Seguridad")
    st.caption(f"Base local: `{ARCHIVO_DB_LOCAL.name}` ({len(df_base)} registros)")

    # Descargar respaldo JSON
    json_respaldo = ARCHIVO_DB_LOCAL.read_text(encoding="utf-8") if ARCHIVO_DB_LOCAL.exists() else "{}"
    st.download_button(
        "⬇️ Descargar Respaldo (.json)",
        data=json_respaldo.encode("utf-8"),
        file_name=f"respaldo_cartera_uy_{date.today().isoformat()}.json",
        mime="application/json",
        use_container_width=True,
    )

    # Restaurar respaldo JSON
    respaldo_subido = st.file_uploader("📂 Cargar Respaldo (.json)", type=["json"])
    if respaldo_subido is not None:
        try:
            datos_json = json.loads(respaldo_subido.getvalue().decode("utf-8"))
            df_restaurado = pd.DataFrame(datos_json)
            st.session_state.df_cartera = df_restaurado
            guardar_db_local(df_restaurado)
            st.success("¡Respaldo restaurado y guardado en disco!")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo cargar el respaldo: {exc}")

    if st.button("♻️ Reiniciar a 50 clientes demo UY", use_container_width=True):
        df_demo = generar_50_polizas_uruguay()
        st.session_state.df_cartera = df_demo
        guardar_db_local(df_demo)
        st.rerun()

# Aplicar filtros
mask = (
    df_base["Departamento"].isin(deptos_sel if deptos_sel else df_base["Departamento"].unique())
    & df_base["Zona_Circulacion"].isin(zonas_sel if zonas_sel else df_base["Zona_Circulacion"].unique())
    & df_base["Compania"].isin(cias_sel if cias_sel else df_base["Compania"].unique())
    & df_base["Cobertura"].isin(cobs_sel if cobs_sel else df_base["Cobertura"].unique())
)
if buscar.strip():
    q = buscar.strip().lower()
    mask = mask & (
        df_base["Cliente"].astype(str).str.lower().str.contains(q, na=False)
        | df_base["Poliza"].astype(str).str.lower().str.contains(q, na=False)
        | df_base["Departamento"].astype(str).str.lower().str.contains(q, na=False)
        | df_base["Compania"].astype(str).str.lower().str.contains(q, na=False)
    )

df = df_base[mask].copy()


def convertir_monto(monto: float, moneda_origen: str, moneda_destino: str) -> float:
    if moneda_origen == moneda_destino:
        return float(monto)
    if moneda_destino == "USD":
        return float(monto) / TC_UYU_USD
    return float(monto) * TC_UYU_USD


if not df.empty:
    df["Premio_Vista"] = [
        convertir_monto(p, m, moneda_vista) for p, m in zip(df["Premio_Cotizado"], df["Moneda"])
    ]
    df["Comision_Vista"] = [
        convertir_monto(c, m, moneda_vista) for c, m in zip(df["Comision_Monto"], df["Moneda"])
    ]
else:
    df["Premio_Vista"] = []
    df["Comision_Vista"] = []

simbolo = "US$" if moneda_vista == "USD" else "$U "
total_premio = df["Premio_Vista"].sum() if not df.empty else 0.0
total_comision = df["Comision_Vista"].sum() if not df.empty else 0.0
por_vencer_30 = len(df[(df["Dias_Restantes"] >= 0) & (df["Dias_Restantes"] <= 30)]) if not df.empty else 0
prom_cuotas = df["Cuotas"].mean() if not df.empty else 0.0

# ---------------------------------------------------------------------------
# 4. KPIs EN TIEMPO REAL
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Premio Gestionado ({moneda_vista})</div>
            <div class="kpi-value">{simbolo}{total_premio:,.0f}</div>
            <div class="kpi-sub">{len(df)} pólizas · {df['Departamento'].nunique() if not df.empty else 0} departamentos</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Comisión Estimada ({moneda_vista})</div>
            <div class="kpi-value">{simbolo}{total_comision:,.0f}</div>
            <div class="kpi-sub">Guardado en disco al instante</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    cls_vence = "kpi-sub-warn" if por_vencer_30 > 0 else "kpi-sub"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Vencen en ≤ 30 días</div>
            <div class="kpi-value">{por_vencer_30}</div>
            <div class="{cls_vence}">Prioridad de renovación</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Cuotas Promedio</div>
            <div class="kpi-value">{prom_cuotas:.1f}</div>
            <div class="kpi-sub">Plan de emisión en cartera</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

if df.empty:
    st.warning("No hay pólizas con los filtros actuales. Ajustá los filtros de la barra lateral.")
    st.stop()

# ---------------------------------------------------------------------------
# 5. PESTAÑAS PRINCIPALES
# ---------------------------------------------------------------------------
tab_ficha, tab_tend, tab_base, tab_comp = st.tabs(
    [
        "⚡ Ficha Rápida (FileMaker)",
        "📈 Tendencias & Zonas UY",
        "📋 Cartera Completa & Edición",
        "⚖️ Comparador",
    ]
)

# --- TAB 1: FICHA RÁPIDA ESTILO FILEMAKER ---
with tab_ficha:
    st.markdown(
        """
        <div class="fm-card">
            <strong>Alta express de cliente y póliza:</strong> Completá los campos, elegí en cuántas cuotas se emitió el seguro
            y guardá. Todo se graba en <code>cartera_corredor_uy.json</code> y actualiza tablero, gráficos y comparador al toque.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_ficha_corredor", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("#### Cliente y Zona (Uruguay)")
            cliente_n = st.text_input("Nombre o Razón Social *", placeholder="Ej. Marcelo Techera / Agro Norte")
            tipo_cli_n = st.selectbox("Tipo de Cliente", ["Persona", "Empresa"])
            depto_n = st.selectbox("Departamento", DEPARTAMENTOS_UY, index=3)
            zona_n = st.selectbox("Zona de Circulación", ZONAS_CIRCULACION)

        with c2:
            st.markdown("#### Compañía, Cobertura y Vigencia")
            compania_n = st.selectbox("Compañía Aseguradora", COMPANIAS_UY)
            cobertura_n = st.selectbox("Cobertura", COBERTURAS_CATALOGO)
            estado_n = st.selectbox("Estado", ["Vigente", "Por Renovar", "Siniestro en Curso", "Vencida"])
            vig_desde_n = st.date_input("Vigencia Desde", value=date.today())
            vig_hasta_n = st.date_input("Vigencia Hasta", value=date.today() + timedelta(days=365))

        with c3:
            st.markdown("#### Premio, Cuotas y Comisión")
            moneda_n = st.selectbox("Moneda", ["USD", "UYU"])
            premio_n = st.number_input("Premio Cotizado *", min_value=1.0, value=1450.0, step=50.0)
            cuotas_n = st.selectbox("Emitido en Cuotas", [1, 2, 3, 4, 5, 6, 8, 10, 12], index=5)
            com_pct_n = st.slider("Comisión (%)", min_value=0.0, max_value=35.0, value=18.0, step=0.5)
            sin_n = st.number_input("Siniestros Acumulados", min_value=0.0, value=0.0, step=50.0)

        cuota_est = round(premio_n / cuotas_n, 2)
        com_est = round(premio_n * (com_pct_n / 100.0), 2)
        st.info(
            f"Resumen de emisión: **{cuotas_n} cuotas de {moneda_n} {cuota_est:,.2f}** · "
            f"Comisión de la póliza: **{moneda_n} {com_est:,.2f}**"
        )

        grabar_btn = st.form_submit_button("💾 Grabar Ficha en Base Local", type="primary")
        if grabar_btn:
            if not cliente_n.strip():
                st.error("Ingresá el nombre o razón social del cliente.")
            elif vig_hasta_n <= vig_desde_n:
                st.error("La fecha de fin de vigencia debe ser mayor a la fecha de inicio.")
            else:
                nueva_poliza = f"UY-{202600 + len(st.session_state.df_cartera) + 1}"
                dias_rest = (vig_hasta_n - date.today()).days
                sin_pct = round((sin_n / premio_n) * 100.0, 1) if premio_n > 0 else 0.0

                nueva_fila = {
                    "Poliza": nueva_poliza,
                    "Cliente": cliente_n.strip(),
                    "Tipo_Cliente": tipo_cli_n,
                    "Departamento": depto_n,
                    "Zona_Circulacion": zona_n,
                    "Compania": compania_n,
                    "Cobertura": cobertura_n,
                    "Moneda": moneda_n,
                    "Premio_Cotizado": float(premio_n),
                    "Cuotas": int(cuotas_n),
                    "Valor_Cuota": float(cuota_est),
                    "Comision_Pct": float(com_pct_n),
                    "Comision_Monto": float(com_est),
                    "Siniestros_Monto": float(sin_n),
                    "Siniestralidad_Pct": sini_pct,
                    "Estado": estado_n,
                    "Vigencia_Desde": vig_desde_n.isoformat(),
                    "Vigencia_Hasta": vig_hasta_n.isoformat(),
                    "Dias_Restantes": int(dias_rest),
                }
                df_actualizado = pd.concat(
                    [st.session_state.df_cartera, pd.DataFrame([nueva_fila])],
                    ignore_index=True,
                )
                st.session_state.df_cartera = df_actualizado
                guardar_db_local(df_actualizado)
                st.success(f"¡Póliza **{nueva_poliza}** grabada para **{cliente_n.strip()}**!")
                st.rerun()

# --- TAB 2: TENDENCIAS & ZONAS UY ---
with tab_tend:
    g_izq, g_der = st.columns([1.25, 1])

    with g_izq:
        st.subheader(f"Premio por Departamento ({moneda_vista})")
        df_depto_g = (
            df.groupby("Departamento", as_index=False)["Premio_Vista"]
            .sum()
            .sort_values("Premio_Vista", ascending=True)
            .tail(10)
        )
        fig_d = px.bar(
            df_depto_g,
            x="Premio_Vista",
            y="Departamento",
            orientation="h",
            labels={"Premio_Vista": f"Premio ({moneda_vista})", "Departamento": ""},
            color="Premio_Vista",
            color_continuous_scale="Blues",
        )
        fig_d.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_d, use_container_width=True)

    with g_der:
        st.subheader(f"Premio por Zona de Circulación ({moneda_vista})")
        df_zona_g = df.groupby("Zona_Circulacion", as_index=False)["Premio_Vista"].sum()
        fig_z = px.pie(df_zona_g, values="Premio_Vista", names="Zona_Circulacion", hole=0.45)
        fig_z.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_z, use_container_width=True)

    st.subheader(f"Comisiones por Compañía Aseguradora ({moneda_vista})")
    df_cia_g = (
        df.groupby("Compania", as_index=False)[["Premio_Vista", "Comision_Vista"]]
        .sum()
        .sort_values("Comision_Vista", ascending=False)
    )
    fig_cia = go.Figure()
    fig_cia.add_trace(
        go.Bar(x=df_cia_g["Compania"], y=df_cia_g["Premio_Vista"], name=f"Premio ({moneda_vista})", marker_color="#1d4ed8")
    )
    fig_cia.add_trace(
        go.Bar(x=df_cia_g["Compania"], y=df_cia_g["Comision_Vista"], name=f"Comisión ({moneda_vista})", marker_color="#10b981")
    )
    fig_cia.update_layout(barmode="group", height=320, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_cia, use_container_width=True)

# --- TAB 3: BASE COMPLETA Y EDICIÓN EN VIVO ---
with tab_base:
    st.subheader("Base completa de pólizas (editá directo y guardá en disco)")
    cols_show = [
        "Poliza",
        "Cliente",
        "Tipo_Cliente",
        "Departamento",
        "Zona_Circulacion",
        "Compania",
        "Cobertura",
        "Moneda",
        "Premio_Cotizado",
        "Cuotas",
        "Valor_Cuota",
        "Comision_Pct",
        "Estado",
        "Vigencia_Desde",
        "Vigencia_Hasta",
        "Dias_Restantes",
    ]
    df_ed_src = df[cols_show].copy()
    df_ed_src["Vigencia_Desde"] = pd.to_datetime(df_ed_src["Vigencia_Desde"]).dt.date
    df_ed_src["Vigencia_Hasta"] = pd.to_datetime(df_ed_src["Vigencia_Hasta"]).dt.date

    df_editada = st.data_editor(
        df_ed_src,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="editor_base_uy_local",
    )

    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("💾 Guardar Cambios en Archivo Local", type="primary"):
            base_idx = st.session_state.df_cartera.set_index("Poliza")
            edit_idx = df_editada.set_index("Poliza")
            for pol_id, row_ed in edit_idx.iterrows():
                if pol_id in base_idx.index:
                    for col_u in [
                        "Cliente",
                        "Tipo_Cliente",
                        "Departamento",
                        "Zona_Circulacion",
                        "Compania",
                        "Cobertura",
                        "Moneda",
                        "Premio_Cotizado",
                        "Cuotas",
                        "Comision_Pct",
                        "Estado",
                        "Vigencia_Desde",
                        "Vigencia_Hasta",
                    ]:
                        if col_u in row_ed:
                            val_u = row_ed[col_u]
                            if isinstance(val_u, date):
                                val_u = val_u.isoformat()
                            base_idx.at[pol_id, col_u] = val_u

                    premio_c = float(pd.to_numeric(base_idx.at[pol_id, "Premio_Cotizado"], errors="coerce") or 0.0)
                    cuotas_c = max(int(pd.to_numeric(base_idx.at[pol_id, "Cuotas"], errors="coerce") or 1), 1)
                    com_c = float(pd.to_numeric(base_idx.at[pol_id, "Comision_Pct"], errors="coerce") or 0.0)
                    base_idx.at[pol_id, "Cuotas"] = cuotas_c
                    base_idx.at[pol_id, "Valor_Cuota"] = round(premio_c / cuotas_c, 2)
                    base_idx.at[pol_id, "Comision_Monto"] = round(premio_c * (com_c / 100.0), 2)

            df_final = base_idx.reset_index()
            st.session_state.df_cartera = df_final
            guardar_db_local(df_final)
            st.success("¡Base local actualizada y guardada!")
            st.rerun()

    with b2:
        csv_export = df_editada.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar cartera filtrada (.csv)",
            data=csv_export,
            file_name=f"cartera_corredor_uy_{date.today().isoformat()}.csv",
            mime="text/csv",
        )

# --- TAB 4: COMPARADOR ---
with tab_comp:
    st.subheader(f"Comparador lado a lado ({moneda_vista})")
    dim_label = st.radio(
        "Comparar por:",
        ["Compañía Aseguradora", "Cobertura", "Departamento", "Zona de Circulación"],
        horizontal=True,
    )
    dim_map = {
        "Compañía Aseguradora": "Compania",
        "Cobertura": "Cobertura",
        "Departamento": "Departamento",
        "Zona de Circulación": "Zona_Circulacion",
    }
    col_dim = dim_map[dim_label]
    ops = sorted(df[col_dim].dropna().unique())

    if len(ops) >= 2:
        ca, cb = st.columns(2)
        with ca:
            op_a = st.selectbox("Opción A", ops, index=0)
        with cb:
            op_b = st.selectbox("Opción B", ops, index=1)

        def resumir_item(valor_item):
            sub = df[df[col_dim] == valor_item]
            p_sum = sub["Premio_Vista"].sum()
            c_sum = sub["Comision_Vista"].sum()
            n_pol = len(sub)
            c_prom = sub["Cuotas"].mean() if n_pol > 0 else 0.0
            return {
                dim_label: valor_item,
                "Pólizas": n_pol,
                f"Premio ({moneda_vista})": round(p_sum, 2),
                f"Comisión ({moneda_vista})": round(c_sum, 2),
                "Cuotas Promedio": round(c_prom, 1),
            }

        ra = resumir_item(op_a)
        rb = resumir_item(op_b)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                f"Premio {op_a}",
                f"{simbolo}{ra[f'Premio ({moneda_vista})']:,.0f}",
                delta=f"{ra[f'Premio ({moneda_vista})'] - rb[f'Premio ({moneda_vista})']:+,.0f} vs {op_b}",
            )
        with m2:
            st.metric(
                f"Comisión {op_a}",
                f"{simbolo}{ra[f'Comisión ({moneda_vista})']:,.0f}",
                delta=f"{ra[f'Comisión ({moneda_vista})'] - rb[f'Comisión ({moneda_vista})']:+,.0f} vs {op_b}",
            )
        with m3:
            st.metric(
                f"Cuotas prom. {op_a}",
                f"{ra['Cuotas Promedio']:.1f}",
                delta=f"{ra['Cuotas Promedio'] - rb['Cuotas Promedio']:+.1f} vs {op_b}",
            )

        st.dataframe(pd.DataFrame([ra, rb]), use_container_width=True, hide_index=True)
    else:
        st.info("Ajustá los filtros para tener al menos 2 opciones distintas que comparar.")
