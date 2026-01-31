"""
Dashboard for NORMAL users - KPI cards and status overview.
Answers 3 questions in 10 seconds:
1. ¿Voy bien o mal este mes?
2. ¿En qué KPI estoy fallando?
3. ¿Qué tengo que hacer el próximo mes?
"""
import streamlit as st
from datetime import date
from typing import Dict, Any, Optional
from services.dashboard_service import (
    get_agency_dashboard_data,
    get_kpi_card_data,
    get_period_status_message
)
from services.onboarding_service import (
    is_onboarding_completed,
    complete_onboarding,
    get_onboarding_checklist,
    is_checklist_complete,
    get_user_primary_agency
)
from services.access_service import get_user_agencies
from services.utils import month_name


def render(current_user: Dict[str, Any]):
    """Render the NORMAL user dashboard."""
    user_id = current_user["id"]

    # Get user's agencies
    agencies = get_user_agencies(user_id)

    if not agencies:
        render_no_agencies_message()
        return

    # Current period
    today = date.today()
    year = today.year
    month = today.month

    # Agency selector (if multiple)
    if len(agencies) > 1:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            agency_options = {a["id"]: f"{a['name']} ({a['city']})" for a in agencies}
            selected_agency_id = st.selectbox(
                "Seleccionar Agencia",
                options=list(agency_options.keys()),
                format_func=lambda x: agency_options[x],
                key="dashboard_agency_select"
            )
        with col2:
            year = st.selectbox("Año", [2025, 2026, 2027], index=1, key="dash_year")
        with col3:
            month = st.selectbox(
                "Mes",
                list(range(1, 13)),
                format_func=lambda m: month_name(m),
                index=today.month - 1,
                key="dash_month"
            )
    else:
        selected_agency_id = agencies[0]["id"]
        # Period selector only
        col1, col2 = st.columns([1, 1])
        with col1:
            year = st.selectbox("Año", [2025, 2026, 2027], index=1, key="dash_year")
        with col2:
            month = st.selectbox(
                "Mes",
                list(range(1, 13)),
                format_func=lambda m: month_name(m),
                index=today.month - 1,
                key="dash_month"
            )

    # Check if onboarding is needed
    if not is_onboarding_completed(user_id):
        render_onboarding(current_user, selected_agency_id, year, month)
        return

    # Get dashboard data
    data = get_agency_dashboard_data(selected_agency_id, year, month)

    if not data:
        st.warning("⚠️ No se pudo cargar la información del dashboard.")
        return

    # Render main dashboard
    render_status_header(data)
    render_kpi_cards(data)
    render_actions_summary(data)
    render_review_summary(data)


def render_no_agencies_message():
    """Show message when user has no agencies assigned."""
    st.markdown("## 👋 ¡Bienvenido!")
    st.info(
        "🏢 Aún no tienes agencias asignadas.\n\n"
        "Contacta al administrador para que te asigne las agencias que gestionarás."
    )


def render_onboarding(current_user: Dict[str, Any], agency_id: int, year: int, month: int):
    """Render onboarding flow for first-time users."""
    user_id = current_user["id"]

    st.markdown("## 👋 ¡Bienvenido al Agency Tracker!")
    st.markdown(f"Hola **{current_user['username']}**, esta es tu primera vez aquí. Te mostramos cómo empezar:")

    st.markdown("---")

    # Get checklist
    checklist = get_onboarding_checklist(user_id, year, month)

    # Progress bar
    completed = sum(1 for v in checklist.values() if v)
    total = len(checklist)
    progress = completed / total if total > 0 else 0

    st.progress(progress, text=f"Progreso: {completed}/{total} pasos completados")

    st.markdown("### 📋 Lista de inicio:")

    # Step 1: Has assigned agencies
    icon1 = "✅" if checklist["has_agency"] else "⬜"
    st.markdown(f"{icon1} **Tienes agencias asignadas**")
    if not checklist["has_agency"]:
        st.caption("   → Contacta al administrador para que te asigne agencias")

    # Step 2: Has targets
    icon2 = "✅" if checklist["viewed_targets"] else "⬜"
    st.markdown(f"{icon2} **Tienes objetivos definidos para {month_name(month)} {year}**")
    if not checklist["viewed_targets"]:
        st.caption("   → Ve a 'Objetivos' y define las metas mensuales")
        if st.button("🎯 Ir a definir objetivos", key="onb_targets"):
            st.session_state.current_page = "targets_setup"
            st.rerun()

    # Step 3: Has previous review
    icon3 = "✅" if checklist["reviewed_previous"] else "⬜"
    st.markdown(f"{icon3} **Has completado la revisión del mes anterior**")
    if not checklist["reviewed_previous"]:
        st.caption("   → Completa la revisión del mes anterior para continuar")

    # Step 4: Has current review
    icon4 = "✅" if checklist["completed_review"] else "⬜"
    st.markdown(f"{icon4} **Has realizado la revisión de {month_name(month)}**")
    if not checklist["completed_review"]:
        st.caption("   → Ve a 'Revisión' cuando tengas los resultados para reportar")

    st.markdown("---")

    # Complete onboarding button
    if checklist["has_agency"] and checklist["viewed_targets"] and checklist["completed_review"]:
        st.success("🎉 ¡Ya tienes todo listo para comenzar!")
        if st.button("✨ Comenzar a usar el dashboard", type="primary", use_container_width=True):
            complete_onboarding(user_id)
            st.rerun()
    else:
        st.info("💡 Completa los pasos anteriores para habilitar tu dashboard")


def render_status_header(data: Dict[str, Any]):
    """Render the main status header - answers '¿Voy bien o mal?'"""
    agency = data["agency"]
    month_str = data["month_name"]
    year = data["year"]
    status = data["overall_status"]

    # Agency name
    st.markdown(f"## 🏢 {agency['name']}")
    st.caption(f"{agency['city']} • {month_str} {year}")

    st.markdown("---")

    # Big status indicator
    status_config = {
        "green": {
            "emoji": "🟢",
            "title": "¡Excelente!",
            "message": "Todos los objetivos cumplidos",
            "color": "#28a745"
        },
        "yellow": {
            "emoji": "🟡",
            "title": "En riesgo",
            "message": "Algunos KPIs necesitan atención",
            "color": "#ffc107"
        },
        "red": {
            "emoji": "🔴",
            "title": "Atención requerida",
            "message": "Hay KPIs por debajo del objetivo",
            "color": "#dc3545"
        },
        "none": {
            "emoji": "⚪",
            "title": "Sin datos",
            "message": "Registra resultados para ver tu estado",
            "color": "#6c757d"
        }
    }

    config = status_config.get(status, status_config["none"])

    # Status card
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.markdown(f"### {config['emoji']} {config['title']}")
        st.caption(config["message"])

    with col2:
        st.metric("🟢 OK", data["green_count"])

    with col3:
        st.metric("🟡 Riesgo", data["yellow_count"])

    with col4:
        st.metric("🔴 Bajo", data["red_count"])

    st.markdown("---")


def render_kpi_cards(data: Dict[str, Any]):
    """Render KPI cards - answers '¿En qué KPI estoy fallando?'"""
    st.markdown("### 📊 Estado de KPIs")

    kpis = data["kpis"]

    if not kpis:
        st.info("No hay KPIs configurados para esta agencia")
        return

    # Sort: red first, then yellow, then green
    sorted_kpis = sorted(kpis, key=lambda k: (
        0 if k["status"] == "red" else (1 if k["status"] == "yellow" else 2)
    ))

    # Display in columns (2 per row)
    for i in range(0, len(sorted_kpis), 2):
        cols = st.columns(2)

        for j, col in enumerate(cols):
            if i + j < len(sorted_kpis):
                kpi = sorted_kpis[i + j]
                card_data = get_kpi_card_data(kpi)

                with col:
                    render_single_kpi_card(card_data)


def render_single_kpi_card(card: Dict[str, Any]):
    """Render a single KPI card."""
    status_bg = {
        "green": "#d4edda",
        "yellow": "#fff3cd",
        "red": "#f8d7da"
    }

    bg_color = status_bg.get(card["status"], "#f8f9fa")

    st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong>{card['code']}</strong>
                <span style="font-size: 1.5rem;">{card['status_emoji']}</span>
            </div>
            <div style="color: #666; font-size: 0.9rem;">{card['label']}</div>
            <div style="margin-top: 0.5rem;">
                <span style="font-size: 1.5rem; font-weight: bold;">{card['actual']:,.0f}</span>
                <span style="color: #666;"> / {card['target']:,.0f} {card['unit']}</span>
            </div>
            <div style="color: {card['status_color']}; font-weight: bold;">
                {card['pct']:.1f}% • {card['status_label']}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_actions_summary(data: Dict[str, Any]):
    """Render actions summary - answers '¿Qué tengo que hacer?'"""
    st.markdown("### ✅ Acciones del mes")

    pending = data["pending_actions"]
    completed = data["completed_actions"]

    if not pending and not completed:
        st.info("No hay acciones registradas. Ve a 'Seguimiento' para agregar acciones.")
        if st.button("📝 Ir a Seguimiento", key="go_tracking"):
            st.session_state.selected_agency_for_review = data["agency"]["id"]
            st.session_state.current_page = "monthly_review"
            st.rerun()
        return

    # Progress
    total = len(pending) + len(completed)
    done = len(completed)
    pct = (done / total * 100) if total > 0 else 0

    st.progress(pct / 100, text=f"{done}/{total} acciones completadas ({pct:.0f}%)")

    # Pending actions
    if pending:
        st.markdown("**Pendientes:**")
        for action in pending[:5]:  # Show max 5
            st.markdown(f"⬜ {action['title']}")
        if len(pending) > 5:
            st.caption(f"... y {len(pending) - 5} más")

    # Link to full list
    if st.button("📋 Ver todas las acciones", key="view_actions"):
        st.session_state.selected_agency_for_review = data["agency"]["id"]
        st.session_state.current_page = "monthly_review"
        st.rerun()

    st.markdown("---")


def render_review_summary(data: Dict[str, Any]):
    """Render review summary with improvement plan."""
    review = data.get("review")

    if data["review_pending"]:
        st.warning("⚠️ **Revisión pendiente**: Tienes resultados registrados pero no has completado las notas del mes.")
        if st.button("📝 Completar revisión", type="primary", key="complete_review"):
            st.session_state.selected_agency_for_review = data["agency"]["id"]
            st.session_state.current_page = "monthly_review"
            st.rerun()
        return

    if review:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📝 ¿Qué pasó este mes?")
            if review.get("what_happened"):
                st.markdown(review["what_happened"])
            else:
                st.caption("Sin notas")

        with col2:
            st.markdown("### 🚀 Plan de mejora")
            if review.get("improvement_plan"):
                st.markdown(review["improvement_plan"])
            else:
                st.caption("Sin plan definido")
