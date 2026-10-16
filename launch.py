"""Prepare isolated PDF dependencies once, then open the local app."""
import pathlib,subprocess,sys,venv
root=pathlib.Path(__file__).resolve().parent
env=root/'.venv'
python=env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
try:
    if not python.exists():
        print('Preparing Finance Local. First setup requires internet to install PDF support.')
        venv.create(env,with_pip=True)
    if subprocess.call([str(python),'-c','import pypdf'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL):
        subprocess.check_call([str(python),'-m','pip','install','-r',str(root/'requirements-pdf.txt')])
    subprocess.call([str(python),str(root/'server.py')])
except (OSError,subprocess.CalledProcessError) as e:
    print('Setup could not complete:',e)
    print('Check your internet connection and Python 3.10+ installation, then run Start-Finance.bat again. Your data was not changed.')
    input('Press Enter to close.')
