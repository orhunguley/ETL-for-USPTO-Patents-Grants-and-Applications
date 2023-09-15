from elasticsearch import Elasticsearch
import yaml
from extract_data import extract_data_from_xml, transform_data_to_patent
from dataclasses import asdict
from tqdm import tqdm
from parse import parse_args

with open('credentials.yaml', 'r') as file:
    creds = yaml.safe_load(file)

USER = creds["username"]
PASSWORD = creds["password"]

# pattern_mapper = {
#     "grant": "us-patent-grant",
#     "application": "us-patent-application"
# }

# path_mapper = {
#     "grant": "grant_data_path",
#     "application": "application_data_path"
# }


def create_index(config):
    """
    Creates an Elasticsearch index with the specified configuration.

    Args:
        config (dict): A dictionary containing Elasticsearch configuration options, including:
            - es_host (str): The Elasticsearch host URL.
            - es_index (str): The name of the index to be created.

    Returns:
        None

    Example:
        config = {
            "es_host": "https://localhost:9200",
            "es_index": "patent_data"
        }
        create_index(config)
        
    """
    es = Elasticsearch(config["es_host"],
                       basic_auth=(USER, PASSWORD),
                       verify_certs=False)

    # Data mapping for the patent
    mapping = {
        "mappings": {
            "properties": {
                "pub_doc_id": {
                    "type": "text"
                },
                "app_doc_id": {
                    "type": "text"
                },
                "patent_type": {
                    "type": "text"
                },
                "abstract": {
                    "type": "text"
                },
                "date_produced": {
                    "type": "date"
                },
                "date_published": {
                    "type": "date"
                },
                "date_applied": {
                    "type": "date"
                },
                "ipcr_list": {
                    "type": "object"
                },
                "cpc_list": {
                    "type": "object"
                },
                "inventors": {
                    "type": "object"
                },
                "assignees": {
                    "type": "object"
                }
            }
        }
    }

    es.options(ignore_status=[400]).indices.create(index=config["es_index"],
                                                   mappings=mapping)


def upload_document_to_es(config, document):
    """
    Uploads a patent document to an Elasticsearch index with optional overwrite behavior.

    This function is designed to upload patent documents to an Elasticsearch index, considering the document type.
    It can either add a new document or overwrite an existing one based on the document type. Patent applications 
    cannot overwrite grants, but grants can overwrite applications.


    Args:
        config (dict): A dictionary containing Elasticsearch configuration options, including:
            - es_host (str): The Elasticsearch host URL.
            - es_index (str): The name of the index where the document will be uploaded.
        document (dict): A dictionary representing the patent document to be uploaded. It should include fields
            like "app_doc_id" and "patent_type" to determine whether to overwrite or add a new document.

    Returns:
        None

    Example:
        config = {
            "es_host": "https://localhost:9200",
            "es_index": "patent_data"
        }
        document = {
            "app_doc_id": "12345",
            "patent_type": "us-patent-grant",
            # ... (other document fields)
        }
        upload_document_to_es(config, document)

    Notes:
        - If the document's "patent_type" is "us-patent-grant," it will add or overwrite a any document.
        - If the document's "patent_type" is "us-patent-application," it will add can only 
        overwrite an application document.
    """
    es = Elasticsearch(config["es_host"],
                       basic_auth=(USER, PASSWORD),
                       verify_certs=False)

    doc_id = document["app_doc_id"]
    doc_patent_type = document["patent_type"]

    # Upload new / Overwride existed grant
    if doc_patent_type == "us-patent-grant":
        es.index(index=config["es_index"], document=document, id=doc_id)
    else:

        response = es.options(ignore_status=[404]).get(
            index=config["es_index"], id=doc_id)
        is_overwrite = False

        if response["found"]:
            response_patent_type = response["_source"]["patent_type"]
            is_overwrite = response_patent_type == "us-patent-application"

        # Upload new / Overwride existed application
        # This prevents an application cannot overwrite a grant
        if is_overwrite or (not response["found"]):
            es.index(index=config["es_index"], document=document, id=doc_id)


def ingest_data_to_es(config, xml_us_patents):

    for xml_patent in tqdm(xml_us_patents):
        patent = transform_data_to_patent(xml_patent=xml_patent,
                                          patent_type=config["patent_type"])
        upload_document_to_es(config=config, document=asdict(patent))


def main(args):

    print("Loading config...")

    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    config["patent_type"] = args.patent_type
    patent_type = config["patent_type"]

    print("Printing config...")
    print(config)

    print("Creating the index for Elasticsearch")

    create_index(config=config)

    print("Extracting data from XML doc.")

    fp_key = f"{patent_type}_data_path"
    xml_us_patents = extract_data_from_xml(file_path=config[fp_key],
                                           patent_type=patent_type)

    ingest_data_to_es(config=config, xml_us_patents=xml_us_patents)


if __name__ == '__main__':

    args = parse_args()
    main(args)
