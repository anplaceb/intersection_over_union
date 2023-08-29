import arcpy
import os
import re

# Paths
reference_data_Friederike_2018 = r"D:\wsf-sat\data\validation\Friedericke_2018\shp\Friederike_2018_kartiergebiet_zeitangepasst_nachkartiert260421_filter025.shp"
reference_data_Friederike_2019 = r"D:\wsf-sat\data\validation\Friedericke_2019\fried_2019_kartiergebiet_zeitangepasst_nachkartiert_260421_filter025.shp"
reference_data_Harz_2021 = r"D:\wsf-sat\data\validation\Harz_2021\shp\Harz_Freiflaeche_stehendesTotholz_2021_025_clipNds.shp"
detection_folder = r"D:\wsf-sat\methods\threshold_analysis\03_postprocessing"
output_folder = r"D:\wsf-sat\methods\threshold_analysis\04_IntersectOverUnion"

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
if not os.path.isfile(os.path.join(output_folder, "thresholds_results.txt")):
    with open(os.path.join(output_folder, "thresholds_results.txt"), "w") as a:
        a.write("threshold year area_intersect_ha area_union_ha intersection_over_union" + "\n")
    a.close()

for detection_file in detection_files:
    year = re.findall(r"(?<!\d)\d{4}(?!\d)", os.path.basename(detection_file))[0]  # search for current year
    print(f'file: {os.path.basename(detection_file)}, year: {year}')
    if year == "2018":
        reference_data = reference_data_Friederike_2018
        print(f"Year: {year}, reference data: {reference_data}")
    elif year == "2019":
        reference_data = reference_data_Friederike_2019
        print(f"Year: {year}, reference data: {reference_data}")
    elif year == "2021":
        reference_data = reference_data_Harz_2021
        print(f"Year: {year}, reference data: {reference_data}")
    else:
        print("No reference data for this year")
        break

    threshold = re.findall(r"(?<!\d)m\d{2}(?!\d)", os.path.basename(detection_file))[0]

    id_detection = f"{threshold}_{year}"
    print(id_detection)

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

    with open(os.path.join(output_folder, "thresholds_results.txt"), "a") as a:
        intersection_over_union = round(area_sum_intersect/area_sum_union * 100, 2)
        a.write(" ".join([threshold, year, str(area_sum_intersect/10000),
                          str(area_sum_union/10000), str(intersection_over_union)]) +"\n")
        a.close()


