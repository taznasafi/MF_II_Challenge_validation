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
    def __init__(self, input_path=None, inputGDB=None, inputGDB2 = None, outputGDBname=None, outputpathfolder=None, outputGDB=None):
        self.inputpath = input_path
        self.inputGDB = inputGDB
        self.inputGDB2 = inputGDB2
        self.outputGDBName = outputGDBname
        self.outputpathfolder = outputpathfolder
        self.outputGDB = outputGDB

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

        #fc1 is state boundary feature class
        fc1 = get_path.pathFinder(env_0=self.inputGDB)
        fc1_list = fc1.get_file_path_with_wildcard_from_gdb(fc1_wildcard)

        #fc2 is provider speed tests
        fc2 = get_path.pathFinder(env_0=self.inputGDB2)
        fc2_list = fc2.get_file_path_with_wildcard_from_gdb(fc2_wildcard)

        for x in fc2_list:
            if arcpy.Exists(os.path.join(self.outputGDB, os.path.basename(x))):
                print("the file exists, skipping!!!!")
            else:

                logging.info("intersecting {} with {}".format(fc1_list[0], x))

                inlist = [fc1_list[0],x]
                try:
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


    def intersect_intersect_points_with_coverages(self, number_of_users=None):
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
                        if arcpy.Exists(os.path.join(self.outputGDB,
                                                 os.path.basename(coverage)+"_"+os.path.basename(user_point_list[0]))):
                            print("The file exits, skipping!!!!!!!!!!!")
                        else:
                            print(coverage)
                            print(user_point_list)
                            inlist = [coverage, user_point_list[0]]

                            arcpy.Intersect_analysis(inlist,
                                                     os.path.join(self.outputGDB,
                                                     os.path.basename(coverage)+"_"+os.path.basename(user_point_list[0])))
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