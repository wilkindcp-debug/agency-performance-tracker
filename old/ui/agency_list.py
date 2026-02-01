"""
Agency List UI - List and view agency details.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any
from services.agency_service import list_agencies, get_agency_detail
from services.access_service import get_user_agency_ids, user_can_access_agency
from ui.sidebar import set_page


def render(current_user: Dict[str, Any]):
    """Render the agency list page."""
    st.header("🏢 Agencias")

    # Filters
    col1, col2 = st.columns([3, 1])
    with col2:
        show_inactive = st.checkbox("Mostrar inactivas", value=False)

    # Get agencies
    agencies = list_agencies(active_only=not show_inactive)

    # Filter by user access (NORMAL users only see assigned agencies)
    if current_user.get("role") != "ADMIN":
        allowed_ids = set(get_user_agency_ids(current_user["id"]))
        agencies = [a for a in agencies if a["id"] in allowed_ids]

    if not agencies:
        if current_user.get("role") == "ADMIN":
            st.info("📭 No hay agencias registradas. Cree una nueva agencia para comenzar.")
            if st.button("➕ Crear Agencia", type="primary"):
                set_page("agency_setup")
                st.rerun()
        else:
            st.info("📭 No tiene agencias asignadas. Contacte al administrador.")
        return

    # Summary stats
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Agencias", len(agencies))
    with col2:
        active_count = sum(1 for a in agencies if a["active"])
        st.metric("Activas", active_count)
    with col3:
        with_manager = sum(1 for a in agencies if a["manager"])
        st.metric("Con Jefe Asignado", with_manager)

    st.markdown("---")

    # Agency cards/list
    for agency in agencies:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                status_icon = "🟢" if agency["active"] else "🔴"
                st.markdown(f"### {status_icon} {agency['name']}")
                st.caption(f"📍 {agency['city'] or 'Sin ciudad'}")

            with col2:
                if agency["manager"]:
                    st.markdown(f"**Jefe:** {agency['manager']['name']}")
                    if agency["manager"]["email"]:
                        st.caption(f"📧 {agency['manager']['email']}")
                else:
                    st.warning("Sin jefe asignado")

            with col3:
                # View detail button
                if st.button("👁️ Ver Detalle", key=f"view_{agency['id']}"):
                    st.session_state.selected_agency_id = agency["id"]
                    st.rerun()

            # KPI badges
            if agency["kpis"]:
                kpi_badges = " ".join([f"`{kpi['code']}`" for kpi in agency["kpis"]])
                st.markdown(f"**KPIs:** {kpi_badges}")
            else:
                st.caption("Sin KPIs asignados")

            st.markdown("---")

    # Agency detail modal/expander
    if "selected_agency_id" in st.session_state and st.session_state.selected_agency_id:
        show_agency_detail(st.session_state.selected_agency_id)


def show_agency_detail(agency_id: int):
    """Show detailed view of an agency."""
    detail = get_agency_detail(agency_id)

    if not detail:
        st.error("Agencia no encontrada")
        return

    st.markdown("---")
    st.subheader(f"📋 Detalle: {detail['name']}")

    # Close button
    if st.button("❌ Cerrar detalle"):
        del st.session_state.selected_agency_id
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Información General")
        st.markdown(f"**Ciudad:** {detail['city'] or 'No especificada'}")
        st.markdown(f"**Estado:** {'Activa' if detail['active'] else 'Inactiva'}")
        if detail['created_at']:
            st.markdown(f"**Creada:** {detail['created_at'].strftime('%d/%m/%Y')}")

    with col2:
        st.markdown("#### Jefe Actual")
        if detail["active_manager"]:
            manager = detail["active_manager"]
            st.markdown(f"**Nombre:** {manager['name']}")
            if manager.get("email"):
                st.markdown(f"**Email:** {manager['email']}")
            if manager.get("phone"):
                st.markdown(f"**Teléfono:** {manager['phone']}")
            if manager.get("start_date"):
                st.markdown(f"**Desde:** {manager['start_date']}")
        else:
            st.warning("Sin jefe asignado")

    # KPIs assigned
    st.markdown("#### KPIs Asignados")
    if detail["kpis"]:
        kpi_data = []
        for kpi in detail["kpis"]:
            kpi_data.append({
                "Código": kpi["code"],
                "Descripción": kpi["label"],
                "Unidad": kpi["unit"]
            })
        st.table(pd.DataFrame(kpi_data))
    else:
        st.info("No hay KPIs asignados a esta agencia")

    # Manager history
    if len(detail.get("manager_history", [])) > 1:
        with st.expander("📜 Historial de Jefes"):
            for manager in detail["manager_history"]:
                status = "🟢 Activo" if manager["active"] else "⚪ Anterior"
                dates = f"{manager['start_date'] or '?'} - {manager['end_date'] or 'Presente'}"
                st.markdown(f"- {status} **{manager['name']}** ({dates})")

    # Quick actions
    st.markdown("#### Acciones Rápidas")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎯 Ver Objetivos", key="goto_targets"):
            st.session_state.selected_agency_for_targets = agency_id
            set_page("targets_setup")
            st.rerun()

    with col2:
        if st.button("📝 Seguimiento", key="goto_review"):
            st.session_state.selected_agency_for_review = agency_id
            set_page("monthly_review")
            st.rerun()

    with col3:
        if st.button("📊 Dashboard", key="goto_dashboard"):
            set_page("dashboard")
            st.rerun()
