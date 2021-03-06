import arcpy
import sys
import traceback
import logging
import time
import get_path
import os
from re import match, search
import pandas as pd

formatter = ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(filename=r"{}_Log_{}.csv".format(__name__.replace(".", "_"), time.strftime("%Y_%m_%d_%H_%M")),
                                 level=logging.DEBUG, format=formatter)

class SpeedChecker:
    def __init__(self, input_path=None, inputGDB=None, inputGDB2 = None, referenceGDB = None,
                 outputGDBname=None, outputpathfolder=None, outputfolder_name = None, outputGDB=None):
        self.inputpath = input_path
        self.inputGDB = inputGDB
        self.inputGDB2 = inputGDB2
        self.referenceGDB = referenceGDB
        self.outputGDBName = outputGDBname
        self.outputpathfolder = outputpathfolder
        self.outputfolder_name = outputfolder_name
        self.outputGDB = outputGDB

        arcpy.env.qualifiedFieldNames = False
        arcpy.env.overwriteOutput = False

    def create_folder(self):
        print("creating folder")
        logging.info("creating folder")
        try:
            if not os.path.exists(self.outputpathfolder):
                os.makedirs(self.outputpathfolder)

        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            message = "Traceback info:\n" + tbinfo
            print(message)
            logging.warning(message)

    def create_gdb(self):
        print("Creating gdb")
        logging.info("Creating GDB named: {}".format(self.outputGDBName))
        try:
            arcpy.CreateFileGDB_management(out_folder_path=self.outputpathfolder, out_name=self.outputGDBName)
            print(arcpy.GetMessages(0))
            logging.info("created GDB, messages: {}".format(arcpy.GetMessages(0)))


        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
            logging.info(msgs)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.info(pymsg)
            logging.info(msgs)

    def define_projection(self, input_gdb, wildcard):
        logging.info("define projection")
        try:

            fc_list = get_path.pathFinder(env_0=input_gdb).get_file_path_with_wildcard_from_gdb(wildcard)

            for fc in fc_list:
                print("Defining projection for: {}.".format(os.path.basename(fc)))
                arcpy.DefineProjection_management(fc, coor_system=r"GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
                logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
            logging.info(msgs)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.info(pymsg)
            logging.info(msgs)

    @classmethod
    def make_grid_id(cls, input_path):
        print("createing Grid IDs")
        fc_list = get_path.pathFinder(env_0=input_path).get_path_for_all_feature_from_gdb()
        #id_fields = ["STATE_FIPS", "GRID_COL", "GRID_ROW"]


        for x in fc_list:

            arcpy.AddField_management(x,"ID","Text")

            codeblock = """def cont(x, y ,z):return str(x)+str(y)+str(z)"""

            arcpy.CalculateField_management(x,"ID", "cont({},{},{})".format("!STATE_FIPS!","!GRID_COL!", "!GRID_ROW!"),
                                            expression_type="PYTHON3",
                                            code_block=codeblock)
            print("added id field to: {}".format(os.path.basename(x)))

    @classmethod
    def deleteEmptyfeaturesFiles(cls, path, type=None):
        print("looking for features to delete")
        print(path)
        try:

            gdb = get_path.pathFinder(env_0=path)
            fcList = gdb.get_path_for_all_feature_from_gdb(type)
            #print(fcList)

            for x in fcList:
                #print(x)
                result = arcpy.GetCount_management(x)
                count = int(result[0])
                if count == 0:
                    print("deleting file: {}".format(x))
                    arcpy.Delete_management(x)
                    print(arcpy.GetMessages(0))
                    logging.info("Deleted: {}".format(x))



        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(
                sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)

    @classmethod
    def addField(cls, input_gdb, fc_wildcard, field_name, field_type, field_length=None):
        logging.info("add field: {}, type: {}".format(field_name, field_type))
        fc_list = get_path.pathFinder(env_0=input_gdb).get_file_path_with_wildcard_from_gdb(fc_wildcard)

        for fc in fc_list:

            print(os.path.basename(fc))
            arcpy.AddField_management(fc,field_name,field_type,field_length=field_length)
            print(arcpy.GetMessages(0))

    @classmethod
    def calculateField(cls, input_gdb, fc_wildcard, field_name, expression):
        logging.info("calucating field for {} with this expression: {}".format(field_name, expression))
        fc_list = get_path.pathFinder(env_0=input_gdb).get_file_path_with_wildcard_from_gdb(fc_wildcard)

        for fc in fc_list:
            print(os.path.basename(fc))
            arcpy.CalculateField_management(fc,field_name,expression, expression_type="PYTHON3")
            print(arcpy.GetMessages(0))

    def import_shapefiles_to_gdb(self, wildcard=None):
        logging.info("importing shapefiles")

        shplist = get_path.pathFinder.get_shapefile_path_wildcard(self.inputpath, wildcard)

        print("\nI found {} files to import!!!".format(len(shplist)))

        try:
            for x in shplist:
                name = os.path.split(x)[1]
                output = os.path.join(self.outputGDB, name.strip(".shp"))
                print(output)
                logging.info("Importing: {}".format(name.strip(".shp")))
                if arcpy.Exists(output):
                    print("exists, passing over this fc")
                    logging.warning("{} exists, passing over this fc".format(name.strip(".shp")))
                else:
                    arcpy.FeatureClassToGeodatabase_conversion(x, self.outputGDB)
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.error(pymsg)

    def intersect_speed_points_with_state_files(self, fc1_wildcard, fc2_wildcard):
        try:
            #fc1 is state boundary feature class
            fc1 = get_path.pathFinder(env_0=self.inputGDB)
            fc1_list = fc1.get_file_path_with_wildcard_from_gdb(fc1_wildcard)

            #fc2 is provider speed tests
            fc2 = get_path.pathFinder(env_0=self.inputGDB2)
            fc2_list = fc2.get_file_path_with_wildcard_from_gdb(fc2_wildcard)

            if len(fc1_list)==0 or len(fc2_list)==0:
                print("one or more parameter is is missing")

            for x in fc2_list:
                if arcpy.Exists(os.path.join(self.outputGDB, os.path.basename(x))):
                    print("the file exists, skipping!!!!")
                else:

                    logging.info("intersecting {} with {}".format(fc1_list[0], x))

                    inlist = [fc1_list[0],x]

                    print("intersect......plz wait!!")
                    logging.info("intersecting files")
                    arcpy.Intersect_analysis(inlist, os.path.join(self.outputGDB, os.path.basename(x)))
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def intersect_points_with_coverages(self, number_of_users=None):
        print("intersecting points with coverages")

        coverages = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb("Coverage_map_*")

        for coverage in coverages:

            try:

                regex =r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)$"
                namedic = match(regex, os.path.basename(coverage)).groupdict()

                pid = str(int(namedic['pid']))

                print(pid)

                users_points = get_path.pathFinder(env_0=self.inputGDB2)

                if number_of_users == None:
                    print("no users specified in the input, parsing input points for users")

                    all_users_list = users_points.get_path_for_all_feature_from_gdb(type="point")

                    user_regex = r"User_(?P<userid>\d{1,3})_(?P<pid>\d{1,2})$"
                    user_dic = users_points.return_list_of_unique_users(all_users_list, user_regex)
                    users = list(user_dic.keys())




                else:

                    users = list(range(1,number_of_users+1))

                print(users)
                for user in users:

                    user_wildcard = "user_"+str(user)+"_"+ pid

                    print(user_wildcard)
                    user_point_list = users_points.get_file_path_with_wildcard_from_gdb(user_wildcard)

                    if len(user_point_list) ==0:
                        print("did not point for this user")
                    else:

                        if arcpy.Exists(os.path.join(self.outputGDB,
                                                 os.path.basename(coverage)+"_"+os.path.basename(user_point_list[0]))):
                            print("The file exits, skipping!!!!!!!!!!!")
                        else:
                            print(coverage)
                            print(user_point_list)
                            inlist = [coverage, user_point_list[0]]

                            arcpy.Intersect_analysis(inlist,
                                                     os.path.join(self.outputGDB,
                                                     os.path.basename(coverage)+"_"+os.path.basename(user_point_list[0])),
                                                     join_attributes="ONLY_FID")
                            print(arcpy.GetMessages(0))
                            logging.info(arcpy.GetMessages(0))

            except arcpy.ExecuteError:
                msgs = arcpy.GetMessages(2)
                arcpy.AddError(msgs)
                print(msgs)
            except:
                tb = sys.exc_info()[2]
                tbinfo = traceback.format_tb(tb)[0]
                pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
                arcpy.AddError(pymsg)
                arcpy.AddError(msgs)
                print(pymsg)
                print(msgs)
                logging.warning(msgs)

    def merge_points(self, number_of_users):
        try:
            users_points = get_path.pathFinder(env_0=self.inputGDB)

            if number_of_users == None:
                print("no users specified in the input, parsing input points for users")

                all_users_list = users_points.get_path_for_all_feature_from_gdb(type="point")

                user_regex = r"User_(?P<userid>\d{1,3})_(?P<pid>\d{1,2})$"
                user_dic = users_points.return_list_of_unique_users(all_users_list, user_regex)
                users = list(user_dic.keys())

            else:


                users = list(range(1, number_of_users + 1))

            for user in users:
                user_wildcard ="*_user_"+str(user)+"_*"

                user_points_list = users_points.get_file_path_with_wildcard_from_gdb(user_wildcard)
                print(user_points_list,sep=",")

                output = os.path.join(self.outputGDB, "_merged_points_user_"+str(user))
                if arcpy.Exists(output):
                    print("output Exists, skipping!!!!!!!!!")
                else:






                    arcpy.Merge_management(user_points_list,output, field_mappings="")
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))


        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def select_state_boundary_grid_cells(self, number_of_users=None):
        print("selecting boundaries")
        arcpy.Delete_management("state_boundary_temp")
        state_grid_list=get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb("state_boundary_*")

        users_points = get_path.pathFinder(env_0=self.inputGDB2)

        if number_of_users == None:

            print("no users specified in the input, parsing input points for users")

            all_users_list = users_points.get_path_for_all_feature_from_gdb(type="point")

            user_regex = r"\w+_(?P<userid>\d{1,3})$"
            users = []
            for x in all_users_list:
                user_dic = search(user_regex, os.path.basename(x)).groupdict()
                users.append(user_dic["userid"])

        else:
            users = list(range(1,number_of_users+1))

        for user in users:
            outpath = os.path.join(self.outputGDB, "selected_grid_user_{}".format(str(user)))

            if arcpy.Exists(outpath):
                print("file exits, skipping")
            else:

                user_wildcard = "*_user_"+str(user)
                user_points_list = users_points.get_file_path_with_wildcard_from_gdb(user_wildcard)
                print(user_points_list)
                try:

                    arcpy.MakeFeatureLayer_management(state_grid_list[0], "state_boundary_temp")

                    arcpy.SelectLayerByLocation_management(in_layer="state_boundary_temp",
                                                           overlap_type="CONTAINS",
                                                           select_features=user_points_list[0],
                                                           selection_type="NEW_SELECTION",
                                                           invert_spatial_relationship="NOT_INVERT")

                    arcpy.CopyFeatures_management("state_boundary_temp",outpath)
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))
                    arcpy.Delete_management("state_boundary_temp")

                except arcpy.ExecuteError:
                    arcpy.Delete_management("state_boundary_temp")
                    msgs = arcpy.GetMessages(2)
                    arcpy.AddError(msgs)
                    print(msgs)
                except:
                    arcpy.Delete_management("state_boundary_temp")
                    tb = sys.exc_info()[2]
                    tbinfo = traceback.format_tb(tb)[0]
                    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
                    arcpy.AddError(pymsg)
                    arcpy.AddError(msgs)
                    print(pymsg)
                    print(msgs)
                    logging.warning(msgs)

    def buffer_points(self, buffer_distance):
        print("buffering points")
        point_list = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb(type="Point")

        try:

            for x in point_list:
                print("buffering {}, please wait".format(os.path.basename(x)))
                outfeature = os.path.join(self.outputGDB, os.path.basename(x)+"_buffered_"+str(buffer_distance))
                print(outfeature)
                if arcpy.Exists(outfeature):
                    print("file exits, skiping!!!!!!")
                else:


                    arcpy.Buffer_analysis(in_features=x,
                                          out_feature_class=outfeature,
                                          buffer_distance_or_field="{} Meters".format(buffer_distance),
                                          line_side="FULL",
                                          line_end_type="ROUND",
                                          dissolve_option="ALL",
                                          dissolve_field="",
                                          method="GEODESIC")
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            arcpy.Delete_management("state_boundary_temp")
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            arcpy.Delete_management("state_boundary_temp")
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def intersect_buffered_area_with_coverage(self, number_of_users):
        print("intersecting buffered polygons with coverage")
        logging.info("intersecting buffered polygons with coverage")
        try:

            reference_List = get_path.pathFinder(env_0=self.referenceGDB).get_file_path_with_wildcard_from_gdb("coverage_map_*")


            for x in reference_List:


                regex = r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)_(?P<user>\d{1,3})_(?P<pid2>\d{1,2})?"

                namedic = match(regex, os.path.basename(x)).groupdict()
                print(namedic)

                buffered_polygon_wildcard = "User_"+str(namedic["user"])+"_"+namedic["pid"]+"_*"
                print(buffered_polygon_wildcard)
                buffered_list = get_path.pathFinder(env_0=self.inputGDB2).get_file_path_with_wildcard_from_gdb(buffered_polygon_wildcard)

                coverage_wildcard = "Coverage_map_"+str(namedic["state_fips"])+"_"+str(namedic["pid"])+"_*"
                print(coverage_wildcard)
                coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(coverage_wildcard)

                if len(buffered_list)==0 or len(coverage_list)==0:
                    print("one or more of the input list is empty, skipping this intersection job")

                else:
                    inlist = [coverage_list[0], buffered_list[0]]


                    outpath = os.path.join(self.outputGDB,
                                           os.path.basename(coverage_list[0])+"_buffered_user_"+str(namedic["user"]))

                    if arcpy.Exists(outpath):
                        print("output_exists, skipping!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                    else:
                        logging.info("Inlist : {}\noutpath_file: {}".format(inlist, outpath))
                        arcpy.Intersect_analysis(inlist, outpath)
                        print(arcpy.GetMessages(0))
                        logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def select_Coverage_by_selected_grid(self, number_of_users):
        print("Selecting coverage by grid")
        logging.info("selecting coverage by grid")
        try:

            reference_List = get_path.pathFinder(env_0=self.referenceGDB).get_file_path_with_wildcard_from_gdb("coverage_map_*")


            for x in reference_List:
                arcpy.Delete_management("coverage_temp")
                regex = r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)_(?P<user>\d{1,3})_(?P<pid2>\d{1,2})?"

                namedic = match(regex, os.path.basename(x)).groupdict()
                print(namedic)

                coverage_wildcard = "Coverage_map_" + str(namedic["state_fips"]) + "_" + str(namedic["pid"]) + "_*"
                print(coverage_wildcard)
                coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(
                    coverage_wildcard)

                selected_grid_wildcard = "selected_grid_user_"+namedic["user"]
                selected_grid = get_path.pathFinder(env_0=self.inputGDB2).get_file_path_with_wildcard_from_gdb(
                    selected_grid_wildcard)

                arcpy.MakeFeatureLayer_management(coverage_list[0],"coverage_temp")

                print("joing the selected_field")
                join_field = "ID"
                arcpy.AddJoin_management("coverage_temp", join_field, selected_grid[0], join_field, join_type="KEEP_COMMON")

                outfeature = os.path.join(self.outputGDB,"selected_"+os.path.basename(coverage_list[0])+"_user_"+namedic["user"])
                if arcpy.Exists(outfeature):
                    print("fc exits, skipping")
                else:

                    arcpy.CopyFeatures_management("coverage_temp",outfeature)
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))
                    arcpy.Delete_management("coverage_temp")

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            arcpy.Delete_management("coverage_temp")
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def erase_measured_from_selected_coverage(self, number_of_users):

        print("eraseing")
        logging.info("erasing buffered polygons from selected coverages for each provider")
        try:

            reference_List = get_path.pathFinder(env_0=self.referenceGDB).get_file_path_with_wildcard_from_gdb(
                "coverage_map_*")

            for x in reference_List:



                regex = r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)_(?P<user>\d{1,3})_(?P<pid2>\d{1,2})?"

                namedic = match(regex, os.path.basename(x)).groupdict()
                print(namedic)

                selected_coverage_wildcard = "selected_coverage_map_"+str(namedic["state_fips"])+\
                                             "_"+str(namedic["pid"])+"_"+"*_user_"+str(namedic["user"])
                selected_Coverage_List = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(
                    selected_coverage_wildcard)

                measured_coverage_wildcard = "coverage_map_"+str(namedic["state_fips"])+\
                                             "_"+str(namedic["pid"])+"_"+"*_user_"+str(namedic["user"])
                print(measured_coverage_wildcard)
                measured_coverage_List = get_path.pathFinder(env_0=self.inputGDB2).get_file_path_with_wildcard_from_gdb(
                    measured_coverage_wildcard)


                if len(selected_Coverage_List)==0 or len(measured_coverage_List)==0:
                    print("Len of selected coverage list is: {} and Len of measured coverage list is: {}".format(len(selected_Coverage_List), len(measured_coverage_List)))
                else:

                    outfeature = os.path.join(self.outputGDB,
                                              "unmeasured_coverage_pid_"+str(namedic["pid"])+"_user_"+str(namedic["user"]))

                    if arcpy.Exists(outfeature):
                        print("fc exits, skipping!!!!!")
                    else:


                        arcpy.Erase_analysis(in_features=selected_Coverage_List[0],
                                             erase_features=measured_coverage_List[0],
                                             out_feature_class=outfeature)
                        print(arcpy.GetMessages(0))
                        logging.info(arcpy.GetMessages(0))


        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:

            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def merge_unmeasured_coverages(self, number_of_users):

        logging.info("intersecting buffered polygons with coverage")
        try:

            users_points = get_path.pathFinder(env_0=self.inputGDB)

            if number_of_users == None:

                print("no users specified in the input, parsing input points for users")

                all_users_list = users_points.get_path_for_all_feature_from_gdb(type="polygon")

                user_regex = r"\w+_(?P<userid>\d{1,3})$"
                empty_list = []

                for x in all_users_list:
                    user_dic = search(user_regex, os.path.basename(x)).groupdict()
                    empty_list.append(user_dic["userid"])
                users = list(set(empty_list))
            else:
                users = list(range(1, number_of_users + 1))


            for user in users:

                coverage_wildcard = "unmeasured_coverage_pid_*" + "_user_" + str(user)
                print(coverage_wildcard)
                coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(
                    coverage_wildcard)

                outfeature = os.path.join(self.outputGDB, '_merged_unmeasured_coverages_pid_user_'+str(user))

                if arcpy.Exists(outfeature):
                    print("The file exits, skipping!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                else:

                    logging.info("inputs: {}\noutput: {}".format(coverage_list, outfeature))
                    arcpy.Merge_management(inputs=coverage_list, output=outfeature)
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            arcpy.Delete_management("coverage_temp")
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)


    def merge_selected_coverages(self, number_of_users):
        logging.info("merging buffered polygons with coverage")
        try:

            users_points = get_path.pathFinder(env_0=self.inputGDB)

            if number_of_users == None:

                print("no users specified in the input, parsing input points for users")

                all_users_list = users_points.get_path_for_all_feature_from_gdb(type="polygon")

                user_regex = r"\w+_(?P<userid>\d{1,3})$"
                empty_list = []

                for x in all_users_list:
                    user_dic = search(user_regex, os.path.basename(x)).groupdict()
                    empty_list.append(user_dic["userid"])
                users = list(set(empty_list))
            else:
                users = list(range(1, number_of_users + 1))

            for user in users:

                coverage_wildcard = "*_user_" + str(user)
                print(coverage_wildcard)
                coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(
                    coverage_wildcard)

                outfeature = os.path.join(self.outputGDB, '_merged_selected_coverages_user_' + str(user))
                if arcpy.Exists(outfeature):
                    print("The file exits, skipping!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                else:

                    logging.info("inputs: {}\noutput: {}".format(coverage_list, outfeature))

                    # field mapping
                    #1 create field map object for each field
                    fm = arcpy.FieldMap() # STATE_FIPS
                    fm1 = arcpy.FieldMap() # GRID_COL
                    fm2 = arcpy.FieldMap() # GRID_ROW
                    fm3 = arcpy.FieldMap() # ID
                    fm4 = arcpy.FieldMap() # PID

                    #2 create field mapping object for the output table
                    fms = arcpy.FieldMappings()

                    #3 add the input field to the field map object

                    for fc in coverage_list:


                        for field in arcpy.ListFields(fc, "STATE_FIPS"):
                            fm.addInputField(fc, field.name)

                        for field in arcpy.ListFields(fc, "GRID_COL"):
                            fm1.addInputField(fc, field.name)

                        for field in arcpy.ListFields(fc, "GRID_ROW"):
                            fm2.addInputField(fc, field.name)

                        for field in arcpy.ListFields(fc, "ID"):
                            fm3.addInputField(fc, field.name)

                        for field in arcpy.ListFields(fc, "PID"):
                            fm4.addInputField(fc, field.name)

                    #4 set field properties for each output field

                    fm.mergeRule = "First"
                    f_name = fm.outputField
                    f_name.name = "STATE_FIPS"
                    f_name.type = "Short Integer"
                    fm.outputField = f_name
                    fms.addFieldMap(fm)

                    fm1.mergeRule = "First"
                    f_name = fm1.outputField
                    f_name.name = "GRID_COL"
                    f_name.type = "Long Integer"
                    fm1.outputField = f_name
                    fms.addFieldMap(fm1)

                    fm2.mergeRule = "First"
                    f_name = fm2.outputField
                    f_name.name = "GRID_ROW"
                    f_name.type = "Long Integer"
                    fm2.outputField = f_name
                    fms.addFieldMap(fm2)

                    fm3.mergeRule = "First"
                    f_name = fm3.outputField
                    f_name.name = "ID"
                    f_name.length = 20
                    f_name.type = "TEXT"
                    fm3.outputField = f_name
                    fms.addFieldMap(fm3)

                    fm4.mergeRule = "First"
                    f_name = fm4.outputField
                    f_name.name = "PID"
                    f_name.type = "Short Integer"
                    fm4.outputField = f_name
                    fms.addFieldMap(fm4)

                    arcpy.Merge_management(inputs=coverage_list, output=outfeature,field_mappings=fms)
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:

            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def erase_unmeasured_from_merged_coverage(self, number_of_users):

        print("eraseing")
        logging.info("erasing unmeasured area from measured coverages for each user")
        try:


            users_points = get_path.pathFinder(env_0=self.inputGDB)

            if number_of_users == None or number_of_users == 0:

                print("no users specified in the input, parsing input points for users")

                all_users_list = users_points.get_path_for_all_feature_from_gdb(type="polygon")

                user_regex = r"\w+_(?P<userid>\d{1,3})$"
                empty_list = []


                for x in all_users_list:
                    user_dic = search(user_regex, os.path.basename(x)).groupdict()
                    empty_list.append(user_dic["userid"])

                users = list(set(empty_list))
            else:

                users = list(range(1, number_of_users+1))



            for user in users:


                merged_selected_coverage_wildcard = "*_"+str(user)

                selected_Coverage_List = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(
                    merged_selected_coverage_wildcard)

                unmeasured_coverage_wildcard = "*_"+str(user)

                print(unmeasured_coverage_wildcard)
                measured_coverage_List = get_path.pathFinder(env_0=self.inputGDB2).get_file_path_with_wildcard_from_gdb(
                    unmeasured_coverage_wildcard)


                outfeature = os.path.join(self.outputGDB, "_measured_area_user_"+str(user))

                arcpy.Erase_analysis(in_features=selected_Coverage_List[0],
                                     erase_features=measured_coverage_List[0],
                                     out_feature_class=outfeature)
                print(arcpy.GetMessages(0))
                logging.info(arcpy.GetMessages(0))
                arcpy.Delete_management("coverage_temp")

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            arcpy.Delete_management("coverage_temp")
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def diss_by_grid(self, dissolved_field):

        logging.info("diss merged unmeasured coverages")
        try:
            coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb()

            for x in coverage_list:

                print("Dissovling unmeasured coverages")
                output = os.path.join(self.outputGDB, 'dissolved_'+os.path.basename(x))
                if arcpy.Exists(output):
                    print("The file exits, skipping!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                else:

                    logging.info("input: {}\noutput: {}".format(x,output))
                    arcpy.Dissolve_management(x,output,dissolve_field=dissolved_field)
                    print(arcpy.GetMessages(0))
                    logging.info(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:

            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def create_results(self):
        logging.info("validating_results")
        try:

            for x in get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb():
                print(x)

                fc_list = get_path.pathFinder(env_0=self.inputGDB2)\
                    .get_file_path_with_wildcard_from_gdb("state_boundary_*")

                regex = r"(?:\W)?(?P<user>\d{1,3})$"
                userdic = search(regex, os.path.basename(x)).groupdict()


                outfeature = os.path.join(self.outputGDB,
                                          "state_boundary_results_user_{}".format(userdic["user"]))
                if arcpy.Exists(outfeature):
                    print("the file exits, skipping!!!!!!!!")
                else:

                    arcpy.MakeFeatureLayer_management(fc_list[0], "temp_state_boundary")

                    print("\nadding fields")
                    arcpy.AddField_management("temp_state_boundary", "agg_unmeasured_pct", "Double")
                    arcpy.AddField_management("temp_state_boundary", "agg_unmeasured", "Double")
                    arcpy.AddField_management("temp_state_boundary", "agg_measured","Double")
                    arcpy.AddField_management("temp_state_boundary", "agg_measured_pct", "Double")



                    print("\nJoining {} to {} based on ID field".format(os.path.basename(x),
                                                                        os.path.basename(fc_list[0])))
                    logging.info("Joining {} to {} based on ID field".format(os.path.basename(x),
                                                                             os.path.basename(fc_list[0])))

                    arcpy.AddJoin_management("temp_state_boundary", "ID", x, "ID", "KEEP_COMMON")

                    arcpy.CopyFeatures_management("temp_state_boundary",
                                                  outfeature)
                    logging.info(arcpy.GetMessages(0))
                    arcpy.Delete_management("temp_state_boundary")

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)
        except:
            arcpy.Delete_management("temp_state_boundary")
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

    def calculate_results(self):
        logging.info("calcuating_results")

        for fc in get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb():
            print(os.path.basename(fc))
            arcpy.CalculateField_management(fc, "agg_measured", "!agg_measured_raw!",
                                            expression_type="PYTHON3")
            arcpy.CalculateField_management(fc, "agg_measured_pct", "(!agg_measured!/!CH_AREA!)*100",
                                            expression_type="PYTHON3")
            arcpy.CalculateField_management(fc, "agg_unmeasured_pct", "100-!agg_measured_pct!",
                                            expression_type="PYTHON3")
            arcpy.CalculateField_management(fc, "agg_unmeasured", '!CH_AREA!-!agg_measured!',
                                            expression_type="PYTHON3")


    def attribute_table_to_csv(self, field_names):


        fc_list = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb()

        for fc in fc_list:

            output = os.path.join(self.outputpathfolder, "results_{}.csv".format(os.path.basename(fc)))

            arr=[]

            with arcpy.da.SearchCursor(fc, field_names) as cursor:
                for row in cursor:
                    arr.append(row)

            df = pd.DataFrame(arr, columns=field_names)
            df.to_csv(output, index=False)
            print("output created: {}".format(output))

    @classmethod
    def repair_geom(cls, input_GDB):

        fc_list = get_path.pathFinder(env_0=input_GDB).get_path_for_all_feature_from_gdb()

        for x in fc_list:
            arcpy.RepairGeometry_management(x)
            print(arcpy.GetMessages())


    def export_points_for_USAC(self, search_distance):
        print("exporting points")

        points_list = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb(type="Point")

        for points in points_list:
            print("points")

            regex = r"^(?P<user>\D{0,10})_(?P<userid>\d{1,3})_(?P<pid>\d{1,2})?"

            namedic = match(regex, os.path.basename(points)).groupdict()
            print(namedic)

            wildcard = "Coverage_map_*_{}_*".format(str(namedic["pid"]))

            fc_list = get_path.pathFinder(env_0=self.inputGDB2).get_file_path_with_wildcard_from_gdb(wildcard=wildcard)

            if len(fc_list) == 0:
                print("did not find any points for that")

            else:


                arcpy.MakeFeatureLayer_management(points, "in_layer")
                arcpy.MakeFeatureLayer_management(fc_list[0], "select_features_layer")

                # select by location the points that are 2 kilometers away
                try:

                    outfeature = os.path.join(self.outputpathfolder,"User_"+str(namedic["userid"])+"_"+str(namedic["pid"])+"_for_USAC_system.shp")
                    if arcpy.Exists(outfeature):
                        print("Feature Exits, Skipping !!!!")
                        arcpy.Delete_management("in_layer")
                        arcpy.Delete_management("select_features_layer")

                    else:



                        arcpy.SelectLayerByLocation_management(in_layer="in_layer",
                                                               overlap_type="WITHIN_A_DISTANCE_GEODESIC",
                                                               select_features="select_features_layer",
                                                               search_distance="{} Kilometers".format(search_distance),
                                                               selection_type="NEW_SELECTION",
                                                               invert_spatial_relationship="NOT_INVERT")

                        arcpy.CopyFeatures_management(in_features= "in_layer",
                                                      out_feature_class=outfeature)
                        print("copied to location")

                        arcpy.Delete_management("in_layer")
                        arcpy.Delete_management("select_features_layer")


                except arcpy.ExecuteError:
                    msgs = arcpy.GetMessages(2)
                    arcpy.AddError(msgs)
                    print(msgs)


                except:
                    arcpy.Delete_management("in_layer")
                    arcpy.Delete_management("select_features_layer")
                    tb = sys.exc_info()[2]
                    tbinfo = traceback.format_tb(tb)[0]
                    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
                    arcpy.AddError(pymsg)
                    arcpy.AddError(msgs)
                    print(pymsg)
                    print(msgs)
                    logging.warning(msgs)


    def split_attribute(self, split_field, num_users):
        logging.info("splitting coverages")

        try:

            user_list = list(range(1,num_users+1))

            for user in user_list:
                fc_user_List = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb("*_{}".format(user))


                for x in fc_user_List:
                    name = os.path.split(x)

                    print("\n\n\nlooking at '{}' feature class, please wait!!!".format(name[1]))
                    logging.info("looking at '{}' feature class, please wait!!!".format(name[1]))
                    print("Splitting the files, might take a while. Go for a walk :) \n\n")
                    arcpy.SplitByAttributes_analysis(x, self.outputGDB, split_field)
                    print(arcpy.GetMessages(0))

                print("renaming the file, based on user number")

                renaming_fc_list = get_path.pathFinder(env_0=self.outputGDB).get_file_path_with_wildcard_from_gdb('T*')

                for fc in renaming_fc_list:
                    arcpy.Rename_management(fc, "user_{}_{}".format(user, os.path.basename(fc)))
                    print(arcpy.GetMessages(0))


        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)

    def merge_general(self, output_name):
        logging.info("merging across users")

        try:


            fc_list = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb()

            output = os.path.join(self.outputGDB, output_name)

            if not arcpy.Exists(output):
                arcpy.Merge_management(fc_list, output)
                print(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)

    def diss_general(self, output_name, wildcard, dissolve_field=""):
        logging.info("merging across users")

        try:

            fc_list = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(wildcard=wildcard)

            output = os.path.join(self.outputGDB, output_name)

            if not arcpy.Exists(output):
                for fc in fc_list:
                    arcpy.Dissolve_management(fc,output,dissolve_field)
                    print(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)


    def split_general(self, split_field):

        try:

            fc_List = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb()


            for x in fc_List:
                name = os.path.split(x)

                print("\n\n\nlooking at '{}' feature class, please wait!!!".format(name[1]))
                logging.info("looking at '{}' feature class, please wait!!!".format(name[1]))
                print("Splitting the files, might take a while. Go for a walk :) \n\n")
                arcpy.SplitByAttributes_analysis(x, self.outputGDB, split_field)
                print(arcpy.GetMessages(0))

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)


    def intersect_general(self, output_name, wildcard_1, wildcard_2):
        logging.info("intersecting features")
        try:

            fc_list_1 = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(wildcard=wildcard_1)
            fc_list_2 = get_path.pathFinder(env_0=self.inputGDB2).get_file_path_with_wildcard_from_gdb(wildcard=wildcard_2)

            in_fc_list = fc_list_1+fc_list_2

            if not arcpy.Exists(os.path.join(self.outputGDB, output_name)):
                arcpy.Intersect_analysis(in_features=in_fc_list, out_feature_class=os.path.join(self.outputGDB, output_name))
                print(arcpy.GetMessages())

        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)

class PointMaker(SpeedChecker):

    def __init__(self):
        SpeedChecker.__init__(self,input_path=None, inputGDB=None, inputGDB2=None, referenceGDB=None,
                              outputGDBname=None, outputpathfolder=None, outputfolder_name = None, outputGDB=None)

    def XY_table_to_Point_feature(self, x_coords, y_coords, z_coords, wildcard, extention_of_file, cs,
                                  regex = r'(?i)^(?P<stem>cst_(?P<state_fips>\d+)_challenger_(?P<user_id>\d+)_provider_(?P<provider_id>\d+))\.(?P<ext>csv)$'):
        print("making XY(Z) Points")
        try:

            in_fc_list = get_path.pathFinder.get_path_of_a_file(self.inputpath,wildcard=wildcard,extention=extention_of_file)

            for x in in_fc_list:

                file_name_parsed_dict = search(regex, os.path.basename(x)).groupdict()
                print(file_name_parsed_dict)

                output = os.path.join(self.outputGDB, "User_{}_{}".format(file_name_parsed_dict['user_id'],
                                                                          file_name_parsed_dict['provider_id']))

                if not arcpy.Exists(output):
                    arcpy.XYTableToPoint_management(x,output,x_coords,y_coords,z_coords,cs)
                    print(arcpy.GetMessages(0))




        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError(msgs)
            print(msgs)


        except:

            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
            print(pymsg)
            print(msgs)
            logging.warning(msgs)

