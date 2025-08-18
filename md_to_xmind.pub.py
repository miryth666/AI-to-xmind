# 时间：2025/8/921:13
# md_to_xmind.py
"""
Markdown to XMind Converter
Author: Miryth666
Date: 2025/8/5
Version: 1.0

This tool converts Markdown content into XMind mind maps.
"""

import json
import os
import pprint
import traceback
import re
import difflib
import emoji
import markdown
import nonrepeat_filename
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from bs4 import BeautifulSoup, NavigableString
from colorama import init, Fore
import xmind
from xmind.core import workbook, saver, styles
from xmind.core.topic import TopicElement

# Initialize colorama
init(autoreset=True)


class MarkdownToXMindConverter:
    def __init__(self):
        # Configuration flags
        self.config = {
            'enter_allowed': True,
            'right_arrow_allowed': True,
            'code_split_allowed': False,
            'table_split_allowed': True,
            'test_mode': False,
            'emoji_allowed': False
        }

        # Constants
        self.IGNORED_TAGS = ['strong', 'i', 'b', 'code', 'em', 'br']
        self.TEXT_TAGS = ['ol', 'ul', 'p', 'blockquote']
        self.HEADER_TAGS = ['h1', 'h2', 'h3', 'h4']

        # State variables
        self.xmind_title = '默认标题'
        self.md_content = None

    def run(self):
        """Main entry point for the converter"""
        if self.config['test_mode']:
            self._run_test_mode()
        else:
            self._show_gui()

    def _run_test_mode(self):
        """Run in test mode with predefined content"""
        with open('md测试.txt', 'r', encoding='UTF-8') as txt:
            self.md_content = txt.read()
        self._convert_md_to_xmind()

    def _show_gui(self):
        """Display the GUI for user input"""
        root = tk.Tk()
        root.title("Markdown 转 XMind 转换器")
        root.geometry("500x400")
        root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=10)
        title_font = tkfont.Font(family="Helvetica", size=10, weight="bold")

        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title input
        label_title = ttk.Label(main_frame, text="中心主题以及文件名：", font=title_font)
        label_title.grid(row=0, column=0, padx=5, pady=(5, 5), sticky='w')
        entry_title = ttk.Entry(main_frame, width=50)
        entry_title.grid(row=0, column=1, padx=5, pady=(5, 5), sticky='ew')

        # Markdown content
        label_md = ttk.Label(main_frame, text="Markdown 文本：", font=title_font)
        label_md.grid(row=1, column=0, padx=5, pady=(10, 5), sticky='nw')
        text_md = tk.Text(main_frame, height=12, width=50, wrap=tk.WORD,
                          font=('Consolas', 10), padx=5, pady=5)
        text_md.grid(row=1, column=1, padx=5, pady=(10, 5), sticky='nsew')
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_md.yview)
        scrollbar.grid(row=1, column=2, sticky='ns')
        text_md['yscrollcommand'] = scrollbar.set

        # Submit button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=(15, 5))
        btn_submit = ttk.Button(btn_frame, text="转换",
                                command=lambda: self._on_submit(entry_title, text_md, root))
        btn_submit.pack()

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        entry_title.focus()
        entry_title.insert(0, "未命名主题")
        root.mainloop()

    def _on_submit(self, entry_title, text_md, root):
        """Handle form submission"""
        self.xmind_title = entry_title.get()
        self.md_content = text_md.get("1.0", tk.END).strip()
        root.destroy()
        self._convert_md_to_xmind()

    def _convert_md_to_xmind(self):
        """Convert Markdown content to XMind"""
        # Preprocess content
        if not self.config['emoji_allowed']:
            self.md_content = self._remove_emoji(self.md_content)

        # Convert Markdown to HTML
        html = markdown.markdown(self.md_content)
        if self.config['test_mode']:
            print('Markdown解析为HTML:')
            print(html)

        # Parse HTML to outline structure
        outline = self._parse_html_to_tree(html)

        # Generate XMind file
        path = nonrepeat_filename.gup(
            os.path.join(os.path.expanduser("~"), f"Desktop/{self.xmind_title}.xmind")
        ) if not self.config['test_mode'] else os.path.join(
            os.path.expanduser("~"), f"Desktop/{self.xmind_title}.xmind"
        )

        self._create_xmind_from_outline(outline, path)

        # Final messages
        if not self.config['test_mode']:
            print(Fore.BLUE + '注：生成的思维导图为默认风格，请在xmind软件中更改风格（推荐"田园"）;'
                              '另外有一些部分级别识别错误，请自行修改;注意以短横线开头的级别，程序难以处理，请手动处理')
        os.startfile(path)

    def _parse_html_to_tree(self, html_content):
        """Parse HTML content into a hierarchical tree structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        self._pre_process_html(soup)
        final_res = {self.xmind_title: self._extract_sections(soup, 'h1')}

        if self.config['test_mode']:
            print(Fore.GREEN + '已生成树状结构:')
            pprint.pprint(final_res)

            # Check for missing content
            df_lst = self._diff_with_edit_distance(soup.get_text(), final_res)
            df = '”\n\t“'.join(df_lst) if df_lst else '无'
            print(Fore.YELLOW + '省略掉原文的部分: “' + df + '”')

            if len(df_lst) > 5:
                print(Fore.RED + '检测到省略的部分过多！请检查有无关键内容缺失，并进行手动添加')

        return final_res

    def _extract_sections(self, soup, tag_name):
        """Recursively extract sections from HTML based on header tags"""
        if tag_name not in self.HEADER_TAGS:
            return []

        sections = []
        headers = soup.find_all(tag_name)

        if headers:
            for header in headers:
                sections.append(self._process_header(header, tag_name))
        else:
            # Try next level header if current not found
            next_level = self.HEADER_TAGS[self.HEADER_TAGS.index(tag_name) + 1]
            sections = self._extract_sections(soup, next_level)

        return sections

    def _process_header(self, header, tag_name):
        """Process a single header and its content"""
        section_title = header.get_text().replace('：', ':').strip().strip(':')
        result = []
        next_sibling = header.next_sibling

        while next_sibling:
            if not next_sibling.name:
                next_sibling = next_sibling.next_sibling
                continue

            # Check if we've reached a same or higher level header
            if next_sibling.name in self.HEADER_TAGS:
                header_idx = self.HEADER_TAGS.index(next_sibling.name)
                current_idx = self.HEADER_TAGS.index(tag_name)
                if header_idx <= current_idx:
                    break

            # Process sub-headers
            if next_sibling.name in self.HEADER_TAGS:
                next_idx = self.HEADER_TAGS.index(next_sibling.name)
                current_idx = self.HEADER_TAGS.index(tag_name)

                if next_idx > current_idx:
                    result.append(self._process_header(next_sibling, next_sibling.name))

            # Process text content
            elif next_sibling.name in self.TEXT_TAGS:
                result.append(self._process_list(next_sibling))

            next_sibling = next_sibling.next_sibling

        # Handle case with no direct content
        if not result and tag_name != 'h4':
            next_level = self.HEADER_TAGS[self.HEADER_TAGS.index(tag_name) + 1]
            result = self._process_header(header, next_level)

        return {section_title: result}

    def _process_list(self, list_container, parent_key=None):
        """Process list-like HTML elements (ol, ul, p, etc.)"""
        # Prepare children elements
        children = [
                       child for child in list_container.children
                       if child.name and child.name not in self.IGNORED_TAGS
                   ] or [list_container]

        items = []
        child_items = {}

        for child in children:
            if not child.name:
                continue

            text = child.get_text().replace('：', ':').replace('；', ';').rstrip()

            # Handle nested structures
            if any(grandchild.name and grandchild.name not in self.IGNORED_TAGS
                   for grandchild in child.children):
                nested = self._process_list(child)
                items.append(nested)
            # Handle bold items as parent nodes
            elif f'<strong>{text.replace(":", "")}</strong>' in str(child):
                if child_items:
                    items.append(child_items)
                child_items = {text.strip(":"): []}
            # Process regular items
            else:
                item = self._process_colon(text)
                if child_items:
                    child_items[list(child_items.keys())[0]].append(item)
                else:
                    items.append(item)

        # Add any remaining child items
        if child_items:
            items.append(child_items)

        # Post-process results
        result = {parent_key: items} if parent_key else items
        return self._post_process_tree(result)

    def _process_colon(self, text):
        """Process text containing colons to create hierarchy"""
        if ':' in text and not text.startswith('```') and not text.endswith('```'):
            idx = text.index(':')

            # Skip if colon is inside parentheses or too long
            if (('(' in text[:idx] or '（' in text[:idx]) and
                    (')' not in text[:idx] and '）' not in text[:idx]) or
                    idx > 30):
                return text.strip(':')

            parts = [p.strip() for p in text.split(':', 1)]
            if len(parts) >= 2 and parts[1]:
                return {parts[0]: [p.strip() for p in parts[1].split(';') if p.strip()]}

        return text

    def _post_process_tree(self, data):
        """Post-process the tree structure for better formatting"""
        if isinstance(data, dict):
            return {k.strip('\n'): self._post_process_tree(v) for k, v in data.items()}

        if isinstance(data, list):
            return [self._post_process_tree(item) for item in data if item]

        if isinstance(data, str):
            # Handle tables
            if ('| :-' in data or '|--' in data) and data.startswith('|') and data.endswith('|') and self.config[
                'table_split_allowed']:
                try:
                    return self._parse_table_data(data)
                except:
                    print(Fore.YELLOW + '表格分裂失败！')

            # Handle multi-line content
            lines = data.splitlines()
            if lines:
                if len(lines) > 1:
                    return [line.strip() for line in lines if line.strip()]
                return lines[0].strip()

        return data

    def _parse_table_data(self, table_text):
        """Parse Markdown table data into structured format"""
        lines = table_text.strip().split('\n')
        headers = [header.strip() for header in lines[0].split('|')[1:-1]]
        feature_names = headers[1:]
        result = []

        for line in lines[2:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) != len(headers):
                continue

            category = cells[0]
            values = cells[1:]
            feature_entries = [{feature_names[i]: values[i]} for i in range(len(feature_names))]
            result.append({category: feature_entries})

        return result

    def _pre_process_html(self, soup):
        """Pre-process HTML content before parsing"""
        if self.config['code_split_allowed']:
            return

        for element in soup.find_all('p'):
            if element.get_text().startswith('```') and not element.get_text().endswith('```'):
                plain_text = element.get_text()
                next_ele = element.next_sibling

                while next_ele and not next_ele.get_text().endswith('```'):
                    if not next_ele.name:
                        plain_text += next_ele.get_text()
                    else:
                        plain_text += next_ele.get_text()
                        next_ele.decompose()
                    next_ele = next_ele.next_sibling

                if next_ele:
                    plain_text += next_ele.get_text()
                    next_ele.decompose()

                while '\n\n\n' in plain_text:
                    plain_text = plain_text.replace('\n\n\n', '\n\n')

                new_p = soup.new_tag('p')
                new_p.string = plain_text
                element.replace_with(new_p)

    def _diff_with_edit_distance(self, original, parsed):
        """Find content in original text missing from parsed structure"""
        parsed_text = json.dumps(parsed, ensure_ascii=False)
        differ = difflib.Differ()
        diff = list(differ.compare(parsed_text, original))

        missing = [item[2:] for item in diff if item.startswith('+ ')]
        missing_text = ''.join(m for m in missing if m.strip() and m.strip().translate(
            str.maketrans('', '', '：:；;→|-')
        ))

        return self._split_missing_text(missing_text, original)

    def _split_missing_text(self, text, original):
        """Split missing text into meaningful segments"""
        segments = []
        start = 0

        while start < len(text):
            # Find the longest substring present in original
            end = len(text)
            while end > start:
                segment = text[start:end]
                if segment in original:
                    segments.append(segment)
                    start = end
                    break
                end -= 1
            else:
                # No segment found, move to next character
                start += 1

        return [s for s in segments if len(s) >= 2]

    def _remove_emoji(self, text):
        """Remove emoji from text"""
        return ''.join(c for c in text if c not in emoji.EMOJI_DATA)

    def _create_xmind_from_outline(self, outline, output_path):
        """Create XMind file from outline structure"""
        wb = xmind.load('new.xmind')
        sheet = wb.getPrimarySheet()
        root_topic = sheet.getRootTopic()
        root_title = list(outline.keys())[0]
        root_topic.setTitle(root_title)
        self._add_subtopics(root_topic, outline[root_title])
        xmind.save(wb, output_path)
        print(Fore.GREEN + f'思维导图生成完毕，保存在{output_path}中。')

    def _add_subtopics(self, parent, subtopics):
        """Recursively add subtopics to XMind"""
        if isinstance(subtopics, dict):
            for title, children in subtopics.items():
                topic = TopicElement(ownerWorkbook=parent.getOwnerWorkbook())
                topic.setTitle(title)
                parent.addSubTopic(topic)
                self._add_subtopics(topic, children)
        elif isinstance(subtopics, list):
            for item in subtopics:
                self._add_subtopics(parent, item)
        else:
            topic = TopicElement(ownerWorkbook=parent.getOwnerWorkbook())
            topic.setTitle(str(subtopics))
            parent.addSubTopic(topic)


if __name__ == '__main__':
    converter = MarkdownToXMindConverter()

    converter.run()
