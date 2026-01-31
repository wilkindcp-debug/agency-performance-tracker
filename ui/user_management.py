"""
User Management UI - Admin only screen for managing users.
"""
import streamlit as st
from services.auth_service import (
    create_user,
    list_users,
    toggle_user_active,
    update_user_role,
    reset_password,
    AuthServiceError
)
from services.access_service import (
    get_assigned_agency_ids,
    set_user_agencies,
    AccessServiceError
)
from services.agency_service import list_agencies


def render(current_user):
    """
    Render user management page.
    Only accessible by ADMIN users.

    Args:
        current_user: Current authenticated user dict
    """
    if current_user.get("role") != "ADMIN":
        st.error("⛔ Acceso denegado. Esta página es solo para administradores.")
        return

    st.header("👥 Gestión de Usuarios")
    st.markdown("Administre los usuarios del sistema.")

    # Tabs for different actions
    tab1, tab2 = st.tabs(["📋 Lista de Usuarios", "➕ Crear Usuario"])

    with tab1:
        render_user_list(current_user)

    with tab2:
        render_create_user()


def render_user_list(current_user):
    """Render the list of users."""
    users = list_users()
    agencies = list_agencies(active_only=True)

    if not users:
        st.info("No hay usuarios registrados")
        return

    # User selection for editing
    st.markdown("### Usuarios del Sistema")

    for user in users:
        with st.expander(f"{'🟢' if user['active'] else '🔴'} {user['username']} ({user['role']})", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.markdown(f"**Usuario:** {user['username']}")
                st.markdown(f"**Rol:** {user['role']}")
                st.markdown(f"**Estado:** {'Activo' if user['active'] else 'Inactivo'}")
                st.markdown(f"**Seguridad:** {'Configurada' if user['has_security'] else 'Pendiente'}")

            with col2:
                if user['role'] == 'NORMAL':
                    st.markdown("**Agencias asignadas:**")
                    assigned_ids = get_assigned_agency_ids(user['id'])

                    # Multi-select for agencies
                    agency_options = {a['id']: f"{a['name']} ({a['city']})" for a in agencies}

                    new_assignments = st.multiselect(
                        "Agencias",
                        options=list(agency_options.keys()),
                        default=assigned_ids,
                        format_func=lambda x: agency_options.get(x, str(x)),
                        key=f"agencies_{user['id']}",
                        label_visibility="collapsed"
                    )

                    if st.button("💾 Guardar Agencias", key=f"save_agencies_{user['id']}"):
                        try:
                            set_user_agencies(user['id'], new_assignments)
                            st.success("Agencias actualizadas")
                            st.rerun()
                        except AccessServiceError as e:
                            st.error(str(e))
                else:
                    st.info("ADMIN tiene acceso a todas las agencias")

            with col3:
                # Don't allow editing self
                if user['id'] != current_user['id']:
                    # Toggle active
                    if user['active']:
                        if st.button("🔴 Desactivar", key=f"deactivate_{user['id']}"):
                            toggle_user_active(user['id'], False)
                            st.rerun()
                    else:
                        if st.button("🟢 Activar", key=f"activate_{user['id']}"):
                            toggle_user_active(user['id'], True)
                            st.rerun()

                    # Change role
                    new_role = "NORMAL" if user['role'] == "ADMIN" else "ADMIN"
                    if st.button(f"🔄 Cambiar a {new_role}", key=f"role_{user['id']}"):
                        update_user_role(user['id'], new_role)
                        st.rerun()

                    # Reset password
                    st.markdown("---")
                    new_pass = st.text_input(
                        "Nueva contraseña",
                        type="password",
                        key=f"newpass_{user['id']}"
                    )
                    if st.button("🔑 Restablecer", key=f"reset_{user['id']}"):
                        if new_pass and len(new_pass) >= 8:
                            reset_password(user['id'], new_pass)
                            st.success("Contraseña restablecida")
                        else:
                            st.error("Mínimo 8 caracteres")
                else:
                    st.info("No puede editar su propia cuenta aquí")


def render_create_user():
    """Render the create user form."""
    st.markdown("### Crear Nuevo Usuario")

    agencies = list_agencies(active_only=True)

    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Nombre de usuario *",
                placeholder="Ej: jperez"
            )

            password = st.text_input(
                "Contraseña *",
                type="password",
                placeholder="Mínimo 8 caracteres"
            )

        with col2:
            role = st.selectbox(
                "Rol *",
                options=["NORMAL", "ADMIN"],
                index=0
            )

            active = st.checkbox("Usuario activo", value=True)

        # Agency assignment for NORMAL users
        st.markdown("---")
        st.markdown("**Asignar agencias** (solo aplica a usuarios NORMAL)")

        agency_options = {a['id']: f"{a['name']} ({a['city']})" for a in agencies}
        selected_agencies = st.multiselect(
            "Agencias",
            options=list(agency_options.keys()),
            format_func=lambda x: agency_options.get(x, str(x)),
            label_visibility="collapsed"
        )

        st.markdown("---")

        if st.form_submit_button("✅ Crear Usuario", type="primary", use_container_width=True):
            # Validation
            errors = []
            if not username or not username.strip():
                errors.append("El nombre de usuario es requerido")
            if not password or len(password) < 8:
                errors.append("La contraseña debe tener al menos 8 caracteres")
            if role == "NORMAL" and not selected_agencies:
                errors.append("Debe asignar al menos una agencia a usuarios NORMAL")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    user = create_user(
                        username=username.strip(),
                        password=password,
                        role=role,
                        active=active
                    )

                    # Assign agencies if NORMAL user
                    if role == "NORMAL" and selected_agencies:
                        set_user_agencies(user.id, selected_agencies)

                    st.success(f"✅ Usuario '{username}' creado exitosamente")
                    st.info("El usuario deberá configurar sus países de seguridad en su primer inicio de sesión")

                except AuthServiceError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Error inesperado: {str(e)}")
