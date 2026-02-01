"""
Dashboard for ADMIN users - Global agency overview.
Shows all agencies, their status, and highlights issues requiring attention.
"""
import streamlit as st
from datetime import date
from typing import Dict, Any, List
from services.dashboard_service import (
    get_admin_dashboard_data,
    get_period_status_message
)
from services.utils import month_name


def render(current_user: Dict[str, Any]):
    """Render the ADMIN dashboard with global view."""
    st.markdown("## 📊 Panel de Administración")
    st.caption(f"Bienvenido, {current_user['username']}")

    # Period selector
    today = date.today()
    col1, col2 = st.columns([1, 1])

    with col1:
        year = st.selectbox("Año", [2025, 2026, 2027], index=1, key="admin_dash_year")
    with col2:
        month = st.selectbox(
            "Mes",
            list(range(1, 13)),
            format_func=lambda m: month_name(m),
            index=today.month - 1,
            key="admin_dash_month"
        )

    st.markdown("---")

    # Get admin dashboard data
    data = get_admin_dashboard_data(year, month)

    if not data or data["total_agencies"] == 0:
        st.warning("⚠️ No hay agencias activas registradas.")
        if st.button("📋 Ir a gestión de agencias", key="go_agencies"):
            st.session_state.current_page = "agency_list"
            st.rerun()
        return

    # Render sections
    render_global_summary(data)
    render_alerts_section(data)
    render_agencies_table(data)
    render_pending_reviews(data)


def render_global_summary(data: Dict[str, Any]):
    """Render global KPI summary across all agencies."""
    st.markdown(f"### 🌍 Resumen Global - {data['month_name']} {data['year']}")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🏢 Agencias", data["total_agencies"])

    with col2:
        st.metric("🟢 OK", data["total_green"])

    with col3:
        st.metric("🟡 Riesgo", data["total_yellow"])

    with col4:
        st.metric("🔴 Bajo", data["total_red"])

    with col5:
        total_kpis = data["total_green"] + data["total_yellow"] + data["total_red"]
        if total_kpis > 0:
            health_pct = (data["total_green"] / total_kpis) * 100
            st.metric("💚 Salud", f"{health_pct:.0f}%")
        else:
            st.metric("💚 Salud", "N/A")

    st.markdown("---")


def render_alerts_section(data: Dict[str, Any]):
    """Render alerts for agencies at risk."""
    at_risk = data["at_risk"]
    pending_reviews = data["pending_reviews"]

    if not at_risk and not pending_reviews:
        st.success("✅ No hay alertas. ¡Todo está bajo control!")
        st.markdown("---")
        return

    st.markdown("### ⚠️ Alertas")

    # Agencies at risk (red KPIs)
    if at_risk:
        with st.expander(f"🔴 {len(at_risk)} agencia(s) con KPIs en rojo", expanded=True):
            for agency_data in at_risk:
                agency = agency_data["agency"]
                red_count = agency_data["red_count"]

                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**{agency['name']}** ({agency['city']})")
                    manager = agency.get("manager")
                    if manager:
                        st.caption(f"Jefe: {manager['name']}")

                with col2:
                    st.markdown(f"🔴 **{red_count}** KPI(s)")

                with col3:
                    if st.button("Ver detalles", key=f"alert_{agency['id']}"):
                        st.session_state.selected_agency_for_review = agency["id"]
                        st.session_state.current_page = "monthly_review"
                        st.rerun()

    # Pending reviews
    if pending_reviews:
        with st.expander(f"📝 {len(pending_reviews)} revisión(es) pendiente(s)", expanded=False):
            for pr in pending_reviews:
                st.markdown(f"• **{pr['agency_name']}** - Jefe: {pr['manager_name']}")

    st.markdown("---")


def render_agencies_table(data: Dict[str, Any]):
    """Render table with all agencies and their status."""
    st.markdown("### 🏢 Estado por Agencia")

    agencies = data["agencies"]

    # Filter options
    filter_option = st.radio(
        "Filtrar por:",
        ["Todas", "Solo con problemas (🔴/🟡)", "Solo OK (🟢)"],
        horizontal=True,
        key="agency_filter"
    )

    if filter_option == "Solo con problemas (🔴/🟡)":
        agencies = [a for a in agencies if a["red_count"] > 0 or a["yellow_count"] > 0]
    elif filter_option == "Solo OK (🟢)":
        agencies = [a for a in agencies if a["red_count"] == 0 and a["yellow_count"] == 0 and a["green_count"] > 0]

    if not agencies:
        st.info("No hay agencias que coincidan con el filtro seleccionado.")
        return

    # Create table data
    import pandas as pd

    table_data = []
    for agency_data in agencies:
        agency = agency_data["agency"]

        # Overall status emoji
        if agency_data["red_count"] > 0:
            status = "🔴"
        elif agency_data["yellow_count"] > 0:
            status = "🟡"
        elif agency_data["green_count"] > 0:
            status = "🟢"
        else:
            status = "⚪"

        manager = agency.get("manager")
        manager_name = manager["name"] if manager else "Sin jefe"

        table_data.append({
            "Estado": status,
            "Agencia": agency["name"],
            "Ciudad": agency["city"],
            "Jefe": manager_name,
            "🟢": agency_data["green_count"],
            "🟡": agency_data["yellow_count"],
            "🔴": agency_data["red_count"],
            "Revisión": "✅" if not agency_data["review_pending"] else "⏳"
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Quick actions
    st.markdown("---")
    st.markdown("**Acciones rápidas:**")

    col1, col2 = st.columns(2)

    with col1:
        agency_options = {a["agency"]["id"]: a["agency"]["name"] for a in data["agencies"]}
        selected = st.selectbox(
            "Seleccionar agencia:",
            options=list(agency_options.keys()),
            format_func=lambda x: agency_options[x],
            key="quick_agency_select"
        )

    with col2:
        st.markdown("")  # Spacing
        st.markdown("")
        if st.button("📝 Ir al seguimiento", key="go_review"):
            st.session_state.selected_agency_for_review = selected
            st.session_state.current_page = "monthly_review"
            st.rerun()

    st.markdown("---")


def render_pending_reviews(data: Dict[str, Any]):
    """Render section with agencies pending review."""
    pending = data["pending_reviews"]

    if not pending:
        return

    st.markdown("### 📋 Revisiones Pendientes")
    st.caption("Estas agencias tienen resultados pero no han completado las notas del mes.")

    for pr in pending:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"• **{pr['agency_name']}** - Jefe: {pr['manager_name']}")

        with col2:
            # Find agency ID
            agency_id = None
            for a in data["agencies"]:
                if a["agency"]["name"] == pr["agency_name"]:
                    agency_id = a["agency"]["id"]
                    break

            if agency_id and st.button("Notificar", key=f"notify_{agency_id}"):
                st.info(f"📧 Funcionalidad de notificación próximamente...")


def render_comparison_chart(data: Dict[str, Any]):
    """Render comparison chart for agencies (optional feature)."""
    try:
        import plotly.express as px
        import pandas as pd

        chart_data = []
        for agency_data in data["agencies"]:
            agency = agency_data["agency"]
            total = agency_data["green_count"] + agency_data["yellow_count"] + agency_data["red_count"]
            if total > 0:
                pct_ok = (agency_data["green_count"] / total) * 100
            else:
                pct_ok = 0

            chart_data.append({
                "Agencia": agency["name"],
                "% Cumplimiento": pct_ok
            })

        if chart_data:
            df = pd.DataFrame(chart_data)
            df = df.sort_values("% Cumplimiento", ascending=True)

            fig = px.bar(
                df,
                x="% Cumplimiento",
                y="Agencia",
                orientation="h",
                title="Cumplimiento por Agencia",
                color="% Cumplimiento",
                color_continuous_scale=["#dc3545", "#ffc107", "#28a745"]
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="% de KPIs Cumplidos",
                yaxis_title=""
            )

            st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        # Plotly not available, skip chart
        pass
