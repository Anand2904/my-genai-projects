# 02_Student_Dashboard/grade_app.py
import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Student Scorecard Dashboard",
    page_icon="🏫",
    layout="wide"
)

# 2. Colorful & High-Contrast School Environment CSS
def set_school_background():
    st.markdown(
        """
        <style>
        /* Colorful School Library background with a rich dark-indigo overlay for contrast */
        .stApp {
            background-image: linear-gradient(135deg, rgba(15, 23, 42, 0.80), rgba(30, 27, 75, 0.85)), 
                              url("https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1920&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        /* Colorful Hero Header Banner */
        .hero-banner {
            background: linear-gradient(90deg, #FF6B6B 0%, #FFD166 50%, #06D6A0 100%);
            padding: 3px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }
        .hero-content {
            background: rgba(15, 23, 42, 0.92);
            padding: 22px 30px;
            border-radius: 14px;
            text-align: center;
        }
        .hero-title {
            color: #FFFFFF !important;
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 0 2px 10px rgba(255, 209, 102, 0.3);
        }
        .hero-subtitle {
            color: #FFD166 !important;
            font-size: 1.1rem;
            margin-top: 8px;
            font-weight: 500;
        }

        /* Section Subheaders */
        .section-header {
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.2), rgba(124, 58, 237, 0.05));
            border-left: 5px solid #38BDF8;
            padding: 10px 18px;
            border-radius: 8px;
            color: #FFFFFF !important;
            font-size: 1.35rem;
            font-weight: 700;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        /* High-Contrast Form & Metric Cards */
        div[data-testid="stForm"] {
            background: rgba(30, 41, 59, 0.92);
            padding: 24px;
            border-radius: 16px;
            border: 2px solid #38BDF8;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            padding: 18px;
            border-radius: 14px;
            border-left: 6px solid #F59E0B;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
        }

        /* Make Metric Labels and Values Pop */
        div[data-testid="stMetricLabel"] p {
            color: #38BDF8 !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }
        div[data-testid="stMetricValue"] {
            color: #FFD166 !important;
            font-weight: 800 !important;
        }
        div[data-testid="stMetricDelta"] {
            color: #06D6A0 !important;
            font-weight: 600 !important;
        }

        /* Colorful Status Badge */
        .status-badge {
            background: linear-gradient(90deg, #2563EB, #7C3AED);
            color: #FFFFFF;
            padding: 12px 20px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1.05rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_school_background()

# 3. Constants & Grading Scale
SUBJECTS = [
    "Tamil",
    "English",
    "Maths",
    "Physics",
    "Chemistry",
    "Informatics Practices"
]

def calculate_grade(mark):
    """Returns letter grade based on inclusive boundaries (0-100)."""
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "E"

# 4. Initialize Session State so student data survives reruns
if "students" not in st.session_state:
    st.session_state.students = []

# --- Main Page Header ---
st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-content">
            <h1 class="hero-title">🏫 TI School Student Scorecard & Dashboard</h1>
            <p class="hero-subtitle">✨ Enter student marks across all 6 subjects to generate instant scorecards & class rankings ✨</p>
        </div>
    </div>
    <div class="status-badge">
        🎓 Currently storing <b>{len(st.session_state.students)}</b> student(s) in active session memory.
    </div>
    """,
    unsafe_allow_html=True
)

# --- STEP 2: Student Entry Form ---
st.markdown('<div class="section-header">📝 Add New Student Scorecard</div>', unsafe_allow_html=True)

with st.form("student_entry_form", clear_on_submit=True):
    student_name = st.text_input("👤 Student Full Name", placeholder="e.g., Karthik Raja")
    
    st.markdown("##### 📚 Drag Sliders to Enter Subject Marks (0 to 100)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tamil_mark = st.slider("Tamil", min_value=0, max_value=100, value=85, step=1)
        physics_mark = st.slider("Physics", min_value=0, max_value=100, value=85, step=1)
    with col2:
        english_mark = st.slider("English", min_value=0, max_value=100, value=85, step=1)
        chemistry_mark = st.slider("Chemistry", min_value=0, max_value=100, value=85, step=1)
    with col3:
        maths_mark = st.slider("Maths", min_value=0, max_value=100, value=85, step=1)
        ip_mark = st.slider("Informatics Practices", min_value=0, max_value=100, value=85, step=1)
        
    submitted = st.form_submit_button("➕ Add Student Scorecard", use_container_width=True)
    
if submitted:
    clean_name = student_name.strip()
    subject_marks = {
        "Tamil": tamil_mark,
        "English": english_mark,
        "Maths": maths_mark,
        "Physics": physics_mark,
        "Chemistry": chemistry_mark,
        "Informatics Practices": ip_mark
    }
    
    if not clean_name:
        st.error("⚠️ Student name cannot be empty! Please enter a valid name.")
    elif any(m < 0 or m > 100 for m in subject_marks.values()):
        st.error("⚠️ Invalid marks! All subject marks must be strictly between 0 and 100.")
    else:
        marks_list = list(subject_marks.values())
        student_avg = round(sum(marks_list) / len(marks_list), 2)
        student_highest = max(marks_list)
        student_lowest = min(marks_list)
        overall_grade = calculate_grade(student_avg)
        
        new_student = {
            "Name": clean_name,
            "raw_marks": subject_marks,
            "Tamil": f"{tamil_mark:.1f} ({calculate_grade(tamil_mark)})",
            "English": f"{english_mark:.1f} ({calculate_grade(english_mark)})",
            "Maths": f"{maths_mark:.1f} ({calculate_grade(maths_mark)})",
            "Physics": f"{physics_mark:.1f} ({calculate_grade(physics_mark)})",
            "Chemistry": f"{chemistry_mark:.1f} ({calculate_grade(chemistry_mark)})",
            "Informatics Practices": f"{ip_mark:.1f} ({calculate_grade(ip_mark)})",
            "Student Avg": student_avg,
            "Student Highest": student_highest,
            "Student Lowest": student_lowest,
            "Overall Grade": overall_grade
        }
        
        st.session_state.students.append(new_student)
        st.rerun()

# --- STEP 3: Results Table & Class Analytics ---
if not st.session_state.students:
    st.warning("👆 No students added yet. Use the form above to add your first student scorecard!")
else:
    # 1. Overall Class Figures (Metrics)
    st.markdown('<div class="section-header">🏆 Overall Class Performance Metrics</div>', unsafe_allow_html=True)
    
    all_student_avgs = [s["Student Avg"] for s in st.session_state.students]
    class_avg = round(sum(all_student_avgs) / len(all_student_avgs), 2)
    
    # Find student with highest and lowest overall average
    top_student = max(st.session_state.students, key=lambda s: s["Student Avg"])
    low_student = min(st.session_state.students, key=lambda s: s["Student Avg"])
    
    # Also find the single highest and lowest individual subject mark across the whole class
    all_individual_marks = [
        mark for s in st.session_state.students for mark in s["raw_marks"].values()
    ]
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric(
        label="📊 Class Average",
        value=f"{class_avg}%",
        delta=f"Class Grade: {calculate_grade(class_avg)}"
    )
    m_col2.metric(
        label="🥇 Highest Student Avg",
        value=f"{top_student['Student Avg']}%",
        delta=f"{top_student['Name']} ({top_student['Overall Grade']})"
    )
    m_col3.metric(
        label="📉 Lowest Student Avg",
        value=f"{low_student['Student Avg']}%",
        delta=f"{low_student['Name']} ({low_student['Overall Grade']})"
    )
    m_col4.metric(
        label="🎯 Highest / Lowest Single Mark",
        value=f"{max(all_individual_marks):.1f} / {min(all_individual_marks):.1f}",
        delta=f"Across {len(st.session_state.students) * 6} total entries"
    )

    # 2. All Students Scorecard Table (Includes Average, Highest, Lowest & Grade for each student)
    st.markdown('<div class="section-header">📋 Student Scorecard Table (With Individual Stats)</div>', unsafe_allow_html=True)
    
    display_columns = [
        "Name", "Tamil", "English", "Maths", "Physics", 
        "Chemistry", "Informatics Practices", 
        "Student Avg", "Student Highest", "Student Lowest", "Overall Grade"
    ]
    scorecard_df = pd.DataFrame(st.session_state.students)[display_columns]
    scorecard_df.index = range(1, len(scorecard_df) + 1)  # Start row numbering at 1
    st.dataframe(scorecard_df, use_container_width=True)

    # 3. Subject-Wise Average, Highest, and Lowest Across the Class
    st.markdown('<div class="section-header">📚 Subject-Wise Class Figures (Average, Highest & Lowest per Subject)</div>', unsafe_allow_html=True)
    
    subj_cols = st.columns(3)
    subject_summary_rows = []
    
    for idx, subject in enumerate(SUBJECTS):
        subj_marks = [s["raw_marks"][subject] for s in st.session_state.students]
        subj_avg = round(sum(subj_marks) / len(subj_marks), 2)
        subj_high = max(subj_marks)
        subj_low = min(subj_marks)
        
        # Identify which student got the highest and lowest in this subject
        top_in_subj = next(s["Name"] for s in st.session_state.students if s["raw_marks"][subject] == subj_high)
        low_in_subj = next(s["Name"] for s in st.session_state.students if s["raw_marks"][subject] == subj_low)
        
        # Display as metric cards in a 2x3 grid
        with subj_cols[idx % 3]:
            st.metric(
                label=f"📘 {subject}",
                value=f"Avg: {subj_avg} ({calculate_grade(subj_avg)})",
                delta=f"High: {subj_high:.1f} ({top_in_subj}) | Low: {subj_low:.1f} ({low_in_subj})"
            )
            
        subject_summary_rows.append({
            "Subject": subject,
            "Subject Average": subj_avg,
            "Subject Grade": calculate_grade(subj_avg),
            "Highest Mark": f"{subj_high:.1f} ({top_in_subj})",
            "Lowest Mark": f"{subj_low:.1f} ({low_in_subj})"
        })

    # Clean summary table for Subject-Wise stats
    subj_df = pd.DataFrame(subject_summary_rows)
    subj_df.index = range(1, len(subj_df) + 1)
    st.dataframe(subj_df, use_container_width=True)

    # 4. Option to Clear All Data
    st.markdown("---")
    if st.button("🗑️ Reset / Clear All Student Data"):
        st.session_state.students = []
        st.rerun()