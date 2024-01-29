import fnmatch
import os


def check_file_exists_with_name_pattern(dir_path, file_name_pattern):
    is_exists = False
    for file in os.listdir(dir_path):
        if fnmatch.fnmatch(file, file_name_pattern):
            is_exists = True
    return is_exists


patter_list = ['cn', 'sf', 'fas', 'fcsam', 'fal', 'fcbsr', 'scsr', 'fsr', 'ucsr', 'gd', 'ff', 'df', 'sar', 'sanm',
               'sna', 'sn', 'sac', 'sca', 'spd', 'spa', 'uanm', 'spp', 'cln', 'srsr', 'gao', 'ana', 'fno', 'fanm',
               'fna', 'far', 'fcd', 'fbri', 'upl']

for patter in patter_list:
    print(patter + "-" + str(check_file_exists_with_name_pattern("./perf_data", patter + "_*.csv")))
