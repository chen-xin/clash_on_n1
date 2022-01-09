from pathlib import Path
import yaml
from datetime import datetime, date
import time
import re
import random
import urllib.request

###############################################################################
# Utils
###############################################################################
def log_wrapper(info):
    def log(fn):
        def f(*args, **kwargs):
            print(datetime.now(), info, args, kwargs)
            return fn(*args, **kwargs)
        return f
    return log

@log_wrapper('downloading')
def fetch_profile(url):
    req = urllib.request.Request(url=url, method='GET')

    req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    # req.add_header("Accept-Encoding", "gzip, deflate, br")
    # req.add_header("Accept-Language", "en-US,en;q=0.5")
    req.add_header("Connection", "keep-alive")
    # req.add_header("Host", "sub.9ups.xyz")
    req.add_header("Upgrade-Insecure-Requests", "1")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0")

    with urllib.request.urlopen(req) as f:
        result = f.read().decode('utf-8', errors='ignore')

    return result

def read_config_yaml(filename):
    # with FileInput(files=(filename)) as input:
    with open(filename) as input:
        data = yaml.safe_load(input.read())
    return data

def save_config_yaml(data, filename):
    with open(filename, 'w', encoding='utf8') as output:
        yaml.dump(data, output, allow_unicode=True, sort_keys=False)

'''
# edu
url: http://localhost:8000/1625538106859.yml
# haojiahuo
url: http://localhost:8000/1625537897280.yml'
# 厘米
url: http://localhost:8000/1614092014120.yml
'''

def sort_proxy_by_rate(pattern, proxies):
    proxy_list = []
    for p in proxies:
        matched = pattern.search(p['name'])
        try:
            rate = float([x for x in re.split(r'[^\d\.]', matched[0]) if x!=''][-1])
        except:
            rate = 1
        print(p['name'], '----', pattern, matched, '===', rate)
        proxy_list.append((rate, p))
    return [ x[1] for x in sorted(proxy_list, key = lambda a: a[0]) ]

def get_game_proxies(patterns, proxies):
    proxy_list = []
    for p in proxies:
        for index, pattern in enumerate(patterns):
            if pattern.search(p['name']):
                proxy_list.append((index, p))
                # proxy_list.append(p)
                continue
    return [ x[1] for x in sorted(proxy_list, key = lambda a: a[0]) ]

###############################################################################
# main
###############################################################################
if __name__ == '__main__':
    '''
    result = re.search(r'\|\d(\.\d)?:\d(\.\d)?\|', '🇭🇰 HK NetFlix CU104.17.12.28·1#20|0.8:1|49')
    result = re.search(r'\[X\d(\.\d)?\]', '🇰🇷 韩国-优化2[X1.3]')
    # result = re.search(r'·\d(\.\d)?', '俄罗斯A·0.5')
    print(result, result[0])
    print(float([x for x in re.split(r'[^\d\.]', result[0]) if x!=''][-1]))
    quit()
    '''

    GAME_REGX = 'game_candidate_regx'
    conf = read_config_yaml('./data/providers.yaml')
    proxy_groups = read_config_yaml('./autoupdater/conf/_proxy-groups.yaml')['proxy-groups']
    proxy_groups_fixed = read_config_yaml('./autoupdater/conf/_proxy-groups_fixed.yaml')['proxy-groups']

    providers = []
    for provider_conf in conf:
        if provider_conf['expire'] > date.today():
            data_yaml = fetch_profile(provider_conf['url'])
            data = yaml.safe_load(data_yaml)
            providers.append({
                'name': provider_conf['name'],
                'proxies': data['proxies'],
                'rules': data['rules'],
                'order_regx': re.compile(provider_conf['order_regx']),
                GAME_REGX: [ re.compile(x) for x in provider_conf[GAME_REGX] ]
            })

    first5_cheap_proxies = [
        x['name'] for provider in providers
        for x in sort_proxy_by_rate(provider['order_regx'], provider['proxies'])[:5]
    ]

    for provider in providers:
        print(provider['name'], len(provider['proxies']))

    get_first5_game_proxies = lambda x: [i for i in filter(lambda y: re.search(x[GAME_REGX], y['name']), x['proxies'])][:5]
    first6_game_proxies = [ x['name'] for p in providers for x in get_game_proxies(p[GAME_REGX], p['proxies'])[:6] ]

    # print(first5_cheap_proxies)
    print(first6_game_proxies )

    get_group_name = lambda x: [v['name'] for v in x]
    all_group_names = get_group_name(providers) + get_group_name(proxy_groups) + get_group_name(proxy_groups_fixed)

# - INSERT PRIOR_PROXIES
# - INSERT ALL_PROVIDERS
# - INSERT GAME_PROXIES
    # print(all_group_names)
    for g in proxy_groups:
        gproxies = []
        for p in g['proxies']:
            print('[%s]'%p)
            if p in all_group_names:
                gproxies.append(p)
            elif p == 'INSERT PRIOR_PROXIES':
                gproxies += first5_cheap_proxies
            elif p == 'INSERT ALL_PROVIDERS':
                gproxies += [provider['name'] for provider in providers]
            elif p == 'INSERT GAME_PROXIES':
                print('=============')
                gproxies += first6_game_proxies
        g['proxies'] = gproxies
    print(proxy_groups)
