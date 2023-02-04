from __future__ import division, print_function

# Python modules
import argparse
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

    parser = argparse.ArgumentParser("Processing args")
    parser.add_argument("--odb_file_name", type=str, help="odb file top read")
    parser.add_argument("--carbon_file_name", type=str, help="carbon file to write")
    args = parser.parse_args()

    # Set call working function
    exit_status = carbon_field_export(odb_file_name=args.odb_file_name, carbon_file_name=args.carbon_file_name,
                                      flat=True, debug=False)
    
    if exit_status:
        print("\n Export completed")
    else:
        print(" Something went wrong.....")

if __name__ == "__main__":
    main()
