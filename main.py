#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import html
import json
import logging
import os
import re
import sys
import time
from string import Template
from typing import Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv

import requests
from tqdm import tqdm

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LatexFormulaHandler:
    """LaTeX 公式处理类，专门用于处理各种复杂的 LaTeX 公式格式问题"""
    
    def __init__(self):
        """初始化 LaTeX 公式处理器"""
        # 定义各种公式模式
        self.inline_math_pattern = r'\$[^\$]+?\$'
        self.block_math_pattern = r'\$\$[\s\S]*?\$\$'
        
        # 复杂公式模式
        self.complex_math_patterns = [
            r'\$.*?\\mathbf\{.*?\}.*?\$',        # 匹配包含\mathbf的公式
            r'\$.*?\\mathrm\{.*?\}.*?\$',        # 匹配包含\mathrm的公式
            r'\$.*?\\text\{.*?\}.*?\$',          # 匹配包含\text的公式
            r'\$.*?\\left.*?\\right.*?\$',       # 匹配包含\left和\right的公式
            r'\$.*?\\frac\{.*?\}\{.*?\}.*?\$',   # 匹配包含\frac的公式
            r'\$.*?\\sum.*?\$',                  # 匹配包含\sum的公式
            r'\$.*?\\prod.*?\$',                 # 匹配包含\prod的公式
            r'\$.*?\\int.*?\$',                  # 匹配包含\int的公式
            r'\$.*? for .*?\$',                  # 匹配包含"for"的公式
            r'\$.*?\^\{.*?\}.*?\$',              # 匹配包含上标的公式
            r'\$.*?_\{.*?\}.*?\$',               # 匹配包含下标的公式
            r'\$.*?\\widetilde\{.*?\}.*?\$',     # 匹配包含\widetilde的公式
            r'\$.*?\\mathit\{.*?\}.*?\$',        # 匹配包含\mathit的公式
            r'\$.*?\\Pi.*?\$',                   # 匹配包含\Pi的公式
            r'\$.*?\\Gamma.*?\$',                # 匹配包含\Gamma的公式
            r'\$.*?\\nabla.*?\$',                # 匹配包含\nabla的公式
            r'\$.*?\\sim.*?\$',                  # 匹配包含\sim的公式
            r'\$.*?\\tilde.*?\$',                # 匹配包含\tilde的公式
            r'\$.*?\\cdot.*?\$',                 # 匹配包含\cdot的公式
            r'\$\^.*?\$',                        # 匹配简单上标公式
            r'\$_.*?\$',                         # 匹配简单下标公式
            r'\$\\.*?\$',                        # 匹配任何带反斜杠的公式
        ]
        
        # 数学占位符模式
        self.math_placeholder_patterns = [
            r'__(?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+__',
            r'_(?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+_',
            r'_ (?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+ _',
            r'{(?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+}',
            r'___ (?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+__',
            r'__ _(?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+__',
            r'__ (?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+__',
            r'___ _(?:COMPLEX|INLINE|BLOCK|ALL)_MATH_\d+__',
        ]
    
    def protect_formulas(self, text: str, special_elements: Dict[str, str], counter: int) -> Tuple[str, Dict[str, str], int]:
        """
        保护文本中的所有 LaTeX 公式
        
        Args:
            text: 原始文本
            special_elements: 特殊元素字典
            counter: 计数器
            
        Returns:
            处理后的文本，更新的特殊元素字典，更新的计数器
        """
        # 先保护块级公式
        block_math = re.findall(self.block_math_pattern, text)
        for formula in block_math:
            placeholder = f"__BLOCK_MATH_{counter}__"
            special_elements[placeholder] = formula
            text = text.replace(formula, placeholder, 1)
            counter += 1
        
        # 保护所有行内公式，避免遗漏
        all_inline_math = re.findall(self.inline_math_pattern, text)
        for formula in all_inline_math:
            placeholder = f"__ALL_MATH_{counter}__"
            special_elements[placeholder] = formula
            text = text.replace(formula, placeholder, 1)
            counter += 1
        
        # 保护复杂的公式
        for pattern in self.complex_math_patterns:
            complex_formulas = re.findall(pattern, text)
            for formula in complex_formulas:
                if any(formula == special_elements[key] for key in special_elements):
                    continue
                placeholder = f"__COMPLEX_MATH_{counter}__"
                special_elements[placeholder] = formula
                text = text.replace(formula, placeholder, 1)
                counter += 1
        
        return text, special_elements, counter
    
    def fix_formula_format(self, formula: str) -> str:
        """
        修复公式格式问题
        
        Args:
            formula: 原始公式
            
        Returns:
            修复后的公式
        """
        # 修复常见的格式问题
        formula = formula.replace(' $', '$')
        formula = formula.replace('$ ', '$')
        
        # 修复上标和下标问题
        formula = formula.replace('$^{', '$^{')
        formula = formula.replace('$_{', '$_{')
        
        # 修复波浪线问题，将 ${\sim}10$ 转换为 $\sim 10$
        formula = re.sub(r'\$\{\\sim\}([^$]+)\$', r'$\\sim \1$', formula)
        formula = re.sub(r'_\$\{\\sim\}([^$]+)\$', r'$\\sim \1$', formula)
        
        # 修复 mathrm 中的多余空格
        formula = re.sub(r'\\mathrm\{\s*([^}]*)\s*\}', r'\\mathrm{\1}', formula)
        
        # 修复 mathbf 中的多余空格
        formula = re.sub(r'\\mathbf\{\s*([^}]*)\s*\}', r'\\mathbf{\1}', formula)
        
        # 修复连续的 mathbf 问题，如 $\mathbf{D}\mathbf{ing}^{2}$
        formula = re.sub(r'\\mathbf\{([^}]+)\}\\mathbf\{([^}]+)\}', r'\\mathbf{\1\2}', formula)
        
        # 修复上标中的多余空格
        formula = re.sub(r'\^\{\s*([^}]*)\s*\}', r'^{\1}', formula)
        
        # 修复下标中的多余空格
        formula = re.sub(r'_\{\s*([^}]*)\s*\}', r'_{\1}', formula)
        
        # 修复波浪线上的数学符号问题
        formula = re.sub(r'\\widetilde\{\s*([^}]*)\s*\}', r'\\widetilde{\1}', formula)
        formula = re.sub(r'\\tilde\{\s*([^}]*)\s*\}', r'\\tilde{\1}', formula)
        
        # 修复空的花括号问题
        formula = formula.replace('{}', '')
        
        return formula
    
    def restore_formulas(self, text: str, special_elements: Dict[str, str]) -> str:
        """
        恢复文本中的所有 LaTeX 公式并修复格式
        
        Args:
            text: 处理后的文本
            special_elements: 特殊元素字典
            
        Returns:
            恢复公式后的文本
        """
        # 创建一个映射，将所有可能的变体映射到原始内容
        all_variations_map = {}
        for placeholder, original in special_elements.items():
            if not placeholder.startswith('__') or not placeholder.endswith('__'):
                continue
                
            # 提取类型和编号
            match = re.match(r'__([A-Za-z_]+)_(\d+)__', placeholder)
            if not match:
                continue
                
            type_name, number = match.groups()
            if not type_name.endswith('MATH'):
                continue
                
            # 添加各种可能的变体
            all_variations_map[placeholder] = original
            all_variations_map[placeholder.lower()] = original
            all_variations_map[f"__{type_name.lower()}_{number}__"] = original
            all_variations_map[f"_{type_name.lower()}_{number}_"] = original
            all_variations_map[f"_ {type_name.lower()}_{number} _"] = original
            all_variations_map[f"{{{type_name.lower()}_{number}}}"] = original
            all_variations_map[f"__{type_name.lower()}_{number.lower()}__"] = original
            # 处理可能的空格变化
            all_variations_map[f"__ {type_name.lower()} _ {number} __"] = original
            # 处理可能的下划线变化
            all_variations_map[f"__{type_name.lower()}_{number}__"] = original
            all_variations_map[f"__{type_name.lower()}{number}__"] = original
            all_variations_map[f"__{type_name.lower()}-{number}__"] = original
            # 处理可能的下划线变化 - 特殊情况
            all_variations_map[f"__ _{type_name.lower()}_{number}__"] = original
            all_variations_map[f"___ {type_name.lower()}_{number}__"] = original
            all_variations_map[f"__ {type_name.lower()}_{number}__"] = original
        
        # 直接替换所有已知的变体
        for variant, original in all_variations_map.items():
            text = text.replace(variant, self.fix_formula_format(original))
        
        # 处理数学占位符的特殊情况
        for pattern in self.math_placeholder_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match_lower = match.lower()
                for placeholder, original in special_elements.items():
                    if not placeholder.startswith('__') or not placeholder.endswith('__'):
                        continue
                        
                    if not re.search(r'MATH', placeholder, re.IGNORECASE):
                        continue
                        
                    placeholder_lower = placeholder.lower()
                    # 使用相似性匹配来处理轻微的格式变化
                    if placeholder_lower in match_lower or match_lower in placeholder_lower:
                        text = text.replace(match, self.fix_formula_format(original))
                        break
        
        # 最后一次检查，确保所有公式占位符都被替换
        for placeholder, original in special_elements.items():
            if not placeholder.startswith('__') or not placeholder.endswith('__'):
                continue
                
            if not re.search(r'MATH', placeholder, re.IGNORECASE):
                continue
                
            if placeholder in text:
                text = text.replace(placeholder, self.fix_formula_format(original))
        
        return text


class TranslationCache:
    """翻译缓存类，用于存储和检索翻译结果"""
    
    def __init__(self, cache_file: str = None):
        """初始化翻译缓存
        
        Args:
            cache_file: 缓存文件路径，默认为None（不使用文件缓存）
        """
        self.cache = {}
        self.cache_file = cache_file
        self._load_cache()
    
    def _load_cache(self):
        """从文件加载缓存"""
        if not self.cache_file:
            return
            
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"已从 {self.cache_file} 加载 {len(self.cache)} 条翻译缓存")
        except Exception as e:
            logger.warning(f"加载翻译缓存失败: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """保存缓存到文件"""
        if not self.cache_file:
            return
            
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(self.cache)} 条翻译缓存到 {self.cache_file}")
        except Exception as e:
            logger.warning(f"保存翻译缓存失败: {e}")
    
    def get(self, key: str, default=None):
        """获取缓存的翻译结果
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存的翻译结果或默认值
        """
        return self.cache.get(key, default)
    
    def set(self, key: str, value: str):
        """设置缓存的翻译结果
        
        Args:
            key: 缓存键
            value: 翻译结果
        """
        self.cache[key] = value
        self._save_cache()
        
    def clear(self):
        """清空缓存"""
        self.cache = {}
        self._save_cache()


def protect_special_elements(text: str) -> Tuple[str, Dict[str, str]]:
    """
    保护Markdown中的特殊元素，包括LaTeX公式、代码块、链接和图片等
    
    Args:
        text: Markdown文本
    
    Returns:
        处理后的文本和特殊元素映射
    """
    special_elements = {}
    counter = 0
    
    # 使用 LatexFormulaHandler 保护所有公式
    latex_handler = LatexFormulaHandler()
    text, special_elements, counter = latex_handler.protect_formulas(text, special_elements, counter)
    
    # 保护代码块
    code_block_pattern = r'```.*?\n(.*?)```'
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)
    for i, code_block in enumerate(code_blocks):
        placeholder = f"__CODE_BLOCK_{i}__"
        special_elements[placeholder] = f"```\n{code_block}```"
        text = text.replace(f"```\n{code_block}```", placeholder, 1)
    
    # 保护行内代码
    inline_code_pattern = r'`([^`]+)`'
    inline_codes = re.findall(inline_code_pattern, text)
    for i, inline_code in enumerate(inline_codes):
        placeholder = f"__INLINE_CODE_{i}__"
        special_elements[placeholder] = f"`{inline_code}`"
        text = text.replace(f"`{inline_code}`", placeholder, 1)
    
    # 保护HTML标签
    html_tag_pattern = r'<([^>]+)>'
    html_tags = re.findall(html_tag_pattern, text)
    for i, html_tag in enumerate(html_tags):
        placeholder = f"__HTML_TAG_{i}__"
        special_elements[placeholder] = f"<{html_tag}>"
        text = text.replace(f"<{html_tag}>", placeholder, 1)
    
    # 保存所有图片路径，包括有标题和无标题的图片
    # 先处理有标题的图片链接: ![title](url)
    titled_image_pattern = r'!\[((?:(?!\]\().)+?)\]\(((?:(?!\)).)+?)\)'
    titled_images = re.findall(titled_image_pattern, text)
    
    # 再处理无标题的图片链接: ![](url)
    untitled_image_pattern = r'!\[\]\(((?:(?!\)).)+?)\)'
    untitled_images = re.findall(untitled_image_pattern, text)
    
    # 创建一个列表保存所有图片信息，格式为 (是否有标题, 标题内容, 图片URL)
    all_image_paths = []
    
    # 处理有标题的图片
    for i, (title, url) in enumerate(titled_images):
        if title:  # 确保这是有标题的图片
            placeholder = f"__IMAGE_LINK_TITLED_{i}__"
            original = f"![{title}]({url})"
            special_elements[placeholder] = original
            text = text.replace(original, placeholder, 1)
            all_image_paths.append((True, title, url, placeholder))
    
    # 处理无标题的图片
    for i, url in enumerate(untitled_images):
        placeholder = f"__IMAGE_LINK_{i}__"
        original = f"![]({url})"
        special_elements[placeholder] = original
        text = text.replace(original, placeholder, 1)
        all_image_paths.append((False, "", url, placeholder))
    
    # 保存图片路径列表到特殊元素字典中
    special_elements["__ALL_IMAGE_PATHS__"] = all_image_paths
    
    # 保护超链接
    link_pattern = r'\[((?:(?!\]\().)+?)\]\(((?:(?!\)).)+?)\)'
    links = re.findall(link_pattern, text)
    for i, (title, url) in enumerate(links):
        # 跳过已经处理过的图片链接
        original = f"[{title}]({url})"
        if f"!{original}" in special_elements.values():
            continue
        placeholder = f"__LINK_{i}__"
        special_elements[placeholder] = original
        text = text.replace(original, placeholder, 1)
    
    return text, special_elements


def restore_special_elements(text: str, special_elements: Dict[str, str]) -> str:
    """
    恢复Markdown中的特殊元素
    
    Args:
        text: 处理后的文本
        special_elements: 特殊元素映射
    
    Returns:
        恢复特殊元素后的文本
    """
    # 使用 LatexFormulaHandler 恢复和修复所有公式
    latex_handler = LatexFormulaHandler()
    text = latex_handler.restore_formulas(text, special_elements)
    
    # 首先处理常见的占位符格式问题
    # 1. 处理小写问题
    lowercase_map = {}
    for placeholder, original in special_elements.items():
        if not placeholder.startswith('__') or not placeholder.endswith('__'):
            continue
        if re.search(r'MATH', placeholder, re.IGNORECASE):
            continue  # 跳过已由 LatexFormulaHandler 处理的公式
        if placeholder == "__ALL_IMAGE_PATHS__":
            continue  # 跳过图片路径列表
        lowercase_map[placeholder.lower()] = original
    
    # 2. 处理下划线问题 (有些翻译服务可能会改变下划线格式)
    pattern_variations = {
        r'__([A-Za-z_]+)_(\d+)__': lambda m: f"__{m.group(1)}_{m.group(2)}__",  # 标准格式
        r'_([A-Za-z_]+)_(\d+)_': lambda m: f"__{m.group(1)}_{m.group(2)}__",    # 单下划线
        r'_ ([A-Za-z_]+)_(\d+) _': lambda m: f"__{m.group(1)}_{m.group(2)}__",  # 带空格
        r'{([A-Za-z_]+)_(\d+)}': lambda m: f"__{m.group(1)}_{m.group(2)}__",    # 大括号格式
    }
    
    # 创建一个映射，将所有可能的变体映射到原始内容
    all_variations_map = {}
    for placeholder, original in special_elements.items():
        if not placeholder.startswith('__') or not placeholder.endswith('__'):
            continue
        if placeholder == "__ALL_IMAGE_PATHS__":
            continue  # 跳过图片路径列表
            
        all_variations_map[placeholder] = original
        all_variations_map[placeholder.lower()] = original
        
        # 提取类型和编号
        match = re.match(r'__([A-Za-z_]+)_(\d+)__', placeholder)
        if match:
            type_name, number = match.groups()
            # 添加各种可能的变体
            all_variations_map[f"__{type_name.lower()}_{number}__"] = original
            all_variations_map[f"_{type_name.lower()}_{number}_"] = original
            all_variations_map[f"_ {type_name.lower()}_{number} _"] = original
            all_variations_map[f"{{{type_name.lower()}_{number}}}"] = original
            all_variations_map[f"__{type_name.lower()}_{number.lower()}__"] = original
            # 处理可能的空格变化
            all_variations_map[f"__ {type_name.lower()} _ {number} __"] = original
            # 处理可能的下划线变化
            all_variations_map[f"__{type_name.lower()}_{number}__"] = original
            all_variations_map[f"__{type_name.lower()}{number}__"] = original
            all_variations_map[f"__{type_name.lower()}-{number}__"] = original
            # 处理可能的下划线变化 - 特殊情况
            all_variations_map[f"__ _{type_name.lower()}_{number}__"] = original
            all_variations_map[f"___ {type_name.lower()}_{number}__"] = original
            all_variations_map[f"__ {type_name.lower()}_{number}__"] = original
    
    # 对于每个模式变体，找到匹配并替换回原始内容
    for pattern, formatter in pattern_variations.items():
        def replace_with_original(match):
            key = formatter(match)
            return all_variations_map.get(key, match.group(0))
        
        text = re.sub(pattern, replace_with_original, text)
    
    # 直接替换所有已知的变体
    for variant, original in all_variations_map.items():
        text = text.replace(variant, original)
    
    # 修复可能被错误翻译的图片和链接格式
    # 将中文感叹号和括号替换为英文格式
    text = text.replace('！[', '![')
    text = text.replace('](', '](')
    text = text.replace('）', ')')
    text = text.replace('（', '(')
    
    # 额外处理图片路径中的空格和下划线问题
    # 查找形如 ![...](__ images/...) 或 ![...](__ 其他路径) 的模式
    def fix_image_path_in_markdown(match):
        alt_text = match.group(1)
        path = match.group(2)
        
        # 修复路径中的下划线和空格问题
        if path.startswith('__'):
            path = path.replace('__ ', '')
            path = path.replace('__', '')
        elif path.startswith('_ '):
            path = path.replace('_ ', '')
        elif path.startswith('_'):
            path = path.replace('_', '')
            
        # 修复images目录的特殊情况
        if '_ images/' in path or '__images/' in path or '__ images/' in path:
            path = path.replace('_ images/', 'images/')
            path = path.replace('__images/', 'images/')
            path = path.replace('__ images/', 'images/')
            
        return f"![{alt_text}]({path})"
    
    # 应用图片路径修复
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', fix_image_path_in_markdown, text)
    
    # 处理图片占位符 - 使用保存的图片路径列表
    if "__ALL_IMAGE_PATHS__" in special_elements:
        all_image_paths = special_elements["__ALL_IMAGE_PATHS__"]
        
        # 创建一个映射，从占位符到原始图片
        image_placeholder_map = {}
        for has_title, title, url, placeholder in all_image_paths:
            if has_title:
                image_placeholder_map[placeholder] = f"![{title}]({url})"
                # 添加可能的变体
                image_placeholder_map[placeholder.lower()] = f"![{title}]({url})"
                image_placeholder_map[placeholder.replace('__', '_')] = f"![{title}]({url})"
                image_placeholder_map[placeholder.replace('__', '_ ')] = f"![{title}]({url})"
                image_placeholder_map[f"image_link_titled_{placeholder.split('_')[-2]}"] = f"![{title}]({url})"
                image_placeholder_map[f"IMAGE_LINK_TITLED_{placeholder.split('_')[-2]}"] = f"![{title}]({url})"
                # 添加更多可能的变体
                image_placeholder_map[f"image_link_titled_{placeholder.split('_')[-2]}".strip()] = f"![{title}]({url})"
                image_placeholder_map[f"image link titled {placeholder.split('_')[-2]}".strip()] = f"![{title}]({url})"
                image_placeholder_map[f"imagelinktitled{placeholder.split('_')[-2]}".strip()] = f"![{title}]({url})"
            else:
                image_placeholder_map[placeholder] = f"![]({url})"
                # 添加可能的变体
                image_placeholder_map[placeholder.lower()] = f"![]({url})"
                image_placeholder_map[placeholder.replace('__', '_')] = f"![]({url})"
                image_placeholder_map[placeholder.replace('__', '_ ')] = f"![]({url})"
                image_placeholder_map[f"image_link_{placeholder.split('_')[-2]}"] = f"![]({url})"
                image_placeholder_map[f"IMAGE_LINK_{placeholder.split('_')[-2]}"] = f"![]({url})"
                # 添加更多可能的变体
                image_placeholder_map[f"image_link_{placeholder.split('_')[-2]}".strip()] = f"![]({url})"
                image_placeholder_map[f"image link {placeholder.split('_')[-2]}".strip()] = f"![]({url})"
                image_placeholder_map[f"imagelink{placeholder.split('_')[-2]}".strip()] = f"![]({url})"
        
        # 替换所有图片占位符
        for placeholder, original in image_placeholder_map.items():
            text = text.replace(placeholder, original)
        
        # 查找所有可能的图片占位符模式
        image_link_patterns = [
            r'__IMAGE_LINK_TITLED_(\d+)__',
            r'__IMAGE_LINK_(\d+)__',
            r'_IMAGE_LINK_TITLED_(\d+)_',
            r'_IMAGE_LINK_(\d+)_',
            r'_ IMAGE_LINK_TITLED_(\d+) _',
            r'_ IMAGE_LINK_(\d+) _',
            r'__image_link_titled_(\d+)__',
            r'__image_link_(\d+)__',
            r'_image_link_titled_(\d+)_',
            r'_image_link_(\d+)_',
            r'image_link_titled_(\d+)',
            r'image_link_(\d+)',
            r'IMAGE_LINK_TITLED_(\d+)',
            r'IMAGE_LINK_(\d+)',
            r'image link titled (\d+)',
            r'image link (\d+)',
            r'imagelinktitled(\d+)',
            r'imagelink(\d+)',
        ]
        
        # 收集所有剩余的占位符
        remaining_placeholders = []
        for pattern in image_link_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match_num in matches:
                # 找到完整的占位符文本
                for full_match in re.finditer(pattern.replace('(\\d+)', f'({match_num})'), text, re.IGNORECASE):
                    remaining_placeholders.append((int(match_num), full_match.group(0)))
        
        # 如果还有剩余的占位符，按照原始图片列表顺序替换
        if remaining_placeholders:
            remaining_placeholders.sort(key=lambda x: x[0])
            for i, (num, placeholder_text) in enumerate(remaining_placeholders):
                if i < len(all_image_paths):
                    has_title, title, url, _ = all_image_paths[i]
                    if has_title:
                        text = text.replace(placeholder_text, f"![{title}]({url})")
                    else:
                        text = text.replace(placeholder_text, f"![]({url})")
    
    # 修复标题格式问题
    def fix_heading_format(match):
        # 获取标题级别（#的数量）和标题文本
        hashes = match.group(1)
        content = match.group(2)
        
        # 确保使用英文的#，并且#后面有空格
        english_hashes = '#' * len(hashes)
        
        # 如果内容前面没有空格，添加一个空格
        if not content.startswith(' '):
            content = ' ' + content
            
        return f"{english_hashes}{content}"
    
    # 修复标题格式，包括中文的#号和缺少空格的情况
    text = re.sub(r'^([#＃]+)(.*?)$', fix_heading_format, text, flags=re.MULTILINE)
    
    return text


def fix_markdown_format(markdown_text: str, special_elements: Dict[str, str] = None) -> str:
    """
    修复Markdown格式问题，包括标题格式和图片链接
    
    Args:
        markdown_text: Markdown文本
        special_elements: 特殊元素映射，用于恢复原始图片路径
    
    Returns:
        修复后的Markdown文本
    """
    # 修复标题格式问题
    def fix_heading_format(match):
        # 获取标题级别（#的数量）和标题文本
        hashes = match.group(1)
        content = match.group(2)
        
        # 确保使用英文的#，并且#后面有空格
        english_hashes = '#' * len(hashes)
        
        # 如果内容前面没有空格，添加一个空格
        if not content.startswith(' '):
            content = ' ' + content
            
        return f"{english_hashes}{content}"
    
    # 修复标题格式，包括中文的#号和缺少空格的情况
    markdown_text = re.sub(r'^([#＃]+)(.*?)$', fix_heading_format, markdown_text, flags=re.MULTILINE)
    
    # 修复图片链接问题
    def fix_image_link(match):
        # 获取图片链接的各部分
        alt_text = match.group(1)
        url = match.group(2)
        
        # 如果alt_text为空，但url不为空，确保返回正确格式
        if not alt_text and url:
            return f"![]({url})"
        
        return f"![{alt_text}]({url})"
    
    # 处理图片链接格式
    markdown_text = re.sub(r'!\[(.*?)\]\((.*?)\)', fix_image_link, markdown_text)
    
    # 处理可能的图片占位符
    if special_elements and "__ALL_IMAGE_PATHS__" in special_elements:
        all_image_paths = special_elements["__ALL_IMAGE_PATHS__"]
        
        # 查找所有可能的图片占位符
        image_placeholders = re.findall(r'image_link_\d+|IMAGE_LINK_\d+|image_link_titled_\d+|IMAGE_LINK_TITLED_\d+|image link \d+|image link titled \d+|imagelink\d+|imagelinktitled\d+', markdown_text, re.IGNORECASE)
        
        # 如果找到占位符，按照原始图片列表顺序替换
        if image_placeholders:
            for i, placeholder in enumerate(image_placeholders):
                if i < len(all_image_paths):
                    has_title, title, url, _ = all_image_paths[i]
                    if has_title:
                        markdown_text = markdown_text.replace(placeholder, f"![{title}]({url})")
                    else:
                        markdown_text = markdown_text.replace(placeholder, f"![]({url})")
        
        # 检查是否还有任何未替换的图片占位符
        remaining_placeholders = []
        for pattern in [r'__IMAGE_LINK_\d+__', r'__IMAGE_LINK_TITLED_\d+__', 
                        r'image_link_\d+', r'image_link_titled_\d+',
                        r'IMAGE_LINK_\d+', r'IMAGE_LINK_TITLED_\d+']:
            matches = re.findall(pattern, markdown_text, re.IGNORECASE)
            remaining_placeholders.extend(matches)
        
        # 如果还有剩余的占位符，尝试按索引替换
        if remaining_placeholders:
            for placeholder in remaining_placeholders:
                # 尝试从占位符中提取索引
                index_match = re.search(r'(\d+)', placeholder)
                if index_match:
                    index = int(index_match.group(1))
                    if index < len(all_image_paths):
                        has_title, title, url, _ = all_image_paths[index]
                        if has_title:
                            markdown_text = markdown_text.replace(placeholder, f"![{title}]({url})")
                        else:
                            markdown_text = markdown_text.replace(placeholder, f"![]({url})")
    
    return markdown_text


def translate_markdown(
    markdown_text: str,
    lang_in: str = "en",
    lang_out: str = "zh",
    service: str = "google",
    model: str = None,
    api_key: str = None,
    base_url: str = None,
    ignore_cache: bool = False,
    prompt_template: str = None,
) -> str:
    """
    翻译Markdown文本，同时保护公式、代码块等特殊元素
    
    Args:
        markdown_text: Markdown文本
        lang_in: 源语言代码
        lang_out: 目标语言代码
        service: 翻译服务，支持google、deepl、openai、deepseek
        model: 模型名称
        api_key: API密钥
        base_url: API基础URL
        ignore_cache: 是否忽略缓存
        prompt_template: 提示模板
    
    Returns:
        翻译后的Markdown文本
    """
    logger.info(f"开始翻译，源语言：{lang_in}，目标语言：{lang_out}，服务：{service}")
    logger.info(f"输入文本长度：{len(markdown_text)} 字符")
    
    # 初始化翻译缓存
    cache_file = f"translation_cache_{service}_{lang_in}_{lang_out}.json"
    cache = TranslationCache(cache_file)
    
    # 保存所有特殊元素的全局映射，用于最终格式修复
    all_special_elements = {}
    
    # 按段落分割文本
    paragraphs = re.split(r'\n\n+', markdown_text)
    logger.info(f"将文本分割为 {len(paragraphs)} 个段落")
    
    # 创建进度条
    progress_bar = tqdm(total=len(paragraphs), desc="翻译进度")
    
    # 翻译每个段落
    translated_paragraphs = []
    for paragraph in paragraphs:
        # 跳过空段落
        if not paragraph.strip():
            translated_paragraphs.append(paragraph)
            progress_bar.update(1)
            continue
        
        # 检查缓存
        cache_key = f"{paragraph}_{lang_in}_{lang_out}_{service}"
        if not ignore_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                translated_paragraphs.append(cached_result)
                progress_bar.update(1)
                continue
        
        # 保护特殊元素
        protected_text, special_elements = protect_special_elements(paragraph)
        # 将特殊元素添加到全局映射
        all_special_elements.update(special_elements)
        logger.debug(f"保护特殊元素后的文本：{protected_text[:100]}...")
        logger.debug(f"特殊元素数量：{len(special_elements)}")
        
        # 翻译文本
        if lang_in == lang_out:
            # 即使源语言和目标语言相同，也执行处理流程，但跳过实际翻译
            logger.info("源语言和目标语言相同，跳过实际翻译")
            translated_text = protected_text
            # 确保即使不翻译，也能正确处理特殊元素
            latex_handler = LatexFormulaHandler()
            restored_text = latex_handler.restore_formulas(translated_text, special_elements)
            
            # 更新缓存
            cache.set(cache_key, restored_text)
            translated_paragraphs.append(restored_text)
            progress_bar.update(1)
            continue
        elif service == "google":
            try:
                # 尝试使用 googletrans-py 库，这是一个更好维护的分支
                try:
                    from googletrans import Translator
                    translator = Translator()
                    
                    # 转换语言代码为 Google 翻译 API 支持的格式
                    google_lang_in = lang_in
                    google_lang_out = lang_out
                    
                    # 处理常见的语言代码转换
                    lang_code_map = {
                        "zh": "zh-cn",
                        "zh-CN": "zh-cn",
                        "zh-TW": "zh-tw",
                        "en": "en",
                        "ja": "ja",
                        "ko": "ko",
                        "fr": "fr",
                        "de": "de",
                        "es": "es",
                        "it": "it",
                        "ru": "ru",
                        "pt": "pt",
                        "ar": "ar",
                        "hi": "hi",
                    }
                    
                    if lang_in in lang_code_map:
                        google_lang_in = lang_code_map[lang_in]
                    if lang_out in lang_code_map:
                        google_lang_out = lang_code_map[lang_out]
                    
                    logger.info(f"Google 翻译：将语言代码 {lang_in} -> {google_lang_in}, {lang_out} -> {google_lang_out}")
                    
                    translated_text = translator.translate(
                        protected_text, src=google_lang_in, dest=google_lang_out
                    ).text
                except (ImportError, AttributeError) as e:
                    logger.warning(f"标准 googletrans 库出错: {e}，尝试使用 requests 直接调用 Google 翻译 API")
                    # 使用 requests 直接调用 Google 翻译 API
                    def google_translate(text, source_lang, target_lang):
                        url = "https://translate.googleapis.com/translate_a/single"
                        params = {
                            "client": "gtx",
                            "sl": source_lang,
                            "tl": target_lang,
                            "dt": "t",
                            "q": text
                        }
                        response = requests.get(url, params=params)
                        response.raise_for_status()
                        result = response.json()
                        translated_text = ''.join([sentence[0] for sentence in result[0]])
                        return translated_text
                    
                    # 转换语言代码为 Google 翻译 API 支持的格式
                    google_lang_in = lang_in
                    google_lang_out = lang_out
                    
                    # 处理常见的语言代码转换
                    lang_code_map = {
                        "zh": "zh-cn",
                        "zh-CN": "zh-cn",
                        "zh-TW": "zh-tw",
                        "en": "en",
                        "ja": "ja",
                        "ko": "ko",
                        "fr": "fr",
                        "de": "de",
                        "es": "es",
                        "it": "it",
                        "ru": "ru",
                        "pt": "pt",
                        "ar": "ar",
                        "hi": "hi",
                    }
                    
                    if lang_in in lang_code_map:
                        google_lang_in = lang_code_map[lang_in]
                    if lang_out in lang_code_map:
                        google_lang_out = lang_code_map[lang_out]
                    
                    logger.info(f"Google 翻译：将语言代码 {lang_in} -> {google_lang_in}, {lang_out} -> {google_lang_out}")
                    
                    translated_text = google_translate(protected_text, google_lang_in, google_lang_out)
            except Exception as e:
                logger.error(f"Google翻译失败：{e}")
                translated_text = protected_text
        elif service == "deepl":
            import deepl
            translator = deepl.Translator(api_key)
            try:
                result = translator.translate_text(
                    protected_text, source_lang=lang_in, target_lang=lang_out
                )
                translated_text = result.text
            except Exception as e:
                logger.error(f"DeepL翻译失败：{e}")
                translated_text = protected_text
        elif service == "openai":
            import openai
            if api_key:
                openai.api_key = api_key
            if base_url:
                openai.api_base = base_url
            
            system_prompt = "你是一个专业的翻译助手，请将以下文本从{source_lang}翻译成{target_lang}，保持原始格式和标记。"
            if prompt_template:
                system_prompt = Template(prompt_template).safe_substitute(
                    source_lang=lang_in, target_lang=lang_out
                )
            
            try:
                response = openai.ChatCompletion.create(
                    model=model or "gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": protected_text},
                    ],
                    temperature=0.3,
                )
                translated_text = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI翻译失败：{e}")
                translated_text = protected_text
        elif service == "deepseek":
            # 从环境变量获取 DeepSeek 配置
            if not api_key:
                api_key = os.getenv("DEEPSEEK_API_KEY")
            if not base_url:
                base_url = os.getenv("DEEPSEEK_API_URL")
            if not model:
                model = os.getenv("DEEPSEEK_MODEL")
                
            if not api_key or not base_url:
                logger.error("DeepSeek翻译失败：缺少API密钥或基础URL")
                translated_text = protected_text
                progress_bar.update(1)
                continue
                
            system_prompt = "你是一个专业的翻译助手，请将以下文本从{source_lang}翻译成{target_lang}，保持原始格式和标记。"
            if prompt_template:
                system_prompt = Template(prompt_template).safe_substitute(
                    source_lang=lang_in, target_lang=lang_out
                )
                
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": protected_text}
                    ],
                    "temperature": 0.3
                }
                
                response = requests.post(base_url, headers=headers, json=payload)
                response.raise_for_status()
                response_data = response.json()
                
                translated_text = response_data["choices"][0]["message"]["content"]
                logger.info(f"DeepSeek翻译成功，使用模型：{model}")
            except Exception as e:
                logger.error(f"DeepSeek翻译失败：{e}")
                translated_text = protected_text
        else:
            logger.error(f"不支持的翻译服务：{service}")
            translated_text = protected_text
        
        # 恢复特殊元素
        latex_handler = LatexFormulaHandler()
        restored_text = latex_handler.restore_formulas(translated_text, special_elements)
        logger.debug(f"恢复特殊元素后的文本：{restored_text[:100]}...")
        
        # 恢复所有特殊元素，包括图片
        restored_text = restore_special_elements(restored_text, special_elements)
        
        # 更新缓存
        cache.set(cache_key, restored_text)
        
        # 添加到结果
        translated_paragraphs.append(restored_text)
        progress_bar.update(1)
    
    progress_bar.close()
    
    # 合并翻译后的段落
    result = "\n\n".join(translated_paragraphs)
    
    # 最终格式修复，传入所有特殊元素的映射
    result = fix_markdown_format(result, all_special_elements)
    
    # 确保所有图片占位符都被正确替换
    if "__ALL_IMAGE_PATHS__" in all_special_elements:
        all_image_paths = all_special_elements["__ALL_IMAGE_PATHS__"]
        
        # 查找所有可能的图片占位符模式
        image_placeholder_patterns = [
            r'image_link_\d+',
            r'IMAGE_LINK_\d+',
            r'image_link_titled_\d+',
            r'IMAGE_LINK_TITLED_\d+',
            r'image link \d+',
            r'image link titled \d+',
            r'imagelink\d+',
            r'imagelinktitled\d+'
        ]
        
        # 合并所有模式为一个正则表达式
        combined_pattern = '|'.join(image_placeholder_patterns)
        
        # 查找所有匹配的占位符
        placeholders = re.findall(combined_pattern, result, re.IGNORECASE)
        
        # 对于每个找到的占位符，尝试提取索引并替换为正确的图片链接
        for placeholder in placeholders:
            # 提取索引
            index_match = re.search(r'(\d+)', placeholder)
            if index_match:
                index = int(index_match.group(1))
                if index < len(all_image_paths):
                    has_title, title, url, _ = all_image_paths[index]
                    if has_title:
                        result = result.replace(placeholder, f"![{title}]({url})")
                    else:
                        result = result.replace(placeholder, f"![]({url})")
    
    logger.info(f"翻译完成，输出文本长度：{len(result)} 字符")
    return result


if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Markdown翻译工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 翻译文件子命令
    translate_file_parser = subparsers.add_parser("translate-file", help="翻译Markdown文件")
    translate_file_parser.add_argument("input_file", help="输入文件路径")
    translate_file_parser.add_argument("output_file", help="输出文件路径")
    translate_file_parser.add_argument("--lang-in", default="en", help="源语言代码，默认为英语(en)")
    translate_file_parser.add_argument("--lang-out", default="zh", help="目标语言代码，默认为中文(zh)")
    translate_file_parser.add_argument("--service", default="google", choices=["google", "deepl", "openai", "deepseek"], help="翻译服务，默认为google")
    translate_file_parser.add_argument("--model", help="模型名称，仅在使用openai或deepseek服务时有效")
    translate_file_parser.add_argument("--api-key", help="API密钥，仅在使用deepl、openai或deepseek服务时有效")
    translate_file_parser.add_argument("--base-url", help="API基础URL，仅在使用openai或deepseek服务时有效")
    translate_file_parser.add_argument("--ignore-cache", action="store_true", help="忽略缓存")
    translate_file_parser.add_argument("--prompt-template", help="提示模板，仅在使用openai或deepseek服务时有效")
    
    # 翻译文本子命令
    translate_text_parser = subparsers.add_parser("translate-text", help="翻译Markdown文本")
    translate_text_parser.add_argument("text", help="要翻译的文本")
    translate_text_parser.add_argument("--lang-in", default="en", help="源语言代码，默认为英语(en)")
    translate_text_parser.add_argument("--lang-out", default="zh", help="目标语言代码，默认为中文(zh)")
    translate_text_parser.add_argument("--service", default="google", choices=["google", "deepl", "openai", "deepseek"], help="翻译服务，默认为google")
    translate_text_parser.add_argument("--model", help="模型名称，仅在使用openai或deepseek服务时有效")
    translate_text_parser.add_argument("--api-key", help="API密钥，仅在使用deepl、openai或deepseek服务时有效")
    translate_text_parser.add_argument("--base-url", help="API基础URL，仅在使用openai或deepseek服务时有效")
    translate_text_parser.add_argument("--ignore-cache", action="store_true", help="忽略缓存")
    translate_text_parser.add_argument("--prompt-template", help="提示模板，仅在使用openai或deepseek服务时有效")
    
    args = parser.parse_args()
    
    if args.command == "translate-file":
        # 读取输入文件
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                markdown_text = f.read()
        except Exception as e:
            logger.error(f"读取输入文件失败: {e}")
            sys.exit(1)
        
        # 翻译文本
        translated_text = translate_markdown(
            markdown_text=markdown_text,
            lang_in=args.lang_in,
            lang_out=args.lang_out,
            service=args.service,
            model=args.model,
            api_key=args.api_key,
            base_url=args.base_url,
            ignore_cache=args.ignore_cache,
            prompt_template=args.prompt_template,
        )
        
        # 写入输出文件
        try:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(translated_text)
            logger.info(f"翻译结果已保存到 {args.output_file}")
        except Exception as e:
            logger.error(f"写入输出文件失败: {e}")
            sys.exit(1)
    
    elif args.command == "translate-text":
        # 翻译文本
        translated_text = translate_markdown(
            markdown_text=args.text,
            lang_in=args.lang_in,
            lang_out=args.lang_out,
            service=args.service,
            model=args.model,
            api_key=args.api_key,
            base_url=args.base_url,
            ignore_cache=args.ignore_cache,
            prompt_template=args.prompt_template,
        )
        
        # 输出翻译结果
        print(translated_text)
    
    else:
        parser.print_help()
