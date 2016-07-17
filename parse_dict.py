# -*- coding: utf8 -*-

import ConfigParser
import logging
import os
import re
from lxml import etree


def test():
    pattern = re.compile(ur'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿]')
    sense_list = pattern.split(u'①道。即初始、根本、规律。出 《老子•二十二章》：“圣人抱一为天下式。”《重阳真 人金关玉锁诀 一者是万物之根本，一者为道也。” 《太平经•脩一却邪法》；“夫一者，乃道之根本也 ……深思其意，谓之知道。”道家为修心养性，守中 抱一;儒家为存心养性，执中贯一;佛家为明心见性， 万法规一；医家为虚心定性，抱元守一。在气功修炼 中能悟解一者，谓之得道。《太平经》：“以思守一，何 也？ 一者，数之始也；一者生之道也；一者，元气之 始也；一者，天之纲纪也。”②内丹。《道家•丹鼎 门》秘诀：“九九归一”，一，即指所成之丹。《抱朴 子内篇•地真卷十八》：“ ‘一’有姓字服色，男长九 分，女长六分，或在脐下二寸四分下丹田中；或在心 下绛宫金阙中丹田也，或在人两眉间，却行一寸为明 堂，二寸为洞房，三寸为上丹田也。”③指修守部位。 《太平经•脩一却邪法》：“故头之一者，顶也；七正 (窍）之一者，目也；腹之一者，脐也；脉之一者，气 也；五脏之一者，心也；四肢之一者，手足心也；骨 之一者，脊也；肉之一者，肠胃也。能坚守，知其道 意，得道者令人仁，失道者令人贪。”④意念。《太平 经•万二千国始火始气诀》：“一者，心也，意也，念 也，一身中之神也。”《老子》：“神得一以灵”。在气 功修炼中“守一”，意念专一是得道的关键。⑤ 《易》书中“阳爻”的符号。')
    print len(sense_list)
    for sense in sense_list:
        print sense.encode('utf8')
    
    return
    
def new_prop(sense, name, text):
    prop = etree.SubElement(sense, 'prop')
    prop.set('name', name)
    value = etree.SubElement(prop, 'value')
    if len(text) > 0:
        value.text = text
        logging.debug(name + '\t' + value.text)

    return

def find_repeat(my_str, suffix_list):
    logging.debug(my_str)
    max_str = ''
    
    pattern = re.compile(ur'(' + ur'|'.join(suffix_list) + ur')')
    for match in pattern.finditer(my_str):
        idx = my_str[match.end():].find(max_str + match.group())
        if idx == 0:
            logging.debug(my_str)
            logging.debug(match.end())
            logging.debug(match.group())
            return match.end()
        elif idx > 0:
            max_str += match.group()
        else:
            return 0

    
def dump_category(file_name, key, value):
    f = open(file_name + '//' + key + '.txt', 'w')
    for v in value:
        f.write(v.encode('utf8'))
        f.write('\n')
    f.close()
    
    return


def categorize(ontology_dict, category_dict):
    for key, value in category_dict.items():
        # 输出到未分类目录
        dump_category(u'Output//未分类//', key, value)
        
        # 输出到分类目录
        pattern = re.compile(ur'(' + ur'|'.join(ontology_dict.keys()) + ur')')
        match_list = re.findall(pattern, key)
        if len(match_list) == 0:
            dump_category(u'Output//其他//', key, value)
        else:
            for match in match_list:
                dump_category(ontology_dict[match], key, value)
            
    return



def load_ontology(file_name):
    dir_name = u'Output//未分类'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    dir_name = u'Output//其他'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    ontology_dict = dict()
    
    # 生成目录
    f = file(file_name)
    for line in f:
        line = line.decode('utf8').strip()
        if len(line) == 0:
            continue
        if line.find('//') == 0:
            continue    # skip comments
        
        dir_list = line.split('\t')
        my_dir = 'Output//' + '//'.join(dir_list)
        if not os.path.exists(my_dir):
            os.makedirs(my_dir)

        # 建立词缀与目录的关联        
        ontology_dict[dir_list[-1]] = my_dir
    f.close()

    return ontology_dict
    
    
def load_list(file_name):
    my_list = list()
    f = file(file_name)
    for line in f:
        line = line.decode('utf8').strip()
        if len(line) == 0:
            continue
        if line.find('//') == 0:
            continue    # skip comments
        
        my_list.append(line)
    f.close()
    logging.debug('|'.join(my_list))

    return my_list


def parse_sense(line, suffix_list, category=''):
    # 解析义项
    sense = etree.Element('sense')
    
    logging.debug(line)
    if len(line) > 0 and len(category) == 0:
        # 格式：(条目)类别，... 或 (条目)类别。...
        # (曲瞅内)经穴别名，即委中别名。->经穴别名
        # (巡经得度传)中医术语。－>中医术语
        pattern = re.compile(ur'(，|。)')
        match = re.search(pattern, line)
        if match:
            category = line[:match.start()]
            logging.debug(line)
        else:
            # 无义项、无类别
            # 无，。：一画
            logging.error(line)
            return None, ''
        
        if len(category) > 0:
            pattern = re.compile(ur'(' + ur'|'.join(suffix_list) + ur')+$')
            match = re.search(pattern, category)
            if match:
                logging.debug(match.group())
                logging.debug(match.start())
                logging.debug(line[:match.start()])
                category = category[match.start():]
                
                # 扩展条目
                # 向左扩展条目
                # 病能论篇《素问》篇名
                pattern_article = re.compile(ur'《.*》篇名')
                match_article = re.search(pattern_article, category)
                if match_article:
                    category = match_article.group()
            else:
                # 无类别
                logging.error(line)
                category = ''
        else:
            # OCR错误：一见知医综合性医书◊清•陈鄂辑于1868 年。
            logging.error(line)
            category = ''
    
#     new_prop(sense, 'category', category)
#     new_prop(sense, 'others', line)
    logging.debug(category)
    
    return sense, category
    

def parse_form(line, suffix_list, suffix_singleton_list, suffix_stoplist):
    # 解析条目
    # 格式：条目类别， 或 条目类别。
    # 曲瞅内经穴别名，即委中别名。->曲瞅内经穴别名->曲瞅内
    # 巡经得度传中医术语。－>巡经得度传中医术语->巡经得度传
    category = ''
    
    pattern = re.compile(ur'(，|。)')
    match = re.search(pattern, line)
    if match:
        line = line[:match.start()]
        logging.debug(line)
    else:
        # 一画
        logging.error(line)
        return line, category
    
    pattern = re.compile(ur'(' + ur'|'.join(suffix_list) + ur')+$')
    match = re.search(pattern, line)
    if match:
        logging.debug(match.group())
        logging.debug(match.start())
        logging.debug(line[:match.start()])
        
        # 扩展条目
        # 向左扩展条目
        # 病能论篇《素问》篇名
        pattern_article = re.compile(ur'《.*》篇名')
        match_article = re.search(pattern_article, line)
        if match_article:
            form = line[:match_article.start()]
            category = match_article.group()
            return form, category
        
        # 向右扩展条目
        start = match.start()
        
        # 忽略仅含有“的、之”的类别
        # ^, $
        # 咽|之
        pattern_stoplist = re.compile(ur'(^' + ur'|'.join(suffix_stoplist) + ur')$')
        match_stoplist = re.search(pattern_stoplist, line[start:])
        if match_stoplist:
            start += 1
                
        # 调整以“学、家、穴”词缀开头的类别：合并条目与“学、家、穴”
        # no +$
        # 华医病理学|医书。－>华医病理学|医书。
        # 丁丙清代藏书家
        # 太阴络即漏谷穴
        pattern_singleton = re.compile(ur'^(' + ur'|'.join(suffix_singleton_list) + ur')')
        match_singleton = re.search(pattern_singleton, line[start:])
        if match_singleton:
            start += 1
        
        # 调整有重复词缀的类别
        # 方剂学方剂学著作－>方剂学|方剂学著作
        # 气功气功术语－>气功｜气功术语
        if len(line[start:]) > 0:
            # 若类别不为空
            end = find_repeat(line[start:], suffix_list)
            if end > 0:
                start += end
        
        # 调整条目为空的类别：使用首词缀作为条目
        # 手针针灸术语－>手针|针灸术语
        if start == 0:
            pattern_initial = re.compile(ur'^(' + ur'|'.join(suffix_list) + ur')')
            match_initial = re.search(pattern_initial, line[start:])
            if match_initial:
                logging.debug(line[:match_initial.end()])
                start = match_initial.end()

        # 暂时使用子义项类别作为条目类别
        # 格式：主义项①...
        # 阳维①奇穴名。->阳维
        if line[:start].find(u'①') == len(line[:start]) - 1:
            form = line[:start - 1]
            category = line[start:]
        else:
            form = line[:start]
            category = line[start:]  
            
        return form, category
    else:
        # 无类别
        # 1. 一纪①指十二年为一纪
        # 2. OCR错误：—扫光①中药名s见《西藏常用中草药》
        logging.error(line)
        idx = line.find(u'①')
        if idx >= 0:
            form = line[:idx]
        else:
            form = line
        category = ''
            
        return form, category
    
    
def parse_entry(entry, suffix_list):
    pattern = re.compile(ur'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿]')
    sense_list = pattern.split(entry.get('fulltext')[len(entry.get('form')):])
    
    # 主义项
    sense, category = parse_sense(sense_list[0], suffix_list)
    if sense is None:
        return None
    entry.append(sense)
    
    # 子义项
    for sense_str in sense_list[1:]:
        # (一上散)方名。①《兰室秘藏》卷下方... -> ['方名。','《兰室秘藏》卷下方...']
        # (一阳)①中医术语。指手、足少阳经，见该条... -> [(空)'', '中医术语。指手、足少阳经，见该条...']
        sense, tmp = parse_sense(sense_str, suffix_list, category)
        if sense is None:
            return None
        entry.append(sense)
        
    return entry


def parse_dict(txt_file_name, ontology_dict, suffix_list, suffix_singleton_list, suffix_stoplist, initial_list, initial_cnt):              
    root = etree.Element('dict')
    
    entry_cnt = 0
    initial = ''.join(initial_list)
    category_dict = dict()
    f = file(txt_file_name)
    for line in f:
        line = line.decode('utf8').strip()
        pattern = re.compile(r'\s')
        line = pattern.sub('', line)
        if len(line) == 0:
            continue
        logging.debug('line\t' + line)
        
        if line.find(u'丁。以上各料装入碗内上笼') >= 0:
            pass
   
        form, category = parse_form(line, suffix_list, suffix_singleton_list, suffix_stoplist)
        
        # 合并条目
        if initial.find(line[0]) >= 0 or len(category) > 0: 
            # 若相似首字 or 类别不为空，则新增条目
            entry = etree.SubElement(root, 'entry')
            entry.set('index', str(entry_cnt))
            entry.set('form', form)
            entry.set('fulltext', line)
            entry_cnt += 1
        else:
            # 否则合并条目
            if len(list(root)) > 0:
                logging.debug(list(root)[-1].get('fulltext'))
                list(root)[-1].set('fulltext', ''.join([list(root)[-1].get('fulltext'), line]))
                logging.debug(list(root)[-1].get('fulltext'))
            else:
                # — 画 •
                logging.error(line)
        
        if initial.find(line[0]) < 0 and len(category) > 0:
            # 若首字不相似 且 类别不为空，则加入initial
            # 一擦光|方名。
            # 乙庚化金|运气术语。－>乙
            if len(initial) >= initial_cnt:
                initial = initial[1:]
            initial += line[0]
                
        parse_entry(entry, suffix_list)
        
        if category not in category_dict:
            category_dict[category] = list()
        category_dict[category].append(entry.get('form'))
            
        if len(entry.get('form')) > 10:
            logging.critical(str(entry.get('index')) + '\t' + entry.get('fulltext') + '\t' + entry.get('form'))
            
    f.close()
    
    categorize(ontology_dict, category_dict)
       
    logging.debug(entry_cnt)
    return root, category_dict
   
   
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
    config_parser.read('Input/config.txt')
    
#     test()
     
    ontology_dict = load_ontology(config_parser.get('input', 'ontology_file_name'))
     
    suffix_list = load_list(config_parser.get('input', 'suffix_file_name'))
    suffix_singleton_list = load_list(config_parser.get('input', 'suffix_singleton_file_name'))
    suffix_stoplist = load_list(config_parser.get('input', 'suffix_stoplist_file_name'))
      
    initial_list = load_list(config_parser.get('input', 'initial_file_name'))
      
    root = parse_dict(config_parser.get('input', 'txt_file_name'), ontology_dict, suffix_list, suffix_singleton_list, suffix_stoplist, initial_list, config_parser.getint('input', 'initial_cnt'), )
    serialize_dict(root, config_parser.get('input', 'xml_schema_file_name'), config_parser.get('output', 'xml_file_name'))

    return


if __name__ == '__main__':
    """ main """
    # Log
    logging.basicConfig(filename='log.txt', filemode='w', level=logging.CRITICAL, 
    format='[%(levelname)s\t%(asctime)s\t%(funcName)s\t%(lineno)d]\t%(message)s')

    main()
    