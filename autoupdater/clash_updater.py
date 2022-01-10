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
def log_wrapper(info, n=0):
    def log(fn):
        def f(*args, **kwargs):
            try:
                result = fn(*args, **kwargs)
                print(datetime.now(), info, args[n])
            except:
                print(datetime.now(), 'FAIL::', info, args[n])
                raise
            return result
        return f
    return log

@log_wrapper('Downloading')
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

@log_wrapper('Load config')
def read_config_yaml(filename):
    # with FileInput(files=(filename)) as input:
    with open(filename) as input:
        data = yaml.safe_load(input.read())
    return data

@log_wrapper('Save config', 1)
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
        # print(p['name'], '----', pattern, matched, '===', rate)
        proxy_list.append((rate, p))
    return [ x[1] for x in sorted(proxy_list, key = lambda a: a[0]) ]

def get_game_proxies(patterns, proxies):
    proxy_list = []
    pattern_regxes = [ re.compile(x) for x in patterns ]
    for p in proxies:
        for index, pattern in enumerate(pattern_regxes):
            if pattern.search(p):
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
    # provider_conf = read_config_yaml('./autoupdater/conf/providers-sample.yaml')
    updater_conf = read_config_yaml('./autoupdater/conf/config.yaml')
    provider_conf = updater_conf['providers']
    configure_cfw = updater_conf['config']
    configure = {  **updater_conf['config'], **updater_conf['config_server'] }
    proxy_groups = updater_conf['proxy-groups']
    proxy_groups_fixed = updater_conf['proxy-groups-fixed']
    additional_rules = updater_conf['additional_rules']

    providers = []
    provider_rules = []
    provider_game_proxies = []
    all_proxies = []
    for provider in provider_conf:
        if provider['expire'] > date.today():
            try:
                data_yaml = fetch_profile(provider['url'])
            except:
                continue
            data = yaml.safe_load(data_yaml)

            if len(provider_rules) == 0 and 'use_rules' in provider and provider['use_rules']:
                provider_rules = data['rules']
            sort_regx = re.compile(provider['order_regx'])
            provider_proxies = [ x for x in sort_proxy_by_rate(sort_regx, data['proxies']) ]
            provider_proxy_names =[ x['name'] for x in provider_proxies]
            all_proxies += provider_proxies
            # add fallback prior to select
            if 'type' in provider and provider['type'] == 'fallback':
                providers.append({
                    'name': provider['name'] + '_FALLBACK',
                    'proxies': provider_proxy_names,
                    # 'rules': data['rules'],
                    # 'game_proxies': [],
                    'type': 'fallback',
                    'url': provider['test_url'],
                    'interval': provider['interval']
                })
            providers.append({
                'name': provider['name'],
                'proxies': provider_proxy_names,
                # 'game_proxies': get_game_proxies(provider[GAME_REGX], provider_proxies),
                'type': 'select'
            })
            provider_game_proxies.append(get_game_proxies(provider[GAME_REGX], provider_proxy_names))

    first5_cheap_proxies = [ x for p in providers if p['type'] != 'fallback' for x in p['proxies'][:5] ]
    first6_game_proxies = [ x for p in provider_game_proxies for x in p[:6] ]

    # print(first5_cheap_proxies)
    # print(first6_game_proxies )

    get_group_name = lambda x: [v['name'] for v in x]
    all_group_names = get_group_name(providers) + get_group_name(proxy_groups) + get_group_name(proxy_groups_fixed)

# - INSERT PRIOR_PROXIES
# - INSERT ALL_PROVIDERS
# - INSERT GAME_PROXIES
    # print(all_group_names)
    for g in proxy_groups:
        gproxies = []
        for p in g['proxies']:
            # print('[%s]'%p)
            if p in all_group_names:
                gproxies.append(p)
            elif p == 'INSERT PRIOR_PROXIES':
                gproxies += first5_cheap_proxies
            elif p == 'INSERT ALL_PROVIDERS':
                gproxies += [provider['name'] for provider in providers]
            elif p == 'INSERT GAME_PROXIES':
                gproxies += first6_game_proxies
        g['proxies'] = gproxies
        # print(g['name'], g['proxies'])
        # print('--------------------')

    for c in [configure, configure_cfw]:
        c['proxies'] = all_proxies
        c['proxy-groups'] = proxy_groups + providers + proxy_groups_fixed
        c['rules'] = additional_rules + provider_rules

    if 'output-server' in updater_conf:
        save_config_yaml(configure, updater_conf['output-server'])
    if 'output-cfw' in updater_conf:
        save_config_yaml(configure_cfw, updater_conf['output-cfw'])

