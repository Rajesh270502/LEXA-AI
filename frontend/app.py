import streamlit as st
import httpx

# Configuration
# FIX: If hitting /register directly fails, change this string to:
# "http://127.0.0.1:8000/api" OR "http://127.0.0.1:8000/api/v1"
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Legal Contract Assistant", layout="wide")
st.title("AI Legal Contract Assistant & Risk Assessor")

# Initialize Session State variables to keep track of logins and files
if "token" not in st.session_state:
    st.session_state.token = None
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# Sidebar: Authentication Section
st.sidebar.header("User Session")
if not st.session_state.token:
    auth_mode = st.sidebar.radio("Choose Action:", ["Login", "Register"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button(auth_mode):
        if username and password:
            try:
                if auth_mode == "Register":
                    # Note: If this still gives an error, add a trailing slash: f"{BACKEND_URL}/register/"
                    response = httpx.post(f"{BACKEND_URL}/register", json={"username": username, "password": password})
                    
                    if response.status_code in [200, 201]:
                        st.sidebar.success("Account created successfully! Please switch to Login.")
                    else:
                        # Defensive check: if backend returns HTML text instead of JSON, print text instead of crashing
                        try:
                            error_detail = response.json().get('detail', 'Unknown error')
                        except Exception:
                            error_detail = f"Server returned status {response.status_code}. (Route might be wrong or missing a prefix like /api)"
                        st.sidebar.error(f"Registration failed: {error_detail}")
                
                elif auth_mode == "Login":
                    # Swagger OAuth2 flow uses form data format
                    login_data = {"grant_type": "password", "username": username, "password": password}
                    response = httpx.post(f"{BACKEND_URL}/token", data=login_data)
                    
                    if response.status_code == 200:
                        st.session_state.token = response.json()["access_token"]
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.sidebar.error("Invalid username or password.")
            except Exception as e:
                st.sidebar.error(f"Cannot connect to backend: {e}")
        else:
            st.sidebar.warning("Please fill in both fields.")
else:
    st.sidebar.success(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.document_id = None
        st.session_state.username = None
        st.rerun()

# Main Application Window (Requires Login)
if not st.session_state.token:
    st.info("Please register or log in using the sidebar to unlock the AI Contract workspace.")
else:
    # App split layout: Upload & Extract on left, Conversational Chat on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("1. Upload Contract Document")
        uploaded_file = st.file_uploader("Upload a Contract (PDF or DOCX)", type=["pdf", "docx"])
        
        if uploaded_file is not None and st.button("Process & Index Contract"):
            with st.spinner("Extracting text, building embeddings, and running AI risk profiling..."):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                try:
                    response = httpx.post(f"{BACKEND_URL}/upload", headers=headers, files=files, timeout=60.0)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.document_id = result.get("document_id")
                        st.success(f"Contract safely vectorized! Document ID: {st.session_state.document_id}")
                        
                        # Display AI Structured Extraction summary if available in response
                        if "analysis" in result:
                            st.subheader("Structural Risk Extraction Summary")
                            analysis = result["analysis"]
                            st.metric(label="Contract Overall Risk Score", value=f"{analysis.get('risk_score', 0)}/100")
                            st.text_area("Effective Date", analysis.get("effective_date"), disabled=True)
                            st.text_area("Governing Law", analysis.get("governing_law"), disabled=True)
                            st.text_area("Identified High Risks", analysis.get("high_risks"), disabled=True)
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error talking to server: {e}")

    with col2:
        st.header("2. Semantic Legal Query Panel")
        if not st.session_state.document_id:
            st.warning("Upload and process a document on the left panel to begin asking contextual questions.")
        else:
            query = st.text_input("Ask a question about this agreement:")
            if query and st.button("Ask AI Assistant"):
                with st.spinner("Searching vectors and synthesizing legal response..."):
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    try:
                        response = httpx.post(
                            f"{BACKEND_URL}/chat/{st.session_state.document_id}?query={query}", 
                            headers=headers,
                            timeout=45.0
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.subheader(" AI Answer:")
                            st.write(data.get("answer"))
                            
                            with st.expander("View Source Context Chunks Used"):
                                for idx, chunk in enumerate(data.get("source_chunks", [])):
                                    st.markdown(f"**Chunk {idx+1}:** {chunk}")
                                    st.markdown("---")
                        else:
                            st.error(f"Query failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error handling request: {e}")