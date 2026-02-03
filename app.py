# ============================================================
# Streamlit App: Live AI Tutor – Multi-Language Syntax Checker
# File: app.py
# ============================================================

import streamlit as st
from src.error_engine import detect_errors
from src.auto_fix import AutoFixer
from src.quality_analyzer import CodeQualityAnalyzer
from src.multi_error_detector import detect_all_errors

# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Live Multi-Language Syntax Error Checker",
    layout="centered"
)

st.title("🧠 Live Multi-Language Syntax Error Checker")

st.write(
    """
This tool acts as an **AI tutor** and detects issues **automatically as you paste or type code**.

✔ Python / Java / C / C++  
✔ ML-based multi-error classification  
✔ Rule-based Python syntax validation  
✔ Clear explanations (why + how to fix)  
✔ Positive feedback for correct code  
"""
)

# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------

if "code" not in st.session_state:
    st.session_state.code = ""

if "show_all_errors" not in st.session_state:
    st.session_state.show_all_errors = False

# ------------------------------------------------------------
# Code Input
# ------------------------------------------------------------

code_input = st.text_area(
    "Paste your code here",
    height=300,
    key="code",
    placeholder="Paste Python / Java / C / C++ code here..."
)

col_upload, col_toggle = st.columns([3, 1])

with col_upload:
    uploaded = st.file_uploader(
        "Or upload a code file",
        type=["py", "java", "c", "cpp"]
    )
    
    if uploaded:
        try:
            st.session_state.code = uploaded.read().decode("utf-8")
            code_input = st.session_state.code
        except Exception:
            st.error("❌ Unable to read uploaded file.")

with col_toggle:
    st.write("")  # Spacing
    show_all = st.checkbox(
        "🔍 Show All Errors",
        value=st.session_state.show_all_errors,
        help="Enable to detect and display all errors in the code (not just the first one)"
    )
    st.session_state.show_all_errors = show_all

# ------------------------------------------------------------
# LIVE DETECTION (NO BUTTON)
# ------------------------------------------------------------

if code_input.strip():
    # Pass filename if file is uploaded (important for Java/C/C++)
    filename = uploaded.name if uploaded else None
    
    # --------------------------------------------------------
    # Multi-Error Detection Mode
    # --------------------------------------------------------
    
    if st.session_state.show_all_errors:
        all_errors = detect_all_errors(code_input, filename)
        
        st.success(f"🗂 Detected Language: **{all_errors['language']}**")
        
        # --------------------------------------------------------
        # NO ERROR CASE (AUTHORITATIVE)
        # --------------------------------------------------------
        
        if all_errors['total_errors'] == 0:
            st.success("✅ No syntax errors detected")
            st.subheader("🧠 AI Tutor Feedback")
            st.write("✔ Your code is syntactically correct.")
            st.write("✔ No corrections are required.")
            error_lines = set()
        else:
            st.error(f"❌ Found **{all_errors['total_errors']} errors** across **{len(all_errors['errors_by_type'])} types**")
            
            # Display errors grouped by type
            st.subheader("🔍 All Detected Errors")
            
            for error_type, errors in all_errors['errors_by_type'].items():
                with st.expander(f"❌ {error_type} ({len(errors)} occurrence{'s' if len(errors) > 1 else ''})", expanded=True):
                    for idx, error in enumerate(errors, 1):
                        st.error(f"**{idx}. Line {error['line']}**: {error['message']}")
                        if error.get('snippet'):
                            st.code(error['snippet'], language=all_errors['language'].lower())
            
            error_lines = set()
            for errors in all_errors['errors_by_type'].values():
                for error in errors:
                    if error.get('line'):
                        error_lines.add(error['line'])
    
    # --------------------------------------------------------
    # Single Error Detection Mode (Original)
    # --------------------------------------------------------
    
    else:
        result = detect_errors(code_input, filename=filename)

        # --------------------------------------------------------
        # Language
        # --------------------------------------------------------

        st.success(f"🗂 Detected Language: **{result['language']}**")

        # --------------------------------------------------------
        # NO ERROR CASE (AUTHORITATIVE)
        # --------------------------------------------------------

        if result["predicted_error"] == "NoError":
            st.success("✅ No syntax errors detected")

            st.subheader("🧠 AI Tutor Feedback")
            st.write("✔ Your code is syntactically correct.")
            st.write("✔ No corrections are required.")

            error_lines = set()

        # --------------------------------------------------------
        # ERROR CASE
        # --------------------------------------------------------

        else:
            st.error(f"❌ Detected Error Type: **{result['predicted_error']}**")

            st.subheader("🧠 AI Tutor Explanation")
            st.write(f"**Why this happened:** {result['tutor']['why']}")
            st.write(f"**How to fix it:** {result['tutor']['fix']}")
            
            # --------------------------------------------------------
            # AUTO-FIX SUGGESTION
            # --------------------------------------------------------
            st.subheader("🔧 Auto-Fix Suggestion")
            fixer = AutoFixer()
            
            # Get line number from rule-based issues if available
            line_num = 0
            if result.get('rule_based_issues'):
                for issue in result['rule_based_issues']:
                    if issue.get('line'):
                        line_num = issue['line'] - 1
                        break
            
            fix_result = fixer.apply_fixes(code_input, result['predicted_error'], line_num, result['language'])
            
            if fix_result['success']:
                st.success("✅ Automatic fix applied!")
                st.code(fix_result['fixed_code'], language=result['language'].lower())
                
                with st.expander("📋 View Changes"):
                    for change in fix_result['changes']:
                        st.write(f"• {change}")
            else:
                st.info("ℹ️ Manual correction recommended for this error type.")

            # ----------------------------------------------------
            # Rule-Based Issues (Python)
            # ----------------------------------------------------

            issues = result.get("rule_based_issues", [])
            error_lines = set()

            if issues:
                st.subheader("⚠️ Detailed Syntax Issues (Python)")
                for i, iss in enumerate(issues, start=1):
                    st.error(f"{i}. {iss.get('type')} (Line {iss.get('line')})")
                    st.write(iss.get("message"))
                    if iss.get("suggestion"):
                        st.info(iss.get("suggestion"))
                    if iss.get("line"):
                        error_lines.add(iss["line"])
            else:
                # Non-Python / ML-only case → highlight entire snippet
                error_lines = set(range(1, len(code_input.splitlines()) + 1))
    
    # --------------------------------------------------------
    # CODE QUALITY ANALYSIS
    # --------------------------------------------------------
    st.subheader("📊 Code Quality Analysis")
    
    try:
        quality = CodeQualityAnalyzer(code_input, result['language'])
        quality_report = quality.analyze()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Quality Score", f"{quality_report['quality_score']}/100")
        with col2:
            st.metric("Code Lines", quality_report['line_counts']['code'])
        with col3:
            complexity = quality_report.get('complexity', 'N/A')
            st.metric("Complexity", complexity)
        
        # Quality suggestions
        if quality_report['suggestions']:
            with st.expander("💡 Quality Suggestions", expanded=False):
                for suggestion in quality_report['suggestions']:
                    st.write(f"• {suggestion}")
        else:
            st.success("✅ Code quality looks good!")
    
    except Exception as e:
        st.info("ℹ️ Quality analysis unavailable for this code snippet.")

    # --------------------------------------------------------
    # Code Display with Highlighting
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("📄 Code with Highlighted Errors")

    lines = code_input.splitlines()
    highlighted_code = []

    for i, line in enumerate(lines, start=1):
        if i in error_lines:
            highlighted_code.append(
                f"<span style='color:red; font-weight:bold;'>❌ {i:03d}: {line}</span>"
            )
        else:
            highlighted_code.append(f"{i:03d}: {line}")

    st.markdown(
        "<pre style='background-color:#f6f8fa; padding:12px; border-radius:6px;'>"
        + "\n".join(highlighted_code)
        + "</pre>",
        unsafe_allow_html=True
    )

else:
    st.info("👆 Paste or upload code to start live analysis.")

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.markdown("---")
st.caption(
    "🔴 Live detection | Hybrid Rule-Based + ML | AI Tutor–Style Feedback | Academic Project"
)
