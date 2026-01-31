"""
Monthly Review UI - Record results, notes, and action items.
"""
import streamlit as st
from datetime import date
from typing import Dict, Any
from services.agency_service import list_agencies, get_agency_kpis
from services.access_service import get_user_agency_ids
from services.tracking_service import (
    get_monthly_targets,
    get_monthly_results,
    upsert_monthly_results,
    get_monthly_review,
    upsert_monthly_review,
    get_action_items,
    add_action_item,
    toggle_action_item_done,
    delete_action_item,
    get_monthly_summary,
    TrackingServiceError
)
from services.utils import month_name, format_number, get_status_emoji


def render(current_user: Dict[str, Any]):
    """Render the monthly review page."""
    st.header("📝 Seguimiento Mensual")
    st.markdown("Registre resultados, notas y acciones para el seguimiento mensual.")

    # Get agencies
    agencies = list_agencies(active_only=True)

    # Filter by user access (NORMAL users only see assigned agencies)
    if current_user.get("role") != "ADMIN":
        allowed_ids = set(get_user_agency_ids(current_user["id"]))
        agencies = [a for a in agencies if a["id"] in allowed_ids]

    if not agencies:
        st.warning("⚠️ No hay agencias disponibles.")
        return

    # Selection filters
    col1, col2, col3 = st.columns(3)

    with col1:
        agency_options = {a["id"]: f"{a['name']} ({a['city']})" for a in agencies}

        # Check for pre-selected agency
        default_agency = None
        if "selected_agency_for_review" in st.session_state:
            default_agency = st.session_state.selected_agency_for_review
            del st.session_state.selected_agency_for_review

        selected_agency_id = st.selectbox(
            "Agencia",
            options=list(agency_options.keys()),
            format_func=lambda x: agency_options[x],
            index=list(agency_options.keys()).index(default_agency) if default_agency in agency_options else 0
        )

    with col2:
        year = st.selectbox(
            "Año",
            options=[2025, 2026, 2027],
            index=1
        )

    with col3:
        month = st.selectbox(
            "Mes",
            options=list(range(1, 13)),
            format_func=lambda m: f"{m} - {month_name(m)}",
            index=0
        )

    st.markdown("---")

    # Get KPIs
    agency_kpis = get_agency_kpis(selected_agency_id)

    if not agency_kpis:
        st.warning("⚠️ Esta agencia no tiene KPIs asignados.")
        return

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resultados",
        "📝 Notas",
        "✅ Acciones",
        "📈 Resumen"
    ])

    # TAB 1: Results
    with tab1:
        render_results_section(selected_agency_id, year, month, agency_kpis)

    # TAB 2: Notes
    with tab2:
        render_notes_section(selected_agency_id, year, month)

    # TAB 3: Action Items
    with tab3:
        render_actions_section(selected_agency_id, year, month)

    # TAB 4: Summary
    with tab4:
        render_summary_section(selected_agency_id, year, month)


def render_results_section(agency_id: int, year: int, month: int, kpis: list):
    """Render the results input section."""
    st.subheader(f"Resultados de {month_name(month)} {year}")

    # Get existing data
    targets = get_monthly_targets(agency_id, year, month)
    results = get_monthly_results(agency_id, year, month)

    if not targets:
        st.warning("⚠️ No hay objetivos definidos para este mes. Defina los objetivos primero.")
        return

    with st.form("results_form"):
        st.markdown("Ingrese los resultados reales para cada KPI:")

        result_inputs = {}

        for kpi in kpis:
            target = targets.get(kpi.id, 0)
            current_result = results.get(kpi.id, 0.0)

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                result_inputs[kpi.id] = st.number_input(
                    f"{kpi.code} - {kpi.label}",
                    min_value=0.0,
                    value=float(current_result),
                    step=1.0,
                    key=f"result_{kpi.id}",
                    help=f"Objetivo: {format_number(target)} {kpi.unit}"
                )

            with col2:
                st.metric("Objetivo", format_number(target))

            with col3:
                if target > 0:
                    pct = (current_result / target) * 100
                    delta = current_result - target
                    st.metric(
                        "% Cumpl.",
                        f"{pct:.1f}%",
                        delta=f"{delta:+,.0f}"
                    )

        st.markdown("---")

        if st.form_submit_button("💾 Guardar Resultados", type="primary", use_container_width=True):
            try:
                upsert_monthly_results(agency_id, year, month, result_inputs)
                st.success("✅ Resultados guardados exitosamente")
                st.rerun()
            except TrackingServiceError as e:
                st.error(f"❌ Error: {str(e)}")


def render_notes_section(agency_id: int, year: int, month: int):
    """Render the notes section."""
    st.subheader(f"Notas de {month_name(month)} {year}")

    # Get existing review
    review = get_monthly_review(agency_id, year, month)

    with st.form("notes_form"):
        review_date = st.date_input(
            "Fecha de la Reunión",
            value=review["review_date"] if review else date.today()
        )

        st.markdown("---")

        what_happened = st.text_area(
            "¿Qué pasó este mes?",
            value=review["what_happened"] if review else "",
            height=150,
            placeholder="Explique los resultados del mes, desafíos enfrentados, logros alcanzados...",
            help="Descripción de lo que ocurrió durante el mes"
        )

        improvement_plan = st.text_area(
            "¿Qué harás para mejorar el próximo mes?",
            value=review["improvement_plan"] if review else "",
            height=150,
            placeholder="Detalle el plan de acción para mejorar los resultados...",
            help="Plan de mejora para el siguiente mes"
        )

        st.markdown("---")

        if st.form_submit_button("💾 Guardar Notas", type="primary", use_container_width=True):
            try:
                upsert_monthly_review(
                    agency_id, year, month,
                    review_date=review_date,
                    what_happened=what_happened,
                    improvement_plan=improvement_plan
                )
                st.success("✅ Notas guardadas exitosamente")
            except TrackingServiceError as e:
                st.error(f"❌ Error: {str(e)}")


def render_actions_section(agency_id: int, year: int, month: int):
    """Render the action items section."""
    st.subheader(f"Acciones de {month_name(month)} {year}")

    # Show previous month's actions if any
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_actions = get_action_items(agency_id, prev_year, prev_month)

    if prev_actions:
        with st.expander(f"📋 Acciones del mes anterior ({month_name(prev_month)} {prev_year})", expanded=False):
            for action in prev_actions:
                status = "✅" if action["done"] else "⬜"
                st.markdown(f"{status} {action['title']}")

    st.markdown("---")

    # Current month's actions
    current_actions = get_action_items(agency_id, year, month)

    st.markdown("**Acciones para este mes:**")

    if current_actions:
        for action in current_actions:
            col1, col2, col3 = st.columns([0.5, 4, 0.5])

            with col1:
                # Toggle done
                new_done = st.checkbox(
                    "",
                    value=action["done"],
                    key=f"action_done_{action['id']}"
                )
                if new_done != action["done"]:
                    toggle_action_item_done(action["id"], new_done)
                    st.rerun()

            with col2:
                if action["done"]:
                    st.markdown(f"~~{action['title']}~~")
                else:
                    st.markdown(action["title"])

            with col3:
                if st.button("🗑️", key=f"del_action_{action['id']}"):
                    delete_action_item(action["id"])
                    st.rerun()
    else:
        st.info("No hay acciones registradas para este mes")

    # Add new action
    st.markdown("---")
    st.markdown("**Agregar nueva acción:**")

    col1, col2 = st.columns([4, 1])
    with col1:
        new_action = st.text_input(
            "Nueva acción",
            placeholder="Ej: Visitar 10 comercios nuevos...",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("➕ Agregar", use_container_width=True):
            if new_action and new_action.strip():
                try:
                    add_action_item(agency_id, year, month, new_action.strip())
                    st.rerun()
                except TrackingServiceError as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Ingrese un texto para la acción")


def render_summary_section(agency_id: int, year: int, month: int):
    """Render the summary section with KPI status."""
    st.subheader(f"Resumen de {month_name(month)} {year}")

    summary = get_monthly_summary(agency_id, year, month)

    if not summary:
        st.info("No hay datos para mostrar. Registre objetivos y resultados primero.")
        return

    # Overall stats
    col1, col2, col3, col4 = st.columns(4)

    total_kpis = len(summary)
    green_count = sum(1 for s in summary if s["status"] == "green")
    yellow_count = sum(1 for s in summary if s["status"] == "yellow")
    red_count = sum(1 for s in summary if s["status"] == "red")

    with col1:
        st.metric("Total KPIs", total_kpis)
    with col2:
        st.metric("🟢 Verde", green_count)
    with col3:
        st.metric("🟡 Amarillo", yellow_count)
    with col4:
        st.metric("🔴 Rojo", red_count)

    st.markdown("---")

    # Detailed table
    import pandas as pd

    data = []
    for s in summary:
        data.append({
            "Estado": s["status_emoji"],
            "KPI": s["kpi_code"],
            "Objetivo": format_number(s["target"]),
            "Real": format_number(s["actual"]),
            "Diferencia": f"{s['diff']:+,.0f}",
            "% Cumpl.": f"{s['pct']:.1f}%"
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Average performance
    if summary:
        avg_pct = sum(s["pct"] for s in summary) / len(summary)
        st.markdown(f"**Promedio de cumplimiento:** {avg_pct:.1f}%")

        if avg_pct >= 100:
            st.success("🎉 ¡Excelente! Objetivos cumplidos")
        elif avg_pct >= 90:
            st.warning("⚠️ Cerca del objetivo, pero hay espacio para mejorar")
        else:
            st.error("❌ Por debajo del objetivo. Revisar plan de mejora.")
