from __future__ import division, print_function

# Python modules
import getopt
import os
import sys

# Abaqus modules
import odbAccess
from abaqusConstants import ELEMENT_NODAL
import abaqusExceptions

print(sys.version)
# ------------------------------------------------------------------------------
# Open specified file and return the file handle
def open_file(inp_file, mode='r'):
    try:
        file_handle = open(inp_file, mode)
    except IOError:
        print(' Can not open the file: ', inp_file)
        raise
    except:
        print('  Unexpected error: ' ,sys.exc_info()[0])
        sys.exit(1)
    return file_handle


def carbon_field_export(odb_file_name=False, carbon_file_name=False, flat=True, debug=False):
    """
    **
    ** ============================================
    **     Program: carbon_field_export.py converter
    **     Written by: Niklas Melin
    **     Version: 1.0.1 RC3
    **  ============================================
    **
    """
    current_version = '1.0.1 RC3'
    try:
        # Check the arguments received by the function.
        if not (odb_file_name or carbon_file_name):
            print(" ERROR: You need to supply both the odbFileName and carbonFileName, Exiting!")
            return False
        
        print(carbon_field_export.__doc__)
        print(" Opening files,")
        
        # Open the odb-repository for reading
        odb_obj = odbAccess.openOdb(path=odb_file_name)
        
        # Create / overwrite the carbonFile
        carbon_file_name_handle = open_file(carbon_file_name, 'w+')
        
        print("         Done")
        
        step = odb_obj.steps.items()[-1][1]
        frame = step.frames[-1]
        
        # Check that the desired output variable is available
        if 'CONC' in frame.fieldOutputs:
            conc_nodal_field = frame.fieldOutputs['CONC'].getSubset(position=ELEMENT_NODAL)
            conc_nodal_field_values = conc_nodal_field.values
        else:
            raise KeyError("ERROR: The odb repository does not contain the required field 'CONC', Exiting!")

        print(" Start writing to file,",)
        carbon_file_name_handle.write('*******************************************************************\n**\n**\n')
        print("**", file=carbon_file_name_handle)
        print("** ============================================", file=carbon_file_name_handle)
        print("**     Program: Odb2Carbon.py converter", file=carbon_file_name_handle)
        print("**     Written by: Niklas Melin", file=carbon_file_name_handle)
        print("**     Version: %s" % current_version, file=carbon_file_name_handle)
        print("**  ============================================", file=carbon_file_name_handle)
        print("**", file=carbon_file_name_handle)
        print("** odb file:  %s " % odb_obj.name, file=carbon_file_name_handle)
        print("**     step:  %s " % step.name, file=carbon_file_name_handle)
        print("**    frame:  %s \n**" % frame.description, file=carbon_file_name_handle)
        
        # Format output depending on if file is using parts and instances or not (flat inp-file)
        if flat:
            carbon_file_name_handle.write('**\n** Node number,  CONC Carbon\n')
            for value in conc_nodal_field_values:
                print("   %11i, %12f" % (value.nodeLabel, value.data), file=carbon_file_name_handle)
        else:
            carbon_file_name_handle.write('**\n** Instance       , Node number,  CONC Carbon\n')
            for value in conc_nodal_field_values:
                print("   %-15s, %11i, %12f" % (value.instance.name, value.nodeLabel, value.data),
                      file=carbon_file_name_handle)
        carbon_file_name_handle.write('** EOF')
        
        print(" Done")
        
        print(" Closing files")
        carbon_file_name_handle.close()
        odb_obj.close()
        print("         Done")
        return True
        
    except odbAccess.OdbError:
        print("ERROR: The odb-file could not be opened, exiting!")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        sys.exit()        
    except IOError:
        print("ERROR: An error was encountered while operating on the carbon file")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        # Close the odb repository
        odb_obj.close()
    except:
        print("ERROR: A general error was encountered")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        # Close the odb repository
        odb_obj.close()
        # Close the carbon file
        carbon_file_name_handle.close()
    

def main(argv=None):
    """
    =========================================================================
    Version:    1.0.1 -  RC3
    Written by: Niklas Melin, 2012
    =========================================================================

    Description:
    -------------------------------------------------------------------------
    Function to read nodal carbon content and write to a file for use in
    subsequent analysis steps.

    Required keywords    Type      Description
    -------------------------------------------------------------
    odb_file_name        file      Name of the output odb-repository

    Required arguments   Type      Description
    -------------------------------------------------------------
                         file      At least one files containing nodal data
                         
    Optional keywords    Type      Description
    -------------------------------------------------------------
    carbon_file_name     file      Name of the nodal carbon concentration file
    """

    # Set initial values
    print(sys.argv)
    debug = True
    odb_file_name = False
    carbon_file_name = False
    flat = True

    print("\n")
    print(" Checking arguments")
    if argv is None:
        argv = sys.argv
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "debug", "odb_file_name", "carbon_file_name"])
    except getopt.error as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # Process passed options ()
    for o, a in opts:
        if o in ("-h", "--help"):   # Print help message
            print(main.__doc__)
            sys.exit(0)
        if o in "--debug":   # Set debug mode
            print(" NOTE: Using debug mode")
            debug = True

    # Print all received arguments
    if debug:
        print(" Received main args: ", args)

    # Check all that all demanded arguments were received
    try:
        for arg in args:
            if arg.startswith('odb_file_name'):
                odb_file_name = os.path.abspath(arg.split('=')[1])
                if not os.path.isfile(odb_file_name):
                    sys.exit("        odb repository not found: %s " % odb_file_name)
            elif arg.startswith('carbon_file_name'):
                carbon_file_name = os.path.abspath(arg.split('=')[1])
            elif arg.startswith('flat'):
                flat = os.path.abspath(arg.split('=')[1])
            elif '=' in arg:
                print(" WARNING: The following argument is unknown: ", arg)
            else:
                odb_data_name = os.path.abspath(arg)
                if not os.path.isfile(odb_data_name):
                    sys.exit("        odb data file not found: %s " % odb_data_name)
                if not odb_data_names:
                    odb_data_names = [odb_data_name]
                else:
                    odb_data_names.append(odb_data_name)
                del odb_data_name

        if not odb_file_name:
            print(" ERROR: The odbFileName was not defined, use syntax odbFileName=file.odb")
            sys.exit(' ERROR: An odb-file was not passed, exiting.')

        if not carbon_file_name:  # If odb-filename was not stated, use default name.
            carbon_file_name = os.path.splitext(odb_file_name)[0] + '.carbon'

        if debug:
            print("\n carbonFileName={0}\n odbFileName={1}\n ".format(carbon_file_name, odb_file_name))
    except SystemExit:
        print(" ERROR: An error while checking the arguments main()")
        raise
    except:
        print(" ERROR: An unknown error occurred while checking the arguments main(): %s" % sys.exc_info()[0])
        raise

    print("    Done")
    
    # Set call working function
    exit_status = carbon_field_export(odb_file_name=odb_file_name, carbon_file_name=carbon_file_name, flat=flat,
                                      debug=debug)
    
    if exit_status:
        print("\n Export completed")
    else:
        print(" Something went wrong.....")
    
    if debug:
        pass
        # print '\n Read Nodes: ',len(hOdb.geoData['Nodes'])
        # print hOdb.geoData['Nodes']
        # for NodeSetKey in hOdb.geoData['NodeSets'].keys():
        #   print '\n Node Set: ',NodeSetKey
        #   print  hOdb.geoData['NodeSets'][NodeSetKey]
           
        # print '\n Read Elements: ',len(hOdb.geoData['Elements'])
        # print hOdb.geoData['Elements']
        # for ElementSetKey in hOdb.geoData['ElementSets'].keys():
        #   print '\n Element Set: ',ElementSetKey
        #   print  hOdb.geoData['ElementSets'][ElementSetKey]

        # print "\n Sections:",hOdb.sectionData

        # print "\n Materials:",hOdb.materialData

        # print "\n\n\n ", hOdb.geoData


if __name__ == "__main__":
    main()
