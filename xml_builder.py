from typing import List, Dict
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom.minidom import parseString
from io import BytesIO

def build_xml(comments: List[Dict[int, str]], start_timestamp, thread_number="2828282828") -> str:
    root = Element('packet')
    
    thread = SubElement(root, 'thread', thread=thread_number)
    global_num_res = SubElement(root, 'global_num_res', thread=thread_number, num_res="5000")
    leaf = SubElement(root, 'leaf', thread=thread_number, count="5000")
    
    for i, comment in enumerate(comments):
        vpos = calc_vpos(start_timestamp, comment['timestamp'])
        if vpos < 0:
            continue
        if "id" not in comment:
            user_id = "nvc:futaba"
        else:
            user_id = comment["id"]
        chat = SubElement(root, 'chat', {
            'thread': thread_number,
            'no': str(i + 1),
            'vpos': str(vpos),
            'date': str(comment['timestamp'] // 1000),
            'date_usec': "28",
            'premium': "0",
            'anonymity': "1",
            'user_id': user_id,
            'mail': ""
        })
        chat.text = comment['comment']
    
    # ElementTreeを使ってXMLを文字列に変換
    tree = ElementTree(root)
    
    xml_bytes = BytesIO()
    tree.write(xml_bytes, encoding='utf-8', xml_declaration=True)
    xml_str = xml_bytes.getvalue().decode('utf-8')
    
    # XMLを整形
    dom = parseString(xml_str)
    pretty_xml_str = dom.toprettyxml(indent="  ")
    return pretty_xml_str

def calc_vpos(start_timestamp: int, comment_timestamp: int) -> int:
    # vposを計算
    vpos = (comment_timestamp - start_timestamp) // 10
    return vpos

# コメントのタイミング調整
def shift_timestamp(comments: List[Dict[int, str]], shift: int) -> int:
    shift = shift * 1000
    for comment in comments:
        timestamp = comment['timestamp']
        comment['timestamp'] = timestamp + shift
    return comments

def remove_comments(comments: List[Dict[int, str]], start_timestamp: int, end_timestamp: int) -> List[Dict[int, str]]:
    new_comments = []
    for comment in comments:
        timestamp = comment['timestamp']
        if start_timestamp <= timestamp <= end_timestamp:
            new_comments.append(comment)
    return new_comments

if __name__ == '__main__':
    comments = [
        {'timestamp': 1730595762000, 'comment': 'test1'},
        {'timestamp': 1730595757000, 'comment': 'test2'},
        {'timestamp': 1730595725000, 'comment': 'test3'},
    ]
    xml_output = build_xml(comments)
    print(xml_output)