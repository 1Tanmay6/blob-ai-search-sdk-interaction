import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged

class AzureBlobAccess:
    def __init__(self) -> None:
        """
        Initialize the AzureBlobAccess class and load environment variables.
        """
        load_dotenv()
        self.blob_service_client: BlobServiceClient
        self.blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])

    def get_blob_list(self, container_name: str) -> dict[str, list]:
        """
        Retrieve a list of blobs from the specified container.

        :param container_name: The name of the container.
        :type container_name: str
        :return: A dictionary containing a list of blob names.
        :rtype: dict[str, list]
        """
        blob_list: ItemPaged
        try:
            container_client = self.blob_service_client.get_container_client(container=container_name)
            blob_list = container_client.list_blob_names()
            return {'blob_list': list(blob_list)}
        except Exception as e:
            raise RuntimeError(e)

    def _get_sas_token(self, validity_in_hours: int, container_name: str, blob_name: str) -> str:
        """
        Generate a SAS token for a blob with specified validity period.

        :param validity_in_hours: The validity period of the SAS token in hours.
        :type validity_in_hours: int
        :param container_name: The name of the container.
        :type container_name: str
        :param blob_name: The name of the blob.
        :type blob_name: str
        :return: The generated SAS token.
        :rtype: str
        """
        try:
            expiry = datetime.now() + timedelta(hours=validity_in_hours)
            sas_token = generate_blob_sas(
                account_name=os.environ['AZURE_STORAGE_ACCOUNT_NAME'],
                container_name=container_name,
                blob_name=blob_name,
                account_key=os.environ['AZURE_STORAGE_ACCOUNT_KEY'], 
                permission=BlobSasPermissions(read=True),
                expiry=expiry
            )
            return sas_token
        except Exception as e:
            raise ValueError(f'The code exited with an exception: {e}')
            
    def get_blob_url(self, container_name: str, blob_name: str) -> dict[str, str]:
        """
        Retrieve the URL of a blob with a SAS token appended for secure access.

        :param container_name: The name of the container.
        :type container_name: str
        :param blob_name: The name of the blob.
        :type blob_name: str
        :return: A dictionary containing the blob URL with SAS token.
        :rtype: dict[str, str]
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_url = blob_client.url
            blob_url_with_sas = f"{blob_url}?{self._get_sas_token(validity_in_hours=1, container_name=container_name, blob_name=blob_name)}"
            return {'blob_url': blob_url_with_sas}
        except Exception as e:
            raise ValueError(f"Blob {blob_name} not found in container {container_name}, with an exception {e}")

if __name__ == '__main__':
    azure_blob_access = AzureBlobAccess()
    list_blob = azure_blob_access.get_blob_list(os.environ['AZURE_CONTAINER_NAME'])['blob_list']
    print(azure_blob_access.get_blob_url(container_name=os.environ['AZURE_CONTAINER_NAME'], blob_name=list_blob[0]))
