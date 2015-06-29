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
my_name = None

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
    div = soup.find('div', {'class': 'contents'})
    h = next(div.children)
    global my_name
    my_name = h.text

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


def filter_(threads: list):
    new_threads = []

    for thread in threads:
        # pick only some threads, remove my name
        if my_name not in thread.names:
            continue
        if len(thread.names) > 2:
            continue
        thread.names.remove(my_name)
        new_threads.append(thread)

    return new_threads


def generate_stats(threads: list):
    t_start = time.time()

    for thread in threads:
        name = thread.names[0]
        msgs_me = 0
        msgs_them = 0
        words_me = 0
        words_them = 0
        for message in thread.messages:
            if message.name == my_name:
                msgs_me += 1
                words_me += len(message.text.split())
            else:
                msgs_them += 1
                words_them += len(message.text.split())

        print(name)
        print(str.format("\tMessages me: {0}", msgs_me))
        print(str.format("\tMessages them: {0}", msgs_them))
        print(str.format("\tWords me: {0}", words_me))
        print(str.format("\tWords them: {0}", words_them))

    t_generated = time.time()
    print("Stats generated in:", t_generated - t_start)


def plot(threads: list):
    t_start = time.time()

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
    val = 0  # the line we plot on
    for thread in threads:
        val_to_name[val] = str.format('{0} ({1})', thread.names[0], len(thread.messages))

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
    print("Message summary generated in:", t_generated - t_generated)

    plt.scatter(first_dates, first_vals, s=50, c=first_colors, marker=2)
    plt.scatter(last_dates, last_vals, s=50, c=last_colors, marker=3)
    plt.scatter(dates, vals, s=50, c=colors, marker='|', alpha=0.2)
    ax = plt.subplot()
    ax.xaxis.grid()
    ax.yaxis.grid()
    ax.yaxis.set_ticks(range(0, len(threads)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: val_to_name.get(x)))
    lims = xlim()
    xlim(lims[0], datetime.datetime.now())  # align right to today

    maximize()

    t_plotted = time.time()
    print("Message summary plotted in:", t_plotted - t_generated)

    #plt.show()


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
    print("Loading...")
    soup = BeautifulSoup(open(path))
    t_loaded = time.time()
    print("Loaded in:", t_loaded - t_start)
    threads = parse(soup)
    t_parsed = time.time()
    print("Parsed in:", t_parsed - t_loaded)
    threads = filter_(threads)
    generate_stats(threads)
    plot(threads)

    plt.show()


if __name__ == '__main__':
    main()
