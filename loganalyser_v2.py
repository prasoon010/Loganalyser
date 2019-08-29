#!/usr/bin/env  python3
import datetime
import os
import sys
from collections import Counter
import threading
import argparse
import socket
import requests
from dateutil.relativedelta import relativedelta
from pyparsing import (
    ParseException,
    pyparsing_common as ppc,
    CaselessKeyword,
    Or,
    StringEnd
)
from file_read_backwards import FileReadBackwards
import plotly.graph_objects as go
from matplotlib import style
from matplotlib import pyplot as plt
import logparser

style.use('fivethirtyeight')

exclude_ips = ['::1', '127.0.0.1']
count_ip = Counter()
count_status = Counter()
count_request = Counter()
lati = []
longi = []
ip_co = []
threadlist = []
keys = 'b03da5eddcca40d9e62f8e410f333b0e'   #provide your ipstack api key here


def info(*, ip=None, hit=None, key=None):
    if ip is not None and key is not None and hit is not None:
        url = 'http://api.ipstack.com/{}?access_key={}'.format(ip, key)
        response = requests.get(url)
        geodata = response.json()
        code = geodata['country_code'].split()
        print('{:20} : {} {}'.format(ip, hit, code))

    elif hit is None:
        url = 'http://api.ipstack.com/{}?access_key={}'.format(ip, key)
        response = requests.get(url)
        geodata = response.json()
        latitude = geodata['latitude']
        longitude = geodata['longitude']
        lati.append(latitude)
        longi.append(longitude)
        ip_co.append(ip)


def scatter_plot(*, count_ip=None, key=None):
    if count_ip is not None and key is not None:
        for ip in count_ip.keys():
            th = threading.Thread(target=info, kwargs=dict(ip=ip, key=key))
            th.start()
            threadlist.append(th)
        for threads in threadlist:
            threads.join

    ip = requests.get('https://api.ipify.org').text
    url = 'http://api.ipstack.com/{}?access_key={}'.format(ip, keys)
    response = requests.get(url)
    geodata = response.json()
    cur_lati = geodata['latitude']
    cur_longi = geodata['longitude']

    mapbox_access_token = open("mapbox_token").read()  #reads mapbox token from file

    fig = go.Figure(go.Scattermapbox(
            lat=lati,
            lon=longi,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=15, color='rgb(255, 0, 0)'
            ),
            text=ip_co,
        ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=cur_lati,
                lon=cur_longi
            ),
            pitch=0,
            zoom=10
        ),
    )

    fig.show()


def plot_bar(
        *, count_ip=None,
        count_status=None,
        count_request=None,
        ip_no=None):

    if (count_ip is not None and
       count_status is not None and
       count_request is not None and
       ip_no is not None):
        for ip_item in count_ip.most_common(ip_no):
            if ip_item[0] not in exclude_ips:
                ip_x2.append(ip_item[0])
                ip_y2.append(ip_item[1])

                try:
                    th = threading.Thread(target=info,
                                          kwargs=dict(ip=ip_item[0],
                                                      hit=ip_item[1],
                                                      key=keys))
                    th.start()
                    threadlist.append(th)
                except:
                    code = 'system'

        for threads in threadlist:
            threads.join

    else:
        for ip_item in count_ip.items():
            ip_x2.append(ip_item[0])
            ip_y2.append(ip_item[1])
        info(ip=ip_item[0], hit=ip_item[1], key=keys)

    for stat_item in count_status.items():
        stat_x2.append(stat_item[0])
        stat_y2.append(stat_item[1])

    for req_item in count_request.items():
        if req_item[0] is not '-' and not req_item[0].startswith(('\\', '@')):
            req_x2.append(req_item[0])
            req_y2.append(req_item[1])

    stat_x2.reverse()
    stat_y2.reverse()
    req_x2.reverse()
    req_y2.reverse()
    ip_x2.reverse()
    ip_y2.reverse()

    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()

    ax1.barh(ip_x2, ip_y2, color="#008fd5")
    ax1.set_xlabel('Connections')
    ax1.set_ylabel('IPs')
    ax1.set_title('Counting number of connections from the IPs')

    ax2.barh(stat_x2, stat_y2, align='center', color="#008fd5")
    ax2.set_xlabel('Connections')
    ax2.set_ylabel('Status Codes')
    ax2.set_title('Number of connection based on Apache Status')

    ax3.barh(req_x2, req_y2, align='center', color="#008fd5")
    ax3.set_xlabel('Connections')
    ax3.set_ylabel('Request Types')
    ax3.set_title('Number of connections based on request method')
    fig1.subplots_adjust(left=0.15)
    fig2.subplots_adjust(left=0.15)
    fig3.subplots_adjust(left=0.15)
    plt.show()


def validate_ip(IP):
    if IP in exclude_ips:
        sys.exit("IP in exclude list")
    try:
        socket.inet_aton(IP)
    except socket.error:
        sys.exit("Invalid IP")


class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return 'from {start} to {end}'.format(start=self.start, end=self.end)


def handle_last(tokens):
    end = datetime.date.today()
    start = end - relativedelta(days=tokens.n)

    return Interval(start, end)


def handle_previous(tokens):

    if tokens.day:
        end = datetime.date.today()
        start = end - relativedelta(days=1)
        return Interval(start, end)

    elif tokens.week:
        end = datetime.date.today()
        start = end - relativedelta(days=7)
        return Interval(start, end)

    elif tokens.month:
        end = datetime.date.today()
        start = end - relativedelta(months=1)
        return Interval(start, end)


def handle_fromto(tokens):
    return Interval(tokens.start, tokens.end)


def make_date_parser():

    date_expr = ppc.iso8601_date.copy()
    date_expr.setParseAction(ppc.convertToDate())

    expr_last = (CaselessKeyword('LAST') &
                 ppc.integer.setResultsName('n') &
                 StringEnd()).setResultsName('interval').setParseAction(handle_last)

    expr_prev = (CaselessKeyword('PREVIOUS') &
                 Or(CaselessKeyword('DAY').setResultsName('day') |
                 CaselessKeyword('WEEK').setResultsName('week') |
                 CaselessKeyword('MONTH').setResultsName('month')) +
                 StringEnd()).setResultsName('interval').setParseAction(handle_previous)

    expr_fromto_date = (CaselessKeyword('FROM') +
                        date_expr.setResultsName('start') +
                        CaselessKeyword('TO') +
                        date_expr.setResultsName('end') +
                        StringEnd()).setResultsName('interval').setParseAction(handle_fromto)

    parser = expr_fromto_date | expr_last | expr_prev
    return parser


class IntervalAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        self._parser = make_date_parser()
        super(IntervalAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            rv = self._parser.parseString(values)
        except ParseException:
            parser.error('argument %s is not valid' % '/'.join(self.option_strings))
        else:
            setattr(namespace, self.dest, rv.interval)


def list_counter(logline):
    d_ip = logparser.parser(logline)['host']
    count_ip.update([d_ip])

    d_status = logparser.parser(logline)['status']
    count_status.update([d_status])

    d_request = logparser.parser(logline)['request'].split()[0]
    count_request.update([d_request])


if __name__ == '__main__':

    clen1 = len(exclude_ips)

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logfile",
                        dest="log",
                        required=True,
                        help="Provide the path of the access log")

    parser.add_argument('-i', '--interval',
                        action=IntervalAction,
                        required=True,
                        help="Provide: 'LAST <days>' or \
                             'PREVIOUS DAY/WEEK/MONTH' or \
                             date range 'FROM yyyy-mm-dd TO yyyy-mm-dd'")

    parser.add_argument("-c", "--count",
                        type=int,
                        dest="count",
                        default="10",
                        help="Provide min number of IP count")

    parser.add_argument("-ip", "--ip",
                        dest="IP",
                        help="Provide IP address")

    parser.add_argument("-e", "--exclude",
                        action='append',
                        dest="IPs",
                        help="Provide IP address to exclude")

    args = parser.parse_args()
    abc = args.interval
    s_epoch = abc.start.strftime("%s")
    e_epoch = abc.end.strftime("%s")

    if not os.path.isfile(args.log):
        sys.exit("log file does not exist")

    if args.IPs:
        exclude_ips.extend(args.IPs)

    clen2 = len(exclude_ips)
    clen = clen2-clen1

    if args.IP:
        validate_ip(args.IP)

    if args.IP is None:
        print("############# Welcome #############")
        print('Exclude IP list: {}'.format(exclude_ips))
        with FileReadBackwards(args.log) as fh:
            for logline in fh:
                r_date = logparser.parser(logline)['time']
                da = datetime.datetime.strptime(r_date, '%d/%b/%Y:%H:%M:%S %z')
                r_epoch = da.strftime("%s")

                if r_epoch >= s_epoch:
                    if r_epoch <= e_epoch:
                        list_counter(logline)
                else:
                    fh.close()

    else:
        print("############# Welcome #############")
        with FileReadBackwards(args.log) as fh:
            for logline in fh:
                r_date = logparser.parser(logline)['time']
                da = datetime.datetime.strptime(r_date, '%d/%b/%Y:%H:%M:%S %z')
                r_epoch = da.strftime("%s")

                if r_epoch >= s_epoch:
                    if r_epoch <= e_epoch:
                        if args.IP == logparser.parser(logline)['host']:
                            list_counter(logline)

                else:
                    fh.close()


ip_no = args.count+clen
ip_x2 = []
ip_y2 = []
stat_x2 = []
stat_y2 = []
req_x2 = []
req_y2 = []


if args.IP is None:
    t_hit = sum(count_ip.values())
    print('Total Hits: {}'.format(t_hit))
    print('\nTop {} hit IPs list:'.format(args.count))
    plot_bar(count_ip=count_ip,
             count_status=count_status,
             count_request=count_request, ip_no=ip_no)
else:
    plot_bar(count_ip=count_ip,
             count_status=count_status,
             count_request=count_request)

a = input("\nWould you like to plot IPs geo-coordinates on Map?(y/n)")

if a == 'y':
    scatter_plot(count_ip=count_ip, key=keys)
