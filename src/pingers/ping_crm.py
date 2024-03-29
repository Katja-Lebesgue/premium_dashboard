from src.utils import *


def ping_crm():
    crm = read_csv_from_s3(bucket="lebesgue-crm", path="crm_dataset_dev.csv", add_global_folder=False)
    crm.shop_id = crm.shop_id.astype(int)
    crm.industry.fillna("unknown", inplace=True)
    return crm
