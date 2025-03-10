import pandas as pd

# Read the first CSV file
df1 = pd.read_csv("data/mimiciv_meds/raw_input/meas_chartevents_main.csv")  # Replace with the path to your first CSV file

# Read the second CSV file
df2 = pd.read_csv("data/mimiciv_meds/raw_input/icu_d_items.csv")  # Replace with the path to your second CSV file

# Merge the two DataFrames based on the itemid column, using df1 as the base
merged_df = pd.merge(
    df1,
    df2,
    left_on="itemid (omop_source_code)",  # itemid column in the first file
    right_on="itemid",  # itemid column in the second file
    how="left"  # Use left join to keep all rows from df1
)

# Rename the unitname column to valueuom
merged_df.rename(columns={"unitname": "valueuom"}, inplace=True)

# If the comment column exists, translate its content to English
if "comment" in merged_df.columns:
    # Example translation logic (replace with actual translation logic if needed)
    merged_df["comment"] = merged_df["comment"].apply(
        lambda x: "Translated comment" if pd.notna(x) else x
    )

# Save the merged result to a new CSV file
merged_df.to_csv("meas_chartevents.csv", index=False)

print("Merge completed. Results saved to merged_output.csv")