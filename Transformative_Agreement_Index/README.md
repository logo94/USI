# Transformative Agreement Index

## Files

The repository constais two files:

- merge of [Transformative Agreements](https://esac-initiative.org/about/transformative-agreements/) Index published at the [link](https://docs.google.com/spreadsheets/d/e/2PACX-1vStezELi7qnKcyE8OiO2OYx2kqQDOnNsDX1JfAsK487n2uB_Dve5iDTwhUFfJ7eFPDhEjkfhXhqVTGw/pub?gid=1130349201&single=true&output=csv) in JSON format
- List of all Journals in the index, expressed as python array for quick import

## JSON schema

```
[
  {
    "ESAC_ID": str,
    "Relationship": str | None,
    "End_date": str,
    "Corresponding_authors": True | False,
    "Doc_url": str,
    "Last_review": str,
    "Journals": [
      {
        "Name": str,
        "ISSN": {
          "Print": str | None,
          "Online": str 
        },
        "Seen": {
          "First": str,
          "Last": str | None
        },
        "Insitution": {
          "Name": str | None,
          "ROR": {
            "ID": str,
            "url" str
          },
          "Seen": {
            "First": str,
            "Last": str | None
          }
        }
      }
    ]
  }
]

```


## Update schedule
Both JSON merge and Journals array are updated monthly

## License
The index, as well as the derived files contained in the repository, are released under the CC0 license
