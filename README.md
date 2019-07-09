# HeadCannon

HeadCannon performs highly-parallel testing of various HTTP header-based vulnerabilities against a large number of targets. It helps developers and security engineers identify unexpected behavior with the following HTTP headers:

* `X-Forwarded-For`
* `True-Client-IP`
* `X-WAP-Profile`
* `Referer`

Under certain conditions, improper handling of these headers can result is certain vulnerabilities:

* DNS rebinding attacks
* XML parsing vulnerabilites
* SSRF attacks
* IP spoofing attacks
* Stored XSS via pre-emptive caching

I made it because MWR Labs never released reson8, and PortSwigger's Collaborator-Everywhere requires Burp Suite Pro. It currently isn't as feature-rich and is basically a PoC at this point, but hey, you get what you pay for, so **it is provided as-is** and you are responsible for how you leverage this tool. I put this together over a pot of coffee on a Saturday morning, so it probably sucks in a number of ways that I'm not even aware of. **ACT RESPONSIBLY**

## Installation

* clone the repo
* `pip install -r requirements.txt`

## Prerequisites

* Python3
* Public server with static IP address
* Registered domain

## Getting Started

1. Set up a public server with a static IP
2. Add two subdomain DNS records to yourdomain.com:
    * `ns1` - an A record pointing to your static server IP
    * `pwn` - an NS record pointing to `ns1.yourdomain.com`. You can name this anything.
3. Have a pint while you wait for your DNS records to propagate.
4. SSH as root into your public server monitor DNS queries with `tcpdump port 53`
5. In a separate terminal, test your setup with `dig +short ns1.yourdomain.com` and `dig +short test.pwn.yourdomain.com`
6. The first `dig` should show the IP of your public server. The second `dig` should timeout but if you see the DNS query in your `tcpdump`, you are ready for testing.

## Usage

    usage: headcannon.py [-h] (-d  | -l ) -a  [-w] [-s] [-t] [-r] [-p] [-v]

    HTTP Header Tester idk

    optional arguments:
    -h, --help        show this help message and exit
    -d , --domain     Domain to target
    -l , --list       Specify list of domains to targets
    -a , --attacker   url of referrer (ex: pwned.com)
    -w , --workers    Max number of concurrent workers (default 10)
    -s, --ssl         use https instead of http
    -t , --timeout    Specify request timeout (default 5 sec)
    -r , --retries    Specify max retries (default 5)
    -p , --proxy      Specify proxy (127.0.0.1:8080 or user:pass@127.0.0.1:8080)
    -v, --verbose     Enable verbose output

Bare minimum requires a target domain and attacker host:

`./headcannon.py --domain google.com --attacker pwn.yourdomain.com`

### Fine-tuning

When using a long list of targets, you can fine-tune the number of concurrent workers, timeout, and retries:

`./headcannon.py --list examples/tesla.com.txt --atacker pwn.yourdomain.com --workers 10  --timeout 3 --retries 1`

`./headcannon.py -l examples/tesla.com.txt -a pwn.yourdomain.com -w 20  -t 3 -r 1`

### Proxy

You can also send it through a proxy if you want to intercept/monitor/log the traffic:

`./headcannon.py --list examples/target_list.txt --attacker pwn.yourdomain.com --proxy 127.0.0.1:8080`

## Notes

* Some vulnerabilities do not manifest as real-time responses to your testing. You'll get some responses minutes, hours, or even days later. After you run HeadCannon, you'll want to leave your DNS sniffer running for a while and check on it periodically.

* I have yet to implement persistent logging, so it is a good idea to pipe the output to a file for future reference.


## Contributions

If you have any ideas for bugfixes or enhancements, feel free to open an issue or submit a pull request.
