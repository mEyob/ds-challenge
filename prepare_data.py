import boto3
from zipfile import ZipFile

BUCKET_NAME = "fairmarkit-hiring-challenges"
OBJECT_NAME = "California Purchases.zip"

def download_from_s3(download_path, bucket_name=BUCKET_NAME, object_name=OBJECT_NAME):
    """Utility function for downloading data from S3

    Args:
        download_path (string): The file/path to save the data to
        bucket_name (string, optional): S3 bucket name. Defaults to BUCKET_NAME.
        object_name (string, optional): S3 object name. Defaults to OBJECT_NAME.
    """
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_name, download_path)

def unzip_data(zip_file, unzip_loc):
    """Unzip a file...

    Args:
        zip_file (string): filename/path to be unzipped
        unzip_loc (string): path to unzip to
    """
    with ZipFile(zip_file) as zip:
        zip.printdir()
        zip.extractall(unzip_loc)

def to_float(number):
    """Converts a dollar formatted data into float

    Args:
        number (string): [value to be converted]

    Returns:
        float: converted value
    """
    try:
        converted = float(number.replace("$", ""))
    except:
        converted = number
    return converted

