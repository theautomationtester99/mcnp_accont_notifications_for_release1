import base64
import errno
import os
import random
import shutil
from datetime import datetime
import pyfiglet
from rich import print as p
import numpy as np
from api_clases import AColors
import jwt
import fnmatch


def get_output_log_file(file_start):
    if not os.path.exists(".\\logs\\"):
        os.makedirs(".\\logs\\")
    now = datetime.now()
    date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
    file_name = str(file_start) + "_" + str(date_time) + ".txt"
    file = open(".\\logs\\" + file_name, 'a')

    return file


def get_base64_encoded_string(input_str, out_file):
    input_str_bytes = input_str.encode("ascii")
    base64_bytes = base64.b64encode(input_str_bytes)
    base64_string = base64_bytes.decode("ascii")
    # print(f"Encoded string: {base64_string}")
    # print(f"Encoded string: {base64_string}", file=out_file)
    return base64_string


def get_random_number_between(start, end):
    return random.randrange(start, end)


def gen_rand(start1, end1, num1):
    res = []

    for j in range(num1):
        res.append(np.random.randint(start1, end1))

    return res


def gen_rand1(start1, end1):
    res = (np.random.randint(start1, end1))
    return res


def gen_rand_list(total, howmany):
    res = random.sample(range(total), howmany)
    return res


def decode_bearer_token(token_str):
    decoded_data = jwt.decode(token_str, options={"verify_signature": False})
    return decoded_data


def check_file_exists_with_name_pattern(dir_path, file_name_pattern):
    is_exists = False
    for file in os.listdir(dir_path):
        if fnmatch.fnmatch(file, file_name_pattern):
            is_exists = True
    return is_exists


def get_file_size_mb(file_path):
    file_stats = os.stat(file_path)
    return round(file_stats.st_size / (1024 * 1024), 2)


def get_logged_in_user_name():
    return os.getlogin()


def get_datetime_string():
    now = datetime.now()
    date_time = now.strftime("%d%b%Y_%I%M%S%f")
    # print("date and time:", date_time)
    return date_time


def get_date_string():
    now = datetime.now()
    date_time = now.strftime("%d%b%Y")
    # print("date and time:", date_time)
    return date_time


def generate_random_notif_id():
    logged_user_name = get_logged_in_user_name()
    date_time_string = get_datetime_string()
    date_string = get_date_string()
    user_name_length = len(logged_user_name)
    if user_name_length >= 10:
        logged_user_name = logged_user_name[:9]
        random_id = logged_user_name + "_" + date_string[:5] + date_time_string[-5:]
    else:
        random_id = logged_user_name + "_" + date_string[:5] + date_time_string[-(14 - user_name_length):]
    return random_id


def silent_remove_file(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def delete_contents_of_folder(folder_name):
    for filename in os.listdir(folder_name):
        file_path = os.path.join(folder_name, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def is_directory_empty(directory_path):
    dir = os.listdir(directory_path)

    # Checking if the list is empty or not
    if len(dir) == 0:
        return True
    else:
        return False


'''Start Code to Custom Print in Colors'''


def pr_red(skk): print("\033[91m {}\033[00m".format(skk))


def pr_red_white_background(skk): print("\33[0;107m\033[91m {}\033[00m".format(skk))


def pr_red_underline(skk): print("\033[4;31m {}\033[00m".format(skk))


def pr_red_underline_white_background(skk): print("\33[0;107m\033[4;31m {}\033[00m".format(skk))


def pr_white(skk): print("\033[37m {}\033[00m".format(skk))


def pr_white_underline(skk): print("\033[4;37m {}\033[00m".format(skk))


def pr_white_underline_blue_background(skk): print("\033[0;104m\033[4;37m {}\033[00m".format(skk))


def pr_green(skk): print("\033[92m {}\033[00m".format(skk))


def pr_green_white_background(skk): print("\33[0;107m\033[92m {}\033[00m".format(skk))


def pr_green_underline(skk): print("\033[4;32m {}\033[00m".format(skk))


def pr_green_underline_white_background(skk): print("\33[0;107m\033[4;32m {}\033[00m".format(skk))


def pr_blue(skk): print("\033[1;34m {}\033[00m".format(skk))


def pr_blue_white_background(skk): print("\33[0;107m\033[1;34m {}\033[00m".format(skk))


def pr_blue_underline(skk): print("\033[4;34m {}\033[00m".format(skk))


def pr_blue_underline_white_background(skk): print("\33[0;107m\033[4;34m {}\033[00m".format(skk))


def pr_yellow(skk): print("\033[93m {}\033[00m".format(skk))


def pr_yellow_white_background(skk): print("\33[0;107m\033[93m {}\033[00m".format(skk))


def pr_yellow_underline(skk): print("\033[4;33m {}\033[00m".format(skk))


def pr_yellow_underline_white_background(skk): print("\33[0;107m\033[4;33m {}\033[00m".format(skk))


def pr_light_purple(skk): print("\033[94m {}\033[00m".format(skk))


def pr_light_purple_white_background(skk): print("\33[0;107m\033[94m {}\033[00m".format(skk))


def pr_purple_underline(skk): print("\033[4;35m {}\033[00m".format(skk))


def pr_purple_underline_white_background(skk): print("\33[0;107m\033[4;35m {}\033[00m".format(skk))


def pr_purple(skk): print("\033[95m {}\033[00m".format(skk))


def pr_cyan(skk): print("\033[96m {}\033[00m".format(skk))


def pr_cyan_white_background(skk): print("\33[0;107m\033[96m {}\033[00m".format(skk))


def pr_cyan_underline(skk): print("\033[4;36m {}\033[00m".format(skk))


def pr_cyan_underline_white_background(skk): print("\33[0;107m\033[4;36m {}\033[00m".format(skk))


def pr_light_gray(skk): print("\033[97m {}\033[00m".format(skk))


def custom_print(txt, color_txt="random", out_file=None, is_fig_font=False, process_id="1"):
    # print(txt, file=out_file)
    # print(txt)
    os.system('color')
    if not is_fig_font:
        if color_txt.lower() == 'green':
            pr_green(txt)
        elif color_txt.lower() == 'cyan':
            pr_cyan(txt)
        elif color_txt.lower() == 'yellow':
            pr_yellow(txt)
        elif color_txt.lower() == 'red':
            pr_red(txt)
        elif color_txt.lower() == 'random':
            if process_id.lower()[-1] == 'a':
                print((AColors.BLUE.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'b':
                print((AColors.BLUE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'c':
                print((AColors.RED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'd':
                print((AColors.GREEN.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'e':
                print((AColors.YELLOW.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'f':
                print((AColors.CYAN.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'g':
                print((AColors.BROWN.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'h':
                print((AColors.PURPLE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'i': print(
                (AColors.RED.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'j': print(
                (AColors.GREEN.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'k': print(
                (AColors.YELLOW.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'l': print(
                (AColors.CYAN.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'm': print(
                (AColors.BROWN.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'n': print(
                (AColors.PURPLE.value + AColors.UNDERLINE.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'o': print(
                (AColors.RED.value + AColors.CROSSED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'p': print(
                (AColors.GREEN.value + AColors.CROSSED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'q': print(
                (AColors.YELLOW.value + AColors.CROSSED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'r': print(
                (AColors.CYAN.value + AColors.CROSSED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 's': print(
                (AColors.BROWN.value + AColors.CROSSED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 't': print(
                (AColors.PURPLE.value + AColors.CROSSED.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'u': print(
                (AColors.RED.value + AColors.ITALIC.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'v': print(
                (AColors.GREEN.value + AColors.ITALIC.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'w': print(
                (AColors.YELLOW.value + AColors.ITALIC.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'x': print(
                (AColors.CYAN.value + AColors.ITALIC.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'y': print(
                (AColors.BROWN.value + AColors.ITALIC.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == 'z': print(
                (AColors.PURPLE.value + AColors.ITALIC.value + "{}" + AColors.END.value).format(txt))
            if process_id.lower()[-1] == '1': print(
                (
                        AColors.LIGHT_WHITE.value + AColors.ITALIC.value + AColors.NEGATIVE.value + "{}" + AColors.END.value).format(
                    txt))

        if out_file is not None:
            print(txt, file=out_file)

    else:
        title = pyfiglet.figlet_format(txt, font='digital')
        # print(f'[blue]{title}[/blue]')
        if out_file is not None:
            print(title, file=out_file)
        p(f'[bold blue]{title}[/bold blue]')


'''End Code to Custom Print in Colors'''
