import scan_downloader
import os
import requests
import unittest


class Test(unittest.TestCase):
    def test_bad_inputs(self):
        urls = [
                "google.com",
                "www.google.com",
                "",
                "google",
                "a.c",
                "sadasdsadasad",
                "12321312",
                "http://www.google.com",
                "https://upload.wikimedia.org/wikipedia/commons/6/60/Matterhorn_from_Domh%C3%BCtte_-_2.jpg",
                #bad name, so rename
                "https://media2.giphy.com/media/jbKbdoKJOFusHTjl80/giphy.gif?cid=790b7611182321bb46b8b609f46509f566a26b829699e39d&rid=giphy.gif"

            ]

        #try None input and 0 threads
        try:
            scan_downloader.MultithreadedChunkDownloader(urls[8], 0).begin_macro_download()
        except ImportWarning:
            print("0 threads error caught!")
        
        try:
            scan_downloader.MultithreadedChunkDownloader(None, 1).begin_macro_download()
        except ImportWarning:
            print("None input error caught!")

        try:
            scan_downloader.MultithreadedChunkDownloader(urls[8], None).begin_macro_download()
        except ImportWarning:
            print("None input error caught!")

        try:
            scan_downloader.MultithreadedChunkDownloader(None, None).begin_macro_download()
        except ImportWarning:
            print("None input error caught!")

        #prints error output as desired
        for i in range(8):
            try:
                scan_downloader.MultithreadedChunkDownloader(urls[i], 3).begin_macro_download()
            except:
                pass
        #try for many thread numbers
        for i in [1, 5, 10, 20]:
            scan_downloader.MultithreadedChunkDownloader(urls[8], i).begin_macro_download()
            #check if previous file exsits
            self.assertTrue(os.path.isfile("Matterhorn_from_Domh%C3%BCtte_-_2.jpg"))
            scan_downloader.MultithreadedChunkDownloader(urls[9], i).begin_macro_download()
            #check if previous file exsits
            self.assertTrue(os.path.isfile("your_downloaded_file.gif"))

       
if __name__ == "__main__":
    unittest.main()