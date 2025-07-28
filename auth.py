#auth.py
import os
import json
import bcrypt
import streamlit as st
import re
from welcome import welcome_screen  # only if welcome screen is in a separate file

USER_DB_PATH = "users.json"

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[\W_]", password):  # special character
        return False
    return True

def password_requirements(password):
    return {
        "At least 8 characters": len(password) >= 8,
        "Contains an uppercase letter": bool(re.search(r"[A-Z]", password)),
        "Contains a lowercase letter": bool(re.search(r"[a-z]", password)),
        "Contains a digit": bool(re.search(r"[0-9]", password)),
        "Contains a special character": bool(re.search(r"[\W_]", password)),
    }


def load_users():
    if not os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, "w") as f:
            json.dump({}, f)
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

def signup(username, password):
    users = load_users()
    if username in users:
        return False
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {"password": hashed_password, "history": []}
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    if username in users:
        stored_hash = users[username]["password"].encode()
        return bcrypt.checkpw(password.encode(), stored_hash)
    return False

def reset_password(username, new_password):
    users = load_users()
    if username in users:
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        users[username]["password"] = hashed_password
        save_users(users)
        return True
    return False

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "show_welcome" not in st.session_state:
        st.session_state.show_welcome = True
    if "username" not in st.session_state:
        st.session_state.username = None
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if "forgot_password" not in st.session_state:
        st.session_state.forgot_password = False

def auth_flow():
    init_session_state()

    # Show welcome screen first
    if not st.session_state.authenticated:
        if st.session_state.show_welcome:
            welcome_screen()
            if st.button("Continue to Login ➡️"):
                st.session_state.show_welcome = False
                st.rerun()
            st.stop()

    if not st.session_state.authenticated and st.session_state.forgot_password:
        show_forgot_password_form()
        st.stop()

    # Show login/signup page
    if not st.session_state.authenticated:
        login_page()
        st.stop()

def login_page():
    st.markdown("<h2 style='text-align: center;'>🔐 Welcome to GPT Shield</h2>", unsafe_allow_html=True)
    st.markdown("##")

    mode = st.radio("Select Mode", ["Login", "Sign Up"], horizontal=True)

    if mode == "Sign Up":
        st.markdown("""
            <style>
            .pw-rules {
                font-size: 13px;
                text-align: left;
                margin-bottom: 5px;
                margin-top: 10px;
                color: #ccc;
                padding-left: 10px;
            }
            .pw-rule {
                margin: 0;
                padding: 0;
            }
            </style>
        """, unsafe_allow_html=True)

        password = st.session_state.get("temp_password", "")
        reqs = password_requirements(password)

        st.markdown("<div class='pw-rules'><b>Password must contain:</b><ul>", unsafe_allow_html=True)
        for rule in reqs.keys():
            st.markdown(f"<li class='pw-rule'>{rule}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

    with st.form("auth_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.session_state.temp_password = password


        if mode == "Sign Up":
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            submit_btn = st.form_submit_button("Create Account")

            if submit_btn:
                if not username or not password or not confirm_password:
                    st.warning("⚠️ Please fill out all fields.")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match.")
                elif not is_strong_password(password):
                    st.warning("⚠️ Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.")
                elif signup(username, password):
                    st.success("✅ Account created! Please log in.")
                    st.rerun()

                else:
                    st.error("❌ Username already exists.")
        else:
            submit_btn = st.form_submit_button("Login")

            if submit_btn:
                if login(username, password):
                    st.success("✅ Login successful!")
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Forgot Password?"):
            st.session_state.forgot_password = True
            st.rerun()

    with col2:
        st.markdown("<p style='text-align: right;'>New here? Sign up above.</p>", unsafe_allow_html=True)

def show_forgot_password_form():
    st.markdown("## 🔒 Reset Your Password")
    username = st.text_input("Username")
    new_pass = st.text_input("New Password", type="password")
    confirm_pass = st.text_input("Confirm New Password", type="password")

    if st.button("Reset Password"):
        if not username or not new_pass or not confirm_pass:
            st.warning("⚠️ Please fill out all fields.")
        elif new_pass != confirm_pass:
            st.error("❌ Passwords do not match.")
        elif not is_strong_password(new_pass):
            st.warning("⚠️ Password must be at least 8 characters and contain uppercase, lowercase, digit, and special character.")
        elif reset_password(username, new_pass):
            st.success("✅ Password reset successful. You can now log in.")
            st.session_state.forgot_password = False
            st.rerun()
        else:
            st.error("❌ Username not found.")
