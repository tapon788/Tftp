import ftplib
import datetime
import os
import time
import sys


# ____ calculation of formated current date ddmmyy _____

dirname_array = []
dirvalue_array = []
fp = open("config.txt",'r')

for line in fp.readlines():
    if line.find("=")>=0:
        dirname_array.append(line.split("=")[0])
        dirvalue_array.append(line.split("=")[1].replace("\n",""))

fp.close()
#print dirname_array
#print dirvalue_array


print "Today: "+time.ctime()+"\n"

os.chdir(dirvalue_array[3])

obj = datetime.date.today()
d = str(obj)
mod_date = d.split("-")[2]+d.split("-")[1]+d[2:4]


try:
    os.mkdir(dirvalue_array[5]+mod_date)
except WindowsError,e:
    pass

dir_name = dirvalue_array[3]+dirvalue_array[5]+mod_date+"\\"
files_in_local = os.listdir(dir_name)
os.chdir(dir_name)

file_size_local =[]

'''
file_size_local is used to store size of local files
If any error ocurred during copy and file not saved fully
in local directory, this size array will compare with the
file size in ftp and based on this file copying will be decided
'''

local_match = []


for f in files_in_local:
    file_size_local.append(str(os.path.getsize(f)))
    local_match.append(f+"__"+str(os.path.getsize(f)))

def countInftp():

    ftp = ftplib.FTP(dirvalue_array[0],dirvalue_array[1],dirvalue_array[2])
    directory = dirvalue_array[4]+mod_date
    ftp.cwd(directory)
    log=[]
    ftp.retrlines('LIST',callback = log.append)

    files = (line.rsplit(None, 1)[1] for line in log)
    files_list = list(files)

    #print files_list
    xml_files = []
    ftp_match = []
    file_size_ftp = []
    xml_count = 0
    for f in files_list:
        if f.find("xml")>=0:
            xml_count+=1
            file_size_ftp.append(str(ftp.size(f)))
            ftp_match.append(f+"__"+str(ftp.size(f)))

    for f in ftp_match:
        if f not in local_match:
            xml_files.append(f.split("__")[0])

    sys.stdout.write("Files in FTP:%25s\n"%str(xml_count))

    return (xml_files,xml_count)

def countDiff():

    count = countInftp()
    files_in_ftp = count[0]
    sys.stdout.write("Files in Local Direactory:%12s\n"%str(len(files_in_local)))
    sys.stdout.write("Files corrupted in local directory:%3s\n"%str((len(files_in_local)+len(files_in_ftp))-count[1]))
    sys.stdout.write("Files to be copied from FTP:%10s\n"%str(len(files_in_ftp)))


    if len(files_in_ftp)>0:
        print "\nFollowing databases will be copied\n"
        i = 0
        for f in files_in_ftp:
            i+=1
            sys.stdout.write(f+"\t\t")
            if i%4==0:
                sys.stdout.write("\n")

    else:
        print "\n\nAlready copied!"
        x = raw_input()
        try:
            sys.exit()
        except SyntaxError,e:
            print "BYE"
    file_diff = files_in_ftp
    return (file_diff,files_in_ftp)


try:
    os.mkdir(dir_name)
except WindowsError,e:
    diff_n_file_ftp  = countDiff()
    file_diff=diff_n_file_ftp[0]
    file_no_ftp = diff_n_file_ftp[1]
print "FILE DIFF IS:"
print file_diff
def handleDownload(block):
    file.write(block)

ftp = ftplib.FTP(dirvalue_array[0],dirvalue_array[1],dirvalue_array[2])
directory = dirvalue_array[4]+mod_date
ftp.cwd(directory)
print "\n\n"+ str(len(file_diff))+" Databases will be copied from "+dirvalue_array[0]+" to "+ os.getcwd()+". Please wait...\n\n"


try:
    y=ftp.nlst()
except ftplib.error_perm, resp:
    if str(resp)=="550 No files found":
        print "No file"
    else:
        raise
counter = 1


for filename in file_diff:
      #print 'Opening local file ' + filename
      file = open(filename, 'wb')

      try:
        ftp.retrbinary('RETR ' + filename, handleDownload)
        if counter==1:
            sys.stdout.write("\r\r"+str(counter)+" file has been copied: Remaining "+str(len(file_diff)-counter))
        else:
            if 10>(len(file_diff)-counter)>8:
                sys.stdout.write("\r\r"+str(counter)+" files have been copied: Remaining   ")
            sys.stdout.write("\r\r"+str(counter)+" files have been copied: Remaining "+str(len(file_diff)-counter))
        time.sleep(1)
        counter+=1


      except ftplib.error_perm, resp:
        if str(resp)=="550 Access denied.":
            print filename+" is a directory and not copied"
            continue
        else:
            raise
      file.close()

ftp.close()
print "\n\n*************__SUMMARY__*****************\n"

print "Total no. of files in FTP server      : "+str(len(file_no_ftp))
print "Total no. of files transfered         : "+str(counter-1)
print "Total no. of files not transfered     : "+str(len(file_no_ftp)-counter+1)+"\n"
print "\n*******************************************\n"

try:
    x=input("\n\t\t\tPlease enter to quit ")
except:
    print " "