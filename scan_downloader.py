import requests
import threading
import shutil
import argparse
import urllib.request
import timeit
import time
import os
import queue


class ChunkItem:
    def __init__(self, chunk_id, range_of_item, interrupted=False):
        #chunk id to be downloaded
        self.chunk_id = chunk_id  
        #chunk range to download from server
        self.range_of_item = range_of_item 
        #check whether thisc chunk downloaded 
        self.interrupted = interrupted  


class MultithreadedChunkDownloader:
    def __init__(self, url=None, number_of_threads=1):
        # url of a file to be downloaded
        if url is None:
            raise ImportWarning("Please enter a non-nul url")
        self.url = url 
        #file extension of file
        self.file_extension = os.path.splitext(url)[1]
        #number of threads
        if  number_of_threads is None or number_of_threads < 1:
            raise ImportWarning("Please enter a number of a threads that's greater than 0")
        self.number_of_threads = number_of_threads  
        #check file type and get file size if ok
        try:
            self.file_size = int(requests.head(self.url, headers={'Accept-Encoding': 'identity'}).headers.get('content-length')) 
        except:
            print("Enter a valid URL that points to a file!")
            exit(0)
        #byte/response header range list
        self.range_list = list() 
        #time to keep track of performance/timing
        self.start_time = None  
        self.end_time = None  
        #name of downloaded file
        self.downloaded_file_name = os.path.basename(self.url)  
        #queue of workers
        self.job_queue = queue.Queue(maxsize=0)  
        #current download_status
        self.download_status = []
        #current overall progress 
        self.current_status = ""

        
        
    def begin_macro_download(self):
        #download the file in chunks if the byte_range is valid
        self.start_time = timeit.default_timer()
        if self.is_valid_byte_range():
            #since we use the temp dir, we need to delete it if it exists
            if os.path.isdir("temp"):
                shutil.rmtree("temp")
            os.makedirs("temp")

            self.initialize_queue()

            print("Initiializing threads and beginning concurrent downloads:")
            for i in range(self.number_of_threads):
                thread = threading.Thread(target=self.download_chunk)
                thread.setDaemon(True)
                thread.start()
            print("Finished initializing threads")

            #print our download status every 0.5 seconds
            while self.get_download_status():
                print(self.current_status)
                time.sleep(0.5)

            self.job_queue.join()
            print(self.current_status)
            print("Done downloading chunks")
            print("Merging chunks to create the final file")
            #rename the file if needed
            try:
                with open(self.downloaded_file_name, "ab") as fun:
                    pass 
            except:
                #default name plus the extension of the file
                self.downloaded_file_name = "your_downloaded_file" +  self.file_extension
            with open(self.downloaded_file_name, "ab") as final_file:
                for i in range(self.number_of_threads):
                    with open("temp/part" + str(i), "rb") as chunk_file:
                        final_file.write(chunk_file.read())
            print("Finished merging")

            if os.path.isdir("temp"):
                shutil.rmtree("temp")

        else:
            print("Range is not supported, so let's download all at once!")
            try:
                self.download_entire_file()
                print("Done")
            except:
                print("Error occurred while downloading.")
        self.end_time = timeit.default_timer()

    def initialize_queue(self):
        #fill the job queue
        self.create_byte_range()
        for chunk_id, range_of_item in enumerate(self.range_list):
            self.job_queue.put(ChunkItem(chunk_id, range_of_item, False))

    def download_chunk(self):
        #download the junk in the queue that we would like
        append_type = "wb"
        while True:
            item = self.job_queue.get()
            try:
                #try again if interrupted
                if item.interrupted:
                    time.sleep(1)
                    if os.path.isfile("temp/part" + str(item.chunk_id)):
                        append_type = "ab"
                        temp = item.range_of_item.split('-')
                        item.range_of_item = str(int(temp[0]) + os.stat("temp/part" + str(item.chunk_id)).st_size) + '-' + temp[1]
                req = urllib.request.Request(self.url)
                req.headers['Range'] = 'bytes={}'.format(item.range_of_item)
                with urllib.request.urlopen(req) as response, open('temp/part' + str(item.chunk_id), append_type) as out_file:
                    shutil.copyfileobj(response, out_file)
            #set interrupted to true if it was
            except IOError:
                item.interrupted = True
                self.job_queue.put(item)
            #when done
            finally:
                self.job_queue.task_done()

    def download_entire_file(self):
        #download the file
        r = requests.get(self.url, stream=True)
        with open(self.target_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                #common practice to keep alive chunks only
                if chunk:
                    f.write(chunk)

    def get_download_status(self):
        #returns current download status separated by tabs for ease of use
        self.download_status.clear()
        for thread in range(self.number_of_threads):
            if os.path.isfile("temp/part" + str(thread)):
                self.download_status.append(str(round(os.stat("temp/part" + str(thread)).st_size/(self.file_size/self.number_of_threads) * 100, 2)) + "%")
            else:
                self.download_status.append("0.00%")
        self.current_status = '\t\t'.join(self.download_status)
        if all(x == "100.0%" for x in self.download_status):
            return False
        else:
            return True

            
    def is_valid_byte_range(self):
        #return whether we our range is valid or not
        server_byte_response = requests.head(self.url, headers={'Accept-Encoding': 'identity'}).headers.get('accept-ranges')
        if server_byte_response is None or server_byte_response == "none" or server_byte_response == "None":
            return False
        else:
            return True

    def create_byte_range(self):
        #Defines the range of bytes to be downloaded per each chunk
        cont_sum = 0
        chunk_size = int(int(self.file_size) / int(self.number_of_threads))
        for j in range(self.number_of_threads):
            if(cont_sum + chunk_size) < self.file_size:
                cur_entry = '%s-%s' % (cont_sum, cont_sum + chunk_size - 1)
            else:
                cur_entry = '%s-%s' % (cont_sum, self.file_size)
            cont_sum += chunk_size
            self.range_list.append(cur_entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('URL', type = str, help='The URL to download from')
    parser.add_argument('-c', metavar = "nThreads", type=int, help = 'The number of threads to use')
    args = parser.parse_args()
    num_threads = args.c
    url = args.URL
    if num_threads is None or url is None or len(url) < 3 or num_threads == 0:
        raise ImportWarning("Please enter both a URL and a number of threads to use that's >= 0! Use the -h for help!")
    MultithreadedChunkDownloader(url, num_threads).begin_macro_download()