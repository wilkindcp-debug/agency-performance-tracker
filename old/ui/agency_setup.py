"""
Agency Setup UI - Create new agency with manager and KPIs.
"""
import streamlit as st
from typing import Dict, Any
from services.agency_service import create_agency, AgencyServiceError
from services.kpi_service import list_kpis


def render(current_user: Dict[str, Any]):
    """Render the agency setup page. ADMIN only."""
    # Check admin access
    if current_user.get("role") != "ADMIN":
        st.error("⛔ Acceso denegado. Solo administradores pueden crear agencias.")
        return

    st.header("➕ Crear Nueva Agencia")
    st.markdown("Complete el formulario para registrar una nueva agencia con su jefe y KPIs asignados.")

    # Get available KPIs
    kpis = list_kpis(active_only=True)

    if not kpis:
        st.warning("⚠️ No hay KPIs disponibles. Ejecute primero: `python -m scripts.init_kpis`")
        return

    # Create form using st.form to prevent re-renders
    with st.form("agency_form", clear_on_submit=True):
        st.subheader("📋 Datos de la Agencia")

        col1, col2 = st.columns(2)
        with col1:
            agency_name = st.text_input(
                "Nombre de la Agencia *",
                placeholder="Ej: WD Genève",
                help="Nombre único de la agencia"
            )
        with col2:
            city = st.text_input(
                "Ciudad",
                placeholder="Ej: Genève",
                help="Ciudad donde se ubica la agencia"
            )

        st.markdown("---")
        st.subheader("👤 Datos del Jefe de Agencia")

        col1, col2 = st.columns(2)
        with col1:
            manager_name = st.text_input(
                "Nombre Completo del Jefe *",
                placeholder="Ej: Jean Dupont",
                help="Nombre completo del responsable"
            )
            manager_email = st.text_input(
                "Email",
                placeholder="Ej: jean.dupont@empresa.com",
                help="Email de contacto (opcional)"
            )
        with col2:
            manager_phone = st.text_input(
                "Teléfono",
                placeholder="Ej: +41 22 123 4567",
                help="Teléfono de contacto (opcional)"
            )

        st.markdown("---")
        st.subheader("📊 KPIs Asignados")

        # Create checkboxes for KPIs
        st.markdown("Seleccione los KPIs que se medirán para esta agencia:")

        kpi_selections = {}
        cols = st.columns(2)
        for i, kpi in enumerate(kpis):
            with cols[i % 2]:
                kpi_selections[kpi.id] = st.checkbox(
                    f"{kpi.code} - {kpi.label}",
                    value=True,  # Default all selected
                    key=f"kpi_{kpi.id}"
                )

        st.markdown("---")

        # Submit button
        submitted = st.form_submit_button(
            "💾 Crear Agencia",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Validation
            errors = []
            if not agency_name or not agency_name.strip():
                errors.append("El nombre de la agencia es requerido")
            if not manager_name or not manager_name.strip():
                errors.append("El nombre del jefe es requerido")

            selected_kpi_ids = [kpi_id for kpi_id, selected in kpi_selections.items() if selected]
            if not selected_kpi_ids:
                errors.append("Debe seleccionar al menos un KPI")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Create agency with manager and KPIs
                    agency = create_agency(
                        name=agency_name.strip(),
                        city=city.strip() if city else "",
                        manager_name=manager_name.strip(),
                        manager_email=manager_email.strip() if manager_email else None,
                        manager_phone=manager_phone.strip() if manager_phone else None,
                        kpi_ids=selected_kpi_ids
                    )

                    st.success(f"✅ Agencia '{agency.name}' creada exitosamente!")
                    st.balloons()

                    # Show summary
                    st.info(f"""
                    **Resumen:**
                    - Agencia: {agency.name} ({city})
                    - Jefe: {manager_name}
                    - KPIs asignados: {len(selected_kpi_ids)}
                    """)

                except AgencyServiceError as e:
                    st.error(f"❌ Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")

    # Help section
    with st.expander("ℹ️ Ayuda"):
        st.markdown("""
        ### Instrucciones
        1. Complete los datos de la agencia (nombre y ciudad)
        2. Ingrese la información del jefe de agencia
        3. Seleccione los KPIs que se medirán para esta agencia
        4. Haga clic en "Crear Agencia"

        ### KPIs Disponibles
        - **CS**: Capital Services
        - **RIA**: Remesas Internacionales
        - **MG**: MoneyGram - Transferencias
        - **CORNERS**: Puntos de venta activos
        """)
