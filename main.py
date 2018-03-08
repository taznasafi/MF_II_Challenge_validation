import SpeedValidation as SV
import path_links
from os import path
from arcpy import Exists, Delete_management


# import shapefiles to main gdb

fips_list = ["55"]

for x in fips_list:

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
    importSHP.import_shapefiles_to_gdb("*")

    # 01: filter out the speed points with the state grid for each users
    pointIntersect = SV.SpeedChecker()
    pointIntersect.outputpathfolder = path.join(path_links.input_base_folder, importSHP.outputGDBName)
    pointIntersect.outputGDBName = "_01_selected_points"
    pointIntersect.create_gdb()
    pointIntersect.inputGDB = importSHP.outputGDB
    pointIntersect.inputGDB2 = path_links.user_input_speed_points_gdb_path
    pointIntersect.outputGDB = path.join(pointIntersect.outputpathfolder, pointIntersect.outputGDBName+".gdb")
    pointIntersect.intersect_speed_points_with_state_files(fc1_wildcard="state_boundary_{}".format(x), fc2_wildcard="*")

    #02: intersect the points with with its own respective coverage

    coverageIntersect = SV.SpeedChecker()
    coverageIntersect.inputGDB = importSHP.outputGDB
    coverageIntersect.inputGDB2 = pointIntersect.outputGDB
    coverageIntersect.outputGDBName = "_02_coverage_points"
    coverageIntersect.outputpathfolder = path.join(path_links.input_base_folder, "baseline_55")
    coverageIntersect.create_gdb()
    coverageIntersect.outputGDB = path.join(coverageIntersect.outputpathfolder, coverageIntersect.outputGDBName + ".gdb")
    coverageIntersect.intersect_intersect_points_with_coverages(number_of_users=path_links.number_of_users)
    SV.SpeedChecker.deleteEmptyfeaturesFiles(coverageIntersect.outputGDB)








