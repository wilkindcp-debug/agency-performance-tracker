"""
Targets Setup UI - Define monthly targets per agency and KPI.
"""
import streamlit as st
from typing import Dict, Any
from services.agency_service import list_agencies, get_agency_kpis
from services.access_service import get_user_agency_ids, user_can_access_agency
from services.tracking_service import (
    upsert_monthly_targets,
    get_monthly_targets,
    copy_targets_to_all_months,
    copy_targets_to_next_month,
    TrackingServiceError
)
from services.utils import month_name, get_current_year


def render(current_user: Dict[str, Any]):
    """Render the targets setup page."""
    st.header("🎯 Objetivos 2026")
    st.markdown("Define los objetivos mensuales por agencia y KPI.")

    # Helpful tip
    with st.expander("💡 ¿Cómo usar esta pantalla?", expanded=False):
        st.markdown("""
        1. **Selecciona** la agencia, año y mes
        2. **Ingresa** los objetivos para cada KPI
        3. **Guarda** con el botón correspondiente

        **Atajos útiles:**
        - 📋 **Copiar a todos los meses**: Usa los mismos objetivos para todo el año
        - ➡️ **Copiar al mes siguiente**: Útil para ajustes graduales
        """)

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
        # Agency selector
        agency_options = {a["id"]: f"{a['name']} ({a['city']})" for a in agencies}

        # Check if there's a pre-selected agency
        default_agency = None
        if "selected_agency_for_targets" in st.session_state:
            default_agency = st.session_state.selected_agency_for_targets
            del st.session_state.selected_agency_for_targets

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
            index=1  # Default to 2026
        )

    with col3:
        month = st.selectbox(
            "Mes",
            options=list(range(1, 13)),
            format_func=lambda m: f"{m} - {month_name(m)}",
            index=0
        )

    st.markdown("---")

    # Get KPIs for selected agency
    agency_kpis = get_agency_kpis(selected_agency_id)

    if not agency_kpis:
        st.warning("⚠️ Esta agencia no tiene KPIs asignados. Asigne KPIs primero.")
        return

    # Get existing targets
    existing_targets = get_monthly_targets(selected_agency_id, year, month)

    # Target input form
    st.subheader(f"📊 Objetivos para {month_name(month)} {year}")

    with st.form("targets_form"):
        targets = {}

        # Create input for each KPI
        cols = st.columns(2)
        for i, kpi in enumerate(agency_kpis):
            with cols[i % 2]:
                default_value = existing_targets.get(kpi.id, 0.0)
                targets[kpi.id] = st.number_input(
                    f"{kpi.code} - {kpi.label} ({kpi.unit})",
                    min_value=0.0,
                    value=float(default_value),
                    step=1.0,
                    key=f"target_{kpi.id}"
                )

        st.markdown("---")

        # Submit buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            save_btn = st.form_submit_button(
                "💾 Guardar Objetivos",
                use_container_width=True,
                type="primary"
            )

        with col2:
            copy_all_btn = st.form_submit_button(
                "📋 Copiar a todos los meses",
                use_container_width=True
            )

        with col3:
            copy_next_btn = st.form_submit_button(
                "➡️ Copiar al mes siguiente",
                use_container_width=True
            )

        # Handle form submissions
        if save_btn:
            try:
                # Filter out zero targets (optional - you might want to keep them)
                non_zero_targets = {k: v for k, v in targets.items() if v > 0}

                if not non_zero_targets:
                    st.warning("⚠️ Ingrese al menos un objetivo mayor a cero")
                else:
                    upsert_monthly_targets(selected_agency_id, year, month, targets)
                    st.success(f"✅ Objetivos guardados para {month_name(month)} {year}")
            except TrackingServiceError as e:
                st.error(f"❌ Error: {str(e)}")

        if copy_all_btn:
            try:
                # First save current month
                upsert_monthly_targets(selected_agency_id, year, month, targets)
                # Then copy to all months
                months_updated = copy_targets_to_all_months(selected_agency_id, year, month)
                st.success(f"✅ Objetivos copiados a {months_updated} meses")
            except TrackingServiceError as e:
                st.error(f"❌ Error: {str(e)}")

        if copy_next_btn:
            try:
                # First save current month
                upsert_monthly_targets(selected_agency_id, year, month, targets)
                # Then copy to next month
                copy_targets_to_next_month(selected_agency_id, year, month)
                next_month = month + 1 if month < 12 else 1
                next_year = year if month < 12 else year + 1
                st.success(f"✅ Objetivos copiados a {month_name(next_month)} {next_year}")
            except TrackingServiceError as e:
                st.error(f"❌ Error: {str(e)}")

    # Show year overview
    st.markdown("---")
    with st.expander("📅 Vista Anual de Objetivos"):
        show_year_overview(selected_agency_id, year, agency_kpis)


def show_year_overview(agency_id: int, year: int, kpis: list):
    """Show a table with all months' targets."""
    import pandas as pd

    # Build data for table
    data = {"Mes": [month_name(m) for m in range(1, 13)]}

    for kpi in kpis:
        kpi_values = []
        for month in range(1, 13):
            targets = get_monthly_targets(agency_id, year, month)
            value = targets.get(kpi.id, 0)
            kpi_values.append(value if value > 0 else "-")
        data[kpi.code] = kpi_values

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Show totals
    st.markdown("**Totales Anuales:**")
    totals = []
    for kpi in kpis:
        total = sum(
            get_monthly_targets(agency_id, year, m).get(kpi.id, 0)
            for m in range(1, 13)
        )
        totals.append(f"{kpi.code}: {total:,.0f}")

    st.markdown(" | ".join(totals))
