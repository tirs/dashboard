import streamlit as st
from streamlit_option_menu import option_menu


def render_advanced_sidebar():
    """
    Renders an advanced sidebar navigation with user profile section,
    organized menu categories, and quick actions.
    
    Returns:
        str: The selected menu option
    """
    with st.sidebar:
        # Top branding section
        st.markdown("""
        <div style='text-align: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #30363D;'>
            <h1 style='margin: 0; font-size: 1.8rem; color: #1F77B4;'>📊</h1>
            <h2 style='margin: 0.5rem 0 0 0; font-size: 1.3rem;'>Analytics</h2>
            <p style='margin: 0.25rem 0; font-size: 0.85rem; color: #8B949E;'>Dashboard Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User profile section
        render_user_profile_card()
        
        st.markdown("<div style='margin-top: 1.5rem; margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        
        # Main navigation menu
        selected = render_navigation_menu()
        
        # Footer section with quick info
        render_sidebar_footer()
        
        return selected


def render_user_profile_card():
    """Displays current user profile information in the sidebar."""
    username = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'user').upper()
    
    # Determine role color
    role_colors = {
        'ADMIN': '#DC3545',
        'MANAGER': '#FFC107',
        'USER': '#58A6FF'
    }
    role_color = role_colors.get(user_role, '#58A6FF')
    
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #161B22 0%, #0E1117 100%);
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
    '>
        <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
            <div style='
                width: 40px;
                height: 40px;
                background-color: {role_color};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 0.8rem;
                font-weight: bold;
                color: white;
            '>
                {username[0].upper()}
            </div>
            <div>
                <p style='margin: 0; color: #F0F6FC; font-weight: 600; font-size: 0.95rem;'>{username}</p>
                <p style='margin: 0.25rem 0 0 0; color: {role_color}; font-size: 0.8rem; font-weight: 500;'>{user_role}</p>
            </div>
        </div>
        <div style='padding-top: 0.8rem; border-top: 1px solid #30363D;'>
            <p style='margin: 0; color: #8B949E; font-size: 0.75rem;'>Status: <span style="color: #2CA02C;">Active</span></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_navigation_menu():
    """Renders the main navigation menu organized by sections."""
    
    # Define menu structure
    menu_sections = [
        ("🏠 HOME", [
            ("Home", "Home"),
        ]),
        ("📈 ANALYTICS", [
            ("Analytics Dashboard", "Analytics"),
            ("Data Browser", "Data Browser"),
        ]),
        ("📋 REPORTING", [
            ("Reports", "Reports"),
        ]),
        ("🔧 ADMINISTRATION", [
            ("User Management", "User Management"),
            ("Settings", "Settings"),
        ]),
        ("👤 ACCOUNT", [
            ("Profile", "Profile"),
        ]),
    ]
    
    # Build flat menu with icons
    all_options = []
    all_icons = []
    section_indices = {}
    
    for section_name, items in menu_sections:
        section_start = len(all_options)
        section_indices[section_name] = section_start
        
        # Add section header (disabled)
        for item_name, item_key in items:
            all_options.append(item_name)
            
            # Assign icons based on item
            if "Home" in item_name:
                all_icons.append("house")
            elif "Dashboard" in item_name:
                all_icons.append("bar-chart")
            elif "Browser" in item_name:
                all_icons.append("database")
            elif "Reports" in item_name:
                all_icons.append("file-text")
            elif "User Management" in item_name:
                all_icons.append("people")
            elif "Settings" in item_name:
                all_icons.append("gear")
            elif "Profile" in item_name:
                all_icons.append("person")
            else:
                all_icons.append("arrow-right")
    
    # Add logout option
    all_options.append("🔓 Logout")
    all_icons.append("box-arrow-right")
    
    selected = option_menu(
        menu_title=None,
        options=all_options,
        icons=all_icons,
        menu_icon="menu-button-wide",
        default_index=0,
        styles={
            "container": {
                "padding": "0.5px",
                "background-color": "#0E1117",
                "border-radius": "8px"
            },
            "icon": {
                "color": "#8B949E",
                "font-size": "16px",
                "margin-right": "8px"
            },
            "nav-link": {
                "font-size": "0.95rem",
                "text-align": "left",
                "margin": "0.3rem 0",
                "--hover-color": "#262730",
                "color": "#E0E0E0",
                "border-radius": "6px",
                "padding": "0.6rem 0.8rem",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background-color": "#1F77B4",
                "color": "#FFFFFF",
                "font-weight": "600",
                "border-left": "3px solid #58A6FF",
                "padding-left": "0.5rem"
            },
        }
    )
    
    # Extract the actual selection (remove emoji prefix if logout)
    if "Logout" in selected:
        return "Logout"
    
    # Map display names back to actual page names
    menu_map = {
        "Home": "Home",
        "Analytics Dashboard": "Analytics",
        "Data Browser": "Data Browser",
        "Reports": "Reports",
        "User Management": "User Management",
        "Settings": "Settings",
        "Profile": "Profile",
    }
    
    # Extract the clean name from the selected option
    for display_name, actual_name in menu_map.items():
        if display_name in selected:
            return actual_name
    
    return "Analytics"


def render_sidebar_footer():
    """Renders footer section with additional info and quick stats."""
    st.markdown("""
    <div style='
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 1rem;
        border-top: 1px solid #30363D;
        background-color: rgba(14, 17, 23, 0.95);
        max-width: 18rem;
        box-sizing: border-box;
    '>
        <div style='text-align: center; font-size: 0.75rem; color: #8B949E;'>
            <p style='margin: 0; padding-bottom: 0.5rem;'>Dashboard v1.0</p>
            <p style='margin: 0; padding-top: 0.5rem; border-top: 1px solid #30363D;'>
                <span style='color: #2CA02C;'>●</span> System Active
            </p>
        </div>
    </div>
    <div style='height: 120px;'></div>
    """, unsafe_allow_html=True)