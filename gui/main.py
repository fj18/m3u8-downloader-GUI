from dearpygui.core import *
from dearpygui.simple import *
import os
import sys
from multiprocessing import Pipe,Process
os.environ['REQUESTS_CA_BUNDLE'] =  os.path.join(os.path.dirname(sys.argv[0]), 'cacert.pem')
sys.path.append("../m3u8-downloader/") 
from m3u8_downloader import *



def directory_picker(sender, data):
    select_directory_dialog(callback=apply_selected_directory)


def apply_selected_directory(sender, data):
    directory = data[0]
    set_value("##folder_path", directory)

def test_callback(sender,data):
    uris= get_value("##uris").split("\n")
    uris = list(filter(lambda x : x, uris))
    print(uris,type(uris))



def download_thread(logs,config):
    # print(logs,config)
    M3U8Downloader(config, 16).run()
    # set_value("##log",logs + "下载完成")


def start_download(sender,data):
    # configs_file = open('config.json', 'rb')
    # configs = json.load(configs_file)
    uris= get_value("##uris").split("\n")
    uris = list(filter(lambda x : x, uris))

    configs = {"concat": True,
               "name": get_value("##NamePre"),
               "output_dir": get_value("##folder_path"),
               "ssl": False,
               "uris": uris,
               "ignore_small_file_size": 0}

    uris = configs['uris']  # 获得配置文件中的多个uri
    uris_index = range(len(uris))

    logs = ""
    processes = []
    # threads = []
    # print(configs,uris,uris_index)
    for i in uris_index:
        if uris[i].find("/1000k/hls/") == -1 and uris[i].find("okzy.com") != -1:  # 如果uri中没有/1000k/hls则加上这部分内容,仅适用于ok资源网的m3u8
            uris[i] = uris[i].replace("index.m3u8", "/1000k/hls/index.m3u8")
        
        if logs == "":
            logs += "开始下载：%s_第%d集" % (configs["name"], i+1)
        else:
            logs += "\n开始下载：%s_第%d集" % (configs["name"], i+1)

        set_value("##log",logs)

        config = {
            "concat": configs["concat"],
            "output_file": '%s_第%d集' % (configs["name"], i+1) + '.ts',
            "output_dir": configs["output_dir"],
            "ssl": configs["ssl"],
            "uri": uris[i],
            "ignore_small_file_size": configs["ignore_small_file_size"]
        }
        # print(config)
        # t = threading.Thread(target= M3U8Downloader(config, 16).run)
        # threads.append(t)
        # t.start()
        
        p1=Process(target=download_thread,args=(logs,config,))
        processes.append(p1)
        p1.start()
        # M3U8Downloader(config, 16).run()
   
    for t in processes:
        t.join()
    logs += "\n全部下载完成"
    set_value("##log",logs)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    add_additional_font("simsun.ttc", 18, "chinese_full")
    set_main_window_size(800, 800)

    with window("Tutorial", width=600, height=600, x_pos=100, y_pos=100, no_title_bar=True):
        add_text("文件名：  \t")
        add_same_line(spacing=10)
        add_input_text(name="##NamePre",default_value="喜羊羊与灰太狼")

        add_text("输出文件夹：  ")
        add_same_line(spacing=10)
        add_button("选择输出文件夹", callback=directory_picker)
        add_same_line(spacing=10)
        add_label_text("##folder_path",default_value="D:\\temp")

        add_text("下载地址：\t")
        add_same_line(spacing=10)
        add_input_text(name="##uris", multiline=True,default_value="https://youku.cdn-8-okzy.com/20180714/19834_63dd109c/index.m3u8\nhttps://youku.cdn-8-okzy.com/20180714/19835_49c2f29f/index.m3u8\nhttps://youku.cdn-8-okzy.com/20180714/19837_33ba4ba3/1000k/hls/index.m3u8")

        add_text("\t")
        add_same_line(spacing=100)
        add_button("开始下载", callback=start_download) # simply sends value through
        # add_same_line(spacing=200)
        # add_button("Press me 2", callback=callback, callback_data=lambda: get_value("##NamePre")) # calls the lambda and sends result through
        add_text("输出信息：\t")
        add_same_line(spacing=10)
        add_input_text(name="##log", multiline=True, height=300)
 
    start_dearpygui()
   
    