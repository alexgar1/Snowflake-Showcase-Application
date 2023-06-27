import subprocess

def callGEN(remove,time,m,n,name,pw):
    host = 'kingspeak33.chpc.utah.edu'
    remLoc = '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/'
    remPy = '/uufs/chpc.utah.edu/common/home/snowflake/RedButte20192020_exp/MASC/Showcase/'
    
    subprocess.call('CD C:\MASC\showcase_setup', shell=True)

    if remove == 1:
        subprocess.call(f'START python uploadFileAndGenHTML.py -v -locLoc C:\MASC\The_Alta_Project_2022\*\ -t {str(time)} -m {str(m)} -n {str(n)} -nolines -un {name} -pw {pw} -host {host} -remLoc {remLoc} -fout index.html -remPY {remPy}', shell=True)
    else:
        subprocess.call(f'START python uploadFileAndGenHTML.py -v -locLoc C:\MASC\The_Alta_Project_2022\*\ -t {str(time)} -m {str(m)} -n {str(n)} -un {name} -pw {pw} -host {host} -remLoc {remLoc} -fout index.html -remPY {remPy}', shell=True)


def callData():
    subprocess.call('simpleDataAcquisition_x64_v0.155.exe -rCfg -diOut C:\MASC\The_Alta_Project_2022 -autoappend', shell=True)
    subprocess.call('pause', shell=True)