# ETL for USPTO Patent Grants & Applications
This is an ETL script for for USPTO Patent Grants & Applications. Script starts with reading the ```xml``` file specified in the ```config.yaml```. It then extracts the relevant information and uploads the data to Elasticsearch.

Run:
```python data_ingestion --patent-type grant```

Patent type can be either ```grant``` or ```application```

#### Data Model

The proposed data model have the following scheme.

``` python
class USPatent:
    date_produced: datetime.date = field(default=None)
    date_published: datetime.date = field(default=None)
    date_applied: datetime.date = field(default=None)
    ipcr_list: Optional[List[Dict]] = field(default=None)
    cpc_list: Optional[List[Dict]] = field(default=None)
    pub_doc_id: str = field(default=None)
    app_doc_id: str = field(default=None)
    patent_type: str = field(default=None)
    invention_title: str = field(default=None)
    inventors: Optional[List[Dict]] = field(default=None)
    assignees: Optional[List[Dict]] = field(default=None)
    abstract: str = field(default=None)
```

#### Dataset
I constructed two different xml files in the ```data/``` folder, with the names ```sample_patent_grants.xml``` and ```sample_patent_applications.xml```. The grants dataset has 208 files and applicaiton dataset has 207 files. 7 of those are included in both of the files because the those applications are granted. The ingestion script handles this and when we run ```data_ingestion.py``` files with the ```--patent-type grant``` and ```--patent-type application``` flags (order of run does not matter), it takes care of it.

#### Visualising Documents
Go to [Kibana](http://localhost:5601/app/dev_tools#/console) interface by entering (http://localhost:5601/app/dev_tools#/console), this link will direct you into the console.

You can make the following queries:

1) Search all documents. You are expected to see 207 + 208 - 7 = 415 documents

```
GET patents-00001/_search/
{
    "query": {
        "match_all": {}
    }
}
```
2) Search applications. If you did not run the script for grants, you are expected to see 207 documents. If grants are already run, it will be 199 because 8 of those applications are granted.
```
GET patents-00001/_search
{
  "query": {
    "term": {
      "patent_type": "application"
    }
  }
}
```

1) Search grants. You are expected to see 208 documents.
```
GET patents-00001/_search
{
  "query": {
    "term": {
      "patent_type": "grant"
    }
  }
}
```