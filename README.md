README for scan_downloader.py

##Background and Overview##

This is a simple Python package that implements a concurrent, chunk-based file downloader. 
Effectively, scan_downloader works by first using the HTTP GET request to elicit the proper
response.  If the response can be broken down into valid chunks, we proceed in this manner;
otherwise, we download the file normally (in a non-concurent manner).  Continuing with
the chunks, we essentially then break the 'file' (really the response) down into chunks,
fill the queue with the number of jobs we have (which is equivalent to the number of 
threads), begin those threads, assign the chunks to our threads, and wait till our
download is complete.  We finally merge the downloaded chunks into the emergent file,
and voilà, our file is downloaded!


##Required external libraries##

Please ensure your system has access (via Pip) to the following packages:

requests
threading
shutil
argparse
urllib.request
timeit
time
os
queue

##Usage##

Proper usage from the command line is as follows:

py scan_downloader.py <URL> -c nThreads

Where <URL> is a valid URL and nThreads is the integer number of threads that will be used to concurrently download the
chunks of the URL to the local system.  


##Some Closing Comments##

Overall, I am extremely happy with the performance of my code.  The approach of breaking the HTTP response down into
managable chunks and then concurrently downloading those chunks is much faster than a simple full download of a the file.
In terms of my design choices, I appreciated my use of the job_queue in order to organize the thread pool.  Moreover,
I also liked that I split the chunks into their own class (i.e. ChunkItem) for ease of use, and that I used the
'interrupted' variable to re-try and identify chunks that are refusing to download.  By doing this, I mitigate
the issue of a connection failing mid-download.  Moreover, I also insure that the quality of the file does not
degrade due to the fact that I break the raw HTTP data into chunks, and thus no quality is lost.  In addition,
I miiigate user mis-use of the program by ensuring that the two necessary parameters are entered.  One potential
issue I forsee is that I currently do not do any regex/other checking for the url, so malformed webpages may be downloaded.
I made this choice, however, because many webpages are odd and may be correct, even if the return header is odd.  In terms
of input verification, however, argparse does check the type of the input for the CLI arguments, so a user can never put 
a letter/non-numeric 'number' for the number of threads.  The last comment I would like to make is on scale: I believe
this program scales incredibly well, but since the number of threads is a user parameter, this crucial portion of the
concurrency (and thus scale of the program) is dependant on the user.  Therefore, moving forward, we might 
consult research in computer science to automatically optimize the number of threads.  

##Testing##

Please run scan_downloader_test.py to see some (successful) preliminary tests
