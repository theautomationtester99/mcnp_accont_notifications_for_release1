import json
import os
import random
import string
import time
from multiprocessing import Process, freeze_support, Lock

import numpy as np
import pandas as pd
import requests
from faker import Faker
from jproperties import Properties

from api_clases import EntityMap, \
    CompanySignatureJsonBlock, CompanySignatureHtmlJsonData, CompanySignatureJson, FetchGuidanceFilesData, \
    FetchGuidanceFilesService, DeleteGuidanceDocumentData, DeleteGuidanceDocumentService, \
    FetchConsigneeSubAccountMappingDetailsData, FetchConsigneeSubAccountMappingDetailsService, FetchAccountListData, \
    FetchAccountListService, FetchConsigneesByServiceRequestData, FetchConsigneesByServiceRequestService, \
    SaveContactServiceRequestData, SaveContactServiceRequestService, SaveContactServiceRequestAccount, \
    FetchServiceRequestData, FetchServiceRequestService, UpdateContactServiceRequestData, \
    UpdateContactServiceRequestService, SaveReopenServiceRequestData, SaveReopenServiceRequestService, \
    FetchActionSetData, FetchActionSetService, FetchNotificationData, FetchNotificationService, \
    FetchAccountNotificationMappingData, FetchAccountNotificationMappingService, FetchConsigneeDetailsData, \
    FetchConsigneeDetailsService, FetchActionsRequiredData, FetchActionsRequiredService, FetchNotificationAssigneesData, \
    FetchNotificationAssigneesService, FetchBrfRecallInformationData, FetchBrfRecallInformationService, SPData, \
    get_product_images_subject_products_files_list, SubjectProductsInputToCreateNotification, \
    get_subject_products_input_file
from api_clases import Welcome5, AccMapData, CloseNotifPayload, \
    PredefinedDatum, \
    CustomAction, \
    DataEntry, Welcome10, NotifSubmitData, UCNList, BrfData, \
    NotificationAssignee, AssigneeData, Welcome4, DataCloseNotif, Welcome8, Welcome2, \
    SaveConsigneeActionsPayload, get_brf_files_list, ReturnProduct, SaveFaqData, \
    SaveFaqService, list_random_file_names, get_brf_one_file, GenerateAssigneeOtpData, \
    GenerateAssigneeOtpService, AcknowledgeNotificationAssigneeData, AcknowledgeNotificationAssigneeService, \
    SaveInquiriesRequestData, SaveInquiriesRequestService, SaveAssignedConsigneeData, SaveAssignedConsigneeService, \
    SavePrfDataData, SavePrfDataDataService, SavePrfAttachmentsData, PrfReturnProduct, SavePrfProductsData, \
    SavePrfProductsService, UpdateAccountNotificationMappingData, UpdateAccountNotificationMappingService
from db_functions import delete_data_notification_images_material_sbj, get_notification_type_from_db, \
    update_notification_issue_date, get_accounts_per_notif_id, get_assignees_per_notif_id, get_consignees_per_account, \
    get_compname_per_notif_id, get_attachment_per_notif_id, \
    get_shipping_label_per_notif_id, get_db_id_per_assignee_notification, \
    get_otp_per_assignee_notification, update_notification_closed_date, update_notification_issue_date_account, \
    update_notification_issue_date_assignees, update_notification_closed_date_account, \
    update_notification_closed_date_assignees, get_rand_dbid_ref_datas_table, get_rand_notif_id_notifications_table, \
    get_rand_mapped_ucn_nbr, get_notif_name_per_notif_id, get_admin_notif_id_per_notif_id, get_account_name_per_ucn_id
from utils import gen_rand1, gen_rand_list, get_output_log_file, delete_contents_of_folder, get_random_number_between

configs = Properties()
with open('input.properties', 'rb') as config_file:
    configs.load(config_file)

number_threads = int(configs.get("number_threads").data)
time_to_run_minutes = int(configs.get("time_to_run_minutes").data)
create_complete = str(configs.get("create_complete").data)
only_delete = str(configs.get("only_delete").data)
use_bearer_token = str(configs.get("use_bearer_token").data)
max_number_of_subject_products_to_load = int(configs.get("max_number_of_subject_products_to_load").data)
min_number_of_subject_products_to_load = int(configs.get("min_number_of_subject_products_to_load").data)
number_of_product_images_to_load = int(configs.get("number_of_product_images_to_load").data)
number_of_supporting_tools_to_load = int(configs.get("number_of_supporting_tools_to_load").data)
number_of_guidance_documents_to_load = int(configs.get("number_of_guidance_documents_to_load").data)
fetch_signe_mapped_sub_accounts_fp = int(configs.get("fetch_signe_mapped_sub_accounts_fp").data)
fetch_signe_mapped_sub_accounts_lp = int(configs.get("fetch_signe_mapped_sub_accounts_lp").data)
fetch_signe_mapped_sub_accounts_nb = int(configs.get("fetch_signe_mapped_sub_accounts_nb").data)
choose_accounts_with_consignees = str(configs.get("choose_accounts_with_consignees").data)
only_hcp_pa = configs.get("only_hcp_pa").data
only_mw_cu_co_re = configs.get("only_mw_cu_co_re").data
total_number_notification_to_create = int(configs.get("total_number_notification_to_create").data)
number_notif_ackn_inprogress = int(configs.get("number_notif_ackn_inprogress").data)
number_notif_all_completed = int(configs.get("number_notif_all_completed").data)
number_notif_few_complete_reopen_request = int(configs.get("number_notif_few_complete_reopen_request").data)
number_notif_all_complete_reopen_request = int(configs.get("number_notif_all_complete_reopen_request").data)
number_notif_new_without_sup_tools = int(configs.get("number_notif_new_without_sup_tools").data)
number_notif_new = int(configs.get("number_notif_new").data)
number_notif_new_pa_cu = int(configs.get("number_notif_new_pa_cu").data)
number_notif_new_aging = int(configs.get("number_notif_new_aging").data)
number_notif_draft = int(configs.get("number_notif_draft").data)
number_notif_new_closed = int(configs.get("number_notif_new_closed").data)
number_notif_few_completed_closed = int(configs.get("number_notif_few_completed_closed").data)
number_notif_all_completed_closed = int(configs.get("number_notif_all_completed_closed").data)
number_notif_new_closed_gt_5y_back = int(configs.get("number_notif_new_closed_gt_5y_back").data)
number_notif_few_completed_closed_gt_5y_back = int(configs.get("number_notif_few_completed_closed_gt_5y_back").data)
number_notif_all_completed_closed_gt_5y_back = int(configs.get("number_notif_all_completed_closed_gt_5y_back").data)
whichdb = str(configs.get("whichdb").data)
delete_existing_data = str(configs.get("delete_existing_data").data)
cn_email_id = str(configs.get("cn_email_id").data)
cn_email_id1 = str(configs.get("cn_email_id1").data)
cn_email_id2 = str(configs.get("cn_email_id2").data)
cn_email_id3 = str(configs.get("cn_email_id3").data)
cn_email_id4 = str(configs.get("cn_email_id4").data)
number_of_assignees = int(configs.get("number_of_assignees").data)
# if console_output: print(whichdb)
which_location = str(configs.get("whichlocation").data)
load_faqs = str(configs.get("load_faqs").data)
load_other_inquiries = str(configs.get("load_other_inquiries").data)
load_deactivate_contact_requests = str(configs.get("load_deactivate_contact_requests").data)
load_new_contact_requests = str(configs.get("load_new_contact_requests").data)
load_guidance_documents = str(configs.get("load_guidance_documents").data)
faker_locale = configs.get("faker_locale").data
bearer_token = use_bearer_token
pid_number_chars = 5000
whats_choice = ["Yes", "Yes"]
whats_boolean_choice = [True, True]
url_local = 'http://10.53.42.229:4200/api/apiGateway'
url_remote = 'https://dev.mecp.jnj.com/api/apiGateway'
url_remote_qa = 'https://qa.mecp.jnj.com/api/apiGateway'
url_remote_stage = 'https://uat.mecp.jnj.com/api/apiGateway'
datalist = []
console_output_info = False
console_output_info_msg = True
console_output_response = True

fake = Faker()


def set_faker(out_file):
    if faker_locale == 'random':
        locale_list = ['bg_BG', 'hr_HR', 'cs_CS', 'da_DK', 'nl_NL', 'en_GB', 'et_EE', 'fi_FI', 'fr_FR', 'de_DE',
                       'el_GR',
                       'hu_HU', 'ga_GA', 'it_IT', 'lv_LV', 'lt_LT', 'mt_MT', 'pl_PL', 'pt_PT', 'ro_RO', 'sk_SK',
                       'sk_SK',
                       'es_ES', 'sv_SE']
        print("Original list is : " + str(locale_list))
        print("Original list is : " + str(locale_list), file=out_file)
        random_locale = random.choices(locale_list, k=1)
        print("Random locale is :", random_locale)
        print("Random locale is :", random_locale, file=out_file)
        return Faker(random_locale)
    else:
        return Faker([faker_locale])


def gen_random_string(nbr_chars):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=nbr_chars))
    return res


def get_url():
    url = ''
    if whichdb == 'mysql':
        url = url_local
    elif whichdb == 'mssql' and which_location == 'remote':
        url = url_remote
    elif whichdb == 'mssql' and which_location == 'remoteqa':
        url = url_remote_qa
    elif whichdb == 'mssql' and which_location == 'remotestage':
        url = url_remote_stage
    elif whichdb == 'mssql' and which_location == 'local':
        url = url_local

    return url


def notif_type_id_from_type(notif_type):
    note_type_id = ''
    if notif_type.lower() == 'removal':
        note_type_id = '5'
    elif notif_type.lower() == 'market withdrawal':
        note_type_id = '6'
    elif notif_type.lower() == 'correction':
        note_type_id = '7'
    elif notif_type.lower() == 'patient notification':
        note_type_id = '8'
    elif notif_type.lower() == 'hcp notification':
        note_type_id = '11'
    elif notif_type.lower() == 'customer notification':
        note_type_id = '12'

    return note_type_id


def convert_to_hr_min_sec_str(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def generate_fake_email(number):
    email_list = []
    unique_list = []
    i = 0
    while i < number:
        email_list.append(fake.email())
        list_set = set(email_list)
        unique_list = (list(list_set))
        i = len(unique_list)

    return unique_list


def notif_p1(n_type, without_support_tools, process_txt, process_lock, out_file):
    df = pd.read_excel(r'subjectprodcuts.xlsx',
                       dtype={"Distribution Start Date": "string", "Distribution End Date": "string",
                              "Expiration Date": "string"})
    df.fillna('')
    df1 = df.replace(np.nan, '', regex=True)
    nbr_subject_products_count = get_random_number_between(min_number_of_subject_products_to_load,
                                                           max_number_of_subject_products_to_load)
    df1 = df1.sample(n=nbr_subject_products_count)
    print("Loading " + str(nbr_subject_products_count) + " Subject Products")
    # if console_output: print(df1["Distribution Start Date"])
    datalist.clear()
    for index, row in df1.iterrows():
        # if console_output: print(row["Distribution Start Date"], row["Description"], index)
        sp_desc = row["Description"].replace("\n", "<br>")
        # data = Datum(row["Product Code"], row["Product Name"], row["Product Lot / Serial"], row["UDI"],
        #              sp_desc,
        #              row["Expiration Date"], row["Distribution Start Date"],
        #              row["Distribution End Date"], True)
        data = SPData(row["Product Code"], row["Product Name"], row["Product Lot / Serial"], row["UDI"],
                      sp_desc,
                      row["Expiration Date"], row["Distribution Start Date"],
                      row["Distribution End Date"], True)
        datalist.append(data)
        # if index >= number_of_subject_products_to_load - 1:
        #     break

    # if console_output: print(datalist)
    nb_nb_note = 20 - (len(process_txt) + 11)
    fake_note_id_part = gen_random_string(nb_nb_note)
    if without_support_tools == 'yes':
        # note_id = process_txt + str(fake.ean(length=nb_nb_note)) + "_nosptls"
        note_id = process_txt + str(fake_note_id_part) + "_nosptls"
    else:
        # note_id = process_txt + str(fake.ean(length=nb_nb_note))
        note_id = process_txt + str(fake_note_id_part)
    issue_date = str(fake.date_between('-2y', '-1y'))
    # if console_output: print(issue_date)

    company_names = (
        "Acclarent", "Biosense Webster", "Cerenovus", "DePuy Synthes", "Ethicon", "J&J Vision", "Mentor",
        "SterilMed",
        "Abiomed")
    rand_acc = gen_rand1(0, len(company_names))

    if only_hcp_pa.lower() == 'yes' and n_type != 5:
        n_type = 2
    if only_mw_cu_co_re.lower() == 'yes' and n_type != 5:
        n_type = 1

    if n_type == 1:
        note_type = ("Removal", "Market Withdrawal", "Correction", "Customer Notification")
    elif n_type == 2:
        note_type = ("Patient Notification", "HCP Notification")
    else:
        note_type = ("Removal", "Market Withdrawal", "Correction", "Customer Notification", "Patient Notification",
                     "HCP Notification")

    rand_type = gen_rand1(0, len(note_type))
    note_id = note_id + "_" + note_type[rand_type][:2]

    # from db
    # note_type_id = get_notification_type_id_from_db(note_type[rand_type])

    note_type_id = notif_type_id_from_type(note_type[rand_type])

    company_sign_plain = note_type[
                             rand_type] + fake.company_suffix() + "\n" + "Subsidary of JnJ\n" + "Phone: " + fake.phone_number() + "\n" + "Address: " + fake.address()

    company_sign_html = "<p>" + company_sign_plain.replace("\n", "</p>\n<p>") + "</p>"

    company_sign_lines = company_sign_plain.split("\n")
    company_sign_lines_length = len(company_sign_lines)

    entmap = EntityMap()
    cs_json_block_list = []

    for i in range(company_sign_lines_length):
        jsonblock = CompanySignatureJsonBlock(str(i), company_sign_lines[i], "unstyled", 0, [], [], entmap)
        cs_json_block_list.append(jsonblock)

    csjson = CompanySignatureJson(cs_json_block_list, entmap)
    company_sign_html_json = CompanySignatureHtmlJsonData(company_sign_html, json.dumps(csjson))

    # spd = SubjectProductsData([], datalist, True)
    spd_input_file_json = SubjectProductsInputToCreateNotification([], datalist, True)
    # delete_contents_of_folder(".\subjectproducts")
    # if is_directory_empty(".\subjectproducts"):
    with open(".\subjectproducts\sample.txt", "w") as outfile:
        outfile.write(json.dumps(spd_input_file_json))
        outfile.close()
    npl = random.randint(1, int(number_of_product_images_to_load))
    prod_desc = fake.text(max_nb_chars=pid_number_chars).replace(". ", ".<br>").replace(".\n", ".<br>")
    po_impact = fake.text(max_nb_chars=pid_number_chars).replace(". ", ".<br>").replace(".\n", ".<br>")
    well = Welcome5(fake.text(max_nb_chars=100), note_id, note_type_id, fake.text(max_nb_chars=100),
                    company_names[rand_acc],
                    prod_desc, po_impact, [], [],
                    "supportMaterial", random.randint(0, int(npl) - 1), False,
                    json.dumps(company_sign_html_json), company_sign_plain,
                    note_type_id,
                    "4", issue_date, "Vinay Babu", "VBabuGut@its.jnj.com", True)

    # if console_output: print(json.dumps(well))
    dta = json.dumps(well)
    url = get_url()
    # print(url)

    headers_cn_p1 = {"Accept": "application/json", "Authorization": bearer_token}
    # headers_cn_p1 = {"Accept": "application/json", "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImZlZGxvZ2luIiwieDV0IjoiSTBYeFNERXp2NXhrNVFmSVNoMFplQkFOdjZzIiwicGkuYXRtIjoiejNsaCJ9.eyJzY29wZSI6ImFkZHJlc3MgcGhvbmUgb3BlbmlkIHByb2ZpbGUgZW1haWwiLCJjbGllbnRfaWQiOiJtZWR0ZWNoX2N1c3RvbWVyX2RldiIsImlzcyI6Imh0dHBzOi8vZmVkbG9naW4uam5qLmNvbSIsImpuak1TVXNlcm5hbWUiOiJWQmFidUd1dCIsImF1ZCI6Im1lZHRlY2hfY3VzdG9tZXJfZGV2IiwiY24iOiI3MDI0MjgxNDEiLCJnaXZlbl9uYW1lIjoiVmluYXkiLCJmYW1pbHlfbmFtZSI6IkJhYnUgR3V0dGEiLCJlbWFpbCI6IlZCYWJ1R3V0QElUUy5KTkouY29tIiwiZXhwIjoxNjg4OTg1NjY3fQ.lHjzKC1WZwcDTOS-v_NAbFyGaudPVS2tVDbA3rSObjjqZkgDudm_PEL5QZgk7CtL7wqJ5mWI3jZQ2v4mP94KfYduHCr4LlKUXZgSIyutFHxDsoKp3ffJ8jIvZaNa0IfErFvwbUzKK4tWej2xO6v7jukeiBgAQra3blQYe61URtOJ-pEZyBG5QfQ5wVl4Ihv-EvUzsJ9BVciFd8fJwg9gxXh1YSwcqaQcFKk5DA9a4cTB2rBSS7v_Vvz3_U8GCbgxmR9OyAJ5ZR6aTGhJjRP4RyAFPof2Om2XrCXI9zdY1heb5lSvU73LlhTlCkv5Z4awcio6K4qyXCRcaLeEJ2dViw"}
    # headers_cn_p1 = {"Accept": "application/json"}
    form_data = {'service': 'notification', 'apiname': 'createNotification', 'auditProductImagesRequired': True,
                 'data': dta}

    # if console_output: print(get_notification_files_list(without_support_tools))
    # if console_output: print(files)

    # print("before response")

    response = requests.post(url, headers=headers_cn_p1, data=form_data,
                             files=get_product_images_subject_products_files_list(npl, out_file, process_lock))

    # print("after response")

    if console_output_response:
        print(response.status_code)
        print(response.status_code, file=out_file)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)
    # if console_output_response: print(response.request.headers)
    # if console_output: print(response.json())
    notification_db_id = int(response.json()["data"])

    # if console_output: print(response.json())
    if console_output_info_msg: print('Create Notification')
    # if console_output_response: print(response.content.decode())

    print([notification_db_id, note_type[rand_type], note_id])

    return [notification_db_id, note_type[rand_type]]


def notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file):
    url = get_url()

    headers_cn_p1 = {"Accept": "application/json", "Authorization": bearer_token}

    sub_tools_form_data = {'service': 'attachments', 'attachmentType': 'supportMaterial', 'apiname': 'saveFiles',
                           'notificationId': notification_db_id}

    if without_support_tools == "no":
        nst = random.randint(1, int(number_of_supporting_tools_to_load))
        files_list_random = list_random_file_names(".\material", int(nst), out_file)
        for filename in files_list_random:
            response_sup_tools = requests.post(url, headers=headers_cn_p1, data=sub_tools_form_data,
                                               files=get_brf_one_file(without_support_tools, filename, process_lock))

            if console_output_info_msg:
                print('Upload support tools to Notification: ' + filename)
                print('Upload support tools to Notification: ' + filename, file=out_file)
            if console_output_response:
                print(response_sup_tools.content.decode())
                print(response_sup_tools.content.decode(), file=out_file)
            # if console_output: print(response_sup_tools.json())


def fetch_action_set_ids_per_notif_type(notif_type, out_file):
    url = get_url()

    notif_type_id = 0

    if notif_type.lower() == 'removal':
        notif_type_id = 5
    elif notif_type.lower() == 'market withdrawal':
        notif_type_id = 6
    elif notif_type.lower() == 'correction':
        notif_type_id = 7
    elif notif_type.lower() == 'patient notification':
        notif_type_id = 8
    elif notif_type.lower() == 'hcp notification':
        notif_type_id = 11
    elif notif_type.lower() == 'customer notification':
        notif_type_id = 12

    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fasd = FetchActionSetData(notif_type_id)
    fasds = FetchActionSetService("actionsRequired", "fetchActionSet", fasd)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fasds))
        print(json.dumps(fasds), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fasds))

    if console_output_info_msg: print("Fetched the actions list")
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info: print(gd_json)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def fetch_all_mapped_accounts_list_json(out_file, filter_consignee):
    url = get_url()

    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    if filter_consignee == "":
        num1 = random.randint(int(fetch_signe_mapped_sub_accounts_fp), int(fetch_signe_mapped_sub_accounts_lp))
        nb_size = int(fetch_signe_mapped_sub_accounts_nb)
    else:
        num1 = 1
        nb_size = 100

    fc = FetchConsigneeSubAccountMappingDetailsData(filter_consignee, num1, nb_size, None, None)
    fcs = FetchConsigneeSubAccountMappingDetailsService("account", "fetchConsigneeSubAccountMappingDetails", fc)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fcs))
        print(json.dumps(fcs), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fcs))

    if console_output_info_msg: print("Fetched the consignee list")
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info:
        print(type(gd_json))

    return str(gd_json)


def fetch_all_mapped_consignee_list(out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fc = FetchConsigneeSubAccountMappingDetailsData("", 1, 10, None, None)
    fcs = FetchConsigneeSubAccountMappingDetailsService("account", "fetchConsigneeSubAccountMappingDetails", fc)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fcs))
        print(json.dumps(fcs), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fcs))

    if console_output_info_msg:
        print("Fetched the consignee list")
        print("Fetched the consignee list", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info:
        print(type(gd_json))

    return str(gd_json)


def fetch_accounts_per_consig_email(consig_email, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fal = FetchAccountListData(consig_email)
    fals = FetchAccountListService("account", "fetchAccountList", 1, 10, "", True, fal)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fals))
        print(json.dumps(fals), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fals))

    if console_output_info_msg: print("Fetched the account list")
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info:
        print(type(gd_json))

    return str(gd_json)


def fetch_team_consignees_per_consig_email(consig_email, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fco = FetchConsigneesByServiceRequestData("", consig_email)
    fcos = FetchConsigneesByServiceRequestService("account", "fetchConsigneesByServiceRequest", fco)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fcos))
        print(json.dumps(fcos), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fcos))

    if console_output_info_msg: print("Fetched the consignee list")
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info:
        print(type(gd_json))

    return str(gd_json)


def raise_contact_service_request(request_type, status, consignee_name, consig_email, accounts, creator_first_name,
                                  creator_last_name, created_by, comments, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    if accounts:
        account_list = []
        for x in accounts:
            a = SaveContactServiceRequestAccount(x['subAccountUCN'], x['accountName'])
            account_list.append(a)
        crs = SaveContactServiceRequestData(request_type, status, consignee_name, consig_email, account_list,
                                            creator_first_name, creator_last_name, created_by, comments)
        crss = SaveContactServiceRequestService("serviceRequest", "saveContactServiceRequest", crs)

        if console_output_info:
            print(url)
            print(url, file=out_file)
        if console_output_info:
            print(json.dumps(crss))
            print(json.dumps(crss), file=out_file)

        response = requests.post(url, headers=headers_fg, data=json.dumps(crss))

        if console_output_info_msg:
            print("Raised contact service request")
            print("Raised contact service request", file=out_file)
        # gd_json = response.json()
        gd_json = str(response.content.decode())
        if console_output_info:
            print(gd_json)
            print(gd_json, file=out_file)
    else:
        crs = SaveContactServiceRequestData(request_type, status, consignee_name, consig_email, accounts,
                                            creator_first_name, creator_last_name, created_by, comments)
        crss = SaveContactServiceRequestService("serviceRequest", "saveContactServiceRequest", crs)

        if console_output_info:
            print(url)
            print(url, file=out_file)
        if console_output_info:
            print(json.dumps(crss))
            print(json.dumps(crss), file=out_file)

        response = requests.post(url, headers=headers_fg, data=json.dumps(crss))

        if console_output_info_msg:
            print("Raised contact service request")
            print("Raised contact service request", file=out_file)
        # gd_json = response.json()
        gd_json = str(response.content.decode())
        if console_output_info:
            print(gd_json)
            print(gd_json, file=out_file)


def fetch_service_requests(req_type, req_status, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fsr = FetchServiceRequestData(req_type, req_status, "", 100, 1)
    fsrs = FetchServiceRequestService("serviceRequest", "fetchServiceRequest", fsr)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fsrs))
        print(json.dumps(fsrs), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fsrs))

    if console_output_info_msg:
        print("Fetched the consignee list")
        print("Fetched the consignee list", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def approve_deny_contact_service_request(service_request_number, req_status, denial_reason, request_type,
                                         consignee_name, consignee_email,
                                         creator_first_name, creator_last_name, creator_email, accounts, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    ucs = UpdateContactServiceRequestData(service_request_number, req_status, denial_reason, "Vinay", "Babu gutta",
                                          "vbabugut@its.jnj.com", request_type, consignee_name, consignee_email,
                                          creator_first_name, creator_last_name, creator_email, accounts)
    ucss = UpdateContactServiceRequestService("serviceRequest", "updateContactServiceRequest", ucs)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(ucss))
        print(json.dumps(ucss), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(ucss))

    if console_output_info_msg:
        print("Updated service request")
        print("Updated service request", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def upload_guidance_document(process_lock, out_file):
    url = get_url()

    headers_guide_doc = {"Accept": "application/json", "Authorization": bearer_token}

    guide_doc_form_data = {'service': 'attachments', 'attachmentType': 'guidanceDocument', 'apiname': 'saveFiles'}

    nst = random.randint(1, int(number_of_guidance_documents_to_load))
    files_list_random = list_random_file_names(".\material", int(nst), out_file)
    for filename in files_list_random:
        response_guide_doc = requests.post(url, headers=headers_guide_doc, data=guide_doc_form_data,
                                           files=get_brf_one_file("no", filename, process_lock))

        if console_output_info_msg:
            print('Upload guidance document: ' + filename)
            print('Upload guidance document: ' + filename, file=out_file)
        if console_output_response:
            print(response_guide_doc.json())
            print(response_guide_doc.json(), file=out_file)


def fetch_guidance_documents(out_file):
    url = get_url()

    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fgd = FetchGuidanceFilesData(None, "guidanceDocument")
    fgds = FetchGuidanceFilesService("attachments", "fetchFiles", fgd)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fgds))
        print(json.dumps(fgds), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fgds))

    if console_output_info_msg:
        print("Fetched the guidance document list")
        print("Fetched the guidance document list", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def delete_guidance_document(file_name, out_file):
    url = get_url()

    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    dgd = DeleteGuidanceDocumentData(file_name, None, "guidanceDocument")
    dgds = DeleteGuidanceDocumentService("attachments", "deleteFiles", dgd)

    response = requests.post(url, headers=headers_fg, data=json.dumps(dgds))

    if console_output_info_msg:
        print("Deleted the guidance document " + file_name)
        print("Deleted the guidance document " + file_name, file=out_file)

    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def notif_actions(notification_db_id, notification_type, out_file):
    url = get_url()

    '''
                saveActionsRequired
                '''
    # get id from previous response
    # get notification type from id
    # get 2 predefined action ids based on notification type
    # give one custom action details
    # invoke the api
    add_attachments = random.choice(whats_boolean_choice)
    add_ship_labels = random.choice(whats_boolean_choice)

    # from db

    # notification_type_id = get_notification_type_id_from_db(notification_type)

    # not from db
    notification_type_id = notif_type_id_from_type(notification_type)

    if notification_type in ["Correction", "Customer Notification"]:
        add_ship_labels = False

    pre_defined_data_list = []
    custom_actions_list = []

    # directly from db
    # all_predef_action_ids = get_all_predefined_action_id_from_db(notification_type)

    # using microservice

    fetch_action_ids_json = fetch_action_set_ids_per_notif_type(notification_type, out_file)
    fetch_action_ids_data = json.loads(fetch_action_ids_json)

    all_predef_action_ids = [dat["id"] for dat in fetch_action_ids_data["data"]]

    # if console_output: print(all_predef_action_ids)

    index = 1

    for x in all_predef_action_ids:
        predif_data = PredefinedDatum(notification_db_id, x, index)
        pre_defined_data_list.append(predif_data)
        index = index + 1

    for x in all_predef_action_ids:
        custom_action_text = fake.paragraph(nb_sentences=1)
        cust_data = CustomAction(notification_db_id, custom_action_text, index)
        custom_actions_list.append(cust_data)
        index = index + 1

    # for j in range(1, 3):
    #     if j == 1:
    #         predif_acid = int(get_rand_predefined_action_id_from_db(notification_type))
    #         predif_data = PredefinedDatum(notification_db_id, predif_acid, 1)
    #         pre_defined_data_list.append(predif_data)
    #     else:
    #         custom_action_text = fake.paragraph(nb_sentences=1)
    #         cust_data = CustomAction(notification_db_id, custom_action_text, 2)
    #         custom_actions_list.append(cust_data)
    brf_data = BrfData(notification_db_id, int(notification_type_id), add_attachments, add_ship_labels)

    actions_data = DataEntry(brf_data, pre_defined_data_list, custom_actions_list)

    actions_service = Welcome10("actionsRequired", "saveActionsRequired", actions_data)

    a_headers = {"Content-Type": "application/json", "Accept": "application/json",
                 "Authorization": bearer_token}
    # if console_output: print(json.dumps(actions_service))
    response = requests.post(url, headers=a_headers, data=json.dumps(actions_service))
    # if console_output: print(json.dumps(actions_service))
    if console_output_info_msg:
        print('Assign actions')
        print('Assign actions', file=out_file)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def notif_assign_accounts(notification_db_id, out_file, consig_filter):
    url = get_url()
    accounts_list_submit = []

    all_consig_filter = consig_filter.split()

    '''
                Assign to accounts
                '''

    # insert_notifications_actions_list_table(note_id, note_type[rand_type], 2)

    ##########################################
    # notification account mapping - to all accounts
    ###########################################
    # directly from db
    # all_accounts = get_consignee_assigned_sub_accounts()
    # all_notification_ids = get_all_notification_ids()

    total_list = []

    for ci in all_consig_filter:
        # using microservices
        accounts_json = fetch_all_mapped_accounts_list_json(out_file, ci)
        accounts_json_data = json.loads(accounts_json)
        # Get all the values for the "hobbies" key

        account_ucns = [([subucn["subAccountUCN"] for subucn in dat["subAccount"]]) for dat in
                        accounts_json_data["data"]]
        for i in account_ucns:
            total_list.extend(i)

    all_accounts = [*set(total_list)]
    if console_output_info:
        print(all_accounts)
        print(all_accounts, file=out_file)

    random_no_acc = gen_rand1(1, len(all_accounts))

    accounts_list = []

    list_num_accounts = gen_rand_list(len(all_accounts), random_no_acc)
    # if console_output: print(list_num_accounts)

    for i in list_num_accounts:
        accounts_list.append(UCNList(all_accounts[i]))
        accounts_list_submit.append(all_accounts[i])

    # for i in range(random_no_acc):
    #     rand_no = gen_rand1(0, len(all_accounts)-1)
    #     accounts_list.append(UCNList(all_accounts[rand_no][0]))
    #     accounts_list_submit.append(all_accounts[rand_no][0])

    # for x in all_accounts:
    #     accounts_list.append(UCNList(x[0]))
    #     accounts_list_submit.append(x[0])

    acmapdata = AccMapData(notification_db_id, [], False, accounts_list)
    wel2 = Welcome2("notification", "saveAccountNotificationMapping", acmapdata)

    s_headers = {"Content-Type": "application/json", "Accept": "application/json",
                 "Authorization": bearer_token}
    # if console_output: print(json.dumps(wel2))
    response = requests.post(url, headers=s_headers, data=json.dumps(wel2))
    # if console_output: print(json.dumps(wel2))
    if console_output_info_msg:
        print('Assign Accounts ' + str(random_no_acc))
        print('Assign Accounts ' + str(random_no_acc), file=out_file)
    # if console_output: print(accounts_list)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)

    return accounts_list_submit


def notif_assign_assignees(notification_db_id, out_file):
    url = get_url()

    '''
                saveNotificationAssignees
                '''
    number_assignees = random.randint(1, int(number_of_assignees))
    email_lst = generate_fake_email(number_assignees)

    if console_output_info_msg:
        print("number of assignees: " + str(number_assignees))
        print("number of assignees: " + str(number_assignees), file=out_file)

    notification_asins = []
    for i in range(len(email_lst) - 1):
        notif_asgne = NotificationAssignee(fake.first_name(), fake.last_name(), email_lst[i])
        notification_asins.append(notif_asgne)

    notif_asgne = NotificationAssignee("fake_first_name", 'fake_last_name', cn_email_id)
    notification_asins.append(notif_asgne)
    notif_asgne1 = NotificationAssignee(fake.first_name(), fake.last_name(), cn_email_id1)
    notification_asins.append(notif_asgne1)
    notif_asgne2 = NotificationAssignee(fake.first_name(), fake.last_name(), cn_email_id2)
    notification_asins.append(notif_asgne2)
    notif_asgne3 = NotificationAssignee(fake.first_name(), fake.last_name(), cn_email_id3)
    notification_asins.append(notif_asgne3)
    notif_asgne4 = NotificationAssignee(fake.first_name(), fake.last_name(), cn_email_id4)
    notification_asins.append(notif_asgne4)

    data = AssigneeData(notification_db_id, [], notification_asins)
    wel4 = Welcome4("notification", "saveNotificationAssignees", data)

    s_headers = {"Content-Type": "application/json", "Accept": "application/json",
                 "Authorization": bearer_token}
    # if console_output: print(json.dumps(wel2))
    response = requests.post(url, headers=s_headers, data=json.dumps(wel4))
    # if console_output: print(json.dumps(wel2))
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)
    if console_output_info_msg:
        print("Assign Assignees")
        print("Assign Assignees", file=out_file)


def notif_submit(notification_db_id, accounts_list_submit, out_file):
    url = get_url()
    '''
            Submit Notification
            '''
    issue_date = str(fake.date_between('-2y', '-1y'))

    if console_output_info:
        print(accounts_list_submit)
        print(accounts_list_submit, file=out_file)

    notif_sub_data = NotifSubmitData(notification_db_id, 9, accounts_list_submit)
    notif_sub_service = Welcome8("notification", "submitNotification", notif_sub_data)

    ns_headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}
    # if console_output: print(json.dumps(notif_sub_service))
    response = requests.post(url, headers=ns_headers, data=json.dumps(notif_sub_service))
    # if console_output: print(json.dumps(notif_sub_service))
    if console_output_info_msg:
        print('Sumitted')
        print('Sumitted', file=out_file)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)
    error_flag = response.json()["errorPopupFlag"]
    if error_flag:
        file_data = response.json()["downloadData"]["bufferData"]["data"]
        some_bytes = bytearray(file_data)
        immutable_bytes = bytes(some_bytes)

        directory = os.path.join(".", "notif_consig_check")
        os.makedirs(directory, exist_ok=True)

        # Write bytes to file
        with open("./notif_consig_check/" + str(notification_db_id) + " notificationAccountErrorReport.xlsx",
                  "wb") as binary_file:
            binary_file.write(immutable_bytes)


def notif_assign_consignee(assig_consig_data, account, out_file):
    url = get_url()
    assign_service = SaveAssignedConsigneeService("notification", "saveAssignedConsignee", assig_consig_data)
    ns_headers = {"Content-Type": "application/json", "Accept": "application/json",
                  "Authorization": bearer_token}

    response = requests.post(url, headers=ns_headers, data=json.dumps(assign_service))

    if console_output_info_msg:
        print('Moved to In progress for one account ' + account)
        print('Moved to In progress for one account ' + account, file=out_file)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def notif_save_consignee_actions(consig_actions_lst, account, out_file):
    url = get_url()
    save_consig_action_service = SaveConsigneeActionsPayload("actionsRequired", "saveConsigneeActions",
                                                             consig_actions_lst)
    # if console_output: print(consig_actions_lst)
    ns_headers = {"Content-Type": "application/json", "Accept": "application/json",
                  "Authorization": bearer_token}

    # if console_output: print(json.dumps(save_consig_action_service))

    response = requests.post(url, headers=ns_headers, data=json.dumps(save_consig_action_service))

    if console_output_info_msg:
        print('Saving Consignee Actions ' + account)
        print('Saving Consignee Actions ' + account, file=out_file)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag, return_product_lst,
                     account,
                     account_unique, account_name, consig_email, consig_name,
                     company_in_notif, adminnotif_id, notif_name, process_lock, out_file):
    url = get_url()
    saveprf_headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}
    saveprf_attach_headers = {"Accept": "application/json", "Authorization": bearer_token}

    mapped_notif_account_unique_json = fetch_accounts_per_notif(int(notification_db_id), out_file)
    mapped_notif_accounts_unique_data = json.loads(mapped_notif_account_unique_json)

    accounts_unique_and_db_id_in_notif = [[dat["id"], dat["uniqueMappingId"]] for dat in
                                          mapped_notif_accounts_unique_data["data"]]

    unique_db_id = -1

    for au_db in accounts_unique_and_db_id_in_notif:
        if au_db[1].lower() == account_unique.lower():
            unique_db_id = int(au_db[0])

    if not return_product_lst:
        # From DB
        # unique_db_id = get_db_id_per_unique_map_id(account_unique)

        save_prf_data = SavePrfDataData(account_unique, False, notification_db_id, unique_db_id, account)

        save_prf_data_service = SavePrfDataDataService("brf", "savePrfData", save_prf_data)
        # if console_output: print(json.dumps(save_prf_data_service))

        response = requests.post(url, headers=saveprf_headers, data=json.dumps(save_prf_data_service))

        if console_output_response:
            print(response.content.decode())
            print(response.content.decode(), file=out_file)
        if console_output_info_msg:
            print("PRF data saved")
            print("PRF data saved", file=out_file)

        if brf_attach_flag == 1:
            do_you_attach = random.choice(whats_choice)
            if do_you_attach.lower() == 'yes':
                # prf_recall_db_id = get_prf_recall_db_id_per_unique_account_map_id(account_unique)
                brf_recall_json = fetch_brf_recall_db_id(int(notification_db_id), account_unique, out_file)
                brf_recall_data = json.loads(brf_recall_json)

                prf_recall_db_id = int(brf_recall_data["data"]["id"])

                prf_attachments_data = SavePrfAttachmentsData(prf_recall_db_id, account_unique, False,
                                                              notification_db_id, unique_db_id, account, [])
                # if console_output: print(json.dumps(prf_attachments_data))

                prf_attach_form_data = {'service': 'brf', 'apiname': 'savePrfAttachments',
                                        'data': json.dumps(prf_attachments_data)}

                response = requests.post(url, headers=saveprf_attach_headers, data=prf_attach_form_data,
                                         files=get_brf_files_list('no', out_file, process_lock))

                if console_output_info_msg:
                    print('Submit PRF Attachments ' + account_unique)
                    print('Submit PRF Attachments ' + account_unique, file=out_file)
                if console_output_response:
                    print(response.content.decode())
                    print(response.content.decode(), file=out_file)

        update_account_notification_mapping_data = UpdateAccountNotificationMappingData(notification_db_id, account,
                                                                                        adminnotif_id, notif_name,
                                                                                        notification_type, consig_name,
                                                                                        consig_email, account_name,
                                                                                        company_in_notif)
        update_account_notification_mapping_service = UpdateAccountNotificationMappingService("notification",
                                                                                              "updateAccountNotificationMapping",
                                                                                              update_account_notification_mapping_data)
        response = requests.post(url, headers=saveprf_headers,
                                 data=json.dumps(update_account_notification_mapping_service))

        if console_output_response:
            print(response.content.decode())
            print(response.content.decode(), file=out_file)
        if console_output_info_msg:
            print("PRF Completed")
            print("PRF Completed", file=out_file)

    else:
        # unique_db_id = get_db_id_per_unique_map_id(account_unique)

        save_prf_data = SavePrfDataData(account_unique, True, notification_db_id, unique_db_id, account)

        save_prf_data_service = SavePrfDataDataService("brf", "savePrfData", save_prf_data)

        response = requests.post(url, headers=saveprf_headers, data=json.dumps(save_prf_data_service))

        if console_output_response:
            print(response.content.decode())
            print(response.content.decode(), file=out_file)
        if console_output_info_msg:
            print("PRF data saved")
            print("PRF data saved", file=out_file)

        brf_recall_json = fetch_brf_recall_db_id(int(notification_db_id), account_unique, out_file)
        brf_recall_data = json.loads(brf_recall_json)

        prf_recall_db_id = int(brf_recall_data["data"]["id"])

        # prf_recall_db_id = get_prf_recall_db_id_per_unique_account_map_id(account_unique)

        if brf_attach_flag == 1:
            do_you_attach = random.choice(whats_choice)
            if do_you_attach.lower() == 'yes':
                prf_attachments_data = SavePrfAttachmentsData(prf_recall_db_id, account_unique, True,
                                                              notification_db_id, unique_db_id, account, [])

                # if console_output: print(json.dumps(prf_attachments_data))

                prf_attach_form_data = {'service': 'brf', 'apiname': 'savePrfAttachments',
                                        'data': json.dumps(prf_attachments_data)}

                response = requests.post(url, headers=saveprf_attach_headers, data=prf_attach_form_data,
                                         files=get_brf_files_list('no', out_file, process_lock))

                if console_output_info_msg:
                    print('Submit PRF Attachments ' + account)
                    print('Submit PRF Attachments ' + account, file=out_file)
                if console_output_response:
                    print(response.content.decode())
                    print(response.content.decode(), file=out_file)
        if brf_ship_label_flag == 1:
            do_you_ship_label = random.choice(whats_choice)
            if do_you_ship_label.lower() == 'yes':
                no_ship_labels = random.randint(1, 10)
                prf_products_data = SavePrfProductsData(prf_recall_db_id, notification_db_id, no_ship_labels, [],
                                                        account_unique, unique_db_id, account, return_product_lst)
                save_prf_product_service = SavePrfProductsService("brf", "savePrfProducts", prf_products_data)

                response = requests.post(url, headers=saveprf_headers, data=json.dumps(save_prf_product_service))
                if console_output_response:
                    print(response.content.decode())
                    print(response.content.decode(), file=out_file)
                if console_output_info_msg:
                    print("Saved PRF products with shipping labels " + str(no_ship_labels))
                    print("Saved PRF products with shipping labels " + str(no_ship_labels), file=out_file)
            else:
                prf_products_data = SavePrfProductsData(prf_recall_db_id, notification_db_id, 0, [],
                                                        account_unique, unique_db_id, account, return_product_lst)
                save_prf_product_service = SavePrfProductsService("brf", "savePrfProducts", prf_products_data)

                response = requests.post(url, headers=saveprf_headers, data=json.dumps(save_prf_product_service))
                if console_output_response:
                    print(response.content.decode())
                    print(response.content.decode(), file=out_file)
                if console_output_info_msg:
                    print("Saved PRF products with shipping labels 0")
                    print("Saved PRF products with shipping labels 0", file=out_file)
        else:
            prf_products_data = SavePrfProductsData(prf_recall_db_id, notification_db_id, 0, [],
                                                    account_unique, unique_db_id, account, return_product_lst)
            save_prf_product_service = SavePrfProductsService("brf", "savePrfProducts", prf_products_data)

            response = requests.post(url, headers=saveprf_headers, data=json.dumps(save_prf_product_service))
            if console_output_response:
                print(response.content.decode())
                print(response.content.decode(), file=out_file)
            if console_output_info_msg:
                print("Saved PRF products with shipping labels 0")
                print("Saved PRF products with shipping labels 0", file=out_file)

        update_account_notification_mapping_data = UpdateAccountNotificationMappingData(notification_db_id, account,
                                                                                        adminnotif_id, notif_name,
                                                                                        notification_type, consig_name,
                                                                                        consig_email, account_name,
                                                                                        company_in_notif)
        update_account_notification_mapping_service = UpdateAccountNotificationMappingService("notification",
                                                                                              "updateAccountNotificationMapping",
                                                                                              update_account_notification_mapping_data)
        response = requests.post(url, headers=saveprf_headers,
                                 data=json.dumps(update_account_notification_mapping_service))

        if console_output_response:
            print(response.content.decode())
            print(response.content.decode(), file=out_file)
        if console_output_info_msg:
            print("PRF Completed")
            print("PRF Completed", file=out_file)


def notif_close(notification_db_id, out_file):
    url = get_url()
    close_notif_data = DataCloseNotif(notification_db_id, 'Vinay Babu', 'VBabuGut@its.jnj.com')
    close_notif_service = CloseNotifPayload('notification', 'closeNotification', close_notif_data)

    cn_headers = {"Content-Type": "application/json", "Accept": "application/json",
                  "Authorization": bearer_token}
    response = requests.post(url, headers=cn_headers, data=json.dumps(close_notif_service))
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def raise_notif_reopen_request(notification_db_id, admin_notif_id, notif_name, ucn_no, account_name, comp,
                               reopen_reason, creator_ln, creator_fn, creator_email, out_file):
    url = get_url()
    reopen_notif_request_data = SaveReopenServiceRequestData(6, 3, notification_db_id, admin_notif_id, notif_name,
                                                             ucn_no, account_name, comp, reopen_reason, creator_ln,
                                                             creator_fn, creator_email)
    reopen_notif_request_service = SaveReopenServiceRequestService('serviceRequest', 'saveReopenServiceRequest',
                                                                   reopen_notif_request_data)

    cn_headers = {"Content-Type": "application/json", "Accept": "application/json",
                  "Authorization": bearer_token}
    response = requests.post(url, headers=cn_headers, data=json.dumps(reopen_notif_request_service))
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def notif_assignee_generate_otp(notification_assignee_id, out_file):
    url = get_url()
    otp_data = GenerateAssigneeOtpData(notification_assignee_id)
    otp_service = GenerateAssigneeOtpService("notification", "generateAssigneeOtp", otp_data)

    otp_headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Authorization": bearer_token}
    response = requests.post(url, headers=otp_headers, data=json.dumps(otp_service))
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


def notif_assignee_acknowledge(notification_assignee_id, assignee_email, assignee_otp, notif_id, notif_name, company,
                               out_file):
    url = get_url()
    ackn_data = AcknowledgeNotificationAssigneeData(notification_assignee_id, assignee_email, assignee_otp, notif_id,
                                                    notif_name, company)
    ackn_service = AcknowledgeNotificationAssigneeService("notification", "acknowledgeNotificationAssignee", ackn_data)

    otp_headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "Authorization": bearer_token}
    response = requests.post(url, headers=otp_headers, data=json.dumps(ackn_service))
    if console_output_response:
        print(response.json()["message"])
        print(response.json()["message"], file=out_file)


def fetch_notif_basic_info(notif_db_id, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fnd = FetchNotificationData(notif_db_id, False)
    fnds = FetchNotificationService("notification", "fetchNotification", fnd)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fnds))
        print(json.dumps(fnds), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fnds))

    if console_output_info_msg:
        print("Fetched the notification basic info")
        print("Fetched the notification basic info", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def fetch_accounts_per_notif(notif_db_id, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fanm = FetchAccountNotificationMappingData(notif_db_id)
    fanms = FetchAccountNotificationMappingService("notification", "fetchAccountNotificationMapping", fanm)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fanms))
        print(json.dumps(fanms), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fanms))

    if console_output_info_msg:
        print("Fetched the notification mapped accounts info")
        print("Fetched the notification mapped accounts info", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def fetch_assignees_per_notif(notif_db_id, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fasid = FetchNotificationAssigneesData(notif_db_id, "")
    fasids = FetchNotificationAssigneesService("notification", "fetchNotificationAssignees", fasid)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fasids))
        print(json.dumps(fasids), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fasids))

    if console_output_info_msg:
        print("Fetched the assignees of the notification info")
        print("Fetched the assignees of the notification info", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def fetch_actions_brf_settings_per_notif(notif_db_id, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fard = FetchActionsRequiredData(notif_db_id, None, None)
    fards = FetchActionsRequiredService("actionsRequired", "fetchActionsRequired", fard)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fards))
        print(json.dumps(fards), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fards))

    if console_output_info_msg:
        print("Fetched the actions and brf settings per notif")
        print("Fetched the actions and brf settings per notif", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_response:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def fetch_consignees_per_account(account_id, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fcd = FetchConsigneeDetailsData(account_id)
    fcds = FetchConsigneeDetailsService("account", "fetchConsigneeDetails", fcd)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fcds))
        print(json.dumps(fcds), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fcds))

    if console_output_info_msg:
        print("Fetched the consignees per account info")
        print("Fetched the consignees per account info", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def fetch_brf_recall_db_id(notif_db_id, unique_account_id, out_file):
    url = get_url()
    headers_fg = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}

    fbrid = FetchBrfRecallInformationData(notif_db_id, unique_account_id)
    fbrids = FetchBrfRecallInformationService("brf", "fetchBrfRecallInformation", fbrid)

    if console_output_info:
        print(url)
        print(url, file=out_file)
    if console_output_info:
        print(json.dumps(fbrids))
        print(json.dumps(fbrids), file=out_file)

    response = requests.post(url, headers=headers_fg, data=json.dumps(fbrids))

    if console_output_info_msg:
        print("Fetched the brf info")
        print("Fetched the brf info", file=out_file)
    # gd_json = response.json()
    gd_json = str(response.content.decode())
    if console_output_info:
        print(gd_json)
        print(gd_json, file=out_file)
    if console_output_info: print(type(gd_json))

    return str(gd_json)


def subject_products_file_check(n_type, without_support_tools, process_txt, process_lock, out_file):
    url = get_url()
    # print(url)

    headers_cn_p1 = {"Accept": "application/json", "Authorization": bearer_token}

    form_data = {'service': 'subjectProducts', 'apiname': 'upload'}

    # if console_output: print(get_notification_files_list(without_support_tools))
    # if console_output: print(files)

    # print("before response")

    response = requests.post(url, headers=headers_cn_p1, data=form_data,
                             files=get_subject_products_input_file(out_file, process_lock))

    # print("after response")

    if console_output_response:
        print(response.status_code)
        print(response.status_code, file=out_file)
    if console_output_response:
        print(response.content.decode())
        print(response.content.decode(), file=out_file)


'''
End of Services Call methods
'''


def delete_all_guidance_documents(out_file):
    all_gd_json = fetch_guidance_documents(out_file)
    all_gd_data = json.loads(all_gd_json)
    # Get all the values for the "hobbies" key
    all_file_names = [dat["fileName"] for dat in all_gd_data["data"]]
    if console_output_info:
        print(all_file_names)
        print(all_file_names, file=out_file)

    if all_file_names:
        for file_name in all_file_names:
            delete_guidance_document(file_name, out_file)
    else:
        if console_output_info_msg:
            print("No guidance documents on server")
            print("No guidance documents on server", file=out_file)


def load_deactivate_contact_requests_data(out_file):
    all_consig_in_system = fetch_all_mapped_consignee_list(out_file)
    all_consign_in_system_data = json.loads(all_consig_in_system)

    all_consig_in_sysem_fnlnemail = [
        (dict((k, dat[k]) for k in ['consigneeFirstName', 'consigneeLastName', 'consigneeEmail'] if k in dat)) for
        dat in all_consign_in_system_data["data"]]
    if console_output_info:
        print(all_consig_in_sysem_fnlnemail)
        print(all_consig_in_sysem_fnlnemail, file=out_file)

    if all_consig_in_sysem_fnlnemail:
        for idy, y in enumerate(all_consig_in_sysem_fnlnemail):
            if idy % 2 != 0:
                creatorfn = y['consigneeFirstName']
                creatorln = y['consigneeLastName']
                creatoremail = y['consigneeEmail']

                all_team_consig = fetch_team_consignees_per_consig_email(creatoremail, out_file)
                all_team_consig_data = json.loads(all_team_consig)

                all_team_consig_nameemail = [
                    (dict((k, dat[k]) for k in ['consigneeEmail', 'consigneeName'] if k in dat)) for
                    dat in all_team_consig_data["data"]]

                for idx, x in enumerate(all_team_consig_nameemail):
                    if idx % 2 == 0:
                        raise_contact_service_request(2, 3, x['consigneeName'], x['consigneeEmail'], [], creatorfn,
                                                      creatorln,
                                                      creatoremail,
                                                      fake.text(200).replace(". ", ".<br>").replace(".\n", ".<br>"),
                                                      out_file)

    else:
        if console_output_info_msg:
            print("No consignees in the system")
            print("No consignees in the system", file=out_file)


def load_add_new_contact_requests_data(number_to_populate, out_file):
    all_consig_in_system = fetch_all_mapped_consignee_list(out_file)
    all_consign_in_system_data = json.loads(all_consig_in_system)

    all_consig_in_sysem_fnlnemail = [
        (dict((k, dat[k]) for k in ['consigneeFirstName', 'consigneeLastName', 'consigneeEmail'] if k in dat)) for
        dat in all_consign_in_system_data["data"]]
    if console_output_info:
        print(all_consig_in_sysem_fnlnemail)
        print(all_consig_in_sysem_fnlnemail, file=out_file)

    if all_consig_in_sysem_fnlnemail:
        for idy, y in enumerate(all_consig_in_sysem_fnlnemail):
            if idy % 2 == 0:
                creatorfn = y['consigneeFirstName']
                creatorln = y['consigneeLastName']
                creatoremail = y['consigneeEmail']

                all_assigned_accounts = fetch_accounts_per_consig_email(creatoremail, out_file)
                all_assigned_accounts_data = json.loads(all_assigned_accounts)

                all_assigned_accounts_nameucn = [
                    (dict((k, dat[k]) for k in ['subAccountUCN', 'accountName'] if k in dat)) for dat in
                    all_assigned_accounts_data["data"]["accountData"]]

                for idx, x in enumerate(all_assigned_accounts_nameucn):
                    if idx % 2 == 0 and idx <= number_to_populate:
                        raise_contact_service_request(1, 3, fake.name(), fake.ascii_safe_email(), [x], creatorfn,
                                                      creatorln, creatoremail, None, out_file)

    else:
        if console_output_info_msg:
            print("No consignees in the system")
            print("No consignees in the system", file=out_file)


def approve_contact_requests_data(type_to_approve, out_file):
    contact_requests_list_json = fetch_service_requests(1, 3, out_file)
    contact_requests_list_data = json.loads(contact_requests_list_json)

    contact_requests_list_input = [(dict((k, dat[k]) for k in
                                         ['serviceRequestNumber', 'requestType', 'consigneeName', 'consigneeEmail',
                                          'creatorFirstName',
                                          'creatorLastName', 'createdBy', 'accounts'] if k in dat)) for dat in
                                   contact_requests_list_data["data"]]
    if console_output_info:
        print(contact_requests_list_input)
        print(contact_requests_list_input, file=out_file)

    if contact_requests_list_input:
        for idy, y in enumerate(contact_requests_list_input):
            if idy % 2 == 0:
                service_req = y['serviceRequestNumber']
                req_type = y['requestType']
                if type_to_approve != req_type:
                    continue
                consigname = y['consigneeName']
                consigemail = y['consigneeEmail']
                creatorfn = y['creatorFirstName']
                creatorln = y['creatorLastName']
                creatoremail = y['createdBy']
                account_obj = json.loads(y['accounts'])

                approve_deny_contact_service_request(service_req, 4, "", req_type, consigname, consigemail, creatorfn,
                                                     creatorln, creatoremail, account_obj, out_file)
    else:
        if console_output_info_msg:
            print("No requests in the system")
            print("No requests in the system", file=out_file)


def deny_contact_requests_data(type_to_approve, out_file):
    contact_requests_list_json = fetch_service_requests(1, 3, out_file)
    contact_requests_list_data = json.loads(contact_requests_list_json)

    contact_requests_list_input = [(dict((k, dat[k]) for k in
                                         ['serviceRequestNumber', 'requestType', 'consigneeName', 'consigneeEmail',
                                          'creatorFirstName',
                                          'creatorLastName', 'createdBy', 'accounts'] if k in dat)) for dat in
                                   contact_requests_list_data["data"]]
    if console_output_info:
        print(contact_requests_list_input)
        print(contact_requests_list_input, file=out_file)

    if contact_requests_list_input:
        for idy, y in enumerate(contact_requests_list_input):
            if idy % 2 == 0:
                service_req = y['serviceRequestNumber']
                req_type = y['requestType']
                if type_to_approve != req_type:
                    continue
                consigname = y['consigneeName']
                consigemail = y['consigneeEmail']
                creatorfn = y['creatorFirstName']
                creatorln = y['creatorLastName']
                creatoremail = y['createdBy']
                account_obj = []

                approve_deny_contact_service_request(service_req, 5,
                                                     fake.text(max_nb_chars=200).replace(". ", ".<br>").replace(".\n",
                                                                                                                ".<br>"),
                                                     req_type, consigname, consigemail, creatorfn,
                                                     creatorln, creatoremail, account_obj, out_file)
    else:
        if console_output_info_msg:
            print("No requests in the system")
            print("No requests in the system", file=out_file)


def load_notif_new(with_aging, without_support_tools, is_closed, process_txt, process_lock, out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(1, without_support_tools, process_txt, process_lock, out_file)

        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        # from db
        # notification_type = str(get_notification_type_from_db(notification_db_id))

        notification_type = create_notif_data[1]
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:

            notif_actions(notification_db_id, notification_type, out_file)
            accounts_list_submit = notif_assign_accounts(notification_db_id, out_file, choose_accounts_with_consignees)
        else:
            notif_assign_assignees(notification_db_id, out_file)

        notif_submit(notification_db_id, accounts_list_submit, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info_msg:
                print("Changing Issued date to " + issue_date)
                print("Changing Issued date to " + issue_date, file=out_file)
            update_notification_issue_date(notification_db_id, issue_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, issue_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, issue_date)

        if is_closed.lower() == "yes":
            notif_close(notification_db_id, out_file)
        if is_closed.lower() == "yesgt5":
            close_date = str(fake.date_between('-8y', '-6y'))
            if console_output_info_msg: print("Changing Closed date to " + close_date)
            update_notification_issue_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, close_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, close_date)
            notif_close(notification_db_id, out_file)
            update_notification_closed_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_closed_date_account(notification_db_id, close_date)
            else:
                update_notification_closed_date_assignees(notification_db_id, close_date)


def load_notif_cu_pa(with_aging, without_support_tools, is_closed, process_txt, process_lock, out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(2, without_support_tools, process_txt, process_lock, out_file)
        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        # from db
        # notification_type = str(get_notification_type_from_db(notification_db_id))

        notification_type = create_notif_data[1]
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:

            notif_actions(notification_db_id, notification_type, out_file)

            accounts_list_submit = notif_assign_accounts(notification_db_id, out_file, choose_accounts_with_consignees)
        else:
            notif_assign_assignees(notification_db_id, out_file)

        notif_submit(notification_db_id, accounts_list_submit, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info_msg: print("Changing Issued date to " + issue_date)
            update_notification_issue_date(notification_db_id, issue_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, issue_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, issue_date)

        if is_closed.lower() == "yes":
            notif_close(notification_db_id, out_file)
        if is_closed.lower() == "yesgt5":
            close_date = str(fake.date_between('-8y', '-6y'))
            if console_output_info: print(close_date)
            update_notification_issue_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, close_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, close_date)
            notif_close(notification_db_id, out_file)
            update_notification_closed_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_closed_date_account(notification_db_id, close_date)
            else:
                update_notification_closed_date_assignees(notification_db_id, close_date)


def load_notif_new_inprogress_completed(with_aging, without_support_tools, is_closed, process_txt, process_lock,
                                        out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(3, without_support_tools, process_txt, process_lock, out_file)
        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        # from db
        # notification_type = str(get_notification_type_from_db(notification_db_id))

        notification_type = create_notif_data[1]
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
            if console_output_info_msg: print("--------------------------------------------")
            if console_output_info_msg: print(notification_type)
            if console_output_info_msg: print("--------------------------------------------")

            notif_actions(notification_db_id, notification_type, out_file)

            accounts_list_submit = notif_assign_accounts(notification_db_id, out_file, choose_accounts_with_consignees)
        else:
            notif_assign_assignees(notification_db_id, out_file)

        notif_submit(notification_db_id, accounts_list_submit, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info_msg: print("Changing Issued date to " + issue_date)
            update_notification_issue_date(notification_db_id, issue_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, issue_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, issue_date)

        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:

            # from db
            # company_in_notif = get_compname_per_notif_id(notification_db_id)
            # adminnotif_id = get_admin_notif_id_per_notif_id(notification_db_id)
            # notif_name = get_notif_name_per_notif_id(notification_db_id)
            # accounts_in_notif = get_accounts_per_notif_id(notification_db_id)

            # from microservices
            basic_notif_json = fetch_notif_basic_info(int(notification_db_id), out_file)
            basic_notif_data = json.loads(basic_notif_json)

            company_in_notif = basic_notif_data["data"]["company"]
            adminnotif_id = basic_notif_data["data"]["adminNotificationId"]
            notif_name = basic_notif_data["data"]["name"]

            mapped_notif_accounts_json = fetch_accounts_per_notif(int(notification_db_id), out_file)
            mapped_notif_accounts_data = json.loads(mapped_notif_accounts_json)

            accounts_in_notif = [dat["subAccountUCN"] for dat in mapped_notif_accounts_data["data"]]

            if len(accounts_in_notif) <= 5 and len(accounts_in_notif) == 2:
                # first_account = accounts_in_notif[0][0]
                first_account = accounts_in_notif[0]
                first_account_unique = str(notification_db_id) + "-" + first_account
                # from db
                # consignees_first_account = get_consignees_per_account(first_account)
                # from microservice

                mapped_consig_first_account_json = fetch_consignees_per_account(first_account, out_file)
                mapped_consig_first_account_data = json.loads(mapped_consig_first_account_json)

                consignees_first_account = [
                    [dat["accountName"], dat["consigneeFirstName"], dat["consigneeLastName"], dat["consigneeEmail"]] for
                    dat in mapped_consig_first_account_data["data"]]

                # from db
                # first_account_name = get_account_name_per_ucn_id(first_account)

                first_account_name = consignees_first_account[0][0]
                # first_consig_id_first_account = str(consignees_first_account[0][0])
                first_consig_name_first_account = str(
                    consignees_first_account[0][1] + " " + consignees_first_account[0][2])
                first_consig_email_first_account = str(consignees_first_account[0][3])

                first_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, first_account,
                                                                    first_consig_email_first_account,
                                                                    first_consig_name_first_account, False,
                                                                    company_in_notif, adminnotif_id, notif_name,
                                                                    notification_type, first_account_name)

                notif_assign_consignee(first_assig_consig_data, first_account, out_file)

                # second_account = accounts_in_notif[1][0]
                second_account = accounts_in_notif[1]
                second_account_unique = str(notification_db_id) + "-" + second_account
                # consignees_second_account = get_consignees_per_account(second_account)

                mapped_consig_second_account_json = fetch_consignees_per_account(second_account, out_file)
                mapped_consig_second_account_data = json.loads(mapped_consig_second_account_json)

                consignees_second_account = [
                    [dat["accountName"], dat["consigneeFirstName"], dat["consigneeLastName"], dat["consigneeEmail"]] for
                    dat in mapped_consig_second_account_data["data"]]

                # second_account_name = get_account_name_per_ucn_id(second_account)
                second_account_name = consignees_second_account[0][0]
                # first_consig_id_second_account = str(consignees_second_account[0][0])
                first_consig_name_second_account = str(
                    consignees_second_account[0][1] + " " + consignees_second_account[0][2])
                first_consig_email_second_account = str(consignees_second_account[0][3])

                second_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, second_account,
                                                                     first_consig_email_second_account,
                                                                     first_consig_name_second_account, False,
                                                                     company_in_notif, adminnotif_id, notif_name,
                                                                     notification_type, second_account_name)

                notif_assign_consignee(second_assig_consig_data, second_account, out_file)

                # notif_action_ids = get_action_ids_per_notif_id(notification_db_id)
                # consig_actions_lst = []
                #
                # for id in notif_action_ids:
                #     consig_action = ConsigneeActions(second_account_unique, notification_db_id, id[0], True)
                #     consig_actions_lst.append(consig_action)
                #
                # notif_save_consignee_actions(consig_actions_lst, second_account)

                # from db
                # brf_attach_flag = get_attachment_per_notif_id(notification_db_id)
                # brf_ship_label_flag = get_shipping_label_per_notif_id(notification_db_id)

                actions_settings_per_notif_json = fetch_actions_brf_settings_per_notif(int(notification_db_id),
                                                                                       out_file)
                actions_settings_per_notif_data = json.loads(actions_settings_per_notif_json)

                brf_attach_flag = int(actions_settings_per_notif_data["data"]["brfData"]["attachmentFlag"])
                brf_ship_label_flag = int(actions_settings_per_notif_data["data"]["brfData"]["shippingLabelFlag"])

                return_product_lst = []
                for dl in datalist:
                    return_product = PrfReturnProduct(dl['productCode'], dl['serialNumber'], random.randint(1, 999))
                    return_product_lst.append(return_product)

                if notification_type in ["Correction", "Customer Notification"]:
                    notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag, [],
                                     second_account, second_account_unique, second_account_name,
                                     first_consig_email_second_account,
                                     first_consig_name_second_account, company_in_notif, adminnotif_id, notif_name,
                                     process_lock, out_file)

                if notification_type in ["Removal", "Market Withdrawal"]:
                    do_you_return_products = random.choice(whats_choice)
                    if do_you_return_products.lower() == "no":
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag,
                                         [],
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id, notif_name,
                                         process_lock, out_file)
                    else:
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag,
                                         return_product_lst,
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id, notif_name,
                                         process_lock, out_file)
            else:
                for i in range(int(len(accounts_in_notif)) // 2):
                    print("Account " + str(i) + " out of " + str(len(accounts_in_notif) // 2))
                    if i % 2 == 0:
                        first_account = accounts_in_notif[i]
                        first_account_unique = str(notification_db_id) + "-" + first_account
                        # consignees_first_account = get_consignees_per_account(first_account)

                        mapped_consig_first_account_json = fetch_consignees_per_account(first_account, out_file)
                        mapped_consig_first_account_data = json.loads(mapped_consig_first_account_json)

                        consignees_first_account = [
                            [dat["accountName"], dat["consigneeFirstName"], dat["consigneeLastName"],
                             dat["consigneeEmail"]] for
                            dat in mapped_consig_first_account_data["data"]]

                        # first_account_name = get_account_name_per_ucn_id(first_account)
                        first_account_name = consignees_first_account[0][0]
                        # first_consig_id_first_account = str(consignees_first_account[0][0])
                        first_consig_name_first_account = str(
                            consignees_first_account[0][1] + " " + consignees_first_account[0][2])
                        first_consig_email_first_account = str(consignees_first_account[0][3])

                        first_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, first_account,
                                                                            first_consig_email_first_account,
                                                                            first_consig_name_first_account, False,
                                                                            company_in_notif, adminnotif_id, notif_name,
                                                                            notification_type, first_account_name)

                        notif_assign_consignee(first_assig_consig_data, first_account, out_file)
                    else:
                        # second_account = accounts_in_notif[i][0]
                        second_account = accounts_in_notif[i]
                        second_account_unique = str(notification_db_id) + "-" + second_account

                        # consignees_second_account = get_consignees_per_account(second_account)

                        mapped_consig_second_account_json = fetch_consignees_per_account(second_account, out_file)
                        mapped_consig_second_account_data = json.loads(mapped_consig_second_account_json)

                        consignees_second_account = [
                            [dat["accountName"], dat["consigneeFirstName"], dat["consigneeLastName"],
                             dat["consigneeEmail"]] for
                            dat in mapped_consig_second_account_data["data"]]

                        # second_account_name = get_account_name_per_ucn_id(second_account)
                        second_account_name = consignees_second_account[0][0]
                        # first_consig_id_second_account = str(consignees_second_account[0][0])
                        first_consig_name_second_account = str(
                            consignees_second_account[0][1] + " " + consignees_second_account[0][2])
                        first_consig_email_second_account = str(consignees_second_account[0][3])

                        second_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, second_account,
                                                                             first_consig_email_second_account,
                                                                             first_consig_name_second_account, False,
                                                                             company_in_notif, adminnotif_id,
                                                                             notif_name,
                                                                             notification_type, second_account_name)

                        notif_assign_consignee(second_assig_consig_data, second_account, out_file)

                        # notif_action_ids = get_action_ids_per_notif_id(notification_db_id)
                        # consig_actions_lst = []
                        #
                        # for id in notif_action_ids:
                        #     consig_action = ConsigneeActions(second_account_unique, notification_db_id, id[0], True)
                        #     consig_actions_lst.append(consig_action)
                        #
                        # notif_save_consignee_actions(consig_actions_lst, second_account)

                        # brf_attach_flag = get_attachment_per_notif_id(notification_db_id)
                        # brf_ship_label_flag = get_shipping_label_per_notif_id(notification_db_id)

                        actions_settings_per_notif_json = fetch_actions_brf_settings_per_notif(int(notification_db_id),
                                                                                               out_file)
                        actions_settings_per_notif_data = json.loads(actions_settings_per_notif_json)

                        # print(actions_settings_per_notif_data)

                        brf_attach_flag = int(actions_settings_per_notif_data["data"]["brfData"]["attachmentFlag"])
                        brf_ship_label_flag = int(
                            actions_settings_per_notif_data["data"]["brfData"]["shippingLabelFlag"])

                        return_product_lst = []
                        for dl in datalist:
                            return_product = ReturnProduct(dl['productCode'], dl['serialNumber'],
                                                           random.randint(1, 1000))
                            return_product_lst.append(return_product)

                        if notification_type in ["Correction", "Customer Notification"]:
                            notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                             brf_ship_label_flag, [],
                                             second_account, second_account_unique, second_account_name,
                                             first_consig_email_second_account,
                                             first_consig_name_second_account, company_in_notif, adminnotif_id,
                                             notif_name,
                                             process_lock, out_file)

                        if notification_type in ["Removal", "Market Withdrawal"]:
                            do_you_return_products = random.choice(whats_choice)
                            if do_you_return_products.lower() == "no":
                                notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                                 brf_ship_label_flag,
                                                 [],
                                                 second_account, second_account_unique, second_account_name,
                                                 first_consig_email_second_account,
                                                 first_consig_name_second_account, company_in_notif, adminnotif_id,
                                                 notif_name,
                                                 process_lock, out_file)
                            else:
                                notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                                 brf_ship_label_flag,
                                                 return_product_lst,
                                                 second_account, second_account_unique, second_account_name,
                                                 first_consig_email_second_account,
                                                 first_consig_name_second_account, company_in_notif, adminnotif_id,
                                                 notif_name,
                                                 process_lock, out_file)

        else:
            # from db
            assignee_in_notif = get_assignees_per_notif_id(notification_db_id)
            ackn_list = random.sample(assignee_in_notif, len(assignee_in_notif) // 2)

            company_in_notif = get_compname_per_notif_id(notification_db_id)
            adminnotif_id = get_admin_notif_id_per_notif_id(notification_db_id)
            notif_name = get_notif_name_per_notif_id(notification_db_id)

            for i in range(int(len(ackn_list))):
                print("Assignee " + str(i) + " out of " + str(len(ackn_list)))
                db_id = get_db_id_per_assignee_notification(notification_db_id, ackn_list[i])
                notif_assignee_generate_otp(db_id, out_file)
                otp_from_db = get_otp_per_assignee_notification(notification_db_id, ackn_list[i])
                notif_assignee_acknowledge(db_id, ackn_list[i], otp_from_db, adminnotif_id, notif_name,
                                           company_in_notif, out_file)

            # for assign_to_ackn in ackn_list:
            #     db_id = get_db_id_per_assignee_notification(notification_db_id, assign_to_ackn)
            #     notif_assignee_generate_otp(db_id)
            #     otp_from_db = get_otp_per_assignee_notification(notification_db_id, assign_to_ackn)
            #     notif_assignee_acknowledge(db_id, assign_to_ackn, otp_from_db, adminnotif_id, notif_name,
            #                                company_in_notif)

        if is_closed.lower() == 'yes':
            notif_close(notification_db_id, out_file)
        if is_closed.lower() == "yesgt5":
            close_date = str(fake.date_between('-8y', '-6y'))
            if console_output_info: print(close_date)
            update_notification_issue_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, close_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, close_date)
            notif_close(notification_db_id, out_file)
            update_notification_closed_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_closed_date_account(notification_db_id, close_date)
            else:
                update_notification_closed_date_assignees(notification_db_id, close_date)


def load_notif_all_completed(with_aging, without_support_tools, is_closed, process_txt, process_lock, out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(3, without_support_tools, process_txt, process_lock, out_file)
        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        # from db
        # notification_type = str(get_notification_type_from_db(notification_db_id))

        notification_type = create_notif_data[1]
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
            if console_output_info_msg: print("--------------------------------------------")
            if console_output_info_msg: print(notification_type)
            if console_output_info_msg: print("--------------------------------------------")

            notif_actions(notification_db_id, notification_type, out_file)

            accounts_list_submit = notif_assign_accounts(notification_db_id, out_file, choose_accounts_with_consignees)
        else:
            notif_assign_assignees(notification_db_id, out_file)

        notif_submit(notification_db_id, accounts_list_submit, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info_msg: print("Changing Issued date to " + issue_date)
            update_notification_issue_date(notification_db_id, issue_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, issue_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, issue_date)

        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:

            # from db
            # company_in_notif = get_compname_per_notif_id(notification_db_id)
            # adminnotif_id = get_admin_notif_id_per_notif_id(notification_db_id)
            # notif_name = get_notif_name_per_notif_id(notification_db_id)
            # accounts_in_notif = get_accounts_per_notif_id(notification_db_id)

            # from microservices
            basic_notif_json = fetch_notif_basic_info(int(notification_db_id), out_file)
            basic_notif_data = json.loads(basic_notif_json)

            company_in_notif = basic_notif_data["data"]["company"]
            adminnotif_id = basic_notif_data["data"]["adminNotificationId"]
            notif_name = basic_notif_data["data"]["name"]

            mapped_notif_accounts_json = fetch_accounts_per_notif(int(notification_db_id), out_file)
            mapped_notif_accounts_data = json.loads(mapped_notif_accounts_json)

            accounts_in_notif = [dat["subAccountUCN"] for dat in mapped_notif_accounts_data["data"]]

            for i in range(int(len(accounts_in_notif))):
                print("Account " + str(i) + " out of " + str(len(accounts_in_notif)))
                if i % 2 == 0:
                    first_account = accounts_in_notif[i]
                    first_account_unique = str(notification_db_id) + "-" + first_account
                    # consignees_first_account = get_consignees_per_account(first_account)

                    mapped_consig_first_account_json = fetch_consignees_per_account(first_account, out_file)
                    mapped_consig_first_account_data = json.loads(mapped_consig_first_account_json)

                    consignees_first_account = [
                        [dat["accountName"], dat["consigneeFirstName"], dat["consigneeLastName"],
                         dat["consigneeEmail"]] for
                        dat in mapped_consig_first_account_data["data"]]

                    # first_account_name = get_account_name_per_ucn_id(first_account)
                    first_account_name = consignees_first_account[0][0]
                    # first_consig_id_first_account = str(consignees_first_account[0][0])
                    first_consig_name_first_account = str(
                        consignees_first_account[0][1] + " " + consignees_first_account[0][2])
                    first_consig_email_first_account = str(consignees_first_account[0][3])

                    first_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, first_account,
                                                                        first_consig_email_first_account,
                                                                        first_consig_name_first_account, False,
                                                                        company_in_notif, adminnotif_id, notif_name,
                                                                        notification_type, first_account_name)

                    notif_assign_consignee(first_assig_consig_data, first_account, out_file)
                else:
                    # second_account = accounts_in_notif[i][0]
                    second_account = accounts_in_notif[i]
                    second_account_unique = str(notification_db_id) + "-" + second_account

                    # consignees_second_account = get_consignees_per_account(second_account)

                    mapped_consig_second_account_json = fetch_consignees_per_account(second_account, out_file)
                    mapped_consig_second_account_data = json.loads(mapped_consig_second_account_json)

                    consignees_second_account = [
                        [dat["accountName"], dat["consigneeFirstName"], dat["consigneeLastName"],
                         dat["consigneeEmail"]] for
                        dat in mapped_consig_second_account_data["data"]]

                    # second_account_name = get_account_name_per_ucn_id(second_account)
                    second_account_name = consignees_second_account[0][0]
                    # first_consig_id_second_account = str(consignees_second_account[0][0])
                    first_consig_name_second_account = str(
                        consignees_second_account[0][1] + " " + consignees_second_account[0][2])
                    first_consig_email_second_account = str(consignees_second_account[0][3])

                    second_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, second_account,
                                                                         first_consig_email_second_account,
                                                                         first_consig_name_second_account, False,
                                                                         company_in_notif, adminnotif_id,
                                                                         notif_name,
                                                                         notification_type, second_account_name)

                    notif_assign_consignee(second_assig_consig_data, second_account, out_file)

                    # notif_action_ids = get_action_ids_per_notif_id(notification_db_id)
                    # consig_actions_lst = []
                    #
                    # for id in notif_action_ids:
                    #     consig_action = ConsigneeActions(second_account_unique, notification_db_id, id[0], True)
                    #     consig_actions_lst.append(consig_action)
                    #
                    # notif_save_consignee_actions(consig_actions_lst, second_account)

                    # brf_attach_flag = get_attachment_per_notif_id(notification_db_id)
                    # brf_ship_label_flag = get_shipping_label_per_notif_id(notification_db_id)

                    actions_settings_per_notif_json = fetch_actions_brf_settings_per_notif(int(notification_db_id),
                                                                                           out_file)
                    actions_settings_per_notif_data = json.loads(actions_settings_per_notif_json)

                    # print(actions_settings_per_notif_data)

                    brf_attach_flag = int(actions_settings_per_notif_data["data"]["brfData"]["attachmentFlag"])
                    brf_ship_label_flag = int(
                        actions_settings_per_notif_data["data"]["brfData"]["shippingLabelFlag"])

                    return_product_lst = []
                    for dl in datalist:
                        return_product = ReturnProduct(dl['productCode'], dl['serialNumber'],
                                                       random.randint(1, 1000))
                        return_product_lst.append(return_product)

                    if notification_type in ["Correction", "Customer Notification"]:
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                         brf_ship_label_flag, [],
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id,
                                         notif_name,
                                         process_lock, out_file)

                    if notification_type in ["Removal", "Market Withdrawal"]:
                        do_you_return_products = random.choice(whats_choice)
                        if do_you_return_products.lower() == "no":
                            notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                             brf_ship_label_flag,
                                             [],
                                             second_account, second_account_unique, second_account_name,
                                             first_consig_email_second_account,
                                             first_consig_name_second_account, company_in_notif, adminnotif_id,
                                             notif_name,
                                             process_lock, out_file)
                        else:
                            notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                             brf_ship_label_flag,
                                             return_product_lst,
                                             second_account, second_account_unique, second_account_name,
                                             first_consig_email_second_account,
                                             first_consig_name_second_account, company_in_notif, adminnotif_id,
                                             notif_name,
                                             process_lock, out_file)

        else:
            # from db
            assignee_in_notif = get_assignees_per_notif_id(notification_db_id)
            # ackn_list = random.sample(assignee_in_notif, len(assignee_in_notif) // 2)
            ackn_list = assignee_in_notif

            company_in_notif = get_compname_per_notif_id(notification_db_id)
            adminnotif_id = get_admin_notif_id_per_notif_id(notification_db_id)
            notif_name = get_notif_name_per_notif_id(notification_db_id)

            for i in range(int(len(ackn_list))):
                print("Assignee " + str(i) + " out of " + str(len(ackn_list)))
                db_id = get_db_id_per_assignee_notification(notification_db_id, ackn_list[i])
                notif_assignee_generate_otp(db_id, out_file)
                otp_from_db = get_otp_per_assignee_notification(notification_db_id, ackn_list[i])
                notif_assignee_acknowledge(db_id, ackn_list[i], otp_from_db, adminnotif_id, notif_name,
                                           company_in_notif, out_file)

            # for assign_to_ackn in ackn_list:
            #     db_id = get_db_id_per_assignee_notification(notification_db_id, assign_to_ackn)
            #     notif_assignee_generate_otp(db_id)
            #     otp_from_db = get_otp_per_assignee_notification(notification_db_id, assign_to_ackn)
            #     notif_assignee_acknowledge(db_id, assign_to_ackn, otp_from_db, adminnotif_id, notif_name,
            #                                company_in_notif)

        if is_closed.lower() == 'yes':
            notif_close(notification_db_id, out_file)
        if is_closed.lower() == "yesgt5":
            close_date = str(fake.date_between('-8y', '-6y'))
            if console_output_info:
                print(close_date)
                print(close_date, out_file)
            update_notification_issue_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, close_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, close_date)
            notif_close(notification_db_id, out_file)
            update_notification_closed_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_closed_date_account(notification_db_id, close_date)
            else:
                update_notification_closed_date_assignees(notification_db_id, close_date)


def load_notif_completed_reopen(with_aging, without_support_tools, is_closed, process_txt, process_lock, out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(5, without_support_tools, process_txt, process_lock, out_file)
        # sending 5 to avoid the paramaters only_hcp_pa and only_mw_cu_co_re
        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        notification_type = str(get_notification_type_from_db(notification_db_id))
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
            if console_output_info_msg: print("--------------------------------------------")
            if console_output_info_msg: print(notification_type)
            if console_output_info_msg: print("--------------------------------------------")

            notif_actions(notification_db_id, notification_type, out_file)

            accounts_list_submit = notif_assign_accounts(notification_db_id, out_file, choose_accounts_with_consignees)
        else:
            notif_assign_assignees(notification_db_id, out_file)

        notif_submit(notification_db_id, accounts_list_submit, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info_msg: print("Changing Issued date to " + issue_date)
            update_notification_issue_date(notification_db_id, issue_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, issue_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, issue_date)

        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
            company_in_notif = get_compname_per_notif_id(notification_db_id)
            adminnotif_id = get_admin_notif_id_per_notif_id(notification_db_id)
            notif_name = get_notif_name_per_notif_id(notification_db_id)
            accounts_in_notif = get_accounts_per_notif_id(notification_db_id)

            if len(accounts_in_notif) <= 5 and len(accounts_in_notif) == 2:
                second_account = accounts_in_notif[1][0]
                second_account_unique = str(notification_db_id) + "-" + second_account
                consignees_second_account = get_consignees_per_account(second_account)
                second_account_name = get_account_name_per_ucn_id(second_account)
                first_consig_id_second_account = str(consignees_second_account[0][0])
                first_consig_fn_second_account = str(consignees_second_account[0][1])
                first_consig_ln_second_account = str(consignees_second_account[0][2])
                first_consig_name_second_account = str(
                    consignees_second_account[0][1] + " " + consignees_second_account[0][2])
                first_consig_email_second_account = str(consignees_second_account[0][3])

                second_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, second_account,
                                                                     first_consig_email_second_account,
                                                                     first_consig_name_second_account, False,
                                                                     company_in_notif, adminnotif_id, notif_name,
                                                                     notification_type, second_account_name)

                notif_assign_consignee(second_assig_consig_data, second_account, out_file)

                brf_attach_flag = get_attachment_per_notif_id(notification_db_id)
                brf_ship_label_flag = get_shipping_label_per_notif_id(notification_db_id)

                return_product_lst = []
                for dl in datalist:
                    return_product = PrfReturnProduct(dl['productCode'], dl['serialNumber'], random.randint(1, 999))
                    return_product_lst.append(return_product)

                if notification_type in ["Correction", "Customer Notification"]:
                    notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag, [],
                                     second_account, second_account_unique, second_account_name,
                                     first_consig_email_second_account,
                                     first_consig_name_second_account, company_in_notif, adminnotif_id, notif_name,
                                     process_lock, out_file)

                if notification_type in ["Removal", "Market Withdrawal"]:
                    do_you_return_products = random.choice(whats_choice)
                    if do_you_return_products.lower() == "no":
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag,
                                         [],
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id, notif_name,
                                         process_lock, out_file)
                    else:
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag, brf_ship_label_flag,
                                         return_product_lst,
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id, notif_name,
                                         process_lock, out_file)

                raise_notif_reopen_request(notification_db_id, adminnotif_id, notif_name, second_account,
                                           second_account_name, company_in_notif, fake.text(200),
                                           first_consig_ln_second_account, first_consig_fn_second_account,
                                           first_consig_email_second_account, out_file)
            else:
                for i in range(int(len(accounts_in_notif)) // 2):
                    print("Account " + str(i) + " out of " + str(len(accounts_in_notif) // 2))
                    second_account = accounts_in_notif[i][0]
                    second_account_unique = str(notification_db_id) + "-" + second_account
                    consignees_second_account = get_consignees_per_account(second_account)
                    second_account_name = get_account_name_per_ucn_id(second_account)
                    first_consig_id_second_account = str(consignees_second_account[0][0])
                    first_consig_fn_second_account = str(consignees_second_account[0][1])
                    first_consig_ln_second_account = str(consignees_second_account[0][2])
                    first_consig_name_second_account = str(
                        consignees_second_account[0][1] + " " + consignees_second_account[0][2])
                    first_consig_email_second_account = str(consignees_second_account[0][3])

                    second_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, second_account,
                                                                         first_consig_email_second_account,
                                                                         first_consig_name_second_account, False,
                                                                         company_in_notif, adminnotif_id,
                                                                         notif_name,
                                                                         notification_type, second_account_name)

                    notif_assign_consignee(second_assig_consig_data, second_account, out_file)

                    brf_attach_flag = get_attachment_per_notif_id(notification_db_id)
                    brf_ship_label_flag = get_shipping_label_per_notif_id(notification_db_id)

                    return_product_lst = []
                    for dl in datalist:
                        return_product = ReturnProduct(dl['productCode'], dl['serialNumber'],
                                                       random.randint(1, 1000))
                        return_product_lst.append(return_product)

                    if notification_type in ["Correction", "Customer Notification"]:
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                         brf_ship_label_flag, [],
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id,
                                         notif_name,
                                         process_lock, out_file)

                    if notification_type in ["Removal", "Market Withdrawal"]:
                        do_you_return_products = random.choice(whats_choice)
                        if do_you_return_products.lower() == "no":
                            notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                             brf_ship_label_flag,
                                             [],
                                             second_account, second_account_unique, second_account_name,
                                             first_consig_email_second_account,
                                             first_consig_name_second_account, company_in_notif, adminnotif_id,
                                             notif_name,
                                             process_lock, out_file)
                        else:
                            notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                             brf_ship_label_flag,
                                             return_product_lst,
                                             second_account, second_account_unique, second_account_name,
                                             first_consig_email_second_account,
                                             first_consig_name_second_account, company_in_notif, adminnotif_id,
                                             notif_name,
                                             process_lock, out_file)

                    raise_notif_reopen_request(notification_db_id, adminnotif_id, notif_name, second_account,
                                               second_account_name, company_in_notif, fake.text(200),
                                               first_consig_ln_second_account, first_consig_fn_second_account,
                                               first_consig_email_second_account, out_file)

        if is_closed.lower() == 'yes':
            notif_close(notification_db_id, out_file)
        if is_closed.lower() == "yesgt5":
            close_date = str(fake.date_between('-8y', '-6y'))
            if console_output_info:
                print(close_date)
                print(close_date, file=out_file)
            update_notification_issue_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, close_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, close_date)
            notif_close(notification_db_id, out_file)
            update_notification_closed_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_closed_date_account(notification_db_id, close_date)
            else:
                update_notification_closed_date_assignees(notification_db_id, close_date)


def load_notif_all_completed_reopen(with_aging, without_support_tools, is_closed, process_txt, process_lock, out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(5, without_support_tools, process_txt, process_lock, out_file)
        # sending 5 to avoid the paramaters only_hcp_pa and only_mw_cu_co_re
        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        notification_type = str(get_notification_type_from_db(notification_db_id))
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
            if console_output_info_msg: print("--------------------------------------------")
            if console_output_info_msg: print(notification_type)
            if console_output_info_msg: print("--------------------------------------------")

            notif_actions(notification_db_id, notification_type, out_file)

            accounts_list_submit = notif_assign_accounts(notification_db_id, out_file, choose_accounts_with_consignees)
        else:
            notif_assign_assignees(notification_db_id, out_file)

        notif_submit(notification_db_id, accounts_list_submit, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info_msg: print("Changing Issued date to " + issue_date)
            update_notification_issue_date(notification_db_id, issue_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, issue_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, issue_date)

        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
            company_in_notif = get_compname_per_notif_id(notification_db_id)
            adminnotif_id = get_admin_notif_id_per_notif_id(notification_db_id)
            notif_name = get_notif_name_per_notif_id(notification_db_id)
            accounts_in_notif = get_accounts_per_notif_id(notification_db_id)

            for i in range(int(len(accounts_in_notif))):
                print("Account " + str(i) + " out of " + str(len(accounts_in_notif)))
                second_account = accounts_in_notif[i][0]
                second_account_unique = str(notification_db_id) + "-" + second_account
                consignees_second_account = get_consignees_per_account(second_account)
                second_account_name = get_account_name_per_ucn_id(second_account)
                first_consig_id_second_account = str(consignees_second_account[0][0])
                first_consig_fn_second_account = str(consignees_second_account[0][1])
                first_consig_ln_second_account = str(consignees_second_account[0][2])
                first_consig_name_second_account = str(
                    consignees_second_account[0][1] + " " + consignees_second_account[0][2])
                first_consig_email_second_account = str(consignees_second_account[0][3])

                second_assig_consig_data = SaveAssignedConsigneeData(notification_db_id, second_account,
                                                                     first_consig_email_second_account,
                                                                     first_consig_name_second_account, False,
                                                                     company_in_notif, adminnotif_id,
                                                                     notif_name,
                                                                     notification_type, second_account_name)

                notif_assign_consignee(second_assig_consig_data, second_account, out_file)

                brf_attach_flag = get_attachment_per_notif_id(notification_db_id)
                brf_ship_label_flag = get_shipping_label_per_notif_id(notification_db_id)

                return_product_lst = []
                for dl in datalist:
                    return_product = ReturnProduct(dl['productCode'], dl['serialNumber'],
                                                   random.randint(1, 1000))
                    return_product_lst.append(return_product)

                if notification_type in ["Correction", "Customer Notification"]:
                    notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                     brf_ship_label_flag, [],
                                     second_account, second_account_unique, second_account_name,
                                     first_consig_email_second_account,
                                     first_consig_name_second_account, company_in_notif, adminnotif_id,
                                     notif_name,
                                     process_lock, out_file)

                if notification_type in ["Removal", "Market Withdrawal"]:
                    do_you_return_products = random.choice(whats_choice)
                    if do_you_return_products.lower() == "no":
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                         brf_ship_label_flag,
                                         [],
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id,
                                         notif_name,
                                         process_lock, out_file)
                    else:
                        notif_submit_brf(notification_db_id, notification_type, brf_attach_flag,
                                         brf_ship_label_flag,
                                         return_product_lst,
                                         second_account, second_account_unique, second_account_name,
                                         first_consig_email_second_account,
                                         first_consig_name_second_account, company_in_notif, adminnotif_id,
                                         notif_name,
                                         process_lock, out_file)

                raise_notif_reopen_request(notification_db_id, adminnotif_id, notif_name, second_account,
                                           second_account_name, company_in_notif, fake.text(200),
                                           first_consig_ln_second_account, first_consig_fn_second_account,
                                           first_consig_email_second_account, out_file)

        if is_closed.lower() == 'yes':
            notif_close(notification_db_id, out_file)
        if is_closed.lower() == "yesgt5":
            close_date = str(fake.date_between('-8y', '-6y'))
            if console_output_info:
                print(close_date)
                print(close_date, file=out_file)
            update_notification_issue_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_issue_date_account(notification_db_id, close_date)
            else:
                update_notification_issue_date_assignees(notification_db_id, close_date)
            notif_close(notification_db_id, out_file)
            update_notification_closed_date(notification_db_id, close_date)
            if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:
                update_notification_closed_date_account(notification_db_id, close_date)
            else:
                update_notification_closed_date_assignees(notification_db_id, close_date)


def load_notif_drft(with_aging, without_support_tools, num_page, process_txt, process_lock, out_file):
    if only_delete != "yes":
        create_notif_data = notif_p1(3, without_support_tools, process_txt, process_lock, out_file)
        notification_db_id = create_notif_data[0]

        if without_support_tools == 'no':
            notif_up_sup_tools(without_support_tools, notification_db_id, process_lock, out_file)

        # from db
        # notification_type = str(get_notification_type_from_db(notification_db_id))
        notification_type = create_notif_data[1]
        accounts_list_submit = []
        if notification_type in ["Removal", "Market Withdrawal", "Correction", "Customer Notification"]:

            if num_page == '2PAG':
                notif_actions(notification_db_id, notification_type, out_file)

            if num_page == '3PAG':
                notif_actions(notification_db_id, notification_type, out_file)
                accounts_list_submit = notif_assign_accounts(notification_db_id, out_file,
                                                             choose_accounts_with_consignees)
        else:
            if num_page == '3PAG':
                notif_assign_assignees(notification_db_id, out_file)

        if with_aging == 'yes':
            issue_date = str(fake.date_between('-2y', '-1y'))
            if console_output_info: print(issue_date)
            update_notification_issue_date(notification_db_id, issue_date)


def load_faq(number, out_file):
    if only_delete != "yes":

        url = get_url()

        for i in range(1, number + 1):
            faq_data = SaveFaqData(fake.text(max_nb_chars=100), fake.text(max_nb_chars=500))

            faq_service = SaveFaqService("serviceRequest", "saveFAQ", faq_data)

            a_headers = {"Content-Type": "application/json", "Accept": "application/json"}
            # if console_output: print(json.dumps(actions_service))
            response = requests.post(url, headers=a_headers, data=json.dumps(faq_service))
            # if console_output: print(json.dumps(actions_service))
            if console_output_info_msg:
                print('faq added')
                print('faq added', file=out_file)
            if console_output_response:
                print(response.content.decode())
                print(response.content.decode(), file=out_file)


def load_other_inquiries_data(number, out_file):
    if only_delete != "yes":
        url = get_url()
        for i in range(1, number + 1):
            inquiry_type = get_rand_dbid_ref_datas_table("inquiryType")
            admin_notification_id = get_rand_notif_id_notifications_table()
            ucn_no = get_rand_mapped_ucn_nbr(admin_notification_id)
            comments = fake.text(max_nb_chars=4000).replace(". ", ".<br>").replace(".\n", ".<br>")
            creator_first_name = "Vinay Babu"
            creator_last_name = "Gutta"
            created_by = "vbabugut@its.jnj.com"

            inquiry_data = SaveInquiriesRequestData(inquiry_type, admin_notification_id, ucn_no, comments,
                                                    creator_first_name, creator_last_name, created_by)

            inquiry_service = SaveInquiriesRequestService("serviceRequest", "saveInquiriesRequest", inquiry_data)

            a_headers = {"Content-Type": "application/json", "Accept": "application/json",
                         "Authorization": bearer_token}
            # if console_output: print(json.dumps(actions_service))
            response = requests.post(url, headers=a_headers, data=json.dumps(inquiry_service))
            # if console_output: print(json.dumps(actions_service))
            if console_output_info_msg:
                print('inquiry added')
                print('inquiry added', file=out_file)
            if console_output_response:
                print(response.content.decode())
                print(response.content.decode(), file=out_file)


def load_one_faq(out_file):
    if only_delete != "yes":
        url = get_url()
        faq_data = SaveFaqData(fake.text(max_nb_chars=100), fake.text(max_nb_chars=500))

        faq_service = SaveFaqService("serviceRequest", "saveFAQ", faq_data)

        a_headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": bearer_token}
        if console_output_info: print(url)
        response = requests.post(url, headers=a_headers, data=json.dumps(faq_service))
        # if console_output: print(json.dumps(actions_service))
        if console_output_info_msg:
            print('faq added')
            print('faq added', file=out_file)
        if console_output_response:
            print(response.content.decode())
            print(response.content.decode(), file=out_file)


def runner(name, locker):
    out_file = get_output_log_file(name)
    global fake
    fake = set_faker(out_file)
    delete_contents_of_folder(".\subjectproducts")
    st = time.time()

    # if console_output: print(load_other_inquiries)

    if load_faqs == 'yes':
        for i in range(1, 100):
            load_one_faq(out_file)

    if load_other_inquiries == 'yes':
        load_other_inquiries_data(5, out_file)

    if load_deactivate_contact_requests == 'yes':
        load_deactivate_contact_requests_data(out_file)
        approve_contact_requests_data(2, out_file)
        deny_contact_requests_data(2, out_file)

    if load_new_contact_requests == 'yes':
        load_add_new_contact_requests_data(10, out_file)
        # approve_contact_requests_data(1)
        # deny_contact_requests_data(1)

    if load_guidance_documents == 'yes':
        if only_delete != "yes":
            delete_all_guidance_documents(out_file)
            upload_guidance_document(locker, out_file)

    if time_to_run_minutes > 0:
        start_time = time.time()
        while True:
            shuffles_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
            random.shuffle(shuffles_list)
            prog = 0

            for j in shuffles_list:
                prog = prog + 1
                print('****************************************')
                print('Progress ' + str(prog) + ' of 15')
                print('****************************************')
                print('****************************************', file=out_file)
                print('Progress ' + str(prog) + ' of 15', file=out_file)
                print('****************************************', file=out_file)
                if j == 1 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''create notifications with "new" status'''
                    print('''create notifications with "new" status''')
                    print('''create notifications with "new" status''', file=out_file)
                    load_notif_new('no', 'no', 'no', name, locker, out_file)

                if j == 2 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''create customer notifications with "new" status'''
                    print('''create customer notifications with "new" status''')
                    print('''create customer notifications with "new" status''', file=out_file)
                    load_notif_cu_pa('no', 'no', 'no', name, locker, out_file)

                if j == 5 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''create notifications with "draft" status'''
                    print('''create notifications with "draft" status''')
                    print('''create notifications with "draft" status''', file=out_file)
                    load_notif_drft('no', 'yes', '3PAG', name, locker, out_file)

                if j == 6 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''create notifications with "new" status and aging'''
                    print('''create notifications with "new" status and aging''')
                    print('''create notifications with "new" status and aging''', file=out_file)
                    load_notif_new('yes', 'no', 'no', name, locker, out_file)
                    load_notif_cu_pa('yes', 'no', 'no', name, locker, out_file)

                if j == 7 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''create notifications with "new" status and without support tools'''
                    print('''create notifications with "new" status and without support tools''')
                    print('''create notifications with "new" status and without support tools''', file=out_file)
                    load_notif_new('no', 'yes', 'no', name, locker, out_file)

                if j == 8 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''new closed notifications'''
                    print('''new closed notifications''')
                    print('''new closed notifications''', file=out_file)
                    load_notif_new('no', 'yes', 'yes', name, locker, out_file)
                    load_notif_new('yes', 'no', 'yes', name, locker, out_file)

                if j == 9 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                    '''completed closed notifications'''
                    print('''completed closed notifications''')
                    print('''completed closed notifications''', file=out_file)
                    load_notif_new_inprogress_completed('no', 'yes', 'yes', name, locker, out_file)

                if j == 10 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                    '''new closed notifications 5y back'''
                    print('''new closed notifications 5y back''')
                    print('''new closed notifications 5y back''', file=out_file)
                    load_notif_new('yes', 'no', 'YesGt5', name, locker, out_file)

                if j == 11 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                    '''completed closed notifications 5y back'''
                    print('''completed closed notifications 5y back''')
                    print('''completed closed notifications 5y back''', file=out_file)
                    load_notif_new_inprogress_completed('yes', 'no', 'yesGt5', name, locker, out_file)

                if j == 12 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                    '''all completed notifications'''
                    print('''all completed notifications''')
                    print('''all completed notifications''', file=out_file)
                    load_notif_all_completed('no', 'no', 'no', name, locker, out_file)

                if j == 13 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                    '''all completed notifications'''
                    print('''all completed notifications''')
                    print('''all completed notifications''', file=out_file)
                    load_notif_all_completed('no', 'yes', 'yes', name, locker, out_file)

                if j == 14 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                    '''all completed notifications'''
                    print('''all completed notifications''')
                    print('''all completed notifications''', file=out_file)
                    load_notif_all_completed_reopen("no", "no", "no", name, locker, out_file)

                if j == 15 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                    '''all completed notifications'''
                    print('''all completed notifications''')
                    print('''all completed notifications''', file=out_file)
                    load_notif_all_completed('yes', 'no', 'yesGt5', name, locker, out_file)

            check_time = time.time()
            how_time = round(check_time - start_time)

            if how_time >= (time_to_run_minutes * 60):
                break

    else:
        #####################
        shuffles_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        random.shuffle(shuffles_list)
        prog = 0

        for j in shuffles_list:
            prog = prog + 1
            print('****************************************')
            print('Progress ' + str(prog) + ' of 15')
            print('****************************************')
            if j == 1 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''create notifications with "new" status'''
                for i in range(1, number_notif_new + 1):
                    print("New notification " + str(i) + " of " + str(number_notif_new))
                    load_notif_new('no', 'no', 'no', name, locker, out_file)

            if j == 2 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''create customer notifications with "new" status'''
                for i in range(1, number_notif_new_pa_cu + 1):
                    print("New notification HCP - PA " + str(i) + " of " + str(number_notif_new_pa_cu))
                    load_notif_cu_pa('no', 'no', 'no', name, locker, out_file)

            if j == 3 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''create notifications with inprogress acknowledged'''
                for i in range(1, number_notif_ackn_inprogress + 1):
                    load_notif_new_inprogress_completed('no', 'no', 'no', name, locker, out_file)

            if j == 4 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                for i in range(1, number_notif_few_complete_reopen_request + 1):
                    load_notif_completed_reopen("no", "no", "no", name, locker, out_file)

            if j == 5 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''create notifications with "draft" status'''
                for i in range(1, number_notif_draft + 1):
                    print("New notification draft " + str(i) + " of " + str(number_notif_draft))
                    if (i % 2) == 0 and (i % 4) == 0:
                        # load_notif_drft('yes', 'no', '1PAG', name, locker)
                        load_notif_drft('no', 'no', '1PAG', name, locker, out_file)
                    elif (i % 2) == 0:
                        # load_notif_drft('yes', 'yes', '2PAG', name, locker)
                        load_notif_drft('no', 'no', '2PAG', name, locker, out_file)
                    else:
                        load_notif_drft('no', 'yes', '3PAG', name, locker, out_file)

            if j == 6 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''create notifications with "new" status and aging'''
                for i in range(1, number_notif_new_aging + 1):
                    print("New notification ageing " + str(i) + " of " + str(number_notif_new_aging))
                    load_notif_new('yes', 'no', 'no', name, locker, out_file)
                    load_notif_cu_pa('yes', 'no', 'no', name, locker, out_file)

            if j == 7 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''create notifications with "new" status and without support tools'''
                for i in range(1, number_notif_new_without_sup_tools + 1):
                    print("New notification without sup tools " + str(i) + " of " + str(
                        number_notif_new_without_sup_tools))
                    load_notif_new('no', 'yes', 'no', name, locker, out_file)

            if j == 8 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''new closed notifications'''
                for i in range(1, number_notif_new_closed + 1):
                    print("New notification closed " + str(i) + " of " + str(number_notif_new_closed))
                    if (i % 2) == 0:
                        load_notif_new('no', 'yes', 'yes', name, locker, out_file)
                    else:
                        load_notif_new('yes', 'no', 'yes', name, locker, out_file)

            if j == 9 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''completed closed notifications'''
                for i in range(1, number_notif_few_completed_closed + 1):
                    if (i % 2) == 0:
                        load_notif_new_inprogress_completed('no', 'yes', 'yes', name, locker, out_file)
                    else:
                        load_notif_new_inprogress_completed('yes', 'no', 'yes', name, locker, out_file)

            if j == 10 and (create_complete.lower() == 'oc' or create_complete.lower() == 'both'):
                '''new closed notifications 5y back'''
                for i in range(1, number_notif_new_closed_gt_5y_back + 1):
                    print("New notification closed 5 back " + str(i) + " of " + str(number_notif_new_closed_gt_5y_back))
                    load_notif_new('yes', 'no', 'YesGt5', name, locker, out_file)

            if j == 11 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''completed closed notifications 5y back'''
                for i in range(1, number_notif_few_completed_closed_gt_5y_back + 1):
                    load_notif_new_inprogress_completed('yes', 'no', 'yesGt5', name, locker, out_file)

            if j == 12 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''all completed notifications'''
                for i in range(1, number_notif_all_completed + 1):
                    load_notif_all_completed('no', 'no', 'no', name, locker, out_file)

            if j == 13 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''all completed notifications'''
                for i in range(1, number_notif_all_completed_closed + 1):
                    load_notif_all_completed('no', 'yes', 'yes', name, locker, out_file)

            if j == 14 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''all completed notifications'''
                for i in range(1, number_notif_all_complete_reopen_request + 1):
                    load_notif_all_completed_reopen("no", "no", "no", name, locker, out_file)

            if j == 15 and (create_complete.lower() == 'cc' or create_complete.lower() == 'both'):
                '''all completed notifications'''
                for i in range(1, number_notif_all_completed_closed_gt_5y_back + 1):
                    load_notif_all_completed('yes', 'no', 'yesGt5', name, locker, out_file)

        #####################################################

    et = time.time()

    # get the execution time
    elapsed_time = round(et - st)
    if console_output_info_msg:
        print('Execution time: ' + name + ' ', convert_to_hr_min_sec_str(elapsed_time))
        print('Execution time: ' + name + ' ', convert_to_hr_min_sec_str(elapsed_time), file=out_file)

    out_file.close()


if __name__ == '__main__':
    freeze_support()

    st = time.time()

    if delete_existing_data == 'yes':
        delete_data_notification_images_material_sbj()

    if total_number_notification_to_create < (
            number_notif_ackn_inprogress + number_notif_new_aging + number_notif_new_without_sup_tools + number_notif_new + number_notif_draft + number_notif_new_closed):
        exit("Total notifications to create is less than the sum of "
             "number_notif_ackn_inprogress+number_notif_new_aging+number_notif_new_without_sup_tools+number_notif_new"
             "+number_notif_draft+number_notif_closed")

    if only_hcp_pa.lower() == only_mw_cu_co_re.lower() == 'yes':
        exit("both parameters 'only_hcp_pa' and 'only_mw_cu_co_re' cannot be 'yes'")

    if number_threads > 25:
        exit("number of threads cannot be more than 25")

    alph_char = list(string.ascii_uppercase)
    random.shuffle(alph_char)

    lock = Lock()

    processes = [Process(target=runner, args=(alph_char[i], lock)) for i in range(number_threads)]

    for process in processes:
        process.start()
    # wait for all processes to complete
    for process in processes:
        process.join()

    # proc1 = Process(target=runner, args=('A', lock))
    # proc1.start()
    #
    # time.sleep(5)
    # proc2 = Process(target=runner, args=('B', lock))
    # # if console_output: print(proc1.is_alive())
    # proc2.start()
    #
    # proc1.join()
    # proc2.join()

    et = time.time()

    # get the execution time
    elapsed_time = round(et - st)
    if console_output_info_msg: print('Total Execution time: ', convert_to_hr_min_sec_str(elapsed_time))
