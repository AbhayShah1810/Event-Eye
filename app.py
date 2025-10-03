import streamlit as st
import pandas as pd
from certificate_generator import process_participants
from email_sender import bulk_send_certificates


st.set_page_config(layout="wide", page_title="EventEye Certificate Automation")

st.title("⚡ AI-Powered Certificate Automation for EventEye")
st.markdown("Automate certificate generation, 'AI' verification, and bulk email distribution.")

uploaded_file = st.file_uploader("Upload Participant List (CSV file with 'name' and 'email' columns)", type="csv")

if uploaded_file is not None:
    st.success("File uploaded successfully!")

    df_preview = pd.read_csv(uploaded_file)
    st.subheader("1. Participant Data Preview")
    st.dataframe(df_preview, use_container_width=True)

    st.subheader("2. Automation Actions")
    col1, col2 = st.columns(2)

    if col1.button("🔥 Step 1: Generate Certificates (with QR/Verification)"):
        st.session_state["results_df"] = None

        file_path = "uploaded_participants.csv"
        df_preview.to_csv(file_path, index=False)

        with st.spinner("Generating certificates... This might take a moment."):
            results_df = process_participants(file_path)

        st.session_state["results_df"] = results_df
        st.success("✅ Certificate Generation Complete!")

    if "results_df" in st.session_state and st.session_state["results_df"] is not None:
        if col2.button("📧 Step 2: Send Bulk Emails"):
            st.warning("Sending real emails! Gmail SMTP must use an App Password.")

            with st.spinner("Sending emails in bulk..."):
                final_results_df = bulk_send_certificates(st.session_state["results_df"].copy())

            st.session_state["final_results_df"] = final_results_df
            st.success("🎉 Bulk Emailing Process Finished!")

    if "final_results_df" in st.session_state and st.session_state["final_results_df"] is not None:
        st.subheader("3. Delivery Status Dashboard (MVP)")

        display_df = st.session_state["final_results_df"][
            ["name", "email", "status", "unique_id"]
        ]

        total_recipients = len(display_df)
        success_count = len(display_df[display_df["status"] == "Sent"])
        fail_count = len(display_df[display_df["status"].str.contains("Error|Failed|Verification")])

        st.metric(label="Total Processed", value=total_recipients)
        st.metric(label="Certificates Sent/Verified", value=f"{success_count} / {total_recipients}")
        st.metric(label="Errors/Bounces (Check logs)", value=fail_count)

        st.dataframe(display_df, use_container_width=True)
        st.download_button(
            "Download Final Status CSV",
            display_df.to_csv(index=False).encode("utf-8"),
            "final_status_report.csv",
            "text/csv",
        )
else:
    st.info("Waiting for a CSV upload to begin the automation process.")
    st.markdown(
        """
---
### ⚙️ How to Run This Project
1.  **Dependencies:** `pip install -r requirements.txt`
2.  **Email Auth:** Create a `.env` file with `SENDER_EMAIL`, `SENDER_NAME`, and `GMAIL_APP_PASSWORD`.
3.  **Template:** Place your certificate image in `assets/base_certificate.png`.
4.  **Run:** `streamlit run app.py`
"""
    )


