# -*- coding: utf8 -*-

import ConfigParser
import logging
import re
from lxml import etree


def test():
    suffix_list = [u'六经', u'简名', u'东晋']
    pattern = re.compile('(' + '|'.join(suffix_list) + ')+')
    match = pattern.search(u'经六简名东晋') 
    if match: 
        # 使用Match获得分组信息 
        print match.group(0)
        print match.group(1)
        print match.start(0)
        print match.start(1)
    if True:
        return None, None
    return 0, 1
    
def new_prop(sense, name, text):
    prop = etree.SubElement(sense, 'prop')
    prop.set('name', name)
    value = etree.SubElement(prop, 'value')
    if len(text) > 0:
        value.text = text
        logging.debug(name + '\t' + value.text)

    return

def parse_sense(sub_line, suffix_list, category):
    sense = etree.Element('sense')
    print sub_line
    
    match = re.match(ur'([^。]*)。(.*)', sub_line)
    if match:
        # Reverse
        # print match.group(1)[::-1]
        print match.group(1)
        print match.group(2)
        
        pattern = re.compile(ur'(' + ur'|'.join(suffix_list) + ur')+$')
 
        category = re.search(pattern, match.group(1))
        if category:
            new_prop(sense, u'类别', category.group())
            new_prop(sense, u'释义', match.group(2))
            print category.group()
        else:
            new_prop(sense, u'释义', sub_line)
            return
    else:
        logging.error(sub_line)
        return
        
    return sense
    

def match_max(s, suffix_list):
    end = 0
    s_max = ''
    
    # no +$
    pattern = re.compile(ur'(' + ur'|'.join(suffix_list) + ur')')
    while True:
        match = re.search(pattern, s[end:])
        if match:
            logging.debug(match.group())
            idx = s[end + match.end():].find(s_max + match.group())
            if idx == 0:
                logging.debug(s)
                logging.debug(end + match.end())
                return end + match.end()
            elif idx > 0:
                end += match.end()
                s_max += match.group()
            else:
                return 0


def preprocess_entry(line, suffix_list, suffix_singleton_list, suffix_stoplist):
    entry = etree.Element('entry')
        
    # 格式：主义项①...
    idx = line.find(u'①')
    # 阳维①奇穴名。->阳维
    if idx >= 0:
        form = line[:idx]
    else:
        form = line
    
    # 格式：条目类别， 或 条目类别。
    # 曲瞅内经穴别名，即委中别名。->曲瞅内经穴别名->曲瞅内
    # 巡经得度传中医术语。－>巡经得度传中医术语->巡经得度传
    pattern = re.compile(ur'(，|。)')
    match = re.search(pattern, form)
    if match:
        form = line[:match.start()]
        logging.debug(form)
    else:
        # 一画
        logging.error(line)
        return None, None
    
    pattern = re.compile(ur'(' + ur'|'.join(suffix_list) + ur')+$')
    match = re.search(pattern, form)
    if not match:
        # 无类别
        logging.error(line)
        return None, None
    
    logging.debug(match.group())
    logging.debug(match.start())
    logging.debug(form[:match.start()])

    # 病能论篇《素问》篇名
    pattern_article = re.compile(ur'《.*》篇名')
    match_article = re.search(pattern_article, form)
    if match_article:
        entry.set('form', form[:match_article.start()])
        category = match_article.group()
        return entry, category
    
    start = match.start()
    category = None
    
    # 忽略仅含有“的、之”的类别
    # ^, $
    # 咽|之
    pattern_stoplist = re.compile(ur'(^' + ur'|'.join(suffix_stoplist) + ur')$')
    match_stoplist = re.search(pattern_stoplist, form[start:])
    if match_stoplist:
        start += 1
            
    # 调整以“学、家、穴”词缀开头的类别：合并条目与“学、家、穴”
    # no +$
    # 华医病理学|医书。－>华医病理学|医书。
    # 丁丙清代藏书家
    # 太阴络即漏谷穴
    pattern_singleton = re.compile(ur'^(' + ur'|'.join(suffix_singleton_list) + ur')')
    match_singleton = re.search(pattern_singleton, form[start:])
    if match_singleton:
        start += 1
    
    # 调整有重复词缀的类别
    # 方剂学方剂学著作－>方剂学|方剂学著作
    # 气功气功术语－>气功｜气功术语
    if start < len(form):
        # 若类别不为空
        end = match_max(form[start:], suffix_list)
        if end > 0:
            start += end
    
    # 调整条目为空的类别：使用首词缀作为条目
    # 手针针灸术语－>手针|针灸术语
    if start == 0:
        pattern_initial = re.compile(ur'^(' + ur'|'.join(suffix_list) + ur')')
        match_initial = re.search(pattern_initial, form[start:])
        if match_initial:
            logging.debug(form[:match_initial.end()])
            start = match_initial.end()

    entry.set('form', form[:start])
    category = form[start:]        
    
    # sense
    sense_cnt = 0

    logging.debug(sense_cnt)
    return entry, category

    
def parse_suffix(suffix_file_name):
    # Initialize suffix_list
    suffix_list = list()
    f = file(suffix_file_name)
    for line in f:
        line = line.decode('utf8').strip()
        if len(line) == 0:
            continue
        if line.find('//') == 0:
            continue    # skip comments
        
        suffix_list.append(line)
    f.close()
    logging.debug('|'.join(suffix_list))

    return suffix_list
    
    
def parse_dict(txt_file_name, suffix_list, suffix_singleton_list, suffix_stoplist):              
    root = etree.Element('dict')
    
    entry_cnt = 0
    category_dict = dict()
    f = file(txt_file_name)
    for line in f:
        line = line.decode('utf8').strip()
        line = line.replace(' ', '')
        if len(line) == 0:
            continue
        logging.debug('line\t' + line)
   
        entry, category = preprocess_entry(line, suffix_list, suffix_singleton_list, suffix_stoplist)
        if entry is None:
            logging.error(line)
            continue        
        entry.set('index', str(entry_cnt))
        root.append(entry)
        
        if category not in category_dict:
            category_dict[category] = list()
            category_dict[category].append(entry.get('form'))
            
        entry_cnt += 1
    f.close()
       
    for key, value in category_dict.items():
        f = open('Output/' + key + '.txt', 'w')
        for v in value:
            f.write(v.encode('utf8'))
            f.write('\n')
        f.close()

    logging.debug(entry_cnt)
    return root
   
   
def serialize_dict(root, xml_schema_file_name, output_file_name):
    try:
#         entry_cnt = 0
        for entry in list(root):
#             sense_cnt = 0
            for sense in list(entry):
                if len(list(sense)) == 0:
                    logging.error(etree.tostring(entry, xml_declaration=True, encoding="UTF-8", pretty_print=True)) 
                    new_prop(sense, u'例句', '')
                prop_cnt = 0
                for prop in list(sense):
                    prop.set('index', str(prop_cnt))
                    prop_cnt += 1
        
        # Validate
        xml_schema_tree = etree.parse(xml_schema_file_name)
        xml_schema = etree.XMLSchema(xml_schema_tree)
        xml_schema.assertValid(root)

        f = file(output_file_name, 'w')
        f.write(etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True))
        f.close() 
        
    except etree.DocumentInvalid as exception:
        print exception.error_log.filter_from_errors()[0].message

     
def main():
    config_parser = ConfigParser.ConfigParser()
    config_parser.read('config.txt')
    
#     x, y = test()
    
    suffix_list = parse_suffix(config_parser.get('input', 'suffix_file_name'))
    suffix_singleton_list = parse_suffix(config_parser.get('input', 'suffix_singleton_file_name'))
    suffix_stoplist = parse_suffix(config_parser.get('input', 'suffix_stoplist_file_name'))
    root = parse_dict(config_parser.get('input', 'txt_file_name'), suffix_list, suffix_singleton_list, suffix_stoplist)
    serialize_dict(root, config_parser.get('input', 'xml_schema_file_name'), config_parser.get('output', 'xml_file_name'))

    return


if __name__ == '__main__':
    """ main """
    # Log
    logging.basicConfig(filename='log.txt', filemode='w', level=logging.CRITICAL, 
    format='[%(levelname)s\t%(asctime)s\t%(funcName)s\t%(lineno)d]\t%(message)s')

    main()
    