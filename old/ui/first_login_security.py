"""
First Login Security Setup UI - Configure security countries.
"""
import streamlit as st
from services.auth_service import assign_security_countries, AuthServiceError
from services.country_service import get_countries_for_setup


def render(user):
    """
    Render the security setup page.
    User MUST configure 5 security countries before accessing the app.

    Args:
        user: Current user dict
    """
    st.markdown("## 🔐 Configuración de Seguridad")
    st.markdown("---")

    st.warning("""
    ⚠️ **Configuración obligatoria**

    Antes de continuar, debe configurar sus países de seguridad.
    Estos países serán utilizados para recuperar su contraseña si la olvida.

    **Importante:**
    - Seleccione exactamente **5 países** que pueda recordar fácilmente
    - Estos países serán su única forma de recuperar acceso a su cuenta
    - Guárdelos en un lugar seguro
    """)

    st.markdown("---")

    # Get random countries for selection
    if "security_countries_options" not in st.session_state:
        st.session_state.security_countries_options = get_countries_for_setup(15)

    countries = st.session_state.security_countries_options

    if not countries:
        st.error("Error: No hay países disponibles. Contacte al administrador.")
        return

    st.markdown("### Seleccione exactamente 5 países:")
    st.markdown("*Estos países serán su clave de recuperación*")

    with st.form("security_setup_form"):
        selected_ids = []

        # Display countries in columns
        cols = st.columns(3)
        for i, country in enumerate(countries):
            with cols[i % 3]:
                if st.checkbox(
                    f"{country['name']}",
                    key=f"country_{country['id']}"
                ):
                    selected_ids.append(country['id'])

        st.markdown("---")

        # Show selection count
        selected_count = len(selected_ids)
        if selected_count < 5:
            st.info(f"Países seleccionados: {selected_count}/5 - Seleccione {5 - selected_count} más")
        elif selected_count == 5:
            st.success("✅ Has seleccionado 5 países. Puedes continuar.")
        else:
            st.warning(f"⚠️ Has seleccionado {selected_count} países. Debe ser exactamente 5.")

        submit = st.form_submit_button(
            "✅ Confirmar Países de Seguridad",
            use_container_width=True,
            type="primary"
        )

        if submit:
            if len(selected_ids) != 5:
                st.error("Debe seleccionar exactamente 5 países")
            else:
                try:
                    assign_security_countries(user["id"], selected_ids)
                    st.success("✅ Países de seguridad configurados correctamente")

                    # Clear the options from session state
                    if "security_countries_options" in st.session_state:
                        del st.session_state.security_countries_options

                    st.info("Redirigiendo a la aplicación...")
                    st.rerun()
                except AuthServiceError as e:
                    st.error(f"Error: {str(e)}")

    # Refresh countries button
    st.markdown("---")
    if st.button("🔄 Ver otros países", use_container_width=True):
        st.session_state.security_countries_options = get_countries_for_setup(15)
        st.rerun()

    st.markdown("---")
    st.caption("Esta configuración es obligatoria y solo se realiza una vez.")
