"""
The original data was exported as a CSV on July 17, 2024, from https://trade.cites.org/, with the following filters:
- Source: "W-wild"
- Purposes: "T-commercial"
- Trade terms: "live" and "meat"
- Years: 2010 only (commercial_live-meat_2010.csv) resp. 2020 only (commercial_live-meat_2020.csv)

Data citation:
CITES Trade Database 2024. Compiled by UNEP-WCMC for the CITES Secretariat. Available
at: trade.cites.org. Accessed July 17, 2024.

This script uses polars for preprocessing (pip install polars), just for fun.
"""
import polars as pl

def preprocess_data():

    df_2010 = pl.read_csv("commercial_live-meat_2010.csv", infer_schema_length=10000)
    df_2020 = pl.read_csv("commercial_live-meat_2020.csv", infer_schema_length=10000)
    df = pl.concat([df_2010, df_2020])

    df_agg = df.with_columns(pl.max_horizontal(pl.col("Importer reported quantity"),pl.col("Exporter reported quantity")).alias("Max_reported_quantity"),
                             pl.col("Unit").replace("","Number of specimens")
                        ).filter(
        ((pl.col("Term") == "live") & (pl.col("Unit").is_in(["Number of specimens"])))
        | ((pl.col("Term") == "meat") & (pl.col("Unit").is_in(["kg"])))
        & (pl.col("Source") == "W")
                        ).group_by([pl.col("Year"), pl.col("Term"),pl.col("Importer"),pl.col("Exporter")]).agg(pl.col("Max_reported_quantity").sum(),
                                                                                                               pl.col("Unit").max()
    ).sort([pl.col("Year"), pl.col("Term"), pl.col("Importer"), pl.col("Exporter")])

    df_agg.write_csv("commercial_live-leather_2010-2020.csv")

if __name__ == "__main__":
    preprocess_data()