#!/usr/bin/env python3

from collections import namedtuple
import datetime
from bs4 import BeautifulSoup
from dateutil import tz
import time
import dateutil.parser
from pytz import tzinfo
import pytz
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import xlim


HEX_BLUE = '#0000ff'
HEX_GREEN = '#00ff00'

Thread = namedtuple('Thread', ['names', 'messages'])
Message = namedtuple('Message', ['name', 'date', 'text'])

path = 'facebook-downloaded/html/messages.htm'
my_name = 'Martin Taibr'


def maximize():
    backend = matplotlib.get_backend()
    mng = plt.get_current_fig_manager()

    # TkAgg and wxAgg are not tested, comment out if they crash
    if backend == 'Qt4Agg':
        mng.window.showMaximized()
    elif backend == 'TkAgg':
        mng.resize(*mng.window.maxsize())
        # mng.window.state('zoomed')  # try this instead on windoze
    elif backend == 'wxAgg':
        mng.frame.Maximize(True)


def parse(soup: BeautifulSoup) -> list:
    threads = []

    for thread_html in soup.find_all('div', {'class': 'thread'}):
        thread = list(thread_html)
        title = thread[0]
        if '@facebook.com' in title: continue  # message from facebook
        messages = thread[1:]
        names = title.split(', ')

        msgs = []
        name = None
        date = None
        text = None
        for i in range(len(messages)):  # message is two tags - div (header) and p (text)
            tag = messages[i]
            if i % 2 == 0:  # message header
                user_spans = tag.find_all('span', {'class': 'user'})
                name = user_spans[0].text
                date_spans = tag.find_all('span', {'class': 'meta'})
                date = dateutil.parser.parse(date_spans[0].text)
            else:  # message text
                text = tag.text
                msgs.append(Message(name, date, text))

        threads.append(Thread(names, list(reversed(msgs))))  # reverse to order messages by date

    return sorted(threads, key=lambda thread: thread.messages[0].date)


def plot(threads: list):
    dates = []  # X
    vals = []  # Y
    first_dates = []  # first message in a day
    first_vals = []
    last_dates = []  # last message in a day
    last_vals = []
    colors = []
    first_colors = []
    last_colors = []

    val_to_name = {}
    val = 0  #
    for thread in threads:
        # pick only some threads, remove my name
        names = thread.names
        if my_name not in names:
            continue
        if len(names) > 2:
            continue
        names.remove(my_name)
        val_to_name[val] = str.format('{0} ({1})', names[0], len(thread.messages))

        # plot messages
        last_date = datetime.datetime(1970, 1, 1, tzinfo=pytz.timezone('GMT'))
        last_message = None
        for message in thread.messages:
            dt = message.date - last_date

            dates.append(message.date)
            vals.append(val)
            if message.name == my_name:
                colors.append(HEX_BLUE)
            else:
                colors.append(HEX_GREEN)

            if dt.days >= 1:
                if last_message is not None:
                    last_dates.append(last_message.date)
                    last_vals.append(val)
                    if last_message.name == my_name:
                        last_colors.append(HEX_BLUE)
                    else:
                        last_colors.append(HEX_GREEN)

                first_dates.append(message.date)
                first_vals.append(val)
                if message.name == my_name:
                    first_colors.append(HEX_BLUE)
                else:
                    first_colors.append(HEX_GREEN)


            last_date = message.date
            last_message = message

        last_dates.append(last_message.date)
        last_vals.append(val)
        if last_message.name == my_name:
            last_colors.append(HEX_BLUE)
        else:
            last_colors.append(HEX_GREEN)

        val += 1

    t_generated = time.time()

    plt.scatter(first_dates, first_vals, s=50, c=first_colors, marker=2)
    plt.scatter(last_dates, last_vals, s=50, c=last_colors, marker=3)
    plt.scatter(dates, vals, s=50, c=colors, marker='|', alpha=0.2)
    ax = plt.subplot()
    ax.xaxis.grid()
    ax.yaxis.grid()
    ax.yaxis.set_ticks(range(0, len(threads) - 1))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: val_to_name.get(x)))
    lims = xlim()
    xlim(lims[0], datetime.datetime.now())  # align right to today

    maximize()

    t_plotted = time.time()

    #plt.show()

    return t_generated, t_plotted


def print_all(threads: list):
    msgs = 0
    words = 0
    for thread in threads:
        print(thread.names)
        for message in thread.messages:
            msgs += 1
            words += len(message.text.split(' '))
            print(message.date, message.name, message.text)
    print(msgs, words)


def main():
    matplotlib.rc('font', family='DejaVu Sans')  # default font doesn't support some chars
    t_start = time.time()
    soup = BeautifulSoup(open(path))
    t_loaded = time.time()
    print("Loaded in:", t_loaded - t_start)
    threads = parse(soup)
    t_parsed = time.time()
    print("Parsed in:", t_parsed - t_loaded)
    t_generated, t_plotted = plot(threads)
    print("Generated in:", t_generated - t_parsed)
    print("Plotted in:", t_plotted - t_generated)
    plt.show()


if __name__ == '__main__':
    main()
