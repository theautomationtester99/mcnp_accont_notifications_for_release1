import csv
import json
import timeit
from enum import Enum
from typing import List, Any
from datetime import datetime
import os
import random

import requests
from jproperties import Properties

configs = Properties()
with open('input.properties', 'rb') as config_file:
    configs.load(config_file)

number_of_supporting_tools_to_load = int(configs.get("number_of_supporting_tools_to_load").data)
number_of_product_images_to_load = int(configs.get("number_of_product_images_to_load").data)
number_of_brf_attachments_to_load = int(configs.get("number_of_brf_attachments_to_load").data)


def get_notification_files_list(without_supporting_tools, npi, out_file, plock):
    plock.acquire()
    files = []
    # image_filenames_list = list_file_names(".\images")
    # material_filenames_list = list_file_names(".\material")
    image_filenames_list = list_random_file_names("./images", 11, out_file)
    material_filenames_list = list_random_file_names("./material", 30, out_file)
    if number_of_supporting_tools_to_load > 30:
        exit("only 10 supporting tools supported")
    if number_of_product_images_to_load > 10:
        exit("only 10 products images supported")

    npl = npi

    for i in range(1, npl + 1):
        if (image_filenames_list[i].split('.')[1].lower()) == 'png':
            files.append(('notificationProductImages',
                          (image_filenames_list[i], open('./images/' + image_filenames_list[i], 'rb'), 'image/png')))

        if (image_filenames_list[i].split('.')[1].lower()) == 'jpg':
            files.append(('notificationProductImages',
                          (image_filenames_list[i], open('./images/' + image_filenames_list[i], 'rb'), 'image/jpeg')))

        if (image_filenames_list[i].split('.')[1].lower()) == 'jpeg':
            files.append(('notificationProductImages',
                          (image_filenames_list[i], open('./images/' + image_filenames_list[i], 'rb'), 'image/jpeg')))

    # if not (without_supporting_tools == 'yes'):
    #     for i in range(1, number_of_supporting_tools_to_load + 1):
    #         files.append(('supportMaterialFiles', (
    #             material_filenames_list[i], open('./material/' + material_filenames_list[i], 'rb'), 'application/pdf')))
    # else:
    #     files.append(('supportMaterialFiles', ('', '', '')))

    plock.release()

    return files


def get_product_images_subject_products_files_list(npi, process_txt, out_file, plock):
    plock.acquire()
    # start_t = timeit.default_timer()
    files = []

    image_filenames_list = list_random_file_names("./images", 10, out_file)
    subjectproducts_filenames_list = list_random_file_names("./subjectproducts", 1, out_file)
    if number_of_product_images_to_load > 10:
        exit("only 10 products images supported")

    npl = npi

    for i in range(1, npl + 1):
        if (image_filenames_list[i].split('.')[1].lower()) == 'png':
            files.append(('notificationProductImages',
                          (image_filenames_list[i], open('./images/' + image_filenames_list[i], 'rb'), 'image/png')))

        if (image_filenames_list[i].split('.')[1].lower()) == 'jpg':
            files.append(('notificationProductImages',
                          (image_filenames_list[i], open('./images/' + image_filenames_list[i], 'rb'), 'image/jpeg')))

        if (image_filenames_list[i].split('.')[1].lower()) == 'jpeg':
            files.append(('notificationProductImages',
                          (image_filenames_list[i], open('./images/' + image_filenames_list[i], 'rb'), 'image/jpeg')))

    if (subjectproducts_filenames_list[0].split('.')[1].lower()) == 'txt':
        # print("attaching subject products " + "./subjectproducts/sample" + process_txt + ".txt")
        # print("attaching subject products " + "./subjectproducts/sample" + process_txt + ".txt", file=out_file)
        files.append(('subjectProductsData', (
            subjectproducts_filenames_list[0], open("./subjectproducts/sample" + process_txt + ".txt", 'rb'),
            'application/json')))

    # cn_time = round(timeit.default_timer() - start_t, 2)
    # append_write = 'a'
    # if os.path.exists(".\perf_data\cn_data" + process_txt + ".csv"):
    #     append_write = 'a'  # append if already exists
    # else:
    #     append_write = 'w'  # make a new file if not
    #     with open(".\perf_data\cn_data" + process_txt + ".csv", append_write, newline='') as f:
    #         writer = csv.writer(f)  # this is the writer object
    #         writer.writerow(["Process", "Service", "Time"])
    #     append_write = 'a'
    #
    # with open(".\perf_data\cn_data" + process_txt + ".csv", append_write, newline='') as f:
    #     writer = csv.writer(f)  # this is the writer object
    #     writer.writerow([process_txt, "Attach Files", str(cn_time)])

    plock.release()

    return files


def get_subject_products_input_file(out_file, plock):
    plock.acquire()
    files = []

    subject_products_filename = list_random_file_names("./subject_products_excel", 1, out_file)

    if (subject_products_filename[0].split('.')[1].lower()) == 'xlsx':
        # print("attaching subject products" + './subject_products_excel' + subject_products_filename[0])
        # print("attaching subject products" + './subject_products_excel' + subject_products_filename[0], file=out_file)
        files.append(('files', (
            subject_products_filename[0], open('./subject_products_excel/' + subject_products_filename[0], 'rb'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')))

    plock.release()

    return files


def get_brf_files_list(no_files, out_file, plock):
    plock.acquire()
    files = []
    image_filenames_list = list_file_names("./images")
    material_filenames_list = list_file_names("./material")
    files_list_random = list_random_file_names("./material", 40, out_file)

    # print(files_list_random)

    npl = int(number_of_brf_attachments_to_load)

    if not (no_files == 'yes'):
        for i in range(0, npl - 1):
            if (files_list_random[i].split('.')[1].lower()) == 'pdf':
                # files.append(('files', (
                #     material_filenames_list[i], open('./material/' + material_filenames_list[i], 'rb'), 'application/pdf')))
                files.append(('files', (
                    files_list_random[i], open('./material/' + files_list_random[i], 'rb'), 'application/pdf')))
            if (files_list_random[i].split('.')[1].lower()) == 'mp4':
                # files.append(('files', (
                #     material_filenames_list[i], open('./material/' + material_filenames_list[i], 'rb'), 'application/pdf')))
                files.append(('files', (
                    files_list_random[i], open('./material/' + files_list_random[i], 'rb'), 'video/mp4')))
    else:
        files.append(('files', ('', '', '')))

    plock.release()

    return files


def get_brf_one_file(no_files, file_name, plock):
    plock.acquire()
    files = []

    # print(files_list_random)

    if not (no_files == 'yes'):
        if (file_name.split('.')[1].lower()) == 'pdf':
            files.append(('files', (file_name, open('./material/' + file_name, 'rb'), 'application/pdf')))
        if (file_name.split('.')[1].lower()) == 'mp4':
            files.append(('files', (
                file_name, open('./material/' + file_name, 'rb'), 'video/mp4')))
        if (file_name.split('.')[1].lower()) == 'jpg':
            files.append(('files', (
                file_name, open('./material/' + file_name, 'rb'), 'image/jpeg')))
        if (file_name.split('.')[1].lower()) == 'jpeg':
            files.append(('files', (
                file_name, open('./material/' + file_name, 'rb'), 'image/jpeg')))
        if (file_name.split('.')[1].lower()) == 'png':
            files.append(('files', (
                file_name, open('./material/' + file_name, 'rb'), 'image/png')))
    else:
        files.append(('files', ('', '', '')))

    plock.release()

    return files


def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]


def list_file_names(directory):
    return [file for file in os.listdir(directory)]


def list_random_file_names(directory, number_files, out_file):
    file_list = []
    del file_list[:]
    res = []
    del res[:]
    i = 0
    while i < number_files:
        file_list.append(random.choice(os.listdir(directory)))
        res = [*set(file_list)]
        i = len(res)
    # res.append("193MB_Honey_and_nuts_AdobeExpress_AdobeExpress.mp4")
    # print(res)
    # print(res, file=out_file)
    return res


# files = [
#     ('notificationProductImages', ('notepad_fR7SB1VRmE - Copy.png',
#                                    open('D:/Users/VBabuGut/OneDrive - JNJ/Desktop/notepad_fR7SB1VRmE - Copy.png', 'rb'),
#                                    'image/png')),
#     ('notificationProductImages', (
#         'notepad_fR7SB1VRmE.png', open('D:/Users/VBabuGut/OneDrive - JNJ/Desktop/notepad_fR7SB1VRmE.png', 'rb'),
#         'image/png')),
#     ('supportMaterialFiles', ('Test Script and Execution - How _bb186a68aa5b46f8a64e0ac2068c9c16-251122-0749-1526.pdf',
#                               open(
#                                   'D:/Users/VBabuGut/OneDrive - JNJ/Desktop/Test Script and Execution - How _bb186a68aa5b46f8a64e0ac2068c9c16-251122-0749-1526.pdf',
#                                   'rb'), 'application/pdf')),
#     ('supportMaterialFiles', ('Test Script and Execution - How _f017209d5885438c93a0fe7efbcb6de3-251122-0751-1528.pdf',
#                               open(
#                                   'D:/Users/VBabuGut/OneDrive - JNJ/Desktop/Test Script and Execution - How _f017209d5885438c93a0fe7efbcb6de3-251122-0751-1528.pdf',
#                                   'rb'), 'application/pdf'))
# ]

'''
Create Notification Service Classes
'''


class Datum(dict):
    product_code: str
    product_name: str
    serial_number: str
    gtin_number: str
    description: str
    expiry_date: str
    distribution_start_date: str
    distribution_end_date: str
    active_flag: bool

    def __init__(self, product_code: str, product_name: str, serial_number: str, gtin_number: str, description: str,
                 expiry_date: str, distribution_start_date: str, distribution_end_date: str, active_flag: bool) -> None:
        self.product_code = product_code
        self.product_name = product_name
        self.serial_number = serial_number
        self.gtin_number = gtin_number
        self.description = description
        self.expiry_date = expiry_date
        self.distribution_start_date = distribution_start_date
        self.distribution_end_date = distribution_end_date
        self.active_flag = active_flag

        dict.__init__(self, productCode=product_code, productName=product_name, serialNumber=serial_number,
                      gtinNumber=gtin_number, description=description, expiryDate=expiry_date,
                      distributionStartDate=distribution_start_date,
                      distributionEndDate=distribution_end_date, activeFlag=active_flag)


class SubjectProductsData(dict):
    deleted_data: List[Any]
    data: List[Datum]
    audit_subject_products_required: bool

    def __init__(self, deleted_data: List[Any], data: List[Datum], audit_subject_products_required: bool) -> None:
        self.deleted_data = deleted_data
        self.data = data
        self.audit_subject_products_required = audit_subject_products_required

        dict.__init__(self, deletedData=deleted_data, data=data,
                      auditSubjectProductsRequired=audit_subject_products_required)


class Welcome5(dict):
    name: str
    admin_notification_id: str
    notification_type: str
    product_name: str
    company: str
    description: str
    potential_impact: str
    deleted_notification_product_images: List[Any]
    deleted_support_material_files: List[Any]
    attachmentType: str
    primary_notification_product_image_index: int
    primary_notification_product_image_id: bool
    company_signature: str
    signature_plain_text: str
    subject_products_data: SubjectProductsData
    ntype: str
    status_id: str
    issue_date: str
    created_by: str
    created_by_email: str
    audit_notification_required: bool

    def __init__(self, name: str, admin_notification_id: str, notification_type: str, product_name: str, company: str,
                 description: str, potential_impact: str, deleted_notification_product_images: List[Any],
                 deleted_support_material_files: List[Any], attachmentType: str,
                 primary_notification_product_image_index: int, primary_notification_product_image_id: bool,
                 company_signature: str, signature_plain_text: str,
                 subject_products_data: SubjectProductsData, ntype: str,
                 status_id: str, issue_date: str, created_by: str, created_by_email: str,
                 audit_notification_required: bool) -> None:
        self.name = name
        self.admin_notification_id = admin_notification_id
        self.notification_type = notification_type
        self.product_name = product_name
        self.company = company
        self.description = description
        self.potential_impact = potential_impact
        self.deleted_notification_product_images = deleted_notification_product_images
        self.deleted_support_material_files = deleted_support_material_files
        self.attachmentType = attachmentType
        self.primary_notification_product_image_index = primary_notification_product_image_index
        self.primary_notification_product_image_id = primary_notification_product_image_id
        self.company_signature = company_signature
        self.signature_plain_text = signature_plain_text
        self.subject_products_data = subject_products_data
        self.ntype = ntype
        self.status_id = status_id
        self.issue_date = issue_date
        self.created_by = created_by
        self.created_by_email = created_by_email
        self.audit_notification_required = audit_notification_required

        dict.__init__(self, name=name, adminNotificationId=admin_notification_id, notificationType=notification_type,
                      productName=product_name, company=company, description=description,
                      potentialImpact=potential_impact,
                      deletedNotificationProductImages=deleted_notification_product_images,
                      deletedSupportMaterialFiles=deleted_support_material_files,
                      attachmentType=attachmentType,
                      primaryNotificationProductImageIndex=primary_notification_product_image_index,
                      primaryNotificationProductImageId=primary_notification_product_image_id,
                      companySignature=company_signature, signaturePlainText=signature_plain_text,
                      subjectProductsData=subject_products_data,
                      type=ntype, statusId=status_id, issueDate=issue_date, createdBy=created_by,
                      createdByEmail=created_by_email, auditNotificationRequired=audit_notification_required)


'''
saveNotificationAssignees service classes
'''


class NotificationAssignee(dict):
    first_name: str
    last_name: str
    email: str

    def __init__(self, first_name: str, last_name: str, email: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        dict.__init__(self, firstName=first_name, lastName=last_name, email=email)


class AssigneeData(dict):
    notification_id: int
    deleted_data: List[Any]
    notification_assignees: List[NotificationAssignee]

    def __init__(self, notification_id: int, deleted_data: List[Any],
                 notification_assignees: List[NotificationAssignee]) -> None:
        self.notification_id = notification_id
        self.deleted_data = deleted_data
        self.notification_assignees = notification_assignees

        dict.__init__(self, notificationId=notification_id, deletedData=deleted_data,
                      notificationAssignees=notification_assignees)


class Welcome4(dict):
    service: str
    apiname: str
    data: AssigneeData

    def __init__(self, service: str, apiname: str, data: AssigneeData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveAccountNotificationMapping Service Classes
'''


class UCNList(dict):
    ucn_no: str

    def __init__(self, ucn_no: str) -> None:
        self.ucn_no = ucn_no

        dict.__init__(self, ucnNo=ucn_no)


class AccMapData(dict):
    notification_id: int
    deleted_data: List[Any]
    # ucn_list: List[int]
    add_account_flag: bool
    ucn_list: List[UCNList]

    def __init__(self, notification_id: int, deleted_data: List[Any], add_account_flag: bool,
                 ucn_list: List[UCNList]) -> None:
        self.notification_id = notification_id
        self.deleted_data = deleted_data
        self.add_account_flag = add_account_flag
        self.ucn_list = ucn_list

        dict.__init__(self, notificationId=notification_id, deletedData=deleted_data, addAccountFlag=add_account_flag,
                      UCNList=ucn_list)


class Welcome2(dict):
    service: str
    apiname: str
    data: AccMapData

    def __init__(self, service: str, apiname: str, data: AccMapData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data
        dict.__init__(self, service=service, apiname=apiname, data=data)


# data = Datum("121212", "tenamere", "11211121", "67889899", "this is alfofldfoer", "7/8/2025", "7/8/2025",
#              "7/8/2025", True)
# spd = SubjectProductsData([], [data])
# well = Welcome5("newondor", "N01010708", "6", "noprodure", "Acclarent", "dfdldlfldfdo", "lsdofdofdf", [], [], spd, "6",
#                 "4", "2020-09-03", "admin")
#
# print(json.dumps(well))
# dta = json.dumps(well)
#
# url = 'http://10.53.42.229:4200/api/apiGateway'
# Headers = {}
# form_data = {'service': 'notification', 'apiname': 'createNotification', 'data': dta}
#
#
# response = requests.post(url, headers=Headers, data=form_data, files=files)
#
# print(response.json())

'''
submitNotification Service Classes
'''


class NotifSubmitData(dict):
    notification_id: int
    status_id: int
    ucn_list: List[int]

    def __init__(self, notification_id: int, status_id: int, ucn_list: List[int]) -> None:
        self.notification_id = notification_id
        self.status_id = status_id
        self.ucn_list = ucn_list

        dict.__init__(self, notificationId=notification_id, statusId=status_id, UCNList=ucn_list)


class Welcome8(dict):
    service: str
    apiname: str
    data: NotifSubmitData

    def __init__(self, service: str, apiname: str, data: NotifSubmitData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveActionsRequired Service Classes
'''


class BrfData(dict):
    notification_id: int
    notification_type: int
    attachment_flag: bool
    shipping_label_flag: bool
    attachment_optional_flag: bool

    def __init__(self, notification_id: int, notification_type: int, attachment_flag: bool,
                 shipping_label_flag: bool, attachment_optional_flag: bool) -> None:
        self.notification_id = notification_id
        self.notification_type = notification_type
        self.attachment_flag = attachment_flag
        self.shipping_label_flag = shipping_label_flag
        self.attachment_optional_flag = attachment_optional_flag

        dict.__init__(self, notificationId=notification_id, notificationType=notification_type,
                      attachmentFlag=attachment_flag, shippingLabelFlag=shipping_label_flag,
                      attachmentOptionalFlag=attachment_optional_flag)


class CustomAction(dict):
    notification_id: int
    action: str
    order: int

    def __init__(self, notification_id: int, action: str, order: int) -> None:
        self.notification_id = notification_id
        self.action = action
        self.order = order

        dict.__init__(self, notificationId=notification_id, action=action, order=order)


class PredefinedDatum(dict):
    notification_id: int
    action_id: int
    order: int

    def __init__(self, notification_id: int, action_id: int, order: int) -> None:
        self.notification_id = notification_id
        self.action_id = action_id
        self.order = order

        dict.__init__(self, notificationId=notification_id, actionId=action_id, order=order)


class DataEntry(dict):
    brf_data: BrfData
    predefined_data: List[PredefinedDatum]
    custom_action: List[CustomAction]
    audit_actions_required: bool
    audit_prf_config_required: bool

    def __init__(self, brf_data: BrfData,
                 predefined_data: List[PredefinedDatum], custom_action: List[CustomAction],
                 audit_actions_required: bool, audit_prf_config_required: bool) -> None:
        self.brf_data = brf_data
        self.predefined_data = predefined_data
        self.custom_action = custom_action
        self.audit_actions_required = audit_actions_required
        self.audit_prf_config_required = audit_prf_config_required

        dict.__init__(self, brfData=brf_data, predefinedData=predefined_data, customAction=custom_action,
                      auditActionsRequired=audit_actions_required, auditPRFConfigRequired=audit_prf_config_required)


class Welcome10(dict):
    service: str
    apiname: str
    data: DataEntry

    def __init__(self, service: str, apiname: str, data: DataEntry) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
Close notification service classes
'''


class DataCloseNotif(dict):
    notification_id: int
    closed_by: str
    closed_by_email: str

    def __init__(self, notification_id: int, closed_by: str, closed_by_email: str) -> None:
        self.notification_id = notification_id
        self.closed_by = closed_by
        self.closed_by_email = closed_by_email

        dict.__init__(self, notificationId=notification_id, closedBy=closed_by, closedByEmail=closed_by_email)


class CloseNotifPayload(dict):
    service: str
    apiname: str
    data: DataCloseNotif

    def __init__(self, service: str, apiname: str, data: DataCloseNotif) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveAssignedConsignee service classes
'''


class AssignConsigData(dict):
    notification_id: int
    ucn_no: str
    consignee_id: str
    consignee_email: str
    consignee_name: str
    re_assign_flag: bool
    company: str

    def __init__(self, notification_id: int, ucn_no: str, consignee_id: str, consignee_email: str, consignee_name: str,
                 re_assign_flag: bool, company: str) -> None:
        self.notification_id = notification_id
        self.ucn_no = ucn_no
        self.consignee_id = consignee_id
        self.consignee_email = consignee_email
        self.consignee_name = consignee_name
        self.re_assign_flag = re_assign_flag
        self.company = company

        dict.__init__(self, notificationId=notification_id, ucnNo=ucn_no, consigneeId=consignee_id,
                      consigneeEmail=consignee_email, consigneeName=consignee_name, reAssignFlag=re_assign_flag,
                      company=company)


class AssignConsigPayload(dict):
    service: str
    apiname: str
    data: AssignConsigData

    def __init__(self, service: str, apiname: str, data: AssignConsigData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveConsigneeActions api classes
'''


class ConsigneeActions(dict):
    unique_mapping_id: str
    notification_id: int
    notification_action_list_id: int
    check_box_flag: bool

    def __init__(self, unique_mapping_id: str, notification_id: int, notification_action_list_id: int,
                 check_box_flag: bool) -> None:
        self.unique_mapping_id = unique_mapping_id
        self.notification_id = notification_id
        self.notification_action_list_id = notification_action_list_id
        self.check_box_flag = check_box_flag

        dict.__init__(self, uniqueMappingId=unique_mapping_id, notificationId=notification_id,
                      notificationActionListId=notification_action_list_id, checkBoxFlag=check_box_flag)


class SaveConsigneeActionsPayload(dict):
    service: str
    apiname: str
    data: List[ConsigneeActions]

    def __init__(self, service: str, apiname: str, data: List[ConsigneeActions]) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveBrfRecallInformation data entry class
'''


class ReturnProduct(dict):
    return_product_code: str
    return_product_lot: str
    return_quantity: int

    def __init__(self, return_product_code: str, return_product_lot: str, return_quantity: int) -> None:
        self.return_product_code = return_product_code
        self.return_product_lot = return_product_lot
        self.return_quantity = return_quantity

        dict.__init__(self, returnProductCode=return_product_code, returnProductLot=return_product_lot,
                      returnQuantity=return_quantity)


class SaveBRFServiceDataOld(dict):
    product_availability_flag: bool
    shipping_label_quantity: int
    notification_id: int
    sub_account_ucn: str
    return_product: List[ReturnProduct]
    unique_mapping_id: str

    def __init__(self, product_availability_flag: bool, shipping_label_quantity: int, notification_id: int,
                 sub_account_ucn: str, return_product: List[ReturnProduct], unique_mapping_id: str) -> None:
        self.product_availability_flag = product_availability_flag
        self.shipping_label_quantity = shipping_label_quantity
        self.notification_id = notification_id
        self.sub_account_ucn = sub_account_ucn
        self.return_product = return_product
        self.unique_mapping_id = unique_mapping_id

        dict.__init__(self, productAvailabilityFlag=product_availability_flag,
                      shippingLabelQuantity=shipping_label_quantity, notificationId=notification_id,
                      subAccountUCN=sub_account_ucn, returnProduct=return_product, uniqueMappingId=unique_mapping_id)


class SaveBRFServiceData(dict):
    product_availability_flag: bool
    notification_id: int
    sub_account_ucn: str
    unique_mapping_id: str
    return_product: List[ReturnProduct]
    deleted_product: List[ReturnProduct]
    deleted_attachments: List[Any]
    notification_account_mapping_id: int

    def __init__(self, product_availability_flag: bool, notification_id: int,
                 sub_account_ucn: str, unique_mapping_id: str, return_product: List[ReturnProduct],
                 deleted_product: List[ReturnProduct], deleted_attachments: List[Any],
                 notification_account_mapping_id: int) -> None:
        self.product_availability_flag = product_availability_flag
        self.notification_id = notification_id
        self.sub_account_ucn = sub_account_ucn
        self.unique_mapping_id = unique_mapping_id
        self.return_product = return_product
        self.deleted_product = deleted_product
        self.deleted_attachments = deleted_attachments
        self.notification_account_mapping_id = notification_account_mapping_id

        dict.__init__(self, productAvailabilityFlag=product_availability_flag,
                      notificationId=notification_id,
                      subAccountUCN=sub_account_ucn, uniqueMappingId=unique_mapping_id, returnProduct=return_product,
                      deletedProductData=deleted_product, deletedAttachmentData=deleted_attachments,
                      notificationAccountMappingId=notification_account_mapping_id)


class SaveBRFServiceDataReMwShp(dict):
    product_availability_flag: bool
    shipping_label_quantity: int
    notification_id: int
    sub_account_ucn: str
    unique_mapping_id: str
    return_product: List[ReturnProduct]
    deleted_product: List[ReturnProduct]
    deleted_attachments: List[Any]
    notification_account_mapping_id: int

    def __init__(self, product_availability_flag: bool, shipping_label_quantity: int, notification_id: int,
                 sub_account_ucn: str, unique_mapping_id: str, return_product: List[ReturnProduct],
                 deleted_product: List[ReturnProduct], deleted_attachments: List[Any],
                 notification_account_mapping_id: int) -> None:
        self.product_availability_flag = product_availability_flag
        self.shipping_label_quantity = shipping_label_quantity
        self.notification_id = notification_id
        self.sub_account_ucn = sub_account_ucn
        self.unique_mapping_id = unique_mapping_id
        self.return_product = return_product
        self.deleted_product = deleted_product
        self.deleted_attachments = deleted_attachments
        self.notification_account_mapping_id = notification_account_mapping_id

        dict.__init__(self, productAvailabilityFlag=product_availability_flag,
                      shippingLabelQuantity=shipping_label_quantity,
                      notificationId=notification_id,
                      subAccountUCN=sub_account_ucn, uniqueMappingId=unique_mapping_id, returnProduct=return_product,
                      deletedProductData=deleted_product, deletedAttachmentData=deleted_attachments,
                      notificationAccountMappingId=notification_account_mapping_id)


'''
save FAQ service classes
'''


class SaveFaqData(dict):
    question: str
    answer: str

    def __init__(self, question: str, answer: str) -> None:
        self.question = question
        self.answer = answer

        dict.__init__(self, question=question, answer=answer)


class SaveFaqService(dict):
    service: str
    apiname: str
    data: SaveFaqData

    def __init__(self, service: str, apiname: str, data: SaveFaqData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
generateAssigneeOtp service classes
'''


class GenerateAssigneeOtpData(dict):
    notification_assignee_id: int

    def __init__(self, notification_assignee_id: int) -> None:
        self.notification_assignee_id = notification_assignee_id

        dict.__init__(self, notificationAssigneeId=notification_assignee_id)


class GenerateAssigneeOtpService(dict):
    service: str
    apiname: str
    data: GenerateAssigneeOtpData

    def __init__(self, service: str, apiname: str, data: GenerateAssigneeOtpData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
acknowledgeNotificationAssignee service classes
'''


class AcknowledgeNotificationAssigneeData(dict):
    notification_assignee_id: int
    email: str
    otp: int
    admin_notification_id: str
    notification_name: str
    company: str

    def __init__(self, notification_assignee_id: int, email: str, otp: int, admin_notification_id: str,
                 notification_name: str, company: str) -> None:
        self.notification_assignee_id = notification_assignee_id
        self.email = email
        self.otp = otp
        self.admin_notification_id = admin_notification_id
        self.notification_name = notification_name
        self.company = company

        dict.__init__(self, notificationAssigneeId=notification_assignee_id, email=email, otp=otp,
                      adminNotificationId=admin_notification_id, notificationName=notification_name, company=company)


class AcknowledgeNotificationAssigneeService(dict):
    service: str
    apiname: str
    data: AcknowledgeNotificationAssigneeData

    def __init__(self, service: str, apiname: str, data: AcknowledgeNotificationAssigneeData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveInquiriesRequest service classes
'''


class SaveInquiriesRequestData(dict):
    inquiry_type: int
    admin_notification_id: int
    ucn_no: int
    comments: int
    creator_first_name: str
    creator_last_name: str
    created_by: str

    def __init__(self, inquiry_type: int, admin_notification_id: int, ucn_no: int, comments: int,
                 creator_first_name: str, creator_last_name: str, created_by: str) -> None:
        self.inquiry_type = inquiry_type
        self.admin_notification_id = admin_notification_id
        self.ucn_no = ucn_no
        self.comments = comments
        self.creator_first_name = creator_first_name
        self.creator_last_name = creator_last_name
        self.created_by = created_by

        dict.__init__(self, inquiryType=inquiry_type, adminNotificationId=admin_notification_id, ucnNo=ucn_no,
                      comments=comments, creatorFirstName=creator_first_name, creatorLastName=creator_last_name,
                      createdBy=created_by)


class SaveInquiriesRequestService(dict):
    service: str
    apiname: str
    data: SaveInquiriesRequestData

    def __init__(self, service: str, apiname: str, data: SaveInquiriesRequestData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveAssignedConsignee service classes
'''


class SaveAssignedConsigneeData(dict):
    notification_id: int
    ucn_no: str
    consignee_email: str
    consignee_name: str
    re_assign_flag: bool
    company: str
    admin_notification_id: str
    notification_name: str
    notification_type: str
    account_name: str

    def __init__(self, notification_id: int, ucn_no: str, consignee_email: str, consignee_name: str,
                 re_assign_flag: bool, company: str, admin_notification_id: str, notification_name: str,
                 notification_type: str, account_name: str) -> None:
        self.notification_id = notification_id
        self.ucn_no = ucn_no
        self.consignee_email = consignee_email
        self.consignee_name = consignee_name
        self.re_assign_flag = re_assign_flag
        self.company = company
        self.admin_notification_id = admin_notification_id
        self.notification_name = notification_name
        self.notification_type = notification_type
        self.account_name = account_name

        dict.__init__(self, notificationId=notification_id, ucnNo=ucn_no, consigneeEmail=consignee_email,
                      consigneeName=consignee_name, reAssignFlag=re_assign_flag, company=company,
                      adminNotificationId=admin_notification_id, notificationName=notification_name,
                      notificationType=notification_type, accountName=account_name)


class SaveAssignedConsigneeService(dict):
    service: str
    apiname: str
    data: SaveAssignedConsigneeData

    def __init__(self, service: str, apiname: str, data: SaveAssignedConsigneeData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
savePrfData service classes
'''


class SavePrfDataData(dict):
    unique_mapping_id: str
    product_availability_flag: bool
    notification_id: int
    notification_account_mapping_id: int
    sub_account_ucn: str

    def __init__(self, unique_mapping_id: str, product_availability_flag: bool, notification_id: int,
                 notification_account_mapping_id: int, sub_account_ucn: str) -> None:
        self.unique_mapping_id = unique_mapping_id
        self.product_availability_flag = product_availability_flag
        self.notification_id = notification_id
        self.notification_account_mapping_id = notification_account_mapping_id
        self.sub_account_ucn = sub_account_ucn

        dict.__init__(self, uniqueMappingId=unique_mapping_id, productAvailabilityFlag=product_availability_flag,
                      notificationId=notification_id, notificationAccountMappingId=notification_account_mapping_id,
                      subAccountUCN=sub_account_ucn)


class SavePrfDataDataService(dict):
    service: str
    apiname: str
    data: SavePrfDataData

    def __init__(self, service: str, apiname: str, data: SavePrfDataData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
savePrfAttachments service data
'''


class SavePrfAttachmentsData(dict):
    id: int
    unique_mapping_id: str
    product_availability_flag: bool
    notification_id: int
    notification_account_mapping_id: int
    sub_account_ucn: str
    deleted_attachment_data: List[Any]

    def __init__(self, id: int, unique_mapping_id: str, product_availability_flag: bool, notification_id: int,
                 notification_account_mapping_id: int, sub_account_ucn: str,
                 deleted_attachment_data: List[Any]) -> None:
        self.id = id
        self.unique_mapping_id = unique_mapping_id
        self.product_availability_flag = product_availability_flag
        self.notification_id = notification_id
        self.notification_account_mapping_id = notification_account_mapping_id
        self.sub_account_ucn = sub_account_ucn
        self.deleted_attachment_data = deleted_attachment_data

        dict.__init__(self, id=id, uniqueMappingId=unique_mapping_id, productAvailabilityFlag=product_availability_flag,
                      notificationId=notification_id, notificationAccountMappingId=notification_account_mapping_id,
                      subAccountUCN=sub_account_ucn, deletedAttachmentData=deleted_attachment_data)


'''
savePrfProducts service classes
'''


class PrfReturnProduct(dict):
    return_product_code: str
    return_product_lot: str
    return_quantity: int

    def __init__(self, return_product_code: str, return_product_lot: str, return_quantity: int) -> None:
        self.return_product_code = return_product_code
        self.return_product_lot = return_product_lot
        self.return_quantity = return_quantity

        dict.__init__(self, returnProductCode=return_product_code, returnProductLot=return_product_lot,
                      returnQuantity=return_quantity)


class SavePrfProductsData(dict):
    brf_recall_id: int
    notification_id: int
    shipping_label_quantity: int
    deleted_product_data: List[Any]
    unique_mapping_id: str
    notification_account_mapping_id: int
    sub_account_ucn: str
    return_product: List[PrfReturnProduct]

    def __init__(self, brf_recall_id: int, notification_id: int, shipping_label_quantity: int,
                 deleted_product_data: List[Any], unique_mapping_id: str, notification_account_mapping_id: int,
                 sub_account_ucn: str, return_product: List[PrfReturnProduct]) -> None:
        self.brf_recall_id = brf_recall_id
        self.notification_id = notification_id
        self.shipping_label_quantity = shipping_label_quantity
        self.deleted_product_data = deleted_product_data
        self.unique_mapping_id = unique_mapping_id
        self.notification_account_mapping_id = notification_account_mapping_id
        self.sub_account_ucn = sub_account_ucn
        self.return_product = return_product

        dict.__init__(self, brfRecallId=brf_recall_id, notificationId=notification_id,
                      shippingLabelQuantity=shipping_label_quantity, deletedProductData=deleted_product_data,
                      uniqueMappingId=unique_mapping_id,
                      notificationAccountMappingId=notification_account_mapping_id, subAccountUCN=sub_account_ucn,
                      returnProduct=return_product)


class SavePrfProductsService(dict):
    service: str
    apiname: str
    data: SavePrfProductsData

    def __init__(self, service: str, apiname: str, data: SavePrfProductsData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
updateAccountNotificationMapping service classes
'''


class UpdateAccountNotificationMappingData(dict):
    notification_id: int
    sub_account_ucn: str
    admin_notification_id: str
    notification_name: str
    notification_type: str
    completed_by: str
    completed_by_email: str
    account_name: str
    company: str

    def __init__(self, notification_id: int, sub_account_ucn: str, admin_notification_id: str, notification_name: str,
                 notification_type: str, completed_by: str, completed_by_email: str, account_name: str,
                 company: str) -> None:
        self.notification_id = notification_id
        self.sub_account_ucn = sub_account_ucn
        self.admin_notification_id = admin_notification_id
        self.notification_name = notification_name
        self.notification_type = notification_type
        self.completed_by = completed_by
        self.completed_by_email = completed_by_email
        self.account_name = account_name
        self.company = company

        dict.__init__(self, notificationId=notification_id, subAccountUCN=sub_account_ucn,
                      adminNotificationId=admin_notification_id, notificationName=notification_name,
                      notificationType=notification_type, completedBy=completed_by, completedByEmail=completed_by_email,
                      accountName=account_name, company=company)


class UpdateAccountNotificationMappingService(dict):
    service: str
    apiname: str
    data: UpdateAccountNotificationMappingData

    def __init__(self, service: str, apiname: str, data: UpdateAccountNotificationMappingData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
Company Signature data classes
'''


class EntityMap(dict):
    pass

    def __init__(self, ) -> None:
        dict.__init__(self, )
        pass


class CompanySignatureJsonBlock(dict):
    key: str
    text: str
    type: str
    depth: int
    inline_style_ranges: List[Any]
    entity_ranges: List[Any]
    data: EntityMap

    def __init__(self, key: str, text: str, type: str, depth: int, inline_style_ranges: List[Any],
                 entity_ranges: List[Any], data: EntityMap) -> None:
        self.key = key
        self.text = text
        self.type = type
        self.depth = depth
        self.inline_style_ranges = inline_style_ranges
        self.entity_ranges = entity_ranges
        self.data = data

        dict.__init__(self, key=key, text=text, type=type, depth=depth, inlineStyleRanges=inline_style_ranges,
                      entityRanges=entity_ranges, data=data)


class CompanySignatureJson(dict):
    blocks: List[CompanySignatureJsonBlock]
    entity_map: EntityMap

    def __init__(self, blocks: List[CompanySignatureJsonBlock], entity_map: EntityMap) -> None:
        self.blocks = blocks
        self.entity_map = entity_map

        dict.__init__(self, blocks=blocks, entityMap=entity_map)


class CompanySignatureHtmlJsonData(dict):
    html_data: str
    json_data: str

    def __init__(self, html_data: str, json_data: str) -> None:
        self.html_data = html_data
        self.json_data = json_data

        dict.__init__(self, htmlData=html_data, jsonData=json_data)


'''
fetch guidance documents service classes
'''


class FetchGuidanceFilesData(dict):
    notification_id: str
    attachment_type: str

    def __init__(self, notification_id: str, attachment_type: str) -> None:
        self.notification_id = notification_id
        self.attachment_type = attachment_type

        dict.__init__(self, notificationId=notification_id, attachmentType=attachment_type)


class FetchGuidanceFilesService(dict):
    service: str
    apiname: str
    data: FetchGuidanceFilesData

    def __init__(self, service: str, apiname: str, data: FetchGuidanceFilesData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
Delete Guidance Document service classes
'''


class DeleteGuidanceDocumentData(dict):
    file_name: str
    notification_id: str
    attachment_type: str

    def __init__(self, file_name: str, notification_id: str, attachment_type: str) -> None:
        self.file_name = file_name
        self.notification_id = notification_id
        self.attachment_type = attachment_type

        dict.__init__(self, fileName=file_name, notificationId=notification_id, attachmentType=attachment_type)


class DeleteGuidanceDocumentService(dict):
    service: str
    apiname: str
    data: DeleteGuidanceDocumentData

    def __init__(self, service: str, apiname: str, data: DeleteGuidanceDocumentData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
FetchConsigneesByServiceRequest service classes
'''


class FetchConsigneesByServiceRequestData(dict):
    filter: str
    consignee_email: str

    def __init__(self, filter: str, consignee_email: str) -> None:
        self.filter = filter
        self.consignee_email = consignee_email

        dict.__init__(self, filter=filter, consigneeEmail=consignee_email)


class FetchConsigneesByServiceRequestService(dict):
    service: str
    apiname: str
    data: FetchConsigneesByServiceRequestData

    def __init__(self, service: str, apiname: str, data: FetchConsigneesByServiceRequestData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
FetchAccountList based on consignee email service classes
'''


class FetchAccountListData(dict):
    consignee_email: str

    def __init__(self, consignee_email: str) -> None:
        self.consignee_email = consignee_email

        dict.__init__(self, consigneeEmail=consignee_email)


class FetchAccountListService(dict):
    service: str
    apiname: str
    page: int
    size: int
    filter: str
    service_request: bool
    data: FetchAccountListData

    def __init__(self, service: str, apiname: str, page: int, size: int, filter: str, service_request: bool,
                 data: FetchAccountListData) -> None:
        self.service = service
        self.apiname = apiname
        self.page = page
        self.size = size
        self.filter = filter
        self.service_request = service_request
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, page=page, size=size, filter=filter,
                      serviceRequest=service_request, data=data)


'''
saveContactServiceRequest service classes
'''


class SaveContactServiceRequestAccount(dict):
    ucn_no: str
    account_name: str

    def __init__(self, ucn_no: str, account_name: str) -> None:
        self.ucn_no = ucn_no
        self.account_name = account_name

        dict.__init__(self, ucnNo=ucn_no, accountName=account_name)


class SaveContactServiceRequestData(dict):
    request_type: int
    status: int
    consignee_name: str
    consignee_email: str
    accounts: List[Any]
    creator_first_name: str
    creator_last_name: str
    created_by: str
    comments: str

    def __init__(self, request_type: int, status: int, consignee_name: str, consignee_email: str, accounts: List[Any],
                 creator_first_name: str, creator_last_name: str, created_by: str, comments: str) -> None:
        self.request_type = request_type
        self.status = status
        self.consignee_name = consignee_name
        self.consignee_email = consignee_email
        self.accounts = accounts
        self.creator_first_name = creator_first_name
        self.creator_last_name = creator_last_name
        self.created_by = created_by
        self.comments = comments

        dict.__init__(self, requestType=request_type, status=status, consigneeName=consignee_name,
                      consigneeEmail=consignee_email, accounts=accounts, creatorFirstName=creator_first_name,
                      creatorLastName=creator_last_name, createdBy=created_by, comments=comments)


class SaveContactServiceRequestService(dict):
    service: str
    apiname: str
    data: SaveContactServiceRequestData

    def __init__(self, service: str, apiname: str, data: SaveContactServiceRequestData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
FetchConsigneeSubAccountMappingDetails service classes
'''


class FetchConsigneeSubAccountMappingDetailsData(dict):
    filter: str
    page: int
    size: int
    sort_by: str
    sort_type: str

    def __init__(self, filter: str, page: int, size: int, sort_by: str, sort_type: str) -> None:
        self.filter = filter
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_type = sort_type

        dict.__init__(self, filter=filter, page=page, size=size, sortBy=sort_by, sortType=sort_type)


class FetchConsigneeSubAccountMappingDetailsService(dict):
    service: str
    apiname: str
    data: FetchConsigneeSubAccountMappingDetailsData

    def __init__(self, service: str, apiname: str, data: FetchConsigneeSubAccountMappingDetailsData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
FetchServiceRequest service classes
'''


class FetchServiceRequestData(dict):
    request_type: int
    status: List[int]
    filter: str
    size: int
    page: int

    def __init__(self, request_type: int, status: List[int], filter: str, size: int, page: int) -> None:
        self.request_type = request_type
        self.status = status
        self.filter = filter
        self.size = size
        self.page = page

        dict.__init__(self, requestType=request_type, status=status, filter=filter, size=size, page=page)


class FetchServiceRequestService(dict):
    service: str
    apiname: str
    data: FetchServiceRequestData

    def __init__(self, service: str, apiname: str, data: FetchServiceRequestData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
updateContactServiceRequest service classes
'''


class UpdateContactServiceRequestAccount(dict):
    ucn_no: str
    account_name: str

    def __init__(self, ucn_no: str, account_name: str) -> None:
        self.ucn_no = ucn_no
        self.account_name = account_name

        dict.__init__(self, ucnNo=ucn_no, accountName=account_name)


class UpdateContactServiceRequestData(dict):
    service_request_number: str
    status: int
    denial_reason: str
    completed_by_first_name: str
    completed_by_last_name: str
    completed_by: str
    request_type: int
    consignee_name: str
    consignee_email: str
    creator_first_name: str
    creator_last_name: str
    created_by: str
    accounts: List[Any]

    def __init__(self, service_request_number: str, status: int, denial_reason: str, completed_by_first_name: str,
                 completed_by_last_name: str, completed_by: str, request_type: int, consignee_name: str,
                 consignee_email: str, creator_first_name: str, creator_last_name: str, created_by: str,
                 accounts: List[Any]) -> None:
        self.service_request_number = service_request_number
        self.status = status
        self.denial_reason = denial_reason
        self.completed_by_first_name = completed_by_first_name
        self.completed_by_last_name = completed_by_last_name
        self.completed_by = completed_by
        self.request_type = request_type
        self.consignee_name = consignee_name
        self.consignee_email = consignee_email
        self.creator_first_name = creator_first_name
        self.creator_last_name = creator_last_name
        self.created_by = created_by
        self.accounts = accounts

        dict.__init__(self, serviceRequestNumber=service_request_number, status=status, denialReason=denial_reason,
                      completedByFirstName=completed_by_first_name, completedByLastName=completed_by_last_name,
                      completedBy=completed_by, requestType=request_type, consigneeName=consignee_name,
                      consigneeEmail=consignee_email, creatorFirstName=creator_first_name,
                      creatorLastName=creator_last_name, createdBy=created_by, accounts=accounts)


class UpdateContactServiceRequestService(dict):
    service: str
    apiname: str
    data: UpdateContactServiceRequestData

    def __init__(self, service: str, apiname: str, data: UpdateContactServiceRequestData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
saveReopenServiceRequest service classes
'''


class SaveReopenServiceRequestData(dict):
    request_type: int
    status: int
    notification_id: int
    admin_notification_id: str
    notification_name: str
    ucn_no: str
    account_name: str
    company: str
    reopen_reason: str
    creator_last_name: str
    creator_first_name: str
    created_by: str

    def __init__(self, request_type: int, status: int, notification_id: int, admin_notification_id: str,
                 notification_name: str, ucn_no: str, account_name: str, company: str, reopen_reason: str,
                 creator_last_name: str, creator_first_name: str, created_by: str) -> None:
        self.request_type = request_type
        self.status = status
        self.notification_id = notification_id
        self.admin_notification_id = admin_notification_id
        self.notification_name = notification_name
        self.ucn_no = ucn_no
        self.account_name = account_name
        self.company = company
        self.reopen_reason = reopen_reason
        self.creator_last_name = creator_last_name
        self.creator_first_name = creator_first_name
        self.created_by = created_by

        dict.__init__(self, requestType=request_type, status=status, notificationId=notification_id,
                      adminNotificationId=admin_notification_id, notificationName=notification_name, ucnNo=ucn_no,
                      accountName=account_name, company=company, reopenReason=reopen_reason,
                      creatorLastName=creator_last_name, creatorFirstName=creator_first_name, createdBy=created_by)


class SaveReopenServiceRequestService(dict):
    service: str
    apiname: str
    data: SaveReopenServiceRequestData

    def __init__(self, service: str, apiname: str, data: SaveReopenServiceRequestData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchActionSet service classes
'''


class FetchActionSetData(dict):
    type: int

    def __init__(self, type: int) -> None:
        self.type = type

        dict.__init__(self, type=type)


class FetchActionSetService(dict):
    service: str
    apiname: str
    data: FetchActionSetData

    def __init__(self, service: str, apiname: str, data: FetchActionSetData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchNotification service classes
'''


class FetchNotificationData(dict):
    id: int
    send_complete_data: bool

    def __init__(self, id: int, send_complete_data: bool) -> None:
        self.id = id
        self.send_complete_data = send_complete_data

        dict.__init__(self, id=id, sendCompleteData=send_complete_data)


class FetchNotificationService(dict):
    service: str
    apiname: str
    data: FetchNotificationData

    def __init__(self, service: str, apiname: str, data: FetchNotificationData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchAccountNotificationMapping service classes
'''


class FetchAccountNotificationMappingData(dict):
    notification_id: int

    def __init__(self, notification_id: int) -> None:
        self.notification_id = notification_id

        dict.__init__(self, notificationId=notification_id)


class FetchAccountNotificationMappingService(dict):
    service: str
    apiname: str
    data: FetchAccountNotificationMappingData

    def __init__(self, service: str, apiname: str, data: FetchAccountNotificationMappingData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchConsigneeDetails service classes
'''


class FetchConsigneeDetailsData(dict):
    sub_account_ucn: str

    def __init__(self, sub_account_ucn: str) -> None:
        self.sub_account_ucn = sub_account_ucn

        dict.__init__(self, subAccountUCN=sub_account_ucn)


class FetchConsigneeDetailsService(dict):
    service: str
    apiname: str
    data: FetchConsigneeDetailsData

    def __init__(self, service: str, apiname: str, data: FetchConsigneeDetailsData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchActionsRequired service classes
'''


class FetchActionsRequiredData(dict):
    notification_id: int
    page: str
    size: str

    def __init__(self, notification_id: int, page: str, size: str) -> None:
        self.notification_id = notification_id
        self.page = page
        self.size = size

        dict.__init__(self, notificationId=notification_id, page=page, size=size)


class FetchActionsRequiredService(dict):
    service: str
    apiname: str
    data: FetchActionsRequiredData

    def __init__(self, service: str, apiname: str, data: FetchActionsRequiredData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchNotificationAssignees service classes
'''


class FetchNotificationAssigneesData(dict):
    notification_id: int
    search: str

    def __init__(self, notification_id: int, search: str) -> None:
        self.notification_id = notification_id
        self.search = search

        dict.__init__(self, notificationId=notification_id, search=search)


class FetchNotificationAssigneesService(dict):
    service: str
    apiname: str
    data: FetchNotificationAssigneesData

    def __init__(self, service: str, apiname: str, data: FetchNotificationAssigneesData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


'''
fetchBrfRecallInformation service classes
'''


class FetchBrfRecallInformationData(dict):
    notification_id: int
    unique_mapping_id: str

    def __init__(self, notification_id: int, unique_mapping_id: str) -> None:
        self.notification_id = notification_id
        self.unique_mapping_id = unique_mapping_id

        dict.__init__(self, notificationId=notification_id, uniqueMappingId=unique_mapping_id)


class FetchBrfRecallInformationService(dict):
    service: str
    apiname: str
    data: FetchBrfRecallInformationData

    def __init__(self, service: str, apiname: str, data: FetchBrfRecallInformationData) -> None:
        self.service = service
        self.apiname = apiname
        self.data = data

        dict.__init__(self, service=service, apiname=apiname, data=data)


''' 
Subject Products Data input to create notification service
'''


class SPData(dict):
    product_code: str
    product_name: str
    serial_number: str
    gtin_number: str
    description: str
    expiry_date: str
    distribution_start_date: str
    distribution_end_date: str
    active_flag: bool

    def __init__(self, product_code: str, product_name: str, serial_number: str, gtin_number: str, description: str,
                 expiry_date: str, distribution_start_date: str, distribution_end_date: str, active_flag: bool) -> None:
        self.product_code = product_code
        self.product_name = product_name
        self.serial_number = serial_number
        self.gtin_number = gtin_number
        self.description = description
        self.expiry_date = expiry_date
        self.distribution_start_date = distribution_start_date
        self.distribution_end_date = distribution_end_date
        self.active_flag = active_flag

        dict.__init__(self, productCode=product_code, productName=product_name, serialNumber=serial_number,
                      gtinNumber=gtin_number, description=description, expiryDate=expiry_date,
                      distributionStartDate=distribution_start_date, distributionEndDate=distribution_end_date,
                      activeFlag=active_flag)


class SubjectProductsInputToCreateNotification(dict):
    deleted_data: List[Any]
    data: List[SPData]
    audit_subject_products_required: bool

    def __init__(self, deleted_data: List[Any], data: List[SPData], audit_subject_products_required: bool) -> None:
        self.deleted_data = deleted_data
        self.data = data
        self.audit_subject_products_required = audit_subject_products_required

        dict.__init__(self, deletedData=deleted_data, data=data,
                      auditSubjectProductsRequired=audit_subject_products_required)


class AColors(Enum):
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"
