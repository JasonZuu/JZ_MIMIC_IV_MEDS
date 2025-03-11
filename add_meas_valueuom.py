import pandas as pd

# Read the first CSV file
df1 = pd.read_csv("data/mimiciv_meds/raw_input/meas_chartevents_main.csv")  # Replace with the path to your first CSV file

# Read the second CSV file
df2 = pd.read_csv("data/mimiciv_meds/raw_input/icu_d_items.csv")  # Replace with the path to your second CSV file
df2 = df2[df2["param_type"]=="Numeric"][["itemid", "label", "unitname"]]  # Keep only the itemid and unitname columns

# Step 1: Perform a left merge
merged_df = pd.merge(
    df1,
    df2[["itemid", "unitname"]],
    left_on="itemid (omop_source_code)",  # itemid column in the first file
    right_on="itemid",  # itemid column in the second file
    how="left"  # Use left join to keep all rows from df1
)

# Step 2: Find rows in df2 that are not in df1
df2_only_rows = df2[~df2["itemid"].isin(df1["itemid (omop_source_code)"])]

# Step 3: Add these rows to df1, keeping only label and unitname from df2
# Create a new DataFrame with the same columns as df1, but fill with NaN
new_rows = pd.DataFrame(columns=df1.columns)

# Add the itemid, label, and unitname from df2_only_rows
new_rows["itemid (omop_source_code)"] = df2_only_rows["itemid"]
new_rows["label"] = df2_only_rows["label"]
new_rows["unitname"] = df2_only_rows["unitname"]

# Step 4: Append these new rows to the merged_df
final_df = pd.concat([merged_df, new_rows], ignore_index=True)

# Step 5: Rename the unitname column to valueuom
final_df.rename(columns={"unitname": "valueuom"}, inplace=True)

# Step 6: If the comment column exists, translate its content to English
if "comment" in final_df.columns:
    # Example translation logic (replace with actual translation logic if needed)
    final_df["comment"] = final_df["comment"].apply(
        lambda x: "Translated comment" if pd.notna(x) else x
    )

# Save the final result to a new CSV file
final_df.to_csv("meas_chartevents.csv", index=False)

print("Merge completed. Results saved to meas_chartevents.csv")