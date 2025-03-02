# MIMIC-IV MEDS Extraction, Tabularisation, and Development

This pipeline extracts the MIMIC-IV dataset (from physionet) into the MEDS format.

## Usage:

```bash
pip install MIMIC_IV_MEDS
export DATASET_DOWNLOAD_USERNAME=$PHYSIONET_USERNAME
export DATASET_DOWNLOAD_PASSWORD=$PHYSIONET_PASSWORD
MEDS_extract-MIMIC_IV root_output_dir=$ROOT_OUTPUT_DIR
```

When you run this, the program will:

1. Download the needed raw MIMIC files for the currently supported version into
    `$ROOT_OUTPUT_DIR/raw_input`.
2. Perform initial, pre-MEDS processing on the raw MIMIC files, saving the results in
    `$ROOT_OUTPUT_DIR/pre_MEDS`.
3. Construct the final MEDS cohort, and save it to `$ROOT_OUTPUT_DIR/MEDS_cohort`.

You can also specify the target directories more directly, with

```bash
export DATASET_DOWNLOAD_USERNAME=$PHYSIONET_USERNAME
export DATASET_DOWNLOAD_PASSWORD=$PHYSIONET_PASSWORD
MEDS_extract-MIMIC_IV raw_input_dir=$RAW_INPUT_DIR pre_MEDS_dir=$PRE_MEDS_DIR MEDS_cohort_dir=$MEDS_COHORT_DIR
```

## Examples and More Info:

You can run `MEDS_extract-MIMIC_IV --help` for more information on the arguments and options. You can also run

```bash
MEDS_extract-MIMIC_IV root_output_dir=$ROOT_OUTPUT_DIR do_demo=True
```

to run the entire pipeline over the publicly available, fully open MIMIC-IV demo dataset.

## Expected runtime and compute needs

This pipeline can be successfully run over the full MIMIC-IV on a 5-core machine leveraging around 165GB of
memory in approximately 7 hours (note this time includes the time to download all of the MIMIC-IV files as
well, and this test was run on a machine with poor network transfer speeds and without any parallelization
applied to the transformation steps, so these speeds can likely be greatly increased). The output folder of
data is 9.8 GB. This can be reduced significantly as well as intermediate files not necessary for the final
MEDS dataset are retained in additional folders. See
[this github issue](https://github.com/mmcdermott/MEDS_transforms/issues/235) for tracking on ensuring these
directories are automatically cleaned up in the future.


## Task label extractuion commands
```bash
aces-cli cohort_name="anemia" cohort_dir="/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds" data.standard=meds data=sharded data.root="/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/MEDS_cohort/data" "data.shard=$(expand_shards train/300 tuning/100 held_out/100)" -m

```

## MEDS-tab (For XGBoost baseline)
1. Account codes
```bash
meds-tab-describe \
    "input_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/MEDS_cohort/data" \
    "output_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/tabular"
```

2. Tabularize static
```bash
meds-tab-tabularize-static \
    "input_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/MEDS_cohort/data" \
    "output_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/tabular" \
    tabularization.min_code_inclusion_count=10 \
    tabularization.window_sizes=[1d] \
    do_overwrite=False \
    tabularization.aggs=[static/present,code/count,value/count,value/sum,value/sum_sqd,value/min,value/max]
```

3. Tabularise time-series
```bash
meds-tab-tabularize-time-series \
    --multirun \
    worker="range(0,8)" \
    hydra/launcher=joblib \
    "input_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/MEDS_cohort/data" \
    "output_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/tabular" \
    tabularization.min_code_inclusion_count=10 \
    tabularization.window_sizes=[1d] \
    tabularization.aggs=[static/present,code/count,value/count,value/sum,value/sum_sqd,value/min,value/max]
```


4. Align tasks
```bash
export TASK="anemia"

meds-tab-cache-task \
    --multirun \
    hydra/launcher=joblib \
    worker="range(0,10)" \
    "input_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/MEDS_cohort/data" \
    "output_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/tabular" \
    "input_label_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/tasks/$TASK" \
    "task_name=$TASK" \
    tabularization.min_code_inclusion_count=10 \
    tabularization.window_sizes=[1d] \
    tabularization.aggs=[static/present,code/count,value/count,value/sum,value/sum_sqd,value/min,value/max]
```

5. Run the XGBoost
```bash
export TASK="short_los"

meds-tab-model \
    model_launcher=xgboost \
    "input_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/MEDS_cohort/data" \
    "output_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/tabular" \
    "output_model_dir=/home/exet6188/Code/JZ_MIMIC_IV_MEDS/data/mimiciv_meds/baselines/$TASK/" \
    "task_name=$TASK" \
    tabularization.min_code_inclusion_count=10 \
    tabularization.window_sizes=[1d] \
    tabularization.aggs=[static/present,code/count,value/count,value/sum,value/sum_sqd,value/min,value/max]
```