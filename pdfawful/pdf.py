from PyPDF2 import PdfFileReader

import re
import os

class EmbeddedPDF:

  def __init__(self, path, data):
    self.path = path
    self.data = data
    

def scan_pdf(file, index_only=False):
  if not file.lower().endswith('.pdf'):
    return
  pdfFile = open(file, 'rb')
  pdfReader = PdfFileReader(pdfFile)
  catalog = pdfReader.trailer['/Root']
  
  # folder structure
  folderMap = {}
  if '/Collection' in catalog and '/Folders' in catalog['/Collection']:
    def findChildFolders(folder, path=''):
      if '/Child' in folder:
        child = folder['/Child']
        id = child['/ID']
        name = child['/Name']
        folderMap[id] = os.path.join(path, name)
        findChildFolders(child, folderMap[id])
        findSiblingFolders(child, path)

    def findSiblingFolders(folder, path=''):
      if '/Next' in folder:
        sibling = folder['/Next']
        id = sibling['/ID']
        name = sibling['/Name']
        folderMap[id] = os.path.join(path, name)
        findChildFolders(sibling, folderMap[id])
        findSiblingFolders(sibling, path)

    findChildFolders(catalog['/Collection']['/Folders'])


  # embedded files
  if '/Names' in catalog:
    names = catalog['/Names'].getObject()
    if '/EmbeddedFiles' in names:
      embeddedFiles = names['/EmbeddedFiles'].getObject()
      if '/Kids' in embeddedFiles:
        kids = embeddedFiles['/Kids']
        for kid in kids:
          fileNames = kid.getObject()['/Names']
          
          # enumeration is name, object, name, object..
          i = 0
          while i < len(fileNames):
            entry = fileNames[i]
            fileName = entry

            # part of the entry label is '<{id}>' where {id} maps to the folders
            m = re.match(r"^<(\d+)>(.*)$", entry)
            if m:
              path = folderMap[int(m.group(1))]
              fileName = m.group(2)

            if index_only:
              # quick run: only return the paths
              yield os.path.join(path, fileName)
              i += 1
            else:
              # full run: return objects for the data to be extracted
              i += 1
              fObj = fileNames[i].getObject()
              fData = fObj['/EF']['/F'].getData()
              yield EmbeddedPDF(os.path.join(path, fileName), fData)
            i += 1

  # on-page attachments
  if pdfReader.pages:
    for page in pdfReader.pages:
      if '/Annots' in page:
        for annot in page['/Annots']:
          annotObj = annot.getObject()
          if '/FS' in annotObj:
            fileName = annotObj['/FS']['/UF']
            if index_only:
              # quick run: only return the filename
              yield fileName
            else:
              # full run: return objects for the data to be extracted
              data = annotObj['/FS']['/EF']['/F'].getData()
              yield EmbeddedPDF(fileName, data)
