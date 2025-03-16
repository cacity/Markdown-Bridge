import os
import sys
import json
import webbrowser
from markdown_converter import MarkdownToHTML

def convert_markdown_file_to_html(markdown_file_path, output_html_path=None, theme='default', custom_css=None, open_browser=False):
    """
    将Markdown文件转换为HTML文件，实现与doocs/md项目相同的渲染效果
    
    Args:
        markdown_file_path (str): Markdown文件的路径
        output_html_path (str, optional): 输出HTML文件的路径。如果为None，则使用与输入文件相同的名称，但扩展名为.html
        theme (str, optional): 主题名称，可选值为'default', 'dark', 'green', 'blue'等
        custom_css (str, optional): 自定义CSS样式内容
        open_browser (bool, optional): 是否在转换完成后自动打开浏览器查看结果
        
    Returns:
        str: 输出HTML文件的路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"找不到Markdown文件: {markdown_file_path}")
    
    # 如果未指定输出路径，则使用默认路径
    if output_html_path is None:
        base_name = os.path.splitext(os.path.basename(markdown_file_path))[0]
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_html_path = os.path.join(output_dir, f"{base_name}.html")
    
    # 读取Markdown文件内容
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        raise IOError(f"读取Markdown文件时出错: {e}")
    
    # 创建转换器实例
    converter = MarkdownToHTML()
    
    # 获取文件元数据（如果有）
    metadata = extract_metadata(markdown_content)
    if metadata:
        # 从元数据中提取主题和自定义CSS（如果有）
        theme = metadata.get('theme', theme)
        custom_css_from_meta = metadata.get('custom_css')
        if custom_css_from_meta:
            custom_css = custom_css_from_meta
        # 移除元数据部分
        markdown_content = remove_metadata(markdown_content)
    
    # 转换Markdown为HTML
    html_content = converter.convert(markdown_content, theme=theme, custom_css=custom_css)
    
    # 写入HTML文件
    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        raise IOError(f"写入HTML文件时出错: {e}")
    
    # 如果需要，在浏览器中打开结果
    if open_browser:
        webbrowser.open(f"file://{os.path.abspath(output_html_path)}")
    
    return output_html_path

def convert_markdown_to_html_string(markdown_content, theme='default', custom_css=None):
    """
    将Markdown文本直接转换为HTML字符串
    
    Args:
        markdown_content (str): Markdown文本内容
        theme (str, optional): 主题名称，可选值为'default', 'dark', 'green', 'blue'等
        custom_css (str, optional): 自定义CSS样式内容
        
    Returns:
        str: 转换后的HTML内容
    """
    # 创建转换器实例
    converter = MarkdownToHTML()
    
    # 获取文件元数据（如果有）
    metadata = extract_metadata(markdown_content)
    if metadata:
        # 从元数据中提取主题和自定义CSS（如果有）
        theme = metadata.get('theme', theme)
        custom_css_from_meta = metadata.get('custom_css')
        if custom_css_from_meta:
            custom_css = custom_css_from_meta
        # 移除元数据部分
        markdown_content = remove_metadata(markdown_content)
    
    # 转换Markdown为HTML
    html_content = converter.convert(markdown_content, theme, custom_css)
    
    return html_content

def extract_metadata(markdown_content):
    """
    从Markdown内容中提取元数据
    元数据格式为YAML风格的前置内容，例如：
    ---
    theme: dark
    custom_css: |
      .custom-class { color: red; }
    ---
    
    Args:
        markdown_content (str): Markdown内容
        
    Returns:
        dict: 元数据字典，如果没有元数据则返回None
    """
    # 检查是否有元数据标记
    if not markdown_content.startswith('---'):
        return None
    
    # 查找元数据结束标记
    end_index = markdown_content.find('---', 3)
    if end_index == -1:
        return None
    
    # 提取元数据部分
    metadata_text = markdown_content[3:end_index].strip()
    
    # 解析元数据
    metadata = {}
    for line in metadata_text.split('\n'):
        line = line.strip()
        if not line or ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # 处理多行值（如自定义CSS）
        if value == '|':
            # 找到下一行的缩进级别
            next_lines = []
            for next_line in metadata_text.split('\n')[metadata_text.split('\n').index(line) + 1:]:
                if next_line.startswith(' '):
                    next_lines.append(next_line.strip())
                else:
                    break
            value = '\n'.join(next_lines)
        
        metadata[key] = value
    
    return metadata

def remove_metadata(markdown_content):
    """
    从Markdown内容中移除元数据部分
    
    Args:
        markdown_content (str): 包含元数据的Markdown内容
        
    Returns:
        str: 移除元数据后的Markdown内容
    """
    if not markdown_content.startswith('---'):
        return markdown_content
    
    end_index = markdown_content.find('---', 3)
    if end_index == -1:
        return markdown_content
    
    return markdown_content[end_index + 3:].strip()

def main():
    # 命令行入口函数
    import argparse
    
    parser = argparse.ArgumentParser(description='将Markdown文件转换为HTML')
    parser.add_argument('input', help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出的HTML文件路径')
    parser.add_argument('-t', '--theme', default='default', help='主题名称')
    parser.add_argument('-c', '--css', help='自定义CSS文件路径')
    parser.add_argument('-b', '--browser', action='store_true', help='转换完成后在浏览器中打开')
    
    args = parser.parse_args()
    
    # 如果提供了自定义CSS文件，读取其内容
    custom_css = None
    if args.css and os.path.exists(args.css):
        with open(args.css, 'r', encoding='utf-8') as f:
            custom_css = f.read()
    
    # 转换文件
    output_path = convert_markdown_file_to_html(
        args.input, 
        args.output, 
        args.theme, 
        custom_css, 
        args.browser
    )
    
    print(f"转换完成，输出文件: {output_path}")

if __name__ == "__main__":
    main()
