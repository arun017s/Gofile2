# Original Author: Codec04
# Re-built by Itz-fork
# Project: Gofile2

import os
from requests import get 
from asyncio import sleep
from time import strftime
from aiohttp import ClientSession
from .errors import (InvalidOption, InvalidPath, InvalidToken, JobFailed,
                     ResponseError)


def is_valid_token(url, token):  
    req = get(f"{url}getAccountDetails?token={token}")
    resp = req.json()
    if resp["status"] == "error-wrongToken":
       raise InvalidToken(
            "Invalid Gofile Token, Get your Gofile token from --> https://gofile.io/myProfile")
    else:
       pass

class GoFile:
    """
    # GoFile Class:
        - Base class of Asynchronous Gofile2
    # Arguments:
        - `token` (optional for some functions)- The access token of an account. Can be retrieved from the profile page
    """

    def __init__(self, token=None):
        self.api_url = "https://api.gofile.io/"
        self.token = token
        if self.token is not None:
            is_valid_token(url=self.api_url, token=self.token)
       

    async def _api_resp_handler(self, response):
        api_status = response["status"]
        if api_status == "ok":
            return response["data"]
        else:
            if "error-" in response["status"]:
                error = response["status"].split("-")[1]
            else:
                error = "Response Status is not ok and reason is unknown"
            raise ResponseError(error)

    async def getServer(self, pre_session=None):
        """
        ### Get Server Function:
            - Get server of Gofile
        ### Arguments:
            - `None`
        """
        if pre_session:
            server_resp = await pre_session.get(f"{self.api_url}getServer")
            server_resp = await server_resp.json()
            return await self._api_resp_handler(server_resp)
        else:
            async with ClientSession() as session:
                try:
                    server_resp = await session.get(f"{self.api_url}getServer")
                    server_resp = await server_resp.json()
                    return await self._api_resp_handler(server_resp)
                except Exception as e:
                    raise JobFailed(e)

    async def getAccountDetails(self):
        """
        ### Get Account Function:
            - Get information about the account
        ### Arguments:
            - `None`
        """
        if self.token is None:
            raise InvalidToken()
        async with ClientSession() as session:
            try:
                get_account_resp = await session.get(url=f"{self.api_url}getAccountDetails?token={self.token}")
                get_account_resp = await get_account_resp.json()                
                return await self._api_resp_handler(get_account_resp)
            except Exception as e:
                raise JobFailed(e)

    async def uploadFolder(self, path: str, folderId: str = "", folder_name: str = "Gofile2", delay: int = 2):
        """
        NOTE: To use this function, you must have a GoFile token
        ### Upload folder Function
            - Upload files in the given path to Gofile
        ### Arguments
            - `path` - Path to the folder
            - `folderId` (optional) - The ID of a folder. When using the folderId, you must pass the token
            - `delay` - Time interval between file uploads (in seconds)
        """
        if not os.path.isdir(path):
            raise InvalidPath(f"{path} is not a valid directory")
        uploaded = []
        files = [val for sublist in [[os.path.join(
            i[0], j) for j in i[2]] for i in os.walk(path)] for val in sublist]
        # Get folder id if not passed
        if not folderId:
            rtfid = (await self.getAccountDetails())["rootFolder"]
            folderId = (await self.createFolder(rtfid, "GoFile2- Created in {}".format(strftime("%b %d, %Y %l:%M%p"))))["id"]
        for file in files:
            udt = await self.uploadFile(file, folderId)
            uploaded.append(udt)
            await sleep(delay)
        return uploaded

    async def uploadFile(self, file: str, folderId: str = ""):
        """
        ### Upload Function:
            - Upload a file to Gofile
        ### Arguments:
            - `file` - Path to file that want to be uploaded
            - `folderId` (optional) - The ID of a folder. When using the folderId, you must pass the token            
        """        
        async with ClientSession() as session:
            # Check time
            if not os.path.isfile(file):
                raise InvalidPath(f"No such file - {file}")
            
            server = await self.getServer(pre_session=session)
            server = server["server"]
            
            # Making dict
            req_dict = {}
            if self.token:
                req_dict["token"] = self.token
            if bool(folderId):
                req_dict["folderId"] = folderId
            
            with open(file, "rb") as go_file_d:
                req_dict["file"] = go_file_d
                try:
                    upload = await session.post(
                        url=f"https://{server}.gofile.io/uploadFile",
                        data=req_dict
                    )
                    upload_file = await upload.json()                  
                    return await self._api_resp_handler(upload_file)
                except Exception as e:
                    raise JobFailed(e)

    async def createFolder(self, parentFolderId, folderName):
        """
        ### Create Folder Function:
            - Create a new folder account
        ### Arguments:
            - `parentFolderId` - The parent folder ID
            - `folderName` - The name of the folder that wanted to create
        """
        if self.token is None:
            raise InvalidToken()
        async with ClientSession() as session:
            try:
                folder_resp = await session.put(
                    url=f"{self.api_url}createFolder",
                    data={
                        "parentFolderId": parentFolderId,
                        "folderName": folderName,
                        "token": self.token
                    }
                )
                folder_resp = await folder_resp.json()
                return await self._api_resp_handler(folder_resp)
            except Exception as e:
                raise JobFailed(e)

    async def setOption(self, contentId, option, value):
        """
        ### Set Folder Option Function:
            - Set an option 
        ### Arguments:
            - `contentId` - The ID of the content 
            - `option` - Option that you want to set. Can be "public", "password", "description", "expire" or "tags"
            - `value` - The value of the option to be defined.
                     - For "public", can be "true" or "false".
                     - For "password", must be the password.
                     - For "description", must be the description.
                     - For "expire", must be the expiration date in the form of unix timestamp.
                     - For "tags", must be a comma seperated list of tags.
        """
        if self.token is None:
            raise InvalidToken()
        if not option in ["public", "password", "description", "expire", "tags"]:
            raise InvalidOption(option)
        async with ClientSession() as session:
            try:
                set_folder_resp = await session.put(
                    url=f"{self.api_url}setOption",
                    data={
                        "token": self.token,
                        "contentId": contentId,
                        "option": option,
                        "value": value
                    }
                )
                set_folder_resp = await set_folder_resp.json()
                return await self._api_resp_handler(set_folder_resp)
            except Exception as e:
                raise JobFailed(e)

    async def getContent(self, contentId):
        """
        ### Get Content Function:
            - Get a specific content details
        ### Arguments:
            - `contentId` - The ID of the file or folder
        """
        if self.token is None:
            raise InvalidToken()
        async with ClientSession() as session:
            try:
                get_content_resp = await session.get(url=f"{self.api_url}getContent?contentId={contentId}&token={self.token}")
                get_content_resp = await get_content_resp.json()
                return await self._api_resp_handler(get_content_resp)
            except Exception as e:
                raise JobFailed(e)

    async def copyContent(self, contentsId, folderIdDest):
        """
        ### Copy Content Function:
            - Copy one or multiple contents to another folder
        ### Arguments:
            - `contentsId` - The ID(s) of the file or folder (Separate each one by comma if there are multiple IDs)
            - `folderIdDest` - Destinatination folder ID
        """
        if self.token is None:
            raise InvalidToken()
        async with ClientSession() as session:
            try:
                copy_content_resp = await session.put(
                    url=f"{self.api_url}copyContent",
                    data={
                        "token": self.token,
                        "contentsId": contentsId,
                        "folderIdDest": folderIdDest
                    }
                )
                copy_content_resp = await copy_content_resp.json()
                return await self._api_resp_handler(copy_content_resp)
            except Exception as e:
                raise JobFailed(e)

    async def deleteContent(self, contentId):
        """
        ### Delete Content Function:
            - Delete a file or folder
        ### Arguments:
            - `contentId` - The ID of the file or folder
        """
        if self.token is None:
            raise InvalidToken()
        async with ClientSession() as session:
            try:
                del_content_resp = await session.delete(
                    url=f"{self.api_url}deleteContent",
                    data={
                        "contentId": contentId,
                        "token": self.token
                    }
                )
                del_content_resp = await del_content_resp.json()
                return await self._api_resp_handler(del_content_resp)
            except Exception as e:
                raise JobFailed(e)
