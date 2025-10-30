# CCCC_fixed.py
import streamlit as st
import pandas as pd
import os
import segno
import tempfile
from io import BytesIO
from xhtml2pdf import pisa
import base64

# ---------------------- CONFIG / PATHS ----------------------
LOGO_PATH = r"C:\Users\muthu\OneDrive\Desktop\collegeapp\clglogo.jpeg"
ICON_PATH = r"C:\Users\muthu\Desktop\FeesApp\Screenshot 2025-04-24 153118.ico"
CREDENTIALS_FILE = r"C:\Users\muthu\OneDrive\Desktop\collegeapp\credentials.csv"
DATA_FILE = r"C:\Users\muthu\OneDrive\Desktop\collegeapp\abi.xlsx"

st.set_page_config(page_title="Fees Management System", page_icon=ICON_PATH, layout="wide")

# ---------------------- SESSION INIT ----------------------
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ---------------------- UTILITIES ----------------------
def image_to_base64(image_path):
    """Convert image to base64 string (safe if file exists)"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

logo_base64 = image_to_base64(LOGO_PATH)

def display_logo():
    """Display college logo (if available)"""
    try:
        st.image(LOGO_PATH, width=100)
    except Exception:
        if logo_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{logo_base64}" width="100"/>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def ensure_columns(df):
    """Ensure all expected fee and meta columns exist with appropriate dtypes."""
    # Basic meta columns
    meta_cols = [
        "UMIS Number", "EMIS Number", "Register Number", "Batch", "Name", "Sex",
        "Department", "Date of Birth", "Community & Subcaste", "Nationality & Religion",
        "Father's Name", "Address", "Mobile Number", "Aadhar Number", "First Graduate"
    ]
    for c in meta_cols:
        if c not in df.columns:
            df[c] = ""

    # Fee structure columns (for 1st-4th year)
    years = ["1st", "2nd", "3rd", "4th"]
    fee_types = [
        "Bus Fees", "Mess Fees", "Hostel Fees", "Exam Fees",
        "Tution Fees", "Fine", "Miscellaneous", "Course Fees",
        "Due Fees", "Paid Fees", "Remaining Fees", "Total Fees"
    ]
    for year in years:
        for ft in fee_types:
            col = f"{ft} {year} year"
            if col not in df.columns:
                df[col] = 0.0

    # Convert numeric columns to numeric type
    for col in df.columns:
        if any(keyword in col for keyword in ["Fees", "Paid", "Remaining", "Total", "Due", "Fine"]):
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

def load_data():
    """Load student data from Excel; if missing, create empty DataFrame with columns."""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, engine='openpyxl')
        except Exception:
            df = pd.read_excel(DATA_FILE)  # fallback
    else:
        df = pd.DataFrame()
    df = ensure_columns(df)
    return df

def save_data(df):
    """Save DataFrame to Excel"""
    # ensure directory exists
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    except Exception:
        pass
    df.to_excel(DATA_FILE, index=False)

# ---------------------- PAGE FUNCTIONS ----------------------
def home_page():
    display_logo()
    st.title("🎓 Dr.G.U.Pope College Of Engineering")
    st.subheader("Welcome to the Fees Management System")
    st.markdown("Please click below to login and access student records.")
    if st.button("Login"):
        st.session_state.page = "login"
        st.rerun()

def login_page():
    display_logo()
    st.title("WELCOME")
    st.title("Dr.G.U.Pope College Of Engineering")

    if os.path.exists(CREDENTIALS_FILE):
        try:
            creds_df = pd.read_csv(CREDENTIALS_FILE)
            valid_users = dict(zip(creds_df['username'], creds_df['password']))
        except Exception:
            st.error("⚠️ credentials.csv found but couldn't be read. Check file format.")
            return
    else:
        st.error("⚠️ credentials.csv file not found!")
        return

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in valid_users and valid_users[username] == password:
            st.session_state.logged_in = True
            st.session_state.page = "main"
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

def view_students_page(df):
    st.subheader("View Students by Batch")
    batch_column = 'Batch'
    if batch_column not in df.columns:
        st.error(f"Column '{batch_column}' not found in data")
        return
    batches = df[batch_column].fillna("Unknown").unique().tolist()
    selected_batch = st.selectbox("Select Batch", batches)
    filtered_df = df[df[batch_column] == selected_batch]
    st.dataframe(filtered_df)

def search_student_page(df):
    st.subheader("🔍 Search Student Details")
    if df.empty or df['Name'].replace('', pd.NA).dropna().empty:
        st.warning("No students available in the system.")
        return

    search_option = st.radio("Search by:", ["Name", "Registration Number"])
    if search_option == "Name":
        student_names = df["Name"].fillna("").unique().tolist()
        selected_name = st.selectbox("Select Student", student_names)
        student = df[df["Name"] == selected_name]
    else:
        reg_nos = df["Register Number"].fillna("").unique().tolist()
        selected_reg = st.selectbox("Select Registration Number", reg_nos)
        student = df[df["Register Number"] == selected_reg]

    if not student.empty:
        student_info = student.iloc[0]
        st.markdown("---")
        st.subheader("📋 Student Information")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **👤 Personal Details:**
            - **Name:** {student_info.get('Name','')}
            - **Registration No:** {student_info.get('Register Number','')}
            - **UMIS No:** {student_info.get('UMIS Number','')}
            - **EMIS No:** {student_info.get('EMIS Number','')}
            - **Batch:** {student_info.get('Batch','')}
            - **Department:** {student_info.get('Department','')}
            - **Sex:** {student_info.get('Sex','')}
            - **Date of Birth:** {student_info.get('Date of Birth','')}
            """)
        with col2:
            st.markdown(f"""
            **👨‍👩‍👧‍👦 Family & Contact:**
            - **Father's Name:** {student_info.get("Father's Name",'')}
            - **Mobile:** {student_info.get('Mobile Number','')}
            - **Aadhar:** {student_info.get('Aadhar Number','')}
            - **Address:** {student_info.get('Address','')}
            - **Community:** {student_info.get('Community & Subcaste','')}
            - **Religion:** {student_info.get('Nationality & Religion','')}
            - **First Graduate:** {student_info.get('First Graduate','')}
            """)
        st.markdown("---")
        st.subheader("💰 Fees Information")
        years = ["1st", "2nd", "3rd", "4th"]
        cols = st.columns(4)
        for i, year in enumerate(years):
            with cols[i]:
                total_fees = student_info.get(f'Total Fees {year} year', 0.0)
                paid_fees = student_info.get(f'Paid Fees {year} year', 0.0)
                remaining = student_info.get(f'Remaining Fees {year} year', 0.0)
                st.markdown(f"**{year.upper()} YEAR**")
                st.metric("Total Fees", f"₹{total_fees}")
                st.metric("Paid", f"₹{paid_fees}")
                st.metric("Balance", f"₹{remaining}")
                if total_fees > 0:
                    progress = min((paid_fees / total_fees) * 100, 100)
                    st.progress(progress / 100)
                    st.caption(f"{progress:.1f}% Paid")
                else:
                    st.caption("No fees data available")
        st.markdown("---")
        st.subheader("📊 Detailed Fees Breakdown")
        selected_year = st.selectbox("Select Year for Detailed View", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        year_key = selected_year.split()[0]  # "1st", "2nd", etc.
        fees_data = {
            "Fee Type": ["Bus Fees", "Mess Fees", "Hostel Fees", "Exam Fees",
                        "Tution Fees", "Fine", "Miscellaneous", "Course Fees", "Due Fees"],
            "Amount": [
                student_info.get(f'Bus Fees {year_key} year', 0),
                student_info.get(f'Mess Fees {year_key} year', 0),
                student_info.get(f'Hostel Fees {year_key} year', 0),
                student_info.get(f'Exam Fees {year_key} year', 0),
                student_info.get(f'Tution Fees {year_key} year', 0),
                student_info.get(f'Fine {year_key} year', 0),
                student_info.get(f'Miscellaneous {year_key} year', 0),
                student_info.get(f'Course Fees {year_key} year', 0),
                student_info.get(f'Due Fees {year_key} year', 0)
            ]
        }
        fees_df = pd.DataFrame(fees_data)
        st.dataframe(fees_df, use_container_width=True)
        st.markdown("---")
        st.subheader("📈 Payment Status Summary")
        status_data = []
        for year in years:
            total = student_info.get(f'Total Fees {year} year', 0)
            paid = student_info.get(f'Paid Fees {year} year', 0)
            remaining = student_info.get(f'Remaining Fees {year} year', 0)
            if total > 0:
                percentage = min((paid / total) * 100, 100)
                status = "✅ Paid" if remaining <= 0 else "⚠️ Partial" if paid > 0 else "❌ Pending"
            else:
                percentage = 0
                status = "ℹ️ No Fees"
            status_data.append({
                "Year": f"{year.upper()} Year",
                "Total": f"₹{total}",
                "Paid": f"₹{paid}",
                "Balance": f"₹{remaining}",
                "Progress": percentage,
                "Status": status
            })
        status_df = pd.DataFrame(status_data)
        st.dataframe(status_df, use_container_width=True)
    else:
        st.warning("No student found with the selected criteria.")

def add_student_page(df):
    st.subheader("Add New Student")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            umis_no = st.text_input("UMIS Number")
            emis_no = st.text_input("EMIS Number")
            reg_no = st.text_input("Registration Number")
            batch_no = st.text_input("Batch")
            name = st.text_input("Name")
            sex = st.selectbox("Sex", ["Male", "Female", "Other"])
            department = st.text_input("Department")
            dob = st.date_input("Date of Birth")
        with col2:
            community_subcaste = st.text_input("Community & Subcaste")
            nationality_religion = st.text_input("Nationality & Religion")
            father_name = st.text_input("Father's Name")
            address = st.text_area("Address")
            mobile = st.text_input("Mobile Number")
            aadhar_no = st.text_input("Aadhar Number")
            first_graduate = st.selectbox("First Graduate", ["Yes", "No"])
        st.subheader("Fees Information")
        years = ["1st", "2nd", "3rd", "4th"]
        fees_cols = st.columns(4)
        fee_components = [
            "Bus Fees", "Mess Fees", "Hostel Fees", "Exam Fees",
            "Tution Fees", "Fine", "Miscellaneous", "Course Fees", "Due Fees", "Paid Fees"
        ]
        fees_data = {}
        for i, year in enumerate(years):
            with fees_cols[i]:
                st.markdown(f"**{year.upper()} YEAR**")
                for fee_name in fee_components:
                    key = f"{fee_name} {year} year"
                    fees_data[key] = st.number_input(f"{fee_name} {year} year", step=100, key=f"{fee_name}_{year}")
        if st.form_submit_button("Add Student"):
            # compute totals / remaining
            for year in years:
                total = 0.0
                for fee_name in ["Bus Fees", "Mess Fees", "Hostel Fees", "Exam Fees",
                                "Tution Fees", "Fine", "Miscellaneous", "Course Fees", "Due Fees"]:
                    total += float(fees_data.get(f"{fee_name} {year} year", 0.0) or 0.0)
                fees_data[f"Total Fees {year} year"] = total
                paid = float(fees_data.get(f"Paid Fees {year} year", 0.0) or 0.0)
                fees_data[f"Remaining Fees {year} year"] = total - paid
            new_data = {
                "UMIS Number": umis_no,
                "EMIS Number": emis_no,
                "Register Number": reg_no,
                "Batch": batch_no,
                "Name": name,
                "Sex": sex,
                "Department": department,
                "Date of Birth": dob.strftime("%d-%m-%Y") if dob else "",
                "Community & Subcaste": community_subcaste,
                "Nationality & Religion": nationality_religion,
                "Father's Name": father_name,
                "Address": address,
                "Mobile Number": mobile,
                "Aadhar Number": aadhar_no,
                "First Graduate": first_graduate,
                **fees_data
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df = ensure_columns(df)
            save_data(df)
            st.success(f"✅ Student {name} added successfully!")

def search_by_department_page(df):
    st.subheader("Search Students by Department")
    dept = st.text_input("Enter Department Name")
    if dept:
        filtered = df[df["Department"].fillna("").str.lower() == dept.lower()]
        if not filtered.empty:
            st.dataframe(filtered)
        else:
            st.warning(f"No students found in department: {dept}")

def students_with_dues_page(df):
    st.subheader("Students with Remaining Fees 1st year")
    dues = df[df["Remaining Fees 1st year"] > 0]
    st.dataframe(dues)
    st.subheader("Students with Remaining Fees 2nd year")
    dues = df[df["Remaining Fees 2nd year"] > 0]
    st.dataframe(dues)
    st.subheader("Students with Remaining Fees 3rd year")
    dues = df[df["Remaining Fees 3rd year"] > 0]
    st.dataframe(dues)
    st.subheader("Students with Remaining Fees 4th year")
    dues = df[df["Remaining Fees 4th year"] > 0]
    st.dataframe(dues)

def pay_fees_page(df):
    st.subheader("Pay Student Fees")
    if df.empty or df['Name'].replace('', pd.NA).dropna().empty:
        st.warning("No students available to pay fees for.")
        return

    # Select student
    student_name = st.selectbox("Select Student", df["Name"].fillna("").unique().tolist())
    student = df[df["Name"] == student_name]

    if not student.empty:
        student_info = student.iloc[0]
        st.write("Student Info:")
        st.write(student[["Name", "Department"]])

        # Year mapping
        year_options = ["I Year", "II Year", "III Year", "IV Year"]
        year_map = {
            "I Year": "1st year",
            "II Year": "2nd year",
            "III Year": "3rd year",
            "IV Year": "4th year"
        }
        selected_fee_year = st.selectbox("Select Academic Year to Pay Fees For", year_options)
        selected_year = year_map[selected_fee_year]  # e.g. "1st year"
        display_year_label = selected_fee_year  # keep UI label

        st.subheader("💳 Payment")
        pay_amount = st.number_input("Enter Payment Amount (INR)", min_value=0.0, step=100.0)

        fee_type = st.selectbox("Select Fee Type", [
            "Bus Fees", "Mess Fees", "Hostel Fees", "Exam Fees",
            "Tution Fees", "Fine", "Miscellaneous", "Course Fees", "Due Fees", "General Payment"
        ])

        if st.button("Submit Payment"):
            idx = student.index[0]

            # ensure numeric columns exist
            paid_col = f"Paid Fees {selected_year}"
            remaining_col = f"Remaining Fees {selected_year}"
            total_col = f"Total Fees {selected_year}"

            # initialize if missing
            for c in [paid_col, remaining_col, total_col]:
                if c not in df.columns:
                    df[c] = 0.0
            df[paid_col] = pd.to_numeric(df[paid_col], errors='coerce').fillna(0.0)
            df[remaining_col] = pd.to_numeric(df[remaining_col], errors='coerce').fillna(0.0)
            df[total_col] = pd.to_numeric(df[total_col], errors='coerce').fillna(0.0)

            # previous paid before update
            previous_paid = float(df.at[idx, paid_col])
            previous_remaining = float(df.at[idx, remaining_col])

            # Update paid and remaining
            df.at[idx, paid_col] = previous_paid + float(pay_amount)
            df.at[idx, remaining_col] = max(previous_remaining - float(pay_amount), 0.0)

            save_data(df)
            st.success(f"💰 ₹{pay_amount} paid successfully for {student_name} in {display_year_label}!")

            # ---------------------- RECEIPT ----------------------
            st.subheader("🧾 Payment Receipt")
            receipt_no = f"RCPT-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
            # Fee summary values
            total_fees_now = df.at[idx, total_col]
            paid_after = df.at[idx, paid_col]
            remaining_after = df.at[idx, remaining_col]
            previous_paid_display = previous_paid

            receipt_html = f"""
              <div style="border:2px dashed #4CAF50; padding:25px; font-family:Arial; background:#f9f9f9;">
                <div style="display:flex; align-items:center; margin-bottom:15px;">
                  <img src="data:image/jpeg;base64,{logo_base64}" width="80" style="margin-right: 20px;"/>
                  <h2 style="color:#4CAF50;">DR.G.U.Pope College Of Engineering</h2>
                </div>
                <h3 style="text-align:center;">Fee Payment Receipt</h3>
                <div style="display:flex; justify-content:space-between;">
                  <div>
                    <p><strong>Student Name:</strong> {student_info.get('Name','')}</p>
                    <p><strong>Reg. No:</strong> {student_info.get('Register Number','')}</p>
                    <p><strong>Department:</strong> {student_info.get('Department','')}</p>
                  </div>
                  <div>
                    <p><strong>Date:</strong> {pd.Timestamp.now().date()}</p>
                    <p><strong>Academic Year:</strong> {display_year_label}</p>
                    <p><strong>Receipt No:</strong> {receipt_no}</p>
                  </div>
                </div>
                <hr>
                <div style="background:#e8f5e9; padding:10px; border-radius:5px; margin-bottom:15px;">
                  <h4 style="margin:0; color:#2e7d32;">Payment Details</h4>
                  <p><strong>Fee Type:</strong> {fee_type}</p>
                  <p><strong>Amount Paid:</strong> ₹{pay_amount}</p>
                </div>
                <h4 style="color:#2e7d32;">Fee Summary</h4>
                <p><strong>Total Fees ({display_year_label}):</strong> ₹{total_fees_now}</p>
                <p><strong>Previously Paid ({display_year_label}):</strong> ₹{previous_paid_display}</p>
                <p><strong>Amount Paid Now:</strong> ₹{pay_amount}</p>
                <p><strong>Paid (Now Total):</strong> ₹{paid_after}</p>
                <p><strong>Remaining Fees ({display_year_label}):</strong> ₹{remaining_after}</p>
                <div style="text-align:right; margin-top:20px;">
                  <p><strong>Signature</strong></p>
                  <div style="border-top:1px solid black; width:200px; display:inline-block;"></div>
                </div>
                <div style="text-align:center; margin-top:20px; font-style:italic; color:#666;">
                  <p>This is a computer generated receipt and does not require a physical signature.</p>
                </div>
              </div>
            """
            st.markdown(receipt_html, unsafe_allow_html=True)

           
         # ---------------------- TRANSFER CERTIFICATE ----------------------
        st.subheader("📄 Transfer Certificate")
        admission_no = st.text_input("Admission No", key="tc_adm_no")
        date_of_admission = st.date_input("Date of Admission", key="tc_doa")
        date_of_leaving = st.date_input("Date of Leaving", key="tc_dol")
        reg_no = student_info.get('Register Number', '')
        if st.button("Generate Transfer Certificate"):
                tc_no = f"TC-{reg_no}-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
                issue_date = pd.Timestamp.now().date().strftime("%d-%m-%Y")
                tc_html = f"""
                <div style="font-family:'Segoe UI', sans-serif; font-size:14px; max-width:800px;
                        margin:auto; color:#000; line-height:1.8; border:2px solid #000; padding:30px;">
                  <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <img src="data:image/jpeg;base64,{logo_base64}" width="80" style="margin-right: 20px;"/>
                    <div style="text-align: center; flex-grow: 1;">
                      <h2 style="margin: 0;">DR.G.U.Pope College Of Engineering</h2>
                      <h3 style="margin: 0;">(Approved by AICTE, Affiliated to Anna University)</h3>
                      <h4 style="margin: 0;">Pope Nagar, Sawyerpuram Thoothukudi District-628251</h4>
                      <h5 style="margin: 5px 0;">TRANSFER CERTIFICATE</h5>
                    </div>
                  </div>
                  <div style="display:flex; justify-content:space-between;">
                    <div><p><strong>TC No:</strong> {tc_no}</p><p><strong>Date:</strong> {issue_date}</p></div>
                    <div><p><strong>Admission No:</strong> {admission_no} </p><p><strong>Roll No:</strong> {reg_no}</p></div>
                  </div>
                  <p><strong>1.</strong> Name: {student_info.get('Name','')}</p>
                  <p><strong>2.</strong> Father’s Name: {student_info.get("Father's Name",'')}</p>
                  <p><strong>3.</strong> Sex: {student_info.get('Sex','')}</p>
                  <p><strong>4.</strong> DOB: {student_info.get('Date of Birth','')}</p>
                  <p><strong>5.</strong> Nationality & Religion: {student_info.get('Nationality & Religion','')}</p>
                  <p><strong>6.</strong> Community & Subcaste: {student_info.get('Community & Subcaste','')}</p>
                  <p><strong>7.</strong> Date of Admission: {date_of_admission.strftime('%d-%m-%Y')}</p>
                  <p><strong>8.</strong> Class and course in which the student was Admitted: {student_info.get('Department','')}</p>
                  <p><strong>9.</strong> Class and course studied at the time of leaving : {student_info.get('Department','')}</p>
                  <p><strong>10.</strong> Whether Qualified for Promotion to higher studies: REFER MARKSHEET</p>
                  <p><strong>11.</strong> Date of Leaving: {date_of_leaving.strftime('%d-%m-%Y')}</p>
                  <p><strong>12.</strong> Issue Date: {issue_date}</p>
                  <p><strong>13.</strong> UMIS No: {student_info.get('UMIS Number','')}</p>
                  <p><strong>14.</strong> EMIS No: {student_info.get('EMIS Number','')}</p>
                  <p>This is to certify that <strong>{student_info.get('Name','')}</strong> has been a student of this institution and the above details are correct.</p>
                  <div style="text-align:right; margin-top:50px;"><strong>Principal</strong></div>
                </div>
                """
                st.markdown(tc_html, unsafe_allow_html=True)
                tc_pdf = BytesIO()
                pisa_status = pisa.CreatePDF(tc_html, dest=tc_pdf)
                if not pisa_status.err:
                    st.download_button("📥 Download TC as PDF", data=tc_pdf.getvalue(), file_name=f"{tc_no}.pdf", mime="application/pdf")
                else:
                    st.error("❌ Failed to generate TC PDF")

        # ---------------------- CONDUCT CERTIFICATE ----------------------
        st.subheader("📜 Conduct Certificate")
        title = st.radio("Student Title:", ["Selvan", "Selvi"])
        period_from = st.date_input("Conduct Period: From", key="cc_from")
        period_to = st.date_input("Conduct Period: To", key="cc_to")
        if st.button("Generate Conduct Certificate"):
                cc_no = f"CC-{reg_no}-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
                issue_date = pd.Timestamp.now().date().strftime("%d-%m-%Y")
                from_str = period_from.strftime("%d-%m-%Y")
                to_str = period_to.strftime("%d-%m-%Y")
                conduct_html = f"""
                <div style="font-family:Arial, sans-serif; font-size:18px; max-width:800px;
                        margin:auto; color:#000; line-height:1.8; border:2px solid #000; padding:30px;">
                  <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <img src="data:image/jpeg;base64,{logo_base64}" width="80" style="margin-right: 20px;"/>
                    <div style="text-align: center; flex-grow: 1; font-size:10px;">
                      <h2 style="margin: 0;">DR.G.U.Pope College Of Engineering</h2>
                      <h4 style="margin: 0;">Pope Nagar, Sawyerpuram-628251, Thoothukudi District</h4>
                      <h5 style="margin: 5px 0;">CONDUCT CERTIFICATE</h5>
                    </div>
                  </div>
                  <div style="display:flex; justify-content:space-between;">
                    <div><strong>Roll No:</strong> {reg_no}</div>
                    <div><strong>C.C. No:</strong> {cc_no}</div>
                  </div>
                  <p>This is to certify that {title} <strong>{student_info.get('Name','')}</strong> was a student of this college in the <strong>{student_info.get('Department','')}</strong> branch during <strong>{from_str} to {to_str}</strong>.</p>
                  <p>His/Her conduct and character were found to be <strong>Good</strong>.</p>
                  <div style="display:flex; justify-content:space-between; margin-top:50px;">
                    <div><strong>Date:</strong> {issue_date}</div>
                    <div style="text-align:right;"><strong>Principal</strong></div>
                  </div>
                </div>
                """
                st.markdown(conduct_html, unsafe_allow_html=True)
                cc_pdf = BytesIO()
                pisa_status = pisa.CreatePDF(conduct_html, dest=cc_pdf)
                if not pisa_status.err:
                    st.download_button("📥 Download CC as PDF", data=cc_pdf.getvalue(), file_name=f"{cc_no}.pdf", mime="application/pdf")
                else:
                    st.error("❌ Failed to generate CC PDF")

def online_payment_page():
    st.subheader("📲 Online UPI Payment")
    upi_id = "devimuthumari388@oksbi"  # change if needed
    name = "DR.G.U.Pope College"
    amount = st.number_input("Enter Amount to Pay (INR)", min_value=1, step=1)
    if amount:
        upi_link = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
        qr = segno.make(upi_link)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            buffer = BytesIO()
            qr.save(buffer, kind="png")
            buffer.seek(0)
            st.image(tmp.name, caption="Scan to Pay via UPI App", use_column_width=False)
        st.markdown(f"Or click to pay: [Pay ₹{amount}]({upi_link})")

# ---------------------- MAIN APP ----------------------
def main_app():
    display_logo()
    df = load_data()
    st.title("FEES MANAGEMENT SYSTEM")
    st.title("STUDENTS DETAILS")
    menu = [
        "View Students", "Search Student", "Add Student", "Search by Department",
        "Students with Dues", "Pay Fees", "Online Payment"
    ]
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "View Students":
        view_students_page(df)
    elif choice == "Search Student":
        search_student_page(df)
    elif choice == "Add Student":
        add_student_page(df)
    elif choice == "Search by Department":
        search_by_department_page(df)
    elif choice == "Students with Dues":
        students_with_dues_page(df)
    elif choice == "Pay Fees":
        pay_fees_page(df)
    elif choice == "Online Payment":
        online_payment_page()

# ---------------------- ROUTING ----------------------
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.logged_in and st.session_state.page == "main":
    main_app()
else:
    # Safety fallback: if logged_in flag isn't set, show home/login depending on page
    if st.session_state.logged_in:
        st.session_state.page = "main"
        st.rerun()
    else:
        st.session_state.page = "home"
        home_page()
