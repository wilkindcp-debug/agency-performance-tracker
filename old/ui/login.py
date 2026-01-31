"""
Login UI - User authentication screen.
"""
import streamlit as st
from services.auth_service import authenticate_user, AuthServiceError


def render():
    """Render the login page."""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🏦 Agency Tracker")
        st.markdown("### Iniciar Sesión")
        st.markdown("---")

        with st.form("login_form"):
            username = st.text_input(
                "Usuario",
                placeholder="Ingrese su usuario",
                key="login_username"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingrese su contraseña",
                key="login_password"
            )

            st.markdown("")

            submit = st.form_submit_button(
                "🔓 Iniciar Sesión",
                use_container_width=True,
                type="primary"
            )

            if submit:
                if not username or not password:
                    st.error("Ingrese usuario y contraseña")
                else:
                    try:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos")
                    except AuthServiceError as e:
                        st.error(str(e))

        st.markdown("---")

        # Forgot password link
        if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
            st.session_state.show_forgot_password = True
            st.rerun()

        st.markdown("---")
        st.caption("© 2026 Agency Performance Tracker")


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False) and st.session_state.get("user") is not None


def get_current_user():
    """Get the current authenticated user."""
    return st.session_state.get("user")


def logout():
    """Log out the current user."""
    if "user" in st.session_state:
        del st.session_state.user
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    if "current_page" in st.session_state:
        del st.session_state.current_page
