import SpeedValidation as SV
import path_links
from os import path
from arcpy import Exists, Delete_management
import traceback, sys

# import shapefiles to main gdb

fips_list = ["23"]

for x in fips_list:
    try:


        # import shapefiles to main gdb
        importSHP = SV.SpeedChecker()
        importSHP.inputpath = path.join(path_links.baseline_05jan2018, "baseline_"+x)
        importSHP.outputGDBName = "baseline_"+x
        importSHP.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        importSHP.create_folder()
        if Exists(path.join(importSHP.outputpathfolder, importSHP.outputGDBName+".gdb")):
            Delete_management(path.join(importSHP.outputpathfolder, importSHP.outputGDBName+".gdb"))
        importSHP.create_gdb()
        importSHP.outputGDB = path.join(importSHP.outputpathfolder, importSHP.outputGDBName+".gdb")
        importSHP.import_shapefiles_to_gdb("coverage_map_*")
        importSHP.import_shapefiles_to_gdb("state_boundary_*")
        importSHP.make_grid_id(importSHP.outputGDB)
        importSHP.define_projection(input_gdb=importSHP.outputGDB, wildcard="*")

        print("01: filter out the speed points with the state grid for each users")
        pointIntersect = SV.SpeedChecker()
        pointIntersect.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        pointIntersect.outputGDBName = "_01_selected_points"
        pointIntersect.create_gdb()
        pointIntersect.inputGDB = importSHP.outputGDB

        pointIntersect.inputGDB2 = path.join(path_links.speed_point_inputs_base,"speed_points_state_{}".format(x),"User_points_pid.gdb")
        print(pointIntersect.inputGDB2)
        pointIntersect.outputGDB = path.join(pointIntersect.outputpathfolder, pointIntersect.outputGDBName+".gdb")
        pointIntersect.intersect_speed_points_with_state_files(fc1_wildcard="state_boundary_{}".format(x), fc2_wildcard="*")
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
        buffer.buffer_points(250)

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
        merge_grid.merge_measured_unmeasured_coverages(path_links.number_of_users)


        print("10: create unmeasured area")
        _merge_diss_grid = SV.SpeedChecker()
        _merge_diss_grid.inputGDB = merge_grid.outputGDB
        _merge_diss_grid.outputGDBName = "_10_diss_merged_unmeasured_coverages"
        _merge_diss_grid.outputpathfolder = path.join(path_links.input_base_folder,importSHP.outputGDBName)
        _merge_diss_grid.create_gdb()
        _merge_diss_grid.outputGDB = path.join(_merge_diss_grid.outputpathfolder, _merge_diss_grid.outputGDBName + ".gdb")
        _merge_diss_grid.diss_merge_unmeasured_coverages()
        _merge_diss_grid.addField(input_gdb=_merge_diss_grid.outputGDB, fc_wildcard="*",field_name="agg_unmeasured_area", field_type="Double")
        _merge_diss_grid.calculateField(field_name="agg_unmeasured_area",expression="!Shape.geodesicArea@SQUAREMETERS!",
                                 input_gdb= _merge_diss_grid.outputGDB, fc_wildcard="*")

        print("11: Validate Coverages")

        validate_results = SV.SpeedChecker()
        validate_results.inputGDB = _merge_diss_grid.outputGDB
        validate_results.inputGDB2 = importSHP.outputGDB
        validate_results.outputGDBName = "_11_validated_results"
        validate_results.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
        validate_results.create_gdb()
        validate_results.outputGDB = path.join(validate_results.outputpathfolder, validate_results.outputGDBName + ".gdb")
        validate_results.create_results()
        validate_results.inputGDB = validate_results.outputGDB
        validate_results.calculate_results()

        print("12: Export Resutls")

        export_results = SV.SpeedChecker()
        export_results.inputGDB = validate_results.outputGDB
        export_results.outputfolder_name = "results"
        export_results.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName, export_results.outputfolder_name)
        export_results.create_folder()
        export_results.attribute_table_to_csv(field_names=["STATE_FIPS", "GRID_COL", "GRID_ROW", "agg_unmeasured","agg_unmeasured_pct", "agg_measured_pct"])






    except:


        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg)














