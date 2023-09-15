# ETL for USPTO Patent Grants & Applications
This is an ETL script for for USPTO Patent Grants & Applications. Script starts with reading the ```xml``` file specified in the ```config.yaml```. It then extracts the relevant information and uploads the data to Elasticsearch.

Run:
```python data_ingestion --patent-type grant```

Patent type can be either ```grant``` or ```application```
```