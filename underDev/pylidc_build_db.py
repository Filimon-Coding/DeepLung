import os
from pathlib import Path
import pylidc as pl

XML_ROOT = Path("/media/neov/NewDisk/NewDownload/XMLFiles/LIDC-XML-only/tcia-lidc-xml")

def main():
    # Dette bygger pylidc sin SQLite-db ved å parse XML.
    # Det kan ta tid (mange filer).
    xml_files = sorted(XML_ROOT.rglob("*.xml"))
    print("XML files:", len(xml_files))

    # PyLIDC har en intern populate-funksjon. Den ligger i _populate_db.
    from pylidc._populate_db import populate

    # populate(dbpath=None, xmlpath=...)
    # db legges som standard i home (~/.pylidc/pylidc.db)
    populate(xmlpath=str(XML_ROOT))

    # sanity check
    scans = pl.query(pl.Scan).all()
    print("Scans in DB:", len(scans))
    if scans:
        s = scans[0]
        print("Example scan patient_id:", s.patient_id)

if __name__ == "__main__":
    main()
