# exploring the files in the local directory and accessing the file properites
import os
from datetime import datetime
from pathlib import Path
import time
import getpass
import mysql.connector
import sys


# display the files in hierarchy
class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


# to extract the files from the directory
def fileextract(userPath, fileextention):
    # """Returns a list with all files with the word/extension in it"""
    file = os.listdir(userPath)
    files = list()
    for f in file:
        file_name = str(f)
        if file_name.endswith(fileextention):
            files.append(file_name)

    # returns files of user specified type
    return files


def fileinfo(fileName):
    info = os.stat(fileName)
    fileInfo = {
        "file_name": fileName,
        "inode_protection_mode": [info[0]],
        "inode_number": [info[1]],
        "device_inode_resides_on": [info[2]],
        "number_of_links_to_the_inode": [info[3]],
        "user_id": [info[4]],
        "group_id": info[5],
        "size_in_bytes": os.path.getsize(fileName),
        "time_of_last_access": time.ctime(os.path.getatime(fileName)),
        "time_of_last_modification": time.ctime(os.path.getmtime(fileName)),
        "creation_time": time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(info[9])),
        "file_path": os.path.realpath(fileName),
        "user_name": getpass.getuser(),
        "system_time":datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    }
    return fileInfo


def commitdb(fileName):
    info = os.stat(fileName)
    #here we are checking for file with filw name and filepath if both matches stored in db else it is recored to filecreated db and aslo here
    #this is to check any newly created files
    sql = "INSERT INTO fileproperties (file_name, inode_protection_mode, inode_number, device_inode_resides_on, " \
              "number_of_links_to_the_inode, user_id, group_id, size_in_bytes, time_of_last_access, " \
              "time_of_last_modification , creation_time , file_path , user_name,system_time) VALUES (%s, %s, %s, %s, %s, %s, %s, " \
          "%s,%s,%s, %s,%s,%s,%s) "
    val = (
            str(fileName), str([info[0]]), str(info[1]), str(info[2]), str(info[3]), str(info[4]),
            str(info[5]),
            str(os.path.getsize(fileName)),
            str(time.ctime(os.path.getatime(fileName))), str(time.ctime(os.path.getmtime(fileName))),
            str(time.strftime("%m/%d/%Y %I:%M:%S:%p", time.localtime(info[9]))), str(os.path.realpath(fileName)),
            str(getpass.getuser()),str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    mycursor.execute(sql, val)
    mydb.commit()
    return "recorded"

def fileexistance(fileName):
    sqlq = "SELECT system_time FROM fileproperties WHERE file_name= %s"
    data1 = (fileName,)
    mycursor.execute(sqlq, data1)
    myresult1 = mycursor.fetchall()
    length1=len(myresult1)
    lastDateUpdated=myresult1[length1-1]
    systemTime=datetime.now()
    # print(str(lastDateUpdated))
    print(lastDateUpdated)
    print(systemTime)
    if lastDateUpdated == systemTime:
        print("file is unaltered")
    #we are comparing here date and time if it is not equal then the file is deleted







# main function
if __name__ == '__main__':
    print('Python %s on %s' % (sys.version, sys.platform))
    # establishing connection with database
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="mydatabase"
    )
    mycursor = mydb.cursor()
    # getting user input of directory to serch files
    userPath = "C:" #input("Enter the directory \n")
    paths = DisplayablePath.make_tree(Path(userPath))
    for path in paths:
        print(path.displayable())
    # getting user input for file type
    fileEndsWith = ".xls" # input("Enter The file extention you need extract\n")
    fileExtractResult = fileextract(userPath, fileEndsWith)
    print(fileExtractResult)
    # iterating through each file for its properties
    for file in fileExtractResult:
        fileName = file

        fileInfoResult = fileinfo(fileName)  # file properties are stored in fileInfoResult
        print(fileInfoResult)
        rocordresult=commitdb(fileName)
        print(rocordresult)
        fileexistance(fileName)


