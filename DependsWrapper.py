#wrapper to provide independence from RB for standalone usage

import os

class DependsWrapperImpl(object):
        @staticmethod
        def find_plugin_file(parent, filename):
            bIsRbPlugin = False
            try:
                import rb
                bIsRbPlugin = True
            except:
                print("running in stand alone mode -> not using RB")
                pass
            fullpathname = None
            if bIsRbPlugin:
                fullpathname = rb.find_plugin_file(parent, filename)
            else:
                #TODO: manually implement for non-RB
                fullpathname = "./"
                for root, dirs, files in os.walk(fullpathname):
                    for file in files:
                        #print("checking file: ", file)
                        if file == filename:
                            fullpathname = file
                            return fullpathname  
            return fullpathname
