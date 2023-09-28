"""Given a reference geometry and a detection geometry, calculate intersection over union and write it to .txt file"""
import arcpy
import os
import re

# Paths
reference_data = r"D:\wsf-sat\data\validation\Harz_Freiflaeche_Totholz_2018_2021\Harz_Freifl_Totholz_2020_ni.shp"
detection_folder = r"D:\wsf-sat\methods\validation\intersect_over_union_rf\input_detection\harz_2020"
output_folder = r"D:\wsf-sat\methods\validation\intersect_over_union_rf\output\harz_2020"
id_detection = "harz_2020"

if not os.path.isdir(os.path.join(output_folder, "IntersectOverUnion.gdb")):
    arcpy.CreateFileGDB_management(output_folder, "IntersectOverUnion")

# Environment
arcpy.env.overwriteOutput = True
arcpy.env.workspace = os.path.join(output_folder, "IntersectOverUnion.gdb")

# List detection files in sub-dirs
detection_files = [os.path.join(root, name)
                   for root, dirs, files in os.walk(detection_folder)
                   for name in files
                   if name.endswith(".shp")]
detection_files = [file for file in detection_files if not "temp" in file]  # filter temp files
print(list(map(os.path.basename, detection_files)))


# Create textfile to write results
if not os.path.isfile(os.path.join(output_folder, "results.txt")):
    with open(os.path.join(output_folder, "results.txt"), "w") as a:
        a.write("id area_intersect_ha area_union_ha intersection_over_union" + "\n")
    a.close()

for detection_file in detection_files:

    # Intersect reference and detection
    arcpy.Intersect_analysis(in_features=[reference_data, detection_file],
                             out_feature_class=f"intersect_{id_detection}")

    arcpy.Statistics_analysis(in_table=f"intersect_{id_detection}",
                              out_table=f"intersect_{id_detection}_area_sum",
                              statistics_fields="Shape_Area SUM")

    # Union of reference and detection
    arcpy.Union_analysis(in_features=[reference_data, detection_file],
                         out_feature_class=f"union_{id_detection}")

    arcpy.Statistics_analysis(in_table=f"union_{id_detection}",
                              out_table=f"union_{id_detection}_area_sum",
                              statistics_fields="Shape_Area SUM")
    print(f"Fertig {detection_file}")

# Get values and write in table
    with arcpy.da.UpdateCursor(f"intersect_{id_detection}_area_sum", ["SUM_Shape_Area"]) as cursor:
        for row in cursor:
            area_sum_intersect = row[0]
            print(area_sum_intersect)

    with arcpy.da.UpdateCursor(f"union_{id_detection}_area_sum", ["SUM_Shape_Area"]) as cursor:
        for row in cursor:
            area_sum_union = row[0]
            print(area_sum_union)

    with open(os.path.join(output_folder, "results.txt"), "a") as a:
        intersection_over_union = round(area_sum_intersect/area_sum_union * 100, 2)
        print(intersection_over_union)
        a.write(" ".join([id_detection, str(area_sum_intersect/10000),
                          str(area_sum_union/10000), str(intersection_over_union)]) +"\n")
        a.close()


