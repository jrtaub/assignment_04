"""
payroll_app.py — the weekly payroll, for someone who has never opened a terminal.

Every Friday the office manager at Salt City Coffee exports the week's timesheet
from the point-of-sale system. This page turns it into a paycheck table and the
CSV the online payroll provider imports — without the manager touching pandas.

The app is mostly *assembly*: the roster is loaded from data/, the upload comes
from the page, and one call to `build_payroll` does all the work. What the page
adds is what a manager needs to trust the numbers: totals, a loud warning about
anything the pipeline could not match, the full lineage table, and the download.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_pipeline.py -k app
"""

# --- The page ---------------------------------------------------------------------
#
# No scaffolding. Every function this page needs already exists in the payroll
# package, and every widget it needs you used in Assignment 03. README Step 8 has
# the exact widgets, keys and labels; the tests in tests/test_pipeline.py -k app
# check them.
#
# The shape, in words:
#
#   title and a sentence of instructions
#   roster  <- load_employees()                      (fixed; not uploaded)
#   upload  <- st.file_uploader, key="timesheet"     (returns None until chosen)
#   if there is an upload:
#       timesheet <- load_timesheet(upload)
#       payroll   <- build_payroll(timesheet, roster)   one call does all the work
#       the pay period (payroll_date) as a subheader
#       four st.metric cards in st.columns(4) — totals are .sum() on a Series,
#           counts are len() of a boolean-indexed frame
#       st.warning naming the unmatched employee_ids, or st.success if none
#       st.dataframe(payroll) — the lineage table, raw and computed side by side
#       st.download_button, key="download": payroll_export(payroll).to_csv(index=False)
#
# What the page does NOT do: arithmetic on rows, cleaning, merging. If you find
# yourself writing a loop or an apply here, that logic belongs in the package.


import streamlit as st


from payroll import (load_employees, load_timesheet, build_payroll, payroll_export)

st.title("Salt City Coffee - weekly Payroll")
st.write("Upload this week's timesheet export. The roster is loaded automatically.Check\
          the totals, fix anything flagged, and then download the file for the payroll\
          provider.")

roster = load_employees()
upload = st.file_uploader("Upload timesheet", key="timesheet")

if upload is not None:
    timesheet = load_timesheet(upload)
    payroll = build_payroll(timesheet, roster)
    pay_period = payroll['payroll_date'].iloc[0]
    st.subheader(f"Pay Period: {pay_period}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        paid_employees = payroll[payroll['gross_pay'] > 0]
        employees_paid = len(paid_employees)
        st.metric("Employees paid", str(employees_paid))

    with col2:
        total_hours = payroll['hours_worked'].sum()
        st.metric("Total hours", f"{total_hours:.2f}")

    with col3:
        paid_payroll = payroll[payroll['gross_pay'] > 0]
        total_gross_pay = paid_payroll['gross_pay'].sum()
        st.metric("Total gross pay", f"${total_gross_pay:,.2f}")
    with col4:
        overtime_rows = payroll[payroll['hours_worked'] > 40.1]
        overtime_count = len(overtime_rows)
        st.metric("Overtime weeks", str(overtime_count))
    unmatched_rows = payroll[payroll['pay_type'] == 'unmatched']
    if len(unmatched_rows) > 0:
        st.warning(f"Unmatched employee_id(s): {', '.join
                                                (map(str, unmatched_rows
                                                     ['employee_id']))}")
    else:
        st.success("All employee IDs matched!")
        st.dataframe(payroll)
    st.dataframe(payroll)
    csv_data = payroll_export(payroll).to_csv(index=False)
    st.download_button(
        label="Download Payroll CSV",
        data=csv_data,
        file_name="payroll_export.csv",
        mime="text/csv",
        key="download"
        )
