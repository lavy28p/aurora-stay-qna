import streamlit as st
import requests

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BACKEND_URL = "http://localhost:7860"

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Aurora Stays - Policy Assistant",
    page_icon="🏨",
    layout="wide"
)

# ---------------------------------------------------------
# Sidebar  -  Model parameters
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parameters")

    k = st.slider(
        "k (chunks to retrieve)",
        min_value=1,
        max_value=10,
        value=3,  # Optimized default depth to satisfy multi-document retrieval completeness
        help="Number of relevant chunks fetched from the vector store."
    )

    temperature = st.sidebar.hidden = 0.0  # Force locked deterministic grounding natively

    max_tokens = st.slider(
        "Max tokens",
        min_value=64,
        max_value=2048,
        value=512,
        step=64,
        help="Maximum number of tokens in the generated answer."
    )

# ---------------------------------------------------------
# Main area
# ---------------------------------------------------------
st.title("🏨 Aurora Stays Guest Policy Engine")
st.write("Ask our intelligent assistant any question regarding property check-in windows, pet guidelines, or stay fees.")

# ---------------------------------------------------------
# Response type selection (two options only)
# ---------------------------------------------------------
response_type = st.radio(
    "Response mode",
    ["Answer only", "Answer + Relevant Chunks"],
    horizontal=True
)

# ---------------------------------------------------------
# Query input (Fully localized to hotel operations)
# ---------------------------------------------------------
query = st.text_input(
    "Your question",
    placeholder="e.g., What are the nightly fees and rules for bringing a dog?"
)

# ---------------------------------------------------------
# Submit Payload Operations
# ---------------------------------------------------------
if st.button("Submit", type="primary"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        # Pick endpoint matching your Flask API router mapping
        if response_type == "Answer only":
            endpoint = "/v1/answer"
        else:
            endpoint = "/v1/answer_with_relevant_chunks"

        payload = {
            "query": query,
            "k": k,
            "temperature": 0.0,
            "max_tokens": max_tokens
        }

        try:
            with st.spinner("Analyzing property guidelines..."):
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json=payload
                )

            if response.status_code == 200:
                result = response.json()

                if response_type == "Answer only":
                    st.subheader("Answer")
                    st.write(result["answer"])
                else:
                    st.subheader("Answer")
                    st.write(result["answer"])

                    st.subheader("Relevant Chunks")
                    for i, chunk in enumerate(result["relevant_chunks"], start=1):
                        with st.expander(f"Chunk {i}"):
                            st.write(chunk)
            else:
                st.error(f"RAG API returned an operational error. Status code: {response.status_code}")
        except requests.exceptions.RequestException:
            st.error("Unable to connect to the RAG API backend. Please ensure the Flask app server is active on port 7860.")
