import os
import pandas as pd


output_folder = r"D:\wsf-sat\methods\threshold_analysis\04_IntersectOverUnion"

# read results
df = pd.read_csv(os.path.join(output_folder, "thresholds_results.txt"), sep=" ")
print(df)

df_mean_iou = df.groupby("threshold").agg({"intersection_over_union": "mean"})
print(df_mean_iou)