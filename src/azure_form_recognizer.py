import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult

class AzureFormRecognizerUtils:
    def __init__(self, form_url) -> None:
        """
        Initialize the AzureFormRecognizerUtils class with the provided form URL.
        
        :param form_url: The URL of the form to be analyzed.
        :type form_url: str
        """
        # Load environment variables
        load_dotenv()
        self.form_url = form_url
        self.endpoint = os.environ['AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT']
        self.key = os.environ['AZURE_DOCUMENT_INTELLIGENCE_API_KEY']

        # Initialize the Document Intelligence Client
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )
        
        # Begin the document analysis process
        self.poller = self.document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", 
            AnalyzeDocumentRequest(url_source=form_url)
        )
        # Retrieve the results of the analysis
        self.result = self.poller.result()

    def is_handwritten(self) -> bool:
        """
        Determine if any part of the document is handwritten.
        
        :return: True if any part of the document is handwritten, False otherwise.
        :rtype: bool
        """
        return any(style.is_handwritten for style in self.result.styles)

    def get_number_of_pages(self) -> int:
        """
        Retrieve the number of pages in the document.
        
        :return: The number of pages in the document.
        :rtype: int
        """
        return len(self.result.pages)
    
    def get_content(self) -> list[dict]:
        """
        Extract the content of the document, organized by pages and lines.
        
        :return: A list of dictionaries containing page numbers and lines of content.
        :rtype: list[dict]
        """
        page_content = []
        for page_num, page in enumerate(self.result.pages):
            content = {
                'page_number': page_num + 1,
                'lines': [{'line_number': line_idx + 1, 'line_content': line.content} for line_idx, line in enumerate(page.lines)]
            }
            page_content.append(content)
        return page_content
    
    def get_tables(self) -> list[dict]:
        """
        Extract the tables from the document, including their page numbers and cell contents.
        
        :return: A list of dictionaries containing table information and cell contents.
        :rtype: list[dict]
        """
        table_content = []
        if self.result.tables:
            for table_number, table in enumerate(self.result.tables):
                content = {
                    'table_number': table_number + 1,
                    'page_number_of_table': {region.page_number for region in table.bounding_regions},
                    'table_cells_information': [{'row': cell.row_index, 'column': cell.column_index, 'cell_content': cell.content} for cell in table.cells]
                }
                table_content.append(content)
        return table_content

if __name__ == '__main__':
    form_url = 'form_url'
    azure_form = AzureFormRecognizerUtils(form_url)
    for stuff in azure_form.get_content():
        print(stuff)
