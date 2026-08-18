import pandas as pd
import pytest

from ena_upload.ena_upload import validate_run_table


def test_validate_run_table_accepts_simple_paired_fastq_without_read_type():
    run_df = pd.DataFrame(
        [
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "sample_1_R1.fastq.gz",
                "file_type": "fastq",
            },
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "sample_1_R2.fastq.gz",
                "file_type": "fastq",
            },
        ]
    )

    validate_run_table(run_df)


def test_validate_run_table_accepts_true_multi_fastq_read_types():
    run_df = pd.DataFrame(
        [
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "single_cell_I1.fastq.gz",
                "file_type": "fastq",
                "read_type": "feature_barcode",
            },
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "single_cell_R1.fastq.gz",
                "file_type": "fastq",
                "read_type": "paired,umi_barcode",
            },
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "single_cell_R2.fastq.gz",
                "file_type": "fastq",
                "read_type": "sample_barcode",
            },
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "single_cell_R3.fastq.gz",
                "file_type": "fastq",
                "read_type": "paired,cell_barcode",
            },
        ]
    )

    validate_run_table(run_df)


def test_validate_run_table_rejects_paired_only_multi_fastq():
    run_df = pd.DataFrame(
        [
            {
                "alias": "run_merged",
                "experiment_alias": "experiment_1",
                "file_name": "sample_1_R1.fastq.gz",
                "file_format": "fastq",
                "read_type": "paired",
            },
            {
                "alias": "run_merged",
                "experiment_alias": "experiment_1",
                "file_name": "sample_1_R2.fastq.gz",
                "file_format": "fastq",
                "read_type": "paired",
            },
            {
                "alias": "run_merged",
                "experiment_alias": "experiment_1",
                "file_name": "sample_2_R1.fastq.gz",
                "file_format": "fastq",
                "read_type": "paired",
            },
            {
                "alias": "run_merged",
                "experiment_alias": "experiment_1",
                "file_name": "sample_2_R2.fastq.gz",
                "file_format": "fastq",
                "read_type": "paired",
            },
        ]
    )

    with pytest.raises(ValueError, match="only simple read_type values"):
        validate_run_table(run_df)


def test_validate_run_table_rejects_invalid_read_type():
    run_df = pd.DataFrame(
        [
            {
                "alias": "run_1",
                "experiment_alias": "experiment_1",
                "file_name": "sample_1_R1.fastq.gz",
                "file_type": "fastq",
                "read_type": "forward",
            },
        ]
    )

    with pytest.raises(ValueError, match="Invalid read_type"):
        validate_run_table(run_df)


def test_validate_run_table_rejects_multiple_experiments_per_run():
    run_df = pd.DataFrame(
        [
            {
                "alias": "run_merged",
                "experiment_alias": "experiment_1",
                "file_name": "sample_1_R1.fastq.gz",
                "file_type": "fastq",
            },
            {
                "alias": "run_merged",
                "experiment_alias": "experiment_2",
                "file_name": "sample_2_R1.fastq.gz",
                "file_type": "fastq",
            },
        ]
    )

    with pytest.raises(ValueError, match="can reference only one experiment_alias"):
        validate_run_table(run_df)
