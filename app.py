
import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io
import os

# Define the data file path
DATA_FILE = "student_data.csv"

# Function to load data from CSV
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            'Student_Name',
            'Class', # Added Class column
            'Subject',
            'Assessment_1',
            'Assessment_2',
            'Exam_1',
            'Exam_2',
            'Final_Grade'
        ])

# Function to save data to CSV
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Load data at the start of the application
student_data_df = load_data()

# Store DataFrame in session state for persistence across reruns
if 'student_data_df' not in st.session_state:
    st.session_state['student_data_df'] = student_data_df

# Define the grading function
def calculate_final_grade(row):
    """
    Calculates the final grade for a student based on assessment and exam scores.
    Assumes assessments contribute 40% and exams contribute 60% to the final grade.
    Handles missing scores by treating them as 0.
    """
    assessment_weight = 0.40
    exam_weight = 0.60

    # Handle potential missing values by treating them as 0
    assessment_1 = row.get('Assessment_1', 0) if pd.notna(row.get('Assessment_1', 0)) else 0
    assessment_2 = row.get('Assessment_2', 0) if pd.notna(row.get('Assessment_2', 0)) else 0
    exam_1 = row.get('Exam_1', 0) if pd.notna(row.get('Exam_1', 0)) else 0
    exam_2 = row.get('Exam_2', 0) if pd.notna(row.get('Exam_2', 0)) else 0


    # Calculate average assessment and exam scores
    avg_assessment = (assessment_1 + assessment_2) / 2
    avg_exam = (exam_1 + exam_2) / 2


    # Calculate the final grade
    final_grade = (avg_assessment * assessment_weight) + (avg_exam * exam_weight)


    return round(final_grade, 2) # Round to 2 decimal places

# Function to generate PDF report
def create_individual_report_pdf(student_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Student Result Sheet", ln=True, align="C")
    pdf.ln(10)

    for index, row in student_data.iterrows():
        pdf.cell(200, 10, txt=f"Student Name: {row['Student_Name']}", ln=True)
        pdf.cell(200, 10, txt=f"Class: {row['Class']}", ln=True) # Added Class to PDF
        pdf.cell(200, 10, txt=f"Subject: {row['Subject']}", ln=True)
        pdf.cell(200, 10, txt=f"Assessment 1 Score: {row['Assessment_1']}", ln=True)
        pdf.cell(200, 10, txt=f"Assessment 2 Score: {row['Assessment_2']}", ln=True)
        pdf.cell(200, 10, txt=f"Exam 1 Score: {row['Exam_1']}", ln=True)
        pdf.cell(200, 10, txt=f"Exam 2 Score: {row['Exam_2']}", ln=True)
        pdf.cell(200, 10, txt=f"Final Grade: {row['Final_Grade']}", ln=True)
        pdf.ln(10)

    return pdf.output(dest='S').encode('latin1') # Return as bytes


st.title("Student Grade Input and Reporting Application")

# Add sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Teacher Input", "Check Result", "Class Summary"])

if page == "Home":
    st.header("Welcome to the Student Grade Application")
    # Add code to display the school logo
    # Replace 'path/to/your/school_logo.png' with the actual path to your logo file
    # Make sure the logo file is in the same directory as your app.py or in a subdirectory
    try:
        st.image("logo", caption="School Logo", width=200) # Example using the uploaded image
    except FileNotFoundError:
        st.warning("School logo not found. Please make sure 'logo' is in the correct directory.")
    st.write("Use the navigation on the left to go to different sections of the application.")
    st.write("Teachers can input scores, and both teachers and students can check individual results.")

elif page == "Teacher Input":
    # Input form for student scores
    st.header("Enter Student Scores")

    # Define class categories, classes, and subjects
    class_categories = ["Junior", "Senior"]
    junior_classes = ["JSS 1", "JSS 2", "JSS 3"]
    senior_classes = ["SS 1", "SS 2", "SS 3"]

    # Define subjects for each class category
    junior_subjects = [
        "English Studies", "Mathematics", "One Nigerian Language",
        "Intermediate Science", "Physical & Health Education",
        "Digital Technologies / Information Technology (ICT)",
        "Christian Religious Studies (CRS) / Islamic Studies (IS)",
        "Nigerian History", "Social and Citizenship Studies",
        "Cultural & Creative Arts (CCA)", "Business Studies or Trade Subject",
        "French (Optional)", "Arabic (Optional)"
    ]
    senior_subjects = [
        "English Language", "General Mathematics", "One Trade Subject",
        "Citizenship & Heritage Studies"
        # Add more senior elective and specialization subjects as needed
    ]


    with st.form("score_form"):
        student_name_input = st.text_input("Student Name")
        selected_class_category = st.selectbox("Select Class Category", class_categories)

        selected_class = ""
        if selected_class_category == "Junior":
            selected_class = st.selectbox("Select Class", junior_classes)
            subject_options = junior_subjects
        elif selected_class_category == "Senior":
            selected_class = st.selectbox("Select Class", senior_classes)
            subject_options = senior_subjects
        else:
             subject_options = [] # No subjects if no category is selected


        selected_subject_input = st.selectbox("Select Subject", subject_options) # Changed to selectbox

        assessment_1_input = st.number_input("Assessment 1 Score", min_value=0.0, max_value=100.0, value=0.0)
        assessment_2_input = st.number_input("Assessment 2 Score", min_value=0.0, max_value=100.0, value=0.0)
        exam_1_input = st.number_input("Exam 1 Score", min_value=0.0, max_value=100.0, value=0.0)
        exam_2_input = st.number_input("Exam 2 Score", min_value=0.0, max_value=100.0, value=0.0)

        submit_button = st.form_submit_button("Add Score")

        if submit_button:
            # Validate input data
            if not student_name_input or not selected_class or not selected_subject_input: # Updated validation
                st.error("Student Name, Class, and Subject cannot be empty.")
            else:
                # Create a new row for the DataFrame
                new_data = {
                    'Student_Name': student_name_input,
                    'Class': selected_class, # Use selected class
                    'Subject': selected_subject_input, # Use selected subject
                    'Assessment_1': assessment_1_input,
                    'Assessment_2': assessment_2_input,
                    'Exam_1': exam_1_input,
                    'Exam_2': exam_2_input,
                    'Final_Grade': None # Final grade will be calculated later
                }
                # Append the new data to the DataFrame
                # Use pd.concat for appending to a DataFrame
                st.session_state['student_data_df'] = pd.concat([st.session_state['student_data_df'], pd.DataFrame([new_data])], ignore_index=True)
                st.success("Score added successfully!")
                # Recalculate grades after adding new data
                st.session_state['student_data_df']['Final_Grade'] = st.session_state['student_data_df'].apply(calculate_final_grade, axis=1)
                # Save data after adding a new entry
                save_data(st.session_state['student_data_df'])

    # Display the current data in the DataFrame within the teacher section
    st.header("Current Student Data Overview")
    st.dataframe(st.session_state['student_data_df'])


elif page == "Check Result":
    # Section to view individual student results (kept separate)
    st.header("View Individual Student Results")

    if 'student_data_df' in st.session_state and not st.session_state['student_data_df'].empty:
        # Get unique student names for individual result selection
        student_names_individual = st.session_state['student_data_df']['Student_Name'].unique()
        subjects_individual = st.session_state['student_data_df']['Subject'].unique() # Keep subject selection for individual view

        # Create select boxes for student and subject selection for individual view
        selected_student_individual = st.selectbox("Select Student (for individual view)", student_names_individual)
        selected_subject_individual = st.selectbox("Select Subject (for individual view)", subjects_individual)


        # Filter the DataFrame based on individual selection
        individual_result_df = st.session_state['student_data_df'][
            (st.session_state['student_data_df']['Student_Name'] == selected_student_individual) &
            (st.session_state['student_data_df']['Subject'] == selected_subject_individual)
        ]

        # Display the filtered data for individual result
        if not individual_result_df.empty:
            st.subheader(f"Results for {selected_student_individual} in {selected_subject_individual}")
            st.dataframe(individual_result_df)

            # Add PDF generation option
            if st.button("Generate PDF Report for Individual Result"):
                pdf_output = create_individual_report_pdf(individual_result_df)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_output,
                    file_name=f"{selected_student_individual}_{selected_subject_individual}_Result_Report.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("No data available for the selected student and subject combination for individual view.")
    else:
        st.info("No student data available yet. Please add scores using the form above.")

elif page == "Class Summary":
    # Section for Overall Class Performance Summary (per subject, as before)
    st.header("Overall Class Performance Summary per Subject")

    # Check if the DataFrame is not empty
    if 'student_data_df' in st.session_state and not st.session_state['student_data_df'].empty:
        # Group by 'Subject' and calculate summary statistics
        subject_summary = st.session_state['student_data_df'].groupby('Subject').agg(
            Average_Assessment_1=('Assessment_1', 'mean'),
            Average_Assessment_2=('Assessment_2', 'mean'),
            Average_Exam_1=('Exam_1', 'mean'),
            Average_Exam_2=('Exam_2', 'mean'),
            Average_Final_Grade=('Final_Grade', 'mean'),
            Number_of_Students=('Student_Name', 'nunique') # Count unique students per subject
        ).reset_index() # Keep Subject as a column

        # Display the summary statistics
        st.subheader("Summary Statistics by Subject")
        st.dataframe(subject_summary)

        # Add grade distribution
        st.subheader("Grade Distribution by Subject")
        # Define grade bins and labels (adjust as needed)
        grade_bins = [0, 39, 44, 50, 60, 70, 101] # Updated bins
        grade_labels = ['F9', 'E8', 'D7', 'C', 'B', 'A'] # Updated labels

        # Create a new column with grade bins (handle potential non-numeric Final_Grade before cutting)
        if pd.api.types.is_numeric_dtype(st.session_state['student_data_df']['Final_Grade']):
            st.session_state['student_data_df']['Grade_Category'] = pd.cut(
                st.session_state['student_data_df']['Final_Grade'],
                bins=grade_bins,
                labels=grade_labels,
                right=False, # Include the left bin edge, exclude the right
                duplicates='drop' # Handle potential issues with bin edges and labels
            )
            # Count students in each grade category per subject
            grade_distribution = st.session_state['student_data_df'].groupby('Subject')['Grade_Category'].value_counts().unstack(fill_value=0)

            # Ensure all grade labels are columns, even if no students in that category
            grade_distribution = grade_distribution.reindex(columns=grade_labels, fill_value=0)

            st.dataframe(grade_distribution)
        else:
            st.info("Final Grade column is not numeric, cannot generate grade distribution.")


    else:
        st.info("No student data available to generate a class summary.")

