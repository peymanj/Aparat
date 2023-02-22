import psutil
import traceback

def clean(process_name):
    if process_name == 'firefox':
        process_name_list = ['firefox', 'geckodriver']
    elif process_name == 'chrome':
        process_name_list = ['chrome', 'chromedriver']


    for process in psutil.process_iter():
        for process_name in process_name_list:
            try:
                if process_name in process.name():	            
                    process.kill()
                    print(f"Process {process_name} terminated")
            except Exception as e:
                traceback.print_exc()
                print(e)
                continue
