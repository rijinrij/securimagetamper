#!/usr/bin/env python

"""
Created by Cyber Security Diskominfo Kota Serang (https://cybersec.serangkota.go.id):
- malwareslayer
- ahdihaikal
- gagaltotal
- Sorong6etar
Dinas Komunikasi Dan Informatika Kota Serang (https://kominfo.serangkota.go.id)
"""

import asyncio
import re
import os
import sys
import json
import pytesseract

from aiohttp import ClientSession
from typing import (
    AnyStr,
    Dict,
    Optional
)

from lib.core.enums import PRIORITY
from lib.core.data import logger


class OCRTamper:
    __default_image_path = "/tmp/captcha.png"
    __default_headers_path = "/tmp/headers"
    __results = None

    def __init__(self, data: json.loads):
        self.images: AnyStr = data["images"]
        self.parameters: AnyStr = data["parameters"]
        self.headers: Dict[AnyStr] = data["headers"]
        self.mode: AnyStr = data["mode"]

        try:
            self.config: Optional[Dict[AnyStr]] = data["config"]
        except json.decoder.JSONDecodeError:
            logger.debug("Something error in config, ignore")
            self.config: Optional[Dict[AnyStr]] = None

        asyncio.get_event_loop().run_until_complete(self.run())

    def __del__(self):
        os.remove(self.__default_image_path)

    async def run(self):
        await self.downloadimage()
        if self.mode == 'math':
            expressions = await self.tesseractloads
            self.__results = await self.calculate(expressions)
        elif self.mode == 'character':
            self.__results = await self.preview
        elif self.mode == 'easy':
            self.__results = await self.tesseractloads
        else:
            logger.critical("input either math, character or easy")
            exit(1)

    async def calculate(self, expressions) -> AnyStr:
        expressions = re.search(r'\d+[-+x*/]\d+', expressions)

        try:
            expressions = re.findall(r'(\d+|[^ 0-9])', expressions.group(0))
        except AttributeError:
            logger.debug("cannot detected by tesseract trying manual")
            return await self.preview

        if expressions[1] == 'x':
            expressions[1] = '*'
        elif expressions[1] == '/':
            expressions[1] = '//'

        expressions = ''.join(expressions)
        results = str(eval(expressions))

        logger.info(f"{expressions} = {results}")

        return "&" + self.parameters + "=" + results

    async def downloadimage(self) -> None:
        async with ClientSession(headers=self.headers) as Session:
            async with Session.get(self.images) as Response:
                image = await Response.read()
                with open(self.__default_image_path, "wb+") as file:
                    file.write(image)

    @property
    def result(self) -> AnyStr:
        return self.__results

    @property
    async def preview(self) -> AnyStr:
        catimg = await asyncio.create_subprocess_shell(
            f"catimg {self.__default_image_path}",
            stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await catimg.communicate()

        if stderr:
            raise stderr
        else:
            return "&" + self.parameters + "=" + input("Real Captcha ? : ")

    @property
    async def tesseractloads(self) -> pytesseract.image_to_string:

        try:
            if self.config is None:
                convert = "-colorspace Gray -blur 3x1 -morphology Erode Diamond:1x4 -level 20%"
            else:
                convert = self.config["convert"]
        except KeyError:
            convert = "-colorspace Gray -blur 3x1 -morphology Erode Diamond:1x4 -level 20%"

        imagick = await asyncio.create_subprocess_shell(
            f"""
            convert {self.__default_image_path} \
            {convert}                           \
            {self.__default_image_path}
            """,
            stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await imagick.communicate()

        try:
            if self.config is None:
                tesseract = None
            else:
                tesseract = self.config["tesseract"]
        except KeyError:
            tesseract = None

        if stderr:
            raise stderr
        else:
            return pytesseract.image_to_string(self.__default_image_path, config=tesseract)


__priority__ = PRIORITY.HIGHEST

baseargv = sys.argv.index(os.path.basename(__file__).split(".")[0])

filejsonpath: str = ""
filejson: str = ""
datajson: json.loads = None

try:
    filejsonpath: str = sys.argv[baseargv + 1]
except IndexError:
    logger.critical("Please input argument json file into tamper or make --tamper securimagecaptcha in last argument")
    exit(1)

logger.debug("Load: " + filejsonpath)

try:
    filejson = open(filejsonpath, "r+").read()
except FileNotFoundError:
    logger.critical("Cannot find the path you input")
    exit(1)

try:
    datajson = json.loads(filejson)
except json.decoder.JSONDecodeError:
    logger.critical("Check your json file")
    exit(1)

def depedencies():
    pass


def tamper(payload, **kwargs):

    ocr = OCRTamper(datajson)

    return payload + ocr.result
