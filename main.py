"""
Agency Performance Tracker - Main Application
Streamlit application for tracking agency manager performance.
"""
import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Agency Performance Tracker",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import services
from services.auth_service import needs_security_setup, ensure_admin_exists

# Import UI modules
from ui.sidebar import render_sidebar
from ui import (
    agency_setup, agency_list, targets_setup,
    monthly_review, dashboard, login,
    first_login_security, forgot_password, user_management
)


def init_system():
    """Initialize system requirements."""
    # Ensure admin user exists
    ensure_admin_exists()


def main():
    """Main application entry point."""

    # Initialize system on first run
    if "system_initialized" not in st.session_state:
        init_system()
        st.session_state.system_initialized = True

    # Check if showing forgot password
    if st.session_state.get("show_forgot_password", False):
        forgot_password.render()
        return

    # Check authentication
    if not login.is_authenticated():
        login.render()
        return

    # Get current user
    current_user = login.get_current_user()

    # Check if user needs to configure security countries
    if needs_security_setup(current_user["id"]):
        first_login_security.render(current_user)
        return

    # User is authenticated and has security configured
    # Render sidebar and get current page
    current_page = render_sidebar(current_user)

    # Route to appropriate page
    if current_page == "dashboard":
        dashboard.render(current_user)

    elif current_page == "agency_list":
        agency_list.render(current_user)

    elif current_page == "agency_setup":
        agency_setup.render(current_user)

    elif current_page == "targets_setup":
        targets_setup.render(current_user)

    elif current_page == "monthly_review":
        monthly_review.render(current_user)

    elif current_page == "user_management":
        user_management.render(current_user)

    else:
        st.error(f"Página no encontrada: {current_page}")


if __name__ == "__main__":
    main()
