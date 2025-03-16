import markdown
import os

class MarkdownToHTML:
    """
    将Markdown转换为HTML的工具类
    """
    
    def __init__(self):
        """
        初始化转换器
        """
        # 支持的主题列表
        self.themes = {
            'default': self._get_default_css(),
            'dark': self._get_dark_css(),
            'blue': self._get_blue_css(),
            'green': self._get_green_css()
        }
    
    def convert(self, markdown_content, theme='default', custom_css=None):
        """
        将Markdown内容转换为HTML
        
        Args:
            markdown_content (str): Markdown内容
            theme (str): 主题名称，可选值为'default', 'dark', 'green', 'blue'等
            custom_css (str): 自定义CSS样式内容
            
        Returns:
            str: 转换后的HTML内容
        """
        # 使用Python-Markdown库将Markdown转换为HTML
        html_body = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br'
            ]
        )
        
        # 获取主题CSS
        theme_css = self.themes.get(theme, self.themes['default'])
        
        # 组合HTML文档
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Markdown Preview</title>
            <style>
                {theme_css}
                {custom_css or ''}
            </style>
        </head>
        <body>
            <div class="markdown-body">
                {html_body}
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_default_css(self):
        """
        获取默认主题的CSS
        """
        return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 16px;
                line-height: 1.6;
                color: #333;
                background-color: #fff;
                margin: 0;
                padding: 20px;
            }
            
            .markdown-body {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }
            
            h1 {
                font-size: 2em;
                border-bottom: 1px solid #eaecef;
                padding-bottom: 0.3em;
            }
            
            h2 {
                font-size: 1.5em;
                border-bottom: 1px solid #eaecef;
                padding-bottom: 0.3em;
            }
            
            h3 {
                font-size: 1.25em;
            }
            
            h4 {
                font-size: 1em;
            }
            
            p {
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            a {
                color: #0366d6;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
            }
            
            code {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: rgba(27, 31, 35, 0.05);
                border-radius: 3px;
            }
            
            pre {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                word-wrap: normal;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: #f6f8fa;
                border-radius: 3px;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                margin: 0;
                font-size: 100%;
                word-break: normal;
                white-space: pre;
                border: 0;
            }
            
            blockquote {
                margin: 0;
                padding: 0 1em;
                color: #6a737d;
                border-left: 0.25em solid #dfe2e5;
            }
            
            ul, ol {
                padding-left: 2em;
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            table {
                border-spacing: 0;
                border-collapse: collapse;
                margin-top: 0;
                margin-bottom: 16px;
                width: 100%;
                overflow: auto;
            }
            
            table th {
                font-weight: 600;
                padding: 6px 13px;
                border: 1px solid #dfe2e5;
            }
            
            table td {
                padding: 6px 13px;
                border: 1px solid #dfe2e5;
            }
            
            table tr {
                background-color: #fff;
                border-top: 1px solid #c6cbd1;
            }
            
            table tr:nth-child(2n) {
                background-color: #f6f8fa;
            }
            
            img {
                max-width: 100%;
                box-sizing: content-box;
            }
            
            hr {
                height: 0.25em;
                padding: 0;
                margin: 24px 0;
                background-color: #e1e4e8;
                border: 0;
            }
        """
    
    def _get_dark_css(self):
        """
        获取暗色主题的CSS
        """
        return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 16px;
                line-height: 1.6;
                color: #c9d1d9;
                background-color: #0d1117;
                margin: 0;
                padding: 20px;
            }
            
            .markdown-body {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                color: #e6edf3;
            }
            
            h1 {
                font-size: 2em;
                border-bottom: 1px solid #21262d;
                padding-bottom: 0.3em;
            }
            
            h2 {
                font-size: 1.5em;
                border-bottom: 1px solid #21262d;
                padding-bottom: 0.3em;
            }
            
            h3 {
                font-size: 1.25em;
            }
            
            h4 {
                font-size: 1em;
            }
            
            p {
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            a {
                color: #58a6ff;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
            }
            
            code {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: rgba(110, 118, 129, 0.4);
                border-radius: 3px;
                color: #e6edf3;
            }
            
            pre {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                word-wrap: normal;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: #161b22;
                border-radius: 3px;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                margin: 0;
                font-size: 100%;
                word-break: normal;
                white-space: pre;
                border: 0;
            }
            
            blockquote {
                margin: 0;
                padding: 0 1em;
                color: #8b949e;
                border-left: 0.25em solid #30363d;
            }
            
            ul, ol {
                padding-left: 2em;
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            table {
                border-spacing: 0;
                border-collapse: collapse;
                margin-top: 0;
                margin-bottom: 16px;
                width: 100%;
                overflow: auto;
            }
            
            table th {
                font-weight: 600;
                padding: 6px 13px;
                border: 1px solid #30363d;
            }
            
            table td {
                padding: 6px 13px;
                border: 1px solid #30363d;
            }
            
            table tr {
                background-color: #0d1117;
                border-top: 1px solid #21262d;
            }
            
            table tr:nth-child(2n) {
                background-color: #161b22;
            }
            
            img {
                max-width: 100%;
                box-sizing: content-box;
            }
            
            hr {
                height: 0.25em;
                padding: 0;
                margin: 24px 0;
                background-color: #30363d;
                border: 0;
            }
        """
    
    def _get_blue_css(self):
        """
        获取蓝色主题的CSS
        """
        return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 16px;
                line-height: 1.6;
                color: #333;
                background-color: #f0f8ff;
                margin: 0;
                padding: 20px;
            }
            
            .markdown-body {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                color: #1e50a2;
            }
            
            h1 {
                font-size: 2em;
                border-bottom: 1px solid #cce5ff;
                padding-bottom: 0.3em;
            }
            
            h2 {
                font-size: 1.5em;
                border-bottom: 1px solid #cce5ff;
                padding-bottom: 0.3em;
            }
            
            h3 {
                font-size: 1.25em;
            }
            
            h4 {
                font-size: 1em;
            }
            
            p {
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            a {
                color: #0366d6;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
                color: #004080;
            }
            
            code {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: #e6f0ff;
                border-radius: 3px;
            }
            
            pre {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                word-wrap: normal;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: #f0f5ff;
                border-radius: 3px;
                border: 1px solid #cce5ff;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                margin: 0;
                font-size: 100%;
                word-break: normal;
                white-space: pre;
                border: 0;
            }
            
            blockquote {
                margin: 0;
                padding: 0 1em;
                color: #4a76a8;
                border-left: 0.25em solid #79a6d2;
                background-color: #f5f9ff;
            }
            
            ul, ol {
                padding-left: 2em;
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            table {
                border-spacing: 0;
                border-collapse: collapse;
                margin-top: 0;
                margin-bottom: 16px;
                width: 100%;
                overflow: auto;
            }
            
            table th {
                font-weight: 600;
                padding: 6px 13px;
                border: 1px solid #cce5ff;
                background-color: #e6f0ff;
            }
            
            table td {
                padding: 6px 13px;
                border: 1px solid #cce5ff;
            }
            
            table tr {
                background-color: #fff;
                border-top: 1px solid #cce5ff;
            }
            
            table tr:nth-child(2n) {
                background-color: #f5f9ff;
            }
            
            img {
                max-width: 100%;
                box-sizing: content-box;
            }
            
            hr {
                height: 0.25em;
                padding: 0;
                margin: 24px 0;
                background-color: #cce5ff;
                border: 0;
            }
        """
    
    def _get_green_css(self):
        """
        获取绿色主题的CSS
        """
        return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 16px;
                line-height: 1.6;
                color: #333;
                background-color: #f0fff0;
                margin: 0;
                padding: 20px;
            }
            
            .markdown-body {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                color: #2e8b57;
            }
            
            h1 {
                font-size: 2em;
                border-bottom: 1px solid #ccffcc;
                padding-bottom: 0.3em;
            }
            
            h2 {
                font-size: 1.5em;
                border-bottom: 1px solid #ccffcc;
                padding-bottom: 0.3em;
            }
            
            h3 {
                font-size: 1.25em;
            }
            
            h4 {
                font-size: 1em;
            }
            
            p {
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            a {
                color: #228b22;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
                color: #006400;
            }
            
            code {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: #e6ffe6;
                border-radius: 3px;
            }
            
            pre {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                word-wrap: normal;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: #f0fff0;
                border-radius: 3px;
                border: 1px solid #ccffcc;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                margin: 0;
                font-size: 100%;
                word-break: normal;
                white-space: pre;
                border: 0;
            }
            
            blockquote {
                margin: 0;
                padding: 0 1em;
                color: #3cb371;
                border-left: 0.25em solid #90ee90;
                background-color: #f5fff5;
            }
            
            ul, ol {
                padding-left: 2em;
                margin-top: 0;
                margin-bottom: 16px;
            }
            
            table {
                border-spacing: 0;
                border-collapse: collapse;
                margin-top: 0;
                margin-bottom: 16px;
                width: 100%;
                overflow: auto;
            }
            
            table th {
                font-weight: 600;
                padding: 6px 13px;
                border: 1px solid #ccffcc;
                background-color: #e6ffe6;
            }
            
            table td {
                padding: 6px 13px;
                border: 1px solid #ccffcc;
            }
            
            table tr {
                background-color: #fff;
                border-top: 1px solid #ccffcc;
            }
            
            table tr:nth-child(2n) {
                background-color: #f5fff5;
            }
            
            img {
                max-width: 100%;
                box-sizing: content-box;
            }
            
            hr {
                height: 0.25em;
                padding: 0;
                margin: 24px 0;
                background-color: #ccffcc;
                border: 0;
            }
        """
