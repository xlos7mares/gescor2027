# 🛡️ CarteraPulse CRM — Gestión y Tendencias para Corredores de Seguros

Micro aplicación web construida con **Streamlit**, **Pandas** y **Plotly** pensada para corredores, agentes y asesores de seguros que quieren visualizar su cartera completa, detectar renovaciones próximas, comparar ramos o aseguradoras y analizar tendencias sin hojas de cálculo caóticas.

## ✨ Funcionalidades clave
- **KPIs en tiempo real:** Prima anual gestionada, comisión estimada, pólizas próximas a vencer (≤ 30 días) y siniestralidad global.
- **Tendencias de cartera:** Evolución mensual de primas y comisiones, distribución por ramo y radar de renovaciones.
- **Cartera completa:** Búsqueda instantánea, filtros combinados, ordenamiento por columnas y exportación a CSV.
- **Comparador lado a lado:** Compará **dos ramos** o **dos aseguradoras** en prima, comisión, ticket promedio y siniestralidad.
- **Carga rápida:** Probá con datos demo precargados, agregá pólizas desde un formulario o subí tu propio archivo `.csv`.

## 🚀 Cómo ejecutar en local
```bash
git clone [https://github.com/TU-USUARIO/crm-cartera-seguros.git](https://github.com/TU-USUARIO/crm-cartera-seguros.git)
cd crm-cartera-seguros
pip install -r requirements.txt
streamlit run app.py
