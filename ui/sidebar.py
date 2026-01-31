"""
Sidebar navigation component for Streamlit app.
"""
import streamlit as st
from typing import Dict, Any


# Page definitions - base pages available to all users
PAGES_BASE = {
    "dashboard": {
        "title": "Dashboard",
        "icon": "📊",
        "admin_only": False
    },
    "agency_list": {
        "title": "Agencias",
        "icon": "🏢",
        "admin_only": False
    },
    "targets_setup": {
        "title": "Objetivos 2026",
        "icon": "🎯",
        "admin_only": False
    },
    "monthly_review": {
        "title": "Seguimiento Mensual",
        "icon": "📝",
        "admin_only": False
    }
}

# Admin-only pages
PAGES_ADMIN = {
    "agency_setup": {
        "title": "Crear Agencia",
        "icon": "➕",
        "admin_only": True
    },
    "user_management": {
        "title": "Gestión Usuarios",
        "icon": "👥",
        "admin_only": True
    }
}


def get_pages_for_user(user: Dict[str, Any]) -> dict:
    """
    Get pages available for the current user based on role.

    Args:
        user: Current user dict

    Returns:
        Dict of available pages
    """
    pages = dict(PAGES_BASE)

    if user and user.get("role") == "ADMIN":
        pages.update(PAGES_ADMIN)

    return pages


def render_sidebar(user: Dict[str, Any]) -> str:
    """
    Render the sidebar navigation.

    Args:
        user: Current authenticated user dict

    Returns:
        Selected page key
    """
    with st.sidebar:
        st.title("🏦 Agency Tracker")

        # User info
        if user:
            role_badge = "🔑 ADMIN" if user.get("role") == "ADMIN" else "👤 NORMAL"
            st.markdown(f"**{user.get('username')}** {role_badge}")

        st.markdown("---")

        # Navigation
        st.subheader("Navegación")

        # Get available pages for this user
        available_pages = get_pages_for_user(user)

        # Initialize page state if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        # Ensure current page is valid for this user
        if st.session_state.current_page not in available_pages:
            st.session_state.current_page = "dashboard"

        # Create navigation buttons
        for page_key, page_info in available_pages.items():
            # Highlight current page
            is_current = st.session_state.current_page == page_key
            button_type = "primary" if is_current else "secondary"

            if st.button(
                f"{page_info['icon']} {page_info['title']}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

        # Footer info
        st.caption("Agency Performance Tracker v1.0")
        st.caption("© 2026 - Seguimiento de Jefes de Agencia")

    return st.session_state.current_page


def set_page(page_key: str) -> None:
    """
    Programmatically set the current page.

    Args:
        page_key: The page key to navigate to
    """
    st.session_state.current_page = page_key
