import SpeedValidation as SV
import path_links
from os import path
from arcpy import Exists, Delete_management
import traceback, sys
import path_links
# import shapefiles to main gdb

number_of_users = input("what is the number of users:    ")
if number_of_users =="":
    path_links.number_of_users = None
else:
    path_links.number_of_users = int(number_of_users)

buffer_size = int(input("what is the buffer size in meters: "))
fips_list = ["20"]

for state in fips_list:
    try:


        # import shapefiles to main gdb
        importSHP = SV.SpeedChecker()
        importSHP.inputpath = path.join(path_links.USAC_baseline, "baseline_" + state)
        importSHP.outputGDBName = "baseline_" + state
        importSHP.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        importSHP.create_folder()
        if Exists(path.join(importSHP.outputpathfolder, importSHP.outputGDBName+".gdb")):
            pass
            Delete_management(path.join(importSHP.outputpathfolder, importSHP.outputGDBName+".gdb"))
        importSHP.create_gdb()
        importSHP.outputGDB = path.join(importSHP.outputpathfolder, importSHP.outputGDBName+".gdb")
        importSHP.import_shapefiles_to_gdb("coverage_map_*")
        importSHP.import_shapefiles_to_gdb("state_boundary_*")
        importSHP.make_grid_id(importSHP.outputGDB)
        importSHP.define_projection(input_gdb=importSHP.outputGDB, wildcard="*")
        importSHP.repair_geom(input_GDB=importSHP.outputGDB)

        print("01: filter out the speed points with the state grid for each users")
        pointIntersect = SV.SpeedChecker()
        pointIntersect.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        pointIntersect.outputGDBName = "_01_selected_points"
        pointIntersect.create_gdb()
        pointIntersect.inputGDB = importSHP.outputGDB

        pointIntersect.inputGDB2 = path.join(path_links.speed_point_inputs_base,"speed_points_state_{}".format(state), "User_points_pid.gdb")
        print(pointIntersect.inputGDB2)
        pointIntersect.outputGDB = path.join(pointIntersect.outputpathfolder, pointIntersect.outputGDBName+".gdb")
        pointIntersect.intersect_speed_points_with_state_files(fc1_wildcard="state_boundary_{}".format(state), fc2_wildcard="*")
        pointIntersect.deleteEmptyfeaturesFiles(pointIntersect.outputGDB)



        print("02: intersect the points with with its own respective coverage (this will be the reference next steps")

        coverageIntersect = SV.SpeedChecker()
        coverageIntersect.inputGDB = importSHP.outputGDB
        coverageIntersect.inputGDB2 = pointIntersect.outputGDB
        coverageIntersect.outputGDBName = "_02_coverage_points"
        coverageIntersect.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        coverageIntersect.create_gdb()
        coverageIntersect.outputGDB = path.join(coverageIntersect.outputpathfolder, coverageIntersect.outputGDBName + ".gdb")
        coverageIntersect.intersect_points_with_coverages(number_of_users=path_links.number_of_users)
        SV.SpeedChecker.deleteEmptyfeaturesFiles(coverageIntersect.outputGDB)

        print("03: Merge the point")

        mergePoints = SV.SpeedChecker()
        mergePoints.inputGDB = coverageIntersect.outputGDB
        mergePoints.outputGDBName = "_03_merge_coverage_points"
        mergePoints.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        mergePoints.create_gdb()
        mergePoints.outputGDB = path.join(mergePoints.outputpathfolder, mergePoints.outputGDBName + ".gdb")
        mergePoints.merge_points(number_of_users=path_links.number_of_users)


        print("04: select_state_boundary by using the merged points")

        select = SV.SpeedChecker()
        select.inputGDB = importSHP.outputGDB
        select.inputGDB2 = mergePoints.outputGDB
        select.outputGDBName = "_04_selected_state_boundary"
        select.outputpathfolder = path.join(path_links.input_base_folder,importSHP.outputGDBName)
        select.create_gdb()
        select.outputGDB = path.join(select.outputpathfolder, select.outputGDBName + ".gdb")
        select.select_state_boundary_grid_cells(path_links.number_of_users)

        print("05: buffered the filtered points from step 1")

        buffer = SV.SpeedChecker()
        buffer.inputGDB = pointIntersect.outputGDB
        buffer.outputGDBName = "_05_buffered_polygons"
        buffer.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        buffer.create_gdb()
        buffer.outputGDB = path.join(buffer.outputpathfolder, buffer.outputGDBName + ".gdb")
        buffer.buffer_points(buffer_distance=buffer_size)

        print("06: Intersect the buffered polygons with its own respective the coverage (measured Coverage)")

        coverageIntersectBuffer = SV.SpeedChecker()
        coverageIntersectBuffer.referenceGDB = coverageIntersect.outputGDB
        coverageIntersectBuffer.inputGDB = importSHP.outputGDB
        coverageIntersectBuffer.inputGDB2 = buffer.outputGDB
        coverageIntersectBuffer.outputGDBName = "_06_intersect_buffered_polygons_coverages"
        coverageIntersectBuffer.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        coverageIntersectBuffer.create_gdb()
        coverageIntersectBuffer.outputGDB = path.join(coverageIntersectBuffer.outputpathfolder, coverageIntersectBuffer.outputGDBName + ".gdb")
        coverageIntersectBuffer.intersect_buffered_area_with_coverage(path_links.number_of_users)

        print("07: create selected coverage")

        selectCoverage = SV.SpeedChecker()
        selectCoverage.referenceGDB = coverageIntersect.outputGDB
        selectCoverage.inputGDB = importSHP.outputGDB
        selectCoverage.inputGDB2 = select.outputGDB
        selectCoverage.outputGDBName = "_07_selected_coverage"
        selectCoverage.outputpathfolder = path.join(path_links.input_base_folder,importSHP.outputGDBName)
        selectCoverage.create_gdb()
        selectCoverage.outputGDB = path.join(selectCoverage.outputpathfolder, selectCoverage.outputGDBName + ".gdb")
        selectCoverage.select_Coverage_by_selected_grid(path_links.number_of_users)
        selectCoverage.repair_geom(input_GDB=selectCoverage.outputGDB)


        print("08: erase the measured coverages from the selected coverage")


        eraseMeasuredCoverage = SV.SpeedChecker()
        eraseMeasuredCoverage.referenceGDB = coverageIntersect.outputGDB
        eraseMeasuredCoverage.inputGDB = selectCoverage.outputGDB
        eraseMeasuredCoverage.inputGDB2 = coverageIntersectBuffer.outputGDB
        eraseMeasuredCoverage.outputGDBName = "_08_unmeasured_coverages"
        eraseMeasuredCoverage.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        eraseMeasuredCoverage.create_gdb()
        eraseMeasuredCoverage.outputGDB = path.join(eraseMeasuredCoverage.outputpathfolder, eraseMeasuredCoverage.outputGDBName + ".gdb")
        eraseMeasuredCoverage.erase_measured_from_selected_coverage(path_links.number_of_users)

        print("09 merged")

        merge_grid = SV.SpeedChecker()
        merge_grid.inputGDB = eraseMeasuredCoverage.outputGDB
        merge_grid.outputGDBName = "_09_merged_unmeasured_coverages"
        merge_grid.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        merge_grid.create_gdb()
        merge_grid.outputGDB = path.join(merge_grid.outputpathfolder, merge_grid.outputGDBName + ".gdb")
        merge_grid.merge_unmeasured_coverages(path_links.number_of_users)


        print("10: create unmeasured area by dissovling the state fips, grid row, grid column, and id")
        _merge_diss_grid = SV.SpeedChecker()
        _merge_diss_grid.inputGDB = merge_grid.outputGDB
        _merge_diss_grid.outputGDBName = "_10_diss_merged_unmeasured_coverages"
        _merge_diss_grid.outputpathfolder = path.join(path_links.input_base_folder,importSHP.outputGDBName)
        _merge_diss_grid.create_gdb()
        _merge_diss_grid.outputGDB = path.join(_merge_diss_grid.outputpathfolder, _merge_diss_grid.outputGDBName + ".gdb")
        _merge_diss_grid.diss_by_grid(dissolved_field=["STATE_FIPS", "GRID_COL", "GRID_ROW", "ID"])


        print("11: Create mearged selected coverages area")
        _merge_selected_coverage = SV.SpeedChecker()
        _merge_selected_coverage.inputGDB = selectCoverage.outputGDB
        _merge_selected_coverage.outputGDBName = "_11_merged_selected_coverages"
        _merge_selected_coverage.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        _merge_selected_coverage.create_gdb()
        _merge_selected_coverage.outputGDB = path.join(_merge_selected_coverage.outputpathfolder,
                                                           _merge_selected_coverage.outputGDBName + ".gdb")
        _merge_selected_coverage.merge_selected_coverages(number_of_users=path_links.number_of_users)


        print("11A: Erase unmeasured area from merged selected area")

        create_measured_area = SV.SpeedChecker()
        create_measured_area.inputGDB = _merge_selected_coverage.outputGDB
        create_measured_area.inputGDB2 = merge_grid.outputGDB
        create_measured_area.outputGDBName = "_11A_erase_unmeasured_from_selected_coverages"
        create_measured_area.outputpathfolder = path.join(path_links.input_base_folder,
                                                          importSHP.outputGDBName)
        create_measured_area.create_gdb()
        create_measured_area.outputGDB = path.join(create_measured_area.outputpathfolder,
                                                   create_measured_area.outputGDBName + ".gdb")

        create_measured_area.erase_unmeasured_from_merged_coverage(path_links.number_of_users)

        print("11B: Merge accross user")
        merge_accross_user = SV.SpeedChecker()
        merge_accross_user.inputGDB = create_measured_area.outputGDB
        merge_accross_user.outputGDBName = "_11B_merged_measured_area"
        merge_accross_user.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        merge_accross_user.create_gdb()
        merge_accross_user.outputGDB = path.join(merge_accross_user.outputpathfolder, merge_accross_user.outputGDBName+".gdb")
        merge_accross_user.merge_general("_merged_mersured_area")

        print("11C: Dissovle by PID")
        diss_fc = SV.SpeedChecker()
        diss_fc.inputGDB = merge_accross_user.outputGDB
        diss_fc.outputGDBName = "_11C_dissovled_by_PID_measured_area"
        diss_fc.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        diss_fc.create_gdb()
        diss_fc.outputGDB = path.join(diss_fc.outputpathfolder,
                                      diss_fc.outputGDBName + ".gdb")
        diss_fc.diss_general(output_name="diss_measured_area",wildcard="_merged_mersured_area", dissolve_field="")



        print("11D: Intersect with the state Grid")
        intersect_grid = SV.SpeedChecker()
        intersect_grid.inputGDB = importSHP.outputGDB
        intersect_grid.inputGDB2 = diss_fc.outputGDB
        intersect_grid.outputGDBName = "_11D_intersect_measured_area_with_state_grid"
        intersect_grid.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        intersect_grid.create_gdb()
        intersect_grid.outputGDB = path.join(intersect_grid.outputpathfolder, intersect_grid.outputGDBName+".gdb")
        intersect_grid.intersect_general("measured_area_PASI",
                                         wildcard_1="state_boundary_{}".format(state),
                                         wildcard_2="diss_measured_area")

        intersect_grid.addField(input_gdb=intersect_grid.outputGDB,
                                fc_wildcard="*",
                                field_name="PASI_agg_measured",
                                field_type="Double")

        intersect_grid.calculateField(input_gdb=intersect_grid.outputGDB,
                                      fc_wildcard="*",
                                      field_name="PASI_agg_measured",
                                      expression="!Shape.geodesicArea@SQUAREMETERS!")

        print("11E: Split the measured area by pid")
        split_measured_area = SV.SpeedChecker()
        split_measured_area.inputGDB = intersect_grid.outputGDB
        split_measured_area.outputGDBName = "_11E_split_by_PID_across_users"
        split_measured_area.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        split_measured_area.create_gdb()
        split_measured_area.outputGDB = path.join(split_measured_area.outputpathfolder,
                                                  split_measured_area.outputGDBName + ".gdb")
        split_measured_area.split_general(split_field=["PID"])


        print("12: Dissolve the merged selected coverages by grid")
        _diss_merge_selected_coverage = SV.SpeedChecker()
        _diss_merge_selected_coverage.inputGDB = _merge_selected_coverage.outputGDB
        _diss_merge_selected_coverage.outputGDBName = "_12_diss_merged_selected_coverages"
        _diss_merge_selected_coverage.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        _diss_merge_selected_coverage.create_gdb()
        _diss_merge_selected_coverage.outputGDB = path.join(_diss_merge_selected_coverage.outputpathfolder,
                                                            _diss_merge_selected_coverage.outputGDBName + ".gdb")
        _diss_merge_selected_coverage.diss_by_grid(dissolved_field=["STATE_FIPS", "GRID_COL", "GRID_ROW", "ID"])


        print("13: Erase dissovled unmeasured area from dissovled merged selected area")

        create_measured_area = SV.SpeedChecker()
        create_measured_area.inputGDB = _diss_merge_selected_coverage.outputGDB
        create_measured_area.inputGDB2 = _merge_diss_grid.outputGDB
        create_measured_area.outputGDBName = "_13_erase_unmeasured_from_selected_coverages"
        create_measured_area.outputpathfolder = path.join(path_links.input_base_folder,
                                                                   importSHP.outputGDBName)
        create_measured_area.create_gdb()
        create_measured_area.outputGDB = path.join(create_measured_area.outputpathfolder,
                                                   create_measured_area.outputGDBName + ".gdb")

        create_measured_area.erase_unmeasured_from_merged_coverage(path_links.number_of_users)
        create_measured_area.addField(create_measured_area.outputGDB, "*", "agg_measured_raw", "Double")
        create_measured_area.calculateField(input_gdb=create_measured_area.outputGDB,fc_wildcard="*",
                                        field_name="agg_measured_raw",expression="!Shape.geodesicArea@SQUAREMETERS!")

        print("14: Validate Coverages")

        validate_results = SV.SpeedChecker()
        validate_results.inputGDB = create_measured_area.outputGDB
        validate_results.inputGDB2 = importSHP.outputGDB
        validate_results.outputGDBName = "_14_validated_results"
        validate_results.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        validate_results.create_gdb()
        validate_results.outputGDB = path.join(validate_results.outputpathfolder, validate_results.outputGDBName + ".gdb")
        validate_results.create_results()
        validate_results.inputGDB = validate_results.outputGDB
        validate_results.calculate_results()

        print("15: Export Resutls")

        export_results = SV.SpeedChecker()
        export_results.inputGDB = validate_results.outputGDB
        export_results.outputfolder_name = "results"
        export_results.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName, export_results.outputfolder_name)
        export_results.create_folder()
        export_results.attribute_table_to_csv(field_names=["STATE_FIPS", "GRID_COL", "GRID_ROW",
                                                           "AREA", "WATER_AREA", "NONWO_AREA",
                                                           "ELIG_AREA", "CH_AREA", "ID",
                                                           "agg_measured", "agg_measured_pct",
                                                           "agg_unmeasured", "agg_unmeasured_pct"])

        print("16: Export points for USAC systems")

        point_exporter = SV.SpeedChecker()
        point_exporter.inputGDB = pointIntersect.outputGDB
        point_exporter.inputGDB2 = importSHP.outputGDB
        point_exporter.outputfolder_name = "points_for_upload"
        point_exporter.outputpathfolder = path.join(path_links.input_base_folder, "baseline_" + state, "results",
                                                    point_exporter.outputfolder_name)
        point_exporter.create_folder()
        point_exporter.export_points_for_USAC(search_distance=0.7)


    except:


        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)














