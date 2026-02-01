"""
Forgot Password UI - Password recovery using security countries.
"""
import streamlit as st
from services.auth_service import (
    get_user_by_username,
    get_user_security_country_ids,
    verify_security_countries,
    reset_password,
    increment_recovery_attempt,
    reset_failed_attempts,
    AuthServiceError
)
from services.country_service import get_countries_for_recovery


def render():
    """Render the forgot password page."""
    st.markdown("## 🔑 Recuperar Contraseña")
    st.markdown("---")

    # Step management
    if "recovery_step" not in st.session_state:
        st.session_state.recovery_step = 1
        st.session_state.recovery_user = None
        st.session_state.recovery_countries = None

    # Back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Volver"):
            clear_recovery_state()
            st.session_state.show_forgot_password = False
            st.rerun()

    st.markdown("---")

    if st.session_state.recovery_step == 1:
        render_step1_username()
    elif st.session_state.recovery_step == 2:
        render_step2_countries()
    elif st.session_state.recovery_step == 3:
        render_step3_new_password()


def render_step1_username():
    """Step 1: Enter username."""
    st.markdown("### Paso 1: Ingrese su usuario")

    with st.form("recovery_username_form"):
        username = st.text_input(
            "Usuario",
            placeholder="Ingrese su nombre de usuario",
            key="recovery_username"
        )

        submit = st.form_submit_button(
            "Continuar",
            use_container_width=True,
            type="primary"
        )

        if submit:
            if not username:
                st.error("Ingrese su nombre de usuario")
            else:
                user = get_user_by_username(username)
                if not user:
                    st.error("Usuario no encontrado")
                elif not user["active"]:
                    st.error("Esta cuenta está desactivada")
                else:
                    # Check if user has security countries configured
                    country_ids = get_user_security_country_ids(user["id"])
                    if len(country_ids) < 5:
                        st.error("Esta cuenta no tiene países de seguridad configurados. Contacte al administrador.")
                    else:
                        # Get countries for recovery (5 correct + 5 decoys = 10 total)
                        countries = get_countries_for_recovery(country_ids, total=10)
                        st.session_state.recovery_user = user
                        st.session_state.recovery_countries = countries
                        st.session_state.recovery_step = 2
                        st.rerun()


def render_step2_countries():
    """Step 2: Select security countries."""
    user = st.session_state.recovery_user
    countries = st.session_state.recovery_countries

    st.markdown("### Paso 2: Verifique su identidad")
    st.markdown(f"Usuario: **{user['username']}**")
    st.markdown("---")

    st.info("""
    Seleccione **al menos 3** de los países que configuró como países de seguridad.
    """)

    with st.form("recovery_countries_form"):
        selected_ids = []

        # Display countries in columns
        cols = st.columns(2)
        for i, country in enumerate(countries):
            with cols[i % 2]:
                if st.checkbox(
                    f"{country['name']}",
                    key=f"recovery_country_{country['id']}"
                ):
                    selected_ids.append(country['id'])

        st.markdown("---")
        st.caption(f"Países seleccionados: {len(selected_ids)}")

        submit = st.form_submit_button(
            "Verificar",
            use_container_width=True,
            type="primary"
        )

        if submit:
            if len(selected_ids) < 3:
                st.warning("Seleccione al menos 3 países")
            else:
                # Verify countries
                if verify_security_countries(user["id"], selected_ids):
                    # Success - reset failed attempts and proceed
                    reset_failed_attempts(user["id"])
                    st.session_state.recovery_step = 3
                    st.rerun()
                else:
                    # Failed attempt
                    attempts = increment_recovery_attempt(user["id"])
                    remaining = 3 - attempts

                    if remaining <= 0:
                        st.error("Demasiados intentos fallidos. La cuenta ha sido bloqueada temporalmente.")
                        clear_recovery_state()
                        st.session_state.show_forgot_password = False
                    else:
                        st.error(f"Países incorrectos. Intentos restantes: {remaining}")
                        # Refresh countries with new random order
                        country_ids = get_user_security_country_ids(user["id"])
                        st.session_state.recovery_countries = get_countries_for_recovery(country_ids, total=10)
                        st.rerun()


def render_step3_new_password():
    """Step 3: Set new password."""
    user = st.session_state.recovery_user

    st.markdown("### Paso 3: Establezca su nueva contraseña")
    st.markdown(f"Usuario: **{user['username']}**")
    st.markdown("---")

    st.success("✅ Identidad verificada correctamente")

    with st.form("new_password_form"):
        new_password = st.text_input(
            "Nueva contraseña",
            type="password",
            placeholder="Ingrese su nueva contraseña"
        )

        confirm_password = st.text_input(
            "Confirmar contraseña",
            type="password",
            placeholder="Confirme su nueva contraseña"
        )

        st.markdown("---")

        submit = st.form_submit_button(
            "Cambiar Contraseña",
            use_container_width=True,
            type="primary"
        )

        if submit:
            if not new_password or not confirm_password:
                st.error("Complete ambos campos")
            elif len(new_password) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres")
            elif new_password != confirm_password:
                st.error("Las contraseñas no coinciden")
            else:
                try:
                    reset_password(user["id"], new_password)
                    st.success("✅ Contraseña cambiada exitosamente")
                    st.info("Ahora puede iniciar sesión con su nueva contraseña")

                    # Clear recovery state and redirect
                    clear_recovery_state()
                    st.session_state.show_forgot_password = False
                    st.session_state.password_reset_success = True

                except AuthServiceError as e:
                    st.error(f"Error: {str(e)}")

    # Button outside the form
    if st.session_state.get("password_reset_success", False):
        if st.button("Ir a Iniciar Sesión", type="primary", use_container_width=True):
            st.session_state.password_reset_success = False
            st.rerun()


def clear_recovery_state():
    """Clear all recovery-related session state."""
    keys_to_clear = [
        "recovery_step",
        "recovery_user",
        "recovery_countries"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
