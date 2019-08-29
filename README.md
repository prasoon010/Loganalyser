# Loganalyser
Use: to get some useful information from apache accesslog
  
 Help menu:
 ----------------------
 -h, --help            #show this help message and exit
 
 -l LOG, --logfile LOG   #Provide the path of the access log
 
 -i INTERVAL, --interval INTERVAL     #Provide: 'LAST <days>' or 'PREVIOUS DAY/WEEK/MONTH' or date range 'FROM yyyy-mm-dd TO yyyy-mm-dd'
  
 -c COUNT, --count COUNT  #Provide min number of IP count
 
 -ip IP, --ip IP       #Provide IP address
 
 -e IPS, --exclude IPS     #Provide IP address to exclude
  
  Usage
  ----------------------
 To get top n IP hit status:
 
 eg usage1: python3 loganalyser_v2.py -l /usr/local/apache/logs/access_log -i "FROM 2019-08-16 TO 2019-08-20" -c 15
 This will given hit details of top 15 IPs and plot it in graph and will plot IP coordinates on map

To exclude IPs:

eg usage2: python3 loganalyser_v2.py -l /usr/local/apache/logs/access_log -i "LAST 10" -c 15 -e 192.168.16.1 -e 192.168.2.4
    
To obtain details of any particular IP:

eg usage3: python3 loganalyser_v2.py -l /usr/local/apache/logs/access_log -i "PREVIOUS WEEK" -ip 192.168.5.7
  
Disclaimer: under development, use at your own risk

  
  
