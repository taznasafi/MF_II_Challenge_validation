import arcpy
import sys
import traceback
import logging
import time
import get_path
import os
from re import match

formatter = ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(filename=r"{}_Log_{}.csv".format(__name__.replace(".", "_"), time.strftime("%Y_%m_%d_%H_%M")),
                                 level=logging.DEBUG, format=formatter)

class SpeedChecker:
    def __init__(self, input_path=None, inputGDB=None, inputGDB2 = None, referenceGDB = None,
                 outputGDBname=None, outputpathfolder=None, outputGDB=None):
        self.inputpath = input_path
        self.inputGDB = inputGDB
        self.inputGDB2 = inputGDB2
        self.referenceGDB = referenceGDB
        self.outputGDBName = outputGDBname
        self.outputpathfolder = outputpathfolder
        self.outputGDB = outputGDB

        arcpy.env.qualifiedFieldNames = False

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

                if number_of_users == None:
                    print("no users")
                else:
                    users_points = get_path.pathFinder(env_0=self.inputGDB2)
                    users = list(range(1,number_of_users+1))

                    for user in users:
                        user_wildcard = "user_"+str(user)+"_pid_"+ pid
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

            if number_of_users == None:
                pass
            else:

                users_points = get_path.pathFinder(env_0=self.inputGDB)
                users = list(range(1, number_of_users + 1))

                for user in users:
                    user_wildcard ="*_user_"+str(user)+"_*"

                    user_points_list = users_points.get_file_path_with_wildcard_from_gdb(user_wildcard)
                    print(user_points_list,sep=",")

                    output = os.path.join(self.outputGDB, "_merged_points_user_"+str(user))
                    if arcpy.Exists(output):
                        print("output Exists, skipping!!!!!!!!!")
                    else:


                        arcpy.Merge_management(user_points_list,output)
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
        if number_of_users == None:
            pass
        else:
            users_points = get_path.pathFinder(env_0=self.inputGDB2)
            users = list(range(1,number_of_users+1))

            for user in users:
                outpath = os.path.join(self.outputGDB, "selected_grid_user_{}".format(str(user)))
                if arcpy.Exists(outpath):
                    print("file exits, skipping")
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

                if number_of_users==None or number_of_users==0:
                    print("number of user has been set or set to zero, still under development")
                    pass

                else:


                    regex = r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)_(?P<user>\d{1,2})_pid_(?P<pid2>\d{1,2})?"

                    namedic = match(regex, os.path.basename(x)).groupdict()
                    #print(namedic)

                    buffered_polygon_wildcard = "user_"+str(namedic["user"])+"_pid_"+namedic["pid"]+"_*"
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
        print("intersecting buffered polygons with coverage")
        logging.info("intersecting buffered polygons with coverage")
        try:

            reference_List = get_path.pathFinder(env_0=self.referenceGDB).get_file_path_with_wildcard_from_gdb("coverage_map_*")


            for x in reference_List:

                if number_of_users==None or number_of_users==0:
                    print("number of user has been set or set to zero, still under development")
                    pass

                else:


                    regex = r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)_(?P<user>\d{1,2})_pid_(?P<pid2>\d{1,2})?"

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
        logging.info("intersecting buffered polygons with coverage")
        try:

            reference_List = get_path.pathFinder(env_0=self.referenceGDB).get_file_path_with_wildcard_from_gdb(
                "coverage_map_*")

            for x in reference_List:

                if number_of_users == None or number_of_users == 0:
                    print("number of user has been set or set to zero, still under development")
                    pass

                else:

                    regex = r"^coverage_map_(?P<state_fips>\d{2})_(?P<pid>\d{1,2})_(?:\w+?)_(?P<user>\d{1,2})_pid_(?P<pid2>\d{1,2})?"

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


                    outfeature = os.path.join(self.outputGDB, "unmeasured_coverage_pid_"+str(namedic["pid"])+"_user_"+str(namedic["user"]))

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



    def merge_measured_unmeasured_coverages(self, number_of_users):

        logging.info("intersecting buffered polygons with coverage")
        try:
            user_list = list(range(1,number_of_users+1))

            for user in user_list:

                coverage_wildcard = "unmeasured_coverage_pid_*" + "_user_" + str(user)
                print(coverage_wildcard)
                coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_file_path_with_wildcard_from_gdb(
                    coverage_wildcard)

                if number_of_users == None or number_of_users == 0:
                    print("number of user has been set or set to zero, still under development")
                    pass

                else:

                    outfeature = os.path.join(self.outputGDB, '_merged_unmeasured_coverages_pid_user_'+str(user))
                    if arcpy.Exists(outfeature):
                        print("The file exits, skipping!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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



    def diss_merge_unmeasured_coverages(self):

        logging.info("diss merged unmeasured coverages")
        try:
            coverage_list = get_path.pathFinder(env_0=self.inputGDB).get_path_for_all_feature_from_gdb()

            for x in coverage_list:

                print("Dissovling unmeasured coverages")
                output = os.path.join(self.outputGDB, 'dissolved_'+os.path.basename(x))
                if arcpy.Exists(output):
                    print("The file exits, skipping!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    continue
                logging.info("input: {}\noutput: {}".format(x,output))
                arcpy.Dissolve_management(x,output,dissolve_field=["STATE_FIPS", "GRID_COL", "GRID_ROW", "ID"])
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














































































































