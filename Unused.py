#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-08-09 14:00:03
# @Author  : Hanxt
# @Version : 1.0

import os,sys,getopt,subprocess,glob,commands

reload(sys)
sys.setdefaultencoding('utf-8')

#当前项目路径
PROJECT_PATH = sys.path[0]

#项目文件路径
project_file_paths = commands.getoutput("find " + PROJECT_PATH + " -name '*.pbxproj'").split()
for path in project_file_paths:
    if "Pods" not in path:
        PROJECT_FILE_PATH = path

TARGET_PATH = os.path.splitext(os.path.dirname(PROJECT_FILE_PATH))[0]

#所有文件
ALL_FILES = commands.getoutput("find " + TARGET_PATH + " -name '*.?ib' -o -name '*.[mh]' -o -name '*.storyboard'")

def searchingImage():
    print ''
    print '注意:'
    print '扫描范围包括所有的xib、nib和.h .m文件'
    print '请放到项目目录下以便能跳转到相应的图片'
    print ''
    #查找所有的图片文件
    searching_cmd = "find " + TARGET_PATH + " -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*.jpeg'"
    # print searching_cmd
    process = subprocess.Popen(searching_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdoutput, erroutput) = process.communicate()
    if erroutput is not None:
        print 'searchingImage() Error.'
        return
    count = 0
    totalsize = 0.0
    unused_files = []
    # print stdoutput
    for image_path in stdoutput.split():
        imagename = commands.getoutput("basename -s .jpg " + image_path + " | xargs basename -s .png | xargs basename -s @2x | xargs basename -s @3x")
        unused = True
        for filePath in ALL_FILES.split():
            (_, ext) = os.path.splitext(filePath)
            if ext in ['.nib', '']:#需要跳过的特殊文件或目录
                continue
            cmd = 'grep -c ' + imagename  + ' ' + filePath
            if int(commands.getoutput(cmd)) > 0:#只要查找到了，就标记为已经用到过
                unused = False
                break
        if unused:
            file_size = float(commands.getoutput('stat -f "%z" ' + image_path)) / 1024.0
            totalsize += file_size
            print image_path + "  (%.2fKB)"%file_size
            unused_files.append(image_path)
            count+=1        
    print ""
    print "There are %d unused files."%count + "  (total size: %.2fKB)"%totalsize
    # print unused_files
    echoFiles(unused_files, totalsize)
    deleteFiles(unused_files)

def searchingClass():
    print ''
    print '注意:'
    print '扫描范围包括pbxproj中引用到的所有文件 (*.h, *.m, *.c, *.a, *.cpp)'
    print '一旦被pbxproj所引用，则默认为是有用的文件'
    print ''
    #查找所有的文件 (*.h, *.m, *.c, *.a, *.cpp)
    searching_cmd = 'find ' + TARGET_PATH + ' -name "*.[hmca]" -o -name "*.cpp"'
    # print searching_cmd
    process = subprocess.Popen(searching_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdoutput, erroutput) = process.communicate()
    if erroutput is not None:
        print 'searchingClass() Error.'
        return
    count = 0
    unused_files = []
    for file in stdoutput.split():
        filename = commands.getoutput("basename " + file)
        cmd = 'grep -c ' + filename  + ' ' + PROJECT_FILE_PATH
        if int(commands.getoutput(cmd)) < 1:
            print file
            unused_files.append(file)
            count+=1
    print ""
    print "There are %d unused files."%count
    # print unused_files
    echoFiles(unused_files)
    deleteFiles(unused_files)


def echoFiles(unused_files, totalsize = -1.0):
    os.chdir(PROJECT_PATH)
    f = open('Unused.html','w')
    f.write('<html>')
    f.write('<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>')
    f.write('<h2> Unused resources </h2>')
    f.write('<body>')
    f.write('<h3>')
    if totalsize < 0:
        f.write('There are ' + str(len(unused_files)) + ' unused files.')
    else :
        f.write('There are ' + str(len(unused_files)) + ' unused images (total size: ' + str(totalsize) + ' kb)')
    f.write('</h3>')
    f.write('<pre>')
    for file in unused_files:
        f.write(file)
    f.write('</pre>')
    f.write('</body>')
    f.write('</html>')
    f.close()


def deleteFiles(unused_files):
    if len(unused_files) < 1:
        print 'Exit.'
        return
    print ""
    print "输入: [y/n] 来删除(y)或保留(n)这些文件"
    print "删除文件时请务必确认这些文件不再会被引用"
    ifDelete = raw_input()
    if ifDelete != 'Y' and ifDelete != 'y':
        print 'Exit.'
        return
    for file in unused_files:
        delele_cmd = 'mv ' + file + ' ~/.Trash'
        # print delele_cmd
        commands.getoutput(delele_cmd)


def usage():
    script_name = os.path.basename(__file__)
    print ''
    print '******************************************************************'
    print '* 请放到项目目录下并执行相应的命令'
    print '* 查找并删除没用到的图片文件：python Unused.py -i'
    print '* 查找并删除没用到的类文件：python Unused.py -c'
    print '* 删除操作只是移动到废纸篓，编译失败时可以去废纸篓找回:)'
    print '******************************************************************'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hic", ["help", "image", "class"])
        if len(opts) < 1:
            usage()
        for name,value in opts:
            if name in ("-i", "--image"):
                searchingImage()
            if name in ("-c", "--class"):
                searchingClass()
            if name in ("-h","--help"):
                usage()
    except getopt.GetoptError as e:
        usage()
        # print("error %s" % e)
        sys.exit(2)

if __name__ == '__main__':
    # print PROJECT_FILE_PATH
    # print TARGET_PATH
    # print ALL_FILES
    main()
