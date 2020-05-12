import sys
import json
import argparse
from functools import reduce

def main():
    response = []
    parser = argparse.ArgumentParser(description='Process inputs')
    parser.add_argument('--capacity', required=True, type=check_capacity,
                        help='No of units are required (Will always be multiple of 10)')
    parser.add_argument('--hour', required=True, type=int,
                        help='No of hours the machine is required to run')
    args = parser.parse_args()
    # print(args.capacity)
    with open('data.json', 'r') as dbf:
        data = json.load(dbf)
    regions = ['India', 'New York', 'China']
    for region in regions:
        resources = list(filter(lambda x: x['region'] == region, data))
        min_ratio_source_type = min_cost_finder(resources)
        total_cost, machines = calculating_price(min_ratio_source_type, resources, region, args.capacity)
        dict = {}
        dict['region'] = region
        dict['total_cost'] = total_cost * args.hour
        dict['machines'] = machines
        response.append(dict)
    print(response)

    
def check_capacity(value: any):
    value = int(value)
    if value <= 0 or value%10 != 0:
        raise argparse.ArgumentTypeError(f"{value} always be multiple of 10")
    return value


def min_cost_finder(resources: list):
    ref = map(lambda x: get_list_of_min_max_ratios(x), resources)
    ratios = reduce(lambda x, y: min_ratio_dict_reduce_func(x, y), ref, {})
    min_ratio_source_type = min(ratios, key=ratios.get)
    return min_ratio_source_type


def calculating_price(min_ratio_source_type, resources, region, capacity):
    total_cost = None
    machines = []
    source = list(filter(lambda x: x['region'] == region and x['type'] == min_ratio_source_type, resources))[0]
    mod = calculate_mod(source, capacity)
    total_cost = source['cost'] * mod[0]
    machines.append((min_ratio_source_type, mod[0]))
    if (mod[1]):
        min_unit_resources = list(filter(lambda x: x['region'] == region and x['unit'] <= mod[1], resources))
        min_ratio_source_type = min_cost_finder(min_unit_resources)
        new_cost, new_machines = calculating_price(min_ratio_source_type, min_unit_resources, region, mod[1])
        total_cost = total_cost + new_cost
        machines = machines + new_machines
    return total_cost, machines
        

def calculate_mod(source, capacity):
    mod = []
    if source['unit'] < capacity:
        mod = [int(capacity / source['unit']), (capacity % source['unit'])]
    else:
        # here is bug we need to fix, to handle the cases where capacity is lesser than source units
        pass
    return mod


def min_ratio_dict_reduce_func(x: dict, y):
    temp = {}
    temp[y[0]] = y[1]
    x.update(temp)
    return x


def get_list_of_min_max_ratios(x):
    y = []
    y.append(x['type'])
    y.append(x['cost'] / x['unit'])
    return y


if __name__ == '__main__':
    main()