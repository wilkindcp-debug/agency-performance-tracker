"""
Dashboard UI - Overview of all agencies performance.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any
from services.tracking_service import get_all_agencies_summary, get_monthly_summary
from services.agency_service import list_agencies
from services.access_service import get_user_agency_ids
from services.utils import month_name, format_number, get_status_emoji, get_status_color


def render(current_user: Dict[str, Any]):
    """Render the dashboard page."""
    st.header("📊 Dashboard")
    st.markdown("Vista general del desempeño de todas las agencias.")

    # Period selector
    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox(
            "Año",
            options=[2025, 2026, 2027],
            index=1,
            key="dash_year"
        )

    with col2:
        month = st.selectbox(
            "Mes",
            options=list(range(1, 13)),
            format_func=lambda m: f"{m} - {month_name(m)}",
            index=0,
            key="dash_month"
        )

    st.markdown("---")

    # Get summary data
    agencies_summary = get_all_agencies_summary(year, month)

    # Filter by user access (NORMAL users only see assigned agencies)
    if current_user.get("role") != "ADMIN":
        allowed_ids = set(get_user_agency_ids(current_user["id"]))
        agencies_summary = [a for a in agencies_summary if a["agency_id"] in allowed_ids]

    if not agencies_summary:
        st.info("📭 No hay datos para mostrar. Registre agencias y objetivos primero.")
        return

    # Overall statistics
    st.subheader(f"📈 Resumen de {month_name(month)} {year}")

    total_agencies = len(agencies_summary)
    agencies_with_data = sum(1 for a in agencies_summary if a["kpi_details"])

    # Count by status
    total_red = sum(a["red_count"] for a in agencies_summary)
    total_yellow = sum(a["yellow_count"] for a in agencies_summary)
    total_green = sum(a["green_count"] for a in agencies_summary)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Agencias", total_agencies)
    with col2:
        st.metric("Con datos", agencies_with_data)
    with col3:
        st.metric("🟢 Verde", total_green)
    with col4:
        st.metric("🟡 Amarillo", total_yellow)
    with col5:
        st.metric("🔴 Rojo", total_red)

    st.markdown("---")

    # Ranking table
    st.subheader("🏆 Ranking de Agencias")

    if agencies_with_data > 0:
        ranking_data = []
        for i, agency in enumerate(agencies_summary, 1):
            if agency["kpi_details"]:
                # Determine overall status
                if agency["red_count"] > 0:
                    overall_status = "🔴"
                elif agency["yellow_count"] > 0:
                    overall_status = "🟡"
                else:
                    overall_status = "🟢"

                ranking_data.append({
                    "Pos": i,
                    "Estado": overall_status,
                    "Agencia": agency["agency_name"],
                    "Ciudad": agency["city"] or "-",
                    "Jefe": agency["manager_name"] or "-",
                    "Promedio": f"{agency['avg_pct']:.1f}%",
                    "🟢": agency["green_count"],
                    "🟡": agency["yellow_count"],
                    "🔴": agency["red_count"]
                })

        if ranking_data:
            df = pd.DataFrame(ranking_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Alerts - Agencies with red KPIs
    st.subheader("⚠️ Alertas - Agencias con KPIs en Rojo")

    agencies_with_red = [a for a in agencies_summary if a["red_count"] > 0]

    if agencies_with_red:
        for agency in agencies_with_red:
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    st.markdown(f"### 🔴 {agency['agency_name']}")
                    st.caption(f"Jefe: {agency['manager_name'] or 'Sin asignar'}")

                with col2:
                    # Show red KPIs
                    red_kpis = [k for k in agency["kpi_details"] if k["status"] == "red"]
                    for kpi in red_kpis:
                        st.markdown(
                            f"- **{kpi['kpi_code']}**: {format_number(kpi['actual'])} / "
                            f"{format_number(kpi['target'])} ({kpi['pct']:.1f}%)"
                        )

                st.markdown("---")
    else:
        st.success("✅ No hay agencias con KPIs en rojo este mes.")

    # Detailed view per agency
    st.markdown("---")
    with st.expander("📋 Vista Detallada por Agencia"):
        for agency in agencies_summary:
            st.markdown(f"### {agency['agency_name']}")

            if agency["kpi_details"]:
                data = []
                for kpi in agency["kpi_details"]:
                    data.append({
                        "Estado": kpi["status_emoji"],
                        "KPI": kpi["kpi_code"],
                        "Objetivo": format_number(kpi["target"]),
                        "Real": format_number(kpi["actual"]),
                        "% Cumpl.": f"{kpi['pct']:.1f}%"
                    })

                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Sin datos para este mes")

            st.markdown("---")

    # Optional: Simple chart
    try:
        render_performance_chart(agencies_summary)
    except Exception:
        pass  # Skip chart if plotly not available


def render_performance_chart(agencies_summary: list):
    """Render a simple performance chart."""
    try:
        import plotly.express as px

        # Filter agencies with data
        chart_data = [
            {
                "Agencia": a["agency_name"],
                "Promedio %": a["avg_pct"]
            }
            for a in agencies_summary
            if a["kpi_details"]
        ]

        if chart_data:
            st.subheader("📊 Gráfico de Desempeño")

            df = pd.DataFrame(chart_data)

            # Create bar chart
            fig = px.bar(
                df,
                x="Agencia",
                y="Promedio %",
                color="Promedio %",
                color_continuous_scale=["red", "yellow", "green"],
                range_color=[0, 120]
            )

            # Add target line at 100%
            fig.add_hline(
                y=100,
                line_dash="dash",
                line_color="green",
                annotation_text="Objetivo 100%"
            )

            fig.update_layout(
                showlegend=False,
                xaxis_tickangle=-45
            )

            st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.info("Instale plotly para ver gráficos: pip install plotly")
