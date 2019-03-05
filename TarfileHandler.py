'''
Specification:
Class
    get current temporary directory
    load tar file and extract to temporary directory
    overwrite tar file with temporary directory

'''
import sys
import os
import tempfile
import tarfile
import shutil

class TarfileHandler():

    # Properties
    tarFilePath = ''
    tempDir = ''

    # Methods

    def extractTarToTemp(self, tarFilePath):
        '''
        Create a temp directory and extrac everything in the tarfile into the temp dir
        This Block used return True/None to indicate whether success or not. While the
        createTarfile block used raising exceptions (means should be called in try statement
        with error handling instead of a if statement)
        '''

        tempDir = tempfile.mkdtemp()
        file_name, file_ext = os.path.splitext(tarFilePath)
        if file_ext  == ".tar": # check if file had format .tar.gz
            try:
                with tarfile.open(tarFilePath, "r") as tar:
                    tar.extractall(path=tempDir) # untar file into same directory
                return tempDir
            except:
                pass
            finally:
                pass

        # delete the temp directory unless returned before (extracting succeeded)
        self.deleteDir(tempDir)

    def overwriteTarWithTemp(self):
        ''' Overwrite the loaded tarfile with the temp dir '''
        if len(self.tarFilePath)>0 and len(self.tempDir)>0:
            try:
                with tarfile.open(self.tarFilePath, "w") as tar:
                    tar.add(self.tempDir, arcname = '', recursive = True)
                return True
            except:
                return None
            finally:
                return None

    def createTar(self, tarFilePath):

        assert (not os.path.exists(tarFilePath)), 'Failed create tar file, file already exists!'

        tempDir = self.createTempDir()
        # Here need a try statement to exclude invalid file names
        try:
            with tarfile.open(tarFilePath, "w") as tar:
                tar.add(tempDir, arcname = '', recursive = True)
            return tempDir
        except:
            self.deleteDir(tempDir) # delete the old one if exists
            raise ValueError('Failed create tar file, file name not valid!')
        finally:
            pass



    def createTempDir(self):
        ''' Create an empty TempDir with folder source and empty folders bgm and img '''
        tempDir = tempfile.mkdtemp()
        #tempDir = os.path.join(tempBaseDir)#,'source')
        #os.mkdir(tempDir)
        os.mkdir(os.path.join(tempDir,'bgm'))
        os.mkdir(os.path.join(tempDir,'img'))
        return tempDir
        #os.mkdir(os.path.join(self.tempDir,'source/img'))

    def deleteDir(self, dir):
        ''''''
        if os.path.exists(dir) and os.path.isdir(dir):
            shutil.rmtree(dir)

    # Private Methods, Be careful only for internal use!!
    def getTempDir(self):
        '''Get the current temporary directory'''
        return tempfile.mkdtemp()



if __name__ == "__main__":
    thisTar = './source/template.tar'
    tarfileHandler = TarfileHandler()
    print(tarfileHandler.extractTarToTemp(thisTar))
    print(tarfileHandler.tempDir)
    print(tarfileHandler.tarFilePath)
    #tarfileHandler.overwriteTarWithTemp()
    #tarfileHandler.createTempDir()
    #tarfileHandler.createTar('test.tar')
    #print(tarfileHandler.tempDir)