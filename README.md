# HeadCannon

HeadCannon performs highly-parallel testing of various HTTP header-based vulnerabilities against a large number of targets. 

I made it because MWR Labs never released reson8, and PortSwigger's Collaborator-Everywhere requires Burp Suite Pro. It currently isn't as feature-rich and is basically a PoC at this point, but hey, you get what you pay for, so **it is provided as-is** and you are responsible for how you leverage this tool. I put this together over a pot of coffee on a Saturday morning, so it probably sucks in a number of ways that I'm not even aware of. **ACT RESPONSIBLY**

## Installation

* clone the repo
* `pip install -r requirements.txt`

## Prerequisites

* Python3
* Public server with static IP address
* Registered domain

## Getting Started

1. Set up a public server with a static ip
2. Add two DNS records to yourdomain.com:
    * `ns1` - an A record pointing to your static server ip
    * `pwn` - an NS record pointing to `ns1.yourdomain.com`
3. SSH at root into your public server monitor DNS with `tcpdump -n port 53`
4. In a separate terminal, test your setup with `dig +short ns1.yourdomain.com` and `dig +short test.pwn.yourdomain.com`

## Usage

Bare minimum requires a target domain and attacker host:

`./headcannon.py --domain google.com --attacker pwn.yourdomain.com

When running a list of domains/subdomains, you can fine-tune the number of concurrent workers, timeout, and retries:

`./headcannon.py --list examples/target_list.txt --workers 10 --atacker pwn.yourdomain.com --timeout 3 --retries 1'
`./headcannon.py -l examples/target_list.txt -w 20 -a pwn.yourdomain.com -t 3 -r 1'

**Note**: some vulnerabilities do not manifest as real-time responses to your testing. You'll get some responses minutes, hours, or even days later. In order to help map responses you receive to the test you performed, each request is assigned a UUID. I have yet to implement proper logging, so you might want to pipe the output to a file for future reference.


## Contributions

If you have any ideas for bugfixes or enhancements, feel free to open an issue or submit a pull request.

