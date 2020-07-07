#!/usr/bin/env python

"""
Created by Cyber Security Diskominfo Kota Serang (https://cybersec.serangkota.go.id):
- malwareslayer
- ahdihaikal
- gagaltotal

Dinas Komunikasi Dan Informatika Kota Serang (https://kominfo.serangkota.go.id)
"""

import asyncio
import pytesseract
import re
import os
import sys

from itertools import count
from aiohttp import ClientSession

from lib.core.enums import PRIORITY
from lib.core.data import logger, conf


class OCRTamper:
    default_image_path = "/tmp/captcha.png"
    default_headers_path = "/tmp/headers"

    def __init__(self, image_url, captcha_params, conf_headers, mode, tesseract_config=None):
        self.image_url = image_url
        self.captcha_params = captcha_params
        self.conf_headers = conf_headers
        self.tesseract_config = tesseract_config
        self.mode = mode
        self._results = None

        asyncio.get_event_loop().run_until_complete(self.run())

    def __del__(self):
        os.remove(self.default_image_path)

    async def run(self):

        for x in count(1):
            if self.preview:
                break

        if self.mode == 'math':
            self._results = await self.calculate(self.tesseract)
        elif self.mode == 'character':
            self._results = await self.preview
        elif self.mode == 'easy':
            self._results = await self.tesseract
        else:
            logger.critical("input either math, character or easy")
            exit(1)

    async def calculate(self, expressions):
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

        return "&" + self.captcha_params + "=" + results

    @property
    async def downloadimage(self):
        try:
            async with ClientSession(headers=self.conf_headers) as Session:
                async with Session.get(self.image_url) as Response:
                    image = await Response.read()
                    with open(self.default_image_path, "wb+") as file:
                        file.write(image)
        except Exception:
            logger.critical("Trying To Download Captcha Again")
            return False

        return True

    @property
    def result(self):
        return self._results

    @property
    async def preview(self):
        catimg = await asyncio.create_subprocess_shell(
            f"catimg {self.default_image_path}",
            stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await catimg.communicate()

        if stderr:
            raise stderr
        else:
            return "&" + self.captcha_params + "=" + input("Real Captcha ? :")

    @property
    async def tesseract(self):
        imagick = await asyncio.create_subprocess_shell(
            f"""
            convert {self.default_image_path} \
            -colorspace Gray                  \
            -blur 3x1                         \
            -morphology Erode Diamond:1x4     \
            -level 20%                        \
            {self.default_image_path}
            """,
            stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await imagick.communicate()

        if stderr:
            raise stderr
        else:
            return pytesseract.image_to_string(self.default_image_path, config=self.tesseract_config)


__priority__ = PRIORITY.HIGHEST

baseargv = sys.argv.index(os.path.basename(__file__).split(".")[0])

try:
    urlpath = sys.argv[baseargv + 1]
    captchaparams = sys.argv[baseargv + 2]
    cookie = sys.argv[baseargv + 3]
except IndexError:
    logger.critical("Please input argument into tamper or make --tamper securimagecaptcha in last argument")
    exit(1)

try:
    tesseract_config = sys.argv[baseargv + 4]
except IndexError:
    tesseract_config = None

mode = input("Captcha Math Mode ? [math/character/easy]")

def depedencies():
    pass


def tamper(payload, **kwargs):

    headers = {
        "Cookie": cookie
    }

    ocr = OCRTamper(urlpath, captchaparams, headers, mode, tesseract_config=tesseract_config)

    return payload + ocr.result
