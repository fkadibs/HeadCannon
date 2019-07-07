#!/usr/bin/python3
import sys
import uuid
import time
import asyncio
import argparse
import requests
from random import choice
from colorama import Fore, Style, init
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor


banner = """
    {}:{}:{} H E A D C A N N O N {}:{}:{}
"""


def timestamp(): return time.strftime('%x %X')
def info(string): print('{}{}[+]{} {}{}{} - {}'.format(Style.BRIGHT, Fore.BLUE, Style.RESET_ALL, Style.DIM, timestamp(), Style.RESET_ALL, string))
def warn(string): print('{}{}[!]{} {}{}{} - {}'.format(Style.BRIGHT, Fore.YELLOW, Style.RESET_ALL, Style.DIM, timestamp(), Style.RESET_ALL, string))
def error(string): print('{}{}[!]{} {}{}{} - {}'.format(Style.BRIGHT, Fore.RED, Style.RESET_ALL, Style.DIM, timestamp(), Style.RESET_ALL, string))
def stats(key, value): print('{:>16}{} : {}{}{}{}'.format(key, Style.DIM, Style.BRIGHT, Fore.CYAN, value, Style.RESET_ALL))


user_agents =  ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']


def test_url(session, host, referer):
    if args.ssl:
        protocol = 'https://'
    else:
        protocol = 'http://'

    # build the headers with uuid for tracking
    forwarded_for = host + '.forwardfor.' + referer
    true_client_ip = host + '.trueclient.' + referer
    wap_profile = protocol + host + '.wap.' + referer + '/wap.xml'
    referer = protocol + host + '.referer.' + referer
    user_agent = choice(user_agents)

    headers = {'X-Forwarded-For' : forwarded_for,
               'True-Client-IP' : true_client_ip,
               'X-WAP-Profile' : wap_profile,
               'Referer' : referer,
               'User-Agent': user_agent,
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    
    info('{}{}{}{} - {}'.format(Style.BRIGHT, Fore.BLUE, 'GET', Style.RESET_ALL, host))

    # send the request, check the status
    try:
        response = session.get(protocol+host, 
                               headers=headers, 
                               timeout=args.timeout, 
                               proxies=proxies,
                               verify=False)

        if response.status_code != 200:
            if args.verbose:
                warn('{}{}{}{} - {}'.format(Style.BRIGHT, Fore.YELLOW, response.status_code, Style.RESET_ALL, host))
        return True

    except Exception as e:
        if args.verbose:
            error('{}{}{}{} - {}'.format(Style.BRIGHT, Fore.RED, 'ERR', Style.RESET_ALL, host))
        return False


async def run_ansync():
    if args.list:
        with open(args.list, 'r') as f:
            target_list = [t.strip() for t in f.readlines()]
    else:
        target_list = [args.domain]

    # show the config
    stats('workers', args.workers)
    stats('targets', len(target_list))
    
    print('')

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        with requests.Session() as session:
            # configure the retries
            retry = Retry(
                total=args.retries,
                backoff_factor=0.3,
                status_forcelist=(500, 502, 504),
            )
            adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=50)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            # configure the connection
            session.keep_alive = False

            # in case SSL fails
            session.verify = False
            requests.packages.urllib3.disable_warnings()

            # run in executor loop
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    test_url,
                    *(session, target, args.attacker)
                )
                for target in target_list
            ]
            for response in await asyncio.gather(*tasks):
                pass
            

def main():
    # cross platform colorama
    init()

    # show the leet banner
    print(banner.format(Fore.CYAN, Fore.MAGENTA, Style.RESET_ALL, Fore.MAGENTA, 
           Fore.CYAN, Style.RESET_ALL))

    # start the async loop
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_ansync())
    loop.run_until_complete(future)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('try ./headcannon.py --help')
        exit(0)

    parser = argparse.ArgumentParser(description="HTTP Header Tester idk")
    parser.add_argument('-d', '--domain', metavar='', help='Domain to target')
    parser.add_argument('-l', '--list', metavar='', help='Specify list of domains to targets')
    parser.add_argument('-w', '--workers', type=int, metavar='', default=10, help='Max number of concurrent workers (default 10)')
    parser.add_argument('-a', '--attacker', required=True, metavar='', help='url of referrer (ex: pwned.com)')
    parser.add_argument('-s', '--ssl', action='store_true', default=False, help='use https instead of http')
    parser.add_argument('-t', '--timeout', type=int, metavar='', default=5, help='Specify request timeout (default 5 sec)')
    parser.add_argument('-r', '--retries', type=int, metavar='', default=5, help='Specify max retries (default 5)')
    parser.add_argument('-p', '--proxy', metavar='', help='Specify proxy (127.0.0.1:8080 or user:pass@127.0.0.1:8080)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    if args.proxy:
        proxies = {'http': args.proxy, 'https': args.proxy}
    else:
        proxies = None

    main()
