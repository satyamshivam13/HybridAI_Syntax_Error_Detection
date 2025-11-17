# app.py - Streamlit UI
import streamlit as st
from syntax_checker import detect_all
st.set_page_config(page_title="Syntax Error Checker", layout="centered")
st.title("Syntax Error Checker — Python (MVP)")
st.write("Paste Python code or upload a `.py` file. Detects: MissingColon, UnmatchedBracket, IndentationError, UnclosedQuotes.")
col1, col2 = st.columns([3,1])
with col1:
    code_input = st.text_area("Paste Python code here", height=300, value="""# Try sample:
def hello()
    print("Hi")
""")
with col2:
    uploaded = st.file_uploader("Or upload a .py file", type=['py'])
    if uploaded:
        code_input = uploaded.read().decode('utf-8')
if st.button("Check Syntax"):
    code = code_input or ""
    if not code.strip():
        st.warning("Please paste or upload some Python code.")
    else:
        with st.spinner("Analyzing..."):
            issues = detect_all(code)
        if not issues:
            st.success("No issues found by static checks (for the 4 specified error types).")
        else:
            st.error(f"Found {len(issues)} issue(s).")
            for i, iss in enumerate(issues, start=1):
                st.write(f"### {i}. {iss.get('type')}")
                line = iss.get('line')
                snippet = iss.get('snippet')
                st.write(f"**Line:** {line if line else 'N/A'}")
                if snippet:
                    st.code(snippet, language='python')
                st.write(f"**Message:** {iss.get('message')}")
                if iss.get('suggestion'):
                    st.info(f"Suggestion: {iss.get('suggestion')}")
        st.write("---")
        st.subheader("Original Code (with line numbers)")
        lines = code.splitlines()
        numbered = "\n".join(f"{i+1:3d}: {ln}" for i,ln in enumerate(lines))
        st.text_area("Code with numbers", value=numbered, height=300)