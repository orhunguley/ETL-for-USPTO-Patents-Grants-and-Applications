import xmltodict
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
from datamodels import USPatent
from datetime import datetime
import time


def format_xml(xml_data):
    """
    Formats an XML document by removing XML and DOCTYPE declarations, adding a <root> tag at the beginning,
    and a </root> tag at the end, while preserving the structure of the document.
    
    Args:
        xml_data (str): The XML document to be formatted.
        
    Returns:
        str: The formatted XML document.
    """
    # Remove <?xml ...> and <!DOCTYPE ...> declarations
    xml_data = re.sub(r'<\?xml[^>]*\?>', '', xml_data)
    xml_data = re.sub(r'<!DOCTYPE[^>]*>', '', xml_data)

    # Add <root> tag at the beginning of the document
    xml_data = '<root>\n' + xml_data

    # Add </root> tag at the end of the document
    xml_data = xml_data.strip() + '\n</root>'

    # Remove extra spaces
    # xml_data = re.sub(r' +', ' ', xml_data)  # Replace consecutive spaces with a single space
    xml_data = re.sub(r'\n+', '\n',
                      xml_data)  # Remove leading spaces on each line

    return xml_data


import re


def split_xml_into_grants(xml_string, patent_type="grant"):
    """
    Splits an XML string into pieces, each starting with "<us-patent-grant"
    and ending with "</us-patent-grant>".

    Args:
        xml_string (str): The XML string to be split.

    Returns:
        list of str: A list of strings, each containing the content within a
        <us-patent-grant> tag.

    """
    # Define the regular expression pattern to find <us-patent-grant> tags
    pattern = fr'<us-patent-{patent_type}.*?</us-patent-{patent_type}>'

    # Use re.findall to find all matching patterns in the XML string
    pieces = re.findall(pattern, xml_string, re.DOTALL)

    return pieces


def get_abstract(patent):
    """
    Extracts the abstract from a patent XML element.

    Args:
        patent (BeautifulSoup): The BeautifulSoup object representing a patent.

    Returns:
        str: The patent's abstract as a string, or an empty string if not found.
    """
    abstract = patent.find("abstract")
    if abstract:
        abstract = abstract.find('p', {'id': 'p-0001'})
        abstract = [str(a) for a in abstract.contents]
        abstract = "".join(abstract)
    else:
        abstract = ""
    return abstract


def get_classifications(bib_data):
    """
    Extracts classification information (IPCR and CPC) from bibliographic data.

    Args:
        bib_data (BeautifulSoup): The BeautifulSoup object representing bibliographic data.

    Returns:
        dict: A dictionary containing IPCR and CPC classification information.
    """

    ipcr_list = bib_data.find("classifications-ipcr")
    if ipcr_list:
        ipcr_list = [
            xmltodict.parse(str(a)) for a in ipcr_list.contents if a != '\n'
        ]
    else:
        ipcr_list = []

    cpc_list = bib_data.find("classifications-cpc")
    if cpc_list:
        cpc_list = [
            xmltodict.parse(str(a)) for a in cpc_list.contents if a != '\n'
        ]
    else:
        cpc_list = []

    classes = dict(ipcr_list=ipcr_list, cpc_list=cpc_list)
    return classes


def get_inventors(bib_data):
    """
    Extracts inventor information from bibliographic data.

    Args:
        bib_data (BeautifulSoup): The BeautifulSoup object representing bibliographic data.

    Returns:
        dict: A dictionary containing inventor information.
    """

    inventors = bib_data.find("us-parties").find("inventors").find_all(
        "inventor")
    inventors = [xmltodict.parse(str(i)) for i in inventors]
    return dict(inventors=inventors)


def get_assignees(bib_data):
    """
    Extracts assignee information from bibliographic data.

    Args:
        bib_data (BeautifulSoup): The BeautifulSoup object representing bibliographic data.

    Returns:
        dict: A dictionary containing assignee information.
    """

    assignees = bib_data.find("assignees")
    if assignees:
        assignees = [
            xmltodict.parse(str(a)) for a in assignees.contents if a != '\n'
        ]
    else:
        assignees = []
    return dict(assignees=assignees)


def get_bib_data(patent, patent_type="grant"):
    """
    Extracts bibliographic data from a patent element.

    Args:
        patent (BeautifulSoup): The BeautifulSoup object representing a patent.
        patent_type (str): The type of patent data (e.g., "grant" or "application").

    Returns:
        dict: A dictionary containing bibliographic information for the patent.
    """

    bib_data = patent.find(f"us-bibliographic-data-{patent_type}",
                           recursive=False)
    pub_doc_id = bib_data.find("publication-reference").find(
        "doc-number").contents[0]
    app_doc_id = bib_data.find("application-reference").find(
        "doc-number").contents[0]

    date_applied = bib_data.find("application-reference").find(
        "date").contents[0]
    date_applied = datetime.strptime(date_applied, '%Y%m%d').date()

    invention_title = bib_data.find("invention-title").contents[0]

    bib_dict = dict(pub_doc_id=pub_doc_id,
                    app_doc_id=app_doc_id,
                    date_applied=date_applied,
                    invention_title=invention_title)

    bib_dict.update(get_classifications(bib_data))
    bib_dict.update(get_inventors(bib_data))
    bib_dict.update(get_assignees(bib_data))

    return bib_dict


def get_document_basics(patent):
    """
    Extracts basic document information from a patent element.

    Args:
        patent (BeautifulSoup): The BeautifulSoup object representing a patent.

    Returns:
        dict: A dictionary containing basic document information.
    """
    patent_type = patent.get("id")
    # date_produced = patent.get("date-produced")
    date_produced = datetime.strptime(patent.get("date-produced"),
                                      '%Y%m%d').date()
    # date_published = patent.get("date-publ")
    date_published = datetime.strptime(patent.get("date-publ"),
                                       '%Y%m%d').date()
    basics = dict(patent_type=patent_type,
                  date_produced=date_produced,
                  date_published=date_published)

    return basics


def transform_data_to_patent(xml_patent, patent_type="grant"):
    """
    Transforms XML data representing a patent into a USPatent object.

    Args:
        xml_patent (str): The XML data string representing a patent.

    Returns:
        USPatent: An instance of the USPatent dataclass representing the patent.

    Example:
        xml_data = '<us-patent-grant>...</us-patent-grant>'
        patent = transform_data_to_patent(xml_data)
        print(patent.abstract)  # Access the abstract of the patent.
    """
    xml_patent = BeautifulSoup(xml_patent, "xml")
    xml_patent = xml_patent.find(f"us-patent-{patent_type}", recursive=False)

    result_dict = {}
    result_dict.update(get_document_basics(xml_patent))
    result_dict.update(get_bib_data(xml_patent, patent_type))
    result_dict["abstract"] = get_abstract(xml_patent)

    return USPatent(**result_dict)


def extract_data_from_xml(file_path, patent_type="grant"):
    """
    Extracts US patent information from XML documents.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        List: A list of extracted patent data.

    Example:
        file_path = 'patents.xml'
        patents = extract_data_from_xml(file_path)
        for patent in patents:
            print(patent.title)  # Access the title of each patent.
    """

    print("Reading file")
    start = time.time()

    with open(file_path, 'r') as f:
        xml_us_patents = f.read()

    print(f"Reading file completed. Elapsed time: {time.time()-start} seconds")

    print("Formatting xml")
    start = time.time()
    xml_us_patents = format_xml(xml_us_patents)

    print(
        f"Formatting is completed. Elapsed time: {time.time()-start} seconds")

    print("Getting patents")
    start = time.time()
    # xml_us_patents = xml_us_patents.find_all('us-patent-grant', recursive=False)
    xml_us_patents = split_xml_into_grants(xml_us_patents,
                                           patent_type=patent_type)
    print(
        f"Getting patents are completed. Elapsed time: {time.time()-start} seconds"
    )

    return xml_us_patents
